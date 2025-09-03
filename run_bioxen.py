#!/usr/bin/env python3
"""
Launch script for BioXen CLI.
"""

if __name__ == "__main__":
    from bioxen_cli.main import BioXenCLI
    cli = BioXenCLI()
    cli.run()