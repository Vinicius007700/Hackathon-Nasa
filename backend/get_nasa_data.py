# get_nasa_data.py (versão final com feedback interativo)

import requests
import pandas as pd
import json
import os
from datetime import date

# --- PAINEL DE CONTROLE ---
# Use sua chave pessoal para evitar limites de taxa
API_KEY = "hzZ9P5wR29MGdvlSvmxvhnFbifYFx5phiIEOJBET" 

# Período longo para criar uma base de dados rica para o jogo
START_DATE = "2023-01-01"
END_DATE = date.today().strftime("%Y-%m-%d")

CACHE_DIR = "cache/"

# Lista completa de todos os tipos de eventos que queremos baixar
EVENT_TYPES = [
    "GST", # Geomagnetic Storm
    "CME", # Coronal Mass Ejection
    "HSS", # High-Speed Stream
    "FLR", # Solar Flare
    "IPS", # Interplanetary Shock
    "SEP", # Solar Energetic Particle
    "RBE", # Radiation Belt Enhancement
    "MPC"  # Magnetopause Crossing
]

# --- FUNÇÃO DE CACHE (nenhuma mudança aqui) ---
def cache_donki_data(event_type, start_date, end_date):
    """
    Busca dados de um tipo de evento da API DONKI e salva a resposta JSON original.
    """
    print(f"Buscando dados para o evento: {event_type}...")
    url = f"https://api.nasa.gov/DONKI/{event_type}?startDate={start_date}&endDate={end_date}&api_key={API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data:
            filename = f"{CACHE_DIR}nasa_{event_type.lower()}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"-> Sucesso! {len(data)} registros salvos em {filename}")
        else:
            print(f"-> Nenhum dado encontrado para {event_type} neste período.")
            
    except requests.exceptions.RequestException as e:
        print(f"-> ERRO ao buscar dados para {event_type}: {e}")

# --- EXECUÇÃO COM FEEDBACK INTERATIVO ---
if __name__ == "__main__":
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    print("="*50)
    print(f"Iniciando o download do 'Grande Cache' de dados da NASA")
    print(f"Período: {START_DATE} a {END_DATE}")
    print("="*50)
    
    # NOVO: Pega o número total de tarefas para o feedback
    total_events = len(EVENT_TYPES)
    
    # NOVO: Usamos enumerate para ter um contador de passos (i)
    for i, event in enumerate(EVENT_TYPES, 1):
        # NOVO: Imprime um cabeçalho claro para cada passo
        print(f"\n--- Passo {i}/{total_events}: Coletando dados de '{event}' ---")
        cache_donki_data(event, START_DATE, END_DATE)

    print("\n" + "="*50)
    print("Download do 'Grande Cache' concluído!")
    print(f"Todos os {total_events} tipos de eventos foram verificados.")
    print("Sua pasta 'cache/' está pronta.")
    print("="*50)