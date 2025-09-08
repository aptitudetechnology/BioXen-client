# Terminal DNA Transcription Monitor Integration Guide

## 🧬 Overview

The BioXen JCVI VM Library includes a comprehensive **Terminal DNA Transcription Monitor** that provides real-time visualization of biological VM operations, gene expression, and cellular processes. This guide shows how to integrate it into your client applications.

## 📦 Available Monitors

The library provides multiple monitor implementations:

### 1. **Enhanced Rich Monitor** (`terminal_biovis.py`)
- **Real-time DNA transcription visualization** with Rich library
- **Multi-VM support** with 2x2 grid layouts  
- **Live updating displays** of gene expression, ribosome activity, ATP levels
- **Professional terminal UI** with panels, tables, and progress bars

### 2. **Core Library Monitor** (`src/bioxen_jcvi_vm_lib/visualization/terminal_monitor.py`)
- **Hypervisor integration** for live VM monitoring
- **DNA activity visualization** with colored nucleotide sequences
- **ATP level tracking** and state monitoring
- **Table-based displays** of VM status

### 3. **Legacy Monitor** (`src/visualization/terminal_monitor.py`)
- **Basic terminal interface** for monitoring biological VMs
- **Simple DNA activity simulation**
- **ATP percentage displays**

## 🚀 Quick Integration

### Step 1: Install Dependencies

Ensure your client environment has the required packages:

```bash
pip install rich>=13.0.0
pip install bioxen-jcvi-vm-lib>=0.0.7
```

### Step 2: Basic Import

Add to your client script:

```python
# Enhanced Rich Monitor (Recommended)
from bioxen_jcvi_vm_lib.terminal_biovis import BioXenTerminalMonitor, run_dna_monitor

# OR Core Library Monitor
from bioxen_jcvi_vm_lib.visualization.terminal_monitor import TerminalMonitor
```

### Step 3: Simple Integration

```python
#!/usr/bin/env python3
"""
BioXen Client with DNA Transcription Monitor
"""

import threading
import time
from bioxen_jcvi_vm_lib.terminal_biovis import run_dna_monitor

class BioXenClient:
    def __init__(self):
        self.monitor_thread = None
        
    def start_dna_monitor(self):
        """Start DNA transcription monitor in background"""
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            print("🧬 Starting DNA Transcription Monitor...")
            self.monitor_thread = threading.Thread(
                target=run_dna_monitor,
                args=("bioxen_data.json", 2.0),
                daemon=True
            )
            self.monitor_thread.start()
            print("✅ DNA Monitor started! Check terminal output.")
        else:
            print("⚠️  DNA Monitor already running.")
```

## 🎮 Menu Integration

### Enhanced Main Menu

```python
def enhanced_main_menu():
    client = BioXenClient()
    
    while True:
        print("\n=== BioXen Factory API ===")
        print("1. Create Biological VM")
        print("2. Manage VMs")
        print("3. Run Workflows")
        print("4. 🧬 Start DNA Transcription Monitor")
        print("5. 🛑 Stop DNA Monitor")
        print("6. Exit")
        
        choice = input("Select option: ")
        
        if choice == "4":
            client.start_dna_monitor()
        elif choice == "5":
            client.stop_dna_monitor()
        elif choice == "6":
            print("Goodbye!")
            break
        # Handle other menu options...
```

## 📊 Data Integration

### Monitor Data Format

Create a data file (`bioxen_data.json`) or generate data dynamically:

```python
import json
from datetime import datetime

def generate_monitor_data(hypervisor):
    """Generate data for DNA transcription monitor"""
    data = {
        "system": {
            "chassis_type": "E_coli_MG1655",
            "total_ribosomes": 80,
            "available_ribosomes": 60,
            "timestamp": datetime.now().isoformat(),
            "atp_pool": 85
        },
        "vms": {}
    }
    
    # Populate VM data from hypervisor
    for vm_id, vm in hypervisor.vms.items():
        data["vms"][vm_id] = {
            "vm_id": vm_id,
            "atp_percentage": vm.get_atp_level(),
            "ribosomes": vm.get_ribosome_count(),
            "active_genes": vm.get_active_gene_count(),
            "protein_count": vm.get_protein_count(),
            "mrna_count": vm.get_mrna_count(),
            "gene_expression_rate": vm.get_expression_rate(),
            "ribosome_utilization": vm.get_ribosome_utilization()
        }
    
    # Save to file for monitor
    with open("bioxen_data.json", "w") as f:
        json.dump(data, f, indent=2)
    
    return data
```

