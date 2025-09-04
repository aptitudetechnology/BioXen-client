#!/usr/bin/env python3
"""
Interactive BioXen CLI with Factory Pattern API and JCVI Integration.
Updated for Phase 1.1 compatibility with chassis selection
"""

import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent / 'src'))

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
    from src.hypervisor.core import BioXenHypervisor, ChassisType
    from src.genome.schema import BioXenGenomeValidator
    from src.genome.parser import BioXenRealGenomeIntegrator
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the BioXen_jcvi_vm_lib root directory")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('bioxen_factory.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class InteractiveBioXenFactory:
    """Interactive CLI for BioXen Factory Pattern API with JCVI Integration."""
    def __init__(self):
        self.validator = BioXenGenomeValidator()
        self.resource_manager = None  # Initialize when needed
        self.config_manager = ConfigManager()
        self.active_vms = {}
        self.chassis_type = ChassisType.ECOLI  # Default chassis
        self.selected_biological_type = "syn3a"
        self.vm_type = "basic"
        logger.info("BioXen Factory API initialized")

    def select_chassis(self):
        """Select chassis type for biological VMs."""
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

    def main_menu(self):
        """Display main menu with chassis and JCVI integration."""
        while True:
            print("\n" + "="*70)
            print("🧬 BioXen Factory Pattern API with JCVI Integration")
            print("="*70)
            print(f"🦠 Current Chassis: {self.chassis_type.value}")
            print(f"🧬 Biological Type: {self.selected_biological_type}")
            print(f"🏗️ VM Type: {self.vm_type}")
            print(f"⚡ Active VMs: {len(self.active_vms)}")
            
            choices = [
                Choice("🔍 Browse Genomes", "browse_genomes"),
                Choice("🧬 Load Genome", "validate_genome"),
                Choice("🖥️ Initialize Hypervisor", "init_hypervisor"),
                Choice("� Download Genomes", "download_genomes"),
                Choice("⚡ Create VM", "create_vm"),
                Choice("� Manage VMs", "manage_vms"),
                Choice("📺 Terminal Visualization", "terminal_visualization"),
                Choice("�️ Destroy VM", "destroy_vm"),
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
            self.hypervisor = BioXenHypervisor()
            print(f"✅ Hypervisor initialized successfully")
        except Exception as e:
            logger.error(f"Init error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def create_vm(self):
        """Create a biological VM using the Factory Pattern API with chassis and JCVI support."""
        if not FACTORY_API_AVAILABLE:
            print("❌ Factory API not available")
            return
        
        print(f"\n🧬 Creating Biological VM with JCVI Integration")
        print(f"🦠 Chassis: {self.chassis_type.value}")
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
            print(f"   🦠 Chassis: {self.chassis_type.value}")
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

    def jcvi_operations_menu(self):
        """JCVI-specific operations menu (Phase 1.1)."""
        if not self.active_vms:
            print("❌ No active VMs for JCVI operations")
            questionary.press_any_key_to_continue().ask()
            return
        
        # Select VM for JCVI operations
        choices = []
        for vm_id, vm in self.active_vms.items():
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
                    if genome_path and hasattr(vm, 'analyze_genome'):
                        result = vm.analyze_genome(genome_path)
                        print(f"🔬 Genome Analysis Result:")
                        for key, value in result.items():
                            print(f"   {key}: {value}")
                    else:
                        print("❌ Genome analysis not available")
                        
                elif action == "comparative_analysis":
                    genome1 = questionary.text("First genome path:", default="genomes/syn3a.genome").ask()
                    genome2 = questionary.text("Second genome path:", default="genomes/syn3a.genome").ask()
                    if genome1 and genome2 and hasattr(vm, 'run_comparative_analysis'):
                        result = vm.run_comparative_analysis(genome1, genome2)
                        print(f"📊 Comparative Analysis Result:")
                        for key, value in result.items():
                            print(f"   {key}: {value}")
                    else:
                        print("❌ Comparative analysis not available")
                        
                elif action == "format_conversion":
                    input_path = questionary.text("Input file path:", default="genomes/syn3a.genome").ask()
                    output_path = questionary.text("Output file path:", default="genomes/syn3a.fasta").ask()
                    if input_path and output_path and hasattr(vm, 'convert_genome_format'):
                        result = vm.convert_genome_format(input_path, output_path)
                        print(f"🔄 Format Conversion Result:")
                        for key, value in result.items():
                            print(f"   {key}: {value}")
                    else:
                        print("❌ Format conversion not available")
                        
                elif action == "jcvi_status":
                    if hasattr(vm, 'get_jcvi_status'):
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
                    status = vm.get_status()
                    print(f"⚡ VM {vm_id} resources: {status}")
                
                questionary.press_any_key_to_continue().ask()
                
        except Exception as e:
            logger.error(f"Resource management error: {e}")
            print(f"❌ Error: {e}")
            questionary.press_any_key_to_continue().ask()

    def jcvi_analysis_menu(self):
        """JCVI analysis and operations menu."""
        if not FACTORY_API_AVAILABLE:
            print("❌ Factory API not available")
            questionary.press_any_key_to_continue().ask()
            return
            
        while True:
            choices = [
                Choice("🔬 Analyze Genome", "analyze_genome"),
                Choice("📊 Comparative Analysis", "comparative_analysis"),
                Choice("🧬 Format Conversion", "format_conversion"),
                Choice("📈 JCVI Status", "jcvi_status"),
                Choice("🔙 Back", "back")
            ]
            
            action = questionary.select("JCVI Analysis:", choices=choices).ask()
            if action == "back" or action is None:
                break
                
            try:
                if action == "analyze_genome":
                    genome_file = questionary.text("Enter genome file path:").ask()
                    if genome_file and os.path.exists(genome_file):
                        # Use JCVI manager for analysis
                        from src.api.jcvi_manager import JCVIManager
                        manager = JCVIManager()
                        if manager.is_available():
                            result = manager.analyze_genome(genome_file)
                            print(f"📊 Analysis Result:\n{result}")
                        else:
                            print("❌ JCVI not available")
                    else:
                        print("❌ File not found")
                        
                elif action == "comparative_analysis":
                    print("🔬 Starting comparative analysis...")
                    genome1 = questionary.text("Enter first genome file:").ask()
                    genome2 = questionary.text("Enter second genome file:").ask()
                    
                    if genome1 and genome2 and os.path.exists(genome1) and os.path.exists(genome2):
                        from src.api.jcvi_manager import JCVIManager
                        manager = JCVIManager()
                        if manager.is_available():
                            result = manager.run_comparative_analysis(genome1, genome2)
                            print(f"📈 Comparative Analysis:\n{result}")
                        else:
                            print("❌ JCVI not available")
                    else:
                        print("❌ Invalid files")
                        
                elif action == "format_conversion":
                    input_file = questionary.text("Enter input file:").ask()
                    output_format = questionary.select("Output format:", 
                                                     choices=["fasta", "genbank", "gff"]).ask()
                    
                    if input_file and output_format and os.path.exists(input_file):
                        from src.api.jcvi_manager import JCVIManager
                        manager = JCVIManager()
                        if manager.is_available():
                            output_file = f"{os.path.splitext(input_file)[0]}.{output_format}"
                            success = manager.convert_format(input_file, output_file, output_format)
                            if success:
                                print(f"✅ Converted to: {output_file}")
                            else:
                                print("❌ Conversion failed")
                        else:
                            print("❌ JCVI not available")
                    else:
                        print("❌ Invalid input")
                        
                elif action == "jcvi_status":
                    from src.api.jcvi_manager import JCVIManager
                    manager = JCVIManager()
                    print(f"🧬 JCVI Available: {'✅' if manager.is_available() else '❌'}")
                    if manager.is_available():
                        print("🔧 Available operations:")
                        print("   • Genome analysis")
                        print("   • Comparative genomics")
                        print("   • Format conversion")
                        print("   • Synteny analysis")
                    
                questionary.press_any_key_to_continue().ask()
                
            except Exception as e:
                logger.error(f"JCVI analysis error: {e}")
                print(f"❌ Error: {e}")
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

    def _validate_single_genome(self, genome):
        """Validate single genome."""
        print(f"\n🔬 Validating {genome['name']}...")
        try:
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
        except Exception as e:
            logger.error(f"Validation error: {e}")
            print(f"❌ Error: {e}")

    def download_genomes(self):
        """Download genomes from NCBI."""
        if not self._check_hypervisor():
            return
        print("\n🌐 Download Genomes")
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
                Choice("📋 Show Current Config", "show_config"),
                Choice("🧬 JCVI Settings", "jcvi_settings"),
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
                            
                elif action == "show_config":
                    print(f"🔬 Biological Type: {self.selected_biological_type}")
                    print(f"🖥️ VM Type: {self.vm_type}")
                    print(f"🖥️ Active VMs: {len(self.active_vms)}")
                    print(f"⚙️ Factory API: {'✅ Available' if FACTORY_API_AVAILABLE else '❌ Not Available'}")
                    
                elif action == "jcvi_settings":
                    print("🧬 JCVI Integration Settings:")
                    print("   • JCVI toolkit integration: Available when installed")
                    print("   • Graceful fallback: Enabled")
                    print("   • Format conversion: .genome ↔ .fasta")
                    print("   • Hardware optimization: Available in jcvi_optimized VMs")
                    print("   • Synteny analysis: Available with JCVI CLI tools")
                    
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
        print(f"🔬 Supported Biological Types: {', '.join(self.supported_bio_types)}")
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
        else:
            print("\n💡 To use the Factory API:")
            print("   1. Ensure src/api/ directory exists")
            print("   2. Install bioxen-jcvi-vm-lib library")
            print("   3. Run from correct working directory")
        
        questionary.press_any_key_to_continue().ask()

if __name__ == "__main__":
    bioxen = InteractiveBioXenFactory()
    bioxen.main_menu()
