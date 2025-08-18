# Forecast Bench Exploratory Data Analysis (EDA)

This Jupyter notebook performs an exploratory data analysis on the Forecast Bench leaderboard data. The analysis focuses on comparing the performance of "freeze" vs. "non-freeze" methods for various large language models (LLMs). The goal is to determine if freezing certain parameters or values provides a statistically significant advantage in forecasting tasks, as measured by the **Market Score (resolved)** column.

***

## Prerequisites

* Python 3.x
* Jupyter Notebook
* A GitHub Personal Access Token (PAT) with `public_repo` scope to access the Forecast Bench GitHub repository.
* The required Python libraries. You can install all of them at once using `pip` and the provided `requirements.txt` file:

    ```bash
    pip install -r requirements.txt
    ```

***

## Getting a GitHub Personal Access Token

To access the GitHub API and retrieve the leaderboard data, you need a **Personal Access Token (PAT)**. This token authenticates your requests.

Here are the steps to create a GitHub personal access token:

1.  **Sign in to GitHub**.
2.  Click your profile picture in the top-right corner and select **Settings**.
3.  In the left sidebar, click **Developer settings**.
4.  Click **Personal access tokens**, then choose **Tokens (classic)**.
5.  Click **Generate new token**, then select **Generate new token (classic)**.
6.  Give your token a descriptive name.
7.  Select the **scopes** or permissions you want the token to have. For this notebook, you only need the **`public_repo`** scope. 8.  Set an expiration date for the token.
9.  Click **Generate token**.
10. **Copy the generated token immediately.** You won’t be able to see it again.

You'll need to set this token as an environment variable named `GITHUB_API_KEY` in your .env file before running the notebook.

    
    'GITHUB_API_KEY' = '<your-api-key-here>'
    

***

## Notebook Structure and Pipeline

The notebook follows a structured pipeline to retrieve, process, and analyze the data.

### 1. Information Retrieval Pipeline

This section handles the data scraping and preparation from the Forecast Bench GitHub repository.

* **`create_folders()`**: Creates the necessary local folders to store the downloaded data.
* **`run_commit_retrieval(commits_url, params, headers)`**: Fetches the commit history for the leaderboard CSV file from the GitHub API.
* **`download_csv_files(headers)`**: Downloads all historical versions of the `leaderboard_overall.csv` file based on the retrieved commit history.
* **`create_master_csv()`**: Concatenates all downloaded CSV files into a single `master.csv` file for unified analysis.

### 2. Data Loading and Initial Setup

* Loads the `master.csv` file into a pandas DataFrame.
* Filters the DataFrame to include only the columns relevant for this analysis: **`Organization`**, **`llm_model`**, **`method`**, **`date`**, **`Market Score (resolved)`**, and **`Market Score (resolved) Dataset Size`**.
* Converts the `date` column to a datetime format and sorts the data chronologically.
* Provides example code to inspect the data, such as listing unique dates and models.

### 3. Statistical Analysis

This section contains the core analysis of the notebook.

* **`analyze_freeze_vs_nonfreeze(df)`**: This function is designed to compare the **best** freeze method against the **best** non-freeze method for a single model on each date.
* **`analyze_all_freeze_vs_nonfreeze(df)`**: This function expands the analysis by comparing **all** freeze methods against **all** non-freeze methods, providing more statistical power. It calculates the average and best scores for each category.
* **`run_statistical_tests(comparison_df, model_name)`**: A helper function that performs a **one-tailed paired t-test** on the differences in scores. The null hypothesis ($H_0$) is that there is no difference in performance (mean difference = 0), while the alternative hypothesis ($H_1$) is that freeze methods are better (mean difference > 0).
* **`analyze_single_model(df, model_name)`**: Runs the complete analysis for a specified model. It prints out details about the data and the statistical test results.
* **`analyze_all_models(df)`**: Iterates through all available models and runs the single-model analysis on each. It then prints a summary table of all models, showing the success rate and statistical significance of the freeze method advantage.