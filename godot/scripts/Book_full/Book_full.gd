# Book_Full.gd
extends Control

# Referências para os nós da cena Book_Full
@onready var test_button = $TestFilterFullButton
@onready var api_request = $APIRequest_FilterFull

func _ready():
	# Conecta os sinais dos nós às nossas funções
	test_button.pressed.connect(_on_test_filter_full_button_pressed)
	api_request.request_completed.connect(_on_request_completed)

# Chamado quando o botão de teste do Full Game é pressionado
func _on_test_filter_full_button_pressed() -> void:
	print("Botão de teste de filtro (Full) pressionado!")
	
	# Para este teste, vamos usar um ano e mês fixos (hardcoded)
	var test_year = 2024
	var test_month = 5 # Maio, mês da supertempestade
	
	# Monta a URL para o endpoint de filtro do Full Game, passando ano e mês
	var url = "http://127.0.0.1:8000/api/data-filter-full?year=%s&month=%s" % [test_year, test_month]
	
	print("Chamando a API de filtro: ", url)
	api_request.request(url)
	test_button.disabled = true

# Chamado quando o backend responde à nossa requisição de filtro
func _on_request_completed(result, response_code, headers, body):
	test_button.disabled = false
	if response_code == 200:
		print("API de filtro (Full) respondeu com sucesso!")
		var json = JSON.new()
		json.parse(body.get_string_from_utf8())
		
		# Apenas imprimimos a resposta para confirmar que a lista de tempestades chegou
		print("Resposta recebida: ", json.get_data())
		
		# Futuramente, aqui você guardaria os dados no GameState
		# e mudaria para a cena que mostra a lista de botões para o jogador.
	else:
		print("Erro na API de filtro (Full). Código: ", response_code)
