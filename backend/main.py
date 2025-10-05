# main.py

import random
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import pandas as pd

# Importa as funções do nosso "cérebro"
from . import data_manager

# --- INICIALIZAÇÃO E CARREGAMENTO ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# Carrega todos os caches para a memória quando o servidor inicia
MASTER_DB = data_manager.load_all_caches()
# Carrega apenas os dados de GST para encontrar as tempestades
try:
    with open('backend/cache/nasa_gst.json', 'r', encoding='utf-8') as f:
        gst_data = json.load(f)
except:
    gst_data = []

# Pré-calcula as tempestades mais fortes
TOP_10_STORMS = data_manager.find_top_n_storms(gst_data, n=10)

# Define nossas histórias
STORIES = [
    {"type": "fisherman", "location": "Costa do Ceará, Brasil", "character_name": "Raimundo"},
    {"type": "farmer", "location": "Meio-Oeste, EUA", "character_name": "Joseph"},
    {"type": "aurora_guide", "location": "Islândia", "character_name": "Kristín"}
]

# --- ENDPOINTS DA API ---

@app.get("/")
def read_root():
    return {"Status": "Servidor do Jogo de Clima Espacial está no ar!", "Top 10 Tempestades Prontas": len(TOP_10_STORMS) > 0}

@app.get("/api/fast-game")
def get_fast_game_data(exclude: Optional[str] = None):
    """
    Prepara e retorna todos os dados para um jogo rápido, usando a lógica correta.
    """
    if not TOP_10_STORMS:
        return {"error": "Nenhuma tempestade disponível na base de dados."}

    selected_storm = random.choice(TOP_10_STORMS)
    
    available_stories = STORIES
    if exclude and any(s['type'] == exclude for s in STORIES):
        available_stories = [s for s in STORIES if s['type'] != exclude]
    selected_story = random.choice(available_stories)

    # Usa nossa função desacoplada para formatar a resposta
    response_data = {
        "story": selected_story,
        "event_data": {
            "gst_id": selected_storm.get('gstID'),
            "start_time": selected_storm.get('startTime'),
            "max_kp": selected_storm.get('maxKp'),
            "kp_timeline": selected_storm.get('allKpIndex', []),
            # Usa a função de cadeia de eventos para obter as causas
            "causes": data_manager.get_event_chain(selected_storm.get('gstID'), MASTER_DB)
        }
    }
    
    return response_data

# Este endpoint substitui o antigo /api/stories
@app.get("/api/full-game-data")
def get_full_game_data():
    """
    Retorna a lista completa de todas as tempestades (GSTs) do cache,
    com o pico de Kp pré-calculado para cada uma.
    """
    if not gst_data:
        return {"error": "A base de dados de tempestades não pôde ser carregada."}

    # A lógica de encontrar o maxKp para cada tempestade
    temp_storms = []
    for storm in gst_data:
        max_kp = 0
        for kp_reading in storm.get('allKpIndex', []):
            if kp_reading.get('kpIndex', 0) > max_kp:
                max_kp = kp_reading.get('kpIndex', 0)
        
        storm_copy = storm.copy()
        storm_copy['maxKp'] = max_kp
        temp_storms.append(storm_copy)

    return {"all_storms": temp_storms}

# NOVO ENDPOINT PARA O FILTRO DO "FAST GAME"
@app.get("/api/data-filter-fast")
def data_filter_fast(date_str: str):
    """
    Recebe uma data (para manter a consistência), mas ignora-a.
    Escolhe aleatoriamente UMA das 10 tempestades mais fortes
    e retorna seu dossiê completo.
    """
    print(f"\n[bold blue]Recebida requisição para Fast Game com data: {date_str}[/bold blue]")
    if not TOP_10_STORMS:
        return {"error": "Nenhuma tempestade disponível na base de dados."}

    # Escolhe aleatoriamente uma das 10 tempestades mais fortes
    selected_storm = random.choice(TOP_10_STORMS)
    
    # Monta a resposta completa para esta única tempestade
    story_data = {
        "gst_id": selected_storm.get('gstID'),
        "start_time": selected_storm.get('startTime'),
        "max_kp": selected_storm.get('maxKp'),
        "kp_timeline": selected_storm.get('allKpIndex', []),
        "causes": data_manager.get_event_chain(selected_storm.get('gstID'), MASTER_DB)
    }
    
    # Retorna os dados de uma única história, prontos para o jogo
    return {"story_data": story_data}


# NOVO ENDPOINT PARA O FILTRO DO "FULL GAME"
@app.get("/api/data-filter-full")
def data_filter_full(year: int, month: int):
    """
    Recebe um ano e mês e retorna uma LISTA de todas as tempestades
    encontradas naquele período para o jogador escolher.
    """
    print(f"\n[bold green]Recebida requisição para Full Game com data: {year}-{month}[/bold green]")
    if gst_data is None:
        return {"error": "Base de dados não carregada."}

    # Lógica de filtragem que já tínhamos
    temp_df = pd.DataFrame(gst_data)
    temp_df['startTime'] = pd.to_datetime(temp_df['startTime'])
    filtered_storms = temp_df[(temp_df['startTime'].dt.year == year) & (temp_df['startTime'].dt.month == month)]

    if filtered_storms.empty:
        return {"available_stories": []}

    # Adiciona o maxKp para cada tempestade filtrada
    stories = []
    for index, storm in filtered_storms.iterrows():
        max_kp = 0
        for kp_reading in storm.get('allKpIndex', []):
            if kp_reading.get('kpIndex', 0) > max_kp:
                max_kp = kp_reading.get('kpIndex', 0)
        stories.append({
            "id": storm['gstID'],
            "date": storm['startTime'].isoformat(),
            "max_kp": max_kp
        })

    return {"available_stories": stories}
