import tkinter as tk
from tkinter import filedialog
import data_analysis as da
import graph

class AFMDataAnalyzer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.mode = "None"
        self.width = 500
        self.height = 500
        self.bar_height = 40
        self.page = None
        
        self.title("AFM Data Analyser")
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)
        
        # Creating Menubar 
        menubar = tk.Menu(self) 
        
        # Adding File Menu and commands 
        file = tk.Menu(menubar, tearoff = 0) 
        menubar.add_cascade(label ='File', menu = file) 
        file.add_command(label ='Analyse General', command = lambda: self.change_mode("General")) 
        file.add_command(label ='Analyse Chainfits', command = lambda: self.change_mode("Chain Fit")) 
        file.add_separator() 
        file.add_command(label ='Exit', command = self.destroy) 
        
        # Adding Help Menu 
        help_ = tk.Menu(menubar, tearoff = 0) 
        menubar.add_cascade(label ='Help', menu = help_) 
        help_.add_command(label ='Help', command = lambda: self.change_mode("Help")) 
        
        # display Menu 
        self.config(menu = menubar) 
        
        # Create Scrollbar
        self.canvas = tk.Canvas(self, width=self.width, height=self.height-self.bar_height)
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT,fill=tk.Y)
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # self.change_mode("Chain Fit")
        
    def change_mode(self, mode):
        
        if mode == self.mode:
            return
        
        if self.page:
            self.page.destroy()
            
        self.mode = mode
        match mode:
            case "General":
                self.page = GeneralAFM(self.canvas)
            case "Chain Fit":
                self.page = ChainFit(self.canvas)
            case "Help":
                self.page = Help(self.canvas)
            case _:
                raise ValueError("Invalid mode")
        
        self.canvas.create_window((0, 0), window=self.page, anchor='nw', height=800, width=self.width)

        self.canvas.config(scrollregion=self.canvas.bbox('all'))
        
        self.page.bind('<Enter>', self._bound_to_mousewheel)
        self.page.bind('<Leave>', self._unbound_to_mousewheel)

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

