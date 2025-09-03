from typing import Dict, Any

try:
    import questionary
    from questionary import Choice
except ImportError:
    print("❌ questionary not installed. Install with: pip install questionary")
    raise

from .status import VMStatusTracker


class VMConverter:
    """Handles VM to physical hardware conversion."""
    
    def __init__(self, vm_manager, vm_tracker: VMStatusTracker):
        self.vm_manager = vm_manager
        self.vm_tracker = vm_tracker

    def convert_vm_to_physical(self):
        """Convert a virtual Lua VM to physical hardware - UI only, calls library methods"""
        if not self.vm_tracker.vm_status:
            print("❌ No VMs available for conversion")
            return

        # Select VM to convert
        vm_choices = [
            Choice(f"{vm_id} ({status.vm_type.title()}, Profile: {status.profile}, Status: {'Running' if status.running else 'Stopped'})", vm_id)
            for vm_id, status in self.vm_tracker.vm_status.items()
        ]
        vm_choices.append(Choice("← Back to Menu", "back"))

        vm_id = questionary.select("Select VM to convert to physical hardware:", choices=vm_choices).ask()
        if not vm_id or vm_id == "back":
            return

        # Check if Xen VM
        vm_status = self.vm_tracker.get_vm(vm_id)
        if vm_status.vm_type == "xen":
            print("⚠️  Xen VM to physical conversion requires different approach")
            print("Xen VMs already run on physical hardware via hypervisor")
            questionary.press_any_key_to_continue().ask()
            return

        # Select target platform
        platform_choice = questionary.select(
            "Select target platform:",
            choices=[
                Choice("eLua (Embedded Lua)", "elua"),
                Choice("Lumorphix", "lumorphix"),
                Choice("← Back", "back")
            ]
        ).ask()

        if not platform_choice or platform_choice == "back":
            return

        if platform_choice == "elua":
            self.convert_to_elua(vm_id)
        elif platform_choice == "lumorphix":
            self.convert_to_lumorphix(vm_id)

    def convert_to_elua(self, vm_id):
        """Handle eLua conversion flow"""
        # Select target hardware
        hardware_choice = questionary.select(
            "Select eLua target hardware:",
            choices=[
                Choice("ESP32 (WiFi, Bluetooth)", "esp32"),
                Choice("ESP8266 (WiFi)", "esp8266"), 
                Choice("STM32F4 (ARM Cortex-M4)", "stm32f4"),
                Choice("STM32F1 (ARM Cortex-M3)", "stm32f1"),
                Choice("Custom target", "custom"),
                Choice("← Back", "back")
            ]
        ).ask()

        if not hardware_choice or hardware_choice == "back":
            return

        try:
            print(f"🔧 Converting VM '{vm_id}' to eLua for {hardware_choice.upper()}...")
            
            # These would be actual library calls once implemented:
            # converter = self.vm_manager.get_elua_converter()
            # result = converter.convert_vm_to_elua(vm_id, target=hardware_choice)
            
            # For now, just placeholder
            print(f"✅ eLua conversion initiated (placeholder)")
            print(f"📁 Would generate: elua_firmware_{vm_id}_{hardware_choice}.bin")
            print(f"🎯 Target: eLua on {hardware_choice.upper()}")
            print(f"⚠️  Note: Actual conversion logic to be implemented in pylua_bioxen_vm_lib")
            
        except Exception as e:
            print(f"❌ eLua conversion failed: {e}")

        questionary.press_any_key_to_continue().ask()

    def convert_to_lumorphix(self, vm_id):
        """Handle Lumorphix conversion flow"""
        # Select target hardware
        hardware_choice = questionary.select(
            "Select Lumorphix target hardware:",
            choices=[
                Choice("Tang Nano 9k FPGA", "tang_nano_9k"),
                Choice("ELM11", "elm11"),
                Choice("← Back", "back")
            ]
        ).ask()

        if not hardware_choice or hardware_choice == "back":
            return

        try:
            print(f"🔧 Converting VM '{vm_id}' to Lumorphix for {hardware_choice.replace('_', ' ').title()}...")
            
            # These would be actual library calls once implemented:
            # converter = self.vm_manager.get_lumorphix_converter()
            # result = converter.convert_vm_to_lumorphix(vm_id, target=hardware_choice)
            
            # For now, just placeholder
            print(f"✅ Lumorphix conversion initiated (placeholder)")
            
            if hardware_choice == "tang_nano_9k":
                print(f"📁 Would generate: lumorphix_bitstream_{vm_id}_tang_nano_9k.bit")
                print(f"🎯 Target: Lumorphix on Tang Nano 9k FPGA")
                print(f"🔌 FPGA Configuration: Bitstream ready for Tang Nano 9k")
            elif hardware_choice == "elm11":
                print(f"📁 Would generate: lumorphix_firmware_{vm_id}_elm11.bin")
                print(f"🎯 Target: Lumorphix on ELM11")
                print(f"💾 Firmware: Ready for ELM11 flash")
            
            print(f"⚠️  Note: Actual conversion logic to be implemented in pylua_bioxen_vm_lib")
            
        except Exception as e:
            print(f"❌ Lumorphix conversion failed: {e}")

        questionary.press_any_key_to_continue().ask()