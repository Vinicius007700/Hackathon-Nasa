# deep_dive_analyzer.py

import json
import os
from collections import deque

# --- CONFIGURAÇÃO ---
CACHE_DIR = 'cache/'
# Lista dos arquivos de cache que vamos carregar para a investigação
# O nome do arquivo deve corresponder à sigla do evento (ex: nasa_gst.json -> GST)
EVENT_FILES = [
    'nasa_gst.json', 'nasa_cme.json', 'nasa_hss.json', 'nasa_ips.json',
    'nasa_flr.json', 'nasa_sep.json', 'nasa_rbe.json', 'nasa_mpc.json'
]

# --- FUNÇÕES ---

def load_all_caches(cache_dir, event_files):
    """
    Carrega todos os caches JSON em um único dicionário para busca rápida.
    A chave é o activityID, o valor é o registro completo do evento.
    """
    print("Carregando todos os arquivos de cache para a memória...")
    master_cache = {}
    for filename in event_files:
        try:
            filepath = os.path.join(cache_dir, filename)
            event_type = filename.split('_')[1].split('.')[0].upper() # ex: 'gst' -> 'GST'
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cada tipo de evento tem uma chave de ID diferente (gstID, cmeID, etc.)
            id_key = f"{event_type.lower()}ID"
            if event_type == 'FLR': id_key = 'flrID' # Pequena inconsistência na API
            
            for event in data:
                if id_key in event:
                    master_cache[event[id_key]] = event
        except FileNotFoundError:
            print(f"Aviso: Arquivo de cache '{filename}' não encontrado. Pulando.")
        except Exception as e:
            print(f"Erro ao carregar '{filename}': {e}")
            
    print(f"Carregamento concluído. {len(master_cache)} eventos no total na base de dados.")
    return master_cache

def find_top_n_storms(gst_filename, n=5):
    """
    Encontra os N eventos de GST com os maiores picos de Kp.
    """
    try:
        with open(gst_filename, 'r', encoding='utf-8') as f:
            gst_data = json.load(f)
    except FileNotFoundError:
        return []

    storm_peaks = []
    for storm in gst_data:
        max_kp = 0
        for kp_reading in storm.get('allKpIndex', []):
            if kp_reading.get('kpIndex', 0) > max_kp:
                max_kp = kp_reading.get('kpIndex', 0)
        
        if 'gstID' in storm:
            storm_peaks.append({'gstID': storm['gstID'], 'maxKp': max_kp})
            
    storm_peaks.sort(key=lambda x: x['maxKp'], reverse=True)
    return storm_peaks[:n]

def get_event_chain(start_id, master_cache):
    """
    A partir de um ID inicial, navega por todos os linkedEvents para encontrar a cadeia completa.
    """
    if start_id not in master_cache:
        return {start_id}

    chain = set()
    queue = deque([start_id]) # Usamos uma fila para a busca

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
    return chain


# --- EXECUÇÃO ---
if __name__ == "__main__":
    # Carrega todos os dados de uma vez para buscas eficientes
    master_database = load_all_caches(CACHE_DIR, EVENT_FILES)
    
    # Encontra as 5 tempestades mais fortes no arquivo GST
    top_5_storms = find_top_n_storms(os.path.join(CACHE_DIR, 'nasa_gst.json'), n=5)
    
    print("\n" + "="*50)
    print("Analisando a cadeia de eventos para as 5 tempestades mais fortes...")
    print("="*50)
    
    if not top_5_storms:
        print("Nenhuma tempestade encontrada no arquivo nasa_gst.json para analisar.")
    else:
        # Para cada uma das top 5, faz a investigação completa
        for i, storm in enumerate(top_5_storms, 1):
            print(f"\nINVESTIGAÇÃO #{i}: Tempestade {storm['gstID']} (Pico Kp: {storm['maxKp']})")
            
            full_chain = get_event_chain(storm['gstID'], master_database)
            
            print(f"-> Encontrados {len(full_chain)} eventos relacionados nesta cadeia:")
            for event_id in sorted(list(full_chain)): # Imprime em ordem para facilitar a leitura
                print(f"   - {event_id}")