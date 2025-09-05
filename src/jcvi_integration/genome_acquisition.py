#!/usr/bin/env python3
"""
JCVI Genome Acquisition Module - v0.0.03

Provides genome acquisition capabilities that integrate with existing BioXen infrastructure.
Built as an enhancement to the proven download_genomes.py and phase4_jcvi_cli_integration.py.

This module serves as a bridge between genome downloading and JCVI analysis,
addressing the gap identified in the specification.
"""

import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import json

# Import existing proven infrastructure  
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from download_genomes import download_genome, MINIMAL_GENOMES, check_dependencies
except ImportError:
    download_genome = None
    MINIMAL_GENOMES = {}
    check_dependencies = None

@dataclass
class GenomeAcquisitionRequest:
    """Request specification for genome acquisition."""
    identifier: str  # Genome key from MINIMAL_GENOMES or custom identifier
    source: str = 'existing'  # 'existing' uses proven download_genomes.py
    output_dir: Optional[str] = None
    jcvi_preparation: bool = True
    metadata_collection: bool = True

class JCVIGenomeAcquisition:
    """
    JCVI-compatible genome acquisition using existing proven infrastructure.
    
    This class enhances the existing download_genomes.py functionality
    with JCVI-specific preparation and metadata collection.
    """
    
    def __init__(self, work_dir: Optional[Path] = None):
        """
        Initialize acquisition system.
        
        Args:
            work_dir: Working directory for acquisition operations
        """
        self.work_dir = work_dir or Path("jcvi_genomes")
        self.work_dir.mkdir(exist_ok=True)
        
        # Set up directory structure
        self.download_dir = self.work_dir / "downloads"
        self.jcvi_ready_dir = self.work_dir / "jcvi_ready"
        self.metadata_dir = self.work_dir / "metadata"
        
        for directory in [self.download_dir, self.jcvi_ready_dir, self.metadata_dir]:
            directory.mkdir(exist_ok=True)
        
        # Check if existing infrastructure is available
        self.download_available = download_genome is not None
        self.dependencies_ok = check_dependencies() if check_dependencies else False
        
        print(f"🧬 JCVI Genome Acquisition initialized")
        print(f"   Work directory: {self.work_dir}")
        print(f"   Download infrastructure: {'✅ Available' if self.download_available else '❌ Not Available'}")
    
    def get_available_genomes(self) -> Dict[str, Dict]:
        """Get list of genomes available through existing infrastructure."""
        if MINIMAL_GENOMES:
            return MINIMAL_GENOMES.copy()
        return {}
    
    def acquire_genome(self, request: GenomeAcquisitionRequest) -> Dict:
        """
        Acquire genome using existing proven download infrastructure.
        
        Args:
            request: Genome acquisition request
            
        Returns:
            Dictionary with acquisition results
        """
        if not self.download_available:
            return {
                'status': 'failed',
                'error': 'Download infrastructure not available'
            }
        
        print(f"📥 Acquiring genome: {request.identifier}")
        
        try:
            # Use existing proven download function
            download_path = Path(request.output_dir) if request.output_dir else self.download_dir
            download_path.mkdir(exist_ok=True)
            
            # Call existing proven download_genome function
            success = download_genome(request.identifier, download_path)
            
            if not success:
                return {
                    'status': 'failed',
                    'error': f'Download failed for {request.identifier}'
                }
            
            # Find downloaded files
            downloaded_files = self._find_downloaded_files(download_path, request.identifier)
            
            if not downloaded_files:
                return {
                    'status': 'failed',
                    'error': 'No files found after download'
                }
            
            result = {
                'status': 'success',
                'identifier': request.identifier,
                'download_path': str(download_path),
                'files': [str(f) for f in downloaded_files]
            }
            
            # JCVI preparation if requested
            if request.jcvi_preparation:
                jcvi_files = self._prepare_for_jcvi(downloaded_files, request.identifier)
                result['jcvi_ready_files'] = [str(f) for f in jcvi_files]
            
            # Metadata collection if requested
            if request.metadata_collection:
                metadata = self._collect_metadata(downloaded_files, request)
                result['metadata'] = metadata
                
                # Save metadata to file
                metadata_file = self.metadata_dir / f"{request.identifier}.json"
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                result['metadata_file'] = str(metadata_file)
            
            print(f"✅ Genome acquired: {request.identifier}")
            return result
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': f'Acquisition error: {str(e)}'
            }
    
    def _find_downloaded_files(self, download_path: Path, identifier: str) -> List[Path]:
        """Find downloaded genome files."""
        # Common genome file patterns
        patterns = ["*.fasta", "*.fa", "*.fna", "*.fas", "*.gbk", "*.gbff"]
        
        files = []
        for pattern in patterns:
            files.extend(download_path.rglob(pattern))
        
        return files
    
    def _prepare_for_jcvi(self, downloaded_files: List[Path], identifier: str) -> List[Path]:
        """
        Prepare downloaded files for JCVI compatibility.
        
        Creates JCVI-ready versions with clean sequence IDs and proper formatting.
        """
        jcvi_files = []
        
        for file_path in downloaded_files:
            if file_path.suffix.lower() in ['.fasta', '.fa', '.fna', '.fas']:
                jcvi_file = self._create_jcvi_fasta(file_path, identifier)
                if jcvi_file:
                    jcvi_files.append(jcvi_file)
        
        return jcvi_files
    
    def _create_jcvi_fasta(self, fasta_file: Path, identifier: str) -> Optional[Path]:
        """Create JCVI-compatible FASTA file."""
        try:
            jcvi_file = self.jcvi_ready_dir / f"{identifier}.jcvi.fasta"
            
            with open(fasta_file, 'r') as infile, open(jcvi_file, 'w') as outfile:
                sequence_count = 0
                for line in infile:
                    if line.startswith('>'):
                        # Clean header for JCVI compatibility
                        sequence_count += 1
                        clean_id = f">{identifier}_seq_{sequence_count}"
                        outfile.write(f"{clean_id}\n")
                    else:
                        # Write sequence line as-is
                        outfile.write(line)
            
            return jcvi_file
            
        except Exception as e:
            print(f"Warning: JCVI FASTA preparation failed for {fasta_file}: {e}")
            return None
    
    def _collect_metadata(self, files: List[Path], request: GenomeAcquisitionRequest) -> Dict:
        """Collect metadata about acquired genome."""
        metadata = {
            'acquisition': {
                'identifier': request.identifier,
                'source': request.source,
                'timestamp': str(Path().absolute()),  # Simple timestamp
            },
            'files': {}
        }
        
        # Add file information
        for file_path in files:
            metadata['files'][file_path.name] = {
                'path': str(file_path),
                'size_bytes': file_path.stat().st_size,
                'type': file_path.suffix.lower()
            }
        
        # Add genome information from MINIMAL_GENOMES if available
        if request.identifier in MINIMAL_GENOMES:
            metadata['genome_info'] = MINIMAL_GENOMES[request.identifier].copy()
        
        return metadata

