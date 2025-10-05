extends Control

@onready var api_request = $ApiRequest

func _ready():
	api_request.request_completed.connect(_on_api_request_completed)

# Funções dos botões que chamam a API
func _on_button_2025_pressed() -> void:
	var ano = 2025
	api_request.request("https://hackathon-nasa.onrender.com/api/generate-story/%s" % ano)

func _on_button_2024_pressed() -> void:
	var ano = 2024
	api_request.request("https://hackathon-nasa.onrender.com/api/generate-story/%s" % ano)

func _on_button_2023_pressed() -> void:
	var ano = 2023
	api_request.request("https://hackathon-nasa.onrender.com/api/generate-story/%s" % ano)

# --- CALLBACK da API ---
# --- CALLBACK da API ---
func _on_api_request_completed(result, response_code, headers, body):
	# 1. Checar se a requisição HTTP deu certo
	if response_code != 200:
		print("Erro na requisição HTTP. Código: ", response_code)
		return

	# 2. Converter o corpo da resposta para String
	var body_string: String = body.get_string_from_utf8()
	print("Corpo da resposta recebido: ", body_string) # Ótimo para debug

	# 3. Parse do JSON (O PONTO CRÍTICO CORRIGIDO)
	var json = JSON.new()
	var error = json.parse(body_string)
	
	# Checagem de erro do parse
	if error != OK:
		print("Erro ao parsear JSON: ", json.get_error_message(), " na linha ", json.get_error_line())
		return

	# Se o parse deu certo, pegamos os dados
	var api_data: Dictionary = json.get_data()
	
	if api_data.is_empty():
		print("JSON parseado com sucesso, mas está vazio.")
		return

	# 4. Acessar os dados e popular o GameState (Seu código aqui já estava bom!)
	# Acessamos a chave "storylines" dentro do JSON principal
	var storylines = api_data.get("storylines", {})
	if storylines.is_empty():
		print("A chave 'storylines' não foi encontrada no JSON.")
		return
		
	# Montar o dicionário para o GameState
	var all_scenes_data: Dictionary = {
		"farmer": {
			"image": "res://images/book/cena_4.png",
			"pages": [
				"Name: Joseph\nLocalization: Arkansas, USA\nAge: 48\nCuriosity: Ex engenheiro de comunicação de satélites\n%s" % storylines["fazendeiro_ato_1_aviso"],
				storylines["fazendeiro_ato_2_impacto"],
				storylines["fazendeiro_ato_3_explicacao"]
			]
		},
		"pescador": {
			"image": "res://images/book/cena_5.png",
			"pages": [
				storylines["pescador_cena_1_calmaria"],
				storylines["pescador_cena_2_perigo"]
			]
		},
		"guia_aurora": {
			"image": "res://images/book/cena_6.png",
			"pages": [
				storylines["guia_aurora_cena_1_previsao"],
				storylines["guia_aurora_cena_2_chegada"],
				storylines["guia_aurora_cena_3_espetaculo"]
			]
		}
	}

	GameState.current_story_data = all_scenes_data
	print("GameState populado com sucesso! Redirecionando...")
	redirect()


func redirect():
	get_tree().change_scene_to_file("res://scenes/cutscene/intial-cutscenes/book1Scene.tscn")
