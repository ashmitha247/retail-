# GlitchGuard - EDI Validation Application

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   streamlit run app.py
   ```

3. Open your browser to the provided URL (typically http://localhost:8501)

## Project Structure

```
retail-/
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python dependencies
├── validators/               # Validation modules
│   ├── edi_validator.py      # EDI structure validation
│   ├── gstin_validator.py    # GSTIN format validation
│   ├── product_validator.py  # Product code validation
│   ├── timing_validator.py   # ASN timing validation
│   └── certificate_validator.py # AS2 certificate validation
├── utils/                    # Utility modules
│   ├── file_handler.py       # File parsing and handling
│   └── report_generator.py   # Report generation
└── sample_data/              # Sample EDI files for testing
    ├── sample_asn.edi        # Valid ASN example
    ├── sample_asn_with_gstin.edi # ASN with GSTIN
    └── sample_asn_with_errors.edi # ASN with intentional errors
```

## Features

- **Multi-format Support**: Handles .txt, .edi, .x12, and .csv files
- **Comprehensive Validation**: EDI structure, GSTIN, product codes, timing, and certificates
- **Interactive UI**: Modern Streamlit interface with real-time validation
- **Detailed Reporting**: JSON and CSV export options
- **Sample Data**: Includes test files to demonstrate functionality

## Sample Files

The `sample_data/` directory contains example EDI files:

- `sample_asn.edi`: Clean ASN with no errors
- `sample_asn_with_gstin.edi`: ASN with GSTIN validation
- `sample_asn_with_errors.edi`: ASN with intentional errors for testing

## Validation Types

1. **EDI Structure**: Validates segment presence and format
2. **GSTIN Format**: Validates Indian tax ID format and state codes
3. **Product Codes**: Validates GTIN-14 and Walmart Item Numbers
4. **ASN Timing**: Ensures proper submission timing
5. **AS2 Certificates**: Validates certificate expiration and security

## Configuration

The application allows configuration of:
- Vendor ID and Shipment ID
- Indian state selection for GSTIN validation
- Individual validation enable/disable options

## Getting Started

1. Upload an EDI file using the file uploader
2. Configure your vendor settings in the sidebar
3. Click "Validate EDI File" to run all checks
4. Review results and download reports as needed

For more detailed information, see the main README.md file.
