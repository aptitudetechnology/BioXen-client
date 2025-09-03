import time
from typing import List, Optional, Dict, Any

try:
    import questionary
    from questionary import Choice
except ImportError:
    print("❌ questionary not installed. Install with: pip install questionary")
    raise

try:
    from pylua_bioxen_vm_lib.utils.curator import quick_install
except ImportError:
    print("❌ pylua_bioxen_vm_lib not installed")
    raise


class PackageInstaller:
    """Handles package installation to VMs and globally."""
    
    def __init__(self, vm_manager, vm_tracker, curator):
        self.vm_manager = vm_manager
        self.vm_tracker = vm_tracker
        self.curator = curator

    def install_packages(self):
        """Enhanced package installation with VM targeting"""
        # First, check available targets
        running_vms = {vm_id: status for vm_id, status in self.vm_tracker.vm_status.items() 
                       if status.running}
        # Build target selection
        target_choices = []
        if running_vms:
            target_choices.extend([
                Choice(f"VM: {vm_id} ({status.vm_type.title()}, {status.profile} profile)", f"vm:{vm_id}")
                for vm_id, status in running_vms.items()
            ])
        target_choices.append(Choice("Global system installation", "global"))
        target_choices.append(Choice("← Back to Menu", "back"))
        # Select installation target
        target = questionary.select(
            "Where would you like to install packages?",
            choices=target_choices
        ).ask()
        if not target or target == "back":
            return
        # Parse target selection
        is_vm_install = target.startswith("vm:")
        target_vm_id = target.split(":", 1)[1] if is_vm_install else None
        
        # Check if target is Xen VM
        if is_vm_install and self.vm_tracker.vm_status[target_vm_id].vm_type == "xen":
            print("⚠️  Package installation to Xen VMs is a placeholder")
            print("Actual Xen VM package management to be implemented")
            questionary.press_any_key_to_continue().ask()
            return
        
        # Select installation type
        install_choice = questionary.select(
            f"How would you like to install packages {'to ' + target_vm_id if is_vm_install else 'globally'}?",
            choices=[
                Choice("Install specific package by name", "specific"),
                Choice("Install recommended packages", "recommended"), 
                Choice("Show available packages", "show_available"),
                Choice("← Back", "back_to_target")
            ],
            default="specific"
        ).ask()
        if not install_choice or install_choice in ["back_to_target", "back"]:
            if install_choice == "back_to_target":
                self.install_packages()  # Restart from target selection
            return

        try:
            if install_choice == "specific":
                package = questionary.text("Enter package name to install:").ask()
                if package:
                    self.install_single_package(package, is_vm_install, target_vm_id)
            elif install_choice == "recommended":
                recommended = ["luasocket", "luafilesystem", "lua-cjson"]
                confirm = questionary.confirm(
                    f"Install recommended packages: {', '.join(recommended)}?"
                ).ask()
                if confirm:
                    self.install_multiple_packages(recommended, is_vm_install, target_vm_id)
            elif install_choice == "show_available":
                self.show_package_status(is_vm_install, target_vm_id)
        except Exception as e:
            print(f"Package operation failed: {e}")
        questionary.press_any_key_to_continue().ask()

    def install_single_package(self, package_name, is_vm_install, target_vm_id):
        """Install a single package to VM or global using 0.1.19 quick_install"""
        if is_vm_install:
            print(f"Installing {package_name} to VM '{target_vm_id}'...")
            success = self.install_package_to_vm(package_name, target_vm_id)
            if success:
                print(f"Successfully installed {package_name} to VM '{target_vm_id}'")
                self.verify_package_in_vm(package_name, target_vm_id)
            else:
                print(f"Failed to install {package_name} to VM '{target_vm_id}'")
        else:
            print(f"Installing {package_name} globally using 0.1.19 quick_install...")
            try:
                success = quick_install(package_name)
                if success:
                    print(f"Successfully installed {package_name} globally")
                else:
                    print(f"Failed to install {package_name} globally")
            except Exception as e:
                print(f"Error installing {package_name}: {e}")

    def install_multiple_packages(self, packages, is_vm_install, target_vm_id):
        """Install multiple packages with progress tracking using 0.1.19 APIs"""
        success_count = 0
        target_desc = f"VM '{target_vm_id}'" if is_vm_install else "globally"
        for pkg in packages:
            print(f"Installing {pkg} {target_desc}...")
            if is_vm_install:
                success = self.install_package_to_vm(pkg, target_vm_id)
            else:
                try:
                    success = quick_install(pkg)
                except Exception as e:
                    print(f"Error installing {pkg}: {e}")
                    success = False
            if success:
                print(f"{pkg} installed")
                success_count += 1
                if is_vm_install:
                    self.verify_package_in_vm(pkg, target_vm_id)
            else:
                print(f"{pkg} failed")
        print(f"Installation complete: {success_count}/{len(packages)} successful")

    def install_package_to_vm(self, package_name, vm_id):
        """Install package directly to a specific VM"""
        try:
            # Send LuaRocks install command to VM
            install_cmd = f'os.execute("luarocks install {package_name}")\n'
            self.vm_manager.send_input(vm_id, install_cmd)
            # Wait for command to complete
            time.sleep(2.0)
            # Read output to check for success
            output = self.vm_manager.read_output(vm_id)
            # Parse output for success indicators
            if output:
                output_lower = output.lower()
                if "successfully installed" in output_lower or "is now installed" in output_lower:
                    return True
                elif "error" in output_lower or "failed" in output_lower:
                    print(f"LuaRocks error: {output.strip()}")
                    return False
            # If no clear indication, assume success (LuaRocks can be quiet on success)
            return True
        except Exception as e:
            print(f"Error installing {package_name} to VM {vm_id}: {e}")
            return False

    def verify_package_in_vm(self, package_name, vm_id):
        """Verify package can be loaded in VM"""
        try:
            # Try to require the package
            verify_cmd = f'local ok, result = pcall(require, "{package_name}"); print("VERIFY:", ok and "SUCCESS" or "FAILED")\n'
            self.vm_manager.send_input(vm_id, verify_cmd)
            time.sleep(0.5)
            output = self.vm_manager.read_output(vm_id)
            if output and "VERIFY: SUCCESS" in output:
                print(f"Verification: {package_name} loads successfully in VM '{vm_id}'")
            elif output and "VERIFY: FAILED" in output:
                print(f"Warning: {package_name} installed but cannot be loaded in VM '{vm_id}'")
        except Exception as e:
            print(f"Could not verify {package_name} in VM {vm_id}: {e}")

    def show_package_status(self, is_vm_install, target_vm_id):
        """Show package status for VM or global using 0.1.19 APIs"""
        try:
            if is_vm_install:
                print(f"\nChecking packages in VM '{target_vm_id}'...")
                # Send command to list installed packages in VM
                list_cmd = 'os.execute("luarocks list")\n'
                self.vm_manager.send_input(target_vm_id, list_cmd)
                time.sleep(1.5)
                output = self.vm_manager.read_output(target_vm_id)
                if output:
                    print("Installed packages in VM:")
                    print(output.strip())
                else:
                    print("No package information available")
            else:
                # Show installed packages using curator
                try:
                    installed = self.curator.list_installed_packages()
                    print("\nCurrently Installed Packages (Global):")
                    if installed:
                        for pkg in installed:
                            print(f"  • {pkg.get('name', 'unknown')} v{pkg.get('version', 'unknown')}")
                    else:
                        print("  No packages installed globally")
                except Exception as e:
                    print(f"  Error listing installed packages: {e}")
                
                # Show health check
                try:
                    health = self.curator.health_check()
                    print(f"\nSystem Health:")
                    print(f"  Lua Version: {health.get('lua_version', 'unknown')}")
                    print(f"  LuaRocks: {'Available' if health.get('luarocks_available') else 'Unavailable'}")
                    print(f"  Total Packages: {health.get('installed_packages', 0)}")
                except Exception as e:
                    print(f"  Error checking system health: {e}")
        except Exception as e:
            print(f"Error showing packages: {e}")