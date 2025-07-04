import json
import requests
import asyncio

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
    

async def fetch_request(*args):
    """
    Make http request
    """