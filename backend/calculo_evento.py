import json
import os
from collections import deque, Counter
from rich import print
from datetime import datetime, timedelta

# ==============================================================================
# PASSO 1: DEFINIÇÕES E REGRAS (Nossa "Fonte da Verdade")
# ==============================================================================
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

# ==============================================================================
# PASSO 2: FUNÇÕES DE CARREGAMENTO E RASTREAMENTO (LÓGICA INTACTA)
# ==============================================================================
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

# ==============================================================================
# PASSO 3: FUNÇÃO DE ANÁLISE DO DOSSIÊ (PEQUENA ADIÇÃO)
# ==============================================================================

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

# ==============================================================================
# PASSO 4: GERADORES DE ROTEIRO PERSONALIZADOS
# ==============================================================================

def get_event_time(event_type, chain_ids):
    event_id = next((eid for eid in chain_ids if f"-{event_type}-" in eid), None)
    if not event_id: return None
    return datetime.fromisoformat(event_id[:19])

def gerar_roteiro_fazendeiro(analysis, chain_ids, personagem):
    # (Lógica intacta)
    causa_ids = [eid for eid in chain_ids if EVENT_DEFINITIONS.get(eid.split('-')[-2], {}).get('categoria') == 'Causa']
    aviso_dt = get_event_time('CME', causa_ids) or get_event_time('FLR', causa_ids)
    aviso_str = f"Notificação Push\n{aviso_dt.strftime('%d/%m %H:%M')} : Alerta de clima espacial. Causa: {analysis['causa_principal']}. Risco para GPS."
    impacto_dt = get_event_time('MPC', chain_ids)
    impacto_str = (f"Em {impacto_dt.strftime('%d/%m às %H:%M')}, Alice chega. No mesmo instante, os tratores de Joseph param. "
                   f"'A tempestade chegou', diz ela. 'Seu GPS não vai funcionar, mas eu ajudo a guiar a colheita.'")
    gst_dt = get_event_time('GST', chain_ids)
    futuro_dt = gst_dt + timedelta(hours=24)
    explicacao_str = (f"Mais tarde, Alice explica: 'Tudo começou com {analysis['causa_principal']}. "
                      f"A partir de {futuro_dt.strftime('%d/%m às %H:%M')}, o perigo continua... ({analysis['futuro_pos_impacto']})'")
    return {"Ato 1: O Aviso": aviso_str, "Ato 2: O Impacto": impacto_str, "Ato 3: A Explicação": explicacao_str}

def gerar_roteiro_pescador(analysis, chain_ids, personagem):
    # (Lógica intacta)
    gst_dt = get_event_time('GST', chain_ids)
    if not gst_dt: return {"erro": "Não foi possível determinar o tempo da tempestade."}
    pre_storm_dt = gst_dt - timedelta(hours=6)
    cena1_str = (f"CENA 1: A CALMARIA\nData: {pre_storm_dt.strftime('%d/%m/%Y, %H:%M')}. Local: Costa do Brasil.\n"
                 f"{personagem['nome']} prepara seu barco, confiando no seu GPS. Mal sabe ele que uma tempestade solar se aproxima.")
    cena2_str = (f"CENA 2: O PERIGO NO MAR\nData: {gst_dt.strftime('%d/%m/%Y, %H:%M')}. Local: Mar aberto.\n"
                 f"Longe da costa, o GPS de Raimundo apaga. Ele está perdido. Alice surge. 'Você foi pego por uma tempestade geomagnética!', ela diz. "
                 f"'{analysis['consequencia_terra']} Seu GPS não voltará tão cedo.'")
    return {"Cena 1: A Calmaria": cena1_str, "Cena 2: O Perigo no Mar": cena2_str}

