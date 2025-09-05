from typing import Dict, Any, Optional
from .biological_vm import BiologicalVM

class BioResourceManager:
    """
    Unified resource management wrapper for biological VMs.
    Mirrors pylua resource management patterns.
    """
    
    def __init__(self, vm: Optional[BiologicalVM] = None):
        """
        Initialize resource manager.
        
        Args:
            vm: BiologicalVM instance. If None, creates a standalone manager
                that requires explicit VM binding before resource operations.
        """
        self.vm = vm
        self.hypervisor = vm.hypervisor if vm else None
    
    def bind_vm(self, vm: BiologicalVM) -> None:
        """
        Bind a VM to this resource manager.
        
        Args:
            vm: BiologicalVM instance to bind
        """
        self.vm = vm
        self.hypervisor = vm.hypervisor
    
    def _ensure_vm_bound(self) -> bool:
        """Ensure a VM is bound before performing operations."""
        if self.vm is None or self.hypervisor is None:
            raise RuntimeError("No VM bound to resource manager. Call bind_vm() first.")
        return True
    
    def allocate_atp(self, percentage: float) -> bool:
        """Allocate ATP resources - universal biological resource."""
        self._ensure_vm_bound()
        return self.hypervisor.allocate_atp(self.vm.vm_id, percentage)
    
    def allocate_ribosomes(self, count: int) -> bool:
        """Allocate ribosomes for protein synthesis."""
        self._ensure_vm_bound()
        return self.hypervisor.allocate_ribosomes(self.vm.vm_id, count)
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage."""
        self._ensure_vm_bound()
        return self.hypervisor.get_resource_usage(self.vm.vm_id)
    
    def get_available_resources(self) -> Dict[str, Any]:
        """Get available resources for allocation."""
        self._ensure_vm_bound()
        return self.hypervisor.get_available_resources(self.vm.vm_id)
    
    def optimize_resources_for_biological_type(self) -> bool:
        """Optimize resource allocation based on biological organism type."""
        self._ensure_vm_bound()
        if self.vm.biological_type == "syn3a":
            return self._optimize_for_minimal_genome()
        elif self.vm.biological_type == "ecoli":
            return self._optimize_for_prokaryote()
        elif self.vm.biological_type == "minimal_cell":
            return self._optimize_for_minimal_cell()
        return False
    
    def _optimize_for_minimal_genome(self) -> bool:
        """Optimize resources for minimal genome (Syn3A)."""
        # Minimal resource allocation for essential functions only
        return (self.allocate_atp(60.0) and 
                self.allocate_ribosomes(10))
    
    def _optimize_for_prokaryote(self) -> bool:
        """Optimize resources for prokaryotic organism (E.coli)."""
        # Standard bacterial resource allocation
        return (self.allocate_atp(80.0) and 
                self.allocate_ribosomes(25))
    
    def _optimize_for_minimal_cell(self) -> bool:
        """Optimize resources for minimal cellular functions."""
        # Basic cellular function resource allocation
        return (self.allocate_atp(50.0) and 
                self.allocate_ribosomes(8))
