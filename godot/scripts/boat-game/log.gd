# Exemplo de script para "log.gd"
extends Area2D

# 1. CRIAR O SINAL
# Esta linha cria a "notificação" que o script principal vai ouvir.
signal hit


func _on_body_entered(body):
	if body.is_in_group("Player"):
		get_tree().paused = true
