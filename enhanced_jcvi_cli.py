#!/usr/bin/env python3
"""
BioXen JCVI Enhanced CLI - v0.0.03
Command-line interface for enhanced JCVI workflows with genome acquisition.

Builds on existing proven infrastructure while adding acquisition capabilities.
"""

import sys
import argparse
from pathlib import Path
from typing import List

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def cmd_list_genomes(args):
    """List available genomes for download."""
    try:
        from src.api.jcvi_manager import create_jcvi_manager
        
        manager = create_jcvi_manager()
        genomes = manager.list_available_genomes()
        
        if not genomes:
            print("❌ No genomes available for download")
            return 1
        
        print(f"📋 Available Genomes ({len(genomes)}):")
        print("=" * 60)
        
        for key, info in genomes.items():
            print(f"🧬 {key}")
            print(f"   Scientific name: {info.get('scientific_name', 'Unknown')}")
            print(f"   Description: {info.get('description', 'No description')}")
            print(f"   Tax ID: {info.get('taxid', 'Unknown')}")
            print()
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to list genomes: {e}")
        return 1

def cmd_acquire_genome(args):
    """Acquire a specific genome."""
    try:
        from src.api.jcvi_manager import create_jcvi_manager
        
        manager = create_jcvi_manager()
        
        print(f"📥 Acquiring genome: {args.genome}")
        result = manager.acquire_genome(args.genome, args.output_dir)
        
        if result['status'] == 'success':
            print(f"✅ Genome acquired successfully!")
            print(f"   Files: {result.get('files', [])}")
            print(f"   JCVI-ready: {result.get('jcvi_ready_files', [])}")
            print(f"   Output directory: {result.get('output_dir', 'Unknown')}")
            return 0
        else:
            print(f"❌ Acquisition failed: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"❌ Acquisition error: {e}")
        return 1

def cmd_run_workflow(args):
    """Run complete workflow from acquisition to analysis."""
    try:
        from src.api.jcvi_manager import create_jcvi_manager
        
        manager = create_jcvi_manager()
        
        genomes = args.genomes.split(',')
        genomes = [g.strip() for g in genomes]
        
        print(f"🚀 Running complete workflow:")
        print(f"   Genomes: {genomes}")
        print(f"   Analysis: {args.analysis}")
        
        result = manager.run_complete_workflow(genomes, args.analysis)
        
        if result['status'] == 'completed':
            print(f"✅ Workflow completed successfully!")
            print(f"   Acquired: {len(result.get('acquisition_results', []))}")
            print(f"   Analysis: {result.get('analysis_results', {}).get('status', 'Unknown')}")
            return 0
        else:
            print(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"❌ Workflow error: {e}")
        return 1

def cmd_status(args):
    """Show JCVI integration status."""
    try:
        from src.api.jcvi_manager import create_jcvi_manager
        
        manager = create_jcvi_manager()
        status = manager.get_status()
        
        print("📊 BioXen JCVI Integration Status:")
        print("=" * 40)
        
        jcvi_status = "✅ Available" if status.get('jcvi_available') else "❌ Not Available"
        print(f"JCVI Integration: {jcvi_status}")
        
        cli_status = "✅ Available" if status.get('cli_available') else "❌ Not Available"
        print(f"CLI Integration: {cli_status}")
        
        converter_status = "✅ Available" if status.get('converter_available') else "❌ Not Available"
        print(f"Format Converter: {converter_status}")
        
        if 'version_info' in status:
            print(f"Version Info: {status['version_info']}")
        
        if 'hardware_info' in status:
            hw = status['hardware_info']
            print(f"\n🖥️  Hardware:")
            print(f"   CPU Cores: {hw.get('cpu_cores', 'Unknown')}")
            print(f"   CPU Model: {hw.get('cpu_model', 'Unknown')}")
            print(f"   Memory: {hw.get('memory_gb', 'Unknown')} GB")
        
        return 0
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return 1

def cmd_test(args):
    """Run integration tests."""
    try:
        print("🧪 Running Enhanced JCVI Integration Tests...")
        
        # Import and run the test suite
        from test_enhanced_jcvi_integration import run_integration_tests
        success = run_integration_tests()
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return 1

def create_parser():
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="BioXen JCVI Enhanced CLI v0.0.03",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available genomes
  %(prog)s list
  
  # Acquire a specific genome  
  %(prog)s acquire mycoplasma_genitalium
  
  # Run complete comparative workflow
  %(prog)s workflow --genomes "mycoplasma_genitalium,mycoplasma_pneumoniae" --analysis synteny
  
  # Check integration status
  %(prog)s status
  
  # Run integration tests
  %(prog)s test
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List genomes command
    list_parser = subparsers.add_parser('list', help='List available genomes')
    list_parser.set_defaults(func=cmd_list_genomes)
    
    # Acquire genome command
    acquire_parser = subparsers.add_parser('acquire', help='Acquire specific genome')
    acquire_parser.add_argument('genome', help='Genome identifier to acquire')
    acquire_parser.add_argument('--output-dir', help='Output directory (default: genomes)')
    acquire_parser.set_defaults(func=cmd_acquire_genome)
    
    # Workflow command
    workflow_parser = subparsers.add_parser('workflow', help='Run complete workflow')
    workflow_parser.add_argument('--genomes', required=True, 
                                help='Comma-separated list of genome identifiers')
    workflow_parser.add_argument('--analysis', choices=['synteny', 'phylogenetic', 'comprehensive'],
                                default='synteny', help='Analysis type')
    workflow_parser.set_defaults(func=cmd_run_workflow)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show integration status')
    status_parser.set_defaults(func=cmd_status)
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run integration tests')
    test_parser.set_defaults(func=cmd_test)
    
    return parser

def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        return 1
    
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
