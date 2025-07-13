"""
File Handler Utility
Handles EDI file parsing and processing
"""

from typing import Dict, Any, List
import re
from datetime import datetime

class FileHandler:
    def __init__(self):
        self.supported_formats = ['.txt', '.edi', '.x12', '.csv']
    
    def parse_edi_file(self, content: str) -> Dict[str, Any]:
        """Parse EDI file content and extract structured data"""
        try:
            parsed_data = {
                'content': content,
                'segments': [],
                'transaction_sets': [],
                'control_numbers': {},
                'metadata': {
                    'parsed_at': datetime.now().isoformat(),
                    'total_lines': len(content.split('\n')),
                    'file_size': len(content)
                }
            }
            
            # Split content into lines and parse segments
            lines = content.split('\n')
            current_transaction_set = None
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                
                # Parse segment
                segment = self._parse_segment(line, line_num)
                if segment:
                    parsed_data['segments'].append(segment)
                    
                    # Handle transaction set boundaries
                    if segment['tag'] == 'ST':
                        current_transaction_set = {
                            'type': segment['elements'][1] if len(segment['elements']) > 1 else 'Unknown',
                            'control_number': segment['elements'][2] if len(segment['elements']) > 2 else '',
                            'segments': []
                        }
                        parsed_data['transaction_sets'].append(current_transaction_set)
                    
                    if current_transaction_set:
                        current_transaction_set['segments'].append(segment)
                    
                    # Extract control numbers
                    if segment['tag'] in ['ISA', 'GS', 'ST']:
                        self._extract_control_numbers(segment, parsed_data['control_numbers'])
            
            return parsed_data
            
        except Exception as e:
            return {
                'content': content,
                'error': f'Failed to parse EDI file: {str(e)}',
                'metadata': {
                    'parsed_at': datetime.now().isoformat(),
                    'parsing_failed': True
                }
            }
    
    def _parse_segment(self, line: str, line_num: int) -> Dict[str, Any]:
        """Parse a single EDI segment"""
        try:
            # EDI segments are typically separated by * or other delimiters
            if '*' in line:
                parts = line.split('*')
                tag = parts[0]
                elements = parts[1:] if len(parts) > 1 else []
            elif '|' in line:
                parts = line.split('|')
                tag = parts[0]
                elements = parts[1:] if len(parts) > 1 else []
            else:
                # Fallback: treat as single element
                tag = line[:3] if len(line) >= 3 else line
                elements = [line[3:]] if len(line) > 3 else []
            
            return {
                'tag': tag,
                'elements': elements,
                'line_number': line_num,
                'raw_content': line
            }
            
        except Exception:
            return None
    
    def _extract_control_numbers(self, segment: Dict[str, Any], control_numbers: Dict[str, str]):
        """Extract control numbers from segments"""
        try:
            tag = segment['tag']
            elements = segment['elements']
            
            if tag == 'ISA' and len(elements) >= 13:
                control_numbers['ISA'] = elements[12]
            elif tag == 'GS' and len(elements) >= 6:
                control_numbers['GS'] = elements[5]
            elif tag == 'ST' and len(elements) >= 2:
                control_numbers['ST'] = elements[1]
                
        except Exception:
            pass
    
    def validate_file_format(self, filename: str, content: str) -> Dict[str, Any]:
        """Validate file format and basic structure"""
        result = {
            'is_valid': False,
            'format': 'unknown',
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check file extension
            file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
            
            if file_ext not in self.supported_formats:
                result['warnings'].append(f'Unsupported file extension: {file_ext}')
            
            # Detect format based on content
            if self._is_edi_format(content):
                result['format'] = 'edi'
                result['is_valid'] = True
            elif self._is_csv_format(content):
                result['format'] = 'csv'
                result['is_valid'] = True
            else:
                result['errors'].append('Unable to detect valid EDI or CSV format')
            
            # Basic content validation
            if len(content.strip()) == 0:
                result['errors'].append('File is empty')
                result['is_valid'] = False
            
            if len(content) > 10 * 1024 * 1024:  # 10MB limit
                result['warnings'].append('File is very large (>10MB)')
            
        except Exception as e:
            result['errors'].append(f'File validation error: {str(e)}')
        
        return result
    
    def _is_edi_format(self, content: str) -> bool:
        """Check if content appears to be in EDI format"""
        try:
            # Look for common EDI segments
            edi_segments = ['ISA*', 'GS*', 'ST*', 'BSN*', 'HL*', 'SE*', 'GE*', 'IEA*']
            found_segments = sum(1 for segment in edi_segments if segment in content)
            
            # If we find at least 3 EDI segments, consider it EDI format
            return found_segments >= 3
            
        except Exception:
            return False
    
    def _is_csv_format(self, content: str) -> bool:
        """Check if content appears to be in CSV format"""
        try:
            lines = content.split('\n')
            if len(lines) < 2:
                return False
            
            # Check if first few lines have consistent comma separation
            first_line_commas = lines[0].count(',')
            if first_line_commas < 2:
                return False
            
            # Check consistency across first few lines
            consistent_lines = 0
            for line in lines[:5]:
                if line.count(',') == first_line_commas:
                    consistent_lines += 1
            
            return consistent_lines >= 2
            
        except Exception:
            return False
    
    def extract_file_metadata(self, filename: str, content: str) -> Dict[str, Any]:
        """Extract metadata from file"""
        metadata = {
            'filename': filename,
            'size_bytes': len(content),
            'line_count': len(content.split('\n')),
            'created_at': datetime.now().isoformat(),
            'encoding': 'utf-8'  # Assumed encoding
        }
        
        try:
            # Try to extract date information from content
            date_patterns = [
                r'(\d{4})(\d{2})(\d{2})',  # YYYYMMDD
                r'(\d{2})/(\d{2})/(\d{4})',  # MM/DD/YYYY
                r'(\d{4})-(\d{2})-(\d{2})'   # YYYY-MM-DD
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    metadata['dates_found'] = len(matches)
                    break
            
            # Extract vendor/partner information if available
            vendor_patterns = [
                r'N1\*VN\*([^*]+)',  # Vendor name in N1 segment
                r'REF\*VN\*([^*]+)'  # Vendor reference
            ]
            
            for pattern in vendor_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    metadata['vendor_info'] = matches[0]
                    break
            
        except Exception:
            pass
        
        return metadata
