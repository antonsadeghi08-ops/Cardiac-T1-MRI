# Bättre dokumentationer kommer senarer
# Läs "alla python-scripts för konceptuell förståelse"
#Info tagen från youtube-tutorial: https://www.youtube.com/watch?v=Q02BMUooqQc

import os
from pathlib import Path

file_types = {

    'IMAGES' :['.dcm'],
    'MASKS' : ['.bam']
}

dct = dict()
for directory, file_formats in file_types.items:
    for file_format in file_formats:
        dct[file_formats] = directory

def file_organizer():
    for entry in os.scandir:
        if entry.is_dir():
            continue

        file_path = Path(entry)
        file_format = file_path.suffix.lower()

        if file_format in dct:
            directory_path = Path(dct[file_format])