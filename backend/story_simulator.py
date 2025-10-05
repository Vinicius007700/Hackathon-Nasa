# story_simulator.py (versão Hackathon - Rápida e Funcional)

import json
import os
import random
from collections import deque
from rich import print
from datetime import datetime

# --- CONFIGURAÇÃO ---
# Garanta que o caminho para o cache esteja correto a partir de onde você executa o script
CACHE_DIR = 'backend/cache' # Supondo que os JSONs estão no mesmo diretório do script
TARGET_STORM_ID = "2024-05-10T15:00:00-GST-001"
STORIES = [
    {"type": "fisherman", "location": "Costa do Ceara, Brasil", "character_name": "Raimundo"},
    {"type": "farmer", "location": "Meio-Oeste, EUA", "character_name": "Joseph"},
    {"type": "aurora_guide", "location": "Islândia", "character_name": "Kristin"}
]

# --- FUNÇÕES ---

def load_all_caches(cache_dir):
    """Carrega todos os caches JSON em um único dicionário mestre."""
    master_cache = {}
    
    # <<<< MELHORIA >>>>
    # Garante que temos todos os tipos de eventos mapeados corretamente
    # Os nomes das chaves (GST, CME...) devem corresponder ao que está no nome do arquivo
    id_key_map = {
        'GST': 'gstID',
        'CME': 'activityID', # CME usa 'activityID' como chave primária nos dados da NASA
        'HSS': 'hssID',
        'IPS': 'ipsID',
        'FLR': 'flrID',
        'SEP': 'sepID',
        'RBE': 'rbeID',
        'MPC': 'mpcID'
    }

    # Procura por arquivos que sigam o padrão "nasa_TIPO.json"
    event_files = [f for f in os.listdir(cache_dir) if f.startswith('nasa_') and f.endswith('.json')]
    print(f"[cyan]Encontrados {len(event_files)} arquivos de cache para carregar.[/cyan]")

    for filename in event_files:
        try:
            # Extrai o tipo de evento do nome do arquivo (ex: 'gst' de 'nasa_gst.json')
            event_type = filename.split('_')[1].split('.')[0].upper()
            
            id_key = id_key_map.get(event_type)
            if not id_key:
                print(f"[yellow]Aviso: Tipo de evento '{event_type}' do arquivo '{filename}' não mapeado. Pulando.[/yellow]")
                continue

            filepath = os.path.join(cache_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            count = 0
            for event in data:
                # <<<< MELHORIA >>>>
                # A chave primária para CMEs nos dados da NASA é 'activityID'
                event_id = event.get('activityID') if event_type == 'CME' else event.get(id_key)
                if event_id:
                    # A chave do nosso banco de dados é o ID único do evento
                    master_cache[event_id] = event
                    count += 1
            print(f"  -> Carregado [green]{count}[/green] eventos do tipo [bold]{event_type}[/bold] de '{filename}'")

        except Exception as e:
            print(f"[bold red]Erro Crítico:[/bold red] Falha ao carregar ou processar '{filename}': {e}")
            
    print(f"\n[bold green]Cache Mestre carregado com {len(master_cache)} eventos totais.[/bold green]")
    return master_cache

def get_event_chain(start_id, master_cache):
    """Usa busca em largura para encontrar todos os IDs de eventos interligados."""
    if start_id not in master_cache:
        print(f"[bold red]Erro:[/bold red] O ID inicial '{start_id}' não foi encontrado no cache mestre!")
        return []
        
    chain = set()
    queue = deque([start_id])
    
    while queue:
        current_id = queue.popleft()
        if current_id in chain:
            continue
            
        chain.add(current_id)
        event_details = master_cache.get(current_id, {})
        
        # linkedEvents pode ser None, então usamos .get com uma lista vazia como padrão
        for linked_event in event_details.get('linkedEvents') or []:
            linked_id = linked_event.get('activityID')
            if linked_id and linked_id not in chain:
                queue.append(linked_id)
                
    return sorted(list(chain))

def get_full_event_details(event_ids, master_cache):
    """Busca os detalhes completos para uma lista de IDs de eventos."""
    details = []
    for event_id in event_ids:
        if event_id in master_cache:
            details.append(master_cache[event_id])
        else:
            print(f"[yellow]Aviso: O ID vinculado '{event_id}' não foi encontrado no cache mestre.[/yellow]")
    return details


def process_and_assign_story(dossier, stories):
    """Recebe o dossiê bruto, 'mastiga' os dados, e os combina com uma história."""
    if not dossier:
        print("[bold red]Erro: Dossiê de eventos está vazio. Impossível gerar história.[/bold red]")
        return None

    selected_story = random.choice(stories)
    
    # Encontra o evento GST principal para obter os dados da tempestade
    gst_event = next((event for event in dossier if "gstID" in event), None)
    if not gst_event:
        print("[bold red]Erro: Nenhum evento GST encontrado no dossiê.[/bold red]")
        return None

    # --- Mastigação dos Dados ---
    all_kp_indices = gst_event.get('allKpIndex', [])
    peak_kp = max([item.get('kpIndex', 0) for item in all_kp_indices]) if all_kp_indices else 0
    start_time = gst_event.get('startTime')
    
    # Identifica as causas potenciais no dossiê
    cme_events = [evt for evt in dossier if "cmeID" in evt or (evt.get("activityID") and "CME" in evt.get("activityID"))]
    hss_events = [evt for evt in dossier if "hssID" in evt]
    
    # Lógica de Causa Raiz (Heurística MVP)
    if cme_events:
        main_cause = f"{len(cme_events)} Ejeção(ões) de Massa Coronal (CME)"
    elif hss_events:
        main_cause = f"{len(hss_events)} Fluxo(s) de Vento de Alta Velocidade (HSS)"
    else:
        main_cause = "Causa Mista ou Indeterminada"

    story_type = selected_story['type']
    explanation_text = generate_impact_explanation(peak_kp, main_cause, story_type)
    
    character_impact = {
        "title": f"Impacto para {story_type.replace('_', ' ').title()}",
        "explanation": explanation_text
    }
    
    # Extrai o primeiro evento IPS para ter a hora de chegada do choque
    ips_event = next((evt for evt in dossier if "ipsID" in evt), None)
    ips_arrival_time = ips_event.get('eventTime') if ips_event else None


    final_package = {
        "character_name": selected_story['character_name'],
        "location": selected_story['location'],
        "story_type": story_type,
        "event_summary": {
            "title": f"Tempestade Geomagnética de {datetime.strptime(start_time, '%Y-%m-%dT%H:%MZ').strftime('%B de %Y')}",
            "peak_kp": round(peak_kp, 2),
            "start_time": start_time,
            "main_cause": main_cause
        },
        "timeline_data": {
            "kp_readings": gst_event.get('allKpIndex', []),
            "cme_launch_times": sorted([evt.get('startTime') for evt in cme_events if evt.get('startTime')]),
            "ips_arrival_time": ips_arrival_time
        },
        "character_impact": character_impact
    }
    return final_package

def generate_impact_explanation(peak_kp, main_cause, story_type):
    """Gera texto dinâmico para o personagem com base nos dados da tempestade."""
    explanation = ""
    if peak_kp >= 9:
        explanation += f"Esta é uma tempestade G5 (Extrema) com pico Kp {peak_kp:.2f}. O impacto no GPS é severo, com perda de sinal generalizada podendo durar por um ou mais dias."
    elif peak_kp >= 8:
        explanation += f"Esta é uma tempestade G4 (Severa) com pico Kp {peak_kp:.2f}. Espera-se erros de posicionamento e perda de sinal de GPS por muitas horas."
    elif peak_kp >= 7:
        explanation += f"Esta é uma tempestade G3 (Forte) com pico Kp {peak_kp:.2f}. Problemas intermitentes com o sinal de GPS podem ocorrer por várias horas."
    elif peak_kp >= 6:
        explanation += f"Esta é uma tempestade G2 (Moderada) com pico Kp {peak_kp:.2f}. Pode causar degradação na precisão do GPS e afetar sistemas de navegação."
    else:
        explanation += f"Esta é uma tempestade G1 (Menor) com pico Kp {peak_kp:.2f}. Impactos em tecnologia são mínimos, mas auroras podem ser visíveis em latitudes mais altas."

    if "CME" in main_cause:
        explanation += " A causa é uma onda de choque explosiva vinda do Sol, tornando o impacto súbito e violento."
    elif "HSS" in main_cause:
        explanation += " A causa é um fluxo persistente de vento solar, tornando o impacto menos súbito, mas potencialmente mais duradouro."

    if story_type == "fisherman":
        explanation += " Para um pescador que depende de GPS para navegação e localização de cardumes, isso pode significar ficar sem rumo ou não conseguir operar seus equipamentos mais modernos, arriscando a segurança e o sustento."
    elif story_type == "farmer":
        explanation += " Para um agricultor de precisão, isso significa a paralisação completa das operações guiadas por satélite, como plantio e colheita automatizados, causando atrasos críticos no cronograma da safra."
    elif story_type == "aurora_guide":
        explanation += " Para um guia de auroras, esta é uma oportunidade de ouro! Uma tempestade dessa magnitude promete auroras espetaculares, visíveis em locais raros, atraindo turistas e garantindo um show inesquecível."
        
    return explanation

# --- EXECUÇÃO ---
if __name__ == "__main__":
    print("[bold yellow]Iniciando Simulação de História - Hackathon Mode[/bold yellow]")
    
    master_database = load_all_caches(CACHE_DIR)
    
    if not master_database:
        print("[bold red]O cache mestre está vazio. Verifique se os arquivos JSON estão no diretório correto e não estão corrompidos. Abortando.[/bold red]")
    else:
        full_chain_ids = get_event_chain(TARGET_STORM_ID, master_database)
        event_dossier = get_full_event_details(full_chain_ids, master_database)
        
        print(f"\n[bold cyan]Cadeia de Eventos Completa para {TARGET_STORM_ID}: {len(full_chain_ids)} IDs encontrados.[/bold cyan]")
        print(f"[bold cyan]Dossiê montado com {len(event_dossier)} detalhes de eventos.[/bold cyan]")

        print("\n[yellow]Analisando e 'mastigando' o dossiê para o jogo...[/yellow]")
        final_story_package = process_and_assign_story(event_dossier, STORIES)
        
        print("\n" + "="*80)
        print("[bold green]SIMULAÇÃO CONCLUÍDA! Pacote de dados 'SUPER-MASTIGADO' pronto para o Godot:[/bold green]")
        print("="*80)
        
        # Usando a biblioteca rich para imprimir o JSON de forma bonita
        print(json.dumps(final_story_package, indent=4))