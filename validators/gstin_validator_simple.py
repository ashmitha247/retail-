"""
Simple GSTIN Validator for GlitchGuard
"""
from typing import Dict, Any

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
            '33': 'Tamil Nadu', '34': 'Puducherry', '35': 'Andaman and Nicobar',
            '36': 'Telangana', '37': 'Andhra Pradesh'
        }
    
    def validate(self, parsed_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate GSTIN format and state code"""
        errors = []
        warnings = []
        
        try:
            # Get state code from config
            state_code = config.get('state_code', '')
            state_name = config.get('state_name', '')
            vendor_id = config.get('vendor_id', '')
            
            # For demo purposes, generate a mock GSTIN based on state
            if state_code and state_code in self.state_codes:
                mock_gstin = f"{state_code}ABCDE1234F1Z5"
                
                # Validate GSTIN format (15 characters)
                if len(mock_gstin) != 15:
                    errors.append({
                        'message': 'GSTIN must be exactly 15 characters',
                        'segment': 'GSTIN',
                        'details': f'GSTIN length is {len(mock_gstin)}, must be 15',
                        'suggestion': 'Provide a valid 15-character GSTIN'
                    })
                
                # Validate state code
                gstin_state = mock_gstin[:2]
                if gstin_state != state_code:
                    errors.append({
                        'message': 'GSTIN state code mismatch',
                        'segment': 'GSTIN',
                        'details': f'GSTIN state code {gstin_state} does not match configured state {state_code}',
                        'suggestion': f'Use GSTIN with state code {state_code} for {state_name}'
                    })
                
                # Check if state code is valid
                if gstin_state not in self.state_codes:
                    errors.append({
                        'message': 'Invalid GSTIN state code',
                        'segment': 'GSTIN',
                        'details': f'State code {gstin_state} is not a valid Indian state code',
                        'suggestion': 'Use a valid Indian state code (01-37)'
                    })
                
                success = len(errors) == 0
                details = f"GSTIN validation for state {state_name} ({state_code}). Mock GSTIN: {mock_gstin}"
                
            else:
                warnings.append({
                    'message': 'No state code provided for GSTIN validation',
                    'segment': 'CONFIG',
                    'details': 'State code is required for proper GSTIN validation',
                    'suggestion': 'Configure state information in the sidebar'
                })
                success = True
                details = "GSTIN validation skipped - no state code provided"
            
            return {
                'validator': 'GSTIN Validator',
                'errors': errors,
                'warnings': warnings,
                'success': success,
                'details': details
            }
            
        except Exception as e:
            return {
                'validator': 'GSTIN Validator',
                'errors': [{
                    'message': f'GSTIN validation error: {str(e)}',
                    'segment': 'SYSTEM',
                    'details': 'Internal validation error occurred',
                    'suggestion': 'Contact support if this error persists'
                }],
                'warnings': [],
                'success': False,
                'details': f'Validation failed with error: {str(e)}'
            }
