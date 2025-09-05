from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from ..hypervisor.core import BioXenHypervisor, VirtualMachine
from .jcvi_manager import JCVIManager

class BiologicalVM(ABC):
    """
    Abstract base class for all biological VMs.
    Mirrors pylua_bioxen_vm_lib VM class hierarchy pattern.
    """
    
    def __init__(self, vm_id: str, biological_type: str, hypervisor: BioXenHypervisor, config: Dict[str, Any]):
        self.vm_id = vm_id
        self.biological_type = biological_type  # syn3a, ecoli, minimal_cell
        self.hypervisor = hypervisor  # Reference to existing hypervisor (delegation pattern)
        self.config = config
        self._vm_instance: Optional[VirtualMachine] = None
        
        # Initialize JCVI Manager if enabled
        self.jcvi: Optional[JCVIManager] = None
        if config.get('enable_jcvi', True):
            try:
                self.jcvi = JCVIManager(config)
            except Exception as e:
                print(f"Warning: JCVI Manager initialization failed: {e}")
                self.jcvi = None
    
    @abstractmethod
    def get_vm_type(self) -> str:
        """Return the VM infrastructure type (basic/xcpng) - pylua pattern."""
        pass
    
    def get_biological_type(self) -> str:
        """Return the biological organism type (syn3a, ecoli, minimal_cell)."""
        return self.biological_type
    
    @property
    def jcvi_available(self) -> bool:
        """Check if JCVI functionality is available for this VM."""
        return self.jcvi is not None and self.jcvi.available
    
    def get_jcvi_status(self) -> Dict[str, Any]:
        """Get JCVI integration status for this VM."""
        if self.jcvi is None:
            return {'enabled': False, 'reason': 'JCVI not initialized'}
        return self.jcvi.get_status()
    
    # Common interface methods that delegate to hypervisor (pylua delegation pattern)
    def start(self) -> bool:
        """Start the biological VM - mirrors pylua VM.start()."""
        return self.hypervisor.start_vm(self.vm_id)
    
    def pause(self) -> bool:
        """Pause the biological VM."""
        return self.hypervisor.pause_vm(self.vm_id)
    
    def resume(self) -> bool:
        """Resume the biological VM."""
        return self.hypervisor.resume_vm(self.vm_id)
    
    def destroy(self) -> bool:
        """Destroy the biological VM - mirrors pylua cleanup pattern."""
        return self.hypervisor.destroy_vm(self.vm_id)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current VM status - mirrors pylua VM.get_status()."""
        return self.hypervisor.get_vm_status(self.vm_id)
    
    # Biological-specific methods (same interface for all VM types)
    def execute_biological_process(self, process_code: str) -> Dict[str, Any]:
        """Execute biological process - equivalent to pylua execute_string()."""
        return self._execute_biological_process_impl(process_code)
    
    def install_biological_package(self, package_name: str) -> Dict[str, Any]:
        """Install biological analysis package."""
        return self._install_biological_package_impl(package_name)
    
    def get_biological_metrics(self) -> Dict[str, Any]:
        """Get biological metrics based on organism type."""
        return self._get_biological_metrics_impl()
    
    # Abstract implementation methods - infrastructure-specific
    @abstractmethod
    def _execute_biological_process_impl(self, process_code: str) -> Dict[str, Any]:
        """Implementation-specific biological process execution."""
        pass
    
    @abstractmethod
    def _install_biological_package_impl(self, package_name: str) -> Dict[str, Any]:
        """Implementation-specific package installation."""
        pass
    
    @abstractmethod
    def _get_biological_metrics_impl(self) -> Dict[str, Any]:
        """Implementation-specific metrics gathering."""
        pass
    
    # Biological-specific helper methods (available for all VM types)
    def start_transcription(self, gene_ids: List[str]) -> bool:
        """Start transcription - available for all VM types."""
        if self.biological_type == "syn3a":
            return self.hypervisor.start_gene_expression(self.vm_id, gene_ids)
        else:
            raise ValueError(f"Transcription not supported for {self.biological_type}")

    def get_essential_genes(self) -> List[str]:
        """Get essential genes - Syn3A specific."""
        if self.biological_type == "syn3a":
            vm = self.hypervisor.get_vm(self.vm_id)
            return vm.genome.essential_genes if vm else []
        return []

    def manage_operons(self, operon_ids: List[str], action: str) -> bool:
        """Manage operons - E.coli specific."""
        if self.biological_type == "ecoli":
            return self.hypervisor.manage_operons(self.vm_id, operon_ids, action)
        else:
            raise ValueError(f"Operons not supported for {self.biological_type}")

    def get_plasmid_count(self) -> int:
        """Get plasmid count - E.coli specific."""
        if self.biological_type == "ecoli":
            status = self.get_status()
            return status.get('plasmid_count', 0)
        return 0


class BasicBiologicalVM(BiologicalVM):
    """
    Basic biological VM running directly on BioXen hypervisor.
    Equivalent to pylua BasicLuaVM - direct process execution.
    """
    
    def __init__(self, vm_id: str, biological_type: str, hypervisor: BioXenHypervisor, config: Dict[str, Any]):
        super().__init__(vm_id, biological_type, hypervisor, config)
    
    def get_vm_type(self) -> str:
        return "basic"
    
    def _execute_biological_process_impl(self, process_code: str) -> Dict[str, Any]:
        """Execute biological process directly on hypervisor."""
        return self.hypervisor.execute_biological_process(self.vm_id, process_code, self.biological_type)

    def _install_biological_package_impl(self, package_name: str) -> Dict[str, Any]:
        """Install biological analysis package."""
        return self.hypervisor.install_package(self.vm_id, package_name)

    def _get_biological_metrics_impl(self) -> Dict[str, Any]:
        """Get biological metrics based on organism type."""
        if self.biological_type == "syn3a":
            return self._get_syn3a_metrics()
        elif self.biological_type == "ecoli":
            return self._get_ecoli_metrics()
        elif self.biological_type == "minimal_cell":
            return self._get_minimal_cell_metrics()
        else:
            return {}

    def _get_syn3a_metrics(self) -> Dict[str, Any]:
        """Get Syn3A-specific metrics."""
        status = self.get_status()
        return {
            'atp_level': status.get('atp_percent', 0.0),
            'essential_genes': status.get('essential_genes', []),
            'ribosome_allocation': status.get('allocated_ribosomes', 0)
        }

    def _get_ecoli_metrics(self) -> Dict[str, Any]:
        """Get E.coli-specific metrics."""
        status = self.get_status()
        return {
            'plasmid_count': status.get('plasmid_count', 0),
            'growth_phase': status.get('growth_phase', 'stationary'),
            'operon_status': status.get('operon_status', {})
        }

    def _get_minimal_cell_metrics(self) -> Dict[str, Any]:
        """Get minimal cell-specific metrics."""
        status = self.get_status()
        return {
            'minimal_functions': ['dna_replication', 'protein_synthesis', 'energy_production'],
            'function_status': status.get('function_status', {})
        }
    
    # JCVI-Enhanced Methods for BasicBiologicalVM
    def analyze_genome(self, genome_path: str) -> Dict[str, Any]:
        """Enhanced genome analysis with optional JCVI integration."""
        if self.jcvi_available:
            jcvi_stats = self.jcvi.get_genome_statistics(genome_path)
            if 'error' not in jcvi_stats:
                return {
                    'analysis_type': 'jcvi_enhanced',
                    'vm_type': self.get_vm_type(),
                    'biological_type': self.biological_type,
                    'jcvi_stats': jcvi_stats,
                    'basic_stats': self._basic_genome_analysis(genome_path)
                }
        
        # Fallback to basic analysis
        return {
            'analysis_type': 'basic_fallback',
            'vm_type': self.get_vm_type(),
            'biological_type': self.biological_type,
            'stats': self._basic_genome_analysis(genome_path),
            'jcvi_available': False
        }
    
    def _basic_genome_analysis(self, genome_path: str) -> Dict[str, Any]:
        """Basic genome analysis without JCVI."""
        try:
            # Simple file-based analysis
            with open(genome_path, 'r') as f:
                content = f.read()
                return {
                    'file_size': len(content),
                    'line_count': content.count('\n'),
                    'contains_fasta': content.startswith('>'),
                    'source': 'basic_bioxen_analysis'
                }
        except Exception as e:
            return {'error': f'Basic analysis failed: {str(e)}'}
    
    def convert_genome_format(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """Convert genome format using JCVI converter if available."""
        if self.jcvi_available and self.jcvi.converter_available:
            success = self.jcvi.convert_format(input_path, output_path)
            return {
                'success': success,
                'method': 'jcvi_converter',
                'input_path': input_path,
                'output_path': output_path
            }
        
        return {
            'success': False,
            'method': 'fallback',
            'error': 'JCVI converter not available',
            'suggestion': 'Use manual format conversion'
        }


class XCPngBiologicalVM(BiologicalVM):
    """
    XCP-ng biological VM running basic VMs inside full virtual machines.
    Equivalent to pylua XCPngVM - template-based VM with SSH execution.
    Provides additional isolation by running BioXen VMs inside XCP-ng VMs.
    """
    
    def __init__(self, vm_id: str, biological_type: str, hypervisor: BioXenHypervisor, config: Dict[str, Any]):
        super().__init__(vm_id, biological_type, hypervisor, config)
        self.xcpng_vm_uuid = None
        self.vm_ip = None
        # XCP-ng specific configuration
        self.xapi_config = config.get('xcpng_config', {})
    
    def get_vm_type(self) -> str:
        return "xcpng"
    
    def start(self) -> bool:
        """Start XCP-ng VM then start biological VM inside it."""
        # First create/start the XCP-ng VM (following pylua XCPngVM pattern)
        self.xcpng_vm_uuid = self._create_xcpng_vm()
        self._start_xcpng_vm()
        self.vm_ip = self._get_vm_ip()
        
        # Then start the biological VM inside the XCP-ng VM via SSH
        return self._start_biological_vm_via_ssh()
    
    def _execute_biological_process_impl(self, process_code: str) -> Dict[str, Any]:
        """Execute biological process via SSH in XCP-ng VM."""
        if not self.vm_ip:
            raise ValueError("XCP-ng VM not started or IP not available")
        
        # Execute biological process via SSH (pylua SSH execution pattern)
        return self._execute_via_ssh(process_code)
    
    def _install_biological_package_impl(self, package_name: str) -> Dict[str, Any]:
        """Install biological package via SSH in XCP-ng VM."""
        if not self.vm_ip:
            raise ValueError("XCP-ng VM not started or IP not available")
        
        return self._install_package_via_ssh(package_name)
    
    def _get_biological_metrics_impl(self) -> Dict[str, Any]:
        """Get biological metrics via SSH."""
        if not self.vm_ip:
            raise ValueError("XCP-ng VM not started or IP not available")
        
        # Get metrics via SSH and parse based on biological type
        ssh_result = self._execute_via_ssh("get_biological_status()")
        return self._parse_biological_metrics(ssh_result)
    
    # XCP-ng specific implementation methods (Phase 1 placeholders)
    def _create_xcpng_vm(self) -> str:
        """Create XCP-ng VM from template (following pylua XAPI pattern)."""
        # Phase 1 placeholder - full implementation in Phase 2
        raise NotImplementedError("XCP-ng VM creation will be implemented in Phase 2")
    
    def _start_xcpng_vm(self) -> bool:
        """Start the XCP-ng VM."""
        # Phase 1 placeholder - full implementation in Phase 2
        raise NotImplementedError("XCP-ng VM start will be implemented in Phase 2")
    
    def _get_vm_ip(self) -> str:
        """Get IP address of started XCP-ng VM."""
        # Phase 1 placeholder - full implementation in Phase 2
        raise NotImplementedError("XCP-ng VM IP discovery will be implemented in Phase 2")
    
    def _start_biological_vm_via_ssh(self) -> bool:
        """Start biological VM inside XCP-ng VM via SSH."""
        # Phase 1 placeholder - full implementation in Phase 2
        raise NotImplementedError("SSH biological VM start will be implemented in Phase 2")
    
    def _execute_via_ssh(self, process_code: str) -> Dict[str, Any]:
        """Execute biological process via SSH."""
        # Phase 1 placeholder - full implementation in Phase 2
        raise NotImplementedError("SSH execution will be implemented in Phase 2")
    
    def _install_package_via_ssh(self, package_name: str) -> Dict[str, Any]:
        """Install package via SSH."""
        # Phase 1 placeholder - full implementation in Phase 2
        raise NotImplementedError("SSH package installation will be implemented in Phase 2")
    
    def _parse_biological_metrics(self, ssh_result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse SSH result into biological metrics based on organism type."""
        # Phase 1 placeholder - full implementation in Phase 2
        raise NotImplementedError("SSH metrics parsing will be implemented in Phase 2")
    
    # JCVI-Enhanced Methods for XCPngBiologicalVM
    def run_comparative_analysis(self, genome1: str, genome2: str, **kwargs) -> Dict[str, Any]:
        """Comparative analysis with JCVI synteny tools."""
        if self.jcvi_available and self.jcvi.cli_available:
            result = self.jcvi.run_synteny_analysis(genome1, genome2, **kwargs)
            return {
                'analysis_type': 'jcvi_synteny',
                'vm_type': self.get_vm_type(),
                'biological_type': self.biological_type,
                'synteny_result': result,
                'hardware_optimized': self.config.get('hardware_optimization', False)
            }
        
        # Fallback to basic comparative analysis
        return {
            'analysis_type': 'basic_comparative',
            'vm_type': self.get_vm_type(),
            'biological_type': self.biological_type,
            'result': self._basic_comparative_analysis(genome1, genome2),
            'jcvi_available': False
        }
    
    def run_multi_genome_analysis(self, genomes: List[str], **kwargs) -> Dict[str, Any]:
        """Multi-genome comparative analysis using JCVI."""
        if self.jcvi_available and self.jcvi.cli_available:
            result = self.jcvi.run_comparative_genomics(genomes, **kwargs)
            return {
                'analysis_type': 'jcvi_multi_genome',
                'vm_type': self.get_vm_type(),
                'biological_type': self.biological_type,
                'genome_count': len(genomes),
                'comparative_result': result,
                'hardware_info': self.jcvi.get_hardware_info()
            }
        
        return {
            'analysis_type': 'basic_multi_genome_fallback',
            'vm_type': self.get_vm_type(),
            'error': 'JCVI CLI integration required for multi-genome analysis',
            'genome_count': len(genomes),
            'suggestion': 'Use pairwise basic comparison instead'
        }
    
    def _basic_comparative_analysis(self, genome1: str, genome2: str) -> Dict[str, Any]:
        """Basic comparative analysis without JCVI."""
        try:
            # Simple file comparison
            with open(genome1, 'r') as f1, open(genome2, 'r') as f2:
                content1 = f1.read()
                content2 = f2.read()
                
                return {
                    'genome1_size': len(content1),
                    'genome2_size': len(content2),
                    'size_ratio': len(content1) / len(content2) if len(content2) > 0 else 0,
                    'identical': content1 == content2,
                    'source': 'basic_bioxen_comparison'
                }
        except Exception as e:
            return {'error': f'Basic comparison failed: {str(e)}'}
    
    def get_hardware_optimization_status(self) -> Dict[str, Any]:
        """Get hardware optimization status for JCVI operations."""
        if self.jcvi_available and self.jcvi.cli_available:
            hardware_info = self.jcvi.get_hardware_info()
            return {
                'vm_type': self.get_vm_type(),
                'optimization_enabled': self.config.get('hardware_optimization', False),
                'jcvi_hardware_info': hardware_info,
                'xcpng_config': self.xapi_config
            }
        
        return {
            'vm_type': self.get_vm_type(),
            'optimization_enabled': False,
            'error': 'JCVI CLI integration not available',
            'xcpng_config': self.xapi_config
        }
