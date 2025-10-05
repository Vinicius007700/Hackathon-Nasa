extends Control

@onready var api_request = $APIRequest
@onready var full_game_button = $VBoxContainer/FullGameButton

func _ready():
	api_request.request_completed.connect(_on_api_request_completed)

func _on_full_game_button_pressed() -> void:
	print("Botão 'Full Game' pressionado. Carregando base de dados completa...")
	_set_buttons_disabled(true)
	api_request.request("https://hackathon-nasa.onrender.com/api/full-game-data")

func _on_api_request_completed(result, response_code, headers, body):
	print("API Respondeu! Preparando para ir para a cena do Livro...")
	_set_buttons_disabled(false)

	if response_code == 200:
		var json = JSON.new()
		json.parse(body.get_string_from_utf8())
		GameState.current_story_data = json.get_data()
		
		var scene_path = "res://scenes/choose_date.tscn" 
			
		print("Dados salvos. Transicionando para: ", scene_path)
		get_tree().change_scene_to_file(scene_path)
	else:
		print("Erro ao receber dados da API. Código: ", response_code)

func _on_exit_button_pressed() -> void:
	get_tree().quit()

func _set_buttons_disabled(disabled: bool) -> void:
	full_game_button.disabled = disabled
