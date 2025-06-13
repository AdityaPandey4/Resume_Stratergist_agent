import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import (FileReadTool,
                            PDFSearchTool,
                            ScrapeWebsiteTool,
                            SerperDevTool
        )

from pydantic import BaseModel
# Assuming you are using Google Gemini via Langchain/CrewAI. Adjust import if using a different provider.
# from langchain_google_genai import ChatGoogleGenerativeAI # Or use from crewai import LLM and configure

# --- API Keys ---
# Ensure these are set in your environment or replaced with actual keys.
# It's best practice to use environment variables outside the script.
# Example: export GOOGLE_API_KEY='...'
# Example: export SERPER_API_KEY='...'
# The keys you have included seem like placeholders or test keys.
# Make sure to use your actual, valid keys.
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "AIzaSyBZkUWjOzIYlQbDPvgjyDzmsadHKqt1HhQ")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY", "9a225a968bf32a2c6fd80f2d5472ded92286178c")
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "AIzaSyDTxEpqy79zwgOkQ0nYBg5cyGkLxeIfbPg")


# --- LLM Setup ---
# Define the LLM model to be used by the agents.
# Using ChatGoogleGenerativeAI as you configured Gemini in the PDF tool.
llm = LLM(model = "gemini/gemini-1.5-flash") # gemini-2.0-flash might be too fast/less capable for complex tasks


# --- Tool Definitions ---
# Define tools using the instantiated objects.
pdf_search_tool = PDFSearchTool(
    # pdf_path="./resume.pdf",
    # encoding='latin-1', # Consider if necessary, utf-8 is more common
    config=dict(
        llm=dict(
            provider="google",
            config=dict(
                model="gemini-1.5-flash", # Use gemini-pro or compatible model for better results
                # temperature=0.1,
            ),
        ),
        embedder=dict(
            provider="huggingface",
            config=dict(
                model="all-MiniLM-L6-v2",
                # task_type="retrieval_document",
            ),
        ),
    )
)

# file_read_tool is useful for general text files, pdf_search_tool is for PDFs
# file_read_tool = FileReadTool() # Not strictly needed if only processing PDF

# Correctly use SerperDevTool for searching
search_tool = SerperDevTool()

# ScrapeWebsiteTool for extracting content from URLs
scrape_website_tool = ScrapeWebsiteTool()

# --- pydantic classes ---

class Resume_analyst_json(BaseModel):
    name : str
    skills : list
    experience : list
    projects : list
    
class Job_researcher_json(BaseModel):
    Link : str
    Description : str
    relevancy : str 
    key_skills : list

# --- Agent Definitions ---

# Resume_analyst
Resume_analyst = Agent(
    role = "Senior Resume Analyst",
    goal = "To extract key details from the resume of the user",
    backstory = ("You are a senior Resume analyst and an expert at your work"
                "You find and extract key details from the user resume, key details like"
                "Skills , experience, Courses, Projects "
                "To access the resume you use the tool `pdf_search_tool` and pass two arguments"
                "the two arguments are {file_path} for the file path of the resume "
                "and your query for the 'query' arguement (example: 'what are the skills in the resume? or 'what are the experiences mentioned in the resume etc)"
                "be sure to extract all the key information from the resume that are neccessary for you to know to search for a new job"
                "provide a final JSON file in the format of "
                ''' {{
                name : Name in the resume,
                skills : All the skills mentioned in the resume
                experience : All the Experiences mentioned in the resume,
                projects : All the projects mentioned in the resume  
                }}'''
    ),
    tools = [pdf_search_tool],
    max_iter =1,
    # max_rpm = 3,
    llm=llm

)



#dummy agent

# dummy_agent = Agent(
#     role = "Resume summarization expert",
#     goal = "provide a summary of the Resume content",
#     backstory = (
#         "You are a Resume summarization expert and provide concise summary of the information on the resume"
#         "the Resume analyst provides you the result of the resume content extraction, based on that you create the summary"
#     ),
#     llm = llm,
#     max_iter = 1,
    
