from typing import Dict, Any, Optional, List
from .biological_vm import BiologicalVM, BasicBiologicalVM, XCPngBiologicalVM
from ..hypervisor.core import BioXenHypervisor, ChassisType

def create_bio_vm(vm_id: str, biological_type: str, vm_type: str = "basic", config: Optional[Dict[str, Any]] = None) -> BiologicalVM:
    """
    Factory function to create biological VMs with VM type support.
    Mirrors pylua_bioxen_vm_lib create_vm() function exactly with vm_type parameter.
    
    Args:
        vm_id: Unique identifier for the VM
        biological_type: Type of biological organism ("syn3a", "ecoli", "minimal_cell")
        vm_type: VM infrastructure type ("basic", "xcpng", "jcvi_optimized") - default "basic"
        config: Optional configuration dictionary (required for xcpng)
    
    Returns:
        BiologicalVM instance of the appropriate type
    
    Raises:
        ValueError: If biological_type or vm_type is not supported
    """
    supported_biological_types = ["syn3a", "ecoli", "minimal_cell"]
    if biological_type not in supported_biological_types:
        raise ValueError(f"Unsupported biological type: {biological_type}. Supported: {supported_biological_types}")
    
    if vm_type not in ["basic", "xcpng", "jcvi_optimized"]:
        raise ValueError(f"Unsupported VM type: {vm_type}. Supported: ['basic', 'xcpng', 'jcvi_optimized']")
    
    if vm_type == "xcpng" and not config:
        raise ValueError("XCP-ng VM type requires config parameter with xcpng_config")
    
    config = config or {}
    
    # Configure JCVI settings based on VM type
    if vm_type == "jcvi_optimized":
        # Enable all JCVI features with hardware optimization
        config.setdefault('enable_jcvi', True)
        config.setdefault('jcvi_cli_enabled', True)
        config.setdefault('hardware_optimization', True)
        config.setdefault('fallback_mode', True)
        # Use XCPng for better isolation and resource management
        actual_vm_type = "xcpng"
        config.setdefault('xcpng_config', {})
    else:
        # Enable JCVI by default for all VM types
        config.setdefault('enable_jcvi', True)
        config.setdefault('jcvi_cli_enabled', True)
        config.setdefault('hardware_optimization', False)
        config.setdefault('fallback_mode', True)
        actual_vm_type = vm_type
    
    # Create hypervisor with appropriate chassis (mirrors pylua XCP-ng setup)
    chassis_type = _get_chassis_for_biological_type(biological_type)
    hypervisor = BioXenHypervisor(chassis_type=chassis_type)
    
    # Create VM in hypervisor first (mirrors pylua template creation)
    vm_template = _create_vm_template(biological_type, actual_vm_type, config)
    
    # For hypervisor, we need the genome template as string (compatibility)
    genome_template_name = vm_template.get('genome_template', biological_type)
    hypervisor.create_vm(vm_id, genome_template=genome_template_name)
    
    # Create and return wrapper VM instance based on actual_vm_type (infrastructure-focused)
    if actual_vm_type == "basic":
        # For basic VMs, use BasicBiologicalVM with biological_type parameter
        return BasicBiologicalVM(vm_id, biological_type, hypervisor, config)
    elif actual_vm_type == "xcpng":
        # For XCP-ng VMs, use XCPngBiologicalVM with biological_type parameter  
        vm = XCPngBiologicalVM(vm_id, biological_type, hypervisor, config)
        if vm_type == "jcvi_optimized":
            # Add JCVI optimization marker
            vm.vm_id = f"{vm_id}_jcvi_optimized"
        return vm

def create_biological_vm(vm_type: str = "basic", config: Optional[Dict[str, Any]] = None) -> BiologicalVM:
    """
    Simplified factory function for Phase 1.1 JCVI integration.
    Creates biological VMs with sensible defaults and JCVI integration.
    
    Args:
        vm_type: VM infrastructure type ("basic", "xcpng", "jcvi_optimized") - default "basic"
        config: Optional configuration dictionary
    
    Returns:
        BiologicalVM instance with JCVI integration enabled
    """
    if config is None:
        config = {}
    
    # Default to syn3a biological type for simplified interface
    biological_type = config.get('biological_type', 'syn3a')
    
    # Generate automatic VM ID if not provided
    vm_id = config.get('vm_id', f"{vm_type}_{biological_type}_vm")
    
    return create_bio_vm(vm_id, biological_type, vm_type, config)

def _get_chassis_for_biological_type(biological_type: str) -> ChassisType:
    """Map biological type to appropriate chassis - mirrors pylua config mapping."""
    chassis_mapping = {
        "syn3a": ChassisType.ECOLI,  # Syn3A runs on E.coli chassis
        "ecoli": ChassisType.ECOLI,
        "minimal_cell": ChassisType.ECOLI
    }
    return chassis_mapping.get(biological_type, ChassisType.ECOLI)

def _create_vm_template(biological_type: str, vm_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create VM template based on biological type, VM type and config.
    Mirrors pylua template creation pattern with XCP-ng support.
    """
    # Delegate to existing genome integration logic
    from ..genome.parser import BioXenRealGenomeIntegrator
    from pathlib import Path
    
    genome_mapping = {
        "syn3a": "genomes/syn3a.genome",
        "ecoli": "genomes/ecoli.genome", 
        "minimal_cell": "genomes/minimal.genome"
    }
    
    genome_file = genome_mapping.get(biological_type)
    if not genome_file:
        raise ValueError(f"No genome file mapping for biological type: {biological_type}")
    
    # Convert to Path object and check if exists
    genome_path = Path(genome_file)
    if not genome_path.exists():
        print(f"⚠️ Genome file {genome_file} not found, creating placeholder")
        genome_path.parent.mkdir(parents=True, exist_ok=True)
        with open(genome_path, 'w') as f:
            f.write(f"# Placeholder genome for {biological_type}\n")
            f.write(f"organism={biological_type}\n")
            f.write("genes=100\n")
    
    integrator = BioXenRealGenomeIntegrator(str(genome_path))
    integrator = BioXenRealGenomeIntegrator(str(genome_path))
    template = integrator.create_vm_template()
    
    # Add VM type specific configuration
    template['vm_type'] = vm_type
    template['biological_type'] = biological_type
    template['genome_template'] = biological_type  # Add genome template name for hypervisor
    
    if vm_type == "xcpng":
        # Add XCP-ng specific template parameters
        xcpng_config = config.get('xcpng_config', {})
        template.update({
            'xcpng_template': xcpng_config.get('template_name', 'bioxen-bio-template'),
            'xcpng_network': xcpng_config.get('network_uuid'),
            'xcpng_storage': xcpng_config.get('storage_repository'),
            'vm_memory': xcpng_config.get('vm_memory', '2GB'),
            'vm_vcpus': xcpng_config.get('vm_vcpus', 2)
        })
    
    return template

# Additional factory functions following pylua pattern
def get_supported_biological_types() -> List[str]:
    """Get list of supported biological types."""
    return ["syn3a", "ecoli", "minimal_cell"]

def get_supported_vm_types() -> List[str]:
    """Get list of supported VM infrastructure types - mirrors pylua capability reporting."""
    return ["basic", "xcpng"]

def validate_biological_type(biological_type: str) -> bool:
    """Validate biological type is supported."""
    return biological_type in get_supported_biological_types()

def validate_vm_type(vm_type: str) -> bool:
    """Validate VM infrastructure type is supported - pylua validation pattern."""
    return vm_type in get_supported_vm_types()
