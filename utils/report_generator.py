"""
Report Generator Utility
Generates validation reports in various formats
"""

import json
import csv
import io
from typing import Dict, Any, List
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        self.report_version = "1.0"
    
    def generate_json_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive JSON report"""
        try:
            report = {
                'report_metadata': {
                    'version': self.report_version,
                    'generated_at': datetime.now().isoformat(),
                    'report_type': 'vendorladon_validation'
                },
                'file_info': results.get('file_info', {}),
                'configuration': results.get('config', {}),
                'summary': results.get('summary', {}),
                'validation_results': results.get('validations', {}),
                'recommendations': self._generate_recommendations(results)
            }
            
            return json.dumps(report, indent=2, default=str)
            
        except Exception as e:
            error_report = {
                'error': f'Failed to generate JSON report: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
            return json.dumps(error_report, indent=2)
    
    def generate_csv_report(self, results: Dict[str, Any]) -> str:
        """Generate CSV report with validation details"""
        try:
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Validation Type',
                'Issue Type',
                'Segment',
                'Message',
                'Details',
                'Suggestion',
                'Severity'
            ])
            
            # Write validation results
            validations = results.get('validations', {})
            
            for validation_type, validation_result in validations.items():
                # Write errors
                for error in validation_result.get('errors', []):
                    writer.writerow([
                        validation_type.upper(),
                        'ERROR',
                        error.get('segment', ''),
                        error.get('message', ''),
                        error.get('details', ''),
                        error.get('suggestion', ''),
                        'High'
                    ])
                
                # Write warnings
                for warning in validation_result.get('warnings', []):
                    writer.writerow([
                        validation_type.upper(),
                        'WARNING',
                        warning.get('segment', ''),
                        warning.get('message', ''),
                        warning.get('details', ''),
                        warning.get('suggestion', ''),
                        'Medium'
                    ])
                
                # Write success entries
                if validation_result.get('success'):
                    writer.writerow([
                        validation_type.upper(),
                        'SUCCESS',
                        'ALL',
                        'Validation passed',
                        validation_result.get('details', 'All checks passed successfully'),
                        'No action required',
                        'Info'
                    ])
            
            # Add summary row
            writer.writerow([])  # Empty row
            writer.writerow(['SUMMARY', '', '', '', '', '', ''])
            writer.writerow([
                'Total Validations',
                '',
                '',
                str(results.get('summary', {}).get('total_validations', 0)),
                '',
                '',
                ''
            ])
            writer.writerow([
                'Total Errors',
                '',
                '',
                str(results.get('summary', {}).get('total_errors', 0)),
                '',
                '',
                ''
            ])
            writer.writerow([
                'Total Warnings',
                '',
                '',
                str(results.get('summary', {}).get('total_warnings', 0)),
                '',
                '',
                ''
            ])
            writer.writerow([
                'Ready to Submit',
                '',
                '',
                'Yes' if results.get('summary', {}).get('is_ready', False) else 'No',
                '',
                '',
                ''
            ])
            
            return output.getvalue()
            
        except Exception as e:
            return f"Error generating CSV report: {str(e)}"
    
    def generate_summary_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary report"""
        try:
            summary = results.get('summary', {})
            validations = results.get('validations', {})
            
            # Calculate validation statistics
            passed_validations = sum(1 for v in validations.values() if v.get('success'))
            failed_validations = len(validations) - passed_validations
            
            # Categorize issues by severity
            critical_issues = []
            warning_issues = []
            
            for validation_type, validation_result in validations.items():
                for error in validation_result.get('errors', []):
                    critical_issues.append({
                        'validation': validation_type,
                        'message': error.get('message', ''),
                        'segment': error.get('segment', '')
                    })
                
                for warning in validation_result.get('warnings', []):
                    warning_issues.append({
                        'validation': validation_type,
                        'message': warning.get('message', ''),
                        'segment': warning.get('segment', '')
                    })
            
            # Generate recommendations
            recommendations = self._generate_recommendations(results)
            
            return {
                'overall_status': 'READY' if summary.get('is_ready', False) else 'NOT_READY',
                'validation_statistics': {
                    'total_validations': summary.get('total_validations', 0),
                    'passed_validations': passed_validations,
                    'failed_validations': failed_validations,
                    'success_rate': f"{(passed_validations / len(validations) * 100):.1f}%" if validations else "0%"
                },
                'issue_summary': {
                    'critical_issues': len(critical_issues),
                    'warning_issues': len(warning_issues),
                    'total_issues': len(critical_issues) + len(warning_issues)
                },
                'top_critical_issues': critical_issues[:5],  # Top 5 critical issues
                'top_warnings': warning_issues[:5],  # Top 5 warnings
                'recommendations': recommendations,
                'next_steps': self._generate_next_steps(results)
            }
            
        except Exception as e:
            return {
                'error': f'Failed to generate summary report: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on validation results"""
        recommendations = []
        
        try:
            validations = results.get('validations', {})
            summary = results.get('summary', {})
            
            # Overall readiness recommendation
            if not summary.get('is_ready', False):
                recommendations.append({
                    'category': 'Critical',
                    'title': 'File Not Ready for Submission',
                    'description': 'Critical errors must be resolved before submitting ASN to Walmart',
                    'action': 'Review and fix all error-level issues highlighted in the validation results'
                })
            
            # Validation-specific recommendations
            for validation_type, validation_result in validations.items():
                errors = validation_result.get('errors', [])
                warnings = validation_result.get('warnings', [])
                
                if errors:
                    recommendations.append({
                        'category': 'Error',
                        'title': f'{validation_type.upper()} Issues Detected',
                        'description': f'Found {len(errors)} critical issues in {validation_type} validation',
                        'action': f'Review {validation_type} requirements and fix identified issues'
                    })
                
                if len(warnings) > 2:  # Multiple warnings in one area
                    recommendations.append({
                        'category': 'Warning',
                        'title': f'Multiple {validation_type.upper()} Warnings',
                        'description': f'Found {len(warnings)} warnings in {validation_type} validation',
                        'action': f'Consider addressing {validation_type} warnings to improve data quality'
                    })
            
            # Best practice recommendations
            if summary.get('total_warnings', 0) == 0 and summary.get('total_errors', 0) == 0:
                recommendations.append({
                    'category': 'Success',
                    'title': 'Excellent Data Quality',
                    'description': 'No issues detected in validation',
                    'action': 'File is ready for submission. Consider this as a quality template for future ASNs'
                })
            
            # Performance recommendations
            total_issues = summary.get('total_errors', 0) + summary.get('total_warnings', 0)
            if total_issues > 10:
                recommendations.append({
                    'category': 'Process',
                    'title': 'High Issue Count',
                    'description': f'Found {total_issues} total issues',
                    'action': 'Consider reviewing EDI generation process to reduce common errors'
                })
            
        except Exception:
            recommendations.append({
                'category': 'System',
                'title': 'Recommendation Generation Failed',
                'description': 'Unable to generate specific recommendations',
                'action': 'Review validation results manually for improvement opportunities'
            })
        
        return recommendations
    
    def _generate_next_steps(self, results: Dict[str, Any]) -> List[str]:
        """Generate next steps based on validation results"""
        next_steps = []
        
        try:
            summary = results.get('summary', {})
            
            if summary.get('is_ready', False):
                next_steps.extend([
                    "✅ Submit ASN to Walmart through your preferred EDI channel",
                    "📋 Keep validation report for your records",
                    "🔄 Monitor for acknowledgment from Walmart",
                    "📦 Proceed with shipment as scheduled"
                ])
            else:
                next_steps.extend([
                    "🔧 Fix all critical errors identified in the validation",
                    "📝 Update EDI file with corrections",
                    "🔍 Re-run validation to confirm fixes",
                    "✅ Submit once all errors are resolved"
                ])
                
                # Add specific next steps based on validation types with errors
                validations = results.get('validations', {})
                for validation_type, validation_result in validations.items():
                    if validation_result.get('errors'):
                        if validation_type == 'gstin':
                            next_steps.append("🏛️ Verify GSTIN with tax authorities if needed")
                        elif validation_type == 'products':
                            next_steps.append("📦 Confirm product codes in Walmart Retail Link")
                        elif validation_type == 'timing':
                            next_steps.append("⏰ Adjust shipment timing if necessary")
                        elif validation_type == 'certificates':
                            next_steps.append("🔐 Renew or update AS2 certificates")
        
        except Exception:
            next_steps.append("📋 Review validation results and address identified issues")
        
        return next_steps
