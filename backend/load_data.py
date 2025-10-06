# load_data.py

import json
import os
import random
from collections import deque, Counter
from datetime import datetime, timedelta
from rich import print

CACHE_DIR = 'backend/cache'
EVENT_DEFINITIONS = { # Dicionário completo EVENT_DEFINITIONS aqui...
    "FLR": {"nome_completo": "Erupção Solar", "categoria": "Causa", "peso_impacto": 7}, 
    "CME": {"nome_completo": "Ejeção de Massa Coronal", "categoria": "Causa", "peso_impacto": 9}, 
    "HSS": {"nome_completo": "Fluxo de Vento de Alta Velocidade", "categoria": "Causa", "peso_impacto": 6}, 
    "SEP": {"nome_completo": "Partículas Solares Energéticas", "categoria": "Viagem", "peso_impacto": 8}, 
    "IPS": {"nome_completo": "Choque Interplanetário", "categoria": "Viagem", "peso_impacto": 5}, 
    "MPC": {"nome_completo": "Cruzamento da Magnetopausa", "categoria": "Impacto", "peso_impacto": 4}, 
    "GST": {"nome_completo": "Tempestade Geomagnética", "categoria": "Impacto", "peso_impacto": 10}, 
    "RBE": {"nome_completo": "Aumento do Cinturão de Radiação", "categoria": "Pós-Impacto", "peso_impacto": 7}
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

def get_event_time(event_type, chain_ids):
    event_id = next((eid for eid in chain_ids if f"-{event_type}-" in eid), None)
    if not event_id: return None
    return datetime.fromisoformat(event_id[:19])

def gerar_roteiro_fazendeiro(analysis, chain_ids):
    """
    Generates a single narrative for the farmer Joseph explaining the solar effects,
    including cause, GPS risk, and Kp level, without including Alice.
    """
    # Extract cause events
    causa_ids = [eid for eid in chain_ids 
                 if EVENT_DEFINITIONS.get(eid.split('-')[-2], {}).get('categoria') == 'Causa']
    
    # Get date/time of CME or other event
    aviso_dt = get_event_time('CME', causa_ids) \
               or get_event_time('FLR', causa_ids) \
               or get_event_time('HSS', causa_ids)
    
    # Build narrative
    narrative = f"""
On {aviso_dt.strftime('%d/%m/%Y, %H:%M')}, Joseph noticed something was wrong with his machines.
The GPS sensors started failing due to intense solar activity: {analysis['causa_principal']}.
The peak Kp index recorded was {analysis['full_analysis']['max_kp']:.2f}, enough to stop communication with the tractors.

Joseph had to manually manage the harvest, aware that geomagnetic storms can affect electronic agricultural systems.
The event's effects continue, with expected outcomes: {analysis['full_analysis']['futuro_pos_impacto']}.
"""
    # Clean up unnecessary line breaks and spaces
    narrative = "\n".join([line.strip() for line in narrative.strip().splitlines()])
    
    return {"ato_unico": narrative}

def gerar_roteiro_pescador(analysis, chain_ids):
    """
    Generates the narrative for Raimundo the fisherman in English,
    only the narrative/falas, no scene titles.
    """
    gst_dt = get_event_time('GST', chain_ids)
    if not gst_dt:
        return {"error": "Could not determine the storm time."}
    
    pre_storm_dt = gst_dt - timedelta(hours=6)
    
    fala_1 = (
        f"On {pre_storm_dt.strftime('%d/%m/%Y, %H:%M')}, Raimundo prepares his boat, trusting the GPS. "
        f"Little does he know, a solar storm is approaching."
    )
    
    fala_2 = (
        f"At {gst_dt.strftime('%d/%m/%Y, %H:%M')}, far from the coast, Raimundo's GPS stops working. "
        f"He is lost. Alice appears: 'You got caught by a geomagnetic storm!' "
        f"'{analysis['consequencia_terra']} Your GPS will not work for a while.'"
    )
    
    return {"fala_1": fala_1, "fala_2": fala_2}


def gerar_roteiro_guia_aurora(analysis, chain_ids):
    """
    Generates the aurora guide narrative in English.
    """
    gst_dt = get_event_time('GST', chain_ids)
    if not gst_dt:
        return {"error": "Could not determine the storm time."}

    # First image: Kristín analyzing data
    previsao_dt = gst_dt - timedelta(hours=2)
    previsao_str = (
        f"At {previsao_dt.strftime('%d/%m/%Y, %H:%M')} in Iceland, Kristín studies NASA data on her computer. "
        f"She sees the Kp forecast ({analysis['full_analysis']['max_kp']:.0f}) and the Bz turning south. "
        f"She senses something exciting is about to happen and expects Alice to arrive."
    )

    # Second image: Kristín with Alice, planning to watch the aurora
    chegada_dt = gst_dt
    chegada_str = (
        f"At {chegada_dt.strftime('%d/%m/%Y, %H:%M')}, Alice joins Kristín. "
        f"Kristín points to the sky and the data on her laptop: 'A geomagnetic storm is coming. "
        f"Let's go see the aurora borealis!'"
    )

    # Third image: Watching the aurora
    show_dt = gst_dt + timedelta(hours=2)
    show_str = (
        f"At {show_dt.strftime('%d/%m/%Y, %H:%M')}, under the northern lights, they watch in awe. "
        f"'It's amazing that this beauty was caused by {analysis['causa_principal']}, "
        f"an explosion 150 million kilometers away,' Kristín remarks."
    )

    return {
        "guia_aurora_previsao": previsao_str,
        "guia_aurora_chegada": chegada_str,
        "guia_aurora_espetaculo": show_str
    }


def generate_story_package_for_year(year: int, master_db: dict, all_storms: list):
    """
    Função principal do motor do jogo: Filtra, seleciona, analisa e gera todo o conteúdo.
    """
    # 1. Filtra tempestades pelo ano
    storms_in_year = [s for s in all_storms if datetime.fromisoformat(s['startTime'].replace('Z','')).year == year]
    if not storms_in_year: return {"error": f"Nenhuma tempestade encontrada para o ano {year}."}

    # 2. Ordena pela mais forte e pega as Top 6
    storms_in_year.sort(key=lambda x: x['maxKp'], reverse=True)
    top_storms = storms_in_year[:6]

    # 3. Sorteia uma das Top 6
    chosen_storm = random.choice(top_storms)
    chosen_storm_id = chosen_storm['gstID']
    print(f"Tempestade Sorteada para o ano {year}: {chosen_storm_id} (Kp: {chosen_storm['maxKp']})")

    # 4. Faz a busca profunda
    full_chain = get_full_event_chain_ids(chosen_storm_id, master_db)

    # 5. Roda a análise completa
    analysis = analyze_storm_dossier(full_chain, chosen_storm)

    # 6. Gera TODOS os roteiros
    storylines = {
        "fazendeiro": gerar_roteiro_fazendeiro(analysis, full_chain),
        "pescador": gerar_roteiro_pescador(analysis, full_chain),
        "guia_aurora": gerar_roteiro_guia_aurora(analysis, full_chain)
    }

    # 7. Monta o pacote final completo e achatado como você pediu
    final_package = {
        "storm_details": {"id": chosen_storm['gstID'], "start_time": chosen_storm['startTime'], "max_kp": chosen_storm['maxKp']},
        "full_analysis": analysis,
        "storylines": {}
    }
    
    # "Achata" os roteiros no dicionário final
    for personagem, roteiro in storylines.items():
        for nome_cena, texto in roteiro.items():
            # Cria chaves como "fazendeiro_ato_1_aviso"
            key_formatada = f"{personagem}_{nome_cena.lower().replace(': ', '_').replace(' ', '_')}"
            final_package["storylines"][key_formatada] = texto
    
    return final_package