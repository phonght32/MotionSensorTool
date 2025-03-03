import os, json

FILE_CONFIG_WINDOW = os.getcwd() + '//GUI//Config//DefaultConfig//DefaultConfig_Window.json'

def LoadConfigFile(file):
    file_content = ''

    with open(file, 'r') as file:
        file_content = file.read()

    jsonData = json.loads(file_content)

    return jsonData

def SaveConfigFile(file, jsonString):
    with open(file, 'w') as output:
        output.write(jsonString)