class Help(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.label = tk.Label(self, text="Help")
        self.label.pack()         
        self.text = tk.Text(self, height=38, width=50, wrap=tk.WORD)
        self.text.pack()

        
        text = """
General Mode: 
Clicking on the run button will filter out all the data with no interaction, and the units for adhesion and area will be changed to pN and aJ respectively. Only the adhesion and area columns are kept. When the save filtered data checkbox is enabled, it will save the filtered data in a folder called filtered_general_data, and when the save interaction count checkbox is enabled, it will save the interaction counts in a file called interaction_count.csv.

Chain Fit Mode:
Clicking on the run button will filter out all the data outside of the expected ranges, and it will adjust the units for bending length, contour length, residual RMS, and breaking force to pm, pm, pN, and pN respectively. The data will be saved in a folder called filtered_chain_fits_data when the save filtered data checkbox is enabled. Likewise breaking_forces.csv and count_num_fitting_segments.csv files will be generated when their respective checkboxes are enabled. 

As of now, the histogram and pie chart feature is only applicable to data collected studying the different root regions: maturation, elongation, and cell division. For successful graph generation, the file names must end with -M, -E, or -CD representing the three root sections (ex. 20240713-M.tsv).
        
        """

        self.text.insert(tk.END, text)
        
        self.text.config(state=tk.DISABLED)

class GeneralAFM(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.save_filtered_data = tk.BooleanVar()
        self.save_interaction_count = tk.BooleanVar()
        self.save_area_adhesion = tk.BooleanVar()
        
        self.columnconfigure(0, weight=1)

        self.elements = [
            tk.Label(self, text="Analyse General AFM Data"),
            FileSelector(self),
            DirectorySelector(self),
            InputBox(self, name="Min Position Threshold [nm]: ", default_value="300"),
            tk.Checkbutton(self, text = "Save Filtered Data", variable = self.save_filtered_data),
            tk.Checkbutton(self, text = "Save Interaction Count Data", variable = self.save_interaction_count),
            tk.Checkbutton(self, text = "Save Area and Adhesion Data", variable = self.save_area_adhesion),
            tk.Button(self, text="Run", command=self.run)
        ]
        
        for i in range(len(self.elements)):
            self.elements[i].grid(row=i, column=0)
            self.grid_rowconfigure(i, minsize=40)
    
    def run(self):
        files = self.elements[1].get_files()
        
        if len(files) == 0:
            tk.messagebox.showerror("Error", "No files selected.")
            return
        
        directory = self.elements[2].get_directory()
        
        min_position_threshold = float(self.elements[3].get_input())
        
        filtered_data, interaction_count_df = da.analyse_general(files, min_position_threshold)
        
        if self.save_filtered_data.get():
            da.save_filtered_dfs(filtered_data, f"{directory}\\filtered_general_data")
        
        if self.save_interaction_count.get():
            interaction_count_df.to_csv(f"{directory}\\interaction_count.csv", index=False)
        
        if self.save_area_adhesion.get():
            _, area_adhesion_df = da.compile_parameter(filtered_data, ["Area [aJ]", "Adhesion [pN]"])
            area_adhesion_df.to_csv(f"{directory}\\area_adhesion.csv", index=False)
        
class ChainFit(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.save_filtered_data = tk.BooleanVar()
        self.save_breaking_forces = tk.BooleanVar()
        self.save_breaking_forces_histograms = tk.BooleanVar()
        self.save_count_num_fitting_segments = tk.BooleanVar()
        self.save_fitting_segment_pie_charts = tk.BooleanVar()
        self.save_contour_length_differences = tk.BooleanVar()
        self.apply_filter = tk.BooleanVar(value=True)
        
        self.columnconfigure(0, weight=1)
        
        self.elements=[
            tk.Label(self, text="Analyse Chain Fit AFM Data"),
            FileSelector(self),
            DirectorySelector(self),
            tk.Checkbutton(self, text = "Filter Data", variable = self.apply_filter),
            InputBox(self, name="Max Bending Length [pm]: ", default_value="4000"),
            InputBox(self, name="Min Bending Length [pm]: ", default_value="20"),
            InputBox(self, name="Max Contour Length [nm]: ", default_value="5000"),
            InputBox(self, name="Min Contour Length [nm]: ", default_value="300"),
            InputBox(self, name="Max Residual RMS [pN]: ", default_value="25"),
            tk.Checkbutton(self, text = "Save Filtered Data", variable = self.save_filtered_data),
            tk.Checkbutton(self, text = "Save Breaking Forces Data", variable = self.save_breaking_forces),
            InputBox(self, name="X-Axis Upper Bound: ", default_value="500"),
            tk.Checkbutton(self, text = "Save Breaking Forces Histograms (Based on Root Regions)", variable = self.save_breaking_forces_histograms),
            tk.Checkbutton(self, text = "Save Number of Fitting Segments Data", variable = self.save_count_num_fitting_segments),
            tk.Checkbutton(self, text = "Save Fitting Segments Pie Charts (Based on Root Regions)", variable = self.save_fitting_segment_pie_charts),
            tk.Checkbutton(self, text = "Save Contour Length Differences", variable = self.save_contour_length_differences),
            tk.Button(self, text="Run", command=self.run)
        ]
        
        for i in range(len(self.elements)):
            self.elements[i].grid(row=i, column=0)
            self.grid_rowconfigure(i, minsize=40)
    
    def run(self):
        files = self.elements[1].get_files()
        
        if len(files) == 0:
            tk.messagebox.showerror("Error", "No files selected.")
            return
        
        directory = self.elements[2].get_directory()

        max_bending_length = float(self.elements[4].get_input())
        min_bending_length = float(self.elements[5].get_input())
        max_contour_length = float(self.elements[6].get_input())
        min_contour_length = float(self.elements[7].get_input())
        max_residual_rms = float(self.elements[8].get_input())
        
        filtered_data = da.analyse_chain_fit(files, max_bending_length, min_bending_length, max_contour_length, min_contour_length, max_residual_rms, apply_filter=self.apply_filter.get())
        
        if self.save_filtered_data.get():
            da.save_filtered_dfs(filtered_data, f"{directory}\\filtered_chain_fits_data")
        
        breaking_forces_dictionary, breaking_forces_df =da.compile_parameter(filtered_data, "Breaking Force [pN]")
        
        if self.save_breaking_forces.get():
            breaking_forces_df.to_csv(f"{directory}\\breaking_forces.csv", index=False)
        
        if self.save_breaking_forces_histograms.get():
            graph.create_histograms_root(breaking_forces_dictionary, f"{directory}\\graphs", float(self.elements[11].get_input()))
        
        count_num_fitting_segments_dictionary, count_num_fitting_segments_df = da.count_fitting_segments(filtered_data)

        if(self.save_count_num_fitting_segments.get()):
            count_num_fitting_segments_df.to_csv(f"{directory}\\count_num_fitting_segments.csv", index=False)
        
        if(self.save_fitting_segment_pie_charts.get()):
            graph.create_pie_charts_root(count_num_fitting_segments_dictionary, f"{directory}\\graphs")
        
        if self.save_contour_length_differences.get():
            contour_length_differences_data = da.get_contour_length_differences(filtered_data)
            da.save_filtered_dfs(contour_length_differences_data, f"{directory}\\filtered_chain_fits_data")
    
        
class FileSelector(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.vertical_scrollbar = tk.Scrollbar(self)
        self.vertical_scrollbar.grid(row=0, column=1, sticky='ns')

        self.horizontal_scrollbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.horizontal_scrollbar.grid(row=1, column=0, sticky='ew')

        self.list_box = tk.Listbox(self, yscrollcommand=self.vertical_scrollbar.set, 
                                   xscrollcommand=self.horizontal_scrollbar.set, height=5, width=50)
        self.list_box.grid(row=0, column=0, sticky='nsew')

        self.vertical_scrollbar.config(command=self.list_box.yview)
        self.horizontal_scrollbar.config(command=self.list_box.xview)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.file_button = tk.Button(self, text="Select Files", command=self.select_file)
        self.file_button.grid(row=2, column=0, columnspan=2)
        
    def select_file(self):
        files = filedialog.askopenfilenames(filetypes=[("File Types:", "*.tsv *.txt")])

        self.list_box.delete(0, tk.END)

        for file in files:
            self.list_box.insert(tk.END, file)
    
    def get_files(self):
        return self.list_box.get(0, tk.END)

class DirectorySelector(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.label = tk.Label(self, text="Output Directory: ")
        self.label.grid(row=0, column=0)
        
        self.entry = tk.Entry(self)
        self.entry.grid(row=0, column=1)
        self.entry.insert(0, '.')
        
        self.button = tk.Button(self, text="Select Directory", command=self.select_directory)
        self.button.grid(row=0, column=2)
        
    def select_directory(self):
        directory = filedialog.askdirectory()
        self.entry.delete(0, tk.END)
        self.entry.insert(0, directory)
        
    def get_directory(self):
        return self.entry.get()

class InputBox(tk.Frame):
    def __init__(self, *args, name="Input: ", default_value=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.label = tk.Label(self, text=name)
        self.label.grid(row=0, column=0)
        
        self.entry = tk.Entry(self)
        if default_value != None:
            self.entry.insert(0, default_value)
        self.entry.grid(row=0, column=1)
        
    def get_input(self):
        return self.entry.get()

if __name__ == "__main__":
    app = AFMDataAnalyzer()
    app.mainloop()