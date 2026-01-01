"""
GOLD Tea Powder - Sales Entry Application
A Streamlit app for managing tea powder sales entries
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json
from streamlit_searchbox import st_searchbox

# Configure page
st.set_page_config(
    page_title="GOLD Tea Powder - Sales Entry",
    page_icon="🍵",
    layout="centered"
)

# Brand and pricing information
BRAND_NAME = "GOLD Tea Powder"
TEA_TYPES = ["Mix", "Barik"]
# All available villages for selection
VILLAGES = ["vairgwadi", "Bardwadi", "Harali KH", "Harali BK"]

# Packaging options with their rates
PACKAGING_RATES = {
    "100gm": 35,
    "250gm": 85,
    "500gm": 170,
    "1kg": 350
}

# Excel file name
EXCEL_FILE = "gold_tea_sales.xlsx"

# Customer database file (JSON)
CUSTOMER_DB_FILE = "customer_database.json"

# Pricing database file (JSON)
PRICING_DB_FILE = "pricing_database.json"

# Days of the week
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Day to Village mapping - Only fixed days are assigned
# Other days (Tuesday, Wednesday, Thursday) allow manual selection
DAY_TO_VILLAGE = {
    "Monday": "Harali KH",
    "Friday": "Bardwadi",
    "Saturday": "vairgwadi",
    "Sunday": "Harali BK"
}
# Customer names mapped to villages
# You can add more customers for each village
VILLAGE_CUSTOMERS = {
    "vairgwadi": [
        " RatanaBai Gaddiwadar",
        " Sadhana Patil",
        "Hausabai Murkute",
        " Murari Patil",
        " Shivaji Sawant",
        "Prakash Patil",
        "Suresh Patil",
        "Anjali Patil",
        "Chandrkant Sawant",
        "Tanaji Sutar",
        "Santosh Gourle",
        "Sachin Kapase",
        "Anil Dhotare",
        "Vasant Patil"

        ],
        "Bardwadi": [
            "Basappa Gholrake",
            "Geeta Gholrake",
            "Sanjay Gholrake",
            "Pushpa Gholrake",
            "Shanakar Pujari",
            "Mahadev Naik",
            "Hirabai Gholrake",
            "Surekha Gholrake",
            "Shanata Naik",
            "Balava Gholrake",
            "Anada Gholrake",
            "Kempanna Gholrake",
            "Maruti Gholrake",
            "Sambhaji Gholrake",
            "Chandrkant Naik",
            "Renuka Arun Gholrake",
            "Gaurabai Gholrake",
            "Vaishali Gholrake",
            "Akkatai naik",
            "Lata Naik",
            "Savatri Bhoi",
            "Ratna Rangnavar",
            "Mahadev Bhoi",
            "Prashram Bhoi",
            "Barama Bhoi",
            "Satyappa Bhoi",
            "Annappa Bhoi",
            "Pushpa M Bhoi",
            "Driver Bhoi",
            "kori",
            "Kallappa Kaujalagi",
            "Suresh Kajualagi",
            "Champabai Karguppi",
            "Vaishali Karguppi",
            "Suvrna Karguppi",
            "Parubai Margudari",
            "Kamal Margudari",
            "Sanjay Margudari",
            "Raju Margudari",
            "Kalappa Margudari",
            "Pradip Khandekar",
            "Basawan Khandekar",
            "Mallappa Kamble",
            "Irrappa Kamble",
            "Mahadev Kamble",
            "Ashok Kamble",
            "Shanta Konare",
            "Bhairu Ragade",
            "Chandrva Dhangar",
            "Kamal Ragade",
            "Mahadev Ragade",
            "Rama Naik",
            "Laxman Naik",
            "Arun Sutar",
            "Ankush Sutar"

        ],
        "Harali KH": [
            "Sagar Kumbhar",
            "Shankar Mali",
            "Shivaji Mali",
            "Ranjit Chavan",
            "Surekha Bagadi",
            "Daynashwar Bagadi ",
            "Pandit Gurav",
            "Gajana Patil",
            "Janadharn Gurav",
            " Laxman Patil",
            "Filips Bardaskar",
           " Chandrkant Kumbhar",
           "Tanji Aapu Kumbhar",
           "Sagar Banekar",
           "Datayatra Bandu Kumbhar",
           "Aavubai Kumbhar",
           "Shivaji Kumbhar",
           "Chaya Kumbhar",
           "Gaurabai Kumbhar",
           "Shivaji Kanade",
           "Siddhava Kanade",
           "Mayava Kanade",
           "Anjana Bagadi",
           "Bagwant Kumbhar",
           "Jaywant Kumbhar",
           "Santosh Bagadi",
           "Arun Chothe",
           "Kavita Chothe",
           "Maruti Naik",
           "Prema Bagadi"
        ],
        "Harali BK": [
            "Vinayak Khanapure",
            "Ravi Morti",
            "Vijay Kamble",
            "Dipak Kamble",
            "Shanakar Kamble",
            "Sanjay Kamble",
            "Suresh Kori",
            "Pundalik Kamble",
            "Parshram Kamble",
            "Suraj Kamble",
            "Bharati Khavare",
            "Narayan Bhalekar",
            "Raju Chavan",
            "Kavita Kokitkar",
            "Hari Patake",
            "Vandana Lohar",
            "Sandip Patil",
            "Sunil Khavare",
            "Vimal Khavare",
            "Aalka Khavare",
            "Sandip Khavare",
            "Shashikant Murukate",
            "Netaji Murukate",
            "Sanjay Hodage",
            "Geeta Khavare",
            "Narayan Patil",
            "Ranaga Khavare",
            "Rupali Koikitkar",
            "Jayshri Parit",
            "Dhanaji Davari",
            "Shantaram Sutar",
            "Ravindra Khavare"
        ]
    
}

def get_day_from_date(date):
    """
    Calculate day of the week from a given date
    Returns: Day name (e.g., 'Monday', 'Tuesday')
    """
    return date.strftime("%A")


def load_customer_database():
    """
    Calculate day of the week from a given date
    Returns: Day name (e.g., 'Monday', 'Tuesday')
    """
    return date.strftime("%A")


def load_customer_database():
    """
    Load customer database from JSON file
    Returns: Dictionary with village names as keys and customer lists as values
    """
    if os.path.exists(CUSTOMER_DB_FILE):
        try:
            with open(CUSTOMER_DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return initialize_default_customers()
    else:
        return initialize_default_customers()


def load_pricing_database():
    """
    Load pricing database from JSON file
    Returns: Dictionary with packaging names as keys and prices as values
    """
    if os.path.exists(PRICING_DB_FILE):
        try:
            with open(PRICING_DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return PACKAGING_RATES.copy()
    else:
        return PACKAGING_RATES.copy()


def save_pricing_database(pricing_db):
    """
    Save pricing database to JSON file
    """
    try:
        with open(PRICING_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(pricing_db, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.warning(f"Could not save pricing database: {str(e)}")


def initialize_default_customers():
    """
    Initialize default customer database
    """
    return {
       "vairgwadi": [
        " RatanaBai Gaddiwadar",
        " Sadhana Patil",
        "Hausabai Murkute",
        " Murari Patil",
        " Shivaji Sawant",
        "Prakash Patil",
        "Suresh Patil",
        "Anjali Patil",
        "Chandrkant Sawant",
        "Tanaji Sutar",
        "Santosh Gourle",
        "Sachin Kapase",
        "Anil Dhotare",
        "Vasant Patil"

        ],
        "Bardwadi": [
            "Basappa Gholrake",
            "Geeta Gholrake",
            "Sanjay Gholrake",
            "Pushpa Gholrake",
            "Shanakar Pujari",
            "Mahadev Naik",
            "Hirabai Gholrake",
            "Surekha Gholrake",
            "Shanata Naik",
            "Balava Gholrake",
            "Anada Gholrake",
            "Kempanna Gholrake",
            "Maruti Gholrake",
            "Sambhaji Gholrake",
            "Chandrkant Naik",
            "Renuka Arun Gholrake",
            "Gaurabai Gholrake",
            "Vaishali Gholrake",
            "Akkatai naik",
            "Lata Naik",
            "Savatri Bhoi",
            "Ratna Rangnavar",
            "Mahadev Bhoi",
            "Prashram Bhoi",
            "Barama Bhoi",
            "Satyappa Bhoi",
            "Annappa Bhoi",
            "Pushpa M Bhoi",
            "Driver Bhoi",
            "kori",
            "Kallappa Kaujalagi",
            "Suresh Kajualagi",
            "Champabai Karguppi",
            "Vaishali Karguppi",
            "Suvrna Karguppi",
            "Parubai Margudari",
            "Kamal Margudari",
            "Sanjay Margudari",
            "Raju Margudari",
            "Kalappa Margudari",
            "Pradip Khandekar",
            "Basawan Khandekar",
            "Mallappa Kamble",
            "Irrappa Kamble",
            "Mahadev Kamble",
            "Ashok Kamble",
            "Shanta Konare",
            "Bhairu Ragade",
            "Chandrva Dhangar",
            "Kamal Ragade",
            "Mahadev Ragade",
            "Rama Naik",
            "Laxman Naik",
            "Arun Sutar",
            "Ankush Sutar"

        ],
        "Harali KH": [
            "Sagar Kumbhar",
            "Shankar Mali",
            "Shivaji Mali",
            "Ranjit Chavan",
            "Surekha Bagadi",
            "Daynashwar Bagadi ",
            "Pandit Gurav",
            "Gajana Patil",
            "Janadharn Gurav",
            " Laxman Patil",
            "Filips Bardaskar",
           " Chandrkant Kumbhar",
           "Tanji Aapu Kumbhar",
           "Sagar Banekar",
           "Datayatra Bandu Kumbhar",
           "Aavubai Kumbhar",
           "Shivaji Kumbhar",
           "Chaya Kumbhar",
           "Gaurabai Kumbhar",
           "Shivaji Kanade",
           "Siddhava Kanade",
           "Mayava Kanade",
           "Anjana Bagadi",
           "Bagwant Kumbhar",
           "Jaywant Kumbhar",
           "Santosh Bagadi",
           "Arun Chothe",
           "Kavita Chothe",
           "Maruti Naik",
           "Prema Bagadi"
        ],
        "Harali BK": [
            "Vinayak Khanapure",
            "Ravi Morti",
            "Vijay Kamble",
            "Dipak Kamble",
            "Shanakar Kamble",
            "Sanjay Kamble",
            "Suresh Kori",
            "Pundalik Kamble",
            "Parshram Kamble",
            "Suraj Kamble",
            "Bharati Khavare",
            "Narayan Bhalekar",
            "Raju Chavan",
            "Kavita Kokitkar",
            "Hari Patake",
            "Vandana Lohar",
            "Sandip Patil",
            "Sunil Khavare",
            "Vimal Khavare",
            "Aalka Khavare",
            "Sandip Khavare",
            "Shashikant Murukate",
            "Netaji Murukate",
            "Sanjay Hodage",
            "Geeta Khavare",
            "Narayan Patil",
            "Ranaga Khavare",
            "Rupali Koikitkar",
            "Jayshri Parit",
            "Dhanaji Davari",
            "Shantaram Sutar",
            "Ravindra Khavare"
        ]
       
    }


def save_customer_database(customer_db):
    """
    Save customer database to JSON file
    """
    try:
        with open(CUSTOMER_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(customer_db, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.warning(f"Could not save customer database: {str(e)}")


def add_customer_to_database(village, customer_name):
    """
    Add a new customer to the database if not already present
    Returns: True if customer was added, False if already exists
    """
    customer_db = load_customer_database()
    
    # Ensure village exists in database
    if village not in customer_db:
        customer_db[village] = []
    
    # Check if customer already exists (case-insensitive)
    customer_name_lower = customer_name.strip().lower()
    existing_customers_lower = [c.lower() for c in customer_db[village]]
    
    if customer_name_lower not in existing_customers_lower:
        # Add new customer
        customer_db[village].append(customer_name.strip())
        save_customer_database(customer_db)
        return True
    
    return False


def search_customers(searchterm: str, village: str):
    """
    Search function for customer searchbox
    Returns list of customers matching the search term
    """
    customer_db = load_customer_database()
    customers = customer_db.get(village, [])
    
    if not searchterm:
        # Return all customers if no search term
        return customers
    
    # Filter customers that contain the search term (case-insensitive)
    searchterm_lower = searchterm.lower()
    filtered = [c for c in customers if searchterm_lower in c.lower()]
    
    # If searchterm doesn't match any customer, allow it as a new entry
    if not filtered:
        return [searchterm]
    
    return filtered


def save_to_excel(data):
    """
    Save sales data to Excel file
    If file exists, append the data. Otherwise, create a new file.
    """
    try:
        # Create a DataFrame from the data
        df_new = pd.DataFrame([data])
        
        # Check if file exists
        if os.path.exists(EXCEL_FILE):
            # Read existing data
            df_existing = pd.read_excel(EXCEL_FILE)
            # Append new data
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            # Save to Excel
            df_combined.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
        else:
            # Create new file with the data
            df_new.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
    except PermissionError:
        raise PermissionError(f"Cannot save to '{EXCEL_FILE}'. Please close the Excel file if it's open and try again.")
    except Exception as e:
        raise Exception(f"Error saving data: {str(e)}")


def load_recent_entries(n=5):
    """
    Load the most recent n entries from the Excel file
    Returns: DataFrame with recent entries or None if file doesn't exist
    """
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        # Return last n entries in reverse order (most recent first)
        return df.tail(n).iloc[::-1]
    return None


# Main app
def main():
    # App title and header
    st.title("🍵 GOLD Tea Powder")
    st.subheader("Sales Entry Application")
    st.markdown("---")
    
    # Sales entry form
    st.markdown("### Enter Sales Details")
    
    # Row 1: Date and Day
    col1, col2 = st.columns(2)
    with col1:
        # Date input - auto-filled with today's date
        selected_date = st.date_input(
            "Date",
            value=datetime.today(),
            help="Select the sales date"
        )
    
    with col2:
        # Calculate day from selected date - updates automatically when date changes
        auto_day = get_day_from_date(selected_date)
        # Day dropdown - auto-filled but editable
        selected_day = st.selectbox(
            "Day",
            options=DAYS_OF_WEEK,
            index=DAYS_OF_WEEK.index(auto_day),
            help="Day is auto-calculated from date but can be changed"
        )
    
    # Row 2: Village and Customer Name
    col3, col4 = st.columns(2)
    with col3:
        # Auto-assign village based on the selected day
        auto_village = DAY_TO_VILLAGE.get(selected_day, VILLAGES[0])
        # Village selection - auto-selected based on day but editable
        village = st.selectbox(
            "Village Name",
            options=VILLAGES,
            index=VILLAGES.index(auto_village) if auto_village in VILLAGES else 0,
            help="Village is auto-assigned based on day but can be changed"
        )
    
    with col4:
        # Load customer database
        customer_db = load_customer_database()
        
        # Get customer suggestions for the selected village
        customer_suggestions = customer_db.get(village, [])
        
        # Searchable dropdown - type or select customer
        customer_name = st_searchbox(
            search_function=lambda searchterm: search_customers(searchterm, village),
            label="Customer Name",
            placeholder="Type or select customer name",
            default=None,
            clear_on_submit=False,
            key=f"customer_search_{village}"
        )
        
        # If no customer selected/typed, show empty
        if customer_name is None:
            customer_name = ""
    
    # Row 3: Tea Type and Packaging
    col5, col6 = st.columns(2)
    with col5:
        # Tea type selection
        tea_type = st.selectbox(
            "Tea Type",
            options=TEA_TYPES,
            help="Select the type of tea"
        )
    
    with col6:
        # Packaging selection
        # Load current pricing from database
        current_pricing = load_pricing_database()
        packaging = st.selectbox(
            "Packaging",
            options=list(current_pricing.keys()),
            help="Select packaging size"
        )
    
    # Row 4: Rate and Quantity
    col7, col8 = st.columns(2)
    with col7:
        # Rate - auto-filled based on packaging selection from database
        rate = current_pricing[packaging]
        st.number_input(
            "Rate (₹)",
            value=rate,
            disabled=True,
            help="Rate is auto-filled based on packaging"
        )
    
    with col8:
        # Quantity input
        quantity = st.number_input(
            "Quantity",
            min_value=1,
            value=1,
            step=1,
            help="Enter the quantity"
        )
    
    # Total Amount - auto-calculated
    total_amount = rate * quantity
    st.number_input(
        "Total Amount (₹)",
        value=total_amount,
        disabled=True,
        help="Total amount is automatically calculated (Rate × Quantity)"
    )
    
    # Row 5: Payment status
    st.markdown("### Payment")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        payment_status = st.selectbox(
            "Payment Status",
            options=["Paid", "Half paid", "Not paid"],
            index=0,
            help="Select payment status"
        )
    with col_p2:
        amount_paid = 0.0
        # Show numeric input only when 'Half paid' is selected
        if payment_status == "Half paid":
            amount_paid = st.number_input(
                "Amount Paid (₹)",
                min_value=0.0,
                value=0.0,
                step=1.0,
                format="%.2f",
                help="Enter the amount paid (numbers only)"
            )
    
    # Submit button
    st.markdown("---")
    submitted = st.button("💾 Save Sales Entry", use_container_width=True, type="primary")
    
    # Handle form submission
    if submitted:
        # Validate customer name
        if not customer_name.strip():
            st.error("⚠️ Please enter customer name!")
        else:
            # Check if this is a new customer for this village
            is_new_customer = add_customer_to_database(village, customer_name.strip())
            
            # Prepare data to save
            sales_data = {
                "Date": selected_date.strftime("%Y-%m-%d"),
                "Day": selected_day,
                "Village": village,
                "Customer Name": customer_name.strip(),
                "Brand": BRAND_NAME,
                "Tea Type": tea_type,
                "Packaging": packaging,
                "Rate": rate,
                "Quantity": quantity,
                "Total Amount": total_amount,
                "Payment Status": payment_status,
                "Amount Paid": float(amount_paid)
            }
            
            # Save to Excel
            try:
                save_to_excel(sales_data)
                
                # Show success message
                if is_new_customer:
                    st.success(f"✅ Sales entry saved successfully! New customer '{customer_name.strip()}' added to {village}.")
                else:
                    st.success("✅ Sales entry saved successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Error saving data: {str(e)}")
    
    # Display recent entries
    st.markdown("---")
    st.markdown("### 📊 Recent Sales Entries (Last 5)")
    
    recent_entries = load_recent_entries(5)
    
    if recent_entries is not None and not recent_entries.empty:
        # Display as a table
        st.dataframe(
            recent_entries,
            use_container_width=True,
            hide_index=True
        )
        
        # Show summary statistics
        st.markdown("#### Quick Summary")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Total Sales", f"₹{recent_entries['Total Amount'].sum():.2f}")
        with col_b:
            st.metric("Total Quantity", int(recent_entries['Quantity'].sum()))
        with col_c:
            st.metric("Entries", len(recent_entries))
    else:
        st.info("No sales entries yet. Start by adding your first sale!")
    
    # Customer Name Correction Section
    st.markdown("---")
    st.markdown("### ✏️ Correct Customer Name Spelling")
    
    # Create a button to show/hide the correction form
    if st.button("🔧 Fix Customer Name Spelling", use_container_width=True):
        st.session_state['show_correction_form'] = not st.session_state.get('show_correction_form', False)
    
    # Show correction form if button was clicked
    if st.session_state.get('show_correction_form', False):
        st.markdown("#### Select and Edit Customer Name")
        
        col_fix1, col_fix2 = st.columns(2)
        
        with col_fix1:
            # Village selection dropdown
            fix_village = st.selectbox(
                "Select Village",
                options=VILLAGES,
                key="fix_village_select",
                help="Choose the village where the customer belongs"
            )
        
        with col_fix2:
            # Load customers for the selected village
            customer_db_fix = load_customer_database()
            customers_in_village = customer_db_fix.get(fix_village, [])
            
            # Customer selection dropdown
            if customers_in_village:
                selected_customer = st.selectbox(
                    "Select Customer to Edit",
                    options=customers_in_village,
                    key="fix_customer_select",
                    help="Choose the customer name you want to correct"
                )
            else:
                st.warning(f"No customers found in {fix_village}")
                selected_customer = None
        
        # Show text input for corrected name
        if selected_customer:
            st.markdown("---")
            corrected_name = st.text_input(
                "Enter Corrected Name",
                value=selected_customer,
                key="corrected_name_input",
                help="Type the correct spelling of the customer name"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                # Save button
                if st.button("💾 Save Corrected Name", type="primary", use_container_width=True):
                    if corrected_name.strip():
                        # Load customer database
                        customer_db_update = load_customer_database()
                        
                        # Remove old name and add corrected name
                        if selected_customer in customer_db_update[fix_village]:
                            customer_db_update[fix_village].remove(selected_customer)
                            customer_db_update[fix_village].append(corrected_name.strip())
                            
                            # Save updated database
                            save_customer_database(customer_db_update)
                            
                            st.success(f"✅ Customer name updated successfully!\n\nOld: {selected_customer}\nNew: {corrected_name.strip()}")
                            st.balloons()
                            
                            # Reset form
                            st.session_state['show_correction_form'] = False
                            st.rerun()
                        else:
                            st.error("Customer not found in database!")
                    else:
                        st.error("Please enter a valid customer name!")
            
            with col_btn2:
                # Cancel button
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state['show_correction_form'] = False
                    st.rerun()
    
    # Pricing Update Section
    st.markdown("---")
    st.markdown("### 💰 Update Package Prices")
    
    # Create a button to show/hide the pricing form
    if st.button("💵 Change Package Prices", use_container_width=True):
        st.session_state['show_pricing_form'] = not st.session_state.get('show_pricing_form', False)
    
    # Show pricing form if button was clicked
    if st.session_state.get('show_pricing_form', False):
        st.markdown("#### Select Package and Update Price")
        
        # Load current pricing
        current_prices = load_pricing_database()
        
        col_price1, col_price2 = st.columns(2)
        
        with col_price1:
            # Package selection dropdown
            selected_package = st.selectbox(
                "Select Package",
                options=list(current_prices.keys()),
                key="price_package_select",
                help="Choose the package size to update price"
            )
        
        with col_price2:
            # Show current price
            current_price = current_prices[selected_package]
            st.metric(
                "Current Price",
                f"₹{current_price}",
                help="This is the current price for selected package"
            )
        
        # Show input for new price
        st.markdown("---")
        new_price = st.number_input(
            "Enter New Price (₹)",
            min_value=1,
            value=current_price,
            step=1,
            key="new_price_input",
            help="Enter the new price for the selected package"
        )
        
        col_price_btn1, col_price_btn2 = st.columns(2)
        
        with col_price_btn1:
            # Save button
            if st.button("💾 Save New Price", type="primary", use_container_width=True, key="save_price_btn"):
                if new_price > 0:
                    # Load pricing database
                    pricing_db_update = load_pricing_database()
                    
                    # Update the price
                    old_price = pricing_db_update[selected_package]
                    pricing_db_update[selected_package] = new_price
                    
                    # Save updated pricing
                    save_pricing_database(pricing_db_update)
                    
                    st.success(f"✅ Price updated successfully!\n\nPackage: {selected_package}\nOld Price: ₹{old_price}\nNew Price: ₹{new_price}")
                    st.balloons()
                    
                    # Reset form
                    st.session_state['show_pricing_form'] = False
                    st.rerun()
                else:
                    st.error("Please enter a valid price (greater than 0)!")
        
        with col_price_btn2:
            # Cancel button
            if st.button("❌ Cancel", use_container_width=True, key="cancel_price_btn"):
                st.session_state['show_pricing_form'] = False
                st.rerun()
    
    # 
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "GOLD Tea Powder Sales Management System | © 2025"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
