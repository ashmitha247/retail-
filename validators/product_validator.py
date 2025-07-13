"""
Product Code Validator
Validates GTIN-14 barcodes and Walmart Item Numbers (WIN)
"""

from typing import Dict, List, Any
import re

class ProductValidator:
    def __init__(self):
        # Sample product database (in real implementation, this would be a proper database)
        self.product_database = {
            '12345678901234': {'name': 'Sample Product 1', 'category': 'Electronics'},
            '98765432109876': {'name': 'Sample Product 2', 'category': 'Clothing'},
            '11111111111111': {'name': 'Test Product', 'category': 'Food'},
            '22222222222222': {'name': 'Demo Item', 'category': 'Home'}
        }
        
        # GTIN-14 pattern (14 digits)
        self.gtin_pattern = r'^[0-9]{14}$'
        
        # WIN pattern (Walmart Item Number - typically starts with specific prefixes)
        self.win_pattern = r'^(WIN|WM|55)[0-9]{8,12}$'
    
    def validate(self, parsed_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate product codes and identifiers"""
        errors = []
        warnings = []
        
        try:
            content = parsed_data.get('content', '')
            
            # Extract product codes from EDI content
            product_codes = self._extract_product_codes(content)
            
            if not product_codes:
                warnings.append({
                    'segment': 'PRODUCT',
                    'message': 'No product codes found in file',
                    'details': 'Could not locate any product identifiers (GTIN, UPC, WIN) in the EDI file',
                    'suggestion': 'Ensure product codes are included in LIN segments or other appropriate locations'
                })
                return {'errors': errors, 'warnings': warnings}
            
            validated_products = 0
            
            for product_code in product_codes:
                # Validate GTIN-14 format
                if re.match(self.gtin_pattern, product_code):
                    # Validate GTIN checksum
                    if not self._validate_gtin_checksum(product_code):
                        errors.append({
                            'segment': 'LIN',
                            'message': f'GTIN checksum validation failed: {product_code}',
                            'details': 'The GTIN check digit does not match the calculated value',
                            'suggestion': 'Verify the GTIN number or recalculate the check digit'
                        })
                        continue
                    
                    # Check if product exists in database
                    if product_code not in self.product_database:
                        errors.append({
                            'segment': 'LIN',
                            'message': f'Product code not found in database: {product_code}',
                            'details': 'The GTIN is not registered in the Walmart master catalog',
                            'suggestion': 'Register the product in Walmart Retail Link or verify the GTIN number'
                        })
                        continue
                    
                    validated_products += 1
                
                # Validate WIN format
                elif re.match(self.win_pattern, product_code):
                    # WIN validation logic
                    if not self._validate_win(product_code):
                        errors.append({
                            'segment': 'LIN',
                            'message': f'Invalid Walmart Item Number: {product_code}',
                            'details': 'WIN format is incorrect or not found in system',
                            'suggestion': 'Verify WIN format and ensure it is registered with Walmart'
                        })
                        continue
                    
                    validated_products += 1
                
                # Handle other product code formats
                elif len(product_code) == 12 and product_code.isdigit():
                    # UPC-12 format
                    warnings.append({
                        'segment': 'LIN',
                        'message': f'UPC-12 format detected: {product_code}',
                        'details': 'Consider using GTIN-14 format for better compatibility',
                        'suggestion': 'Convert UPC-12 to GTIN-14 by padding with leading zeros'
                    })
                    validated_products += 1
                
                else:
                    errors.append({
                        'segment': 'LIN',
                        'message': f'Invalid product code format: {product_code}',
                        'details': 'Product code does not match GTIN-14, UPC-12, or WIN format',
                        'suggestion': 'Use valid product identifiers: GTIN-14 (14 digits) or WIN (Walmart Item Number)'
                    })
            
            # Check for duplicate product codes
            unique_codes = set(product_codes)
            if len(unique_codes) != len(product_codes):
                warnings.append({
                    'segment': 'LIN',
                    'message': 'Duplicate product codes detected',
                    'details': 'Some product codes appear multiple times in the shipment',
                    'suggestion': 'Verify quantities and ensure each product line is correctly specified'
                })
            
            # Check product quantity consistency
            self._validate_product_quantities(content, errors, warnings)
            
            # Success case
            if not errors:
                return {
                    'success': True,
                    'errors': errors,
                    'warnings': warnings,
                    'details': f'Product validation passed for {validated_products} product(s) out of {len(product_codes)} total codes found'
                }
                
        except Exception as e:
            errors.append({
                'segment': 'VALIDATION',
                'message': 'Product validation failed',
                'details': f'Error during validation: {str(e)}',
                'suggestion': 'Check product code format and ensure they follow GTIN or WIN standards'
            })
        
        return {'errors': errors, 'warnings': warnings}
    
    def _extract_product_codes(self, content: str) -> List[str]:
        """Extract product codes from EDI content"""
        product_codes = []
        
        # Look for product codes in LIN segments
        # LIN*1*UP*12345678901234 (UP = UPC, IN = Walmart Item Number, etc.)
        lin_pattern = r'LIN\*[0-9]+\*(?:UP|IN|UK|EN)\*([0-9A-Z]+)'
        matches = re.findall(lin_pattern, content)
        product_codes.extend(matches)
        
        # Look for GTINs in other segments
        gtin_pattern = r'([0-9]{14})'
        lines = content.split('\n')
        for line in lines:
            if 'LIN*' in line or 'UPC*' in line or 'GTIN*' in line:
                gtin_matches = re.findall(gtin_pattern, line)
                product_codes.extend(gtin_matches)
        
        # Remove duplicates and empty strings
        return list(filter(None, set(product_codes)))
    
    def _validate_gtin_checksum(self, gtin: str) -> bool:
        """Validate GTIN-14 checksum using the standard algorithm"""
        try:
            if len(gtin) != 14 or not gtin.isdigit():
                return False
            
            # GTIN-14 checksum calculation
            check_digit = int(gtin[-1])
            digits = [int(d) for d in gtin[:-1]]
            
            # Apply weight factors (3, 1, 3, 1, ...)
            weighted_sum = sum(digit * (3 if i % 2 == 0 else 1) for i, digit in enumerate(digits))
            
            # Calculate check digit
            calculated_check = (10 - (weighted_sum % 10)) % 10
            
            return check_digit == calculated_check
            
        except Exception:
            return False
    
    def _validate_win(self, win: str) -> bool:
        """Validate Walmart Item Number format"""
        try:
            # Basic WIN validation (simplified)
            if re.match(self.win_pattern, win):
                return True
            return False
        except Exception:
            return False
    
    def _validate_product_quantities(self, content: str, errors: List, warnings: List):
        """Validate product quantities in shipment"""
        try:
            # Look for quantity information in SN1 segments
            # SN1*1*10*EA (line number, quantity, unit of measure)
            sn1_pattern = r'SN1\*[0-9]+\*([0-9]+)\*([A-Z]{2,3})'
            quantities = re.findall(sn1_pattern, content)
            
            for qty, uom in quantities:
                qty_value = int(qty)
                
                # Check for reasonable quantity values
                if qty_value <= 0:
                    errors.append({
                        'segment': 'SN1',
                        'message': f'Invalid quantity: {qty_value}',
                        'details': 'Product quantity must be greater than zero',
                        'suggestion': 'Correct the quantity value in SN1 segment'
                    })
                
                elif qty_value > 10000:
                    warnings.append({
                        'segment': 'SN1',
                        'message': f'Large quantity detected: {qty_value}',
                        'details': 'Quantity seems unusually high',
                        'suggestion': 'Verify the quantity is correct'
                    })
                
                # Validate unit of measure
                valid_uoms = ['EA', 'CS', 'BX', 'PK', 'LB', 'KG', 'PC', 'DZ']
                if uom not in valid_uoms:
                    warnings.append({
                        'segment': 'SN1',
                        'message': f'Uncommon unit of measure: {uom}',
                        'details': f'Unit of measure {uom} may not be recognized',
                        'suggestion': f'Consider using standard UOM codes: {", ".join(valid_uoms)}'
                    })
        
        except Exception:
            # If quantity validation fails, just skip it
            pass
