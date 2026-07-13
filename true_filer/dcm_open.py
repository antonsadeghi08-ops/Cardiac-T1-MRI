# Testa att importera dicom och öppna en bild från till_anton
# Exempelbild
# # Slope resclae & intercept ( Be att använda)


import matplotlib as plt
import pydicom
import pydicom.data
import napari
import numpy as np
from skimage.draw import polygon


# Läs av DICOM-filen
print("Input .dcm file path")
dcm_test = str(input())
ds = pydicom.dcmread(dcm_test)

# Extrahera pixel-array
image_data = ds.pixel_array

# öppna Napari
viewer = napari.Viewer()
viewer.add_image(image_data)


napari.run()

# /Users/Anton_Sadeghi/Desktop/data_sorted/p0/s2/im/t1.dcm
# /Users/Anton_Sadeghi/Desktop/anton_rawdata/patient20/ECV/_.MR.Klinik_Kliniska.47465.1.2026.06.22.18.41.59.204.76781131.dcm
# /Users/Anton_Sadeghi/Desktop/data_sorted/p1/s0/im_c/ecv.dcm
# /Users/Anton_Sadeghi/Desktop/data_sorted/p0/s0/im_c/ecv.dcm

# /Users/Anton_Sadeghi/Desktop/data_sorted/p3/s0/im_i/ecv.dcm
# /Users/Anton_Sadeghi/Desktop/rawdata_final/patient20/ECV/_.MR.Klinik_Kliniska.47465.1.2026.06.22.18.41.59.204.76781131.dcm
# /Users/Anton_Sadeghi/Desktop/rawdata_final/patient20/ECV/_.MR.Klinik_Kliniska.47465.1.2026.06.22.18.41.59.204.76781120.dcm
# /Users/Anton_Sadeghi/Desktop/data_sorted/p3/s0/im/ecv.dcm
# /Users/Anton_Sadeghi/Desktop/data_sorted_save_30-6-26/p3/s4/im_c/t1rho.dcm
# /Users/Anton_Sadeghi/Desktop/data_sorted_save_30_6_26/p3/s4/im_c/t1rho.dcm
# /Users/Anton_Sadeghi/Downloads/IM-0001-0001.dcm
# /Users/Anton_Sadeghi/Desktop/data_sorted/p8/s1/im_c/ecv.dcm
