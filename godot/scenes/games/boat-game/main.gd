extends Node

var game_running: bool
var game_over: bool
var score
const SCROLL_SPEED : int = 200
var screen_size: Vector2i
var ground_height : int = 80
var logs: Array = []
var game_time: float = 0.0
const TIME_LIMIT: float = 30.0
const PIPE_DELAY : int = 100
const PIPE_RANGE: int = 200

@onready var log_scene = preload("res://scripts/boat-game/log.tscn")
@onready var time_label = $HUD/PanelTempo/Tempo
@onready var panelinicio_label = $HUD/PanelInicio
@onready var panelfinal_label = $HUD/PanelFim
@onready var mensagemfinalwin_label = $HUD/PanelFim/Mensagem_fim_win
@onready var mensagemfinallose_label = $HUD/PanelFim/Mensagem_fim_lose

func _ready():
	screen_size = get_window().size
	# CORREÇÃO: Chamamos new_game() para configurar a tela inicial corretamente.
	new_game()

func new_game():
	# CORREÇÃO: Remove os nós de tronco antigos da cena antes de limpar o array.
	for log in logs:
		log.queue_free()
	logs.clear()
	
	game_running = false
	game_over = false
	score = 0
	game_time = 0.0
	
	$boat.reset()
	# Conectamos o sinal do barco aqui para garantir a conexão a cada novo jogo.
	$boat.hit.connect(boat_hit)
	
	# Configura a UI para o estado de "menu inicial".
	time_label.text = "Tempo: 0"
	panelinicio_label.show()
	panelfinal_label.hide()

func start_game():
	game_running = true
	game_over = false
	score = 0
	game_time = 0.0
	

	panelinicio_label.hide()
	$LogTimer.start()
	print("Game started!")

# CORREÇÃO: A função de input foi completamente reescrita para lidar com os estados do jogo.
func _input(event):
	generate_log()
	# A função só reage a um clique de mouse.
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		
		# 1. Se o jogo acabou (tela de vitória/derrota)...
		if game_over:
			# ...um clique chama new_game() para reiniciar tudo.
			new_game()
			return # Sai da função para não executar o resto.
			
		# 2. Se o jogo não está rodando (está na tela inicial)...
		if not game_running:
			# ...um clique inicia o jogo.
			start_game()
		# 3. Se o jogo já está rolando...
		else:
			# ...um clique faz o barco pular.
			if $boat.flying:
				$boat.flap()

func _process(delta: float):
	# Se o jogo não está rodando, nada de movimento acontece.
	if not game_running:
		return

	# Move o fundo
	$Background.position.x -= SCROLL_SPEED * delta
	if $Background.position.x <= -$Background.texture.get_size().x:
		$Background.position.x = 0
		
	# Atualiza o tempo e verifica a condição de vitória.
	game_time += delta
	time_label.text = "Tempo: " + str(int(game_time))
	if game_time >= TIME_LIMIT:
		stop_game(true) # O jogador venceu
		return
		
	# Move e remove os troncos.
	for log_obstacle in logs:
		log_obstacle.position.x -= SCROLL_SPEED * delta
	
	for log_obstacle in logs.duplicate():
		if log_obstacle.position.x < -200:
			log_obstacle.queue_free()
			logs.erase(log_obstacle)

# CORREÇÃO: A função foi unificada e não usa mais get_tree().paused.
func stop_game(player_won: bool):
	if game_over:
		return
		
	game_over = true
	game_running = false # Desliga a "chave geral" do movimento.
	$LogTimer.stop()
	
	panelfinal_label.show()
	if player_won:
		print("🏆 Você venceu!")
		mensagemfinalwin_label.show()
		mensagemfinallose_label.hide()
	else:
		print("💥 Barco bateu!")
		mensagemfinallose_label.show()
		mensagemfinalwin_label.hide()

func _on_LogTimer_timeout():
	generate_log()

func generate_log():
	var new_log = log_scene.instantiate()
	new_log.position.x = screen_size.x + PIPE_DELAY
	var playable_area_height = screen_size.y - ground_height
	var middle_point_y = playable_area_height / 2
	new_log.position.y = middle_point_y + randi_range(-PIPE_RANGE, PIPE_RANGE)
	new_log.hit.connect(boat_hit)
	add_child(new_log)
	logs.append(new_log)

func boat_hit():
	stop_game(false)
	
# CORREÇÃO: Removida a função duplicada _on_log_timer_timeout
