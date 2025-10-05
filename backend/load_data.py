# load_data.py

import json
import os
from collections import deque, Counter
from rich import print
from datetime import datetime, timedelta

CACHE_DIR = 'backend/cache'

EVENT_DEFINITIONS = {
    "FLR": {"nome_completo": "Erupção Solar", "categoria": "Causa", "peso_impacto": 7},
    "CME": {"nome_completo": "Ejeção de Massa Coronal", "categoria": "Causa", "peso_impacto": 9},
    "HSS": {"nome_completo": "Fluxo de Vento de Alta Velocidade", "categoria": "Causa", "peso_impacto": 6},
    "SEP": {"nome_completo": "Partículas Solares Energéticas", "categoria": "Viagem", "peso_impacto": 8},
    "IPS": {"nome_completo": "Choque Interplanetário", "categoria": "Viagem", "peso_impacto": 5},
    "MPC": {"nome_completo": "Cruzamento da Magnetopausa", "categoria": "Impacto", "peso_impacto": 4},
    "GST": {"nome_completo": "Tempestade Geomagnética", "categoria": "Impacto", "peso_impacto": 10},
    "RBE": {"nome_completo": "Aumento do Cinturão de Radiação", "categoria": "Pós-Impacto", "peso_impacto": 7}
}

def load_all_caches(cache_dir):
    master_cache = {}
    id_key_map = {
        'GST': 'gstID', 'CME': 'activityID', 'HSS': 'hssID', 'IPS': 'ipsID',
        'FLR': 'flrID', 'SEP': 'sepID', 'RBE': 'rbeID', 'MPC': 'mpcID'
    }
    try:
        files = os.listdir(cache_dir)
    except FileNotFoundError: return None
    for filename in [f for f in files if f.startswith('nasa_') and f.endswith('.json')]:
        try:
            event_type = filename.split('_')[1].split('.')[0].upper()
            id_key = id_key_map.get(event_type)
            if not id_key: continue
            with open(os.path.join(cache_dir, filename), 'r', encoding='utf-8') as f: data = json.load(f)
            for event in data:
                event_id = event.get('activityID') if event_type == 'CME' else event.get(id_key)
                if event_id: master_cache[event_id] = event
        except Exception: continue
    return master_cache

def get_full_event_chain_ids(start_id, master_cache):
    if start_id not in master_cache: return []
    chain, queue = set(), deque([start_id])
    while queue:
        current_id = queue.popleft()
        if current_id in chain: continue
        chain.add(current_id)
        for linked_event in master_cache.get(current_id, {}).get('linkedEvents') or []:
            if linked_id := linked_event.get('activityID'): queue.append(linked_id)
    return sorted(list(chain))