extends Node2D

var contador_de_trigos = 288

func _ready():
	print("O jogo começou com ", contador_de_trigos, " trigos.")

func trigo_foi_coletado():
	contador_de_trigos -= 1
	print("Trigo coletado diretamente! Restam: ", contador_de_trigos)
	if contador_de_trigos <= 0:
		print("VOCÊ VENCEU!")
