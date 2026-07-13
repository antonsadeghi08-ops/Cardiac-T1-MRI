import numpy as np
import os
import shutil as sh
import pydicom

#Fil jag vill walka
# "/Users/Anton_Sadeghi/Desktop/data_sorted/rawdata/patient20/ECV"

files_array = os.listdir("/Users/Anton_Sadeghi/Desktop/data_sorted/rawdata/patient20/ECV")
for x in range(len(files_array)):
    print(files_array[x])
