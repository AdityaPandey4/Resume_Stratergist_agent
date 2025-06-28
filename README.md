
# 🤖 AI Resume Strategist

An end-to-end agentic workflow powered by **CrewAI** that takes a user's resume and a desired job city, and returns a tailored resume optimized to stand out for relevant job descriptions. This project demonstrates a sophisticated multi-agent system, a robust backend API, and a clean user interface, all containerized with Docker.

## 🚀 Live Demo

![Demo GIF of the Application](httpsd://i.imgur.com/your-demo-gif.gif)
*(Recommendation: Record a short GIF of your application in action and upload it to a site like Imgur to embed it here. It makes a huge difference!)*

---

## ✨ Project Goal & Vision

The primary goal of this project is to automate the tedious and time-consuming process of tailoring a resume for each job application. By leveraging a team of specialized AI agents, the **Resume Strategist** handles everything from skill extraction and job searching to deep analysis and content rewriting. This showcases the power of AI agentic workflows to create tangible, high-value results in a real-world scenario.

## 🧠 CrewAI & Multi-Agent System

This project is built around a sophisticated multi-agent system managed by the **CrewAI** framework. Each agent has a distinct role, set of tools, and a specific goal, working in a sequential pipeline to build upon the work of the previous agent.

### The Agentic Crew

1.  **📄 Resume Analyst (`Resume_analyst`)**
    *   **Goal:** Meticulously parse the user's PDF resume.
    *   **Output:** A structured JSON object containing the user's name, skills, and detailed descriptions of their work experience and projects. This rich, structured data is the foundation for the entire workflow.

2.  **🔍 Job Researcher (`Job_researcher`)**
    *   **Goal:** Find a single, highly relevant job posting based on the user's skills and desired city.
    *   **Output:** A JSON object with the job description, URL, and key skills required for the role. It is prompted to use advanced search queries to find individual job posting pages, not just job board lists.

3.  **📊 Resume Profiler (`Resume_profiler`)**
    *   **Goal:** Perform a gap analysis between the user's resume and the target job description.
    *   **Output:** A Markdown report (`Review.md`) detailing missing keywords, strengths, and actionable suggestions for improving the resume.

4.  **✍️ Resume Builder (`Resume_builder`)**
    *   **Goal:** Rewrite and enhance the original resume content based on the Profiler's suggestions.
    *   **Output:** The final, tailored resume as a Markdown file (`New_resume.md`), rephrasing bullet points and adding a targeted summary to align with the job description.

This structured, multi-agent approach ensures a high-quality, detailed output that a single, monolithic agent would struggle to achieve.

---

## 🏗️ Architecture & System Design

The application is designed as a modern, scalable client-server system, fully containerized with Docker for consistency and ease of deployment.

![Architecture Diagram](httpsd://i.imgur.com/your-architecture-diagram.png)
*(Recommendation: Use a tool like diagrams.net or Excalidraw to create a simple architecture diagram and link it here.)*

### Backend (FastAPI)

*   **Framework:** Built with **FastAPI**, a high-performance Python web framework.
*   **API Structure:**
    *   `POST /process-resume/`: The main endpoint that accepts a resume (PDF) and a city (form data). It orchestrates the entire CrewAI workflow in the background. It returns a JSON response containing the content of the primary output files (`New_resume.md`, `Review.md`) and a list of secondary JSON artifacts.
    *   `GET /results/{run_id}/{filename}`: A dynamic endpoint to fetch any of the secondary JSON files generated during the run, allowing the user to inspect the intermediate outputs.
*   **Asynchronous:** Leverages FastAPI's `async` capabilities to handle requests efficiently.
*   **Pydantic Models:** Uses Pydantic for robust data validation and clear API schema definition, visible in the automatic `/docs`.

### Frontend (Streamlit)

*   **Framework:** Built with **Streamlit**, a fast and intuitive Python library for creating data apps.
*   **User Interface:** Provides a clean, multi-step interface for file uploads and text input.
*   **Dynamic Results:** After processing, it immediately displays the tailored resume and AI review using tabs. It also includes an expandable section with a dropdown menu to dynamically fetch and display the technical JSON outputs from the backend on demand.
*   **State Management:** Uses `st.session_state` to maintain the application's state across user interactions, such as storing the `run_id` and the list of generated files.

### Containerization (Docker)

*   **`Dockerfile`:** Separate, optimized Dockerfiles for both the backend and frontend services, ensuring clean and reproducible builds.
*   **`docker-compose.yml`:** A single Docker Compose file to define, build, and orchestrate the entire multi-container application with one command.
*   **Key Features:**
    *   Uses multi-stage best practices to keep image sizes small.
    *   Leverages volumes for live-reloading during development.
    *   Uses a shared Docker network for seamless communication between the frontend and backend containers.
    *   Manages secrets securely using `.env` files.

---

## 🛠️ How to Set Up and Run Locally

This project is fully containerized, so the only prerequisite is **Docker**.

1.  **Prerequisites:**
    *   [Docker](httpsd://www.docker.com/get-started/) installed and running on your machine.

2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/resume-strategist-app.git
    cd resume-strategist-app
    ```

3.  **Set Up Environment Variables:**
    *   Navigate to the `backend` directory.
    *   Create a file named `.env` by copying the example:
        ```bash
        cp backend/.env.example backend/.env
        ```
    *   Edit the `backend/.env` file and add your secret API keys:
        ```
        SERPER_API_KEY="your_serper_key_here"
        GEMINI_API_KEY="your_gemini_key_here"
        ```

4.  **Build and Run with Docker Compose:**
    *   From the **root directory** of the project, run the following command:
        ```bash
        docker-compose up --build
        ```
    *   This will build the Docker images for both the frontend and backend and start the services. The initial build may take a few minutes.

5.  **Access the Application:**
    *   **Frontend:** Open your web browser and navigate to `http://localhost:8501`.
    *   **Backend API Docs:** You can explore the API documentation at `http://localhost:8000/docs`.

6.  **Alternative Approach**
    *   One can also set it up using simple commands for the Frontend and Backend seperately.
        * Install the required libraries for the Backend and Frontend using :
        ```bash 
        pip install -r requirements
        ```
        for both Backend and Frontend, Besure to `cd` into the Frontend directory for Frontend requirements and in the Backend directory for the Backend requirements
        * Run Two terminals, One for the Backend and one for the Frontend, and then run the following Commands:
        
        **Frontend:**
        ```bash
        streamlit run app.py
        
        ```
        **Backend:**
        ```bash 
        uvicorn main:app --host 0.0.0.0 --port 8000 --reload

        ```
---

## 💡 Skills Showcase

This project demonstrates a wide range of skills essential for a modern AI Engineer or Backend Developer:

*   **AI & Machine Learning:**
    *   **Agentic Workflows:** Deep understanding of designing, implementing, and orchestrating multi-agent systems using CrewAI.
    *   **Prompt Engineering:** Crafting detailed, role-specific prompts and goals for each agent to ensure high-quality, predictable outputs.
    *   **LLM Integration:** Experience with integrating and utilizing powerful language models (e.g., Gemini) for complex reasoning and generation tasks.
    *   **Tool Usage:** Integrating external tools (Web Search, PDF Reading) into an agentic framework.

*   **Backend Development & Architecture:**
    *   **API Design:** Proficiency in designing and building robust, scalable REST APIs with FastAPI.
    *   **Asynchronous Programming:** Knowledge of `async/await` patterns in Python for building non-blocking, high-performance services.
    *   **System Design:** Ability to architect a decoupled, client-server application.
    *   **Data Validation:** Using Pydantic for creating clear data contracts and ensuring data integrity.

*   **DevOps & Deployment:**
    *   **Containerization:** Expertise in containerizing applications with **Docker**, creating reproducible and isolated environments.
    *   **Orchestration:** Using **Docker Compose** to manage a multi-service application stack.
    *   **CI/CD Mindset:** Building a project with clear separation of concerns, environment variables for secrets, and a focus on reproducible builds, which are foundational for continuous integration and deployment pipelines.

*   **Frontend Development:**
    *   **Rapid Prototyping:** Ability to quickly build interactive and user-friendly web interfaces for AI applications using Streamlit.
    *   **API Consumption:** Experience in connecting a frontend application to a backend API to fetch and display data dynamically.