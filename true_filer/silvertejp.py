# Tar masker från min save-fil:
# /Users/Anton_Sadeghi/Desktop/data_sorted_save_29-6-26
# ...och lägger in dem i den nya sorterade data_sorted foldern (utan färgbilder!!!!)

import os
import shutil as sh

root = "/Users/Anton_Sadeghi/Desktop"
data_save = "data_sorted_save_29-6-26"
data_destination = "data_sorted"

def fixa_allt():
    methods = ["ecv", "lge", "t1", "t1rho", "t2"]
    for patient in range(50):
        for slice in range(5):
            for method in range(len(methods)):
                input_donut_path = f"{root}/{data_save}/p{patient}/s{slice}/im_c/{methods[method]}.dcm"
                destination_donut_path = f"{root}/{data_destination}/p{patient}/s{slice}/im_c/{methods[method]}.dcm"
                input_ref_path = f"{root}/{data_save}/p{patient}/s{slice}/im_r/{methods[method]}.dcm"
                input_roi_path = f"{root}/{data_save}/p{patient}/s{slice}/im_i/{methods[method]}.dcm"
                destination_ref_path = f"{root}/{data_destination}/p{patient}/s{slice}/im_r/{methods[method]}.dcm"
                destination_roi_path = f"{root}/{data_destination}/p{patient}/s{slice}/im_i/{methods[method]}.dcm"
                if os.path.exists(input_ref_path) == True:
                    new_ref_path = input_ref_path
                    sh.copy2(new_ref_path, destination_ref_path)
                if os.path.exists(input_roi_path) == True:
                    new_roi_path = input_roi_path
                    sh.copy2(new_roi_path, destination_roi_path)
                if os.path.exists(input_donut_path) == True:
                    new_donut_path = input_donut_path
                    sh.copy2(new_donut_path, destination_donut_path)


fixa_allt()

