extends Control

@onready var icelandButton = $Iceland

var brazil_visited = false
var usa_visited = false
var iceland_disabled = true

func _ready():
	update_iceland()
	
func update_iceland():
	print("Update iceland")
	if (!brazil_visited or !usa_visited):
		print("iceland desativada")
		icelandButton.disabled = true
		return
	icelandButton.disabled = false
		
func _on_brazil_pressed() -> void:
	print("Brazil")
	brazil_visited = true
	update_iceland()


func _on_iceland_pressed() -> void:
	if (!brazil_visited or !usa_visited):
		print("Can't visit yet. Visite the other places before!")
		return
	print("Iceland")


func _on_eua_pressed() -> void:
	print("USA")
	usa_visited = true
	update_iceland()
	#get_tree().change_scene_to_file("res://scenes/cutscene/farmer-cutscene/farmerCutscene.tscn")
	get_tree().change_scene_to_file("res://scenes/cutscene/farmer-cutscene/farmerCutscene.tscn")
