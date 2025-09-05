#!/usr/bin/env python3
"""
BioXen Launcher - Interactive Biological Virtualization System

This script launches the appropriate BioXen interface based on available dependencies.
"""

import sys
import subprocess
from pathlib import Path

def check_questionary():
    """Check if questionary is installed."""
    try:
        import questionary
        return True
    except ImportError:
        return False

def install_questionary():
    """Install questionary via pip."""
    print("📦 Installing questionary...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'questionary==2.1.0'])
        print("✅ questionary installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install questionary")
        return False

def main():
    """Main launcher logic."""
    print("🧬 BioXen Biological Virtualization System")
    print("=" * 50)
    
    # Check if questionary is available
    if not check_questionary():
        print("⚠️  questionary not found - required for interactive interface")
        print("\nOptions:")
        print("1. Install questionary automatically")
        print("2. Install manually: pip install questionary==2.1.0")
        print("3. Use command-line interface only")
        
        choice = input("\nChoice (1/2/3): ").strip()
        
        if choice == "1":
            if not install_questionary():
                print("❌ Installation failed. Try manual installation.")
                sys.exit(1)
        elif choice == "2":
            print("📋 Run: pip install questionary==2.1.0")
            print("Then restart this script.")
            sys.exit(0)
        elif choice == "3":
            print("\n📋 Command-line usage:")
            print("  python3 download_genomes.py list")
            print("  python3 download_genomes.py mycoplasma_genitalium")
            print("  python3 test_real_genome.py")
            sys.exit(0)
        else:
            print("❌ Invalid choice")
            sys.exit(1)
    
    # Launch interactive interface
    print("\n🚀 Launching interactive BioXen interface...")
    
    # Ask what the user wants to do
    print("\nWhat would you like to do?")
    print("1. 📥 Download and manage genomes")
    print("2. 🖥️  Launch BioXen hypervisor interface")
    print("3. 🧪 Test with existing genome (test_real_genome.py)")
    
    choice = input("\nChoice (1/2/3): ").strip()
    
    if choice == "1":
        print("🚀 Launching genome downloader...")
        subprocess.run([sys.executable, "download_genomes.py"])
    elif choice == "2":
        print("🚀 Launching BioXen hypervisor...")
        subprocess.run([sys.executable, "interactive_bioxen.py"])
    elif choice == "3":
        print("🚀 Running genome test...")
        subprocess.run([sys.executable, "test_real_genome.py"])
    else:
        print("❌ Invalid choice")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
