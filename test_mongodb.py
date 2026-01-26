"""
Test MongoDB Connection
Quick script to verify MongoDB connection is working
"""

import os
from dotenv import load_dotenv
from db_mongodb import get_mongodb_client

# Load environment variables
load_dotenv()

def test_connection():
    """Test MongoDB connection"""
    print("Testing MongoDB connection...")
    print(f"MongoDB URI: {os.getenv('MONGODB_URI')[:50]}...")
    print(f"Database Name: {os.getenv('DB_NAME')}")
    print()
    
    try:
        # Get MongoDB client
        db_manager = get_mongodb_client()
        
        # Test connection
        if db_manager.test_connection():
            print("✅ Successfully connected to MongoDB!")
            
            # Test basic operations
            print("\nTesting basic operations...")
            
            # Get pricing
            pricing = db_manager.get_all_pricing()
            print(f"✅ Pricing loaded: {pricing}")
            
            # Get customers
            customers = db_manager.get_all_customers()
            print(f"✅ Customers loaded: {len(customers)} villages")
            
            # Get sales
            sales = db_manager.get_all_sales()
            print(f"✅ Sales loaded: {len(sales)} records")
            
            print("\n🎉 All tests passed! MongoDB is ready to use.")
            return True
        else:
            print("❌ Failed to connect to MongoDB")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_connection()
