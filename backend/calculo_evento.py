import json
import os
from collections import deque, Counter
from rich import print

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
    print(f"[cyan]Carregando arquivos de '{os.path.abspath(cache_dir)}'[/cyan]")
    try:
        files = os.listdir(cache_dir)
    except FileNotFoundError:
        print(f"[bold red]ERRO: Diretório não encontrado. Verifique se a pasta '{cache_dir}' existe.[/bold red]")
        return None
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
# PASSO 3: FUNÇÃO DE ANÁLISE DO DOSSIÊ (LÓGICA INTACTA)
# ==============================================================================

def analyze_storm_dossier(chain_ids, gst_event):
    # Sua correção está aqui, usando o penúltimo item do split
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

    max_kp = max(item.get('kpIndex', 0) for item in gst_event.get('allKpIndex', [])) if gst_event.get('allKpIndex') else 0
    
    if event_counts.get("MPC") and event_counts.get("GST"):
        earth_consequence_str = f"O escudo magnético foi atingido (MPC), iniciando a Tempestade Geomagnética (GST) com pico de Kp {max_kp:.2f}."
    elif event_counts.get("GST"):
        earth_consequence_str = f"Ocorreu uma Tempestade Geomagnética (GST) com pico de Kp {max_kp:.2f}."
    else:
        earth_consequence_str = "Impacto geomagnético mínimo ou não registrado."

    post_impact_outlook_str = "Efeitos de longo prazo mínimos."
    if event_counts.get("RBE"):
        post_impact_outlook_str = "Aumento no cinturão de radiação (RBE), um risco duradouro para satélites."

    return {
        "resumo_por_categoria": category_summary,
        "causa_principal": main_cause_str,
        "consequencia_terra": earth_consequence_str,
        "futuro_pos_impacto": post_impact_outlook_str,
    }

# ==============================================================================
# PASSO 4: <<<< NOVA FUNÇÃO >>>> GERADOR DE NARRATIVA
# ==============================================================================

def gerar_narrativa_historia(analysis, personagem):
    """Usa a análise pronta para gerar os textos da história para um personagem."""
    
    # ATO 1: O Aviso (Baseado na Causa Principal)
    causa = analysis['causa_principal']
    ato1 = (
        f"[bold]ATO 1: O AVISO[/bold]\n"
        f"{personagem['nome']}, um(a) {personagem['profissao']}, recebe uma notificação em seu terminal: "
        f"'Alerta de clima espacial. Causa provável: [yellow]{causa}[/yellow]. "
        f"Recomenda-se cautela com sistemas de navegação e equipamentos eletrônicos nas próximas 24-48 horas.'"
    )

    # ATO 2: O Impacto (Baseado na Consequência)
    consequencia = analysis['consequencia_terra']
    ato2 = (
        f"[bold]ATO 2: O IMPACTO[/bold]\n"
        f"No dia seguinte, enquanto {personagem['nome']} trabalha, uma figura misteriosa surge. No mesmo instante, "
        f"o GPS do seu trator autônomo perde o sinal e o rádio da oficina começa a emitir apenas ruído branco. A tempestade chegou. "
        f"([red]{consequencia}[/red])"
    )

    # ATO 3: A Explicação (Baseado no Resumo e no Futuro)
    futuro = analysis['futuro_pos_impacto']
    causas_detalhadas = ", ".join(analysis['resumo_por_categoria']['Causa'])
    ato3 = (
        f"[bold]ATO 3: A EXPLICAÇÃO[/bold]\n"
        f"A personagem explica o ocorrido: 'O que você presenciou foi o clímax de uma longa jornada que começou no Sol. "
        f"Tudo foi desencadeado por: [yellow]{causas_detalhadas}[/yellow]. "
        f"O impacto direto na Terra foi a tempestade, mas o perigo ainda não passou por completo. {futuro}'"
    )

    return {"ato1": ato1, "ato2": ato2, "ato3": ato3}

# ==============================================================================
# EXECUÇÃO PRINCIPAL
# ==============================================================================

if __name__ == "__main__":
    master_db = load_all_caches(CACHE_DIR)
    
    if not master_db:
        print("[bold red]Análise falhou.[/bold red]")
    else:
        TARGET_EVENT_ID = "2023-03-23T12:00:00-GST-001"
        target_event_details = master_db.get(TARGET_EVENT_ID)

        if target_event_details:
            # Lógica de análise que já tínhamos
            full_chain = get_full_event_chain_ids(TARGET_EVENT_ID, master_db)
            analysis = analyze_storm_dossier(full_chain, target_event_details)

            # <<<< NOVO >>>>
            # Agora, usamos a análise pronta para gerar a história
            personagem_exemplo = {"nome": "Joseph", "profissao": "Fazendeiro"}
            narrativa = gerar_narrativa_historia(analysis, personagem_exemplo)

            print("\n" + "="*80)
            print("[bold green]NARRATIVA GERADA PARA A HISTÓRIA[/bold green]")
            print("-" * 80)
            print(narrativa["ato1"])
            print("\n" + "-"*30)
            print(narrativa["ato2"])
            print("\n" + "-"*30)
            print(narrativa["ato3"])
            print("="*80)