import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import (FileReadTool,
                            PDFSearchTool,
                            ScrapeWebsiteTool,
                            SerperDevTool,
                            FileReadTool
        )
from pydantic import BaseModel, Field
from typing import List


def run_resume_crew(resume_path : str, city : str)->str :
# --- API Keys ---
    from dotenv import load_dotenv
    load_dotenv()
    os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
    os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

    # --- LLM Setup ---
    # Using gemini-1.5-flash is a great choice for speed and capability.
    llm = LLM(
        model="gemini/gemini-1.5-flash"
        # model="gemini/gemini-2.0-pro"
    )


    # --- Tool Definitions ---
    # The PDFSearchTool is correctly configured. It will use the file_path passed at runtime.
    pdf_search_tool = PDFSearchTool(
        config=dict(
            llm=dict(
                provider="google",
                config=dict(
                    model="gemini-1.5-flash",
                ),
            ),
            embedder=dict(
                provider="huggingface",
                config=dict(
                    model="all-MiniLM-L6-v2",
                ),
            ),
        )
    )

    search_tool = SerperDevTool()
    scrape_website_tool = ScrapeWebsiteTool()
    file_read_tool = FileReadTool()

    # --- Pydantic Classes ---
    # These are well-defined and a great way to ensure structured output.
    class workexperience(BaseModel):
        role:str = Field(description="the position held in the company")
        company:str = Field(description="name of the company")
        dates:str = Field(description="Start and the end date of the employement")
        description:str = Field(description="Bulleted points about the work Carried out, key responsibilities in this role")

    class Projects(BaseModel):
        Name:str = Field(description="Name of the Project")
        description:str = Field(description="Bulleted points details about the project")
        Technologies_used : list[str] = Field(description="list of technologies used in the project")
    class Resume_analyst_json(BaseModel):
        name: str
        skills: list[str]
        experience: list[workexperience] = Field(description="A list of all detailed work experience for the resume")
        projects: list[Projects] = Field(description="list of all detaild projects from the resume")

    class Job_researcher_json(BaseModel):
        Link: str
        Description: str
        relevancy: str
        key_skills: list[str]

    class Resume_profiler_json(BaseModel):
        key_skills : list[str]
        missing_keywords : list[str]
        Actionable_Suggestions : list[str] 

    # --- Add these to your Pydantic Classes section ---

    class AuditItem(BaseModel):
        suggestion: str = Field(description="The specific suggestion made by the Resume Profiler.")
        implementation_evidence: str = Field(description="The concrete evidence or quote from the new resume that shows how the suggestion was implemented.")
        verdict: str = Field(description="A verdict on the implementation, e.g., 'SUCCESSFUL', 'PARTIALLY IMPLEMENTED', or 'NOT IMPLEMENTED'.")

    class Resume_Audit_Report_json(BaseModel):
        audit_summary: str = Field(description="A brief, one-sentence summary of the audit's findings.")
        audit_results: List[AuditItem] = Field(description="A detailed list of comparisons, validating each suggestion against the final resume.")



    # --- Agent Definitions ---

    # Resume_analyst Agent
    Resume_analyst = Agent(
        role="Senior Resume Analyst",
        goal="Meticulously extract key details like name, skills, work experience, and projects from a user's resume using the 'pdf_search_tool.",
        backstory=(
            "You are a senior Resume Analyst with exceptional attention to detail. "
            "Your expertise lies in parsing PDF resumes to extract structured information. "
            "You methodically query the resume using the `pdf_search_tool` for each piece of information required "
            "To access the resume you use the tool `pdf_search_tool` and pass two arguments"
            "the two arguments are {file_path} for the file path of the resume "
            "and your query for the 'query' arguement"
            "to ensure accuracy and completeness. You understand that your output is critical for the next agent's success."
        ),
        tools=[pdf_search_tool],
        # --- CHANGE 1: Increased max_iter to prevent hallucinations and allow self-correction ---
        max_iter=5,
        max_rpm =3,
        llm=llm,
        verbose=True
    )

    # Job Researcher Agent
    Job_researcher = Agent(
        role="Expert Job Researcher",
        goal="Find a single, highly relevant job posting for the user based on their skills and preferred city.",
        backstory=(
            "You are a highly skilled Job Researcher who excels at navigating the web to find the perfect job match. "
            "You analyze the user's profile (skills, experience) and then craft very specific search queries to find individual job postings, not just lists of jobs. "
            "You know how to use search operators like 'site:' to target specific job boards (e.g., 'site:linkedin.com/jobs/view/' or 'site:greenhouse.io'). "
            "After finding a promising link, you diligently scrape it to extract the job description. If a link leads to a list or is not a valid job post, you discard it and try the next one."
        ),
        tools=[search_tool, scrape_website_tool],
        # --- CHANGE 2: Increased max_iter and max_rpm to allow for a search-validate-scrape loop ---
        max_iter=5,
        max_rpm=5, # Allow more calls per minute for the search/scrape loop
        llm=llm,
        verbose=True
    )

    #Resume_profiler 

    Resume_profiler = Agent(
        role = "expert Resume Profiler",
        goal = "Find the Gaps in the user Resume and the selected Job and Provide key details to strengthen the user Resume ",
        backstory = (
            "You are a highly skilled Resume Profiler with exceptional attention to detail and "
            "understanding of the skills gaps by looking at a resume and the job posting"
            "Your job is identify the skill gaps in the user Resume provided by the Resume_analyst Agent "
            "and the new Job posting provided by the Job_researcher Agent and provide Key areas to focus on"
            "in the user Resume to strengthen it according to the job Posting, to make the user Resume Stand apart"
            "Your findings and suggestion should be only from the user Resume "
            "and DO NOT make any information or the skills that is not in the Resume "
            "Provide your output in a clear structured JSON"

        ),
        llm=llm,
        max_iter = 3,
        max_rpm = 3,
        verbose = True

    )

    # Resume Builder 
    Resume_builder = Agent(
        role = "Expert Resume Builder",
        goal = "Based on user original Resume and the Resume_profiler suggestion build a professional and strong resume",
        backstory = (
            "You are a expert Resume builder and have great eye for details and make a resume such that it stands out for the job postings"
            "analyse the users's original resume contents provided by Resume_analyst Agent and the gaps provided by the Resume_profiler agent"
            "use the 'Key_skills' section provided by the Resume_profiler Agent that gives the skills that are common in both users resume and job posting "
            "and emphasize more on these skills while creating a new resume."
            "take suggestion from 'Actionable_suggestion' section from Resume_profiler to add to the new resume"
            "Provide the final output in a markdown file with proper structuring of the new Resume which should be highly professional"
            "provide suggestion in '[]' brackets for the user to further enhance its resume"
            "DO NOT create any new information on your own"
            "To get more information to populate the resume use pdf_search_tool and pass two arguments"
            "the two arguments are {file_path} for the file path of the resume "
            "and your query for the 'query' arguement"
        ),
        llm = llm,
        max_iter = 5,
        max_rpm = 3,
        tools = [pdf_search_tool]

    )

    # --- Add this to your Agent Definitions section ---



    Resume_Audit_Analyst = Agent(
        role="Meticulous Resume Audit Analyst",
        goal="Rigorously verify that the final resume draft successfully incorporates all suggestions made by the Resume Profiler.",
        backstory=(
            "You are the final checkpoint in the resume enhancement pipeline. Your attention to detail is legendary. "
            "You function like a QA engineer, systematically taking each suggestion from the profiler's report and checking for its presence and proper implementation in the final resume markdown file. "
            "Your job is to provide a clear, structured, and objective report on how well the Resume Builder agent followed its instructions."
        ),
        tools=[file_read_tool], # Can read the files directly if needed
        llm=llm,
        max_iter=3,
        verbose=True
    )
    Markdown_Formatter = Agent(
        role="Markdown Formatting Specialist",
        goal="Convert structured JSON data into a beautiful, human-readable Markdown table.",
        backstory="You are a formatting expert. You take clean JSON data and transform it into perfectly structured Markdown tables. You do not analyze or change the content, you only format it.",
        llm=llm
    )


    # --- Task Definitions ---

    Resume_analyst_Task = Task(
        description=(
            "Analyze the user's resume located at '{file_path}'. "
            # --- CHANGE 3: Add forceful, non-negotiable instructions ---
            "Your mission is to act as a data extractor ONLY. **You are strictly forbidden from inventing, hallucinating, or using any prior knowledge.** "
            "Your ONLY source of information is the document provided at '{file_path}'.\n\n"
            "You MUST use the `pdf_search_tool` to find every piece of information. "
            "To do this, use the `pdf_search_tool` multiple times with specific, targeted queries. "
            "First, query for the candidate's name. "
            "Second, query for a comprehensive list of all their skills. "
            "You must populate the data structure precisely. For each work experience entry, you MUST extract:\n"
            "- The company name.\n"
            "- The job title/role.\n"
            "- The employment dates.\n"
            "- A list of all the descriptive bullet points detailing the work, responsibilities, and achievements for that role.\n"
            "Similarly, for each project, you MUST extract its name and a list of descriptive bullet points and technologies used in the project.\n"
            "Use the `pdf_search_tool` strategically. You might need to query first for the list of job titles, and then query again for the details of each specific job. "
            "Compile all this information into the required JSON format."
            "Compile all this information into a single, clean JSON object. Do not invent any information."
        ),
        expected_output="A JSON file containing the candidate's 'name', 'skills', 'experience', and 'projects' extracted directly from the resume.",
        agent=Resume_analyst,
        output_json=Resume_analyst_json,
        output_file="Resume_analyst.json"
    )

    Job_researcher_Task = Task(
        description=(
            "Using the skills and experience from the Resume Analyst's output and the user's preferred city of '{city}', find one highly relevant job posting. "
            # --- CHANGE 4: Guiding the agent to use better search strategies ---
            "1. Formulate a precise search query. Use operators like 'site:linkedin.com/jobs/view/' or 'site:greenhouse.io' to find direct job postings. For example: 'Senior Python Developer jobs in {city} site:linkedin.com/jobs/view/'.\n"
            "2. Use the `search_tool` with this query to get a list of links.\n"
            "3. From the search results, select the most promising URL that appears to be a direct job posting, not a search list.\n"
            "4. Use the `scrape_website_tool` on that single URL to get the job description text.\n"
            "5. Analyze the scraped text to create your final report. If the scrape fails or the content is not a job description, go back to step 3 and try a different link.\n"
            "The final JSON output must be strictly structured as specified."
        ),
        expected_output=(
            "A single JSON object detailing a relevant job posting, including the 'Link', a 'Description' from the website, "
            "'relevancy' explaining why it's a good match for the user, and a list of 'key_skills' that match between the user and the job."
        ),
        agent=Job_researcher,
        output_json=Job_researcher_json,
        output_file="Job_researcher.json",
        context=[Resume_analyst_Task]
    )

    Resume_profiler_task = Task(
        description = (
            "Using the Job posting details from Job_researcher Agent and details about user's Resume from the Resume_analyst Agent, identify the missing Gaps, missing keywords"
            "and provide Actionable suggestions to enhance and strengthen the user Resume, such that it would stand out as a best fit for the job"
            "use only the information that are in the resume and DO NOT make any new information or skills"
            "if the job posting require skill set or experience that the user does not have, but has skills or experience very close to it"
            "provide in the Actionable Suggestion about the way it can be best written to look very promising and close to the job posting "

        ),
        expected_output = (
            "A Single JSON object detailing the 'key_skills' explaining the key skills that are common in both user resume and job posting"
            "'missing_keywords' explaining the keywords that are not in the Resume and 'Actionable_Suggestions' providing your key insights of how to make the Resume better"
        ),
        agent = Resume_profiler,
        context =[Resume_analyst_Task, Job_researcher_Task],
        output_json = Resume_profiler_json,
        output_file = 'Resume_profiler.json'

    )
    Resume_builder_task = Task(
        description=(
            "Your final and most important mission is to **rewrite and enhance** the user's original resume to be perfectly tailored for the target job. "
            "You will receive three crucial pieces of information:\n"
            "1. The full, detailed original resume content from the `Resume_analyst` (including all bullet-point descriptions for each job and project).\n"
            "2. The specific job posting details from the `Job_researcher`.\n"
            "3. A list of actionable suggestions and keywords from the `Resume_profiler`.\n\n"

            "**Your Process MUST be as follows:**\n"
            "1. **Start with the original resume content.** Do NOT start from a blank page. Go through the original resume section by section (Summary, Experience, Projects).\n"
            "2. **For each bullet point in the original 'Experience' and 'Projects' sections, rewrite it.** Your goal is to incorporate the 'Actionable_Suggestions' and 'missing_keywords' from the `Resume_profiler`'s report. Rephrase the original points to highlight the skills and achievements most relevant to the target job description.\n"
            "3. **Enhance the 'Skills' section.** Ensure the 'key_skills' identified by the profiler are prominently featured.\n"
            "4. **Craft a new, powerful 'Summary' section.** This summary should be a concise pitch directly targeting the job, using keywords from the job description and highlighting the user's most relevant qualifications.\n"
            "5. **Preserve all original facts.** You must not change company names, dates, or the core truth of the user's work. You are only enhancing the *description* of that work.\n\n"
            "The final output must be a complete, professional resume in Markdown format, filled with detailed, rewritten descriptions. It should not be a template but a ready-to-use document."
        ),
        expected_output=(
            "A complete, professionally formatted, and fully detailed resume in a single markdown file. "
            "This resume should be a rewritten version of the original, enhanced with keywords and suggestions to align perfectly with the target job. "
            "It must include fully populated 'Experience' and 'Projects' sections with detailed, rewritten bullet points."
        ),
        agent=Resume_builder,
        # --- CHANGE: Make sure builder has access to all prior context ---
        context=[Resume_analyst_Task, Job_researcher_Task, Resume_profiler_task],
        output_file='New_resume.md'
    )

    # --- Add this to your Task Definitions section ---

    resume_audit_task = Task(
        description=(
            "You must conduct a final audit of the resume-building process. "
            "Your task is to compare the 'Actionable_Suggestions' from the `Resume_profiler`'s output against the final `New_resume.md` generated by the `Resume_builder`.\n\n"
            "Follow this process:\n"
            "1. Go through each suggestion in the `Actionable_Suggestions` list from the profiler's report.\n"
            "2. For each suggestion, meticulously scan the final `New_resume.md` to find evidence of its implementation.\n"
            "3. Create a structured JSON report based on your findings. For each suggestion, you must provide the original suggestion, the evidence you found in the resume, and a clear verdict.\n\n"
            "Note: If the builder implemented a suggestion by adding a placeholder like `[Add details here]`, this counts as a 'SUCCESSFUL' implementation, as the agent correctly identified the need for user input. Your goal is to verify the agent's work, not the user's."
        ),
        expected_output=(
            "A JSON object that strictly follows the `Resume_Audit_Report_json` schema. "
            "It must contain a list of `AuditItem` objects, where each object validates one suggestion against the final resume, providing the suggestion, evidence, and a verdict."
        ),
        agent=Resume_Audit_Analyst,
        context=[Resume_profiler_task, Resume_builder_task], # Needs output from both tasks
        output_json=Resume_Audit_Report_json,
        output_file='resume_audit_report.json'
    )

    markdown_formatting_task = Task(
        description=(
            "You will be given a JSON object containing a list of audit results. "
            "Your only job is to convert this data into a perfect 3-column Markdown table. "
            "The columns should be 'Profiler Suggestion', 'Implementation & Evidence', and 'Verdict'. "
            "Do not add any text before or after the table."
        ),
        expected_output="A single markdown file containing only a flawless, 3-column Markdown table representing the provided JSON data.",
        agent=Markdown_Formatter,
        context=[resume_audit_task], # Takes input from the JSON-producing task
        output_file="Review.md"
    )

    job_search_crew = Crew(
        agents=[Resume_analyst, Job_researcher, Resume_profiler, Resume_builder, Resume_Audit_Analyst,Markdown_Formatter],
        tasks=[Resume_analyst_Task, Job_researcher_Task, Resume_profiler_task,Resume_builder_task, resume_audit_task, markdown_formatting_task],
        process=Process.sequential,
        verbose=True
    )

    # --- Kickoff the Crew ---
    inputs = {
        "file_path": resume_path,
        "city": city  
    }
    print("## Starting the Job Search Crew...")
    results = job_search_crew.kickoff(inputs=inputs)
    print("\n## Crew work finished.")
    final_resume_filename = "New_resume.md"
    return final_resume_filename