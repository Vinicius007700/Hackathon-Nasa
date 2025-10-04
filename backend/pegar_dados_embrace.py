# data_downloader.py (versão final, simplificada e correta)

import requests
import pandas as pd
from datetime import datetime
from io import StringIO
import os
import time

# --- Constantes Globais ---
# O padrão da URL que você descobriu
BASE_URL = "https://embracedata.inpe.br/scintillation/{year}/{station_code}/{day_of_year}/{file_prefix}_{date_str}.dat"
CACHE_DIR = "cache/"

# --- Função Principal Simplificada ---

def fetch_scintillation_data_direct(station_code, start_date_str, end_date_str):
    """
    Baixa os dados de cintilação minuto a minuto, com um feedback de progresso interativo.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    minute_range = pd.date_range(start=start_date_str, end=end_date_str, freq='T')
    
    total_minutes = len(minute_range)
    print(f"Iniciando verificação de {total_minutes} minutos de dados para a estação '{station_code}'...")
    
    all_dataframes = []
    success_count = 0  # Novo: contador para arquivos encontrados
    
    # Usamos enumerate para ter um contador (i) para o progresso
    for i, timestamp in enumerate(minute_range, 1):
        # --- INÍCIO DO FEEDBACK DE PROGRESSO ---
        # Imprime o status na mesma linha. end='\r' faz a mágica acontecer.
        progress_text = f"Progresso: {i}/{total_minutes} minutos verificados | Arquivos encontrados: {success_count}"
        print(progress_text, end='\r')
        # --- FIM DO FEEDBACK DE PROGRESSO ---

        year = timestamp.year
        day_of_year = timestamp.strftime('%j')
        file_prefix = station_code[:3]
        date_str = timestamp.strftime('%Y-%m-%d-%H-%M')
        
        file_url = BASE_URL.format(
            year=year,
            station_code=station_code,
            day_of_year=day_of_year,
            file_prefix=file_prefix,
            date_str=date_str
        )
        
        try:
            response = requests.get(file_url)
            response.raise_for_status() 
            
            # Se chegamos aqui, o arquivo foi encontrado!
            success_count += 1 # Novo: incrementa o contador
            
            data_text = response.text
            if not data_text.strip():
                continue

            col_names = ['satellite_prn', 's4_index', 'status_flag', 'azimuth', 'elevation','param6', 'param7', 'param8', 'param9', 'param10', 'internal_code']
            data_io = StringIO(data_text)
            df = pd.read_csv(data_io, delim_whitespace=True, header=None, names=col_names)
            df['timestamp'] = timestamp
            df['station'] = station_code
            all_dataframes.append(df)
            
            # Pausa para não sobrecarregar o servidor
            time.sleep(0.1)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                continue
            else:
                # Se der um erro diferente de 404, é bom saber
                print(f"\nErro de HTTP para {timestamp}: {e}")
        except Exception:
            # Ignora outros erros para continuar o processo
            continue

    # Adiciona uma linha em branco ao final para não sobrescrever a última linha de progresso
    print("\n" + "="*50)

    print("\nAgregando todos os dados encontrados...")
    master_df = pd.concat(all_dataframes, ignore_index=True)
    
    # 2. Define o nome do arquivo CSV de saída
    start_date_file_str = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M").strftime("%Y%m%d")
    output_filename = f"{CACHE_DIR}embrace_scintillation_{station_code}_{start_date_file_str}_consolidado.csv"
    
    # 3. SALVA A TABELA NO ARQUIVO CSV
    master_df.to_csv(output_filename, index=False)

    # 4. Imprime a confirmação final para você
    print(f"\nSUCESSO! {success_count} arquivos de minuto processados.")
    print(f"Dados consolidados salvos em: {output_filename}")

    if not all_dataframes:
        print("Nenhum dado de cintilação foi encontrado no período especificado.")
        return

    print("Agregando todos os dados encontrados...")
    master_df = pd.concat(all_dataframes, ignore_index=True)
    
    start_date_file_str = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M").strftime("%Y%m%d")
    output_filename = f"{CACHE_DIR}embrace_scintillation_{station_code}_{start_date_file_str}_consolidado.csv"
    master_df.to_csv(output_filename, index=False)

    print(f"SUCESSO! {success_count} arquivos de minuto processados.")
    print(f"Dados consolidados salvos em: {output_filename}")


# --- PAINEL DE CONTROLE E EXECUÇÃO ---
if __name__ == "__main__":
    # --- AJUSTE AQUI ---
    # Defina a estação e o período que você quer baixar.
    
    STATION = "ceeu"  # Estação para a história no Ceará
    # Inclui o último minuto do dia 01/11 para garantir que o dia inteiro seja coberto
    START_DATE_STR = "2024-10-31 00:00"
    END_DATE_STR = "2024-11-01 23:59"
    
    # --- LÓGICA DO SCRIPT ---
    print("="*50)
    print(f"Iniciando download direto de dados do EMBRACE")
    print(f"Estação: {STATION}")
    print(f"Período: {START_DATE_STR} a {END_DATE_STR}")
    print("="*50)
    
    fetch_scintillation_data_direct(STATION, START_DATE_STR, END_DATE_STR)
    
    print("\n" + "="*50)
    print("Download concluído!")
    print("="*50)