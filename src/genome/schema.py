"""
BioXen Genome Schema Definition and Validation

This module defines the standardized schema for BioXen .genome files
and provides validation, conversion, and export functionality.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Union, Any
from pathlib import Path
import json
import re
from enum import Enum

class GeneType(Enum):
    """Standard gene types in BioXen genome format."""
    PROTEIN_CODING = 1
    RNA_GENE = 0
    TRNA = 2
    RRNA = 3
    NCRNA = 4
    PSEUDOGENE = 5

class Strand(Enum):
    """DNA strand orientation."""
    FORWARD = 1
    REVERSE = -1
    UNKNOWN = 0

@dataclass
class BioXenGeneRecord:
    """
    Standard BioXen gene record format.
    
    Schema version: 1.0
    Compatible with JCVI-Syn3A and other minimal genomes.
    """
    # Core identification
    start: int              # 1-based start position
    length: int             # Gene length in base pairs
    end: int                # 1-based end position
    strand: int             # +1 (forward), -1 (reverse), 0 (unknown)
    gene_type: int          # 1=protein, 0=RNA, 2=tRNA, 3=rRNA, 4=ncRNA, 5=pseudogene
    gene_id: str            # Unique gene identifier
    description: str        # Gene product/function description
    
    # Extended metadata (optional)
    locus_tag: Optional[str] = None
    gene_name: Optional[str] = None
    product: Optional[str] = None
    protein_id: Optional[str] = None
    go_terms: Optional[List[str]] = None
    ec_numbers: Optional[List[str]] = None
    
    # BioXen-specific annotations
    essential: Optional[bool] = None
    functional_category: Optional[str] = None
    vm_priority: Optional[int] = None
    resource_weight: Optional[float] = None
    
    # Compatibility fields for parser integration
    name: Optional[str] = None
    function: Optional[str] = None
    
    def validate(self) -> bool:
        """Validate gene record integrity."""
        if self.start <= 0 or self.end <= 0:
            return False
        if self.length != abs(self.end - self.start) + 1:
            return False
        if self.strand not in [-1, 0, 1]:
            return False
        if self.gene_type not in [0, 1, 2, 3, 4, 5]:
            return False
        if not self.gene_id or not self.description:
            return False
        return True
    
    def to_bioxen_line(self) -> str:
        """Export as BioXen .genome format line."""
        return f"{self.start:>8} {self.length:>6} {self.end:>8} {self.strand:>2} {self.gene_type:>2}  {self.gene_id:<20}  {self.description}"
    
    @classmethod
    def from_bioxen_line(cls, line: str) -> 'BioXenGeneRecord':
        """Parse from BioXen .genome format line."""
        parts = line.strip().split()
        if len(parts) < 7:
            raise ValueError(f"Invalid BioXen genome line: {line}")
        
        return cls(
            start=int(parts[0]),
            length=int(parts[1]),
            end=int(parts[2]),
            strand=int(parts[3]),
            gene_type=int(parts[4]),
            gene_id=parts[5],
            description=' '.join(parts[6:])
        )

@dataclass
class BioXenGenomeSchema:
    """
    Complete BioXen genome schema.
    
    This represents the full genome with metadata and all genes.
    """
    # Genome metadata
    organism: str
    strain: Optional[str] = None
    assembly_accession: Optional[str] = None
    assembly_level: Optional[str] = None
    genome_size: int = 0
    gc_content: Optional[float] = None
    
    # Gene records
    genes: List[BioXenGeneRecord] = None
    
    # BioXen-specific metadata
    schema_version: str = "1.0"
    bioxen_compatible: bool = True
    minimal_genome: bool = False
    
    # Statistics (auto-calculated)
    total_genes: int = 0
    protein_coding_genes: int = 0
    rna_genes: int = 0
    essential_genes: int = 0
    coding_density: float = 0.0
    
    def __post_init__(self):
        """Initialize genes list and calculate statistics."""
        if self.genes is None:
            self.genes = []
        self.calculate_statistics()
    
    @classmethod
    def load_from_file(cls, genome_path: Path) -> 'BioXenGenomeSchema':
        """Load a BioXen genome schema from a .genome file."""
        genes = []
        metadata = {}
        
        with open(genome_path, 'r') as f:
            lines = f.readlines()
        
        # Parse file
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Parse metadata from comments
            if line.startswith('#'):
                if 'Organism:' in line:
                    metadata['organism'] = line.split('Organism:', 1)[1].strip()
                elif 'Strain:' in line:
                    metadata['strain'] = line.split('Strain:', 1)[1].strip()
                elif 'Genome size:' in line:
                    # Extract number from "# Genome size: 580,076 bp"
                    size_str = line.split(':', 1)[1].strip().replace(',', '').split()[0]
                    try:
                        metadata['genome_size'] = int(size_str)
                    except ValueError:
                        pass
                continue
            
            # Parse gene records
            try:
                # The BioXen format uses space-separated values, not tabs
                # Format: start length end strand type gene_id description
                parts = line.split()
                if len(parts) >= 7:
                    start = int(parts[0])
                    length = int(parts[1])
                    end = int(parts[2])
                    strand = int(parts[3])
                    gene_type = int(parts[4])
                    gene_id = parts[5]
                    description = ' '.join(parts[6:]) if len(parts) > 6 else ""
                    
                    # Create gene record
                    gene = BioXenGeneRecord(
                        start=start,
                        length=length,
                        end=end,
                        strand=strand,
                        gene_type=gene_type,
                        gene_id=gene_id,
                        description=description,
                        essential=(gene_type == 1),  # Default: protein coding genes are essential
                        name=gene_id,
                        function=description
                    )
                    genes.append(gene)
                    
            except (ValueError, IndexError) as e:
                # Skip invalid lines - don't print errors for now
                continue
        
        # Create schema instance with organism name fallback
        organism_name = metadata.get('organism')
        
        # If no organism found in comments, try to extract from filename or gene IDs
        if not organism_name or organism_name == 'Unknown':
            # Extract from filename (e.g., "buchnera_aphidicola.genome" -> "Buchnera aphidicola")
            filename = genome_path.stem.lower()
            if filename == 'syn3a':
                organism_name = 'JCVI-Syn3A'
            elif 'buchnera' in filename and 'aphidicola' in filename:
                organism_name = 'Buchnera aphidicola'
            elif 'mycoplasma' in filename and 'genitalium' in filename:
                organism_name = 'Mycoplasma genitalium'
            elif 'mycoplasma' in filename and 'pneumoniae' in filename:
                organism_name = 'Mycoplasma pneumoniae'
            elif 'carsonella' in filename and 'ruddii' in filename:
                organism_name = 'Carsonella ruddii'
            else:
                # Try to extract from gene IDs (e.g., "BUCHNERAAPHIDICOLA_0001")
                if genes and genes[0].gene_id:
                    gene_prefix = genes[0].gene_id.split('_')[0].upper()
                    if 'BUCHNERA' in gene_prefix:
                        organism_name = 'Buchnera aphidicola'
                    elif 'MYCOPLASMA' in gene_prefix:
                        organism_name = 'Mycoplasma species'
                    elif 'CARSONELLA' in gene_prefix:
                        organism_name = 'Carsonella ruddii'
                    else:
                        # Format the filename nicely as fallback
                        organism_name = filename.replace('_', ' ').title()
        
        if not organism_name:
            organism_name = 'Unknown'
        
        schema = cls(
            organism=organism_name,
            strain=metadata.get('strain'),
            genome_size=metadata.get('genome_size', 0),
            genes=genes
        )
        
        return schema
    
    def calculate_statistics(self):
        """Calculate genome statistics from gene records."""
        if not self.genes:
            return
            
        self.total_genes = len(self.genes)
        self.protein_coding_genes = sum(1 for g in self.genes if g.gene_type == 1)
        self.rna_genes = sum(1 for g in self.genes if g.gene_type in [0, 2, 3, 4])
        self.essential_genes = sum(1 for g in self.genes if g.essential)
        
        total_coding_length = sum(g.length for g in self.genes)
        if self.genome_size > 0:
            self.coding_density = (total_coding_length / self.genome_size) * 100
        
        # Auto-detect if this is a minimal genome
        if self.total_genes < 1000 and self.coding_density > 80:
            self.minimal_genome = True
    
    def add_gene(self, gene: BioXenGeneRecord):
        """Add a gene record and update statistics."""
        if gene.validate():
            self.genes.append(gene)
            self.calculate_statistics()
        else:
            raise ValueError(f"Invalid gene record: {gene.gene_id}")
    
    def get_genes_by_type(self, gene_type: int) -> List[BioXenGeneRecord]:
        """Get all genes of a specific type."""
        return [g for g in self.genes if g.gene_type == gene_type]
    
    def get_essential_genes(self) -> List[BioXenGeneRecord]:
        """Get all essential genes."""
        return [g for g in self.genes if g.essential]
    
    def export_bioxen_format(self, output_path: Path):
        """Export to standard BioXen .genome format."""
        with open(output_path, 'w') as f:
            # Write header comment
            f.write(f"# BioXen Genome Format v{self.schema_version}\n")
            f.write(f"# Organism: {self.organism}\n")
            if self.strain:
                f.write(f"# Strain: {self.strain}\n")
            f.write(f"# Total genes: {self.total_genes}\n")
            f.write(f"# Genome size: {self.genome_size:,} bp\n")
            f.write(f"# Coding density: {self.coding_density:.1f}%\n")
            f.write("# Format: start length end strand type gene_id description\n")
            f.write("#\n")
            
            # Write gene records
            for gene in sorted(self.genes, key=lambda x: x.start):
                f.write(gene.to_bioxen_line() + "\n")
    
    def export_json_format(self, output_path: Path):
        """Export to JSON format with full metadata."""
        data = asdict(self)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def to_vm_template(self) -> Dict[str, Any]:
        """Convert to BioXen VM template format."""
        essential_genes = self.get_essential_genes()
        
        return {
            'organism': self.organism,
            'genome_size': self.genome_size,
            'total_genes': self.total_genes,
            'essential_genes': len(essential_genes),
            'minimal_genome': self.minimal_genome,
            'gene_categories': self._categorize_genes(),
            'essential_by_function': self._group_essential_by_function(),
            'minimal_gene_set': [asdict(g) for g in essential_genes[:50]],  # Top 50 essential
            'min_memory_kb': len(essential_genes) * 2,
            'min_cpu_percent': 15 if self.minimal_genome else 25,
            'boot_time_ms': 500 + len(essential_genes) * 2,
            'schema_version': self.schema_version
        }
    
    def _categorize_genes(self) -> Dict[str, int]:
        """Count genes by functional category."""
        categories = {}
        for gene in self.genes:
            category = gene.functional_category or 'other'
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _group_essential_by_function(self) -> Dict[str, List[Dict]]:
        """Group essential genes by function."""
        groups = {}
        for gene in self.get_essential_genes():
            category = gene.functional_category or 'other'
            if category not in groups:
                groups[category] = []
            groups[category].append({
                'id': gene.gene_id,
                'description': gene.description,
                'position': gene.start,
                'length': gene.length
            })
        return groups

class BioXenGenomeValidator:
    """Validates BioXen genome files and schemas."""
    
    def validate_genome(self, genome_data: str) -> tuple[bool, list]:
        """
        Validate genome data (string format).
        
        Args:
            genome_data: String containing genome sequence data
        
        Returns:
            tuple: (is_valid: bool, messages: list)
        """
        errors = []
        if not genome_data:
            errors.append("Genome data is empty.")
            return False, errors
        
        valid_bases = set('ATGC')
        if isinstance(genome_data, str):
            base_count = sum(1 for char in genome_data.upper() if char in valid_bases)
            total_chars = len(genome_data)
            if total_chars == 0:
                errors.append("Genome data has zero length.")
                return False, errors
            validity_ratio = base_count / total_chars
            if validity_ratio >= 0.8:
                return True, []
            else:
                errors.append(f"Only {validity_ratio*100:.1f}% of bases are valid DNA (ATGC). Minimum required: 80%.")
                return False, errors
        errors.append("Genome data is not a string.")
        return False, errors
    
    @staticmethod
    def validate_file(genome_path: Path) -> tuple[bool, List[str]]:
        """Validate a BioXen genome file."""
        errors = []
        
        if not genome_path.exists():
            return False, [f"File not found: {genome_path}"]
        
        try:
            with open(genome_path, 'r') as f:
                lines = f.readlines()
            
            gene_count = 0
            positions = []
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                try:
                    gene = BioXenGeneRecord.from_bioxen_line(line)
                    if not gene.validate():
                        errors.append(f"Line {line_num}: Invalid gene record {gene.gene_id}")
                    
                    # Check for overlaps (basic)
                    for pos in positions:
                        if not (gene.end < pos[0] or gene.start > pos[1]):
                            errors.append(f"Line {line_num}: Gene {gene.gene_id} overlaps with previous gene")
                    
                    positions.append((gene.start, gene.end))
                    gene_count += 1
                    
                except Exception as e:
                    errors.append(f"Line {line_num}: Parse error - {e}")
            
            if gene_count == 0:
                errors.append("No valid gene records found")
                
        except Exception as e:
            errors.append(f"File read error: {e}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_schema(schema: BioXenGenomeSchema) -> tuple[bool, List[str]]:
        """Validate a BioXen genome schema object."""
        errors = []
        
        if not schema.organism:
            errors.append("Missing organism name")
        
        if schema.genome_size <= 0:
            errors.append("Invalid genome size")
        
        if not schema.genes:
            errors.append("No genes defined")
        
        # Validate individual genes
        for i, gene in enumerate(schema.genes):
            if not gene.validate():
                errors.append(f"Gene {i}: Invalid record {gene.gene_id}")
        
        return len(errors) == 0, errors

# Schema specification for documentation
BIOXEN_GENOME_SCHEMA = {
    "name": "BioXen Genome Format",
    "version": "1.0",
    "description": "Standardized format for biological genomes compatible with BioXen virtualization",
    "file_extension": ".genome",
    "format": "tab-separated text",
    "fields": [
        {"name": "start", "type": "integer", "description": "1-based start position"},
        {"name": "length", "type": "integer", "description": "Gene length in base pairs"},
        {"name": "end", "type": "integer", "description": "1-based end position"},
        {"name": "strand", "type": "integer", "description": "+1 (forward), -1 (reverse), 0 (unknown)"},
        {"name": "gene_type", "type": "integer", "description": "1=protein, 0=RNA, 2=tRNA, 3=rRNA, 4=ncRNA, 5=pseudogene"},
        {"name": "gene_id", "type": "string", "description": "Unique gene identifier"},
        {"name": "description", "type": "string", "description": "Gene product/function description"}
    ],
    "optional_metadata": [
        "organism", "strain", "assembly_accession", "genome_size", "gc_content"
    ],
    "bioxen_extensions": [
        "essential", "functional_category", "vm_priority", "resource_weight"
    ]
}
