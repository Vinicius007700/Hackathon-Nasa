import json
import os
from collections import deque
from rich import print

# --- CONFIGURAÇÃO ---
# Assumindo que os caches estão em 'backend/cache/'
CACHE_DIR = 'backend/cache' # Mude se necessário
GST_FILE = os.path.join(CACHE_DIR, 'nasa_gst.json')

# --- FUNÇÕES (Reutilizando as funções robustas que já fizemos) ---

def load_all_caches(cache_dir):
    """Carrega todos os caches JSON em um único dicionário mestre para acesso rápido."""
    master_cache = {}
    id_key_map = {
        'GST': 'gstID', 'CME': 'activityID', 'HSS': 'hssID', 'IPS': 'ipsID',
        'FLR': 'flrID', 'SEP': 'sepID', 'RBE': 'rbeID', 'MPC': 'mpcID'
    }
    event_files = [f for f in os.listdir(cache_dir) if f.startswith('nasa_') and f.endswith('.json')]
    print(f"[cyan]Carregando {len(event_files)} arquivos de cache...[/cyan]")

    for filename in event_files:
        try:
            event_type = filename.split('_')[1].split('.')[0].upper()
            id_key = id_key_map.get(event_type)
            if not id_key: continue

            filepath = os.path.join(cache_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for event in data:
                event_id = event.get('activityID') if event_type == 'CME' else event.get(id_key)
                if event_id:
                    master_cache[event_id] = event
        except Exception as e:
            print(f"[bold red]Erro ao carregar '{filename}': {e}[/bold red]")
            
    print(f"[bold green]Cache Mestre pronto com {len(master_cache)} eventos totais.[/bold green]")
    return master_cache

def get_full_event_chain_ids(start_id, master_cache):
    """Rastreia recursivamente TODOS os eventos ligados, não importa a profundidade."""
    if start_id not in master_cache: return []
    chain = set()
    queue = deque([start_id])
    while queue:
        current_id = queue.popleft()
        if current_id in chain: continue
        chain.add(current_id)
        event_details = master_cache.get(current_id, {})
        for linked_event in event_details.get('linkedEvents') or []:
            linked_id = linked_event.get('activityID')
            if linked_id: queue.append(linked_id)
    return sorted(list(chain))

# --- EXECUÇÃO PRINCIPAL ---

if __name__ == "__main__":
    # Passo 1: Carregar toda a base de dados
    master_database = load_all_caches(CACHE_DIR)
    
    if not master_database:
        print("[bold red]Nenhum dado carregado. Saindo.[/bold red]")
    else:
        # Passo 2: Pegar o primeiro evento GST como nosso alvo
        try:
            with open(GST_FILE, 'r', encoding='utf-8') as f:
                all_gst_events = json.load(f)
            
            if not all_gst_events:
                raise ValueError("Arquivo GST está vazio.")
            
            target_event = all_gst_events[1] # Pegando o segundo evento para variar
            target_event_id = target_event.get('gstID')
            
            print("\n" + "="*50)
            print(f"Analisando o primeiro evento GST encontrado: [bold yellow]{target_event_id}[/bold yellow]")
            print("="*50)

            # Passo 3: Análise Nível 1 (Superficial)
            print("\n[bold cyan]--- ANÁLISE NÍVEL 1: DADOS DIRETOS DO EVENTO ---[/bold cyan]")
            
            # Calcular o Kp máximo
            all_kp = target_event.get('allKpIndex', [])
            max_kp = 0
            if all_kp:
                max_kp = max(item.get('kpIndex', 0) for item in all_kp)
            print(f"-> Pico de Kp Index registrado: [bold red]{max_kp:.2f}[/bold red]")

            # Listar "suspeitos" diretos
            direct_links = [link['activityID'] for link in target_event.get('linkedEvents', [])]
            print(f"-> {len(direct_links)} 'suspeitos' diretos encontrados:")
            for link in direct_links:
                print(f"  - {link}")

            # Passo 4: Análise Nível 2 (Profunda)
            print("\n[bold cyan]--- ANÁLISE NÍVEL 2: RASTREAMENTO PROFUNDO DA CAUSA RAIZ ---[/bold cyan]")
            
            full_chain = get_full_event_chain_ids(target_event_id, master_database)
            
            print(f"-> Rastreamento completo encontrou [bold green]{len(full_chain)}[/bold green] eventos na cadeia total:")
            for event_id in full_chain:
                is_new = " (NOVO!)" if event_id not in direct_links and event_id != target_event_id else ""
                color = "green" if is_new else "white"
                print(f"  - [{color}]{event_id}{is_new}[/{color}]")

            # Passo 5: Conclusão da Análise
            print("\n" + "="*50)
            print("[bold green]CONCLUSÃO DA ANÁLISE:[/bold green]")
            if len(full_chain) > len(direct_links) + 1:
                print("A análise profunda revelou eventos adicionais. A iteração [bold]NÃO é redundante[/bold] e é essencial para montar o dossiê completo.")
            else:
                print("Neste caso específico, a análise profunda não encontrou mais eventos, mas o processo é vital para garantir que nada seja perdido.")
            
        except FileNotFoundError:
            print(f"[bold red]ERRO: Arquivo de eventos GST '{GST_FILE}' não encontrado![/bold red]")
        except Exception as e:
            print(f"[bold red]ERRO ao processar o evento GST: {e}[/bold red]")