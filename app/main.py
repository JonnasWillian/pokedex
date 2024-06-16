from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from app.models import Pokemon
from app.schemas import PokemonListResponse
from app.utils import fetch_pokemon_data
from pydantic import BaseModel
from typing import List 
import httpx
import logging

class Ability(BaseModel):
    name: str
    url: str

class Pokemon(BaseModel):
    name: str
    abilities: List[Ability]
    weight: int
    url: str

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Configurar CORS
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def fetch_pokemon_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


BASE_URL = "https://pokeapi.co/api/v2/pokemon"

@app.get("/pokemon")
async def get_pokemon():
    try:
        url = BASE_URL
        data = await fetch_pokemon_data(url)
        return data  # Retorna diretamente os dados da API
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="Service unavailable") from e
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="HTTP error") from e
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Internal server error", "detail": str(e)})


@app.get("/pokemon/{name}", response_model=Pokemon)
async def get_pokemon_details(name: str = Path(..., title="The name of the Pokemon to retrieve")):
    url = f"{BASE_URL}/{name}"
    
    try:
        data = await fetch_pokemon_data(url)
        
        # Validar os dados antes de criar a instância de Pokemon
        if 'name' in data and 'abilities' in data and 'weight' in data and 'height' in data:
            abilities = [
                Ability(name=ability['ability']['name'], url=ability['ability']['url'])
                for ability in data['abilities']
            ]
            pokemon = Pokemon(name=data['name'], abilities=abilities, weight=data['weight'], height=data['height'],url=url)
            return pokemon
        else:
            missing_keys = [key for key in ['name', 'abilities', 'weight', 'height'] if key not in data]
            raise HTTPException(status_code=500, detail=f"Invalid data received from PokeAPI, missing keys: {missing_keys}")
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Error fetching data from PokeAPI") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error") from e


@app.get("/pokemon/export", response_model=str)
async def export_pokemon():
    data = await fetch_pokemon_data(f"{BASE_URL}?limit=10000")
    data['results'] = sorted(data['results'], key=lambda x: x['name'])

    xml_data = '<pokemon_list>\n'
    for pokemon in data['results']:
        xml_data += f"  <pokemon>\n"
        xml_data += f"    <name>{pokemon['name']}</name>\n"
        xml_data += f"    <url>{pokemon['url']}</url>\n"
        xml_data += f"  </pokemon>\n"
    xml_data += '</pokemon_list>'

    return xml_data
