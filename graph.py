import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import os

PLOT_SAVE_FOLDER = "graphs"



def fix_labels(labels, tooclose=0.1, outer_radius = 1.25):
    """
    This function fixes the labels of a pie chart so that they do not overlap (for the most part). If the labels overlap, then the function will move them out of the pie chart as specified by the outer radius.
    
    Parameters:
    labels (list): The labels of the pie chart.
    tooclose (float): The minimum distance between two labels.
    outer_radius (float): The adjusted distance from the center of the pie chart to the label
    """
    
    for i in range(0, len(labels)-1):
        
        for j in range(i+1, len(labels)):
            
            a = np.array(labels[i].get_position())
            b = np.array(labels[j].get_position())
            
            dist = np.linalg.norm(a-b)
            
            if dist < tooclose:
                
                norm_b = b / np.linalg.norm(b)
                
                labels[j].set_x(norm_b[0]*outer_radius)
                labels[j].set_y(norm_b[1]*outer_radius)



def create_custom_pie_chart_legend(axis, series, colors = list(mpl.rcParams["axes.prop_cycle"])):    
    """
    This function generates a custom legend with square markers for a pie chart.
    
    Parameters:
    axis (matplotlib.axis): The axis of the pie chart.
    series (pandas.Series): The series that contains the data for the pie chart.
    colors (list): The list of colors to use for the markers.
    """
    
    legend_elements = [mpl.lines.Line2D([], [], color=colors[i]["color"], label=series.index[i], marker='s', markersize=3, linestyle='None') for i in range(len(series))]
    
    # Can change handletextpad and columnspacing to adjust the spacing between the legend elements. Change bbox_to_anchor to adjust the position of the legend.
    axis.legend(handles=legend_elements, handletextpad=-0.5, columnspacing=0.5, loc="lower center", ncol=len(series), framealpha=0, bbox_to_anchor=(0.5, -0.1))



def create_pie_chart_set(dictionary, filename, directory):
    """
    This function creates a figure containing three pie charts.
    
    Parameters:
    cell_type_dictionary (dict): The dictionary containing the data for the pie charts. Should contain three elements.
    filename (str): The name of the file to save the pie chart as.
    directory (str): The directory to save the pie chart in.
    """
    
    figure, axis = plt.subplots(1, 3, figsize=(8, 3)) 

    for i, (key, values) in enumerate(dictionary.items()):
        
        wedges, labels, autopct = axis[i].pie(values, autopct='%1.1f', startangle=90)
        
        fix_labels(autopct)
        
        create_custom_pie_chart_legend(axis[i], values)
    
    figure.tight_layout()
    
    plt.savefig(f"{directory}\\{filename}.svg")

def create_sub_dictionaries(dictionary):
    """
    This function creates a dictionary of dictionaries from a dictionary with keys that contain a hyphen. The first part of the key is the key of the new dictionary and the second part is the key of the inner dictionary.
    
    Parameters:
    dictionary (dict): The dictionary to split.
    """
    
    new_dict = {}
    
    for key in dictionary:
        
        first, last = key.split("-")[0], key.split("-")[-1]
        
        if first in new_dict:
            new_dict[first][last] = dictionary[key]
        else:
            new_dict[first] = {last: dictionary[key]}
    
    return new_dict


def create_pie_charts_root(dictionary, directory):
    """
    This function generates pie charts for data categorized in the different root sections: maturation, elongation, and cell division. 
    
    Parameters:
    dictionary (dict): The dictionary containing full name as the keys and pandas series as the values. The full names should end with -M, -E, or -CD for the three root sections (ex. 20240713-M). The pie charts would be then saved as 20240713-Pie.svg.
    directory (str): The directory to save the pie charts in.
    """
    
    if not os.path.exists(f"{directory}\\{PLOT_SAVE_FOLDER}"):
        os.makedirs(f"{directory}\\")
    
    names = create_sub_dictionaries(dictionary)
    
    # Loop through each name and generate pie charts for them
    for name in names:
        
        if len(names[name]) < 3:
            print(f"Skipping {name} as it does not have all the necessary data.")
            continue

        # Reorder dictionary
        names[name] = {k: names[name][k] for k in ["M", "E", "CD"]}
    
        create_pie_chart_set(names[name], f"{name}-Pie", f"{directory}\\{PLOT_SAVE_FOLDER}")    