### Mock Data for Testing

```python
def generate_mock_data():
    """Generate mock data for testing"""
    import random
    
    return {
        "system": {
            "chassis_type": "E_coli_MG1655",
            "total_ribosomes": 80,
            "available_ribosomes": random.randint(20, 60),
            "timestamp": datetime.now().isoformat(),
            "atp_pool": random.randint(60, 95)
        },
        "vms": {
            f"vm_{i}": {
                "vm_id": f"vm_{i}",
                "atp_percentage": random.randint(50, 95),
                "ribosomes": random.randint(5, 25),
                "active_genes": random.randint(3, 15),
                "protein_count": random.randint(20, 80),
                "mrna_count": random.randint(2, 12),
                "gene_expression_rate": random.randint(20, 90),
                "ribosome_utilization": random.randint(40, 95)
            } for i in range(1, 5)
        }
    }
```

## 🔧 Advanced Integration Options

### Option 1: Direct Monitor Instance

```python
from bioxen_jcvi_vm_lib.terminal_biovis import BioXenTerminalMonitor

def start_custom_monitor():
    """Start monitor with custom configuration"""
    monitor = BioXenTerminalMonitor("bioxen_data.json")
    monitor.run(refresh_rate=1.5)  # Custom refresh rate
```

### Option 2: Hypervisor Integration

```python
from bioxen_jcvi_vm_lib.visualization.terminal_monitor import TerminalMonitor

def setup_hypervisor_monitor(hypervisor):
    """Integrate monitor with hypervisor"""
    monitor = TerminalMonitor(hypervisor)
    
    try:
        monitor.start()
        while True:
            monitor.display()
            time.sleep(2)
    except KeyboardInterrupt:
        monitor.stop()
```

### Option 3: Background Monitoring

```python
import threading
import signal
import sys

class MonitorManager:
    def __init__(self):
        self.monitor_thread = None
        self.running = False
        
    def start_background_monitor(self):
        """Start monitor in background with proper cleanup"""
        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()
        
        # Setup signal handlers for cleanup
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _monitor_loop(self):
        """Monitor loop with error handling"""
        try:
            run_dna_monitor("bioxen_data.json", 2.0)
        except Exception as e:
            print(f"Monitor error: {e}")
            
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.running = False
        print("\n🛑 Shutting down DNA Monitor...")
        sys.exit(0)
        
    def stop(self):
        """Stop background monitor"""
        self.running = False
```

## 🎯 Complete Client Example

