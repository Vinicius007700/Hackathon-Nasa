extends Control

@onready var api_request = $ApiRequest

var ano

func _on_button_2025_pressed() -> void:
	ano = 2025
	api_request.request("https://hackathon-nasa.onrender.com/api/select-storm/2025")
	redirect()

func _on_button_2024_pressed() -> void:
	ano = 2024
	api_request.request("https://hackathon-nasa.onrender.com/api/select-storm/2025")
	redirect()

func _on_button_2023_pressed() -> void:
	ano = 2023
	api_request.request("https://hackathon-nasa.onrender.com/api/select-storm/2025")
	redirect()
	
func redirect():
	get_tree().change_scene_to_file("res://scenes/book_cutscene.tscn" )
