# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rich import print

# Importa nosso módulo de dados
import load_data

# --- INICIALIZAÇÃO VAZIA ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# <<< MUDANÇA IMPORTANTE >>>
# Variáveis globais para armazenar os dados na memória após o carregamento
MASTER_DB = None
ALL_STORMS = None

# --- ENDPOINTS DA API ---

@app.get("/")
def read_root():
    status = "Dados não carregados."
    if ALL_STORMS is not None:
        status = f"{len(ALL_STORMS)} tempestades carregadas e prontas."
    return {"Status": "Servidor do Stellar Stories está no ar!", "Data Status": status}

@app.get("/api/load-game-data")
def load_game_data():
    """
    Endpoint chamado pelo 'Play'. Carrega TODOS os dados e os armazena
    nas variáveis globais do servidor.
    """
    global MASTER_DB, ALL_STORMS
    print("\n[bold cyan]Endpoint /api/load-game-data ATIVADO.[/bold cyan]")
    
    master_db, all_storms = load_data.load_all_data_on_demand()
    
    if master_db is None or all_storms is None:
        return {"status": "error", "message": "Falha ao carregar os dados."}

    # Armazena os dados carregados nas variáveis globais
    MASTER_DB = master_db
    ALL_STORMS = all_storms

    return {"status": "success", "message": f"Dados carregados. {len(ALL_STORMS)} tempestades prontas."}


# <<<< NOVO ENDPOINT >>>>
@app.get("/api/select-storm/{year}")
def select_storm(year: int):
    """
    Recebe um ano, seleciona aleatoriamente uma das 6 tempestades mais fortes
    e retorna o ID (start_id) dela.
    """
    print(f"\n[bold cyan]Endpoint /api/select-storm/{year} ATIVADO.[/bold cyan]")

    # Verifica se os dados foram carregados primeiro
    if ALL_STORMS is None:
        return {"error": "Dados não foram carregados. Chame /api/load-game-data primeiro."}

    # Chama a nova função do load_data para fazer a seleção
    selected_storm = load_data.select_random_top_storm_for_year(year, ALL_STORMS)

    if selected_storm is None:
        return {"error": f"Nenhuma tempestade encontrada para o ano {year}."}

    # Retorna o ID da tempestade para o Godot usar no próximo passo
    return {"selected_storm_id": selected_storm['gstID']}