# analyze_top_storms.py

import json
from collections import Counter

# O nome do arquivo JSON que você salvou com os dados do GST
GST_CACHE_FILE = 'cache/nasa_gst.json'

def analyze_top_storm_causes_corrected(filename, top_n=100):
    """
    Lê o cache de dados do GST, encontra as N tempestades mais fortes (baseado no pico de Kp)
    e conta a frequência de suas causas associadas (CME, HSS, etc.).
    """
    print(f"Analisando o arquivo: {filename}")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            gst_data = json.load(f)
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{filename}' não encontrado.")
        return

    # 1. Encontrar o pico de Kp para CADA tempestade
    storm_peaks = []
    for storm in gst_data:
        max_kp = 0
        # Encontra o valor máximo de kpIndex dentro de uma tempestade
        for kp_reading in storm.get('allKpIndex', []):
            if kp_reading.get('kpIndex', 0) > max_kp:
                max_kp = kp_reading.get('kpIndex', 0)
        
        # Armazena a tempestade inteira junto com seu pico de Kp
        if 'gstID' in storm and max_kp > 0:
            storm['maxKp'] = max_kp # Adiciona o pico de Kp ao objeto da tempestade
            storm_peaks.append(storm)
            
    # 2. Ordenar as tempestades pelo seu pico de Kp
    storm_peaks.sort(key=lambda x: x['maxKp'], reverse=True)
    
    # 3. Pegar as top N tempestades
    top_n_storms = storm_peaks[:top_n]
    
    print(f"\nAnalisando as causas das {len(top_n_storms)} tempestades mais fortes...")

    # 4. Contar as ocorrências das causas para essas tempestades únicas
    cause_counter = Counter()
    for storm in top_n_storms:
        for event in storm.get('linkedEvents', []):
            activity_id = event.get('activityID', '')
            try:
                event_type = activity_id.split('-')[-2]
                cause_counter[event_type] += 1
            except IndexError:
                continue

    # 5. Apresentar os resultados
    print("\n--- Frequência de Causas Associadas às Tempestades Mais Fortes (Lógica Corrigida) ---")
    if not cause_counter:
        print("Nenhuma causa encontrada para analisar.")
        return
        
    for cause, count in cause_counter.most_common():
        print(f"- {cause}: {count} ocorrências")
    print("--------------------------------------------------------------------------------")


if __name__ == "__main__":
    analyze_top_storm_causes_corrected(GST_CACHE_FILE, top_n=100)