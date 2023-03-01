import os
import pandas as pd
from github import Github


def save_file_to_github(file_path, buffer):

    access_token = os.environ["GITHUB_ACCESS_TOKEN"]
    repo_name = os.environ["GITHUB_REPO_NAME"]
    owner_name = os.environ["GITHUB_OWNER_NAME"]

    # Authenticate with GitHub API
    g = Github(access_token)
    repo = g.get_user(owner_name).get_repo(repo_name)

    try:
        # Get the existing file contents and update file
        contents = repo.get_contents(file_path)
        repo.update_file(
            contents.path, "Updated file from Python script", buffer, contents.sha
        )
    except:
        # If the file doesn't exist yet, create it
        repo.create_file(file_path, "Created file from Python script", buffer)


def save_question(question_text):
    file_path = os.path.join("data", "questions.csv")

    # create an empty dataframe if csv file doesn't exist
    if not os.path.isfile(file_path):
        df = pd.DataFrame(columns=["questions"])

    else:
        df = pd.concat(
            [
                pd.read_csv(file_path),
                pd.DataFrame.from_records([{"questions": question_text}]),
            ],
            ignore_index=True,
        )

    save_file_to_github(file_path, df.to_csv(index=False))
