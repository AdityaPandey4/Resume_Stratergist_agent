# frontend/app.py

import streamlit as st
import requests
import os
from dotenv import load_dotenv
# --- Page Configuration ---
st.set_page_config(
    page_title="Resume Strategist",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="auto",
)

# --- API Configuration ---
# The trailing slashes are important!
load_dotenv()
PROCESS_URL = os.getenv("BACKEND_URL")
RESULTS_URL = os.getenv("RESULTS_URL")

# --- Initialize Session State ---
# Simplified state without run_id
if 'primary_content' not in st.session_state:
    st.session_state['primary_content'] = {}
if 'secondary_files' not in st.session_state:
    st.session_state['secondary_files'] = []
if 'selected_json_content' not in st.session_state:
    st.session_state['selected_json_content'] = None


# --- Callback Function ---
def fetch_selected_json():
    """Callback function to fetch and store the content of the selected JSON file."""
    selected_file = st.session_state.get('json_selector') 

    if selected_file:
        try:
            # --- CHANGE: Simplified URL construction without run_id ---
            file_url = f"{RESULTS_URL}{selected_file}"
            file_response = requests.get(file_url)

            if file_response.status_code == 200:
                st.session_state['selected_json_content'] = file_response.json()
            else:
                st.session_state['selected_json_content'] = {"error": "Could not retrieve JSON content.", "status_code": file_response.status_code}
        except requests.exceptions.RequestException as e:
            st.session_state['selected_json_content'] = {"error": f"Failed to fetch JSON file: {e}"}


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

# --- Main Logic on Button Click ---
if st.button("✨ Generate Tailored Resume", type="primary", use_container_width=True):
    # Reset state on every new run
    st.session_state['primary_content'] = {}
    st.session_state['secondary_files'] = []
    st.session_state['selected_json_content'] = None

    if uploaded_file is not None and city:
        with st.spinner("🚀 The AI agents are hard at work... This may take a minute or two."):
            try:
                files = {'resume_file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {'city': city}
                response = requests.post(PROCESS_URL, files=files, data=data)
                
                if response.status_code == 200:
                    st.success("✅ Crew finished! Review your new resume below.")
                    
                    result_data = response.json()
                    st.session_state['primary_content'] = result_data.get('primary_content', {})
                    st.session_state['secondary_files'] = result_data.get('secondary_files', [])
                else:
                    error_message = response.json().get('detail', 'An unknown error occurred.')
                    st.error(f"❌ An error occurred: {error_message} (Status code: {response.status_code})")
            
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Failed to connect to the backend service. Please ensure it's running. Error: {e}")
    else:
        st.warning("Please upload a resume and enter a city to proceed.")


# --- Display Logic ---
if st.session_state.get('primary_content'):
    st.subheader("Results")

    tab_titles = ["✨ Tailored Resume", "📝 AI Review"]
    tab1, tab2 = st.tabs(tab_titles)

    with tab1:
        st.header("Tailored Resume (New_resume.md)")
        resume_content = st.session_state['primary_content'].get("New_resume.md", "Resume content not available.")
        st.markdown(resume_content)
        st.download_button(
            label="📥 Download Tailored Resume",
            data=resume_content.encode('utf-8'),
            file_name="New_resume.md",
            mime="text/markdown",
            use_container_width=True
        )

    with tab2:
        st.header("AI Analysis & Review (Review.md)")
        review_content = st.session_state['primary_content'].get("Review.md", "Review content not available.")
        st.markdown(review_content)
        st.download_button(
            label="📥 Download AI Review",
            data=review_content.encode('utf-8'),
            file_name="Review.md",
            mime="text/markdown",
            use_container_width=True
        )

    if st.session_state.get('secondary_files'):
        with st.expander("🔬 View Technical JSON Outputs"):
            st.selectbox(
                label="Choose a JSON file to inspect:",
                options=st.session_state['secondary_files'],
                index=None,
                placeholder="Select a file...",
                key='json_selector',
                on_change=fetch_selected_json
            )
            
            if st.session_state.get('selected_json_content'):
                st.json(st.session_state['selected_json_content'])