"""
BioXen Genome Format Converter

Converts standard genome formats (GFF3, GenBank, FASTA) to BioXen .genome format.
Handles NCBI downloads and other common genome sources.
"""

import re
import gzip
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

from .schema import BioXenGenomeSchema, BioXenGeneRecord, GeneType, Strand

@dataclass
class GenomeSource:
    """Information about the source of genome data."""
    fasta_file: Optional[Path] = None
    gff_file: Optional[Path] = None
    genbank_file: Optional[Path] = None
    organism: str = ""
    strain: str = ""
    assembly_accession: str = ""

class BioXenGenomeConverter:
    """
    Convert various genome formats to BioXen .genome format.
    
    Supports:
    - GFF3 + FASTA (from NCBI downloads)
    - GenBank files
    - Custom annotation formats
    """
    
    def __init__(self):
        self.essential_gene_keywords = [
            # Core cellular processes
            'ribosomal', 'ribosome', 'rRNA', 'tRNA', 'elongation factor',
            'DNA polymerase', 'RNA polymerase', 'DNA gyrase', 'helicase',
            'ATP synthase', 'ATPase', 'translation', 'transcription',
            'replication', 'aminoacyl', 'ligase', 'synthetase',
            
            # Minimal genome essentials (from Syn3A studies)
            'DnaA', 'DnaB', 'DnaG', 'DnaE', 'DnaQ', 'DnaN',  # DNA replication
            'RpoA', 'RpoB', 'RpoC', 'RpoZ',  # RNA polymerase
            'EF-Tu', 'EF-G', 'IF-1', 'IF-2', 'IF-3',  # Translation factors
            'FtsZ', 'MinD', 'MinE',  # Cell division
            'SecA', 'SecY', 'SecE',  # Protein transport
            'ClpP', 'ClpX', 'HslV',  # Protein degradation
        ]
        
        self.functional_categories = {
            'protein_synthesis': ['ribosomal', 'ribosome', 'rrna', 'elongation factor', 'translation'],
            'dna_replication': ['dna polymerase', 'replication', 'helicase', 'dnaa', 'dnab', 'dnag'],
            'transcription': ['rna polymerase', 'transcription', 'rpoa', 'rpob', 'rpoc'],
            'energy_metabolism': ['atp synthase', 'atpase', 'kinase', 'phosphate'],
            'translation': ['trna', 'aminoacyl', 'ligase', 'synthetase', 'ef-tu', 'ef-g'],
            'cell_division': ['ftsz', 'mind', 'mine', 'cell division'],
            'transport': ['transport', 'abc', 'permease', 'seca', 'secy'],
            'metabolism': ['transferase', 'hydrolase', 'oxidase', 'dehydrogenase'],
            'protein_folding': ['clpp', 'clpx', 'hslv', 'chaperone', 'dnak']
        }
    
    def convert_ncbi_download(self, download_dir: Path, organism_name: str) -> BioXenGenomeSchema:
        """
        Convert NCBI genome download to BioXen format.
        
        Expected structure from ncbi-genome-download:
        download_dir/
        ├── organism_assembly.fna.gz (genome FASTA)
        ├── organism_assembly.gff.gz (annotations)
        └── organism_assembly_feature_table.txt.gz
        """
        
        # Find files in download directory
        fasta_files = list(download_dir.glob("*.fna.gz")) + list(download_dir.glob("*.fna"))
        gff_files = list(download_dir.glob("*.gff.gz")) + list(download_dir.glob("*.gff"))
        
        if not fasta_files or not gff_files:
            raise FileNotFoundError(f"Could not find FASTA and GFF files in {download_dir}")
        
        fasta_file = fasta_files[0]
        gff_file = gff_files[0]
        
        print(f"Converting {organism_name} from NCBI download...")
        print(f"  FASTA: {fasta_file.name}")
        print(f"  GFF: {gff_file.name}")
        
        # Extract assembly info from filename
        assembly_accession = self._extract_assembly_from_filename(fasta_file.name)
        
        source = GenomeSource(
            fasta_file=fasta_file,
            gff_file=gff_file,
            organism=organism_name,
            assembly_accession=assembly_accession
        )
        
        return self.convert_from_source(source)
    
    def convert_from_source(self, source: GenomeSource) -> BioXenGenomeSchema:
        """Convert from a GenomeSource specification."""
        
        # Get genome size from FASTA
        genome_size = 0
        gc_content = 0.0
        if source.fasta_file:
            genome_size, gc_content = self._parse_fasta_stats(source.fasta_file)
        
        # Parse genes from GFF
        genes = []
        if source.gff_file:
            genes = self._parse_gff3(source.gff_file)
        elif source.genbank_file:
            genes = self._parse_genbank(source.genbank_file)
        
        # Create schema
        schema = BioXenGenomeSchema(
            organism=source.organism,
            strain=source.strain,
            assembly_accession=source.assembly_accession,
            genome_size=genome_size,
            gc_content=gc_content,
            genes=genes
        )
        
        # Annotate with BioXen-specific information
        self._annotate_essential_genes(schema)
        self._categorize_genes(schema)
        
        return schema
    
    def _parse_fasta_stats(self, fasta_file: Path) -> Tuple[int, float]:
        """Parse FASTA file to get genome size and GC content."""
        total_length = 0
        gc_count = 0
        
        open_func = gzip.open if fasta_file.suffix == '.gz' else open
        mode = 'rt' if fasta_file.suffix == '.gz' else 'r'
        
        with open_func(fasta_file, mode) as f:
            for line in f:
                if line.startswith('>'):
                    continue
                sequence = line.strip().upper()
                total_length += len(sequence)
                gc_count += sequence.count('G') + sequence.count('C')
        
        gc_content = (gc_count / total_length * 100) if total_length > 0 else 0.0
        return total_length, gc_content
    
    def _parse_gff3(self, gff_file: Path) -> List[BioXenGeneRecord]:
        """Parse GFF3 file to extract gene records."""
        genes = []
        
        open_func = gzip.open if gff_file.suffix == '.gz' else open
        mode = 'rt' if gff_file.suffix == '.gz' else 'r'
        
        with open_func(gff_file, mode) as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                
                parts = line.strip().split('\t')
                if len(parts) < 9:
                    continue
                
                # Parse GFF3 fields
                seqname = parts[0]
                source = parts[1]
                feature_type = parts[2]
                start = int(parts[3])
                end = int(parts[4])
                score = parts[5]
                strand_str = parts[6]
                phase = parts[7]
                attributes = parts[8]
                
                # Only process genes and CDS
                if feature_type not in ['gene', 'CDS', 'tRNA', 'rRNA', 'ncRNA']:
                    continue
                
                # Parse attributes
                attr_dict = self._parse_gff3_attributes(attributes)
                
                # Extract gene information
                gene_id = attr_dict.get('ID', attr_dict.get('locus_tag', attr_dict.get('Name', f"gene_{start}")))
                description = attr_dict.get('product', attr_dict.get('function', attr_dict.get('Note', 'Unknown function')))
                locus_tag = attr_dict.get('locus_tag')
                gene_name = attr_dict.get('gene')
                protein_id = attr_dict.get('protein_id')
                
                # Determine gene type
                gene_type = self._determine_gene_type(feature_type, description)
                
                # Convert strand
                strand = 1 if strand_str == '+' else -1 if strand_str == '-' else 0
                
                # Calculate length
                length = abs(end - start) + 1
                
                gene = BioXenGeneRecord(
                    start=start,
                    length=length,
                    end=end,
                    strand=strand,
                    gene_type=gene_type,
                    gene_id=gene_id,
                    description=description,
                    locus_tag=locus_tag,
                    gene_name=gene_name,
                    protein_id=protein_id
                )
                
                genes.append(gene)
        
        return genes
    
    def _parse_gff3_attributes(self, attributes: str) -> Dict[str, str]:
        """Parse GFF3 attributes field."""
        attr_dict = {}
        
        for attr in attributes.split(';'):
            if '=' in attr:
                key, value = attr.split('=', 1)
                attr_dict[key] = value.replace('%20', ' ').replace('%2C', ',')
        
        return attr_dict
    
    def _determine_gene_type(self, feature_type: str, description: str) -> int:
        """Determine BioXen gene type from GFF3 feature type and description."""
        feature_type = feature_type.lower()
        description = description.lower()
        
        if feature_type in ['trna']:
            return GeneType.TRNA.value
        elif feature_type in ['rrna']:
            return GeneType.RRNA.value
        elif feature_type in ['ncrna']:
            return GeneType.NCRNA.value
        elif 'trna' in description:
            return GeneType.TRNA.value
        elif 'rrna' in description or 'ribosomal rna' in description:
            return GeneType.RRNA.value
        elif feature_type in ['gene', 'cds'] and ('protein' in description or 'enzyme' in description):
            return GeneType.PROTEIN_CODING.value
        elif feature_type in ['gene', 'cds']:
            return GeneType.PROTEIN_CODING.value  # Default for genes
        else:
            return GeneType.RNA_GENE.value
    
    def _annotate_essential_genes(self, schema: BioXenGenomeSchema):
        """Annotate genes as essential based on known patterns."""
        for gene in schema.genes:
            gene.essential = self._is_essential_gene(gene.description, gene.gene_name)
    
    def _is_essential_gene(self, description: str, gene_name: Optional[str] = None) -> bool:
        """Determine if a gene is essential based on description and name."""
        text = (description + ' ' + (gene_name or '')).lower()
        
        return any(keyword.lower() in text for keyword in self.essential_gene_keywords)
    
    def _categorize_genes(self, schema: BioXenGenomeSchema):
        """Categorize genes by function."""
        for gene in schema.genes:
            gene.functional_category = self._get_functional_category(gene.description)
    
    def _get_functional_category(self, description: str) -> str:
        """Get functional category for a gene."""
        desc_lower = description.lower()
        
        for category, keywords in self.functional_categories.items():
            if any(keyword in desc_lower for keyword in keywords):
                return category
        
        return 'other'
    
    def _extract_assembly_from_filename(self, filename: str) -> str:
        """Extract assembly accession from NCBI filename."""
        # Pattern: organism_GCF_123456789.1_ASM123v1_genomic.fna.gz
        match = re.search(r'(GCF_\d+\.\d+)', filename)
        return match.group(1) if match else ""
    
    def _parse_genbank(self, genbank_file: Path) -> List[BioXenGeneRecord]:
        """Parse GenBank file (basic implementation)."""
        # This would be a more complex parser for GenBank format
        # For now, raise NotImplementedError
        raise NotImplementedError("GenBank parsing not yet implemented. Use GFF3 + FASTA instead.")

