@tool
extends Node2D

@export var result_panel_path: NodePath 
@export var initial_radius: float = 40.0
@export var final_radius: float = 120.0
@export var pulse_duration: float = 1.0 
@export var ring_color: Color = Color.WHITE
@export var ring_width: float = 5.0

# Certifique-se que estes valores estão corretos no seu Inspetor
@export var target_radius: float = 80.0
@export var win_margin: float = 15.0 

@onready var result_panel: Control = get_node_or_null(result_panel_path)
var tween: Tween
var is_game_active: bool = true

func _ready():
	if result_panel:
		result_panel.visible = false
	start_pulse_animation()

func start_pulse_animation():
	if tween:
		tween.kill()
	tween = create_tween()
	tween.set_loops()
	tween.tween_property(self, "initial_radius", final_radius, pulse_duration).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_SINE)
	tween.tween_property(self, "initial_radius", 40.0, pulse_duration).set_ease(Tween.EASE_IN).set_trans(Tween.TRANS_SINE)

func _input(event: InputEvent):
	# Verificamos apenas o clique, sem a condição is_game_active por agora
	if event is InputEventMouseButton and event.is_pressed():
		
		
		
		if is_game_active:
			print("--- PASSO 2: Jogo está ativo. A processar o clique... ---") # ESPAÇO 2
			if tween:
				tween.kill()
			check_win_condition()
		
			

func check_win_condition():

	
	# Corrigi o bug do rad_min aqui para garantir que o teste é válido
	var difference = abs(40 - initial_radius)
	var did_win = (difference <= win_margin)
	
	show_result(did_win)

func show_result(did_win: bool):
	
	
	if not result_panel:

		return

	result_panel.visible = true
	var message_label_win = result_panel.find_child("MensagemLabelWin", true, false)
	var message_label_lose = result_panel.find_child("MensagemLabelLose", true, false)
	
	if not message_label_win:
	
		return

	if did_win:
		message_label_win.visible = true
		message_label_lose.visible = false
		message_label_win.text = "WIN!"
		message_label_win.modulate = Color.GREEN
		ring_color = Color.GREEN
		get_tree().create_timer(2).timeout
		get_tree().change_scene_to_file("res://scenes/cutscene/post-conection/book-post-conection.tscn")
	else:
		message_label_win.visible = false
		message_label_lose.visible = true
		message_label_lose.text = "TRY AGAIN"
		message_label_lose.modulate = Color.RED
		ring_color = Color.RED
		await get_tree().create_timer(3).timeout
		result_panel.visible = false
		reset()

func _process(delta):
	queue_redraw()
	
func _draw():
	var center: Vector2 = Vector2.ZERO
	draw_arc(center, initial_radius, 0, TAU, 64, ring_color, ring_width, true)

func reset():
	is_game_active = true
	ring_color = Color.WHITE
	self.initial_radius = 40.0
	start_pulse_animation()
