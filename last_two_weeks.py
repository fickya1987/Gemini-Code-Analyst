import os
import git
import datetime
# from github import Github
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
# Ensure you set these environment variables before running the script
username = os.getenv("GITHUB_USERNAME")
token = os.getenv("GITHUB_TOKEN")
# repository_name = "Gemini-Code-Analyst"
# target_directory = "./Gemini-Code-Analyst"

if not username or not token:
    st.write("Error: GITHUB_USERNAME and GITHUB_TOKEN environment variables are not set.")
    print("Error: GITHUB_USERNAME and GITHUB_TOKEN environment variables are not set.")
    exit(1)

# Construct the repository URL with the access token
repo_url = st.text_input("Enter repository name: ")


if st.button("Submit"):
    # Clone the repository if not already cloned
    # repo_url = f"https://{username}:{token}@github.com/{username}/{repository_name}.git"
    # repo_url = st.text_input("Enter Repository URL:")
    target_directory = "./" + repo_url.split('/')[-1].replace('.git', '')
    if not os.path.exists(target_directory):
        try:
            git.Repo.clone_from(repo_url, target_directory)
            print(f"Repository cloned to {target_directory}")
            st.write("Repository cloned to " + target_directory)
        except git.exc.GitCommandError as e:
            st.write(f"Error cloning repository: {e}")
            print(f"Error cloning repository: {e}")
            exit(1)
    else:
        print(f"Repository already cloned to {target_directory}")
        st.write(f"Repository already cloned to {target_directory}")

    # Initialize GitPython Repo object
    print(f"Initializing Repo : {target_directory}")
    repo = git.Repo(target_directory)

    # Get the commits from the last two weeks
    two_weeks_ago = datetime.datetime.now() - datetime.timedelta(weeks=4)
    commits = list(repo.iter_commits(since=two_weeks_ago.isoformat()))

    # Print the commit details
    if not commits: 
        st.write("No commits found in the last two weeks")
        print("No commits found in the last two weeks")
        exit(1)
    content = ""
    for commit in commits:
        st.header("Commit")
        print("Commmit")

        print(f"Commit: {commit.hexsha}")
        print(f"Author: {commit.author.name}")
        print(f"Date: {commit.committed_datetime}")
        print(f"Message: {commit.message}")
        print("\n" + "-"*60 + "\n")
        print("Changes:")

        st.write(f"Author: {commit.author.name}")
        st.write(f"Commit: {commit.hexsha}")
        st.write(f"Date: {commit.committed_datetime}")
        st.write(f"Message: {commit.message}")
        # st.write(f"Show: {commit.show()}")
        st.write("\n" + "-"*60 + "\n")
        st.write("Changes:")

        # Iterate over all files in the commit
        for item in commit.tree.traverse():
            if isinstance(item, git.objects.blob.Blob):
                file_path = item.path
                blob = commit.tree / file_path
                file_contents = blob.data_stream.read()
                content += f"\n\n--- {file_path} ---\n\n"
                # print(f"File: {file_path}")
                # print(f"Contents: {file_contents.decode('utf-8')}")
                content += f"```{file_contents.decode('utf-8')}```"
                # print("------------")
                # st.write(f"File: {file_path}")
                # st.write(f"Contents: {file_contents.decode('utf-8')}")
                # st.write("------------")


        # Parent commits
        parent_shas = [parent.hexsha for parent in commit.parents]
        print(f"Parent Commits: {', '.join(parent_shas)}")
        st.write(f"Parent Commits: {', '.join(parent_shas)}")
        
        # Commit stats
        stats = commit.stats.total
        print(f"Stats: {stats}")
        st.write(f"Stats: {stats}")
        
        # Diff with parent
        if commit.parents:
            diffs = commit.diff(commit.parents[0])
            for diff in diffs:
                print("Difference:")
                print(f"File: {diff.a_path}")
                print(f"New file: {diff.new_file}")
                print(f"Deleted file: {diff.deleted_file}")
                print(f"Renamed file: {diff.renamed_file}")
                print(f"Changes:\n{diff.diff}")


                st.header("Difference")
                st.write(f"File: {diff.a_path}")
                st.write(f"New file: {diff.new_file}")
                st.write(f"Deleted file: {diff.deleted_file}")
                st.write(f"Renamed file: {diff.renamed_file}")
                st.write(f"Changes: {diff.diff}")
                # st.write(f"Git Commit Diff: }")
                # st.write(f"Stats: {diff.stats}")
                # st.write(f"")
            
            print("\n" + "-"*60 + "\n")
            st.write("\n" + "-"*60 + "\n")

        st.write(f"Content: {content}")
        print(f"Content: \n{content}")
           
