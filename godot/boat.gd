extends CharacterBody2D

const SPEED_Y := 300   # velocidade vertical
const SPEED_X := 500   # velocidade horizontal constante
const START_POS := Vector2(100, 400)
const MIN_Y := 50
const MAX_Y := 600
var flying: bool = false
func _ready():
	reset()

func reset():
	position = START_POS
	velocity = Vector2.ZERO
	rotation = 0

func _physics_process(delta: float):
 
	# Movimento vertical controlado
	if Input.is_action_pressed("ui_up"):
		velocity.y = -SPEED_Y
	elif Input.is_action_pressed("ui_down"):
		velocity.y = SPEED_Y
	else:
		velocity.y = 0

	move_and_slide()
	if position.y < MIN_Y:
		position.y = MIN_Y
		velocity.y = 0
	elif position.y > MAX_Y:
		position.y = MAX_Y
		velocity.y = 0

	# Rotaciona um pouco para parecer que o barco "inclina" quando sobe/desce
	rotation = lerp_angle(rotation, velocity.y * 0.002, 0.1)
