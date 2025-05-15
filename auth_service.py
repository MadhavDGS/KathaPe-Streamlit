import os
import json
import uuid
from datetime import datetime
import streamlit as st
import supabase_service

# Mock user database stored in session state
def init_mock_data():
    """Initialize mock data if it doesn't exist"""
    if "mock_users" not in st.session_state:
        st.session_state.mock_users = {
            # Sample business user
            "9999999999": {
                "id": str(uuid.uuid4()),
                "name": "Sample Business",
                "phone_number": "9999999999",
                "password": "password123",
                "user_type": "business",
                "created_at": datetime.now().isoformat()
            }
        }
    
    if "mock_businesses" not in st.session_state:
        st.session_state.mock_businesses = {}
        
    if "mock_customers" not in st.session_state:
        st.session_state.mock_customers = {}
        
    if "mock_customer_credits" not in st.session_state:
        st.session_state.mock_customer_credits = []
        
    if "mock_transactions" not in st.session_state:
        st.session_state.mock_transactions = []
        
    # Create business record if not exists
    business_user_id = st.session_state.mock_users["9999999999"]["id"]
    if business_user_id not in st.session_state.mock_businesses:
        business_id = str(uuid.uuid4())
        st.session_state.mock_businesses[business_user_id] = {
            "id": business_id,
            "user_id": business_user_id,
            "name": "Sample Business Account",
            "description": "Mock business account",
            "access_pin": "1234",
            "created_at": datetime.now().isoformat()
        }


def save_to_session_state():
    """Save current session data to session state"""
    # Already using session state, so this is a no-op
    pass


def mock_login(phone, password, user_type='customer'):
    """
    Attempt a login with proper error handling
    Returns (success, user_data_or_error_message) tuple
    """
    # Initialize mock data if it's not already present
    init_mock_data()
    
    # Try Supabase login if available
    try:
        supabase = supabase_service.get_supabase_admin_client()
        if supabase:
            # Try to find the user in Supabase
            user_response = supabase.table('users').select('*').eq('phone_number', phone).eq('user_type', user_type).execute()
            
            if user_response.data:
                user = user_response.data[0]
                
                # Check password
                if user['password'] == password:
                    # Set session data
                    st.session_state.user_id = user['id']
                    st.session_state.user_name = user['name']
                    st.session_state.user_type = user_type
                    st.session_state.phone_number = phone
                    
                    if user_type == 'business':
                        # Get business data
                        business_response = supabase.table('businesses').select('*').eq('user_id', user['id']).execute()
                        if business_response.data:
                            business = business_response.data[0]
                            st.session_state.business_id = business['id']
                            st.session_state.business_name = business['name']
                            st.session_state.access_pin = business['access_pin']
                    else:
                        # Get customer data
                        customer_response = supabase.table('customers').select('*').eq('user_id', user['id']).execute()
                        if customer_response.data:
                            customer = customer_response.data[0]
                            st.session_state.customer_id = customer['id']
                    
                    return True, user
                else:
                    return False, "Incorrect password. Please check and try again."
            
            # If we're in development mode with demo credentials, allow mock users
            if password == 'demo123' or password == 'password123' or phone == '9999999999':
                print("Demo credentials detected, allowing mock login")
            else:
                # User not found in database and not using demo credentials
                return False, "User not found. Please check your phone number or register for a new account."
    except Exception as e:
        print(f"Error in Supabase login: {str(e)}")
        print("Falling back to mock login for demo purposes only")
    
    # DEVELOPMENT/DEMO MODE: Continue with mock login logic for demo purposes
    # This section is only for demo and testing - in production, we would return an error
    
    # First check if this user exists in our mock database
    if phone in st.session_state.mock_users:
        user = st.session_state.mock_users[phone]
        
        # Verify password and user type
        if user['password'] == password and user['user_type'] == user_type:
            # Set session data
            st.session_state.user_id = user['id']
            st.session_state.user_name = user['name']
            st.session_state.user_type = user_type
            st.session_state.phone_number = phone
            
            if user_type == 'business':
                # Get business data
                for business_user_id, business in st.session_state.mock_businesses.items():
                    if business['user_id'] == user['id']:
                        st.session_state.business_id = business['id']
                        st.session_state.business_name = business['name']
                        st.session_state.access_pin = business['access_pin']
                        break
                else:
                    # Create mock business if not found
                    business_id = str(uuid.uuid4())
                    st.session_state.business_id = business_id
                    st.session_state.business_name = f"{user['name']}'s Business"
                    st.session_state.access_pin = '1234'
            else:
                # Get customer data
                for customer_user_id, customer in st.session_state.mock_customers.items():
                    if customer['user_id'] == user['id']:
                        st.session_state.customer_id = customer['id']
                        break
                else:
                    # Create mock customer if not found
                    customer_id = str(uuid.uuid4())
                    st.session_state.customer_id = customer_id
            
            return True, user
        else:
            return False, "Incorrect password or user type."
    
    # Demo mode: Auto-create user if using demo credentials
    if password == 'demo123' or phone == '9999999999':
        user_id = str(uuid.uuid4())
        user = {
            'id': user_id,
            'name': f"Demo {user_type.title()}",
            'phone_number': phone,
            'password': password,
            'user_type': user_type,
            'created_at': datetime.now().isoformat()
        }
        
        # Set session data
        st.session_state.user_id = user_id
        st.session_state.user_name = user['name']
        st.session_state.user_type = user_type
        st.session_state.phone_number = phone
        
        if user_type == 'business':
            business_id = str(uuid.uuid4())
            st.session_state.business_id = business_id
            st.session_state.business_name = f"{user['name']}'s Business"
            st.session_state.access_pin = '1234'
        else:
            customer_id = str(uuid.uuid4())
            st.session_state.customer_id = customer_id
        
        # Add to mock database
        st.session_state.mock_users[phone] = user
        return True, user
    
    # For any other credentials, reject login
    return False, "Invalid credentials. Please check your phone number and password."


