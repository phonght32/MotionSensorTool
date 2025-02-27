import os, json

def LoadConfigFile():
	file_content = ''
	file_path = os.getcwd() + '//GUI//Config//DefaultConfig//DefaultConfig_Window.json'

	with open(file_path, 'r') as file:
		file_content = file.read()

	jsonData = json.loads(file_content)

	return jsonData