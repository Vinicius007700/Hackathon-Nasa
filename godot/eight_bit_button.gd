extends TextureButton

@export var label_text: String = "Start"
@onready var label = $Label

func _ready():
	if label:
		label.text = label_text
