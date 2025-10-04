extends TextureRect

var amplitude = 5
var speed = 2.5
var base_y = 0.0
var time = 0.0

func _ready():
	base_y = position.y

func _process(delta):
	time += delta * speed
	position.y = base_y + sin(time) * amplitude
