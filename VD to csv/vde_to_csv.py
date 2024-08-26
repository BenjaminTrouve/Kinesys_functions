import pandas as pd
import os
import pyarrow.feather as feather

def func_convert_vde_to_csv(file_path, output_folder):

    def parse_vd_file(file_path):
        header_info = {}
        data = []

        with open(file_path, 'rt',encoding='latin-1') as file:
            for line in file:
                line = line.strip()
                if line.startswith("*"):
                    parts = line.split("-")
                    key = parts[0].strip("*")
                    value = parts[1].strip()
                    header_info[key] = value
                elif line:
                    data.append(line)

        return header_info, data
    def parse_data_lines(data):
        parsed_data = []
        for line in data:
            row = line.split(',')
            row = [item.strip('"') for item in row]
            parsed_data.append(row)
        
        return pd.DataFrame(parsed_data)
    
    header_info, data_lines = parse_vd_file(file_path)
    parsed_data = parse_data_lines(data_lines)
    parsed_data = parsed_data.dropna(axis = 1)

    filename = file_path.split("/")[-1]

    unique_values = parsed_data[0].unique()

    # Define the new folder 
    # new_folder = r'C:\Users\trouvebe\Desktop\Thesis\Chapter 1\Output\test vd' + '/' + filename.replace('.vd', "") 
    new_folder = output_folder.replace('\\','/') + '/' + filename.replace('.vde', "") 
    # path  = new_folder + "/"

    # Create the directory
    os.makedirs(new_folder, exist_ok=True)
    os.chdir(new_folder)

    # Loop through unique values
    for value in unique_values:
        # Filter the DataFrame based on the value of the column
        filtered_df = parsed_data[parsed_data[0] == value]
        
        # Export the filtered DataFrame to a separate sheet in the Excel file
        filtered_df.to_csv(str(value) + '_'+ filename.replace(".vd", ".csv"), index=False)


# func_convert_vd_to_csv(r'D:\Veda\Veda\GAMS_WrkTIMES\NZE\NZE~0004' + '/' + 'nze~0004_1406.vd')
