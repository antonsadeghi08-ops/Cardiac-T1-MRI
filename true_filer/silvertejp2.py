# Tar cropped från min save mellan p0 och p3 och lägger in dem i nya data_saved så att jag inte har en massa skit som inte ska vara där

import os
import shutil as sh

root = "/Users/Anton_Sadeghi/Desktop"
data_save = "data_sorted_save_30-6-26"
data_destination = "data_sorted"

def fixa_allt():
    methods = ["ecv", "lge", "t1", "t1rho", "t2"]
    for patient in range(4):
        for slice in range(5):
            for method in range(len(methods)):
                input_donut_path = f"{root}/{data_save}/p{patient}/s{slice}/im_c/{methods[method]}.dcm"
                destination_donut_path = f"{root}/{data_destination}/p{patient}/s{slice}/im_c/{methods[method]}.dcm"
                print(destination_donut_path)
                print(input_donut_path)
                if os.path.exists(input_donut_path) == True:
                    new_donut_path = input_donut_path
                    sh.copy2(new_donut_path, destination_donut_path)
                    print(destination_donut_path)

fixa_allt()