def batch_acquire_genomes(identifiers: List[str], 
                         work_dir: Optional[Path] = None,
                         jcvi_preparation: bool = True) -> List[Dict]:
    """
    Batch acquisition of multiple genomes.
    
    Args:
        identifiers: List of genome identifiers
        work_dir: Working directory for operations
        jcvi_preparation: Whether to prepare files for JCVI
        
    Returns:
        List of acquisition results
    """
    acquirer = JCVIGenomeAcquisition(work_dir)
    results = []
    
    for identifier in identifiers:
        request = GenomeAcquisitionRequest(
            identifier=identifier,
            jcvi_preparation=jcvi_preparation
        )
        
        result = acquirer.acquire_genome(request)
        results.append(result)
        
        if result['status'] != 'success':
            print(f"⚠️  Failed to acquire {identifier}: {result.get('error', 'Unknown error')}")
    
    return results

# Convenience functions for integration
def acquire_minimal_genome_set() -> List[Dict]:
    """Acquire a minimal set of genomes for testing/demo purposes."""
    if not MINIMAL_GENOMES:
        return []
    
    # Select first 2 genomes for minimal testing
    test_genomes = list(MINIMAL_GENOMES.keys())[:2]
    return batch_acquire_genomes(test_genomes)

def get_acquisition_status() -> Dict:
    """Get status of acquisition infrastructure."""
    return {
        'download_available': download_genome is not None,
        'available_genomes': len(MINIMAL_GENOMES),
        'dependencies_ok': check_dependencies() if check_dependencies else False,
        'genome_list': list(MINIMAL_GENOMES.keys()) if MINIMAL_GENOMES else []
    }
