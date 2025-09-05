"""
Real genome data parser for JCVI-Syn3A and other organisms.
Extends BioXen to work with actual biological data.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import re

try:
    from .schema import BioXenGenomeSchema, BioXenGeneRecord
except ImportError:
    # Fallback for direct execution
    from schema import BioXenGenomeSchema, BioXenGeneRecord

@dataclass
class Gene:
    """Represents a gene from real genome data."""
    start: int
    length: int
    end: int
    strand: int  # +1 or -1
    type: int    # 1=protein coding, 0=RNA
    id: str
    description: str
    
    @property
    def is_essential(self) -> bool:
        """Determine if gene is essential based on known essential functions."""
        essential_keywords = [
            'ribosomal', 'ribosome', 'rRNA', 'tRNA',
            'DNA polymerase', 'RNA polymerase',
            'ATP synthase', 'translation', 'transcription',
            'replication', 'gyrase', 'helicase',
            'aminoacyl', 'ligase', 'synthetase'
        ]
        return any(keyword.lower() in self.description.lower() 
                  for keyword in essential_keywords)
    
    @property
    def functional_category(self) -> str:
        """Categorize gene by function."""
        desc_lower = self.description.lower()
        
        if any(term in desc_lower for term in ['ribosomal', 'ribosome', 'rrna']):
            return 'protein_synthesis'
        elif any(term in desc_lower for term in ['dna polymerase', 'replication', 'helicase']):
            return 'dna_replication'
        elif any(term in desc_lower for term in ['rna polymerase', 'transcription']):
            return 'transcription'
        elif any(term in desc_lower for term in ['atp synthase', 'kinase', 'phosphate']):
            return 'energy_metabolism'
        elif any(term in desc_lower for term in ['ligase', 'synthetase', 'transferase']):
            return 'metabolism'
        elif 'trna' in desc_lower:
            return 'translation'
        elif any(term in desc_lower for term in ['transport', 'abc']):
            return 'transport'
        else:
            return 'other'

@dataclass
class RealGenome:
    """Represents a parsed real genome."""
    organism: str
    genes: List[Gene]
    total_length: int
    
    @property
    def essential_genes(self) -> List[Gene]:
        """Get all essential genes."""
        return [gene for gene in self.genes if gene.is_essential]
    
    @property
    def gene_count_by_category(self) -> Dict[str, int]:
        """Count genes by functional category."""
        categories = {}
        for gene in self.genes:
            cat = gene.functional_category
            categories[cat] = categories.get(cat, 0) + 1
        return categories
    
    def genes_in_region(self, start: int, end: int) -> List[Gene]:
        """Get genes within a genomic region."""
        return [gene for gene in self.genes 
                if gene.start >= start and gene.end <= end]

class RealGenomeParser:
    """Parser for real genome annotation files."""
    
    @staticmethod
    def parse_syn3a(genome_file: Path) -> RealGenome:
        """Parse JCVI-Syn3A genome file."""
        genes = []
        max_pos = 0
        
        with open(genome_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Parse the fixed-width format
                parts = line.split()
                if len(parts) < 7:
                    continue
                
                try:
                    start = int(parts[0])
                    length = int(parts[1])
                    end = int(parts[2])
                    strand = int(parts[3])
                    gene_type = int(parts[4])
                    gene_id = parts[5]
                    description = ' '.join(parts[6:])
                    
                    gene = Gene(
                        start=start,
                        length=length,
                        end=end,
                        strand=strand,
                        type=gene_type,
                        id=gene_id,
                        description=description
                    )
                    genes.append(gene)
                    max_pos = max(max_pos, end)
                    
                except (ValueError, IndexError) as e:
                    print(f"Warning: Could not parse line: {line[:50]}...")
                    continue
        
        return RealGenome(
            organism="JCVI-Syn3A",
            genes=genes,
            total_length=max_pos
        )
    
    @staticmethod
    def create_bioxen_compatible_template(real_genome: RealGenome) -> Dict:
        """Convert real genome to BioXen template format."""
        essential_genes = real_genome.essential_genes
        
        template = {
            'organism': real_genome.organism,
            'genome_size': real_genome.total_length,
            'total_genes': len(real_genome.genes),
            'essential_genes': len(essential_genes),
            'gene_categories': real_genome.gene_count_by_category,
            
            # Essential genes by category for VM construction
            'essential_by_function': {},
            'minimal_gene_set': [],
            
            # Resource requirements (estimated)
            'min_memory_kb': len(essential_genes) * 2,  # 2KB per essential gene
            'min_cpu_percent': 15,  # Minimum CPU for essential processes
            'boot_time_ms': 500 + len(essential_genes) * 2,  # Proportional to complexity
        }
        
        # Group essential genes by function
        for gene in essential_genes:
            category = gene.functional_category
            if category not in template['essential_by_function']:
                template['essential_by_function'][category] = []
            template['essential_by_function'][category].append({
                'id': gene.id,
                'description': gene.description,
                'position': gene.start,
                'length': gene.length
            })
        
        # Create minimal gene set (most critical genes)
        critical_functions = ['protein_synthesis', 'dna_replication', 'transcription', 'energy_metabolism']
        for category in critical_functions:
            if category in template['essential_by_function']:
                template['minimal_gene_set'].extend(template['essential_by_function'][category])
        
        return template

class BioXenRealGenomeIntegrator:
    """Integrates real genome data with BioXen virtualization system."""
    
    def __init__(self, genome_path):
        # Convert to Path object if string is passed
        from pathlib import Path
        if isinstance(genome_path, str):
            self.genome_path = Path(genome_path)
        else:
            self.genome_path = genome_path
        self.real_genome = None
        self.bioxen_template = None
    
    def load_genome(self) -> RealGenome:
        """Load and parse the real genome."""
        if self.genome_path.name.lower().startswith('syn3a'):
            # Legacy syn3A format
            self.real_genome = RealGenomeParser.parse_syn3a(self.genome_path)
        elif self.genome_path.suffix == '.genome':
            # New BioXen schema format
            self.real_genome = self._parse_bioxen_format()
        else:
            raise ValueError(f"Unsupported genome format: {self.genome_path.name}")
        
        return self.real_genome
    
    def _parse_bioxen_format(self) -> RealGenome:
        """Parse BioXen schema format genome files."""
        from .schema import BioXenGenomeSchema
        
        try:
            # Load the BioXen schema
            schema = BioXenGenomeSchema.load_from_file(self.genome_path)
            
            # Convert to RealGenome format
            genes = []
            for gene_record in schema.genes:
                gene = Gene(
                    start=gene_record.start,
                    length=gene_record.length,
                    end=gene_record.end,
                    strand=gene_record.strand,
                    type=gene_record.gene_type,
                    id=gene_record.gene_id,
                    description=gene_record.description or "Unknown function"
                )
                genes.append(gene)
            
            # Create RealGenome instance with correct parameters
            real_genome = RealGenome(
                organism=schema.organism,
                genes=genes,
                total_length=schema.genome_size or 0
            )
            
            # Add gc_content as an attribute if available
            if hasattr(schema, 'gc_content') and schema.gc_content:
                real_genome.gc_content = schema.gc_content
            else:
                real_genome.gc_content = 40.0  # Default value
            
            return real_genome
            
        except Exception as e:
            raise ValueError(f"Failed to parse BioXen format genome: {e}")
    
    
    def create_vm_template(self) -> Dict:
        """Create BioXen VM template from real genome."""
        if not self.real_genome:
            self.load_genome()
        
        self.bioxen_template = RealGenomeParser.create_bioxen_compatible_template(self.real_genome)
        return self.bioxen_template
    
    def simulate_vm_creation(self, vm_id: str, allocated_resources: Dict) -> Dict:
        """Simulate creating a VM with real genome constraints."""
        if not self.bioxen_template:
            self.create_vm_template()
        
        # Check resource constraints against real genome requirements
        min_memory = self.bioxen_template['min_memory_kb']
        min_cpu = self.bioxen_template['min_cpu_percent']
        
        memory_ok = allocated_resources.get('memory_kb', 0) >= min_memory
        cpu_ok = allocated_resources.get('cpu_percent', 0) >= min_cpu
        
        # Simulate gene expression based on available resources
        active_genes = []
        if memory_ok and cpu_ok:
            # All essential genes can be active
            active_genes = self.bioxen_template['minimal_gene_set'].copy()
            
            # Add non-essential genes based on excess resources
            excess_memory = allocated_resources.get('memory_kb', 0) - min_memory
            excess_cpu = allocated_resources.get('cpu_percent', 0) - min_cpu
            
            # Each additional 10KB memory and 5% CPU allows 1 more non-essential gene
            bonus_genes = min(excess_memory // 10, excess_cpu // 5)
            
            non_essential = [g for g in self.real_genome.genes if not g.is_essential]
            for i, gene in enumerate(non_essential[:bonus_genes]):
                active_genes.append({
                    'id': gene.id,
                    'description': gene.description,
                    'position': gene.start,
                    'length': gene.length
                })
        
        return {
            'vm_id': vm_id,
            'organism': self.real_genome.organism,
            'resource_constraints_met': memory_ok and cpu_ok,
            'active_gene_count': len(active_genes),
            'total_genome_genes': len(self.real_genome.genes),
            'essential_genes_active': len([g for g in active_genes 
                                         if any(eg['id'] == g['id'] 
                                               for eg in self.bioxen_template['minimal_gene_set'])]),
            'genome_utilization_percent': (len(active_genes) / len(self.real_genome.genes)) * 100 if len(self.real_genome.genes) > 0 else 0,
            'estimated_boot_time_ms': self.bioxen_template['boot_time_ms'],
            'active_genes': active_genes[:10]  # Show first 10 for brevity
        }
    
    def get_genome_stats(self) -> Dict:
        """Get comprehensive statistics about the real genome."""
        if not self.real_genome:
            self.load_genome()
        
        total_genes = len(self.real_genome.genes)
        essential_genes = len(self.real_genome.essential_genes)
        
        return {
            'organism': self.real_genome.organism,
            'total_genes': total_genes,
            'essential_genes': essential_genes,
            'genome_length_bp': self.real_genome.total_length,
            'protein_coding_genes': len([g for g in self.real_genome.genes if g.type == 1]),
            'rna_genes': len([g for g in self.real_genome.genes if g.type == 0]),
            'gene_categories': self.real_genome.gene_count_by_category,
            'essential_percentage': (essential_genes / total_genes) * 100 if total_genes > 0 else 0,
            'average_gene_length': sum(g.length for g in self.real_genome.genes) / total_genes if total_genes > 0 else 0,
            'coding_density': (sum(g.length for g in self.real_genome.genes) / self.real_genome.total_length) * 100 if self.real_genome.total_length > 0 else 0
        }
