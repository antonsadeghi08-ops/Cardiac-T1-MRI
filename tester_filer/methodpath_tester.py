import numpy as np
import os
import shutil as sh
import pydicom

def method(path):
    methods = ["ECV", "PSIR_phase", "LGE", "T1", "T1rho", "T2"]

    if methods[0] in path:
        return "ecv", 0
    elif methods[1] in path:
        return "lge", 1
    elif methods[2] in path:
        return "lge", 2
    elif methods[3] in path:        
        return "t1rho", 4 #KOLLA T1rho FÖRST FÖR ATT UNDVIKA ATT MISSA SUBSTRINGEN!
    elif methods[4] in path:
        return "t1", 3
    elif methods[5] in path:
        return "t2", 5
    else:
        print(f"ERROR! Method unintelligible in '{path}'")
        return None, -1      

root = "/Users/Anton_Sadeghi/Desktop/data_sorted/rawdata/patient22"
files_array = os.listdir(root)
for x in range(len(files_array)):
    print(files_array[x])
    file_name = f"{root}/{files_array[x]}"
    name, nr = method(file_name)
    print(f"Name: {name}, Nr: {nr}")

