"""
GOLD Tea Powder - Sales Management Application
A comprehensive Streamlit app with Google Sheets integration
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import io
import os
from streamlit_searchbox import st_searchbox
from db_mongodb import get_mongodb_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# MongoDB will be initialized via db_mongodb module

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
        app_password = os.getenv("APP_PASSWORD", "gold123")
        if st.session_state["password"] == app_password:
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
# MONGODB INITIALIZATION
# ============================================
def init_mongodb():
    """Initialize MongoDB connection and default data"""
    try:
        db_manager = get_mongodb_client()
        
        # Test connection
        if not db_manager.test_connection():
            st.error("❌ Failed to connect to MongoDB")
            return None
        
        # Initialize default pricing if not exists
        db_manager.initialize_default_pricing(DEFAULT_PRICING)
        
        return db_manager
    except Exception as e:
        st.error(f"❌ MongoDB initialization error: {str(e)}")
        return None

# ============================================
# DATA FUNCTIONS
# ============================================
@st.cache_data(ttl=30)
def load_sales_data(_db_manager=None):
    """Load all sales data from MongoDB"""
    if _db_manager:
        try:
            sales = _db_manager.get_all_sales()
            if sales:
                # Convert MongoDB documents to DataFrame
                df = pd.DataFrame(sales)
                
                # Convert date strings to datetime
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                
                # Rename columns to match old format (capitalize first letter)
                column_mapping = {
                    'sale_id': 'ID',
                    'date': 'Date',
                    'day': 'Day',
                    'village': 'Village',
                    'customer_name': 'Customer Name',
                    'brand': 'Brand',
                    'tea_type': 'Tea Type',
                    'packaging': 'Packaging',
                    'rate': 'Rate',
                    'quantity': 'Quantity',
                    'total_amount': 'Total Amount',
                    'payment_status': 'Payment Status',
                    'amount_paid': 'Amount Paid',
                    'balance': 'Balance',
                    'created_at': 'Created At',
                    'updated_at': 'Updated At'
                }
                df = df.rename(columns=column_mapping)
                return df
        except Exception as e:
            st.error(f"Error loading sales: {str(e)}")
    
    return pd.DataFrame(columns=[
        "ID", "Date", "Day", "Village", "Customer Name", "Brand",
        "Tea Type", "Packaging", "Rate", "Quantity", "Total Amount",
        "Payment Status", "Amount Paid", "Balance", "Created At", "Updated At"
    ])

@st.cache_data(ttl=300)  # Cache for 5 minutes to reduce API calls
def load_customers_data(_db_manager=None):
    """Load customers from MongoDB and local JSON file"""
    # First, load from local JSON file
    customers = load_default_customers()
    
    # Then merge with MongoDB data if available
    if _db_manager:
        try:
            mongo_customers = _db_manager.get_all_customers()
            for village, customer_list in mongo_customers.items():
                if village not in customers:
                    customers[village] = []
                for customer in customer_list:
                    if customer not in customers[village]:
                        customers[village].append(customer)
        except Exception as e:
            st.warning(f"Could not load from MongoDB: {str(e)}")
    
    return customers

@st.cache_data(ttl=60)
def load_pricing_data(_db_manager=None):
    """Load pricing from MongoDB"""
    if _db_manager:
        try:
            pricing = _db_manager.get_all_pricing()
            if pricing:
                return pricing
        except Exception as e:
            st.error(f"Error loading pricing: {str(e)}")
    
    return DEFAULT_PRICING.copy()

def load_default_customers():
    """Load customer list from customer_database.json file"""
    # Try to load from customer_database.json file
    json_path = os.path.join(os.path.dirname(__file__), 'customer_database.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            customers = json.load(f)
            # Strip whitespace from customer names
            for village in customers:
                customers[village] = [name.strip() for name in customers[village]]
            return customers
    except FileNotFoundError:
        st.warning("customer_database.json not found, using default customers")
    except json.JSONDecodeError as e:
        st.error(f"Error reading customer_database.json: {e}")
    
    # Fallback to hardcoded defaults if file not found
    return {
        "vairgwadi": [],
        "Bardwadi": [],
        "Harali KH": [],
        "Harali BK": []
    }

def save_customer_to_json(village, customer_name):
    """Save a new customer to customer_database.json file"""
    json_path = os.path.join(os.path.dirname(__file__), 'customer_database.json')
    try:
        # Load existing data
        with open(json_path, 'r', encoding='utf-8') as f:
            customers = json.load(f)
        
        # Add new customer if not exists
        customer_name = customer_name.strip()
        if village not in customers:
            customers[village] = []
        
        if customer_name and customer_name not in [c.strip() for c in customers[village]]:
            customers[village].append(customer_name)
            
            # Save back to file
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(customers, f, indent=4, ensure_ascii=False)
            return True
    except Exception as e:
        st.error(f"Error saving customer to JSON: {e}")
    return False

def search_customers(search_term, village, customers):
    """Search function for customer autocomplete"""
    if not search_term or len(search_term) < 2:
        # Return all customers for the village when less than 2 characters
        customer_list = customers.get(village, [])
        return customer_list[:10]  # Limit to 10 suggestions
    
    # Filter customers based on search term
    customer_list = customers.get(village, [])
    search_lower = search_term.lower()
    matches = [c for c in customer_list if search_lower in c.lower()]
    
    # If no matches found, include the typed text as an option to add new customer
    if not matches:
        return [f"➕ Add: {search_term}"]
    
    return matches[:10]  # Limit to 10 suggestions

def save_sale(db_manager, sale_data):
    """Save a new sale to MongoDB"""
    if db_manager:
        try:
            # Convert keys to lowercase with underscores for MongoDB
            mongo_data = {
                'date': sale_data.get('Date'),
                'day': sale_data.get('Day'),
                'village': sale_data.get('Village'),
                'customer_name': sale_data.get('Customer Name'),
                'brand': sale_data.get('Brand'),
                'tea_type': sale_data.get('Tea Type'),
                'packaging': sale_data.get('Packaging'),
                'rate': sale_data.get('Rate'),
                'quantity': sale_data.get('Quantity'),
                'total_amount': sale_data.get('Total Amount'),
                'payment_status': sale_data.get('Payment Status'),
                'amount_paid': sale_data.get('Amount Paid')
            }
            
            success = db_manager.add_sale(mongo_data)
            if success:
                # Clear cache to refresh data
                load_sales_data.clear()
            return success
        except Exception as e:
            st.error(f"Error saving sale: {str(e)}")
            return False
    return False

def update_sale(db_manager, sale_id, updated_data):
    """Update an existing sale record"""
    if db_manager:
        try:
            # Convert keys to lowercase with underscores for MongoDB
            mongo_data = {
                'date': updated_data.get('Date'),
                'day': updated_data.get('Day'),
                'village': updated_data.get('Village'),
                'customer_name': updated_data.get('Customer Name'),
                'brand': updated_data.get('Brand'),
                'tea_type': updated_data.get('Tea Type'),
                'packaging': updated_data.get('Packaging'),
                'rate': updated_data.get('Rate'),
                'quantity': updated_data.get('Quantity'),
                'total_amount': updated_data.get('Total Amount'),
                'payment_status': updated_data.get('Payment Status'),
                'amount_paid': updated_data.get('Amount Paid')
            }
            
            success = db_manager.update_sale(sale_id, mongo_data)
            if success:
                load_sales_data.clear()
            return success
        except Exception as e:
            st.error(f"Error updating sale: {str(e)}")
            return False
    return False

def delete_sale(db_manager, sale_id):
    """Delete a sale record from MongoDB"""
    if db_manager:
        try:
            success = db_manager.delete_sale(sale_id)
            if success:
                load_sales_data.clear()
            return success
        except Exception as e:
            st.error(f"Error deleting sale: {str(e)}")
            return False
    return False

def add_customer(db_manager, village, customer_name):
    """Add a new customer to MongoDB"""
    if db_manager:
        try:
            success = db_manager.add_customer(village, customer_name)
            if success:
                load_customers_data.clear()
            return success
        except Exception as e:
            st.error(f"Error adding customer: {str(e)}")
            return False
    return False

def delete_customer(db_manager, village, customer_name):
    """Delete a customer from MongoDB and local JSON"""
    deleted = False
    
    # Delete from MongoDB
    if db_manager:
        try:
            deleted = db_manager.delete_customer(village, customer_name)
            if deleted:
                load_customers_data.clear()
        except Exception as e:
            st.error(f"Error deleting customer from MongoDB: {str(e)}")
            return False
    
    # Also delete from local JSON file
    json_path = os.path.join(os.path.dirname(__file__), 'customer_database.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            customers = json.load(f)
        
        customer_name_clean = customer_name.strip()
        if village in customers:
            # Remove customer (case-insensitive and whitespace-trimmed comparison)
            customers[village] = [c for c in customers[village] if c.strip() != customer_name_clean]
            
            # Save back to file
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(customers, f, indent=4, ensure_ascii=False)
            deleted = True
    except Exception as e:
        st.warning(f"Could not update local customer database: {e}")
    
    return deleted

def edit_customer(db_manager, village, old_name, new_name):
    """Edit a customer name in MongoDB"""
    if db_manager:
        try:
            success = db_manager.update_customer(village, old_name, new_name)
            if success:
                load_customers_data.clear()
                # Also update in local JSON file
                save_customer_to_json(village, new_name.strip())
            return success
        except Exception as e:
            st.error(f"Error editing customer: {str(e)}")
    return False

def update_pricing(db_manager, package, new_rate):
    """Update pricing in MongoDB"""
    if db_manager:
        try:
            success = db_manager.update_pricing(package, new_rate)
            if success:
                load_pricing_data.clear()
            return success
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
        if 'db_manager' in st.session_state and st.session_state.db_manager:
            df = load_sales_data(st.session_state.db_manager)
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

def render_dashboard(db_manager):
    """Render the dashboard page"""
    st.markdown("<div class='page-title'><h2>🏠 Dashboard</h2></div>", unsafe_allow_html=True)
    
    df = load_sales_data(db_manager)
    
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

def render_new_sale(db_manager):
    """Render the new sale entry page"""
    st.markdown("<div class='page-title'><h2>➕ New Sale Entry</h2></div>", unsafe_allow_html=True)
    
    # Load data
    customers = load_customers_data(db_manager)
    pricing = load_pricing_data(db_manager)
    
    # Initialize session state for village
    if 'selected_village' not in st.session_state:
        st.session_state.selected_village = VILLAGES[0]
    
    # Row 1: Date and Day (outside form for better interaction)
    col1, col2 = st.columns(2)
    with col1:
        selected_date = st.date_input("📅 Date", value=datetime.today(), key="sale_date")
    with col2:
        auto_day = get_day_from_date(selected_date)
        selected_day = st.selectbox("📆 Day", options=DAYS_OF_WEEK, index=DAYS_OF_WEEK.index(auto_day), key="sale_day")
    
    # Row 2: Village and Customer
    col3, col4 = st.columns(2)
    with col3:
        auto_village = DAY_TO_VILLAGE.get(selected_day, VILLAGES[0])
        village_index = VILLAGES.index(auto_village) if auto_village in VILLAGES else 0
        village = st.selectbox("🏘️ Village", options=VILLAGES, index=village_index, key="sale_village")
        st.session_state.selected_village = village
    
    with col4:
        # Customer searchbox with autocomplete
        customer_list = customers.get(village, [])
        
        def search_customer(search_term):
            """Search function for customer autocomplete"""
            if not search_term:
                return customer_list[:15]  # Show first 15 customers
            
            search_lower = search_term.lower().strip()
            matches = [c for c in customer_list if search_lower in c.lower()]
            
            # If typed name not in list, include it as an option (will be saved automatically)
            if search_term.strip() and search_term.strip() not in [c.strip() for c in customer_list]:
                matches.insert(0, search_term.strip())  # Add typed name at top
            
            return matches[:15] if matches else [search_term.strip()]
        
        selected_customer = st_searchbox(
            search_customer,
            key=f"customer_search_{village}",
            placeholder="Type customer name...",
            label="👤 Customer Name",
            clear_on_submit=False,
            default=None
        )
    
    # Payment Status - OUTSIDE form so conditional input appears immediately
    st.markdown("---")
    st.markdown("### 💳 Payment Details")
    payment_status = st.selectbox("Payment Status", options=PAYMENT_OPTIONS, key="payment_status_select")
    
    # Amount paid input for Half paid
    amount_paid_input = 0
    if payment_status == "Half paid":
        amount_paid_input = st.number_input(
            "How much paid (₹)", 
            min_value=0, 
            value=0, 
            step=10,
            key="half_paid_amount"
        )
    
    # Tea Type and Packaging - OUTSIDE form so rate updates immediately
    st.markdown("---")
    col5, col6 = st.columns(2)
    with col5:
        tea_type = st.selectbox("🍵 Tea Type", options=TEA_TYPES, key="tea_type_select")
    with col6:
        packaging = st.selectbox("📦 Packaging", options=list(pricing.keys()), key="packaging_select")
    
    # Display Rate and Total
    rate = pricing.get(packaging, 0)
    st.info(f"💵 Rate: ₹{rate} per {packaging}")
    
    # Quantity - OUTSIDE form so total updates immediately
    st.markdown("---")
    quantity = st.number_input("🔢 Quantity", min_value=1, value=1, step=1, key="quantity_input")
    
    # Calculate total dynamically
    total_amount = rate * quantity
    st.markdown(f"### 💰 Total Amount: ₹{total_amount:,.0f}")
    
    with st.form("sale_form", clear_on_submit=True):
        # Submit
        submitted = st.form_submit_button("💾 Save Sale", use_container_width=True, type="primary")
        
        if submitted:
            # Calculate amount paid based on payment status
            if payment_status == "Paid":
                amount_paid = float(total_amount)
            elif payment_status == "Half paid":
                amount_paid = float(amount_paid_input)
            else:  # Not paid
                amount_paid = 0.0
            # Process customer selection from searchbox
            final_customer = selected_customer.strip() if selected_customer else ""
            
            if not final_customer:
                st.error("⚠️ Please enter a customer name!")
            else:
                # Check if this is a new customer and save automatically
                customer_list = customers.get(village, [])
                if final_customer not in [c.strip() for c in customer_list]:
                    # Save to MongoDB
                    add_customer(db_manager, village, final_customer)
                    # Also save to local JSON file
                    save_customer_to_json(village, final_customer)
                    load_customers_data.clear()  # Clear cache to reload customers
                
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
                
                if save_sale(db_manager, sale_data):
                    st.success(f"✅ Sale saved successfully for {final_customer}!")
                    st.balloons()
                else:
                    st.error("❌ Failed to save sale. Please try again.")

def render_view_sales(db_manager):
    """Render the view/edit/delete sales page"""
    st.markdown("<div class='page-title'><h2>📋 View & Manage Sales</h2></div>", unsafe_allow_html=True)
    
    df = load_sales_data(db_manager)
    
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
                # row_index is no longer needed with MongoDB migration as we use sale_id (ID)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✏️ Edit Entry", use_container_width=True):
                        st.session_state['editing_id'] = selected_id
                        st.session_state['editing_row'] = row_index
                
                with col2:
                    if st.button("🗑️ Delete Entry", use_container_width=True, type="secondary"):
                        if delete_sale(db_manager, selected_id):
                            st.success("✅ Entry deleted successfully!")
                            st.rerun()
                
                # Edit form
                if st.session_state.get('editing_id') == selected_id:
                    st.markdown("#### Edit Entry")
                    
                    pricing = load_pricing_data(db_manager)
                    
                    # Initialize session state for edit values if not exists
                    if f'edit_packaging_{selected_id}' not in st.session_state:
                        st.session_state[f'edit_packaging_{selected_id}'] = selected_row.get('Packaging', list(pricing.keys())[0])
                    if f'edit_quantity_{selected_id}' not in st.session_state:
                        st.session_state[f'edit_quantity_{selected_id}'] = int(selected_row.get('Quantity', 1))
                    
                    # Inputs outside form for dynamic calculation
                    col1, col2 = st.columns(2)
                    with col1:
                        edit_date = st.date_input("Date", value=pd.to_datetime(selected_row['Date']).date() if pd.notna(selected_row.get('Date')) else datetime.now().date(), key=f"edit_date_{selected_id}")
                        edit_village = st.selectbox("Village", VILLAGES, index=VILLAGES.index(selected_row['Village']) if selected_row.get('Village') in VILLAGES else 0, key=f"edit_village_{selected_id}")
                        edit_tea = st.selectbox("Tea Type", TEA_TYPES, index=TEA_TYPES.index(selected_row['Tea Type']) if selected_row.get('Tea Type') in TEA_TYPES else 0, key=f"edit_tea_{selected_id}")
                        edit_packaging = st.selectbox("Packaging", list(pricing.keys()), index=list(pricing.keys()).index(st.session_state[f'edit_packaging_{selected_id}']) if st.session_state[f'edit_packaging_{selected_id}'] in pricing else 0, key=f"edit_packaging_{selected_id}")
                    
                    with col2:
                        edit_customer = st.text_input("Customer Name", value=selected_row.get('Customer Name', ''), key=f"edit_customer_{selected_id}")
                        edit_quantity = st.number_input("Quantity", min_value=1, value=st.session_state[f'edit_quantity_{selected_id}'], key=f"edit_quantity_{selected_id}")
                        edit_payment = st.selectbox("Payment Status", PAYMENT_OPTIONS, index=PAYMENT_OPTIONS.index(selected_row['Payment Status']) if selected_row.get('Payment Status') in PAYMENT_OPTIONS else 0, key=f"edit_payment_{selected_id}")
                        edit_paid = st.number_input("Amount Paid", min_value=0.0, value=float(selected_row.get('Amount Paid', 0)), key=f"edit_paid_{selected_id}")
                    
                    # Calculate total dynamically
                    edit_rate = pricing.get(edit_packaging, 0)
                    edit_total = edit_rate * edit_quantity
                    st.markdown(f"### 💰 Total Amount: ₹{edit_total:,.0f}")
                    
                    # Form with just the submit button
                    with st.form(f"edit_form_{selected_id}"):
                        if st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary"):
                            # Calculate amount paid based on payment status
                            if edit_payment == "Paid":
                                final_edit_paid = float(edit_total)
                            elif edit_payment == "Not paid":
                                final_edit_paid = 0.0
                            else:
                                final_edit_paid = float(edit_paid)

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
                                "Amount Paid": final_edit_paid
                            }
                            
                            if update_sale(db_manager, selected_id, updated_data):
                                st.success("✅ Entry updated successfully!")
                                # Clean up session state
                                del st.session_state['editing_id']
                                del st.session_state['editing_row']
                                if f'edit_packaging_{selected_id}' in st.session_state:
                                    del st.session_state[f'edit_packaging_{selected_id}']
                                if f'edit_quantity_{selected_id}' in st.session_state:
                                    del st.session_state[f'edit_quantity_{selected_id}']
                                st.rerun()

def render_reports(db_manager):
    """Render the reports page"""
    st.markdown("<div class='page-title'><h2>📊 Reports & Analytics</h2></div>", unsafe_allow_html=True)
    
    df = load_sales_data(db_manager)
    
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

def render_pending_payments(db_manager):
    """Render the pending payments page"""
    st.markdown("<div class='page-title'><h2>💰 Pending Payments</h2></div>", unsafe_allow_html=True)
    
    df = load_sales_data(db_manager)
    
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

def render_settings(db_manager):
    """Render the settings page"""
    st.markdown("<div class='page-title'><h2>⚙️ Settings</h2></div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["💰 Pricing", "👥 Customers", "🏘️ Villages"])
    
    with tab1:
        st.markdown("### Update Package Prices")
        pricing = load_pricing_data(db_manager)
        
        for package, rate in pricing.items():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.text(f"📦 {package}")
            with col2:
                new_rate = st.number_input(f"Rate for {package}", value=rate, min_value=1, key=f"price_{package}", label_visibility="collapsed")
            with col3:
                if new_rate != rate:
                    if st.button("💾", key=f"save_{package}"):
                        if update_pricing(db_manager, package, new_rate):
                            st.success(f"✅ {package} price updated!")
                            st.rerun()
    
    with tab2:
        st.markdown("### Manage Customers")
        customers = load_customers_data(db_manager)
        
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
                    if add_customer(db_manager, add_village, add_name.strip()):
                        st.success(f"✅ Customer added!")
                        st.rerun()
        
        st.markdown("---")
        
        # View/Edit/Delete customers
        st.markdown("#### 📋 Manage Customers")
        view_village = st.selectbox("Select Village", VILLAGES, key="view_cust_village")
        
        village_customers = customers.get(view_village, [])
        if village_customers:
            for customer in village_customers:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.text(f"👤 {customer}")
                with col2:
                    if st.button("✏️", key=f"edit_{view_village}_{customer}", help="Edit customer name"):
                        st.session_state[f'editing_{view_village}_{customer}'] = True
                with col3:
                    if st.button("🗑️", key=f"del_{view_village}_{customer}", help="Delete customer"):
                        if delete_customer(db_manager, view_village, customer):
                            st.success(f"✅ Deleted {customer}")
                            st.rerun()
                
                # Show edit form if editing
                if st.session_state.get(f'editing_{view_village}_{customer}', False):
                    with st.form(key=f"edit_form_{view_village}_{customer}"):
                        new_name = st.text_input("New customer name", value=customer, key=f"new_name_{view_village}_{customer}")
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.form_submit_button("💾 Save"):
                                if new_name.strip() and new_name.strip() != customer:
                                    if edit_customer(db_manager, view_village, customer, new_name.strip()):
                                        st.success(f"✅ Updated to {new_name.strip()}")
                                        st.session_state[f'editing_{view_village}_{customer}'] = False
                                        st.rerun()
                                else:
                                    st.warning("⚠️ Please enter a different name")
                        with col_b:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state[f'editing_{view_village}_{customer}'] = False
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
        
        # MongoDB Connection Info
        st.markdown("---")
        st.markdown("### 📡 Database Connection")
        if db_manager:
            db_name = os.getenv("DB_NAME", "teasale")
            st.success("✅ Connected to MongoDB")
            st.markdown(f"**Database:** {db_name}")
            st.caption("Your data is securely stored in MongoDB Atlas")
        else:
            st.warning("⚠️ Not connected to MongoDB")

# ============================================
# MAIN APP
# ============================================
def main():
    """Main application entry point"""
    
    # Check authentication
    if not check_password():
        return
    
    # Initialize MongoDB
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = init_mongodb()
    
    db_manager = st.session_state.db_manager
    
    # Show warning if not connected to MongoDB
    if db_manager is None:
        st.error("❌ Not connected to MongoDB. Please check your connection settings.")
        st.stop()
    
    # Render sidebar and get selected page
    page = render_sidebar()
    
    # Render selected page
    if page == "🏠 Dashboard":
        render_dashboard(db_manager)
    elif page == "➕ New Sale":
        render_new_sale(db_manager)
    elif page == "📋 View Sales":
        render_view_sales(db_manager)
    elif page == "📊 Reports":
        render_reports(db_manager)
    elif page == "💰 Pending Payments":
        render_pending_payments(db_manager)
    elif page == "⚙️ Settings":
        render_settings(db_manager)

if __name__ == "__main__":
    main()
