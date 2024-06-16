import httpx

async def fetch_pokemon_data(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        # Verifica se a requisição foi bem sucedida (código 200)
        if response.status_code == 200:
            return response.json()  # Retorna os dados JSON da resposta
        else:
            return None  # Ou trata o erro de acordo com sua lógica de negócio
