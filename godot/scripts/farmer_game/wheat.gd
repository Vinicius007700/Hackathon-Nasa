extends Area2D

var main_node

func _ready():
	main_node = get_tree().get_root().get_node("FarmerGame")

func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("Trator"):
		if main_node:
			main_node.trigo_foi_coletado()
		queue_free()
