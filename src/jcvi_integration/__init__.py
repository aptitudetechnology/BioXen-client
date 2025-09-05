"""
JCVI Integration Package

Enhanced JCVI integration with genome acquisition capabilities.
Addresses the gap between genome downloading and JCVI analysis workflows.

Components:
- genome_acquisition: JCVI-compatible genome downloading
- analysis_coordinator: Complete workflow coordination  
- acquisition_cli: Command-line interface for enhanced workflows

Version: 0.0.03 - JCVI Acquisition Integration
"""

from .genome_acquisition import JCVIGenomeAcquisition, GenomeAcquisitionRequest
from .analysis_coordinator import JCVIWorkflowCoordinator

__version__ = "0.0.03"
__all__ = [
    "JCVIGenomeAcquisition",
    "GenomeAcquisitionRequest", 
    "JCVIWorkflowCoordinator"
]
