extends Node

var game_running: bool
var game_over: bool
var score
var scroll
const SCROLL_SPEED : int = 80
var screen_size: Vector2i
var ground_height : int = 80
var logs: Array = []
const PIPE_DELAY : int = 100
const PIPE_RANGE: int = 200
@onready var log_scene = preload("res://scripts/boat-game/log.tscn")

func _ready():
	screen_size = get_window().size

func new_game():
	game_running = false
	game_over = false
	score = 0
	scroll = 0
	logs.clear()
	generate_log()
	$boat.reset()

func start_game():
	game_running = true
	game_over = false
	score = 0
	scroll = 0
	generate_log()
	$LogTimer.start()
	print("Game started!")
	


func _input(event):
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		if not game_running:
			start_game()
		else:
			if $boat.flying:
				$boat.flap()

func _process(delta: float):
	if game_running:
		# Move o fundo e o chão
		$Background.position.x -= SCROLL_SPEED * delta
		# Move os troncos
		for log_obstacle in logs:
			log_obstacle.position.x -= SCROLL_SPEED * delta
		# Remove troncos que saíram da tela
		for log_obstacle in logs.duplicate():
			if log_obstacle.position.x < -200:  # saiu da tela
				log_obstacle.queue_free()
				logs.erase(log_obstacle)
		if $Background.position.x <= -$Background.texture.get_size().x:
			$Background.position.x = 0



func _on_LogTimer_timeout():
	generate_log()

# Substitua sua função antiga por esta
func generate_log():
	print("Gerando um novo tronco!") # Mensagem mais clara que "ERRO 3"
	
	var new_log = log_scene.instantiate() # 1. Variável com nome seguro

	# Posição X (horizontal): Fora da tela, à direita. Perfeito!
	new_log.position.x = screen_size.x + PIPE_DELAY

	var playable_area_height = screen_size.y - ground_height
	var middle_point_y = playable_area_height / 2
	# 3. Definimos a posição do tronco no ponto central, com uma variação aleatória
	new_log.position.y = middle_point_y + randi_range(-PIPE_RANGE, PIPE_RANGE)
	print(new_log.position.y)
	new_log.hit.connect(boat_hit)
	add_child(new_log)
	logs.append(new_log)
	print(len(logs))

func boat_hit():
	game_over = true
	game_running = false
	$LogTimer.stop()
	print("💥 Barco bateu em um tronco!")


func _on_log_timer_timeout() -> void:
	generate_log() # Replace with function body.
