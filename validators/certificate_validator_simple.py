"""
Simple Certificate Validator for GlitchGuard
"""
from typing import Dict, Any

class CertificateValidator:
    def validate(self, parsed_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate certificates and compliance documentation"""
        errors = []
        warnings = []
        
        try:
            content = parsed_data.get('content', '')
            
            # Look for reference segments that might contain certificates
            ref_lines = [line for line in content.split('\n') if 'REF*' in line]
            
            certificate_indicators = ['FSSAI', 'ISO', 'CERT', 'LIC', 'WHO', 'GMP']
            found_certs = []
            
            for ref_line in ref_lines:
                for indicator in certificate_indicators:
                    if indicator in ref_line.upper():
                        found_certs.append(indicator)
            
            if not found_certs:
                warnings.append({
                    'message': 'No certificate references found',
                    'segment': 'REF',
                    'details': 'Could not locate certificate or license references',
                    'suggestion': 'Include relevant certificates (FSSAI, ISO, etc.) in REF segments'
                })
            else:
                # Check for required certificates based on content
                if any(word in content.upper() for word in ['FOOD', 'DAIRY', 'MEAT', 'PRODUCE']):
                    if 'FSSAI' not in [cert.upper() for cert in found_certs]:
                        warnings.append({
                            'message': 'FSSAI license may be required for food products',
                            'segment': 'COMPLIANCE',
                            'details': 'Food products typically require FSSAI certification',
                            'suggestion': 'Include FSSAI license reference for food items'
                        })
                
                if any(word in content.upper() for word in ['PHARMACEUTICAL', 'VACCINE', 'MEDICINE']):
                    if not any(cert in ['WHO', 'GMP'] for cert in found_certs):
                        warnings.append({
                            'message': 'Pharmaceutical certification may be required',
                            'segment': 'COMPLIANCE',
                            'details': 'Pharmaceutical products may require WHO or GMP certification',
                            'suggestion': 'Include relevant pharmaceutical certifications'
                        })
            
            success = len(errors) == 0
            details = f"Certificate validation completed. Found {len(found_certs)} certificate references: {', '.join(found_certs) if found_certs else 'None'}"
            
            return {
                'validator': 'Certificate Validator',
                'errors': errors,
                'warnings': warnings,
                'success': success,
                'details': details
            }
            
        except Exception as e:
            return {
                'validator': 'Certificate Validator',
                'errors': [{
                    'message': f'Certificate validation error: {str(e)}',
                    'segment': 'SYSTEM',
                    'details': 'Internal validation error occurred',
                    'suggestion': 'Contact support if this error persists'
                }],
                'warnings': [],
                'success': False,
                'details': f'Validation failed with error: {str(e)}'
            }
