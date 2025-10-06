extends Control

# Parâmetros exportáveis
@export_multiline var page_text: String = ""     # Texto único da cutscene
@export var image_path: String = ""    # Caminho da imagem
@export var next: String = ""          # Caminho da próxima cena opcional

@onready var image_page = $Panel/Image
@onready var text_page = $Panel2/Text
@onready var next_button = $NextButton
@onready var anim_player = $AnimationPlayer
@onready var som_livro = $SomLivro


func _ready():
	# Carrega imagem se existir
	if image_path != "":
		image_page.texture = load(image_path)
	
	# Exibe o texto único
	update_page()


func update_page():
	play_fade_out()
	som_livro.play()
	text_page.text = page_text


func _on_next_button_pressed() -> void:
	play_fade_in()
	
	if next == "":
		queue_free()
	else:
		get_tree().change_scene_to_file(next)


func play_fade_in():
	anim_player.play("fade_in")


func play_fade_out():
	anim_player.play("fade_out")
