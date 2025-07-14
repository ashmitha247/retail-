#!/usr/bin/env python3
"""
Test script to verify ColdChain Validator functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from validators.coldchain_validator import ColdChainValidator

def test_coldchain_validator():
    """Test the ColdChain validator with sample data"""
    
    print("🧊 Testing ColdChain Validator...")
    
    # Create validator instance
    validator = ColdChainValidator()
    
    # Sample test data for cold chain validation
    test_data = {
        'shipment_id': 'TEST-001',
        'temperature_readings': [2.1, 2.3, 2.0, 2.5, 2.2, 2.4, 2.1],
        'sensor_data': {
            'TEMP_001': {
                'last_calibration': '2024-06-01',
                'battery_level': 85,
                'status': 'ACTIVE'
            },
            'TEMP_002': {
                'last_calibration': '2024-05-15', 
                'battery_level': 92,
                'status': 'ACTIVE'
            }
        },
        'documents': {
            'fssai_license': {
                'number': 'FSSAI12345678901234',
                'expiry_date': '2025-12-31'
            },
            'sanitation_cert': {
                'number': 'SAN001',
                'expiry_date': '2025-06-30'
            }
        },
        'product_info': {
            'category': 'dairy',
            'days_to_expiry': 45
        }
    }
    
    try:
        # Configuration for the validator
        config = {
            'temperature_range': {'min': 2.0, 'max': 8.0},
            'enable_iot': True,
            'enable_ml': True,
            'compliance_checks': ['fssai', 'sanitation', 'calibration']
        }
        
        # Run validation
        result = validator.validate(test_data, config)
        
        print("✅ Validation completed successfully!")
        print(f"📊 Overall Status: {result.get('overall_status', 'Unknown')}")
        
        # Print key results
        if 'spoilage_risk' in result:
            risk = result['spoilage_risk']
            print(f"🤖 AI Risk Level: {risk.get('risk_level')} ({risk.get('confidence', 0):.1%} confidence)")
        
        if 'sensor_health' in result:
            sensor = result['sensor_health']
            print(f"📡 Sensor Health: {sensor.get('data_quality', 'N/A')}")
        
        if 'document_compliance' in result:
            docs = result['document_compliance']
            valid_docs = sum([docs.get('fssai_valid', False), 
                            docs.get('sanitation_valid', False), 
                            docs.get('calibration_valid', False)])
            print(f"📋 Document Compliance: {valid_docs}/3 documents valid")
        
        print("\n🎯 ColdChain Validator is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_coldchain_validator()
    sys.exit(0 if success else 1)
