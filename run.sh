#!/bin/bash
# Simple script to run the Streamlit app

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null
then
    echo "Streamlit not found. Installing requirements..."
    pip install -r requirements.txt
fi

# Run the Streamlit app
echo "Starting KathaPe Streamlit app..."
streamlit run app.py 