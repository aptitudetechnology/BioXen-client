#!/usr/bin/env python3
"""
Monkey patch for typing._ClassVar compatibility
"""

import sys
import typing

# Fix typing._ClassVar compatibility issue
if not hasattr(typing, '_ClassVar'):
    typing._ClassVar = typing.ClassVar

sys.path.insert(0, '/home/chris/BioXen-luavm/venv/lib/python3.10/site-packages')

print("🔧 Applied typing._ClassVar compatibility fix...")

# Now test imports
try:
    print("📦 Testing hypervisor import with fix...")
    from src.hypervisor.core import BioXenHypervisor
    print("✅ Hypervisor import successful with patch")
    
    print("📦 Testing API import with fix...")
    from src.api import create_bio_vm
    print("✅ API import successful with patch")
    
    print("📦 Testing JCVI manager import with fix...")
    from src.api.jcvi_manager import create_jcvi_manager
    print("✅ JCVI manager import successful with patch")
    
    print("\n🎉 All imports successful! Library is compatible with patching.")
    
except Exception as e:
    print(f"❌ Import still failed: {e}")
    sys.exit(1)
