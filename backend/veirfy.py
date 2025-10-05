import json
import os
from collections import Counter
from datetime import datetime
from rich import print

# Caminho para o arquivo de dados
GST_FILE_PATH = 'backend/cache/nasa_gst.json'

def count_storms_by_year(file_path: str):
    """
    Carrega o arquivo de tempestades (GST) e conta quantas ocorrências
    existem para os anos de 2023, 2024 e 2025.

    Args:
        file_path: O caminho para o arquivo nasa_gst.json.

    Returns:
        Um dicionário com a contagem de tempestades por ano.
    """
    print(f"Analisando o arquivo em: '{os.path.abspath(file_path)}'")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            all_storms = json.load(f)
    except FileNotFoundError:
        print(f"[bold red]Erro: Arquivo não encontrado em '{file_path}'.[/bold red]")
        return None
    except json.JSONDecodeError:
        print(f"[bold red]Erro: O arquivo '{file_path}' não é um JSON válido.[/bold red]")
        return None

    # Extrai o ano de cada tempestade usando a string 'startTime'
    years = []
    for storm in all_storms:
        if 'startTime' in storm:
            try:
                # Converte a string de data para um objeto datetime e pega o ano
                year = datetime.fromisoformat(storm['startTime'].replace('Z', '')).year
                years.append(year)
            except (ValueError, TypeError):
                # Ignora entradas com formato de data inválido
                continue
    
    # Usa o Counter para fazer a contagem de forma eficiente
    year_counts = Counter(years)
    return year_counts

# --- Execução do Teste ---
if __name__ == "__main__":
    print("[bold cyan]Iniciando teste de contagem de tempestades por ano...[/bold cyan]")
    
    storm_counts = count_storms_by_year(GST_FILE_PATH)
    
    if storm_counts:
        print("\n" + "="*40)
        print("[bold green]Resultado da Contagem:[/bold green]")
        print("-" * 40)
        
        # Exibe os resultados para os anos específicos que você pediu
        count_2023 = storm_counts.get(2023, 0)
        count_2024 = storm_counts.get(2024, 0)
        count_2025 = storm_counts.get(2025, 0)
        
        print(f"Tempestades em 2023: [yellow]{count_2023}[/yellow]")
        print(f"Tempestades em 2024: [yellow]{count_2024}[/yellow]")
        print(f"Tempestades em 2025: [yellow]{count_2025}[/yellow]")
        
        print("="*40)