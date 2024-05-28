import pandas as pd
from pathlib import Path
from tkinter import filedialog
import units
import matplotlib.pyplot as plt
import numpy as np


def histogram(values, x_label, y_label):
    """
    This function creates a bar graph from the given data.
    """
    w = 20
    plt.hist(values, bins=np.arange(min(values), max(values) + w, w))
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()

def analyse_data(file_path):
    
    data = pd.read_csv(file_path, sep="\t")

    # print(data.columns)
    
    data = units.change_column_prefix(data, "Bending Length [m]", "p")
    data = units.change_column_prefix(data, "Contour Length [m]", "n")
    data = units.change_column_prefix(data, "Residual RMS [N]", "p")
    data = units.change_column_prefix(data, "Breaking Force [N]", "p")

    data = data[(data["Bending Length [pm]"] < 4000) & (data["Bending Length [pm]"] > 20) & (data["Contour Length [nm]"] < 5000) & (data["Contour Length [nm]"] > 300) & (data["Residual RMS [pN]"] < 25)]

    return data

def max_length_dict(dictionary):
    
    max_length = 0
    
    for key in dictionary:
        if len(dictionary[key]) > max_length:
            max_length = len(dictionary[key])
    
    return max_length


if __name__ == "__main__":
    
    
    breaking_forces = {}
    
    # Prompt the user to select files
    files = filedialog.askopenfilenames(filetypes=[("File Types:", "*.tsv *.txt")])

    for file in files:

        filtered_data = analyse_data(file)
        
        segments = Path(file).stem.split("-")
        new_name = segments[0] + segments[2]
        
        breaking_forces[new_name] = filtered_data["Breaking Force [pN]"].tolist()
        # histogram(filtered_data["Breaking Force [pN]"], "Breaking Force [pN]", "Frequency")

        # Save the filtered data to a new CSV file
        filtered_data.to_csv(f"chainfits\\{Path(file).stem}_filtered.csv", index=False)
    
    max_length = max_length_dict(breaking_forces)
    for key in breaking_forces:
        breaking_forces[key] = list(np.pad(breaking_forces[key], (0, max_length - len(breaking_forces[key])), 'constant', constant_values=(np.nan)))
        print(len(breaking_forces[key]))

    
    breaking_forces_df = pd.DataFrame(breaking_forces)
    breaking_forces_df.to_csv(f"breaking_forces.csv", index=False)
