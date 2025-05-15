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
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.1rem;
            margin-bottom: 1rem;
        }
        .card {
            padding: 0.8rem;
            margin-bottom: 0.8rem;
            border-radius: 0.6rem;
        }
        .card h2 {
            font-size: 1.5rem;
        }
        .card h3 {
            font-size: 0.9rem;
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
        /* Larger buttons for touch interaction on mobile */
        .stButton>button {
            padding: 0.7rem !important;
            font-size: 1rem !important;
            height: auto !important;
            min-height: 3rem !important;
            margin-bottom: 0.8rem !important;
            border-radius: 0.6rem !important;
        }
        /* Adjust card padding */
        .card {
            padding: 1rem;
            margin-bottom: 1rem;
        }
        /* Smaller headings */
        h1 {
            font-size: 1.8rem !important;
            margin-bottom: 1rem !important;
        }
        h2 {
            font-size: 1.5rem !important;
            margin-bottom: 0.8rem !important;
        }
        h3 {
            font-size: 1.2rem !important;
            margin-bottom: 0.6rem !important;
        }
        /* Reduce transaction padding */
        .transaction {
            padding: 0.8rem;
            margin-bottom: 0.8rem;
            border-radius: 0.6rem;
        }
        /* Make forms more touch-friendly */
        .stTextInput>div>div>input, 
        .stNumberInput>div>div>input, 
        .stSelectbox>div>div>div {
            font-size: 16px !important; /* Prevents iOS zoom on focus */
            height: 3rem !important;
            padding: 0.5rem 1rem !important;
            border-radius: 0.6rem !important;
            margin-bottom: 0.8rem !important;
        }
        /* Improve tab interface for touch */
        .stTabs [data-baseweb="tab"] {
            padding: 0.8rem 1rem !important;
            font-size: 1rem !important;
            height: auto !important;
            min-height: 3rem !important;
        }
        /* Create more space between form items */
        .stForm > div {
            margin-bottom: 1rem !important;
        }
        /* Improve QR code display */
        .qr-container {
            padding: 1rem;
            margin: 0.5rem auto 1.5rem auto;
            max-width: 90%;
        }
        .qr-code-image {
            max-width: 180px;
            margin: 0 auto;
            display: block;
        }
        /* Better spacing for mobile */
        .row-widget {
            padding: 0.5rem 0 !important;
        }
        /* Make alerts more readable on mobile */
        .stAlert {
            padding: 0.8rem !important;
            border-radius: 0.6rem !important;
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
    <div style="text-align: center; animation: fadeIn 1s ease-in-out;">
        <h1 class='main-header' style="margin-bottom: 0.5rem; font-size: 3rem;">KathaPe</h1>
        <h2 class='sub-header' style="margin-top: 0; margin-bottom: 1rem; font-size: 1.5rem;">Manage your business credits easily</h2>
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
    
    if not st.session_state.show_signup:
        # Login Form
        with st.container():
            st.markdown("<h3 style='text-align: center; margin-bottom: 1rem; font-size: 1.6rem;'>Welcome Back</h3>", unsafe_allow_html=True)
            
        with st.form("login_form"):
                # Larger, clearer inputs
                st.markdown("""
                <style>
                .large-input div[data-testid="stFormSubmitButton"] > button {
                    height: 3.5rem;
                    font-size: 1.2rem;
                    font-weight: bold;
                }
                div[data-testid="stTextInput"] label {
                    font-size: 1.1rem;
                    font-weight: 500;
                }
                div[data-testid="stTextInput"] input {
                    font-size: 1.1rem;
                    padding: 0.8rem !important;
                }
                div[data-testid="stSelectbox"] label {
                    font-size: 1.1rem;
                    font-weight: 500;
                }
                div[data-testid="stSelectbox"] div[data-baseweb="select"] {
                    font-size: 1.1rem;
                }
                </style>
                """, unsafe_allow_html=True)
            
                phone = st.text_input("Phone Number", placeholder="Enter your 10-digit phone number", 
                              help="Your registered phone number",
                              key="login_phone")
                
                password = st.text_input("Password", type="password", placeholder="Enter your password",
                                help="Your account password",
                                key="login_password")
                
                user_type = st.selectbox("Login As", ["business", "customer"], 
                                 help="Select whether you're a business or a customer")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submit = st.form_submit_button("Login", use_container_width=True)
            
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
    
            # Sign up link
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("""
                <div style="text-align: center; margin-top: 1rem;">
                    <p style="font-size: 1.1rem;">Don't have an account? <a href="#" id="signup-link" style="font-weight: bold;">Sign up</a></p>
                </div>
                <script>
                    document.querySelector("#signup-link").addEventListener("click", function(e) {
                        e.preventDefault();
                        window.parent.postMessage({type: "streamlit:setComponentValue", value: true}, "*");
                    });
                </script>
                """, unsafe_allow_html=True)
                
                if st.button("Sign up instead", key="signup_toggle", use_container_width=True):
                    st.session_state.show_signup = True
                    st.rerun()
    else:
        # Registration Form
        with st.container():
            st.markdown("<h3 style='text-align: center; margin-bottom: 1rem; font-size: 1.6rem;'>Create a New Account</h3>", unsafe_allow_html=True)
            
        with st.form("register_form"):
                # Larger, clearer inputs
                st.markdown("""
                <style>
                .large-input div[data-testid="stFormSubmitButton"] > button {
                    height: 3.5rem;
                    font-size: 1.2rem;
                    font-weight: bold;
                }
                div[data-testid="stTextInput"] label {
                    font-size: 1.1rem;
                    font-weight: 500;
                }
                div[data-testid="stTextInput"] input {
                    font-size: 1.1rem;
                    padding: 0.8rem !important;
                }
                div[data-testid="stSelectbox"] label {
                    font-size: 1.1rem;
                    font-weight: 500;
                }
                div[data-testid="stSelectbox"] div[data-baseweb="select"] {
                    font-size: 1.1rem;
                }
                </style>
                """, unsafe_allow_html=True)
            
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
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                    r_submit = st.form_submit_button("Create Account", use_container_width=True)
            
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
            
            # Login link
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("""
                <div style="text-align: center; margin-top: 1rem;">
                    <p style="font-size: 1.1rem;">Already have an account? <a href="#" id="login-link" style="font-weight: bold;">Log in</a></p>
                </div>
                <script>
                    document.querySelector("#login-link").addEventListener("click", function(e) {
                        e.preventDefault();
                        window.parent.postMessage({type: "streamlit:setComponentValue", value: false}, "*");
                    });
                </script>
                """, unsafe_allow_html=True)
                
                if st.button("Log in instead", key="login_toggle", use_container_width=True):
                    st.session_state.show_signup = False
                    st.rerun()
    
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
    # Hide the default Streamlit menu
    hide_streamlit_style = """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    # Add larger font and easier to read styles
    st.markdown("""
    <style>
    /* Larger text for better readability */
    .streamlit-container {
        font-size: 18px !important;
    }
    /* Bigger touch targets */
    button, select, input {
        min-height: 48px !important;
        font-size: 16px !important;
    }
    /* Improved spacing */
    .larger-header {
        font-size: 2.2rem !important;
        margin-bottom: 1.5rem !important;
        text-align: center;
    }
    .summary-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 20px;
        border: 1px solid #ddd;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.3s ease;
    }
    .summary-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    .card-title {
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
        color: #555;
    }
    .card-value {
        font-size: 1.8rem;
        font-weight: bold;
    }
    .transaction-item {
        padding: 15px;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 15px;
        border: 1px solid #ddd;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with user name for personalization
    st.markdown(f"<h2 style='text-align: center; margin-bottom: 0.5rem;'>Welcome, {st.session_state.user_name}</h2>", unsafe_allow_html=True)
    st.markdown("<h1 class='larger-header'>Business Dashboard</h1>", unsafe_allow_html=True)
    
    business_id = st.session_state.business_id
    
    # Get business summary data
    summary, transactions, customers = data_service.get_business_summary(business_id)
    
    # Add a divider for clean separation
    st.markdown("<hr style='margin: 1rem 0 1.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # Display summary cards in a clearer, more accessible format
    st.markdown("<h3 style='text-align: center; margin-bottom: 1.5rem; font-size: 1.8rem;'>Business Summary</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class='summary-card'>
            <div class='card-title'>Total Customers</div>
            <div class='card-value'>{summary['total_customers']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='summary-card'>
            <div class='card-title'>Total Credit Given</div>
            <div class='card-value' style='color: #4CAF50;'>₹{summary['total_credit']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='summary-card'>
            <div class='card-title'>Total Payments Received</div>
            <div class='card-value' style='color: #F44336;'>₹{summary['total_payments']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add a divider for clean separation
    st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # Quick actions for common tasks
    st.markdown("<h3 style='text-align: center; margin-bottom: 1rem; font-size: 1.8rem;'>Quick Actions</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("View All Customers", use_container_width=True):
            st.session_state.page = "business_customers"
            st.rerun()
    
    with col2:
        if st.button("Share Business ID", use_container_width=True):
            st.session_state.page = "business_profile"
            st.rerun()
    
    # Add a divider for clean separation
    st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # Recent transactions with clearer formatting
    st.markdown("<h3 style='text-align: center; margin-bottom: 1rem; font-size: 1.8rem;'>Recent Transactions</h3>", unsafe_allow_html=True)
    
    if transactions:
        for transaction in transactions[:5]:  # Show only most recent 5
            transaction_type = transaction.get('transaction_type', '')
            amount = float(transaction.get('amount', 0))
            customer_name = transaction.get('customer_name', 'Unknown Customer')
            date = data_service.format_datetime(transaction.get('created_at', ''))
            
            # Style based on transaction type
            if transaction_type == 'credit':
                type_display = "Credit Given"
                color = "#4CAF50"  # Green
            elif transaction_type == 'payment':
                type_display = "Payment Received"
                color = "#F44336"  # Red
            else:
                type_display = transaction_type.replace('_', ' ').title()
                color = "#9E9E9E"  # Grey
            
            st.markdown(f"""
            <div class='transaction-item'>
                <div style='display: flex; justify-content: space-between;'>
                    <div>
                        <div style='font-size: 1.2rem; font-weight: bold;'>{customer_name}</div>
                        <div style='color: {color}; font-size: 1.1rem;'>{type_display}</div>
                    </div>
                    <div>
                        <div style='font-size: 1.4rem; font-weight: bold; color: {color};'>₹{amount}</div>
                        <div style='font-size: 0.9rem; color: #666;'>{date}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No transactions yet. Add your first customer and start recording transactions.")

def business_customers():
    # Hide the default Streamlit menu
    hide_streamlit_style = """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    # Add larger font and easier to read styles
    st.markdown("""
    <style>
    /* Larger text for better readability */
    .streamlit-container {
        font-size: 18px !important;
    }
    /* Bigger touch targets */
    button, select, input {
        min-height: 48px !important;
        font-size: 16px !important;
    }
    /* Improved spacing */
    .larger-header {
        font-size: 2.2rem !important;
        margin-bottom: 1.5rem !important;
        text-align: center;
    }
    .customer-card {
        padding: 15px;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 15px;
        border: 1px solid #ddd;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: transform 0.2s ease;
    }
    .customer-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .customer-name {
        font-size: 1.3rem;
        font-weight: bold;
    }
    .customer-phone {
        font-size: 1.1rem;
        color: #555;
        margin-top: 5px;
    }
    .customer-balance {
        font-size: 1.2rem;
        font-weight: 500;
        margin-top: 5px;
    }
    /* Add customer form styles */
    .add-form {
        background-color: #f0f4f8;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .form-title {
        font-size: 1.4rem;
        margin-bottom: 15px;
        font-weight: bold;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with better styling
    st.markdown("<h1 class='larger-header'>My Customers</h1>", unsafe_allow_html=True)
    
    # Back button for easier navigation
    if st.button("← Back to Dashboard", use_container_width=True):
        st.session_state.page = "business_dashboard"
        st.rerun()
        
    # Add a divider for clean separation
    st.markdown("<hr style='margin: 1rem 0 1.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    business_id = st.session_state.business_id
    
    # Get all customers for this business
    customers = data_service.get_business_customers(business_id)
    
    # Add new customer section with improved UI
    st.markdown("<div class='form-title'>Add New Customer</div>", unsafe_allow_html=True)
    
    with st.form("add_customer_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("Customer Name", placeholder="Enter full name")
        with col2:
            customer_phone = st.text_input("Customer Phone", placeholder="10-digit number", max_chars=10)
        
        submit_customer = st.form_submit_button("Add Customer", use_container_width=True)
        
        if submit_customer:
            if not customer_name or not customer_phone:
                st.error("Please enter both name and phone number")
            elif len(customer_phone) != 10 or not customer_phone.isdigit():
                st.error("Please enter a valid 10-digit phone number")
            else:
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
    
    # Add a divider for clean separation
    st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # Display customers with improved UI
    if customers:
        st.markdown("<h2 style='text-align: center; margin-bottom: 1.5rem; font-size: 1.8rem;'>Your Customers</h2>", unsafe_allow_html=True)
        
        # Use st.text_input to create a search box
        search_term = st.text_input("Search customers by name or phone", placeholder="Type to search...", key="customer_search")
        
        # Filter customers based on search
        if search_term:
            filtered_customers = [
                c for c in customers 
                if search_term.lower() in c.get('name', '').lower() or 
                search_term in c.get('phone_number', '')
            ]
        else:
            filtered_customers = customers
            
        if not filtered_customers:
            st.info("No customers match your search.")
        
        # Display customers in a more accessible format
        for i, customer in enumerate(filtered_customers):
            name = customer.get('name', 'Unknown')
            phone = customer.get('phone_number', 'N/A')
            balance = customer.get('current_balance', 0)
            
            # Determine balance color
            balance_color = "#4CAF50" if float(balance) > 0 else "#9E9E9E"
            
            st.markdown(f"""
            <div class='customer-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <div class='customer-name'>{name}</div>
                        <div class='customer-phone'>📱 {phone}</div>
                        <div class='customer-balance' style='color: {balance_color};'>Balance: ₹{balance}</div>
                    </div>
                    <div>
                        <button class="view-customer-btn-{i}" style="
                            background-color: #1E88E5;
                            color: white;
                            border: none;
                            padding: 10px 20px;
                            border-radius: 5px;
                            font-size: 1.1rem;
                            cursor: pointer;
                            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                        ">View Details</button>
                    </div>
                </div>
            </div>
            
            <script>
                document.querySelector('.view-customer-btn-{i}').addEventListener('click', function() {{
                    // This is just for the HTML representation, the actual button is below
                }});
            </script>
            """, unsafe_allow_html=True)
            
            # Hidden button that actually works with Streamlit
            col1, col2, col3 = st.columns([4, 1, 1])
            with col3:
                if st.button(f"View", key=f"business_view_customer_{i}", use_container_width=True):
                    st.session_state.selected_customer_id = customer.get('id')
                    st.session_state.page = "business_customer_detail"
                    st.rerun()
    else:
        st.info("No customers yet. Add your first customer using the form above!")

def business_customer_detail():
    # Hide the default Streamlit menu
    hide_streamlit_style = """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    # Add larger font and easier to read styles
    st.markdown("""
    <style>
    /* Larger text for better readability */
    .streamlit-container {
        font-size: 18px !important;
    }
    /* Bigger touch targets */
    button, select, input {
        min-height: 48px !important;
        font-size: 16px !important;
    }
    /* Improved spacing */
    .larger-header {
        font-size: 2.2rem !important;
        margin-bottom: 1.5rem !important;
        text-align: center;
    }
    /* Summary card styling */
    .summary-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 20px;
        border: 1px solid #ddd;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .card-title {
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
        color: #555;
    }
    .card-value {
        font-size: 1.8rem;
        font-weight: bold;
    }
    /* Transaction styles */
    .transaction-item {
        padding: 15px;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 15px;
        border: 1px solid #ddd;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    /* Transaction form styles */
    .form-section {
        background-color: #f0f4f8;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .form-title {
        font-size: 1.4rem;
        margin-bottom: 15px;
        font-weight: bold;
        text-align: center;
    }
    /* Button styling */
    .big-button {
        padding: 12px !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Use a cleaner header layout
    st.markdown("<h1 class='larger-header'>Customer Details</h1>", unsafe_allow_html=True)
    
    # Large back button at the top
    if st.button("← Back to Customers", key="back_to_customers", use_container_width=True):
        st.session_state.page = "business_customers"
        st.rerun()
    
    # Add a divider for clean separation
    st.markdown("<hr style='margin: 1rem 0 1.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    business_id = st.session_state.business_id
    customer_id = st.session_state.selected_customer_id
    
    # Get customer and transaction details
    business, customer, transactions, credit_total, payment_total, current_balance = \
        data_service.get_customer_business_view(business_id, customer_id)
    
    # Customer name and details in a clear format
    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 1.5rem;'>
        <h2 style='font-size: 2rem; margin-bottom: 0.5rem;'>{customer.get('name', 'Unknown')}</h2>
        <div style='font-size: 1.2rem;'>📱 {customer.get('phone_number', 'N/A')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Summary cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class='summary-card'>
            <div class='card-title'>Total Credit</div>
            <div class='card-value' style='color: #4CAF50;'>₹{credit_total}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='summary-card'>
            <div class='card-title'>Total Payments</div>
            <div class='card-value' style='color: #F44336;'>₹{payment_total}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='summary-card'>
            <div class='card-title'>Current Balance</div>
            <div class='card-value'>₹{current_balance}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add a divider for clean separation
    st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # Add transaction forms with improved UI
    st.markdown("<div class='form-title'>Add New Transaction</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        with st.form("add_credit_form", clear_on_submit=True):
            st.markdown("<h3 style='text-align: center; color: #4CAF50; font-size: 1.3rem;'>Add Credit</h3>", unsafe_allow_html=True)
            credit_amount = st.number_input("Credit Amount (₹)", min_value=1, value=100, step=10)
            credit_note = st.text_input("Note (optional)", key="credit_note", placeholder="What is this credit for?")
            submit_credit = st.form_submit_button("Add Credit Entry", use_container_width=True)
            
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
        with st.form("add_payment_form", clear_on_submit=True):
            st.markdown("<h3 style='text-align: center; color: #F44336; font-size: 1.3rem;'>Record Payment</h3>", unsafe_allow_html=True)
            payment_amount = st.number_input("Payment Amount (₹)", min_value=1, value=100, step=10)
            payment_note = st.text_input("Note (optional)", key="payment_note", placeholder="Payment details")
            submit_payment = st.form_submit_button("Record Payment", use_container_width=True)
            
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
    
    # Add a divider for clean separation
    st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # Transaction history with improved readability
    st.markdown("<h2 style='text-align: center; margin-bottom: 1.5rem; font-size: 1.8rem;'>Transaction History</h2>", unsafe_allow_html=True)
    
    if transactions:
        # First, display pending credit requests at the top with approve buttons
        pending_requests = [t for t in transactions if t.get('transaction_type') == 'credit_request']
        if pending_requests:
            st.markdown("<h3 style='text-align: center; color: #FF9800; margin-bottom: 1rem; font-size: 1.5rem;'>Pending Credit Requests</h3>", unsafe_allow_html=True)
            for request in pending_requests:
                amount = float(request.get('amount', 0))
                date = data_service.format_datetime(request.get('created_at', ''))
                note = request.get('notes', '')
                request_id = request.get('id', '')
                
                st.markdown(f"""
                <div class='transaction-item' style='border-left: 4px solid #FF9800;'>
                    <div style='display: flex; justify-content: space-between;'>
                        <div>
                            <div style='font-size: 1.3rem; font-weight: bold; color: #FF9800;'>Credit Request: ₹{amount}</div>
                            <div style='font-size: 1rem; margin-top: 5px;'>{note if note else 'No note provided'}</div>
                            <div style='font-size: 0.9rem; color: #666; margin-top: 5px;'>{date}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Approve", key=f"approve_{request_id}", use_container_width=True):
                        # Create approved credit transaction
                        transaction_data = {
                            'id': str(uuid.uuid4()),
                            'business_id': business_id,
                            'customer_id': customer_id,
                            'amount': amount,
                            'transaction_type': 'credit',
                            'notes': f"Approved request: {note}",
                            'created_at': datetime.now().isoformat()
                        }
                        
                        # Insert approved transaction
                        transaction_response = data_service.query_table('transactions', query_type='insert', data=transaction_data)
                        
                        # Delete the request
                        delete_response = data_service.query_table('transactions', query_type='delete', filters=[('id', 'eq', request_id)])
                        
                        if transaction_response and transaction_response.data:
                            st.success(f"Approved ₹{amount} credit request")
                            st.rerun()
                        else:
                            st.error("Failed to approve. Please try again.")
                
                with col2:
                    if st.button(f"Reject", key=f"reject_{request_id}", use_container_width=True):
                        # Delete the request
                        delete_response = data_service.query_table('transactions', query_type='delete', filters=[('id', 'eq', request_id)])
                        
                        if delete_response:
                            st.success("Request rejected")
                            st.rerun()
                        else:
                            st.error("Failed to reject. Please try again.")
        
        # Show regular transactions
        regular_transactions = [t for t in transactions if t.get('transaction_type') != 'credit_request']
        for transaction in regular_transactions:
            transaction_type = transaction.get('transaction_type', '')
            amount = float(transaction.get('amount', 0))
            date = data_service.format_datetime(transaction.get('created_at', ''))
            note = transaction.get('notes', '')
            
            if transaction_type == 'credit':
                border_color = "#4CAF50"
                type_display = "Credit Given"
                amount_color = "#4CAF50"
            elif transaction_type == 'payment':
                border_color = "#F44336"
                type_display = "Payment Received"
                amount_color = "#F44336"
            else:
                border_color = "#9E9E9E"
                type_display = transaction_type.replace('_', ' ').title()
                amount_color = "#9E9E9E"
            
            st.markdown(f"""
            <div class='transaction-item' style='border-left: 4px solid {border_color};'>
                <div style='display: flex; justify-content: space-between;'>
                    <div>
                        <div style='font-size: 1.3rem; font-weight: bold; color: {amount_color};'>{type_display}: ₹{amount}</div>
                        <div style='font-size: 1rem; margin-top: 5px;'>{note if note else 'No note provided'}</div>
                        <div style='font-size: 0.9rem; color: #666; margin-top: 5px;'>{date}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No transactions yet. Add your first transaction using the forms above.")

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
    
    # Add larger font and easier to read styles
    st.markdown("""
    <style>
    /* Larger text for better readability */
    .streamlit-container {
        font-size: 18px !important;
    }
    /* Bigger touch targets */
    button, select, input {
        min-height: 48px !important;
        font-size: 16px !important;
    }
    /* Improved spacing */
    .larger-header {
        font-size: 2.2rem !important;
        margin-bottom: 1.5rem !important;
        text-align: center;
    }
    .business-card {
        padding: 15px;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 15px;
        border: 1px solid #ddd;
    }
    .business-name {
        font-size: 1.4rem;
        font-weight: bold;
    }
    .business-balance {
        font-size: 1.2rem;
        font-weight: 500;
    }
    .action-button {
        font-size: 1.1rem !important;
        padding: 10px 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Welcome message with user name
    customer_id = st.session_state.customer_id
    
    # Header with welcome and clear title
    st.markdown(f"<h2 style='text-align: center; margin-bottom: 0.5rem;'>Welcome, {st.session_state.user_name}</h2>", unsafe_allow_html=True)
    st.markdown("<h1 class='larger-header'>My Credit Book</h1>", unsafe_allow_html=True)
    
    # Get businesses where customer has credit
    businesses = data_service.get_customer_businesses(customer_id)
    
    # Add a divider for clean separation
    st.markdown("<hr style='margin: 1rem 0 1.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # Display businesses
    if businesses:
        st.markdown("<h3 style='text-align: center; margin-bottom: 1.5rem; font-size: 1.8rem;'>Your Credit Accounts</h3>", unsafe_allow_html=True)
        
        # Create a cleaner, more accessible list of businesses
        for i, business in enumerate(businesses):
            # Use a card-like design for each business
            st.markdown(f"""
            <div class='business-card'>
                <div class='business-name'>{business.get('name', 'Unknown Business')}</div>
                <div class='business-balance' style='color: {"#E57373" if float(business.get("current_balance", 0)) > 0 else "#81C784"}'>
                    Balance: ₹{business.get('current_balance', 0)}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"View Details", key=f"customer_view_business_{i}", use_container_width=True):
                st.session_state.selected_business_id = business.get('id')
                st.session_state.page = "customer_business_detail"
                st.rerun()
    else:
        st.info("No credit accounts yet. Connect to a business to get started.")
    
    # Add a divider for clean separation
    st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # QR code scanner with improved layout
    st.markdown("<h3 style='text-align: center; margin-bottom: 1rem; font-size: 1.8rem;'>Connect to Business</h3>", unsafe_allow_html=True)
    
    # Simplified connection options - no tabs for easier understanding
    with st.container():
        st.markdown("<h4 style='margin-bottom: 1rem; text-align: center;'>Enter Business Details</h4>", unsafe_allow_html=True)
    
        with st.form("connect_business_form"):
            business_code = st.text_input("Business ID", placeholder="Enter the business ID", 
                                help="Ask the business owner for their ID")
            
            business_pin = st.text_input("Access PIN (4-digit)", max_chars=4, placeholder="Enter the 4-digit PIN",
                               help="Ask the business owner for their 4-digit PIN")
            
            connect_button = st.form_submit_button("Connect to Business", use_container_width=True)
            
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
    
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Camera option below text input
    st.markdown("<h4 style='text-align: center; margin-bottom: 1rem;'>Or Scan QR Code</h4>", unsafe_allow_html=True)
    
    # Center the camera input
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        uploaded_qr = st.camera_input("Take a picture of QR code", key="qr_camera")
        
        if uploaded_qr is not None:
            # In a real app, we would process the QR code image here
            st.info("QR code processing would happen here. For now, please use the manual entry option above.")
def customer_business_detail():
    # Hide the default Streamlit menu
    hide_streamlit_style = """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # Add larger font and easier to read styles
    st.markdown("""
    <style>
    /* Larger text for better readability */
    .streamlit-container {
        font-size: 18px !important;
    }
    /* Bigger touch targets */
    button, select, input {
        min-height: 48px !important;
        font-size: 16px !important;
    }
    /* Improved spacing */
    .large-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 20px;
        border: 1px solid #ddd;
        text-align: center;
    }
    .card-title {
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
        color: #555;
    }
    .card-value {
        font-size: 1.8rem;
        font-weight: bold;
    }
    .transaction-item {
        padding: 15px;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 15px;
        border: 1px solid #ddd;
    }
    .transaction-type {
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .transaction-amount {
        font-size: 1.4rem;
        margin-bottom: 5px;
    }
    .transaction-date {
        font-size: 1rem;
        color: #666;
    }
    </style>
    """, unsafe_allow_html=True)

    # Large back button
    if st.button("← Back to Dashboard", key="back_to_dashboard", use_container_width=True):
            st.session_state.page = "customer_dashboard"
            st.rerun()
    
    # Main heading
    st.markdown(f"<h1 style='text-align: center; margin: 1rem 0; font-size: 2.2rem;'>Business Details</h1>", unsafe_allow_html=True)
    
    business_id = st.session_state.selected_business_id
    customer_id = st.session_state.customer_id
    
    # Get business and transaction details
    business, customer, transactions, credit_total, payment_total, current_balance = \
        data_service.get_customer_business_view(business_id, customer_id)
    
    st.markdown(f"<h2 style='text-align: center; margin-bottom: 1.5rem; font-size: 1.8rem;'>{business.get('name', 'Unknown Business')}</h2>", unsafe_allow_html=True)
    
    # Summary cards in a clean, modern layout
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class='large-card'>
            <div class='card-title'>Total Credit</div>
            <div class='card-value' style='color: #E57373;'>₹{credit_total}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='large-card'>
            <div class='card-title'>Total Payments</div>
            <div class='card-value' style='color: #81C784;'>₹{payment_total}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Current balance - make this stand out
        st.markdown(f"""
    <div class='large-card' style='background-color: #e8eaf6; border: 2px solid #3f51b5;'>
        <div class='card-title' style='font-size: 1.4rem;'>Current Balance</div>
        <div class='card-value' style='font-size: 2.2rem; color: {"#E57373" if float(current_balance) > 0 else "#81C784"};'>₹{current_balance}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add a divider for clean separation
    st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # Transaction forms in a cleaner layout - simplified to buttons first
    st.markdown("<h3 style='text-align: center; margin-bottom: 1.5rem; font-size: 1.8rem;'>What would you like to do?</h3>", unsafe_allow_html=True)
    
    # Action buttons first for clearer navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Take Credit", key="show_credit_form", use_container_width=True):
            st.session_state.show_form = "credit"
            st.rerun()
    
    with col2:
        if st.button("Make Payment", key="show_payment_form", use_container_width=True):
            st.session_state.show_form = "payment"
            st.rerun()
    
    # Initialize session state if needed
    if "show_form" not in st.session_state:
        st.session_state.show_form = None
    
    # Show the selected form if any
    if st.session_state.show_form == "credit":
        st.markdown("<h3 style='text-align: center; margin: 1.5rem 0 1rem 0;'>Take Credit</h3>", unsafe_allow_html=True)
            
        with st.form("take_credit_form"):
            # More elegant number input with clear layout
            credit_amount = st.number_input("Credit Amount (₹)", min_value=1, value=100, 
                                           step=10, help="Enter the amount of credit to take")
            
            credit_note = st.text_input("Note (optional)", key="credit_note_customer", 
                                        placeholder="What is this credit for?")
            
            credit_col1, credit_col2 = st.columns(2)
            with credit_col1:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.show_form = None
                    st.rerun()
                    
            with credit_col2:
                submit_credit = st.form_submit_button("Confirm Credit", use_container_width=True)
            
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
                    st.session_state.show_form = None
                    st.rerun()
                else:
                    st.error("Failed to record credit transaction")
    
    elif st.session_state.show_form == "payment":
        st.markdown("<h3 style='text-align: center; margin: 1.5rem 0 1rem 0;'>Make Payment</h3>", unsafe_allow_html=True)
            
        with st.form("make_payment_form"):
            # More elegant number input with clear layout
            payment_amount = st.number_input("Payment Amount (₹)", min_value=1, value=100, 
                                          step=10, help="Enter the amount you paid to the business")
            
            payment_note = st.text_input("Note (optional)", key="payment_note_customer", 
                                       placeholder="Any details about this payment?")
            
            payment_col1, payment_col2 = st.columns(2)
            with payment_col1:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.show_form = None
                    st.rerun()
                    
            with payment_col2:
                submit_payment = st.form_submit_button("Confirm Payment", use_container_width=True)
            
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
                    st.session_state.show_form = None
                    st.rerun()
                else:
                    st.error("Failed to record payment transaction")
    
    # Add a divider for clean separation
    st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # Transaction history with clearer formatting
    st.markdown("<h3 style='text-align: center; margin-bottom: 1rem; font-size: 1.8rem;'>Transaction History</h3>", unsafe_allow_html=True)
    
    if transactions:
            for t in transactions:
                transaction_type = t.get('transaction_type', '')
                amount = float(t.get('amount', 0))
                date = data_service.format_datetime(t.get('created_at', ''))
                note = t.get('notes', '')
                
            # Simplified transaction display with clear formatting
                    if transaction_type == 'credit':
                icon = "🔴"
                color = "#E57373"
                type_text = "Credit"
                    elif transaction_type == 'payment':
                icon = "🟢"
                color = "#81C784"
                type_text = "Payment"
                    else:
                icon = "⚪"
                color = "#9E9E9E"
                type_text = transaction_type.capitalize()
                
            st.markdown(f"""
            <div class='transaction-item'>
                <div class='transaction-type' style='color: {color};'>{icon} {type_text}</div>
                <div class='transaction-amount'>₹{amount:.2f}</div>
                <div class='transaction-date'>{date}</div>
                {f"<div style='margin-top: 5px; font-style: italic;'>{note}</div>" if note else ""}
            </div>
            """, unsafe_allow_html=True)
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