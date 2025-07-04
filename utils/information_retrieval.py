"""----------------------------------
The file is about getting the past commits from a GitHub page 
from ForecastBench and saving the files locally.
----------------------------------"""

import os
import requests
import asyncio
import pandas as pd

from utils.utils import read_json, write_json


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


# Maybe make a read and write JSON function? Would make it so that I don't have to keep repeating the same thing over and over

"""-------------------------
    CSV RETRIEVAL FUNCS
-------------------------"""

def download_csv_files():
    """
    Based on the commit history, in an async manner, download the past leaderboards.

    Get the commits we have
    
    Raise an error in the event we get a 429 error.

    Save the file with the date in front so it's not just the commit id (?)
    """

    saved_commit_history = read_json(COMMIT_FILEPATH)

    # Logic to check what csv files we currently have

    # Load csv files to download in an couroutine object
    for commit in saved_commit_history:
        
        pass

    # Kick off the async file saving with error handling




def master_csv_file():
    """
    Create and update the master csv file containing the data across all days
    """
    pass