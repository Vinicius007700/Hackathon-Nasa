# data_manager.py

import json
import os
from collections import deque

# --- CONFIGURAÇÃO ---
CACHE_DIR = 'backend/cache/'
EVENT_FILES = [
    'nasa_gst.json', 'nasa_cme.json', 'nasa_hss.json', 'nasa_ips.json',
    'nasa_flr.json', 'nasa_sep.json', 'nasa_rbe.json', 'nasa_mpc.json'
]

# --- FUNÇÕES DE GERENCIAMENTO DE DADOS ---

def load_all_caches():
    """
    Carrega todos os caches JSON em um único dicionário mestre para busca rápida.
    """
    print("Carregando todos os arquivos de cache para a memória...")
    master_cache = {}
    for filename in EVENT_FILES:
        try:
            filepath = os.path.join(CACHE_DIR, filename)
            event_type = filename.split('_')[1].split('.')[0].upper()
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            id_key = f"{event_type.lower()}ID"
            if event_type == 'FLR': id_key = 'flrID'
            
            for event in data:
                if id_key in event:
                    master_cache[event[id_key]] = event
        except FileNotFoundError:
            print(f"Aviso: Arquivo de cache '{filename}' não encontrado.")
        except Exception as e:
            print(f"Erro ao carregar '{filename}': {e}")
            
    print(f"Carregamento concluído. {len(master_cache)} eventos na base de dados.")
    return master_cache

def find_top_n_storms(gst_data, n=10):
    """
    Encontra os N eventos de GST com os maiores picos de Kp.
    Retorna a lista completa dos objetos de tempestade, não apenas os IDs.
    """
    storm_peaks = []
    for storm in gst_data:
        max_kp = 0
        for kp_reading in storm.get('allKpIndex', []):
            if kp_reading.get('kpIndex', 0) > max_kp:
                max_kp = kp_reading.get('kpIndex', 0)
        
        if 'gstID' in storm and max_kp > 0:
            storm['maxKp'] = max_kp
            storm_peaks.append(storm)
            
    storm_peaks.sort(key=lambda x: x['maxKp'], reverse=True)
    return storm_peaks[:n]

def get_event_chain(start_id, master_cache):
    """
    A partir de um ID inicial, navega por todos os linkedEvents para encontrar a cadeia completa.
    """
    if start_id not in master_cache:
        return []

    chain = set()
    queue = deque([start_id])

    while queue:
        current_id = queue.popleft()
        if current_id in chain:
            continue
        
        chain.add(current_id)
        
        event_details = master_cache.get(current_id, {})
        for linked_event in event_details.get('linkedEvents', []):
            linked_id = linked_event.get('activityID')
            if linked_id:
                queue.append(linked_id)
    return sorted(list(chain)) # Retorna uma lista ordenada