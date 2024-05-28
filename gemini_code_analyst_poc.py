import os
# import shutil
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
    with open(output_file, 'w') as outfile:
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        outfile.write(f"\n\n--- {file_path} ---\n\n")
                        outfile.write(content)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")


# Step 1: Load the model
print("Loading Gemini 1.5 pro model...")
llm = genai.GenerativeModel('gemini-1.5-flash')



# Display title
st.title("Gemini Code Analyst")

# Input for GitHub repository URL
print("Gemini Code Analyst Started...")
repo_url = st.text_input("Enter GitHub repository URL: ")

# Button to trigger analysis
if st.button("Submit"):
    # st.session_state.chat_history.append("You: " + repo_url)
    local_path = './' + repo_url.split('/')[-1].replace('.git', '')
    output_file = local_path + '_output.txt'

    # Step 2: Clone the repository if not already cloned
    if not os.path.exists(local_path):
        print("Cloning Repository...")
        st.write("Cloning repository...")
        try:
            git.Repo.clone_from(repo_url, local_path)
        except Exception as e:
            st.write(f"Error cloning repository: {e}")
    else:
        st.write("Repository already exists")

    # Process the files in the repository
    print("Processing files...")
    read_and_append_files(local_path, output_file)

    st.write("Reading files...")
    print("Reading files...")
    try:
        with open(output_file, 'r') as file:
            text = file.read()
        st.write("Files read successfully.")
    except Exception as e:
        st.write(f"Error reading output file: {e}")
        text = ""

    # Output Format of LLM
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
    # Define prompt for Generative AI model
    prompt = f"""You are a Software Engineer. You have to read the following code of a github repository in triple backticks and 
    based on the code you have to perform the following actions if the context is empty then return "Context Empty"1.
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
    
    You have to get the above details from the code and then you have to write the report in the below format:
    {output_format}
    Replace with actual data for <>.
    Code:  ```{text}```
    """ 
    
    # Generate response from Generative AI model
    print("Generating response...")
    st.write("Waiting for Gemini response...")
    input_tokens = llm.count_tokens(prompt)
    # st.write(llm.count_tokens(prompt))
    
    try:
        # processed_data = ""
        response = llm.generate_content(prompt)
        output_tokens = llm.count_tokens(response.text)
        total_tokens = input_tokens.total_tokens + output_tokens.total_tokens
        st.write(f"Total tokens: {total_tokens}")
        print("Total tokens: ", total_tokens)
        print(response.text)        
        st.write(response.text)
        
        # for chunk in response:
        #     if chunk:
        #         # processed_data = processed_data + response.text.replace("\n", " ")
        #         st.write(chunk.text, unsafe_allow_html=False)
        #         st.write("--------------------------------------------------------------------------------------------------")
        #         print(chunk.text)
        print("Gemini response successfully generated")
    except Exception as e:
        st.write(f"Error generating response: {e}")
        print("Error generating response: ", e)

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
