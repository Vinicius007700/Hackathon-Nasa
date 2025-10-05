# Nó pai: Control
# Filho: AnimatedSprite2D (sua animação)
extends Control

@onready var anim: AnimatedSprite2D = $AnimatedSprite2D

func _ready():
	# Centraliza o pivô do Control (por exemplo, no centro da animação)
	# Ajuste conforme o tamanho do seu sprite sheet (ex.: 128x64 → metade = (64, 32))
	#pivot_offset = Vector2(64, 32)

	# Define e inicia a animação
	anim.animation = "idle"
	anim.play()
	anim.speed_scale = 1.0  # multiplicador de velocidade
