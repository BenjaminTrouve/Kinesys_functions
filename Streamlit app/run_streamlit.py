import os
import webbrowser
import time
import subprocess

# Path to your Streamlit app file
# app_file = "C:\\Users\\trouvebe\\Desktop\\Thesis\\Chapter 1\\Python functions\\Kinesys post-processing\\Main code\\Test Streamlit\\main_dashboard.py"
app_file = r"C:\Users\trouvebe\Desktop\Thesis\Chapter 1\Python functions\Kinesys post-processing\Main code\Test Streamlit\main_dashboard.py"
app_file = app_file.replace('/','\\')
# Command to run the Streamlit app
command = f"streamlit run \"{app_file}\""

# Start the Streamlit app
# process = subprocess.Popen(command, shell=True)
os.system(command)

# Wait for a few seconds to ensure the server starts
time.sleep(2)

webbrowser.open('http://localhost:8501')

# process.wait()