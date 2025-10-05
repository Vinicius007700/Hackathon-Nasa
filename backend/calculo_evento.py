# load_data.py

import json
import os
import random
from collections import deque, Counter
from datetime import datetime, timedelta

CACHE_DIR = 'backend/cache'
EVENT_DEFINITIONS = {
    "FLR": {"nome_completo": "Erupção Solar", "categoria": "Causa", "peso_impacto": 7}, "CME": {"nome_completo": "Ejeção de Massa Coronal", "categoria": "Causa", "peso_impacto": 9}, "HSS": {"nome_completo": "Fluxo de Vento de Alta Velocidade", "categoria": "Causa", "peso_impacto": 6}, "SEP": {"nome_completo": "Partículas Solares Energéticas", "categoria": "Viagem", "peso_impacto": 8}, "IPS": {"nome_completo": "Choque Interplanetário", "categoria": "Viagem", "peso_impacto": 5}, "MPC": {"nome_completo": "Cruzamento da Magnetopausa", "categoria": "Impacto", "peso_impacto": 4}, "GST": {"nome_completo": "Tempestade Geomagnética", "categoria": "Impacto", "peso_impacto": 10}, "RBE": {"nome_completo": "Aumento do Cinturão de Radiação", "categoria": "Pós-Impacto", "peso_impacto": 7}
}

# --- FUNÇÕES DE LÓGICA (Todas as nossas funções de base) ---

def initialize_data():
    master_cache = {}
    id_key_map = {'GST': 'gstID', 'CME': 'activityID', 'HSS': 'hssID', 'IPS': 'ipsID', 'FLR': 'flrID', 'SEP': 'sepID', 'RBE': 'rbeID', 'MPC': 'mpcID'}
    try:
        files = [f for f in os.listdir(CACHE_DIR) if f.startswith('nasa_') and f.endswith('.json')]
    except FileNotFoundError: return None, None
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
    gst_events = [event for event in master_cache.values() if 'gstID' in event]
    for storm in gst_events:
        storm['maxKp'] = max([kp.get('kpIndex', 0) for kp in storm.get('allKpIndex', [])], default=0)
    print(f"Inicialização completa. {len(master_cache)} eventos e {len(gst_events)} tempestades processadas.")
    return master_cache, gst_events

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

def analyze_storm_dossier(chain_ids, gst_event):
    # ... (função analyze_storm_dossier completa, como na versão anterior)
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
    max_kp = gst_event.get('maxKp', 0)
    if event_counts.get("MPC") and event_counts.get("GST"):
        earth_consequence_str = f"O escudo magnético foi atingido (MPC), iniciando a Tempestade Geomagnética (GST) com pico de Kp {max_kp:.2f}."
    elif event_counts.get("GST"):
        earth_consequence_str = f"Ocorreu uma Tempestade Geomagnética (GST) com pico de Kp {max_kp:.2f}."
    else: earth_consequence_str = "Impacto geomagnético mínimo ou não registrado."
    post_impact_outlook_str = "Efeitos de longo prazo mínimos."
    if event_counts.get("RBE"):
        post_impact_outlook_str = "Aumento no cinturão de radiação (RBE), um risco duradouro para satélites."
    return {"resumo_por_categoria": category_summary, "causa_principal": main_cause_str, "consequencia_terra": earth_consequence_str, "futuro_pos_impacto": post_impact_outlook_str, "max_kp": max_kp}

def get_event_time(event_type, chain_ids):
    event_id = next((eid for eid in chain_ids if f"-{event_type}-" in eid), None)
    if not event_id: return None
    return datetime.fromisoformat(event_id[:19])