def create_histogram_set(dictionary, filename, y_label, directory, x_label, bar_width = 20, legend_names = ["Cell Division", "Elongation", "Maturation"], x_axis_range=[0,500], colors=["red","cyan","yellow"]):
    """
    This function creates a set of three histograms.
    
    Parameters:
    dictionary (dict): The dictionary containing the data for the histograms. Should contain three elements.
    filename (str): The name of the file to save the histograms as.
    y_label (str): The label for the y-axis can be either "Count" or "Frequency".
    directory (str): The directory to save the histograms in.
    x_label (str): The label for the x-axis.
    bar_width (int): The width of the bars in the histogram.
    legend_names (list): The names of the legends for the histograms.
    x_axis_range (list): The range of the x-axis.
    colors (list): The list containing colors for each of the three histograms.
    """
    figure, axis = plt.subplots(3, 1, figsize=(8, 8)) 

    for i, (key, values) in enumerate(dictionary.items()):
        
        # Change the weights based on the y_label
        if(y_label == "Count"):
            weights = np.ones_like(values)
        elif(y_label == "Frequency"):
            weights = np.ones_like(values) / np.array(values).size
        
        axis[i].hist(values, bins=np.arange(x_axis_range[0], x_axis_range[1], bar_width), weights = weights , label=legend_names[i], color=colors[i], edgecolor = "black")
        
        axis[i].set_xlim(x_axis_range)
        axis[i].legend(loc="upper right")
        axis[i].set_xlabel(x_label)
        axis[i].set_ylabel(y_label)
    
    # Adjust spacing
    figure.tight_layout()
    
    # Adjust y axis
    plt.setp(axis, ylim=max([a.get_ylim() for a in axis.reshape(-1)]))
    
    plt.savefig(f"{directory}\\{PLOT_SAVE_FOLDER}\\{filename}.svg")


def create_histograms_root(dictionary, directory, x_axis_upper_bound, x_label="Breaking Force (pN)"):
    """
    This function creates histograms (one for count and one for frequency) for data categorized in the different root sections: maturation, elongation, and cell division. A final count and frequency histogram is also generated combining all the data.
    
    Parameters:
    dictionary (dict): The dictionary containing full name as the keys and pandas series as the values. The full names should end with -M, -E, or -CD for the three root sections (ex. 20240713-M).
    directory (str): The directory to save the histograms in.
    x_axis_upper_bound (int): The upper bound of the x-axis.
    x_label (str): The label for the x-axis.
    """
    
    if not os.path.exists(f"{directory}\\{PLOT_SAVE_FOLDER}"):
        os.makedirs(f"{directory}\\{PLOT_SAVE_FOLDER}")
    
    # Create dictionary to store combined histogram data
    final = {"CD": [], "E": [], "M": []}
    
    names = create_sub_dictionaries(dictionary)
    
    for name in names:
        
        if len(names[name]) < 3:
            print(f"Skipping {name} as it does not have all the necessary data.")
            continue
        
        # Reorder dictionary
        names[name] = {k: names[name][k] for k in ["M", "E", "CD"]}
        
        create_histogram_set(names[name], f"{name}-Count" , "Count", directory, x_label, x_axis_range=[0,x_axis_upper_bound])
        create_histogram_set(names[name], f"{name}-Frequency" , "Frequency", directory, x_label, x_axis_range=[0,x_axis_upper_bound])
        
        # Update combined data
        for key in names[name]:
            final[key] += names[name][key]
    
    create_histogram_set(final, "Final Frequency", "Frequency", directory, x_label, x_axis_range=[0,x_axis_upper_bound])
    create_histogram_set(final, "Final Count", "Count", directory, x_label, x_axis_range=[0,x_axis_upper_bound])
    