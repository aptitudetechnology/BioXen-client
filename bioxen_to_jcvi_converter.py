#!/usr/bin/env python3
"""
BioXen to JCVI Format Converter

Converts BioXen's custom .genome format to JCVI-compatible FASTA format.
The original .genome format contains tab-separated gene annotation data,
but JCVI tools expect FASTA sequences.

This converter:
1. Reads BioXen .genome annotation files
2. Generates synthetic DNA sequences for each gene
3. Creates JCVI-compatible FASTA files
4. Maintains gene metadata in compatible format
"""

import os
import sys
import argparse
from pathlib import Path

class BioXenToJCVIConverter:
    """Convert BioXen genome format to JCVI-compatible FASTA"""
    
    def __init__(self):
        self.codon_table = {
            'A': 'GCT', 'R': 'CGT', 'N': 'AAT', 'D': 'GAT', 'C': 'TGT',
            'Q': 'CAG', 'E': 'GAG', 'G': 'GGT', 'H': 'CAT', 'I': 'ATT',
            'L': 'CTG', 'K': 'AAG', 'M': 'ATG', 'F': 'TTT', 'P': 'CCT',
            'S': 'TCT', 'T': 'ACT', 'W': 'TGG', 'Y': 'TAT', 'V': 'GTT',
            '*': 'TAG'  # Stop codon
        }
    
    def read_bioxen_genome(self, genome_path):
        """Read BioXen .genome file and parse gene annotations"""
        genes = []
        
        if not os.path.exists(genome_path):
            print(f"❌ Error: Genome file not found: {genome_path}")
            return genes
            
        try:
            with open(genome_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse BioXen format: start length end strand type gene_id description
                    parts = line.split(None, 6)  # Split on whitespace, max 7 parts
                    
                    if len(parts) < 6:
                        print(f"⚠️  Warning: Line {line_num} has insufficient columns, skipping")
                        continue
                    
                    try:
                        start = int(parts[0])
                        length = int(parts[1]) 
                        end = int(parts[2])
                        strand = int(parts[3])
                        gene_type = int(parts[4])
                        gene_id = parts[5]
                        description = parts[6] if len(parts) > 6 else "Hypothetical protein"
                        
                        genes.append({
                            'start': start,
                            'length': length,
                            'end': end,
                            'strand': strand,
                            'type': gene_type,
                            'id': gene_id,
                            'description': description
                        })
                        
                    except ValueError as e:
                        print(f"⚠️  Warning: Line {line_num} has invalid numeric values: {e}")
                        continue
                        
        except Exception as e:
            print(f"❌ Error reading genome file: {e}")
            return []
            
        print(f"✅ Parsed {len(genes)} genes from {genome_path}")
        return genes
    
    def generate_synthetic_sequence(self, gene_info):
        """Generate a synthetic DNA sequence for a gene"""
        length = gene_info['length']
        gene_type = gene_info['type']
        
        # Generate different sequences based on gene type
        if gene_type == 0:  # RNA genes
            return self._generate_rna_sequence(length)
        elif gene_type == 1:  # Protein-coding genes  
            return self._generate_protein_coding_sequence(length)
        else:  # Other types (tRNA, rRNA, etc.)
            return self._generate_functional_rna_sequence(length, gene_type)
    
    def _generate_protein_coding_sequence(self, length):
        """Generate a protein-coding DNA sequence"""
        # Ensure length is divisible by 3 for codons
        coding_length = (length // 3) * 3
        
        # Start with start codon
        sequence = "ATG"
        
        # Generate random codons for the middle
        import random
        amino_acids = "ARNDCQEGHILKMFPSTWYVK"  # Common amino acids
        
        for _ in range((coding_length - 6) // 3):  # -6 for start and stop codons
            aa = random.choice(amino_acids)
            sequence += self.codon_table[aa]
        
        # Add stop codon
        sequence += "TAG"
        
        # Pad to desired length if needed
        while len(sequence) < length:
            sequence += random.choice("ATGC")
            
        return sequence[:length]  # Trim to exact length
    
    def _generate_rna_sequence(self, length):
        """Generate an RNA gene sequence"""
        import random
        # RNA genes often have more AT content
        bases = "AATTGGCC"  # Biased toward AT
        return ''.join(random.choice(bases) for _ in range(length))
    
    def _generate_functional_rna_sequence(self, length, gene_type):
        """Generate sequences for tRNA, rRNA, etc."""
        import random
        
        if gene_type == 2:  # tRNA - more structured
            # tRNA sequences have characteristic structure
            bases = "ATGCATGC"  # More balanced
        elif gene_type == 3:  # rRNA - GC rich
            bases = "GGCCGGCC"  # GC rich
        else:  # Other functional RNAs
            bases = "ATGC"
            
        return ''.join(random.choice(bases) for _ in range(length))
    
    def convert_to_fasta(self, genes, output_path, organism_name="BioXen_Genome"):
        """Convert genes to FASTA format"""
        
        try:
            with open(output_path, 'w') as f:
                for i, gene in enumerate(genes):
                    # Create FASTA header
                    header = f">{gene['id']}_{i+1:03d} {gene['description'][:50]}"
                    if gene['strand'] == -1:
                        header += " [reverse]"
                    header += f" len={gene['length']} type={gene['type']}"
                    
                    # Generate synthetic sequence
                    sequence = self.generate_synthetic_sequence(gene)
                    
                    # Write to file
                    f.write(header + "\n")
                    
                    # Write sequence in 80-character lines (FASTA standard)
                    for j in range(0, len(sequence), 80):
                        f.write(sequence[j:j+80] + "\n")
                        
            print(f"✅ Created FASTA file: {output_path}")
            print(f"   📊 {len(genes)} sequences, {sum(g['length'] for g in genes):,} total bases")
            return True
            
        except Exception as e:
            print(f"❌ Error writing FASTA file: {e}")
            return False
    
    def convert_genome(self, input_path, output_path=None):
        """Main conversion function"""
        
        # Determine output path
        if output_path is None:
            input_path_obj = Path(input_path)
            output_path = input_path_obj.with_suffix('.fasta')
        
        print(f"🔄 Converting {input_path} to JCVI-compatible FASTA...")
        
        # Read BioXen genome
        genes = self.read_bioxen_genome(input_path)
        if not genes:
            return False
        
        # Extract organism name from filename
        organism_name = Path(input_path).stem
        
        # Convert to FASTA
        success = self.convert_to_fasta(genes, output_path, organism_name)
        
        if success:
            print(f"🎉 Conversion successful!")
            print(f"   📁 Input:  {input_path}")
            print(f"   📁 Output: {output_path}")
            return True
        else:
            return False

def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description="Convert BioXen .genome files to JCVI-compatible FASTA format"
    )
    parser.add_argument(
        'input', 
        nargs='?',  # Make input optional when using --batch
        help='Input .genome file path'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output FASTA file path (default: input.fasta)'
    )
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Convert all .genome files in genomes/ directory'
    )
    
    args = parser.parse_args()
    
    converter = BioXenToJCVIConverter()
    
    if args.batch:
        print("🔄 Batch conversion mode: converting all .genome files...")
        genomes_dir = Path("genomes")
        
        if not genomes_dir.exists():
            print("❌ Error: genomes/ directory not found")
            return 1
        
        genome_files = list(genomes_dir.glob("*.genome"))
        if not genome_files:
            print("❌ Error: No .genome files found in genomes/ directory")
            return 1
        
        success_count = 0
        for genome_file in genome_files:
            print(f"\n📄 Processing {genome_file.name}...")
            if converter.convert_genome(str(genome_file)):
                success_count += 1
        
        print(f"\n🎉 Batch conversion complete: {success_count}/{len(genome_files)} files converted")
        return 0 if success_count == len(genome_files) else 1
    
    else:
        # Single file conversion - require input argument
        if not args.input:
            print("❌ Error: Input file required for single file conversion")
            print("   Use --batch to convert all .genome files in genomes/ directory")
            parser.print_help()
            return 1
            
        if converter.convert_genome(args.input, args.output):
            return 0
        else:
            return 1

if __name__ == "__main__":
    sys.exit(main())
