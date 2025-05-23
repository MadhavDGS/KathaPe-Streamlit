import os
from dotenv import load_dotenv
import streamlit as st
import uuid
from datetime import datetime

# Try to import Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Supabase module not available. Please install with: pip install supabase==1.0.4")

# Load environment variables
load_dotenv()

# Constants
DB_RETRY_ATTEMPTS = 3
DB_RETRY_DELAY = 1  # seconds

# Initialize Supabase client objects
supabase_client = None
supabase_admin_client = None
create_client_fn = None

def get_supabase_client():
    """Get a regular Supabase client for normal operations"""
    global supabase_client, create_client_fn
    
    # If Supabase is not available, return None
    if not SUPABASE_AVAILABLE:
        print("Supabase module not available, using mock data")
        return None
    
    # If we already have a client, return it
    if supabase_client:
        return supabase_client
    
    # Get Supabase credentials from Streamlit secrets or environment
    try:
        supabase_url = st.secrets["SUPABASE_URL"]
        print(f"Using Supabase URL from secrets: {supabase_url[:20]}...")
    except:
        supabase_url = os.getenv('SUPABASE_URL', "https://ghbmfgomnqmffixfkdyp.supabase.co")
        print(f"Using Supabase URL from env or default: {supabase_url[:20]}...")
    
    try:
        supabase_key = st.secrets["SUPABASE_KEY"]
        print("Using Supabase key from secrets")
    except:
        supabase_key = os.getenv('SUPABASE_KEY', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdoYm1mZ29tbnFtZmZpeGZrZHlwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcxNDAxNTcsImV4cCI6MjA2MjcxNjE1N30.Fw750xiDWVPrl6ssr9p6AJTt--8zvnPoboxJiURvsOI")
        print("Using Supabase key from env or default")
    
    if not supabase_url or not supabase_key:
        print("Supabase URL and key must be set in environment variables or secrets")
        return None
    
    # Try to create a Supabase client with retry logic
    import time
    try:
        for attempt in range(DB_RETRY_ATTEMPTS):
            try:
                # Import create_client if not already available
                if not create_client_fn:
                    from supabase import create_client
                    create_client_fn = create_client
                
                # Create client - for version 1.0.4, no options parameter
                supabase_client = create_client_fn(supabase_url, supabase_key)
                
                # Test the connection
                test_response = supabase_client.table('users').select('id').limit(1).execute()
                print("Successfully connected to Supabase")
                return supabase_client
            except Exception as e:
                if attempt < DB_RETRY_ATTEMPTS - 1:
                    print(f"Supabase connection attempt {attempt+1} failed: {str(e)}. Retrying...")
                    time.sleep(DB_RETRY_DELAY)
                else:
                    raise
    except Exception as e:
        print(f"Failed to connect to Supabase after {DB_RETRY_ATTEMPTS} attempts: {str(e)}")
        print("Falling back to mock data system")
        return None

def get_supabase_admin_client():
    """Get a Supabase client with service role permissions"""
    global supabase_admin_client, create_client_fn
    
    # If Supabase is not available, return None
    if not SUPABASE_AVAILABLE:
        print("Supabase module not available, using mock data")
        return None
    
    # If we already have an admin client, return it
    if supabase_admin_client:
        return supabase_admin_client
    
    # Get Supabase credentials from Streamlit secrets or environment
    try:
        supabase_url = st.secrets["SUPABASE_URL"]
        print(f"Using Supabase URL from secrets: {supabase_url[:20]}...")
    except:
        supabase_url = os.getenv('SUPABASE_URL', "https://ghbmfgomnqmffixfkdyp.supabase.co")
        print(f"Using Supabase URL from env or default: {supabase_url[:20]}...")
    
    try:
        supabase_service_key = st.secrets["SUPABASE_SERVICE_KEY"]
        print("Using Supabase service key from secrets")
    except:
        supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdoYm1mZ29tbnFtZmZpeGZrZHlwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzE0MDE1NywiZXhwIjoyMDYyNzE2MTU3fQ.RnbSqdIM5A67NuKHDOTdpqpu6G2zKJfhMeQapGUI2kw")
        print("Using Supabase service key from env or default")
    
    if not supabase_url or not supabase_service_key:
        print("Supabase URL and service key must be set in environment variables or secrets")
        return None
    
    # Try to create a Supabase admin client with retry logic
    import time
    try:
        for attempt in range(DB_RETRY_ATTEMPTS):
            try:
                # Import create_client if not already available
                if not create_client_fn:
                    from supabase import create_client
                    create_client_fn = create_client
                
                # Create client - for version 1.0.4, no options parameter
                supabase_admin_client = create_client_fn(supabase_url, supabase_service_key)
                
                # Test the connection
                test_response = supabase_admin_client.table('users').select('id').limit(1).execute()
                print("Successfully connected to Supabase with admin privileges")
                return supabase_admin_client
            except Exception as e:
                if attempt < DB_RETRY_ATTEMPTS - 1:
                    print(f"Supabase admin connection attempt {attempt+1} failed: {str(e)}. Retrying...")
                    time.sleep(DB_RETRY_DELAY)
                else:
                    raise
    except Exception as e:
        print(f"Failed to connect to Supabase with admin privileges after {DB_RETRY_ATTEMPTS} attempts: {str(e)}")
        print("Falling back to mock data system")
        return None

def mock_query_table(table_name, query_type='select', fields='*', filters=None, data=None):
    """
    Mock implementation of query_table function when Supabase is unavailable
    
    This provides minimal functionality to allow the app to work without Supabase
    """
    # Response class with data attribute to match Supabase responses
    class MockResponse:
        def __init__(self, data):
            self.data = data
    
    print(f"Using mock data for {query_type} on {table_name}")
    
    try:
        # Ensure session state has the required mock data structures
        if "mock_users" not in st.session_state:
            st.session_state.mock_users = {}
        
        if "mock_businesses" not in st.session_state:
            st.session_state.mock_businesses = {}
            
        if "mock_customers" not in st.session_state:
            st.session_state.mock_customers = {}
            
        if "mock_customer_credits" not in st.session_state:
            st.session_state.mock_customer_credits = []
            
        if "mock_transactions" not in st.session_state:
            st.session_state.mock_transactions = []
        
        # Initialize with a sample business user if no users exist
        if not st.session_state.mock_users:
            business_user_id = str(uuid.uuid4())
            business_id = str(uuid.uuid4())
            
            # Sample business user
            st.session_state.mock_users["9999999999"] = {
                "id": business_user_id,
                "name": "Sample Business",
                "phone_number": "9999999999",
                "password": "password123",
                "user_type": "business",
                "created_at": datetime.now().isoformat()
            }
            
            # Create matching business record
            st.session_state.mock_businesses[business_user_id] = {
                "id": business_id,
                "user_id": business_user_id,
                "name": "Sample Business Account",
                "description": "Mock business account",
                "access_pin": "1234",
                "created_at": datetime.now().isoformat()
            }
            
        # Handle different query types
        if query_type == 'select':
            results = []
            
            # Get data based on table name
            if table_name == 'users':
                results = list(st.session_state.mock_users.values())
            elif table_name == 'businesses':
                results = list(st.session_state.mock_businesses.values())
            elif table_name == 'customers':
                results = list(st.session_state.mock_customers.values())
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
            
            # Ensure created_at is present
            if 'created_at' not in data:
                data['created_at'] = datetime.now().isoformat()
            
            # Insert into the correct "table"
            if table_name == 'users':
                st.session_state.mock_users[data['phone_number']] = data
                return MockResponse([data])
            elif table_name == 'businesses':
                st.session_state.mock_businesses[data['user_id']] = data
                return MockResponse([data])
            elif table_name == 'customers':
                st.session_state.mock_customers[data['user_id']] = data
                return MockResponse([data])
            elif table_name == 'customer_credits':
                # Check if credit relationship already exists
                for i, credit in enumerate(st.session_state.mock_customer_credits):
                    if (credit['business_id'] == data['business_id'] and 
                        credit['customer_id'] == data['customer_id']):
                        # Update existing credit
                        st.session_state.mock_customer_credits[i].update(data)
                        return MockResponse([st.session_state.mock_customer_credits[i]])
                
                # Add new credit relationship
                st.session_state.mock_customer_credits.append(data)
                return MockResponse([data])
            elif table_name == 'transactions':
                # Add transaction
                st.session_state.mock_transactions.append(data)
                
                # Update customer credit balance if needed
                transaction_type = data.get('transaction_type')
                if transaction_type in ['credit', 'payment']:
                    business_id = data.get('business_id')
                    customer_id = data.get('customer_id')
                    amount = float(data.get('amount', 0))
                    
                    # Find or create a credit relationship
                    for i, credit in enumerate(st.session_state.mock_customer_credits):
                        if (credit['business_id'] == business_id and 
                            credit['customer_id'] == customer_id):
                            # Update balance
                            current_balance = float(credit.get('current_balance', 0))
                            if transaction_type == 'credit':
                                st.session_state.mock_customer_credits[i]['current_balance'] = current_balance + amount
                            elif transaction_type == 'payment':
                                st.session_state.mock_customer_credits[i]['current_balance'] = current_balance - amount
                            break
                    else:
                        # Credit relationship doesn't exist, create it
                        credit_data = {
                            'id': str(uuid.uuid4()),
                            'business_id': business_id,
                            'customer_id': customer_id,
                            'current_balance': amount if transaction_type == 'credit' else -amount,
                            'created_at': datetime.now().isoformat()
                        }
                        st.session_state.mock_customer_credits.append(credit_data)
                
                return MockResponse([data])
            else:
                return MockResponse([])
        
        # Handle update queries (simplified)
        elif query_type == 'update':
            updated_items = []
            
            # For now, we'll just return success without actual updates
            # This could be enhanced for better mock behavior if needed
            return MockResponse([data] if data else [])
        
        # Handle delete queries (simplified)
        elif query_type == 'delete':
            # For now, we'll just return success without actual deletion
            # This could be enhanced for better mock behavior if needed
            return MockResponse([])
        
        else:
            print(f"Unsupported query type: {query_type}")
            return MockResponse([])
            
    except Exception as e:
        print(f"Error in mock_query_table: {str(e)}")
        return MockResponse([])

def query_table(table_name, query_type='select', fields='*', filters=None, data=None):
    """
    Query a Supabase table with proper error handling
    Falls back to mock data if Supabase is unavailable
    
    Args:
        table_name: The name of the table to query
        query_type: 'select', 'insert', 'update', or 'delete'
        fields: Fields to select (for select queries)
        filters: List of tuples (field, operator, value) for filtering
        data: Data dictionary for insert/update operations
        
    Returns:
        Response object with .data attribute containing the results
    """
    # First try to get Supabase admin client
    supabase = get_supabase_admin_client() or get_supabase_client()
    
    # If no Supabase client is available, fall back to mock data
    if not supabase:
        print(f"No Supabase client available, using mock data for {query_type} on {table_name}")
        return mock_query_table(table_name, query_type, fields, filters, data)
    
    try:
        # Start with the table reference
        query = supabase.table(table_name)
        
        # Handle different query types
        if query_type == 'select':
            # Add field selection
            query = query.select(fields)
            
            # Add filters if provided
            if filters:
                for field, op, value in filters:
                    if op == 'eq':
                        query = query.eq(field, value)
                    elif op == 'neq':
                        query = query.neq(field, value)
                    elif op == 'gt':
                        query = query.gt(field, value)
                    elif op == 'lt':
                        query = query.lt(field, value)
                    elif op == 'gte':
                        query = query.gte(field, value)
                    elif op == 'lte':
                        query = query.lte(field, value)
                    elif op == 'like':
                        query = query.like(field, value)
                    elif op == 'in':
                        query = query.in_(field, value)
            
            # Execute the query
            response = query.execute()
            return response
            
        elif query_type == 'insert':
            if not data:
                raise ValueError("Data must be provided for insert operations")
            
            # Ensure ID is present
            if 'id' not in data:
                data['id'] = str(uuid.uuid4())
            
            # Ensure created_at is present
            if 'created_at' not in data:
                data['created_at'] = datetime.now().isoformat()
            
            # Insert the data
            response = query.insert(data).execute()
            
            # Handle specific table post-processing
            if table_name == 'transactions' and response.data:
                # Update customer_credits balance
                transaction = response.data[0]
                
                # Get the customer credit record
                customer_credit_filters = [
                    ('business_id', 'eq', transaction['business_id']),
                    ('customer_id', 'eq', transaction['customer_id'])
                ]
                
                credit_response = supabase.table('customer_credits').select('*').eq('business_id', transaction['business_id']).eq('customer_id', transaction['customer_id']).execute()
                
                if credit_response.data:
                    credit = credit_response.data[0]
                    current_balance = float(credit.get('current_balance', 0))
                    
                    # Update the balance based on transaction type
                    if transaction['transaction_type'] == 'credit':
                        new_balance = current_balance + float(transaction['amount'])
                    else:  # payment
                        new_balance = current_balance - float(transaction['amount'])
                    
                    # Update the customer_credits record
                    update_data = {
                        'current_balance': new_balance,
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    supabase.table('customer_credits').update(update_data).eq('id', credit['id']).execute()
            
            return response
            
        elif query_type == 'update':
            if not data or not filters:
                raise ValueError("Data and filters must be provided for update operations")
            
            # Ensure updated_at is present
            if 'updated_at' not in data:
                data['updated_at'] = datetime.now().isoformat()
            
            # Add filters
            for field, op, value in filters:
                if op == 'eq':
                    query = query.eq(field, value)
                elif op == 'neq':
                    query = query.neq(field, value)
                # Add other operators as needed
            
            # Update the data
            response = query.update(data).execute()
            return response
            
        elif query_type == 'delete':
            if not filters:
                raise ValueError("Filters must be provided for delete operations")
            
            # Add filters
            for field, op, value in filters:
                if op == 'eq':
                    query = query.eq(field, value)
                elif op == 'neq':
                    query = query.neq(field, value)
                # Add other operators as needed
            
            # Delete the data
            response = query.delete().execute()
            return response
            
        else:
            raise ValueError(f"Unsupported query type: {query_type}")
            
    except Exception as e:
        print(f"Error in Supabase query for {query_type} on {table_name}: {str(e)}")
        
        # Fall back to mock data as a last resort
        print("Falling back to mock data system")
        return mock_query_table(table_name, query_type, fields, filters, data)

# Initialize the Supabase clients
def init_supabase():
    """Initialize Supabase connections"""
    # Try to connect to Supabase with both client types
    get_supabase_client()
    get_supabase_admin_client()

# Auto-initialize on import
init_supabase() 