def mock_register(phone, password, name, user_type='customer'):
    """
    Register a new user in the system
    Tries Supabase first, falls back to mock system
    Returns (success, message) tuple
    """
    # Initialize mock data if it's not already present
    init_mock_data()
    
    # First try to register with Supabase if available
    try:
        supabase = supabase_service.get_supabase_admin_client()
        if supabase:
            # Check if phone number already exists
            existing_user = supabase.table('users').select('id').eq('phone_number', phone).execute()
            if existing_user.data:
                return False, "Phone number already registered"
            
            # Create user
            user_id = str(uuid.uuid4())
            user_data = {
                'id': user_id,
                'name': name or f"User {phone[-4:]}",
                'phone_number': phone,
                'password': password,
                'user_type': user_type,
                'created_at': datetime.now().isoformat()
            }
            
            # Insert user into Supabase
            user_response = supabase.table('users').insert(user_data).execute()
            
            if not user_response.data:
                raise Exception("Failed to create user in Supabase")
            
            # Create related record based on user type
            if user_type == 'business':
                business_id = str(uuid.uuid4())
                business_data = {
                    'id': business_id,
                    'user_id': user_id,
                    'name': f"{name}'s Business",
                    'description': 'Auto-created business account',
                    'access_pin': '1234',
                    'created_at': datetime.now().isoformat()
                }
                business_response = supabase.table('businesses').insert(business_data).execute()
                
                if not business_response.data:
                    raise Exception("Failed to create business record in Supabase")
            else:
                customer_id = str(uuid.uuid4())
                customer_data = {
                    'id': customer_id,
                    'user_id': user_id,
                    'name': name,
                    'phone_number': phone,
                    'created_at': datetime.now().isoformat()
                }
                customer_response = supabase.table('customers').insert(customer_data).execute()
                
                if not customer_response.data:
                    raise Exception("Failed to create customer record in Supabase")
            
            return True, "User registered successfully in Supabase"
            
    except Exception as e:
        print(f"Error in Supabase registration: {str(e)}")
        print("Falling back to mock registration system")
    
    # Continue with mock registration if Supabase failed
    if phone in st.session_state.mock_users:
        return False, "Phone number already registered"
    
    user_id = str(uuid.uuid4())
    user = {
        'id': user_id,
        'name': name or f"User {phone[-4:]}",
        'phone_number': phone,
        'password': password,
        'user_type': user_type,
        'created_at': datetime.now().isoformat()
    }
    
    st.session_state.mock_users[phone] = user
    
    if user_type == 'business':
        business_id = str(uuid.uuid4())
        st.session_state.mock_businesses[user_id] = {
            'id': business_id,
            'user_id': user_id,
            'name': f"{name}'s Business",
            'description': 'Auto-created business account',
            'access_pin': '1234',
            'created_at': datetime.now().isoformat()
        }
    else:
        customer_id = str(uuid.uuid4())
        st.session_state.mock_customers[user_id] = {
            'id': customer_id,
            'user_id': user_id,
            'name': name,
            'phone_number': phone,
            'created_at': datetime.now().isoformat()
        }
    
    return True, "User registered successfully"


