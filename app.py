import streamlit as st
import os
import uuid
import qrcode
from io import BytesIO
import base64
from datetime import datetime
import auth_service
import data_service

# App configuration
st.set_page_config(
    page_title="KathaPe - Digital Credit Book",
    page_icon="📒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper function to generate QR code
def generate_qr_code(data, size=200):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save image to BytesIO
    buffered = BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

# Theme configuration with dark mode and mobile optimization
theme_css = """
<style>
    /* Base styles - common for both light and dark mode */
    .main-header {
        font-size: 2.2rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
    }
    .card {
        padding: 1.2rem;
        border-radius: 0.8rem;
        box-shadow: 0 0.15rem 1.75rem rgba(0, 0, 0, 0.12);
        margin-bottom: 1rem;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 0.5rem 2rem rgba(0, 0, 0, 0.18);
    }
    .positive {
        color: #4CAF50;
        font-weight: bold;
    }
    .negative {
        color: #F44336;
        font-weight: bold;
    }
    
    .neutral {
        color: #9E9E9E;
        font-weight: bold;
    }
    
    /* Card title */
    .card h3 {
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        opacity: 0.8;
    }
    
    /* Card value */
    .card h2 {
        font-size: 1.8rem;
        margin-top: 0;
    }
    
    /* Make buttons more consistent and modern */
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem !important;
        padding: 0.5rem !important;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        border: none !important;
        font-weight: 500 !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
    }
    
    /* QR code container */
    .qr-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border-radius: 0.8rem;
        box-shadow: 0 0.15rem 1.75rem rgba(0, 0, 0, 0.1);
    }
    
    .qr-code-image {
        max-width: 100%;
        height: auto;
        margin-bottom: 0.5rem;
        border-radius: 0.5rem;
    }
    
    .pin-display {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        letter-spacing: 0.25rem;
    }
    
    /* Transaction history */
    .transaction {
        padding: 0.75rem;
        margin-bottom: 0.8rem;
        border-radius: 0.5rem;
        display: flex;
        flex-direction: column;
        transition: transform 0.2s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .transaction:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    
    .transaction-type {
        font-weight: bold;
        margin-bottom: 0.25rem;
    }
    
    .transaction-amount {
        font-size: 1.2rem;
        margin-bottom: 0.25rem;
    }
    
    .transaction-date {
        font-size: 0.8rem;
        opacity: 0.8;
    }
    
    /* Camera upload button */
    .camera-upload {
        width: 100%;
        margin-top: 1rem;
    }
    
    /* Form styling */
    .stTextInput>div>div>input {
        border-radius: 0.5rem !important;
        padding: 0.5rem 1rem !important;
        border: 1px solid rgba(150, 150, 150, 0.2) !important;
    }
    
    .stNumberInput>div>div>input {
        border-radius: 0.5rem !important;
        padding: 0.5rem 1rem !important;
        border: 1px solid rgba(150, 150, 150, 0.2) !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5em;
        border-radius: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        height: 3em;
        white-space: nowrap;
        border-radius: 0.5rem;
        padding: 0 1rem;
        font-weight: 500;
    }
    
    /* Dividers */
    hr {
        margin: 1.5rem 0;
        opacity: 0.2;
        border: none;
        height: 1px;
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem;
        }
        .sub-header {
            font-size: 1.1rem;
        }
        .card h2 {
            font-size: 1.5rem;
        }
        body {
            font-size: 14px;
        }
        /* Center everything for mobile */
        .stApp {
            max-width: 100%;
            margin: 0 auto;
            padding: 0 !important;
        }
        /* Reduce margins for mobile */
        .block-container {
            max-width: 100% !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            padding-top: 0.5rem !important;
        }
        /* Make sidebar full width on mobile */
        section[data-testid="stSidebar"] {
            width: 100% !important;
            min-width: 100% !important;
        }
        /* Smaller buttons on mobile */
        .stButton>button {
            padding: 0.4rem !important;
            font-size: 0.9rem !important;
        }
        /* Adjust card padding */
        .card {
            padding: 0.8rem;
            margin-bottom: 0.8rem;
        }
        /* Smaller headings */
        h1 {
            font-size: 1.8rem !important;
        }
        h2 {
            font-size: 1.5rem !important;
        }
        h3 {
            font-size: 1.2rem !important;
        }
        /* Reduce transaction padding */
        .transaction {
            padding: 0.6rem;
            margin-bottom: 0.6rem;
        }
        /* Reduce tab padding */
        .stTabs [data-baseweb="tab"] {
            padding: 0 0.5rem;
            font-size: 0.9rem;
        }
    }
    
    /* Dark mode specific styles */
    @media (prefers-color-scheme: dark) {
        .main-header {
            color: #64B5F6;
        }
        .sub-header {
            color: #E0E0E0;
        }
        .card {
            background-color: #2C3333;
            color: #E0E0E0;
        }
        .card h3 {
            color: #B0BEC5;
        }
        .positive {
            color: #81C784;
        }
        .negative {
            color: #E57373;
        }
        .neutral {
            color: #BDBDBD;
        }
        .highlight {
            background-color: #2C3333;
        }
        .pin-display {
            background-color: #1E2222;
            color: #E0E0E0;
            border: 1px solid #546E7A;
        }
        .transaction {
            background-color: #1E2222;
        }
        /* Sidebar and button styles for dark mode */
        .stButton>button {
            background-color: #455A64;
            color: #E0E0E0;
            border: none;
        }
        .stButton>button:hover {
            background-color: #546E7A;
        }
        .active-button>button {
            background-color: #1976D2;
            color: white;
        }
        .qr-container {
            background-color: #1E2222;
        }
        /* Form styling for dark mode */
        .stTextInput>div>div>input {
            background-color: #263238 !important;
            color: #E0E0E0 !important;
        }
        .stNumberInput>div>div>input {
            background-color: #263238 !important;
            color: #E0E0E0 !important;
        }
        /* Tab styling for dark mode */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #263238;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #37474F;
            color: #E0E0E0;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #1976D2;
        }
    }
    
    /* Light mode specific styles */
    @media (prefers-color-scheme: light) {
        .main-header {
            color: #1E88E5;
        }
        .sub-header {
            color: #424242;
        }
        .card {
            background-color: white;
            color: #333333;
        }
        .card h3 {
            color: #616161;
        }
        .highlight {
            background-color: #f0f2f6;
        }
        .pin-display {
            background-color: #f0f2f6;
            color: #333333;
            border: 1px solid #ddd;
        }
        .transaction {
            background-color: #f8f9fa;
        }
        /* Sidebar and button styles for light mode */
        .stButton>button {
            background-color: #f0f2f6;
            color: #424242;
            border: none;
        }
        .stButton>button:hover {
            background-color: #e0e5eb;
        }
        .active-button>button {
            background-color: #1E88E5;
            color: white;
        }
        .qr-container {
            background-color: #f0f2f6;
        }
        .negative {
            color: #F44336;
        }
        .neutral {
            color: #757575;
        }
        /* Form styling for light mode */
        .stTextInput>div>div>input {
            background-color: #ffffff !important;
            border: 1px solid #e0e0e0 !important;
        }
        .stNumberInput>div>div>input {
            background-color: #ffffff !important;
            border: 1px solid #e0e0e0 !important;
        }
        /* Tab styling for light mode */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #f0f2f6;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #e0e5eb;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #1E88E5;
            color: white;
        }
    }
</style>
"""

# Apply the theme CSS
st.markdown(theme_css, unsafe_allow_html=True)

# Force dark mode (optional)
dark_mode_css = """
<style>
html {
    color-scheme: dark;
}
</style>
"""
st.markdown(dark_mode_css, unsafe_allow_html=True)

# Mobile optimization - Additional CSS for better mobile experience
mobile_responsive_css = """
<style>
    /* Optimize for mobile screens */
    @media (max-width: 768px) {
        /* Make inputs more touch-friendly */
        input, select, textarea {
            font-size: 16px !important; /* Prevents iOS zoom on focus */
        }
        
        /* Improve form layout on mobile */
        .st-bq {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        
        /* Adjust widgets to be more touch-friendly */
        .stSlider, .stCheckbox {
            padding: 1rem 0 !important;
        }
        
        /* Reduce padding around elements */
        div.stButton > button {
            margin-top: 0.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Better spacing for mobile */
        .row-widget {
            padding: 0.2rem 0 !important;
        }
        
        /* Fix sidebar behavior on mobile */
        section[data-testid="stSidebar"][aria-expanded="true"] {
            width: 80% !important;
        }
        
        /* Improve column layout on mobile */
        .row-widget.stHorizontal {
            flex-wrap: wrap !important;
        }
        
        /* Make alerts more readable on mobile */
        .stAlert {
            padding: 0.5rem !important;
        }
    }
</style>
"""
st.markdown(mobile_responsive_css, unsafe_allow_html=True)

# Global navigation
def show_navbar():
    if auth_service.is_logged_in():
        cols = st.columns([1, 3, 1])
        with cols[0]:
            st.markdown(f"**Welcome, {st.session_state.user_name}**")
        with cols[2]:
            if st.button("Logout", key="navbar_logout"):
                auth_service.logout()
                st.rerun()

# Pages
def login_page():
    # Hide the default Streamlit menu
    hide_streamlit_style = """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    # Centered logo/app name with animation
    st.markdown("""
    <div style="text-align: center; animation: fadeIn 1s ease-in-out;">
        <h1 class='main-header' style="margin-bottom: 0.5rem;">KathaPe</h1>
        <h2 class='sub-header' style="margin-top: 0; margin-bottom: 2rem;">Digital Credit Book</h2>
    </div>
    
    <style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create more modern tabs
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            st.markdown("<h3 style='text-align: center; margin-bottom: 1rem;'>Welcome Back</h3>", unsafe_allow_html=True)
            
            phone = st.text_input("Phone Number", placeholder="Enter your 10-digit phone number")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            user_type = st.selectbox("Login As", ["business", "customer"])
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not phone or not password:
                    st.error("Please enter both phone number and password")
                else:
                    success, user = auth_service.mock_login(phone, password, user_type)
                    if success:
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("User not found or invalid credentials. Please check your details and try again.")
    
    with tab2:
        with st.form("register_form"):
            st.markdown("<h3 style='text-align: center; margin-bottom: 1rem;'>Create Account</h3>", unsafe_allow_html=True)
            
            r_name = st.text_input("Full Name", placeholder="Enter your full name")
            r_phone = st.text_input("Phone Number", placeholder="Enter a 10-digit phone number")
            r_password = st.text_input("Password", type="password", placeholder="Create a strong password")
            r_user_type = st.selectbox("Register As", ["business", "customer"])
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                r_submit = st.form_submit_button("Register", use_container_width=True)
            
            if r_submit:
                if not r_name or not r_phone or not r_password:
                    st.error("Please fill in all the fields")
                elif len(r_phone) != 10 or not r_phone.isdigit():
                    st.error("Please enter a valid 10-digit phone number")
                elif len(r_password) < 6:
                    st.error("Password should be at least 6 characters long")
                else:
                    success, message = auth_service.mock_register(r_phone, r_password, r_name, r_user_type)
                    if success:
                        st.success(message)
                        st.info("Please login with your new account")
                    else:
                        st.error(message)
    
    # Demo credentials info in a more elegant expandable section
    with st.expander("Demo Credentials", expanded=False):
        st.markdown("""
        <div style="background-color: rgba(0,0,0,0.05); padding: 1rem; border-radius: 0.5rem; margin-top: 0.5rem;">
            <p><strong>Business:</strong> Phone: 9999999999, Password: password123</p>
            <p><strong>Customer:</strong> Use any 10-digit number and 'demo123' as password</p>
        </div>
        """, unsafe_allow_html=True)

def business_dashboard():
    st.markdown("<h1 class='main-header'>Business Dashboard</h1>", unsafe_allow_html=True)
    
    business_id = st.session_state.business_id
    
    # Get business summary data
    summary, transactions, customers = data_service.get_business_summary(business_id)
    
    # Display summary cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class='card'>
            <h3>Total Customers</h3>
            <h2>{summary['total_customers']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='card'>
            <h3>Total Credit Given</h3>
            <h2 class='positive'>₹{summary['total_credit']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='card'>
            <h3>Total Payments Received</h3>
            <h2 class='negative'>₹{summary['total_payments']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Business QR code
    qr_col1, qr_col2 = st.columns([1, 2])
    with qr_col1:
        st.markdown("<h3 style='text-align: center;'>Your Business QR Code</h3>", unsafe_allow_html=True)
        
        # Generate QR code with business ID
        qr_image = generate_qr_code(business_id)
        
        # Display QR code and PIN
        st.markdown(f"""
        <div class='qr-container'>
            <img src="{qr_image}" class="qr-code-image" alt="Business QR Code">
            <div>Business ID: {business_id[:8]}...</div>
            <div>Access PIN: <span class='pin-display'>{st.session_state.access_pin}</span></div>
            <small>Share this QR code with your customers to connect</small>
        </div>
        """, unsafe_allow_html=True)
    
    with qr_col2:
        st.markdown("<h3 style='text-align: center;'>Recent Transactions</h3>", unsafe_allow_html=True)
        if transactions:
            for t in transactions[:5]:  # Show only 5 most recent
                transaction_type = t.get('transaction_type', '')
                amount = float(t.get('amount', 0))
                date = data_service.format_datetime(t.get('created_at', ''))
                customer_name = t.get('customer_name', 'Unknown')
                
                # Different styling for credit vs payment
                transaction_class = "negative" if transaction_type == 'credit' else "positive"
                transaction_icon = "🔴" if transaction_type == 'credit' else "🟢"
                transaction_text = f"Gave credit to {customer_name}" if transaction_type == 'credit' else f"Received payment from {customer_name}"
                
                st.markdown(f"""
                <div class='transaction'>
                    <div class='transaction-type'>{transaction_icon} {transaction_text}</div>
                    <div class='transaction-amount class='{transaction_class}'>₹{amount}</div>
                    <div class='transaction-date'>{date}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No transactions yet")

def business_customers():
    st.markdown("<h1 class='main-header'>Customers</h1>", unsafe_allow_html=True)
    
    business_id = st.session_state.business_id
    
    # Get all customers for this business
    customers = data_service.get_business_customers(business_id)
    
    # Add new customer section
    with st.expander("Add New Customer"):
        with st.form("add_customer_form"):
            customer_name = st.text_input("Customer Name")
            customer_phone = st.text_input("Customer Phone")
            submit_customer = st.form_submit_button("Add Customer")
            
            if submit_customer:
                # Check if customer exists first
                customer_exists = False
                # Check in customers list
                for customer in customers:
                    if customer.get('phone_number') == customer_phone:
                        customer_exists = True
                        st.success(f"Customer {customer_name} already exists!")
                        break
                
                if not customer_exists:
                    # Register new customer and create credit relationship
                    success, message = auth_service.mock_register(
                        customer_phone, 
                        "password123",  # Default password for simplicity
                        customer_name, 
                        "customer"
                    )
                    
                    if success:
                        # Find the newly created customer in mock users
                        for phone, user in st.session_state.mock_users.items():
                            if phone == customer_phone:
                                # Ensure this customer has a credit relationship with this business
                                data_service.ensure_customer_credit_exists(business_id, user['id'])
                                st.success(f"Added customer {customer_name}")
                                st.rerun()
                                break
                    else:
                        st.error(message)
    
    # Display customers
    if customers:
        st.markdown("<h3>Your Customers</h3>", unsafe_allow_html=True)
        
        for i, customer in enumerate(customers):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.write(f"**{customer.get('name', 'Unknown')}**")
            with col2:
                st.write(f"Phone: {customer.get('phone_number', 'N/A')}")
            with col3:
                st.write(f"Balance: ₹{customer.get('current_balance', 0)}")
            with col4:
                if st.button(f"View", key=f"business_view_customer_{i}"):
                    st.session_state.selected_customer_id = customer.get('id')
                    st.session_state.page = "business_customer_detail"
                    st.rerun()
    else:
        st.info("No customers yet. Add your first customer!")

def business_customer_detail():
    st.markdown("<h1 class='main-header'>Customer Details</h1>", unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Customers", key="back_to_customers"):
        st.session_state.page = "business_customers"
        st.rerun()
    
    business_id = st.session_state.business_id
    customer_id = st.session_state.selected_customer_id
    
    # Get customer and transaction details
    business, customer, transactions, credit_total, payment_total, current_balance = \
        data_service.get_customer_business_view(business_id, customer_id)
    
    st.markdown(f"<h2 class='sub-header'>{customer.get('name', 'Unknown')}</h2>", unsafe_allow_html=True)
    st.write(f"Phone: {customer.get('phone_number', 'N/A')}")
    
    # Summary cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class='card'>
            <h3>Total Credit</h3>
            <h2 class='positive'>₹{credit_total}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='card'>
            <h3>Total Payments</h3>
            <h2 class='negative'>₹{payment_total}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='card'>
            <h3>Current Balance</h3>
            <h2>₹{current_balance}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Add transaction form
    st.markdown("<h3>Add Transaction</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        with st.form("add_credit_form"):
            credit_amount = st.number_input("Credit Amount", min_value=1, value=100)
            credit_note = st.text_input("Note (optional)", key="credit_note")
            submit_credit = st.form_submit_button("Add Credit")
            
            if submit_credit:
                # Create credit transaction
                transaction_data = {
                    'id': str(uuid.uuid4()),
                    'business_id': business_id,
                    'customer_id': customer_id,
                    'amount': credit_amount,
                    'transaction_type': 'credit',
                    'notes': credit_note,
                    'created_at': datetime.now().isoformat()
                }
                
                # Insert transaction - this will automatically update the balance in supabase_service.py
                transaction_response = data_service.query_table('transactions', query_type='insert', data=transaction_data)
                
                if transaction_response and transaction_response.data:
                    # Ensure the customer credit record exists with the updated balance
                    data_service.ensure_customer_credit_exists(business_id, customer_id)
                    st.success(f"Added ₹{credit_amount} credit")
                    st.rerun()
                else:
                    st.error("Failed to add credit. Please try again.")
    
    with col2:
        with st.form("add_payment_form"):
            payment_amount = st.number_input("Payment Amount", min_value=1, value=100)
            payment_note = st.text_input("Note (optional)", key="payment_note")
            submit_payment = st.form_submit_button("Add Payment")
            
            if submit_payment:
                # Create payment transaction
                transaction_data = {
                    'id': str(uuid.uuid4()),
                    'business_id': business_id,
                    'customer_id': customer_id,
                    'amount': payment_amount,
                    'transaction_type': 'payment',
                    'notes': payment_note,
                    'created_at': datetime.now().isoformat()
                }
                
                # Insert transaction - this will automatically update the balance in supabase_service.py
                transaction_response = data_service.query_table('transactions', query_type='insert', data=transaction_data)
                
                if transaction_response and transaction_response.data:
                    st.success(f"Added ₹{payment_amount} payment")
                    st.rerun()
                else:
                    st.error("Failed to add payment. Please try again.")
    
    # Transaction history
    st.markdown("<h3>Transaction History</h3>", unsafe_allow_html=True)
    
    if transactions:
        # First, display pending credit requests at the top with approve buttons
        pending_requests = [t for t in transactions if t.get('transaction_type') == 'credit_request']
        if pending_requests:
            st.markdown("<h4>Pending Credit Requests</h4>", unsafe_allow_html=True)
            for request in pending_requests:
                amount = float(request.get('amount', 0))
                date = data_service.format_datetime(request.get('created_at', ''))
                note = request.get('notes', '')
                request_id = request.get('id', '')
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"⚪ **Credit Request:** ₹{amount} on {date}")
                    if note:
                        st.markdown(f"Note: {note}")
                with col2:
                    if st.button("Approve", key=f"approve_request_{request_id}"):
                        # Create credit transaction
                        transaction_data = {
                            'id': str(uuid.uuid4()),
                            'business_id': business_id,
                            'customer_id': customer_id,
                            'amount': amount,
                            'transaction_type': 'credit',
                            'notes': f"Approved request: {note}" if note else "Approved request",
                            'created_at': datetime.now().isoformat()
                        }
                        
                        # Insert transaction
                        transaction_response = data_service.query_table('transactions', query_type='insert', data=transaction_data)
                        
                        if transaction_response and transaction_response.data:
                            # Now mark the request as processed
                            update_data = {
                                'transaction_type': 'credit_request_approved',
                                'updated_at': datetime.now().isoformat()
                            }
                            
                            data_service.query_table('transactions', query_type='update', 
                                                   data=update_data, 
                                                   filters=[('id', 'eq', request_id)])
                            
                            st.success(f"Approved ₹{amount} credit request")
                            st.rerun()
                        else:
                            st.error("Failed to approve request. Please try again.")
                
                st.markdown("---")
            
        # Display all transactions
        st.markdown("<h4>All Transactions</h4>", unsafe_allow_html=True)
        for t in transactions:
            transaction_type = t.get('transaction_type', '')
            amount = float(t.get('amount', 0))
            date = data_service.format_datetime(t.get('created_at', ''))
            note = t.get('notes', '')
            
            if transaction_type == 'credit':
                st.markdown(f"🔴 **Credit:** ₹{amount} on {date}")
            elif transaction_type == 'payment':
                st.markdown(f"🟢 **Payment:** ₹{amount} on {date}")
            elif transaction_type == 'credit_request':
                st.markdown(f"⚪ **Credit Request (Pending):** ₹{amount} on {date}")
            elif transaction_type == 'credit_request_approved':
                st.markdown(f"⚪ **Credit Request (Approved):** ₹{amount} on {date}")
            else:
                st.markdown(f"⚪ **{transaction_type.capitalize()}:** ₹{amount} on {date}")
            
            if note:
                st.markdown(f"Note: {note}")
            
            st.markdown("---")
    else:
        st.info("No transactions yet")

def business_profile():
    st.markdown("<h1 class='main-header'>Business Profile</h1>", unsafe_allow_html=True)
    
    business_id = st.session_state.business_id
    
    # Get business details
    business_response = data_service.query_table('businesses', filters=[('id', 'eq', business_id)])
    business = business_response.data[0] if business_response and business_response.data else {}
    
    # Display business details
    st.markdown(f"<h2 class='sub-header'>{business.get('name', st.session_state.business_name)}</h2>", unsafe_allow_html=True)
    
    with st.form("update_business_form"):
        business_name = st.text_input("Business Name", value=business.get('name', st.session_state.business_name))
        business_description = st.text_area("Business Description", value=business.get('description', ''))
        access_pin = st.text_input("Access PIN", value=business.get('access_pin', st.session_state.access_pin), max_chars=4)
        
        submit_business = st.form_submit_button("Update Business Profile")
        
        if submit_business:
            # Update business data
            business_data = {
                'name': business_name,
                'description': business_description,
                'access_pin': access_pin
            }
            
            # Update business
            business_response = data_service.query_table('businesses', 
                                                       query_type='update', 
                                                       data=business_data,
                                                       filters=[('id', 'eq', business_id)])
            
            if business_response and business_response.data:
                st.session_state.business_name = business_name
                st.session_state.access_pin = access_pin
                st.success("Business profile updated successfully")
            else:
                st.error("Failed to update business profile. Please try again.")

def customer_dashboard():
    # Hide the default Streamlit menu
    hide_streamlit_style = """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    # Welcome message with user name
    customer_id = st.session_state.customer_id
    
    # Header row with welcome and logout - removing duplicate
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"<h4>Welcome, {st.session_state.user_name}</h4>", unsafe_allow_html=True)
    
    # Main heading - no duplicate welcome
    st.markdown("<h1 class='main-header'>My Credit Book</h1>", unsafe_allow_html=True)
    
    # Get businesses where customer has credit
    businesses = data_service.get_customer_businesses(customer_id)
    
    # Add a divider for clean separation
    st.markdown("<hr style='margin: 1rem 0 1.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # Display businesses
    if businesses:
        st.markdown("<h3 style='text-align: center; margin-bottom: 1.5rem;'>Your Credit Accounts</h3>", unsafe_allow_html=True)
        
        # Create a cleaner, more modern list of businesses
        for i, business in enumerate(businesses):
            # Use a card-like design for each business
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.markdown(f"<h4 style='margin-bottom: 0.3rem;'>{business.get('name', 'Unknown Business')}</h4>", unsafe_allow_html=True)
                with col2:
                    balance = business.get('current_balance', 0)
                    balance_color = "#E57373" if float(balance) > 0 else "#81C784"
                    st.markdown(f"<div style='margin-top: 0.2rem;'>Balance: <span style='color: {balance_color}; font-weight: bold;'>₹{balance}</span></div>", unsafe_allow_html=True)
                with col3:
                    if st.button(f"View", key=f"customer_view_business_{i}", use_container_width=True):
                        st.session_state.selected_business_id = business.get('id')
                        st.session_state.page = "customer_business_detail"
                        st.rerun()
                
                # Add a subtle divider between businesses
                st.markdown("<hr style='margin: 0.5rem 0 1rem 0; opacity: 0.15;'>", unsafe_allow_html=True)
    else:
        st.info("No credit accounts yet. Connect to a business to get started.")
    
    # Add a divider for clean separation
    st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # QR code scanner with improved layout
    st.markdown("<h3 style='text-align: center; margin-bottom: 1rem;'>Connect to Business</h3>", unsafe_allow_html=True)
    
    # Create two tabs - one for manual entry, one for camera
    scan_tab1, scan_tab2 = st.tabs(["Manual Entry", "Scan QR"])
    
    with scan_tab1:
        with st.form("connect_business_form"):
            st.markdown("<h4 style='margin-bottom: 1rem;'>Enter Business Details</h4>", unsafe_allow_html=True)
            
            business_code = st.text_input("Business ID", placeholder="Enter the business ID")
            business_pin = st.text_input("Access PIN (4-digit)", max_chars=4, placeholder="Enter the 4-digit PIN")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                connect_button = st.form_submit_button("Connect", use_container_width=True)
            
            if connect_button and business_code:
                # Check if business exists
                business_response = data_service.query_table('businesses', filters=[('id', 'eq', business_code)])
                
                if business_response and business_response.data:
                    business = business_response.data[0]
                    # Verify PIN if provided
                    if business_pin and business_pin != business.get('access_pin', ''):
                        st.error("Incorrect business PIN. Please check and try again.")
                    else:
                        # Ensure credit relationship exists
                        data_service.ensure_customer_credit_exists(business_code, customer_id)
                        st.success("Connected to business successfully!")
                        st.rerun()
                else:
                    st.error("Business not found. Please check the code and try again.")
    
    with scan_tab2:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 1rem;'>
            <p>Scan business QR code with your camera</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Camera upload option with better styling
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            uploaded_qr = st.camera_input("Take a picture of QR code", key="qr_camera")
            
            if uploaded_qr is not None:
                # In a real app, we would process the QR code image here
                # For now, show a placeholder message
                st.info("QR code processing would happen here. For now, please use the Manual Entry tab.")

def customer_business_detail():
    # Hide the default Streamlit menu
    hide_streamlit_style = """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # Back button in a cleaner layout
    col_back, col_title, col_spacer = st.columns([1, 2, 1])
    with col_back:
        if st.button("← Back", key="back_to_dashboard", use_container_width=True):
            st.session_state.page = "customer_dashboard"
            st.rerun()
    
    with col_title:
        st.markdown("<h1 class='main-header'>Business Account</h1>", unsafe_allow_html=True)
    
    business_id = st.session_state.selected_business_id
    customer_id = st.session_state.customer_id
    
    # Get business and transaction details
    business, customer, transactions, credit_total, payment_total, current_balance = \
        data_service.get_customer_business_view(business_id, customer_id)
    
    st.markdown(f"<h2 class='sub-header'>{business.get('name', 'Unknown Business')}</h2>", unsafe_allow_html=True)
    
    # Summary cards in a clean, modern layout
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class='card'>
            <h3>Total Credit</h3>
            <h2 class='positive'>₹{credit_total}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='card'>
            <h3>Total Payments</h3>
            <h2 class='negative'>₹{payment_total}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='card'>
            <h3>Current Balance</h3>
            <h2>₹{current_balance}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Add a divider for clean separation
    st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # Transaction forms in a cleaner layout
    st.markdown("<h3 style='text-align: center; margin-bottom: 1.5rem;'>Transactions</h3>", unsafe_allow_html=True)
    
    # Create tabs for different actions
    tabs = st.tabs(["Take Credit", "Make Payment"])
    
    with tabs[0]:
        with st.form("take_credit_form"):
            st.markdown("<h4 style='margin-bottom: 1rem;'>Take Credit</h4>", unsafe_allow_html=True)
            
            # More elegant number input with clear layout
            credit_amount = st.number_input("Credit Amount (₹)", min_value=1, value=100, 
                                           step=10, help="Enter the amount of credit to take")
            
            credit_note = st.text_input("Note (optional)", key="credit_note_customer", 
                                        placeholder="What is this credit for?")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submit_credit = st.form_submit_button("Take Credit", use_container_width=True)
            
            if submit_credit:
                # Create direct credit transaction
                transaction_data = {
                    'id': str(uuid.uuid4()),
                    'business_id': business_id,
                    'customer_id': customer_id,
                    'amount': credit_amount,
                    'transaction_type': 'credit',
                    'notes': credit_note,
                    'created_at': datetime.now().isoformat()
                }
                
                # Insert transaction - this will automatically update the balance in supabase_service.py
                transaction_response = data_service.query_table('transactions', query_type='insert', data=transaction_data)
                
                if transaction_response and transaction_response.data:
                    # Ensure the customer credit record exists with the updated balance
                    data_service.ensure_customer_credit_exists(business_id, customer_id)
                    st.success(f"Received ₹{credit_amount} credit")
                    st.rerun()
                else:
                    st.error("Failed to take credit. Please try again.")
    
    with tabs[1]:
        with st.form("make_payment_form"):
            st.markdown("<h4 style='margin-bottom: 1rem;'>Make Payment</h4>", unsafe_allow_html=True)
            
            # More elegant number input with clear layout
            payment_amount = st.number_input("Payment Amount (₹)", min_value=1, value=100, 
                                           step=10, help="Enter the amount to pay")
            
            payment_note = st.text_input("Note (optional)", key="payment_note_customer", 
                                       placeholder="Add details about this payment")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submit_payment = st.form_submit_button("Make Payment", use_container_width=True)
            
            if submit_payment:
                # Create payment transaction
                transaction_data = {
                    'id': str(uuid.uuid4()),
                    'business_id': business_id,
                    'customer_id': customer_id,
                    'amount': payment_amount,
                    'transaction_type': 'payment',
                    'notes': payment_note,
                    'created_at': datetime.now().isoformat()
                }
                
                # Insert transaction - this will automatically update the balance in supabase_service.py
                transaction_response = data_service.query_table('transactions', query_type='insert', data=transaction_data)
                
                if transaction_response and transaction_response.data:
                    st.success(f"Made ₹{payment_amount} payment")
                    st.rerun()
                else:
                    st.error("Failed to make payment. Please try again.")
    
    # Add a divider for clean separation
    st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # Transaction history with improved formatting
    st.markdown("<h3 style='text-align: center; margin-bottom: 1rem;'>Transaction History</h3>", unsafe_allow_html=True)
    
    if transactions:
        # Create a better-looking container for transaction history
        history_container = st.container()
        with history_container:
            for t in transactions:
                transaction_type = t.get('transaction_type', '')
                amount = float(t.get('amount', 0))
                date = data_service.format_datetime(t.get('created_at', ''))
                note = t.get('notes', '')
                
                # Create a card-like container for each transaction
                cols = st.columns([1, 3, 2])
                
                with cols[0]:
                    if transaction_type == 'credit':
                        st.markdown("<h3 style='color: #E57373; font-size: 1.8rem; text-align: center;'>🔴</h3>", unsafe_allow_html=True)
                    elif transaction_type == 'payment':
                        st.markdown("<h3 style='color: #81C784; font-size: 1.8rem; text-align: center;'>🟢</h3>", unsafe_allow_html=True)
                    else:
                        st.markdown("<h3 style='color: #9E9E9E; font-size: 1.8rem; text-align: center;'>⚪</h3>", unsafe_allow_html=True)
                
                with cols[1]:
                    if transaction_type == 'credit':
                        st.markdown(f"<div><strong style='color: #E57373;'>Credit</strong><br>₹{amount:.2f}</div>", unsafe_allow_html=True)
                    elif transaction_type == 'payment':
                        st.markdown(f"<div><strong style='color: #81C784;'>Payment</strong><br>₹{amount:.2f}</div>", unsafe_allow_html=True)
                    elif transaction_type == 'credit_request':
                        st.markdown(f"<div><strong style='color: #9E9E9E;'>Credit Request (Pending)</strong><br>₹{amount:.2f}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div><strong>{transaction_type.capitalize()}</strong><br>₹{amount:.2f}</div>", unsafe_allow_html=True)
                    
                    if note:
                        st.markdown(f"<div style='font-size: 0.9rem; opacity: 0.7;'>{note}</div>", unsafe_allow_html=True)
                
                with cols[2]:
                    st.markdown(f"<div style='text-align: right; font-size: 0.9rem;'>{date}</div>", unsafe_allow_html=True)
                
                # Add a subtle divider between transactions
                st.markdown("<hr style='margin: 0.5rem 0 1rem 0; opacity: 0.2;'>", unsafe_allow_html=True)
    else:
        st.info("No transactions yet")

def customer_profile():
    st.markdown("<h1 class='main-header'>My Profile</h1>", unsafe_allow_html=True)
    
    customer_id = st.session_state.customer_id
    
    # Get customer details
    customer_response = data_service.query_table('customers', filters=[('id', 'eq', customer_id)])
    customer = customer_response.data[0] if customer_response and customer_response.data else {}
    
    # Display customer details
    st.markdown(f"<h2 class='sub-header'>{customer.get('name', st.session_state.user_name)}</h2>", unsafe_allow_html=True)
    
    with st.form("update_customer_form"):
        customer_name = st.text_input("Name", value=customer.get('name', st.session_state.user_name))
        customer_phone = st.text_input("Phone Number", value=customer.get('phone_number', st.session_state.phone_number))
        
        submit_customer = st.form_submit_button("Update Profile")
        
        if submit_customer:
            # Update customer data
            customer_data = {
                'name': customer_name,
                'phone_number': customer_phone
            }
            
            # Update customer
            customer_response = data_service.query_table('customers', 
                                                      query_type='update', 
                                                      data=customer_data,
                                                      filters=[('id', 'eq', customer_id)])
            
            if customer_response and customer_response.data:
                st.session_state.user_name = customer_name
                st.session_state.phone_number = customer_phone
                st.success("Profile updated successfully")
            else:
                st.error("Failed to update profile. Please try again.")

# App router
def main():
    # Initialize mock data for auth service
    auth_service.init_mock_data()
    
    # On first run or after login, set default page based on user type
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        
        if auth_service.is_logged_in():
            if auth_service.is_business():
                st.session_state.page = "business_dashboard"
            elif auth_service.is_customer():
                st.session_state.page = "customer_dashboard"
        else:
            st.session_state.page = "login"
    
    # Initialize default page if not set
    if "page" not in st.session_state:
        st.session_state.page = "login" if not auth_service.is_logged_in() else (
            "business_dashboard" if auth_service.is_business() else "customer_dashboard"
        )
    
    # Router
    current_page = st.session_state.page
    
    if not auth_service.is_logged_in():
        login_page()
    else:
        # Only show navbar in specific pages
        if current_page not in ["customer_dashboard", "business_dashboard"]:
            show_navbar()
        
        # For business users
        if auth_service.is_business():
            # Create sidebar for business
            st.sidebar.title("Business Menu")
            
            # Highlight active button based on current page
            dashboard_button_class = "active-button" if st.session_state.page == "business_dashboard" else ""
            customers_button_class = "active-button" if st.session_state.page == "business_customers" else ""
            profile_button_class = "active-button" if st.session_state.page == "business_profile" else ""
            
            with st.sidebar.container():
                st.markdown(f"<div class='{dashboard_button_class}'>", unsafe_allow_html=True)
                if st.button("Dashboard", key="business_dashboard_btn"):
                    st.session_state.page = "business_dashboard"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown(f"<div class='{customers_button_class}'>", unsafe_allow_html=True)
                if st.button("Customers", key="business_customers_btn"):
                    st.session_state.page = "business_customers"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown(f"<div class='{profile_button_class}'>", unsafe_allow_html=True)
                if st.button("Profile", key="business_profile_btn"):
                    st.session_state.page = "business_profile"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
                
                if st.button("Logout", key="business_logout_btn"):
                    auth_service.logout()
                    st.rerun()
                
            # Render appropriate business page
            if current_page == "business_dashboard":
                business_dashboard()
            elif current_page == "business_customers":
                business_customers()
            elif current_page == "business_customer_detail":
                business_customer_detail()
            elif current_page == "business_profile":
                business_profile()
            # If a business user somehow gets to a customer page, redirect them
            elif current_page in ["customer_dashboard", "customer_business_detail", "customer_profile"]:
                st.session_state.page = "business_dashboard"
                st.rerun()
            else:
                # Fallback to dashboard
                business_dashboard()
        
        # For customer users
        elif auth_service.is_customer():
            # Create sidebar for customer - use st.sidebar instead of showing it in the customer_dashboard
            st.sidebar.title("Customer Menu")
            
            # Highlight active button based on current page
            dashboard_button_class = "active-button" if st.session_state.page == "customer_dashboard" else ""
            profile_button_class = "active-button" if st.session_state.page == "customer_profile" else ""
            
            with st.sidebar.container():
                st.markdown(f"<div class='{dashboard_button_class}'>", unsafe_allow_html=True)
                if st.button("Dashboard", key="customer_dashboard_btn"):
                    st.session_state.page = "customer_dashboard"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown(f"<div class='{profile_button_class}'>", unsafe_allow_html=True)
                if st.button("Profile", key="customer_profile_btn"):
                    st.session_state.page = "customer_profile"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
                
                if st.button("Logout", key="customer_logout_btn"):
                    auth_service.logout()
                    st.rerun()
            
            # Render appropriate customer page
            if current_page == "customer_dashboard":
                customer_dashboard()
            elif current_page == "customer_business_detail":
                customer_business_detail()
            elif current_page == "customer_profile":
                customer_profile()
            # If a customer user somehow gets to a business page, redirect them
            elif current_page in ["business_dashboard", "business_customers", "business_customer_detail", "business_profile"]:
                st.session_state.page = "customer_dashboard"
                st.rerun()
            else:
                # Fallback to dashboard
                customer_dashboard()

if __name__ == "__main__":
    main() 