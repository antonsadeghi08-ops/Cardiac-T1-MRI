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


root = "/Users/Anton_Sadeghi/Desktop"
data = "data_sorted"


# Skapar en folder-struktur
def create_sorted_folder():
    for patient in range(4): #JUSTERAT FÖR 3 ST PATIENTER --- ÄNDRA NÄR JAG HAR HELA DATASETET
        for slice in range(5): #Slices
            for method in range(4):
                steps = ["im", "im_c", "im_i", "im_r"]

                path = f"{root}/{data}/p{patient}/s{slice}/{steps[int(method)]}"

                if os.path.exists(path):
                    sh.rmtree(path)     #Skriver över ifall pathen redan existerar :)
                os.makedirs(path)


destpath = "/Users/Anton_Sadeghi/Desktop/data_sorted/rawdata"
root_new = "/Users/Anton_Sadeghi/Desktop/data_sorted/"

def importdatato_sortfolder():
    if os.path.exists(destpath):
        sh.rmtree(destpath)     # Skriv EFTER path har definerats men INNAN någon data flyttats dit
    print("Input raw data URL:")
    rawdata = sh.copytree(input(), destpath) #FLyttar den foldern man inputar till den vi nyss skapat med create_sorted_folder()



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
        return "t1rho", 4 #KOLLA T1rho FÖRST FÖR ATT UNDVIKA ATT MISSA SUBSTRINGEN!
    elif methods[3] in path:
        return "t1", 3
    elif methods[5] in path:
        return "t2", 5
    else:
        print(f"ERROR! Method unintelligible in '{path}'")
        return None, -1      


def slice(nr):          #ANTAGLIGEN felaktig :()
    if nr < 2:
        slice_name = "s1"
    elif nr < 4:
        slice_name = "s2"
    elif nr < 6:
        slice_name = "s3"
    elif nr < 8:
        slice_name = "s4"
    elif nr < 10:
        slice_name = "s5"
    return slice_name

def current_folder(patient, method, file):
    methods = ["ECV", "LGE", "T1", "T1rho", "T2"]     
    patient_name = f"patient{patient +20}"     #+20-termen är för att vi för tillfället börjar på patient 20
    if method == 1 :
        current_folder_test_lge = f"{destpath}/{patient_name}/LGE"
        current_folder_test_psir = f"{destpath}/{patient_name}/PSIR_phase"
        if os.path.exists(current_folder_test_lge):
            current_path = current_folder_test_lge
        elif os.path.exists(current_folder_test_psir):
            current_path = current_folder_test_psir
        else: 
            print("ERROR: No LGE-folder")
    else: 
        method_name = methods[method]
        current_path = f"{destpath}/{patient_name}/{method_name}"
    return current_path

# Nestad for-loop som, i det innersta steget, identifierar .dcm-filens slice & metod, skapar en destpath, och flyttar fil.
def sortdata_insortfolder():
    for p in range(3): #justera sen när jag har fler patienter
        for m in range(5):
            for f in range(10):
                cf = current_folder(p, m, f)
                if os.path.exists(cf):
                    current_folder_dir = cf
                    files_array = os.listdir(current_folder_dir)
                    current_path = os.path.join(current_folder_dir, files_array[f])
                    if is_bw(current_path) == True:
                        patient = f"p{p}"
                        slices = slice(f)
                        step = "im"
                        method_name, method_nr = method(current_path)
                        new_path = f"{root_new}/{patient}/{slices}/{step}/{method_name}.dcm"
                        print(new_path)
                
                #+20-termen är för att vi börjar på patient 20
    # Radera foldern som skapas i importdatato_sortfolder() här





create_sorted_folder()
importdatato_sortfolder()
sortdata_insortfolder()