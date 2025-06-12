from pydantic import BaseModel


class Place(BaseModel):
    name: str
    address: str
    rating: str