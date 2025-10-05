extends CharacterBody2D

@onready var trator = $TratorSound

var speed = 80.0
var controlavel = false
var last_direction = "up"

func _physics_process(delta: float) -> void:
	if controlavel == true:
		var direction = Vector2.ZERO

		if Input.is_action_pressed("ui_up"):
			direction = Vector2.UP
			rotation_degrees = 0 # Adicionado: Aponta para cima
		elif Input.is_action_pressed("ui_down"):
			direction = Vector2.DOWN
			rotation_degrees = 180 # Adicionado: Aponta para baixo
		elif Input.is_action_pressed("ui_left"):
			direction = Vector2.LEFT
			rotation_degrees = -90 # Adicionado: Aponta para a esquerda
		elif Input.is_action_pressed("ui_right"):
			direction = Vector2.RIGHT
			rotation_degrees = 90 # Adicionado: Aponta para a direita

		if direction != Vector2.ZERO:
			velocity = direction * speed
		else:
			velocity = Vector2.ZERO
			
		move_and_slide()

func _on_area_do_trator_body_entered(body: Node2D) -> void:
	if body.is_in_group("Alice"):
		body.desativar()
		controlavel = true
		trator.play()
