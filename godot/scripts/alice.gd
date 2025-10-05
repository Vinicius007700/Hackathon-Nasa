extends CharacterBody2D

const SPEED = 100.0
const SPEED_TRATOR = 50.0
var last_direction = "down"
@onready var animation_player = $AnimationPlayer

func _physics_process(delta: float) -> void:
	var direction = Vector2.ZERO

	if Input.is_action_pressed("ui_up"):
		direction = Vector2.UP
		last_direction = "up"
	elif Input.is_action_pressed("ui_down"):
		direction = Vector2.DOWN
		last_direction = "down"
	elif Input.is_action_pressed("ui_left"):
		direction = Vector2.LEFT
		last_direction = "left"
	elif Input.is_action_pressed("ui_right"):
		direction = Vector2.RIGHT
		last_direction = "right"

	if direction != Vector2.ZERO:
		velocity = direction * SPEED
		animation_player.play(last_direction)
	else:
		velocity = Vector2.ZERO
		animation_player.play("idle_" + last_direction)
		
	move_and_slide()

func desativar():
	queue_free() # Esconde o nó do jogador e seus filhos
