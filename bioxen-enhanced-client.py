#!/usr/bin/env python3
"""
BioXen Enhanced Client with Working Components Integration

This client integrates the proven working BioXen components including:
- Real NCBI genome downloads via download_genomes.py
- Factory pattern API for biological VM creation  
- JCVI integration for advanced genomics workflows
- Hypervisor management via pylua_bioxen_vm_lib

Built by integrating working components from the complete BioXen system.
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# Add src to path for API imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

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

# Import factory API
try:
    from api.factory import create_bio_vm, create_biological_vm
    from api.jcvi_manager import JCVIManager
    FACTORY_API_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Factory API not available: {e}")
    FACTORY_API_AVAILABLE = False

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
    LIBRARY_VM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  VM library not available: {e}")
    LIBRARY_VM_AVAILABLE = False


class BioXenEnhancedClient:
    """Enhanced BioXen client integrating working components."""
    
    def __init__(self):
        """Initialize the enhanced client."""
        self.vm_manager = None
        self.jcvi_integration = None
        self.jcvi_manager = None
        self.converter = None
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize available components."""
        print("🧬 BioXen Enhanced Client")
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
        
        # Initialize JCVI Manager
        if FACTORY_API_AVAILABLE:
            try:
                config = {
                    'jcvi_cli_enabled': True,
                    'hardware_optimization': False,
                    'fallback_mode': True
                }
                self.jcvi_manager = JCVIManager(config)
                print("✅ JCVI Manager initialized")
            except Exception as e:
                print(f"⚠️  JCVI Manager initialization failed: {e}")
        
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
            print("\n🧬 BioXen Enhanced Client")
            print("=" * 50)
            
            choices = [
                Choice("📥 Genome Management", "genomes"),
                Choice("🏭 VM Factory (Create Biological VMs)", "factory"),
                Choice("🧪 JCVI Workflows", "jcvi"),
                Choice("🖥️  VM Management", "vms"),
                Choice("🔄 Format Conversion", "convert"),
                Choice("📊 System Status", "status"),
                Choice("❌ Exit", "exit")
            ]
            
            action = questionary.select("Select an option:", choices=choices).ask()
            
            if action == "genomes":
                self._genome_management_menu()
            elif action == "factory":
                self._factory_menu()
            elif action == "jcvi":
                self._jcvi_workflows_menu()
            elif action == "vms":
                self._vm_management_menu()
            elif action == "convert":
                self._conversion_menu()
            elif action == "status":
                self._show_system_status()
            elif action == "exit" or action is None:
                print("\n👋 Goodbye!")
                break
    
    def _genome_management_menu(self):
        """Handle genome management operations."""
        if not GENOME_DOWNLOADER_AVAILABLE:
            print("❌ Genome downloader not available")
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
    
    def _factory_menu(self):
        """Handle biological VM factory operations."""
        if not FACTORY_API_AVAILABLE:
            print("❌ Factory API not available")
            return
        
        print("\n🏭 Biological VM Factory")
        print("=" * 40)
        
        # Select biological type
        bio_choices = [
            Choice("🦠 syn3a (Synthetic Minimal Cell)", "syn3a"),
            Choice("🧫 ecoli (E. coli)", "ecoli"),
            Choice("⚗️  minimal_cell (Minimal Cell)", "minimal_cell")
        ]
        
        bio_type = questionary.select("Select biological type:", choices=bio_choices).ask()
        if not bio_type:
            return
        
        # Select VM type
        vm_choices = [
            Choice("🔧 basic (Basic VM)", "basic"),
            Choice("🏢 xcpng (Enterprise XCP-ng)", "xcpng"),
            Choice("⚡ jcvi_optimized (JCVI Optimized)", "jcvi_optimized")
        ]
        
        vm_type = questionary.select("Select VM type:", choices=vm_choices).ask()
        if not vm_type:
            return
        
        # Get VM ID
        vm_id = questionary.text("Enter VM ID:", default=f"{vm_type}_{bio_type}_001").ask()
        if not vm_id:
            return
        
        try:
            print(f"\n🔄 Creating {bio_type} VM of type {vm_type}...")
            
            config = {}
            if vm_type == "xcpng":
                config['xcpng_config'] = {}
            
            vm = create_bio_vm(vm_id, bio_type, vm_type, config)
            
            print(f"✅ Successfully created VM: {vm_id}")
            print(f"   Biological Type: {bio_type}")
            print(f"   VM Type: {vm_type}")
            print(f"   VM Object: {type(vm).__name__}")
            
        except Exception as e:
            print(f"❌ Failed to create VM: {e}")
    
    def _jcvi_workflows_menu(self):
        """Handle JCVI workflow operations."""
        if not self.jcvi_manager or not self.jcvi_manager.available:
            print("❌ JCVI functionality not available")
            return
        
        choices = [
            Choice("📋 List Available Genomes", "list"),
            Choice("📥 Acquire Genome for JCVI", "acquire"),
            Choice("🔬 Run Analysis Workflow", "workflow"),
            Choice("📊 Check JCVI Status", "status"),
            Choice("🔙 Back", "back")
        ]
        
        action = questionary.select("JCVI Workflows:", choices=choices).ask()
        
        if action == "list":
            self._jcvi_list_genomes()
        elif action == "acquire":
            self._jcvi_acquire_genome()
        elif action == "workflow":
            self._jcvi_run_workflow()
        elif action == "status":
            self._jcvi_status()
        elif action == "back":
            return
    
    def _vm_management_menu(self):
        """Handle VM management operations."""
        if not self.vm_manager:
            print("❌ VM Manager not available")
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
    
    def _conversion_menu(self):
        """Handle format conversion operations."""
        if not self.converter:
            print("❌ Format converter not available")
            return
        
        print("🔄 Format Conversion")
        print("Available soon - BioXen to JCVI format conversion")
    
    def _show_system_status(self):
        """Show system component status."""
        print("\n📊 System Status")
        print("=" * 40)
        
        components = [
            ("Questionary (Interactive UI)", QUESTIONARY_AVAILABLE),
            ("Genome Downloader", GENOME_DOWNLOADER_AVAILABLE),
            ("Factory API", FACTORY_API_AVAILABLE),
            ("JCVI Integration", JCVI_INTEGRATION_AVAILABLE),
            ("VM Library", LIBRARY_VM_AVAILABLE),
        ]
        
        for name, available in components:
            status = "✅ Available" if available else "❌ Not Available"
            print(f"   {name}: {status}")
        
        if self.jcvi_manager:
            jcvi_status = "✅ Available" if self.jcvi_manager.available else "❌ Not Available"
            print(f"   JCVI Manager: {jcvi_status}")
    
    def _list_genomes(self):
        """List available genomes."""
        print("\n📋 Available Minimal Genomes:")
        print("=" * 50)
        
        for key, info in MINIMAL_GENOMES.items():
            print(f"🧬 {key}")
            print(f"   Description: {info['description']}")
            print(f"   Tax ID: {info['taxid']}")
            print()
    
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
    
    def _interactive_genome_selection(self):
        """Run interactive genome selection."""
        if 'interactive_genome_selection' in globals():
            interactive_genome_selection()
        else:
            print("❌ Interactive genome selection not available")
    
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
            print("Text-based download not implemented")
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
    client = BioXenEnhancedClient()
    
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
