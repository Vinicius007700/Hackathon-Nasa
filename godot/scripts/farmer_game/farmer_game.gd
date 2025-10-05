extends Node2D

var contador_de_trigos = 288
var tempo_restante_em_segundos = 60
@onready var contador_label = $HUD/PanelContador/Contador
@onready var cronometro_label = $HUD/PanelTempo/Tempo
@onready var panel_inicio = $HUD/PanelInicio
@onready var panel_fim = $HUD/PanelFim
@onready var alice = $Alice 
@onready var trator = $Trator
@onready var cronometro_timer = $Timer

func _ready():
	panel_fim.hide()
	print("O jogo começou com ", contador_de_trigos, " trigos.")

func trigo_foi_coletado():
	if contador_de_trigos == 288:
		cronometro_timer.timeout.connect(_on_cronometro_timeout)
		cronometro_timer.start()

	atualizar_cronometro_ui()
	
	contador_de_trigos -= 1
	atualizar_contador_ui()
	
	trator.speed += 0.3
	
	print("Trigo coletado diretamente! Restam: ", contador_de_trigos)
	if contador_de_trigos <= 0:
		fim_de_jogo()

func atualizar_contador_ui():
	contador_label.text = "Milhos: %d/288" % [contador_de_trigos]
	
func _on_cronometro_timeout():
	tempo_restante_em_segundos -= 1
	atualizar_cronometro_ui()
	if tempo_restante_em_segundos <= 0:
		fim_de_jogo()

func atualizar_cronometro_ui():
	var minutos = tempo_restante_em_segundos / 60
	var segundos = tempo_restante_em_segundos % 60
	
	var texto_tempo = "Timer: %02d:%02d" % [minutos, segundos]
	cronometro_label.text = texto_tempo

func fim_de_jogo():
	cronometro_timer.stop()
	get_tree().paused = true
	cronometro_label.text = "TIME IS OVER!"
	panel_fim.show()

func _on_button_pressed() -> void:
	panel_inicio.hide()
	alice.set_enable_true()

func _on_button_fim_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/level_menu.tscn")
