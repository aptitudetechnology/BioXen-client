import sys
import time
from typing import Optional

try:
    import questionary
    from questionary import Choice
except ImportError:
    print("❌ questionary not installed. Install with: pip install questionary")
    raise

from ..vm.basic_vm import BasicVMOperations
from ..vm.xcpng_vm import XCPngVMOperations
from ..vm.converter import VMConverter
from ..packages.installer import PackageInstaller
from ..utils.cleanup import cleanup_handler


class MainMenu:
    """Main menu and UI controller."""
    
    def __init__(self, vm_manager, config_manager, vm_tracker, package_installer, 
                 basic_vm_ops, xcpng_vm_ops, vm_converter, curator, env_manager):
        self.vm_manager = vm_manager
        self.config_manager = config_manager
        self.vm_tracker = vm_tracker
        self.package_installer = package_installer
        self.basic_vm_ops = basic_vm_ops
        self.xcpng_vm_ops = xcpng_vm_ops
        self.vm_converter = vm_converter
        self.curator = curator
        self.env_manager = env_manager

    def run(self):
        """Main menu loop"""
        print("\n[INFO] BioXen Interactive CLI started. If you do not see the menu below, check your terminal and Python environment.")
        while True:
            action = questionary.select(
                "⚡ ModularNucleoid CLI v0.1.22 - VM Control",
                choices=[
                    Choice("🚀 Create new Lua VM", "create_vm"),
                    Choice("🔗 Attach to existing VM", "attach_vm"),
                    Choice("📦 Install Packages", "install_packages"),
                    Choice("👤 Manage Profiles", "setup_profile"),
                    Choice("⚙️  Configuration Settings", "config_settings"),
                    Choice("🔧 Convert VM to Physical", "convert_vm"),
                    Choice("🖥️  Environment Status", "env_status"),
                    Choice("📋 List VMs", "list_vms"),
                    Choice("🛑 Stop VM", "stop_vm"),
                    Choice("❌ Exit", "exit")
                ]
            ).ask()

            if action == "create_vm":
                self.create_lua_vm()
            elif action == "attach_vm":
                self.attach_to_vm_terminal()
            elif action == "install_packages":
                self.package_installer.install_packages()
            elif action == "setup_profile":
                self.setup_profile()
            elif action == "config_settings":
                self.manage_configuration()
            elif action == "convert_vm":
                self.vm_converter.convert_vm_to_physical()
            elif action == "env_status":
                self.show_environment_status()
            elif action == "list_vms":
                self.list_vms()
            elif action == "stop_vm":
                self.stop_vm()
            elif action == "exit":
                cleanup_handler(self.vm_manager, self.vm_tracker)
                sys.exit(0)

    def create_lua_vm(self):
        """Create a new Lua VM"""
        # Step 1: Choose VM type using 0.1.20 multi-VM factory pattern
        vm_type = questionary.select(
            "Select VM type:",
            choices=[
                Choice("🐍 Basic VM (subprocess-based, local)", "basic"),
                Choice("🌐 XCP-ng VM (hypervisor, full integration)", "xcpng"),
                Choice("← Back to Menu", "back")
            ]
        ).ask()
        
        if not vm_type or vm_type == "back":
            return

        # Get VM ID
        vm_id = questionary.text("Enter VM identifier:").ask()
        if not vm_id:
            return

        # Get profile
        profile = questionary.text("Enter profile name:", default="default").ask()
        if not profile:
            profile = "default"

        # Create VM based on type
        if vm_type == "basic":
            self.basic_vm_ops.create_vm(vm_id, profile)
        elif vm_type == "xcpng":
            # Get XCP-ng configuration first
            config = self._get_xcpng_config()
            if config:
                self.xcpng_vm_ops.create_vm(vm_id, profile, config)

    def attach_to_vm_terminal(self):
        """Attach to an existing VM"""
        if not self.vm_tracker.vm_status:
            print("❌ No running VMs available")
            return

        # Select VM
        vm_choices = [
            Choice(f"{vm_id} ({status.vm_type.title()}, {status.profile})", vm_id)
            for vm_id, status in self.vm_tracker.vm_status.items()
            if status.running
        ]
        vm_choices.append(Choice("← Back to Menu", "back"))

        vm_id = questionary.select("Select VM to attach to:", choices=vm_choices).ask()
        if not vm_id or vm_id == "back":
            return

        # Attach based on VM type
        status = self.vm_tracker.get_vm(vm_id)
        if status.vm_type == "basic":
            self.basic_vm_ops.attach_to_vm(vm_id)
        elif status.vm_type == "xcpng":
            self.xcpng_vm_ops.attach_to_vm(vm_id)

    def setup_profile(self):
        """Profile management placeholder"""
        print("⚠️  Profile management placeholder")
        questionary.press_any_key_to_continue().ask()

    def manage_configuration(self):
        """Configuration management placeholder"""
        print("⚠️  Configuration management placeholder")
        questionary.press_any_key_to_continue().ask()

    def show_environment_status(self):
        """Show environment status"""
        print("\n🖥️  Environment Status:")
        
        # VM status
        if not self.vm_tracker.vm_status:
            print("  📭 No VMs created yet")
        else:
            running_vms = self.vm_tracker.get_running_vms()
            print(f"  🏃 {len(running_vms)} VMs running")
            for vm_id in running_vms:
                status = self.vm_tracker.get_vm(vm_id)
                print(f"    • {vm_id} ({status.vm_type}, {status.profile})")

        questionary.press_any_key_to_continue().ask()

    def list_vms(self):
        """List all VMs"""
        if not self.vm_tracker.vm_status:
            print("❌ No VMs available")
        else:
            print("\n📋 VM List:")
            for vm_id, status in self.vm_tracker.vm_status.items():
                state = "Running" if status.running else "Stopped"
                attached = " (Attached)" if status.attached else ""
                print(f"  • {vm_id}: {status.vm_type.title()}, {status.profile}, {state}{attached}")

        questionary.press_any_key_to_continue().ask()

    def stop_vm(self):
        """Stop a VM"""
        running_vms = self.vm_tracker.get_running_vms()
        if not running_vms:
            print("❌ No running VMs")
            return

        # Select VM to stop
        vm_choices = [Choice(vm_id, vm_id) for vm_id in running_vms]
        vm_choices.append(Choice("← Back to Menu", "back"))

        vm_id = questionary.select("Select VM to stop:", choices=vm_choices).ask()
        if not vm_id or vm_id == "back":
            return

        try:
            self.vm_manager.terminate_vm_session(vm_id)
            status = self.vm_tracker.get_vm(vm_id)
            status.running = False
            status.attached = False
            print(f"✅ VM '{vm_id}' stopped")
        except Exception as e:
            print(f"❌ Failed to stop VM '{vm_id}': {e}")

        questionary.press_any_key_to_continue().ask()

    def _get_xcpng_config(self):
        """Get XCP-ng configuration (placeholder)"""
        print("⚠️  XCP-ng configuration placeholder")
        return None