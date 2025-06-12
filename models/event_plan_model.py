from typing import List
from pydantic import BaseModel
from models.activity_model import Activity

class EventPlan(BaseModel):
    comment_from_assistant: str
    venue_name: str
    venue_address: str
    schedule: List[Activity]
    activities: List[str]

