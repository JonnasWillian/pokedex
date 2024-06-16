from pydantic import BaseModel
from typing import List

class Pokemon(BaseModel):
    name: str
    url: str

class PokemonListResponse(BaseModel):
    count: int
    next: str
    previous: str
    results: List[Pokemon]
