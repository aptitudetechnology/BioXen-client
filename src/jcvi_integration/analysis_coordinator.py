#!/usr/bin/env python3
"""
JCVI Analysis Coordinator - v0.0.03

Coordinates complete workflows from genome acquisition to JCVI analysis.
Integrates with existing proven phase4_jcvi_cli_integration.py and download_genomes.py.

This module addresses the workflow gap identified in the specification by providing
end-to-end coordination between acquisition and analysis.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json

# Import existing proven infrastructure
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from .genome_acquisition import JCVIGenomeAcquisition, GenomeAcquisitionRequest

try:
    from phase4_jcvi_cli_integration import JCVICLIIntegrator
except ImportError:
    JCVICLIIntegrator = None

class JCVIWorkflowCoordinator:
    """
    Coordinates complete JCVI workflows from acquisition to analysis.
    
    This class bridges the gap between genome downloading and JCVI analysis
    by providing unified workflow coordination using existing proven components.
    """
    
    def __init__(self, work_dir: Optional[Path] = None):
        """
        Initialize workflow coordinator.
        
        Args:
            work_dir: Working directory for all workflow operations
        """
        self.work_dir = work_dir or Path("jcvi_complete_workflows")
        self.work_dir.mkdir(exist_ok=True)
        
        # Initialize components using existing infrastructure
        self.acquisition = JCVIGenomeAcquisition(self.work_dir / "genomes")
        
        # Initialize analysis component if available
        self.analysis_available = JCVICLIIntegrator is not None
        if self.analysis_available:
            try:
                self.analyzer = JCVICLIIntegrator()
            except Exception as e:
                print(f"Warning: JCVI CLI integrator initialization failed: {e}")
                self.analysis_available = False
                self.analyzer = None
        
        # Workflow tracking
        self.workflow_log = self.work_dir / "workflow_history.json"
        self.workflows = self._load_workflow_history()
        
        print(f"🔬 JCVI Workflow Coordinator initialized")
        print(f"   Work directory: {self.work_dir}")
        print(f"   Acquisition: ✅ Ready")
        print(f"   Analysis: {'✅ Ready' if self.analysis_available else '❌ Not Available'}")
    
    def run_complete_workflow(self, 
                            genome_identifiers: List[str],
                            analysis_type: str = 'synteny',
                            workflow_name: Optional[str] = None) -> Dict:
        """
        Run complete workflow from acquisition to analysis.
        
        Args:
            genome_identifiers: List of genome identifiers to acquire and analyze
            analysis_type: Type of analysis ('synteny', 'phylogenetic', 'comprehensive')
            workflow_name: Optional name for this workflow
            
        Returns:
            Complete workflow results
        """
        # Create workflow ID and tracking
        workflow_id = workflow_name or f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        workflow_result = {
            'workflow_id': workflow_id,
            'start_time': datetime.now().isoformat(),
            'genome_identifiers': genome_identifiers,
            'analysis_type': analysis_type,
            'status': 'running',
            'phases': {}
        }
        
        print(f"🚀 Starting workflow: {workflow_id}")
        print(f"   Genomes: {genome_identifiers}")
        print(f"   Analysis: {analysis_type}")
        
        try:
            # Phase 1: Genome Acquisition
            print(f"\n📥 Phase 1: Genome Acquisition")
            acquisition_results = self._run_acquisition_phase(genome_identifiers)
            workflow_result['phases']['acquisition'] = acquisition_results
            
            if acquisition_results['status'] != 'completed':
                workflow_result['status'] = 'failed'
                workflow_result['error'] = 'Acquisition phase failed'
                return workflow_result
            
            # Phase 2: Analysis Preparation
            print(f"\n🔧 Phase 2: Analysis Preparation")
            preparation_results = self._prepare_for_analysis(acquisition_results)
            workflow_result['phases']['preparation'] = preparation_results
            
            if preparation_results['status'] != 'completed':
                workflow_result['status'] = 'failed'
                workflow_result['error'] = 'Preparation phase failed'
                return workflow_result
            
            # Phase 3: JCVI Analysis (if available)
            if self.analysis_available:
                print(f"\n🧬 Phase 3: JCVI Analysis")
                analysis_results = self._run_analysis_phase(
                    preparation_results['prepared_genomes'], 
                    analysis_type
                )
                workflow_result['phases']['analysis'] = analysis_results
            else:
                print(f"\n⚠️  Phase 3: Analysis Skipped (JCVI CLI not available)")
                workflow_result['phases']['analysis'] = {
                    'status': 'skipped',
                    'reason': 'JCVI CLI integration not available'
                }
            
            # Phase 4: Results Integration
            print(f"\n📊 Phase 4: Results Integration")
            integration_results = self._integrate_results(workflow_result)
            workflow_result['phases']['integration'] = integration_results
            
            workflow_result['status'] = 'completed'
            workflow_result['end_time'] = datetime.now().isoformat()
            
            print(f"✅ Workflow completed: {workflow_id}")
            
        except Exception as e:
            workflow_result['status'] = 'failed'
            workflow_result['error'] = str(e)
            workflow_result['end_time'] = datetime.now().isoformat()
            print(f"❌ Workflow failed: {e}")
        
        # Save workflow result
        self.workflows[workflow_id] = workflow_result
        self._save_workflow_history()
        
        return workflow_result
    
    def _run_acquisition_phase(self, genome_identifiers: List[str]) -> Dict:
        """Run genome acquisition phase."""
        acquisition_results = {
            'status': 'running',
            'requested': len(genome_identifiers),
            'successful': 0,
            'failed': 0,
            'results': []
        }
        
        for identifier in genome_identifiers:
            print(f"  📥 Acquiring {identifier}...")
            
            request = GenomeAcquisitionRequest(
                identifier=identifier,
                jcvi_preparation=True,
                metadata_collection=True
            )
            
            result = self.acquisition.acquire_genome(request)
            acquisition_results['results'].append(result)
            
            if result['status'] == 'success':
                acquisition_results['successful'] += 1
                print(f"    ✅ Success")
            else:
                acquisition_results['failed'] += 1
                print(f"    ❌ Failed: {result.get('error', 'Unknown error')}")
        
        if acquisition_results['successful'] >= 2:
            acquisition_results['status'] = 'completed'
        else:
            acquisition_results['status'] = 'failed'
            acquisition_results['error'] = 'Need at least 2 genomes for comparative analysis'
        
        return acquisition_results
    
    def _prepare_for_analysis(self, acquisition_results: Dict) -> Dict:
        """Prepare acquired genomes for JCVI analysis."""
        preparation_results = {
            'status': 'running',
            'prepared_genomes': {},
            'preparation_notes': []
        }
        
        successful_acquisitions = [
            r for r in acquisition_results['results'] 
            if r['status'] == 'success'
        ]
        
        for acquisition in successful_acquisitions:
            identifier = acquisition['identifier']
            
            # Find JCVI-ready files
            jcvi_files = acquisition.get('jcvi_ready_files', [])
            if not jcvi_files:
                # Fallback to regular files
                jcvi_files = acquisition.get('files', [])
            
            if jcvi_files:
                # Use the first FASTA file found
                fasta_file = None
                for file_path in jcvi_files:
                    if Path(file_path).suffix.lower() in ['.fasta', '.fa', '.fna']:
                        fasta_file = Path(file_path)
                        break
                
                if fasta_file and fasta_file.exists():
                    preparation_results['prepared_genomes'][identifier] = {
                        'fasta_path': fasta_file,
                        'size_mb': fasta_file.stat().st_size / (1024 * 1024),
                        'metadata': acquisition.get('metadata', {}),
                        'source': 'acquired'
                    }
                    print(f"  🔧 Prepared {identifier} for analysis")
                else:
                    preparation_results['preparation_notes'].append(
                        f"No suitable FASTA file found for {identifier}"
                    )
            else:
                preparation_results['preparation_notes'].append(
                    f"No files available for {identifier}"
                )
        
        prepared_count = len(preparation_results['prepared_genomes'])
        if prepared_count >= 2:
            preparation_results['status'] = 'completed'
            print(f"  ✅ Prepared {prepared_count} genomes for analysis")
        else:
            preparation_results['status'] = 'failed'
            preparation_results['error'] = f'Only {prepared_count} genomes prepared, need at least 2'
        
        return preparation_results
    
    def _run_analysis_phase(self, prepared_genomes: Dict, analysis_type: str) -> Dict:
        """Run JCVI analysis phase using existing CLI integrator."""
        if not self.analyzer:
            return {
                'status': 'failed',
                'error': 'JCVI analyzer not available'
            }
        
        try:
            if analysis_type == 'synteny':
                result = self.analyzer.run_real_synteny_analysis(prepared_genomes)
            elif analysis_type == 'phylogenetic':
                result = self.analyzer.generate_phylogenetic_tree(prepared_genomes)
            elif analysis_type == 'comprehensive':
                # Run multiple analyses
                synteny_result = self.analyzer.run_real_synteny_analysis(prepared_genomes)
                phylo_result = self.analyzer.generate_phylogenetic_tree(prepared_genomes)
                
                result = {
                    'type': 'comprehensive',
                    'synteny': synteny_result,
                    'phylogenetic': phylo_result,
                    'status': 'completed'
                }
            else:
                return {
                    'status': 'failed',
                    'error': f'Unknown analysis type: {analysis_type}'
                }
            
            print(f"  ✅ {analysis_type.title()} analysis completed")
            return result
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': f'Analysis failed: {str(e)}'
            }
    
    def _integrate_results(self, workflow_result: Dict) -> Dict:
        """Integrate and summarize workflow results."""
        integration = {
            'status': 'completed',
            'summary': {},
            'output_files': [],
            'recommendations': []
        }
        
        # Summarize acquisition
        acquisition = workflow_result['phases'].get('acquisition', {})
        integration['summary']['acquisition'] = {
            'requested': acquisition.get('requested', 0),
            'successful': acquisition.get('successful', 0),
            'failed': acquisition.get('failed', 0)
        }
        
        # Summarize preparation
        preparation = workflow_result['phases'].get('preparation', {})
        integration['summary']['preparation'] = {
            'prepared_genomes': len(preparation.get('prepared_genomes', {}))
        }
        
        # Summarize analysis
        analysis = workflow_result['phases'].get('analysis', {})
        if analysis.get('status') == 'completed':
            integration['summary']['analysis'] = 'completed'
        elif analysis.get('status') == 'skipped':
            integration['summary']['analysis'] = 'skipped'
            integration['recommendations'].append(
                'Install JCVI CLI tools for analysis functionality'
            )
        else:
            integration['summary']['analysis'] = 'failed'
        
        # Collect output files
        for phase_name, phase_data in workflow_result['phases'].items():
            if isinstance(phase_data, dict) and 'output_files' in phase_data:
                integration['output_files'].extend(phase_data['output_files'])
        
        return integration
    
    def _load_workflow_history(self) -> Dict:
        """Load previous workflow history."""
        if self.workflow_log.exists():
            try:
                with open(self.workflow_log, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_workflow_history(self):
        """Save workflow history."""
        try:
            with open(self.workflow_log, 'w') as f:
                json.dump(self.workflows, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save workflow history: {e}")
    
    def list_workflows(self) -> List[Dict]:
        """List all previous workflows."""
        return list(self.workflows.values())
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        """Get specific workflow details."""
        return self.workflows.get(workflow_id)
    
    def get_status(self) -> Dict:
        """Get coordinator status."""
        return {
            'acquisition_ready': True,
            'analysis_ready': self.analysis_available,
            'workflow_count': len(self.workflows),
            'work_directory': str(self.work_dir)
        }

# Convenience functions for common workflows
def quick_comparative_genomics(genome_identifiers: List[str], 
                              work_dir: Optional[Path] = None) -> Dict:
    """Quick comparative genomics workflow."""
    coordinator = JCVIWorkflowCoordinator(work_dir)
    return coordinator.run_complete_workflow(
        genome_identifiers, 
        'comprehensive', 
        'quick_comparative'
    )

def synteny_analysis_workflow(genome_identifiers: List[str],
                             work_dir: Optional[Path] = None) -> Dict:
    """Synteny-focused analysis workflow."""
    coordinator = JCVIWorkflowCoordinator(work_dir)
    return coordinator.run_complete_workflow(
        genome_identifiers,
        'synteny',
        'synteny_analysis'
    )
