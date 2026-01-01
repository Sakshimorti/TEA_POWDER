"""
GOLD Tea Powder - Sales Management Application
A comprehensive Streamlit app with Google Sheets integration
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import io
import gspread
from google.oauth2.service_account import Credentials

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="GOLD Tea Powder - Sales Management",
    page_icon="🍵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CONSTANTS
# ============================================
BRAND_NAME = "GOLD Tea Powder"
TEA_TYPES = ["Mix", "Barik"]
VILLAGES = ["vairgwadi", "Bardwadi", "Harali KH", "Harali BK"]
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
PAYMENT_OPTIONS = ["Paid", "Half paid", "Not paid"]

DAY_TO_VILLAGE = {
    "Monday": "Harali KH",
    "Friday": "Bardwadi",
    "Saturday": "vairgwadi",
    "Sunday": "Harali BK"
}

DEFAULT_PRICING = {
    "100gm": 35,
    "250gm": 85,
    "500gm": 170,
    "1kg": 350
}

# Google Sheets Configuration
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Sheet names
SALES_SHEET = "Sales"
CUSTOMERS_SHEET = "Customers"
PRICING_SHEET = "Pricing"
SETTINGS_SHEET = "Settings"

# ============================================
# CUSTOM CSS FOR BETTER UI
# ============================================
st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a472a 0%, #2d5a3d 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card h3 {
        margin: 0;
        font-size: 2rem;
    }
    
    .metric-card p {
        margin: 5px 0 0 0;
        opacity: 0.9;
    }
    
    /* Success card */
    .success-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
    }
    
    /* Warning card */
    .warning-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
    }
    
    /* Info card */
    .info-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
    }
    
    /* Page title */
    .page-title {
        background: linear-gradient(90deg, #1a472a 0%, #2d5a3d 100%);
        padding: 15px 25px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Button styling */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
    }
    
    .stSelectbox > div > div {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# AUTHENTICATION
# ============================================
def check_password():
    """Returns True if the user has entered the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets.get("app_password", "gold123"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show login
        st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h1>🍵 GOLD Tea Powder</h1>
            <h3>Sales Management System</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input(
                "Enter Password", 
                type="password", 
                on_change=password_entered, 
                key="password",
                placeholder="Enter your password"
            )
            st.caption("Default password: gold123")
        return False
    
    elif not st.session_state["password_correct"]:
        # Password incorrect
        st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h1>🍵 GOLD Tea Powder</h1>
            <h3>Sales Management System</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input(
                "Enter Password", 
                type="password", 
                on_change=password_entered, 
                key="password",
                placeholder="Enter your password"
            )
            st.error("😕 Incorrect password. Please try again.")
        return False
    
    return True

# ============================================
# GOOGLE SHEETS FUNCTIONS
# ============================================
@st.cache_resource
def get_google_sheets_connection():
    """Create a connection to Google Sheets"""
    try:
        # Try to get credentials from Streamlit secrets
        if "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=SCOPES
            )
            client = gspread.authorize(creds)
            return client
        else:
            st.warning("⚠️ Google Sheets not configured. Using local storage.")
            return None
    except Exception as e:
        st.warning(f"⚠️ Could not connect to Google Sheets: {str(e)}")
        return None

def get_or_create_spreadsheet(client, spreadsheet_name="GOLD_Tea_Sales"):
    """Get or create the main spreadsheet"""
    try:
        spreadsheet = client.open(spreadsheet_name)
    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(spreadsheet_name)
        # Share with user's email if provided in secrets
        if "user_email" in st.secrets:
            try:
                spreadsheet.share(st.secrets["user_email"], perm_type='user', role='writer')
            except Exception as e:
                st.warning(f"Could not share sheet: {str(e)}")
        # Make it accessible to anyone with link (optional - for easy access)
        try:
            spreadsheet.share('', perm_type='anyone', role='writer')
        except Exception:
            pass
    return spreadsheet

def get_or_create_worksheet(spreadsheet, sheet_name, headers=None):
    """Get or create a worksheet with headers"""
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
        if headers:
            worksheet.append_row(headers)
    return worksheet

def init_google_sheets():
    """Initialize all Google Sheets worksheets"""
    client = get_google_sheets_connection()
    if client is None:
        return None
    
    spreadsheet = get_or_create_spreadsheet(client)
    
    # Sales sheet headers
    sales_headers = [
        "ID", "Date", "Day", "Village", "Customer Name", "Brand", 
        "Tea Type", "Packaging", "Rate", "Quantity", "Total Amount",
        "Payment Status", "Amount Paid", "Balance", "Created At", "Updated At"
    ]
    get_or_create_worksheet(spreadsheet, SALES_SHEET, sales_headers)
    
    # Customers sheet headers
    customers_headers = ["Village", "Customer Name", "Added On"]
    get_or_create_worksheet(spreadsheet, CUSTOMERS_SHEET, customers_headers)
    
    # Pricing sheet headers
    pricing_headers = ["Package", "Rate", "Updated On"]
    pricing_ws = get_or_create_worksheet(spreadsheet, PRICING_SHEET, pricing_headers)
    
    # Initialize default pricing if empty
    if len(pricing_ws.get_all_values()) <= 1:
        for package, rate in DEFAULT_PRICING.items():
            pricing_ws.append_row([package, rate, datetime.now().strftime("%Y-%m-%d %H:%M")])
    
    return spreadsheet

