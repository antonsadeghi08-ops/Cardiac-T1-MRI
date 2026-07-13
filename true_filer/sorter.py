# Riktiga sortern (Jippiiii)
# 100% Clanker free!!!
# "This code is written entirely with the use of human stupidity"
import numpy as np
import os
import shutil as sh
import pydicom


# /Users/Anton_Sadeghi/Desktop/anton_rawdata/       (halv-riktig)
# /Users/Anton_Sadeghi/Desktop/till_anton           (test)
# /Users/Anton_Sadeghi/Desktop/data_sorted/rawdata  (Sorterad datafolder, andvänds i nästa funktion)
# /Users/Anton_Sadeghi/Desktop/rawdata_final


root = "/Users/Anton_Sadeghi/Desktop"
data = "data_sorted"


# Skapar en folder-struktur
def create_sorted_folder():
    for patient in range(55):
        for slice in range(5):  # Slices
            for method in range(5):
                steps = ["im", "im_c", "im_d", "im_i", "im_r"]

                path = f"{root}/{data}/p{patient}/s{slice}/{steps[method]}"

                if os.path.exists(path):
                    # Skriver över ifall pathen redan existerar :)
                    sh.rmtree(path)
                os.makedirs(path)


destpath = "/Users/Anton_Sadeghi/Desktop/data_sorted/rawdata"
root_new = "/Users/Anton_Sadeghi/Desktop/data_sorted/"


def importdatato_sortfolder():
    if os.path.exists(destpath):
        # Skriv EFTER path har definerats men INNAN någon data flyttats dit
        sh.rmtree(destpath)
    print("Input raw data URL:")
    # FLyttar den foldern man inputar till den vi nyss skapat med create_sorted_folder()
    rawdata = sh.copytree(input(), destpath)


# Kollar om en given .dcm-fil är svartvit eller i färg. Returnerar True om BW, False om färg.
def is_bw(dcm_path: str) -> bool:
    ds = pydicom.dcmread(dcm_path)
    photometric = ds.PhotometricInterpretation
    return photometric in ("MONOCHROME1", "MONOCHROME2")


def method(path):
    methods = ["ECV", "PSIR_phase", "LGE", "T1", "T1rho", "T2"]

    if methods[0] in path:
        return "ecv", 0
    elif methods[1] in path:
        return "lge", 1
    elif methods[2] in path:
        return "lge", 1
    elif methods[4] in path:
        return "t1rho", 4  # KOLLA T1rho FÖRST FÖR ATT UNDVIKA ATT MISSA SUBSTRINGEN!
    elif methods[3] in path:
        return "t1", 3
    elif methods[5] in path:
        return "t2", 5
    else:
        print(f"ERROR! Method unintelligible in '{path}'")
        return None, -1


def current_folder(patient, method_nr, file):
    methods = ["ECV", "LGE", "LGE", "T1", "T1rho", "T2"]
    # +20-termen är för att vi börjar på patient 20
    patient_name = f"patient{patient + 17}"

    if method_nr == 1 or method_nr == 2:
        for folder_name in ["LGE", "PSIR_phase"]:
            path = f"{destpath}/{patient_name}/{folder_name}"
            if os.path.exists(path):
                return path
        print(f"ERROR: No LGE or PSIR_phase folder for {patient_name}")
        return None
    else:
        method_name = methods[method_nr]
        current_path = f"{destpath}/{patient_name}/{method_name}"
        return current_path


# Nestad for-loop som, i det innersta steget, identifierar .dcm-filens slice & metod, skapar en destpath, och flyttar fil.
def sortdata_insortfolder():
    for p in range(55):  # justera sen när jag har fler patienter
        for m in [0, 1, 3, 4, 5]:
            for f in range(10):
                cf = current_folder(p, m, f)
                if cf is None or not os.path.exists(cf):
                    continue
                if os.path.exists(cf):
                    current_folder_dir = cf
                    files_array = os.listdir(current_folder_dir)
                    if f >= len(files_array):
                        continue
                    current_path = os.path.join(
                        current_folder_dir, files_array[f])
                    if is_bw(current_path) == True:
                        patient = f"p{p}"
                        step = "im"
                        method_name, method_nr = method(current_path)
                        new_path = None
                        for x in range(5):
                            new_path_test = f"{root_new}/{patient}/s{x}/{step}/{method_name}.dcm"
                            if os.path.exists(new_path_test) == False:
                                new_path = new_path_test
                                sh.copy2(current_path, new_path)
                                break
                        if new_path:
                            print(new_path)
                        else:
                            print(
                                f"ERROR! No matching path for {patient}, {method_name}")

    # Radera foldern som skapas i importdatato_sortfolder() här


create_sorted_folder()
importdatato_sortfolder()
sortdata_insortfolder()


# /Users/Anton_Sadeghi/Desktop/rawdata_final