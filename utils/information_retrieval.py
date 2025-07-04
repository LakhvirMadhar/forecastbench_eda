"""----------------------------------
The file is about getting the past commits from a GitHub page 
from ForecastBench and saving the files locally.
----------------------------------"""

import os
import re
import requests
import base64
from io import StringIO
import asyncio
import pandas as pd

from utils.utils import read_json, write_json, read_csv_files


BASE_FILEPATH = 'data/'
CSV_FILEPATH = 'data/csv/'
CHARTS_FILEPATH = 'output/'
COMMIT_FILEPATH = 'data/commits.json'

FILEPATHS = [CSV_FILEPATH, CHARTS_FILEPATH]


def create_folders():
    """
    Create directory files for where files will be saved to
    """
    for filepath in FILEPATHS:
        os.makedirs(filepath, exist_ok=True)

"""-------------------------
  COMMIT RETRIEVAL FUNCS
-------------------------"""

def run_commit_retrieval(commits_url, params, headers):
    """
    Orchestrates the complete commit retrieval process by fetching all commits 
    from a GitHub repository and saving them to local storage.

    Args:
        commits_url (str): GitHub API endpoint URL for repository commits
        params (dict): Query parameters for the API request (e.g., since, until, author)
    """
    retrieved_commits = retrieve_all_commits(commits_url, params, headers)
    
    save_commit_history(retrieved_commits)

    
def retrieve_all_commits(commits_url, params, headers):
    """
    Retrieves the complete commit history from a GitHub repository using pagination.
    
    Fetches all commits across multiple pages and returns them in chronological order
    (oldest to newest). Uses GitHub API authentication via environment variable.

    Args:
        commits_url (str): GitHub API endpoint URL for repository commits
        params (dict): Query parameters for the API request (e.g., since, until, author)

    Returns:
        list[dict]: Complete commit history ordered from oldest to newest, where each
                   dict contains commit metadata including SHA, author, message, and timestamp
    """

    retrieved_commits = []
    page = 1

    while True:
        params['page'] = page
        response = requests.get(url=commits_url, params=params, headers=headers)
        commits = response.json()

        # Break pagination loop when no more commits are returned
        if not commits:
            break

        retrieved_commits.extend(commits)
        print(f"Page {page}: Got {len(commits)} commits")
        page +=1
    
    print(f"Retrieved a total of {len(retrieved_commits)} commits\n")

    # Return the list in reverse order (oldest to newest)
    retrieved_commits.reverse()

    return retrieved_commits


def save_commit_history(retrieved_commits):
    """
    Saves commit history to local JSON file, creating new file or updating existing one.
    
    If the file doesn't exist, creates a new commit history file. If it exists,
    delegates to update_commit_history() to merge new commits with existing data.

    Args:
        retrieved_commits (list[dict]): List of commit dictionaries ordered oldest to newest
    """
    
    commit_exists = os.path.exists(COMMIT_FILEPATH) 
    
    if not commit_exists:
        write_json(COMMIT_FILEPATH, retrieved_commits)
        print(f"Initialized commit history to {COMMIT_FILEPATH}")
    elif commit_exists:
        # Update the commit history with the latest updates
        update_commit_history(retrieved_commits)


def update_commit_history(retrieved_commits):
    """
    Updates existing commit history file with new commits from GitHub.
    
    Compares local commit history with retrieved commits using SHA hashes.
    If new commits are found, overwrites the entire file with the updated history
    maintaining chronological order (oldest to newest).

    Args:
        retrieved_commits (list[dict]): Complete commit history from GitHub API,
                                       ordered oldest to newest
    """
    saved_commit_history = read_json(COMMIT_FILEPATH)

    # Compare SHA hashes between local and GitHub versions 
    saved_hases = {saved_commit['sha'] for saved_commit in saved_commit_history}
    retrieved_hashes = {retrieved_commit['sha'] for retrieved_commit in retrieved_commits}

    if saved_hases == retrieved_hashes:
        print("Commit history is up-to date!")
        return

    # If there are differences in the commits, overwrite the old file with the new file    
    new_commits = [commit for commit in retrieved_commits if commit['sha'] not in saved_hases]

    if new_commits:
        write_json(COMMIT_FILEPATH, retrieved_commits)        
        print(f"Updated the commit history with **{len(new_commits)}** new entries!")


