import datetime
import time
import schedule
import streamlit as st
import git
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

llm = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={
        "temperature": 0.8,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    },
)

today = datetime.datetime.now()
last_week = today - datetime.timedelta(days=7)

def commit_diff(commits):
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
                content += f"```{file_contents.decode('utf-8')}```"


        # Parent commits
        parent_shas = [parent.hexsha for parent in commit.parents]
        print(f"Parent Commits: {', '.join(parent_shas)}")
        st.write(f"Parent Commits: {', '.join(parent_shas)}")
        # Commit stats
        stats = commit.stats.total
        print(f"Stats: {stats}")
        st.write(f"Stats: {stats}")
        # commits_changes = f"""Commit: {commit.hexsha}\n Author: {commit.author.name}\nDate: {commit.committed_datetime}\nMessage: {commit.message}\n
                # Parent Commits: {', '.join(parent_shas)}\nStats: {stats}"""
        
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

                if diff.diff:
                    st.code(diff.diff.decode('utf-8'), language='diff')
            
            print("\n" + "-"*60 + "\n")
            st.write("\n" + "-"*60 + "\n")

        # st.write(f"Content: {content}")
        # print(f"Content: \n{content}")
    return content

output_format = """
    Structured Output Format:
    ## <Repository Name> Codebase Analysis Report

    This report provides an in-depth analysis of the <Repo name> <techstack> application codebase, 
    focusing on key aspects such as repository activity, code quality, and adherence to best practices.

    **1. Repository Metadata:**

    * **Commits:** <Info about Commit>
    * **Branches:** <Info About Branches>
    * **Contributors:**  <Info about contributers>

    **2. Code Quality & Best Practices Evaluation:**

    * **Code Quality:** 
        * **Positive:** <detail about code quality>.
        * **Areas for Improvement:**  <areas where the code could be improved> 
    * **Activity Level:**  
        * <Repository activity>
    * **Refactoring Suggestions:**  
        *  <Refactoring Suggestion>
    * **DRY Principle:** 
        *  <Feedback about the code following DRY principle>

    **3. Insights:**
    - Using its understanding of coding best practices, you have to evaluate code quality based on factors like syntax, error frequency, and use of best practices.
    - you should assess the activity level by analyzing commit frequency, number of active branches, and recent pull requests.
    - You will suggest refactoring opportunities by identifying code duplications, complex methods, or inefficient algorithms.
    - Adherence to principles like DRY (Don’t Repeat Yourself) will be evaluated by detecting repeated code blocks and 
      suggesting optimizations refactoring opportunities, and DRY principle adherence is limited due to the small code sample.

    **4. Recommendations:**

    * **Code Review & Testing:** As the project evolves, prioritize regular code reviews and thorough testing to maintain code quality and identify potential issues early.
    * **Refactoring & Optimization:**  Continuously monitor for code duplication and complexity, implementing refactoring techniques as needed to enhance code maintainability and efficiency.
    * **Collaboration:**  Consider inviting more contributors or seeking feedback from the Rails community to foster diverse perspectives and enhance code quality.
    
    """

def generate_report(prompt):
    response = llm.generate_content(prompt)
    return response
def send_email(subject, body, to_email):
    # Your email credentials
    from_email = os.getenv('EMAIL_ADDRESS')
    password = os.getenv('EMAIL_PASSWORD')

    # Create the email content
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Connect to the Gmail SMTP server
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")

def clone_repo_and_get_commits(repo_name, user_name, token, emai):
    repo_url = f"https://{user_name}:{token}@github.com/{user_name}/{repo_name}.git"
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
    last_week = datetime.datetime.now() - datetime.timedelta(weeks=1)
    commits = list(repo.iter_commits(since=last_week.isoformat()))

    # Print the commit details
    if not commits: 
        st.write("No commits found in the last week")
        print("No commits found in the last week")
        exit(1)
    else:
        content = commit_diff(commits)
        print(f"Content: {content}")
    return content


def weekly_job(repo_name, response, emails):
    for email in emails:
        schedule.every(60).seconds.do(send_email, subject=f"{repo_name} : {str(last_week)[:10]} - {str(today)[:10]}", body=response.text, to_email=email)
        while True:
            schedule.run_pending()
            time.sleep(60)
            print(f"Email sent to {email}")
def generate_and_send(repo_name, user_name, token, emails, prompt):
    response = generate_report(prompt)
    emails = emails.split(',')
    # for email in emails:
        # send_email(to_email=email, subject=f"{repo_name} : {str(last_week)[:10]} - {str(today)[:10]}", body=response.text)
    weekly_job(repo_name, response, emails)