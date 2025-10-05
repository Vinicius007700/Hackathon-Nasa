# event_definitions.py
# Nosso dicionário centralizado para definir e categorizar todos os eventos espaciais.

EVENT_DEFINITIONS = {
    "FLR": {
        "nome_completo": "Solar Flare (Erupção Solar)",
        "categoria": "Causa",
        "peso_impacto": 7,
        "descricao": "Uma explosão de radiação no Sol que viaja à velocidade da luz, chegando à Terra em 8 minutos. Causa blackouts de rádio."
    },
    "CME": {
        "nome_completo": "Coronal Mass Ejection (Ejeção de Massa Coronal)",
        "categoria": "Causa",
        "peso_impacto": 9,
        "descricao": "Uma gigantesca nuvem de plasma e campo magnético arremessada pelo Sol. Leva de 1 a 3 dias para chegar e é a principal causa de grandes tempestades."
    },
    "HSS": {
        "nome_completo": "High-Speed Stream (Fluxo de Vento de Alta Velocidade)",
        "categoria": "Causa",
        "peso_impacto": 6,
        "descricao": "Um fluxo contínuo e rápido de vento solar vindo de 'buracos' na coroa solar. Causa tempestades menos intensas, mas mais duradouras."
    },
    "SEP": {
        "nome_completo": "Solar Energetic Particle Event (Evento de Partículas Solares Energéticas)",
        "categoria": "Viagem",
        "peso_impacto": 8,
        "descricao": "Um bombardeio de partículas de alta energia que viajam perto da velocidade da luz. Chegam em minutos/horas e são um risco para astronautas e satélites."
    },
    "IPS": {
        "nome_completo": "Interplanetary Shock (Choque Interplanetário)",
        "categoria": "Viagem",
        "peso_impacto": 5,
        "descricao": "A onda de choque na frente de uma CME ou HSS. Sua detecção marca o momento exato da chegada iminente do evento principal na Terra."
    },
    "MPC": {
        "nome_completo": "Magnetopause Crossing (Cruzamento da Magnetopausa)",
        "categoria": "Impacto",
        "peso_impacto": 4,
        "descricao": "O momento em que a onda de choque comprime o escudo magnético da Terra (magnetosfera), marcando o primeiro contato físico."
    },
    "GST": {
        "nome_completo": "Geomagnetic Storm (Tempestade Geomagnética)",
        "categoria": "Impacto",
        "peso_impacto": 10,
        "descricao": "A perturbação global do campo magnético da Terra. Causa auroras espetaculares, falhas em redes elétricas e problemas de GPS."
    },
    "RBE": {
        "nome_completo": "Radiation Belt Enhancement (Aumento do Cinturão de Radiação)",
        "categoria": "Pós-Impacto",
        "peso_impacto": 7,
        "descricao": "O 'enchimento' dos cinturões de radiação de Van Allen com partículas energéticas após uma tempestade. Um perigo duradouro para satélites."
    }
}

# --- Exemplo de como usar este dicionário ---
if __name__ == "__main__":
    print("--- Dossiê de Fatores do Clima Espacial ---")
    
    # Imprime uma tabela-resumo de todos os eventos
    print(f"{'Sigla':<5} | {'Categoria':<12} | {'Peso':<5} | {'Nome Completo'}")
    print("-" * 60)
    for sigla, dados in EVENT_DEFINITIONS.items():
        print(f"{sigla:<5} | {dados['categoria']:<12} | {dados['peso_impacto']:<5} | {dados['nome_completo']}")

    print("\n" + "="*60)
    
    # Exemplo de como acessar os dados de um evento específico
    evento_alvo = "CME"
    dados_cme = EVENT_DEFINITIONS.get(evento_alvo)
    
    if dados_cme:
        print(f"\nDetalhes do evento: [ {evento_alvo} ]")
        print(f"  - Nome: {dados_cme['nome_completo']}")
        print(f"  - Categoria: {dados_cme['categoria']}")
        print(f"  - Peso de Impacto: {dados_cme['peso_impacto']}")
        print(f"  - Descrição: {dados_cme['descricao']}")