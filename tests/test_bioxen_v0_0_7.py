#!/usr/bin/env python3
"""
BioXen JCVI VM Library v0.0.07 Comprehensive Test Suite
Tests all claims made in specification-document-bioxen_jcvi_vm_lib_ver0.0.07.md

This test validates:
- Package import functionality (100% success claimed)
- Factory Pattern API (fully functional claimed)
- CLI integration (all commands working claimed)
- VM creation and management (operational claimed)
- Enhanced error handling (production-grade claimed)
- Production configuration (working claimed)
- All documented features claimed to be "FULLY FUNCTIONAL"
"""

import sys
import traceback
import subprocess
from pathlib import Path

# Test configuration
TEST_VM_ID = "test_vm_v0_0_7"
TEST_BIOLOGICAL_TYPE = "syn3a"
TEST_VM_TYPE = "basic"

class TestResult:
    def __init__(self, test_name):
        self.test_name = test_name
        self.success = False
        self.error = None
        self.details = None

    def mark_success(self, details=None):
        self.success = True
        self.details = details
        print(f"✅ {self.test_name}: PASSED")
        if details:
            print(f"   Details: {details}")

    def mark_failure(self, error):
        self.success = False
        self.error = str(error)
        print(f"❌ {self.test_name}: FAILED")
        print(f"   Error: {self.error}")

