# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import load_data

# --- INICIALIZAÇÃO E CARREGAMENTO ÚNICO (A melhor prática) ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
MASTER_DB, ALL_STORMS = load_data.initialize_data()

# --- ENDPOINTS DA API ---

@app.get("/")
def read_root():
    return {"Status": "Servidor do Stellar Stories está no ar!"}

@app.get("/api/generate-story/{year}")
def generate_story_endpoint(year: int):
    """
    O endpoint principal do jogo! Recebe um ano, sorteia uma tempestade forte
    e retorna o pacote completo de análise e todas as histórias formatadas.
    """
    if not MASTER_DB or not ALL_STORMS:
        return {"error": "A base de dados não está pronta."}
    
    return load_data.generate_story_package_for_year(year, MASTER_DB, ALL_STORMS)