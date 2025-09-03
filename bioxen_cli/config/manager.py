import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages configuration settings including XCP-ng credentials"""
    
    def __init__(self, config_file="bioxen_config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading config: {e}")
                return self.default_config()
        return self.default_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving config: {e}")
            return False
    
    def default_config(self):
        """Return default configuration for 0.1.22 (Phase 3)"""
        return {
            "xcpng": {
                "xapi_url": "https://192.168.1.100:443",
                "username": "root",
                "password": "",
                "template_name": "lua-bio-template",
                "vm_name_prefix": "bioxen-lua",
                "ssh_user": "root",
                "ssh_key_path": "",
                "pool_uuid": "",
                "network_uuid": "",
                "storage_repository": "",
                "save_credentials": False
            },
            "vm_defaults": {
                "profile": "standard",
                "networked": False,
                "persistent": True,
                "debug_mode": False
            },
            "xcpng_configs": {}
        }
    
    def get_xcpng_config(self):
        """Get XCP-ng configuration"""
        return self.config.get("xcpng", {})
    
    def get_xcpng_configs(self):
        """Get all saved XCP-ng configurations"""
        return self.config.get("xcpng_configs", {})
    
    def load_xcpng_file_config(self, file_path="xcpng_config.json"):
        """Load XCP-ng configuration from file (0.1.22 spec)"""
        config_file = Path(file_path)
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                    # Validate required keys
                    required_keys = ["xapi_url", "username", "password", "template_name"]
                    if all(key in file_config for key in required_keys):
                        return file_config
                    else:
                        print(f"⚠️ xcpng_config.json missing required keys: {required_keys}")
                        return None
            except Exception as e:
                print(f"⚠️ Error loading xcpng_config.json: {e}")
                return None
        return None
    
    def save_xcpng_config(self, config):
        """Save XCP-ng configuration with 0.1.20 format"""
        existing_configs = self.get_xcpng_configs()
        
        # Use host as the key
        config_key = config['xcp_host']
        existing_configs[config_key] = config
        
        self.config['xcpng_configs'] = existing_configs
        self.save_config()
        print(f"✅ XCP-ng configuration saved for {config_key}")
        print(f"🔧 Template: {config['template_name']}")
        print(f"👤 VM user: {config['vm_username']}")
        print("🔐 Credentials stored securely in config file")
    
    def get_vm_defaults(self):
        """Get VM default settings"""
        return self.config.get("vm_defaults", {})