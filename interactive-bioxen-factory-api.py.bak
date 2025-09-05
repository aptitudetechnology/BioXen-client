#!/usr/bin/env python3
"""
Interactive BioXen CLI for genome selection and VM management with bioxen-jcvi-vm-lib v0.0.5.
Factory Pattern API Implementation - Hypervisor-Focused Production Library.
"""

import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional

# Add src path for the factory API
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    import questionary
    from questionary import Choice
except ImportError:
    print("❌ questionary not installed. Install with: pip install questionary")
    sys.exit(1)

# New Factory Pattern API imports - bioxen-jcvi-vm-lib v0.0.5 (Hypervisor-Focused)
try:
    from src.api import (
        create_bio_vm, 
        BioResourceManager, 
        ConfigManager,
        get_supported_biological_types,
        get_supported_vm_types,
        validate_biological_type,
        validate_vm_type
    )
    from src.api.biological_vm import BiologicalVM
    
    # For v0.0.5 hypervisor-focused architecture, avoid direct hypervisor imports
    # All functionality should go through the clean API layer
    
    FACTORY_API_AVAILABLE = True
    print("✅ BioXen JCVI VM Library v0.0.5 (Hypervisor-Focused) Factory API loaded successfully")
except ImportError as e:
    print(f"⚠️ BioXen JCVI VM library Factory API not available: {e}")
    print("💡 Make sure you're running from the correct directory with src/api/ available")
    FACTORY_API_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('bioxen.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class InteractiveBioXenFactoryAPI:
    """Interactive CLI for BioXen Factory Pattern API v0.0.5 (Hypervisor-Focused)."""
    
    def __init__(self):
        # Factory Pattern API state for v0.0.5
        self.active_vms = {}  # Dict[str, BiologicalVM] - track created VMs
        self.selected_biological_type = "syn3a"  # Default biological type
        self.vm_type = "basic"  # Default infrastructure type (basic/xcpng)
        
        if FACTORY_API_AVAILABLE:
            # Initialize Factory API components
            self.supported_bio_types = get_supported_biological_types()
            self.supported_vm_types = get_supported_vm_types()
            logger.info(f"BioXen Factory API v0.0.5 initialized - Bio types: {self.supported_bio_types}, VM types: {self.supported_vm_types}")
        else:
            logger.warning("BioXen initialized without Factory API support")
            self.supported_bio_types = ["syn3a", "ecoli", "minimal_cell"]
            self.supported_vm_types = ["basic", "xcpng"]

    def main_menu(self):
        """Display main menu with Factory Pattern API."""
        while True:
            print("\n" + "="*70)
            print("🧬 BioXen Factory Pattern API v0.0.5 (Hypervisor-Focused)")
            print(f"🔬 Current: {self.selected_biological_type} | {self.vm_type}")
            print(f"🖥️ Active VMs: {len(self.active_vms)}")
            print("="*70)
            
            choices = [
                Choice("🔬 Select Biological Type", "select_biological_type"),
                Choice("⚡ Create Biological VM", "create_biological_vm"),
                Choice("📊 Manage VMs", "manage_vms"),
                Choice("🔧 VM Operations", "vm_operations_menu"),
                Choice("📈 Resource Management", "resource_management"),
                Choice("🧬 Biological Metrics", "biological_metrics_menu"),
                Choice("⚙️ Configuration", "configuration_menu"),
                Choice("ℹ️ Factory API Info", "api_info"),
                Choice("❌ Exit", "exit")
            ]
            
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

    def select_biological_type(self):
        """Select biological type for VM creation."""
        choices = []
        for bio_type in self.supported_bio_types:
            status = "✅" if bio_type == self.selected_biological_type else "  "
            choices.append(Choice(f"{status} {bio_type.title()}", bio_type))
        choices.append(Choice("🔙 Back", "back"))
        
        action = questionary.select("Select biological type:", choices=choices).ask()
        if action != "back" and action is not None:
            self.selected_biological_type = action
            print(f"✅ Selected biological type: {action}")
            
            # Load default configuration for this type
            if FACTORY_API_AVAILABLE:
                try:
                    config = ConfigManager.load_defaults(action)
                    print(f"📋 Loaded configuration: {config}")
                except Exception as e:
                    print(f"⚠️ Could not load config: {e}")
        
        questionary.press_any_key_to_continue().ask()

    def create_biological_vm(self):
        """Create a biological VM using the Factory Pattern API v0.0.5."""
        if not FACTORY_API_AVAILABLE:
            print("❌ Factory API not available")
            return
        
        print(f"\n🧬 Creating Biological VM (v0.0.5 Hypervisor-Focused)")
        print(f"🔬 Biological Type: {self.selected_biological_type}")
        print(f"🖥️ VM Type: {self.vm_type}")
        
        vm_id = questionary.text("Enter VM ID:", default=f"vm_{self.selected_biological_type}_{int(time.time() % 10000)}").ask()
        if not vm_id:
            return
            
        try:
            print(f"🔄 Creating VM: {vm_id}")
            
            # Use Factory Pattern API v0.0.5
            vm = create_bio_vm(vm_id, self.selected_biological_type, self.vm_type)
            
            print(f"✅ VM created successfully: {vm_id}")
            print(f"   Type: {vm.get_vm_type()}")
            print(f"   Biological: {vm.get_biological_type()}")
            
            # Store reference
            self.active_vms[vm_id] = vm
            
            # Start the VM and allocate initial resources (v0.0.5 enhancement)
            if questionary.confirm("Start VM now?").ask():
                if vm.start():
                    print(f"🚀 VM {vm_id} started successfully")
                    
                    # v0.0.5: Allocate default resources
                    if questionary.confirm("Allocate default resources?").ask():
                        resources = {"atp": 50.0, "ribosomes": 10}
                        if vm.allocate_resources(resources):
                            print(f"⚡ Resources allocated: {resources}")
                        else:
                            print("⚠️ Resource allocation failed")
                else:
                    print(f"❌ Failed to start VM {vm_id}")
            
        except Exception as e:
            logger.error(f"VM creation error: {e}")
            print(f"❌ Error creating VM: {e}")
        
        questionary.press_any_key_to_continue().ask()

    def biological_metrics_menu(self):
        """New v0.0.5 feature: Biological metrics monitoring."""
        if not self.active_vms:
            print("❌ No active VMs for metrics monitoring")
            questionary.press_any_key_to_continue().ask()
            return
        
        # Select VM for metrics
        choices = []
        for vm_id in self.active_vms.keys():
            choices.append(Choice(f"🖥️ {vm_id}", vm_id))
        choices.append(Choice("🔙 Back", "back"))
        
        vm_id = questionary.select("Select VM for biological metrics:", choices=choices).ask()
        if vm_id == "back" or vm_id is None:
            return
            
        vm = self.active_vms[vm_id]
        
        try:
            print(f"\n🧬 Biological Metrics for {vm_id}")
            print("="*50)
            
            # v0.0.5 API: Get biological metrics
            metrics = vm.get_biological_metrics()
            for key, value in metrics.items():
                print(f"   {key}: {value}")
            
            print("\n📊 Resource Usage:")
            usage = vm.get_resource_usage()
            for key, value in usage.items():
                print(f"   {key}: {value}")
                
        except Exception as e:
            logger.error(f"Metrics error: {e}")
            print(f"❌ Error getting metrics: {e}")
        
        questionary.press_any_key_to_continue().ask()

    def manage_vms(self):
        """Manage active biological VMs."""
        if not self.active_vms:
            print("❌ No active VMs")
            questionary.press_any_key_to_continue().ask()
            return
        
        print(f"\n📊 Active VMs ({len(self.active_vms)})")
        print("="*50)
        
        for vm_id, vm in self.active_vms.items():
            try:
                status = vm.get_status()
                print(f"🖥️ {vm_id}")
                print(f"   Type: {vm.get_vm_type()} | Bio: {vm.get_biological_type()}")
                print(f"   Status: {status}")
                print()
            except Exception as e:
                print(f"❌ Error getting status for {vm_id}: {e}")
        
        questionary.press_any_key_to_continue().ask()

    def vm_operations_menu(self):
        """VM operations menu."""
        if not self.active_vms:
            print("❌ No active VMs")
            questionary.press_any_key_to_continue().ask()
            return
        
        while True:
            # Create choices from active VMs
            choices = []
            for vm_id in self.active_vms.keys():
                choices.append(Choice(f"🖥️ {vm_id}", vm_id))
            choices.append(Choice("🔙 Back", "back"))
            
            vm_id = questionary.select("Select VM for operations:", choices=choices).ask()
            if vm_id == "back" or vm_id is None:
                break
                
            self.vm_operations_for_vm(vm_id)

    def vm_operations_for_vm(self, vm_id: str):
        """Operations for a specific VM."""
        vm = self.active_vms.get(vm_id)
        if not vm:
            print(f"❌ VM {vm_id} not found")
            return
        
        while True:
            choices = [
                Choice("🚀 Start", "start"),
                Choice("⏸️ Pause", "pause"),
                Choice("▶️ Resume", "resume"),
                Choice("📊 Status", "status"),
                Choice("⚡ Allocate Resources", "allocate_resources"),
                Choice("📈 Resource Usage", "resource_usage"),
                Choice("🧬 Execute Process", "execute"),
                Choice("📦 Install Package", "install_package"),
                Choice("� Biological Metrics", "metrics"),
                Choice("🗑️ Destroy", "destroy"),
                Choice("🔙 Back", "back")
            ]
            
            action = questionary.select(f"Operations for {vm_id}:", choices=choices).ask()
            if action == "back" or action is None:
                break
                
            try:
                if action == "start":
                    result = vm.start()
                    print(f"{'✅' if result else '❌'} Start result: {result}")
                elif action == "pause":
                    result = vm.pause()
                    print(f"{'✅' if result else '❌'} Pause result: {result}")
                elif action == "resume":
                    result = vm.resume()
                    print(f"{'✅' if result else '❌'} Resume result: {result}")
                elif action == "status":
                    status = vm.get_status()
                    print(f"📊 Status: {status}")
                elif action == "allocate_resources":
                    # v0.0.5 enhanced resource allocation
                    atp = questionary.text("ATP allocation (0-100%):", default="50.0").ask()
                    ribosomes = questionary.text("Ribosome count:", default="10").ask()
                    if atp and ribosomes:
                        resources = {"atp": float(atp), "ribosomes": int(ribosomes)}
                        result = vm.allocate_resources(resources)
                        print(f"{'✅' if result else '❌'} Resource allocation: {resources}")
                elif action == "resource_usage":
                    # v0.0.5 resource usage monitoring
                    usage = vm.get_resource_usage()
                    print(f"📈 Resource Usage: {usage}")
                elif action == "execute":
                    process = questionary.text("Enter biological process code:").ask()
                    if process:
                        result = vm.execute_biological_process(process)
                        print(f"🧬 Process result: {result}")
                elif action == "install_package":
                    package = questionary.text("Enter package name:").ask()
                    if package:
                        result = vm.install_biological_package(package)
                        print(f"📦 Install result: {result}")
                elif action == "metrics":
                    # v0.0.5 biological metrics
                    metrics = vm.get_biological_metrics()
                    print(f"� Biological Metrics: {metrics}")
                elif action == "destroy":
                    if questionary.confirm(f"Destroy VM {vm_id}?").ask():
                        result = vm.destroy()
                        if result:
                            del self.active_vms[vm_id]
                            print(f"🗑️ VM {vm_id} destroyed")
                            break
                        else:
                            print(f"❌ Failed to destroy VM {vm_id}")
                            
            except Exception as e:
                logger.error(f"VM operation error: {e}")
                print(f"❌ Error: {e}")
            
            if action != "destroy":  # Don't pause if we're going back after destroy
                questionary.press_any_key_to_continue().ask()

    def resource_management(self):
        """Resource management using BioResourceManager."""
        if not self.active_vms:
            print("❌ No active VMs for resource management")
            questionary.press_any_key_to_continue().ask()
            return
        
        if not FACTORY_API_AVAILABLE:
            print("❌ Factory API not available for resource management")
            questionary.press_any_key_to_continue().ask()
            return
        
        # Select VM for resource management
        choices = []
        for vm_id in self.active_vms.keys():
            choices.append(Choice(f"🖥️ {vm_id}", vm_id))
        choices.append(Choice("🔙 Back", "back"))
        
        vm_id = questionary.select("Select VM for resource management:", choices=choices).ask()
        if vm_id == "back" or vm_id is None:
            return
            
        vm = self.active_vms[vm_id]
        
        try:
            # Create resource manager for the VM
            manager = BioResourceManager(vm)
            
            while True:
                choices = [
                    Choice("🔋 Allocate ATP", "allocate_atp"),
                    Choice("🧬 Allocate Ribosomes", "allocate_ribosomes"),
                    Choice("⚡ Optimize Resources", "optimize"),
                    Choice("📊 Resource Usage", "usage"),
                    Choice("📈 Available Resources", "available"),
                    Choice("🔙 Back", "back")
                ]
                
                action = questionary.select(f"Resource management for {vm_id}:", choices=choices).ask()
                if action == "back" or action is None:
                    break
                    
                if action == "allocate_atp":
                    atp = questionary.text("ATP allocation (0-100%):", default="70.0").ask()
                    if atp:
                        # v0.0.5: Use VM's direct resource allocation
                        resources = {"atp": float(atp)}
                        result = manager.vm.allocate_resources(resources)
                        print(f"🔋 ATP allocated: {atp}% - {'✅' if result else '❌'}")
                elif action == "allocate_ribosomes":
                    ribosomes = questionary.text("Ribosome count:", default="15").ask()
                    if ribosomes:
                        # v0.0.5: Use VM's direct resource allocation
                        resources = {"ribosomes": int(ribosomes)}
                        result = manager.vm.allocate_resources(resources)
                        print(f"🧬 Ribosomes allocated: {ribosomes} - {'✅' if result else '❌'}")
                elif action == "optimize":
                    manager.optimize_resources_for_biological_type()
                    print("⚡ Resources optimized for biological type")
                elif action == "usage":
                    # v0.0.5: Use VM's direct resource usage
                    usage = manager.vm.get_resource_usage()
                    print(f"📊 Resource usage: {usage}")
                elif action == "available":
                    available = manager.get_available_resources()
                    print(f"📈 Available resources: {available}")
                
                questionary.press_any_key_to_continue().ask()
                
        except Exception as e:
            logger.error(f"Resource management error: {e}")
            print(f"❌ Error: {e}")
            questionary.press_any_key_to_continue().ask()

    def configuration_menu(self):
        """Configuration management menu."""
        while True:
            choices = [
                Choice("🔬 Load Bio Type Defaults", "load_defaults"),
                Choice("✅ Validate Configuration", "validate_config"),
                Choice("🔧 Set VM Type", "set_vm_type"),
                Choice("📋 Show Current Config", "show_config"),
                Choice("🔙 Back", "back")
            ]
            
            action = questionary.select("Configuration:", choices=choices).ask()
            if action == "back" or action is None:
                break
                
            try:
                if action == "load_defaults":
                    if FACTORY_API_AVAILABLE:
                        config = ConfigManager.load_defaults(self.selected_biological_type)
                        print(f"📋 Defaults for {self.selected_biological_type}: {config}")
                    else:
                        print("❌ Factory API not available")
                elif action == "validate_config":
                    # Create a sample config to validate
                    config = {"biological_type": self.selected_biological_type, "vm_type": self.vm_type}
                    if FACTORY_API_AVAILABLE:
                        is_valid = ConfigManager.validate_config(config, self.vm_type)
                        print(f"✅ Configuration valid: {is_valid}")
                    else:
                        print("❌ Factory API not available")
                elif action == "set_vm_type":
                    choices = []
                    for vm_type in self.supported_vm_types:
                        status = "✅" if vm_type == self.vm_type else "  "
                        choices.append(Choice(f"{status} {vm_type}", vm_type))
                    
                    new_type = questionary.select("Select VM type:", choices=choices).ask()
                    if new_type and (not FACTORY_API_AVAILABLE or validate_vm_type(new_type)):
                        self.vm_type = new_type
                        print(f"🖥️ VM type set to: {new_type}")
                elif action == "show_config":
                    print(f"🔬 Biological Type: {self.selected_biological_type}")
                    print(f"🖥️ VM Type: {self.vm_type}")
                    print(f"🖥️ Active VMs: {len(self.active_vms)}")
                    print(f"⚙️ Factory API: {'✅ Available' if FACTORY_API_AVAILABLE else '❌ Not Available'}")
                    
            except Exception as e:
                logger.error(f"Configuration error: {e}")
                print(f"❌ Error: {e}")
            
            questionary.press_any_key_to_continue().ask()

    def api_info(self):
        """Display Factory API information for v0.0.5."""
        print("\n" + "="*60)
        print("🧬 BioXen Factory Pattern API v0.0.5 Information")
        print("   (Hypervisor-Focused Production Library)")
        print("="*60)
        print(f"📊 Status: {'✅ Available' if FACTORY_API_AVAILABLE else '❌ Not Available'}")
        print(f"🔬 Supported Biological Types: {', '.join(self.supported_bio_types)}")
        print(f"🖥️ Supported VM Types: {', '.join(self.supported_vm_types)}")
        print(f"⚡ Active VMs: {len(self.active_vms)}")
        
        if FACTORY_API_AVAILABLE:
            print("\n🔧 Factory API v0.0.5 Usage:")
            print("   vm = create_bio_vm(vm_id, biological_type, vm_type)")
            print("   vm.allocate_resources({'atp': 50.0, 'ribosomes': 10})")
            print("   usage = vm.get_resource_usage()")
            print("   metrics = vm.get_biological_metrics()")
            print("   manager = BioResourceManager(vm)")
            print("   config = ConfigManager.load_defaults(biological_type)")
            
            print("\n🏗️ v0.0.5 Hypervisor-Focused Features:")
            print("   ✅ Clean dependencies (JCVI excluded)")
            print("   ✅ Complete VM lifecycle management")
            print("   ✅ Enhanced resource allocation")
            print("   ✅ Biological metrics monitoring")
            print("   ✅ Multi-chassis support")
            print("   ✅ Production-ready hypervisor")
        else:
            print("\n💡 To use the Factory API v0.0.5:")
            print("   1. Ensure src/api/ directory exists")
            print("   2. Install bioxen-jcvi-vm-lib v0.0.5 library")
            print("   3. Run from correct working directory")
        
        questionary.press_any_key_to_continue().ask()

if __name__ == "__main__":
    bioxen = InteractiveBioXenFactoryAPI()
    bioxen.main_menu()
