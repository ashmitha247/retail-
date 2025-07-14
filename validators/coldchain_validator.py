"""
Module B - ColdChain Validator
Comprehensive cold chain compliance validation for temperature-sensitive shipments
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
import json
import requests
from dataclasses import dataclass
import pickle
import os

@dataclass
class SensorReading:
    """IoT sensor data structure"""
    timestamp: datetime
    temperature: float
    humidity: float
    sensor_id: str
    location: str

@dataclass
class ComplianceDocument:
    """Legal compliance document structure"""
    doc_type: str
    doc_number: str
    issue_date: datetime
    expiry_date: datetime
    issuing_authority: str
    status: str

class IoTVerifier:
    """Handles IoT sensor data validation and health checks"""
    
    def __init__(self):
        self.calibration_threshold_days = 365  # Annual calibration requirement
        self.temp_stability_threshold = 2.0    # Max temperature variation (°C)
        
    def fetch_sensor_data(self, shipment_id: str, api_endpoint: str = None) -> List[SensorReading]:
        """Fetch real-time sensor data from IoT API"""
        try:
            # Mock API call - replace with actual IoT endpoint
            if api_endpoint:
                response = requests.get(f"{api_endpoint}/sensors/{shipment_id}")
                sensor_data = response.json()
            else:
                # Mock data for demonstration
                sensor_data = self._generate_mock_sensor_data()
                
            readings = []
            for reading in sensor_data.get('readings', []):
                readings.append(SensorReading(
                    timestamp=datetime.fromisoformat(reading['timestamp']),
                    temperature=reading['temperature'],
                    humidity=reading['humidity'],
                    sensor_id=reading['sensor_id'],
                    location=reading['location']
                ))
            return readings
        except Exception as e:
            return []
    
    def _generate_mock_sensor_data(self) -> Dict:
        """Generate mock sensor data for testing"""
        base_time = datetime.now() - timedelta(hours=24)
        readings = []
        
        for i in range(24):  # 24 hours of hourly readings
            readings.append({
                'timestamp': (base_time + timedelta(hours=i)).isoformat(),
                'temperature': np.random.normal(4.0, 0.5),  # 4°C ± 0.5°C
                'humidity': np.random.normal(85, 5),        # 85% ± 5%
                'sensor_id': 'TEMP_001',
                'location': 'TRUCK_COMPARTMENT'
            })
        
        return {
            'shipment_id': 'SHP20241201',
            'readings': readings,
            'calibration_date': (datetime.now() - timedelta(days=180)).isoformat(),
            'sensor_status': 'ACTIVE'
        }
    
    def validate_sensor_health(self, readings: List[SensorReading], calibration_date: datetime) -> Dict[str, Any]:
        """Validate sensor calibration and stability"""
        results = {
            'calibration_valid': False,
            'temperature_stable': False,
            'data_quality': 'POOR',
            'issues': []
        }
        
        # Check calibration age
        calibration_age = (datetime.now() - calibration_date).days
        if calibration_age <= self.calibration_threshold_days:
            results['calibration_valid'] = True
        else:
            results['issues'].append(f"Sensor calibration overdue by {calibration_age - self.calibration_threshold_days} days")
        
        # Check temperature stability
        if readings:
            temps = [r.temperature for r in readings]
            temp_range = max(temps) - min(temps)
            if temp_range <= self.temp_stability_threshold:
                results['temperature_stable'] = True
            else:
                results['issues'].append(f"Temperature range {temp_range:.1f}°C exceeds threshold {self.temp_stability_threshold}°C")
        
        # Determine data quality
        if results['calibration_valid'] and results['temperature_stable']:
            results['data_quality'] = 'EXCELLENT'
        elif results['calibration_valid'] or results['temperature_stable']:
            results['data_quality'] = 'GOOD'
        
        return results

class FSSAILicenseCheck:
    """FSSAI license validation for food transport compliance"""
    
    def validate(self, document: ComplianceDocument) -> Dict[str, Any]:
        """Validate FSSAI license document"""
        result = {
            'valid': False,
            'issues': [],
            'expiry_warning': False
        }
        
        # Check document type
        if document.doc_type != 'FSSAI_LICENSE':
            result['issues'].append("Invalid document type for FSSAI validation")
            return result
        
        # Check expiry date
        days_to_expiry = (document.expiry_date - datetime.now()).days
        if days_to_expiry < 0:
            result['issues'].append(f"FSSAI license expired {abs(days_to_expiry)} days ago")
        elif days_to_expiry < 30:
            result['expiry_warning'] = True
            result['issues'].append(f"FSSAI license expires in {days_to_expiry} days")
        
        # Check license number format (14 digits)
        if not (document.doc_number.isdigit() and len(document.doc_number) == 14):
            result['issues'].append("Invalid FSSAI license number format")
        
        # Check issuing authority
        valid_authorities = ['FSSAI', 'STATE_FOOD_AUTHORITY']
        if document.issuing_authority not in valid_authorities:
            result['issues'].append("Invalid issuing authority")
        
        result['valid'] = len(result['issues']) == 0
        return result

class CalibrationCheck:
    """Temperature sensor calibration validation"""
    
    def validate(self, calibration_date: datetime, sensor_id: str) -> Dict[str, Any]:
        """Validate sensor calibration status"""
        result = {
            'valid': False,
            'calibration_age_days': 0,
            'issues': []
        }
        
        calibration_age = (datetime.now() - calibration_date).days
        result['calibration_age_days'] = calibration_age
        
        if calibration_age > 365:
            result['issues'].append(f"Sensor {sensor_id} calibration overdue by {calibration_age - 365} days")
        elif calibration_age > 330:  # Warning at 11 months
            result['issues'].append(f"Sensor {sensor_id} calibration due soon ({365 - calibration_age} days remaining)")
        
        result['valid'] = calibration_age <= 365
        return result

class SanitationCheck:
    """Vehicle sanitation certificate validation"""
    
    def validate(self, document: ComplianceDocument) -> Dict[str, Any]:
        """Validate sanitation certificate"""
        result = {
            'valid': False,
            'issues': []
        }
        
        # Check document validity period (sanitation certs valid for 6 months)
        days_since_issue = (datetime.now() - document.issue_date).days
        if days_since_issue > 180:
            result['issues'].append(f"Sanitation certificate expired {days_since_issue - 180} days ago")
        
        # Check certificate number format
        if not document.doc_number.startswith('SAN'):
            result['issues'].append("Invalid sanitation certificate number format")
        
        result['valid'] = len(result['issues']) == 0
        return result

class SpoilagePredictor:
    """ML model for predicting spoilage risk"""
    
    def __init__(self):
        self.model = None
        self.model_path = 'models/spoilage_predictor.pkl'
        self.load_model()
    
    def load_model(self):
        """Load pre-trained ML model"""
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
        else:
            # Create a simple mock model for demonstration
            self.create_mock_model()
    
    def create_mock_model(self):
        """Create a mock ML model for demonstration"""
        from sklearn.ensemble import RandomForestClassifier
        
        # Generate mock training data
        np.random.seed(42)
        n_samples = 1000
        
        # Features: temp_range, calibration_age, truck_age, route_temp_avg
        X = np.random.rand(n_samples, 4)
        X[:, 0] *= 10  # temp_range: 0-10°C
        X[:, 1] *= 500  # calibration_age: 0-500 days
        X[:, 2] *= 10   # truck_age: 0-10 years
        X[:, 3] = X[:, 3] * 30 + 5  # route_temp_avg: 5-35°C
        
        # Generate labels (spoilage risk)
        y = (X[:, 0] > 5) | (X[:, 1] > 365) | (X[:, 2] > 7) | (X[:, 3] > 25)
        
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        
        # Save model
        os.makedirs('models', exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
    
    def predict_spoilage_risk(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Predict spoilage risk based on features"""
        if not self.model:
            return {'risk_score': 0.5, 'risk_level': 'UNKNOWN', 'confidence': 0.0}
        
        # Extract features in correct order
        feature_vector = np.array([[
            features.get('temp_range', 0),
            features.get('calibration_age', 0),
            features.get('truck_age', 5),
            features.get('route_temp_avg', 20)
        ]])
        
        # Get prediction and probability
        risk_prob = self.model.predict_proba(feature_vector)[0][1]
        risk_prediction = self.model.predict(feature_vector)[0]
        
        # Determine risk level
        if risk_prob < 0.3:
            risk_level = 'LOW'
        elif risk_prob < 0.7:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'HIGH'
        
        return {
            'risk_score': float(risk_prob),
            'risk_level': risk_level,
            'prediction': bool(risk_prediction),
            'confidence': float(max(risk_prob, 1 - risk_prob))
        }

