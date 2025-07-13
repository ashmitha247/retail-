"""
GSTIN Validator
Validates Indian Goods and Services Tax Identification Number (GSTIN)
"""

from typing import Dict, List, Any
import re

class GSTINValidator:
    def __init__(self):
        self.state_codes = {
            '01': 'Jammu and Kashmir', '02': 'Himachal Pradesh', '03': 'Punjab',
            '04': 'Chandigarh', '05': 'Uttarakhand', '06': 'Haryana',
            '07': 'Delhi', '08': 'Rajasthan', '09': 'Uttar Pradesh',
            '10': 'Bihar', '11': 'Sikkim', '12': 'Arunachal Pradesh',
            '13': 'Nagaland', '14': 'Manipur', '15': 'Mizoram',
            '16': 'Tripura', '17': 'Meghalaya', '18': 'Assam',
            '19': 'West Bengal', '20': 'Jharkhand', '21': 'Odisha',
            '22': 'Chhattisgarh', '23': 'Madhya Pradesh', '24': 'Gujarat',
            '25': 'Daman and Diu', '26': 'Dadra and Nagar Haveli',
            '27': 'Maharashtra', '28': 'Andhra Pradesh', '29': 'Karnataka',
            '30': 'Goa', '31': 'Lakshadweep', '32': 'Kerala',
            '33': 'Tamil Nadu', '34': 'Puducherry', '35': 'Andaman and Nicobar Islands',
            '36': 'Telangana', '37': 'Andhra Pradesh', '38': 'Ladakh'
        }
        
        # GSTIN format: 2 digits state code + 10 digits PAN + 1 digit entity number + 1 digit check digit + 1 alpha Z
        self.gstin_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}$'
    
    def validate(self, parsed_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate GSTIN format and details"""
        errors = []
        warnings = []
        
        try:
            content = parsed_data.get('content', '')
            
            # Extract GSTIN from EDI content
            gstins = self._extract_gstins(content)
            
            if not gstins:
                warnings.append({
                    'segment': 'GSTIN',
                    'message': 'No GSTIN found in file',
                    'details': 'Could not locate any GSTIN numbers in the EDI file',
                    'suggestion': 'Ensure GSTIN is included in the appropriate segments (REF*TJ* or N1 segments)'
                })
                return {'errors': errors, 'warnings': warnings}
            
            expected_state_code = config.get('state_code', '27')
            state_name = config.get('state_name', 'Maharashtra')
            
            for gstin in gstins:
                # Validate GSTIN format
                if not re.match(self.gstin_pattern, gstin):
                    errors.append({
                        'segment': 'GSTIN',
                        'message': f'Invalid GSTIN format: {gstin}',
                        'details': 'GSTIN must be 15 characters: 2-digit state + 10-digit PAN + 1-digit entity + 1-digit check + Z',
                        'suggestion': 'Verify GSTIN format and ensure all characters are correct'
                    })
                    continue
                
                # Extract state code from GSTIN
                gstin_state_code = gstin[:2]
                
                # Validate state code
                if gstin_state_code not in self.state_codes:
                    errors.append({
                        'segment': 'GSTIN',
                        'message': f'Invalid state code in GSTIN: {gstin_state_code}',
                        'details': f'State code {gstin_state_code} is not a valid Indian state code',
                        'suggestion': 'Use a valid Indian state code (01-38)'
                    })
                    continue
                
                # Check state code mismatch
                if gstin_state_code != expected_state_code:
                    errors.append({
                        'segment': 'GSTIN',
                        'message': 'GSTIN state code mismatch',
                        'details': f'GSTIN state code {gstin_state_code} ({self.state_codes[gstin_state_code]}) does not match selected state {expected_state_code} ({state_name})',
                        'suggestion': f'Update GSTIN to use state code {expected_state_code} or change state selection to {self.state_codes[gstin_state_code]}'
                    })
                
                # Validate checksum (simplified validation)
                if not self._validate_gstin_checksum(gstin):
                    errors.append({
                        'segment': 'GSTIN',
                        'message': f'GSTIN checksum validation failed: {gstin}',
                        'details': 'The GSTIN check digit does not match the calculated value',
                        'suggestion': 'Verify the GSTIN number with the tax authority or recalculate the check digit'
                    })
                
                # Validate PAN pattern within GSTIN
                pan_part = gstin[2:12]
                pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
                if not re.match(pan_pattern, pan_part):
                    errors.append({
                        'segment': 'GSTIN',
                        'message': f'Invalid PAN format within GSTIN: {pan_part}',
                        'details': 'PAN portion of GSTIN must follow format: 5 letters + 4 digits + 1 letter',
                        'suggestion': 'Verify the PAN number format within the GSTIN'
                    })
            
            # Success case
            if not errors:
                return {
                    'success': True,
                    'errors': errors,
                    'warnings': warnings,
                    'details': f'GSTIN validation passed for {len(gstins)} GSTIN(s). State: {state_name} ({expected_state_code})'
                }
                
        except Exception as e:
            errors.append({
                'segment': 'VALIDATION',
                'message': 'GSTIN validation failed',
                'details': f'Error during validation: {str(e)}',
                'suggestion': 'Check GSTIN format and ensure it follows Indian tax ID standards'
            })
        
        return {'errors': errors, 'warnings': warnings}
    
    def _extract_gstins(self, content: str) -> List[str]:
        """Extract GSTIN numbers from EDI content"""
        gstins = []
        
        # Look for GSTIN in REF segments (REF*TJ*GSTIN)
        ref_pattern = r'REF\*TJ\*([0-9]{2}[A-Z0-9]{13})'
        matches = re.findall(ref_pattern, content)
        gstins.extend(matches)
        
        # Look for GSTIN in other common locations
        # N1 segments, DTM segments, etc.
        gstin_pattern = r'([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1})'
        general_matches = re.findall(gstin_pattern, content)
        gstins.extend(general_matches)
        
        # Remove duplicates
        return list(set(gstins))
    
    def _validate_gstin_checksum(self, gstin: str) -> bool:
        """Validate GSTIN checksum (simplified version)"""
        try:
            # This is a simplified checksum validation
            # In a real implementation, you would use the official GSTIN algorithm
            
            # For now, just check that the check digit is alphanumeric
            check_digit = gstin[14]
            return check_digit.isalnum()
            
        except Exception:
            return False
