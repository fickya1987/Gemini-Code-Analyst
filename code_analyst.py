import os
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
        repo = git.Repo(repo_path)
        commits = len(list(repo.iter_commits()))
        outfile.write(f"Total commits: {commits}\n\n")
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
print("Loading Gemini 1.5 flash model...")
generation_config = {
  "temperature": 0.5,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
#   "max_input_tokens": 1000000,
  "response_mime_type": "text/plain",
}

llm = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config
)



# Display title
st.title("Betacraft AI Code Analyst")

# Input for GitHub repository URL
print("Betacraft AI Code Analyst Started...")
repo_url = st.text_input("Enter GitHub repository URL: ")

# Button to trigger analysis
if st.button("Submit"):
    # st.session_state.chat_history.append("You: " + repo_url)
    local_path = './repo/' + repo_url.split('/')[-1].replace('.git', '')
    output_file = local_path + '_output.txt'

    # Step 2: Clone the repository if not already cloned
    if not os.path.exists(local_path):
        print("Cloning Repository...")
        st.write("Cloning repository...")
        try:
            git.Repo.clone_from(repo_url, local_path)
        except Exception as e:
            print(f"Error cloning repository: {e}")
    # else:
    #     st.write("Repository already exists")

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
        st.write(f"Error reading output file: {e}\n\n")
        text = ""

    # Output Format of LLM
    non_technical_output_format = """Non-Technical Report (For Management/Stakeholders)
        Repository Health Report

        Repository: [Insert Repository Name Here]

        I. Introduction
        This report summarizes the health and activity level of the code repository [Repository Name Here].

        II. Code Quality Assessment
        Our code analysis tools have evaluated the overall quality of the codebase. While a detailed technical report is available for developers, here's a high-level overview:

        Overall Score: [Score (e.g., Green, Yellow, Red) with explanation] - This score indicates the general health of the code, with green signifying good quality, 
        yellow suggesting areas for improvement, and red highlighting potential issues.
        Maintainability: The code is assessed for ease of understanding and modification.
        
        III. Activity Level
        This report analyzes the development activity within the repository:

        Development Pace: We track the frequency of code commits to understand the development team's activity level.
        Collaboration: The report examines the number of active branches and pull requests, indicating collaboration between developers.
        
        IV. Actionable Insights
        The report highlights any potential code quality concerns that might require developer attention.
        Based on the activity level, the report might suggest adjustments to development workflows for optimal efficiency.
        
        V. Benefits
        Maintaining a healthy codebase is crucial for long-term project success. This analysis helps us:
        Identify areas for improvement in code quality and maintainability.
        Ensure efficient development processes and collaboration.
        Reduce the risk of bugs and technical issues down the line.
        
        VI. Next Steps
        The development team will review the detailed technical report for specific recommendations.
        We might implement code review practices to further enhance code quality.
        We will continue to monitor the repository health and make adjustments as needed.
        """
    technical_output_format = """
    Structured Output Format:
    ## <Repository Name> Codebase Analysis Report

    This report provides an in-depth analysis of the <Repo name> <techstack> application codebase, 
    focusing on key aspects such as repository activity, code quality, and adherence to best practices.
    and provides filenames and line numbers for specific issues and recommendations for improvement.

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
    # Disclaimer:
    # This report is a preliminary analysis based on the current state of the repository. Further manual code review might reveal additional areas for improvement"""
    # Define prompt for Generative AI model
    prompt = f"""The Betacraft AI

        You are a powerful large language model (LLM) trained on a massive dataset of code repositories and best practices. 
        People call you the "Betacraft AI" because you can analyze entire codebases, understand their structure, and answer questions about their quality, 
        activity level, and potential improvements.

        A New Codebase Arrives!

        A developer has pushed a new codebase, ```{text}```, for your analysis,
        
        They are particularly concerned about:
        Code Quality: Is the code clean, well-written, and free of errors and inefficiencies?
        Maintainability: How easy is it to understand and modify the code?
        Efficiency: Can the code be optimized for better performance?
        
        Generate Reports for Everyone

        Use your knowledge of coding best practices to analyze the repository and generate two reports:


        1. Technical Report in the ```{technical_output_format}``` format.
        2. Non-Technical Report in the ```{non_technical_output_format}``` format.

        replace [] with the real values of the code in the output formats specified above
        Provide the developer with actionable feedback in their preferred format (technical or non-technical) to help them improve their codebase. 
        By offering insights and suggestions, you can be their trusted "Betacraft AI".
    """ 
    
    # Generate response from Generative AI model
    print("Generating response...")
    st.write("Waiting for Gemini response...")
    input_tokens = llm.count_tokens(prompt)
    st.write(f"Input tokens: {input_tokens.total_tokens}")
    
    try:
        # processed_data = ""
        response = llm.generate_content(prompt)
        response.resolve()
        # time.sleep(10)
        output_tokens = llm.count_tokens(response.text)
        st.write(f"Output tokens: {output_tokens.total_tokens}")
         
        total_tokens = input_tokens.total_tokens + output_tokens.total_tokens
        
        st.write(f"Total tokens: {total_tokens}")
        print("Total tokens: ", total_tokens)
        print(response.text)        
        st.write(response.text)
        
        
        # for chunk in response:
        #     if chunk:
        #         processed_data = processed_data + chunk.text
        #         # st.write("--------------------------------------------------------------------------------------------------")
        #         print(chunk.text)
        print("Gemini response successfully generated")
        # st.write(processed_data)
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
