"""
MongoDB Database Module for GOLD Tea Powder Sales Management
Handles all database operations with MongoDB Atlas
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import streamlit as st
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError, PyMongoError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "teasale")

# Collection names
SALES_COLLECTION = "sales"
CUSTOMERS_COLLECTION = "customers"
PRICING_COLLECTION = "pricing"


class MongoDBManager:
    """MongoDB connection and operations manager"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB"""
        try:
            if not MONGODB_URI:
                raise ValueError("MONGODB_URI not found in environment variables")
            
            self.client = MongoClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                retryWrites=True
            )
            
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[DB_NAME]
            
            # Create indexes
            self._create_indexes()
            
        except ConnectionFailure as e:
            st.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            raise
        except Exception as e:
            st.error(f"❌ MongoDB initialization error: {str(e)}")
            raise
    
    def _create_indexes(self):
        """Create database indexes for optimized queries"""
        try:
            # Sales collection indexes
            self.db[SALES_COLLECTION].create_index("sale_id", unique=True)
            self.db[SALES_COLLECTION].create_index([("date", DESCENDING)])
            self.db[SALES_COLLECTION].create_index("village")
            self.db[SALES_COLLECTION].create_index("customer_name")
            
            # Customers collection indexes
            self.db[CUSTOMERS_COLLECTION].create_index(
                [("village", ASCENDING), ("customer_name", ASCENDING)],
                unique=True
            )
            
            # Pricing collection indexes
            self.db[PRICING_COLLECTION].create_index("package", unique=True)
            
        except Exception as e:
            st.warning(f"⚠️ Could not create indexes: {str(e)}")
    
    def test_connection(self) -> bool:
        """Test if MongoDB connection is active"""
        try:
            self.client.admin.command('ping')
            return True
        except Exception:
            return False
    
    # ============================================
    # SALES OPERATIONS
    # ============================================
    
    def get_all_sales(self) -> List[Dict]:
        """Retrieve all sales records"""
        try:
            sales = list(self.db[SALES_COLLECTION].find().sort("date", DESCENDING))
            return sales
        except Exception as e:
            st.error(f"Error fetching sales: {str(e)}")
            return []
    
    def add_sale(self, sale_data: Dict) -> bool:
        """Add a new sale record"""
        try:
            # Generate unique sale ID
            sale_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
            
            # Calculate balance
            total = sale_data.get('total_amount', 0)
            paid = sale_data.get('amount_paid', 0)
            balance = total - paid if sale_data.get('payment_status') != 'Paid' else 0
            
            document = {
                "sale_id": sale_id,
                "date": sale_data.get('date'),
                "day": sale_data.get('day'),
                "village": sale_data.get('village'),
                "customer_name": sale_data.get('customer_name'),
                "brand": sale_data.get('brand'),
                "tea_type": sale_data.get('tea_type'),
                "packaging": sale_data.get('packaging'),
                "rate": sale_data.get('rate'),
                "quantity": sale_data.get('quantity'),
                "total_amount": total,
                "payment_status": sale_data.get('payment_status'),
                "amount_paid": paid,
                "balance": balance,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            self.db[SALES_COLLECTION].insert_one(document)
            return True
            
        except Exception as e:
            st.error(f"Error adding sale: {str(e)}")
            return False
    
    def update_sale(self, sale_id: str, updated_data: Dict) -> bool:
        """Update an existing sale record"""
        try:
            # Calculate balance
            total = updated_data.get('total_amount', 0)
            paid = updated_data.get('amount_paid', 0)
            balance = total - paid if updated_data.get('payment_status') != 'Paid' else 0
            
            update_doc = {
                "$set": {
                    "date": updated_data.get('date'),
                    "day": updated_data.get('day'),
                    "village": updated_data.get('village'),
                    "customer_name": updated_data.get('customer_name'),
                    "brand": updated_data.get('brand'),
                    "tea_type": updated_data.get('tea_type'),
                    "packaging": updated_data.get('packaging'),
                    "rate": updated_data.get('rate'),
                    "quantity": updated_data.get('quantity'),
                    "total_amount": total,
                    "payment_status": updated_data.get('payment_status'),
                    "amount_paid": paid,
                    "balance": balance,
                    "updated_at": datetime.now()
                }
            }
            
            result = self.db[SALES_COLLECTION].update_one(
                {"sale_id": sale_id},
                update_doc
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            st.error(f"Error updating sale: {str(e)}")
            return False
    
    def delete_sale(self, sale_id: str) -> bool:
        """Delete a sale record"""
        try:
            result = self.db[SALES_COLLECTION].delete_one({"sale_id": sale_id})
            return result.deleted_count > 0
        except Exception as e:
            st.error(f"Error deleting sale: {str(e)}")
            return False
    
    # ============================================
    # CUSTOMER OPERATIONS
    # ============================================
    
    def get_all_customers(self) -> Dict[str, List[str]]:
        """Retrieve all customers grouped by village"""
        try:
            customers_dict = {}
            customers = self.db[CUSTOMERS_COLLECTION].find().sort("village", ASCENDING)
            
            for customer in customers:
                village = customer.get('village')
                name = customer.get('customer_name')
                
                if village not in customers_dict:
                    customers_dict[village] = []
                
                if name and name not in customers_dict[village]:
                    customers_dict[village].append(name)
            
            return customers_dict
            
        except Exception as e:
            st.error(f"Error fetching customers: {str(e)}")
            return {}
    
    def add_customer(self, village: str, customer_name: str) -> bool:
        """Add a new customer"""
        try:
            document = {
                "village": village,
                "customer_name": customer_name.strip(),
                "added_on": datetime.now()
            }
            
            self.db[CUSTOMERS_COLLECTION].insert_one(document)
            return True
            
        except DuplicateKeyError:
            st.warning(f"Customer '{customer_name}' already exists in {village}")
            return False
        except Exception as e:
            st.error(f"Error adding customer: {str(e)}")
            return False
    
    def update_customer(self, village: str, old_name: str, new_name: str) -> bool:
        """Update a customer's name"""
        try:
            result = self.db[CUSTOMERS_COLLECTION].update_one(
                {"village": village, "customer_name": old_name},
                {"$set": {"customer_name": new_name.strip(), "updated_on": datetime.now()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            st.error(f"Error updating customer: {str(e)}")
            return False
    
    def delete_customer(self, village: str, customer_name: str) -> bool:
        """Delete a customer"""
        try:
            result = self.db[CUSTOMERS_COLLECTION].delete_one(
                {"village": village, "customer_name": customer_name.strip()}
            )
            
            return result.deleted_count > 0
            
        except Exception as e:
            st.error(f"Error deleting customer: {str(e)}")
            return False
    
    # ============================================
    # PRICING OPERATIONS
    # ============================================
    
    def get_all_pricing(self) -> Dict[str, int]:
        """Retrieve all pricing information"""
        try:
            pricing_dict = {}
            pricing = self.db[PRICING_COLLECTION].find()
            
            for item in pricing:
                package = item.get('package')
                rate = item.get('rate')
                if package:
                    pricing_dict[package] = int(rate)
            
            return pricing_dict
            
        except Exception as e:
            st.error(f"Error fetching pricing: {str(e)}")
            return {}
    
    def update_pricing(self, package: str, new_rate: int) -> bool:
        """Update pricing for a package"""
        try:
            result = self.db[PRICING_COLLECTION].update_one(
                {"package": package},
                {
                    "$set": {
                        "rate": new_rate,
                        "updated_on": datetime.now()
                    }
                },
                upsert=True
            )
            
            return True
            
        except Exception as e:
            st.error(f"Error updating pricing: {str(e)}")
            return False
    
    def initialize_default_pricing(self, default_pricing: Dict[str, int]):
        """Initialize default pricing if not exists"""
        try:
            for package, rate in default_pricing.items():
                self.db[PRICING_COLLECTION].update_one(
                    {"package": package},
                    {
                        "$setOnInsert": {
                            "package": package,
                            "rate": rate,
                            "updated_on": datetime.now()
                        }
                    },
                    upsert=True
                )
        except Exception as e:
            st.warning(f"Could not initialize default pricing: {str(e)}")
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()


@st.cache_resource
def get_mongodb_client():
    """Get cached MongoDB client instance"""
    return MongoDBManager()
