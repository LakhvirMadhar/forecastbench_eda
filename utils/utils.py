import os
import json


def read_json(filepath):
    """
    Read a JSON file
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    return data

def write_json(filepath, file_to_write):
    """
    Write a JSON file
    """
    with open(filepath, 'w') as f:
        json.dump(file_to_write, f, indent=4)
    

def read_csv_files(CSV_FILEPATH):
    """
    Returns a list of csv files
    """
    files = []

    for entry in os.listdir(CSV_FILEPATH):
        full_path = os.path.join(CSV_FILEPATH, entry)

        if os.path.isfile(full_path):
            files.append(full_path)
    
    return files