# ============================================
# DATA FUNCTIONS
# ============================================
@st.cache_data(ttl=30)
def load_sales_data(_spreadsheet=None):
    """Load all sales data from Google Sheets or local"""
    if _spreadsheet:
        try:
            worksheet = _spreadsheet.worksheet(SALES_SHEET)
            data = worksheet.get_all_records()
            if data:
                df = pd.DataFrame(data)
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                return df
        except Exception as e:
            st.error(f"Error loading sales: {str(e)}")
    
    return pd.DataFrame(columns=[
        "ID", "Date", "Day", "Village", "Customer Name", "Brand",
        "Tea Type", "Packaging", "Rate", "Quantity", "Total Amount",
        "Payment Status", "Amount Paid", "Balance", "Created At", "Updated At"
    ])

@st.cache_data(ttl=60)
def load_customers_data(_spreadsheet=None):
    """Load customers from Google Sheets or local"""
    if _spreadsheet:
        try:
            worksheet = _spreadsheet.worksheet(CUSTOMERS_SHEET)
            data = worksheet.get_all_records()
            customers = {}
            for row in data:
                village = row.get('Village', '')
                customer = row.get('Customer Name', '')
                if village and customer:
                    if village not in customers:
                        customers[village] = []
                    if customer not in customers[village]:
                        customers[village].append(customer)
            return customers
        except Exception as e:
            st.error(f"Error loading customers: {str(e)}")
    
    # Return default customers
    return load_default_customers()

@st.cache_data(ttl=60)
def load_pricing_data(_spreadsheet=None):
    """Load pricing from Google Sheets or local"""
    if _spreadsheet:
        try:
            worksheet = _spreadsheet.worksheet(PRICING_SHEET)
            data = worksheet.get_all_records()
            pricing = {}
            for row in data:
                package = row.get('Package', '')
                rate = row.get('Rate', 0)
                if package:
                    pricing[package] = int(rate)
            if pricing:
                return pricing
        except Exception as e:
            st.error(f"Error loading pricing: {str(e)}")
    
    return DEFAULT_PRICING.copy()

def load_default_customers():
    """Load default customer list"""
    return {
        "vairgwadi": [
            "RatanaBai Gaddiwadar", "Sadhana Patil", "Hausabai Murkute",
            "Murari Patil", "Shivaji Sawant", "Prakash Patil", "Suresh Patil",
            "Anjali Patil", "Chandrkant Sawant", "Tanaji Sutar", "Santosh Gourle",
            "Sachin Kapase", "Anil Dhotare", "Vasant Patil"
        ],
        "Bardwadi": [
            "Basappa Gholrake", "Geeta Gholrake", "Sanjay Gholrake", "Pushpa Gholrake",
            "Shanakar Pujari", "Mahadev Naik", "Hirabai Gholrake", "Surekha Gholrake",
            "Shanata Naik", "Balava Gholrake", "Anada Gholrake", "Kempanna Gholrake",
            "Maruti Gholrake", "Sambhaji Gholrake", "Chandrkant Naik", "Renuka Arun Gholrake",
            "Gaurabai Gholrake", "Vaishali Gholrake", "Akkatai naik", "Lata Naik",
            "Savatri Bhoi", "Ratna Rangnavar", "Mahadev Bhoi", "Prashram Bhoi",
            "Barama Bhoi", "Satyappa Bhoi", "Annappa Bhoi", "Pushpa M Bhoi",
            "Driver Bhoi", "kori", "Kallappa Kaujalagi", "Suresh Kajualagi"
        ],
        "Harali KH": [
            "Sagar Kumbhar", "Shankar Mali", "Shivaji Mali", "Ranjit Chavan",
            "Surekha Bagadi", "Daynashwar Bagadi", "Pandit Gurav", "Gajana Patil",
            "Janadharn Gurav", "Laxman Patil", "Filips Bardaskar", "Chandrkant Kumbhar",
            "Tanji Aapu Kumbhar", "Sagar Banekar", "Datayatra Bandu Kumbhar",
            "Aavubai Kumbhar", "Shivaji Kumbhar", "Chaya Kumbhar", "Gaurabai Kumbhar",
            "Shivaji Kanade", "Siddhava Kanade", "Mayava Kanade", "Anjana Bagadi"
        ],
        "Harali BK": [
            "Vinayak Khanapure", "Ravi Morti", "Vijay Kamble", "Dipak Kamble",
            "Shanakar Kamble", "Sanjay Kamble", "Suresh Kori", "Pundalik Kamble",
            "Parshram Kamble", "Suraj Kamble", "Bharati Khavare", "Narayan Bhalekar",
            "Raju Chavan", "Kavita Kokitkar", "Hari Patake", "Vandana Lohar",
            "Sandip Patil", "Sunil Khavare", "Vimal Khavare", "Aalka Khavare"
        ]
    }

