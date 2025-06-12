from pydantic import BaseModel


class Invitation(BaseModel):
    invitation_text: str
