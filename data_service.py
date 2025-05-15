import os
import uuid
from datetime import datetime
import streamlit as st
import auth_service
import supabase_service

# Utility function to ensure valid UUIDs
def safe_uuid(id_value):
    """Ensure a value is a valid UUID string or generate a new one"""
    if not id_value:
        return str(uuid.uuid4())
    
    try:
        # Test if it's a valid UUID
        uuid.UUID(str(id_value))
        return str(id_value)
    except (ValueError, TypeError, AttributeError):
        print(f"WARNING: Invalid UUID '{id_value}' - generating new UUID")
        return str(uuid.uuid4())

def query_table(table_name, query_type='select', fields='*', filters=None, data=None):
    """
    Query a table with proper error handling
    Tries to use real Supabase first, falls back to mock data if needed
    """
    # Use the Supabase service to query the table
    return supabase_service.query_table(table_name, query_type, fields, filters, data)

def ensure_customer_credit_exists(business_id, customer_id, initial_balance=0):
    """
    Ensure a credit relationship exists between a business and customer.
    If it doesn't exist, create it. If it does, return it.
    
    Args:
        business_id: UUID of the business
        customer_id: UUID of the customer
        initial_balance: Initial balance if a new relationship is created
        
    Returns:
        The credit record
    """
    business_id = safe_uuid(business_id)
    customer_id = safe_uuid(customer_id)
    
    # Check if relationship already exists
    existing_credit = query_table('customer_credits', 
                                 filters=[('business_id', 'eq', business_id),
                                         ('customer_id', 'eq', customer_id)])
    
    # Return existing credit if found
    if existing_credit and existing_credit.data:
        return existing_credit.data[0]
    
    # Create a new credit relationship
    credit_data = {
        'id': str(uuid.uuid4()),
        'business_id': business_id,
        'customer_id': customer_id,
        'current_balance': initial_balance,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    credit_insert = query_table('customer_credits', query_type='insert', data=credit_data)
    
    if credit_insert and credit_insert.data:
        return credit_insert.data[0]
    else:
        # Return the data even if insert failed (for mock data system)
        return credit_data

def get_business_customers(business_id):
    """Get all customers associated with a business"""
    business_id = safe_uuid(business_id)
    
    # Get all customer credits for this business
    customers_response = query_table('customer_credits', filters=[('business_id', 'eq', business_id)])
    customer_credits = customers_response.data if customers_response and customers_response.data else []
    
    # Gather all customer details
    customers = []
    for credit in customer_credits:
        customer_id = credit.get('customer_id')
        if customer_id:
            # Get customer details
            customer_response = query_table('customers', filters=[('id', 'eq', customer_id)])
            if customer_response and customer_response.data:
                customer = customer_response.data[0]
                # Merge customer details with credit information
                customer_with_credit = {
                    **customer,
                    'current_balance': credit.get('current_balance', 0)
                }
                customers.append(customer_with_credit)
    
    return customers

def get_business_summary(business_id):
    """Get summary data for a business"""
    business_id = safe_uuid(business_id)
    
    # Get summary data with error handling
    total_customers = 0
    total_credit = 0
    total_payments = 0
    transactions = []
    customers = []
    
    # Get customer credits to display customers on dashboard
    customers_response = query_table('customer_credits', filters=[('business_id', 'eq', business_id)])
    customer_credits = customers_response.data if customers_response and customers_response.data else []
    
    # Total customers
    total_customers = len(customer_credits)
    
    # Get customer details for each customer credit
    for credit in customer_credits:
        customer_id = safe_uuid(credit.get('customer_id'))
        try:
            customer_response = query_table('customers', filters=[('id', 'eq', customer_id)])
            if customer_response and customer_response.data:
                customer = customer_response.data[0]
                # Merge customer details with credit information
                customer_with_credit = {
                    **customer,
                    'current_balance': credit.get('current_balance', 0)
                }
                customers.append(customer_with_credit)
        except Exception as e:
            print(f"ERROR retrieving customer {customer_id}: {str(e)}")
    
    # Total credit
    credit_response = query_table('transactions', fields='amount', 
                                filters=[('business_id', 'eq', business_id), ('transaction_type', 'eq', 'credit')])
    total_credit = sum([float(t.get('amount', 0)) for t in credit_response.data]) if credit_response and credit_response.data else 0
    
    # Total payments
    payment_response = query_table('transactions', fields='amount',
                                filters=[('business_id', 'eq', business_id), ('transaction_type', 'eq', 'payment')])
    total_payments = sum([float(t.get('amount', 0)) for t in payment_response.data]) if payment_response and payment_response.data else 0
    
    # Recent transactions
    transactions_response = query_table('transactions', 
                                   filters=[('business_id', 'eq', business_id)])
    transactions = transactions_response.data if transactions_response and transactions_response.data else []
    
    # Get customer names for transactions
    for transaction in transactions:
        customer_id = safe_uuid(transaction.get('customer_id'))
        try:
            customer_response = query_table('customers', fields='name', filters=[('id', 'eq', customer_id)])
            if customer_response and customer_response.data:
                transaction['customer_name'] = customer_response.data[0].get('name', 'Unknown')
            else:
                transaction['customer_name'] = 'Unknown'
        except Exception as e:
            print(f"ERROR getting customer name: {str(e)}")
            transaction['customer_name'] = 'Unknown'
    
    # Sort transactions by date, newest first
    transactions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    # Prepare data to return
    summary = {
        'total_customers': total_customers,
        'total_credit': total_credit,
        'total_payments': total_payments
    }
    
    return summary, transactions, customers

def get_customer_businesses(customer_id):
    """Get all businesses associated with a customer"""
    customer_id = safe_uuid(customer_id)
    
    # Get businesses where customer has credit
    businesses = []
    businesses_response = query_table('customer_credits', filters=[('customer_id', 'eq', customer_id)])
    credit_records = businesses_response.data if businesses_response and businesses_response.data else []
    
    # For each credit record, get the business details
    for credit in credit_records:
        business_id = credit.get('business_id')
        if business_id:
            business_response = query_table('businesses', filters=[('id', 'eq', business_id)])
            if business_response and business_response.data:
                business = business_response.data[0]
                # Merge business data with credit data
                business_with_credit = {**business, 'current_balance': credit.get('current_balance', 0)}
                businesses.append(business_with_credit)
            else:
                # If we can't get business details, still show the credit record with minimal info
                businesses.append({
                    'id': business_id,
                    'name': 'Unknown Business',
                    'current_balance': credit.get('current_balance', 0)
                })
    
    return businesses

def get_customer_business_view(business_id, customer_id):
    """Get business and transaction details for a customer view"""
    business_id = safe_uuid(business_id)
    customer_id = safe_uuid(customer_id)
    
    # Ensure credit relationship exists - this will create it if it doesn't
    credit = ensure_customer_credit_exists(business_id, customer_id)
    
    # Get business details
    business_response = query_table('businesses', filters=[('id', 'eq', business_id)])
    business = business_response.data[0] if business_response and business_response.data else {}
    
    # Get customer details
    customer_response = query_table('customers', filters=[('id', 'eq', customer_id)])
    customer = customer_response.data[0] if customer_response and customer_response.data else {}
    
    # Merge customer details with credit information
    current_balance = credit.get('current_balance', 0) if credit else 0
    if customer:
        customer = {**customer, 'current_balance': current_balance}
    
    # Get transaction history for this customer with this business
    transactions = []
    credit_total = 0
    payment_total = 0
    
    transactions_response = query_table('transactions',
                                      filters=[('business_id', 'eq', business_id),
                                              ('customer_id', 'eq', customer_id)])
    transactions = transactions_response.data if transactions_response and transactions_response.data else []
    
    # Calculate totals and sort transactions by date, newest first
    for transaction in transactions:
        if transaction.get('transaction_type') == 'credit':
            credit_total += float(transaction.get('amount', 0))
        else:  # payment
            payment_total += float(transaction.get('amount', 0))
    
    # Sort transactions by date, newest first
    transactions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return business, customer, transactions, credit_total, payment_total, current_balance

def format_datetime(value, format='%d %b %Y, %I:%M %p'):
    """Format datetime string"""
    if value:
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                return value
        return value.strftime(format)
    return '' 