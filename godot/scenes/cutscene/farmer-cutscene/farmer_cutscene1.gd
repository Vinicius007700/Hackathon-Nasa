extends Control

func load_cutscene(path: String):
	var file = FileAccess.open(path, FileAccess.READ)
	if not file:
		push_error("Não foi possível abrir o JSON da cutscene: " + path)
		return {}
	
	var content = file.get_as_text()
	file.close()

	# Substitui o placeholder pelo texto real do GameState
	var story_text = GameState.current_story_data.get("fazendeiro_ato_1_aviso", "")
	content = content.replace("{{API_TEXT}}", story_text)

	# Sobrescreve o arquivo JSON com o conteúdo atualizado
	var write_file = FileAccess.open(path, FileAccess.WRITE)
	write_file.store_string(content)
	write_file.close()

	# Agora faz o parse normalmente
	var data = JSON.parse_string(content)
	if data == null:
		push_error("Erro ao parsear JSON da cutscene: " + path)
		return {}
	
	return data


func _ready():
	var cutscene_path = "res://scenes/cutscene/farmer-cutscene/farmer.json"
	var cutscene_data = load_cutscene(cutscene_path)
	print("Texto final salvo no JSON:", cutscene_data["pages"][0])
