from github import Github
import streamlit as st


def save_csv_to_github(
    file_path,
    df,
    access_token=st.secrets["GITHUB_ACCESS_TOKEN"],
    repo_name=st.secrets["GITHUB_REPO_NAME"],
    owner_name=st.secrets["GITHUB_OWNER_NAME"],
):
    # Authenticate with GitHub API
    g = Github(access_token)
    repo = g.get_user(owner_name).get_repo(repo_name)

    # Write the modified CSV data to a buffer
    buffer = df.to_csv(index=False)

    # Commit changes to GitHub
    try:
        # Get the existing file contents
        contents = repo.get_contents(file_path)
        # Update the file with the new contents
        repo.update_file(
            contents.path, "Updated file from Python script", buffer, contents.sha
        )
    except:
        # If the file doesn't exist yet, create it
        repo.create_file(file_path, "Created file from Python script", buffer)
