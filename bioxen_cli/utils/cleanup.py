def cleanup_handler(vm_manager, vm_tracker):
    """Cleanup resources before exit."""
    print("\n🧹 Cleaning up running VMs...")
    for vm_id in list(vm_tracker.vm_status.keys()):
        if vm_tracker.vm_status[vm_id].running:
            try:
                vm_manager.terminate_vm_session(vm_id)
                print(f"✅ VM {vm_id} terminated")
            except Exception as e:
                print(f"⚠️  Could not terminate VM {vm_id}: {e}")
    vm_tracker.vm_status.clear()