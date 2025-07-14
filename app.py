import streamlit as st
import pandas as pd
import json
import io
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import re

# Import validation modules
from validators.edi_validator import EDIValidator
from validators.gstin_validator import GSTINValidator
from validators.product_validator import ProductValidator
from validators.timing_validator import TimingValidator
from validators.certificate_validator import CertificateValidator
from validators.coldchain_validator import ColdChainValidator
from utils.file_handler import FileHandler
from utils.report_generator import ReportGenerator

# Configure page
st.set_page_config(
    page_title="GlitchGuard - AI Retail Validator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# WHITE THEME ACTIVATED
st.markdown("""
<style>
    .stApp {
        background-color: #FFFFFF;
        color: #333333;
    }
    .stSidebar {
        background-color: #F8F9FA;
    }
    .stButton > button {
        background-color: #007BFF;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stSelectbox > div > div {
        background-color: #FFFFFF;
        color: #333333;
    }
    .metric-card {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .error-card {
        background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
        color: #C62828;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .success-card {
        background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%);
        color: #2E7D32;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    h1, h2, h3 {
        color: #1976D2 !important;
    }
    .stMarkdown {
        color: #333333;
    }
</style>
""", unsafe_allow_html=True)



# Add error handling for deployment issues
try:
    # Check if running on Streamlit Cloud
    import os
    if os.environ.get('STREAMLIT_SHARING_MODE'):
        st.cache_data.clear()
except Exception:
    pass  # Continue if cache clear fails

# Force cache clear and rerun for immediate deployment
if 'force_rerun' not in st.session_state:
    st.session_state['force_rerun'] = True
    st.rerun()

def detect_shipment_type(file_content: str) -> Dict[str, bool]:
    """
    Automatically detect shipment type and required validation modules.
    Returns dict with boolean flags for each module.
    """
    content_lower = file_content.lower()
    
    # Always activate VendorLadon module for all EDI files
    modules = {
        'vendorladon': True,  # Always active
        'coldchain': False    # Conditionally active
    }
    
    # ColdChain detection keywords
    coldchain_keywords = [
        'frozen', 'fresh', 'refrigerat', 'temperature', 'cold', 'chilled',
        'dairy', 'meat', 'fish', 'seafood', 'produce', 'vegetable', 'fruit',
        'pharmaceutical', 'vaccine', 'medical', 'biotech', 'pharma',
        'ice cream', 'yogurt', 'milk', 'cheese', 'beef', 'chicken', 'pork',
        'temp controlled', 'cold chain', 'cold storage', 'reefer',
        'controlled temperature', 'perishable', 'frozen food'
    ]
    
    # Medical/pharmaceutical product codes
    medical_codes = ['pharma', 'med', 'drug', 'vaccine', 'bio']
    
    # Check for cold chain indicators
    for keyword in coldchain_keywords:
        if keyword in content_lower:
            modules['coldchain'] = True
            break
    
    # Check for medical product codes
    for code in medical_codes:
        if code in content_lower:
            modules['coldchain'] = True
            break
    
    return modules

def get_module_description(modules: Dict[str, bool]) -> str:
    """Generate description of active modules"""
    active_modules = []
    if modules['vendorladon']:
        active_modules.append("VendorLadon (EDI Validation)")
    if modules['coldchain']:
        active_modules.append("ColdChain (Temperature Control)")
    
    return " + ".join(active_modules)

# Enhanced CSS for professional, sleek design
st.markdown("""
<style>
    /* Global Styles */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header Styles */
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .main-header p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Card Styles */
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.05);
        margin: 0.5rem 0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        color: #333333;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    }
    
    .success-card {
        background: linear-gradient(145deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 5px solid #28a745;
        color: #155724;
    }
    
    .error-card {
        background: linear-gradient(145deg, #f8d7da 0%, #f5c6cb 100%);
        border-left: 5px solid #dc3545;
        color: #721c24;
    }
    
    .warning-card {
        background: linear-gradient(145deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 5px solid #ffc107;
        color: #856404;
    }
    
    .info-card {
        background: linear-gradient(145deg, #d1ecf1 0%, #bee5eb 100%);
        border-left: 5px solid #17a2b8;
        color: #0c5460;
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #007BFF 0%, #0056B3 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
    }
    
    /* Sidebar Styles */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* File Upload Styles */
    .uploadedFile {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border: 2px dashed #667eea;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .uploadedFile:hover {
        border-color: #764ba2;
        background: linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Progress Bar Styles */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Expander Styles */
    .streamlit-expanderHeader {
        background: linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 8px;
        border: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    /* Metric Styles */
    [data-testid="metric-container"] {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid rgba(0, 0, 0, 0.05);
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    /* Table Styles */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Alert Styles */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Status Indicator */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-ready { background-color: #28a745; }
    .status-error { background-color: #dc3545; }
    .status-warning { background-color: #ffc107; }
    .status-info { background-color: #17a2b8; }
</style>
""", unsafe_allow_html=True)

def main():
    # Professional Header
    st.markdown("""
    <div class="main-header">
        <h1>⚡ GlitchGuard</h1>
        <p>Intelligent Supply Chain Validation Platform</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar configuration with enhanced styling
    with st.sidebar:
        st.markdown("## ⚙️ Configuration Panel")
        
        st.markdown("### 🏢 Vendor Information")
        vendor_id = st.text_input(
            "Vendor ID", 
            placeholder="e.g., WMTIN-REL100",
            help="Your unique Walmart vendor identifier"
        )
        shipment_id = st.text_input(
            "Shipment ID", 
            placeholder="e.g., SHP20241201",
            help="Unique identifier for this shipment"
        )
        
        st.markdown("### 🗺️ Geographic Configuration")
        indian_states = {
            "Maharashtra": "27", "Gujarat": "24", "Karnataka": "29", "Tamil Nadu": "33",
            "Telangana": "36", "Andhra Pradesh": "37", "West Bengal": "19", "Uttar Pradesh": "09",
            "Rajasthan": "08", "Haryana": "06", "Delhi": "07", "Punjab": "03"
        }
        selected_state = st.selectbox(
            "Indian State", 
            list(indian_states.keys()), 
            index=0,
            help="Select your state for GSTIN validation"
        )
        state_code = indian_states[selected_state]
        
        st.markdown("### 🎯 Intelligent Module Detection")
        st.markdown("GlitchGuard automatically detects your shipment type and activates the right validation modules:")
        
        st.info("""
        **VendorLadon Module**: Always active for all EDI files  
        **ColdChain Module**: Auto-activated for temperature-sensitive products
        """)
        
        # Configuration summary
        st.markdown("---")
        st.markdown("### 📊 Configuration Summary")
        
        # Check if configuration is complete
        config_complete = bool(vendor_id and shipment_id)
        
        if config_complete:
            st.success(f"""
            **Vendor**: {vendor_id}  
            **Shipment**: {shipment_id}  
            **State**: {selected_state} ({state_code})  
            **Detection**: Automatic based on file content
            """)
        else:
            missing_items = []
            if not vendor_id:
                missing_items.append("Vendor ID")
            if not shipment_id:
                missing_items.append("Shipment ID")
                
            st.warning(f"""
            **Configuration Incomplete**  
            Please provide: {', '.join(missing_items)}
            """)

    # Main content area with improved layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("## 📁 File Processing Center")
        
        # Check if configuration is ready
        config_ready = bool(vendor_id and shipment_id)
        
        if not config_ready:
            st.info("👈 Please complete the configuration in the sidebar before uploading files.")
            return
        
        # Enhanced file upload section
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin-top: 0;">� Document Upload</h3>
            <p>Upload your ASN file for comprehensive validation analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Select EDI File",
            type=['txt', 'edi', 'x12', 'csv'],
            help="Supported formats: .txt, .edi, .x12, .csv (Max size: 10MB)"
        )
        
        if uploaded_file is not None:
            # Professional file info display
            file_size_mb = uploaded_file.size / 1024 / 1024
            st.markdown(f"""
            <div class="info-card">
                <h4>📄 File Information</h4>
                <ul>
                    <li><strong>Filename:</strong> {uploaded_file.name}</li>
                    <li><strong>Size:</strong> {file_size_mb:.2f} MB ({uploaded_file.size:,} bytes)</li>
                    <li><strong>Type:</strong> {uploaded_file.type or 'Unknown'}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced file preview
            try:
                file_content = uploaded_file.read().decode('utf-8')
                uploaded_file.seek(0)  # Reset file pointer
                
                with st.expander("📖 File Content Preview", expanded=False):
                    preview_length = min(500, len(file_content))
                    st.code(file_content[:preview_length] + ("..." if len(file_content) > preview_length else ""), language="text")
                    if len(file_content) > preview_length:
                        st.caption(f"Showing first {preview_length} of {len(file_content)} characters")
                
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
                return
            
            # Auto-detect shipment type and update config
            detected_modules = detect_shipment_type(file_content)
            st.session_state['detected_modules'] = detected_modules
            
            # Display detected modules
            st.markdown("### 🔍 Detected Modules")
            st.write(get_module_description(detected_modules))
            
            # Enhanced validation button
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔍 Execute Validation Analysis", type="primary", use_container_width=True):
                validate_file(uploaded_file, {
                    'vendor_id': vendor_id,
                    'shipment_id': shipment_id,
                    'state_code': state_code,
                    'state_name': selected_state,
                    'detected_modules': detected_modules
                })
        else:
            # Professional empty state
            st.markdown("""
            <div class="metric-card" style="text-align: center; padding: 3rem;">
                <h3>📁 No File Selected</h3>
                <p>Upload an EDI file to begin validation analysis</p>
                <small>Supported formats: .txt, .edi, .x12, .csv</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("## 📊 Analytics Dashboard")
        if 'validation_results' not in st.session_state:
            st.markdown("""
            <div class="metric-card" style="text-align: center;">
                <h4>⏳ Awaiting Analysis</h4>
                <p>Upload and validate a file to view metrics</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            display_analytics_dashboard()

def display_analytics_dashboard():
    """Display enhanced analytics dashboard"""
    if 'validation_results' in st.session_state:
        results = st.session_state['validation_results']
        
        # Status indicator
        if results['summary']['is_ready']:
            st.markdown("""
            <div class="success-card">
                <span class="status-indicator status-ready"></span>
                <strong>Ready for Submission</strong>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="error-card">
                <span class="status-indicator status-error"></span>
                <strong>Requires Attention</strong>
            </div>
            """, unsafe_allow_html=True)
        
        # Metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Validations", results['summary']['total_validations'])
            st.metric("Errors", results['summary']['total_errors'])
        with col2:
            st.metric("Warnings", results['summary']['total_warnings'])
            success_rate = ((results['summary']['total_validations'] - len([v for v in results['validations'].values() if v.get('errors')])) / max(1, results['summary']['total_validations']) * 100)
            st.metric("Success Rate", f"{success_rate:.0f}%")

def validate_file(uploaded_file, config):
    """Execute comprehensive validation analysis"""
    
    # Professional progress indicators
    progress_container = st.container()
    with progress_container:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin-top: 0;">🔄 Executing Validation Analysis</h3>
            <p>Processing your ASN file through comprehensive validation checks...</p>
        </div>
        """, unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    try:
        # Initialize comprehensive results structure
        results = {
            'file_info': {
                'name': uploaded_file.name,
                'size': uploaded_file.size,
                'timestamp': datetime.now().isoformat(),
                'format_detected': 'EDI X12'
            },
            'config': config,
            'validations': {},
            'summary': {
                'total_errors': 0,
                'total_warnings': 0,
                'total_validations': 0,
                'is_ready': False,
                'processing_time': None
            }
        }
        
        start_time = datetime.now()
        
        # Read and parse file content
        status_text.markdown("🔍 **Analyzing file structure...**")
        progress_bar.progress(0.1)
        
        file_content = uploaded_file.read().decode('utf-8')
        file_handler = FileHandler()
        parsed_data = file_handler.parse_edi_file(file_content)
        
        # Configure validation pipeline based on detected modules
        validation_pipeline = []
        detected_modules = config.get('detected_modules', {'vendorladon': True, 'coldchain': False})
        
        # VendorLadon module - always active
        if detected_modules['vendorladon']:
            validation_pipeline.extend([
                ('edi', 'EDI Structure Compliance'),
                ('gstin', 'GSTIN Tax ID Validation'),
                ('products', 'Product Code Verification'),
                ('timing', 'ASN Timing Analysis'),
                ('certificates', 'Certificate Security Check')
            ])
        
        # ColdChain module - conditionally active
        if detected_modules['coldchain']:
            validation_pipeline.append(('coldchain', 'Cold Chain Compliance Check'))
        
        total_steps = len(validation_pipeline)
        
        # Execute validation pipeline
        for i, (validation_type, validation_name) in enumerate(validation_pipeline):
            progress = 0.1 + (0.8 * (i + 1) / total_steps)
            status_text.markdown(f"⚙️ **Executing: {validation_name}**")
            progress_bar.progress(progress)
            
            # Import and execute appropriate validator
            if validation_type == 'edi':
                validator = EDIValidator()
            elif validation_type == 'gstin':
                validator = GSTINValidator()
            elif validation_type == 'products':
                validator = ProductValidator()
            elif validation_type == 'timing':
                validator = TimingValidator()
            elif validation_type == 'certificates':
                validator = CertificateValidator()
            elif validation_type == 'coldchain':
                validator = ColdChainValidator()
            
            validation_result = validator.validate(parsed_data, config)
            results['validations'][validation_type] = validation_result
            
            # Aggregate results
            results['summary']['total_errors'] += len(validation_result.get('errors', []))
            results['summary']['total_warnings'] += len(validation_result.get('warnings', []))
            results['summary']['total_validations'] += 1
        
        # Finalize analysis
        status_text.markdown("✅ **Finalizing analysis results...**")
        progress_bar.progress(0.95)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        results['summary']['processing_time'] = f"{processing_time:.2f}s"
        results['summary']['is_ready'] = results['summary']['total_errors'] == 0
        
        # Store results and complete
        st.session_state['validation_results'] = results
        
        progress_bar.progress(1.0)
        status_text.markdown("🎯 **Analysis Complete!**")
        
        # Brief delay for UX, then clear progress and show results
        import time
        time.sleep(1)
        progress_container.empty()
        
        # Display comprehensive results
        display_validation_results(results)
        
    except Exception as e:
        st.error(f"❌ **Validation Analysis Failed**: {str(e)}")
        status_text.markdown("❌ **Analysis encountered an error**")
        
        # Display error details in professional format
        st.markdown(f"""
        <div class="error-card">
            <h4>🚨 Processing Error</h4>
            <p><strong>Error:</strong> {str(e)}</p>
            <p><strong>Recommendation:</strong> Verify file format and try again</p>
        </div>
        """, unsafe_allow_html=True)

def display_validation_results(results):
    """Display enhanced validation results"""
    st.markdown("## 📊 Validation Analysis Results")
    
    # Executive Summary Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if results['summary']['is_ready']:
            st.markdown("""
            <div class="success-card">
                <div style="text-align: center;">
                    <h3 style="margin: 0;">✅</h3>
                    <h4 style="margin: 0.5rem 0;">Ready</h4>
                    <p style="margin: 0; font-size: 0.9rem;">No critical issues</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="error-card">
                <div style="text-align: center;">
                    <h3 style="margin: 0;">❌</h3>
                    <h4 style="margin: 0.5rem 0;">Not Ready</h4>
                    <p style="margin: 0; font-size: 0.9rem;">Requires fixes</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="error-card">
            <div style="text-align: center;">
                <h3 style="margin: 0; color: #dc3545;">{results['summary']['total_errors']}</h3>
                <h4 style="margin: 0.5rem 0;">Critical Errors</h4>
                <p style="margin: 0; font-size: 0.9rem;">Must be resolved</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="warning-card">
            <div style="text-align: center;">
                <h3 style="margin: 0; color: #856404;">{results['summary']['total_warnings']}</h3>
                <h4 style="margin: 0.5rem 0;">Warnings</h4>
                <p style="margin: 0; font-size: 0.9rem;">Should review</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="info-card">
            <div style="text-align: center;">
                <h3 style="margin: 0; color: #0c5460;">{results['summary']['total_validations']}</h3>
                <h4 style="margin: 0.5rem 0;">Validations</h4>
                <p style="margin: 0; font-size: 0.9rem;">Total executed</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Detailed Results with Enhanced UI
    st.markdown("### 🔍 Detailed Analysis")
    
    tabs = st.tabs([f"📋 {vtype.upper()}" for vtype in results['validations'].keys()])
    
    for i, (validation_type, validation_result) in enumerate(results['validations'].items()):
        with tabs[i]:
            # Special handling for cold chain validation
            if validation_type == 'coldchain':
                display_coldchain_results(validation_result)
            else:
                display_standard_validation_results(validation_result)

    # Enhanced Report Download Section
    st.markdown("---")
    st.markdown("### 📋 Export & Reporting")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card" style="text-align: center;">
            <h4>📄 Technical Report</h4>
            <p>JSON format for system integration</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📄 Generate JSON Report", use_container_width=True):
            report_generator = ReportGenerator()
            json_report = report_generator.generate_json_report(results)
            st.download_button(
                label="⬇️ Download JSON",
                data=json_report,
                file_name=f"vendorladon_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    with col2:
        st.markdown("""
        <div class="metric-card" style="text-align: center;">
            <h4>📊 Business Report</h4>
            <p>CSV format for analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 Generate CSV Report", use_container_width=True):
            report_generator = ReportGenerator()
            csv_report = report_generator.generate_csv_report(results)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_report,
                file_name=f"vendorladon_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col3:
        st.markdown("""
        <div class="metric-card" style="text-align: center;">
            <h4>👁️ Data Preview</h4>
            <p>Raw validation data</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("👁️ View Raw Data", use_container_width=True):
            with st.expander("📊 Raw Validation Data", expanded=True):
                st.json(results)

def display_coldchain_results(validation_result):
    """Display enhanced cold chain validation results"""
    if validation_result.get('overall_status') == 'APPROVED':
        st.markdown("""
        <div class="success-card">
            <h5 style="margin-top: 0;">🧊✅ Cold Chain Compliance Approved</h5>
            <p>All temperature monitoring and compliance checks passed successfully.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show detailed metrics
        col1, col2, col3 = st.columns(3)
        
        if 'sensor_health' in validation_result:
            sensor_health = validation_result['sensor_health']
            with col1:
                st.metric("Sensor Health", sensor_health.get('data_quality', 'N/A'))
                
        if 'spoilage_risk' in validation_result:
            spoilage_risk = validation_result['spoilage_risk']
            with col2:
                risk_level = spoilage_risk.get('risk_level', 'UNKNOWN')
                risk_score = spoilage_risk.get('risk_score', 0)
                st.metric("Spoilage Risk", f"{risk_level} ({risk_score:.1%})")
                
        if 'document_compliance' in validation_result:
            docs = validation_result['document_compliance']
            compliance_count = sum([docs.get('fssai_valid', False), 
                                  docs.get('sanitation_valid', False), 
                                  docs.get('calibration_valid', False)])
            with col3:
                st.metric("Document Compliance", f"{compliance_count}/3")
                
    elif validation_result.get('overall_status') == 'BLOCKED':
        st.markdown("""
        <div class="error-card">
            <h5 style="margin-top: 0;">🧊❌ Cold Chain Compliance Failed</h5>
            <p>Critical issues detected that prevent shipment approval.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if validation_result.get('blocking_issues'):
            st.markdown("#### 🚨 Blocking Issues")
            for issue in validation_result['blocking_issues']:
                st.markdown(f"""
                <div class="error-card">
                    <p><strong>Critical:</strong> {issue}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Show warnings if any
    if validation_result.get('warnings'):
        st.markdown("#### ⚠️ Advisory Notices")
        for warning in validation_result['warnings']:
            st.markdown(f"""
            <div class="warning-card">
                <p><strong>Warning:</strong> {warning}</p>
            </div>
            """, unsafe_allow_html=True)

def display_standard_validation_results(validation_result):
    """Display standard validation results (existing logic)"""
    if validation_result.get('errors'):
        st.markdown("#### 🚨 Critical Issues")
        for j, error in enumerate(validation_result['errors'], 1):
            st.markdown(f"""
            <div class="error-card">
                <h5 style="margin-top: 0;">Error #{j}: {error.get('message', 'Unknown error')}</h5>
                <p><strong>Segment:</strong> {error.get('segment', 'N/A')}</p>
                <p><strong>Details:</strong> {error.get('details', 'No details')}</p>
                <p><strong>💡 Resolution:</strong> {error.get('suggestion', 'No suggestion')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    if validation_result.get('warnings'):
        st.markdown("#### ⚠️ Advisory Notices")
        for j, warning in enumerate(validation_result['warnings'], 1):
            st.markdown(f"""
            <div class="warning-card">
                <h5 style="margin-top: 0;">Warning #{j}: {warning.get('message', 'Unknown warning')}</h5>
                <p><strong>Segment:</strong> {warning.get('segment', 'N/A')}</p>
                <p><strong>Details:</strong> {warning.get('details', 'No details')}</p>
                <p><strong>💡 Recommendation:</strong> {warning.get('suggestion', 'No suggestion')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    if validation_result.get('success'):
        st.markdown(f"""
        <div class="success-card">
            <h5 style="margin-top: 0;">✅ Validation Successful</h5>
            <p>{validation_result.get('details', 'All checks passed successfully')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    if not validation_result.get('errors') and not validation_result.get('warnings') and not validation_result.get('success'):
        st.markdown("""
        <div class="info-card">
            <h5 style="margin-top: 0;">ℹ️ No Issues Found</h5>
            <p>This validation completed without any issues to report.</p>
        </div>
        """, unsafe_allow_html=True)

def display_coldchain_validation_results(validation_result):
    """Display ColdChain validation results with enhanced IoT and ML displays"""
    
    # Temperature Monitoring Section
    if 'temperature_data' in validation_result:
        temp_data = validation_result['temperature_data']
        st.markdown("#### 🌡️ Temperature Monitoring")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_temp = temp_data.get('average_temp', 0)
            st.metric("Average Temperature", f"{avg_temp}°C", 
                     delta=f"{avg_temp - temp_data.get('target_temp', 4):.1f}°C from target")
        
        with col2:
            min_temp = temp_data.get('min_temp', 0)
            max_temp = temp_data.get('max_temp', 0)
            st.metric("Temperature Range", f"{min_temp}°C - {max_temp}°C")
        
        with col3:
            stability = temp_data.get('stability_score', 0)
            st.metric("Stability Score", f"{stability}%", 
                     delta="Good" if stability > 85 else "Poor")
    
    # ML Risk Prediction
    if 'spoilage_risk' in validation_result:
        risk_data = validation_result['spoilage_risk']
        st.markdown("#### 🤖 AI Risk Analysis")
        
        risk_level = risk_data.get('risk_level', 'Unknown')
        confidence = risk_data.get('confidence', 0)
        
        if risk_level == 'LOW':
            risk_color = "#28a745"
            risk_icon = "✅"
        elif risk_level == 'MEDIUM':
            risk_color = "#ffc107"
            risk_icon = "⚠️"
        else:
            risk_color = "#dc3545"
            risk_icon = "🚨"
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {risk_color}20, {risk_color}10); 
                    border-left: 4px solid {risk_color}; padding: 15px; border-radius: 8px;">
            <h5 style="color: {risk_color}; margin-top: 0;">{risk_icon} Spoilage Risk: {risk_level}</h5>
            <p><strong>Confidence:</strong> {confidence:.1%}</p>
            <p><strong>Prediction:</strong> {risk_data.get('prediction_details', 'No details available')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # IoT Sensor Status
    if 'iot_status' in validation_result:
        iot_data = validation_result['iot_status']
        st.markdown("#### 📡 IoT Sensor Network")
        
        for sensor_id, sensor_data in iot_data.items():
            status = sensor_data.get('status', 'Unknown')
            battery = sensor_data.get('battery_level', 0)
            
            status_color = "#28a745" if status == "ACTIVE" else "#dc3545"
            status_icon = "🟢" if status == "ACTIVE" else "🔴"
            
            st.markdown(f"""
            <div style="background: #f8f9fa; border: 1px solid #dee2e6; padding: 10px; 
                        border-radius: 8px; margin-bottom: 10px;">
                <h6 style="margin-top: 0;">{status_icon} Sensor {sensor_id}</h6>
                <p><strong>Status:</strong> <span style="color: {status_color};">{status}</span></p>
                <p><strong>Battery:</strong> {battery}% | <strong>Last Reading:</strong> {sensor_data.get('last_reading', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Compliance Check Results
    if 'compliance' in validation_result:
        compliance_data = validation_result['compliance']
        st.markdown("#### 📋 Compliance Status")
        
        for check_type, result in compliance_data.items():
            check_status = result.get('status', 'UNKNOWN')
            check_icon = "✅" if check_status == "COMPLIANT" else "❌"
            check_color = "#28a745" if check_status == "COMPLIANT" else "#dc3545"
            
            st.markdown(f"""
            <div style="border-left: 4px solid {check_color}; padding: 10px; margin-bottom: 10px; 
                        background: {check_color}10;">
                <h6 style="margin-top: 0; color: {check_color};">{check_icon} {check_type.replace('_', ' ').title()}</h6>
                <p><strong>Status:</strong> {check_status}</p>
                <p><strong>Details:</strong> {result.get('details', 'No details available')}</p>
            </div>
            """, unsafe_allow_html=True)
     # Display any standard errors/warnings
    display_standard_validation_results(validation_result)

if __name__ == "__main__":
    main()
