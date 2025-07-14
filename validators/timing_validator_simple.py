"""
Simple Timing Validator for GlitchGuard
"""
from typing import Dict, Any
from datetime import datetime, timedelta

class TimingValidator:
    def validate(self, parsed_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate timing and dates"""
        errors = []
        warnings = []
        
        try:
            content = parsed_data.get('content', '')
            
            # Look for date segments
            date_lines = [line for line in content.split('\n') if 'DTM*' in line]
            
            if not date_lines:
                warnings.append({
                    'message': 'No date information found',
                    'segment': 'DTM',
                    'details': 'Could not locate date/time segments in EDI file',
                    'suggestion': 'Include DTM segments for delivery and shipment dates'
                })
            else:
                # Check if dates are reasonable
                for date_line in date_lines:
                    parts = date_line.split('*')
                    if len(parts) > 2:
                        date_str = parts[2]
                        try:
                            # Try to parse the date (YYYYMMDD format)
                            if len(date_str) == 8:
                                date_obj = datetime.strptime(date_str, '%Y%m%d')
                                
                                # Check if date is in the past (more than 30 days ago)
                                if date_obj < datetime.now() - timedelta(days=30):
                                    warnings.append({
                                        'message': f'Date {date_str} is more than 30 days in the past',
                                        'segment': 'DTM',
                                        'details': 'Old dates may indicate stale data',
                                        'suggestion': 'Verify date accuracy and update if necessary'
                                    })
                                
                                # Check if date is too far in the future
                                if date_obj > datetime.now() + timedelta(days=365):
                                    warnings.append({
                                        'message': f'Date {date_str} is more than 1 year in the future',
                                        'segment': 'DTM',
                                        'details': 'Future dates should be reasonable',
                                        'suggestion': 'Verify date accuracy'
                                    })
                        except ValueError:
                            errors.append({
                                'message': f'Invalid date format: {date_str}',
                                'segment': 'DTM',
                                'details': 'Date should be in YYYYMMDD format',
                                'suggestion': 'Use YYYYMMDD format for all dates'
                            })
            
            success = len(errors) == 0
            details = f"Timing validation completed. Found {len(date_lines)} date segments."
            
            return {
                'validator': 'Timing Validator',
                'errors': errors,
                'warnings': warnings,
                'success': success,
                'details': details
            }
            
        except Exception as e:
            return {
                'validator': 'Timing Validator',
                'errors': [{
                    'message': f'Timing validation error: {str(e)}',
                    'segment': 'SYSTEM',
                    'details': 'Internal validation error occurred',
                    'suggestion': 'Contact support if this error persists'
                }],
                'warnings': [],
                'success': False,
                'details': f'Validation failed with error: {str(e)}'
            }
