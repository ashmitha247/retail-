"""
Simple Product Validator for GlitchGuard
"""
from typing import Dict, Any

class ProductValidator:
    def validate(self, parsed_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate product codes and descriptions"""
        errors = []
        warnings = []
        
        try:
            content = parsed_data.get('content', '')
            
            # Look for product information in the EDI content
            product_lines = [line for line in content.split('\n') if 'LIN*' in line or 'PID*' in line]
            
            if not product_lines:
                warnings.append({
                    'message': 'No product lines found in EDI file',
                    'segment': 'LIN',
                    'details': 'Could not locate product information (LIN segments)',
                    'suggestion': 'Ensure product details are included with LIN and PID segments'
                })
            else:
                # Check product codes format
                lin_segments = [line for line in content.split('\n') if line.strip().startswith('LIN*')]
                for lin in lin_segments:
                    parts = lin.split('*')
                    if len(parts) > 4:
                        product_code = parts[4] if len(parts) > 4 else ''
                        if product_code and len(product_code) < 8:
                            warnings.append({
                                'message': f'Product code {product_code} may be too short',
                                'segment': 'LIN',
                                'details': f'Product code length is {len(product_code)}, typically 8-14 characters',
                                'suggestion': 'Verify product code format with Walmart standards'
                            })
            
            success = len(errors) == 0
            details = f"Product validation completed. Found {len(product_lines)} product-related lines."
            
            return {
                'validator': 'Product Validator',
                'errors': errors,
                'warnings': warnings,
                'success': success,
                'details': details
            }
            
        except Exception as e:
            return {
                'validator': 'Product Validator',
                'errors': [{
                    'message': f'Product validation error: {str(e)}',
                    'segment': 'SYSTEM',
                    'details': 'Internal validation error occurred',
                    'suggestion': 'Contact support if this error persists'
                }],
                'warnings': [],
                'success': False,
                'details': f'Validation failed with error: {str(e)}'
            }
