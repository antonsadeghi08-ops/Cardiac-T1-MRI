

def path(patient, slice, step, method):
    root = "/Users/Anton_Sadeghi/Desktop/data_sorted"
    methods_array = ["ecv", "lge", "t1", "t1rho", "t2"]
    method_name = methods_array[method]
    path = f"{root}/p{patient}/s{slice}/{step}/{method_name}.dcm"
    return path

print(path(1, 2, "im", 2))