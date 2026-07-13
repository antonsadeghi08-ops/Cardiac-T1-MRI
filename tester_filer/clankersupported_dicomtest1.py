import pydicom
import napari
import numpy as np
from skimage.draw import polygon


# Ish-Allt här under ska sen loopas.

# Läs av DICOM-filen
dcm_path = "/Users/Anton_Sadeghi/Desktop/till_anton/Patient3Amyloidosisi/T1rho_bw/Amyloidosis2_.MR._.50001.1.2026.02.27.19.02.31.969.34999792.dcm"
ds = pydicom.dcmread(dcm_path)

# Värdena i mappen är INTE T1-rho värdena, utan transformerade utifrån en linjär funktion. 
# Slope = k, intercept = m. 
slope = float(getattr(ds, 'RescaleSlope', 1))
intercept = float(getattr(ds, 'RescaleIntercept', 0))

raw_pixels = ds.pixel_array.astype(np.float32)
image_data = raw_pixels * slope + intercept  #Transforma pixelvärden till T1-rho-värden

# öppna "imagedata bilden" (Värdena där motsvarar inte värdena i 'ds'). Döp till cmr_image
viewer = napari.Viewer()
viewer.add_image(image_data, name='cmr_image')

# Lägg till tomma shapes-lager som användaren ritar i
viewer.add_shapes(name='epi', shape_type='polygon', face_color='transparent', edge_color='green', opacity = 0.3)
viewer.add_shapes(name='endo', shape_type='polygon', face_color='transparent', edge_color='red', opacity = 0.3)

print("Rita EPI-konturen i det gröna lagret och ENDO-konturen i det röda lagret.")
print("Stäng Napari när du är klar.")

napari.run()  # Blockerar tills fönstret stängs

#Hämta masker efter att Napari stängts
epi_layer = viewer.layers['epi']
endo_layer = viewer.layers['endo']

#Height och Width av bilden, taget från image_data. Hade lika gära kunnat vara från image_pixels
h, w = image_data.shape


def shapes_to_mask(shapes_layer, image_shape):
    """Konverterar ett napari shapes-lager till en binär mask."""
    mask = np.zeros(image_shape, dtype=bool)
    for shape_data in shapes_layer.data:
        # shape_data är (N, 2) med koordinater i [row, col]
        rr, cc = polygon(shape_data[:, 0], shape_data[:, 1], image_shape)
        mask[rr, cc] = True
    return mask


epi_mask = shapes_to_mask(epi_layer, (h, w))
endo_mask = shapes_to_mask(endo_layer, (h, w))

#Applicera masken
# Pixlar utanför epi och innanför endo sätts till bakgrundsvärde
background_value = image_data.min()

masked_image = image_data.copy()
masked_image[~epi_mask] = background_value   # Utanför epi blir blank (därav squiglly)
masked_image[endo_mask] = background_value   # Innanför endo blir blank

# --- Vänd rescaling för att spara som raw integers ---
# raw = (rescaled - intercept) / slope
raw_output = (masked_image - intercept) / slope
raw_output = np.clip(raw_output, 0, np.iinfo(ds.pixel_array.dtype).max)
raw_output = raw_output.astype(ds.pixel_array.dtype)

# --- Spara ny DICOM-fil ---
ds_out = ds.copy()
ds_out.PixelData = raw_output.tobytes()
ds_out.RescaleSlope = slope
ds_out.RescaleIntercept = intercept

output_path = dcm_path.replace('.dcm', '_myocardium_masked.dcm')
ds_out.save_as(output_path)

print(f"Sparad maskerad fil: {output_path}")

dcm_cropped_test = output_path
ds_cropped = pydicom.dcmread(dcm_cropped_test)

# Extrahera pixel-array
image_data_cropped = ds_cropped.pixel_array

# öppna Napari
viewer = napari.Viewer()
viewer.add_image(image_data_cropped)






napari.run()


#Idé för hur jag ska göra semi-automatiseringen:
# 0: Spara endo- och epi-polygonerna varje gång man stänger ett napari-fönster med lager som heter just "epi" och "endo"
    # Min tanke är att man har det som en variabel som skrivs över så fort ett fönster med de korrekta lagernamnen stängs
    # Borde kanske ha med en algoritm som kollar om masken som sparas är identisk som bara skriver över om det inte håller.
# 1: Datan för själva masken som användes sparas paralellt med den croppade .dcm-filen.
# 2: Nästa fil som öppnas kommer ha lager med senaste sparade endo- och epi polygoner
# 3: I det öppnade napari-fönstret kommer man kunna se hur polygonerna är alignade med LV
    # 3a: Ifall det är korrekt alignat stänger man fönstret, och masken skrivs över men ändras inte .
    # 3b0: Ifall det inte är korrekt alignat tar man bort masken manuellt, och ritar in en ny. 
        # 3b1: Första gångerna masken inte är alignad bör jag döpa om de nya lagrena till "endo1" och "epi1" så de inte sparas 
        # och skriver över den redan sparade.
        # 3b2: Ifall nog med bilder har varit felalignade på samma sätt (eller om första var felalignad) kan man ignorera att
        # skriva om lagernamnet och spara den nya masken för att underlätta framöver. 
# 4: Jag bör dock hålla koll på när den byter lager så jag vet när jag *måste* byta mask.


# Måste lära mig mer om just datahanteringen
