#!/usr/bin/env python3
"""
Main controller for BioXen CLI.
"""

import signal
import sys

try:
    # pylua_bioxen_vm_lib imports
    from pylua_bioxen_vm_lib import VMManager, InteractiveSession, SessionManager
    from pylua_bioxen_vm_lib.utils.curator import get_curator
    from pylua_bioxen_vm_lib.env import EnvironmentManager
except ImportError:
    print("❌ pylua_bioxen_vm_lib not installed")
    sys.exit(1)

from .config.manager import ConfigManager
from .vm.status import VMStatusTracker
from .vm.basic_vm import BasicVMOperations
from .vm.xcpng_vm import XCPngVMOperations
from .vm.converter import VMConverter
from .packages.installer import PackageInstaller
from .ui.menus import MainMenu
from .ui.interactive import InteractiveSession as UIInteractiveSession
from .utils.cleanup import cleanup_handler


class BioXenCLI:
    """Main BioXen CLI application."""
    
    def __init__(self):
        # Initialize core components
        self.vm_manager = VMManager()
        self.config_manager = ConfigManager()
        self.vm_tracker = VMStatusTracker()
        
        # Initialize curator and environment manager
        self.curator = get_curator()
        self.env_manager = EnvironmentManager()
        
        # Initialize VM operations
        self.basic_vm_ops = BasicVMOperations(self.vm_manager, self.vm_tracker)
        self.xcpng_vm_ops = XCPngVMOperations(self.vm_manager, self.vm_tracker)
        self.vm_converter = VMConverter(self.vm_manager, self.vm_tracker)
        
        # Initialize package installer
        self.package_installer = PackageInstaller(
            self.vm_manager, self.vm_tracker, self.curator
        )
        
        # Initialize main menu
        self.main_menu = MainMenu(
            self.vm_manager,
            self.config_manager,
            self.vm_tracker,
            self.package_installer,
            self.basic_vm_ops,
            self.xcpng_vm_ops,
            self.vm_converter,
            self.curator,
            self.env_manager
        )
        
        # Setup signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print("\n🛑 Shutting down...")
        cleanup_handler(self.vm_manager, self.vm_tracker)
        sys.exit(0)
    
    def run(self):
        """Run the main CLI application."""
        try:
            self.main_menu.run()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            cleanup_handler(self.vm_manager, self.vm_tracker)
        except Exception as e:
            print(f"❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            cleanup_handler(self.vm_manager, self.vm_tracker)