# )

# Job Researcher Agent

Job_researcher = Agent(
    role = "Job Researcher Specialist",
    goal = "To find user relevant jobs based on the Skills and city of the user",
    backstory = (
        "You are a highly skilled Job Researcher and have the expertise to search through the Internet "
        "and find jobs that are most relevant based on users skills set"
        "You look into the output given by the Resume_analyst which is a JSON file and look at the 'skills' section 'experience' section "
        "to determine the most relevant search words to search for the job "
        "You can access the internet using search_tool"
        "Once you find the job posting relevant to user skill set and experience,"
        "Use the scrape_website_tool to extract key informations about the job posting."
        "Extract key details like 'Location', 'Prefered skills', 'Key Responsibility' or 'skill Required' "
        "which will allow you to understand the Location of the Job, What is the Job posting Description(from 'Key Responsibility'),"
        "What are the skill required for the job(from 'Prefered skills' or 'Skill Required')"
        "After you understand it, you provide a detailed understanding of the job and how this job description is "
        "suited for the user and the key skills that are matched in the job description"
        "provide your output in a JSON file"
        "You need to map the skills that are present in user Resume, given by Resume_analyst and what skills are required for the job that you searched"
        "The format of the JSON file should be "
        '''
        {{
            Link : The website link of the Job Posting 
            Description : Your understanding of the job description
            relevancy : How the job is relevant to the user, based on the job description
            Key_skills : Key skills of the user that were matched based on the job description 
        }}
        '''

    ),
    tools = [search_tool, scrape_website_tool],
    llm = llm,
    # max_iter = 3,
    max_rpm = 3


)

## Job Researcher Agent
# Job_Researcher = Agent (
#     role="Tech Job Researcher",
#     goal="Find the most relevant job opportunities based on the user's resume skills and location.",
#     backstory=(
#         "You are a highly skilled Tech Job Researcher with an eye for detail."
#         " Your primary goal is to analyze a user's resume, identify key skills,"
#         " and then use online search tools to find relevant job postings."
#         " You are adept at crafting effective search queries and sifting through results."
#         " Once promising job links are found, you use website scraping tools to extract"
#         " the full job description text."
#         " You will read the resume using the `pdf_search_tool`, pass the {file_path} as the argument for the file path to understand the user's profile."
#         " To use the pdf_search_tool effectively pass your query in the 'query' argument (example:'what are the skills defined in the resume' or 'what projects are in the resume') "
#         " Use the `search_tool` to find job postings based on extracted skills and location."
#         " For each promising link found by the search tool, use the `scrape_website_tool`"
#         " to get the detailed job description."
#         " Your output should be a summary of the best job matches, including key details"
#         " extracted from the scraped descriptions."
#     ),
#     tools=[pdf_search_tool, search_tool, scrape_website_tool], # Provide the tools it needs
#     llm=llm, # Assign the defined LLM
#     max_iter=5, # Increased iterations might be needed for search/scrape loop
#     max_rpm=3 # Be cautious with RPM, might be too restrictive for external calls
# )

# # Resume Profiler Agent
# Resume_Profiler = Agent (
#     role="Resume Profiler Expert",
#     goal="Analyze the user's resume and compare it against specific job descriptions to provide tailored improvement suggestions.",
#     backstory=(
#         "You are a top-tier Resume Profiler."
#         " You receive the user's resume and detailed job descriptions"
#         " found by the Job Researcher."
#         " Your expertise lies in identifying alignment gaps, highlighting strengths,"
#         " and pinpointing areas in the resume that can be optimized with keywords"
#         " and phrasing from the job descriptions for better ATS and recruiter visibility."
#         " You will provide a structured report with actionable suggestions for the Resume Builder."
#     ),
#     tools=[pdf_search_tool], # Needs access to the resume
#     llm=llm,
#     max_iter=3,
#     max_rpm=3
# )

