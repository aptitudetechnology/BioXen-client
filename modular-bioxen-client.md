# GitHub Copilot Instructions for BioXen CLI Modularization - Updated

## Context
Based on the refactor report, the modular directory structure exists but is mostly empty. All the required logic exists in the monolithic `interactive-bioxen.py` file and needs to be extracted into the appropriate modules. The report confirms that all classes and methods referenced in the plan are present in the codebase.

## Current State
- Directory structure: **COMPLETE** (`bioxen_cli/` with all subdirectories)
- Module files: **EXIST but mostly empty**
- Source code: **ALL in monolithic `interactive-bioxen.py`**
- Task: **Extract and refactor existing code into modules**

## Extraction Tasks (In Order)

### 1. `bioxen_cli/__init__.py` - Package Metadata
```python
"""
BioXen Lua VM Interactive CLI v0.1.22

Enhanced CLI for managing BioXen Lua VMs with Phase 3 XCP-ng integration.
"""

__version__ = "0.1.22"
__author__ = "BioXen Development Team"
```

### 2. `bioxen_cli/config/manager.py` - Extract ConfigManager Class
**EXTRACT EXACTLY:**
- Complete `ConfigManager` class from the monolithic file
- All methods: `__init__`, `load_config`, `save_config`, `default_config`
- XCP-ng methods: `get_xcpng_config`, `get_xcpng_configs`, `load_xcpng_file_config`, `save_xcpng_config`
- VM defaults: `get_vm_defaults`

**Add imports:**
```python
import json
from pathlib import Path
from typing import Dict, Any, Optional
```

### 3. `bioxen_cli/vm/status.py` - Extract VMStatus + Create VMStatusTracker
**EXTRACT:**
- Complete `VMStatus` class from monolithic file
- All methods including `get_uptime()`

**CREATE NEW:**
```python
class VMStatusTracker:
    """Tracks status of all VMs."""
    
    def __init__(self):
        self.vm_status: Dict[str, VMStatus] = {}
    
    # Add methods for managing the vm_status dictionary that was in VMCLI
```

### 4. `bioxen_cli/vm/basic_vm.py` - Extract Basic VM Operations
**EXTRACT and convert to class:**
- `_create_basic_vm` method → `BasicVMOperations.create_vm`
- `_attach_to_subprocess_vm` method → `BasicVMOperations.attach_to_vm`
- Part of `_interactive_loop` method → `BasicVMOperations.interactive_loop`

**Class structure:**
```python
class BasicVMOperations:
    def __init__(self, vm_manager, vm_tracker: VMStatusTracker):
        self.vm_manager = vm_manager
        self.vm_tracker = vm_tracker
```

### 5. `bioxen_cli/vm/xcpng_vm.py` - Extract XCP-ng VM Operations  
**EXTRACT and convert to class:**
- `_create_xcpng_vm` method → `XCPngVMOperations.create_vm`
- `_collect_xen_config` method → `XCPngVMOperations.collect_config`
- `_attach_to_xen_vm` method → `XCPngVMOperations.attach_to_vm`

### 6. `bioxen_cli/vm/converter.py` - Extract Conversion Logic
**EXTRACT and convert to class:**
- `convert_vm_to_physical` method → `VMConverter.convert_vm_to_physical`
- `_convert_to_elua` method → `VMConverter.convert_to_elua`
- `_convert_to_lumorphix` method → `VMConverter.convert_to_lumorphix`

### 7. `bioxen_cli/packages/installer.py` - Extract Package Management
**EXTRACT and convert to class:**
- `install_packages` method → `PackageInstaller.install_packages`
- `_install_single_package` method → `PackageInstaller.install_single_package`
- `_install_multiple_packages` method → `PackageInstaller.install_multiple_packages`
- `_install_package_to_vm` method → `PackageInstaller.install_package_to_vm`
- `_verify_package_in_vm` method → `PackageInstaller.verify_package_in_vm`
- `_show_package_status` method → `PackageInstaller.show_package_status`

