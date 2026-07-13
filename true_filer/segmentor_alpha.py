# display_image = rotate_if_needed(image_data, methods[method])

import pydicom
import napari
import numpy as np
from skimage.draw import polygon
import os
from skimage import measure


root = "/Users/Anton_Sadeghi/Desktop"
data = "data_sorted"


def load_dicom(path):
    ds = pydicom.dcmread(path)
    slope = float(getattr(ds, 'RescaleSlope', 1))
    intercept = float(getattr(ds, 'RescaleIntercept', 0))
    return ds, slope, intercept

def to_t1rho(ds, slope, intercept):
    raw_pixels = ds.pixel_array.astype(np.float32)
    return raw_pixels * slope + intercept


def to_raw_integers(t1rho_image, ds, slope, intercept):
    raw = (t1rho_image - intercept) / slope
    raw = np.clip(raw, 0, np.iinfo(ds.pixel_array.dtype).max)
    return raw.astype(ds.pixel_array.dtype)


def shapes_to_mask(shapes_layer, image_shape):
    mask = np.zeros(image_shape, dtype=bool)
    for shape_data in shapes_layer.data:
        rr, cc = polygon(shape_data[:, 0], shape_data[:, 1], image_shape)
        mask[rr, cc] = True
    return mask


def save_dicom(ds_original, raw_output, slope, intercept, output_path):
    ds_out = ds_original.copy()
    ds_out.PixelData = raw_output.tobytes()
    ds_out.RescaleSlope = slope
    ds_out.RescaleIntercept = intercept
    ds_out.Rows, ds_out.Columns = raw_output.shape
    ds_out.BitsAllocated = raw_output.dtype.itemsize * 8
    ds_out.BitsStored = ds_out.BitsAllocated
    ds_out.HighBit = ds_out.BitsAllocated - 1
    ds_out.SamplesPerPixel = 1                   
    ds_out.PhotometricInterpretation = "MONOCHROME2" 
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    ds_out.save_as(output_path, enforce_file_format=False)

def välj_patienter():
    print("Hur många gubbar vill du hacka up? []")
    nr_patients = int(input())
    print("Vem är näst på huggklossen?")
    first_patient = int(input())
    patient_range = list(range(first_patient, (first_patient + nr_patients)))
    return patient_range


def ensure_2d(image_data):
    if image_data.ndim == 2:
        return image_data
    elif image_data.ndim == 3:
        return image_data[:, :, 0] if image_data.shape[0] > image_data.shape[2] else image_data[0]
    else:
        return image_data.squeeze()


def save_masks(viewer, new_mask_path, h, w, ds):
    layer_names = [layer.name for layer in viewer.layers]
    if "endo" not in layer_names or "epi" not in layer_names:
        print("Layers must be named 'endo' and 'epi' to save. Skipping save.")
        return False

    epi_mask  = shapes_to_mask(viewer.layers['epi'],  (h, w))
    endo_mask = shapes_to_mask(viewer.layers['endo'], (h, w))

    os.makedirs(new_mask_path, exist_ok=True)
    np.save(f"{new_mask_path}/epi.npy",  epi_mask)
    np.save(f"{new_mask_path}/endo.npy", endo_mask)
    np.save(f"{new_mask_path}/pixel_spacing.npy", np.array(ds.PixelSpacing, dtype=float))
    print(f"Masks saved to {new_mask_path}")
    return True


def mask_to_shapes(mask, scale_row=1.0, scale_col=1.0):
    contours = measure.find_contours(mask, level=0.5)
    shapes = []
    for contour in contours:
        scaled = contour * np.array([scale_row, scale_col])
        shapes.append(scaled)
    return shapes


def load_masks(viewer, mask_path, ds_new):
    epi_mask    = np.load(f"{mask_path}/epi.npy")
    endo_mask   = np.load(f"{mask_path}/endo.npy")
    old_spacing = np.load(f"{mask_path}/pixel_spacing.npy")
    new_spacing = np.array(ds_new.PixelSpacing, dtype=float)

    scale_row = old_spacing[0] / new_spacing[0]
    scale_col = old_spacing[1] / new_spacing[1]

    viewer.layers['epi'].data  = mask_to_shapes(epi_mask,  scale_row, scale_col)
    viewer.layers['endo'].data = mask_to_shapes(endo_mask, scale_row, scale_col)
    print(f"Preloaded masks from {mask_path}")


def find_latest_mask(root, data, patient, slice, methods, method):
    for x in range(method + 1):
        candidate = f"{root}/{data}/p{patient}/s{slice}/im_c/masks/{methods[method - x]}"
        if os.path.exists(candidate):
            return candidate
    return None


def alpha_segment(root, data, patient, slice, methods, method):
    input_path    = f"{root}/{data}/p{patient}/s{slice}/im/{methods[method]}.dcm"
    output_path   = f"{root}/{data}/p{patient}/s{slice}/im_c/{methods[method]}.dcm"
    new_mask_path = f"{root}/{data}/p{patient}/s{slice}/im_c/masks/{methods[method]}"
    mask_path     = find_latest_mask(root, data, patient, slice, methods, method)

    ds, slope, intercept = load_dicom(input_path)
    image_data = ensure_2d(to_t1rho(ds, slope, intercept))
    h, w = image_data.shape

    viewer = napari.Viewer()
    image_layer = viewer.add_image(image_data, name=f"/p{patient}/s{slice}/im/{methods[method]}.dcm")
    viewer.add_shapes(name='epi',  shape_type='polygon',
                      face_color='transparent', edge_color='green', opacity=0.3)
    viewer.add_shapes(name='endo', shape_type='polygon',
                      face_color='transparent', edge_color='red',   opacity=0.3)

    if mask_path is not None:
        load_masks(viewer, mask_path, ds)

    @viewer.bind_key('k')
    def rotate_clockwise(viewer):
        image_layer.data = np.rot90(image_layer.data, k=-1)

    @viewer.bind_key('j')
    def rotate_counterclockwise(viewer):
        image_layer.data = np.rot90(image_layer.data, k=1)

    @viewer.bind_key('h')
    def flip_vertical(viewer):
        image_layer.data = np.flipud(image_layer.data)


    napari.run()

    layer_names = [layer.name for layer in viewer.layers]
    if "endo" not in layer_names or "epi" not in layer_names:
        print("Layers not named 'endo'/'epi' — skipping save and mask.")
        return

    epi_mask  = shapes_to_mask(viewer.layers['epi'],  (h, w))
    endo_mask = shapes_to_mask(viewer.layers['endo'], (h, w))

    background_value = image_data.min()
    masked_image = image_data.copy()
    masked_image[~epi_mask] = background_value
    masked_image[endo_mask] = background_value

    raw_output = to_raw_integers(masked_image, ds, slope, intercept)
    save_dicom(ds, raw_output, slope, intercept, output_path)
    save_masks(viewer, new_mask_path, h, w, ds)


def segmentor_alpha(patient_range):
    methods = ["ecv", "lge", "t1", "t1rho", "t2"]
    for patient in patient_range:
        for slice in range(5):
            for method in range(len(methods)):
                input_path    = f"{root}/{data}/p{patient}/s{slice}/im/{methods[method]}.dcm"
                if os.path.exists(input_path):
                    alpha_segment(root, data, patient, slice, methods, method)
                else:
                    break


pat_len = välj_patienter()
segmentor_alpha(pat_len)
