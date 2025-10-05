extends Control

@onready var page_display: TextureRect = $TextureRect/PageDisplay
@onready var anim_player: AnimationPlayer = $AnimationPlayer
@onready var botao_proximo: Button = $BotaoProximo
@onready var som: AudioStreamPlayer2D = $SomLivro

var pages := [
	preload("res://images/book/cena_1.png"),
	preload("res://images/book/cena_2.png"),
	preload("res://images/book/cena_3.png")
]
var current_page := 0
var changing := false

func _ready():
	page_display.texture = pages[current_page]
	botao_proximo.pressed.connect(_on_next_button_pressed)
	anim_player.animation_finished.connect(_on_animation_finished)

func _on_next_button_pressed():
	if changing:
		return
	changing = true
	som.play()
	anim_player.play("fade_page")

func _on_animation_finished(anim_name: String):
	if anim_name != "fade_page":
		return
	
	if changing == true:
		current_page += 1
		if current_page >= pages.size():
			get_tree().change_scene_to_file("res://scenes/games/intro-game/ConexaoSolar.tscn")
			return
		page_display.texture = pages[current_page]
		anim_player.play_backwards("fade_page")
		
	changing = false
