import tkinter as tk

class AFM_data_analyser(tk.Tk):
    def __init__(self):
        super().__init__()

        self.width = 500
        self.height = 500
        
        self.title("AFM Data Analyser")
        self.geometry(f"{self.width}x{self.height}")

        self.label = tk.Label(self, text="Select the type of data you would like to analyse:")
        self.label.grid(row=1, column=0, columnspan=5) 

        # Create bar
        
        
        
        self.button_frame = tk.Frame(self)
        self.button_frame.grid(row=0, column=0, columnspan=2) 
        
        self.button_frame_bg = tk.Frame(self.button_frame, bg="orange", width=self.width,height=40)
        self.button_frame_bg.grid(row=0, column=0,columnspan=2) 

        self.general_button = tk.Button(self.button_frame, text="General AFM Data", command=self.general)
        self.general_button.grid(row=0, column=0)

        self.chainfit_button = tk.Button(self.button_frame, text="Chain Fit Data", command=self.chainfit)
        self.chainfit_button.grid(row=0, column=1) 
        
        

        
        for i in range(5):
            for j in range(5):
                label = tk.Label(self, text=f'{i},{j}', bd=1, relief='solid')
                label.grid(row=i, column=j)

    def general(self):
        self.destroy()
        general_window = GeneralWindow()
        general_window.mainloop()

    def chainfit(self):
        self.destroy()
        chainfit_window = ChainFitWindow()
        chainfit_window.mainloop()

if __name__ == "__main__":
    app = AFM_data_analyser()
    app.mainloop()