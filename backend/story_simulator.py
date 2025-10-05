# story_simulator.py

import json
import os
import random
from collections import deque
from rich import print # Usaremos 'rich' para uma saída mais bonita. Se não tiver, 'pip install rich'

# --- CONFIGURAÇÃO DA SIMULAÇÃO ---
CACHE_DIR = 'backend/cache/'
# O ID da supertempestade de Maio de 2024, nosso alvo para o teste
TARGET_STORM_ID = "2024-05-10T15:00:00-GST-001"

# As 3 histórias que temos disponíveis
STORIES = [
    {"type": "fisherman", "location": "Costa do Ceará, Brasil", "character_name": "Raimundo"},
    {"type": "farmer", "location": "Meio-Oeste, EUA", "character_name": "Joseph"},
    {"type": "aurora_guide", "location": "Islândia", "character_name": "Kristín"}
]

# --- FUNÇÕES (Reaproveitando nossa lógica modular) ---

def load_all_caches(cache_dir):
    """Carrega todos os caches JSON em um único dicionário mestre."""
    master_cache = {}
    event_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
    for filename in event_files:
        try:
            filepath = os.path.join(cache_dir, filename)
            event_type = filename.split('_')[1].split('.')[0].upper()
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            id_key = f"{event_type.lower()}ID"
            if event_type == 'FLR': id_key = 'flrID'
            
            for event in data:
                if id_key in event:
                    master_cache[event[id_key]] = event
        except Exception as e:
            print(f"Aviso: Erro ao carregar '{filename}': {e}")
            
    return master_cache

def get_event_chain(start_id, master_cache):
    """A partir de um ID inicial, encontra a cadeia completa de eventos relacionados."""
    if start_id not in master_cache: return []
    chain = set()
    queue = deque([start_id])
    while queue:
        current_id = queue.popleft()
        if current_id in chain: continue
        chain.add(current_id)
        event_details = master_cache.get(current_id, {})
        for linked_event in event_details.get('linkedEvents', []):
            linked_id = linked_event.get('activityID')
            if linked_id: queue.append(linked_id)
    return sorted(list(chain))

def get_full_event_details(event_ids, master_cache):
    """Pega a lista de IDs e retorna os detalhes completos de cada evento."""
    details = []
    for event_id in event_ids:
        if event_id in master_cache:
            details.append(master_cache[event_id])
    return details

# --- EXECUÇÃO DA SIMULAÇÃO ---
if __name__ == "__main__":
    print("[bold cyan]Iniciando Simulação de Geração de História...[/bold cyan]")
    
    # PASSO 1: Carregar toda a nossa base de conhecimento
    print("\n[yellow]Passo 1: Carregando todos os caches da pasta 'cache/'...[/yellow]")
    master_database = load_all_caches(CACHE_DIR)
    print(f"-> {len(master_database)} eventos carregados.")

    # PASSO 2: Rastrear a cadeia completa do nosso evento alvo
    print(f"\n[yellow]Passo 2: Rastreando a cadeia de eventos para a tempestade alvo ({TARGET_STORM_ID})...[/yellow]")
    full_chain_ids = get_event_chain(TARGET_STORM_ID, master_database)
    print(f"-> Cadeia encontrada com {len(full_chain_ids)} eventos interligados.")
    print(full_chain_ids)

    # PASSO 3: Juntar os detalhes completos de todos os eventos da cadeia
    print("\n[yellow]Passo 3: Montando o 'Dossiê Completo' do evento...[/yellow]")
    event_dossier = get_full_event_details(full_chain_ids, master_database)
    print(f"-> Dossiê montado com os detalhes de {len(event_dossier)} eventos.")

    # PASSO 4: Fazer o "mix" com uma das 3 histórias
    print("\n[yellow]Passo 4: Selecionando aleatoriamente uma das 3 histórias...[/yellow]")
    selected_story = random.choice(STORIES)
    print(f"-> História selecionada: {selected_story['type']} ({selected_story['character_name']})")

    # PASSO 5: Juntar tudo no pacote final
    print("\n[yellow]Passo 5: Juntando tudo no pacote de dados final para o jogo...[/yellow]")
    final_story_package = {
        "story_template": selected_story,
        "event_dossier": event_dossier
    }

    print("\n" + "="*50)
    print("[bold green]SIMULAÇÃO CONCLUÍDA! [/bold green]")
    print("Isto é o que teríamos juntado e enviado para o Godot:")
    print("="*50)
    
    # Imprime o resultado final de forma legível
    print(final_story_package)