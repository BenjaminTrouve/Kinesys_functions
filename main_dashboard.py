import streamlit as st
import pandas as pd
import os
import warnings 
import glob
from nbconvert import PythonExporter
import nbformat
import glob
import importlib.util
import matplotlib.pyplot as plt
import requests
import json

warnings.filterwarnings('ignore')

storage_file = 'C:/Users/trouvebe/Desktop/Test streamlit 2/input storage/input_storage.json'

# Function to load inputs from the storage file
def load_inputs():
    if os.path.exists(storage_file):
        with open(storage_file, 'r') as f:
            return json.load(f)
    return {}

# Function to save inputs to the storage file
def save_inputs(inputs):
    with open(storage_file, 'w') as f:
        json.dump(inputs, f)

if 'inputs' not in st.session_state:
    st.session_state.inputs = load_inputs()

input_fields = {
    'vd_file_path': 'Enter vd file path',
    'folder_path': "Enter folder path",
    'figure_path': "Enter file name",
}

# Initialize inputs in session state if not already set
for key in input_fields.keys():
    if key not in st.session_state.inputs:
        st.session_state.inputs[key] = ""

def inverse_process_string_list(input_list):
        processed_list = []
        for input_string in input_list:
            # Prepend 'func_' to the entire string
            reconstructed_string = 'func_' + '_'.join(input_string.split())
            processed_list.append(reconstructed_string)
        return processed_list


def get_python_files_from_github_folder(folder_url):
    """Retrieve and execute .py files from a GitHub folder."""
    # Extract the API URL to list contents of the folder
    folder_api_url = folder_url.replace('https://github.com/', 'https://api.github.com/repos/')
    folder_api_url = folder_api_url.replace('tree/main/', 'contents/')

    # Get the list of files in the folder
    response = requests.get(folder_api_url)
    
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve folder contents: {response.status_code}")

    contents = response.json()
    
    # Filter out .py files
    py_files = [item for item in contents if item['name'].endswith('.py') and item['type'] == 'file']

    if not py_files:
        raise Exception("No Python (.py) files found in the folder.")
    
    # Process each .py file
    all_functions = {}
    for file_info in py_files:
        file_url = file_info['download_url']
        # print(file_url)  # Direct URL to the raw file content
        # print(f"Processing file: {file_info['name']}")
        f = import_functions_from_github(file_url)
        all_functions.update(f)
    return all_functions

def import_functions_from_github(file_url):
    """Import functions starting with 'func_' from a Python script on GitHub."""
    # Fetch the script content from GitHub
    response = requests.get(file_url)
    
    if response.status_code != 200:
        raise Exception(f"Failed to download script: {response.status_code}")
    
    script_content = response.text

    # Create a temporary module
    module_name = os.path.splitext(os.path.basename(file_url))[0]
    spec = importlib.util.spec_from_loader(module_name, loader=None)
    module = importlib.util.module_from_spec(spec)
    
    # Execute the script content within this module
    exec(script_content, module.__dict__)
    
    # Import and return all functions starting with 'func_'
    functions = {name: obj for name, obj in module.__dict__.items() if callable(obj) and name.startswith('func_')}
    # print(functions)
    return functions

####################################
################################
############################


st.set_page_config(page_title='KINESYS dashboard', page_icon=':bar_chart:',layout='wide')
# st.set_option('server.maxUploadSize', 400)

st.title(':bar_chart: KINESYS Results')

tab0, tab1, tab2 = st.tabs(["**Guidelines**","**VD to CSV**", "**Figure display**"])

with tab0:
    st.write('**Function template**')
    