### 8. `bioxen_cli/ui/menus.py` - Extract Menu Logic
**EXTRACT and convert to class:**
- `main_menu` method → `MainMenu.run`
- `setup_profile` method → `MainMenu.setup_profile`
- `show_environment_status` method → `MainMenu.show_environment_status`
- `list_vms` method → `MainMenu.list_vms`
- `stop_vm` method → `MainMenu.stop_vm`
- `manage_configuration` method → `MainMenu.manage_configuration`
- All the `_manage_*` configuration methods

**Dependencies to inject:**
```python
class MainMenu:
    def __init__(self, vm_manager, config_manager, vm_tracker, package_installer, curator, env_manager):
        # Store all dependencies
```

### 9. `bioxen_cli/ui/interactive.py` - Extract Interactive Session
**EXTRACT:**
- `_interactive_loop` method → `InteractiveSession.run_loop`
- User input handling logic

### 10. `bioxen_cli/utils/cleanup.py` - Extract Cleanup Logic
**EXTRACT and convert to function:**
- `cleanup` method from VMCLI → `cleanup_handler(vm_manager, vm_tracker)`

```python
def cleanup_handler(vm_manager, vm_tracker):
    """Cleanup resources before exit."""
    print("\n🧹 Cleaning up running VMs...")
    # Move existing cleanup logic here
```

### 11. `bioxen_cli/main.py` - Create New Main Controller
**EXTRACT from VMCLI class:**
- `__init__` logic → `BioXenCLI.__init__`
- Signal handling setup
- Main orchestration logic

**NEW structure:**
```python
class BioXenCLI:
    def __init__(self):
        # Initialize all components
        self.vm_manager = VMManager()
        self.config_manager = ConfigManager()
        self.vm_tracker = VMStatusTracker()
        self.package_installer = PackageInstaller(self.vm_manager, self.vm_tracker)
        # etc.
        
        self.main_menu = MainMenu(...)
        
    def run(self):
        # Run the main menu loop
        self.main_menu.run()
```

### 12. `run_bioxen.py` - Create Launcher
```python
#!/usr/bin/env python3
"""Launch script for BioXen CLI."""

if __name__ == "__main__":
    from bioxen_cli.main import BioXenCLI
    cli = BioXenCLI()
    cli.run()
```

## Critical Requirements

### Preserve Everything
- **Every print statement** must remain exactly the same
- **Every questionary prompt** must remain identical  
- **All error handling** must be preserved
- **User experience** must be unchanged
- **Menu flows** must work exactly as before

### Import Pattern for Each Module
```python
# Standard library
import os
import sys
import json
from typing import Dict, List, Optional, Any

# Third-party
import questionary
from questionary import Choice

# pylua_bioxen_vm_lib imports (keep exactly as in original)
try:
    from pylua_bioxen_vm_lib import VMManager, InteractiveSession
    # ... other imports
except ImportError as e:
    # Keep original error handling
```

### Method Conversion Pattern
When converting methods from VMCLI to new classes:

**Original:**
```python
def create_lua_vm(self):
    # existing logic using self.vm_status, self.config_manager
```

**Converted:**
```python
def create_lua_vm(self):
    # same logic but using self.vm_tracker.vm_status, self.config_manager
```

## Validation Steps

After each module:
1. **Import test**: `python -c "from bioxen_cli.config.manager import ConfigManager"`
2. **No missing dependencies**: Check all imports resolve
3. **Functionality preserved**: Original methods work the same way

## Implementation Order
1. `config/manager.py` (no dependencies)
2. `vm/status.py` (no dependencies)  
3. `utils/cleanup.py` (minimal dependencies)
4. `packages/installer.py` (depends on vm/status)
5. `vm/basic_vm.py`, `vm/xcpng_vm.py`, `vm/converter.py` (depend on vm/status)
6. `ui/interactive.py` (minimal dependencies)
7. `ui/menus.py` (depends on everything)
8. `main.py` (orchestrates everything)
9. `run_bioxen.py` (depends on main.py)

## Key Success Criteria
- User runs `python run_bioxen.py` and gets identical experience to original
- All VM creation, attachment, package installation works unchanged
- Configuration management works identically
- No functionality is lost or modified