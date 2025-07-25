"""
EDI Structure Validator
Validates EDI file structure, segments, and control numbers
"""

from typing import Dict, List, Any
import re
from datetime import datetime

class EDIValidator:
    def __init__(self):
        self.required_segments = ['ISA', 'GS', 'ST', 'BSN', 'HL', 'SE', 'GE', 'IEA']
    
    def validate(self, parsed_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate EDI structure"""
        errors = []
        warnings = []
        
        try:
            # Get file content - check multiple possible keys
            file_content = ""
            if 'content' in parsed_data:
                file_content = parsed_data['content']
            elif 'raw_content' in parsed_data:
                file_content = parsed_data['raw_content']
            elif isinstance(parsed_data, str):
                file_content = parsed_data
            
            if not file_content:
                errors.append({
                    'message': 'No file content found for validation',
                    'segment': 'FILE',
                    'details': 'Cannot validate empty or missing file content',
                    'suggestion': 'Ensure file is properly uploaded and contains data'
                })
                return {
                    'validator': 'EDI Structure Validator',
                    'errors': errors,
                    'warnings': warnings,
                    'success': False,
                    'details': 'Validation failed - no content'
                }
            
            # Check for required segments
            missing_segments = []
            for segment in self.required_segments:
                if segment + '*' not in file_content:
                    missing_segments.append(segment)
            
            if missing_segments:
                errors.append({
                    'message': f'Missing required EDI segments: {", ".join(missing_segments)}',
                    'segment': 'STRUCTURE',
                    'details': f'EDI file must contain all required segments for proper processing',
                    'suggestion': f'Add missing segments: {", ".join(missing_segments)}'
                })
            
            # Check ISA segment format
            if 'ISA*' in file_content:
                isa_lines = [line for line in file_content.split('\n') if line.strip().startswith('ISA*')]
                if isa_lines:
                    isa_parts = isa_lines[0].split('*')
                    if len(isa_parts) < 16:
                        errors.append({
                            'message': 'ISA segment has insufficient fields',
                            'segment': 'ISA',
                            'details': f'ISA segment has {len(isa_parts)} fields, requires 16',
                            'suggestion': 'Ensure ISA segment follows EDI X12 standard format'
                        })
            
            # Check vendor ID format in config
            vendor_id = config.get('vendor_id', '')
            if vendor_id and not vendor_id.startswith('WMTIN-'):
                warnings.append({
                    'message': 'Vendor ID format may not follow Walmart India standard',
                    'segment': 'CONFIG',
                    'details': f'Vendor ID "{vendor_id}" does not start with WMTIN-',
                    'suggestion': 'Verify vendor ID format with Walmart India standards'
                })
            
            # Check for proper line endings
            if not file_content.strip().endswith('~'):
                warnings.append({
                    'message': 'EDI file should end with segment terminator (~)',
                    'segment': 'FILE',
                    'details': 'File does not end with proper EDI segment terminator',
                    'suggestion': 'Add ~ at the end of your EDI file'
                })
            
            # Success case
            success = len(errors) == 0
            details = f"EDI structure validation completed. Found {len(self.required_segments) - len(missing_segments)}/{len(self.required_segments)} required segments."
            
            return {
                'validator': 'EDI Structure Validator',
                'errors': errors,
                'warnings': warnings,
                'success': success,
                'details': details
            }
            
        except Exception as e:
            return {
                'validator': 'EDI Structure Validator',
                'errors': [{
                    'message': f'Validation error: {str(e)}',
                    'segment': 'SYSTEM',
                    'details': 'Internal validation error occurred',
                    'suggestion': 'Contact support if this error persists'
                }],
                'warnings': [],
                'success': False,
                'details': f'Validation failed with error: {str(e)}'
            }
            if not parsed_data.get('content'):
                errors.append({
                    'segment': 'FILE',
                    'message': 'Empty or invalid file content',
                    'details': 'The uploaded file appears to be empty or corrupted',
                    'suggestion': 'Upload a valid EDI file with proper content'
                })
                return {'errors': errors, 'warnings': warnings}
            
            content = parsed_data['content']
            lines = content.split('\n')
            
            # Check for required segments
            found_segments = set()
            control_numbers = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check segment patterns
                for segment, pattern in self.segment_patterns.items():
                    if re.match(pattern, line):
                        found_segments.add(segment)
                        
                        # Extract control numbers
                        if segment == 'ISA':
                            parts = line.split('*')
                            if len(parts) >= 14:
                                control_numbers['ISA'] = parts[13]
                        elif segment == 'GS':
                            parts = line.split('*')
                            if len(parts) >= 7:
                                control_numbers['GS'] = parts[6]
                        elif segment == 'ST':
                            parts = line.split('*')
                            if len(parts) >= 3:
                                control_numbers['ST'] = parts[2]
            
            # Validate required segments
            missing_segments = set(self.required_segments) - found_segments
            if missing_segments:
                for segment in missing_segments:
                    errors.append({
                        'segment': segment,
                        'message': f'Missing required segment: {segment}',
                        'details': f'The {segment} segment is mandatory for ASN documents',
                        'suggestion': f'Add the {segment} segment to your EDI file'
                    })
            
            # Validate ASN-specific requirements
            if 'ST' in found_segments:
                st_found = False
                for line in lines:
                    if line.strip().startswith('ST*856*'):
                        st_found = True
                        break
                
                if not st_found:
                    errors.append({
                        'segment': 'ST',
                        'message': 'Invalid transaction set type',
                        'details': 'ST segment must specify transaction set 856 (ASN)',
                        'suggestion': 'Ensure ST segment starts with ST*856*'
                    })
            
            # Check for PO number (BSN segment)
            bsn_found = False
            for line in lines:
                if line.strip().startswith('BSN*'):
                    bsn_found = True
                    parts = line.split('*')
                    if len(parts) < 4:
                        errors.append({
                            'segment': 'BSN',
                            'message': 'Incomplete BSN segment',
                            'details': 'BSN segment is missing required fields',
                            'suggestion': 'Ensure BSN segment has all required fields: purpose code, shipment ID, date, time'
                        })
                    break
            
            if not bsn_found:
                errors.append({
                    'segment': 'BSN',
                    'message': 'Missing PO number segment',
                    'details': 'BSN segment is required to identify the purchase order',
                    'suggestion': 'Add BSN segment with shipment identification details'
                })
            
            # Validate control number consistency
            if len(control_numbers) > 1:
                unique_numbers = set(control_numbers.values())
                if len(unique_numbers) != len(control_numbers):
                    warnings.append({
                        'segment': 'CONTROL',
                        'message': 'Duplicate control numbers detected',
                        'details': 'Multiple segments have the same control number',
                        'suggestion': 'Ensure each control number is unique'
                    })
            
            # Check file structure integrity
            if len(lines) < 10:
                warnings.append({
                    'segment': 'FILE',
                    'message': 'File appears to be very short',
                    'details': f'File has only {len(lines)} lines, which seems minimal for an ASN',
                    'suggestion': 'Verify that the complete EDI file was uploaded'
                })
            
            # Success case
            if not errors:
                return {
                    'success': True,
                    'errors': errors,
                    'warnings': warnings,
                    'details': f'EDI structure validation passed. Found {len(found_segments)} required segments.'
                }
            
        except Exception as e:
            errors.append({
                'segment': 'VALIDATION',
                'message': 'EDI structure validation failed',
                'details': f'Error during validation: {str(e)}',
                'suggestion': 'Check file format and ensure it is a valid EDI file'
            })
        
        return {'errors': errors, 'warnings': warnings}
