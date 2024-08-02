import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

FILE_PATH = "MB_pH5,7,9_Ag50ul.xlsm"

if __name__ == "__main__":
    # Load the data
    df = pd.read_excel(FILE_PATH, header=30, skipfooter=5)

    df.plot(x='Wavelength', y=['A1', 'A2'], kind='line', xlabel='Wavelength (nm)', ylabel='Absorbance', title='UV-Vis Spectrum', xlim=(300,800))
    
    plt.legend(labels = ['Label 1', 'Label 2'])
    
    plt.show()
    
    
