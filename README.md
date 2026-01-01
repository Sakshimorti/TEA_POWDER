# 🍵 GOLD Tea Powder - Sales Management System

A comprehensive Streamlit application for managing tea powder sales with **Google Sheets integration** for real-time data persistence.

## ✨ Features

### 🏠 Dashboard
- Real-time sales overview
- Key metrics (Total Sales, Orders, Items Sold, Pending Payments)
- Sales charts by Village and Tea Type
- Period filters (Today, This Week, This Month, All Time)

### ➕ New Sale Entry
- Auto-filled date and day
- Village auto-selection based on day
- Customer searchable dropdown with "Add New Customer" option
- Tea Type and Packaging selection
- Auto-calculated totals
- Payment status tracking (Paid, Half paid, Not paid)

### 📋 View & Manage Sales
- Full sales history with filters
- Filter by date range, village, payment status
- Edit existing entries
- Delete entries
- Export to Excel

### 📊 Reports & Analytics
- Daily Summary with trends
- Weekly Summary
- Monthly Summary with charts
- Customer-wise Report
- Village-wise Report
- Product-wise Report (by Tea Type & Packaging)

### 💰 Pending Payments
- Total pending amount overview
- Customer-wise pending breakdown
- Village filter
- Export pending report to Excel

### ⚙️ Settings
- Update package prices
- Add/Delete customers
- View village information

### 🔐 Security
- Password protected login
- Default password: `gold123`

---

## 🚀 Deployment to Streamlit Cloud

### Step 1: Set Up Google Sheets API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)

2. Create a new project (or select existing)

3. Enable APIs:
   - Search for "Google Sheets API" → Enable
   - Search for "Google Drive API" → Enable

4. Create Service Account:
   - Go to "IAM & Admin" → "Service Accounts"
   - Click "Create Service Account"
   - Give it a name (e.g., "streamlit-sheets")
   - Click "Create and Continue"
   - Skip the optional steps and click "Done"

5. Create Key:
   - Click on the service account you created
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Select "JSON" → "Create"
   - Save the downloaded JSON file

### Step 2: Push to GitHub

```bash
git add .
git commit -m "Add Google Sheets integration and new features"
git push
```

### Step 3: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)

2. Click "New app"

3. Select your repository:
   - Repository: `Sakshimorti/TEA_POWDER`
   - Branch: `main`
   - Main file path: `app.py`

4. Click "Advanced settings" → "Secrets"

5. Add your secrets in TOML format:

```toml
# App password
app_password = "your_secure_password"

# Google Service Account (paste contents of your JSON key file)
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_KEY_HERE\n-----END PRIVATE KEY-----\n"
client_email = "your-service@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

6. Click "Deploy!"

### Step 4: Share the Google Sheet

After first run, a Google Sheet named "GOLD_Tea_Sales" will be created. To access it:

1. Find the sheet in Google Drive of your service account
2. Share it with your personal Gmail for easy access
3. Or access via the service account email

---

## 📁 Project Structure

```
TEA_POWDER/
├── app.py                    # Main application
├── requirements.txt          # Python dependencies
├── .python-version          # Python version for Streamlit Cloud
├── secrets.toml.example     # Template for secrets
├── customer_database.json   # Local customer backup
├── pricing_database.json    # Local pricing backup
└── README.md               # This file
```

---

## 🔧 Local Development

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Set Up Secrets

Create `.streamlit/secrets.toml`:

```bash
mkdir .streamlit
cp secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your credentials
```

### Run Locally

```bash
streamlit run app.py
```

---

## 📊 Google Sheets Structure

The app creates 3 sheets automatically:

### Sales Sheet
| Column | Description |
|--------|-------------|
| ID | Unique identifier |
| Date | Sale date |
| Day | Day of week |
| Village | Village name |
| Customer Name | Customer |
| Brand | GOLD Tea Powder |
| Tea Type | Mix/Barik |
| Packaging | 100gm/250gm/500gm/1kg |
| Rate | Price per unit |
| Quantity | Number of units |
| Total Amount | Rate × Quantity |
| Payment Status | Paid/Half paid/Not paid |
| Amount Paid | Amount received |
| Balance | Pending amount |
| Created At | Entry timestamp |
| Updated At | Last modified |

### Customers Sheet
| Column | Description |
|--------|-------------|
| Village | Village name |
| Customer Name | Customer name |
| Added On | Date added |

### Pricing Sheet
| Column | Description |
|--------|-------------|
| Package | Package size |
| Rate | Current price |
| Updated On | Last updated |

---

## 💼 Business Configuration

### Tea Types
- Mix
- Barik

### Packaging & Default Rates
- 100gm → ₹35
- 250gm → ₹85
- 500gm → ₹170
- 1kg → ₹350

### Villages & Day Mapping
| Day | Village |
|-----|---------|
| Monday | Harali KH |
| Friday | Bardwadi |
| Saturday | vairgwadi |
| Sunday | Harali BK |

---

## 🔒 Security Notes

- Never commit `secrets.toml` to GitHub
- Change the default password after deployment
- The service account JSON should be kept secure
- Use Streamlit Cloud's secrets management for production

---

## 📞 Support

For issues or feature requests, contact the developer.

---

© 2026 GOLD Tea Powder Sales Management System
