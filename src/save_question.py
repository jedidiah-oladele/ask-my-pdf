import os
import pandas as pd
from github import Github


def save_question_to_github(question_text):

    file_path = os.path.join("data", "questions.csv")
    new_question_df = pd.DataFrame.from_records([{"questions": question_text}])

    access_token = os.environ["GITHUB_ACCESS_TOKEN"]
    repo_name = os.environ["GITHUB_REPO_NAME"]
    owner_name = os.environ["GITHUB_OWNER_NAME"]

    # Authenticate with GitHub API
    g = Github(access_token)
    repo = g.get_user(owner_name).get_repo(repo_name)

    try:
        # If the file exists append to it and update
        contents = repo.get_contents(file_path)
        df = pd.concat(
            [
                pd.read_csv(contents.download_url),
                new_question_df,
            ],
            ignore_index=True,
        )
        buffer = df.to_csv(index=False)
        repo.update_file(contents.path, "Added question", buffer, contents.sha)

    except:
        # If the file doesn't exist yet, create it
        buffer = new_question_df.to_csv(index=False)
        repo.create_file(file_path, "Created questions.csv", buffer)
