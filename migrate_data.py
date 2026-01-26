"""
Data Migration Script for GOLD Tea Powder Sales Management
Migrates data from local JSON files to MongoDB
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from db_mongodb import get_mongodb_client

# Load environment variables
load_dotenv()

DEFAULT_PRICING = {
    "100gm": 35,
    "250gm": 85,
    "500gm": 170,
    "1kg": 350
}

def migrate_customers():
    """Migrate customers from customer_database.json to MongoDB"""
    print("\n📋 Migrating Customers...")
    
    json_path = os.path.join(os.path.dirname(__file__), 'customer_database.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            customers = json.load(f)
        
        db_manager = get_mongodb_client()
        migrated_count = 0
        
        for village, customer_list in customers.items():
            for customer_name in customer_list:
                customer_name = customer_name.strip()
                if customer_name:
                    try:
                        db_manager.add_customer(village, customer_name)
                        migrated_count += 1
                        print(f"  ✅ Added: {customer_name} ({village})")
                    except Exception as e:
                        # Customer might already exist
                        print(f"  ⚠️  Skipped: {customer_name} ({village}) - {str(e)}")
        
        print(f"\n✅ Customer migration complete! Migrated {migrated_count} customers.")
        return True
        
    except FileNotFoundError:
        print(f"  ⚠️  customer_database.json not found")
        return False
    except Exception as e:
        print(f"  ❌ Error migrating customers: {str(e)}")
        return False

def migrate_pricing():
    """Migrate pricing from pricing_database.json or use defaults"""
    print("\n💰 Migrating Pricing...")
    
    json_path = os.path.join(os.path.dirname(__file__), 'pricing_database.json')
    pricing = DEFAULT_PRICING.copy()
    
    # Try to load from JSON file
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            file_pricing = json.load(f)
            pricing.update(file_pricing)
    except FileNotFoundError:
        print(f"  ⚠️  pricing_database.json not found, using defaults")
    except Exception as e:
        print(f"  ⚠️  Error reading pricing file: {str(e)}, using defaults")
    
    try:
        db_manager = get_mongodb_client()
        
        for package, rate in pricing.items():
            db_manager.update_pricing(package, rate)
            print(f"  ✅ Set: {package} = ₹{rate}")
        
        print(f"\n✅ Pricing migration complete!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error migrating pricing: {str(e)}")
        return False

def show_summary():
    """Show summary of migrated data"""
    print("\n" + "="*50)
    print("📊 MIGRATION SUMMARY")
    print("="*50)
    
    try:
        db_manager = get_mongodb_client()
        
        # Count customers
        customers = db_manager.get_all_customers()
        total_customers = sum(len(cust_list) for cust_list in customers.values())
        print(f"\n👥 Customers: {total_customers} total")
        for village, cust_list in customers.items():
            print(f"   - {village}: {len(cust_list)} customers")
        
        # Show pricing
        pricing = db_manager.get_all_pricing()
        print(f"\n💰 Pricing: {len(pricing)} packages")
        for package, rate in pricing.items():
            print(f"   - {package}: ₹{rate}")
        
        # Count sales
        sales = db_manager.get_all_sales()
        print(f"\n📈 Sales: {len(sales)} records")
        
        print("\n" + "="*50)
        print("✅ Migration completed successfully!")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ Error showing summary: {str(e)}")

def main():
    """Main migration function"""
    print("="*50)
    print("🚀 GOLD Tea Powder - Data Migration to MongoDB")
    print("="*50)
    
    # Test connection first
    print("\n🔌 Testing MongoDB connection...")
    try:
        db_manager = get_mongodb_client()
        if not db_manager.test_connection():
            print("❌ Failed to connect to MongoDB. Please check your connection settings.")
            return
        print("✅ Connected to MongoDB successfully!")
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return
    
    # Confirm migration
    print("\n⚠️  This will migrate data from JSON files to MongoDB.")
    print("   Existing data in MongoDB will be preserved (duplicates will be skipped).")
    response = input("\n   Continue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\n❌ Migration cancelled.")
        return
    
    # Run migrations
    migrate_pricing()
    migrate_customers()
    
    # Show summary
    show_summary()
    
    print("\n🎉 You can now run the application with: streamlit run app.py")

if __name__ == "__main__":
    main()
