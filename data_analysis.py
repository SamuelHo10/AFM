import pandas as pd
from pathlib import Path
from tkinter import filedialog
import units
import matplotlib.pyplot as plt
import numpy as np
import os

CHAIN_FIT_FOLDER = "chainfits"
PLOT_SAVE_FOLDER = "breaking_force_plots"
GENERAL_FOLDER = "general"

def analyze_chain_fit(files, directory, max_bending_length, min_bending_length, max_contour_length, min_contour_length, max_residual_rms):
    filtered_dfs = []
    
    for file in files:
        df = pd.read_csv(file, sep="\t")

        # Adjust units
        df = units.change_column_prefix(df, "Bending Length [m]", "p")
        df = units.change_column_prefix(df, "Contour Length [m]", "n")
        df = units.change_column_prefix(df, "Residual RMS [N]", "p")
        df = units.change_column_prefix(df, "Breaking Force [N]", "p")

        # Filter out data that is not within the expected range
        df = df[(df["Bending Length [pm]"] < max_bending_length) & (df["Bending Length [pm]"] > min_bending_length) & (df["Contour Length [nm]"] < max_contour_length) & (df["Contour Length [nm]"] > min_contour_length) & (df["Residual RMS [pN]"] < max_residual_rms)]
        
        filtered_dfs.append((df,file))
    
    save_filtered_dfs(filtered_dfs, directory, CHAIN_FIT_FOLDER)

    return filtered_dfs

def analyze_general(files, directory, min_position_threshold):
    
    filtered_dfs = []
    interaction_count_list = []
    
    for file in files:
        df = pd.read_csv(file, sep="\t")

        df = units.change_column_prefix(df, "Adhesion [N]", "p")
        df = units.change_column_prefix(df, "Area [J]", "a")

        no_interaction = ((df["Fitted Segment Count"] == 0) | ((df["Fitted Segment Count"] == 1) & (df["Minimum Position [m]"] < min_position_threshold))).sum()
        specific = ((df["Fitted Segment Count"] == 1) & (df["Minimum Position [m]"] >= min_position_threshold)).sum()
        non_specific = (df["Fitted Segment Count"] > 1).sum()
        total = no_interaction + specific + non_specific
        
        el = [Path(file).stem, no_interaction, specific, non_specific, round(no_interaction/total*100,1), round(specific/total*100,1), round(non_specific/total*100,1)]
        
        interaction_count_list.append(el)
        
        df = df[(df["Fitted Segment Count"] > 1) | ((df["Fitted Segment Count"] == 1) & (df["Minimum Position [m]"] >= min_position_threshold))]

        df = df.drop(columns=['Filename', 'Position Index', 'X Position', 'Y Position','Baseline Offset [N]', 'Baseline Slope [N/m]','Contact Point Offset [m]', 'Minimum Value [N]','Minimum Position [m]', 'Filter Group', 'Lower Bound [m]','Upper Bound [m]', 'Fitted Segment Count'])

        df = df.round(1)
        
        filtered_dfs.append((df,file))

    data_output = pd.DataFrame(interaction_count_list, columns=['File Name', 'No Interaction', 'Specific', 'Non-specific','No Interaction %', 'Specific %', 'Non-specific %'])
    data_output.to_csv(f"{directory}\\interaction_count.csv", index=False)
    
    save_filtered_dfs(filtered_dfs, directory, GENERAL_FOLDER)
    
    return filtered_dfs

def max_length_dict(dictionary):
    """
    This function returns the maximum length of the lists in the dictionary.
    """
    max_length = 0
    
    for key in dictionary:
        if len(dictionary[key]) > max_length:
            max_length = len(dictionary[key])
    
    return max_length

def save_filtered_dfs(filtered_data, directory, folder):
    """
    This function saves the filtered data to new CSV files.
    """
    
    if not os.path.exists(f"{directory}\\{folder}"):
        os.makedirs(f"{directory}\\{folder}")
    
    for filtered_df, file in filtered_data:
        filtered_df.to_csv(f"{directory}\\{folder}\\{Path(file).stem}_filtered.csv", index=False)

