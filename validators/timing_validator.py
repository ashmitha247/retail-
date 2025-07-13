"""
ASN Timing Validator
Validates timing requirements for Advance Shipment Notice (ASN)
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import re

class TimingValidator:
    def __init__(self):
        # ASN timing requirements
        self.min_advance_hours = 0  # Minimum hours before shipping
        self.max_advance_hours = 24  # Maximum hours before shipping
        self.optimal_advance_hours = 12  # Optimal timing
    
    def validate(self, parsed_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ASN timing requirements"""
        errors = []
        warnings = []
        
        try:
            content = parsed_data.get('content', '')
            
            # Extract dates from EDI content
            dates = self._extract_dates(content)
            
            if not dates:
                warnings.append({
                    'segment': 'TIMING',
                    'message': 'No dates found in ASN',
                    'details': 'Could not locate shipment dates in the EDI file',
                    'suggestion': 'Ensure DTM segments include ship date and delivery date'
                })
                return {'errors': errors, 'warnings': warnings}
            
            current_time = datetime.now()
            
            # Validate ship date
            ship_date = dates.get('ship_date')
            if ship_date:
                hours_until_ship = (ship_date - current_time).total_seconds() / 3600
                
                # Check if ASN is too early
                if hours_until_ship > self.max_advance_hours:
                    errors.append({
                        'segment': 'DTM',
                        'message': f'ASN submitted too early ({hours_until_ship:.1f} hours before shipping)',
                        'details': f'ASN should be submitted between {self.min_advance_hours}-{self.max_advance_hours} hours before shipping',
                        'suggestion': f'Submit ASN closer to ship date (within {self.max_advance_hours} hours)'
                    })
                
                # Check if ASN is too late
                elif hours_until_ship < self.min_advance_hours:
                    if hours_until_ship < 0:
                        errors.append({
                            'segment': 'DTM',
                            'message': f'ASN submitted after ship date ({abs(hours_until_ship):.1f} hours late)',
                            'details': 'ASN must be submitted before the actual shipment',
                            'suggestion': 'Submit ASN before shipping or update ship date'
                        })
                    else:
                        warnings.append({
                            'segment': 'DTM',
                            'message': f'ASN submitted very close to ship time ({hours_until_ship:.1f} hours)',
                            'details': 'This may not provide sufficient processing time',
                            'suggestion': 'Consider submitting ASN earlier for better processing'
                        })
                
                # Optimal timing advice
                elif hours_until_ship > self.optimal_advance_hours:
                    warnings.append({
                        'segment': 'DTM',
                        'message': f'ASN submitted {hours_until_ship:.1f} hours before shipping',
                        'details': f'While acceptable, optimal timing is around {self.optimal_advance_hours} hours',
                        'suggestion': 'Consider submitting closer to optimal timing window'
                    })
            
            # Validate delivery date
            delivery_date = dates.get('delivery_date')
            if delivery_date and ship_date:
                delivery_window = (delivery_date - ship_date).total_seconds() / 3600
                
                # Check reasonable delivery window
                if delivery_window < 1:
                    errors.append({
                        'segment': 'DTM',
                        'message': 'Delivery date too close to ship date',
                        'details': f'Only {delivery_window:.1f} hours between ship and delivery',
                        'suggestion': 'Allow sufficient transit time between ship and delivery dates'
                    })
                
                elif delivery_window > 72:  # More than 3 days
                    warnings.append({
                        'segment': 'DTM',
                        'message': f'Long delivery window ({delivery_window:.1f} hours)',
                        'details': 'Delivery date is more than 3 days after ship date',
                        'suggestion': 'Verify delivery date is correct'
                    })
            
            # Validate creation date
            creation_date = dates.get('creation_date')
            if creation_date:
                creation_age = (current_time - creation_date).total_seconds() / 3600
                
                if creation_age > 48:  # More than 2 days old
                    warnings.append({
                        'segment': 'DTM',
                        'message': f'ASN created {creation_age:.1f} hours ago',
                        'details': 'This ASN was created more than 2 days ago',
                        'suggestion': 'Consider creating fresh ASN closer to ship date'
                    })
            
            # Validate business hours
            if ship_date:
                self._validate_business_hours(ship_date, warnings)
            
            # Validate weekend/holiday considerations
            if ship_date or delivery_date:
                self._validate_business_days(ship_date, delivery_date, warnings)
            
            # Success case
            if not errors:
                return {
                    'success': True,
                    'errors': errors,
                    'warnings': warnings,
                    'details': f'ASN timing validation passed. Ship date: {ship_date.strftime("%Y-%m-%d %H:%M") if ship_date else "Not found"}'
                }
                
        except Exception as e:
            errors.append({
                'segment': 'VALIDATION',
                'message': 'ASN timing validation failed',
                'details': f'Error during validation: {str(e)}',
                'suggestion': 'Check date formats and ensure DTM segments are properly formatted'
            })
        
        return {'errors': errors, 'warnings': warnings}
    
    def _extract_dates(self, content: str) -> Dict[str, datetime]:
        """Extract dates from EDI content"""
        dates = {}
        
        # DTM date patterns
        # DTM*011*20240315*1430 (Ship date)
        # DTM*017*20240316*0800 (Delivery date)
        # DTM*137*20240314*1200 (Creation date)
        
        dtm_patterns = {
            '011': 'ship_date',      # Shipment date
            '017': 'delivery_date',  # Delivery date
            '137': 'creation_date'   # Document creation date
        }
        
        for qualifier, date_type in dtm_patterns.items():
            pattern = rf'DTM\*{qualifier}\*(\d{{8}})\*?(\d{{4}})?'
            matches = re.findall(pattern, content)
            
            for date_str, time_str in matches:
                try:
                    # Parse date (YYYYMMDD format)
                    year = int(date_str[:4])
                    month = int(date_str[4:6])
                    day = int(date_str[6:8])
                    
                    # Parse time (HHMM format) or default to noon
                    if time_str:
                        hour = int(time_str[:2])
                        minute = int(time_str[2:4])
                    else:
                        hour, minute = 12, 0
                    
                    dates[date_type] = datetime(year, month, day, hour, minute)
                    
                except (ValueError, IndexError):
                    continue
        
        return dates
    
    def _validate_business_hours(self, ship_date: datetime, warnings: List):
        """Validate if shipping is during business hours"""
        try:
            hour = ship_date.hour
            
            # Typical business hours: 8 AM to 6 PM
            if hour < 8 or hour > 18:
                warnings.append({
                    'segment': 'DTM',
                    'message': f'Ship time outside business hours ({ship_date.strftime("%H:%M")})',
                    'details': 'Shipping scheduled outside typical business hours (8 AM - 6 PM)',
                    'suggestion': 'Consider scheduling shipment during business hours for better processing'
                })
        
        except Exception:
            pass
    
    def _validate_business_days(self, ship_date: datetime, delivery_date: datetime, warnings: List):
        """Validate if dates fall on business days"""
        try:
            # Check if ship date is on weekend
            if ship_date and ship_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                day_name = ship_date.strftime('%A')
                warnings.append({
                    'segment': 'DTM',
                    'message': f'Ship date falls on {day_name}',
                    'details': 'Shipping scheduled on weekend',
                    'suggestion': 'Verify weekend shipping arrangements with carrier'
                })
            
            # Check if delivery date is on weekend
            if delivery_date and delivery_date.weekday() >= 5:
                day_name = delivery_date.strftime('%A')
                warnings.append({
                    'segment': 'DTM',
                    'message': f'Delivery date falls on {day_name}',
                    'details': 'Delivery scheduled on weekend',
                    'suggestion': 'Confirm weekend delivery is acceptable to receiver'
                })
        
        except Exception:
            pass