"""-------------------------
    CSV RETRIEVAL FUNCS
-------------------------"""

def download_csv_files():
    """
    Download and process historical leaderboard CSV files from GitHub commits.
    
    Compares locally saved CSV files with available commit history to identify
    missing files, downloads them from GitHub API, processes the model data
    by cleaning and splitting model names, and saves cleaned CSV files with
    additional metadata (hash_id, date, cleaned model names, and methods).

    TODO: Implement async processing for better performance
    """

    saved_commit_history = read_json(COMMIT_FILEPATH)

    # Create a lookup dictionary to quickly retrieve the date for each commit
    commit_date_lookup = {commit['sha']: commit for commit in saved_commit_history}

    # Logic to check what downloaded csv files we currently have
    csv_files = read_csv_files(CSV_FILEPATH)

    # Strip the csv files
    # Compare hashes between commit history and csv files
    csv_hashes = [file.split('.csv')[0] for file in csv_files]
    saved_hashes = {saved_commit['sha'] for saved_commit in saved_commit_history}

    # Store hashes for csv files we don't have yet
    hashes_to_request = [saved_hash for saved_hash in saved_hashes if saved_hash not in csv_hashes]
    
    file_url = "https://api.github.com/repos/forecastingresearch/forecastbench-datasets/contents/leaderboards/csv/leaderboard_overall.csv"
    
    if not hashes_to_request:
        print("Files are all upto date!")
        return

    # TODO: Turn this into an async process
    # TODO: Do entire dataset, not just size 1
    # TODO: Add error handling to the requests, raiseError if we do get an error as we don't want to keep pinging if we failed to save something
    for request_hash in hashes_to_request[:2]:

        file_params = {'ref': request_hash}
        file_response = requests.get(file_url, params=file_params)
        file_data = file_response.json()

        content = base64.b64decode(file_data['content']).decode('utf-8')
        
        # Process and save the cleaned CSV
        save_cleaned_csv(content, request_hash, commit_date_lookup)


def save_cleaned_csv(content, request_hash, commit_date_lookup):
    """
    Process the CSV content and save it as a cleaned CSV file.
    
    Args:
        content (str): The decoded CSV content
        request_hash (str): The commit hash
        commit_date_lookup (dict): Dictionary mapping commit hashes to commit objects
    """
    df = pd.read_csv(StringIO(content))
    
    # Get the date using the lookup dictionary
    date = commit_date_lookup.get(request_hash, {}).get('commit', {}).get('author', {}).get('date', 'Unknown')
    date = date.split('T')[0]

    all_processed_data = []
    
    # Process each row in the Model column
    for index, row in df.iterrows():
        model = row['Model']
        
        # Split the model names
        raw_model = (re.split(r"\(|\)", model))

        # Data cleaning
        if raw_model[-1] == '':
            raw_model.pop()

        # Determine the llm_model and method
        if len(raw_model) > 2:
            cleaned_model_name = ''.join(raw_model[:-1]) # Join all but the last 
            method = raw_model[-1]
        elif len(raw_model) == 2:
            cleaned_model_name = raw_model[0]
            method = raw_model[1]
        else:
            cleaned_model_name = 'ForecastBench'
            method = raw_model[0]

        # Create row data
        processed_row = {
            'hash_id': request_hash,
            'llm_model': cleaned_model_name.strip(),
            'method': method.strip(),
            'date': date.strip()
        }

        # Populate the rest of the table
        for col in df.columns:
            processed_row[col] = row[col]

        all_processed_data.append(processed_row)
    
    # Save it locally
    final_df = pd.DataFrame(all_processed_data)
    final_df.to_csv(f'{CSV_FILEPATH}{request_hash}.csv', index=False)


def create_or_update_master_csv():
    """
    Create and update the master csv file containing the data across all days
    """
    pass