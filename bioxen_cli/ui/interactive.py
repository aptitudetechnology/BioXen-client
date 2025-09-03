import time


class InteractiveSession:
    """Handles interactive VM sessions."""
    
    def __init__(self, vm_manager):
        self.vm_manager = vm_manager

    def run_loop(self, vm_id):
        """Interactive loop for VM session"""
        try:
            while True:
                try:
                    user_input = input(f"lua[{vm_id}]> ")
                    
                    if user_input.strip() in ['exit', 'quit']:
                        break
                    
                    if user_input.strip():
                        self.vm_manager.send_input(vm_id, user_input + "\n")
                        time.sleep(0.1)
                        
                        # Read and display output
                        output = self.vm_manager.read_output(vm_id)
                        if output:
                            print(output.strip())
                            
                except KeyboardInterrupt:
                    print("\nUse 'exit' to detach from VM")
                except EOFError:
                    break
                    
        except Exception as e:
            print(f"Error in interactive loop: {e}")