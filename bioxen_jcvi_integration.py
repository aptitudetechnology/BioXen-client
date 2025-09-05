#!/usr/bin/env python3
"""
BioXen-JCVI Integration Module

This module provides seamless integration between BioXen and JCVI tools,
implementing the "graceful enhancement pattern" where JCVI features are
available when possible, with automatic fallback to BioXen's original
functionality when JCVI is not available.
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

# Import the converter
from bioxen_to_jcvi_converter import BioXenToJCVIConverter

class BioXenJCVIIntegration:
    """Main integration class for BioXen-JCVI functionality"""
    
    def __init__(self):
        self.jcvi_available = self._check_jcvi_availability()
        self.converter = BioXenToJCVIConverter()
        self._init_status()
    
    def _check_jcvi_availability(self) -> bool:
        """Check if JCVI is available for use"""
        try:
            import jcvi
            return True
        except ImportError:
            return False
    
    def _init_status(self):
        """Initialize integration status"""
        if self.jcvi_available:
            print("🧬 BioXen-JCVI Integration: JCVI features available")
        else:
            print("🧬 BioXen-JCVI Integration: Running in fallback mode (JCVI not available)")
    
    def ensure_fasta_format(self, genome_path: str) -> Optional[str]:
        """
        Ensure a genome file is in FASTA format for JCVI compatibility.
        
        Args:
            genome_path: Path to genome file (.genome or .fasta)
            
        Returns:
            Path to FASTA file, or None if conversion failed
        """
        if genome_path.endswith('.fasta'):
            return genome_path if os.path.exists(genome_path) else None
        
        if genome_path.endswith('.genome'):
            fasta_path = genome_path.replace('.genome', '.fasta')
            
            # Check if FASTA version already exists
            if os.path.exists(fasta_path):
                return fasta_path
            
            # Convert if needed
            print(f"🔄 Converting {os.path.basename(genome_path)} to FASTA for JCVI compatibility...")
            success = self.converter.convert_genome(genome_path, fasta_path)
            return fasta_path if success else None
        
        return None
    
    def get_genome_statistics(self, genome_path: str) -> Dict[str, Any]:
        """
        Get enhanced genome statistics using JCVI if available,
        fallback to basic statistics otherwise.
        
        Args:
            genome_path: Path to genome file
            
        Returns:
            Dictionary with genome statistics
        """
        stats = {
            'source': 'BioXen (fallback)',
            'jcvi_enhanced': False
        }
        
        if self.jcvi_available:
            fasta_path = self.ensure_fasta_format(genome_path)
            if fasta_path:
                jcvi_stats = self._get_jcvi_statistics(fasta_path)
                if jcvi_stats:
                    stats.update(jcvi_stats)
                    stats['source'] = 'JCVI (enhanced)'
                    stats['jcvi_enhanced'] = True
                    return stats
        
        # Fallback to basic BioXen statistics
        basic_stats = self._get_basic_statistics(genome_path)
        stats.update(basic_stats)
        return stats
    
    def _get_jcvi_statistics(self, fasta_path: str) -> Optional[Dict[str, Any]]:
        """Get statistics using JCVI tools"""
        try:
            result = subprocess.run([
                sys.executable, "-m", "jcvi.formats.fasta", "summary", fasta_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return self._parse_jcvi_output(result.stdout)
            else:
                return None
                
        except Exception:
            return None
    
    def _parse_jcvi_output(self, output: str) -> Dict[str, Any]:
        """Parse JCVI summary output"""
        lines = output.strip().split('\n')
        
        total_sequences = 0
        total_bases = 0
        sequence_lengths = []
        
        for line in lines:
            if line.strip() and not line.startswith('Seqid'):
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        # Parse sequence length (remove commas)
                        length_str = parts[3].replace(',', '')
                        length = int(length_str)
                        sequence_lengths.append(length)
                        total_sequences += 1
                        total_bases += length
                    except (ValueError, IndexError):
                        continue
        
        if sequence_lengths:
            return {
                'total_sequences': total_sequences,
                'total_bases': total_bases,
                'average_length': total_bases / total_sequences,
                'min_length': min(sequence_lengths),
                'max_length': max(sequence_lengths),
                'sequence_lengths': sequence_lengths
            }
        else:
            return {}
    
    def _get_basic_statistics(self, genome_path: str) -> Dict[str, Any]:
        """Get basic statistics from BioXen format"""
        if genome_path.endswith('.genome'):
            return self._parse_genome_file(genome_path)
        else:
            return self._parse_fasta_file_basic(genome_path)
    
    def _parse_genome_file(self, genome_path: str) -> Dict[str, Any]:
        """Parse BioXen .genome file for basic statistics"""
        genes = self.converter.read_bioxen_genome(genome_path)
        
        if not genes:
            return {}
        
        lengths = [gene['length'] for gene in genes]
        total_bases = sum(lengths)
        
        return {
            'total_sequences': len(genes),
            'total_bases': total_bases,
            'average_length': total_bases / len(genes),
            'min_length': min(lengths),
            'max_length': max(lengths)
        }
    
    def _parse_fasta_file_basic(self, fasta_path: str) -> Dict[str, Any]:
        """Basic FASTA parsing without JCVI"""
        sequences = []
        current_seq = ""
        
        try:
            with open(fasta_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('>'):
                        if current_seq:
                            sequences.append(len(current_seq))
                            current_seq = ""
                    else:
                        current_seq += line
                
                # Don't forget the last sequence
                if current_seq:
                    sequences.append(len(current_seq))
            
            if sequences:
                total_bases = sum(sequences)
                return {
                    'total_sequences': len(sequences),
                    'total_bases': total_bases,
                    'average_length': total_bases / len(sequences),
                    'min_length': min(sequences),
                    'max_length': max(sequences)
                }
            else:
                return {}
                
        except Exception:
            return {}
    
    def compare_genomes(self, genome1_path: str, genome2_path: str) -> Dict[str, Any]:
        """
        Compare two genomes using JCVI if available,
        fallback to basic comparison otherwise.
        """
        comparison = {
            'genome1': os.path.basename(genome1_path),
            'genome2': os.path.basename(genome2_path),
            'jcvi_enhanced': False
        }
        
        if self.jcvi_available:
            # Try JCVI-enhanced comparison
            fasta1 = self.ensure_fasta_format(genome1_path)
            fasta2 = self.ensure_fasta_format(genome2_path)
            
            if fasta1 and fasta2:
                jcvi_comparison = self._compare_with_jcvi(fasta1, fasta2)
                if jcvi_comparison:
                    comparison.update(jcvi_comparison)
                    comparison['jcvi_enhanced'] = True
                    return comparison
        
        # Fallback to basic comparison
        stats1 = self.get_genome_statistics(genome1_path)
        stats2 = self.get_genome_statistics(genome2_path)
        
        comparison.update({
            'genome1_stats': stats1,
            'genome2_stats': stats2,
            'size_ratio': stats2.get('total_bases', 0) / max(stats1.get('total_bases', 1), 1),
            'gene_count_ratio': stats2.get('total_sequences', 0) / max(stats1.get('total_sequences', 1), 1)
        })
        
        return comparison
    
    def _compare_with_jcvi(self, fasta1: str, fasta2: str) -> Optional[Dict[str, Any]]:
        """Perform JCVI-enhanced genome comparison"""
        # For now, return enhanced statistics comparison
        # Future versions could include synteny analysis
        
        stats1 = self._get_jcvi_statistics(fasta1)
        stats2 = self._get_jcvi_statistics(fasta2)
        
        if stats1 and stats2:
            return {
                'genome1_stats': stats1,
                'genome2_stats': stats2,
                'size_ratio': stats2['total_bases'] / max(stats1['total_bases'], 1),
                'gene_count_ratio': stats2['total_sequences'] / max(stats1['total_sequences'], 1),
                'avg_length_ratio': stats2['average_length'] / max(stats1['average_length'], 1)
            }
        
        return None
    
    def is_jcvi_available(self) -> bool:
        """Check if JCVI features are available"""
        return self.jcvi_available
    
    def get_capabilities(self) -> List[str]:
        """Get list of available capabilities"""
        capabilities = [
            "Basic genome statistics",
            "Format conversion (.genome to .fasta)",
            "Basic genome comparison"
        ]
        
        if self.jcvi_available:
            capabilities.extend([
                "Enhanced JCVI genome statistics",
                "Professional sequence analysis",
                "Advanced genome comparison",
                "JCVI tool integration"
            ])
        
        return capabilities

# Convenience functions for easy integration
def get_enhanced_genome_stats(genome_path: str) -> Dict[str, Any]:
    """Convenience function to get enhanced genome statistics"""
    integration = BioXenJCVIIntegration()
    return integration.get_genome_statistics(genome_path)

def compare_genomes_enhanced(genome1: str, genome2: str) -> Dict[str, Any]:
    """Convenience function to compare genomes with enhancement"""
    integration = BioXenJCVIIntegration()
    return integration.compare_genomes(genome1, genome2)

def ensure_jcvi_compatible(genome_path: str) -> Optional[str]:
    """Convenience function to ensure JCVI compatibility"""
    integration = BioXenJCVIIntegration()
    return integration.ensure_fasta_format(genome_path)

# Demo function
def demo_integration():
    """Demonstrate the integration capabilities"""
    print("🧬 BioXen-JCVI Integration Demo")
    print("=" * 40)
    
    integration = BioXenJCVIIntegration()
    
    print(f"\n📋 Available capabilities:")
    for cap in integration.get_capabilities():
        print(f"   • {cap}")
    
    # Test with syn3A genome if available
    genome_path = "genomes/syn3A.genome"
    if os.path.exists(genome_path):
        print(f"\n📊 Testing with {genome_path}:")
        stats = integration.get_genome_statistics(genome_path)
        
        print(f"   Source: {stats.get('source', 'Unknown')}")
        print(f"   Sequences: {stats.get('total_sequences', 'N/A')}")
        print(f"   Total bases: {stats.get('total_bases', 'N/A'):,}")
        if 'average_length' in stats:
            print(f"   Average length: {stats['average_length']:.1f}")
    
    print(f"\n🎉 Integration demo complete!")

if __name__ == "__main__":
    demo_integration()
