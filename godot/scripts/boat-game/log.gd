# Exemplo de script para "log.gd"
extends Area2D

signal hit

func _on_body_entered(body):
	if body.is_in_group("Player"):
		hit.emit()
