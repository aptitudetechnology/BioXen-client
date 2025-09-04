#!/usr/bin/env python3
"""
Reproduction Script for bioxen-jcvi-vm-lib Issues
For Library Maintainer Testing

This script demonstrates the issues encountered during integration testing
and provides minimal examples for debugging.
"""

import sys
import os
from pathlib import Path

print("🧪 bioxen-jcvi-vm-lib Issue Reproduction Script")
print("=" * 50)

# Test 1: Demonstrate typing compatibility issue
print("\n1. Testing Python typing compatibility...")
print("Python version:", sys.version)

try:
    print("   Attempting import without patch...")
    # This should fail in current library versions
    from src.hypervisor.core import BioXenHypervisor
    print("   ✅ Import successful (issue already fixed!)")
except AttributeError as e:
    if "_ClassVar" in str(e):
        print(f"   ❌ Typing issue confirmed: {e}")
        print("   🔧 Applying compatibility patch...")
        
        import typing
        if not hasattr(typing, '_ClassVar'):
            typing._ClassVar = typing.ClassVar
        
        try:
            from src.hypervisor.core import BioXenHypervisor
            print("   ✅ Import successful with patch")
        except Exception as e:
            print(f"   ❌ Still failing: {e}")
    else:
        print(f"   ❌ Unexpected error: {e}")
except ImportError as e:
    print(f"   ⚠️  Import path issue: {e}")
    print("   (Install library and adjust sys.path as needed)")
except Exception as e:
    print(f"   ❌ Unexpected error: {e}")

# Test 2: Check BioResourceManager API
print("\n2. Testing BioResourceManager API...")
try:
    from src.api.resource_manager import BioResourceManager
    
    # Test initialization without parameters (expected to work per spec)
    print("   Attempting BioResourceManager() without parameters...")
    try:
        resource_manager = BioResourceManager()
        print("   ✅ BioResourceManager initialized successfully")
    except TypeError as e:
        if "missing 1 required positional argument" in str(e):
            print(f"   ❌ API change detected: {e}")
            print("   💡 Suggestion: Make 'vm' parameter optional or document requirement")
        else:
            print(f"   ❌ Unexpected TypeError: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        
except ImportError as e:
    print(f"   ⚠️  Cannot import BioResourceManager: {e}")

# Test 3: Check JCVI integration availability
print("\n3. Testing JCVI integration modules...")
try:
    from bioxen_jcvi_integration import *
    print("   ✅ JCVI integration modules available")
except ImportError as e:
    print(f"   ❌ JCVI integration missing: {e}")
    print("   💡 This module is referenced in code but not included in package")

# Test 4: Test Factory Pattern API
print("\n4. Testing Factory Pattern API...")
try:
    from src.api import create_bio_vm
    print("   ✅ create_bio_vm import successful")
    
    # Test if we can call the factory function
    try:
        # Note: This might fail due to other dependencies, but import should work
        bio_vm = create_bio_vm()
        print("   ✅ create_bio_vm() call successful")
    except Exception as e:
        print(f"   ⚠️  create_bio_vm() call failed: {e}")
        print("   (This may be expected depending on configuration)")
        
except ImportError as e:
    print(f"   ❌ Factory API import failed: {e}")

# Test 5: Installation dependency check
print("\n5. Testing installation dependencies...")
try:
    import pkg_resources
    dist = pkg_resources.get_distribution('bioxen-jcvi-vm-lib')
    print(f"   Library version: {dist.version}")
    print(f"   Install location: {dist.location}")
    
    # Check for dependency conflicts
    try:
        requirements = dist.requires()
        print(f"   Dependencies: {len(requirements)} found")
        for req in requirements:
            print(f"     - {req}")
    except Exception as e:
        print(f"   ⚠️  Could not read dependencies: {e}")
        
except ImportError:
    print("   ⚠️  pkg_resources not available")
except pkg_resources.DistributionNotFound:
    print("   ❌ bioxen-jcvi-vm-lib not found in installed packages")

# Summary and Recommendations
print("\n" + "=" * 50)
print("📋 SUMMARY FOR LIBRARY MAINTAINER")
print("=" * 50)

recommendations = [
    "1. Fix typing._ClassVar → typing.ClassVar throughout codebase",
    "2. Document BioResourceManager initialization requirements",
    "3. Include missing bioxen_jcvi_integration module in package",
    "4. Resolve dependency conflicts (twine/pkginfo)",
    "5. Add compatibility tests for Python 3.8+"
]

for rec in recommendations:
    print(rec)

print("\n🔧 Quick Fix Commands:")
print("   # Search for typing issues:")
print("   grep -r '_ClassVar' src/")
print("   # Replace with:")
print("   sed -i 's/typing\\._ClassVar/typing.ClassVar/g' src/**/*.py")

print("\n📝 Test this script with:")
print("   python3 reproduction_script.py")
print("   # Run after each fix to verify resolution")

print("\n✉️  Contact: Provide this output to integration team for validation")
