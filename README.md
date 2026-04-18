# AI-First CRM HCP Module – LogInteractionScreen

An intelligent CRM dashboard built for Life Science Field Representatives to log interactions with Healthcare Professionals (HCPs) using a premium Web UI and a LangGraph-powered conversational agent.

## Core Features
1.  **Dual UI Setup**: A beautiful split-screen interface displaying both a classical structured form and an advanced Conversational Chat AI side-by-side.<img width="899" height="1599" alt="WhatsApp Image 2025-12-08 at 11 39 29" src="https://github.com/user-attachments/assets/85b2c253-9c8d-4158-b72a-a1cc46a63147" />
<img width="996" height="1280" alt="Me" src="https://github.com/user-attachments/assets/dfbe811f-cebf-4307-afeb-455f25b5c967" />

2.  **LangGraph AI Agent**: The backbone of the interaction. The agent has been equipped with 5 tools:
    *   `log_interaction`: Formally records the context into the DB.
    *   `edit_interaction`: Modifies an already logged event.
    *   `search_hcp_history`: Looks up previous historical interactions given an HCP name.
    *   `schedule_follow_up`: Schedules a follow-up action.
    *   `extract_medical_insights`: An NLP simulation to parse specific medical conversational intent.
3.  **Modern Stack**: 
    *   *Backend*: FastAPI (Python), SQLAlchemy, SQLite (easily swappable to PostgreSQL), LangGraph, Groq (`llama-3.3-70b-versatile`).
    *   *Frontend*: React + Vite, Redux Toolkit, pure modern CSS utilizing Glassmorphism and the Google Inter font.

## Quick Start Guide

### 1. Backend Setup
1.  Navigate to the `backend/` folder:
    ```bash
    cd backend
    ```
2.  Create a virtual environment and install dependencies:
    ```bash
    python -m venv venv
    venv\Scripts\activate  # Windows
    # source venv/bin/activate # Mac/Linux
    pip install -r requirements.txt
    ```
3.  Set your Groq API Key: The `.env` file should contain `GROQ_API_KEY="your_token"`.
4.  Run the FastAPI server:
    ```bash
    uvicorn main:app --reload
    ```
    *The server will run on `http://localhost:8000`*.

### 2. Frontend Setup
1.  Navigate to the `frontend/` folder:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the Vite development server:
    ```bash
    npm run dev
    ```
    *The UI will be accessible on `http://localhost:5173`*.

## LangGraph Tools Demonstration

When using the interface, try typing these prompts into the AI to invoke the LangGraph tools dynamically:
1.  *"Get the history for Dr. House."* -> **Invokes `search_hcp_history`**
2.  *"I just met with Dr. House. He showed a high intent level for our new drug format. Can you log this In-Person interaction?"* -> **Invokes `log_interaction`**
3.  *"Wait, change the intent level of that last interaction to Medium."* -> **Invokes `edit_interaction`**
4.  *"Schedule a follow up for 7 days from now to give him the new samples."* -> **Invokes `schedule_follow_up`**

## Technologies Used
- LLM: `llama-3.3-70b-versatile` via **Groq**
- Framework: **LangGraph**, **FastAPI**, **React**
- State Management: **Redux**


Deployment Status
1.) Backend: https://company-backend-1-916i.onrender.com
2.) Front-End: https://aicrmproject-jc2dnkt9k-vatsals-projects-68d115a9.vercel.app/



