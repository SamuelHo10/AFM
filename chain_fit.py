import pandas as pd
from pathlib import Path
from tkinter import filedialog
import units



OUTPUT_FILE = "general_output.csv"
min_position_threshold = 300e-9

def analyse_data(file_path):
    
    data = pd.read_csv(file_path, sep="\t")

    print(data.columns)
    
    data = units.change_column_prefix(data, "Bending Length [m]", "p")
    data = units.change_column_prefix(data, "Contour Length [m]", "n")
    data = units.change_column_prefix(data, "Residual RMS [N]", "p")

    data = data[(data["Bending Length [pm]"] < 4000) & (data["Bending Length [pm]"] > 20) & (data["Contour Length [nm]"] < 5000) & (data["Contour Length [nm]"] > 300) & (data["Residual RMS [pN]"] < 25)]

    # no_interaction = ((data["Fitted Segment Count"] == 0) | ((data["Fitted Segment Count"] == 1) & (data["Minimum Position [m]"] < min_position_threshold))).sum()
    # specific = ((data["Fitted Segment Count"] == 1) & (data["Minimum Position [m]"] >= min_position_threshold)).sum()
    # non_specific = (data["Fitted Segment Count"] > 1).sum()
    # total = no_interaction + specific + non_specific
    
    
    # el = [Path(file_path).stem, no_interaction, specific, non_specific, no_interaction/total, specific/total, non_specific/total]
    
    # file_names = [x[0] for x in output_list]
    
    # if el[0] not in file_names:
    #     output_list.append(el)
    
    # data = data[(data["Fitted Segment Count"] > 1) | ((data["Fitted Segment Count"] == 1) & (data["Minimum Position [m]"] >= min_position_threshold))]

    # data = data.drop(columns=['Filename', 'Position Index', 'X Position', 'Y Position','Baseline Offset [N]', 'Baseline Slope [N/m]','Contact Point Offset [m]', 'Minimum Value [N]','Minimum Position [m]', 'Filter Group', 'Lower Bound [m]','Upper Bound [m]', 'Fitted Segment Count'])

    return data


if __name__ == "__main__":
    
    # Prompt the user to select files
    files = filedialog.askopenfilenames(filetypes=[("TSV files", "*.tsv")])

    for file in files:

        filtered_data = analyse_data(file)

        # Save the filtered data to a new CSV file
        filtered_data.to_csv(f"{Path(file).stem}_filtered.csv", index=False)

