"""
This module provides functionality for analysing and modifying general AFM data. The data is then saved to a new CSV file.
"""

from pathlib import Path
from tkinter import filedialog
import pandas as pd
import units

OUTPUT_FILE = "general_output.csv"
min_position_threshold = 300e-9

def analyse_data(file_path, output_list):
    
    data = pd.read_csv(file_path, sep="\t")

    data = units.change_column_prefix(data, "Adhesion [N]", "p")
    data = units.change_column_prefix(data, "Area [J]", "a")

    no_interaction = ((data["Fitted Segment Count"] == 0) | ((data["Fitted Segment Count"] == 1) & (data["Minimum Position [m]"] < min_position_threshold))).sum()
    specific = ((data["Fitted Segment Count"] == 1) & (data["Minimum Position [m]"] >= min_position_threshold)).sum()
    non_specific = (data["Fitted Segment Count"] > 1).sum()
    total = no_interaction + specific + non_specific
    
    
    el = [Path(file_path).stem, no_interaction, specific, non_specific, round(no_interaction/total*100,1), round(specific/total*100,1), round(non_specific/total*100,1)]
    
    for i in range(len(output_list)):
        if output_list[i][0] == el[0]:
            output_list.pop(i)
            break
    
    output_list.append(el)
    
    data = data[(data["Fitted Segment Count"] > 1) | ((data["Fitted Segment Count"] == 1) & (data["Minimum Position [m]"] >= min_position_threshold))]

    data = data.drop(columns=['Filename', 'Position Index', 'X Position', 'Y Position','Baseline Offset [N]', 'Baseline Slope [N/m]','Contact Point Offset [m]', 'Minimum Value [N]','Minimum Position [m]', 'Filter Group', 'Lower Bound [m]','Upper Bound [m]', 'Fitted Segment Count'])

    data = data.round(1)

    return data


if __name__ == "__main__":

    data_output = pd.read_csv(OUTPUT_FILE)
    output_list = data_output.values.tolist()

    # Prompt the user to select files
    files = filedialog.askopenfilenames(filetypes=[("TSV files", "*.tsv")])

    for file in files:

        filtered_data = analyse_data(file, output_list)

        # Save the filtered data to a new CSV file
        filtered_data.to_csv(f"{Path(file).stem}_filtered.csv", index=False)

    data_output = pd.DataFrame(output_list, columns=['File Name', 'No Interaction', 'Specific', 'Non-specific','No Interaction %', 'Specific %', 'Non-specific %'])
    data_output.to_csv(OUTPUT_FILE, index=False)