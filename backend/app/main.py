import os 
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from services.crew_service import run_resume_crew
app = FastAPI(
    title="Resume Stratergist API",
    description="An API to process the given resume and provide a tailored Resume based on user's city using CrewAI"

)

origins = ["https://resume-stratergist-agent.onrender.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_headers=['*'],
    allow_methods = ['*']

)

@app.post("/process-resume", response_class=FileResponse)
def process_resume(city : str = Form(...),resume_file : UploadFile = File(...)):
    upload_dir = "resume_uploads"
    os.makedirs(upload_dir, exist_ok =True)
    resume_dir = os.path.join(upload_dir, resume_file.filename)
    try:
        with open(resume_dir, "wb") as buffer:
            shutil.copyfileobj(resume_file.file, buffer)
    finally:
        resume_file.file.close()

    try:
        result_file = run_resume_crew(resume_path = resume_dir, city = city)

        if not os.path.exists(result_file):
            return HTTPException(status_code=500, detail="Crew process completed, file not recived")
        return FileResponse(path=result_file, filename=os.path.basename(result_file),
        media_type='text/markdown')

    except Exception as e:
        print(f"error occured {e}")
        HTTPException(status_code=500, detail=str(e)) 



