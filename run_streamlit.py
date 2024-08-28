import streamlit 
import requests
import os
import subprocess
import time
import tempfile
import webbrowser

# GitHub URL containing the Streamlit app code
url = 'https://raw.githubusercontent.com/BenjaminTrouve/Kinesys_functions/main/main_dashboard.py'

# Step 1: Download the content from the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    file_content = response.text
    
    # Step 2: Save the content to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
        temp_file.write(file_content.encode('utf-8'))
        temp_file_path = temp_file.name
    
    # Step 3: Command to run the Streamlit app
    command = f"streamlit run \"{temp_file_path}\" --server.maxUploadSize 400"
    
    # Start the Streamlit app
    os.system(command)
    
    # Wait for a few seconds to ensure the server starts
    time.sleep(2)
    
    # Open the web browser to access the Streamlit app
    webbrowser.open('http://localhost:8501')
else:
    print(f"Failed to download the file. Status code: {response.status_code}")