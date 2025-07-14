# GlitchGuard Sample EDI Files for Testing

This folder contains sample EDI files to test the GlitchGuard validation system. Each file demonstrates different scenarios and validation modules.

## Available Sample Files:

### 1. **sample_basic_shipment.txt**
- **Type**: Basic EDI shipment (VendorLadon module only)
- **Products**: Dry goods (rice, wheat flour)
- **Expected Result**: ✅ Should pass all basic validations
- **Tests**: EDI structure, GSTIN, product codes, timing, certificates

### 2. **sample_coldchain_shipment.txt** 
- **Type**: Cold chain shipment (VendorLadon + ColdChain modules)
- **Products**: Frozen chicken, milk, ice cream, vaccines
- **Expected Result**: ✅ Should pass with cold chain compliance
- **Tests**: All basic validations + temperature control requirements

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

The system will automatically detect and activate:

- **VendorLadon**: Always active for all EDI files
- **ColdChain**: Activated for files containing keywords like:
  - `frozen`, `fresh`, `refrigerat`, `cold`, `chilled`
  - `dairy`, `meat`, `pharmaceutical`, `vaccine`
  - `temperature`, `temp controlled`

## Testing Tips:

1. **Try Different States**: Test GSTIN validation with various Indian states
2. **Compare Results**: Upload different files to see validation differences  
3. **Check Reports**: Download JSON/CSV reports to see detailed data
4. **Error Analysis**: Use error file to understand validation logic
5. **Module Switching**: Notice how cold chain detection works automatically

These files will help you understand the complete validation process and see how GlitchGuard handles different supply chain scenarios!
