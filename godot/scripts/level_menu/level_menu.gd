extends Control

func _on_brazil_pressed() -> void:
	print("Brazil")


func _on_iceland_pressed() -> void:
	print("Iceland")


func _on_eua_pressed() -> void:
	print("USA")
	get_tree().change_scene_to_file("res://scenes/cutscene/farmer-cutscene/farmerCutscene.tscn")
