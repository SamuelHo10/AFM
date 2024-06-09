import pandas as pd
from pathlib import Path
from tkinter import filedialog
import units
import matplotlib.pyplot as plt
import numpy as np

data_save_folder = "chainfits"
plot_save_folder = "breaking_force_plots"


def analyse_files(files):
    filtered_data = []
    
    for file in files:
        df = pd.read_csv(file, sep="\t")

        # Adjust units
        df = units.change_column_prefix(df, "Bending Length [m]", "p")
        df = units.change_column_prefix(df, "Contour Length [m]", "n")
        df = units.change_column_prefix(df, "Residual RMS [N]", "p")
        df = units.change_column_prefix(df, "Breaking Force [N]", "p")

        # Filter out data that is not within the expected range
        df = df[(df["Bending Length [pm]"] < 4000) & (df["Bending Length [pm]"] > 20) & (df["Contour Length [nm]"] < 5000) & (df["Contour Length [nm]"] > 300) & (df["Residual RMS [pN]"] < 25)]
        
        filtered_data.append((df,file))

    return filtered_data

def max_length_dict(dictionary):
    """
    This function returns the maximum length of the lists in the dictionary.
    """
    max_length = 0
    
    for key in dictionary:
        if len(dictionary[key]) > max_length:
            max_length = len(dictionary[key])
    
    return max_length

def save_filtered_dfs(filtered_data):
    """
    This function saves the filtered data to new CSV files.
    """
    
    for filtered_df, file in filtered_data:
        filtered_df.to_csv(f"{data_save_folder}\\{Path(file).stem}_filtered.csv", index=False)

def compile_breaking_forces(filtered_data):
    """
    This function compiles all the breaking forces from the dataframes and saves them into on CSV file.
    """
    
    breaking_forces = {}

    for filtered_df, file in filtered_data:
        
        # Rename file names and have them as column headers for each file
        segments = Path(file).stem.split("-")
        new_name = segments[0] + "-" + segments[2]
        
        # Add each column to a dictionary
        breaking_forces[new_name] = filtered_df["Breaking Force [pN]"].tolist()
    
    # Ensure all lists in the dictionary are the same length
    breaking_forces_padded = {}
    max_length = max_length_dict(breaking_forces)
    for key in breaking_forces:
        breaking_forces_padded[key] = list(np.pad(breaking_forces[key], (0, max_length - len(breaking_forces[key])), 'constant', constant_values=(np.nan)))

    # Save the dictionary to a CSV file
    breaking_forces_df = pd.DataFrame(breaking_forces_padded)
    breaking_forces_df.to_csv(f"breaking_forces.csv", index=False)
    
    return breaking_forces



def create_histogram_set(dictionary, name, y_label, x_label="Breaking Force (pN)", bar_width = 20, legend_names = ["Cell Division", "Elongation", "Maturation"], force_range=[0,500], colors=["red","cyan","yellow"]):
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
    
    plt.savefig(f"{plot_save_folder}\\{name}.svg")


def create_histograms(breaking_forces):
    """
    This function creates histograms from the list of breaking forces. It also compiles all the files and creates a histogram with all the data.
    """
    
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
        
        create_histogram_set(dates[date], f"{date}-Count" , "Count")
        create_histogram_set(dates[date], f"{date}-Frequency" , "Frequency")
        
        for key in dates[date]:
            final[key] += dates[date][key]
    
    create_histogram_set(final, "Final Frequency", "Frequency")
    create_histogram_set(final, "Final Count", "Count")
    
    
if __name__ == "__main__":
    
    # Prompt the user to select files
    files = filedialog.askopenfilenames(filetypes=[("File Types:", "*.tsv *.txt")])

    filtered_data = analyse_files(files)
    
    save_filtered_dfs(filtered_data)
    
    breaking_forces = compile_breaking_forces(filtered_data)
    
    create_histograms(breaking_forces)
    

