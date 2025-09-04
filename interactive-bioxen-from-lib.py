
#!/usr/bin/env python3
"""
Interactive BioXen CLI for genome selection and VM management with bioxen-jcvi-vm-lib v0.0.1.
Factory Pattern API Implementation.
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

# New Factory Pattern API imports - bioxen-jcvi-vm-lib v0.0.1
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
    
    # Direct access to underlying components when needed
    from hypervisor.core import BioXenHypervisor
    from chassis import ChassisType, EcoliChassis, YeastChassis
    from genome.parser import BioXenRealGenomeIntegrator
    from monitoring.profiler import PerformanceProfiler
    
    MODERN_VM_AVAILABLE = True
    print("✅ BioXen JCVI VM Library v0.0.1 Factory API loaded successfully")
except ImportError as e:
    print(f"⚠️ BioXen JCVI VM library Factory API not available: {e}")
    print("💡 Make sure you're running from the correct directory with src/api/ available")
    MODERN_VM_AVAILABLE = False

# Legacy support fallback (commented out - old library)
# try:
#     from pylua_bioxen_vm_lib import VMManager, InteractiveSession
#     from pylua_bioxen_vm_lib.exceptions import (
#         InteractiveSessionError, AttachError, DetachError, 
#         SessionNotFoundError, SessionAlreadyExistsError, 
#         VMManagerError, LuaVMError
#     )
#     from pylua_bioxen_vm_lib.utils.curator import (
#         get_curator, bootstrap_lua_environment, Package,
#         PackageRegistry, PackageInstaller, search_packages
#     )
#     from pylua_bioxen_vm_lib.env import EnvironmentManager
#     from pylua_bioxen_vm_lib.package_manager import PackageManager, RepositoryManager
#     LEGACY_VM_AVAILABLE = True
# except ImportError:
#     LEGACY_VM_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('bioxen.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class InteractiveBioXen:
    """Interactive CLI for BioXen hypervisor and genome management using Factory Pattern API v0.0.1."""
    def __init__(self):
        # Factory Pattern API state
        self.hypervisor = None  # Will be BioXenHypervisor instance
        self.active_vms = {}  # Dict[str, BiologicalVM] - track created VMs
        self.available_genomes = []
        self.chassis_type = ChassisType.ECOLI
        self.selected_biological_type = "syn3a"  # Default biological type
        self.vm_type = "basic"  # Default infrastructure type (basic/xcpng)
        self.visualization_active = False
        
        if MODERN_VM_AVAILABLE:
            # Initialize Factory API components
            self.supported_bio_types = get_supported_biological_types()
            self.supported_vm_types = get_supported_vm_types()
            logger.info(f"BioXen Factory API initialized - Bio types: {self.supported_bio_types}, VM types: {self.supported_vm_types}")
        else:
            logger.warning("BioXen initialized without Factory API support")

    def _check_hypervisor(self):
        """Check if hypervisor is initialized."""
        if self.hypervisor is None:
            print("❌ Hypervisor not initialized. Select 'Initialize Hypervisor'.")
            return False
        return True

    def _suggest_unique_vm_id(self, base_name: str) -> str:
        """Suggest a unique VM ID."""
        if not self.hypervisor:
            return f"vm_{base_name}"
        
        # Use new API to get existing VMs
        existing_vms = self.hypervisor.list_vms()
        existing_ids = set(vm_info.get('id', '') for vm_info in existing_vms.values())
        
        candidate = f"vm_{base_name}"
        if candidate not in existing_ids:
            return candidate
        for i in range(1, 100):
            candidate = f"vm_{base_name}_{i}"
            if candidate not in existing_ids:
                return candidate
        return f"vm_{base_name}_{int(time.time() % 10000)}"

    def main_menu(self):
        """Display main menu with Factory Pattern API."""
        while True:
            print("\n" + "="*70)
            print("🧬 BioXen Factory Pattern API v0.0.1")
            print(f"🔬 Current: {self.selected_biological_type} | {self.vm_type}")
            print("="*70)
            
            choices = [
                Choice("🔍 Browse Genomes", "browse_genomes"),
                Choice("🧬 Select Biological Type", "select_biological_type"),
                Choice("🖥️ Initialize Hypervisor", "init_hypervisor"),
                Choice("🌐 Download Genomes", "download_new"),
            ]
            
            if MODERN_VM_AVAILABLE:
                choices.extend([
                    Choice("⚡ Create Biological VM", "create_biological_vm"),
                    Choice("📊 Manage VMs", "manage_vms"),
                    Choice("🔧 VM Operations", "vm_operations_menu"),
                    Choice("📈 Resource Management", "resource_management"),
                    Choice("⚙️ Configuration", "configuration_menu"),
                ])
            
            choices.extend([
                Choice("📺 Terminal Visualization", "terminal_vis"),
                Choice("❌ Exit", "exit")
            ])
            
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
        if not MODERN_VM_AVAILABLE:
            print("❌ Factory API not available")
            return
            
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
            try:
                config = ConfigManager.load_defaults(action)
                print(f"📋 Loaded configuration: {config}")
            except Exception as e:
                print(f"⚠️ Could not load config: {e}")
        
        questionary.press_any_key_to_continue().ask()

    def create_biological_vm(self):
        """Create a biological VM using the Factory Pattern API."""
        if not MODERN_VM_AVAILABLE:
            print("❌ Factory API not available")
            return
        
        print(f"\n🧬 Creating Biological VM")
        print(f"� Biological Type: {self.selected_biological_type}")
        print(f"🖥️ VM Type: {self.vm_type}")
        
        vm_id = questionary.text("Enter VM ID:", default=self._suggest_unique_vm_id(self.selected_biological_type)).ask()
        if not vm_id:
            return
            
        try:
            print(f"🔄 Creating VM: {vm_id}")
            
            # Use Factory Pattern API
            vm = create_bio_vm(vm_id, self.selected_biological_type, self.vm_type)
            
            print(f"✅ VM created successfully: {vm_id}")
            print(f"   Type: {vm.get_vm_type()}")
            print(f"   Biological: {vm.get_biological_type()}")
            
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
        """Resource management using BioResourceManager."""
        if not self.active_vms:
            print("❌ No active VMs for resource management")
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
                        manager.allocate_atp(float(atp))
                        print(f"🔋 ATP allocated: {atp}%")
                elif action == "allocate_ribosomes":
                    ribosomes = questionary.text("Ribosome count:", default="15").ask()
                    if ribosomes:
                        manager.allocate_ribosomes(int(ribosomes))
                        print(f"🧬 Ribosomes allocated: {ribosomes}")
                elif action == "optimize":
                    manager.optimize_resources_for_biological_type()
                    print("⚡ Resources optimized for biological type")
                elif action == "usage":
                    usage = manager.get_resource_usage()
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
                    config = ConfigManager.load_defaults(self.selected_biological_type)
                    print(f"📋 Defaults for {self.selected_biological_type}: {config}")
                elif action == "validate_config":
                    # Create a sample config to validate
                    config = {"biological_type": self.selected_biological_type, "vm_type": self.vm_type}
                    is_valid = ConfigManager.validate_config(config, self.vm_type)
                    print(f"✅ Configuration valid: {is_valid}")
                elif action == "set_vm_type":
                    choices = []
                    for vm_type in self.supported_vm_types:
                        status = "✅" if vm_type == self.vm_type else "  "
                        choices.append(Choice(f"{status} {vm_type}", vm_type))
                    
                    new_type = questionary.select("Select VM type:", choices=choices).ask()
                    if new_type and validate_vm_type(new_type):
                        self.vm_type = new_type
                        print(f"🖥️ VM type set to: {new_type}")
                elif action == "show_config":
                    print(f"🔬 Biological Type: {self.selected_biological_type}")
                    print(f"🖥️ VM Type: {self.vm_type}")
                    print(f"🏗️ Chassis: {self.chassis_type}")
                    
            except Exception as e:
                logger.error(f"Configuration error: {e}")
                print(f"❌ Error: {e}")
            
            questionary.press_any_key_to_continue().ask()

    # Compatibility methods for existing functionality
    def browse_genomes(self):
        """Browse available genomes."""
        print("\n🔍 Browsing Genomes")
        genome_dir = Path("genomes")
        if not genome_dir.exists():
            print("❌ No genomes directory found")
            print("💡 Use 'Download Genomes' to get genome files")
        else:
            genomes = list(genome_dir.glob("*.genome"))
            if genomes:
                print(f"✅ Found {len(genomes)} genomes:")
                for i, genome in enumerate(genomes, 1):
                    print(f"   {i}. {genome.name}")
            else:
                print("❌ No genome files found")
        questionary.press_any_key_to_continue().ask()

    def validate(self):
        """Validate/load a genome - updated for Factory API."""
        print("\n🧬 Load Genome for Factory API")
        print("ℹ️  In Factory API, genomes are loaded automatically when creating VMs")
        print(f"🔬 Current biological type: {self.selected_biological_type}")
        
        if questionary.confirm("Change biological type?").ask():
            self.select_biological_type()
        questionary.press_any_key_to_continue().ask()

    def download_new(self):
        """Download new genomes."""
        print("\n🌐 Download Genomes")
        print("📥 Genome download functionality")
        print("💡 This would connect to genome repositories")
        questionary.press_any_key_to_continue().ask()

    def terminal_vis(self):
        """Terminal visualization."""
        print("\n📺 Terminal Visualization")
        if self.active_vms:
            print(f"🖥️ Active VMs: {len(self.active_vms)}")
            for vm_id, vm in self.active_vms.items():
                try:
                    status = vm.get_status()
                    print(f"   {vm_id}: {status}")
                except:
                    print(f"   {vm_id}: Status unavailable")
        else:
            print("❌ No active VMs to visualize")
        questionary.press_any_key_to_continue().ask()

    def genetic_circuits_menu(self):
        """Genetic circuits management menu - new feature from JCVI library."""
        while True:
            choices = [
                Choice("🔧 Create Demo Circuit", "create_demo_circuit"),
                Choice("🧬 Create Metabolic Circuit", "create_metabolic_circuit"),
                Choice("✅ Validate Circuit", "validate_circuit"),
                Choice("📊 Circuit Factory", "circuit_factory_menu"),
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

    def vm_image_builder_menu(self):
        """VM Image Builder menu - new feature."""
        while True:
            choices = [
                Choice("🏗️ Build VM Image", "build_vm_image"),
                Choice("📋 List Available Images", "list_vm_images"),
                Choice("🔙 Back", "back")
            ]
            action = questionary.select("VM Image Builder:", choices=choices).ask()
            if action is None or action == "back":
                break
            try:
                getattr(self, action)()
            except Exception as e:
                logger.error(f"VM Image Builder error: {e}")
                print(f"❌ Error: {e}")
                questionary.press_any_key_to_continue().ask()
            choice = questionary.select("📦 Package Management", choices=choices).ask()
            if choice is None or choice == "back":
                break
            try:
                getattr(self, choice)()
            except KeyboardInterrupt:
                print("\n⚠️ Cancelled")
                continue
            except Exception as e:
                logger.error(f"Package error: {e}")
                print(f"❌ Error: {e}")
                questionary.press_any_key_to_continue().ask()

    # New genetic circuit implementations 
    def create_demo_circuit(self):
        """Create a demo genetic circuit."""
        print("🔧 Creating demo genetic circuit...")
        try:
            circuit = create_demo_circuit()
            print(f"✅ Demo circuit created: {circuit}")
            
            # Display circuit information
            if hasattr(circuit, 'get_info'):
                info = circuit.get_info()
                print(f"📊 Circuit Info: {info}")
                
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

    def circuit_factory_menu(self):
        """Circuit factory operations."""
        print("📊 Circuit Factory")
        try:
            factory_info = self.circuit_factory
            print(f"🏭 Factory available: {factory_info}")
            
        except Exception as e:
            print(f"❌ Error accessing circuit factory: {e}")
        
        questionary.press_any_key_to_continue().ask()

    def build_vm_image(self):
        """Build a VM image."""
        print("🏗️ Building VM image...")
        try:
            builder_info = self.vm_image_builder
            print(f"🔧 VM Image Builder: {builder_info}")
            
        except Exception as e:
            print(f"❌ Error building VM image: {e}")
        
        questionary.press_any_key_to_continue().ask()

    def list_vm_images(self):
        """List available VM images."""
        print("📋 Available VM Images:")
        try:
            # This would list available images
            print("🔧 VM image listing functionality")
            
        except Exception as e:
            print(f"❌ Error listing VM images: {e}")
        
        questionary.press_any_key_to_continue().ask()

    # Legacy package methods (now disabled in new library)
    def search_lua_packages(self):
        """Search Lua packages."""
        query = questionary.text("🔍 Search query:").ask()
        if not query:
            return
        try:
            packages = search_packages(query)
            if packages:
                print(f"\n📦 Found {len(packages)} packages:")
                for pkg in packages:
                    print(f"  • {pkg.name} ({pkg.version}) - {pkg.description}")
            else:
                print("❌ No packages found")
        except Exception as e:
            logger.error(f"Search error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def install_lua_package(self):
        """Install Lua package."""
        package_name = questionary.text("📦 Package name:").ask()
        if not package_name:
            return
        version = questionary.text("🏷️ Version (empty for latest):").ask()
        try:
            print(f"🔄 Installing '{package_name}'...")
            success = self.package_installer.install_package(package_name, version=version) if version else self.package_installer.install_package(package_name)
            print(f"{'✅' if success else '❌'} Package '{package_name}' {'installed' if success else 'failed'}")
        except Exception as e:
            logger.error(f"Install error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def list_installed_packages(self):
        """List installed Lua packages."""
        try:
            packages = self.package_registry.get_installed_packages()
            if packages:
                print(f"\n📋 Installed ({len(packages)}):")
                for pkg in packages:
                    print(f"  • {pkg.name} ({pkg.version}) - {pkg.description}")
            else:
                print("📦 No packages installed")
        except Exception as e:
            logger.error(f"List error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def update_lua_package(self):
        """Update Lua package."""
        try:
            packages = self.package_registry.get_installed_packages()
            if not packages:
                print("📦 No packages installed")
                return
            choices = [Choice(f"{pkg.name} ({pkg.version})", pkg.name) for pkg in packages]
            package_name = questionary.select("⬆️ Update package:", choices=choices).ask()
            if package_name:
                print(f"🔄 Updating '{package_name}'...")
                success = self.package_installer.update_package(package_name)
                print(f"{'✅' if success else '❌'} Package '{package_name}' {'updated' if success else 'failed'}")
        except Exception as e:
            logger.error(f"Update error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def remove_lua_package(self):
        """Remove Lua package."""
        try:
            packages = self.package_registry.get_installed_packages()
            if not packages:
                print("📦 No packages installed")
                return
            choices = [Choice(f"{pkg.name} ({pkg.version})", pkg.name) for pkg in packages]
            package_name = questionary.select("🗑️ Remove package:", choices=choices).ask()
            if package_name and questionary.confirm(f"Remove '{package_name}'?").ask():
                success = self.package_installer.remove_package(package_name)
                print(f"{'✅' if success else '❌'} Package '{package_name}' {'removed' if success else 'failed'}")
        except Exception as e:
            logger.error(f"Remove error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def bootstrap_lua_environment(self):
        """Bootstrap Lua environment."""
        env_name = questionary.text("🏗️ Environment name:").ask()
        if not env_name:
            return
        try:
            print(f"🔄 Bootstrapping '{env_name}'...")
            success = bootstrap_lua_environment(env_name)
            print(f"{'✅' if success else '❌'} Environment '{env_name}' {'bootstrapped' if success else 'failed'}")
        except Exception as e:
            logger.error(f"Bootstrap error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def manage_lua_environments(self):
        """Manage Lua environments."""
        try:
            choices = [
                Choice("🆕 Create Environment", "create"),
                Choice("🔄 Switch Environment", "switch"),
                Choice("📋 List Environments", "list"),
                Choice("🗑️ Delete Environment", "delete"),
                Choice("🔙 Back", "back")
            ]
            action = questionary.select("🔧 Environment Management:", choices=choices).ask()
            if action == "create":
                env_name = questionary.text("Environment name:").ask()
                if env_name:
                    self.env_manager.create_environment(env_name)
                    print(f"✅ Environment '{env_name}' created")
            elif action == "switch":
                environments = self.env_manager.list_environments()
                if environments:
                    choices = [Choice(env.name, env.name) for env in environments]
                    selected = questionary.select("Select environment:", choices=choices).ask()
                    if selected:
                        self.env_manager.activate_environment(selected)
                        print(f"✅ Switched to '{selected}'")
                else:
                    print("No environments available")
            elif action == "list":
                environments = self.env_manager.list_environments()
                if environments:
                    print("\n📋 Environments:")
                    for env in environments:
                        print(f"  {'✅' if env.is_active else '  '} {env.name}")
                else:
                    print("📋 No environments")
            elif action == "delete":
                environments = self.env_manager.list_environments()
                if environments:
                    choices = [Choice(env.name, env.name) for env in environments]
                    selected = questionary.select("Delete environment:", choices=choices).ask()
                    if selected and questionary.confirm(f"Delete '{selected}'?").ask():
                        self.env_manager.delete_environment(selected)
                        print(f"✅ Environment '{selected}' deleted")
                else:
                    print("No environments to delete")
        except Exception as e:
            logger.error(f"Environment error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def package_info(self):
        """Display Lua package info."""
        package_name = questionary.text("📊 Package name:").ask()
        if not package_name:
            return
        try:
            package_info = self.package_registry.get_package_info(package_name)
            if package_info is None:
                print(f"❌ Package '{package_name}' not found")
                return
            print(f"\n📦 {package_name}\n   Version: {package_info.version}\n   Description: {package_info.description}\n   Dependencies: {', '.join(package_info.dependencies) if package_info.dependencies else 'None'}")
        except Exception as e:
            logger.error(f"Package info error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def update_all_packages(self):
        """Update all Lua packages."""
        try:
            packages = self.package_registry.get_installed_packages()
            if not packages:
                print("📦 No packages installed")
                return
            if not questionary.confirm(f"Update {len(packages)} packages?").ask():
                return
            print(f"🔄 Updating {len(packages)} packages...")
            updated_count = 0
            for pkg in packages:
                try:
                    success = self.package_installer.update_package(pkg.name)
                    print(f"  {'✅' if success else '⚠️'} {pkg.name} {'updated' if success else '- no update'}")
                    if success:
                        updated_count += 1
                except Exception as e:
                    print(f"  ❌ {pkg.name} - error: {e}")
            print(f"✅ Updated {updated_count}/{len(packages)}")
        except Exception as e:
            logger.error(f"Update error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def package_settings(self):
        """Configure package settings."""
        try:
            choices = [
                Choice("📝 View Settings", "view"),
                Choice("🔄 Update Repositories", "repos"),
                Choice("🧹 Clean Cache", "cache"),
                Choice("🔙 Back", "back")
            ]
            action = questionary.select("⚙️ Settings:", choices=choices).ask()
            if action == "view":
                settings = self.package_manager.get_settings()
                print("\n📝 Settings:")
                for k, v in settings.items():
                    print(f"  {k}: {v}")
            elif action == "repos":
                print("🔄 Updating repositories...")
                self.repository_manager.update_repositories()
                print("✅ Repositories updated")
            elif action == "cache":
                print("🧹 Cleaning cache...")
                self.package_manager.clean_cache()
                print("✅ Cache cleaned")
        except Exception as e:
            logger.error(f"Settings error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def create_lua_vm(self):
        """Create one-shot Lua VM."""
        print("\n🌙 Lua VM (One-shot)\n💡 Temporary VM, exits on completion")
        use_packages = questionary.confirm("📦 Load packages?").ask()
        try:
            with self.vm_manager as manager:
                session = manager.create_interactive_vm("temp_vm")
                if use_packages:
                    try:
                        packages = self.package_registry.get_installed_packages()
                        for pkg in packages:
                            session.load_package(pkg.name)
                        print(f"📦 Loaded {len(packages)} packages")
                    except Exception as e:
                        logger.warning(f"Package load error: {e}")
                        print(f"⚠️ Warning: {e}")
                print("✅ VM created\n💡 Type 'exit' or Ctrl+D")
                session.interactive_loop()
                print("👋 Session ended")
        except (VMManagerError, LuaVMError, InteractiveSessionError) as e:
            logger.error(f"VM error: {e}")
            print(f"❌ Error: {e}")
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted")
        questionary.press_any_key_to_continue().ask()

    def create_persistent_vm(self):
        """Create persistent Lua VM."""
        print("\n🖥️ Persistent Lua VM\n💡 Attachable multiple times")
        vm_id = questionary.text("VM ID:", default=self._suggest_unique_vm_id("lua"), validate=lambda x: x.strip() or "ID required").ask()
        if not vm_id:
            return
        sessions = self.vm_manager.list_sessions()
        if any(s.vm_id == vm_id for s in sessions):
            print(f"❌ VM ID '{vm_id}' exists")
            return
        env_choices = [Choice("Default", None)] + [Choice(env.name, env.name) for env in self.env_manager.list_environments()]
        selected_env = questionary.select("Environment:", choices=env_choices).ask()
        try:
            session = self.vm_manager.create_interactive_vm(vm_id)
            if selected_env:
                session.set_environment(selected_env)
                print(f"📦 Environment '{selected_env}' loaded")
            print(f"✅ VM '{vm_id}' created\n💡 Use 'Attach Lua VM'")
        except (SessionAlreadyExistsError, VMManagerError, LuaVMError) as e:
            logger.error(f"VM error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def attach_lua_vm(self):
        """Attach to persistent Lua VM."""
        print("\n🔗 Attach Lua VM")
        try:
            sessions = self.vm_manager.list_sessions()
            if not sessions:
                print("❌ No VMs available\n💡 Create a persistent VM")
                return
            choices = [Choice(f"🖥️ {s.vm_id}", s.vm_id) for s in sessions]
            vm_id = questionary.select("Select VM:", choices=choices).ask()
            if not vm_id:
                return
            print(f"🔗 Attaching to '{vm_id}'...")
            session = self.vm_manager.attach_to_vm(vm_id)
            print("✅ Attached\n💡 Type 'exit' or Ctrl+D")
            session.interactive_loop()
            self.vm_manager.detach_from_vm(vm_id)
            print(f"👋 Detached from '{vm_id}'")
        except (SessionNotFoundError, AttachError, DetachError) as e:
            logger.error(f"Attach error: {e}")
            print(f"❌ Error: {e}")
        except KeyboardInterrupt:
            print("\n⚠️ Detached")
        questionary.press_any_key_to_continue().ask()

    def select_chassis(self):
        """Select chassis type."""
        print("\n🧬 Select Chassis")
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
        return chassis

    def validate(self):
        """Alias for validate_genomes for menu compatibility.""" 
        return self.validate_genomes()

    def browse_genomes(self):
        """Alias for browse_available_genomes for menu compatibility."""
        return self.browse_available_genomes()

    def status(self):
        """Alias for status method for menu compatibility."""
        return self.vm_status()

    def destroy_vm(self):
        """Alias for destroy_vm_interactive for menu compatibility."""
        return self.destroy_vm_interactive()

    def terminal_vis(self):
        """Alias for terminal_visualization for menu compatibility."""
        return self.terminal_visualization()

    def download_new(self):
        """Alias for download_genome_interactive for menu compatibility."""
        return self.download_genome_interactive()

    def init_hypervisor(self):
        """Alias for initialize_hypervisor for menu compatibility."""
        return self.initialize_hypervisor()

    def initialize_hypervisor(self):
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
            print(f"✅ Hypervisor initialized: {self.chassis_type.value}")
        except Exception as e:
            logger.error(f"Init error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def browse_available_genomes(self):
        """Browse genomes."""
        print("\n🔍 Browse Genomes")
        genome_dir = Path("genomes")
        if not genome_dir.exists():
            print("❌ No genomes directory\n💡 Use 'Download Genomes'")
            return questionary.press_any_key_to_continue().ask()
        genomes = list(genome_dir.glob("*.genome"))
        if not genomes:
            print("❌ No genomes found\n💡 Use 'Download Genomes'")
            return questionary.press_any_key_to_continue().ask()
        print(f"✅ Found {len(genomes)} genomes\n" + "="*60)
        for i, genome in enumerate(genomes, 1):
            try:
                size_kb = genome.stat().st_size / 1024
                print(f"\n{i}. 🧬 {genome.stem}\n   📁 {genome.name}\n   💾 {size_kb:.1f} KB")
                integrator = BioXenRealGenomeIntegrator(genome)
                stats = integrator.get_genome_stats()
                if stats:
                    print(f"   🔬 Genes: {stats.get('total_genes', 'Unknown')}")
                    if 'essential_genes' in stats:
                        print(f"   ⚡ Essential: {stats['essential_genes']} ({stats.get('essential_percentage', 0):.1f}%)")
                    print(f"   🦠 Organism: {stats.get('organism', 'Unknown')}")
            except Exception as e:
                logger.warning(f"Error reading {genome}: {e}")
                print(f"   ❌ Error: {e}")
        print("\n" + "="*60 + f"\n📋 Total: {len(genomes)} genomes")
        questionary.press_any_key_to_continue().ask()

    def download_genomes(self):
        """Download genomes from NCBI."""
        if not self._check_hypervisor():
            return
        print("\n📥 Download Genomes")
        options = [
            {"display": "🌐 All Genomes", "accession": "download_all_real", "name": "all", "size": 0},
            {"display": "🦠 E. coli K-12", "accession": "NC_000913.3", "name": "E_coli_K12", "size": 4641652},
            {"display": "🍄 S. cerevisiae", "accession": "NC_001133.9", "name": "S_cerevisiae", "size": 230218},
            {"display": "🔬 M. genitalium", "accession": "NC_000908.2", "name": "M_genitalium", "size": 580076},
            {"display": "🧪 Custom genome", "accession": "custom", "name": "custom", "size": 1000000}
        ]
        choice = questionary.select("Select genome:", choices=[Choice(opt["display"], opt) for opt in options]).ask()
        if choice is None:
            return
        if choice["accession"] == "download_all_real":
            self._download_all_real_genomes()
        elif choice["accession"] == "custom":
            self._download_custom_genome()
        else:
            self._download_individual_genome(choice)
        questionary.press_any_key_to_continue().ask()

    def _download_all_real_genomes(self):
        """Download all bacterial genomes."""
        print("\n🌐 Downloading All Genomes")
        if not questionary.confirm("Download all genomes?").ask():
            return
        try:
            import subprocess
            result = subprocess.run([sys.executable, 'download_genomes.py', 'all'], capture_output=True, text=True, cwd=Path(__file__).parent)
            print(f"{'✅' if result.returncode == 0 else '❌'} Downloaded all genomes{'!' if result.returncode == 0 else f': {result.stderr}'}")
        except Exception as e:
            logger.error(f"Download error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def _download_individual_genome(self, choice):
        """Download individual genome."""
        accession, name, size = choice["accession"], choice["name"], choice["size"]
        print(f"\n🌐 Downloading {name}\n   Accession: {accession}")
        if not questionary.confirm(f"Download {name}?").ask():
            return
        try:
            from genome_download_helper import GenomeDownloadHelper
            helper = GenomeDownloadHelper("genomes")
            success, msg = helper.download_genome(accession, name)
            genome_file = Path("genomes") / f"{name}.genome"
            if genome_file.exists() and genome_file.stat().st_size > 1000:
                print(f"✅ Downloaded {name}: {genome_file.stat().st_size / (1024 * 1024):.1f} MB")
            else:
                print(f"⚠️ {msg}\n🔄 Creating simulated genome...")
                self._create_simulated_genome(accession, name, size)
        except Exception as e:
            logger.error(f"Download error: {e}")
            print(f"❌ Error: {e}\n🔄 Creating simulated genome...")
            self._create_simulated_genome(accession, name, size)

    def _download_custom_genome(self):
        """Download custom genome."""
        accession = questionary.text("Accession (e.g., NC_000913.3):").ask()
        if not accession:
            return
        name = questionary.text("Name:").ask() or accession.replace(".", "_")
        self._download_individual_genome({"accession": accession, "name": name, "size": 1000000})

    def _create_simulated_genome(self, accession: str, name: str, size: int):
        """Create simulated genome."""
        print(f"\n🔄 Generating {name}...")
        try:
            import random
            genome_data = ''.join(random.choice(['A', 'T', 'G', 'C']) for _ in range(size))
            self.available_genomes.append({"accession": accession, "name": name, "data": genome_data})
            print(f"✅ Created {name}: {len(genome_data):,} bp (simulated)")
        except Exception as e:
            logger.error(f"Simulated genome error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

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
                is_valid, messages = self.validator.validate_genome(genome['file_path'])
                if is_valid:
                    print("✅ Valid")
                else:
                    print("❌ Invalid:")
                    for msg in messages:
                        print(f"   - {msg}")
                    all_valid = False
            except Exception as e:
                logger.error(f"Validation error: {e}")
                print(f"❌ Error: {e}")
                all_valid = False
        print("\n" + ("✅ All valid" if all_valid else "⚠️ Some failed"))
        questionary.press_any_key_to_continue().ask()

    def _validate_single_genome(self, genome):
        """Validate single genome."""
        print(f"\n🔬 Validating {genome['name']}...")
        try:
            is_valid, messages = self.validator.validate_genome(genome['file_path'])
            if is_valid:
                print("✅ Valid")
                self.available_genomes.append({"name": genome['name'], "file_path": genome['file_path'], "data": None})
            else:
                print("❌ Invalid:")
                for msg in messages:
                    print(f"   - {msg}")
        except Exception as e:
            logger.error(f"Validation error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def create_vm(self):
        """Create BioXen VM."""
        if not self._check_hypervisor():
            return
        print("\n⚡ Create VM")
        genome_dir = Path("genomes")
        if not genome_dir.exists() or not list(genome_dir.glob("*.genome")):
            print("❌ No genomes\n💡 Use 'Download Genomes'")
            return questionary.press_any_key_to_continue().ask()
        choices = [Choice(f"🧬 {g.stem}", g) for g in genome_dir.glob("*.genome")]
        if not choices:
            print("❌ No valid genomes")
            return questionary.press_any_key_to_continue().ask()
        genome_path = questionary.select("Select genome:", choices=choices).ask()
        if not genome_path:
            print("❌ Cancelled")
            return
        genome_name = genome_path.stem
        vm_id = self._suggest_unique_vm_id(genome_name)
        print(f"\n⚙️ Configuring {genome_name}")
        min_memory_kb, boot_time_ms = 1024, 100
        try:
            integrator = BioXenRealGenomeIntegrator(genome_path)
            template = integrator.create_vm_template()
            if template:
                min_memory_kb = template.get('min_memory_kb', min_memory_kb)
                boot_time_ms = template.get('boot_time_ms', boot_time_ms)
        except Exception as e:
            logger.warning(f"Template error: {e}")
            print(f"⚠️ Using defaults: {e}")
        mem = questionary.text(f"Memory (KB, default: {min_memory_kb}):", default=str(min_memory_kb), validate=lambda x: x.isdigit() and int(x) > 0).ask()
        boot = questionary.text(f"Boot time (ms, default: {boot_time_ms}):", default=str(boot_time_ms), validate=lambda x: x.isdigit() and int(x) > 0).ask()
        try:
            print(f"\n🔄 Creating '{vm_id}'...")
            resource_alloc = ResourceAllocation(
                memory_kb=int(mem or min_memory_kb), 
                boot_time_ms=int(boot or boot_time_ms),
                ribosomes=4,  # Default allocation
                atp_percentage=10.0  # Default 10% ATP
            )
            result = self.hypervisor.create_vm(vm_id, str(genome_path), resource_alloc)
            if result:
                vm_state = self.hypervisor.get_vm_state(vm_id)
                print(f"✅ VM '{vm_id}' created: {genome_name}, state: {vm_state}")
            else:
                print(f"❌ Failed to create VM '{vm_id}'")
        except Exception as e:
            logger.error(f"VM error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def vm_status(self):
        """Display hypervisor/VM status."""
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
                    action = questionary.select(f"Actions for '{vm_id}':", choices=[
                        Choice("⏹️ Stop", "stop"), Choice("🔄 Restart", "restart"), Choice("🗑️ Destroy", "destroy"), Choice("↩️ Back", "back")
                    ]).ask()
                    if action == "stop":
                        self.hypervisor.stop_vm(vm_id)
                        print(f"✅ '{vm_id}' stopped")
                    elif action == "restart":
                        self.hypervisor.restart_vm(vm_id)
                        print(f"✅ '{vm_id}' restarted")
                    elif action == "destroy":
                        self.hypervisor.destroy_vm(vm_id)
                        print(f"✅ '{vm_id}' destroyed")
        questionary.press_any_key_to_continue().ask()

    def destroy_vm(self):
        """Destroy VM."""
        if not self._check_hypervisor():
            return
        if not self.hypervisor.vms:
            print("❌ No VMs to destroy")
            return questionary.press_any_key_to_continue().ask()
        choices = [Choice(f"{vm_id} ({self.hypervisor.get_vm_state(vm_id).value})", vm_id) for vm_id in self.hypervisor.vms]
        vm_id = questionary.select("Destroy VM:", choices=choices).ask()
        if vm_id and questionary.confirm(f"Destroy '{vm_id}'?").ask():
            try:
                self.hypervisor.destroy_vm(vm_id)
                print(f"✅ '{vm_id}' destroyed")
            except Exception as e:
                logger.error(f"Destroy error: {e}")
                print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def destroy_vm_interactive(self):
        """Destroy a VM interactively."""
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

    def terminal_visualization(self):
        """Terminal visualization menu."""
        return self.toggle_terminal_visualization()

    def download_genome_interactive(self):
        """Download genomes interactively."""
        print("\n🌐 Download Genomes")
        print("💡 This would connect to genome repositories and download genomes")
        print("🔧 Implementation placeholder for new JCVI library")
        questionary.press_any_key_to_continue().ask()

    def toggle_terminal_visualization(self):
        """Toggle visualization."""
        if not self._check_hypervisor():
            return
        print("\n📺 Visualization")
        self.visualization_active = not self.visualization_active
        print(f"{'✅ Started' if self.visualization_active else '✅ Stopped'} (placeholder)")
        questionary.press_any_key_to_continue().ask()

if __name__ == "__main__":
    bioxen = InteractiveBioXen()
    bioxen.main_menu()
```