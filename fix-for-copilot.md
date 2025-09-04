# Fix Instructions for GitHub Copilot

## Runtime Error: BioXenRealGenomeIntegrator Missing Required Argument

**Error Location:** Line 66 in `interactive-bioxen-jcvi-api.py`

**Error Message:**
```
TypeError: BioXenRealGenomeIntegrator.__init__() missing 1 required positional argument: 'genome_path'
```

## Problem Analysis

The `BioXenRealGenomeIntegrator` class requires a `genome_path` parameter during initialization, but the current code attempts to create it without any arguments.

## Fix Option 1: Delayed Initialization (Recommended)

Change line 66 from:
```python
self.genome_integrator = BioXenRealGenomeIntegrator()
```

To:
```python
self.genome_integrator = None
```

Then add initialization when needed:
```python
def _ensure_genome_integrator(self, genome_path: str):
    """Initialize genome integrator when needed."""
    if self.genome_integrator is None:
        self.genome_integrator = BioXenRealGenomeIntegrator(genome_path)
```

## Fix Option 2: Default Genome Path

If you have a default genome file, initialize with it:
```python
self.genome_integrator = BioXenRealGenomeIntegrator("genomes/default.genome")
```

## Fix Option 3: Check Class Definition

First examine the `BioXenRealGenomeIntegrator` class to understand:
- What genome_path format it expects
- Whether it has optional parameters
- If there's a factory method available

## Additional Missing Initializations

The `__init__` method is also missing several required attributes:

```python
def __init__(self):
    # Existing code...
    
    # Add these missing initializations:
    self.chassis_type = ChassisType.ECOLI  # Default chassis
    self.selected_biological_type = "syn3a"  # Default biological type
    self.vm_type = "basic"  # Default VM type
    self.active_vms = {}  # Dictionary to store active VMs
    self.supported_bio_types = ["syn3a", "ecoli", "minimal_cell"]
    self.supported_vm_types = ["basic", "xcpng", "jcvi_optimized"]
    
    # Fix genome integrator (choose one option above)
    self.genome_integrator = None
```

## Missing Import

Add this import at the top:
```python
import os
```

## Missing Global Variable

Define this after imports:
```python
FACTORY_API_AVAILABLE = True  # Set based on successful imports
```

## Copilot Prompt Suggestions

Use these prompts with GitHub Copilot:

1. "Fix BioXenRealGenomeIntegrator initialization to handle missing genome_path argument"

2. "Add missing instance variable initializations in __init__ method for chassis_type, selected_biological_type, vm_type, active_vms"

3. "Implement delayed initialization pattern for genome integrator that requires genome_path"

4. "Add error handling for optional genome integrator initialization"

## Testing the Fix

After implementing the fix, test by running:
```bash
python3 interactive-bioxen-jcvi-api.py
```

The initialization should complete without the TypeError, and you should see the main menu.