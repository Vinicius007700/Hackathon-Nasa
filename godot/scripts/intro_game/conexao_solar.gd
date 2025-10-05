@tool
extends Node2D

# --- Variáveis de Configuração do Anel ---
@export var initial_radius: float = 40.0
@export var final_radius: float = 120.0
@export var pulse_duration: float = 1.0 
@export var ring_color: Color = Color.GOLD
@export var ring_width: float = 5.0

# --- Variáveis da Lógica do Jogo ---
@export var target_radius: float = 80.0
@export var win_margin: float = 10.0
# Mudamos o nome e o tipo para refletir que agora é um painel
@export var result_panel_path: NodePath 
@onready var painel_resultado = $PainelResultado

# --- Variáveis de Controle ---
@onready var result_panel: Control = get_node_or_null(result_panel_path)
@onready var anel_pulso = $AnelPulso
@onready var mensagem_label = $PainelResultado/MensagemLabel
@onready var botao_avancar = $PainelResultado/ButtonAvancar
@onready var botao_reiniciar = $PainelResultado/ButtonReiniciar

var tween: Tween
var is_game_active: bool = true

func _ready():
	anel_pulso.win.connect(_on_anel_pulso_win())
	anel_pulso.lose(_on_anel_pulso_lose())
	
	
	if result_panel:
		result_panel.visible = false
	start_pulse_animation()
	
func start_level():
	painel_resultado.visible = false

func start_pulse_animation():
	tween = create_tween()
	tween.set_loops()
	
	tween.tween_property(self, "initial_radius", final_radius, pulse_duration) \
		 .set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_SINE)
		 
	tween.tween_property(self, "initial_radius", 40.0, pulse_duration) \
		 .set_ease(Tween.EASE_IN).set_trans(Tween.TRANS_SINE)

func _on_anel_pulso_win():
	painel_resultado.visible = true
	mensagem_label.text = "NEXT LEVEL!"
	mensagem_label.modulate = Color.GREEN
	botao_avancar.visible = true
	botao_reiniciar.visible = false
	
func _on_anel_pulso_lose():
	painel_resultado.visible = true
	mensagem_label.text = "GAME OVER!"
	mensagem_label.modulate = Color.RED
	botao_reiniciar.visible = true
	botao_avancar.visible = false
	
func _on_botao_avancar_pressed():
	if result_panel:
		result_panel.visible = false
	start_level()
		
func _on_botao_reiniciar_pressed():
	if result_panel:
		result_panel.visible = false
	start_level()
	
	
	
		
func restart_game():
	result_panel.visible = false
	anel_pulso.react()
	
func _on_botton_reiniciar_pressed():
	restart_game()
	
func _input(event: InputEvent):
	if is_game_active and event is InputEventMouseButton and event.is_pressed():
		is_game_active = true
		if tween:
			tween.kill()
		check_win_condition()

func check_win_condition():
	var difference = abs(initial_radius - target_radius)
	show_result(difference <= win_margin)

func show_result(did_win: bool):
	if not result_panel:
		print("Painel de resultado não encontrado!")
		return
	
	# 1. Torna o painel inteiro visível
	result_panel.visible = true
	
	# 2. Encontra o nó Label que é FILHO do painel
	#    find_child() procura por um nó filho com aquele tipo.
	var message_label = result_panel.find_child("Label", true, false)
	
	if not message_label:
		print("Nó de Label não encontrado DENTRO do painel!")
		return
		
	# 3. Altera o texto e a cor do Label encontrado
	if did_win:
		message_label.text = "WIN!"
		message_label.modulate = Color.GREEN
		ring_color = Color.GREEN
	else:
		message_label.text = "GAME OVER"
		message_label.modulate = Color.RED
		ring_color = Color.RED

func _process(delta):
	queue_redraw()
	
func _draw():
	var center: Vector2 = Vector2.ZERO
	draw_arc(center, initial_radius, 0, TAU, 64, ring_color, ring_width, true)