with tab1:
    
    col1, col2, col3 = st.columns([3, 1, 3], vertical_alignment='center')
    
    with col1:
        st.session_state.inputs['vd_file_path'] = st.text_input(':open_file_folder: Enter the WorkTIMES directory'
                                                               , st.session_state.inputs['vd_file_path'])
        directory = st.session_state.inputs['vd_file_path']

    with col2:
        st.markdown(
            """
            <div style='text-align: center; font-size: 36px; line-height: 1.5;'>&rarr;</div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.session_state.inputs['folder_path'] = st.text_input(':open_file_folder: Enter the folder for CSV files'
                                                               , st.session_state.inputs['folder_path'])
        output_data_in = st.session_state.inputs['folder_path'] 

    # col4 = st.columns((1))
    run_options1 = ['nze~0004','aps~0003','steps~0002','KSRef_Tot_2','NZE_H2prod_cost~0004']
    
    # with col4:
    scenario_name_vd = st.selectbox(':lower_left_fountain_pen: Choose scenario name:', key='reference name vd', options=  run_options1)
    if '~' in scenario_name_vd:
        scenario = scenario_name_vd.split('~')
        scenario =  scenario[0].upper()
    else:
        scenario = None

    fl_vd = st.file_uploader(":page_facing_up: Choose VD file:", type=['vd'])
    fl_vde = st.file_uploader(":page_facing_up: Choose VDE file:", type=['vde'])
    
    if fl_vd and directory and output_data_in and scenario_name_vd:
        filename = fl_vd.name
        if scenario:
            directory_vd = directory.replace('\\','/') + '/' + scenario + '/' + scenario_name_vd
        else:
            directory_vd = directory.replace('\\','/') + '/' + scenario_name_vd
        file_path = directory_vd + '/' + filename
        # st.write(file_path)

        folder_url_csv = 'https://github.com/BenjaminTrouve/Kinesys_functions/tree/main/VD%20to%20csv'
        function_to_csv  = get_python_files_from_github_folder(folder_url_csv)


        str_keys = [str(key) for key in function_to_csv.keys()]
        vd_to_csv_func =  function_to_csv[str_keys[0]]
        #vde_to_csv_func = function_to_csv[str_keys[1]]
        vd_to_csv_func(file_path,output_data_in)
        #vde_to_csv_func(file_path,output_data_in)

        st.write(' Successfully converted !!!')
        
    if fl_vde and directory and output_data_in and scenario_name_vd:
        filename = fl_vde.name
        if scenario:
            directory_vde = directory.replace('\\','/') + '/' + scenario + '/' + scenario_name_vd
        else:
            directory_vde = directory.replace('\\','/') + '/' + scenario_name_vd
        file_path = directory_vde + '/' + filename
        # st.write(file_path)

        folder_url_csv = 'https://github.com/BenjaminTrouve/Kinesys_functions/tree/main/VD%20to%20csv'
        function_to_csv  = get_python_files_from_github_folder(folder_url_csv)


        str_keys = [str(key) for key in function_to_csv.keys()]
        # vd_to_csv_func =  function_to_csv[str_keys[0]]
        vde_to_csv_func = function_to_csv[str_keys[1]]
        # vd_to_csv_func(file_path,output_data_in)
        vde_to_csv_func(file_path,output_data_in)

        st.write(' Successfully converted !!!')    

with tab2:
    st.markdown('**STEP 1: Set the directory for the input data and figures output**')
    col1, col2, col3 = st.columns([3, 1, 3], vertical_alignment='center')
    with col1:
        
        st.session_state.inputs['folder_path'] = st.text_input(":open_file_folder: Enter the path for in input data"
                                                               , st.session_state.inputs['folder_path'])
        input_path = st.session_state.inputs['folder_path']
    with col2:
        st.markdown(
            """
            <div style='text-align: center; font-size: 36px; line-height: 1.5;'>&rarr;</div>
            """,
            unsafe_allow_html=True
        )
    with col3:

        st.session_state.inputs['figure_path'] = st.text_input(":open_file_folder: Enter figure output folder"
                                                               , st.session_state.inputs['figure_path'])
        output_path = st.session_state.inputs['figure_path']

    st.markdown('**STEP 2: Choose your scenario name**')
    col4, col5 = st.columns((2))

    run_options1 = ['nze~0004','aps~0003','steps~0002','KSRef_Tot_2','NZE_H2prod_cost~0004']
    run_options2 = ['nze~0004','aps~0003','steps~0002','KSRef_Tot_2','NZE_H2prod_cost~0004']
    with col4:
        reference_name = st.selectbox(':lower_left_fountain_pen: Choose reference scenario name:', key='reference name', options=  run_options1)

    with col5:
        scenario_name = st.selectbox(':lower_left_fountain_pen: Choose scenario name:',key='scenario name', options = run_options2)
        
    st.markdown('**STEP 3: Choose the reference and the scenario run based on the running date**')
    col6, col7 = st.columns((2))
    start_date = '2024-05-28'
    end_date = '2024-06-14'
    date_series = pd.date_range(start=start_date, end=end_date,freq='D')

    ref_date = date_series.min()
    scen_date = date_series.max()

    with col6:
        date_ref = pd.to_datetime(st.date_input(':date: Reference date', ref_date))
        date_ref_ddmm = date_ref.strftime('%d%m')

    with col7:
        date_scen = pd.to_datetime(st.date_input(':date: Scenario date', scen_date))
        date_scen_ddmm = date_scen.strftime('%d%m')

    st.markdown('**STEP 4: Choose figure to display!**')

    def scenario_param(name_ref,name_scen, date_ref, date_scen,input_path,output_path):
        date_list = [date_ref, date_scen]
        run_name_ref = f'{name_ref}_{date_list[0]}'
        run_name_scen = f'{name_scen}_{date_list[1]}'
        folder_path = input_path.replace('\\','/')
        # file_path_ref = os.path.join(folder_path,run_name_ref) 
        file_path_ref = folder_path + '/' + run_name_ref + '/'
        # file_path_scen = os.path.join(folder_path,run_name_scen)
        file_path_scen = folder_path + '/' + run_name_scen + '/'
        
        output_path1 = output_path.replace('\\','/')
        output_folder = os.path.join(output_path1,run_name_scen) + '/'


        os.makedirs(output_folder, exist_ok=True)
        return run_name_ref, run_name_scen, file_path_ref, file_path_scen, output_folder

    if input_path and output_path and date_ref_ddmm and date_scen_ddmm and reference_name and scenario_name:
        run_name_ref, run_name_scen, file_path_ref, file_path_scen, output_folder = scenario_param(reference_name, scenario_name, date_ref_ddmm,date_scen_ddmm,input_path,output_path)


    folder_url = 'https://github.com/BenjaminTrouve/Kinesys_functions/tree/main/Analysis'
    all_functions  = get_python_files_from_github_folder(folder_url)

    def process_string_list(input_list):
        processed_list = []
        for input_string in input_list:
            substrings = input_string.split('_')
            filtered_substrings = [s for s in substrings if "func" not in s]
            result_string = ' '.join(filtered_substrings)
            processed_list.append(result_string)
        return processed_list


    def get_function_args(func):
        signature = inspect.signature(func)
        return signature.parameters
        
    # st.sidebar.title('Figure selection')
    # function_choice = st.multiselect('Choose your figures:', process_string_list(all_functions.keys()))
    with st.form(key='multiselect_form'):
        function_choice = st.multiselect(':chart_with_upwards_trend: Choose your figures:', process_string_list(all_functions.keys()))
        
        # Create a submit button
        submit_button = st.form_submit_button(label='Confirm Selection')
    
    # Check if the submit button is clicked and if all options are selected
    if submit_button:
        function_choice_list = inverse_process_string_list(function_choice)
        
        # user_inputs = {}  # Dictionary to hold the user's inputs for each function's arguments

        # for func_name in function_choice_list:
        #     func = all_functions[func_name]
        #     func_args = get_function_args(func)
    
        #     # Display the function name as a header
        #     st.write(f"**Parameters for {func_name}:**")
    
        #     # Collect input for each argument
        #     func_input = {}
        #     for arg_name, arg_param in func_args.items():
        #         default_value = arg_param.default if arg_param.default != inspect.Parameter.empty else None
        #         func_input[arg_name] = st.checkbox(f"{arg_name}", value=default_value)
        #     user_inputs[func_name] = func_input
            
        # for func_name in function_choice_list:
        #     func = all_functions[func_name]
        #     inputs = user_inputs[func_name]
        #     fig = func(**inputs)  # Pass the inputs as keyword arguments
        #     st.pyplot(fig, use_container_width=True)
        #     plt.close(fig)

        
        for func_name in function_choice_list:
            func =  all_functions[func_name]
            # st.set_option('deprecation.showPyplotGlobalUse', False) 
            fig = func(file_path_scen,file_path_ref, run_name_scen,run_name_ref,output_folder)
            st.pyplot(fig,use_container_width=True)
            plt.close(fig)


save_inputs(st.session_state.inputs)

