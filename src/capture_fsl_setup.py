import os
import sys
from tinydb import TinyDB, Query

fsl_settings_path = os.path.expanduser('~').replace('\\', '/') + '/AppData/Roaming/FarmingSimulatorLauncher/fsl_settings.json'

settings_fs22_path = os.path.expanduser('~').replace('\\', '/') + '/AppData/Roaming/FarmingSimulatorLauncher/settings_fs22.json'
settings_fs19_path = os.path.expanduser('~').replace('\\', '/') + '/AppData/Roaming/FarmingSimulatorLauncher/settings_fs19.json'
settings_ls22_path = os.path.expanduser('~').replace('\\', '/') + '/AppData/Roaming/FarmingSimulatorLauncher/settings_ls22.json'
settings_ls19_path = os.path.expanduser('~').replace('\\', '/') + '/AppData/Roaming/FarmingSimulatorLauncher/settings_ls19.json'

games_fs22_path = os.path.expanduser('~').replace('\\', '/') + '/AppData/Roaming/FarmingSimulatorLauncher/games_fs22.json'
games_fs19_path = os.path.expanduser('~').replace('\\', '/') + '/AppData/Roaming/FarmingSimulatorLauncher/games_fs19.json'
games_ls22_path = os.path.expanduser('~').replace('\\', '/') + '/AppData/Roaming/FarmingSimulatorLauncher/games_ls22.json'
games_ls19_path = os.path.expanduser('~').replace('\\', '/') + '/AppData/Roaming/FarmingSimulatorLauncher/games_ls19.json'

output = os.path.expanduser('~').replace('\\', '/') + '/Desktop/fsl_captured.txt'

fsl_settings = 'None'
settings_fs19_json = 'None'
games_fs19_json = 'None'
settings_fs22_json = 'None'
games_fs22_json = 'None'
settings_ls19_json = 'None'
games_ls19_json = 'None'
settings_ls22_json = 'None'
games_ls22_json = 'None'
FS19_folder = ''
FS22_folder = ''