def compile_parameter(filtered_data, directory, parameter_name, file_name):
    
    parameters_dict = {}

    for filtered_df, file in filtered_data:
        
        # Rename file names and have them as column headers for each file
        segments = Path(file).stem.split("-")
        new_name = segments[0] + "-" + segments[2]
        
        # Add each column to a dictionary
        parameters_dict[new_name] = filtered_df[parameter_name].tolist()
    
    # Ensure all lists in the dictionary are the same length
    parameters_dict_padded = {}
    max_length = max_length_dict(parameters_dict)
    for key in parameters_dict:
        parameters_dict_padded[key] = list(np.pad(parameters_dict[key], (0, max_length - len(parameters_dict[key])), 'constant', constant_values=(np.nan)))

    # Save the dictionary to a CSV file
    parameters_df = pd.DataFrame(parameters_dict_padded)
    parameters_df.to_csv(f"{directory}\\{file_name}.csv", index=False)
    
    return parameters_dict



def create_histogram_set(dictionary, name, y_label, directory,x_label="Breaking Force (pN)", bar_width = 20, legend_names = ["Cell Division", "Elongation", "Maturation"], force_range=[0,500], colors=["red","cyan","yellow"]):
    """
    This function creates a set of histograms for maturation, elongation, and cell division.
    # """
    figure, axis = plt.subplots(3, 1, figsize=(8, 8)) 

    for i, (key, values) in enumerate(dictionary.items()):
        
        if(y_label == "Count"):
            weights = np.ones_like(values)
        elif(y_label == "Frequency"):
            weights = np.ones_like(values) / np.array(values).size
        
        axis[i].hist(values, bins=np.arange(force_range[0], force_range[1], bar_width), weights = weights , label=legend_names[i], color=colors[i], edgecolor = "black")
        axis[i].set_xlim(force_range)
        axis[i].legend(loc="upper right")
        axis[i].set_xlabel(x_label)
        axis[i].set_ylabel(y_label)
    
    # Adjust spacing
    figure.tight_layout()
    
    # Adjust axis
    plt.setp(axis, ylim=max([a.get_ylim() for a in axis.reshape(-1)]))
    
    plt.savefig(f"{directory}\\{PLOT_SAVE_FOLDER}\\{name}.svg")


def create_histograms(breaking_forces, directory, x_axis_upper_bound):
    """
    This function creates histograms from the list of breaking forces. It also compiles all the files and creates a histogram with all the data.
    """
    
    if not os.path.exists(f"{directory}\\{PLOT_SAVE_FOLDER}"):
        os.makedirs(f"{directory}\\{PLOT_SAVE_FOLDER}")
    
    final = {"CD": [], "E": [], "M": []}
    
    # Group the data so that cell maturation, elongation, and cell division are in the same dictionary
    dates = {}
    for key in breaking_forces:
        date, step = key.split("-")
        if date in dates:
            dates[date][step] = breaking_forces[key]
        else:
            dates[date] = {step: breaking_forces[key]}
    
    for date in dates:
        
        if len(dates[date]) < 3:
            print(f"Skipping {date} as it does not have all the necessary data.")
            continue
        
        # Reorder dictionary
        dates[date] = {k: dates[date][k] for k in ["M", "E", "CD"]}
        
        create_histogram_set(dates[date], f"{date}-Count" , "Count", directory, force_range=[0,x_axis_upper_bound])
        create_histogram_set(dates[date], f"{date}-Frequency" , "Frequency", directory, force_range=[0,x_axis_upper_bound])
        
        for key in dates[date]:
            final[key] += dates[date][key]
    
    create_histogram_set(final, "Final Frequency", "Frequency", directory, force_range=[0,x_axis_upper_bound])
    create_histogram_set(final, "Final Count", "Count", directory, force_range=[0,x_axis_upper_bound])
    
    
# if __name__ == "__main__":
    
#     # Prompt the user to select files
#     files = filedialog.askopenfilenames(filetypes=[("File Types:", "*.tsv *.txt")])

#     filtered_data = analyse_files(files)
    
#     save_filtered_dfs(filtered_data)
    
#     breaking_forces = compile_breaking_forces(filtered_data)
    
#     create_histograms(breaking_forces)
    

