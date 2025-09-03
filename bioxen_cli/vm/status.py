from datetime import datetime
from typing import Dict, List, Optional


class VMStatus:
    def __init__(self, profile, vm_type="basic"):
        self.profile = profile
        self.vm_type = vm_type  # "basic" or "xcpng" (0.1.19 multi-VM types)
        self.running = False
        self.attached = False
        self.pid = None
        self.created_at = datetime.now()
        self.packages_installed = 0
        # XCP-ng specific fields (Phase 1 placeholder support)
        self.xcpng_config = {} if vm_type == "xcpng" else None

    def get_uptime(self) -> str:
        delta = datetime.now() - self.created_at
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        return f"{delta.days}d {hours}h {minutes}m"


class VMStatusTracker:
    """Tracks status of all VMs."""
    
    def __init__(self):
        self.vm_status: Dict[str, VMStatus] = {}
    
    def add_vm(self, vm_id: str, profile: str, vm_type: str = "basic") -> VMStatus:
        """Add a new VM to tracking."""
        status = VMStatus(profile, vm_type)
        self.vm_status[vm_id] = status
        return status
    
    def get_vm(self, vm_id: str) -> Optional[VMStatus]:
        """Get VM status by ID."""
        return self.vm_status.get(vm_id)
    
    def remove_vm(self, vm_id: str) -> bool:
        """Remove VM from tracking."""
        if vm_id in self.vm_status:
            del self.vm_status[vm_id]
            return True
        return False
    
    def get_running_vms(self) -> List[str]:
        """Get list of running VM IDs."""
        return [vm_id for vm_id, status in self.vm_status.items() if status.running]
    
    def get_available_vms(self) -> List[str]:
        """Get list of all VM IDs."""
        return list(self.vm_status.keys())
    
    def get_attached_vms(self) -> List[str]:
        """Get list of attached VM IDs."""
        return [vm_id for vm_id, status in self.vm_status.items() if status.attached]