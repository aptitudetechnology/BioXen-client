import time
from typing import Optional, Dict, Any

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


class XCPngVMOperations:
    """Handles XCP-ng VM operations like creation and attachment."""
    
    def __init__(self, vm_manager, vm_tracker: VMStatusTracker):
        self.vm_manager = vm_manager
        self.vm_tracker = vm_tracker

    def create_vm(self, vm_id, profile_name, config, networked=False, persistent=True, debug_mode=False):
        """Create XCP-ng VM using 0.1.22 (Phase 3) implementation"""
        try:
            print(f"🔄 Creating XCP-ng VM '{vm_id}' with profile '{profile_name}'...")
            host_display = config.get('xapi_url', config.get('xcp_host', 'Unknown'))
            print(f"🌐 Connecting to XCP-ng host: {host_display}")
            
            # 0.1.22 uses the config directly - no conversion needed
            # The library expects: xapi_url, username, password, template_name, etc.
            
            # Use 0.1.22 create_vm factory function with XCP-ng type
            vm_instance = create_vm(
                vm_id=vm_id, 
                vm_type="xcpng", 
                networked=networked, 
                persistent=persistent, 
                debug_mode=debug_mode,
                config=config
            )
            
            # Start the VM (this now works in 0.1.22!)
            print("🚀 Starting VM and establishing SSH connection...")
            vm_instance.start()
            
            # Track VM status with XCP-ng config
            status = self.vm_tracker.add_vm(vm_id, profile_name, "xcpng")
            status.xcpng_config = config
            status.running = True
            
            print(f"✅ XCP-ng VM '{vm_id}' created successfully!")
            template_name = config.get('template_name', 'unknown')
            print(f"🔧 Host: {host_display}, Template: {template_name}")
            print(f"🌐 SSH session established to VM")
            print("💡 Use 'Attach to existing VM' to interact with this VM")
            
            # Offer to attach immediately
            attach_now = questionary.confirm("Attach to VM now?", default=True).ask()
            if attach_now:
                status.attached = True
                print("Entering interactive XCP-ng VM session...")
                # Note: We'll need to import interactive_loop from basic_vm or create our own
                # For now, this is a placeholder that would need the interactive loop
                status.attached = False
            
        except Exception as e:
            print(f"❌ Failed to create XCP-ng VM: {e}")
            print("💡 Check XCP-ng host connectivity and credentials")
            host_display = config.get('xapi_url', config.get('xcp_host', 'Unknown'))
            template_name = config.get('template_name', 'unknown')
            username = config.get('username', config.get('xcp_username', 'unknown'))
            print(f"🔧 Host: {host_display}, Template: {template_name}")
            print(f"👤 Username: {username}")
            self.vm_tracker.remove_vm(vm_id)

    def collect_config(self):
        """Collect Xen VM configuration from user"""
        print("🔧 Configuring Xen VM parameters...")
        
        # Memory configuration
        memory_choices = [
            Choice("512 MB", 512),
            Choice("1 GB", 1024), 
            Choice("2 GB", 2048),
            Choice("4 GB", 4096),
            Choice("Custom amount", "custom")
        ]
        
        memory = questionary.select(
            "Select memory allocation:",
            choices=memory_choices
        ).ask()
        
        if memory == "custom":
            memory = questionary.text(
                "Enter memory in MB:",
                validate=lambda x: x.isdigit() and int(x) > 0 or "Must be positive number"
            ).ask()
            if not memory:
                return None
            memory = int(memory)
        
        # vCPU configuration
        vcpu_choices = [
            Choice("1 vCPU", 1),
            Choice("2 vCPUs", 2),
            Choice("4 vCPUs", 4),
            Choice("Custom count", "custom")
        ]
        
        vcpus = questionary.select(
            "Select vCPU count:",
            choices=vcpu_choices
        ).ask()
        
        if vcpus == "custom":
            vcpus = questionary.text(
                "Enter vCPU count:",
                validate=lambda x: x.isdigit() and int(x) > 0 or "Must be positive number"
            ).ask()
            if not vcpus:
                return None
            vcpus = int(vcpus)
        
        # Disk configuration
        disk_choices = [
            Choice("8 GB", 8),
            Choice("16 GB", 16),
            Choice("32 GB", 32),
            Choice("64 GB", 64),
            Choice("Custom size", "custom")
        ]
        
        disk_size = questionary.select(
            "Select disk size:",
            choices=disk_choices
        ).ask()
        
        if disk_size == "custom":
            disk_size = questionary.text(
                "Enter disk size in GB:",
                validate=lambda x: x.isdigit() and int(x) > 0 or "Must be positive number"
            ).ask()
            if not disk_size:
                return None
            disk_size = int(disk_size)
        
        # OS Template
        os_choices = [
            Choice("Alpine Linux", "alpine"),
            Choice("Custom ISO", "custom")
        ]
        
        os_template = questionary.select(
            "Select OS template:",
            choices=os_choices
        ).ask()
        
        if os_template == "custom":
            iso_path = questionary.text(
                "Enter path to custom ISO:"
            ).ask()
            if not iso_path:
                return None
            os_template = f"custom:{iso_path}"
        
        # Network configuration
        network_type = questionary.select(
            "Select network configuration:",
            choices=[
                Choice("NAT (default)", "nat"),
                Choice("Bridged", "bridge"),
                Choice("Host-only", "hostonly"),
                Choice("No network", "none")
            ]
        ).ask()
        
        # Advanced options
        advanced = questionary.confirm("Configure advanced options?").ask()
        
        xen_config = {
            'memory': memory,
            'vcpus': vcpus,
            'disk_size': disk_size,
            'os_template': os_template,
            'network_type': network_type
        }
        
        if advanced:
            # Boot options
            boot_order = questionary.select(
                "Boot order:",
                choices=[
                    Choice("CD-ROM first (virtual CD-ROM, ISO file installation)", "cd")
                ]
            ).ask()
            xen_config['boot_order'] = boot_order
            
        return xen_config

    def attach_to_vm(self, vm_id):
        """Attach to Xen-based VM (placeholder)"""
        status = self.vm_tracker.get_vm(vm_id)
        if not status:
            print(f"❌ VM '{vm_id}' not found")
            return
            
        print(f"🌐 Attaching to Xen VM '{vm_id}'...")
        print("⚠️  Xen VM attachment is a placeholder - actual implementation pending")
        
        # Show Xen VM info
        xen_config = status.xcpng_config
        print(f"🔧 VM Configuration:")
        print(f"  Memory: {xen_config.get('memory', 'unknown')} MB")
        print(f"  vCPUs: {xen_config.get('vcpus', 'unknown')}")
        print(f"  Network: {xen_config.get('network_type', 'unknown')}")
        
        # Placeholder console options
        console_choice = questionary.select(
            "Select connection method:",
            choices=[
                Choice("🖥️  Console (xl console)", "console"),
                Choice("📺 VNC Viewer", "vnc"),
                Choice("🌐 SSH Connection", "ssh"),
                Choice("← Back", "back")
            ]
        ).ask()
        
        if console_choice == "back":
            return
            
        print(f"⚠️  {console_choice.upper()} connection placeholder")
        print("Actual Xen VM interaction to be implemented")
        
        questionary.press_any_key_to_continue().ask()