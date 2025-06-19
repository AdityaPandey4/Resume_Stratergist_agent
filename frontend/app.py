# frontend/app.py

import streamlit as st
import requests
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Resume Strategist",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="auto",
)

# --- API Configuration ---
# It's better to use an environment variable for the API URL in production
# but for local development, this is fine.
BACKEND_URL = os.getenv("BACKEND_URL")

# --- UI Components ---
st.title("📄 Resume Strategist AI")
st.markdown("""
Welcome! This tool helps you tailor your resume for a specific job by leveraging AI agents. 
Upload your resume, specify your desired city, and let the agents do the work.
""")

st.subheader("1. Upload Your Resume")
uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type="pdf",
    help="Please upload your resume in PDF format."
)

st.subheader("2. Enter Your Desired City")
city = st.text_input(
    "E.g., 'San Francisco', 'Remote', 'London'",
    placeholder="Enter the city for your job search"
)

st.divider()

if st.button("✨ Generate Tailored Resume", type="primary", use_container_width=True):
    if uploaded_file is not None and city:
        with st.spinner("🚀 The AI agents are hard at work... This may take a minute or two."):
            try:
                # Prepare the file and data for the API request
                files = {'resume_file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {'city': city}

                # Send the request to the FastAPI backend
                response = requests.post(BACKEND_URL, files=files, data=data)
                
                # Check the response from the backend
                if response.status_code == 200:
                    st.success("✅ Resume tailored successfully!")
                    
                    # Provide a download button for the result
                    st.download_button(
                        label="📥 Download Your New Resume",
                        data=response.content,
                        file_name="Tailored_Resume.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                    
                    # Optionally display the resume content
                    st.markdown("### Preview of Your New Resume:")
                    st.markdown(response.content.decode('utf-8'))

                else:
                    # Show an error message if something went wrong
                    error_message = response.json().get('detail', 'An unknown error occurred.')
                    st.error(f"❌ An error occurred: {error_message} (Status code: {response.status_code})")
            
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Failed to connect to the backend service. Please ensure it's running. Error: {e}")

    else:
        # Show a warning if the user hasn't provided all the required inputs
        st.warning("Please upload a resume and enter a city to proceed.")