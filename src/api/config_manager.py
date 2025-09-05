from typing import Dict, Any, Optional
import json
import os

class ConfigManager:
    """
    Configuration management for biological VMs.
    Mirrors pylua configuration patterns.
    """
    
    @staticmethod
    def load_defaults(biological_type: str) -> Dict[str, Any]:
        """Load default configuration for biological type."""
        default_configs = {
            "syn3a": {
                "resource_limits": {
                    "max_atp": 70.0,
                    "max_ribosomes": 15
                },
                "genome_optimization": True,
                "minimal_mode": True
            },
            "ecoli": {
                "resource_limits": {
                    "max_atp": 90.0,
                    "max_ribosomes": 30
                },
                "operon_management": True,
                "plasmid_support": True
            },
            "minimal_cell": {
                "resource_limits": {
                    "max_atp": 60.0,
                    "max_ribosomes": 12
                },
                "basic_functions_only": True,
                "function_validation": True
            }
        }
        return default_configs.get(biological_type, {})
    
    @staticmethod
    def load_from_file(config_path: str) -> Dict[str, Any]:
        """Load configuration from file - mirrors pylua file loading."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def validate_config(config: Dict[str, Any], vm_type: str) -> bool:
        """Validate configuration for VM type."""
        if vm_type == "xcpng":
            return ConfigManager._validate_xcpng_config(config)
        elif vm_type == "basic":
            return ConfigManager._validate_basic_config(config)
        return False
    
    @staticmethod
    def _validate_xcpng_config(config: Dict[str, Any]) -> bool:
        """Validate XCP-ng specific configuration."""
        xcpng_config = config.get('xcpng_config', {})
        required_fields = ['xapi_url', 'username', 'password', 'ssh_user']
        return all(field in xcpng_config for field in required_fields)
    
    @staticmethod
    def _validate_basic_config(config: Dict[str, Any]) -> bool:
        """Validate basic VM configuration."""
        # Basic VMs have minimal config requirements
        return True
    
    @staticmethod
    def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge configurations with override priority."""
        merged = base_config.copy()
        merged.update(override_config)
        return merged
