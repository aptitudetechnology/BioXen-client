#!/usr/bin/env python3
"""
Simple test script for bioxen-jcvi-vm-lib v0.0.3
"""

import sys
sys.path.insert(0, '/home/chris/BioXen-luavm/venv/lib/python3.10/site-packages')

print("🧪 Testing bioxen-jcvi-vm-lib v0.0.3 imports...")

# Test basic Python imports first
try:
    import os
    from pathlib import Path
    print("✅ Basic Python imports work")
except Exception as e:
    print(f"❌ Basic Python imports failed: {e}")
    sys.exit(1)

# Try to import specific modules step by step
try:
    print("📦 Testing hypervisor import...")
    from src.hypervisor.core import BioXenHypervisor
    print("✅ Hypervisor import successful")
except Exception as e:
    print(f"❌ Hypervisor import failed: {e}")

try:
    print("📦 Testing API import...")
    from src.api import create_bio_vm
    print("✅ API import successful")
except Exception as e:
    print(f"❌ API import failed: {e}")

try:
    print("📦 Testing JCVI manager import...")
    from src.api.jcvi_manager import create_jcvi_manager
    print("✅ JCVI manager import successful")
except Exception as e:
    print(f"❌ JCVI manager import failed: {e}")

print("\n🎯 Import test complete.")
