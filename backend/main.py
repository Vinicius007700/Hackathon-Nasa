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

# NENHUM DADO É CARREGADO NA INICIALIZAÇÃO DO SERVIDOR

CACHE_DIR = 'backend/cache'

# --- ENDPOINTS DA API ---

@app.get("/")
def read_root():
    return {"Status": "Servidor do Stellar Stories está no ar! Aguardando comando para carregar dados."}

@app.get("/api/load-game-data")
def load_game_data():
    """
    Este endpoint é chamado pelo botão 'Play' do jogo.
    Ele executa a função que carrega TODOS os dados do disco para a memória do servidor.
    """
    print("\n[bold cyan]Endpoint /api/load-game-data ATIVADO.[/bold cyan]")
    
    # --- CORREÇÃO AQUI ---
    
    # 1. Chamamos a função que retorna APENAS o master_db
    master_db = load_data.load_all_caches(CACHE_DIR)
    
    # 2. Verificamos se o carregamento deu certo
    if master_db is None:
        return {
            "status": "error",
            "message": "Falha ao carregar os dados. Verifique o console do servidor."
        }

    # 3. AGORA, criamos a lista 'all_storms' a partir do master_db que acabamos de carregar
    all_storms = [event for event in master_db.values() if 'gstID' in event]
    
    # Adiciona uma mensagem no terminal para confirmar a contagem, como pedido
    print(f"[bold green]Carregamento concluído. {len(all_storms)} tempestades (GSTs) disponíveis.[/bold green]")

    # 4. A API responde com uma confirmação e o número de tempestades disponíveis.
    return {
        "status": "success",
        "message": f"Dados carregados. {len(all_storms)} tempestades estão prontas para serem escolhidas."
    }