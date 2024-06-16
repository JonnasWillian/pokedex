from pydantic import BaseModel

# class Pokemon(BaseModel):
#     count: str
#     next: str
#     previous: bool
#     results: []

class Pokemon(BaseModel):
    name: str
    url: str
    id: int = None
    types: list = []
    height: int = None
    weight: int = None
    abilities: list = []
    stats: list = []