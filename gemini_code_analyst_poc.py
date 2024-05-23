import os
import shutil
import streamlit as st
import git
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google API key for Generative AI model
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Function to read files from a repository and append their content to an output file
def read_and_append_files(repo_path, output_file):
    with open(output_file, 'a') as outfile:
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as infile:
                        content = infile.read()
                        outfile.write(f"\n\n--- {file_path} ---\n\n")
                        outfile.write(content)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

# Initialize chat history in session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Step 1: Load the model
llm = genai.GenerativeModel('gemini-1.5-pro-latest')

# Display title
st.title("Gemini Code Analyst")

# Input for GitHub repository URL
repo_url = st.text_input("Enter GitHub repository URL: ")

# Button to trigger analysis
if st.button("Submit"):
    st.session_state.chat_history.append("You: " + repo_url)
    local_path = './' + repo_url.split('/')[-1].replace('.git', '')
    output_file = local_path + '_output.txt'

    # Step 2: Clone the repository if not already cloned
    if not os.path.exists(local_path):
        st.write("Cloning repository...")
        try:
            git.Repo.clone_from(repo_url, local_path)
        except Exception as e:
            st.write(f"Error cloning repository: {e}")
    else:
        st.write("Repository already exists")

    # Process the files in the repository
    read_and_append_files(local_path, output_file)

    st.write("Reading files...")
    try:
        with open(output_file, 'r') as file:
            text = file.read()
        st.write("Files read successfully.")
    except Exception as e:
        st.write(f"Error reading output file: {e}")
        text = ""

    # Define prompt for Generative AI model
    prompt = f"""You are a Software Engineer. You have to read the following code of a github repository in triple backticks and 
    based on the code you have to perform the following actions.
    1. Metadata collection on commits, branches, and contributors to understand repository activity.
    2. Answer the following questions \n
        - "What is the code quality of this repository?"
        - "What is the activity level in this repository?"
        - "Are there any suggestions for refactoring in this repository?"
        - "Does this repository follow the DRY principle?"
    3. *Insight Generation:**
        - Using its understanding of coding best practices, the model will evaluate code quality based on factors like syntax, error frequency, and use of best practices.
        - It will assess the activity level by analyzing commit frequency, number of active branches, and recent pull requests.
        - The model will suggest refactoring opportunities by identifying code duplications, complex methods, or inefficient algorithms.
        - Adherence to principles like DRY (Dont Repeat Yourself) will be evaluated by detecting repeated code blocks and suggesting optimizations.
    4. Reporting:**
        - Generate comprehensive reports detailing the analysis, which can be used for code review sessions and development strategy planning.
    Code:  ```{text}```
    """
    
    # Generate response from Generative AI model
    st.write("Waiting for Gemini response...")
    try:
        response = llm.generate_content(prompt)
        st.write(response.text)
        st.session_state.chat_history.append("AI: " + response.text)
    except Exception as e:
        st.write(f"Error generating response: {e}")

    # Delete the cloned repository
    # try:
    #     if os.path.exists(local_path):
    #         shutil.rmtree(local_path)
    #         st.write("Cloned repository deleted.")
    #     if os.path.exists(output_file):
    #         os.remove(output_file)
    #         st.write("Output file deleted.")
    # except Exception as e:
    #     st.write(f"Error deleting files: {e}")

# Display chat history
st.title("Chat History")
for chat in st.session_state.chat_history:
    st.write(chat)
