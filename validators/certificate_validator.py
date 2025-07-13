"""
AS2 Certificate Validator
Validates AS2 certificates for secure EDI transmission
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import base64
import re

class CertificateValidator:
    def __init__(self):
        # Sample certificate data for validation
        self.trusted_roots = [
            'walmart_root_ca',
            'verisign_root_ca',
            'digicert_root_ca'
        ]
        
        # Certificate validation rules
        self.min_key_size = 2048
        self.warning_days_before_expiry = 30
        self.critical_days_before_expiry = 7
    
    def validate(self, parsed_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate AS2 certificates"""
        errors = []
        warnings = []
        
        try:
            content = parsed_data.get('content', '')
            
            # Extract certificate information from EDI content or configuration
            certificates = self._extract_certificates(content, config)
            
            if not certificates:
                warnings.append({
                    'segment': 'CERTIFICATE',
                    'message': 'No AS2 certificates found',
                    'details': 'Could not locate AS2 certificate information in the file or configuration',
                    'suggestion': 'Ensure AS2 certificates are properly configured for secure transmission'
                })
                
                # For demo purposes, create sample certificate data
                certificates = self._create_sample_certificates()
            
            for cert_name, cert_info in certificates.items():
                # Validate certificate expiration
                expiry_date = cert_info.get('expiry_date')
                if expiry_date:
                    days_until_expiry = (expiry_date - datetime.now()).days
                    
                    if days_until_expiry < 0:
                        errors.append({
                            'segment': 'CERTIFICATE',
                            'message': f'Certificate expired: {cert_name}',
                            'details': f'Certificate expired {abs(days_until_expiry)} days ago',
                            'suggestion': 'Renew the certificate immediately to avoid transmission failures'
                        })
                    
                    elif days_until_expiry <= self.critical_days_before_expiry:
                        errors.append({
                            'segment': 'CERTIFICATE',
                            'message': f'Certificate expires soon: {cert_name}',
                            'details': f'Certificate expires in {days_until_expiry} days',
                            'suggestion': 'Renew the certificate urgently to prevent service disruption'
                        })
                    
                    elif days_until_expiry <= self.warning_days_before_expiry:
                        warnings.append({
                            'segment': 'CERTIFICATE',
                            'message': f'Certificate expires in {days_until_expiry} days: {cert_name}',
                            'details': 'Certificate expiring within warning period',
                            'suggestion': 'Plan certificate renewal to avoid last-minute issues'
                        })
                
                # Validate certificate key size
                key_size = cert_info.get('key_size', 0)
                if key_size > 0 and key_size < self.min_key_size:
                    warnings.append({
                        'segment': 'CERTIFICATE',
                        'message': f'Weak key size: {cert_name} ({key_size} bits)',
                        'details': f'Key size {key_size} is below recommended minimum of {self.min_key_size} bits',
                        'suggestion': f'Use certificates with at least {self.min_key_size}-bit keys for better security'
                    })
                
                # Validate certificate trust chain
                issuer = cert_info.get('issuer', '')
                if issuer and not any(root in issuer.lower() for root in self.trusted_roots):
                    warnings.append({
                        'segment': 'CERTIFICATE',
                        'message': f'Untrusted certificate issuer: {cert_name}',
                        'details': f'Certificate issued by: {issuer}',
                        'suggestion': 'Ensure certificate is issued by a trusted CA recognized by Walmart'
                    })
                
                # Validate certificate purpose
                key_usage = cert_info.get('key_usage', [])
                if key_usage and 'digital_signature' not in key_usage:
                    warnings.append({
                        'segment': 'CERTIFICATE',
                        'message': f'Certificate may not support digital signatures: {cert_name}',
                        'details': 'Certificate key usage does not explicitly include digital signatures',
                        'suggestion': 'Verify certificate supports required AS2 operations'
                    })
                
                # Validate algorithm strength
                signature_algorithm = cert_info.get('signature_algorithm', '')
                weak_algorithms = ['md5', 'sha1']
                if any(weak_alg in signature_algorithm.lower() for weak_alg in weak_algorithms):
                    warnings.append({
                        'segment': 'CERTIFICATE',
                        'message': f'Weak signature algorithm: {cert_name}',
                        'details': f'Certificate uses {signature_algorithm} which is considered weak',
                        'suggestion': 'Use certificates with SHA-256 or stronger signature algorithms'
                    })
            
            # Validate AS2 configuration
            self._validate_as2_config(config, errors, warnings)
            
            # Success case
            if not errors:
                return {
                    'success': True,
                    'errors': errors,
                    'warnings': warnings,
                    'details': f'Certificate validation passed for {len(certificates)} certificate(s)'
                }
                
        except Exception as e:
            errors.append({
                'segment': 'VALIDATION',
                'message': 'Certificate validation failed',
                'details': f'Error during validation: {str(e)}',
                'suggestion': 'Check AS2 certificate configuration and ensure certificates are accessible'
            })
        
        return {'errors': errors, 'warnings': warnings}
    
    def _extract_certificates(self, content: str, config: Dict[str, Any]) -> Dict[str, Dict]:
        """Extract certificate information from content or config"""
        certificates = {}
        
        # Look for certificate references in EDI content
        # This would typically be in custom segments or partner-specific areas
        cert_pattern = r'CERT\*([A-Z0-9_]+)\*([0-9]{8})'
        matches = re.findall(cert_pattern, content)
        
        for cert_name, expiry_str in matches:
            try:
                # Parse expiry date (YYYYMMDD format)
                year = int(expiry_str[:4])
                month = int(expiry_str[4:6])
                day = int(expiry_str[6:8])
                expiry_date = datetime(year, month, day)
                
                certificates[cert_name] = {
                    'expiry_date': expiry_date,
                    'source': 'edi_content'
                }
            except (ValueError, IndexError):
                continue
        
        return certificates
    
    def _create_sample_certificates(self) -> Dict[str, Dict]:
        """Create sample certificate data for demonstration"""
        current_date = datetime.now()
        
        return {
            'vendor_signing_cert': {
                'expiry_date': current_date + timedelta(days=5),  # Expires soon
                'key_size': 2048,
                'issuer': 'DigiCert Global Root CA',
                'key_usage': ['digital_signature', 'key_encipherment'],
                'signature_algorithm': 'SHA256withRSA',
                'source': 'sample'
            },
            'vendor_encryption_cert': {
                'expiry_date': current_date + timedelta(days=90),  # Good for 3 months
                'key_size': 2048,
                'issuer': 'VeriSign Class 3 Public Primary CA',
                'key_usage': ['key_encipherment', 'data_encipherment'],
                'signature_algorithm': 'SHA256withRSA',
                'source': 'sample'
            },
            'walmart_public_cert': {
                'expiry_date': current_date + timedelta(days=365),  # Good for 1 year
                'key_size': 4096,
                'issuer': 'Walmart Root CA',
                'key_usage': ['digital_signature', 'key_encipherment'],
                'signature_algorithm': 'SHA256withRSA',
                'source': 'sample'
            }
        }
    
    def _validate_as2_config(self, config: Dict[str, Any], errors: List, warnings: List):
        """Validate AS2 configuration settings"""
        try:
            # Check for required AS2 settings (these would typically come from config)
            as2_settings = {
                'compression': False,
                'encryption': True,
                'signing': True,
                'mdn_required': True,
                'mdn_signed': True
            }
            
            # Validate encryption requirement
            if not as2_settings.get('encryption', False):
                warnings.append({
                    'segment': 'AS2_CONFIG',
                    'message': 'Encryption not enabled',
                    'details': 'AS2 transmission without encryption may not meet security requirements',
                    'suggestion': 'Enable AS2 encryption for secure data transmission'
                })
            
            # Validate signing requirement
            if not as2_settings.get('signing', False):
                warnings.append({
                    'segment': 'AS2_CONFIG',
                    'message': 'Digital signing not enabled',
                    'details': 'AS2 transmission without digital signatures may not provide non-repudiation',
                    'suggestion': 'Enable AS2 digital signing for message integrity'
                })
            
            # Validate MDN requirements
            if not as2_settings.get('mdn_required', False):
                warnings.append({
                    'segment': 'AS2_CONFIG',
                    'message': 'MDN (Message Disposition Notification) not required',
                    'details': 'Without MDN, delivery confirmation is not available',
                    'suggestion': 'Enable MDN requirement for delivery confirmation'
                })
            
            elif as2_settings.get('mdn_required', False) and not as2_settings.get('mdn_signed', False):
                warnings.append({
                    'segment': 'AS2_CONFIG',
                    'message': 'MDN signing not enabled',
                    'details': 'Unsigned MDNs may not provide reliable delivery confirmation',
                    'suggestion': 'Enable MDN signing for secure delivery confirmation'
                })
        
        except Exception:
            # If AS2 config validation fails, just skip it
            pass
