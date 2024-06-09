import tkinter as tk
import data_analysis as da

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

        # Create bar
        self.button_frame = tk.Frame(self)
        self.button_frame.pack()
        
        self.button_frame_bg = tk.Frame(self.button_frame, bg="orange", width=self.width,height=self.bar_height)
        self.button_frame_bg.grid(row=0, column=0,columnspan=2) 

        self.general_button = tk.Button(self.button_frame, text="General AFM Data", command=lambda: self.change_mode("General"))
        self.general_button.grid(row=0, column=0)

        self.chainfit_button = tk.Button(self.button_frame, text="Chain Fit Data", command=lambda: self.change_mode("Chain Fit"))
        self.chainfit_button.grid(row=0, column=1)
        
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
            case _:
                raise ValueError("Invalid mode")
        
        self.canvas.create_window((0, 0), window=self.page, anchor='nw', height=700, width=self.width)

        self.canvas.config(scrollregion=self.canvas.bbox('all'))
        
        self.page.bind('<Enter>', self._bound_to_mousewheel)
        self.page.bind('<Leave>', self._unbound_to_mousewheel)

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                

class GeneralAFM(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
                
        self.label = tk.Label(self, text="General AFM Data")
        self.columnconfigure(0, weight=1)
        self.label.grid(row=0, column=0)
        
        self.file_selector = FileSelector(self)
        self.file_selector.grid(row=1, column=0)
        
        self.directory_selector = DirectorySelector(self)
        self.directory_selector.grid(row=3, column=0)
        
        self.input_min_position_threshold = InputBox(self, name="Min Position Threshold [nm]: ", default_value="300e-9")
        self.input_min_position_threshold.grid(row=4, column=0)
        
        self.analyze_button = tk.Button(self, text="Filter Data", command=self.analyze_data)
        self.analyze_button.grid(row=5, column=0)
        
        for i in range(5):
            self.grid_rowconfigure(i, minsize=40)
    
    def analyze_data(self):
        files = self.file_selector.get_files()
        
        if len(files) == 0:
            tk.messagebox.showerror("Error", "No files selected.")
            return
        
        directory = self.directory_selector.get_directory()
        
        min_position_threshold = float(self.input_min_position_threshold.get_input())
        
        self.filtered_data = da.analyze_general(files, directory, min_position_threshold)
        
class ChainFit(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.filtered_data = None
        self.breaking_forces = None
        
        self.label = tk.Label(self, text="Chain Fit AFM Data")
        self.columnconfigure(0, weight=1)
        self.label.grid(row=0, column=0)
        
        self.file_selector = FileSelector(self)
        self.file_selector.grid(row=1, column=0)
        
        self.directory_selector = DirectorySelector(self)
        self.directory_selector.grid(row=3, column=0)
        
        self.input_max_bending_length = InputBox(self, name="Max Bending Length [pm]: ", default_value="4000")
        self.input_max_bending_length.grid(row=4, column=0)
        
        self.input_min_bending_length = InputBox(self, name="Min Bending Length [pm]: ", default_value="20")
        self.input_min_bending_length.grid(row=5, column=0)
        
        self.input_max_contour_length = InputBox(self, name="Max Contour Length [nm]: ", default_value="5000")
        self.input_max_contour_length.grid(row=6, column=0)
        
        self.input_min_contour_length = InputBox(self, name="Min Contour Length [nm]: ", default_value="300")
        self.input_min_contour_length.grid(row=7, column=0)
        
        self.input_max_residual_rms = InputBox(self, name="Max Residual RMS [pN]: ", default_value="25")
        self.input_max_residual_rms.grid(row=8, column=0)
        
        self.filter_button = tk.Button(self, text="Filter Data", command=self.filter_data)
        self.filter_button.grid(row=9, column=0)
        
        self.input_x_axis_upper_bound = InputBox(self, name="X-Axis Upper Bound: ", default_value="500")
        self.input_x_axis_upper_bound.grid(row=10, column=0)
        
        self.graph_button = tk.Button(self, text="Save Breaking Force Graphs", command=self.create_graphs)
        self.graph_button.grid(row=11, column=0)
        
        for i in range(12):
            self.grid_rowconfigure(i, minsize=40)
    
    def filter_data(self):
        files = self.file_selector.get_files()
        
        if len(files) == 0:
            tk.messagebox.showerror("Error", "No files selected.")
            return
        
        directory = self.directory_selector.get_directory()

        max_bending_length = float(self.input_max_bending_length.get_input())
        min_bending_length = float(self.input_min_bending_length.get_input())
        max_contour_length = float(self.input_max_contour_length.get_input())
        min_contour_length = float(self.input_min_contour_length.get_input())
        max_residual_rms = float(self.input_max_residual_rms.get_input())
        
        self.filtered_data = da.analyze_chain_fit(files, directory, max_bending_length, min_bending_length, max_contour_length, min_contour_length, max_residual_rms)
    
        self.breaking_forces = da.compile_parameter(self.filtered_data, directory, "Breaking Force [pN]", "breaking_forces")
    
    def create_graphs(self):
        if self.breaking_forces == None:
            tk.messagebox.showerror("Error", "Need to filter data first.")
            return
        
        da.create_histograms(self.breaking_forces, self.directory_selector.get_directory(), float(self.input_x_axis_upper_bound.get_input()))
        
        
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
        files = tk.filedialog.askopenfilenames(filetypes=[("File Types:", "*.tsv *.txt")])

        self.list_box.delete(0, tk.END)

        for file in files:
            self.list_box.insert(tk.END, file)
        
        # Reset master variables
        self.master.filtered_data = None
        self.master.breaking_forces = None
    
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
        directory = tk.filedialog.askdirectory()
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