# # Resume Builder Agent
# Resume_Builder = Agent (
#     role="Tailored Resume Builder",
#     goal="Generate an updated resume draft incorporating feedback from the Resume Profiler and aligning it with specific job requirements.",
#     backstory=(
#         "You are a skilled Resume Builder."
#         " You take the original resume content (via `pdf_search_tool`), job description summaries,"
#         " and the detailed improvement suggestions from the Resume Profiler."
#         " Your task is to rewrite and restructure sections of the resume to create a compelling"
#         " application document that strongly resonates with the target job descriptions."
#         " You must maintain the user's core experience and qualifications while enhancing"
#         " relevance, clarity, and keyword density based on the provided input."
#         " The final output should be the text content of the revised resume."
#     ),
#     tools=[pdf_search_tool], # Needs access to the original resume
#     llm=llm,
#     max_iter=3,
#     max_rpm=3
# )


# # --- Task Definitions ---

Resume_analyst_Task = Task(
    description = (
        "Analyse the user resume for key details like skills, experience, projects etc"
        "Provide a well structured JSON file for the key findings"
        "as your output will be given to the next agent"
    ),
    expected_output = "JSON file with all the key information ",
    agent = Resume_analyst,
    output_json = Resume_analyst_json,
    output_file = "Resume_analyst.json"
)

# dummy_agent_Task = Task(
#     description = (
#         "provide a concise summary on the contents of the user resume"
#         "based on the results provided by the Resume_analyst agent"
#     ),
#     expected_output= (
#         "Summary of the resume based on the Resume analyst agent results"

#     ),
#     context = [Resume_analyst_Task],
#     agent = dummy_agent
# )

#job Researcher Task 

Job_researcher_Task = Task(
    description = (
        "Analyse the user skills set and experience given by the Resume_analyst agent"
        "and based on the 'skills' section and {city} of the user, find the most suited and relevant job posting"
        "use search_tool to access the internet and find the job posting"
        "Once the job posting is found, understand the job posting and provide a detailed description "
        "of the job decription, relevancy, and the skills matched in a properly structure JSON format"
        "The Final JSON file should follow the following structure STRICTLY"
        '''
        {{
            Link : The website link of the job posting 
            Description : Job description provided in the job posting 
            relevancy : How the job is relevant to the user, based on the job description, explain it in terms of user's skills or past experiences
            Key_skills : Key skills of the user that were matched based on the job description 
        }}
        '''


    ),
    agent = Job_researcher,
    expected_output = "Properly structure JSON output with all the information",
    output_json = Job_researcher_json,
    output_file = "Job_researcher.json",
    context = [Resume_analyst_Task]
)

# job_research_task = Task(
#     description=(
#         "Analyze the user's resume using `pdf_search_tool` to understand their skills and experience.\n"
#         "Based on the skills identified and the provided location '{city}', use the `search_tool` to find relevant tech job postings.\n"
#         "Craft effective search queries like 'Python Developer jobs in Bangalore' or '{{skill}} {{job_title}} jobs in {city}'.\n"
#         "Find at least 5 promising job posting URLs.\n"
#         "For each promising URL, use the `scrape_website_tool` to extract the full job description text.\n"
#         "Summarize the key requirements, qualifications, and responsibilities for each job.\n"
#         "Provide the extracted summaries and original URLs."
#         "Output format: A list of found jobs, each with URL and summarized description."
#         "Ensure you identify key skills needed for each job from the scraped text."
#     ),
#     expected_output=(
#         "A markdown formatted list of at least **5 relevant job opportunities**, each entry including:\n"
#         "- Job title\n"
#         "- Company name\n"
#         "- Location (as per listing)\n"
#         "- A concise summary of key job requirements and responsibilities (extracted from scraped text)\n"
#         "- Key skills required for the job (extracted from scraped text)\n"
#         "- Job listing URL\n\n"
#         "Example:\n\n"
#         "## Found Jobs:\n\n"
#         "1.  **Job Title:** Senior Software Engineer\n"
#         "    **Company:** TechCorp\n"
#         "    **Location:** Bangalore, India\n"
#         "    **Summary:** Requires 5+ years experience, building scalable backend services, REST APIs, microservices architecture. Needs strong Python, Django, SQL skills. Experience with AWS a plus.\n"
#         "    **Required Skills:** Python, Django, SQL, Microservices, REST API, AWS\n"
#         "    **URL:** https://jobboard.com/techcorp/senior-swe-bangalore\n\n"
#         "2.  ...\n"
#     ),
#     tools=[pdf_search_tool, search_tool, scrape_website_tool],
#     agent=Job_Researcher,
#     output_file='found_jobs.md' # Optional: Save output to a file
# )

