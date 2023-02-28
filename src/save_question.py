import os
import pandas as pd
from github import Github


def save_question_to_github(question_text):

    file_path = os.path.join("data", "questions.csv")

    access_token = os.environ["GITHUB_ACCESS_TOKEN"]
    repo_name = os.environ["GITHUB_REPO_NAME"]
    owner_name = os.environ["GITHUB_OWNER_NAME"]

    import streamlit as st

    # Authenticate with GitHub API
    g = Github(access_token)
    repo = g.get_user(owner_name).get_repo(repo_name)

    try:
        file_content = repo.get_contents(file_path)
        df = pd.read_csv(file_content.download_url)
        st.write(df)

    except:
        # If the file doesn't exist yet, create it
        df = pd.DataFrame(columns=["questions"])
        buffer = df.to_csv(index=False)
        repo.create_file(file_path, "Created questions.csv", buffer)

    st.write(df)
    buffer = pd.concat(
        [df, pd.DataFrame.from_records([{"questions": question_text}])],
        ignore_index=True,
    ).to_csv(index=False)

    # Commit changes to GitHub
    contents = repo.get_contents(file_path)
    repo.update_file(contents.path, "Added question", buffer, contents.sha)