def convert_ncbi_bacteria_download(download_dir: Path, organism_name: str, output_dir: Path):
    """
    High-level function to convert NCBI bacterial genome download.
    
    Usage:
        # After running: ncbi-genome-download bacteria --assembly-level complete
        convert_ncbi_bacteria_download(
            Path("ncbi_downloads/bacteria/Mycoplasma_genitalium"),
            "Mycoplasma genitalium",
            Path("genomes/")
        )
    """
    converter = BioXenGenomeConverter()
    
    try:
        # Convert to BioXen schema
        schema = converter.convert_ncbi_download(download_dir, organism_name)
        
        # Generate output filenames
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', organism_name.replace(' ', '_'))
        bioxen_file = output_dir / f"{safe_name}.genome"
        json_file = output_dir / f"{safe_name}.json"
        
        # Export in both formats
        output_dir.mkdir(parents=True, exist_ok=True)
        schema.export_bioxen_format(bioxen_file)
        schema.export_json_format(json_file)
        
        print(f"\n✅ Conversion successful!")
        print(f"📊 Genome: {schema.organism}")
        print(f"   Size: {schema.genome_size:,} bp")
        print(f"   Genes: {schema.total_genes}")
        print(f"   Essential: {schema.essential_genes}")
        print(f"   GC content: {schema.gc_content:.1f}%")
        print(f"📁 Output files:")
        print(f"   BioXen format: {bioxen_file}")
        print(f"   JSON metadata: {json_file}")
        
        return schema
        
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        raise

# CLI integration example
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: python -m bioxen.genome.converter <download_dir> <organism_name> <output_dir>")
        sys.exit(1)
    
    download_dir = Path(sys.argv[1])
    organism_name = sys.argv[2]
    output_dir = Path(sys.argv[3])
    
    convert_ncbi_bacteria_download(download_dir, organism_name, output_dir)
