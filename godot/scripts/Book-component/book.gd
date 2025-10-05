extends Control

@export var data_path: String
@export var next: String = ""

@onready var image_page = $Panel/Image
@onready var text_page = $Panel2/Text
@onready var next_button = $NextButton
@onready var anim_player = $AnimationPlayer

var current_page := 0
var pages := []
var image_path := ""

func _ready():
	load_data()
	update_page()
	
func load_data():
	var file = FileAccess.open(data_path, FileAccess.READ)
	var json = JSON.parse_string(file.get_as_text())
	image_path = json["image"]
	pages = json["pages"]
	image_page.texture = load(image_path)

func update_page():
	play_fade_out()
	text_page.text = pages[current_page]

func _on_next_button_pressed() -> void:
	current_page += 1
	play_fade_in()
	if current_page < pages.size():
		update_page()
	else:
		if next == "":
			queue_free()
		else:
			get_tree().change_scene_to_file(next)

func play_fade_in():
	anim_player.play("fade_in")

func play_fade_out():
	anim_player.play("fade_out")