def mock_query_table(table_name, query_type='select', fields='*', filters=None, data=None):
    """
    Mock implementation of query_table function
    """
    # Initialize mock data if it's not already present
    init_mock_data()
    
    # Response class with data attribute to match Supabase responses
    class MockResponse:
        def __init__(self, data):
            self.data = data
    
    try:
        # Handle select queries
        if query_type == 'select':
            results = []
            
            # Get data based on table name
            if table_name == 'users':
                all_users = list(st.session_state.mock_users.values())
                results = all_users
            elif table_name == 'businesses':
                all_businesses = list(st.session_state.mock_businesses.values())
                results = all_businesses
            elif table_name == 'customers':
                all_customers = list(st.session_state.mock_customers.values())
                results = all_customers
            elif table_name == 'customer_credits':
                results = st.session_state.mock_customer_credits
            elif table_name == 'transactions':
                results = st.session_state.mock_transactions
            
            # Apply filters if any
            if filters:
                filtered_results = []
                for item in results:
                    matches = True
                    for field, op, value in filters:
                        if field in item:
                            if op == 'eq' and item[field] != value:
                                matches = False
                            elif op == 'neq' and item[field] == value:
                                matches = False
                            # Add more operations as needed
                    
                    if matches:
                        filtered_results.append(item)
                
                results = filtered_results
            
            return MockResponse(results)
        
        # Handle insert queries
        elif query_type == 'insert':
            if not data:
                return MockResponse([])
            
            # Ensure ID is present
            if 'id' not in data:
                data['id'] = str(uuid.uuid4())
            
            # Insert into the correct "table"
            if table_name == 'users':
                st.session_state.mock_users[data['phone_number']] = data
            elif table_name == 'businesses':
                st.session_state.mock_businesses[data['user_id']] = data
            elif table_name == 'customers':
                st.session_state.mock_customers[data['user_id']] = data
            elif table_name == 'customer_credits':
                st.session_state.mock_customer_credits.append(data)
            elif table_name == 'transactions':
                st.session_state.mock_transactions.append(data)
                
                # Update customer credit balance
                for credit in st.session_state.mock_customer_credits:
                    if (credit['business_id'] == data['business_id'] and 
                        credit['customer_id'] == data['customer_id']):
                        if data['transaction_type'] == 'credit':
                            credit['current_balance'] = credit.get('current_balance', 0) + data['amount']
                        elif data['transaction_type'] == 'payment':
                            credit['current_balance'] = credit.get('current_balance', 0) - data['amount']
            
            # Save to session state
            save_to_session_state()
            
            return MockResponse([data])
        
        # Handle update queries
        elif query_type == 'update':
            updated_items = []
            
            # For each table type, find items matching filters and update
            if table_name == 'users':
                for phone, user in st.session_state.mock_users.items():
                    matches = True
                    if filters:
                        for field, op, value in filters:
                            if field in user:
                                if op == 'eq' and user[field] != value:
                                    matches = False
                    
                    if matches:
                        for key, value in data.items():
                            user[key] = value
                        updated_items.append(user)
            
            elif table_name == 'businesses':
                for user_id, business in st.session_state.mock_businesses.items():
                    matches = True
                    if filters:
                        for field, op, value in filters:
                            if field in business:
                                if op == 'eq' and business[field] != value:
                                    matches = False
                    
                    if matches:
                        for key, value in data.items():
                            business[key] = value
                        updated_items.append(business)
            
            elif table_name == 'customers':
                for user_id, customer in st.session_state.mock_customers.items():
                    matches = True
                    if filters:
                        for field, op, value in filters:
                            if field in customer:
                                if op == 'eq' and customer[field] != value:
                                    matches = False
                    
                    if matches:
                        for key, value in data.items():
                            customer[key] = value
                        updated_items.append(customer)
            
            elif table_name == 'customer_credits':
                for i, credit in enumerate(st.session_state.mock_customer_credits):
                    matches = True
                    if filters:
                        for field, op, value in filters:
                            if field in credit:
                                if op == 'eq' and credit[field] != value:
                                    matches = False
                    
                    if matches:
                        for key, value in data.items():
                            st.session_state.mock_customer_credits[i][key] = value
                        updated_items.append(st.session_state.mock_customer_credits[i])
            
            # Save to session state
            save_to_session_state()
            
            return MockResponse(updated_items)
            
        # Handle delete queries
        elif query_type == 'delete':
            deleted_items = []
            
            # Not implementing delete for simplicity
            # If needed, this would filter and remove items from the lists
            
            return MockResponse(deleted_items)
        
        else:
            print(f"Unsupported query type: {query_type}")
            return MockResponse([])
            
    except Exception as e:
        print(f"Error in mock_query_table: {str(e)}")
        return MockResponse([])


def logout():
    """Clear user session data"""
    for key in ['user_id', 'user_name', 'user_type', 'phone_number', 
                'business_id', 'business_name', 'access_pin', 'customer_id']:
        if key in st.session_state:
            del st.session_state[key]


def is_logged_in():
    """Check if user is logged in"""
    return 'user_id' in st.session_state


def get_user_type():
    """Get current user type"""
    return st.session_state.get('user_type', None)


def is_business():
    """Check if current user is a business"""
    return is_logged_in() and get_user_type() == 'business'


def is_customer():
    """Check if current user is a customer"""
    return is_logged_in() and get_user_type() == 'customer'


# Initialize mock data when module is imported
init_mock_data() 