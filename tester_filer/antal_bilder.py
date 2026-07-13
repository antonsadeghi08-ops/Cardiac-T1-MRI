# /Users/Anton_Sadeghi/Desktop/anton_rawdata

from pathlib import Path

# Hardcoded path to the main folder
MAIN_FOLDER = Path("/Users/Anton_Sadeghi/Desktop/rawdata_final") 

def count_files(folder: Path) -> int:
    return sum(1 for item in folder.rglob("*") if item.is_file())

if __name__ == "__main__":
    if not MAIN_FOLDER.exists():
        print(f"Error: '{MAIN_FOLDER}' does not exist.")
    elif not MAIN_FOLDER.is_dir():
        print(f"Error: '{MAIN_FOLDER}' is not a directory.")
    else:
        total_files = count_files(MAIN_FOLDER)
        print(f"Total files in '{MAIN_FOLDER}': {total_files}")