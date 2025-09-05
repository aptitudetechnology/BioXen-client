```python
#!/usr/bin/env python3
"""
Interactive BioXen CLI for genome selection and VM management with pylua_bioxen_vm_lib v0.1.6.
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
    from pylua_bioxen_vm_lib import VMManager, InteractiveSession
    from pylua_bioxen_vm_lib.exceptions import (
        InteractiveSessionError, AttachError, DetachError, 
        SessionNotFoundError, SessionAlreadyExistsError, 
        VMManagerError, LuaVMError
    )
    from pylua_bioxen_vm_lib.utils.curator import (
        get_curator, bootstrap_lua_environment, Package,
        PackageRegistry, PackageInstaller, search_packages
    )
    from pylua_bioxen_vm_lib.env import EnvironmentManager
    from pylua_bioxen_vm_lib.package_manager import PackageManager, RepositoryManager
    MODERN_VM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Modern VM library not available: {e}")
    print("💡 Install with: pip install pylua-bioxen-vm-lib")
    MODERN_VM_AVAILABLE = False

try:
    from genome.parser import BioXenRealGenomeIntegrator
    from genome.schema import BioXenGenomeValidator
    from hypervisor.core import BioXenHypervisor, ResourceAllocation, VMState
    from chassis import ChassisType
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the BioXen root directory")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('bioxen.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class InteractiveBioXen:
    """Interactive CLI for BioXen hypervisor and Lua VM management."""
    def __init__(self):
        self.validator = BioXenGenomeValidator()
        self.hypervisor = None
        self.available_genomes = []
        self.chassis_type = ChassisType.ECOLI
        self.visualization_active = False
        if MODERN_VM_AVAILABLE:
            self.vm_manager = VMManager(debug_mode=False)
            self.curator = get_curator()
            self.env_manager = EnvironmentManager()
            self.package_manager = PackageManager()
            self.package_registry = PackageRegistry()
            self.package_installer = PackageInstaller()
            self.repository_manager = RepositoryManager()
            logger.info("BioXen initialized with package management")
        else:
            logger.warning("BioXen initialized without modern VM support")

    def _check_hypervisor(self):
        """Check if hypervisor is initialized."""
        if self.hypervisor is None:
            print("❌ Hypervisor not initialized. Select 'Initialize Hypervisor'.")
            return False
        return True

    def _suggest_unique_vm_id(self, base_name: str) -> str:
        """Suggest a unique VM ID."""
        if not self.hypervisor or not self.hypervisor.vms:
            return f"vm_{base_name}"
        existing_ids = set(self.hypervisor.vms.keys())
        candidate = f"vm_{base_name}"
        if candidate not in existing_ids:
            return candidate
        for i in range(1, 100):
            candidate = f"vm_{base_name}_{i}"
            if candidate not in existing_ids:
                return candidate
        return f"vm_{base_name}_{int(time.time() % 10000)}"

    def main_menu(self):
        """Display main menu."""
        while True:
            print("\n" + "="*60 + "\n🧬 BioXen Hypervisor\n" + "="*60)
            choices = [
                Choice("🔍 Browse Genomes", "browse_genomes"),
                Choice("🧬 Load Genome", "validate"),
                Choice("🖥️ Initialize Hypervisor", "init_hypervisor"),
                Choice("🌐 Download Genomes", "download_new"),
                Choice("⚡ Create VM", "create_vm"),
                Choice("📊 Manage VMs", "status"),
                Choice("📺 Terminal Visualization", "terminal_vis"),
                Choice("🗑️ Destroy VM", "destroy_vm"),
            ]
            if MODERN_VM_AVAILABLE:
                choices.extend([
                    Choice("🌙 Lua VM (One-shot)", "create_lua_vm"),
                    Choice("🖥️ Persistent Lua VM", "create_persistent_vm"),
                    Choice("🔗 Attach Lua VM", "attach_lua_vm"),
                    Choice("📦 Package Management", "package_management_menu"),
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

    def package_management_menu(self):
        """Package management menu."""
        while True:
            choices = [
                Choice("🔍 Search Packages", "search_lua_packages"),
                Choice("📋 List Installed", "list_installed_packages"),
                Choice("⬇️ Install Package", "install_lua_package"),
                Choice("⬆️ Update Package", "update_lua_package"),
                Choice("🗑️ Remove Package", "remove_lua_package"),
                Choice("📊 Package Info", "package_info"),
                Choice("🔄 Update All", "update_all_packages"),
                Choice("🏗️ Bootstrap Environment", "bootstrap_lua_environment"),
                Choice("🔧 Manage Environments", "manage_lua_environments"),
                Choice("⚙️ Settings", "package_settings"),
                Choice("🔙 Back", "back")
            ]
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
            self.hypervisor.create_vm(vm_id, genome_path, ResourceAllocation(memory_kb=int(mem or min_memory_kb), boot_time_ms=int(boot or boot_time_ms)))
            print(f"✅ VM '{vm_id}' created: {genome_name}, {self.hypervisor.get_vm_state(vm_id).value}")
        except Exception as e:
            logger.error(f"VM error: {e}")
            print(f"❌ Error: {e}")
        questionary.press_any_key_to_continue().ask()

    def show_status(self):
        """Display hypervisor/VM status."""
        if not self._check_hypervisor():
            return
        print("\n📊 Hypervisor Status\n" + "="*60)
        print(f"Chassis: {self.hypervisor.chassis_type.value}\nActive VMs: {len(self.hypervisor.vms)}")
        if not self.hypervisor.vms:
            print("No VMs running\n💡 Use 'Create VM'")
        else:
            for vm_id, vm in self.hypervisor.vms.items():
                state = self.hypervisor.get_vm_state(vm_id)
                print(f"   • {vm_id}: {state.value}, {vm.genome_name}")
                if state == VMState.RUNNING:
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