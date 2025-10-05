extends Control

@onready var api_request = $APIRequest
@onready var fast_game_button = $VBoxContainer/FastGameButton
@onready var full_game_button = $VBoxContainer/FullGameButton

func _ready():
	api_request.request_completed.connect(_on_api_request_completed)

# --- FLUXO DO FAST GAME ---
func _on_fast_game_button_pressed() -> void:
	print("Botão 'Fast Game' pressionado. Chamando API...")
	GameState.game_mode = "fast"
	_set_buttons_disabled(true)
	# Chama o endpoint que já escolhe uma história aleatória
	api_request.request("https://hackathon-nasa.onrender.com/api/fast-game")

# --- FLUXO DO FULL GAME ---
func _on_full_game_button_pressed() -> void:
	print("Botão 'Full Game' pressionado. Carregando base de dados completa...")
	GameState.game_mode = "full"
	_set_buttons_disabled(true)
	# Chama o endpoint que retorna TODAS as tempestades para o Godot
	api_request.request("https://hackathon-nasa.onrender.com/api/full-game-data")

# --- FUNÇÃO ÚNICA PARA LIDAR COM A RESPOSTA DA API ---
func _on_api_request_completed(result, response_code, headers, body):
	print("API Respondeu! Preparando para ir para a cena do Livro...")
	_set_buttons_disabled(false)

	if response_code == 200:
		var json = JSON.new()
		json.parse(body.get_string_from_utf8())
		GameState.current_story_data = json.get_data()
		
		# ** IMPORTANTE **
		# Verifique se o caminho abaixo está correto. Use o "Copiar Caminho"
		# do Godot para ter certeza.
		var scene_path = ""
		if GameState.game_mode == "fast":
			scene_path = "res://scenes/book_cutscene.tscn" # Coloque o caminho certo aqui
		else: # if GameState.game_mode == "full"
			scene_path = "res://scenes/book_cutscene.tscn" # Coloque o caminho certo aqui
			
		print("Dados salvos. Transicionando para: ", scene_path)
		get_tree().change_scene_to_file(scene_path)
	else:
		print("Erro ao receber dados da API. Código: ", response_code)

# --- FUNÇÕES AUXILIARES ---
func _on_exit_button_pressed() -> void:
	get_tree().quit()

func _set_buttons_disabled(disabled: bool) -> void:
	fast_game_button.disabled = disabled
	full_game_button.disabled = disabled