```python
#!/usr/bin/env python3
"""
Complete BioXen Client with DNA Transcription Monitor
"""

import json
import time
import threading
from datetime import datetime
from bioxen_jcvi_vm_lib.terminal_biovis import run_dna_monitor
from bioxen_jcvi_vm_lib.core.factory import BiologicalVMFactory

class EnhancedBioXenClient:
    def __init__(self):
        self.factory = BiologicalVMFactory()
        self.hypervisor = None
        self.monitor_thread = None
        
    def initialize(self):
        """Initialize the client"""
        print("🚀 Initializing BioXen Client...")
        self.hypervisor = self.factory.create_hypervisor()
        
    def start_dna_monitor(self):
        """Start DNA transcription monitor"""
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            print("🧬 Starting DNA Transcription Monitor...")
            
            # Generate initial data
            self.update_monitor_data()
            
            self.monitor_thread = threading.Thread(
                target=run_dna_monitor,
                args=("bioxen_data.json", 2.0),
                daemon=True
            )
            self.monitor_thread.start()
            print("✅ DNA Monitor started!")
        else:
            print("⚠️  DNA Monitor already running.")
            
    def update_monitor_data(self):
        """Update data for monitor"""
        if self.hypervisor:
            data = self.generate_real_data()
        else:
            data = self.generate_mock_data()
            
        with open("bioxen_data.json", "w") as f:
            json.dump(data, f, indent=2)
            
    def generate_real_data(self):
        """Generate real data from hypervisor"""
        # Implementation depends on your hypervisor API
        pass
        
    def generate_mock_data(self):
        """Generate mock data for demonstration"""
        import random
        return {
            "system": {
                "chassis_type": "E_coli_MG1655",
                "total_ribosomes": 80,
                "available_ribosomes": random.randint(20, 60),
                "timestamp": datetime.now().isoformat(),
                "atp_pool": random.randint(60, 95)
            },
            "vms": {
                f"vm_{i}": {
                    "vm_id": f"vm_{i}",
                    "atp_percentage": random.randint(50, 95),
                    "ribosomes": random.randint(5, 25),
                    "active_genes": random.randint(3, 15),
                    "protein_count": random.randint(20, 80),
                    "mrna_count": random.randint(2, 12),
                    "gene_expression_rate": random.randint(20, 90),
                    "ribosome_utilization": random.randint(40, 95)
                } for i in range(1, 4)
            }
        }
        
    def run(self):
        """Main application loop"""
        self.initialize()
        
        while True:
            print("\n=== Enhanced BioXen Factory API ===")
            print("1. Create Biological VM")
            print("2. Manage VMs")
            print("3. Run Workflows")
            print("4. 🧬 Start DNA Transcription Monitor")
            print("5. 📊 Update Monitor Data")
            print("6. Exit")
            
            choice = input("Select option: ")
            
            if choice == "1":
                self.create_vm()
            elif choice == "2":
                self.manage_vms()
            elif choice == "3":
                self.run_workflows()
            elif choice == "4":
                self.start_dna_monitor()
            elif choice == "5":
                self.update_monitor_data()
                print("✅ Monitor data updated.")
            elif choice == "6":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    client = EnhancedBioXenClient()
    try:
        client.run()
    except KeyboardInterrupt:
        print("\n🛑 Application terminated by user.")
```

## 🔍 Monitor Features

### Real-time Visualization
- **DNA strand visualization** with transcription bubbles
- **Ribosome activity bars** showing utilization
- **ATP level indicators** with color coding
- **Gene expression rates** and active gene counts
- **System overview** with chassis type and resource pools

### Multi-VM Support
- **2x2 grid layout** for up to 4 VMs simultaneously
- **Individual VM panels** with detailed metrics
- **System-wide resource tracking**
- **Live updating displays** with configurable refresh rates

### Professional UI
- **Rich terminal library** for enhanced visuals
- **Color-coded metrics** for quick status assessment
- **Progress bars and indicators**
- **Panel-based layout** with clear organization

## 🛠️ Troubleshooting

### Common Issues

1. **Monitor not starting**
   ```python
   # Check if Rich is installed
   pip install rich>=13.0.0
   
   # Verify data file exists
   import os
   if not os.path.exists("bioxen_data.json"):
       print("Creating mock data file...")
       generate_mock_data()
   ```

2. **Monitor crashing**
   ```python
   # Add error handling
   try:
       run_dna_monitor("bioxen_data.json", 2.0)
   except Exception as e:
       print(f"Monitor error: {e}")
   ```

3. **No data displayed**
   ```python
   # Verify data format
   with open("bioxen_data.json", "r") as f:
       data = json.load(f)
       print(f"VMs found: {len(data.get('vms', {}))}")
   ```

## 📚 Additional Resources

- **Library Documentation**: See `src/bioxen_jcvi_vm_lib/visualization/`
- **Rich Library Docs**: https://rich.readthedocs.io/
- **Example Implementation**: `terminal_biovis.py`
- **Core Monitor**: `src/bioxen_jcvi_vm_lib/visualization/terminal_monitor.py`

## 🎯 Next Steps

1. **Copy the integration code** into your client script
2. **Test with mock data** to verify the monitor works
3. **Connect to real hypervisor data** for live monitoring
4. **Customize refresh rates** and display options as needed
5. **Add error handling** for production use

The Terminal DNA Transcription Monitor is **ready to use** and provides a professional interface for monitoring biological VM operations in real-time!