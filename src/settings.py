import os
import platform
import PySimpleGUI as sg
import translation as tr
import import_ls as im

from tinydb import TinyDB, Query

window_size = (800, 350)

fsl_config_path = ''
settings_json = ''
games_json = ''
vers = ''

def init():
	global settings_json
	global fsl_config_path
	global games_json
	global vers

	if platform.system() == 'Darwin':
		fsl_config_path = os.path.expanduser('~') + '/Library/Application Support/FarmingSimulatorLauncher/'
	elif platform.system() == 'Windows':
		fsl_config_path = os.path.expanduser('~').replace('\\', '/') + '/AppData/Roaming/FarmingSimulatorLauncher/'
	else:
		sg.popup_error('Unsuported operating system.')
		return False

	layout = [[sg.Button('LS19', key = '-LS19-', size = (14, 2)), sg.Button('LS22', key = '-LS22-', size = (14, 2))]]

	window = sg.Window('Farming Simulator SaveGames', layout, finalize = True, location = (50, 50))

	while True:
		event, values = window.read()
		#print(event, values)
		if event == sg.WIN_CLOSED:
			break
		elif event == '-LS19-':
			vers = 'ls19'
			settings_json = fsl_config_path + 'settings_ls19.json'
			break
		elif event == '-LS22-':
			vers = 'ls22'
			break
	window.close()

	games_json = fsl_config_path + 'games_' + vers + '.json'
	settings_json = fsl_config_path + 'settings_' + vers + '.json'

	if not os.path.exists(fsl_config_path):
		os.makedirs(fsl_config_path)

def saveSettings(values):
	db = TinyDB(settings_json)
	# TODO check fs_path / fs_game_data_pass exists
	if values['-FS_PATH-'] == '':
		sg.popup_error(tr.getTrans(values['-COMBO-'], 'empty_fs_path'), title = 'miss_path', location = (50, 50))
		return False
	if values['-FS_GAME_DATA_PATH-'] == '':
		sg.popup_error(tr.getTrans(values['-COMBO-'], 'empty_fs_gd_path'), title = 'miss_path', location = (50, 50))
		return False
	if values['-ALL_MODS_PATH-'] == '':
		sg.popup_error(tr.getTrans(values['-COMBO-'], 'empty_all_mods_path'), title = 'miss_path', location = (50, 50))
		return False
	else:
		if 'fsl_all_mods_' + vers in values['-ALL_MODS_PATH-']:
			all_mods_path = values['-ALL_MODS_PATH-']
		else:
			all_mods_path = values['-ALL_MODS_PATH-'] + os.sep + 'fsl_all_mods_' + vers
		try:
			os.makedirs(all_mods_path)
		except FileExistsError:
			pass
	db.update({'language': values['-COMBO-'], 'fs_path': values['-FS_PATH-'], 'fs_game_data_path': values['-FS_GAME_DATA_PATH-'], 'all_mods_path': all_mods_path}, doc_ids = [1])
	return True

def getSettings(key):
	db = TinyDB(settings_json)
	q = Query()
	settings = db.get(doc_id = 1)
	return settings[key]

def checkInit(lang, init):
	if init:
		db = TinyDB(settings_json)
		if platform.system() == 'Windows':
			db.insert({'language': lang, 'fs_path': 'C:/Program Files (x86)', 'fs_game_data_path': os.path.expanduser('~').replace('\\', '/') + '/Documents/My Games', 'all_mods_path': os.path.expanduser('~').replace('\\', '/') + '/Documents/My Games', 'last_sg': '', 'sg_hash': '', 'sgb_hash': '', 'mods_hash': ''})
		elif platform.system() == 'Darwin':
			db.insert({'language': lang, 'fs_path': '/Applications', 'fs_game_data_path': os.path.expanduser('~') + '/Library/Application Support/', 'all_mods_path': os.path.expanduser('~') + '/Library/Application Support/', 'last_sg': '', 'sg_hash': '', 'sgb_hash': '', 'mods_hash': ''})

def guiSettings(lang, init = False):
	io = True
	checkInit(lang, init)
	p = getSettings('fs_path').split(os.sep)
	fs = getSettings('fs_path')
	gd = getSettings('fs_game_data_path')
	am = getSettings('all_mods_path')
	lang = getSettings('language')

	if vers == 'ls19':
		def_fs_text = tr.getTrans('def_fs19')
		def_fs_steam_text = tr.getTrans('def_fs19_steam')
		def_sg_fs_text = tr.getTrans('def_sg_fs19')
	else:
		def_fs_text = tr.getTrans('def_fs22')
		def_fs_steam_text = tr.getTrans('def_fs22_steam')
		def_sg_fs_text = tr.getTrans('def_sg_fs22')

	layout = [	[sg.Text(tr.getTrans('set_lang'), key = '-SET_LANG-'), sg.Combo(values = tr.getLangs(), size = (window_size[0]-10,5), default_value = lang, key = '-COMBO-', enable_events = True)],
				[sg.Text(tr.getTrans('get_fs_path'), key = '-FS_PATH_TEXT-')], 
				[sg.Input(fs, key = '-FS_PATH-', size = (100, 1)), sg.FileBrowse(initial_folder = fs)], 
				[sg.Button(def_fs_text, key = '-DEF_FS-'), sg.Button(def_fs_steam_text, key = '-DEF_FS_STEAM-'), ],
				[sg.Text(tr.getTrans('get_fs_game_data_path'), key = '-FS_GAME_DATA_PATH_TEXT-')], 
				[sg.Input(gd, key = '-FS_GAME_DATA_PATH-', size = (100, 1)), sg.FolderBrowse(initial_folder = gd)],
				[sg.Button(def_sg_fs_text, key = '-DEF_SG_FS-')],
				[sg.Text(tr.getTrans('get_all_mods_path'), key = '-ALL_MODS_PATH_TEXT-')], 
				[sg.Input(am, key = '-ALL_MODS_PATH-', size = (80, 1)), sg.FolderBrowse(initial_folder = am)], #sg.Button(tr.getTrans('import_mods'), key = '-IMPORT-')],
				[	sg.Button(tr.getTrans('save'), key = '-SAVE-'),
					sg.Button(tr.getTrans('exit'), key = '-EXIT-')
				]
			]

	window = sg.Window(tr.getTrans('settings'), layout, size = window_size, finalize = True, location = (50, 50))
