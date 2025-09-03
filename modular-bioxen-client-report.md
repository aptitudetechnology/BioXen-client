
# Modular BioXen Client Refactor Report (Updated)

## Overview
This report reflects the updated modularization plan in `modular-bioxen-client.md` and the current state of the codebase. The modular directory structure exists and all required logic is present in the monolithic `interactive-bioxen.py` file, but the new modules are mostly empty.

## Current State
- Modular directory structure (`bioxen_cli/` and subfolders) is complete.
- Module files exist but are mostly empty.
- All CLI, VM, and package logic remains in the monolithic file.

## Extraction & Refactor Tasks
The updated plan provides a strict extraction order and conversion pattern:

### 1. `bioxen_cli/__init__.py`
Add package metadata and version info as specified.

### 2. `bioxen_cli/config/manager.py`
Extract the full `ConfigManager` class and all config/XCP-ng/VM default methods. Add required imports.

### 3. `bioxen_cli/vm/status.py`
Extract the full `VMStatus` class. Create a new `VMStatusTracker` class to manage VM status dictionaries and related operations.

### 4. `bioxen_cli/vm/basic_vm.py`
Convert `_create_basic_vm`, `_attach_to_subprocess_vm`, and part of `_interactive_loop` into a `BasicVMOperations` class. Use dependency injection for managers and trackers.

### 5. `bioxen_cli/vm/xcpng_vm.py`
Convert `_create_xcpng_vm`, `_collect_xen_config`, and `_attach_to_xen_vm` into a `XCPngVMOperations` class.

### 6. `bioxen_cli/vm/converter.py`
Convert `convert_vm_to_physical`, `_convert_to_elua`, and `_convert_to_lumorphix` into a `VMConverter` class.

### 7. `bioxen_cli/packages/installer.py`
Convert all package management methods into a `PackageInstaller` class.

### 8. `bioxen_cli/ui/menus.py`
Convert menu logic and configuration management methods into a `MainMenu` class. Inject all dependencies.

### 9. `bioxen_cli/ui/interactive.py`
Convert `_interactive_loop` and user input handling into an `InteractiveSession` class.

### 10. `bioxen_cli/utils/cleanup.py`
Convert the `cleanup` method into a standalone `cleanup_handler` function.

### 11. `bioxen_cli/main.py`
Refactor orchestration logic from `VMCLI` into a new `BioXenCLI` class. Set up all components and main menu loop.

### 12. `run_bioxen.py`
Launcher script matches the updated specification.

## Implementation Guidelines
- **Preserve all print statements, prompts, and error handling exactly.**
- **No changes to user experience or menu flows.**
- **Use dependency injection and type hints.**
- **Follow the import pattern and method conversion pattern provided.**

## Validation Steps
After each module is refactored:
1. Import test (e.g. `python -c "from bioxen_cli.config.manager import ConfigManager"`)
2. Check for missing dependencies
3. Confirm original functionality is preserved

## Implementation Order
1. `config/manager.py`
2. `vm/status.py`
3. `utils/cleanup.py`
4. `packages/installer.py`
5. `vm/basic_vm.py`, `vm/xcpng_vm.py`, `vm/converter.py`
6. `ui/interactive.py`
7. `ui/menus.py`
8. `main.py`
9. `run_bioxen.py`

## Key Success Criteria
- Running `python run_bioxen.py` gives an identical experience to the original.
- All VM, package, and configuration features work unchanged.
- No functionality or error handling is lost.

## Recommendations
- Begin extraction in the order above, strictly following the updated plan.
- After each module, run import and functionality tests.
- Only proceed to the next module when the previous passes validation.

## Conclusion
The codebase is ready for modularization. The updated plan provides a clear extraction order and strict requirements for preserving user experience and functionality. All logic must be moved from the monolithic file to the new modules, with no changes to behavior.
