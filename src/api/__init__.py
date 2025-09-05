"""
BioXen Factory Pattern API

Infrastructure-focused biological VM management following pylua_bioxen_vm_lib patterns.
Phase 1.1: JCVI Integration - Unified API access to JCVI functionality.
"""

from typing import Optional
from .biological_vm import BiologicalVM, BasicBiologicalVM, XCPngBiologicalVM
from .factory import create_bio_vm, create_biological_vm, get_supported_biological_types, get_supported_vm_types, validate_biological_type, validate_vm_type
from .resource_manager import BioResourceManager
from .config_manager import ConfigManager
from .jcvi_manager import JCVIManager, create_jcvi_manager

# Public API exports (mirrors pylua exports)
__all__ = [
    # Core VM classes
    'BiologicalVM',
    'BasicBiologicalVM', 
    'XCPngBiologicalVM',
    
    # Factory functions
    'create_bio_vm',
    'create_biological_vm',  # Phase 1.1 simplified interface
    'get_supported_biological_types',
    'get_supported_vm_types',
    'validate_biological_type',
    'validate_vm_type',
    
    # Management classes
    'BioResourceManager',
    'ConfigManager',
    
    # JCVI Integration (Phase 1.1)
    'JCVIManager',
    'create_jcvi_manager'
]

# Convenience functions (mirrors pylua convenience patterns)
def quick_start_vm(biological_type: str, vm_id: Optional[str] = None) -> BiologicalVM:
    """Quick start a basic biological VM with default settings."""
    vm_id = vm_id or f"quick_{biological_type}"
    return create_bio_vm(vm_id, biological_type)

def quick_start_jcvi_vm(biological_type: str = "syn3a", vm_id: Optional[str] = None) -> BiologicalVM:
    """Quick start a JCVI-optimized VM with default settings."""
    config = {
        'biological_type': biological_type,
        'vm_id': vm_id or f"jcvi_{biological_type}"
    }
    return create_biological_vm(vm_type="jcvi_optimized", config=config)

# Alias for pylua compatibility
create_vm = create_bio_vm  # Alias for pylua compatibility
