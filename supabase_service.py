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
    print("Supabase module not available. Please install with: pip install supabase")

# Load environment variables
load_dotenv()

# Constants
DB_RETRY_ATTEMPTS = 3
DB_RETRY_DELAY = 1  # seconds

# Initialize Supabase client objects
supabase_client = None
supabase_admin_client = None
create_client_fn = None

# Try to determine if ClientOptions is available
try:
    from supabase.lib.client_options import ClientOptions
    HAS_CLIENT_OPTIONS = True
except ImportError:
    HAS_CLIENT_OPTIONS = False

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
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL', "https://ghbmfgomnqmffixfkdyp.supabase.co")
    supabase_key = os.getenv('SUPABASE_KEY', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdoYm1mZ29tbnFtZmZpeGZrZHlwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcxNDAxNTcsImV4cCI6MjA2MjcxNjE1N30.Fw750xiDWVPrl6ssr9p6AJTt--8zvnPoboxJiURvsOI")
    
    if not supabase_url or not supabase_key:
        print("Supabase URL and key must be set in environment variables")
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
                
                # Version-compatible options handling
                if HAS_CLIENT_OPTIONS:
                    try:
                        from supabase.lib.client_options import ClientOptions
                        # Try with ClientOptions
                        options = ClientOptions(
                            schema="public",
                            headers={},
                            auto_refresh_token=True,
                            persist_session=True
                        )
                    except Exception as e:
                        print(f"Error creating ClientOptions: {str(e)}")
                        options = {}  # Fallback to empty dict
                else:
                    # Simple dict for older versions
                    options = {}
                
                # Create a new client with proper options
                supabase_client = create_client_fn(supabase_url, supabase_key, options=options)
                
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
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL', "https://ghbmfgomnqmffixfkdyp.supabase.co")
    supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdoYm1mZ29tbnFtZmZpeGZrZHlwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzE0MDE1NywiZXhwIjoyMDYyNzE2MTU3fQ.RnbSqdIM5A67NuKHDOTdpqpu6G2zKJfhMeQapGUI2kw") 
    
    if not supabase_url or not supabase_service_key:
        print("Supabase URL and service key must be set in environment variables")
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
                
                # Version-compatible options handling
                if HAS_CLIENT_OPTIONS:
                    try:
                        from supabase.lib.client_options import ClientOptions
                        # Try with ClientOptions
                        options = ClientOptions(
                            schema="public",
                            headers={},
                            auto_refresh_token=True,
                            persist_session=True
                        )
                    except Exception as e:
                        print(f"Error creating ClientOptions: {str(e)}")
                        options = {}  # Fallback to empty dict
                else:
                    # Simple dict for older versions
                    options = {}
                
                # Create admin client with proper options
                supabase_admin_client = create_client_fn(supabase_url, supabase_service_key, options=options)
                
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
        import auth_service
        return auth_service.mock_query_table(table_name, query_type, fields, filters, data)
    
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
        
        # Create a response-like object with empty data
        class MockResponse:
            def __init__(self, data):
                self.data = data
        
        # Fall back to mock data as a last resort
        print("Falling back to mock data system")
        import auth_service
        return auth_service.mock_query_table(table_name, query_type, fields, filters, data)

# Initialize the Supabase clients
def init_supabase():
    """Initialize Supabase connections"""
    # Try to connect to Supabase with both client types
    get_supabase_client()
    get_supabase_admin_client()

# Auto-initialize on import
init_supabase() 