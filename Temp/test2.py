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
# from langchain_google_genai import ChatGoogleGenerativeAI # This import is not needed when using CrewAI's LLM class

# --- API Keys ---
# Best practice: Load from a .env file using a library like python-dotenv
# For this example, we'll continue with os.getenv
# Make sure your actual keys are set as environment variables before running the script.
os.environ["SERPER_API_KEY"] = "9a225a968bf32a2c6fd80f2d5472ded92286178c"
os.environ["GEMINI_API_KEY"] = "AIzaSyDTxEpqy79zwgOkQ0nYBg5cyGkLxeIfbPg"
os.environ["GOOGLE_API_KEY"] = "AIzaSyBZkUWjOzIYlQbDPvgjyDzmsadHKqt1HhQ"


# --- LLM Setup ---
# Using gemini-1.5-flash is a great choice for speed and capability.
llm = LLM(
    model="gemini/gemini-1.5-flash"
    # model="gemini/gemini-2.0-pro"
)
file_read_tool = FileReadTool()


Markdown_Formatter = Agent(
    role="Markdown Formatting Specialist",
    goal="Convert structured JSON data into a beautiful, human-readable Markdown table using the file_read_tool",
    backstory="You are a formatting expert. You take clean JSON data which is at {file_path} and transform it into perfectly structured Markdown tables. You do not analyze or change the content, you only format it.",
    llm=llm,
    tools = [file_read_tool]
)



markdown_formatting_task = Task(
    description=(
        "You will be given a JSON object containing a list of audit results. "
        "Go through each of the 'audit_results' section and create a a row in the table"
        "format the information in such a way that 'suggestion','implementation_evidence' and 'verdict' all comes in their respective columns only "
        "if the information is too much for any column try to wrap it into the next line but dont overflow the columns"
        "At the end of your implementation, there should be a table which contains information in their own columns and no column information overflow, or the column overlaps with other"
    ),
    expected_output="A single markdown file containing only a flawless, 3-column Markdown table representing the provided JSON data.",
    agent=Markdown_Formatter,
    output_file="Review.md"
)


job_search_crew = Crew(
    agents=[Markdown_Formatter],
    tasks=[markdown_formatting_task],
    process=Process.sequential,
    verbose=True
)

# --- Kickoff the Crew ---
# Make sure the resume.pdf file is in the same directory as your script.
resume_file_path = "./resume_audit_report.json"
if not os.path.exists(resume_file_path):
    print("Error: resume.pdf not found. Please place the resume file in the correct path.")
else:
    inputs = {
        "file_path": resume_file_path,
        "city": "Bangalore"  # Example city
    }

    print("## Starting the Job Search Crew...")
    results = job_search_crew.kickoff(inputs=inputs)

    print("\n## Crew work finished.")
    print("## Final Output:")
    print(results)
    
# import json

# with open('resume_audit_report.json', 'r') as f:
#     data = json.load(f)
# # print(data['audit_results'])
# with open("Review.md", 'w') as f2:

#     for i in data['audit_results']:
#         f2.write("**SUGGESTION**\t\t\t **VERDICT**\t\t\t **IMPLEMENTATION_EVIDENCE**")
#         f2.write(f"{i['suggestion']} \t\t\t {i['verdict']} \t\t\t { i['implementation_evidence']}")
#         f2.write("\n")
#     f2.write("Bye")