class ColdChainValidator:
    """Main ColdChain Validator - Module B"""
    
    def __init__(self):
        self.iot_verifier = IoTVerifier()
        self.fssai_checker = FSSAILicenseCheck()
        self.calibration_checker = CalibrationCheck()
        self.sanitation_checker = SanitationCheck()
        self.spoilage_predictor = SpoilagePredictor()
    
    def validate(self, parsed_data: Dict, config: Dict) -> Dict[str, Any]:
        """Main validation entry point"""
        results = {
            'sensor_health': {},
            'document_compliance': {},
            'spoilage_risk': {},
            'overall_status': 'PENDING',
            'blocking_issues': [],
            'warnings': [],
            'success': False,
            'details': 'Cold chain validation completed'
        }
        
        try:
            # 1. IoT Sensor Validation
            shipment_id = config.get('shipment_id', 'UNKNOWN')
            sensor_readings = self.iot_verifier.fetch_sensor_data(shipment_id)
            
            if sensor_readings:
                # Mock calibration date from sensor data
                calibration_date = datetime.now() - timedelta(days=180)
                sensor_health = self.iot_verifier.validate_sensor_health(sensor_readings, calibration_date)
                results['sensor_health'] = sensor_health
                
                if not sensor_health['calibration_valid']:
                    results['blocking_issues'].extend(sensor_health['issues'])
            
            # 2. Document Compliance Checks
            doc_results = self._validate_documents(config)
            results['document_compliance'] = doc_results
            
            # 3. ML Risk Prediction
            risk_features = self._extract_risk_features(sensor_readings, config)
            spoilage_risk = self.spoilage_predictor.predict_spoilage_risk(risk_features)
            results['spoilage_risk'] = spoilage_risk
            
            if spoilage_risk['risk_level'] == 'HIGH':
                results['blocking_issues'].append(f"High spoilage risk detected: {spoilage_risk['risk_score']:.2f}")
            elif spoilage_risk['risk_level'] == 'MEDIUM':
                results['warnings'].append(f"Medium spoilage risk: {spoilage_risk['risk_score']:.2f}")
            
            # 4. Overall Decision
            if len(results['blocking_issues']) == 0:
                results['overall_status'] = 'APPROVED'
                results['success'] = True
                results['details'] = 'Cold chain validation passed - shipment approved for dispatch'
            else:
                results['overall_status'] = 'BLOCKED'
                results['details'] = 'Cold chain validation failed - shipment blocked'
            
        except Exception as e:
            results['blocking_issues'].append(f"Cold chain validation error: {str(e)}")
            results['overall_status'] = 'ERROR'
        
        return results
    
    def _validate_documents(self, config: Dict) -> Dict[str, Any]:
        """Validate all required compliance documents"""
        doc_results = {
            'fssai_valid': False,
            'sanitation_valid': False,
            'calibration_valid': False,
            'issues': []
        }
        
        # Mock FSSAI document
        fssai_doc = ComplianceDocument(
            doc_type='FSSAI_LICENSE',
            doc_number='12345678901234',
            issue_date=datetime.now() - timedelta(days=100),
            expiry_date=datetime.now() + timedelta(days=200),
            issuing_authority='FSSAI',
            status='ACTIVE'
        )
        
        fssai_result = self.fssai_checker.validate(fssai_doc)
        doc_results['fssai_valid'] = fssai_result['valid']
        if not fssai_result['valid']:
            doc_results['issues'].extend(fssai_result['issues'])
        
        # Mock sanitation certificate
        sanitation_doc = ComplianceDocument(
            doc_type='SANITATION_CERT',
            doc_number='SAN2024001',
            issue_date=datetime.now() - timedelta(days=30),
            expiry_date=datetime.now() + timedelta(days=150),
            issuing_authority='MUNICIPAL_HEALTH',
            status='ACTIVE'
        )
        
        sanitation_result = self.sanitation_checker.validate(sanitation_doc)
        doc_results['sanitation_valid'] = sanitation_result['valid']
        if not sanitation_result['valid']:
            doc_results['issues'].extend(sanitation_result['issues'])
        
        # Calibration check
        calibration_date = datetime.now() - timedelta(days=180)
        calibration_result = self.calibration_checker.validate(calibration_date, 'TEMP_001')
        doc_results['calibration_valid'] = calibration_result['valid']
        if not calibration_result['valid']:
            doc_results['issues'].extend(calibration_result['issues'])
        
        return doc_results
    
    def _extract_risk_features(self, sensor_readings: List[SensorReading], config: Dict) -> Dict[str, float]:
        """Extract features for ML risk prediction"""
        features = {
            'temp_range': 0.0,
            'calibration_age': 180.0,  # Mock 6 months
            'truck_age': 3.0,          # Mock 3 years
            'route_temp_avg': 25.0     # Mock 25°C average
        }
        
        if sensor_readings:
            temps = [r.temperature for r in sensor_readings]
            features['temp_range'] = max(temps) - min(temps)
            features['route_temp_avg'] = np.mean(temps)
        
        return features
