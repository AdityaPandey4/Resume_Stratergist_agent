import os 
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict
from services.crew_service import run_resume_crew
app = FastAPI(
    title="Resume Stratergist API",
    description="An API to process the given resume and provide a tailored Resume based on user's city using CrewAI"

)

class ResponseModel(BaseModel):
    secondary_files:List[str]
    primary_content: Dict[str, str]= Field(description="dictionary with the file name as 'New_resume.md': and its file contents")
    primary_file:List[str]
    message:str

origins = [
    "http://localhost",
    "http://localhost:8501",  # The default port for Streamlit
]
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_headers=['*'],
    allow_methods = ['*']

)
upload_dir = "resume_uploads"
result_dir = "results_dir"
os.makedirs(upload_dir, exist_ok =True)
os.makedirs(result_dir, exist_ok=True)

@app.post("/process-resume/", response_model=ResponseModel)
def process_resume(city : str = Form(...),resume_file : UploadFile = File(...)):
    
    resume_dir = os.path.join(upload_dir, resume_file.filename)
    try:
        with open(resume_dir, "wb") as buffer:
            shutil.copyfileobj(resume_file.file, buffer)
    finally:
        resume_file.file.close()

    try:
        run_resume_crew(resume_path = resume_dir, city = city, result_dir=result_dir)

        
        returned_files_dir = os.listdir(result_dir)

        if not returned_files_dir:
            raise HTTPException(status_code=500, detail="Crew process finished but no file returned")
        primary_files = ["New_resume.md","Review.md"]
        secondary_files = []
        primary_content={}
        for filename in returned_files_dir:
            if filename in primary_files:
                with open(os.path.join(result_dir,filename), 'r', encoding='utf-8') as f:
                    primary_content[filename] = f.read()

            else:
                secondary_files.append(filename)
        if "New_resume.md" not in primary_content:
            raise HTTPException(status_code=500, detail="Crew process finished but New Resume was not found")
        response_data = {
            "secondary_files":secondary_files,
            "primary_content":primary_content,
            "primary_file":primary_files,
            "message":"Completed the Process with all the files"
        }
        return response_data
    except Exception as e:
        print(f"error occured {e}")
        raise HTTPException(status_code=500, detail=str(e)) 


@app.get("/requested-files/{filename}", response_class=FileResponse)
def requested_files(filename:str):
    file_path = os.path.join(result_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(path=file_path, filename=filename)
