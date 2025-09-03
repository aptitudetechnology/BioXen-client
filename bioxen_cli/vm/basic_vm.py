import time
from typing import Optional

try:
    import questionary
    from questionary import Choice
except ImportError:
    print("❌ questionary not installed. Install with: pip install questionary")
    raise

try:
    from pylua_bioxen_vm_lib import create_vm
except ImportError:
    print("❌ pylua_bioxen_vm_lib not installed")
    raise

from .status import VMStatus, VMStatusTracker


class BasicVMOperations:
    """Handles basic VM operations like creation and attachment."""
    
    def __init__(self, vm_manager, vm_tracker: VMStatusTracker):
        self.vm_manager = vm_manager
        self.vm_tracker = vm_tracker

    def create_vm(self, vm_id, profile_name, networked=False, persistent=True, debug_mode=False):
        """Create basic VM using 0.1.19 factory pattern"""
        try:
            print(f"🔄 Creating Basic VM '{vm_id}' with profile '{profile_name}'...")
            
            # Use 0.1.19 create_vm factory function
            vm_instance = create_vm(
                vm_id=vm_id, 
                vm_type="basic", 
                networked=networked, 
                persistent=persistent, 
                debug_mode=debug_mode
            )
            
            # Create interactive session
            session = self.vm_manager.create_interactive_vm(vm_id)
            
            # Track VM status
            status = self.vm_tracker.add_vm(vm_id, profile_name, "basic")
            status.running = True

            print(f"✅ Basic VM '{vm_id}' created with profile '{profile_name}'")
            print("💡 Use 'Attach to existing VM' to interact with this VM")
            print("-" * 70)

            # Mark as attached and enter interactive mode if requested
            attach_now = questionary.confirm("Attach to VM now?", default=True).ask()
            if attach_now:
                status.attached = True
                
                # Send welcome message
                welcome_msg = f"""
-- Basic VM '{vm_id}' started with {profile_name} profile
print('🌙 VM ready! Type Lua commands or exit to return to menu')
"""
                self.vm_manager.send_input(vm_id, welcome_msg)
                time.sleep(0.2)
                
                print("Entering interactive session...")
                self.interactive_loop(vm_id)
                
                status.attached = False

        except Exception as e:
            print(f"❌ Failed to create basic VM: {e}")
            self.vm_tracker.remove_vm(vm_id)

    def attach_to_vm(self, vm_id):
        """Attach to subprocess-based VM"""
        try:
            status = self.vm_tracker.get_vm(vm_id)
            if not status:
                print(f"❌ VM '{vm_id}' not found")
                return
                
            print(f"🔗 Attaching to Subprocess VM '{vm_id}' (Profile: {status.profile})")
            print("💡 Press Ctrl+D or type 'exit' to detach and return to menu")
            print("💡 The VM will continue running after detachment")
            print("-" * 70)

            status.attached = True
            
            # Attach to existing session
            session = self.vm_manager.attach_to_vm(vm_id)
            
            self.interactive_loop(vm_id)
            
            status.attached = False
            print(f"✅ Detached from VM '{vm_id}' - VM continues running")

        except Exception as e:
            print(f"❌ Failed to attach to VM: {e}")
            status = self.vm_tracker.get_vm(vm_id)
            if status:
                status.attached = False

    def interactive_loop(self, vm_id):
        """Interactive loop for VM session"""
        try:
            while True:
                try:
                    user_input = input(f"lua[{vm_id}]> ")
                    
                    if user_input.strip() in ['exit', 'quit']:
                        break
                    
                    if user_input.strip():
                        self.vm_manager.send_input(vm_id, user_input + "\n")
                        time.sleep(0.1)
                        
                        # Read and display output
                        output = self.vm_manager.read_output(vm_id)
                        if output:
                            print(output.strip())
                            
                except KeyboardInterrupt:
                    print("\nUse 'exit' to detach from VM")
                except EOFError:
                    break
                    
        except Exception as e:
            print(f"Error in interactive loop: {e}")