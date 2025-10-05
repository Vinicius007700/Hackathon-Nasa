extends Control

@onready var api_request = $ApiRequest

var ano

func _on_button_2025_pressed() -> void:
	ano = 2025
	api_request.request("https://hackathon-nasa.onrender.com/api/select-storm/2025")
	redirect()

func _on_button_2024_pressed() -> void:
	ano = 2024
	api_request.request("https://hackathon-nasa.onrender.com/api/select-storm/2025")
	redirect()

func _on_button_2023_pressed() -> void:
<<<<<<< Updated upstream
	ano = 2023
	api_request.request("https://hackathon-nasa.onrender.com/api/select-storm/2025")
	redirect()
	
func redirect():
	get_tree().change_scene_to_file("res://scenes/book_cutscene.tscn" )
=======
	var ano = 2023
	api_request.request("https://hackathon-nasa.onrender.com/api/generate-story/%s" % ano)

# --- Função de Callback ---
# Esta função SÓ vai rodar QUANDO a API responder.
# O redirecionamento foi movido para cá.
func _on_api_request_completed(result, response_code, headers, body):
	if true:
		print("Requisição para o ano selecionado completa! Redirecionando...")
		# Opcional: você pode querer salvar os dados recebidos aqui também
		# var json = JSON.new()
		# json.parse(body.get_string_from_utf8())
		# GameState.selected_storm_data = json.get_data() # Exemplo
		
		redirect()
	else:
		print("Erro ao receber dados da API. Código: ", response_code)

# A função de redirecionamento permanece a mesma
func redirect():
	get_tree().change_scene_to_file("res://scenes/cutscene/intial-cutscenes/book1Scene.tscn")
>>>>>>> Stashed changes
