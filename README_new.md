⚡ **GlitchGuard – Intelligent Supply Chain Validation Platform**
🔗 **[Access GlitchGuard Platform](https://ashmitha247-retail--app-zurwdh.streamlit.app)**

Enterprise-grade validation platform designed to **catch mistakes before they reach Walmart's loading docks**. By validating shipments at the source, GlitchGuard helps reduce rejections, spoilage, and compliance failures—*before* they become costly.

---

## 🎯 What is GlitchGuard?

GlitchGuard is a modular shipment validation system built to **act as a net that catches issues early** in the supply chain—*not after the damage is done*.

To make this possible, we've designed two focused validation modules that work in tandem:

1. **VendorLadon Module** – ensures digital documentation like EDI files are accurate and legally compliant.
2. **ColdChain Compliance Module** – validates temperature-sensitive shipments using IoT data, sensor health checks, and spoilage risk prediction.

No manual setup is needed—GlitchGuard detects shipment type and activates the right modules automatically.

---

## 🧩 How GlitchGuard Works

### 1. Smart Shipment Detection

* Upload your shipment file (.txt, .edi, .x12, .csv)
* System auto-identifies:

  * Shipment type (standard or cold-chain)
  * Required validations
* VendorLadon and ColdChain modules run based on shipment contents.

### 2. Real-Time Validation Pipeline

* Runs all checks in parallel
* Connects to IoT sensors for live temperature and device health data
* Applies AI-based spoilage prediction
* Validates legal documents like FSSAI licenses and sanitation certificates

### 3. Decision and Reporting

* Color-coded results dashboard
* Exportable compliance reports with audit trails
* Failures flagged before shipments are dispatched

---

## 🔑 Key Terms Explained

* **EDI (Electronic Data Interchange):** Digital files used for sharing shipment data between vendors and retailers.
* **ASN (Advance Shipment Notice):** Notification containing product and delivery details.
* **GSTIN:** India's Goods and Services Tax Identification Number—validated for format and state consistency.
* **Cold-Chain Shipment:** Any shipment requiring controlled temperature and handling conditions.
* **IoT Sensor Monitoring:** Collects live data about temperature, sensor calibration age, and sensor status.
* **AI Spoilage Prediction:** Uses environmental and route data to estimate spoilage risk levels before dispatch.
* **Cryptographic Audit Trail:** Securely logs all validations and data changes for tamper-proof compliance records.

---

## 🧊 ColdChain Compliance Module

This module ensures **temperature-sensitive shipments are validated thoroughly before they leave the warehouse**.

### Key Capabilities:

* **IoT Integration:**

  * Live temperature feeds
  * Sensor calibration and battery checks
  * Multi-zone monitoring
  * Data stability scoring

* **AI Risk Prediction:**

  * Spoilage risk classified as LOW / MEDIUM / HIGH
  * Model trained on real shipment data
  * Factors in route history, humidity, sensor variance

* **Legal Compliance Checks:**

  * FSSAI license validation (14-digit format + expiry)
  * Sanitation certificate checks
  * Sensor calibration status (annual requirement)
  * All validations logged cryptographically

* **Preventive Focus:**
  Unlike many existing systems that only detect issues *after* arrival, this module stops shipments that are non-compliant or at high spoilage risk—*before they're dispatched*.

---

## 📋 VendorLadon Module

Ensures the digital paperwork behind every shipment is **accurate, timely, and legally valid**.

### What It Checks:

| Validation Type       | What It Does                                              |
| --------------------- | --------------------------------------------------------- |
| EDI File Format       | Ensures structure follows Retail India's schema           |
| GSTIN Format          | Confirms 14-digit tax ID is valid and state-aligned       |
| Product Code Matching | Verifies all product SKUs exist in the retailer's catalog |
| ASN Timing            | Checks if shipment notice is within expected window       |
| AS2 Certificate       | Validates secure data exchange via certificate matching   |

All of these are run automatically when a shipment file is uploaded.

---

## 👤 Who Uses the Platform?

* **Vendors:**

  * Upload their EDI files
  * Select shipment type (ColdChain is auto-detected)
  * Monitor validation status in real-time
  * Fix issues before Walmart receives the shipment

* **Compliance Teams / 3PLs:**

  * Review dashboard insights, sensor data, and audit trails
  * Generate downloadable compliance reports
  * Ensure all documentation and risk scores pass internal thresholds

---

## 🚀 Getting Started

1. **Launch GlitchGuard**

   * Click the platform link and open the dashboard

2. **Set Up Shipment Details**

   * Vendor ID
   * Shipment ID
   * Indian state for GSTIN verification
   * (Optional) Enable ColdChain if handling temperature-sensitive goods

3. **Upload EDI File**

   * Drag and drop supported formats
   * Platform will run all applicable checks

4. **Review Results**

   * See progress indicators and validation outcomes
   * Download professional compliance reports
   * Fix any flagged issues before dispatch

---

## 🔐 Supported File Types

* `.txt`, `.edi`, `.x12`, `.csv` (Under 10MB)

## 🖥️ Browser Compatibility

* Chrome ✅ (recommended for all features)
* Firefox ✅
* Edge ✅
* Safari ✅ (basic ColdChain supported)

---

## 🆘 Troubleshooting

| Problem                          | Suggested Fix                                                             |
| -------------------------------- | ------------------------------------------------------------------------- |
| ColdChain not activating         | Ensure product is marked temperature-sensitive and module is enabled      |
| Spoilage risk too high           | Review route temperature history, sensor accuracy, and handling protocols |
| EDI file not uploading           | Ensure format is supported and file size is under 10MB                    |
| Sensor data looks wrong          | Check calibration date and battery level in the IoT panel                 |
| Compliance document failed check | Double-check FSSAI and sanitation expiry and formatting                   |

---
