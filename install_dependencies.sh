#!/bin/bash

# Simple BioXen Dependencies Installer
# Installs requirements.txt and upgrades PyYAML

set -e  # Exit on any error

echo "🔧 Installing BioXen Dependencies..."
echo

# Install Python dependencies from requirements.txt
echo "📦 Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt
echo "✅ Python dependencies installed successfully"

echo

# Upgrade PyYAML to version 6.0+
echo "🔄 Upgrading PyYAML to version 6.0+..."
pip install --upgrade PyYAML

# Verify PyYAML version
echo "🔍 Verifying PyYAML version..."
PYYAML_VERSION=$(python3 -c "import yaml; print(yaml.__version__)" 2>/dev/null || echo "failed")
if [[ "$PYYAML_VERSION" != "failed" ]]; then
    echo "✅ PyYAML version: $PYYAML_VERSION"
else
    echo "❌ Failed to verify PyYAML installation"
    exit 1
fi

echo
echo "🎉 Installation complete!"
echo
echo "Quick test commands:"
echo "  python3 -c \"import bioxen_jcvi_vm_lib; print('BioXen import successful!')\""
echo "  python3 tests/test_bioxen_v0_0_7_clean.py"
