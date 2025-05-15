import os
import json
import uuid
from datetime import datetime
import streamlit as st
import supabase_service

def init_supabase_connection():
    """Initialize Supabase connection"""
    # This will be called automatically by the supabase_service module
    pass

def save_to_session_state():
    """Save current session data to session state"""
    # Already using session state, so this is a no-op
    pass

def login(phone, password, user_type='customer'):
    """
    Attempt a login using Supabase
    Returns (success, user_data_or_error_message) tuple
    """
    try:
        # For debugging
        print(f"Login attempt: phone={phone}, user_type={user_type}")
        
        supabase = supabase_service.get_supabase_admin_client()
        if not supabase:
            print("Login failed: No Supabase connection")
            return False, "Database connection error. Please try again later."
            
        # Try to find the user in Supabase
        user_response = supabase.table('users').select('*').eq('phone_number', phone).execute()
        
        print(f"User query response: {len(user_response.data) if user_response.data else 0} users found")
        
        # First check if any user exists with this phone number
        if not user_response.data:
            print(f"Login failed: No user found with phone {phone}")
            return False, "User not found. Please check your phone number or register for a new account."
        
        # Find user with matching user_type
        matched_users = [u for u in user_response.data if u.get('user_type') == user_type]
        
        if not matched_users:
            users_types = [u.get('user_type') for u in user_response.data]
            print(f"Login failed: User found but wrong type. Found: {users_types}, requested: {user_type}")
            return False, f"No {user_type} account found with this phone number. You might have registered as a {', '.join(users_types)}."
            
        user = matched_users[0]
        
        # Check password
        if user['password'] != password:
            print(f"Login failed: Incorrect password for {phone}")
            return False, "Incorrect password. Please check and try again."
            
        print(f"Login successful for {phone} as {user_type}")
        
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
    except Exception as e:
        print(f"Error in Supabase login: {str(e)}")
        return False, f"Login error: {str(e)}. Please try again later."

def register(phone, password, name, user_type='customer'):
    """
    Register a new user in Supabase
    Returns (success, message) tuple
    """
    try:
        supabase = supabase_service.get_supabase_admin_client()
        if not supabase:
            return False, "Database connection error. Please try again later."
        
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
            return False, "Failed to create user. Please try again."
        
        # Create related record based on user type
        if user_type == 'business':
            business_id = str(uuid.uuid4())
            business_data = {
                'id': business_id,
                'user_id': user_id,
                'name': f"{name}'s Business",
                'description': 'Business account',
                'access_pin': '1234',
                'created_at': datetime.now().isoformat()
            }
            business_response = supabase.table('businesses').insert(business_data).execute()
            
            if not business_response.data:
                # Roll back user creation
                supabase.table('users').delete().eq('id', user_id).execute()
                return False, "Failed to create business record."
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
                # Roll back user creation
                supabase.table('users').delete().eq('id', user_id).execute()
                return False, "Failed to create customer record."
        
        return True, "User registered successfully"
            
    except Exception as e:
        print(f"Error in Supabase registration: {str(e)}")
        return False, f"Registration error: {str(e)}. Please try again later."

def query_table(table_name, query_type='select', fields='*', filters=None, data=None):
    """
    Query a table using Supabase
    """
    return supabase_service.query_table(table_name, query_type, fields, filters, data)

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