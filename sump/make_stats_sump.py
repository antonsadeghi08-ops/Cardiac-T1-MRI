# Tar en .dcm-fil och tar genomsnittet av värdena och omvandlar till en siffra.
# CSV'n ska innehålla bokstavligen all relevant info som kan behövas. 
# Analyze_stats.py ska sen ta en massa jävla korrelationer. Typ allt som kan behövas. 
# Poängen med den här är att skapan en ny CSV varje gång den runnas som skriver över den gamla

# SPARA SÄKERHETSKOPIOR NÄR JAG HAR ANVÄNDBAR DATA!!!

import pydicom
import numpy as np
import os
import csv



def load_dicom(path):
    ds = pydicom.dcmread(path)
    slope = float(getattr(ds, 'RescaleSlope', 1))
    intercept = float(getattr(ds, 'RescaleIntercept', 0))
    return ds, slope, intercept


def correction(ds, slope, intercept):
    raw_pixels = ds.pixel_array.astype(np.float32)
    return raw_pixels * slope + intercept

def dcm_to_array(path: str) -> np.ndarray:
    ds = pydicom.dcmread(path)
    ds, slope, intercept = load_dicom(path)

    pre_pixel_array = correction(ds, slope, intercept)

    pixel_array = pre_pixel_array.pixel_array 

    pixel_array.flatten()
    file_array = pixel_array.flatten()
    output_array = file_array[file_array != 0]

    return output_array

def get_stats(array):
    return np.mean(array), np.std(array)

def create_new_csv(path):
    csv_file_path = 'example.csv'
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)


def statistika():
    print("Vilken folder vill du statistika [url]")
    root = input()
    csv_path = f"{root}.csv"
    create_new_csv(path)
    for patient in range(55):
        for slice in range(5):
            for method in range(5):
                image_path = f"{root}/p{patient}/s{slice}/im/{method}.dcm"
                cropped_path = f"/Users/Anton_Sadeghi/Desktop/data_sorted/p{patient}/s{slice}/im_c/{method}.dcm"
                roi_path = f"/Users/Anton_Sadeghi/Desktop/data_sorted/p{patient}/s{slice}/im_i/{method}.dcm"
                ref_path = f"/Users/Anton_Sadeghi/Desktop/data_sorted/p{patient}/s{slice}/im_r/{method}.dcm"
                if os.path.exists(image_path) == True:
                    path = image_path
                    if os.path.exists(roi_path) == True:
                        mu_roi, sigma_roi = get_stats(dcm_to_array(roi_path))
                        if os.path.exists(ref_path) == True:
                            mu_ref, sigma_ref = get_stats(dcm_to_array(ref_path))
                            stats = [image_path, patient, slice, method, mu_roi, sigma_roi, mu_ref, sigma_ref]
                    #GÖR DET SOM BEHÖVER GÖRAS: LÄGG IN STATISTIKFAN i CSVn