def save_sale(spreadsheet, sale_data):
    """Save a new sale to Google Sheets"""
    if spreadsheet:
        try:
            worksheet = spreadsheet.worksheet(SALES_SHEET)
            
            # Generate unique ID
            all_data = worksheet.get_all_values()
            new_id = len(all_data)
            
            # Calculate balance
            total = sale_data['Total Amount']
            paid = sale_data['Amount Paid']
            balance = total - paid if sale_data['Payment Status'] != 'Paid' else 0
            
            row = [
                new_id,
                sale_data['Date'],
                sale_data['Day'],
                sale_data['Village'],
                sale_data['Customer Name'],
                sale_data['Brand'],
                sale_data['Tea Type'],
                sale_data['Packaging'],
                sale_data['Rate'],
                sale_data['Quantity'],
                sale_data['Total Amount'],
                sale_data['Payment Status'],
                sale_data['Amount Paid'],
                balance,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            worksheet.append_row(row)
            
            # Clear cache to refresh data
            load_sales_data.clear()
            return True
        except Exception as e:
            st.error(f"Error saving sale: {str(e)}")
            return False
    return False

def update_sale(spreadsheet, row_index, updated_data):
    """Update an existing sale"""
    if spreadsheet:
        try:
            worksheet = spreadsheet.worksheet(SALES_SHEET)
            
            # Calculate balance
            total = updated_data['Total Amount']
            paid = updated_data['Amount Paid']
            balance = total - paid if updated_data['Payment Status'] != 'Paid' else 0
            
            # Update the row (row_index + 2 because of header and 1-based index)
            cell_range = f'B{row_index + 2}:P{row_index + 2}'
            values = [[
                updated_data['Date'],
                updated_data['Day'],
                updated_data['Village'],
                updated_data['Customer Name'],
                updated_data['Brand'],
                updated_data['Tea Type'],
                updated_data['Packaging'],
                updated_data['Rate'],
                updated_data['Quantity'],
                updated_data['Total Amount'],
                updated_data['Payment Status'],
                updated_data['Amount Paid'],
                balance,
                worksheet.cell(row_index + 2, 15).value,  # Keep original Created At
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]]
            worksheet.update(cell_range, values)
            
            load_sales_data.clear()
            return True
        except Exception as e:
            st.error(f"Error updating sale: {str(e)}")
            return False
    return False

def delete_sale(spreadsheet, row_index):
    """Delete a sale from Google Sheets"""
    if spreadsheet:
        try:
            worksheet = spreadsheet.worksheet(SALES_SHEET)
            worksheet.delete_rows(row_index + 2)  # +2 for header and 1-based index
            load_sales_data.clear()
            return True
        except Exception as e:
            st.error(f"Error deleting sale: {str(e)}")
            return False
    return False

def add_customer(spreadsheet, village, customer_name):
    """Add a new customer to Google Sheets"""
    if spreadsheet:
        try:
            worksheet = spreadsheet.worksheet(CUSTOMERS_SHEET)
            worksheet.append_row([
                village,
                customer_name.strip(),
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ])
            load_customers_data.clear()
            return True
        except Exception as e:
            st.error(f"Error adding customer: {str(e)}")
            return False
    return False

def delete_customer(spreadsheet, village, customer_name):
    """Delete a customer from Google Sheets"""
    if spreadsheet:
        try:
            worksheet = spreadsheet.worksheet(CUSTOMERS_SHEET)
            data = worksheet.get_all_values()
            for i, row in enumerate(data):
                if len(row) >= 2 and row[0] == village and row[1] == customer_name:
                    worksheet.delete_rows(i + 1)
                    load_customers_data.clear()
                    return True
        except Exception as e:
            st.error(f"Error deleting customer: {str(e)}")
    return False

def update_pricing(spreadsheet, package, new_rate):
    """Update pricing in Google Sheets"""
    if spreadsheet:
        try:
            worksheet = spreadsheet.worksheet(PRICING_SHEET)
            data = worksheet.get_all_values()
            for i, row in enumerate(data):
                if len(row) >= 1 and row[0] == package:
                    worksheet.update_cell(i + 1, 2, new_rate)
                    worksheet.update_cell(i + 1, 3, datetime.now().strftime("%Y-%m-%d %H:%M"))
                    load_pricing_data.clear()
                    return True
        except Exception as e:
            st.error(f"Error updating pricing: {str(e)}")
    return False

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_day_from_date(date):
    """Get day name from date"""
    return date.strftime("%A")

def generate_id():
    """Generate unique ID"""
    return datetime.now().strftime("%Y%m%d%H%M%S")

# ============================================
# PAGE FUNCTIONS
# ============================================
def render_sidebar():
    """Render the sidebar navigation"""
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <h1 style='color: white; margin: 0;'>🍵</h1>
            <h2 style='color: white; margin: 0;'>GOLD Tea</h2>
            <p style='color: #a8d5a2; margin: 5px 0;'>Sales Management</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "📍 Navigation",
            ["🏠 Dashboard", "➕ New Sale", "📋 View Sales", "📊 Reports", 
             "💰 Pending Payments", "⚙️ Settings"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Quick stats
        if 'spreadsheet' in st.session_state and st.session_state.spreadsheet:
            df = load_sales_data(st.session_state.spreadsheet)
            if not df.empty:
                today = datetime.now().date()
                today_sales = df[pd.to_datetime(df['Date']).dt.date == today] if 'Date' in df.columns else pd.DataFrame()
                
                st.markdown("### 📈 Today's Stats")
                st.metric("Sales", len(today_sales))
                if not today_sales.empty and 'Total Amount' in today_sales.columns:
                    st.metric("Revenue", f"₹{today_sales['Total Amount'].sum():,.0f}")
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state["password_correct"] = False
            st.rerun()
        
        st.markdown("""
        <div style='text-align: center; padding: 20px 0; color: #a8d5a2;'>
            <small>© 2026 GOLD Tea Powder</small>
        </div>
        """, unsafe_allow_html=True)
        
        return page

def render_dashboard(spreadsheet):
    """Render the dashboard page"""
    st.markdown("<div class='page-title'><h2>🏠 Dashboard</h2></div>", unsafe_allow_html=True)
    
    df = load_sales_data(spreadsheet)
    
    if df.empty:
        st.info("No sales data yet. Start by adding your first sale!")
        return
    
    # Date filters
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        period = st.selectbox("📅 Period", ["Today", "This Week", "This Month", "All Time"])
    
    # Filter data based on period
    today = datetime.now().date()
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        if period == "Today":
            filtered_df = df[df['Date'].dt.date == today]
        elif period == "This Week":
            week_start = today - timedelta(days=today.weekday())
            filtered_df = df[df['Date'].dt.date >= week_start]
        elif period == "This Month":
            filtered_df = df[(df['Date'].dt.month == today.month) & (df['Date'].dt.year == today.year)]
        else:
            filtered_df = df
    else:
        filtered_df = df
    
    # Key metrics
    st.markdown("### 📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = filtered_df['Total Amount'].sum() if 'Total Amount' in filtered_df.columns else 0
        st.markdown(f"""
        <div class='metric-card'>
            <h3>₹{total_sales:,.0f}</h3>
            <p>Total Sales</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_orders = len(filtered_df)
        st.markdown(f"""
        <div class='success-card'>
            <h3>{total_orders}</h3>
            <p>Total Orders</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_quantity = filtered_df['Quantity'].sum() if 'Quantity' in filtered_df.columns else 0
        st.markdown(f"""
        <div class='info-card'>
            <h3>{total_quantity:,.0f}</h3>
            <p>Items Sold</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        pending = filtered_df[filtered_df['Payment Status'] != 'Paid']['Balance'].sum() if 'Balance' in filtered_df.columns else 0
        st.markdown(f"""
        <div class='warning-card'>
            <h3>₹{pending:,.0f}</h3>
            <p>Pending Amount</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏘️ Sales by Village")
        if 'Village' in filtered_df.columns and 'Total Amount' in filtered_df.columns:
            village_sales = filtered_df.groupby('Village')['Total Amount'].sum().reset_index()
            if not village_sales.empty:
                st.bar_chart(village_sales.set_index('Village'))
    
    with col2:
        st.markdown("### 🍵 Sales by Tea Type")
        if 'Tea Type' in filtered_df.columns and 'Total Amount' in filtered_df.columns:
            tea_sales = filtered_df.groupby('Tea Type')['Total Amount'].sum().reset_index()
            if not tea_sales.empty:
                st.bar_chart(tea_sales.set_index('Tea Type'))
    
    # Recent sales
    st.markdown("### 🕐 Recent Sales")
    if not filtered_df.empty:
        display_df = filtered_df.tail(10).iloc[::-1]
        display_cols = ['Date', 'Customer Name', 'Village', 'Tea Type', 'Packaging', 'Quantity', 'Total Amount', 'Payment Status']
        available_cols = [col for col in display_cols if col in display_df.columns]
        st.dataframe(display_df[available_cols], use_container_width=True, hide_index=True)

def render_new_sale(spreadsheet):
    """Render the new sale entry page"""
    st.markdown("<div class='page-title'><h2>➕ New Sale Entry</h2></div>", unsafe_allow_html=True)
    
    # Load data
    customers = load_customers_data(spreadsheet)
    pricing = load_pricing_data(spreadsheet)
    
    with st.form("sale_form", clear_on_submit=True):
        # Row 1: Date and Day
        col1, col2 = st.columns(2)
        with col1:
            selected_date = st.date_input("📅 Date", value=datetime.today())
        with col2:
            auto_day = get_day_from_date(selected_date)
            selected_day = st.selectbox("📆 Day", options=DAYS_OF_WEEK, index=DAYS_OF_WEEK.index(auto_day))
        
        # Row 2: Village and Customer
        col3, col4 = st.columns(2)
        with col3:
            auto_village = DAY_TO_VILLAGE.get(selected_day, VILLAGES[0])
            village_index = VILLAGES.index(auto_village) if auto_village in VILLAGES else 0
            village = st.selectbox("🏘️ Village", options=VILLAGES, index=village_index)
        
        with col4:
            customer_list = customers.get(village, [])
            customer_options = ["-- Select Customer --"] + customer_list + ["➕ Add New Customer"]
            customer_selection = st.selectbox("👤 Customer", options=customer_options)
        
        # New customer input
        new_customer_name = ""
        if customer_selection == "➕ Add New Customer":
            new_customer_name = st.text_input("Enter New Customer Name")
        
        # Row 3: Tea Type and Packaging
        col5, col6 = st.columns(2)
        with col5:
            tea_type = st.selectbox("🍵 Tea Type", options=TEA_TYPES)
        with col6:
            packaging = st.selectbox("📦 Packaging", options=list(pricing.keys()))
        
        # Row 4: Quantity and Rate
        col7, col8 = st.columns(2)
        with col7:
            quantity = st.number_input("🔢 Quantity", min_value=1, value=1, step=1)
        with col8:
            rate = pricing.get(packaging, 0)
            st.number_input("💵 Rate (₹)", value=rate, disabled=True)
        
        # Total
        total_amount = rate * quantity
        st.markdown(f"### 💰 Total Amount: ₹{total_amount:,.0f}")
        
        # Payment
        st.markdown("---")
        st.markdown("### 💳 Payment Details")
        col9, col10 = st.columns(2)
        with col9:
            payment_status = st.selectbox("Payment Status", options=PAYMENT_OPTIONS)
        with col10:
            amount_paid = 0.0
            if payment_status == "Paid":
                amount_paid = float(total_amount)
            elif payment_status == "Half paid":
                amount_paid = st.number_input("Amount Paid (₹)", min_value=0.0, max_value=float(total_amount), value=0.0, step=10.0)
        
        # Submit
        submitted = st.form_submit_button("💾 Save Sale", use_container_width=True, type="primary")
        
        if submitted:
            # Validate
            final_customer = new_customer_name.strip() if customer_selection == "➕ Add New Customer" else customer_selection
            
            if final_customer in ["-- Select Customer --", ""] or not final_customer:
                st.error("⚠️ Please select or enter a customer name!")
            else:
                # Add new customer if needed
                if customer_selection == "➕ Add New Customer" and new_customer_name.strip():
                    add_customer(spreadsheet, village, new_customer_name.strip())
                
                # Save sale
                sale_data = {
                    "Date": selected_date.strftime("%Y-%m-%d"),
                    "Day": selected_day,
                    "Village": village,
                    "Customer Name": final_customer,
                    "Brand": BRAND_NAME,
                    "Tea Type": tea_type,
                    "Packaging": packaging,
                    "Rate": rate,
                    "Quantity": quantity,
                    "Total Amount": total_amount,
                    "Payment Status": payment_status,
                    "Amount Paid": amount_paid
                }
                
                if save_sale(spreadsheet, sale_data):
                    st.success("✅ Sale saved successfully!")
                    st.balloons()
                else:
                    st.error("❌ Failed to save sale. Please try again.")

def render_view_sales(spreadsheet):
    """Render the view/edit/delete sales page"""
    st.markdown("<div class='page-title'><h2>📋 View & Manage Sales</h2></div>", unsafe_allow_html=True)
    
    df = load_sales_data(spreadsheet)
    
    if df.empty:
        st.info("No sales data available.")
        return
    
    # Filters
    st.markdown("### 🔍 Filters")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        date_filter = st.date_input("From Date", value=datetime.now().date() - timedelta(days=30))
    with col2:
        date_filter_end = st.date_input("To Date", value=datetime.now().date())
    with col3:
        village_filter = st.selectbox("Village", ["All"] + VILLAGES)
    with col4:
        payment_filter = st.selectbox("Payment Status", ["All"] + PAYMENT_OPTIONS)
    
    # Apply filters
    filtered_df = df.copy()
    
    if 'Date' in filtered_df.columns:
        filtered_df['Date'] = pd.to_datetime(filtered_df['Date'], errors='coerce')
        filtered_df = filtered_df[
            (filtered_df['Date'].dt.date >= date_filter) & 
            (filtered_df['Date'].dt.date <= date_filter_end)
        ]
    
    if village_filter != "All" and 'Village' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Village'] == village_filter]
    
    if payment_filter != "All" and 'Payment Status' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Payment Status'] == payment_filter]
    
    # Summary
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", len(filtered_df))
    with col2:
        total = filtered_df['Total Amount'].sum() if 'Total Amount' in filtered_df.columns else 0
        st.metric("Total Amount", f"₹{total:,.0f}")
    with col3:
        pending = filtered_df[filtered_df['Payment Status'] != 'Paid']['Balance'].sum() if 'Balance' in filtered_df.columns else 0
        st.metric("Pending", f"₹{pending:,.0f}")
    
    # Export button
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col2:
        if not filtered_df.empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name='Sales')
            
            st.download_button(
                label="📥 Download Excel",
                data=buffer.getvalue(),
                file_name=f"sales_export_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    # Display data
    st.markdown("### 📊 Sales Data")
    
    # Add edit/delete functionality
    if not filtered_df.empty:
        # Display with selection
        display_cols = ['ID', 'Date', 'Customer Name', 'Village', 'Tea Type', 'Packaging', 
                       'Quantity', 'Total Amount', 'Payment Status', 'Balance']
        available_cols = [col for col in display_cols if col in filtered_df.columns]
        
        st.dataframe(filtered_df[available_cols].iloc[::-1], use_container_width=True, hide_index=True)
        
        # Edit/Delete section
        st.markdown("---")
        st.markdown("### ✏️ Edit / Delete Entry")
        
        if 'ID' in filtered_df.columns:
            entry_ids = filtered_df['ID'].tolist()
            selected_id = st.selectbox("Select Entry ID to Edit/Delete", options=entry_ids)
            
            if selected_id:
                selected_row = filtered_df[filtered_df['ID'] == selected_id].iloc[0]
                row_index = df[df['ID'] == selected_id].index[0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✏️ Edit Entry", use_container_width=True):
                        st.session_state['editing_id'] = selected_id
                        st.session_state['editing_row'] = row_index
                
                with col2:
                    if st.button("🗑️ Delete Entry", use_container_width=True, type="secondary"):
                        if delete_sale(spreadsheet, row_index):
                            st.success("✅ Entry deleted successfully!")
                            st.rerun()
                
                # Edit form
                if st.session_state.get('editing_id') == selected_id:
                    st.markdown("#### Edit Entry")
                    with st.form("edit_form"):
                        pricing = load_pricing_data(spreadsheet)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            edit_date = st.date_input("Date", value=pd.to_datetime(selected_row['Date']).date() if pd.notna(selected_row.get('Date')) else datetime.now().date())
                            edit_village = st.selectbox("Village", VILLAGES, index=VILLAGES.index(selected_row['Village']) if selected_row.get('Village') in VILLAGES else 0)
                            edit_tea = st.selectbox("Tea Type", TEA_TYPES, index=TEA_TYPES.index(selected_row['Tea Type']) if selected_row.get('Tea Type') in TEA_TYPES else 0)
                            edit_quantity = st.number_input("Quantity", min_value=1, value=int(selected_row.get('Quantity', 1)))
                        
                        with col2:
                            edit_customer = st.text_input("Customer Name", value=selected_row.get('Customer Name', ''))
                            edit_packaging = st.selectbox("Packaging", list(pricing.keys()), index=list(pricing.keys()).index(selected_row['Packaging']) if selected_row.get('Packaging') in pricing else 0)
                            edit_payment = st.selectbox("Payment Status", PAYMENT_OPTIONS, index=PAYMENT_OPTIONS.index(selected_row['Payment Status']) if selected_row.get('Payment Status') in PAYMENT_OPTIONS else 0)
                            edit_paid = st.number_input("Amount Paid", min_value=0.0, value=float(selected_row.get('Amount Paid', 0)))
                        
                        edit_rate = pricing.get(edit_packaging, 0)
                        edit_total = edit_rate * edit_quantity
                        st.markdown(f"**Total Amount: ₹{edit_total:,.0f}**")
                        
                        if st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary"):
                            updated_data = {
                                "Date": edit_date.strftime("%Y-%m-%d"),
                                "Day": get_day_from_date(edit_date),
                                "Village": edit_village,
                                "Customer Name": edit_customer,
                                "Brand": BRAND_NAME,
                                "Tea Type": edit_tea,
                                "Packaging": edit_packaging,
                                "Rate": edit_rate,
                                "Quantity": edit_quantity,
                                "Total Amount": edit_total,
                                "Payment Status": edit_payment,
                                "Amount Paid": edit_paid
                            }
                            
                            if update_sale(spreadsheet, row_index, updated_data):
                                st.success("✅ Entry updated successfully!")
                                del st.session_state['editing_id']
                                del st.session_state['editing_row']
                                st.rerun()

def render_reports(spreadsheet):
    """Render the reports page"""
    st.markdown("<div class='page-title'><h2>📊 Reports & Analytics</h2></div>", unsafe_allow_html=True)
    
    df = load_sales_data(spreadsheet)
    
    if df.empty:
        st.info("No data available for reports.")
        return
    
    # Report type selection
    report_type = st.selectbox("Select Report", [
        "📅 Daily Summary",
        "📆 Weekly Summary", 
        "🗓️ Monthly Summary",
        "👤 Customer-wise Report",
        "🏘️ Village-wise Report",
        "📦 Product-wise Report"
    ])
    
    st.markdown("---")
    
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    if report_type == "📅 Daily Summary":
        st.markdown("### Daily Sales Summary")
        if 'Date' in df.columns:
            daily = df.groupby(df['Date'].dt.date).agg({
                'Total Amount': 'sum',
                'Quantity': 'sum',
                'ID': 'count'
            }).rename(columns={'ID': 'Orders'}).reset_index()
            daily = daily.sort_values('Date', ascending=False)
            st.dataframe(daily, use_container_width=True, hide_index=True)
            
            st.markdown("### 📈 Daily Trend")
            st.line_chart(daily.set_index('Date')['Total Amount'])
    
    elif report_type == "📆 Weekly Summary":
        st.markdown("### Weekly Sales Summary")
        if 'Date' in df.columns:
            df['Week'] = df['Date'].dt.isocalendar().week
            df['Year'] = df['Date'].dt.year
            weekly = df.groupby(['Year', 'Week']).agg({
                'Total Amount': 'sum',
                'Quantity': 'sum',
                'ID': 'count'
            }).rename(columns={'ID': 'Orders'}).reset_index()
            st.dataframe(weekly, use_container_width=True, hide_index=True)
    
    elif report_type == "🗓️ Monthly Summary":
        st.markdown("### Monthly Sales Summary")
        if 'Date' in df.columns:
            df['Month'] = df['Date'].dt.to_period('M').astype(str)
            monthly = df.groupby('Month').agg({
                'Total Amount': 'sum',
                'Quantity': 'sum',
                'ID': 'count'
            }).rename(columns={'ID': 'Orders'}).reset_index()
            st.dataframe(monthly, use_container_width=True, hide_index=True)
            
            st.markdown("### 📈 Monthly Trend")
            st.bar_chart(monthly.set_index('Month')['Total Amount'])
    
    elif report_type == "👤 Customer-wise Report":
        st.markdown("### Customer-wise Sales Summary")
        if 'Customer Name' in df.columns:
            customer_report = df.groupby('Customer Name').agg({
                'Total Amount': 'sum',
                'Quantity': 'sum',
                'ID': 'count',
                'Balance': 'sum'
            }).rename(columns={'ID': 'Orders'}).reset_index()
            customer_report = customer_report.sort_values('Total Amount', ascending=False)
            st.dataframe(customer_report, use_container_width=True, hide_index=True)
    
    elif report_type == "🏘️ Village-wise Report":
        st.markdown("### Village-wise Sales Summary")
        if 'Village' in df.columns:
            village_report = df.groupby('Village').agg({
                'Total Amount': 'sum',
                'Quantity': 'sum',
                'ID': 'count',
                'Balance': 'sum'
            }).rename(columns={'ID': 'Orders'}).reset_index()
            st.dataframe(village_report, use_container_width=True, hide_index=True)
            
            st.markdown("### 📊 Village Comparison")
            st.bar_chart(village_report.set_index('Village')['Total Amount'])
    
    elif report_type == "📦 Product-wise Report":
        st.markdown("### Product-wise Sales Summary")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### By Tea Type")
            if 'Tea Type' in df.columns:
                tea_report = df.groupby('Tea Type').agg({
                    'Total Amount': 'sum',
                    'Quantity': 'sum'
                }).reset_index()
                st.dataframe(tea_report, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("#### By Packaging")
            if 'Packaging' in df.columns:
                pack_report = df.groupby('Packaging').agg({
                    'Total Amount': 'sum',
                    'Quantity': 'sum'
                }).reset_index()
                st.dataframe(pack_report, use_container_width=True, hide_index=True)

def render_pending_payments(spreadsheet):
    """Render the pending payments page"""
    st.markdown("<div class='page-title'><h2>💰 Pending Payments</h2></div>", unsafe_allow_html=True)
    
    df = load_sales_data(spreadsheet)
    
    if df.empty:
        st.info("No sales data available.")
        return
    
    # Filter unpaid/half-paid
    pending_df = df[df['Payment Status'].isin(['Not paid', 'Half paid'])].copy() if 'Payment Status' in df.columns else pd.DataFrame()
    
    if pending_df.empty:
        st.success("🎉 No pending payments! All dues are cleared.")
        return
    
    # Summary cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_pending = pending_df['Balance'].sum() if 'Balance' in pending_df.columns else 0
        st.markdown(f"""
        <div class='warning-card'>
            <h3>₹{total_pending:,.0f}</h3>
            <p>Total Pending</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        not_paid = pending_df[pending_df['Payment Status'] == 'Not paid']['Balance'].sum() if 'Balance' in pending_df.columns else 0
        st.markdown(f"""
        <div class='metric-card'>
            <h3>₹{not_paid:,.0f}</h3>
            <p>Not Paid</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        half_paid = pending_df[pending_df['Payment Status'] == 'Half paid']['Balance'].sum() if 'Balance' in pending_df.columns else 0
        st.markdown(f"""
        <div class='info-card'>
            <h3>₹{half_paid:,.0f}</h3>
            <p>Half Paid</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filter by village
    village_filter = st.selectbox("Filter by Village", ["All"] + VILLAGES)
    
    if village_filter != "All":
        pending_df = pending_df[pending_df['Village'] == village_filter]
    
    # Customer-wise pending
    st.markdown("### 👤 Customer-wise Pending")
    if 'Customer Name' in pending_df.columns and 'Balance' in pending_df.columns:
        customer_pending = pending_df.groupby(['Village', 'Customer Name']).agg({
            'Balance': 'sum',
            'ID': 'count'
        }).rename(columns={'ID': 'Entries'}).reset_index()
        customer_pending = customer_pending.sort_values('Balance', ascending=False)
        st.dataframe(customer_pending, use_container_width=True, hide_index=True)
    
    # Detailed list
    st.markdown("---")
    st.markdown("### 📋 Detailed Pending Entries")
    display_cols = ['Date', 'Customer Name', 'Village', 'Total Amount', 'Amount Paid', 'Balance', 'Payment Status']
    available_cols = [col for col in display_cols if col in pending_df.columns]
    st.dataframe(pending_df[available_cols].iloc[::-1], use_container_width=True, hide_index=True)
    
    # Export
    if not pending_df.empty:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            pending_df.to_excel(writer, index=False, sheet_name='Pending')
        
        st.download_button(
            label="📥 Download Pending Report",
            data=buffer.getvalue(),
            file_name=f"pending_payments_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

def render_settings(spreadsheet):
    """Render the settings page"""
    st.markdown("<div class='page-title'><h2>⚙️ Settings</h2></div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["💰 Pricing", "👥 Customers", "🏘️ Villages"])
    
    with tab1:
        st.markdown("### Update Package Prices")
        pricing = load_pricing_data(spreadsheet)
        
        for package, rate in pricing.items():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.text(f"📦 {package}")
            with col2:
                new_rate = st.number_input(f"Rate for {package}", value=rate, min_value=1, key=f"price_{package}", label_visibility="collapsed")
            with col3:
                if new_rate != rate:
                    if st.button("💾", key=f"save_{package}"):
                        if update_pricing(spreadsheet, package, new_rate):
                            st.success(f"✅ {package} price updated!")
                            st.rerun()
    
    with tab2:
        st.markdown("### Manage Customers")
        customers = load_customers_data(spreadsheet)
        
        # Add customer
        st.markdown("#### ➕ Add New Customer")
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            add_village = st.selectbox("Village", VILLAGES, key="add_cust_village")
        with col2:
            add_name = st.text_input("Customer Name", key="add_cust_name")
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Add", key="add_cust_btn"):
                if add_name.strip():
                    if add_customer(spreadsheet, add_village, add_name.strip()):
                        st.success(f"✅ Customer added!")
                        st.rerun()
        
        st.markdown("---")
        
        # View/Delete customers
        st.markdown("#### 📋 View/Delete Customers")
        view_village = st.selectbox("Select Village", VILLAGES, key="view_cust_village")
        
        village_customers = customers.get(view_village, [])
        if village_customers:
            for customer in village_customers:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(f"👤 {customer}")
                with col2:
                    if st.button("🗑️", key=f"del_{view_village}_{customer}"):
                        if delete_customer(spreadsheet, view_village, customer):
                            st.success(f"✅ Deleted {customer}")
                            st.rerun()
        else:
            st.info("No customers in this village.")
    
    with tab3:
        st.markdown("### Village Information")
        st.info("Villages are currently fixed. Contact developer to add new villages.")
        
        for village in VILLAGES:
            day = [d for d, v in DAY_TO_VILLAGE.items() if v == village]
            day_str = day[0] if day else "Not assigned"
            st.markdown(f"**🏘️ {village}** - Assigned Day: {day_str}")
        
        # Google Sheet Link
        st.markdown("---")
        st.markdown("### 📊 Google Sheet Access")
        if spreadsheet:
            sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
            st.success("✅ Connected to Google Sheets")
            st.markdown(f"**📎 Sheet Link:** [Open Google Sheet]({sheet_url})")
            st.code(sheet_url, language=None)
            st.caption("Click the link above to view/edit your data directly in Google Sheets")
        else:
            st.warning("⚠️ Not connected to Google Sheets")

# ============================================
# MAIN APP
# ============================================
def main():
    """Main application entry point"""
    
    # Check authentication
    if not check_password():
        return
    
    # Initialize Google Sheets
    if 'spreadsheet' not in st.session_state:
        st.session_state.spreadsheet = init_google_sheets()
    
    spreadsheet = st.session_state.spreadsheet
    
    # Show warning if not connected to Google Sheets
    if spreadsheet is None:
        st.warning("⚠️ Not connected to Google Sheets. Data will not be saved permanently.")
    
    # Render sidebar and get selected page
    page = render_sidebar()
    
    # Render selected page
    if page == "🏠 Dashboard":
        render_dashboard(spreadsheet)
    elif page == "➕ New Sale":
        render_new_sale(spreadsheet)
    elif page == "📋 View Sales":
        render_view_sales(spreadsheet)
    elif page == "📊 Reports":
        render_reports(spreadsheet)
    elif page == "💰 Pending Payments":
        render_pending_payments(spreadsheet)
    elif page == "⚙️ Settings":
        render_settings(spreadsheet)

if __name__ == "__main__":
    main()
