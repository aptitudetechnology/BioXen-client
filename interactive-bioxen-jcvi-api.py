#!/usr/bin/env python3
"""
Interactive BioXen CLI with Factory Pattern API and JCVI Integration.
Updated compatibility with chassis selection
"""

import sys
import time
import logging
import typing
import os
from pathlib import Path
from typing import List, Dict, Optional

# Import the working genome downloader
try:
    from download_genomes import (
        MINIMAL_GENOMES, 
        download_genome, 
        list_available_genomes,
        download_and_convert_genome,
        interactive_genome_selection
    )
    REAL_GENOME_DOWNLOADER_AVAILABLE = True
    print("✅ Real genome downloader available")
except ImportError as e:
    print(f"⚠️  Real genome downloader not available: {e}")
    REAL_GENOME_DOWNLOADER_AVAILABLE = False

# Fix typing._ClassVar compatibility issue for bioxen-jcvi-vm-lib
if not hasattr(typing, '_ClassVar'):
    typing._ClassVar = typing.ClassVar

# Add the correct path for the API module
sys.path.insert(0, '/home/chris/BioXen-luavm/venv/lib/python3.10/site-packages')

try:
    import questionary
    from questionary import Choice
except ImportError:
    print("❌ questionary not installed. Install with: pip install questionary")
    sys.exit(1)

try:
    # Import factory API and JCVI integration
    from src.api import create_bio_vm, create_biological_vm
    from src.api.resource_manager import BioResourceManager
    from src.api.config_manager import ConfigManager
    from src.api.jcvi_manager import create_jcvi_manager
    from src.hypervisor.core import BioXenHypervisor, ChassisType
    from src.genome.schema import BioXenGenomeValidator
    from src.genome.parser import BioXenRealGenomeIntegrator
    # Enhanced v0.0.03: Import acquisition capabilities
    try:
        from src.jcvi_integration.genome_acquisition import JCVIGenomeAcquisition
        from src.jcvi_integration.analysis_coordinator import JCVIWorkflowCoordinator
        ACQUISITION_AVAILABLE = True
    except ImportError:
        print("⚠️  Enhanced acquisition features not available (v0.0.03)")
        ACQUISITION_AVAILABLE = False
    FACTORY_API_AVAILABLE = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure the bioxen-jcvi-vm-lib package is properly installed")
    print("Run from /home/chris/BioXen-luavm/ directory with activated venv")
    FACTORY_API_AVAILABLE = False
    ACQUISITION_AVAILABLE = False

