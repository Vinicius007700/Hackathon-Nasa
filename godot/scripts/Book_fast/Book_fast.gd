# Book_Fast.gd
extends Control

# Referências para os nós que acabamos de configurar
@onready var test_button = $TestFilterButton
@onready var api_request = $APIRequest_Filter

func _ready():
	# Conecta os sinais dos nós às nossas funções
	test_button.pressed.connect(_on_test_filter_button_pressed)
	api_request.request_completed.connect(_on_request_completed)

# Chamado quando o nosso novo botão de teste é pressionado
func _on_test_filter_button_pressed():
	print("Botão de teste de filtro pressionado!")
	
	# Para este teste, vamos usar uma data fixa (hardcoded)
	var test_date = "2024-05-10"
	
	# Monta a URL para o endpoint de filtro do Fast Game
	var url = "http://127.0.0.1:8000/api/data-filter-fast?date_str=%s" % test_date
	
	print("Chamando a API de filtro: ", url)
	api_request.request(url)
	test_button.disabled = true

# Chamado quando o backend responde à nossa requisição de filtro
func _on_request_completed(result, response_code, headers, body):
	test_button.disabled = false
	if response_code == 200:
		print("API de filtro respondeu com sucesso!")
		var json = JSON.new()
		json.parse(body.get_string_from_utf8())
		
		# Por enquanto, apenas imprimimos a resposta para confirmar
		print("Resposta recebida: ", json.get_data())
		
		# AQUI, no futuro, você guardaria os dados no GameState
		# e mudaria para a cena de jogo principal.
	else:
		print("Erro na API de filtro. Código: ", response_code)