def run_test_suite():
    """Run comprehensive test suite for BioXen v0.0.07"""
    print("="*80)
    print("🧬 BioXen JCVI VM Library v0.0.07 Comprehensive Test Suite")
    print("   Testing claims from specification-document-bioxen_jcvi_vm_lib_ver0.0.07.md")
    print("="*80)

    results = []

    # Test 1: Basic Package Import (Claimed 100% success)
    test1 = TestResult("Basic Package Import")
    try:
        import bioxen_jcvi_vm_lib
        version = getattr(bioxen_jcvi_vm_lib, '__version__', getattr(bioxen_jcvi_vm_lib, 'get_version', lambda: 'Unknown')())
        test1.mark_success(f"Package imported successfully, version: {version}")
        results.append(test1)
    except Exception as e:
        test1.mark_failure(e)
        results.append(test1)
        print("\n🚨 CRITICAL: Basic package import failed. Cannot continue with API tests.")
        print("   This indicates v0.0.07 fixes were not successfully applied.")
        return results

    # Test 2: Factory API Import (Claimed fully functional)
    test2 = TestResult("Factory API Import")
    try:
        from bioxen_jcvi_vm_lib.api import create_bio_vm
        test2.mark_success("create_bio_vm imported successfully")
        results.append(test2)
    except Exception as e:
        test2.mark_failure(e)
        results.append(test2)

    # Test 3: Direct Factory Import (Claimed working)
    test3 = TestResult("Direct Factory Import")
    try:
        from bioxen_jcvi_vm_lib.api.factory import create_bio_vm
        test3.mark_success("Direct factory import successful")
        results.append(test3)
    except Exception as e:
        test3.mark_failure(e)
        results.append(test3)

    # Test 4: Compatibility Alias Import (Claimed working)
    test4 = TestResult("Compatibility Alias Import")
    try:
        from bioxen_jcvi_vm_lib import create_vm
        test4.mark_success("create_vm alias imported successfully")
        results.append(test4)
    except Exception as e:
        test4.mark_failure(e)
        results.append(test4)

    # Test 5: Enhanced Error Handling Import (Claimed production-grade)
    test5 = TestResult("Enhanced Error Handling Import")
    try:
        from bioxen_jcvi_vm_lib.api.enhanced_error_handling import BioXenErrorCode
        test5.mark_success("BioXenErrorCode imported successfully")
        results.append(test5)
    except Exception as e:
        test5.mark_failure(e)
        results.append(test5)

    # Test 6: Production Config Import (Claimed working)
    test6 = TestResult("Production Config Import")
    try:
        from bioxen_jcvi_vm_lib.api.production_config import ProductionConfigManager
        test6.mark_success("ProductionConfigManager imported successfully")
        results.append(test6)
    except Exception as e:
        test6.mark_failure(e)
        results.append(test6)

    # Test 7: Utility Functions Import (Claimed working)
    test7 = TestResult("Utility Functions Import")
    try:
        from bioxen_jcvi_vm_lib import get_supported_biological_types, get_supported_vm_types
        test7.mark_success("Utility functions imported successfully")
        results.append(test7)
    except Exception as e:
        test7.mark_failure(e)
        results.append(test7)

    # Test 8: Supported Types Query (Claimed working)
    test8 = TestResult("Supported Types Query")
    try:
        bio_types = get_supported_biological_types()
        vm_types = get_supported_vm_types()
        test8.mark_success(f"Bio types: {bio_types}, VM types: {vm_types}")
        results.append(test8)
    except Exception as e:
        test8.mark_failure(e)
        results.append(test8)

    # Test 9: VM Creation via Factory API (Claimed operational)
    test9 = TestResult("VM Creation via Factory API")
    try:
        vm = create_bio_vm(TEST_VM_ID, TEST_BIOLOGICAL_TYPE, TEST_VM_TYPE)
        vm_type = vm.get_vm_type() if hasattr(vm, 'get_vm_type') else 'Unknown'
        bio_type = vm.get_biological_type() if hasattr(vm, 'get_biological_type') else 'Unknown'
        test9.mark_success(f"VM created: {vm_type}/{bio_type}")
        results.append(test9)

        # Store VM for subsequent tests
        test_vm = vm
    except Exception as e:
        test9.mark_failure(e)
        results.append(test9)
        test_vm = None

    # Test 10: VM Operations (Claimed working)
    test10 = TestResult("VM Operations")
    if test_vm:
        try:
            start_result = test_vm.start() if hasattr(test_vm, 'start') else False
            status = test_vm.get_status() if hasattr(test_vm, 'get_status') else {}
            test10.mark_success(f"Start: {start_result}, Status: {status.get('status', 'Unknown')}")
            results.append(test10)
        except Exception as e:
            test10.mark_failure(e)
            results.append(test10)
    else:
        test10.mark_failure("VM creation failed, cannot test operations")
        results.append(test10)

    # Test 11: Resource Management (Claimed operational)
    test11 = TestResult("Resource Management")
    if test_vm:
        try:
            alloc_result = test_vm.allocate_resources({"atp": 50.0, "ribosomes": 10}) if hasattr(test_vm, 'allocate_resources') else False
            usage = test_vm.get_resource_usage() if hasattr(test_vm, 'get_resource_usage') else {}
            test11.mark_success(f"Allocation: {alloc_result}, Usage: {usage}")
            results.append(test11)
        except Exception as e:
            test11.mark_failure(e)
            results.append(test11)
    else:
        test11.mark_failure("VM creation failed, cannot test resource management")
        results.append(test11)

    # Test 12: CLI Module Import (Claimed working)
    test12 = TestResult("CLI Module Import")
    try:
        from bioxen_jcvi_vm_lib.cli import main
        test12.mark_success("CLI module imported successfully")
        results.append(test12)
    except Exception as e:
        test12.mark_failure(e)
        results.append(test12)

    # Test 13: CLI Entry Point Test (Claimed all commands working)
    test13 = TestResult("CLI Entry Point")
    try:
        result = subprocess.run(['bioxen', '--help'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            test13.mark_success("CLI command executed successfully")
        else:
            test13.mark_failure(f"CLI failed with code {result.returncode}: {result.stderr}")
        results.append(test13)
    except FileNotFoundError:
        test13.mark_failure("CLI command 'bioxen' not found")
        results.append(test13)
    except subprocess.TimeoutExpired:
        test13.mark_failure("CLI command timed out")
        results.append(test13)
    except Exception as e:
        test13.mark_failure(e)
        results.append(test13)

    # Test 14: BiologicalVM Interface (Claimed working)
    test14 = TestResult("BiologicalVM Interface")
    try:
        from bioxen_jcvi_vm_lib.api.biological_vm import BiologicalVM
        interface_methods = [method for method in dir(BiologicalVM) if not method.startswith('_')]
        test14.mark_success(f"Interface available with {len(interface_methods)} methods")
        results.append(test14)
    except Exception as e:
        test14.mark_failure(e)
        results.append(test14)

    # Test 15: Resource Manager Instantiation (Claimed operational)
    test15 = TestResult("Resource Manager Instantiation")
    try:
        from bioxen_jcvi_vm_lib.api import BioResourceManager
        manager = BioResourceManager()
        manager_methods = [method for method in dir(manager) if not method.startswith('_')]
        test15.mark_success(f"Resource manager created with {len(manager_methods)} methods")
        results.append(test15)
    except Exception as e:
        test15.mark_failure(e)
        results.append(test15)

    # Test 16: Specification Claims Validation (Claimed 100% success rate)
    test16 = TestResult("Specification Claims Validation")
    try:
        claims_validated = 0
        total_claims = 7

        # Claim 1: Package Import Fixed (100% success claimed)
        if any(r.test_name == "Basic Package Import" and r.success for r in results):
            claims_validated += 1

        # Claim 2: Factory API Fully Functional
        if any(r.test_name == "Factory API Import" and r.success for r in results):
            claims_validated += 1

        # Claim 3: CLI Integration Complete
        if any(r.test_name == "CLI Entry Point" and r.success for r in results):
            claims_validated += 1

        # Claim 4: VM Creation Operational
        if any(r.test_name == "VM Creation via Factory API" and r.success for r in results):
            claims_validated += 1

        # Claim 5: Enhanced Error Handling Working
        if any(r.test_name == "Enhanced Error Handling Import" and r.success for r in results):
            claims_validated += 1

        # Claim 6: Production Config Working
        if any(r.test_name == "Production Config Import" and r.success for r in results):
            claims_validated += 1

        # Claim 7: 100% Test Success Rate
        if len([r for r in results if r.success]) == len(results):
            claims_validated += 1

        test16.mark_success(f"{claims_validated}/{total_claims} specification claims validated")
        results.append(test16)
    except Exception as e:
        test16.mark_failure(e)
        results.append(test16)

    return results

def print_summary(results):
    """Print test summary"""
    print("\n" + "="*80)
    print("📊 Test Summary")
    print("="*80)

    passed = len([r for r in results if r.success])
    failed = len([r for r in results if not r.success])
    total = len(results)

    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")

    if failed > 0:
        print(f"\n🚨 Failed Tests:")
        for result in results:
            if not result.success:
                print(f"   • {result.test_name}: {result.error}")

    print(f"\n💡 Analysis:")
    if passed == total:
        print("   🎉 ALL TESTS PASSED! v0.0.07 claims are validated.")
        print("   ✅ The specification-document-bioxen_jcvi_vm_lib_ver0.0.07.md is accurate.")
        print("   ✅ Library is ready for production use.")
        print("   ✅ 100% success rate achieved as claimed.")
    elif passed >= total * 0.8:
        print("   ⚠️ MOSTLY WORKING: Most features functional with minor issues.")
        print("   🔧 Some specification claims need additional work.")
    elif passed >= total * 0.5:
        print("   ⚠️ PARTIALLY WORKING: Some core features working, others broken.")
        print("   🚨 Significant gaps between specification and implementation.")
    else:
        print("   🚨 MOSTLY BROKEN: Major implementation issues remain.")
        print("   ❌ Specification claims not validated by implementation.")
        print("   🔧 Recommend continuing with working alternatives.")

def main():
    """Main test execution"""
    try:
        results = run_test_suite()
        print_summary(results)

        # Exit with appropriate code
        failed = len([r for r in results if not r.success])
        sys.exit(0 if failed == 0 else 1)

    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n🚨 Test suite crashed: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
    test2 = TestResult("Package Version Verification")
    try:
        version = getattr(bioxen_jcvi_vm_lib, '__version__', 'Unknown')
        if version == 'Unknown':
            # Try alternative version detection
            import pkg_resources
            version = pkg_resources.get_distribution('bioxen_jcvi_vm_lib').version
        test2.mark_success(f"Version: {version}")
        results.append(test2)
    except Exception as e:
        test2.mark_failure(e)
        results.append(test2)

    # Test 3: Factory API Import
    test3 = TestResult("Factory API Import")
    try:
        from bioxen_jcvi_vm_lib.api import create_bio_vm
        test3.mark_success("create_bio_vm imported successfully")
        results.append(test3)
    except Exception as e:
        test3.mark_failure(e)
        results.append(test3)

    # Test 4: Secondary Factory Imports
    test4 = TestResult("Secondary Factory API Imports")
    try:
        from bioxen_jcvi_vm_lib.api import (
            BioResourceManager,
            get_supported_biological_types,
            get_supported_vm_types
        )
        test4.mark_success("All secondary factory imports successful")
        results.append(test4)
    except Exception as e:
        test4.mark_failure(e)
        results.append(test4)

    # Test 5: Compatibility Alias Import
    test5 = TestResult("Compatibility Alias Import")
    try:
        from bioxen_jcvi_vm_lib import create_vm
        test5.mark_success("create_vm alias imported successfully")
        results.append(test5)
    except Exception as e:
        test5.mark_failure(e)
        results.append(test5)

    # Test 6: Enhanced Error Handling Import
    test6 = TestResult("Enhanced Error Handling Import")
    try:
        from bioxen_jcvi_vm_lib.api.enhanced_error_handling import BioXenErrorCode
        test6.mark_success("BioXenErrorCode imported successfully")
        results.append(test6)
    except Exception as e:
        test6.mark_failure(e)
        results.append(test6)

    # Test 7: Production Config Import
    test7 = TestResult("Production Config Import")
    try:
        from bioxen_jcvi_vm_lib.api.production_config import ProductionConfigManager
        test7.mark_success("ProductionConfigManager imported successfully")
        results.append(test7)
    except Exception as e:
        test7.mark_failure(e)
        results.append(test7)

    # Test 8: Supported Types Query
    test8 = TestResult("Supported Types Query")
    try:
        bio_types = get_supported_biological_types()
        vm_types = get_supported_vm_types()
        test8.mark_success(f"Bio types: {bio_types}, VM types: {vm_types}")
        results.append(test8)
    except Exception as e:
        test8.mark_failure(e)
        results.append(test8)

    # Test 9: VM Creation
    test9 = TestResult("VM Creation via Factory API")
    try:
        vm = create_bio_vm(TEST_VM_ID, TEST_BIOLOGICAL_TYPE, TEST_VM_TYPE)
        vm_type = vm.get_vm_type() if hasattr(vm, 'get_vm_type') else 'Unknown'
        bio_type = vm.get_biological_type() if hasattr(vm, 'get_biological_type') else 'Unknown'
        test9.mark_success(f"VM created: {vm_type}/{bio_type}")
        results.append(test9)
        
        # Store VM for subsequent tests
        test_vm = vm
    except Exception as e:
        test9.mark_failure(e)
        results.append(test9)
        test_vm = None

    # Test 10: VM Operations (if VM was created)
    test10 = TestResult("VM Operations")
    if test_vm:
        try:
            start_result = test_vm.start() if hasattr(test_vm, 'start') else False
            status = test_vm.get_status() if hasattr(test_vm, 'get_status') else {}
            test10.mark_success(f"Start: {start_result}, Status: {status.get('status', 'Unknown')}")
            results.append(test10)
        except Exception as e:
            test10.mark_failure(e)
            results.append(test10)
    else:
        test10.mark_failure("VM creation failed, cannot test operations")
        results.append(test10)

    # Test 11: Resource Management
    test11 = TestResult("Resource Management")
    if test_vm:
        try:
            alloc_result = test_vm.allocate_resources({"atp": 50.0, "ribosomes": 10}) if hasattr(test_vm, 'allocate_resources') else False
            usage = test_vm.get_resource_usage() if hasattr(test_vm, 'get_resource_usage') else {}
            test11.mark_success(f"Allocation: {alloc_result}, Usage: {usage}")
            results.append(test11)
        except Exception as e:
            test11.mark_failure(e)
            results.append(test11)
    else:
        test11.mark_failure("VM creation failed, cannot test resource management")
        results.append(test11)

    # Test 12: BiologicalVM Interface
    test12 = TestResult("BiologicalVM Interface")
    try:
        from bioxen_jcvi_vm_lib.api.biological_vm import BiologicalVM
        interface_methods = [method for method in dir(BiologicalVM) if not method.startswith('_')]
        test12.mark_success(f"Interface available with {len(interface_methods)} methods")
        results.append(test12)
    except Exception as e:
        test12.mark_failure(e)
        results.append(test12)

    # Test 13: CLI Entry Point Test
    test13 = TestResult("CLI Entry Point")
    try:
        result = subprocess.run(['bioxen', '--help'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            test13.mark_success("CLI command executed successfully")
        else:
            test13.mark_failure(f"CLI failed with code {result.returncode}: {result.stderr}")
        results.append(test13)
    except FileNotFoundError:
        test13.mark_failure("CLI command 'bioxen' not found")
        results.append(test13)
    except subprocess.TimeoutExpired:
        test13.mark_failure("CLI command timed out")
        results.append(test13)
    except Exception as e:
        test13.mark_failure(e)
        results.append(test13)

    # Test 14: Resource Manager Instantiation
    test14 = TestResult("Resource Manager Instantiation")
    try:
        manager = BioResourceManager()
        manager_methods = [method for method in dir(manager) if not method.startswith('_')]
        test14.mark_success(f"Resource manager created with {len(manager_methods)} methods")
        results.append(test14)
    except Exception as e:
        test14.mark_failure(e)
        results.append(test14)

    # Test 15: Specification Validation
    test15 = TestResult("Specification Claims Validation")
    try:
        claims_validated = 0
        total_claims = 6
        
        # Claim 1: Package Structure Fixed
        if any(r.test_name == "Basic Package Import" and r.success for r in results):
            claims_validated += 1
            
        # Claim 2: Import Paths Fixed  
        if any(r.test_name == "Factory API Import" and r.success for r in results):
            claims_validated += 1
            
        # Claim 3: CLI Entry Points Fixed
        if any(r.test_name == "CLI Entry Point" and r.success for r in results):
            claims_validated += 1
            
        # Claim 4: Factory API Importable
        if any(r.test_name == "Secondary Factory API Imports" and r.success for r in results):
            claims_validated += 1
            
        # Claim 5: Package Initialization Fixed
        if any(r.test_name == "Compatibility Alias Import" and r.success for r in results):
            claims_validated += 1
            
        # Claim 6: Enhanced Features Available
        if any(r.test_name == "Enhanced Error Handling Import" and r.success for r in results):
            claims_validated += 1
            
        test15.mark_success(f"{claims_validated}/{total_claims} specification claims validated")
        results.append(test15)
    except Exception as e:
        test15.mark_failure(e)
        results.append(test15)

    return results

def print_summary(results):
    """Print test summary"""
    print("\n" + "="*80)
    print("📊 Test Summary")
    print("="*80)
    
    passed = len([r for r in results if r.success])
    failed = len([r for r in results if not r.success])
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if failed > 0:
        print(f"\n🚨 Failed Tests:")
        for result in results:
            if not result.success:
                print(f"   • {result.test_name}: {result.error}")
    
    print(f"\n💡 Analysis:")
    if passed == total:
        print("   🎉 ALL TESTS PASSED! v0.0.06.1 claims are validated.")
        print("   ✅ The specification-document-bioxen_jcvi_vm_lib_ver0.0.06.1.md is accurate.")
        print("   ✅ Library is ready for production use.")
    elif passed >= total * 0.8:
        print("   ⚠️ MOSTLY WORKING: Most features functional with minor issues.")
        print("   🔧 Some specification claims need additional work.")
    elif passed >= total * 0.5:
        print("   ⚠️ PARTIALLY WORKING: Some core features working, others broken.")
        print("   🚨 Significant gaps between specification and implementation.")
    else:
        print("   🚨 MOSTLY BROKEN: Major implementation issues remain.")
        print("   ❌ Specification claims not validated by implementation.")
        print("   🔧 Recommend continuing with working alternatives.")

def main():
    """Main test execution"""
    try:
        results = run_test_suite()
        print_summary(results)
        
        # Exit with appropriate code
        failed = len([r for r in results if not r.success])
        sys.exit(0 if failed == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n🚨 Test suite crashed: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
