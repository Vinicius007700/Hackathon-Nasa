extends Node2D

#region --- Variáveis do Jogo ---
var contador_de_trigos = 288
var tempo_restante_em_segundos = 60
#endregion

#region --- Referências de Nós da Cena (Onready Vars) ---
# Nós da interface principal do jogo
@onready var contador_label = $HUD/PanelContador/Contador
@onready var cronometro_label = $HUD/PanelTempo/Tempo

# Painéis de controle de estado do jogo
@onready var panel_inicio = $HUD/PanelInicio
@onready var panel_fim = $HUD/PanelFim

# Nós dos personagens e elementos de jogo
@onready var alice = $Alice
@onready var trator = $Trator
@onready var cronometro_timer = $Timer

# --- Nós do Painel de Início (para mostrar a história) ---
# <<<<<--- ATENÇÃO AQUI: Se o erro 'null instance' continuar, o problema está nestas 2 linhas.
# Use o truque de segurar CTRL e arrastar seus nós de texto e imagem para cá para corrigir o caminho.
@onready var texto_historia_label = $HUD/PanelInicio/TextLabel
@onready var imagem_historia_texture = $HUD/PanelInicio/Image
#endregion


# A função _ready() é executada quando a cena inicia.
func _ready():
	panel_fim.hide()
	print("O jogo começou com ", contador_de_trigos, " trigos.")

	# --- LÓGICA FINAL: Exibir dados da API diretamente do GameState ---
	
	# 1. Verifica se os dados do 'farmer' foram carregados no GameState
	if GameState.current_story_data.has("farmer"):
		var dados_fazendeiro = GameState.current_story_data["farmer"]
		
		# 2. Pega as informações de texto e imagem
		var textos_do_fazendeiro = dados_fazendeiro.get("pages", [])
		var caminho_da_imagem = dados_fazendeiro.get("image", "")
		
		# 3. Atualiza o painel de início com as informações
		if not textos_do_fazendeiro.is_empty():
			# Pega o primeiro texto (fazendeiro_ato_1_aviso) e exibe
			texto_historia_label.text = textos_do_fazendeiro[0]
		else:
			texto_historia_label.text = "ERRO: Nenhum texto encontrado no GameState."
			
		if not caminho_da_imagem.is_empty():
			imagem_historia_texture.texture = load(caminho_da_imagem)
			
	else:
		# Mensagem de erro se os dados da API não chegaram nesta cena
		texto_historia_label.text = "ERRO: Dados da história não foram carregados do GameState."


#region --- Lógica do Gameplay ---
func trigo_foi_coletado():
	# Inicia o cronômetro na primeira coleta
	if contador_de_trigos == 288:
		cronometro_timer.timeout.connect(_on_cronometro_timeout)
		cronometro_timer.start()

	atualizar_cronometro_ui()
	
	contador_de_trigos -= 1
	atualizar_contador_ui()
	
	trator.speed += 0.3
	
	if contador_de_trigos <= 0:
		fim_de_jogo(true) # Passa 'true' para indicar vitória

func atualizar_contador_ui():
	contador_label.text = "Wheat: %d/288" % [contador_de_trigos]

func atualizar_cronometro_ui():
	var minutos = tempo_restante_em_segundos / 60
	var segundos = tempo_restante_em_segundos % 60
	cronometro_label.text = "Timer: %02d:%02d" % [minutos, segundos]
#endregion

#region --- Lógica de Estado do Jogo (Início, Fim, Tempo) ---
func _on_cronometro_timeout():
	tempo_restante_em_segundos -= 1
	atualizar_cronometro_ui()
	if tempo_restante_em_segundos <= 0:
		fim_de_jogo(false) # Passa 'false' para indicar derrota por tempo

func fim_de_jogo(venceu: bool):
	cronometro_timer.stop()
	get_tree().paused = true
	
	if venceu:
		cronometro_label.text = "COMPLETED!"
	else:
		cronometro_label.text = "TIME'S OVER!"
		
	panel_fim.show()

# Botão no painel de início para começar a jogar
func _on_button_pressed() -> void:
	panel_inicio.hide()
	alice.set_enable_true()

# Botão no painel de fim de jogo para voltar ao menu
func _on_button_fim_pressed() -> void:
	get_tree().paused = false # Despausar antes de mudar de cena
	get_tree().change_scene_to_file("res://scenes/level_menu.tscn")
#endregion
