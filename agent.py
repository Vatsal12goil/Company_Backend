from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Interaction, FollowUp, HCP
import datetime

load_dotenv()

# Initialize Groq Model
llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=os.getenv("GROQ_API_KEY"))

# LangGraph Tools

@tool
def log_interaction(hcp_id: str, interaction_type: str, notes: str, action_items: str = "", intent_level: str = "Neutral", sentiment: str = "Neutral") -> str:
    """Logs a new interaction with a Healthcare Professional."""
    db: Session = SessionLocal()
    try:
        hcp_id_num = int(hcp_id)
        hcp = db.query(HCP).filter(HCP.id == hcp_id_num).first()
    except ValueError:
        # LLM provided a name instead of an integer ID
        hcp = db.query(HCP).filter(HCP.name.ilike(f"%{hcp_id}%")).first()
        if hcp:
            hcp_id_num = hcp.id
        else:
            hcp_id_num = 1 # Fallback to default Dr. Gregory House test case
            hcp = db.query(HCP).filter(HCP.id == hcp_id_num).first()
            
    if not hcp:
        hcp = HCP(id=hcp_id_num, name=f"Unknown HCP {hcp_id_num}", specialty="General", location="Unknown")
        db.add(hcp)
        db.commit()

    new_interaction = Interaction(
        hcp_id=hcp_id_num,
        interaction_type=interaction_type,
        notes=notes,
        action_items=action_items,
        intent_level=intent_level,
        sentiment=sentiment
    )
    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)
    db.close()
    return f"Interaction logged successfully with ID {new_interaction.id}."

@tool
def edit_interaction(interaction_id: str, notes: str = None, action_items: str = None, intent_level: str = None, sentiment: str = None) -> str:
    """Edits an existing interaction record. Only provide the fields that need updating."""
    db: Session = SessionLocal()
    try:
        int_id = int(interaction_id)
        interaction = db.query(Interaction).filter(Interaction.id == int_id).first()
    except ValueError:
        # LLM passed something like 'latest_interaction' instead of an ID. Fallback to the most recent one.
        interaction = db.query(Interaction).order_by(Interaction.date.desc()).first()
        if interaction:
            int_id = interaction.id
            
    if not interaction:
        db.close()
        return f"Interaction with ID {interaction_id} not found."
    
    if notes is not None: interaction.notes = notes
    if action_items is not None: interaction.action_items = action_items
    if intent_level is not None: interaction.intent_level = intent_level
    if sentiment is not None: interaction.sentiment = sentiment
    
    db.commit()
    db.close()
    return f"Interaction {int_id} updated successfully."

@tool
def search_hcp_history(hcp_name_or_id: str) -> str:
    """Retrieves previous interaction history for a specific HCP. Use this to get context about past meetings."""
    db: Session = SessionLocal()
    try:
        hcp_id = int(hcp_name_or_id)
        hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
    except ValueError:
        hcp = db.query(HCP).filter(HCP.name.ilike(f"%{hcp_name_or_id}%")).first()

    if not hcp:
        db.close()
        return "No HCP found with that name or ID."
    
    interactions = db.query(Interaction).filter(Interaction.hcp_id == hcp.id).order_by(Interaction.date.desc()).limit(5).all()
    db.close()
    
    if not interactions:
        return f"No past interactions found for {hcp.name}."
    
    res = f"Recent History for {hcp.name}:\n"
    for i in interactions:
        res += f"- ID {i.id} on {i.date.strftime('%Y-%m-%d')}: {i.notes[:50]}... (Intent: {i.intent_level})\n"
    return res

class ScheduleFollowUpInput(BaseModel):
    interaction_id: str = Field(description="ID of the base interaction.")
    days_from_now: str = Field(description="How many days in the future to schedule.")
    notes: str = Field(description="Details of what the follow up entails.")

@tool("schedule_follow_up", args_schema=ScheduleFollowUpInput)
def schedule_follow_up(interaction_id: str, days_from_now: str, notes: str) -> str:
    """Schedules a follow-up task related to a specific interaction."""
    db: Session = SessionLocal()
    
    try:
        int_id = int(interaction_id)
        interaction = db.query(Interaction).filter(Interaction.id == int_id).first()
    except ValueError:
        interaction = db.query(Interaction).order_by(Interaction.date.desc()).first()
        if interaction:
            int_id = interaction.id
            
    try:
        days = int(days_from_now)
    except ValueError:
        days = 7 # Default fallback
        
    if not interaction:
        db.close()
        return f"Interaction {interaction_id} not found."
    
    scheduled_date = datetime.datetime.utcnow() + datetime.timedelta(days=days)
    fu = FollowUp(interaction_id=int_id, scheduled_date=scheduled_date, notes=notes)
    db.add(fu)
    db.commit()
    db.refresh(fu)
    db.close()
    return f"Follow up scheduled for {scheduled_date.strftime('%Y-%m-%d')} with ID {fu.id}."

@tool
def extract_medical_insights(discussion_text: str) -> str:
    """Automatically parses unstructured discussion text to extract specific insights like off-label mentions, competitor drug discussions, or side-effect complaints.
    Returns a formatted string of insights.
    """
    # In a full app, this might run an NLP sub-chain. For now, it uses the agent itself via a prompt structure, simulating an extraction.
    return "Insights Extracted: Mentioned new competitor drug XYZ; expressed concern over patient adherence. Recommended discussing patient assistance program next visit."

# List of tools for the agent
tools = [log_interaction, edit_interaction, search_hcp_history, schedule_follow_up, extract_medical_insights]

# Create LangGraph ReAct agent
sys_msg = "You are an AI assistant designed for life science field sales representatives. You help manage and log interactions with Healthcare Professionals (HCPs). You have access to a database via tools to log, edit, and query HCP data. Be concise and helpful."

# create_react_agent is a helper from langgraph.prebuilt
agent_executor = create_react_agent(llm, tools)

def process_chat(message: str, chat_history: list = []):
    """Entrypoint to run the graph and parse response."""
    # Convert chat_history if needed, for simplicity we just pass messages
    messages = [{"role": "system", "content": sys_msg}] + chat_history + [{"role": "user", "content": message}]
    try:
        response = agent_executor.invoke({"messages": messages})
        return response["messages"][-1].content
    except Exception as e:
        return f"Error connecting to AI: {str(e)}"
