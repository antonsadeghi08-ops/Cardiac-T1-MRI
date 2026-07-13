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
    
    # Update header to match actual pixel data
    ds_out.Rows, ds_out.Columns = raw_output.shape
    ds_out.BitsAllocated = raw_output.dtype.itemsize * 8
    ds_out.BitsStored = ds_out.BitsAllocated
    ds_out.HighBit = ds_out.BitsAllocated - 1
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    ds_out.save_as(output_path, write_like_original=False)

# Generera en array med de patientnr som segmenteringen ska göras för. Printar detta i terminal for further reference.


def välj_patienter():
    print("Hur många munkar vill du hacka up? []")
    nr_patients = int(input())
    print("Vem är näst på munkklossen?")
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

def save_masks(viewer, new_mask_path, h, w, ds):
    layer_names = [layer.name for layer in viewer.layers]
    if "roi" not in layer_names or "ref" not in layer_names:
        print("Layers must be named 'roi' and 'ref' to save. Skipping save.")
        return False

    roi_mask = shapes_to_mask(viewer.layers['roi'], (h, w))
    ref_mask = shapes_to_mask(viewer.layers['ref'], (h, w))

    os.makedirs(new_mask_path, exist_ok=True)
    np.save(f"{new_mask_path}/roi.npy", roi_mask)
    np.save(f"{new_mask_path}/ref.npy", ref_mask)
    np.save(f"{new_mask_path}/pixel_spacing.npy", np.array(ds.PixelSpacing, dtype=float))
    print(f"Masks saved to {new_mask_path}")
    return True

def load_masks(viewer, mask_path, ds_new):
    roi_mask    = np.load(f"{mask_path}/roi.npy")
    ref_mask    = np.load(f"{mask_path}/ref.npy")
    old_spacing = np.load(f"{mask_path}/pixel_spacing.npy")
    new_spacing = np.array(ds_new.PixelSpacing, dtype=float)

    scale_row = old_spacing[0] / new_spacing[0]
    scale_col = old_spacing[1] / new_spacing[1]

    viewer.layers['roi'].data = mask_to_shapes(roi_mask, scale_row, scale_col)
    viewer.layers['ref'].data = mask_to_shapes(ref_mask, scale_row, scale_col)
    print(f"Preloaded masks from {mask_path}")


def mask_to_shapes(mask, scale_row=1.0, scale_col=1.0):
    contours = measure.find_contours(mask, level=0.5)
    shapes = []
    for contour in contours:
        scaled = contour * np.array([scale_row, scale_col])
        shapes.append(scaled)
    return shapes


def find_latest_mask(root, data, patient, slice, methods, method):
    # Walk backwards through methods to find the most recent saved mask
    for x in range(method + 1):
        candidate = f"{root}/{data}/p{patient}/s{slice}/im_i/masks/{methods[method - x]}"
        if os.path.exists(candidate):
            return candidate
    return None


def beta_segment (root, data, patient, slice, methods, method):
    input_path = f"{root}/{data}/p{patient}/s{slice}/im_c/{methods[method]}.dcm"

    if not os.path.exists(input_path):  # ← add this
        print(f"Skipping: {input_path} not found")
        return

    output_path_roi =f"{root}/{data}/p{patient}/s{slice}/im_i/{methods[method]}.dcm"
    output_path_ref =f"{root}/{data}/p{patient}/s{slice}/im_r/{methods[method]}.dcm"
    new_mask_roi_path = f"{root}/{data}/p{patient}/s{slice}/im_i/masks/{methods[method]}"
    new_mask_ref_path = f"{root}/{data}/p{patient}/s{slice}/im_r/masks/{methods[method]}"
    mask_path = find_latest_mask(root, data, patient, slice, methods, method)


    ds, slope, intercept = load_dicom(input_path)
    image_data = ensure_2d(to_t1rho(ds, slope, intercept))
    h, w = image_data.shape

    viewer = napari.Viewer()
    viewer.add_image(image_data, name=f"/p{patient}/s{slice}/im_c/{methods[method]}.dcm")
    viewer.add_shapes(name='roi',  shape_type='polygon',
        face_color='transparent', edge_color='blue', opacity=0.3)
    viewer.add_shapes(name='ref', shape_type='polygon',
        face_color='transparent', edge_color='yellow',   opacity=0.3)

    if mask_path is not None:
        load_masks(viewer, mask_path, ds)  

    @viewer.bind_key('k')
    def rotate_clockwise(viewer):
        image_data.data = np.rot90(image_data.data, k=-1)

    @viewer.bind_key('j')
    def rotate_counterclockwise(viewer):
        image_data.data = np.rot90(image_data.data, k=1)

    @viewer.bind_key('h')
    def flip_vertical(viewer):
        image_data.data = np.flipud(image_data.data)

    napari.run()

    layer_names = [layer.name for layer in viewer.layers]
    if "roi" not in layer_names or "ref" not in layer_names:
        print("Layers not named 'roi'/'ref' — skipping save and mask.")
        return

    roi_mask  = shapes_to_mask(viewer.layers['roi'],  (h, w))
    ref_mask = shapes_to_mask(viewer.layers['ref'], (h, w))

    background_value = image_data.min()
    masked_image_roi = image_data.copy()
    masked_image_ref = image_data.copy()
    masked_image_roi[~roi_mask]  = background_value   
    masked_image_ref[~ref_mask]  = background_value   

    raw_output_roi = to_raw_integers(masked_image_roi, ds, slope, intercept)
    raw_output_ref = to_raw_integers(masked_image_ref, ds, slope, intercept)
    save_dicom(ds, raw_output_roi, slope, intercept, output_path_roi)
    save_dicom(ds, raw_output_ref, slope, intercept, output_path_ref)
    save_masks(viewer, new_mask_roi_path, h, w, ds)  
    save_masks(viewer, new_mask_ref_path, h, w, ds) 




def segmentor_beta(patient_range):
    methods = ["ecv", "lge", "t1", "t1rho", "t2"]
    for patient in patient_range:
        for slice in range(5):
            for method in range(len(methods)):
                beta_segment(root, data, patient, slice, methods, method)





pat_len = välj_patienter()
segmentor_beta(pat_len)