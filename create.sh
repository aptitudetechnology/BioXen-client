#!/bin/bash

# Script to create modular directory structure for BioXen CLI
# Run this script from the root of your project directory

set -e  # Exit on any error

echo "Creating modular BioXen CLI directory structure..."

# Create main package directory
mkdir -p bioxen_cli

# Create subdirectories
mkdir -p bioxen_cli/config
mkdir -p bioxen_cli/vm
mkdir -p bioxen_cli/ui
mkdir -p bioxen_cli/packages
mkdir -p bioxen_cli/utils

echo "Creating package __init__.py files..."

# Create __init__.py files
touch bioxen_cli/__init__.py
touch bioxen_cli/config/__init__.py
touch bioxen_cli/vm/__init__.py
touch bioxen_cli/ui/__init__.py
touch bioxen_cli/packages/__init__.py
touch bioxen_cli/utils/__init__.py

echo "Creating main module files..."

# Main entry point
touch bioxen_cli/main.py

# Configuration management
touch bioxen_cli/config/manager.py

# VM management modules
touch bioxen_cli/vm/status.py
touch bioxen_cli/vm/basic_vm.py
touch bioxen_cli/vm/xcpng_vm.py
touch bioxen_cli/vm/converter.py

# UI modules
touch bioxen_cli/ui/menus.py
touch bioxen_cli/ui/interactive.py

# Package management
touch bioxen_cli/packages/installer.py

# Utilities
touch bioxen_cli/utils/cleanup.py

echo "Creating additional project files..."

# Create setup.py for packaging
touch setup.py

# Create requirements.txt
touch requirements.txt

# Create README for the new structure
touch README_MODULAR.md

# Create a launcher script
touch run_bioxen.py

echo "Directory structure created successfully!"
echo ""
echo "Created structure:"
echo "bioxen_cli/"
echo "├── __init__.py"
echo "├── main.py"
echo "├── config/"
echo "│   ├── __init__.py"
echo "│   └── manager.py"
echo "├── vm/"
echo "│   ├── __init__.py"
echo "│   ├── status.py"
echo "│   ├── basic_vm.py"
echo "│   ├── xcpng_vm.py"
echo "│   └── converter.py"
echo "├── ui/"
echo "│   ├── __init__.py"
echo "│   ├── menus.py"
echo "│   └── interactive.py"
echo "├── packages/"
echo "│   ├── __init__.py"
echo "│   └── installer.py"
echo "└── utils/"
echo "    ├── __init__.py"
echo "    └── cleanup.py"
echo ""
echo "Additional files:"
echo "├── setup.py"
echo "├── requirements.txt"
echo "├── README_MODULAR.md"
echo "└── run_bioxen.py"
echo ""
echo "Next steps:"
echo "1. Run this script: chmod +x create_bioxen_modular_structure.sh && ./create_bioxen_modular_structure.sh"
echo "2. Move/refactor code from interactive-bioxen.py into the appropriate modules"
echo "3. Update imports and dependencies"
echo "4. Test the modular structure"

# Make the directory structure visible
ls -la bioxen_cli/
echo ""
ls -la bioxen_cli/*/