import git
import streamlit as st
import os
import time
import datetime
from helper import  generate_and_send, output_format, send_email, generate_report, clone_repo_and_get_commits
import google.generativeai as genai
from dotenv import load_dotenv
import schedule

load_dotenv()

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

llm = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={
        "temperature": 0.9,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    },
)

st.title("Betacraft Code Analyst")
repo_name = st.text_input("Enter repository name: ")
user_name = st.text_input("Enter user name: ")
token = st.text_input("Enter token: ")
emails = st.text_input("Enter email: ")

content = ""
prompt = f"""You are a Software Engineer. You have to read the following code of a github repository in triple backticks and 

    based on the code you have to perform the following actions if the context is empty then return "Context Empty"
    1. Metadata collection on commits, branches, and contributors to understand repository activity.
    2. Answer the following questions \n
        - "What is the code quality of this repository?"
        - "What is the activity level in this repository?"
        - "Are there any suggestions for refactoring in this repository?"
        - "Does this repository follow the DRY principle?"
        - "List out the duplicate code which can be refactored"
    3. *Insight Generation:**
        - Using its understanding of coding best practices, the model will evaluate code quality based on factors like syntax, error frequency, and use of best practices.
        - It will assess the activity level by analyzing commit frequency, number of active branches, and recent pull requests.
        - The model will suggest refactoring opportunities by identifying code duplications, complex methods, or inefficient algorithms.
        - Adherence to principles like DRY (Dont Repeat Yourself) will be evaluated by detecting repeated code blocks and suggesting optimizations.
    4. Reporting:**
        - Generate comprehensive reports detailing the analysis, which can be used for code review sessions and development strategy planning.
    
    
    You have to get the above details from the code and then you have to generate the report for technical and non technical persons and    
    you have to get the code which are not following the above actions it in the Technical Reports.

    Code:
    """
if st.button("Submit"):
    content = clone_repo_and_get_commits(repo_name, user_name, token, emails)

    prompt += f"\n```\n{content}\n```\n"
    response = generate_report(prompt)
    st.title("Report")
    st.write(response.text)
    print(f"Response: {response.text}")

    generate_and_send(repo_name, user_name, token, emails, prompt)
# body = f"""The last week Sprint Report of {repo_name}\n""" + response.text
