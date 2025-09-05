"""
Base chassis classes and types for BioXen biological virtualization.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

class ChassisType(Enum):
    """Supported chassis types for biological virtualization"""
    ECOLI = "ecoli"
    YEAST = "yeast"
    ORTHOGONAL = "orthogonal"  # Synthetic cell chassis
    MAMMALIAN = "mammalian"  # Future support
    PLANT = "plant"          # Future support

@dataclass
class ChassisCapabilities:
    """Defines the capabilities and resources of a chassis"""
    max_ribosomes: int
    has_nucleus: bool
    has_mitochondria: bool
    has_chloroplasts: bool
    has_endoplasmic_reticulum: bool
    max_concurrent_vms: int
    memory_architecture: str  # "prokaryotic" or "eukaryotic"
    metabolic_pathways: List[str]
    protein_processing: List[str]  # post-translational modifications

@dataclass
class ChassisResources:
    """Current resource allocation for a chassis"""
    available_ribosomes: int
    available_atp: float
    available_memory_kb: int
    organelle_capacity: Dict[str, int]
    
class BaseChassis(ABC):
    """Abstract base class for all chassis implementations"""
    
    def __init__(self, chassis_id: str):
        self.chassis_id = chassis_id
        self.chassis_type: ChassisType = None
        self.capabilities: ChassisCapabilities = None
        self.current_resources: ChassisResources = None
        self.active_vms: Dict[str, Any] = {}
        
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the chassis for virtualization"""
        pass
        
    @abstractmethod
    def get_capabilities(self) -> ChassisCapabilities:
        """Get the capabilities of this chassis"""
        pass
        
    @abstractmethod
    def allocate_resources(self, vm_id: str, resource_request: Dict[str, Any]) -> bool:
        """Allocate resources to a VM"""
        pass
        
    @abstractmethod
    def deallocate_resources(self, vm_id: str) -> bool:
        """Deallocate resources from a VM"""
        pass
        
    @abstractmethod
    def get_resource_status(self) -> ChassisResources:
        """Get current resource utilization"""
        pass
        
    @abstractmethod
    def create_isolation_environment(self, vm_id: str) -> bool:
        """Create isolation environment for a VM"""
        pass
        
    @abstractmethod
    def cleanup_vm_environment(self, vm_id: str) -> bool:
        """Clean up VM environment after termination"""
        pass
        
    def get_chassis_info(self) -> Dict[str, Any]:
        """Get chassis information summary"""
        return {
            "chassis_id": self.chassis_id,
            "chassis_type": self.chassis_type.value if self.chassis_type else "unknown",
            "capabilities": self.capabilities,
            "current_resources": self.current_resources,
            "active_vms": len(self.active_vms),
            "max_vms": self.capabilities.max_concurrent_vms if self.capabilities else 0
        }
