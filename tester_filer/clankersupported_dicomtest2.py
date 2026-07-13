import pydicom
import napari
import numpy as np
from skimage.draw import polygon

#Lägg till hotkeys för rotera och flippa ordning i napari
 
 
# Paths
 
DCM_INPUT_PATH = "/Users/Anton_Sadeghi/Desktop/tester/im/HCM_2_.MR._.58001.1.2026.03.26.15.03.23.963.51947765 (kopia).dcm"
 
# Alfa: myokard-maskad fil (hela hjärtat, endo borttagen)
OUTPUT_MASKED_PATH = "/Users/Anton_Sadeghi/Desktop/tester/im_c/m0.dcm"
 
# Beta: ROI-klippt fil
OUTPUT_ROI_PATH = "/Users/Anton_Sadeghi/Desktop/tester/im_i/m0.dcm"
 
# Beta: REF-klippt fil
OUTPUT_REF_PATH = "/Users/Anton_Sadeghi/Desktop/tester/im_r/m0.dcm"
 
 
# Hjälpfunktioner
 

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

 
 

# segmentor_alpha – Rita EPI + ENDO på originalbilden → spara myokard-maskad DICOM

 
ds, slope, intercept = load_dicom(DCM_INPUT_PATH)
image_data = to_t1rho(ds, slope, intercept)
h, w = image_data.shape
 
viewer = napari.Viewer()
viewer.add_image(image_data, name='cmr_image')
viewer.add_shapes(name='epi',  shape_type='polygon', face_color='transparent', edge_color='green', opacity=0.3)
viewer.add_shapes(name='endo', shape_type='polygon', face_color='transparent', edge_color='red',   opacity=0.3)
 

napari.run()
 
epi_mask  = shapes_to_mask(viewer.layers['epi'],  (h, w))
endo_mask = shapes_to_mask(viewer.layers['endo'], (h, w))
 
background_value = image_data.min()
masked_image = image_data.copy()
masked_image[~epi_mask]  = background_value   # Utanför epi blir blank
masked_image[endo_mask]  = background_value   # Innanför endo blir blank
 
raw_output = to_raw_integers(masked_image, ds, slope, intercept)
save_dicom(ds, raw_output, slope, intercept, OUTPUT_MASKED_PATH)
 

# segmentor_beta – Öppna den maskade filen och rita ROI + REF → spara två klippta filer
 
ds_masked, slope_m, intercept_m = load_dicom(OUTPUT_MASKED_PATH)
image_masked = to_t1rho(ds_masked, slope_m, intercept_m)
h2, w2 = image_masked.shape
 
viewer2 = napari.Viewer()
viewer2.add_image(image_masked, name='masked_image')
viewer2.add_shapes(name='roi', shape_type='polygon', face_color='transparent', edge_color='cyan',   opacity=0.3)
viewer2.add_shapes(name='ref', shape_type='polygon', face_color='transparent', edge_color='yellow', opacity=0.3)
 
napari.run()
 
roi_mask = shapes_to_mask(viewer2.layers['roi'], (h2, w2))
ref_mask = shapes_to_mask(viewer2.layers['ref'], (h2, w2))
 
# Applicera varje mask och spara som egen DICOM-fil
for mask, out_path, label in [
    (roi_mask, OUTPUT_ROI_PATH, 'ROI'),
    (ref_mask, OUTPUT_REF_PATH, 'REF'),
]:
    cropped = image_masked.copy()
    cropped[~mask] = image_masked.min()          # allt utanför masken blir bakgrund
    raw_crop = to_raw_integers(cropped, ds_masked, slope_m, intercept_m)
    save_dicom(ds_masked, raw_crop, slope_m, intercept_m, out_path)

 
print("\n Sparade (image_id)")
print(f"  cropped bild finns i   : {OUTPUT_MASKED_PATH}")
print(f"  ROI-bild finns i       : {OUTPUT_ROI_PATH}")
print(f"  REF-bild finns i       : {OUTPUT_REF_PATH}")