#!/usr/bin/env python3
"""
BioXen Working Client - Focused on Genome Operations

This client focuses on the proven working functionality:
- Real NCBI genome downloads via download_genomes.py
- JCVI integration for genomics workflows
- VM management via pylua_bioxen_vm_lib

Built using the working components from the complete BioXen system,
without the complex factory pattern that requires hypervisor components.
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

try:
    import questionary
    from questionary import Choice
    QUESTIONARY_AVAILABLE = True
except ImportError:
    print("⚠️  questionary not available - install with: pip install questionary==2.1.0")
    QUESTIONARY_AVAILABLE = False

# Import working genome downloader
try:
    from download_genomes import (
        download_genome, download_and_convert_genome, 
        MINIMAL_GENOMES, list_available_genomes,
        interactive_genome_selection
    )
    GENOME_DOWNLOADER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Genome downloader not available: {e}")
    GENOME_DOWNLOADER_AVAILABLE = False

# Import JCVI integration
try:
    from bioxen_jcvi_integration import BioXenJCVIIntegration
    from bioxen_to_jcvi_converter import BioXenToJCVIConverter
    JCVI_INTEGRATION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  JCVI integration not available: {e}")
    JCVI_INTEGRATION_AVAILABLE = False

# Import library VM manager
try:
    from pylua_bioxen_vm_lib import VMManager, InteractiveSession
    from pylua_bioxen_vm_lib.factory import create_vm
    LIBRARY_VM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  VM library not available: {e}")
    LIBRARY_VM_AVAILABLE = False


class BioXenWorkingClient:
    """BioXen client focused on proven working functionality."""
    
    def __init__(self):
        """Initialize the working client."""
        self.vm_manager = None
        self.jcvi_integration = None
        self.converter = None
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize available components."""
        print("🧬 BioXen Working Client")
        print("=" * 50)
        
        # Initialize VM Manager
        if LIBRARY_VM_AVAILABLE:
            try:
                self.vm_manager = VMManager()
                print("✅ VM Manager initialized")
            except Exception as e:
                print(f"⚠️  VM Manager initialization failed: {e}")
        
        # Initialize JCVI Integration
        if JCVI_INTEGRATION_AVAILABLE:
            try:
                self.jcvi_integration = BioXenJCVIIntegration()
                print("✅ JCVI Integration initialized")
            except Exception as e:
                print(f"⚠️  JCVI Integration initialization failed: {e}")
        
        # Initialize converter
        if JCVI_INTEGRATION_AVAILABLE:
            try:
                self.converter = BioXenToJCVIConverter()
                print("✅ Format Converter initialized")
            except Exception as e:
                print(f"⚠️  Format Converter initialization failed: {e}")
    
    def run_interactive_menu(self):
        """Run the main interactive menu."""
        if not QUESTIONARY_AVAILABLE:
            print("❌ Interactive menu requires questionary")
            return self._run_text_menu()
        
        while True:
            print("\n🧬 BioXen Working Client")
            print("=" * 50)
            
            choices = [
                Choice("📥 Genome Management", "genomes"),
                Choice("🏭 Create VM (Library Factory)", "create_vm"),
                Choice("🖥️  VM Management", "vms"),
                Choice("🧪 JCVI Workflows", "jcvi"),
                Choice("🔄 Format Conversion", "convert"),
                Choice("🚀 Launch Main BioXen", "launcher"),
                Choice("📊 System Status", "status"),
                Choice("❌ Exit", "exit")
            ]
            
            action = questionary.select("Select an option:", choices=choices).ask()
            
            if action == "genomes":
                self._genome_management_menu()
            elif action == "create_vm":
                self._create_vm_menu()
            elif action == "vms":
                self._vm_management_menu()
            elif action == "jcvi":
                self._jcvi_workflows_menu()
            elif action == "convert":
                self._conversion_menu()
            elif action == "launcher":
                self._launch_main_bioxen()
            elif action == "status":
                self._show_system_status()
            elif action == "exit" or action is None:
                print("\n👋 Goodbye!")
                break
    
    def _genome_management_menu(self):
        """Handle genome management operations."""
        if not GENOME_DOWNLOADER_AVAILABLE:
            print("❌ Genome downloader not available")
            questionary.press_any_key_to_continue().ask()
            return
        
        choices = [
            Choice("📋 List Available Genomes", "list"),
            Choice("📥 Download Single Genome", "download"),
            Choice("🌐 Download Multiple Genomes", "multi"),
            Choice("🎯 Interactive Selection", "interactive"),
            Choice("🔙 Back", "back")
        ]
        
        action = questionary.select("Genome Management:", choices=choices).ask()
        
        if action == "list":
            self._list_genomes()
        elif action == "download":
            self._download_single_genome()
        elif action == "multi":
            self._download_multiple_genomes()
        elif action == "interactive":
            self._interactive_genome_selection()
        elif action == "back":
            return
    
    def _create_vm_menu(self):
        """Handle VM creation using library factory."""
        if not LIBRARY_VM_AVAILABLE:
            print("❌ VM library not available")
            questionary.press_any_key_to_continue().ask()
            return
        
        print("\n🏭 Create Biological VM")
        print("=" * 40)
        
        # Get VM ID
        vm_id = questionary.text("Enter VM ID:", default="bio_vm_001").ask()
        if not vm_id:
            return
        
        # Select genome template
        genome_choices = [
            Choice("🦠 syn3a (Synthetic Minimal Cell)", "syn3a"),
            Choice("🧫 ecoli (E. coli)", "ecoli"),
            Choice("⚗️  minimal_cell (Minimal Cell)", "minimal_cell"),
            Choice("🧬 custom (Custom Genome)", "custom")
        ]
        
        genome_template = questionary.select("Select genome template:", choices=genome_choices).ask()
        if not genome_template:
            return
        
        try:
            print(f"\n🔄 Creating VM '{vm_id}' with genome '{genome_template}'...")
            
            # Use library factory to create VM
            vm = create_vm(vm_id, genome_template)
            
            print(f"✅ Successfully created VM: {vm_id}")
            print(f"   Genome Template: {genome_template}")
            print(f"   VM ID: {vm.vm_id}")
            
            # Ask if user wants to start the VM
            if questionary.confirm("Start the VM now?").ask():
                vm.start()
                print(f"▶️  VM {vm_id} started")
            
        except Exception as e:
            print(f"❌ Failed to create VM: {e}")
        
        questionary.press_any_key_to_continue().ask()
    
    def _vm_management_menu(self):
        """Handle VM management operations."""
        if not self.vm_manager:
            print("❌ VM Manager not available")
            questionary.press_any_key_to_continue().ask()
            return
        
        choices = [
            Choice("📋 List VMs", "list"),
            Choice("▶️  Start VM", "start"),
            Choice("⏹️  Stop VM", "stop"),
            Choice("🗑️  Delete VM", "delete"),
            Choice("📊 VM Status", "status"),
            Choice("🔙 Back", "back")
        ]
        
        action = questionary.select("VM Management:", choices=choices).ask()
        
        if action == "list":
            self._list_vms()
        elif action == "start":
            self._start_vm()
        elif action == "stop":
            self._stop_vm()
        elif action == "delete":
            self._delete_vm()
        elif action == "status":
            self._vm_status()
        elif action == "back":
            return
    
    def _jcvi_workflows_menu(self):
        """Handle JCVI workflow operations."""
        if not self.jcvi_integration:
            print("❌ JCVI integration not available")
            questionary.press_any_key_to_continue().ask()
            return
        
        choices = [
            Choice("📊 Check JCVI Status", "status"),
            Choice("🔄 Convert Genome to JCVI Format", "convert"),
            Choice("🧪 Test JCVI Integration", "test"),
            Choice("🔙 Back", "back")
        ]
        
        action = questionary.select("JCVI Workflows:", choices=choices).ask()
        
        if action == "status":
            self._jcvi_status()
        elif action == "convert":
            self._jcvi_convert_genome()
        elif action == "test":
            self._jcvi_test()
        elif action == "back":
            return
    
    def _jcvi_convert_genome(self):
        """Convert a genome to JCVI format."""
        print("🔄 Genome to JCVI Format Conversion")
        print("This feature will convert BioXen .genome files to JCVI-compatible formats")
        questionary.press_any_key_to_continue().ask()
    
    def _jcvi_test(self):
        """Test JCVI integration."""
        print("🧪 Testing JCVI Integration")
        if self.jcvi_integration:
            print("✅ JCVI integration object created successfully")
            if hasattr(self.jcvi_integration, 'jcvi_available'):
                status = "available" if self.jcvi_integration.jcvi_available else "not available"
                print(f"   JCVI toolkit: {status}")
        else:
            print("❌ JCVI integration not available")
        questionary.press_any_key_to_continue().ask()
    
    def _conversion_menu(self):
        """Handle format conversion operations."""
        if not self.converter:
            print("❌ Format converter not available")
            questionary.press_any_key_to_continue().ask()
            return
        
        print("🔄 BioXen to JCVI Format Conversion")
        print("Available conversion capabilities:")
        print("- .genome to FASTA")
        print("- .genome to GFF3")
        print("- NCBI downloads to JCVI format")
        
        questionary.press_any_key_to_continue().ask()
    
    def _launch_main_bioxen(self):
        """Launch the main BioXen system."""
        print("\n🚀 Launching Main BioXen System...")
        import subprocess
        try:
            subprocess.run([sys.executable, "bioxen.py"])
        except Exception as e:
            print(f"❌ Failed to launch main BioXen: {e}")
    
    def _show_system_status(self):
        """Show system component status."""
        print("\n📊 System Status")
        print("=" * 40)
        
        components = [
            ("Questionary (Interactive UI)", QUESTIONARY_AVAILABLE),
            ("Genome Downloader", GENOME_DOWNLOADER_AVAILABLE),
            ("JCVI Integration", JCVI_INTEGRATION_AVAILABLE),
            ("VM Library", LIBRARY_VM_AVAILABLE),
        ]
        
        for name, available in components:
            status = "✅ Available" if available else "❌ Not Available"
            print(f"   {name}: {status}")
        
        # Show JCVI status
        if self.jcvi_integration:
            jcvi_available = self.jcvi_integration.jcvi_available
            jcvi_status = "✅ Available" if jcvi_available else "❌ Not Available"
            print(f"   JCVI Toolkit: {jcvi_status}")
        
        # Show genome counts
        if GENOME_DOWNLOADER_AVAILABLE:
            genome_count = len(MINIMAL_GENOMES)
            print(f"   Available Genomes: {genome_count}")
        
        questionary.press_any_key_to_continue().ask()
    
    def _list_genomes(self):
        """List available genomes."""
        print("\n📋 Available Minimal Genomes:")
        print("=" * 50)
        
        for key, info in MINIMAL_GENOMES.items():
            print(f"🧬 {key}")
            print(f"   Description: {info['description']}")
            print(f"   Tax ID: {info['taxid']}")
            print()
        
        questionary.press_any_key_to_continue().ask()
    
    def _download_single_genome(self):
        """Download a single genome."""
        genome_choices = [Choice(f"🧬 {key}: {info['description']}", key) 
                         for key, info in MINIMAL_GENOMES.items()]
        
        genome_key = questionary.select("Select genome:", choices=genome_choices).ask()
        if not genome_key:
            return
        
        output_dir = Path("genomes")
        output_dir.mkdir(exist_ok=True)
        
        print(f"\n📥 Downloading {genome_key}...")
        success = download_and_convert_genome(genome_key, output_dir)
        
        if success:
            print(f"✅ Successfully downloaded {genome_key}")
            print(f"📁 Available in: {output_dir}")
        else:
            print(f"❌ Failed to download {genome_key}")
        
        questionary.press_any_key_to_continue().ask()
    
    def _download_multiple_genomes(self):
        """Download multiple genomes."""
        genome_choices = [Choice(f"🧬 {key}: {info['description']}", key) 
                         for key, info in MINIMAL_GENOMES.items()]
        
        selected = questionary.checkbox("Select genomes to download:", choices=genome_choices).ask()
        if not selected:
            return
        
        output_dir = Path("genomes")
        output_dir.mkdir(exist_ok=True)
        
        success_count = 0
        for genome_key in selected:
            print(f"\n📥 Downloading {genome_key}...")
            if download_and_convert_genome(genome_key, output_dir):
                success_count += 1
                print(f"✅ {genome_key} completed")
            else:
                print(f"❌ {genome_key} failed")
        
        print(f"\n📊 Download Summary: {success_count}/{len(selected)} genomes successful")
        questionary.press_any_key_to_continue().ask()
    
    def _interactive_genome_selection(self):
        """Run interactive genome selection."""
        try:
            interactive_genome_selection()
        except Exception as e:
            print(f"❌ Interactive genome selection failed: {e}")
        
        questionary.press_any_key_to_continue().ask()
    
    def _list_vms(self):
        """List running VMs."""
        try:
            vms = self.vm_manager.list_vms()
            if vms:
                print(f"\n📋 Running VMs ({len(vms)}):")
                for vm_id in vms:
                    print(f"   🖥️  {vm_id}")
            else:
                print("\n📋 No running VMs")
        except Exception as e:
            print(f"❌ Failed to list VMs: {e}")
        
        questionary.press_any_key_to_continue().ask()
    
    def _jcvi_status(self):
        """Show JCVI integration status."""
        if self.jcvi_integration:
            status = "✅ Available" if self.jcvi_integration.jcvi_available else "❌ Not Available"
            print(f"\n🧪 JCVI Integration Status: {status}")
            
            if self.jcvi_integration.jcvi_available:
                print("   - JCVI toolkit is installed and functional")
                print("   - Format conversion available")
                print("   - Enhanced analysis workflows enabled")
            else:
                print("   - Running in fallback mode")
                print("   - Basic BioXen functionality available")
                print("   - Install JCVI for enhanced features")
        else:
            print("❌ JCVI integration not initialized")
        
        questionary.press_any_key_to_continue().ask()
    
    def _run_text_menu(self):
        """Run text-based menu fallback."""
        print("\n📋 Text Menu (questionary not available)")
        print("1. List genomes")
        print("2. Download genome")
        print("3. List VMs")
        print("4. System status")
        print("5. Exit")
        
        choice = input("\nChoice (1-5): ").strip()
        
        if choice == "1":
            self._list_genomes()
        elif choice == "2":
            print("Use: python3 download_genomes.py [genome_key]")
        elif choice == "3":
            self._list_vms()
        elif choice == "4":
            self._show_system_status()
        elif choice == "5":
            print("👋 Goodbye!")
            return
        else:
            print("❌ Invalid choice")


def main():
    """Main entry point."""
    client = BioXenWorkingClient()
    
    if QUESTIONARY_AVAILABLE:
        client.run_interactive_menu()
    else:
        client._run_text_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