def gerar_roteiro_fazendeiro(analysis, chain_ids):
    # ... (função gerar_roteiro_fazendeiro completa)
    causa_ids = [eid for eid in chain_ids if EVENT_DEFINITIONS.get(eid.split('-')[-2], {}).get('categoria') == 'Causa']
    aviso_dt = get_event_time('CME', causa_ids) or get_event_time('FLR', causa_ids)
    aviso_str = f"Notificação Push\n{aviso_dt.strftime('%d/%m %H:%M')} : Alerta de clima espacial. Causa: {analysis['causa_principal']}. Risco para GPS."
    impacto_dt = get_event_time('MPC', chain_ids)
    impacto_str = (f"Em {impacto_dt.strftime('%d/%m às %H:%M')}, Alice chega. No mesmo instante, os tratores de Joseph param. 'A tempestade chegou', diz ela. 'Seu GPS não vai funcionar, mas eu ajudo a guiar a colheita.'")
    gst_dt = get_event_time('GST', chain_ids)
    futuro_dt = gst_dt + timedelta(hours=24)
    explicacao_str = (f"Mais tarde, Alice explica: 'Tudo começou com {analysis['causa_principal']}. A partir de {futuro_dt.strftime('%d/%m às %H:%M')}, o perigo continua... ({analysis['futuro_pos_impacto']})'")
    return {"ato_1_aviso": aviso_str, "ato_2_impacto": impacto_str, "ato_3_explicacao": explicacao_str}

def gerar_roteiro_pescador(analysis, chain_ids):
    # ... (função gerar_roteiro_pescador completa)
    gst_dt = get_event_time('GST', chain_ids)
    if not gst_dt: return {"erro": "Não foi possível determinar o tempo da tempestade."}
    pre_storm_dt = gst_dt - timedelta(hours=6)
    cena1_str = (f"CENA 1: A CALMARIA\nData: {pre_storm_dt.strftime('%d/%m/%Y, %H:%M')}. Local: Costa do Brasil.\n"
                 f"Raimundo prepara seu barco, confiando no seu GPS. Mal sabe ele que uma tempestade solar se aproxima.")
    cena2_str = (f"CENA 2: O PERIGO NO MAR\nData: {gst_dt.strftime('%d/%m/%Y, %H:%M')}. Local: Mar aberto.\n"
                 f"Longe da costa, o GPS de Raimundo apaga. Ele está perdido. Alice surge. 'Você foi pego por uma tempestade geomagnética!', ela diz. "
                 f"'{analysis['consequencia_terra']} Seu GPS não voltará tão cedo.'")
    return {"cena_1_calmaria": cena1_str, "cena_2_perigo": cena2_str}

def gerar_roteiro_guia_aurora(analysis, chain_ids):
    # ... (função gerar_roteiro_guia_aurora completa)
    gst_dt = get_event_time('GST', chain_ids)
    if not gst_dt: return {"erro": "Não foi possível determinar o tempo da tempestade."}
    previsao_dt = gst_dt - timedelta(hours=2)
    cena1_str = (f"CENA 1: A PREVISÃO\nData: {previsao_dt.strftime('%d/%m/%Y, %H:%M')}. Local: Islândia.\n"
                 f"Kristín analisa os dados da NASA e vê a previsão de Kp ({analysis['max_kp']:.0f}) e o Bz virando para o sul. 'Agora vai ser um espetáculo', ela sussurra.")
    chegada_dt = gst_dt
    cena2_str = (f"CENA 2: A CHEGADA\nData: {chegada_dt.strftime('%d/%m/%Y, %H:%M')}.\n"
                 f"Alice entra no observatório. Kristín a cumprimenta: 'Eu sabia que você viria. Os dados não mentem. O show está para começar.'")
    show_dt = gst_dt + timedelta(hours=2)
    cena3_str = (f"CENA 3: O ESPETÁCULO\nData: {show_dt.strftime('%d/%m/%Y, %H:%M')}.\n"
                 f"Sob a aurora, Alice diz: 'Pensar que toda essa beleza foi causada por {analysis['causa_principal']}, uma explosão a 150 milhões de quilômetros.'")
    return {"cena_1_previsao": cena1_str, "cena_2_chegada": cena2_str, "cena_3_espetaculo": cena3_str}

# --- FUNÇÃO MESTRE DO JOGO ---

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