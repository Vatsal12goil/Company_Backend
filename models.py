from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import datetime
import enum
from database import Base
from pydantic import BaseModel
from typing import Optional, List

class InteractionType(enum.Enum):
    in_person = "In-Person"
    virtual = "Virtual"
    email = "Email"
    phone = "Phone"

class IntentLevel(enum.Enum):
    high = "High"
    medium = "Medium"
    low = "Low"
    none = "None"

class Sentiment(enum.Enum):
    positive = "Positive"
    neutral = "Neutral"
    negative = "Negative"

class HCP(Base):
    __tablename__ = "hcps"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    specialty = Column(String)
    location = Column(String)
    
    interactions = relationship("Interaction", back_populates="hcp")

class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"))
    date = Column(DateTime, default=datetime.datetime.utcnow)
    interaction_type = Column(String) # Cast to string for simplicity, or use Enum
    notes = Column(Text)
    action_items = Column(Text)
    intent_level = Column(String, default="Neutral")
    sentiment = Column(String, default="Neutral")
    
    hcp = relationship("HCP", back_populates="interactions")

class FollowUp(Base):
    __tablename__ = "follow_ups"
    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"))
    scheduled_date = Column(DateTime)
    notes = Column(Text)
    status = Column(String, default="Pending")

# Pydantic Schemas for API
class HCPBase(BaseModel):
    name: str
    specialty: str
    location: str

class HCPCreate(HCPBase):
    pass

class HCPResponse(HCPBase):
    id: int
    class Config:
        from_attributes = True

class InteractionBase(BaseModel):
    hcp_id: Optional[int] = None
    interaction_type: str
    notes: str
    action_items: str = ""
    intent_level: str = "Neutral"
    sentiment: str = "Neutral"

class InteractionCreate(InteractionBase):
    pass

class InteractionUpdate(InteractionBase):
    id: int

class InteractionResponse(InteractionBase):
    id: int
    date: datetime.datetime
    class Config:
        from_attributes = True