# resume_profiling_task = Task(
#     description=(
#         "Read the user's resume using `pdf_search_tool`.\n"
#         "Analyze the job summaries and required skills provided by the Job Researcher (from the previous task).\n"
#         "Compare the skills and experience in the resume to the requirements of the target jobs.\n"
#         "Identify areas where the resume can be strengthened to match the job descriptions.\n"
#         "Generate specific, actionable suggestions for the Resume Builder.\n"
#         "Focus on:\n"
#         "- Which sections need modification (Summary, Experience, Skills)?\n"
#         "- What keywords from job descriptions should be added or emphasized?\n"
#         "- How existing bullet points in experience can be rephrased to highlight relevant achievements?\n"
#         "- Suggestions for quantifiable results where possible.\n"
#         "- Any formatting or structural recommendations for ATS compliance."
#     ),
#     expected_output=(
#         "A detailed **Resume Improvement Report** in markdown format, structured as follows:\n\n"
#         "## Resume Improvement Report\n\n"
#         "**Target Jobs Analysis:** (Briefly mention the key requirements from the analyzed jobs)\n\n"
#         "**Strengths Identified in Current Resume:** (Based on comparison)\n\n"
#         "**Gaps/Areas for Improvement:** (Skills or experiences mentioned in jobs but less prominent in resume)\n\n"
#         "**Specific Modification Suggestions:**\n"
#         "- **Summary/Objective:** (Suggested phrasing or focus)\n"
#         "- **Skills Section:** (Keywords to add or emphasize based on job requirements)\n"
#         "- **Experience Section:** (Suggestions for specific bullet points to rephrase, add metrics, or highlight technologies relevant to jobs. Refer to original experience points if possible.)\n"
#         "- **Other Sections (Education, Projects, etc.):** (Any relevant suggestions)\n\n"
#         "**ATS Optimization Tips:** (General or specific tips)\n\n"
#         "This report will guide the Resume Builder in tailoring the resume."
#     ),
#     tools=[pdf_search_tool],
#     context = [job_research_task],
#     agent=Resume_Profiler,
#     output_file='resume_profiling_report.md' # Optional: Save output
# )

# # IMPORTANT: Generating a *physical* PDF file directly from an LLM agent is complex and usually requires
# # integrating with external libraries or services (like ReportLab in Python).
# # For this project, it's more feasible for the agent to generate the *text content* of the polished resume,
# # perhaps in a structured format like Markdown, which you can then manually or programmatically convert to PDF.
# resume_building_task = Task(
#     description=(
#         "Receive the original resume content (using `pdf_search_tool`), the job summaries, and the Resume Improvement Report.\n"
#         "Synthesize all the information to generate a new, tailored resume draft.\n"
#         "Apply the suggestions from the Resume Improvement Report to enhance the resume's relevance to the target jobs.\n"
#         "Ensure the core facts (employment history, education, projects) from the original resume are retained.\n"
#         "Focus on incorporating keywords, tailoring bullet points in the experience section,"
#         " and crafting a relevant summary or objective based on the target jobs.\n"
#         "Format the output as a professional-looking resume draft in markdown text.\n"
#         "Do NOT attempt to generate a PDF file directly. Output the text content only."
#     ),

