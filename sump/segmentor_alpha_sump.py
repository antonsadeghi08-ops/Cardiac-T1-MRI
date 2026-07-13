import pydicom
import napari
import numpy as np
from skimage.draw import polygon
import os
from skimage import measure


root = "/Users/Anton_Sadeghi/Desktop"
data = "data_sorted"

# Läser en DICOM-fil och returnerar (dataset, slope, intercept).
def load_dicom(path):
    ds = pydicom.dcmread(path)
    slope = float(getattr(ds, 'RescaleSlope', 1))
    intercept = float(getattr(ds, 'RescaleIntercept', 0))
    return ds, slope, intercept

 # Konverterar råa pixelvärden till T1-rho-värden med slope/intercept.


def to_t1rho(ds, slope, intercept):
    raw_pixels = ds.pixel_array.astype(np.float32)
    return raw_pixels * slope + intercept

 # Omvandlar T1-rho-värden tillbaka till råa heltal (inverterad rescaling).


def to_raw_integers(t1rho_image, ds, slope, intercept):
    raw = (t1rho_image - intercept) / slope
    raw = np.clip(raw, 0, np.iinfo(ds.pixel_array.dtype).max)
    return raw.astype(ds.pixel_array.dtype)

# Konverterar ett napari shapes-lager till en binär mask.


def shapes_to_mask(shapes_layer, image_shape):
    mask = np.zeros(image_shape, dtype=bool)
    for shape_data in shapes_layer.data:
        rr, cc = polygon(shape_data[:, 0], shape_data[:, 1], image_shape)
        mask[rr, cc] = True
    return mask

 # Sparar ett modifierat pixel-array som ny DICOM-fil.


def save_dicom(ds_original, raw_output, slope, intercept, output_path):
    ds_out = ds_original.copy()
    ds_out.PixelData = raw_output.tobytes()
    ds_out.RescaleSlope = slope
    ds_out.RescaleIntercept = intercept
    ds_out.save_as(output_path)

# Generera en array med de patientnr som segmenteringen ska göras för. Printar detta i terminal for further reference.


def välj_patienter():
    print("Hur många gubbar vill du hacka up? []")
    nr_patients = int(input())
    print("Vem är näst på huggklossen?")
    first_patient = int(input())
    patient_range = list(range(first_patient, (first_patient+nr_patients)))
    return patient_range


# /Users/Anton_Sadeghi/Desktop/data_sorted/p0/s0/im/ecv.dcm

# Ger pathnamnet från indexen jag tänker loopa över
def path(patient, slice, step, method):
    root = "/Users/Anton_Sadeghi/Desktop/data_sorted"
    methods_array = ["ecv", "lge", "t1", "t1rho", "t2"]
    method_name = methods_array[method]
    path = f"{root}/p{patient}/s{slice}/{step}/{method_name}.dcm"
    return path

def ensure_2d(image_data):
    if image_data.ndim == 2:
        return image_data
    elif image_data.ndim == 3:
        return image_data[:, :, 0] if image_data.shape[0] > image_data.shape[2] else image_data[0]
    else:
        return image_data.squeeze()

def save_masks(viewer, new_mask_path, h, w):
    # Require layers to be named "endo" and "epi"
    layer_names = [layer.name for layer in viewer.layers]
    if "endo" not in layer_names or "epi" not in layer_names:
        print("Layers must be named 'endo' and 'epi' to save. Skipping save.")
        return False

    epi_mask  = shapes_to_mask(viewer.layers['epi'],  (h, w))
    endo_mask = shapes_to_mask(viewer.layers['endo'], (h, w))

    os.makedirs(new_mask_path, exist_ok=True)
    np.save(f"{new_mask_path}/epi.npy",  epi_mask)
    np.save(f"{new_mask_path}/endo.npy", endo_mask)
    print(f"Masks saved to {new_mask_path}")
    return True

def mask_to_shapes(mask):
    """
    Converts a binary 2D mask to a list of polygon shapes compatible with napari.
    """
    contours = measure.find_contours(mask, level=0.5)
    shapes = []
    for contour in contours:
        # napari expects (row, col) which is what find_contours already returns
        shapes.append(contour)
    return shapes


def load_masks(viewer, mask_path):
    epi_mask  = np.load(f"{mask_path}/epi.npy")
    endo_mask = np.load(f"{mask_path}/endo.npy")

    # Convert masks back to shapes and preload into viewer
    viewer.layers['epi'].data  = mask_to_shapes(epi_mask)
    viewer.layers['endo'].data = mask_to_shapes(endo_mask)
    print(f"Preloaded masks from {mask_path}")


def find_latest_mask(root, data, patient, slice, methods, method):
    # Walk backwards through methods to find the most recent saved mask
    for x in range(method + 1):
        candidate = f"{root}/{data}/p{patient}/s{slice}/im_c/masks/{methods[method - x]}"
        if os.path.exists(candidate):
            return candidate
    return None


def alpha_segment (root, data, patient, slice, methods, method):
    input_path = f"{root}/{data}/p{patient}/s{slice}/im/{methods[method]}.dcm"
    output_path =f"{root}/{data}/p{patient}/s{slice}/im_c/{methods[method]}.dcm"
    new_mask_path = f"{root}/{data}/p{patient}/s{slice}/im_c/masks/{methods[method]}"
    for x in range(len(methods)):
        latest_mask_path = f"{root}/{data}/p{patient}/s{slice}/im_c/masks/{methods[method - x]}"
        if os.path.exists(latest_mask_path):
            return latest_mask_path
        else:
            latest_mask_path = None

    ds, slope, intercept = load_dicom(input_path)
    image_data = to_t1rho(ds, slope, intercept)
    image_data = ensure_2d(to_t1rho(ds, slope, intercept))
    h, w = image_data.shape


    ds, slope, intercept = load_dicom(input_path)
    image_data = to_t1rho(ds, slope, intercept)
    image_data = ensure_2d(to_t1rho(ds, slope, intercept))
    h, w = image_data.shape


    viewer = napari.Viewer()
    viewer.add_image(image_data, name=f"/p{patient}/s{slice}/im/{methods[method]}.dcm")
    viewer.add_shapes(name='epi',  shape_type='polygon',
    face_color='transparent', edge_color='green', opacity=0.3)
    viewer.add_shapes(name='endo', shape_type='polygon',
    face_color='transparent', edge_color='red',   opacity=0.3)


    napari.run()

    epi_mask  = shapes_to_mask(viewer.layers['epi'],  (h, w))
    endo_mask = shapes_to_mask(viewer.layers['endo'], (h, w))

    background_value = image_data.min()
    masked_image = image_data.copy()
    masked_image[~epi_mask]  = background_value   # Utanför epi blir blank
    masked_image[endo_mask]  = background_value   # Innanför endo blir blank

    raw_output = to_raw_integers(masked_image, ds, slope, intercept)
    save_dicom(ds, raw_output, slope, intercept, output_path)








def segmentor_alpha(patient_range):
    for patient in patient_range:
        for slice in range(5):
            slice_path = f"{root}/{data}/p{patient}/s{slice}"
            methods_len = len(os.listdir(slice_path))
            for method in range(methods_len):
                methods = ["ecv", "lge", "t1", "t1rho", "t2"]
                alpha_segment(root, data, patient, slice, methods, method)





pat_len = välj_patienter()
segmentor_alpha(pat_len)