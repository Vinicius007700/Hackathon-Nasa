# analyze_top_storms_verbose.py

import json
from collections import Counter

GST_CACHE_FILE = 'cache/nasa_gst.json'

def analyze_top_storm_causes_verbose(filename, top_n=5): # Vamos focar nas top 5 para o dossiê
    """
    Versão verbosa que, além de contar, mostra o "dossiê" de causas para cada
    uma das N tempestades mais fortes.
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
        for kp_reading in storm.get('allKpIndex', []):
            if kp_reading.get('kpIndex', 0) > max_kp:
                max_kp = kp_reading.get('kpIndex', 0)
        
        if 'gstID' in storm and max_kp > 0:
            storm['maxKp'] = max_kp
            storm_peaks.append(storm)
            
    # 2. Ordenar as tempestades e pegar as N mais fortes
    storm_peaks.sort(key=lambda x: x['maxKp'], reverse=True)
    top_n_storms = storm_peaks[:top_n]
    
    print(f"\nAnalisando todas as {len(storm_peaks)} tempestades encontradas no arquivo.")

    # 3. Contar as ocorrências das causas para o total de tempestades
    total_cause_counter = Counter()
    for storm in storm_peaks:
        for event in storm.get('linkedEvents', []):
            try:
                event_type = event.get('activityID', '').split('-')[-2]
                total_cause_counter[event_type] += 1
            except IndexError:
                continue

    # 4. Apresentar o resumo geral
    print("\n--- Frequência de Causas para TODAS as Tempestades ---")
    for cause, count in total_cause_counter.most_common():
        print(f"- {cause}: {count} ocorrências")
    print("--------------------------------------------------")

    # 5. NOVO: Gerar o dossiê detalhado para as top N
    print("\n" + "="*50)
    print(f"DOSSIÊ DETALHADO: As {len(top_n_storms)} Tempestades Mais Fortes")
    print("="*50)
    
    for i, storm in enumerate(top_n_storms, 1):
        print(f"\n{i}. Tempestade: {storm['gstID']} (Pico Kp: {storm['maxKp']})")
        print("   Causas Associadas (linkedEvents):")
        if storm.get('linkedEvents'):
            for event in storm.get('linkedEvents', []):
                print(f"   -> {event.get('activityID')}")
        else:
            print("   -> Nenhuma causa listada.")
            
if __name__ == "__main__":
    analyze_top_storm_causes_verbose(GST_CACHE_FILE, top_n=5)