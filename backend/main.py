# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rich import print

# Importa nosso cérebro de dados
from . import load_data

# --- INICIALIZAÇÃO E "CACHE" GLOBAL ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# Variáveis globais que funcionarão como um "cache" na memória do servidor.
# Elas começam vazias.
MASTER_DB = None
ALL_STORMS = None

# --- ENDPOINTS DA API ---

# @app.get("/")
# def read_root():
#     status = "Dados não carregados."
#     if ALL_STORMS is not in None:
#         status = f"{len(ALL_STORMS)} tempestades carregadas e prontas."
#     return {"Status": "Servidor do Stellar Stories está no ar!", "Data Status": status}

@app.get("/api/load-game-data")
def load_game_data():
    """
    ENDPOINT 1: Chamado pelo botão 'Play'.
    Carrega todos os dados do disco e os armazena nas variáveis globais do servidor.
    """
    global MASTER_DB, ALL_STORMS
    print("\n[bold cyan]Endpoint /api/load-game-data ATIVADO.[/bold cyan]")
    
    # Chama a função de inicialização do load_data
    master_db_loaded, all_storms_loaded = load_data.load_all_data_on_demand()
    
    if master_db_loaded is None or all_storms_loaded is None:
        return {"status": "error", "message": "Falha ao carregar os dados."}

    # Armazena os dados carregados nas variáveis globais para uso futuro
    MASTER_DB = master_db_loaded
    ALL_STORMS = all_storms_loaded

    return {
        "status": "success",
        "message": f"Dados carregados. {len(ALL_STORMS)} tempestades estão prontas na memória do servidor."
    }

@app.get("/api/generate-story/{year}")
def generate_story_endpoint(year: int):
    """
    ENDPOINT 2: Chamado após o jogador escolher um ano.
    Usa os dados já em memória para selecionar uma tempestade e gerar o pacote completo.
    """
    print(f"\n[bold cyan]Endpoint /api/generate-story/{year} ATIVADO.[/bold cyan]")
    
    # Primeiro, verifica se o endpoint de carregamento já foi chamado
    if MASTER_DB is None or ALL_STORMS is None:
        return {"error": "Os dados ainda não foram carregados. Chame /api/load-game-data primeiro."}

    final_package = load_data.generate_story_package_for_year(year, MASTER_DB, ALL_STORMS)

    return final_package

