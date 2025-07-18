# GlitchGuard Sample EDI Files for Testing

This folder contains sample EDI files to test the GlitchGuard validation system. Each file demonstrates different scenarios and validation modules.

## Available Sample Files:

### 1. **sample_basic_shipment.txt**
- **Type**: Basic EDI shipment (GlitchGuard comprehensive validation)
- **Products**: Dry goods (rice, wheat flour)
- **Expected Result**: ✅ Should pass all basic validations
- **Tests**: EDI structure, GSTIN, product codes, timing, certificates

### 2. **sample_temperature_sensitive_shipment.txt** 
- **Type**: Temperature-sensitive products shipment (GlitchGuard validation)
- **Products**: Frozen chicken, milk, ice cream, vaccines
- **Expected Result**: ✅ Should pass comprehensive validation
- **Tests**: All GlitchGuard validations including product classification

### 3. **sample_error_shipment.txt**
- **Type**: Intentionally flawed shipment  
- **Products**: Missing/invalid data
- **Expected Result**: ❌ Should fail with multiple errors
- **Tests**: Missing vendor info, invalid dates, empty fields

### 4. **sample_pharmaceutical_shipment.txt**
- **Type**: Medical/pharmaceutical shipment
- **Products**: Vaccines, insulin, biotech medicines
- **Expected Result**: ✅ Should pass with medical compliance
- **Tests**: Pharmaceutical cold chain, certifications, expiry dates

### 5. **sample_fresh_produce_shipment.txt**
- **Type**: Fresh produce shipment
- **Products**: Fruits, vegetables, dairy
- **Expected Result**: ✅ Should pass fresh food validations
- **Tests**: Fresh produce temperature requirements, short shelf life

## How to Test:

1. **Open GlitchGuard**: Visit your deployed Streamlit app
2. **Configure Sidebar**: Fill in vendor details (use matching IDs from files)
3. **Upload File**: Choose one of the sample files above
4. **Run Validation**: Click "Execute Validation Analysis"
5. **Review Results**: Check the detailed analysis and reports

## Test Configurations:

### For Basic Shipment:
- Vendor ID: `WMTIN-REL100`
- Shipment ID: `SHP20241201`
- State: Maharashtra (or any)

### For Cold Chain Shipment:
- Vendor ID: `WMTIN-REL200`  
- Shipment ID: `SHP20241201COLD`
- State: Delhi (or any)

### For Error Shipment:
- Vendor ID: `INVALID-VENDOR`
- Shipment ID: Any
- State: Any (will show errors regardless)

### For Pharmaceutical Shipment:
- Vendor ID: `WMTIN-REL300`
- Shipment ID: `SHP20241201PHARM`
- State: Telangana (or any)

### For Fresh Produce:
- Vendor ID: `WMTIN-REL400`
- Shipment ID: `SHP20241201FRESH`  
- State: Maharashtra (or any)

## Expected Validation Results:

### ✅ **Successful Files** (1, 2, 4, 5):
- Green "Ready for Submission" status
- All validation modules pass
- Downloadable reports available
- Detailed compliance metrics

### ❌ **Error File** (3):
- Red "Requires Attention" status  
- Multiple critical errors shown
- Detailed error descriptions with fixes
- Blocked submission status

## Module Detection:

The system automatically activates:

- **GlitchGuard**: Comprehensive EDI validation including:
  - EDI structure compliance
  - GSTIN tax validation  
  - Product code verification
  - ASN timing analysis
  - Certificate security checks

## Testing Tips:

1. **Try Different States**: Test GSTIN validation with various Indian states
2. **Compare Results**: Upload different files to see validation differences  
3. **Error Analysis**: Use error file to understand validation logic
4. **Product Variety**: Notice how different product types are handled
5. **Comprehensive Testing**: All files test the complete GlitchGuard validation suite

These files will help you understand the complete validation process and see how GlitchGuard handles different supply chain scenarios!
