from pydantic import BaseModel


class Activity(BaseModel):
    hour: str
    description: str

    def __str__(self):
        return f"{self.hour} – {self.description}"


