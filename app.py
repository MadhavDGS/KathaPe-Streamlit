import streamlit as st
import os
import uuid
import qrcode
from io import BytesIO
import base64
from datetime import datetime
import auth_service
import data_service
import supabase_service

# App configuration
st.set_page_config(
    page_title="KathaPe - Digital Credit Book",
    page_icon="📒",
    layout="wide",
    initial_sidebar_state="collapsed"
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
        background-color: #ffffff;
        border-left: 4px solid #1E88E5;
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
        padding: 0.7rem !important;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        border: none !important;
        font-weight: 500 !important;
        font-size: 1.1rem !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
    }
    
    /* Primary action button */
    .primary-action button {
        background-color: #1E88E5 !important;
        color: white !important;
        font-weight: 600 !important;
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
        background-color: #ffffff;
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
        background-color: #f5f5f5;
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
        background-color: #ffffff;
        border-left: 3px solid #ddd;
    }
    
    .credit-transaction {
        border-left: 3px solid #4CAF50;
    }
    
    .payment-transaction {
        border-left: 3px solid #F44336;
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
        padding: 0.7rem 1rem !important;
        border: 1px solid rgba(150, 150, 150, 0.2) !important;
        font-size: 1.1rem !important;
    }
    
    .stNumberInput>div>div>input {
        border-radius: 0.5rem !important;
        padding: 0.7rem 1rem !important;
        border: 1px solid rgba(150, 150, 150, 0.2) !important;
        font-size: 1.1rem !important;
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
    
    /* Business theme elements */
    .business-card {
        background-color: #ffffff;
        border-radius: 0.8rem;
        box-shadow: 0 0.15rem 1.75rem rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-top: 4px solid #1E88E5;
    }
    
    .customer-row {
        display: flex;
        padding: 0.8rem;
        background-color: #ffffff;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        align-items: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }
    
    .customer-row:hover {
        transform: translateY(-2px);
        box-shadow: 0 3px 6px rgba(0,0,0,0.15);
    }
    
    .customer-name {
        font-weight: 600;
        font-size: 1.1rem;
        color: #333;
    }
    
    .customer-phone {
        color: #666;
        font-size: 0.9rem;
    }
    
    .customer-balance {
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .balance-positive {
        color: #4CAF50;
    }
    
    .balance-negative {
        color: #F44336;
    }
    
    .app-section {
        background-color: #f8f9fa;
        border-radius: 0.8rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1rem;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 0.5rem;
    }
    
    /* Login and Registration styling */
    .auth-container {
        max-width: 400px;
        margin: 0 auto;
        background-color: #ffffff;
        border-radius: 1rem;
        box-shadow: 0 0.5rem 2rem rgba(0, 0, 0, 0.1);
        padding: 2rem;
    }
    
    .auth-header {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .auth-link {
        text-align: center;
        margin-top: 1rem;
        font-size: 1rem;
    }
    
    .auth-link a {
        color: #1E88E5;
        text-decoration: none;
        font-weight: 500;
    }
    
    .auth-link a:hover {
        text-decoration: underline;
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .card {
            padding: 1rem;
        }
        
        .card h2 {
            font-size: 1.5rem;
        }
        
        .main-header {
            font-size: 1.8rem;
        }
        
        .sub-header {
            font-size: 1.3rem;
        }
        
        .stButton>button {
            padding: 0.8rem 0.5rem !important;
            font-size: 1rem !important;
        }
        
        .customer-row {
            flex-direction: column;
            align-items: flex-start;
        }
        
        .customer-name, .customer-phone, .customer-balance {
            width: 100%;
            margin-bottom: 0.3rem;
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
            height: 3rem !important;
        }
        
        /* Fix form layout with better spacing */
        .st-bq {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        
        /* Adjust widgets to be more touch-friendly */
        .stSlider, .stCheckbox {
            padding: 1rem 0 !important;
            margin-bottom: 1rem !important;
        }
        
        /* Better spacing for mobile */
        div.stButton > button {
            width: 100% !important;
            margin-top: 0.8rem !important;
            margin-bottom: 0.8rem !important;
            height: 3rem !important;
        }
        
        /* Improve column layout on mobile */
        .row-widget.stHorizontal {
            flex-wrap: wrap !important;
        }
        
        /* Improve form field appearance */
        .stForm label {
            font-size: 1rem !important;
            margin-bottom: 0.4rem !important;
            font-weight: 500 !important;
        }
        
        /* Better spacing in tables and containers */
        [data-testid="stVerticalBlock"] > div {
            padding-top: 0.5rem !important;
            padding-bottom: 0.5rem !important;
        }
        
        /* Fix button alignment in rows */
        [data-testid="stHorizontalBlock"] {
            gap: 0.5rem !important;
        }
        
        /* Fix expander appearance */
        .streamlit-expanderHeader {
            font-size: 1rem !important;
            padding: 0.8rem !important;
        }
        
        /* Better padding in columns */
        [data-testid="column"] {
            padding: 0.3rem !important;
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
    <div style="text-align: center; animation: fadeIn 1s ease-in-out; margin-bottom: 2rem;">
        <h1 class='main-header' style="margin-bottom: 0.5rem; font-size: 3rem;">KathaPe</h1>
        <h2 class='sub-header' style="margin-top: 0; margin-bottom: 0.5rem; font-size: 1.5rem;">Digital Credit Book</h2>
        <p style="color: #666; margin-top: 0; margin-bottom: 1.5rem;">Manage your business credits easily</p>
    </div>
    
    <style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # State to toggle between login and signup
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False
    
    # Create a container with the auth-container class
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    
    if not st.session_state.show_signup:
        # Login Form
        st.markdown('<div class="auth-header">', unsafe_allow_html=True)
        st.markdown('<h3 style="font-size: 1.8rem; margin-bottom: 0.5rem;">Welcome Back</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color: #666;">Log in to access your account</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            phone = st.text_input("Phone Number", placeholder="Enter your 10-digit phone number", 
                          help="Your registered phone number",
                          key="login_phone")
            
            password = st.text_input("Password", type="password", placeholder="Enter your password",
                            help="Your account password",
                            key="login_password")
            
            user_type = st.selectbox("Login As", ["business", "customer"], 
                             help="Select whether you're a business or a customer")
            
            # Primary action styling
            st.markdown('<div class="primary-action">', unsafe_allow_html=True)
            submit = st.form_submit_button("Login", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if submit:
                if not phone or not password:
                    st.error("Please enter both phone number and password")
                else:
                    success, user = auth_service.login(phone, password, user_type)
                    if success:
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("User not found or invalid credentials. Please check your details and try again.")
        
        # Sign up link - more obvious for older users
        st.markdown('<div class="auth-link" style="font-size: 1.1rem; margin-top: 1.5rem;">', unsafe_allow_html=True)
        st.markdown('Don\'t have an account? <a href="#" id="signup-link" style="color: #1E88E5; font-weight: bold;">Sign up here</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Sign up instead", key="signup_toggle", use_container_width=True):
            st.session_state.show_signup = True
            st.rerun()
    else:
        # Registration Form
        st.markdown('<div class="auth-header">', unsafe_allow_html=True)
        st.markdown('<h3 style="font-size: 1.8rem; margin-bottom: 0.5rem;">Create a New Account</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color: #666;">Join KathaPe to manage your credits</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.form("register_form"):
            r_name = st.text_input("Full Name", placeholder="Enter your full name", 
                          help="Your name as it will appear in the app",
                          key="reg_name")
            
            r_phone = st.text_input("Phone Number", placeholder="Enter a 10-digit phone number", 
                           help="This will be used for login",
                           key="reg_phone")
            
            r_password = st.text_input("Password", type="password", placeholder="Create a strong password", 
                             help="At least 6 characters long",
                             key="reg_password")
            
            r_user_type = st.selectbox("Register As", ["business", "customer"], 
                              help="Select whether you're registering as a business or a customer")
            
            # Primary action styling
            st.markdown('<div class="primary-action">', unsafe_allow_html=True)
            r_submit = st.form_submit_button("Create Account", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if r_submit:
                if not r_name or not r_phone or not r_password:
                    st.error("Please fill in all the fields")
                elif len(r_phone) != 10 or not r_phone.isdigit():
                    st.error("Please enter a valid 10-digit phone number")
                elif len(r_password) < 6:
                    st.error("Password should be at least 6 characters long")
                else:
                    success, message = auth_service.register(r_phone, r_password, r_name, r_user_type)
                    if success:
                        st.success(message)
                        st.session_state.show_signup = False
                        st.rerun()
                    else:
                        st.error(message)
        
        # Login link - more obvious for older users
        st.markdown('<div class="auth-link" style="font-size: 1.1rem; margin-top: 1.5rem;">', unsafe_allow_html=True)
        st.markdown('Already have an account? <a href="#" id="login-link" style="color: #1E88E5; font-weight: bold;">Log in here</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Log in instead", key="login_toggle", use_container_width=True):
            st.session_state.show_signup = False
            st.rerun()
    
    # Close auth-container div
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Demo credentials info in a more elegant expandable section
    with st.expander("Need help logging in?", expanded=False):
        st.markdown("""
        <div style="background-color: rgba(0,0,0,0.05); padding: 1rem; border-radius: 0.5rem; margin-top: 0.5rem; font-size: 1.1rem;">
            <p><strong>Try these demo accounts:</strong></p>
            <p>• <strong>Business:</strong> Phone: 9999999999, Password: password123</p>
            <p>• <strong>Customer:</strong> Use any 10-digit number and 'demo123' as password</p>
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
    st.markdown("<h1 class='main-header'>Customer Management</h1>", unsafe_allow_html=True)
    
    business_id = st.session_state.business_id
    
    # Get all customers for this business
    customers = data_service.get_business_customers(business_id)
    
    # Create two sections side by side
    col1, col2 = st.columns([2, 1])
    
    with col2:
        # Add new customer section
        st.markdown('<div class="business-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Add New Customer</div>', unsafe_allow_html=True)
        
        with st.form("add_customer_form"):
            customer_name = st.text_input("Customer Name", placeholder="Full name")
            customer_phone = st.text_input("Customer Phone", placeholder="10-digit number")
            
            st.markdown('<div class="primary-action">', unsafe_allow_html=True)
            submit_customer = st.form_submit_button("Add Customer")
            st.markdown('</div>', unsafe_allow_html=True)
            
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
                    success, message = auth_service.register(
                        customer_phone, 
                        "password123",  # Default password for simplicity
                        customer_name, 
                        "customer"
                    )
                    
                    if success:
                        # Find the newly created customer in Supabase
                        customer_response = supabase_service.query_table(
                            'customers', 
                            query_type='select', 
                            filters=[('phone_number', 'eq', customer_phone)]
                        )
                        
                        if customer_response.data:
                            customer_data = customer_response.data[0]
                            # Ensure this customer has a credit relationship with this business
                            data_service.ensure_customer_credit_exists(business_id, customer_data['id'])
                            st.success(f"Added customer {customer_name}")
                            st.rerun()
                    else:
                        st.error(message)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick stats
        if customers:
            st.markdown('<div class="business-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">Customer Stats</div>', unsafe_allow_html=True)
            
            # Total customers
            st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <p style="font-size: 0.9rem; color: #666; margin-bottom: 0.2rem;">Total Customers</p>
                <p style="font-size: 1.5rem; font-weight: 600; margin-top: 0;">{len(customers)}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Calculate total balance
            total_balance = sum(float(customer.get('current_balance', 0)) for customer in customers)
            
            # Total outstanding
            st.markdown(f"""
            <div>
                <p style="font-size: 0.9rem; color: #666; margin-bottom: 0.2rem;">Total Outstanding</p>
                <p style="font-size: 1.5rem; font-weight: 600; margin-top: 0; {'color: #4CAF50;' if total_balance > 0 else 'color: #F44336;'} ">₹{total_balance}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col1:
        # Display customers
        if customers:
            st.markdown('<div class="app-section">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">Your Customers</div>', unsafe_allow_html=True)
            
            # Search box for customers
            search = st.text_input("Search customers by name or phone", placeholder="Type to search...")
            
            # Filter customers based on search
            filtered_customers = customers
            if search:
                filtered_customers = [
                    c for c in customers 
                    if search.lower() in c.get('name', '').lower() or 
                       search in str(c.get('phone_number', ''))
                ]
            
            if not filtered_customers:
                st.info("No customers found matching your search.")
            
            # Display customers in an improved format
            for i, customer in enumerate(filtered_customers):
                customer_name = customer.get('name', 'Unknown')
                phone = customer.get('phone_number', 'N/A')
                balance = float(customer.get('current_balance', 0))
                
                # Create a card-like structure for each customer
                st.markdown(f"""
                <div class="customer-row">
                    <div style="display: flex; justify-content: space-between; width: 100%; align-items: center;">
                        <div style="flex: 3;">
                            <div class="customer-name">{customer_name}</div>
                            <div class="customer-phone">{phone}</div>
                        </div>
                        <div style="flex: 2; text-align: right;">
                            <div class="customer-balance {'balance-positive' if balance > 0 else 'balance-negative'}">
                                ₹{balance}
                            </div>
                        </div>
                        <div style="flex: 1; text-align: right;">
                            <button id="view-customer-{i}" style="background-color: #1E88E5; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer;">
                                View
                            </button>
                        </div>
                    </div>
                </div>
                <script>
                    document.getElementById("view-customer-{i}").addEventListener("click", function() {{
                        // This will be handled by Streamlit button
                    }});
                </script>
                """, unsafe_allow_html=True)
                
                # Hidden button that will be triggered by the HTML button (for Streamlit functionality)
                if st.button(f"View", key=f"business_view_customer_{i}", label_visibility="collapsed"):
                    st.session_state.selected_customer_id = customer.get('id')
                    st.session_state.page = "business_customer_detail"
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="app-section" style="text-align: center; padding: 3rem 1rem;">
                <img src="https://cdn-icons-png.flaticon.com/512/1170/1170577.png" width="100" style="opacity: 0.5; margin-bottom: 1rem;"/>
                <h3>No customers yet</h3>
                <p style="color: #666;">Add your first customer to get started with your credit book.</p>
            </div>
            """, unsafe_allow_html=True)

def business_customer_detail():
    # Hide the default Streamlit menu
    hide_streamlit_style = """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    # Back button in a cleaner layout
    col_back, col_title = st.columns([1, 3])
    with col_back:
        if st.button("← Back", key="back_to_dashboard", use_container_width=True):
            st.session_state.page = "business_customers"
            st.rerun()
    
    with col_title:
        st.markdown("<h1 class='main-header'>Customer Details</h1>", unsafe_allow_html=True)
    
    business_id = st.session_state.business_id
    customer_id = st.session_state.selected_customer_id
    
    # Get customer and transaction details
    business, customer, transactions, credit_total, payment_total, current_balance = \
        data_service.get_customer_business_view(business_id, customer_id)
    
    # Customer info section
    st.markdown('<div class="business-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2 style="margin-bottom: 0.2rem; font-size: 1.8rem;">{customer.get('name', 'Unknown')}</h2>
            <p style="color: #666; margin-top: 0;">Phone: {customer.get('phone_number', 'N/A')}</p>
        </div>
        <div>
            <p style="color: #666; margin-bottom: 0;">Current Balance</p>
            <p style="font-size: 1.5rem; font-weight: 600; margin-top: 0; text-align: right; {'color: #4CAF50;' if float(current_balance) > 0 else 'color: #F44336;'}">
                ₹{current_balance}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Layout for the rest of the page
    col1, col2 = st.columns([2, 1])
    
    with col2:
        # Summary cards in a single container
        st.markdown('<div class="business-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Transaction Summary</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="margin-bottom: 1rem;">
            <p style="font-size: 0.9rem; color: #666; margin-bottom: 0.2rem;">Total Credit Given</p>
            <p style="font-size: 1.5rem; font-weight: 600; margin-top: 0; color: #4CAF50;">₹{credit_total}</p>
        </div>
        
        <div>
            <p style="font-size: 0.9rem; color: #666; margin-bottom: 0.2rem;">Total Payments Received</p>
            <p style="font-size: 1.5rem; font-weight: 600; margin-top: 0; color: #F44336;">₹{payment_total}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add transaction forms
        st.markdown('<div class="business-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Add Transaction</div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Add Credit", "Add Payment"])
        
        with tab1:
            with st.form("add_credit_form"):
                credit_amount = st.number_input("Credit Amount", min_value=1, value=100)
                credit_note = st.text_input("Note (optional)", key="credit_note", placeholder="What is this credit for?")
                
                st.markdown('<div class="primary-action">', unsafe_allow_html=True)
                submit_credit = st.form_submit_button("Add Credit")
                st.markdown('</div>', unsafe_allow_html=True)
                
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
        
        with tab2:
            with st.form("add_payment_form"):
                payment_amount = st.number_input("Payment Amount", min_value=1, value=100)
                payment_note = st.text_input("Note (optional)", key="payment_note", placeholder="Payment received for?")
                
                st.markdown('<div class="primary-action">', unsafe_allow_html=True)
                submit_payment = st.form_submit_button("Add Payment")
                st.markdown('</div>', unsafe_allow_html=True)
                
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
                
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col1:
        # Transaction history
        st.markdown('<div class="app-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Transaction History</div>', unsafe_allow_html=True)
        
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
                    
                    st.markdown(f"""
                    <div class="transaction credit-transaction" style="border-left-color: #FF9800;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div class="transaction-type" style="color: #FF9800;">Credit Request</div>
                                <div class="transaction-amount">₹{amount}</div>
                                <div class="transaction-date">{date}</div>
                                {f'<div style="font-style: italic; margin-top: 0.25rem;">{note}</div>' if note else ''}
                            </div>
                            <div>
                                <button 
                                    id="approve-{request_id}" 
                                    style="background-color: #4CAF50; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; margin-right: 8px;">
                                    Approve
                                </button>
                                <button 
                                    id="reject-{request_id}" 
                                    style="background-color: #F44336; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer;">
                                    Reject
                                </button>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Approve", key=f"approve_{request_id}", label_visibility="collapsed"):
                            # First, update the existing request to be "approved"
                            update_response = data_service.query_table(
                                'transactions', 
                                query_type='update', 
                                data={'status': 'approved'},
                                filters=[('id', 'eq', request_id)]
                            )
                            
                            # Then create a new credit transaction
                            transaction_data = {
                                'id': str(uuid.uuid4()),
                                'business_id': business_id,
                                'customer_id': customer_id,
                                'amount': amount,
                                'transaction_type': 'credit',
                                'notes': f"Approved credit request: {note}",
                                'created_at': datetime.now().isoformat()
                            }
                            
                            transaction_response = data_service.query_table('transactions', query_type='insert', data=transaction_data)
                            
                            if transaction_response and transaction_response.data:
                                st.success(f"Approved credit request for ₹{amount}")
                                st.rerun()
                            else:
                                st.error("Failed to approve credit request. Please try again.")
                    
                    with col2:
                        if st.button(f"Reject", key=f"reject_{request_id}", label_visibility="collapsed"):
                            # Update the request to be "rejected"
                            update_response = data_service.query_table(
                                'transactions', 
                                query_type='update', 
                                data={'status': 'rejected'},
                                filters=[('id', 'eq', request_id)]
                            )
                            
                            if update_response:
                                st.success(f"Rejected credit request for ₹{amount}")
                                st.rerun()
                            else:
                                st.error("Failed to reject credit request. Please try again.")
            
            # Then, list regular transactions
            regular_transactions = [t for t in transactions if t.get('transaction_type') != 'credit_request']
            
            if not regular_transactions:
                st.info("No transactions yet with this customer.")
            
            for transaction in regular_transactions:
                transaction_type = transaction.get('transaction_type', '')
                amount = float(transaction.get('amount', 0))
                date = data_service.format_datetime(transaction.get('created_at', ''))
                note = transaction.get('notes', '')
                
                if transaction_type == 'credit':
                    icon = "📥"
                    class_name = "credit-transaction"
                    type_label = "Credit Given"
                elif transaction_type == 'payment':
                    icon = "📤"
                    class_name = "payment-transaction"
                    type_label = "Payment Received"
                else:
                    icon = "🔄"
                    class_name = ""
                    type_label = transaction_type.replace('_', ' ').title()
                
                st.markdown(f"""
                <div class="transaction {class_name}">
                    <div style="display: flex; align-items: center;">
                        <div style="font-size: 1.5rem; margin-right: 10px;">{icon}</div>
                        <div style="flex-grow: 1;">
                            <div class="transaction-type">{type_label}</div>
                            <div class="transaction-amount">₹{amount}</div>
                            <div class="transaction-date">{date}</div>
                            {f'<div style="font-style: italic; margin-top: 0.25rem;">{note}</div>' if note else ''}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No transaction history yet with this customer.")
        
        st.markdown('</div>', unsafe_allow_html=True)

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
    
    # Add customer styling that matches business theme
    st.markdown("""
    <style>
    .larger-text {
        font-size: 1.2rem !important;
    }
    .extra-large-text {
        font-size: 1.4rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Welcome message with user name
    customer_id = st.session_state.customer_id
    
    # Header with welcome and clear title
    st.markdown("<h1 class='main-header'>My Credit Book</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 1.3rem; margin-bottom: 1.5rem;'>Welcome, {st.session_state.user_name}</p>", unsafe_allow_html=True)
    
    # Get businesses where customer has credit
    businesses = data_service.get_customer_businesses(customer_id)
    
    # Create two sections side by side like in business view
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Display businesses
        if businesses:
            st.markdown('<div class="app-section">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">Your Credit Accounts</div>', unsafe_allow_html=True)
            
            for i, business in enumerate(businesses):
                # Match customer row styling from the business page
                business_name = business.get('name', 'Unknown Business')
                balance = float(business.get('current_balance', 0))
                
                # Create a card-like structure for each business
                st.markdown(f"""
                <div class="customer-row">
                    <div style="display: flex; justify-content: space-between; width: 100%; align-items: center;">
                        <div style="flex: 3;">
                            <div class="customer-name extra-large-text">{business_name}</div>
                        </div>
                        <div style="flex: 2; text-align: right;">
                            <div class="customer-balance {'balance-positive' if balance > 0 else 'balance-negative'} extra-large-text">
                                ₹{balance}
                            </div>
                        </div>
                        <div style="flex: 1; text-align: right;">
                            <button id="view-business-{i}" style="background-color: #1E88E5; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; font-size: 1.1rem;">
                                View
                            </button>
                        </div>
                    </div>
                </div>
                <script>
                    document.getElementById("view-business-{i}").addEventListener("click", function() {{
                        // This will be handled by Streamlit button
                    }});
                </script>
                """, unsafe_allow_html=True)
                
                # Hidden button that will be triggered by the HTML button (for Streamlit functionality)
                if st.button(f"View", key=f"customer_view_business_{i}", label_visibility="collapsed"):
                    st.session_state.selected_business_id = business.get('id')
                    st.session_state.page = "customer_business_detail"
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="app-section" style="text-align: center; padding: 3rem 1rem;">
                <img src="https://cdn-icons-png.flaticon.com/512/1170/1170577.png" width="100" style="opacity: 0.5; margin-bottom: 1rem;"/>
                <h3 style="font-size: 1.4rem;">No credit accounts yet</h3>
                <p style="color: #666; font-size: 1.2rem;">Connect to a business to get started with your credit book.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # QR code scanner section
        st.markdown('<div class="business-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Connect to Business</div>', unsafe_allow_html=True)
        
        with st.form("connect_business_form"):
            business_code = st.text_input("Business ID", placeholder="Enter the business ID", 
                                help="Ask the business owner for their ID")
            
            business_pin = st.text_input("Access PIN (4-digit)", max_chars=4, placeholder="Enter the 4-digit PIN",
                               help="Ask the business owner for their 4-digit PIN")
            
            st.markdown('<div class="primary-action">', unsafe_allow_html=True)
            connect_button = st.form_submit_button("Connect to Business", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
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
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick stats if the user has businesses
        if businesses:
            st.markdown('<div class="business-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">Your Stats</div>', unsafe_allow_html=True)
            
            # Total businesses
            st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <p style="font-size: 1rem; color: #666; margin-bottom: 0.2rem;">Total Businesses</p>
                <p style="font-size: 1.5rem; font-weight: 600; margin-top: 0;">{len(businesses)}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Calculate total balance
            total_balance = sum(float(business.get('current_balance', 0)) for business in businesses)
            
            # Total outstanding
            st.markdown(f"""
            <div>
                <p style="font-size: 1rem; color: #666; margin-bottom: 0.2rem;">Total Outstanding</p>
                <p style="font-size: 1.5rem; font-weight: 600; margin-top: 0; {'color: #4CAF50;' if total_balance > 0 else 'color: #F44336;'} ">₹{total_balance}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Camera option below in its own section
    st.markdown('<div class="app-section" style="margin-top: 1.5rem;">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Or Scan QR Code</div>', unsafe_allow_html=True)
    
    # Center the camera input
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_qr = st.camera_input("Take a picture of QR code", key="qr_camera")
        
        if uploaded_qr is not None:
            # In a real app, we would process the QR code image here
            st.info("QR code processing would happen here. For now, please use the manual entry option above.")
    
    st.markdown('</div>', unsafe_allow_html=True)

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
    col_back, col_title = st.columns([1, 3])
    with col_back:
        if st.button("← Back", key="back_to_dashboard", use_container_width=True):
            st.session_state.page = "customer_dashboard"
            st.rerun()
    
    with col_title:
        st.markdown("<h1 class='main-header'>Business Details</h1>", unsafe_allow_html=True)
    
    business_id = st.session_state.selected_business_id
    customer_id = st.session_state.customer_id
    
    # Get business and transaction details
    business, customer, transactions, credit_total, payment_total, current_balance = \
        data_service.get_customer_business_view(business_id, customer_id)
    
    # Business info section
    st.markdown('<div class="business-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2 style="margin-bottom: 0.2rem; font-size: 1.8rem;">{business.get('name', 'Unknown Business')}</h2>
        </div>
        <div>
            <p style="color: #666; margin-bottom: 0;">Current Balance</p>
            <p style="font-size: 1.5rem; font-weight: 600; margin-top: 0; text-align: right; {'color: #4CAF50;' if float(current_balance) > 0 else 'color: #F44336;'}">
                ₹{current_balance}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Layout for the rest of the page
    col1, col2 = st.columns([2, 1])
    
    with col2:
        # Summary cards in a single container
        st.markdown('<div class="business-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Transaction Summary</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="margin-bottom: 1rem;">
            <p style="font-size: 0.9rem; color: #666; margin-bottom: 0.2rem;">Total Credit Taken</p>
            <p style="font-size: 1.5rem; font-weight: 600; margin-top: 0; color: #4CAF50;">₹{credit_total}</p>
        </div>
        
        <div>
            <p style="font-size: 0.9rem; color: #666; margin-bottom: 0.2rem;">Total Payments Made</p>
            <p style="font-size: 1.5rem; font-weight: 600; margin-top: 0; color: #F44336;">₹{payment_total}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add transaction forms
        st.markdown('<div class="business-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Add Transaction</div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Take Credit", "Make Payment"])
        
        with tab1:
            with st.form("take_credit_form"):
                credit_amount = st.number_input("Credit Amount", min_value=1, value=100, 
                                       step=10, help="Enter the amount of credit to take")
                
                credit_note = st.text_input("Note (optional)", key="credit_note_customer", 
                                  placeholder="What is this credit for?")
                
                st.markdown('<div class="primary-action">', unsafe_allow_html=True)
                submit_credit = st.form_submit_button("Take Credit")
                st.markdown('</div>', unsafe_allow_html=True)
                
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
                    
                    success, _ = data_service.create_transaction(transaction_data)
                    if success:
                        st.success(f"Successfully recorded ₹{credit_amount} credit")
                        st.rerun()
                    else:
                        st.error("Failed to record credit transaction")
        
        with tab2:
            with st.form("make_payment_form"):
                payment_amount = st.number_input("Payment Amount", min_value=1, value=100, 
                                        step=10, help="Enter the amount you paid to the business")
                
                payment_note = st.text_input("Note (optional)", key="payment_note_customer", 
                                   placeholder="Any details about this payment?")
                
                st.markdown('<div class="primary-action">', unsafe_allow_html=True)
                submit_payment = st.form_submit_button("Make Payment")
                st.markdown('</div>', unsafe_allow_html=True)
                
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
                    
                    success, _ = data_service.create_transaction(transaction_data)
                    if success:
                        st.success(f"Successfully recorded ₹{payment_amount} payment")
                        st.rerun()
                    else:
                        st.error("Failed to record payment transaction")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col1:
        # Transaction history
        st.markdown('<div class="app-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Transaction History</div>', unsafe_allow_html=True)
        
        if transactions:
            for transaction in transactions:
                transaction_type = transaction.get('transaction_type', '')
                amount = float(transaction.get('amount', 0))
                date = data_service.format_datetime(transaction.get('created_at', ''))
                note = transaction.get('notes', '')
                
                if transaction_type == 'credit':
                    icon = "📥"
                    class_name = "credit-transaction"
                    type_label = "Credit Taken"
                elif transaction_type == 'payment':
                    icon = "📤"
                    class_name = "payment-transaction"
                    type_label = "Payment Made"
                else:
                    icon = "🔄"
                    class_name = ""
                    type_label = transaction_type.replace('_', ' ').title()
                
                st.markdown(f"""
                <div class="transaction {class_name}">
                    <div style="display: flex; align-items: center;">
                        <div style="font-size: 1.5rem; margin-right: 10px;">{icon}</div>
                        <div style="flex-grow: 1;">
                            <div class="transaction-type">{type_label}</div>
                            <div class="transaction-amount">₹{amount}</div>
                            <div class="transaction-date">{date}</div>
                            {f'<div style="font-style: italic; margin-top: 0.25rem;">{note}</div>' if note else ''}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No transaction history yet with this business.")
        
        st.markdown('</div>', unsafe_allow_html=True)

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
                
                st.markdown(f"<div class='{customers_button_class}'>", unsafe_allow_html=True)
                if st.button("Customers", key="business_customers_btn"):
                    st.session_state.page = "business_customers"
                    st.rerun()
                
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