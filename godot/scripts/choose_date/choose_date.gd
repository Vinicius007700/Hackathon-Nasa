extends Control

@onready var api_request = $ApiRequest

var ano

func _on_button_2025_pressed() -> void:
	ano = 2025
	send_to_backend(ano)

func _on_button_2024_pressed() -> void:
	ano = 2024
	send_to_backend(ano)

func _on_button_2023_pressed() -> void:
	ano = 2023
	send_to_backend(ano)

func send_to_backend(ano):
	api_request.request("https://hackathon-nasa.onrender.com/api/data-filter-full/")
	get_tree().change_scene_to_file("res://scenes/cutscene/intial-cutscenes/book1Scene.tscn")
