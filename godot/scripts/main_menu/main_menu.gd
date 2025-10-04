extends Control

func _on_fast_game_button_pressed() -> void:
	get_tree().change_scene_to_file("res://cenarios/oppening_fast.tscn")

func _on_full_game_button_pressed() -> void:
	get_tree().change_scene_to_file("res://cenarios/oppening_full.tscn")

func _on_exit_button_pressed() -> void:
	get_tree().quit()