#	if init:
#		window['-IMPORT-'].update(disabled = True)
		
	while True:
		event, values = window.read()
		if event == sg.WIN_CLOSED or event=="-EXIT-":
			if init:
				os.remove(settings_json)
				io = False
			break
		elif event == "-SAVE-":
			if saveSettings(values):
				break
		elif event == '-COMBO-':
			window['-SET_LANG-'].update(tr.getTrans('set_lang', values['-COMBO-']))
			window['-FS_PATH_TEXT-'].update(tr.getTrans('get_fs_path', values['-COMBO-']))
			window['-FS_GAME_DATA_PATH_TEXT-'].update(tr.getTrans('get_fs_game_data_path', values['-COMBO-']))
			window['-ALL_MODS_PATH_TEXT-'].update(tr.getTrans('get_all_mods_path', values['-COMBO-']))
			window['-SAVE-'].update(tr.getTrans('save', values['-COMBO-']))
			window['-EXIT-'].update(tr.getTrans('exit', values['-COMBO-']))
			if vers == 'ls19':
				window['-DEF_FS-'].update(tr.getTrans('def_fs19', values['-COMBO-']))
				window['-DEF_SG_FS-'].update(tr.getTrans('def_sg_fs19', values['-COMBO-']))
			else:
				window['-DEF_SG_FS-'].update(tr.getTrans('def_sg_fs22', values['-COMBO-']))
				window['-DEF_FS-'].update(tr.getTrans('def_fs22', values['-COMBO-']))
		elif event == '-IMPORT-':
			window.Hide()
			im.guiImportMods()
			window.UnHide()
		elif event == '-DEF_FS-' and vers == 'ls19':
			if platform.system() == 'Windows':
				window['-FS_PATH-'].update('C:/Program Files (x86)/Farming Simulator 2019/FarmingSimulator2019.exe')
			elif platform.system() == 'Darwin':
				window['-FS_PATH-'].update('/Applications/Farming Simulator 2019.app/Contents/MacOS/FarmingSimulator2019Game')
		elif event == '-DEF_FS-'  and vers == 'ls22':
			if platform.system() == 'Windows':
				window['-FS_PATH-'].update('C:/Program Files (x86)/Farming Simulator 2022/FarmingSimulator2022.exe')
			elif platform.system() == 'Darwin':
				window['-FS_PATH-'].update('/Applications/Farming Simulator 2022.app/Contents/MacOS/FarmingSimulator2022Game')
		elif event == '-DEF_FS_STEAM-' and vers == 'ls19':
			if platform.system() == 'Windows':
				window['-FS_PATH-'].update('') # TODO add path
			elif platform.system() == 'Darwin':
				window['-FS_PATH-'].update(os.path.expanduser('~') + '/Library/Application Support/Steam/SteamApps/common/Farming Simulator 19/Farming Simulator 2019.app/Contents/MacOS/FarmingSimulator2019Game')
		elif event == '-DEF_FS_STEAM-'  and vers == 'ls22':
			if platform.system() == 'Windows':
				window['-FS_PATH-'].update('') # TODO add path
			elif platform.system() == 'Darwin':
				window['-FS_PATH-'].update(os.path.expanduser('~') + '/Library/Application Support/Steam/SteamApps/common/Farming Simulator 19/Farming Simulator 2022.app/Contents/MacOS/FarmingSimulator2022Game')
		elif event == '-DEF_SG_FS-' and vers == 'ls19':
			if platform.system() == 'Windows':
				window['-FS_GAME_DATA_PATH-'].update(os.path.expanduser('~').replace('\\', '/') + '/Documents/My Games/FarmingSimulator2019')
			elif platform.system() == 'Darwin':
				window['-FS_GAME_DATA_PATH-'].update(os.path.expanduser('~') + '/Library/Application Support/FarmingSimulator2019')
		elif event == '-DEF_SG_FS-' and vers == 'ls22':
			if platform.system() == 'Windows':
				window['-FS_GAME_DATA_PATH-'].update(os.path.expanduser('~').replace('\\', '/') + '/Documents/My Games/FarmingSimulator2022')
			elif platform.system() == 'Darwin':
				window['-FS_GAME_DATA_PATH-'].update(os.path.expanduser('~') + '/Library/Application Support/FarmingSimulator2022')
	window.close()
	return io