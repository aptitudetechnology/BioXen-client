"""
JCVI-Syn3A genome definitions and VM image builder

This module handles the minimal genome templates and builds
virtualized versions for use in the BioXen hypervisor.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import json

@dataclass
class Gene:
    """Represents a gene in the Syn3A genome"""
    gene_id: str
    name: str
    sequence: str
    function: str
    essential: bool
    category: str  # "transcription", "translation", "metabolism", etc.
    start_pos: int = 0
    end_pos: int = 0

@dataclass
class Syn3AGenome:
    """Complete Syn3A genome definition"""
    genome_id: str
    genes: List[Gene]
    total_size: int  # Total genome size in base pairs
    gc_content: float
    
    def get_essential_genes(self) -> List[Gene]:
        """Get all essential genes"""
        return [gene for gene in self.genes if gene.essential]
    
    def get_genes_by_category(self, category: str) -> List[Gene]:
        """Get genes by functional category"""
        return [gene for gene in self.genes if gene.category == category]

class Syn3ATemplate:
    """Syn3A genome template and manipulation"""
    
    def __init__(self):
        self.base_genome = self._create_minimal_genome()
        
    def _create_minimal_genome(self) -> Syn3AGenome:
        """Create the base Syn3A minimal genome"""
        
        # Essential genes for basic cellular functions
        # Note: This is a simplified representation
        essential_genes = [
            # DNA Replication
            Gene("MGAS_RS00005", "dnaA", 
                 "ATGAACACCCTGAAGCGCATCGACCTGAAACAGGCAATCACC", 
                 "Chromosomal replication initiator", True, "replication"),
            Gene("MGAS_RS00010", "dnaN",
                 "ATGAAAGCAATTTTCGTACTGAAAGGTTGGTGGCGCACTTCC",
                 "DNA polymerase sliding clamp", True, "replication"),
            Gene("MGAS_RS00015", "dnaG",
                 "ATGGGTACCCTGAAGCGCATCGACCTGAAACAGGCAATCACC",
                 "DNA primase", True, "replication"),
                 
            # Transcription
            Gene("MGAS_RS00020", "rpoA",
                 "ATGAAACGCATCGGCTACGTGCAGGCAATCACCAAGATCATC",
                 "RNA polymerase alpha subunit", True, "transcription"),
            Gene("MGAS_RS00025", "rpoB", 
                 "ATGCGTCGTCTGACCCTGAAACAGGCAATCACCAAGATCGTC",
                 "RNA polymerase beta subunit", True, "transcription"),
            Gene("MGAS_RS00030", "rpoC",
                 "ATGACCCTGAAGCGCATCGACCTGAAACAGGCAATCACCAAG",
                 "RNA polymerase beta' subunit", True, "transcription"),
                 
            # Translation  
            Gene("MGAS_RS00035", "rpsA",
                 "ATGACCAAGATCATCGACCTGAAACAGGCAATCACCAAGATC",
                 "30S ribosomal protein S1", True, "translation"),
            Gene("MGAS_RS00040", "rplA",
                 "ATGCAGGCAATCACCAAGATCATCGACCTGAAACAGGCAATC",
                 "50S ribosomal protein L1", True, "translation"),
            Gene("MGAS_RS00045", "infA",
                 "ATGACCAAGATCGTCGACCTGAAACAGGCAATCACCAAGATC",
                 "Translation initiation factor IF-1", True, "translation"),
                 
            # Metabolism
            Gene("MGAS_RS00050", "pgi",
                 "ATGAAGCGCATCGACCTGAAACAGGCAATCACCAAGATCGTC",
                 "Glucose-6-phosphate isomerase", True, "metabolism"),
            Gene("MGAS_RS00055", "pfk",
                 "ATGCTGAAACAGGCAATCACCAAGATCGTCGACCTGAAACAG",
                 "6-phosphofructokinase", True, "metabolism"),
            Gene("MGAS_RS00060", "eno",
                 "ATGGGCAATCACCAAGATCGTCGACCTGAAACAGGCAATCAC",
                 "Enolase", True, "metabolism"),
                 
            # tRNA synthesis
            Gene("MGAS_RS00065", "trpS",
                 "ATGACCAAGATCGTCGACCTGAAACAGGCAATCACCAAGATC",
                 "Tryptophanyl-tRNA synthetase", True, "translation"),
            Gene("MGAS_RS00070", "ileS",
                 "ATGAATCACCAAGATCGTCGACCTGAAACAGGCAATCACCAA",
                 "Isoleucyl-tRNA synthetase", True, "translation"),
        ]
        
        # Non-essential genes for enhanced function
        non_essential_genes = [
            Gene("MGAS_RS00200", "lacI",
                 "ATGACCCTGCGCATCGACCTGAAACAGGCAATCACCAAGATC",
                 "Lactose repressor", False, "regulation"),
            Gene("MGAS_RS00205", "malT", 
                 "ATGCACCAAGATCGTCGACCTGAAACAGGCAATCACCAAGAT",
                 "Maltose activator", False, "regulation"),
        ]
        
        all_genes = essential_genes + non_essential_genes
        
        # Calculate positions
        current_pos = 1
        for gene in all_genes:
            gene.start_pos = current_pos
            gene.end_pos = current_pos + len(gene.sequence) - 1
            current_pos = gene.end_pos + 100  # 100bp spacer
        
        return Syn3AGenome(
            genome_id="syn3a_minimal_v1.0",
            genes=all_genes,
            total_size=current_pos,
            gc_content=0.32  # Typical for Mycoplasma
        )
    
    def get_genome(self) -> Syn3AGenome:
        """Get the base Syn3A genome"""
        return self.base_genome

class VMImageBuilder:
    """Builds VM images from Syn3A genome templates"""
    
    def __init__(self):
        self.syn3a_template = Syn3ATemplate()
        
    def build_vm_image(self, vm_id: str, config: Dict) -> Dict[str, any]:
        """
        Build a VM image with hypervisor modifications
        
        Args:
            vm_id: Unique VM identifier
            config: VM configuration options
            
        Returns:
            VM image dictionary with modified genome
        """
        base_genome = self.syn3a_template.get_genome()
        
        # Clone the genome for modification
        vm_genome = self._clone_genome(base_genome, f"{vm_id}_genome")
        
        # Add VM-specific modifications
        self._add_vm_tags(vm_genome, vm_id)
        self._add_isolation_markers(vm_genome, vm_id)
        self._add_monitoring_genes(vm_genome, vm_id)
        
        # Apply resource constraints
        if "resource_limits" in config:
            self._apply_resource_limits(vm_genome, config["resource_limits"])
        
        # Create VM image
        vm_image = {
            "vm_id": vm_id,
            "genome": vm_genome,
            "config": config,
            "hypervisor_version": "bioxen-1.0",
            "creation_time": "2025-08-01T00:00:00Z",
            "compatibility": ["bioxen-1.0", "bioxen-1.1"],
            "resource_requirements": self._calculate_resource_requirements(vm_genome)
        }
        
        return vm_image
    
    def _clone_genome(self, source: Syn3AGenome, new_id: str) -> Syn3AGenome:
        """Create a copy of the genome for modification"""
        cloned_genes = []
        for gene in source.genes:
            cloned_gene = Gene(
                gene_id=gene.gene_id,
                name=gene.name,
                sequence=gene.sequence,
                function=gene.function,
                essential=gene.essential,
                category=gene.category,
                start_pos=gene.start_pos,
                end_pos=gene.end_pos
            )
            cloned_genes.append(cloned_gene)
            
        return Syn3AGenome(
            genome_id=new_id,
            genes=cloned_genes,
            total_size=source.total_size,
            gc_content=source.gc_content
        )
    
    def _add_vm_tags(self, genome: Syn3AGenome, vm_id: str) -> None:
        """Add VM-specific protein tags to all genes"""
        try:
            from ..genetics.circuits import ProteinTagging
        except ImportError:
            # Fallback for direct execution
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from genetics.circuits import ProteinTagging
        
        tagger = ProteinTagging()
        tag_sequence = tagger.get_protein_tag(vm_id)
        
        # Add tags to all protein-coding genes
        for gene in genome.genes:
            if gene.category in ["transcription", "translation", "metabolism"]:
                # Insert tag sequence after start codon
                if gene.sequence.startswith("ATG"):
                    # Convert tag to DNA sequence (simplified)
                    tag_dna = self._protein_to_dna(tag_sequence)
                    gene.sequence = "ATG" + tag_dna + gene.sequence[3:]
    
    def _add_isolation_markers(self, genome: Syn3AGenome, vm_id: str) -> None:
        """Add genetic markers for VM isolation"""
        
        # Add VM identifier gene
        vm_marker = Gene(
            gene_id=f"{vm_id}_marker",
            name=f"vmid_{vm_id}",
            sequence="ATGAAACGCATTGGCTACGTGCAGGCAATCACCAAGATCTAA",
            function=f"VM identifier for {vm_id}",
            essential=False,
            category="hypervisor"
        )
        
        genome.genes.append(vm_marker)
        genome.total_size += len(vm_marker.sequence) + 100
    
    def _add_monitoring_genes(self, genome: Syn3AGenome, vm_id: str) -> None:
        """Add genes for hypervisor monitoring"""
        
        # Health reporter gene
        health_reporter = Gene(
            gene_id=f"{vm_id}_health",
            name="health_reporter",
            sequence="ATGGTGAGCAAGGGCGAGGAGCTGTTCACCGGGGTGGTG",  # GFP-like
            function="Health status reporter",
            essential=False,
            category="hypervisor"
        )
        
        # Resource usage reporter
        resource_reporter = Gene(
            gene_id=f"{vm_id}_resources", 
            name="resource_reporter",
            sequence="ATGGTGAGCAAGGGCGAGGAGCTGTTCACCGGGGTGCTG",  # RFP-like
            function="Resource usage reporter",
            essential=False,
            category="hypervisor"
        )
        
        genome.genes.extend([health_reporter, resource_reporter])
        genome.total_size += len(health_reporter.sequence) + len(resource_reporter.sequence) + 200
    
    def _apply_resource_limits(self, genome: Syn3AGenome, limits: Dict) -> None:
        """Apply resource limitations to the genome"""
        
        # Reduce ribosome genes if limited
        if "max_ribosomes" in limits:
            max_ribosomes = limits["max_ribosomes"]
            # Find ribosomal protein genes and potentially remove some
            ribosomal_genes = [g for g in genome.genes if "rps" in g.name or "rpl" in g.name]
            if len(ribosomal_genes) > max_ribosomes:
                # Remove non-essential ribosomal genes
                for gene in ribosomal_genes[max_ribosomes:]:
                    if not gene.essential:
                        genome.genes.remove(gene)
    
    def _calculate_resource_requirements(self, genome: Syn3AGenome) -> Dict[str, int]:
        """Calculate minimum resource requirements for the VM"""
        
        essential_genes = genome.get_essential_genes()
        
        return {
            "min_ribosomes": len([g for g in essential_genes if g.category == "translation"]),
            "min_atp_percentage": 15.0,  # Minimum ATP allocation
            "min_memory_kb": len(essential_genes) * 2,  # 2KB per essential gene
            "min_rna_polymerase": 3  # Minimum RNA polymerase molecules
        }
    
    def _protein_to_dna(self, protein_seq: str) -> str:
        """Convert protein sequence to DNA (simplified codon usage)"""
        codon_table = {
            'M': 'ATG', 'H': 'CAC', 'G': 'GGC', 'S': 'AGC',
            'Y': 'TAC', 'P': 'CCC', 'D': 'GAC', 'V': 'GTC',
            'A': 'GCC', 'L': 'CTC', 'F': 'TTC', 'N': 'AAC',
            'E': 'GAG', 'T': 'ACC', 'K': 'AAG', 'R': 'CGC'
        }
        
        dna_seq = ""
        for aa in protein_seq:
            dna_seq += codon_table.get(aa, 'NNN')  # NNN for unknown
            
        return dna_seq
    
    def save_vm_image(self, vm_image: Dict, filepath: str) -> None:
        """Save VM image to file"""
        
        # Convert to serializable format
        serializable_image = {
            "vm_id": vm_image["vm_id"],
            "genome_id": vm_image["genome"].genome_id,
            "genes": [
                {
                    "gene_id": gene.gene_id,
                    "name": gene.name,
                    "sequence": gene.sequence,
                    "function": gene.function,
                    "essential": gene.essential,
                    "category": gene.category,
                    "start_pos": gene.start_pos,
                    "end_pos": gene.end_pos
                }
                for gene in vm_image["genome"].genes
            ],
            "total_size": vm_image["genome"].total_size,
            "gc_content": vm_image["genome"].gc_content,
            "config": vm_image["config"],
            "hypervisor_version": vm_image["hypervisor_version"],
            "creation_time": vm_image["creation_time"],
            "compatibility": vm_image["compatibility"],
            "resource_requirements": vm_image["resource_requirements"]
        }
        
        with open(filepath, 'w') as f:
            json.dump(serializable_image, f, indent=2)
    
    def load_vm_image(self, filepath: str) -> Dict[str, any]:
        """Load VM image from file"""
        
        with open(filepath, 'r') as f:
            image_data = json.load(f)
        
        # Reconstruct genome object
        genes = []
        for gene_data in image_data["genes"]:
            gene = Gene(
                gene_id=gene_data["gene_id"],
                name=gene_data["name"],
                sequence=gene_data["sequence"],
                function=gene_data["function"],
                essential=gene_data["essential"],
                category=gene_data["category"],
                start_pos=gene_data["start_pos"],
                end_pos=gene_data["end_pos"]
            )
            genes.append(gene)
        
        genome = Syn3AGenome(
            genome_id=image_data["genome_id"],
            genes=genes,
            total_size=image_data["total_size"],
            gc_content=image_data["gc_content"]
        )
        
        return {
            "vm_id": image_data["vm_id"],
            "genome": genome,
            "config": image_data["config"],
            "hypervisor_version": image_data["hypervisor_version"],
            "creation_time": image_data["creation_time"],
            "compatibility": image_data["compatibility"],
            "resource_requirements": image_data["resource_requirements"]
        }
