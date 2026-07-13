# Tar en .dcm-fil och tar genomsnittet av värdena och omvandlar till en siffra.
# CSV'n ska innehålla bokstavligen all relevant info som kan behövas. 
# Analyze_stats.py ska sen ta en massa jävla korrelationer. Typ allt som kan behövas. 
# Poängen med den här är att skapa en ny CSV varje gång den runnas som skriver över den gamla
 
# SPARA SÄKERHETSKOPIOR NÄR JAG HAR ANVÄNDBAR DATA!!!

# /Users/Anton_Sadeghi/Desktop/data_sorted
 
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
    ds, slope, intercept = load_dicom(path)

    pixel_array = correction(ds, slope, intercept)
 
    file_array = pixel_array.flatten()
    output_array = file_array[file_array != 0]
 
    return output_array
 
 
def get_stats(array):
    return np.mean(array), np.std(array)
 
 
def create_new_csv(csv_path):
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            'image_path', 'patient', 'slice', 'method',
            'mu_roi', 'sigma_roi', 'mu_ref', 'sigma_ref'
        ])
 
 
def append_row_to_csv(csv_path, row):
    with open(csv_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)
 
 # /Users/Anton_Sadeghi/Desktop/data_sorted
 # /Users/Anton_Sadeghi/Desktop/data_sorted_save_26-6-26
 
def statistika():
    print("Vilken folder vill du statistika [url]")
    root = input()
    csv_path = f"{root}.csv"
 
    create_new_csv(csv_path)
    methods = ["ecv", "lge", "t1", "t1rho", "t2"]
    for patient in range(55):
        for slice in range(5):
            for method in range(len(methods)):
                image_path = f"{root}/p{patient}/s{slice}/im/{methods[method]}.dcm"
                roi_path   = f"{root}/p{patient}/s{slice}/im_i/{methods[method]}.dcm"
                ref_path   = f"{root}/p{patient}/s{slice}/im_r/{methods[method]}.dcm"

                print(f"Letar efter: {image_path}")
                print(f"Finns: {os.path.exists(image_path)}") 
 
                if not os.path.exists(image_path):
                    continue
 
                mu_roi = sigma_roi = mu_ref = sigma_ref = None
 
                if os.path.exists(roi_path):
                    roi_array = dcm_to_array(roi_path)
                    mu_roi, sigma_roi = get_stats(roi_array)
 
                if os.path.exists(ref_path):
                    ref_array = dcm_to_array(ref_path)
                    mu_ref, sigma_ref = get_stats(ref_array)
 
                stats = [image_path, patient, slice, method,
                         mu_roi, sigma_roi, mu_ref, sigma_ref]
                append_row_to_csv(csv_path, stats)
 
 
statistika()
 

# /Users/Anton_Sadeghi/Desktop/data_sorted