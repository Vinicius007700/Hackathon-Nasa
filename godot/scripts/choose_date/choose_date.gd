extends Control

@onready var api_request = $ApiRequest

# Não precisa mais de uma variável 'ano' global se não for usar o dado
# var ano 

# Conecte o sinal assim que a cena estiver pronta
func _ready():
	api_request.request_completed.connect(_on_api_request_completed)

# --- Funções dos Botões ---
# Agora elas apenas iniciam a requisição

func _on_button_2025_pressed() -> void:
	# Dica: use a variável para montar a URL dinamicamente!
	var ano = 2025
	api_request.request("https://hackathon-nasa.onrender.com/api/select-storm/%s" % ano)

func _on_button_2024_pressed() -> void:
	var ano = 2024
	# Você estava chamando a API com '2025' em todos os botões, corrigi isso.
	api_request.request("https://hackathon-nasa.onrender.com/api/select-storm/%s" % ano)

func _on_button_2023_pressed() -> void:
	var ano = 2023
	api_request.request("https://hackathon-nasa.onrender.com/api/select-storm/%s" % ano)

# --- Função de Callback ---
# Esta função SÓ vai rodar QUANDO a API responder.
# O redirecionamento foi movido para cá.
func _on_api_request_completed(result, response_code, headers, body):
	if response_code == 200:
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
	get_tree().change_scene_to_file("res://scenes/book_cutscene.tscn")