def gerar_roteiro_guia_aurora(analysis, chain_ids, personagem):
    """ <<<< NOVA FUNÇÃO >>>> Gera a narrativa de 3 cenas para a Guia de Aurora."""
    gst_dt = get_event_time('GST', chain_ids)
    if not gst_dt: return {"erro": "Não foi possível determinar o tempo da tempestade."}
    
    previsao_dt = gst_dt - timedelta(hours=2)
    cena1_str = (
        f"CENA 1: A PREVISÃO\nData: {previsao_dt.strftime('%d/%m/%Y, %H:%M')}. Local: Islândia.\n"
        f"{personagem['nome']}, uma especialista em auroras, analisa os dados da NASA. Ela vê a alta previsão de Kp ({analysis['max_kp']:.0f}) e sorri "
        f"ao notar que o componente Bz (o 'convite VIP') virou para o sul. 'A previsão era boa', ela sussurra, 'mas agora vai ser um espetáculo.'"
    )

    chegada_dt = gst_dt
    cena2_str = (
        f"CENA 2: A CHEGADA\nData: {chegada_dt.strftime('%d/%m/%Y, %H:%M')}.\n"
        f"Alice entra no observatório. {personagem['nome']} a cumprimenta sem surpresa. 'Eu sabia que você viria. Os dados não mentem', diz ela. "
        f"'A conexão está aberta. O show está para começar.'"
    )

    show_dt = gst_dt + timedelta(hours=2)
    cena3_str = (
        f"CENA 3: O ESPETÁCULO\nData: {show_dt.strftime('%d/%m/%Y, %H:%M')}.\n"
        f"Sob um céu dançante de luzes verdes e violetas, elas observam a aurora. 'É lindo, não é?', diz Alice. "
        f"'Pensar que toda essa beleza foi causada por [yellow]{analysis['causa_principal']}[/yellow], uma explosão a 150 milhões de quilômetros de distância.'"
    )

    return {"Cena 1: A Previsão": cena1_str, "Cena 2: A Chegada": cena2_str, "Cena 3: O Espetáculo": cena3_str}


def gerar_historia(analysis, chain_ids, personagem):
    """Função 'diretora' que escolhe o roteiro certo."""
    tipo_personagem = personagem.get("tipo")
    if tipo_personagem == "fazendeiro":
        return gerar_roteiro_fazendeiro(analysis, chain_ids, personagem)
    elif tipo_personagem == "pescador":
        return gerar_roteiro_pescador(analysis, chain_ids, personagem)
    elif tipo_personagem == "guia_aurora":
        # <<<< ADIÇÃO >>>>
        return gerar_roteiro_guia_aurora(analysis, chain_ids, personagem)
    else:
        return {"erro": "Tipo de personagem não reconhecido."}

# ==============================================================================
# EXECUÇÃO PRINCIPAL
# ==============================================================================
if __name__ == "__main__":
    master_db = load_all_caches(CACHE_DIR)
    
    if master_db:
        TARGET_EVENT_ID = "2023-03-23T12:00:00-GST-001"
        target_event_details = master_db.get(TARGET_EVENT_ID)

        if target_event_details:
            full_chain = get_full_event_chain_ids(TARGET_EVENT_ID, master_db)
            analysis = analyze_storm_dossier(full_chain, target_event_details)

            # Definição dos nossos 3 personagens
            personagem_fazendeiro = {"nome": "Joseph", "profissao": "Fazendeiro", "tipo": "fazendeiro"}
            personagem_pescador = {"nome": "Raimundo", "profissao": "Pescador", "tipo": "pescador"}
            personagem_guia_aurora = {"nome": "Kristín", "profissao": "Guia de Auroras", "tipo": "guia_aurora"}

            # Geração das histórias
            roteiro_fazendeiro = gerar_historia(analysis, full_chain, personagem_fazendeiro)
            roteiro_pescador = gerar_historia(analysis, full_chain, personagem_pescador)
            roteiro_guia_aurora = gerar_historia(analysis, full_chain, personagem_guia_aurora)

            # Apresentação dos roteiros
            print("\n" + "="*80)
            print("[bold green]ROTEIRO GERADO PARA: FAZENDEIRO (JOSEPH)[/bold green]")
            for nome_ato, texto in roteiro_fazendeiro.items(): print(f"\n[bold cyan]{nome_ato}[/bold cyan]\n{texto}")
            
            print("\n" + "="*80)
            print("[bold green]ROTEIRO GERADO PARA: PESCADOR (RAIMUNDO)[/bold green]")
            for nome_cena, texto in roteiro_pescador.items(): print(f"\n[bold cyan]{nome_cena}[/bold cyan]\n{texto}")

            print("\n" + "="*80)
            print("[bold green]ROTEIRO GERADO PARA: GUIA DE AURORAS (KRISTÍN)[/bold green]")
            for nome_cena, texto in roteiro_guia_aurora.items(): print(f"\n[bold cyan]{nome_cena}[/bold cyan]\n{texto}")
            print("="*80)