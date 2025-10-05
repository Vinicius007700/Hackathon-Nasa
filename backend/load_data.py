# load_data.py

import json
import os
import random
from collections import deque, Counter
from datetime import datetime, timedelta
from rich import print

CACHE_DIR = 'backend/cache'
EVENT_DEFINITIONS = { # Dicionário completo EVENT_DEFINITIONS aqui...
    "FLR": {"nome_completo": "Erupção Solar", "categoria": "Causa", "peso_impacto": 7}, "CME": {"nome_completo": "Ejeção de Massa Coronal", "categoria": "Causa", "peso_impacto": 9}, "HSS": {"nome_completo": "Fluxo de Vento de Alta Velocidade", "categoria": "Causa", "peso_impacto": 6}, "SEP": {"nome_completo": "Partículas Solares Energéticas", "categoria": "Viagem", "peso_impacto": 8}, "IPS": {"nome_completo": "Choque Interplanetário", "categoria": "Viagem", "peso_impacto": 5}, "MPC": {"nome_completo": "Cruzamento da Magnetopausa", "categoria": "Impacto", "peso_impacto": 4}, "GST": {"nome_completo": "Tempestade Geomagnética", "categoria": "Impacto", "peso_impacto": 10}, "RBE": {"nome_completo": "Aumento do Cinturão de Radiação", "categoria": "Pós-Impacto", "peso_impacto": 7}
}

def load_all_data_on_demand():
    """Carrega TODOS os arquivos JSON do cache e processa as tempestades (GSTs)."""
    print(f"\nIniciando carregamento de todos os arquivos em: '{os.path.abspath(CACHE_DIR)}'")
    master_cache = {}
    id_key_map = {'GST': 'gstID', 'CME': 'activityID', 'HSS': 'hssID', 'IPS': 'ipsID', 'FLR': 'flrID', 'SEP': 'sepID', 'RBE': 'rbeID', 'MPC': 'mpcID'}
    try:
        files = [f for f in os.listdir(CACHE_DIR) if f.startswith('nasa_') and f.endswith('.json')]
    except FileNotFoundError:
        print(f"[bold red]ERRO CRÍTICO: Diretório de cache '{CACHE_DIR}' não encontrado.[/bold red]")
        return None, None
    for filename in files:
        try:
            event_type = filename.split('_')[1].split('.')[0].upper()
            id_key = id_key_map.get(event_type)
            if not id_key: continue
            with open(os.path.join(CACHE_DIR, filename), 'r', encoding='utf-8') as f: data = json.load(f)
            for event in data:
                event_id = event.get('activityID') if event_type == 'CME' else event.get(id_key)
                if event_id: master_cache[event_id] = event
        except Exception: continue
    
    all_storms = [event for event in master_cache.values() if 'gstID' in event]
    for storm in all_storms:
        storm['maxKp'] = max([kp.get('kpIndex', 0) for kp in storm.get('allKpIndex', [])], default=0)
    print(f"[bold green]Carregamento concluído. {len(all_storms)} tempestades (GSTs) disponíveis.[/bold green]")
    return master_cache, all_storms




# <<<< NOVA FUNÇÃO >>>>
def select_random_top_storm_for_year(year: int, all_storms: list):
    """
    Implementa a lógica principal de seleção do jogo:
    1. Filtra por ano.
    2. Acha as 6 mais fortes.
    3. Sorteia uma.
    4. Retorna o objeto da tempestade sorteada.
    """
    # 1. Filtra tempestades pelo ano
    storms_in_year = [s for s in all_storms if datetime.fromisoformat(s['startTime'].replace('Z','')).year == year]
    if not storms_in_year:
        print(f"Nenhuma tempestade encontrada para o ano {year}.")
        return None

    # 2. Ordena pela mais forte e pega as Top 6
    storms_in_year.sort(key=lambda x: x['maxKp'], reverse=True)
    top_storms = storms_in_year[:6]

    # 3. Sorteia uma das Top 6
    chosen_storm = random.choice(top_storms)
    print(f"Tempestade Sorteada para o ano {year}: {chosen_storm['gstID']} (Kp: {chosen_storm['maxKp']})")

    # 4. Retorna o objeto completo da tempestade escolhida
    return chosen_storm

def get_full_event_chain_ids(start_id, master_cache):
    """Função que você mencionou, para ser usada no próximo passo."""
    if start_id not in master_cache: return []
    chain, queue = set(), deque([start_id])
    while queue:
        current_id = queue.popleft()
        if current_id in chain: continue
        chain.add(current_id)
        for linked_event in master_cache.get(current_id, {}).get('linkedEvents') or []:
            if linked_id := linked_event.get('activityID'): queue.append(linked_id)
    return sorted(list(chain))

def analyze_storm_dossier(chain_ids, gst_event):
    # Lógica de contagem e score (intacta)
    event_types = [event_id.split('-')[-2] for event_id in chain_ids]
    event_counts = Counter(event_types)
    category_summary = {"Causa": [], "Viagem": [], "Impacto": [], "Pós-Impacto": []}
    for event_type, count in sorted(event_counts.items()):
        definition = EVENT_DEFINITIONS.get(event_type)
        if definition:
            summary_str = f"{count}x {event_type} ({definition['nome_completo']})"
            category_summary[definition["categoria"]].append(summary_str)
    cause_scores = {etype: count * EVENT_DEFINITIONS[etype]['peso_impacto']
                    for etype, count in event_counts.items()
                    if EVENT_DEFINITIONS.get(etype, {}).get("categoria") == "Causa"}
    main_cause_str = "Causa indeterminada."
    if cause_scores:
        top_cause_type = max(cause_scores, key=cause_scores.get)
        main_cause_str = f"{event_counts[top_cause_type]}x {top_cause_type} ({EVENT_DEFINITIONS[top_cause_type]['nome_completo']})"
    
    # Extração do Kp (intacta)
    max_kp = max(item.get('kpIndex', 0) for item in gst_event.get('allKpIndex', [])) if gst_event.get('allKpIndex') else 0
    
    # Lógica de strings de consequência (intacta)
    if event_counts.get("MPC") and event_counts.get("GST"):
        earth_consequence_str = f"O escudo magnético foi atingido (MPC), iniciando a Tempestade Geomagnética (GST) com pico de Kp {max_kp:.2f}."
    elif event_counts.get("GST"):
        earth_consequence_str = f"Ocorreu uma Tempestade Geomagnética (GST) com pico de Kp {max_kp:.2f}."
    else: earth_consequence_str = "Impacto geomagnético mínimo ou não registrado."
    post_impact_outlook_str = "Efeitos de longo prazo mínimos."
    if event_counts.get("RBE"):
        post_impact_outlook_str = "Aumento no cinturão de radiação (RBE), um risco duradouro para satélites."
        
    # <<< ADIÇÃO >>> Retornar também o max_kp para ser usado na história.
    return {
        "resumo_por_categoria": category_summary, "causa_principal": main_cause_str,
        "consequencia_terra": earth_consequence_str, "futuro_pos_impacto": post_impact_outlook_str,
        "max_kp": max_kp
    }