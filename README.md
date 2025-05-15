# KathaPe - Streamlit App

A Streamlit version of the KathaPe digital credit book application.

## Features

- Business and Customer user types
- Credit management for businesses
- Transaction history
- Profile management
- QR code generation for business-customer connection

## Installation

1. Make sure you have Python installed (3.8+ recommended)
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Application

Run the Streamlit app with:

```bash
streamlit run app.py
```

The app will start and automatically open in your default web browser.

## Demo Credentials

- **Business**: 
  - Phone: 9999999999
  - Password: password123

- **Customer**: 
  - You can use any 10-digit number and 'demo123' as password

## Development

This app uses session state to store mock data, so all data will be reset when the server restarts.

## Running alongside Flask app

The Streamlit app can run alongside the Flask app without conflicts. When running both:

1. Run the Flask app on its default port (5003 or as configured):
   ```bash
   python app.py
   ```

2. Run the Streamlit app in a separate terminal:
   ```bash
   cd streamlit_app
   streamlit run app.py
   ```

The Streamlit app will run on port 8501 by default, which doesn't conflict with the Flask app. 