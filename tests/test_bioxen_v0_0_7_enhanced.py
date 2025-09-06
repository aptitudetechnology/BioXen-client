#!/usr/bin/env python3
"""
BioXen Package Diagnostic Script
Identifies package installation and naming issues
"""

import sys
import pkg_resources
import importlib.util
from pathlib import Path

def check_installed_packages():
    """Check what BioXen-related packages are installed"""
    print("🔍 Installed Package Analysis")
    print("="*60)
    
    installed_packages = [pkg.project_name for pkg in pkg_resources.working_set]
    bioxen_packages = [pkg for pkg in installed_packages if 'bioxen' in pkg.lower()]
    
    print(f"📦 BioXen-related packages found: {len(bioxen_packages)}")
    for pkg in bioxen_packages:
        try:
            dist = pkg_resources.get_distribution(pkg)
            print(f"   • {pkg} v{dist.version}")
            print(f"     Location: {dist.location}")
            if hasattr(dist, 'requires'):
                deps = [str(req) for req in dist.requires()]
                if deps:
                    print(f"     Dependencies: {deps}")
        except Exception as e:
            print(f"   • {pkg}: Error getting details - {e}")
    
    return bioxen_packages

def check_import_variations():
    """Try different import variations to find the correct module name"""
    print("\n🔬 Import Variations Test")
    print("="*60)
    
    import_attempts = [
        'bioxen_jcvi_vm_lib',
        'bioxen-jcvi-vm-lib',
        'bioxen_jcvi_vm_lib.api',
        'bioxen',
        'jcvi_vm_lib',
        'biovm'
    ]
    
    successful_imports = []
    
    for module_name in import_attempts:
        try:
            module = __import__(module_name)
            print(f"✅ '{module_name}' - SUCCESS")
            print(f"   Location: {getattr(module, '__file__', 'Unknown')}")
            print(f"   Version: {getattr(module, '__version__', 'Not specified')}")
            successful_imports.append(module_name)
        except ImportError as e:
            print(f"❌ '{module_name}' - FAILED: {e}")
        except Exception as e:
            print(f"⚠️  '{module_name}' - ERROR: {e}")
    
    return successful_imports

def check_site_packages():
    """Check site-packages directory for BioXen modules"""
    print("\n📁 Site-packages Directory Analysis")
    print("="*60)
    
    for path in sys.path:
        if 'site-packages' in path:
            site_path = Path(path)
            if site_path.exists():
                bioxen_dirs = list(site_path.glob('*bioxen*'))
                if bioxen_dirs:
                    print(f"📂 {site_path}:")
                    for dir_path in bioxen_dirs:
                        print(f"   • {dir_path.name}")
                        if dir_path.is_dir():
                            init_file = dir_path / '__init__.py'
                            print(f"     Has __init__.py: {init_file.exists()}")
                            if init_file.exists():
                                try:
                                    content = init_file.read_text()[:200]
                                    print(f"     __init__.py preview: {content[:100]}...")
                                except Exception as e:
                                    print(f"     __init__.py read error: {e}")

def check_console_scripts():
    """Check if console scripts are installed"""
    print("\n🖥️  Console Scripts Analysis")
    print("="*60)
    
    try:
        import subprocess
        result = subprocess.run(['which', 'bioxen'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ 'bioxen' command found at: {result.stdout.strip()}")
        else:
            print("❌ 'bioxen' command not found in PATH")
        
        # Check pip show output
        pip_result = subprocess.run(['pip', 'show', 'bioxen-jcvi-vm-lib'], 
                                  capture_output=True, text=True)
        if pip_result.returncode == 0:
            print("\n📋 Package Details:")
            print(pip_result.stdout)
        else:
            print("❌ Package not found in pip")
            
    except Exception as e:
        print(f"⚠️  Console script check failed: {e}")

def fix_suggestions(successful_imports, bioxen_packages):
    """Provide specific fix suggestions based on findings"""
    print("\n🔧 Fix Suggestions")
    print("="*60)
    
    if not bioxen_packages:
        print("❌ No BioXen packages found. Solutions:")
        print("   1. Check if you're in the correct virtual environment")
        print("   2. Reinstall the package: pip install -e .")
        print("   3. Check if package is in TestPyPI vs PyPI")
        return
    
    if not successful_imports:
        print("❌ Package installed but not importable. Solutions:")
        print("   1. Package naming mismatch - check actual module structure")
        print("   2. Installation incomplete - missing __init__.py files")
        print("   3. Python path issues")
        print("   4. Try: pip uninstall bioxen-jcvi-vm-lib && pip install -e .")
        return
    
    if successful_imports:
        print("✅ Found working import(s):")
        for imp in successful_imports:
            print(f"   • Use: import {imp}")
        
        print("\n🔄 Update your test script to use the working import name")
        return
    
    print("⚠️  Mixed results - manual investigation needed")

def main():
    """Main diagnostic routine"""
    print("🧬 BioXen JCVI VM Library Package Diagnostics")
    print("="*80)
    print(f"🐍 Python {sys.version}")
    print(f"📍 Working directory: {Path.cwd()}")
    print(f"🔧 Virtual environment: {sys.prefix}")
    
    # Run all diagnostic checks
    bioxen_packages = check_installed_packages()
    successful_imports = check_import_variations()
    check_site_packages()
    check_console_scripts()
    
    # Provide targeted suggestions
    fix_suggestions(successful_imports, bioxen_packages)
    
    # Final recommendation
    print("\n🎯 Recommended Next Steps:")
    if successful_imports:
        print("   1. Update test scripts to use working import names")
        print("   2. Fix PyYAML dependency issue")
        print("   3. Re-run tests")
    else:
        print("   1. Reinstall package locally: pip install -e .")
        print("   2. Check package structure in src/ directory") 
        print("   3. Verify virtual environment activation")

if __name__ == "__main__":
    main()