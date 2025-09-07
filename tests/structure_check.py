#!/usr/bin/env python3
"""
Check BioXen project structure and suggest fixes
"""

import os
from pathlib import Path

def check_project_structure():
    """Check if the project has the correct structure"""
    print("🏗️  Project Structure Analysis")
    print("="*60)
    
    current_dir = Path.cwd()
    print(f"📍 Current directory: {current_dir}")
    
    # Check for common Python project files
    project_files = [
        "setup.py",
        "setup.cfg", 
        "pyproject.toml",
        "requirements.txt",
        "README.md"
    ]
    
    print(f"\n📋 Project Files:")
    for file in project_files:
        file_path = current_dir / file
        if file_path.exists():
            print(f"   ✅ {file}")
            if file == "setup.py":
                try:
                    content = file_path.read_text()
                    if "name=" in content:
                        # Extract package name
                        for line in content.split('\n'):
                            if 'name=' in line and ('bioxen' in line.lower() or 'jcvi' in line.lower()):
                                print(f"      Package name: {line.strip()}")
                                break
                except Exception as e:
                    print(f"      Error reading setup.py: {e}")
        else:
            print(f"   ❌ {file}")
    
    # Check for source directory structures
    possible_src_dirs = [
        "src/bioxen_jcvi_vm_lib",
        "bioxen_jcvi_vm_lib", 
        "src",
        "lib",
        "biovm"
    ]
    
    print(f"\n📂 Source Directory Structure:")
    found_src = False
    for src_dir in possible_src_dirs:
        src_path = current_dir / src_dir
        if src_path.exists():
            print(f"   ✅ {src_dir}/")
            found_src = True
            
            # Check for Python modules
            if src_path.is_dir():
                python_files = list(src_path.glob("*.py"))
                init_file = src_path / "__init__.py"
                
                print(f"      __init__.py: {'✅' if init_file.exists() else '❌'}")
                print(f"      Python files: {len(python_files)}")
                
                # Check subdirectories
                subdirs = [d for d in src_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
                if subdirs:
                    print(f"      Subdirectories: {[d.name for d in subdirs]}")
                    
                    # Check api directory specifically
                    api_dir = src_path / "api"
                    if api_dir.exists():
                        api_files = list(api_dir.glob("*.py"))
                        print(f"         api/: {len(api_files)} Python files")
                        factory_file = api_dir / "factory.py"
                        print(f"         factory.py: {'✅' if factory_file.exists() else '❌'}")
        else:
            print(f"   ❌ {src_dir}/")
    
    if not found_src:
        print("   ⚠️  No source directory found!")
    
    return found_src

def check_git_status():
    """Check git status and suggest actions"""
    print(f"\n🔄 Git Status:")
    try:
        import subprocess
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, cwd=Path.cwd())
        if result.returncode == 0:
            if result.stdout.strip():
                print("   📝 Uncommitted changes detected")
                stdout_lines = result.stdout.strip().split('\n')
                lines = stdout_lines[:5]  # Show first 5
                for line in lines:
                    print(f"      {line}")
                if len(stdout_lines) > 5:
                    remaining = len(stdout_lines) - 5
                    print(f"      ... and {remaining} more")
            else:
                print("   ✅ Working directory clean")
        else:
            print("   ⚠️  Not a git repository or git error")
    except Exception as e:
        print(f"   ❌ Git check failed: {e}")

def suggest_fixes():
    """Suggest specific fixes based on findings"""
    print(f"\n🔧 Recommended Fix Actions:")
    print("="*60)
    
    current_dir = Path.cwd()
    
    # Check if we're in the right directory
    if "BioXen-client" in str(current_dir):
        print("1. 🎯 Switch to working environment:")
        print("   cd /home/chris/BioXen-luavm")
        print("   source venv/bin/activate")
        print("   python3 -c 'import bioxen_jcvi_vm_lib; print(bioxen_jcvi_vm_lib.__version__)'")
        print()
        
    print("2. 🧹 Clean current environment:")
    print("   pip uninstall bioxen-jcvi-vm-lib -y")
    print("   pip uninstall bioxen_jcvi_vm_lib -y")
    print()
    
    print("3. 🔄 Reinstall properly:")
    if (current_dir / "setup.py").exists():
        print("   pip install -e .")
    else:
        print("   cd /home/chris/BioXen-luavm")
        print("   pip install -e .")
    print()
    
    print("4. ✅ Verify installation:")
    print("   python3 -c 'import bioxen_jcvi_vm_lib; print(\"Success!\")' ")
    print()
    
    print("5. 🧪 Run tests:")
    print("   python3 tests/test_bioxen_v0_0_7_enhanced.py")

def main():
    """Main structure check"""
    print("🧬 BioXen Project Structure Checker")
    print("="*80)
    
    found_src = check_project_structure()
    check_git_status()
    suggest_fixes()
    
    if not found_src:
        print("\n⚠️  CRITICAL: No source code structure found!")
        print("   This explains why imports are failing.")
        print("   You may be in the wrong directory or the project needs setup.")

if __name__ == "__main__":
    main()