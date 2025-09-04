#!/usr/bin/env python3
"""
Interactive BioXen CLI for genome selection and VM management with bioxen-jcvi-vm-lib v0.0.1.
This is the migrated version from pylua_bioxen_vm_lib to bioxen-jcvi-vm-lib.
"""

import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional

try:
    import questionary
    from questionary import Choice
except ImportError:
    print("❌ questionary not installed. Install with: pip install questionary")
    sys.exit(1)

# New library imports - bioxen-jcvi-vm-lib
try:
    from hypervisor.core import BioXenHypervisor, VirtualMachine, ResourceAllocation
    from chassis import ChassisType, EcoliChassis, YeastChassis, BaseChassis
    from genome.parser import BioXenRealGenomeIntegrator, RealGenomeParser
    from genome.converter import BioXenGenomeConverter
    from genome.syn3a import Syn3AGenome, VMImageBuilder
    from genetics.circuits import (
        GeneticCircuit, CircuitFactory, CircuitValidator, 
        create_demo_circuit, create_metabolic_circuit
    )
    from monitoring.profiler import PerformanceProfiler, ResourceMetrics
    MODERN_VM_AVAILABLE = True
    print("✅ BioXen JCVI VM Library v0.0.1 loaded successfully")
except ImportError as e:
    print(f"⚠️ BioXen JCVI VM library not available: {e}")
    print("💡 Install with: pip install --index-url https://test.pypi.org/simple/ bioxen-jcvi-vm-lib")
    MODERN_VM_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('bioxen.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class InteractiveBioXen:
    """Interactive CLI for BioXen hypervisor and genome management with new JCVI library."""
    
    def __init__(self):
        # Initialize with new API
        self.hypervisor = None  # Will be BioXenHypervisor instance
        self.available_genomes = []
        self.chassis_type = ChassisType.ECOLI
        self.visualization_active = False
        
        if MODERN_VM_AVAILABLE:
            # Initialize new JCVI-based components (defer profiler until hypervisor is ready)
            self.genome_parser = RealGenomeParser()
            self.genome_converter = BioXenGenomeConverter()
            self.profiler = None  # Will be initialized when hypervisor is created
            self.circuit_factory = CircuitFactory()
            self.vm_image_builder = VMImageBuilder()
            logger.info("BioXen initialized with JCVI VM library v0.0.1")
        else:
            logger.warning("BioXen initialized without modern VM support")

    def _check_hypervisor(self):
        """Check if hypervisor is initialized."""
        if self.hypervisor is None:
            print("❌ Hypervisor not initialized. Select 'Initialize Hypervisor'.")
            return False
        return True

    def main_menu(self):
        """Display main menu."""
        while True:
            print("\n" + "="*60 + "\n🧬 BioXen JCVI Hypervisor v0.0.1\n" + "="*60)
            choices = [
                Choice("🖥️ Initialize Hypervisor", "init_hypervisor"),
                Choice("📊 Hypervisor Status", "status"),
                Choice("⚡ Create VM", "create_vm"),
                Choice("🗑️ Destroy VM", "destroy_vm"),
            ]
            if MODERN_VM_AVAILABLE:
                choices.extend([
                    Choice("🧬 Genetic Circuits", "genetic_circuits_menu"),
                    Choice("📊 Performance Profiling", "performance_profiling"),
                    Choice("🔬 Chassis Management", "chassis_management"),
                ])
            choices.append(Choice("❌ Exit", "exit"))
            
            action = questionary.select("Select action:", choices=choices, use_shortcuts=True).ask()
            if action is None or action == "exit":
                print("👋 Goodbye!")
                break
            try:
                getattr(self, action)()
            except KeyboardInterrupt:
                print("\n⚠️ Cancelled")
                continue
            except Exception as e:
                logger.error(f"Menu error: {e}")
                print(f"❌ Error: {e}")
                questionary.press_any_key_to_continue().ask()

    def init_hypervisor(self):
        """Initialize hypervisor."""
        if self.hypervisor and not questionary.confirm("Reinitialize hypervisor?").ask():
            return
        print("\n🚀 Initializing Hypervisor")
        if not self.select_chassis():
            print("❌ Cancelled")
            return
        try:
            print(f"\n🔄 Initializing {self.chassis_type.value}...")
            self.hypervisor = BioXenHypervisor(chassis_type=self.chassis_type)
            
            # Initialize profiler now that hypervisor is available
            if MODERN_VM_AVAILABLE and self.profiler is None:
                self.profiler = PerformanceProfiler(self.hypervisor)
                
            print(f"✅ Hypervisor initialized: {self.chassis_type.value}")
        except Exception as e:
            logger.error(f"Init error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def select_chassis(self):
        """Select chassis type."""
        chassis = questionary.select(
            "🔬 Select chassis:",
            choices=[
                Choice("🦠 E. coli (Prokaryotic)", ChassisType.ECOLI),
                Choice("🍄 Yeast (Eukaryotic)", ChassisType.YEAST),
                Choice("🧩 Orthogonal (Experimental)", ChassisType.ORTHOGONAL),
            ]
        ).ask()
        if chassis:
            self.chassis_type = chassis
            print(f"\n✅ {chassis.value} chassis selected")
        return chassis

    def status(self):
        """Display hypervisor status."""
        if not self._check_hypervisor():
            return
        print("\n📊 Hypervisor Status\n" + "="*60)
        
        # Get system resources
        resources = self.hypervisor.get_system_resources()
        print(f"Chassis: {self.chassis_type.value}")
        print(f"Total Ribosomes: {resources.get('total_ribosomes', 0)}")
        print(f"Available Ribosomes: {resources.get('available_ribosomes', 0)}")
        print(f"Active VMs: {resources.get('active_vms', 0)}")
        
        # Get VM list
        vms = self.hypervisor.list_vms()
        if not vms:
            print("No VMs running\n💡 Use 'Create VM'")
        else:
            print(f"\n🖥️ Virtual Machines ({len(vms)}):")
            for vm_id, vm_info in vms.items():
                try:
                    state = self.hypervisor.get_vm_state(vm_id)
                    print(f"   • {vm_id}: {state}")
                except Exception as e:
                    print(f"   • {vm_id}: <error getting state: {e}>")
        questionary.press_any_key_to_continue().ask()

    def create_vm(self):
        """Create a demo VM."""
        if not self._check_hypervisor():
            return
        
        print("\n⚡ Create VM")
        vm_id = questionary.text("VM ID:", default="demo_vm").ask()
        if not vm_id:
            return
        
        try:
            print(f"\n🔄 Creating '{vm_id}'...")
            resource_alloc = ResourceAllocation(
                memory_kb=1024, 
                boot_time_ms=100,
                ribosomes=4,
                atp_percentage=10.0
            )
            result = self.hypervisor.create_vm(vm_id, "syn3a_minimal", resource_alloc)
            if result:
                vm_state = self.hypervisor.get_vm_state(vm_id)
                print(f"✅ VM '{vm_id}' created successfully, state: {vm_state}")
            else:
                print(f"❌ Failed to create VM '{vm_id}'")
        except Exception as e:
            logger.error(f"VM error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def destroy_vm(self):
        """Destroy a VM."""
        if not self._check_hypervisor():
            return
        
        vms = self.hypervisor.list_vms()
        if not vms:
            print("❌ No VMs to destroy")
            return questionary.press_any_key_to_continue().ask()
        
        print("\n🗑️ Destroy VM")
        choices = [Choice(f"🖥️ {vm_id}", vm_id) for vm_id in vms.keys()]
        choices.append(Choice("🔙 Cancel", None))
        
        vm_id = questionary.select("Select VM to destroy:", choices=choices).ask()
        if not vm_id:
            return
        
        if questionary.confirm(f"⚠️ Really destroy '{vm_id}'?").ask():
            try:
                print(f"\n🔄 Destroying '{vm_id}'...")
                result = self.hypervisor.destroy_vm(vm_id)
                if result:
                    print(f"✅ '{vm_id}' destroyed")
                else:
                    print(f"❌ Failed to destroy '{vm_id}'")
            except Exception as e:
                logger.error(f"Destroy error: {e}")
                print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def genetic_circuits_menu(self):
        """Genetic circuits management menu."""
        while True:
            choices = [
                Choice("🔧 Create Demo Circuit", "create_demo_circuit"),
                Choice("🧬 Create Metabolic Circuit", "create_metabolic_circuit"),
                Choice("✅ Validate Circuit", "validate_circuit"),
                Choice("🔙 Back", "back")
            ]
            action = questionary.select("Genetic Circuits:", choices=choices).ask()
            if action is None or action == "back":
                break
            try:
                getattr(self, action)()
            except Exception as e:
                logger.error(f"Genetic circuits error: {e}")
                print(f"❌ Error: {e}")
                questionary.press_any_key_to_continue().ask()

    def create_demo_circuit(self):
        """Create a demo genetic circuit."""
        print("🔧 Creating demo genetic circuit...")
        try:
            circuit = create_demo_circuit()
            print(f"✅ Demo circuit created: {circuit}")
        except Exception as e:
            print(f"❌ Error creating demo circuit: {e}")
        questionary.press_any_key_to_continue().ask()

    def create_metabolic_circuit(self):
        """Create a metabolic circuit."""
        print("🧬 Creating metabolic circuit...")
        try:
            circuit = create_metabolic_circuit()
            print(f"✅ Metabolic circuit created: {circuit}")
        except Exception as e:
            print(f"❌ Error creating metabolic circuit: {e}")
        questionary.press_any_key_to_continue().ask()

    def validate_circuit(self):
        """Validate a genetic circuit."""
        print("✅ Circuit validation functionality")
        try:
            validator = CircuitValidator()
            print(f"📊 Circuit validator initialized: {validator}")
        except Exception as e:
            print(f"❌ Error with circuit validation: {e}")
        questionary.press_any_key_to_continue().ask()

    def performance_profiling(self):
        """Performance profiling with new monitoring capabilities."""
        if not self._check_hypervisor():
            return
        
        print("📊 Starting performance profiling...")
        try:
            # Get current system metrics
            resources = self.hypervisor.get_system_resources()
            vms = self.hypervisor.list_vms()
            
            print(f"🔋 System Resources:")
            print(f"   Total Ribosomes: {resources.get('total_ribosomes', 0)}")
            print(f"   Available Ribosomes: {resources.get('available_ribosomes', 0)}")
            print(f"   Active VMs: {resources.get('active_vms', 0)}")
            print(f"   ATP Allocated: {resources.get('total_atp_allocated', 0)}")
            
            # Use profiler for detailed metrics
            metrics = self.profiler.profile_system()
            print(f"\n📈 Performance Metrics:")
            for key, value in metrics.items():
                print(f"   {key}: {value}")
                
        except Exception as e:
            print(f"❌ Profiling error: {e}")
        
        questionary.press_any_key_to_continue().ask()

    def chassis_management(self):
        """Chassis management with new chassis types."""
        choices = []
        for chassis_type in ChassisType:
            choices.append(Choice(f"🧬 {chassis_type.value.title()}", chassis_type.value))
        choices.append(Choice("🔙 Back", "back"))
        
        action = questionary.select("Select chassis type:", choices=choices).ask()
        if action == "back" or action is None:
            return
            
        try:
            self.chassis_type = ChassisType(action)
            print(f"✅ Chassis type set to: {self.chassis_type.value}")
            
            # Initialize chassis-specific components
            if self.chassis_type == ChassisType.ECOLI:
                chassis = EcoliChassis()
            elif self.chassis_type == ChassisType.YEAST:
                chassis = YeastChassis()
            else:
                chassis = BaseChassis()
                
            chassis.initialize()
            print(f"🔧 {self.chassis_type.value.title()} chassis initialized")
            
        except Exception as e:
            print(f"❌ Chassis management error: {e}")
        
        questionary.press_any_key_to_continue().ask()

def main():
    """Main entry point."""
    print("🧬 BioXen JCVI Interactive CLI")
    print("📚 Library: bioxen-jcvi-vm-lib v0.0.1")
    print("🔄 Migration from pylua_bioxen_vm_lib completed")
    
    cli = InteractiveBioXen()
    try:
        cli.main_menu()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
