# load_data.py

import json
import os
import random
from collections import deque, Counter
from datetime import datetime, timedelta
from rich import print

CACHE_DIR = 'backend/cache'
EVENT_DEFINITIONS = {  # Full EVENT_DEFINITIONS dictionary here...
    "FLR": {"nome_completo": "Solar Flare", "categoria": "Causa", "peso_impacto": 7}, 
    "CME": {"nome_completo": "Coronal Mass Ejection", "categoria": "Causa", "peso_impacto": 9}, 
    "HSS": {"nome_completo": "High-Speed Solar Wind Stream", "categoria": "Causa", "peso_impacto": 6}, 
    "SEP": {"nome_completo": "Solar Energetic Particles", "categoria": "Viagem", "peso_impacto": 8}, 
    "IPS": {"nome_completo": "Interplanetary Shock", "categoria": "Viagem", "peso_impacto": 5}, 
    "MPC": {"nome_completo": "Magnetopause Crossing", "categoria": "Impacto", "peso_impacto": 4}, 
    "GST": {"nome_completo": "Geomagnetic Storm", "categoria": "Impacto", "peso_impacto": 10}, 
    "RBE": {"nome_completo": "Radiation Belt Enhancement", "categoria": "Pós-Impacto", "peso_impacto": 7}
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
    
        # Consequence strings logic (unchanged)
    if event_counts.get("MPC") and event_counts.get("GST"):
        earth_consequence_str = f"The magnetic shield was hit (MPC), triggering the Geomagnetic Storm (GST) with a peak Kp of {max_kp:.2f}."
    elif event_counts.get("GST"):
        earth_consequence_str = f"A Geomagnetic Storm (GST) occurred with a peak Kp of {max_kp:.2f}."
    else:
        earth_consequence_str = "Minimal or unrecorded geomagnetic impact."
    post_impact_outlook_str = "Minimal long-term effects."
    if event_counts.get("RBE"):
        post_impact_outlook_str = "Increased radiation belt (RBE), a lasting risk for satellites."

        
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
    cause_ids = [eid for eid in chain_ids if EVENT_DEFINITIONS.get(eid.split('-')[-2], {}).get('categoria') == 'Causa']
    aviso_dt = get_event_time('CME', cause_ids) or get_event_time('FLR', cause_ids) or get_event_time('HSS', cause_ids)
    if not aviso_dt:
        return {"ato_1_aviso": "No event time available for farmer's warning."}
    aviso_str = f"Push Notification {aviso_dt.strftime('%d/%m %H:%M')} : Space weather alert. Cause: {analysis['causa_principal']}. GPS risk detected."

    impacto_dt = get_event_time('MPC', chain_ids) or get_event_time('GST', chain_ids)
    if not impacto_dt:
        return {"ato_2_impacto": "No impact event available for farmer's storyline."}
    impacto_str = (
        f"On {impacto_dt.strftime('%d/%m at %H:%M')}, Alice arrives. At the same moment, Joseph's tractors stop. "
        f"'The storm has arrived,' she says. 'Your GPS will not work, but I will help guide the harvest.'"
    )

    gst_dt = get_event_time('GST', chain_ids)
    if not gst_dt:
        return {"ato_3_explicacao": "No GST time available for farmer's explanation."}
    futuro_dt = gst_dt + timedelta(hours=24)
    explicacao_str = (
        f"Later, Alice explains: 'It all started with {analysis['causa_principal']}. "
        f"From {futuro_dt.strftime('%d/%m at %H:%M')}, the danger continues... ({analysis['futuro_pos_impacto']})'"
    )

    return {"ato_1_aviso": aviso_str, "ato_2_impacto": impacto_str, "ato_3_explicacao": explicacao_str}


def gerar_roteiro_pescador(analysis, chain_ids):
    gst_dt = get_event_time('GST', chain_ids)
    if not gst_dt:
        return {"error": "Could not determine the storm time for fisherman."}
    pre_storm_dt = gst_dt - timedelta(hours=6)

    cena1_str = (
        f"Date: {pre_storm_dt.strftime('%d/%m/%Y, %H:%M')}. Location: Coast of Brazil."
        f"Raimundo prepares his boat, trusting his GPS. Little does he know, a solar storm is approaching."
    )
    cena2_str = (
        f"DANGER AT SEA Date: {gst_dt.strftime('%d/%m/%Y, %H:%M')}. Location: Open sea."
        f"Far from the coast, Raimundo's GPS shuts down. He is lost. Alice appears. "
        f"'You got caught by a geomagnetic storm!' she says. "
        f"'{analysis['consequencia_terra']} Your GPS will not return anytime soon.'"
    )

    return {"cena_1_calmaria": cena1_str, "cena_2_perigo": cena2_str}


def gerar_roteiro_guia_aurora(analysis, chain_ids):
    gst_dt = get_event_time('GST', chain_ids)
    if not gst_dt:
        return {"error": "Could not determine the storm time for aurora guide."}
    previsao_dt = gst_dt - timedelta(hours=2)

    cena1_str = (
        f"SCENE 1: THE FORECAST Date: {previsao_dt.strftime('%d/%m/%Y, %H:%M')}. Location: Iceland."
        f"Kristín analyzes NASA data and sees the Kp forecast ({analysis['max_kp']:.0f}) and the Bz turning south. "
        f"'This will be a show,' she whispers."
    )
    chegada_dt = gst_dt
    cena2_str = (
        f"SCENE 2: THE ARRIVAL Date: {chegada_dt.strftime('%d/%m/%Y, %H:%M')}."
        f"Alice enters the observatory. Kristín greets her: 'I knew you would come. The data doesn’t lie. "
        f"The show is about to begin.'"
    )
    show_dt = gst_dt + timedelta(hours=2)
    cena3_str = (
        f"SCENE 3: THE SPECTACLE Date: {show_dt.strftime('%d/%m/%Y, %H:%M')}."
        f"Under the aurora, Alice says: 'To think that all this beauty was caused by {analysis['causa_principal']}, "
        f"an explosion 150 million kilometers away.'"
    )

    return {"cena_1_previsao": cena1_str, "cena_2_chegada": cena2_str, "cena_3_espetaculo": cena3_str}


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