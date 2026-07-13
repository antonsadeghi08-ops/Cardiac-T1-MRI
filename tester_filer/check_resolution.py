import pydicom


def get_dicom_info(dicom_path):
    try:
        ds = pydicom.dcmread(dicom_path)

        # Image resolution
        rows = ds.Rows
        cols = ds.Columns

        print(f"\nImage resolution:")
        print(f"  {cols} × {rows} pixels")

        # Pixel spacing
        if hasattr(ds, "PixelSpacing"):
            row_spacing, col_spacing = map(float, ds.PixelSpacing)

            print("\nPixel spacing:")
            print(f"  Row spacing:    {row_spacing:.6f} mm/pixel")
            print(f"  Column spacing: {col_spacing:.6f} mm/pixel")

            # Physical dimensions
            width_mm = cols * col_spacing
            height_mm = rows * row_spacing

            print("\nPhysical image size:")
            print(f"  Width:  {width_mm:.2f} mm")
            print(f"  Height: {height_mm:.2f} mm")

        else:
            print("\nPixel spacing information is not available in this DICOM file.")

    except Exception as e:
        print(f"\nError reading DICOM file:\n{e}")


if __name__ == "__main__":
    dicom_path = input("Enter the path to the DICOM file: ").strip()

    get_dicom_info(dicom_path)

#   /Users/Anton_Sadeghi/Desktop/data_sorted/p0/s0/im/ecv.dcm
#   /Users/Anton_Sadeghi/Desktop/data_sorted/p0/s0/im/lge.dcm
#   /Users/Anton_Sadeghi/Desktop/data_sorted/p0/s0/im/t1.dcm
#   /Users/Anton_Sadeghi/Desktop/data_sorted/p0/s0/im/t1rho.dcm
#   /Users/Anton_Sadeghi/Desktop/data_sorted/p0/s0/im/t2.dcm
