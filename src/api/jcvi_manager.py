"""
JCVI Manager - Unified API access to JCVI functionality

This module provides a clean API wrapper around the existing JCVI integration
infrastructure, making JCVI capabilities accessible through the factory pattern
while maintaining graceful fallback mechanisms.
"""

import sys
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

# Add root directory to path for imports
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

try:
    # Import enhanced v0.0.03 JCVI integration
    from src.jcvi_integration.genome_acquisition import JCVIGenomeAcquisition
    from src.jcvi_integration.analysis_coordinator import JCVIWorkflowCoordinator
    from phase4_jcvi_cli_integration import JCVICLIIntegrator
    from bioxen_to_jcvi_converter import BioXenToJCVIConverter
    from download_genomes import download_genome, MINIMAL_GENOMES
    ENHANCED_JCVI_AVAILABLE = True
except ImportError as e:
    print(f"🧬 BioXen-JCVI Integration: Running in fallback mode (JCVI not available)")
    JCVIGenomeAcquisition = None
    JCVIWorkflowCoordinator = None
    JCVICLIIntegrator = None
    BioXenToJCVIConverter = None
    download_genome = None
    MINIMAL_GENOMES = {}
    ENHANCED_JCVI_AVAILABLE = False


class JCVIManager:
    """
    Unified JCVI functionality manager for the API layer.
    
    This class wraps the existing JCVI integration infrastructure to provide
    clean API access while maintaining all existing capabilities including
    graceful fallback, format conversion, and hardware optimization.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize JCVI Manager with configuration.
        
        Args:
            config: Configuration dictionary with JCVI settings
        """
        self.config = config
        self._integration = None
        self._cli_integrator = None
        self._converter = None
        self._available = False
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize JCVI integration components if available."""
        try:
            # Initialize enhanced v0.0.03 integration components
            if ENHANCED_JCVI_AVAILABLE:
                # Initialize acquisition system
                if JCVIGenomeAcquisition:
                    self._genome_acquisition = JCVIGenomeAcquisition()
                
                # Initialize workflow coordinator  
                if JCVIWorkflowCoordinator:
                    self._workflow_coordinator = JCVIWorkflowCoordinator()
                
                self._available = True
            else:
                self._genome_acquisition = None
                self._workflow_coordinator = None
                self._available = False
            
            # Initialize CLI integrator if enabled and available
            if (JCVICLIIntegrator and 
                self.config.get('jcvi_cli_enabled', True) and 
                self._available):
                try:
                    self._cli_integrator = JCVICLIIntegrator()
                except Exception as e:
                    print(f"Warning: CLI integrator initialization failed: {e}")
                    self._cli_integrator = None
            
            # Initialize converter if available
            if BioXenToJCVIConverter:
                self._converter = BioXenToJCVIConverter()
                
        except Exception as e:
            print(f"Warning: JCVI component initialization failed: {e}")
            self._available = False
    
    @property
    def available(self) -> bool:
        """Check if JCVI functionality is available."""
        return self._available and self._integration is not None
    
    @property
    def cli_available(self) -> bool:
        """Check if JCVI CLI integration is available."""
        return self.available and self._cli_integrator is not None
    
    @property
    def converter_available(self) -> bool:
        """Check if format converter is available."""
        return self._converter is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive JCVI integration status."""
        return {
            'jcvi_available': self.available,
            'cli_integration_available': self.cli_available,
            'converter_available': self.converter_available,
            'config': {
                'jcvi_cli_enabled': self.config.get('jcvi_cli_enabled', True),
                'hardware_optimization': self.config.get('hardware_optimization', False),
                'fallback_mode': self.config.get('fallback_mode', True)
            }
        }
    
    def get_genome_statistics(self, genome_path: str) -> Dict[str, Any]:
        """
        Get enhanced genome statistics using JCVI integration.
        
        Args:
            genome_path: Path to genome file
            
        Returns:
            Dictionary with genome statistics, enhanced if JCVI available
        """
        if not self.available:
            return {
                'error': 'JCVI integration not available',
                'fallback': 'Use basic genome analysis instead'
            }
        
        try:
            return self._integration.get_genome_statistics(genome_path)
        except Exception as e:
            return {
                'error': f'JCVI analysis failed: {str(e)}',
                'fallback': 'Basic analysis recommended'
            }
    
    def run_synteny_analysis(self, genome1: str, genome2: str, **kwargs) -> Dict[str, Any]:
        """
        Run synteny analysis using JCVI CLI tools.
        
        Args:
            genome1: Path to first genome file
            genome2: Path to second genome file
            **kwargs: Additional parameters for synteny analysis
            
        Returns:
            Dictionary with synteny analysis results
        """
        if not self.cli_available:
            return {
                'error': 'JCVI CLI integration not available',
                'available': self.available,
                'cli_enabled': self.config.get('jcvi_cli_enabled', True)
            }
        
        try:
            # Ensure genomes are in FASTA format
            fasta1 = self.ensure_fasta_format(genome1)
            fasta2 = self.ensure_fasta_format(genome2)
            
            if not fasta1 or not fasta2:
                return {
                    'error': 'Could not convert genomes to FASTA format',
                    'genome1_fasta': fasta1,
                    'genome2_fasta': fasta2
                }
            
            # Run synteny analysis
            return self._cli_integrator.run_synteny_analysis(fasta1, fasta2, **kwargs)
            
        except Exception as e:
            return {
                'error': f'Synteny analysis failed: {str(e)}',
                'fallback': 'Basic comparative analysis recommended'
            }
    
    def ensure_fasta_format(self, genome_path: str) -> Optional[str]:
        """
        Ensure genome file is in FASTA format for JCVI compatibility.
        
        Args:
            genome_path: Path to genome file (.genome or .fasta)
            
        Returns:
            Path to FASTA file, or None if conversion failed
        """
        if not self.available:
            return None
            
        try:
            return self._integration.ensure_fasta_format(genome_path)
        except Exception as e:
            print(f"Warning: FASTA format conversion failed: {e}")
            return None
    
    def convert_format(self, input_path: str, output_path: str) -> bool:
        """
        Convert between BioXen and JCVI formats.
        
        Args:
            input_path: Path to input file
            output_path: Path to output file
            
        Returns:
            True if conversion successful, False otherwise
        """
        if not self.converter_available:
            print("Warning: Format converter not available")
            return False
        
        try:
            return self._converter.convert_genome(input_path, output_path)
        except Exception as e:
            print(f"Warning: Format conversion failed: {e}")
            return False
    
    def run_comparative_genomics(self, genomes: List[str], **kwargs) -> Dict[str, Any]:
        """
        Run comprehensive comparative genomics analysis.
        
        Args:
            genomes: List of genome file paths
            **kwargs: Additional parameters for analysis
            
        Returns:
            Dictionary with comparative analysis results
        """
        if not self.cli_available:
            return {
                'error': 'JCVI CLI integration required for comparative genomics',
                'available_methods': ['basic_comparison'] if self.available else []
            }
        
        if len(genomes) < 2:
            return {'error': 'At least 2 genomes required for comparative analysis'}
        
        try:
            # Ensure all genomes are in FASTA format
            fasta_genomes = []
            for genome in genomes:
                fasta_path = self.ensure_fasta_format(genome)
                if fasta_path:
                    fasta_genomes.append(fasta_path)
                else:
                    return {
                        'error': f'Could not convert genome to FASTA: {genome}',
                        'converted': fasta_genomes
                    }
            
            # Run comprehensive analysis using CLI integrator
            if hasattr(self._cli_integrator, 'run_comparative_genomics'):
                return self._cli_integrator.run_comparative_genomics(fasta_genomes, **kwargs)
            else:
                # Fallback to pairwise synteny analysis
                results = {}
                for i in range(len(fasta_genomes)):
                    for j in range(i + 1, len(fasta_genomes)):
                        pair_key = f"{Path(fasta_genomes[i]).name}_vs_{Path(fasta_genomes[j]).name}"
                        results[pair_key] = self.run_synteny_analysis(
                            fasta_genomes[i], fasta_genomes[j], **kwargs
                        )
                return {
                    'method': 'pairwise_synteny',
                    'results': results,
                    'genome_count': len(fasta_genomes)
                }
        
        except Exception as e:
            return {
                'error': f'Comparative genomics analysis failed: {str(e)}',
                'genomes_processed': len(fasta_genomes) if 'fasta_genomes' in locals() else 0
            }
    
    def get_hardware_info(self) -> Dict[str, Any]:
        """Get hardware information and optimization status."""
        if not self.cli_available:
            return {'error': 'CLI integration not available'}
        
        try:
            if hasattr(self._cli_integrator, 'hardware_info'):
                return self._cli_integrator.hardware_info
            elif hasattr(self._cli_integrator, '_detect_hardware'):
                return self._cli_integrator._detect_hardware()
            else:
                return {'info': 'Hardware detection not available in CLI integrator'}
        except Exception as e:
            return {'error': f'Hardware detection failed: {str(e)}'}
    
    def cleanup(self):
        """Cleanup JCVI resources and temporary files."""
        try:
            if self._cli_integrator and hasattr(self._cli_integrator, 'cleanup'):
                self._cli_integrator.cleanup()
            
            if self._integration and hasattr(self._integration, 'cleanup'):
                self._integration.cleanup()
                
        except Exception as e:
            print(f"Warning: JCVI cleanup failed: {e}")
    
    # Enhanced v0.0.03: Genome Acquisition Integration
    def list_available_genomes(self) -> Dict[str, Dict]:
        """List genomes available for download through existing infrastructure."""
        if download_genome and MINIMAL_GENOMES:
            return MINIMAL_GENOMES.copy()
        return {}
    
    def acquire_genome(self, genome_key: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Acquire genome using existing proven download infrastructure.
        
        Args:
            genome_key: Key from MINIMAL_GENOMES or custom identifier
            output_dir: Optional output directory
            
        Returns:
            Dictionary with acquisition results
        """
        if not download_genome:
            return {
                'status': 'failed',
                'error': 'Genome download functionality not available'
            }
        
        try:
            from pathlib import Path
            
            # Use existing proven download function
            download_dir = Path(output_dir) if output_dir else Path("genomes")
            download_dir.mkdir(exist_ok=True)
            
            success = download_genome(genome_key, download_dir)
            
            if success:
                # Find downloaded files and prepare for JCVI
                genome_files = []
                for pattern in ["*.fasta", "*.fa", "*.fna"]:
                    genome_files.extend(download_dir.glob(pattern))
                
                if genome_files:
                    # Use existing converter if available for JCVI preparation
                    jcvi_ready_files = []
                    for genome_file in genome_files:
                        if self.converter_available:
                            try:
                                # Convert to JCVI-compatible format using existing converter
                                jcvi_file = self._prepare_for_jcvi(genome_file)
                                if jcvi_file:
                                    jcvi_ready_files.append(str(jcvi_file))
                            except Exception as e:
                                print(f"Warning: JCVI preparation failed for {genome_file}: {e}")
                                jcvi_ready_files.append(str(genome_file))  # Use original
                        else:
                            jcvi_ready_files.append(str(genome_file))
                    
                    return {
                        'status': 'success',
                        'genome_key': genome_key,
                        'files': [str(f) for f in genome_files],
                        'jcvi_ready_files': jcvi_ready_files,
                        'output_dir': str(download_dir)
                    }
                else:
                    return {
                        'status': 'failed',
                        'error': 'No genome files found after download'
                    }
            else:
                return {
                    'status': 'failed', 
                    'error': f'Download failed for genome: {genome_key}'
                }
                
        except Exception as e:
            return {
                'status': 'failed',
                'error': f'Acquisition error: {str(e)}'
            }
    
    def _prepare_for_jcvi(self, genome_file: Path) -> Optional[Path]:
        """Prepare genome file for JCVI analysis using existing infrastructure."""
        try:
            # Create JCVI-optimized filename
            jcvi_file = genome_file.parent / f"{genome_file.stem}.jcvi.fasta"
            
            # Simple preparation: ensure clean sequence IDs for JCVI compatibility
            with open(genome_file, 'r') as infile, open(jcvi_file, 'w') as outfile:
                for line in infile:
                    if line.startswith('>'):
                        # Clean header for JCVI compatibility
                        header = line.strip()
                        clean_id = header.split()[0].replace('|', '_').replace(' ', '_')
                        outfile.write(f"{clean_id}\n")
                    else:
                        outfile.write(line)
            
            return jcvi_file
            
        except Exception as e:
            print(f"Warning: JCVI preparation failed: {e}")
            return None
    
    def run_complete_workflow(self, genome_keys: List[str], 
                            analysis_type: str = 'synteny') -> Dict[str, Any]:
        """
        Run complete workflow from acquisition to analysis using existing infrastructure.
        
        Args:
            genome_keys: List of genome identifiers to acquire and analyze
            analysis_type: Type of analysis ('synteny', 'phylogenetic', 'comprehensive')
            
        Returns:
            Complete workflow results
        """
        if not self.cli_available:
            return {
                'status': 'failed',
                'error': 'JCVI CLI integration not available for analysis'
            }
        
        workflow_results = {
            'status': 'running',
            'acquisition_results': [],
            'analysis_results': {},
            'start_time': str(Path(__file__).stat().st_mtime)  # Simple timestamp
        }
        
        try:
            # Phase 1: Acquire genomes using existing proven method
            print(f"🧬 Phase 1: Acquiring {len(genome_keys)} genomes...")
            acquired_genomes = {}
            
            for genome_key in genome_keys:
                print(f"  📥 Acquiring {genome_key}...")
                result = self.acquire_genome(genome_key)
                workflow_results['acquisition_results'].append(result)
                
                if result['status'] == 'success':
                    # Prepare genome data for existing JCVI CLI integrator
                    if result['jcvi_ready_files']:
                        fasta_file = Path(result['jcvi_ready_files'][0])
                        acquired_genomes[genome_key] = {
                            'fasta_path': fasta_file,
                            'size_mb': fasta_file.stat().st_size / (1024 * 1024),
                            'source': 'acquired'
                        }
            
            successful_count = len(acquired_genomes)
            print(f"  ✅ Successfully acquired {successful_count}/{len(genome_keys)} genomes")
            
            if successful_count < 2:
                return {
                    'status': 'failed',
                    'error': 'Need at least 2 genomes for comparative analysis',
                    'acquisition_results': workflow_results['acquisition_results']
                }
            
            # Phase 2: Run analysis using existing CLI integrator
            print(f"🔬 Phase 2: Running {analysis_type} analysis...")
            
            if analysis_type == 'synteny':
                analysis_result = self._cli_integrator.run_real_synteny_analysis(acquired_genomes)
            elif analysis_type == 'phylogenetic':
                analysis_result = self._cli_integrator.generate_phylogenetic_tree(acquired_genomes)
            elif analysis_type == 'comprehensive':
                # Run multiple analyses using existing methods
                synteny_result = self._cli_integrator.run_real_synteny_analysis(acquired_genomes)
                phylo_result = self._cli_integrator.generate_phylogenetic_tree(acquired_genomes)
                analysis_result = {
                    'type': 'comprehensive',
                    'synteny': synteny_result,
                    'phylogenetic': phylo_result
                }
            else:
                return {
                    'status': 'failed',
                    'error': f'Unknown analysis type: {analysis_type}'
                }
            
            workflow_results['analysis_results'] = analysis_result
            workflow_results['status'] = 'completed'
            
            print(f"✅ Complete workflow finished successfully")
            return workflow_results
            
        except Exception as e:
            workflow_results['status'] = 'failed'
            workflow_results['error'] = str(e)
            print(f"❌ Workflow failed: {e}")
            return workflow_results


def create_jcvi_manager(config: Optional[Dict[str, Any]] = None) -> JCVIManager:
    """
    Factory function to create a JCVI Manager instance.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured JCVIManager instance
    """
    if config is None:
        config = {
            'jcvi_cli_enabled': True,
            'hardware_optimization': False,
            'fallback_mode': True
        }
    
    return JCVIManager(config)