# Import os for file operations
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('bioxen_factory.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class InteractiveBioXenFactory:
    """Interactive CLI for BioXen Factory Pattern API with JCVI Integration."""
    def __init__(self):
        """Initialize the interactive BioXen JCVI API interface"""
        if FACTORY_API_AVAILABLE:
            self.hypervisor = BioXenHypervisor()
            self.resource_manager = BioResourceManager()
            self.config_manager = ConfigManager()
            self.validator = BioXenGenomeValidator()
        else:
            self.hypervisor = None
            self.resource_manager = None
            self.config_manager = None
            self.validator = None
            
        self.genome_integrator = None
        
        # Enhanced v0.0.03: Initialize JCVI capabilities
        self.jcvi_manager = None
        self.acquisition_system = None
        self.workflow_coordinator = None
        
        # Initialize chassis type and biological type
        self.chassis_type = ChassisType.ECOLI if FACTORY_API_AVAILABLE else "E. coli"
        self.selected_biological_type = "prokaryotic"
        self.vm_type = "basic"
        
        # Define supported types
        self.supported_bio_types = ["prokaryotic", "eukaryotic", "synthetic"]
        self.supported_vm_types = ["basic", "optimized", "jcvi_optimized"]
        
        # Active VMs tracking
        self.active_vms = {}
        
        try:
            if FACTORY_API_AVAILABLE:
                self.jcvi_manager = create_jcvi_manager()
            if ACQUISITION_AVAILABLE:
                self.acquisition_system = JCVIGenomeAcquisition()
                self.workflow_coordinator = JCVIWorkflowCoordinator()
                print("✅ v0.0.03 Enhanced JCVI acquisition capabilities loaded")
        except Exception as e:
            print(f"⚠️  JCVI features partially available: {e}")
        
        self.current_vm = None
        self.vms = []

    def select_chassis(self):
        """Select chassis type for biological VMs."""
        print("\n🧬 Select Chassis")
        if FACTORY_API_AVAILABLE:
            chassis = questionary.select(
                "Chassis type:",
                choices=[
                    Choice("🦠 E. coli (Prokaryotic)", ChassisType.ECOLI),
                    Choice("🍄 Yeast (Eukaryotic, PLACEHOLDER)", ChassisType.YEAST),
                    Choice("🧩 Orthogonal (Experimental)", ChassisType.ORTHOGONAL),
                ]
            ).ask()
            if chassis:
                self.chassis_type = chassis
                print(f"\n✅ {chassis.value} chassis selected")
        else:
            chassis = questionary.select(
                "Chassis type:",
                choices=[
                    Choice("🦠 E. coli (Prokaryotic)", "E. coli"),
                    Choice("🍄 Yeast (Eukaryotic, PLACEHOLDER)", "Yeast"),
                    Choice("🧩 Orthogonal (Experimental)", "Orthogonal"),
                ]
            ).ask()
            if chassis:
                self.chassis_type = chassis
                print(f"\n✅ {chassis} chassis selected")
        return chassis

    def main_menu(self):
        """Display main menu with chassis and JCVI integration."""
        while True:
            print("\n" + "="*70)
            print("🧬 BioXen Factory Pattern API with JCVI Integration")
            print("="*70)
            chassis_display = self.chassis_type.value if hasattr(self.chassis_type, 'value') else str(self.chassis_type)
            print(f"🦠 Current Chassis: {chassis_display}")
            print(f"🧬 Biological Type: {self.selected_biological_type}")
            print(f"🏗️ VM Type: {self.vm_type}")
            print(f"⚡ Active VMs: {len(self.active_vms)}")
            
            choices = [
                Choice("🔍 Browse Genomes", "browse_genomes"),
                Choice("🧬 Load Genome", "validate_genomes"),
                Choice("🖥️ Initialize Hypervisor", "init_hypervisor"),
                Choice("📥 Download Genomes", "download_genomes"),
                Choice("⚡ Create VM", "create_vm"),
                Choice("🔧 Manage VMs", "manage_vms"),
                Choice("📺 Terminal Visualization", "terminal_visualization"),
                Choice("🗑️ Destroy VM", "destroy_vm"),
                Choice("🧪 JCVI Analysis", "jcvi_analysis_menu"),
                Choice("🧬 Select Chassis", "select_chassis"),
                Choice("⚙️ Configuration", "configuration_menu"),
                Choice("❌ Exit", "exit"),
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

    def browse_genomes(self):
        """Browse available genomes."""
        print("\n🔍 Browse Genomes")
        genome_dir = Path("genomes")
        if not genome_dir.exists():
            print("❌ Genomes directory not found")
            print("💡 Use 'Download Genomes' to create some genomes first")
        else:
            genomes = list(genome_dir.glob("*"))
            if not genomes:
                print("❌ No genomes found in genomes/ directory")
                print("💡 Use 'Download Genomes' to add some genomes")
            else:
                print(f"📁 Found {len(genomes)} files in genomes/:")
                for genome in genomes:
                    size_kb = genome.stat().st_size / 1024 if genome.is_file() else 0
                    print(f"   🧬 {genome.name} ({size_kb:.1f} KB)")
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
                    config_manager = ConfigManager()
                    # Note: ConfigManager.load_defaults might need adjustment based on actual implementation
                    print(f"📋 Configuration ready for {action}")
                except Exception as e:
                    print(f"⚠️ Could not load config: {e}")
        
        questionary.press_any_key_to_continue().ask()

    def init_hypervisor(self):
        """Initialize hypervisor."""
        if self.hypervisor and not questionary.confirm("Reinitialize hypervisor?").ask():
            return
        
        print("\n🚀 Initializing Hypervisor")
        try:
            print(f"🔄 Initializing hypervisor...")
            if FACTORY_API_AVAILABLE:
                self.hypervisor = BioXenHypervisor()
            else:
                self.hypervisor = "Mock Hypervisor"
            print(f"✅ Hypervisor initialized successfully")
        except Exception as e:
            logger.error(f"Init error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def create_vm(self):
        """Create a biological VM using the Factory Pattern API with chassis and JCVI support."""
        if not FACTORY_API_AVAILABLE:
            print("❌ Factory API not available")
            print("💡 This is a simulation mode")
            return self._create_mock_vm()
        
        print(f"\n🧬 Creating Biological VM with JCVI Integration")
        chassis_display = self.chassis_type.value if hasattr(self.chassis_type, 'value') else str(self.chassis_type)
        print(f"🦠 Chassis: {chassis_display}")
        print(f"🔬 Biological Type: {self.selected_biological_type}")
        print(f"🖥️ VM Type: {self.vm_type}")
        
        vm_id = questionary.text("Enter VM ID:", default=f"vm_{self.selected_biological_type}_{int(time.time() % 10000)}").ask()
        if not vm_id:
            return
            
        try:
            print(f"🔄 Creating VM: {vm_id}")
            
            # Create configuration with chassis
            config = {
                'vm_id': vm_id,
                'biological_type': self.selected_biological_type,
                'chassis_type': self.chassis_type,
                'enable_jcvi': True,
                'jcvi_cli_enabled': True,
                'hardware_optimization': self.vm_type == "jcvi_optimized"
            }
            
            # Use Factory Pattern API - choose method based on VM type
            if self.vm_type == "jcvi_optimized":
                # Use convenience function for JCVI-optimized VMs
                vm = create_biological_vm(vm_type="jcvi_optimized", config=config)
            else:
                # Use full factory function
                vm = create_bio_vm(vm_id, self.selected_biological_type, self.vm_type, config)
            
            print(f"✅ VM created successfully: {vm_id}")
            chassis_display = self.chassis_type.value if hasattr(self.chassis_type, 'value') else str(self.chassis_type)
            print(f"   🦠 Chassis: {chassis_display}")
            print(f"   🔬 Type: {vm.get_vm_type()}")
            print(f"   🧬 Biological: {vm.get_biological_type()}")
            
            # Check JCVI availability
            if hasattr(vm, 'jcvi_available'):
                print(f"   🔍 JCVI Available: {vm.jcvi_available}")
                if vm.jcvi_available:
                    jcvi_status = vm.get_jcvi_status()
                    print(f"   📊 JCVI Status: {jcvi_status}")
            
            # Store reference
            self.active_vms[vm_id] = vm
            
            # Start the VM
            if questionary.confirm("Start VM now?").ask():
                if vm.start():
                    print(f"🚀 VM {vm_id} started successfully")
                else:
                    print(f"❌ Failed to start VM {vm_id}")
            
        except Exception as e:
            logger.error(f"VM creation error: {e}")
            print(f"❌ Error creating VM: {e}")
            import traceback
            traceback.print_exc()
        
        questionary.press_any_key_to_continue().ask()

    def _create_mock_vm(self):
        """Create a mock VM when Factory API is not available."""
        print(f"\n🧬 Creating Mock Biological VM")
        chassis_display = str(self.chassis_type)
        print(f"🦠 Chassis: {chassis_display}")
        print(f"🔬 Biological Type: {self.selected_biological_type}")
        print(f"🖥️ VM Type: {self.vm_type}")
        
        vm_id = questionary.text("Enter VM ID:", default=f"mock_vm_{int(time.time() % 10000)}").ask()
        if not vm_id:
            return
            
        # Create a simple mock VM object
        mock_vm = {
            'id': vm_id,
            'type': self.vm_type,
            'biological_type': self.selected_biological_type,
            'chassis': chassis_display,
            'status': 'created',
            'jcvi_available': True
        }
        
        self.active_vms[vm_id] = mock_vm
        print(f"✅ Mock VM created: {vm_id}")
        questionary.press_any_key_to_continue().ask()

    def jcvi_operations_menu(self):
        """JCVI-specific operations menu (Phase 1.1)."""
        if not self.active_vms:
            print("❌ No active VMs for JCVI operations")
            questionary.press_any_key_to_continue().ask()
            return
        
        # Select VM for JCVI operations
        choices = []
        for vm_id, vm in self.active_vms.items():
            if isinstance(vm, dict):
                jcvi_status = "🧬" if vm.get('jcvi_available', False) else "  "
            else:
                jcvi_status = "🧬" if hasattr(vm, 'jcvi_available') and vm.jcvi_available else "  "
            choices.append(Choice(f"{jcvi_status} {vm_id}", vm_id))
        choices.append(Choice("🔙 Back", "back"))
        
        vm_id = questionary.select("Select VM for JCVI operations:", choices=choices).ask()
        if vm_id == "back" or vm_id is None:
            return
            
        vm = self.active_vms[vm_id]
        
        while True:
            choices = [
                Choice("🔬 Genome Analysis", "genome_analysis"),
                Choice("📊 Comparative Analysis", "comparative_analysis"),
                Choice("🔄 Format Conversion", "format_conversion"),
                Choice("📈 JCVI Status", "jcvi_status"),
                Choice("🔙 Back", "back")
            ]
            
            action = questionary.select(f"JCVI operations for {vm_id}:", choices=choices).ask()
            if action == "back" or action is None:
                break
                
            try:
                if action == "genome_analysis":
                    genome_path = questionary.text("Genome file path:", default="genomes/syn3a.genome").ask()
                    if genome_path:
                        if isinstance(vm, dict):
                            print(f"🔬 Mock genome analysis for {genome_path}")
                            print("   Mock results: 1000 genes, 500kb genome size")
                        elif hasattr(vm, 'analyze_genome'):
                            result = vm.analyze_genome(genome_path)
                            print(f"🔬 Genome Analysis Result:")
                            for key, value in result.items():
                                print(f"   {key}: {value}")
                        else:
                            print("❌ Genome analysis not available")
                            
                elif action == "comparative_analysis":
                    genome1 = questionary.text("First genome path:", default="genomes/syn3a.genome").ask()
                    genome2 = questionary.text("Second genome path:", default="genomes/syn3a.genome").ask()
                    if genome1 and genome2:
                        if isinstance(vm, dict):
                            print(f"📊 Mock comparative analysis between {genome1} and {genome2}")
                            print("   Mock results: 85% similarity, 150 unique genes")
                        elif hasattr(vm, 'run_comparative_analysis'):
                            result = vm.run_comparative_analysis(genome1, genome2)
                            print(f"📊 Comparative Analysis Result:")
                            for key, value in result.items():
                                print(f"   {key}: {value}")
                        else:
                            print("❌ Comparative analysis not available")
                            
                elif action == "format_conversion":
                    input_path = questionary.text("Input file path:", default="genomes/syn3a.genome").ask()
                    output_path = questionary.text("Output file path:", default="genomes/syn3a.fasta").ask()
                    if input_path and output_path:
                        if isinstance(vm, dict):
                            print(f"🔄 Mock format conversion: {input_path} -> {output_path}")
                            print("   Mock conversion completed")
                        elif hasattr(vm, 'convert_genome_format'):
                            result = vm.convert_genome_format(input_path, output_path)
                            print(f"🔄 Format Conversion Result:")
                            for key, value in result.items():
                                print(f"   {key}: {value}")
                        else:
                            print("❌ Format conversion not available")
                            
                elif action == "jcvi_status":
                    if isinstance(vm, dict):
                        print(f"📈 Mock JCVI Status for {vm_id}:")
                        print(f"   Available: {vm.get('jcvi_available', False)}")
                        print(f"   Version: Mock v1.0")
                    elif hasattr(vm, 'get_jcvi_status'):
                        status = vm.get_jcvi_status()
                        print(f"📈 JCVI Status for {vm_id}:")
                        for key, value in status.items():
                            print(f"   {key}: {value}")
                    else:
                        print("❌ JCVI status not available")
                        
            except Exception as e:
                logger.error(f"JCVI operation error: {e}")
                print(f"❌ Error: {e}")
            
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
                if isinstance(vm, dict):
                    status = vm.get('status', 'unknown')
                    jcvi_indicator = "🧬" if vm.get('jcvi_available', False) else ""
                    print(f"🖥️ {vm_id} {jcvi_indicator}")
                    print(f"   Type: {vm.get('type', 'unknown')} | Bio: {vm.get('biological_type', 'unknown')}")
                    print(f"   Status: {status}")
                else:
                    status = vm.get_status()
                    jcvi_indicator = "🧬" if hasattr(vm, 'jcvi_available') and vm.jcvi_available else ""
                    print(f"🖥️ {vm_id} {jcvi_indicator}")
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
                Choice("🧬 Execute Process", "execute"),
                Choice("📦 Install Package", "install_package"),
                Choice("📈 Metrics", "metrics"),
                Choice("🗑️ Destroy", "destroy"),
                Choice("🔙 Back", "back")
            ]
            
            action = questionary.select(f"Operations for {vm_id}:", choices=choices).ask()
            if action == "back" or action is None:
                break
                
            try:
                if isinstance(vm, dict):
                    # Mock VM operations
                    if action == "start":
                        vm['status'] = 'running'
                        print("✅ Mock VM started")
                    elif action == "pause":
                        vm['status'] = 'paused'
                        print("✅ Mock VM paused")
                    elif action == "resume":
                        vm['status'] = 'running'
                        print("✅ Mock VM resumed")
                    elif action == "status":
                        print(f"📊 Status: {vm.get('status', 'unknown')}")
                    elif action == "execute":
                        process = questionary.text("Enter biological process code:").ask()
                        if process:
                            print(f"🧬 Mock process executed: {process}")
                    elif action == "install_package":
                        package = questionary.text("Enter package name:").ask()
                        if package:
                            print(f"📦 Mock package installed: {package}")
                    elif action == "metrics":
                        print("📈 Mock metrics: CPU: 10%, Memory: 256MB, Processes: 5")
                    elif action == "destroy":
                        if questionary.confirm(f"Destroy VM {vm_id}?").ask():
                            del self.active_vms[vm_id]
                            print(f"🗑️ VM {vm_id} destroyed")
                            break
                else:
                    # Real VM operations
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
                        metrics = vm.get_biological_metrics()
                        print(f"📈 Metrics: {metrics}")
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
        """Resource management using ResourceManager."""
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
                    Choice("📊 Resource Usage", "usage"),
                    Choice("📈 Available Resources", "available"),
                    Choice("⚡ VM Resources", "vm_resources"),
                    Choice("🔙 Back", "back")
                ]
                
                action = questionary.select(f"Resource management for {vm_id}:", choices=choices).ask()
                if action == "back" or action is None:
                    break
                    
                if action == "usage":
                    usage = manager.get_resource_usage()
                    print(f"📊 Resource usage: {usage}")
                elif action == "available":
                    available = manager.get_available_resources()
                    print(f"📈 Available resources: {available}")
                elif action == "vm_resources":
                    # VM-specific resource info
                    if isinstance(vm, dict):
                        print(f"⚡ VM {vm_id} resources: {vm}")
                    else:
                        status = vm.get_status()
                        print(f"⚡ VM {vm_id} resources: {status}")
                
                questionary.press_any_key_to_continue().ask()
                
        except Exception as e:
            logger.error(f"Resource management error: {e}")
            print(f"❌ Error: {e}")
            questionary.press_any_key_to_continue().ask()

    def jcvi_analysis_menu(self):
        """Enhanced JCVI analysis and operations menu with v0.0.03 features."""
        if not FACTORY_API_AVAILABLE:
            print("❌ Factory API not available - using simulation mode")
        
        while True:
            print(f"\n🧪 JCVI Analysis {'(Enhanced v0.0.03)' if ACQUISITION_AVAILABLE else '(Legacy)'}")
            
            choices = [
                Choice("🔬 Analyze Genome", "analyze_genome"),
                Choice("📊 Comparative Analysis", "comparative_analysis"),
                Choice("🔄 Format Conversion", "format_conversion"),
                Choice("📈 JCVI Status", "jcvi_status"),
            ]
            
            # Add v0.0.03 enhanced features if available
            if ACQUISITION_AVAILABLE and self.jcvi_manager:
                choices.insert(1, Choice("📥 Acquire & Analyze", "acquire_analyze"))
                choices.insert(2, Choice("🔄 Complete Workflow", "complete_workflow_local"))
                choices.insert(3, Choice("📋 List Available Genomes", "list_genomes"))
            
            choices.append(Choice("🔙 Back", "back"))
            
            action = questionary.select("JCVI Analysis:", choices=choices).ask()
            if action == "back" or action is None:
                break
                
            try:
                if action == "acquire_analyze":
                    # New v0.0.03 feature: acquire and immediately analyze
                    if self.jcvi_manager:
                        available = self.jcvi_manager.list_available_genomes()
                        if available:
                            choices = [Choice(f"🧬 {genome}", genome) for genome in available]
                            genome = questionary.select("Select genome:", choices=choices).ask()
                            if genome:
                                print(f"📥 Acquiring and analyzing {genome}...")
                                success = self.jcvi_manager.acquire_genome(genome)
                                if success:
                                    result = self.jcvi_manager.run_complete_workflow([genome])
                                    print(f"✅ Analysis complete: {result}")
                                else:
                                    print("❌ Acquisition failed")
                        else:
                            print("❌ No genomes available")
                    else:
                        print("❌ JCVI manager not available")
                        
                elif action == "complete_workflow_local":
                    # Local version of complete workflow
                    self.complete_workflow()
                    
                elif action == "list_genomes":
                    # List available genomes
                    if self.jcvi_manager:
                        available = self.jcvi_manager.list_available_genomes()
                        print(f"🧬 Available genomes: {available}")
                    else:
                        print("❌ JCVI manager not available")
                        
                elif action == "analyze_genome":
                    genome_file = questionary.text("Enter genome file path:").ask()
                    if genome_file and os.path.exists(genome_file):
                        # Use enhanced JCVI manager if available
                        manager = self.jcvi_manager if self.jcvi_manager else None
                        if not manager and FACTORY_API_AVAILABLE:
                            from src.api.jcvi_manager import JCVIManager
                            manager = JCVIManager()
                            
                        if manager and hasattr(manager, 'is_available') and manager.is_available():
                            result = manager.analyze_genome(genome_file)
                            print(f"📊 Analysis Result:\n{result}")
                        else:
                            print("❌ JCVI not available - using simulation")
                            print(f"🔬 Mock analysis for {genome_file}")
                            print("   Mock results: 1000 genes, 500kb genome")
                    else:
                        print("❌ File not found")
                        
                elif action == "comparative_analysis":
                    print("🔬 Starting comparative analysis...")
                    genome1 = questionary.text("Enter first genome file:").ask()
                    genome2 = questionary.text("Enter second genome file:").ask()
                    
                    if genome1 and genome2:
                        if FACTORY_API_AVAILABLE and os.path.exists(genome1) and os.path.exists(genome2):
                            from src.api.jcvi_manager import JCVIManager
                            manager = JCVIManager()
                            if hasattr(manager, 'is_available') and manager.is_available():
                                result = manager.run_comparative_analysis(genome1, genome2)
                                print(f"📈 Comparative Analysis:\n{result}")
                            else:
                                print("❌ JCVI not available - using simulation")
                                print(f"📊 Mock comparative analysis: {genome1} vs {genome2}")
                                print("   Mock results: 85% similarity, 150 unique genes")
                        else:
                            print("❌ Invalid files or API not available - using simulation")
                            print(f"📊 Mock comparative analysis: {genome1} vs {genome2}")
                            print("   Mock results: 85% similarity, 150 unique genes")
                        
                elif action == "format_conversion":
                    input_file = questionary.text("Enter input file:").ask()
                    output_format = questionary.select("Output format:", 
                                                     choices=["fasta", "genbank", "gff"]).ask()
                    
                    if input_file and output_format:
                        if FACTORY_API_AVAILABLE and os.path.exists(input_file):
                            from src.api.jcvi_manager import JCVIManager
                            manager = JCVIManager()
                            if hasattr(manager, 'is_available') and manager.is_available():
                                output_file = f"{os.path.splitext(input_file)[0]}.{output_format}"
                                success = manager.convert_format(input_file, output_file, output_format)
                                if success:
                                    print(f"✅ Converted to: {output_file}")
                                else:
                                    print("❌ Conversion failed")
                            else:
                                print("❌ JCVI not available - using simulation")
                                output_file = f"{os.path.splitext(input_file)[0]}.{output_format}"
                                print(f"🔄 Mock conversion: {input_file} -> {output_file}")
                        else:
                            print("❌ Invalid input or API not available - using simulation")
                            output_file = f"{os.path.splitext(input_file)[0]}.{output_format}"
                            print(f"🔄 Mock conversion: {input_file} -> {output_file}")
                        
                elif action == "jcvi_status":
                    if FACTORY_API_AVAILABLE:
                        from src.api.jcvi_manager import JCVIManager
                        manager = JCVIManager()
                        available = hasattr(manager, 'is_available') and manager.is_available()
                        print(f"🧬 JCVI Available: {'✅' if available else '❌'}")
                        if available:
                            print("🔧 Available operations:")
                            print("   • Genome analysis")
                            print("   • Comparative genomics")
                            print("   • Format conversion")
                            print("   • Synteny analysis")
                        else:
                            print("💡 JCVI toolkit not found - using simulation mode")
                    else:
                        print("🧬 JCVI Available: ❌ (API not available)")
                        print("💡 Running in simulation mode")
                    
                questionary.press_any_key_to_continue().ask()
                
            except Exception as e:
                logger.error(f"JCVI analysis error: {e}")
                print(f"❌ Error: {e}")
                questionary.press_any_key_to_continue().ask()

    def acquire_genome(self):
        """Acquire genome using JCVI manager if available."""
        print("\n📥 Genome Acquisition")
        print("="*50)
        
        try:
            # Check if JCVI manager is available
            if not self.jcvi_manager:
                print("❌ JCVI manager not available")
                print("   Creating simulated genomes instead...")
                self._create_default_genomes()
                return
            
            # Try to get available genomes from JCVI manager
            try:
                available = self.jcvi_manager.list_available_genomes()
                print(f"🧬 Available genomes: {available}")
            except Exception as e:
                print(f"⚠️  Could not list genomes: {e}")
                available = []
            
            # If no genomes available, create some defaults
            if not available:
                print("📝 No remote genomes found, creating local simulated genomes...")
                self._create_default_genomes()
                return
                
            # Let user select from available genomes
            choices = [Choice(f"🧬 {genome}", genome) for genome in available]
            choices.append(Choice("🔙 Back", "back"))
            
            genome = questionary.select("Select genome to acquire:", choices=choices).ask()
            if genome == "back" or genome is None:
                return
                
            print(f"📥 Acquiring {genome}...")
            
            # Try to acquire genome using JCVI manager
            try:
                if hasattr(self.jcvi_manager, 'acquire_genome'):
                    success = self.jcvi_manager.acquire_genome(genome)
                    if success:
                        print(f"✅ Successfully acquired {genome}")
                        print("🔧 Genome is ready for analysis")
                    else:
                        print(f"❌ Failed to acquire {genome}")
                        print("   Creating simulated version instead...")
                        self._create_simulated_genome(f"sim_{genome}", genome, 1000000)
                else:
                    print("⚠️  Direct acquisition not supported")
                    print("   Creating simulated version...")
                    self._create_simulated_genome(f"sim_{genome}", genome, 1000000)
            except Exception as e:
                print(f"❌ Acquisition error: {e}")
                print("   Creating simulated version...")
                self._create_simulated_genome(f"sim_{genome}", genome, 1000000)
                    
        except Exception as e:
            logger.error(f"Acquisition error: {e}")
            print(f"❌ Acquisition error: {e}")
            
        questionary.press_any_key_to_continue().ask()

    def _create_default_genomes(self):
        """Create a set of default simulated genomes."""
        print("🧬 Creating default genome collection...")
        default_genomes = [
            {"accession": "NC_000913.3", "name": "E_coli_K12", "size": 4641652},
            {"accession": "NC_000908.2", "name": "M_genitalium", "size": 580076},
            {"accession": "NC_001133.9", "name": "S_cerevisiae", "size": 230218},
            {"accession": "SYN3A", "name": "Syn3A_minimal", "size": 531000}
        ]
        
        for genome in default_genomes:
            self._create_simulated_genome(genome["accession"], genome["name"], genome["size"])
            
        print("✅ Default genome collection created")

    def _use_real_genome_downloader(self):
        """Use the real NCBI genome downloader."""
        print("\n🧬 Real NCBI Genome Downloader")
        print("="*50)
        
        # Show available genomes
        print("📋 Available minimal genomes:")
        for key, info in MINIMAL_GENOMES.items():
            print(f"   🔑 {key}: {info['description']}")
        
        # Let user choose download option
        choices = [
            Choice("📋 List All Available Genomes", "list"),
            Choice("📥 Download Single Genome", "single"), 
            Choice("🌐 Download All Genomes", "all"),
            Choice("🔙 Back to Simulated Mode", "back")
        ]
        
        action = questionary.select("Select download option:", choices=choices).ask()
        if action == "back" or action is None:
            return
            
        # Create output directory
        output_dir = Path("genomes")
        output_dir.mkdir(exist_ok=True)
        
        try:
            if action == "list":
                list_available_genomes()
                
            elif action == "single":
                # Let user select specific genome
                genome_choices = [Choice(f"🧬 {key}: {info['description']}", key) 
                                for key, info in MINIMAL_GENOMES.items()]
                genome_choices.append(Choice("🔙 Back", "back"))
                
                genome_key = questionary.select("Select genome to download:", choices=genome_choices).ask()
                if genome_key != "back" and genome_key is not None:
                    print(f"\n📥 Downloading {genome_key}...")
                    success = download_and_convert_genome(genome_key, output_dir)
                    if success:
                        print(f"✅ Successfully downloaded and converted {genome_key}")
                        print(f"📁 Available in: {output_dir}")
                    else:
                        print(f"❌ Failed to download {genome_key}")
                        
            elif action == "all":
                if questionary.confirm("Download ALL minimal genomes? This may take several minutes.").ask():
                    print("\n🌐 Downloading all minimal genomes...")
                    success_count = 0
                    for genome_key in MINIMAL_GENOMES.keys():
                        print(f"\n📥 Downloading {genome_key}...")
                        if download_and_convert_genome(genome_key, output_dir):
                            success_count += 1
                            print(f"✅ {genome_key} completed")
                        else:
                            print(f"❌ {genome_key} failed")
                    
                    print(f"\n📊 Download Summary: {success_count}/{len(MINIMAL_GENOMES)} genomes successful")
                    if success_count > 0:
                        print(f"📁 Genomes available in: {output_dir}")
                        
        except Exception as e:
            print(f"❌ Download error: {e}")
            print("   Falling back to simulated genomes...")
            self._create_default_genomes()
        
        questionary.press_any_key_to_continue().ask()

    def complete_workflow(self):
        """Enhanced v0.0.03: Run complete acquisition + analysis workflow."""
        if not ACQUISITION_AVAILABLE or not self.workflow_coordinator:
            print("⚠️  Complete workflow features not available")
            return
            
        print("\n🔄 Complete Workflow (v0.0.03)")
        print("="*50)
        print("This will acquire genomes and run comparative analysis")
        
        try:
            # Get species for comparative analysis
            species_list = []
            print("\n📝 Enter species for comparative analysis:")
            print("   (Enter empty line to finish)")
            
            while True:
                species = questionary.text("Species name:").ask()
                if not species:
                    break
                species_list.append(species)
                print(f"   ✅ Added: {species}")
                
            if len(species_list) < 2:
                print("❌ Need at least 2 species for comparative analysis")
                return
                
            # Run complete workflow
            print(f"\n🔄 Running complete workflow for {len(species_list)} species...")
            results = self.workflow_coordinator.run_complete_workflow(species_list)
            
            if results:
                print("✅ Workflow completed successfully!")
                print(f"📊 Results: {results}")
            else:
                print("❌ Workflow failed")
                
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            print(f"❌ Workflow error: {e}")
            
        questionary.press_any_key_to_continue().ask()

    def _check_hypervisor(self):
        """Check if hypervisor is initialized."""
        if self.hypervisor is None:
            print("❌ Hypervisor not initialized. Select 'Initialize Hypervisor'.")
            return False
        return True

    def validate_genomes(self):
        """Validate genomes."""
        if not self._check_hypervisor():
            return
        print("\n🧬 Load Genome")
        genome_dir = Path("genomes")
        if not genome_dir.exists() or not list(genome_dir.glob("*.genome")):
            print("❌ No genomes found\n💡 Use 'Download Genomes'")
            return questionary.press_any_key_to_continue().ask()
        genomes = list(genome_dir.glob("*.genome"))
        print(f"✅ Found {len(genomes)} genomes")
        choices = []
        valid_genomes = []
        for genome in genomes:
            try:
                name = genome.stem
                size_kb = genome.stat().st_size / 1024
                display_name = f"🧬 {name} ({size_kb:.1f} KB)"
                choices.append(Choice(display_name, {"name": name, "file_path": genome}))
                valid_genomes.append({"name": name, "file_path": genome})
            except Exception as e:
                logger.warning(f"Error reading {genome}: {e}")
        if not valid_genomes:
            print("❌ No valid genomes\n💡 Use 'Download Genomes'")
            return questionary.press_any_key_to_continue().ask()
        choices.append(Choice("🔍 Validate all", "all"))
        choice = questionary.select("Select genome:", choices=choices).ask()
        if choice is None:
            return
        if choice == "all":
            self._validate_all_genomes(valid_genomes)
        else:
            self._validate_single_genome(choice)
        questionary.press_any_key_to_continue().ask()

    def _validate_all_genomes(self, genomes):
        """Validate all genomes."""
        print("\n🔄 Validating all...")
        all_valid = True
        for genome in genomes:
            print(f"\n🔬 Validating {genome['name']}...")
            try:
                if FACTORY_API_AVAILABLE and self.validator:
                    is_valid, messages = self.validator.validate_genome(genome['file_path'])
                    if is_valid:
                        print("✅ Valid")
                    else:
                        print("❌ Invalid:")
                        for msg in messages:
                            print(f"   - {msg}")
                        all_valid = False
                else:
                    print("✅ Mock validation passed")
            except Exception as e:
                logger.error(f"Validation error: {e}")
                print(f"❌ Error: {e}")
                all_valid = False
        print("\n" + ("✅ All valid" if all_valid else "⚠️ Some failed"))

    def _validate_single_genome(self, genome):
        """Validate single genome."""
        print(f"\n🔬 Validating {genome['name']}...")
        try:
            if FACTORY_API_AVAILABLE and self.validator:
                is_valid, messages = self.validator.validate_genome(genome['file_path'])
                if is_valid:
                    print("✅ Valid")
                    if not hasattr(self, 'available_genomes'):
                        self.available_genomes = []
                    self.available_genomes.append({"name": genome['name'], "file_path": genome['file_path'], "data": None})
                else:
                    print("❌ Invalid:")
                    for msg in messages:
                        print(f"   - {msg}")
            else:
                print("✅ Mock validation passed")
        except Exception as e:
            logger.error(f"Validation error: {e}")
            print(f"❌ Error: {e}")

    def download_genomes(self):
        """Enhanced: Download genomes with real NCBI downloads when available."""
        if not self._check_hypervisor():
            return
            
        print("\n🌐 Download Genomes")
        
        # Check if real genome downloader is available
        if REAL_GENOME_DOWNLOADER_AVAILABLE:
            print("✅ Real NCBI genome downloader available")
            use_real = questionary.confirm("Use real NCBI genome downloads?").ask()
            if use_real:
                self._use_real_genome_downloader()
                return
        
        # Check if JCVI manager is available for real genome download
        if FACTORY_API_AVAILABLE and self.jcvi_manager:
            print("✅ JCVI manager available - attempting real genome acquisition")
            try:
                # Try to list available genomes from JCVI manager
                available = self.jcvi_manager.list_available_genomes()
                if available:
                    print(f"🧬 Available genomes: {available}")
                    use_real = questionary.confirm("Download real genomes using JCVI?").ask()
                    if use_real:
                        self.acquire_genome()
                        return
            except Exception as e:
                print(f"⚠️  JCVI acquisition failed: {e}")
        
        print("📥 Simulated genome creation mode")
        print("📥 Available genome options:")
        
        options = [
            {"display": "🦠 E. coli K-12", "accession": "NC_000913.3", "name": "E_coli_K12", "size": 4641652},
            {"display": "🍄 S. cerevisiae", "accession": "NC_001133.9", "name": "S_cerevisiae", "size": 230218},
            {"display": "🔬 M. genitalium", "accession": "NC_000908.2", "name": "M_genitalium", "size": 580076},
            {"display": "🧪 Custom genome", "accession": "custom", "name": "custom", "size": 1000000}
        ]
        
        choice = questionary.select("Select genome:", choices=[Choice(opt["display"], opt) for opt in options]).ask()
        if choice is None:
            return
            
        if choice["accession"] == "custom":
            accession = questionary.text("Accession (e.g., NC_000913.3):").ask()
            if not accession:
                return
            name = questionary.text("Name:").ask() or accession.replace(".", "_")
            print(f"🔄 Simulating download for {name} ({accession})")
            self._create_simulated_genome(accession, name, 1000000)
        else:
            print(f"🔄 Simulating download for {choice['name']}")
            self._create_simulated_genome(choice["accession"], choice["name"], choice["size"])
        
        questionary.press_any_key_to_continue().ask()

    def _create_simulated_genome(self, accession: str, name: str, size: int):
        """Create simulated genome."""
        genome_dir = Path("genomes")
        genome_dir.mkdir(exist_ok=True)
        
        genome_file = genome_dir / f"{name}.genome"
        print(f"📝 Creating {genome_file}")
        
        # Create a simple simulated genome file
        with open(genome_file, 'w') as f:
            f.write(f"# Simulated genome: {name} ({accession})\n")
            f.write(f"# Size: {size} bp\n")
            f.write("gene_id\tstart\tend\tstrand\tproduct\n")
            
            # Generate some sample genes
            gene_count = max(10, size // 1000)  # Rough gene density
            for i in range(1, min(gene_count, 100)):  # Limit for demo
                start = i * 1000
                end = start + 900
                strand = "+" if i % 2 == 0 else "-"
                f.write(f"gene_{i:03d}\t{start}\t{end}\t{strand}\tHypothetical protein\n")
        
        print(f"✅ Created simulated genome: {genome_file}")

    def terminal_visualization(self):
        """Toggle terminal visualization."""
        print("\n📺 Terminal Visualization")
        
        # Check if terminal_biovis.py exists
        vis_script = Path("terminal_biovis.py")
        if not vis_script.exists():
            print("❌ Terminal visualization script not found")
            print("💡 terminal_biovis.py should be in the project root")
            questionary.press_any_key_to_continue().ask()
            return
        
        if hasattr(self, 'visualization_active') and self.visualization_active:
            print("⚠️ Visualization already active")
            if questionary.confirm("Stop visualization?").ask():
                self.visualization_active = False
                print("⏹️ Visualization stopped")
        else:
            print("🚀 Starting terminal visualization...")
            try:
                # Start visualization in background
                import subprocess
                subprocess.Popen([sys.executable, "terminal_biovis.py"], 
                               cwd=str(Path.cwd()))
                self.visualization_active = True
                print("✅ Visualization started in background")
                print("💡 Check your terminal for the visualization display")
            except Exception as e:
                print(f"❌ Error starting visualization: {e}")
        
        questionary.press_any_key_to_continue().ask()

    def destroy_vm(self):
        """Destroy VM."""
        if not self._check_hypervisor():
            return
            
        if not self.active_vms:
            print("❌ No active VMs to destroy")
            questionary.press_any_key_to_continue().ask()
            return
        
        print("\n🗑️ Destroy VM")
        choices = []
        for vm_id in self.active_vms.keys():
            choices.append(Choice(f"🖥️ {vm_id}", vm_id))
        choices.append(Choice("🔙 Cancel", "cancel"))
        
        vm_id = questionary.select("Select VM to destroy:", choices=choices).ask()
        if vm_id == "cancel" or vm_id is None:
            return
        
        if questionary.confirm(f"⚠️ Really destroy VM '{vm_id}'?").ask():
            try:
                vm = self.active_vms[vm_id]
                if isinstance(vm, dict):
                    # Mock VM
                    del self.active_vms[vm_id]
                    print(f"✅ Mock VM '{vm_id}' destroyed")
                else:
                    # Real VM
                    if hasattr(vm, 'shutdown'):
                        vm.shutdown()
                    del self.active_vms[vm_id]
                    print(f"✅ VM '{vm_id}' destroyed")
            except Exception as e:
                logger.error(f"Error destroying VM: {e}")
                print(f"❌ Error destroying VM: {e}")
        
        questionary.press_any_key_to_continue().ask()

    def configuration_menu(self):
        """Configuration management menu."""
        while True:
            choices = [
                Choice("🔧 Set VM Type", "set_vm_type"),
                Choice("🧬 Select Biological Type", "select_biological_type"),
                Choice("📋 Show Current Config", "show_config"),
                Choice("🧬 JCVI Settings", "jcvi_settings"),
                Choice("ℹ️ API Info", "api_info"),
                Choice("🔙 Back", "back")
            ]
            
            action = questionary.select("Configuration:", choices=choices).ask()
            if action == "back" or action is None:
                break
                
            try:
                if action == "set_vm_type":
                    choices = []
                    for vm_type in self.supported_vm_types:
                        status = "✅" if vm_type == self.vm_type else "  "
                        desc = ""
                        if vm_type == "jcvi_optimized":
                            desc = " (JCVI + Hardware Optimization)"
                        choices.append(Choice(f"{status} {vm_type}{desc}", vm_type))
                    
                    new_type = questionary.select("Select VM type:", choices=choices).ask()
                    if new_type:
                        self.vm_type = new_type
                        print(f"🖥️ VM type set to: {new_type}")
                        if new_type == "jcvi_optimized":
                            print("   🧬 JCVI integration and hardware optimization enabled")
                            
                elif action == "select_biological_type":
                    self.select_biological_type()
                    
                elif action == "show_config":
                    chassis_display = self.chassis_type.value if hasattr(self.chassis_type, 'value') else str(self.chassis_type)
                    print(f"🦠 Chassis: {chassis_display}")
                    print(f"🔬 Biological Type: {self.selected_biological_type}")
                    print(f"🖥️ VM Type: {self.vm_type}")
                    print(f"🖥️ Active VMs: {len(self.active_vms)}")
                    print(f"⚙️ Factory API: {'✅ Available' if FACTORY_API_AVAILABLE else '❌ Not Available'}")
                    print(f"🧬 JCVI Acquisition: {'✅ Available' if ACQUISITION_AVAILABLE else '❌ Not Available'}")
                    
                elif action == "jcvi_settings":
                    print("🧬 JCVI Integration Settings:")
                    print("   • JCVI toolkit integration: Available when installed")
                    print("   • Graceful fallback: Enabled")
                    print("   • Format conversion: .genome ↔ .fasta")
                    print("   • Hardware optimization: Available in jcvi_optimized VMs")
                    print("   • Synteny analysis: Available with JCVI CLI tools")
                    if ACQUISITION_AVAILABLE:
                        print("   • Enhanced acquisition (v0.0.03): ✅ Available")
                    else:
                        print("   • Enhanced acquisition (v0.0.03): ❌ Not Available")
                        
                elif action == "api_info":
                    self.api_info()
                    
            except Exception as e:
                logger.error(f"Configuration error: {e}")
                print(f"❌ Error: {e}")
            
            questionary.press_any_key_to_continue().ask()

    def api_info(self):
        """Display Factory API information."""
        print("\n" + "="*60)
        print("🧬 BioXen Factory Pattern API v0.0.2 + JCVI Integration")
        print("="*60)
        print(f"📊 Status: {'✅ Available' if FACTORY_API_AVAILABLE else '❌ Not Available'}")
        print(f"🖥️ Supported VM Types: {', '.join(self.supported_vm_types)}")
        print(f"⚡ Active VMs: {len(self.active_vms)}")
        
        if FACTORY_API_AVAILABLE:
            print("\n🔧 Factory API Usage:")
            print("   vm = create_bio_vm(vm_id, biological_type, vm_type)")
            print("   vm = create_biological_vm(vm_type='jcvi_optimized')")
            print("   manager = ResourceManager()")
            print("   config = ConfigManager()")
            
            print("\n🧬 JCVI Integration Features:")
            print("   • Enhanced genome analysis with JCVI toolkit")
            print("   • Comparative genomics and synteny analysis")
            print("   • Automatic format conversion (.genome ↔ .fasta)")
            print("   • Hardware optimization for JCVI workflows")
            print("   • Graceful fallback when JCVI unavailable")
            
            if ACQUISITION_AVAILABLE:
                print("\n📥 Enhanced Acquisition (v0.0.03):")
                print("   • Automated genome acquisition from databases")
                print("   • Complete workflow coordination")
                print("   • Integrated analysis pipelines")
        else:
            print("\n💡 To use the Factory API:")
            print("   1. Ensure src/api/ directory exists")
            print("   2. Install bioxen-jcvi-vm-lib library")
            print("   3. Run from correct working directory")
            print("   4. Currently running in simulation mode")
        
        questionary.press_any_key_to_continue().ask()


if __name__ == "__main__":
    try:
        bioxen = InteractiveBioXenFactory()
        bioxen.main_menu()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()