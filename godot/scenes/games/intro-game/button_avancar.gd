extends Button # Ou "extends Button"

# Um sinal diferente para uma ação diferente.
signal advanced_to_next_level

func _on_pressed():
	advanced_to_next_level.emit()
