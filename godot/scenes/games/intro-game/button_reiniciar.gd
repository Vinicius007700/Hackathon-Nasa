extends Button # Ou "extends Button" se for um botão normal

signal restarted_level

func _on_pressed():
	restarted_level.emit()
