# data_downloader.py (versão final com Selenium)

import requests
import pandas as pd
from datetime import datetime
from io import StringIO
import os
import bz2
import time

# Novas importações para o Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Constantes Globais ---
BASE_URL = "https://embracedata.inpe.br/scintillation/"
CACHE_DIR = "cache/"

# --- Função Principal com Selenium ---

def fetch_scintillation_data(year, month, day, station_code):
    os.makedirs(CACHE_DIR, exist_ok=True)
    target_date = datetime(year, month, day)
    day_of_year = target_date.strftime('%j')
    directory_url = f"{BASE_URL}{year}/{station_code}/{day_of_year}/"
    
    print(f"Acessando diretório com Selenium: {directory_url}")

    # Configuração do Selenium para usar o geckodriver local
    options = FirefoxOptions()
    # options.add_argument("--headless") # Descomente esta linha para rodar sem abrir a janela do navegador
    service = FirefoxService(executable_path='./geckodriver') # Procura o geckodriver na pasta atual
    driver = webdriver.Firefox(service=service, options=options)
    
    all_dataframes = []

    try:
        driver.get(directory_url)
        # Espera ATÉ 15 segundos para que os links que contêm '.dat.bz2' apareçam na página
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, '.dat.bz2'))
        )
        
        # Pega o HTML final, depois que o JavaScript rodou
        html_content = driver.page_source
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        file_links = [a['href'] for a in soup.find_all('a') if a['href'].endswith('.dat.bz2')]

        if not file_links:
            print(f"-> Mesmo com Selenium, nenhum arquivo .dat.bz2 foi encontrado para '{station_code}' em {target_date.date()}.")
            return

        print(f"-> Encontrados {len(file_links)} arquivos. Processando...")

        # O resto do código para baixar e processar é o mesmo, pois já temos os links
        col_names = ['satellite_prn', 's4_index', 'status_flag', 'azimuth', 'elevation','param6', 'param7', 'param8', 'param9', 'param10', 'internal_code']
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'}

        for link in file_links:
            try:
                # O link completo já está no href
                file_url = link
                filename = file_url.split('/')[-1]
                timestamp_str = '_'.join(filename.split('_')[1:]).rsplit('.', 2)[0]
                file_timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d-%H-%M')
                
                file_response = requests.get(file_url, headers=headers)
                file_response.raise_for_status()
                decompressed_data = bz2.decompress(file_response.content)
                data_text = decompressed_data.decode('utf-8')

                if not data_text.strip(): continue

                data_io = StringIO(data_text)
                df = pd.read_csv(data_io, delim_whitespace=True, header=None, names=col_names)
                df['timestamp'] = file_timestamp
                df['station'] = station_code
                all_dataframes.append(df)
            except Exception:
                continue

        if not all_dataframes:
            print(f"-> Nenhum dado válido pôde ser processado.")
            return

        master_df = pd.concat(all_dataframes, ignore_index=True)
        output_filename = f"{CACHE_DIR}embrace_scintillation_{station_code}_{year}-{month:02d}-{day:02d}.csv"
        master_df.to_csv(output_filename, index=False)
        print(f"-> SUCESSO! Dados salvos em: {output_filename}")

    finally:
        # Garante que o navegador seja fechado, mesmo que ocorra um erro
        driver.quit()

# --- PAINEL DE CONTROLE E EXECUÇÃO ---
if __name__ == "__main__":
    STATION = "ceeu"
    START_DATE_STR = "2024-10-31"
    END_DATE_STR = "2024-11-01"
    
    print("="*50)
    print(f"Iniciando download com Selenium")
    print(f"Estação: {STATION} | Período: {START_DATE_STR} a {END_DATE_STR}")
    print("="*50)
    
    date_range = pd.date_range(start=START_DATE_STR, end=END_DATE_STR)
    
    for single_date in date_range:
        print(f"\nBuscando dados para {single_date.date()}...")
        fetch_scintillation_data(single_date.year, single_date.month, single_date.day, station_code=STATION)
        
    print("\n" + "="*50)
    print("Download concluído!")
    print("="*50)