import pydicom
import numpy as np


def dcm_to_array(path: str) -> np.ndarray:
    ds = pydicom.dcmread(path)

    pixel_array = ds.pixel_array 
    return pixel_array.flatten() # Tar bort dimension och ger bara en lång lista på alla pixelvärden.

path = "/Users/Anton_Sadeghi/Desktop/data_sorted/p0/s0/im_c/t1rho.dcm" # BAra för att testa den här filen

file_array = dcm_to_array(path)
output_array = file_array[file_array != 0]
print(output_array)