#     expected_output=(
#         "The complete text content of a professionally formatted resume draft in markdown.\n"
#         "The resume should be tailored towards the identified job opportunities, incorporating keywords and suggestions from the profiling report.\n"
#         "It should include standard resume sections like:\n"
#         "- Contact Information\n"
#         "- Summary/Objective\n"
#         "- Skills\n"
#         "- Work Experience (with tailored bullet points)\n"
#         "- Education\n"
#         "- Projects (if applicable)\n"
#         "- Awards/Certifications (if applicable)\n\n"
#         "Example Markdown Resume:\n\n"
#         "# Your Name\n\n"
#         "**Phone:** (123) 456-7890 | **Email:** your.email@example.com | **LinkedIn:** linkedin.com/in/yourprofile | **GitHub:** github.com/yourprofile\n\n"
#         "## Summary\n\n"
#         "Highly motivated [Your Role] with X years of experience in [Area relevant to job]... (Tailored using keywords)\n\n"
#         "## Skills\n\n"
#         "**Languages:** Python, Java, C++ (Emphasize job-relevant skills)\n"
#         "**Frameworks:** Django, Flask, Spring Boot (Add relevant ones)\n"
#         "**Tools:** Docker, Kubernetes, AWS (As needed by jobs)\n\n"
#         "## Work Experience\n\n"
#         "**Company Name**, City, State | Your Title | Dates of Employment\n"
#         "- Achieved [Quantifiable result] by implementing [Action/Technology relevant to job]...\n"
#         "- Collaborated with team to develop [Feature] using [Job-relevant tech stack]...\n"
#         "(Tailor bullet points based on profiling report)\n\n"
#         "## Education\n\n"
#         "Degree, Major, University Name, Graduation Date\n\n"
#         "## Projects\n\n"
#         "**Project Name:** (Brief description and technologies used - highlight job relevance)\n"
#     ),
#     tools=[pdf_search_tool],
#     context = [resume_profiling_task],
#     agent=Resume_Builder,
#     output_file='tailored_resume_draft.md' # Optional: Save output
# )

# --- Crew Definition ---
job_search_crew = Crew(
    agents=[Resume_analyst, Job_researcher],#Job_Researcher, Resume_Profiler, Resume_Builder,dummy_agent
    tasks=[Resume_analyst_Task,Job_researcher_Task], #job_research_task, resume_profiling_task, resume_building_task,dummy_agent_Task
    process=Process.sequential, # Tasks run in order
    verbose=True, # See the agents' thought process
    # memory=True # Enable memory for better context sharing between tasks if needed
)


# --- Kickoff the Crew ---
resume_file_path = "./resume.pdf" # Make sure this file exists
# Define inputs for the tasks. The first task takes the inputs directly.
# Subsequent tasks receive outputs from the previous task implicitly.
inputs = {
    "file_path": resume_file_path,
    "city": "bangalore" # Example input for location
}

print("## Starting the Job Search and Resume Tailoring Crew...")
results = job_search_crew.kickoff(inputs=inputs)

print("\n## Crew work finished.")
print("## Final Tailored Resume Draft (in Markdown):")
print(results) # The output of the last task is returned by kickoff

# You can also read the output files if saved:
# try:
#     with open('found_jobs.md', 'r') as f:
#         print("\n--- Found Jobs ---\n")
#         print(f.read())
#     with open('resume_profiling_report.md', 'r') as f:
#         print("\n--- Resume Profiling Report ---\n")
#         print(f.read())
#     with open('tailored_resume_draft.md', 'r') as f:
#         print("\n--- Tailored Resume Draft ---\n")
#         print(f.read())
# except FileNotFoundError:
#     print("\nOutput files not found. Check crew execution logs.")