with open(output, 'w') as out:
	if os.path.exists(fsl_settings_path):
		with open(fsl_settings_path, 'r') as f:
			fsl_settings_json = f.read()
			out.write('FSL Settings:\n')
			out.write(fsl_settings_json + '\n')
			out.write('\n-------------------------------------------------------------------------------------------------------------------\n')

	if os.path.exists(settings_fs22_path):
		with open(settings_fs22_path, 'r') as f:
			settings_fs22_json = f.read()
			out.write('FS22 Settings:\n')
			out.write(settings_fs22_json + '\n')
			out.write('\n-------------------------------------------------------------------------------------------------------------------\n')

	if os.path.exists(games_fs22_path):
		with open(games_fs22_path, 'r') as f:
			games_fs22_json = f.read()
			out.write('FS22 Games:\n')
			out.write(games_fs22_json.replace('{"name"', '\n{"name"') + '\n')
			out.write('\n-------------------------------------------------------------------------------------------------------------------\n')

	if os.path.exists(settings_fs19_path):
		with open(settings_fs19_path, 'r') as f:
			settings_fs19_json = f.read()
			out.write('FS19 Settings:\n')
			out.write(settings_fs19_json + '\n')
			out.write('\n-------------------------------------------------------------------------------------------------------------------\n')

	if os.path.exists(games_fs19_path):
		with open(games_fs19_path, 'r') as f:
			games_fs19_json = f.read()
			out.write('FS19 Games:\n')
			out.write(games_fs19_json.replace('{"name"', '\n{"name"') + '\n')
			out.write('\n-------------------------------------------------------------------------------------------------------------------\n')
			
	if os.path.exists(settings_ls22_path):
		with open(settings_ls22_path, 'r') as f:
			settings_ls22_json = f.read()
			out.write('LS22 Settings:\n')
			out.write(settings_ls22_json + '\n')
			out.write('\n-------------------------------------------------------------------------------------------------------------------\n')

	if os.path.exists(games_ls22_path):
		with open(games_ls22_path, 'r') as f:
			games_ls22_json = f.read()
			out.write('LS22 Games:\n')
			out.write(games_ls22_json.replace('{"name"', '\n{"name"') + '\n')
			out.write('\n-------------------------------------------------------------------------------------------------------------------\n')

	if os.path.exists(settings_ls19_path):
		with open(settings_ls19_path, 'r') as f:
			settings_ls19_json = f.read()
			out.write('LS19 Settings:\n')
			out.write(settings_ls19_json + '\n')
			out.write('\n-------------------------------------------------------------------------------------------------------------------\n')

	if os.path.exists(games_ls19_path):
		with open(games_ls19_path, 'r') as f:
			games_ls19_json = f.read()
			out.write('LS19 Games:\n')
			out.write(games_ls19_json.replace('{"name"', '\n{"name"') + '\n')
			out.write('\n-------------------------------------------------------------------------------------------------------------------\n')

	if settings_fs19_json != 'None':
		fs_game_data_19 = os.listdir(TinyDB(settings_fs19_path).all()[0]['fs_game_data_path'])
		all_mods_list_19 = os.listdir(TinyDB(settings_fs19_path).all()[0]['all_mods_path'])
		games = TinyDB(games_fs19_path).all()
		folder_19 = []
		for f in games:
			folder_19.append(f['folder'])
		for f in folder_19:
			try:
				with open(TinyDB(settings_fs19_path).all()[0]['fs_game_data_path'] + os.sep + f + os.sep + 'careerSavegame.xml') as sg:
					c = sg.read()
					out.write(str(f) + '\n')
					out.write(c)
					out.write('\n-------------------------------------------------------------------------------------------------------------------\n')
			except FileNotFoundError:
				out.write(str(f) + ' not found\n')
				out.write('\n-------------------------------------------------------------------------------------------------------------------\n')
	if settings_fs22_json != 'None':
		fs_game_data_22 = os.listdir(TinyDB(settings_fs22_path).all()[0]['fs_game_data_path'])
		all_mods_list_22 = os.listdir(TinyDB(settings_fs22_path).all()[0]['all_mods_path'])
		games = TinyDB(games_fs22_path).all()
		folder_22 = []
		for f in games:
			folder_22.append(f['folder'])
		for f in folder_22:
			try:
				with open(TinyDB(settings_fs22_path).all()[0]['fs_game_data_path'] + os.sep + f + os.sep + 'careerSavegame.xml') as sg:
					c = sg.read()
					out.write(str(f) + '\n')
					out.write(c)
					out.write('\n-------------------------------------------------------------------------------------------------------------------\n')
			except FileNotFoundError:
				out.write(str(f) + ' not found\n')
				out.write('\n-------------------------------------------------------------------------------------------------------------------\n')
	if settings_ls19_json != 'None':
		fs_game_data_19 = os.listdir(TinyDB(settings_ls19_path).all()[0]['fs_game_data_path'])
		all_mods_list_19 = os.listdir(TinyDB(settings_ls19_path).all()[0]['all_mods_path'])
		games = TinyDB(games_ls19_path).all()
		folder_19 = []
		for f in games:
			folder_19.append(f['folder'])
		for f in folder_19:
			try:
				with open(TinyDB(settings_ls19_path).all()[0]['fs_game_data_path'] + os.sep + f + os.sep + 'careerSavegame.xml') as sg:
					c = sg.read()
					out.write(str(f) + '\n')
					out.write(c)
					out.write('\n-------------------------------------------------------------------------------------------------------------------\n')
			except FileNotFoundError:
				out.write(str(f) + ' not found\n')
				out.write('\n-------------------------------------------------------------------------------------------------------------------\n')
	if settings_ls22_json != 'None':
		fs_game_data_22 = os.listdir(TinyDB(settings_ls22_path).all()[0]['fs_game_data_path'])
		all_mods_list_22 = os.listdir(TinyDB(settings_ls22_path).all()[0]['all_mods_path'])
		games = TinyDB(games_ls22_path).all()
		folder_22 = []
		for f in games:
			folder_22.append(f['folder'])
		for f in folder_22:
			try:
				with open(TinyDB(settings_ls22_path).all()[0]['fs_game_data_path'] + os.sep + f + os.sep + 'careerSavegame.xml') as sg:
					c = sg.read()
					out.write(str(f) + '\n')
					out.write(c)
					out.write('\n-------------------------------------------------------------------------------------------------------------------\n')
			except FileNotFoundError:
				out.write(str(f) + ' not found\n')
				out.write('\n-------------------------------------------------------------------------------------------------------------------\n')