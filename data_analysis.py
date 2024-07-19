import pandas as pd
from pathlib import Path
import units, graph
import numpy as np
import os



def analyse_chain_fit(files, max_bending_length, min_bending_length, max_contour_length, min_contour_length, max_residual_rms):
    """
    This function analyzes the chain fits data and filters out data that is not within the expected range and adjusts units.
    
    Parameters:
    files (list): The list of files to analyze.
    directory (str): The directory to save the filtered data.
    max_bending_length (float): The maximum bending length [pm].
    min_bending_length (float): The minimum bending length [pm].
    max_contour_length (float): The maximum contour length [pm].
    min_contour_length (float): The minimum contour length [pm].
    max_residual_rms (float): The maximum residual RMS [pN].
    
    Returns:
    filtered_dfs (list): The list of filtered dataframes.
    """
    
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
    
    return filtered_dfs



def analyse_general(files, min_position_threshold):
    """
    This function analyzes the general data and filters the data considered as having no interaction and adjusts units. It also counts the number of interactions for each interaction type.
    
    Parameters:
    files (list): The list of files to analyze.
    min_position_threshold (float): The minimum position threshold [m].
    
    Returns:
    (tuple): The filtered data and the interaction count dataframe.
    """
    
    filtered_data = []
    interaction_count_list = []
    
    for file in files:
        df = pd.read_csv(file, sep="\t")

        df = units.change_column_prefix(df, "Adhesion [N]", "p")
        df = units.change_column_prefix(df, "Area [J]", "a")
        df = units.change_column_prefix(df, "Minimum Position [m]", "n")

        # Count interactions and append them to the interaction counts list
        no_interaction = ((df["Fitted Segment Count"] == 0) | ((df["Fitted Segment Count"] == 1) & (df["Minimum Position [nm]"] < min_position_threshold))).sum()
        specific = ((df["Fitted Segment Count"] == 1) & (df["Minimum Position [nm]"] >= min_position_threshold)).sum()
        non_specific = (df["Fitted Segment Count"] > 1).sum()
        total = no_interaction + specific + non_specific
        el = [Path(file).stem, no_interaction, specific, non_specific, round(no_interaction/total*100,1), round(specific/total*100,1), round(non_specific/total*100,1)]
        interaction_count_list.append(el)
        
        # Filter out data that is considered as having no interaction
        df = df[(df["Fitted Segment Count"] > 1) | ((df["Fitted Segment Count"] == 1) & (df["Minimum Position [nm]"] >= min_position_threshold))]
        
        # Round values to one decimal place
        df = df.round(1)
        
        filtered_data.append((df,file))

    interaction_count_df = pd.DataFrame(interaction_count_list, columns=['File Name', 'No Interaction', 'Specific', 'Non-specific','No Interaction %', 'Specific %', 'Non-specific %'])
        
    return filtered_data, interaction_count_df



def count_fitting_segments(filtered_data, num_categories=5):
    """
    This function counts the number of fitting segments for each file.
    
    Parameters:
    filtered_data (list): The list of filtered data of the format (file, dataframe).
    directory (str): The directory to save the count data.
    
    Returns:
    dictionary (dict): The dictionary containing the count data.
    count_num_fitting_segments_df (pandas.DataFrame): The dataframe containing the count data.
    """
    dictionary = {}
    count_num_fitting_segments_df = pd.DataFrame()
    
    # Create an index for the dataframe
    index = [str(i) for i in range(1, num_categories)]
    index.append(f"\u2265{num_categories}")
    
    count_num_fitting_segments_df = pd.concat([count_num_fitting_segments_df, pd.Series(index, index=index)], axis=1)
    
    for (df, file) in filtered_data:
        
        # Count number of occurrences of each file name
        num_fitting_segments = df["Filename"].value_counts()
        
        count_num_fitting_segments = []
        
        # Determine the number of occurrences of each category
        for i in range(1, num_categories):
            count_num_fitting_segments.append((num_fitting_segments == i).sum())
        
        # Determine the number of occurrences of the last category
        count_num_fitting_segments.append((num_fitting_segments >= num_categories).sum())
        
        # Convert the list to a series
        count_num_fitting_segments_series = pd.Series(count_num_fitting_segments, index=index, name=Path(file).stem)
        
        # Add the series to the dataframe
        count_num_fitting_segments_df = pd.concat([count_num_fitting_segments_df, count_num_fitting_segments_series], axis=1)
        
        dictionary[Path(file).stem] = count_num_fitting_segments_series
    
    return dictionary, count_num_fitting_segments_df

def max_length_dict(dictionary):
    """
    This function returns the maximum length of the lists in the dictionary.
    
    Parameters:
    dictionary (dict): The dictionary containing the lists.
    
    Returns:
    max_length (int): The maximum length of the lists.
    """
    max_length = 0
    
    for key in dictionary:
        if len(dictionary[key]) > max_length:
            max_length = len(dictionary[key])
    
    return max_length



def save_filtered_dfs(filtered_data, directory):
    """
    This function saves the filtered data to new CSV files.
    
    Parameters:
    filtered_data (list): The list of filtered data of the format (file, dataframe).
    directory (str): The directory to save the filtered data.
    """
    
    if not os.path.exists(f"{directory}"):
        os.makedirs(f"{directory}")
    
    for filtered_df, file in filtered_data:
        filtered_df.to_csv(f"{directory}\\{Path(file).stem}_filtered.csv", index=False)



def compile_parameter(filtered_data, parameter_names):
    """
    This function compiles a parameter from the filtered data and and also adds it all onto one dataframe.
    
    Parameters:
    filtered_data (list): The list of filtered data of the format (file, dataframe).
    parameter_names (str | list): The name of the parameter(s) to compile.
    
    Returns:
    parameters_dict (dict): The dictionary containing the parameter values.
    """
    parameters_dict = {}
    
    if isinstance(parameter_names, str):
        parameter_names = [parameter_names]

    for filtered_df, file in filtered_data:
        
        for parameter_name in parameter_names:
            # Rename file names and have them as column headers for each file
            segments = Path(file).stem.split("-")
            new_name = segments[0]+ "-" + parameter_name + "-" + segments[-1] 
            
            # Add each column to a dictionary
            parameters_dict[new_name] = filtered_df[parameter_name].tolist()
    
    # Ensure all lists in the dictionary are the same length
    parameters_dict_padded = {}
    max_length = max_length_dict(parameters_dict)
    for key in parameters_dict:
        parameters_dict_padded[key] = list(np.pad(parameters_dict[key], (0, max_length - len(parameters_dict[key])), 'constant', constant_values=(np.nan)))

    # Convert the dictionary to a dataframe
    parameters_df = pd.DataFrame(parameters_dict_padded)
    
    return parameters_dict, parameters_df



if __name__ == "__main__":
    
    # For testing purposes only.
    files =[r"c:\Users\samue\Downloads\OneDrive_2_5-28-2024\20230306-VFB-E.txt", r"c:\Users\samue\Downloads\OneDrive_2_5-28-2024\20230306-VFB-M.txt" ,r"c:\Users\samue\Downloads\OneDrive_2_5-28-2024\20230306-VFB-CD.txt"]
    directory = "."

    filtered_data = analyse_chain_fit(files, directory, 4000, 20, 5000, 300, 25)
        
    num_fitting_segments = count_fitting_segments(filtered_data, directory)
    
    breaking_force_dict = compile_parameter(filtered_data, directory, "Breaking Force [pN]", "breaking_force")
    
    graph.create_histograms_root(breaking_force_dict, directory, 500)
    

