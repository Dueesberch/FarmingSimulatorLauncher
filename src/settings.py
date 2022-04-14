import os
import sys
import ctypes
import platform
import PySimpleGUI as sg
import translation as tr
import import_ls as im
import logging as log

from tinydb import TinyDB, Query
from pathlib import Path

fsl_config_path = ''
settings_json = ''
games_json = ''
vers = ''
def_vers = ''
logger = None
fs19_internal_maps = {'Ravenport': 'MapUS', 'Felsbrunn': 'MapEU'}
fs22_internal_maps = {'Elmcreek': 'MapUS', 'Haut-Beyleron': 'MapFR', 'Erlengrat': 'mapAlpine'}
logo = ''

def resource_path(relative_path):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
	return os.path.join(base_path, relative_path)

def init():
	global settings_json
	global fsl_config_path
	global games_json
	global vers
	global def_vers
	global fsl_settings_json
	global logger
	global logo

	ret = True
	logger = log.getLogger('fsl')
	#logger.debug('-------------------------------------------------------------------------')
	if platform.system() == 'Darwin':
		#logger.debug('settings:init:OS Darwin')
		fsl_config_path = os.path.expanduser('~') + '/Library/Application Support/FarmingSimulatorLauncher/'
		#logo = resource_path("logo.icns")
	elif platform.system() == 'Windows':
		#logger.debug('settings:init:OS Windows')
		if not ctypes.windll.shell32.IsUserAnAdmin():
			sg.popup_error('FSL must be run with administrator rights.')
			return False
		fsl_config_path = os.path.expanduser('~').replace('\\', '/') + '/AppData/Roaming/FarmingSimulatorLauncher/'
		logo = resource_path("logo.ico")
	else:
		#logger.debug('settings:init:unsupported OS')
		sg.popup_error('Unsuported operating system.')
		return False

	sg.set_options(icon = logo)
		
	fsl_settings_json = fsl_config_path + 'fsl_settings.json'
	#logger.debug('settings:init:' + fsl_settings_json)

	if os.path.exists(fsl_settings_json):
		def_vers = TinyDB(fsl_settings_json).get(doc_id = 1)['def_vers']
		#logger.debug('settings:init:dev_vers "' + def_vers + '"')
		lang = TinyDB(fsl_settings_json).get(doc_id = 1)['language']
		#logger.debug('settings:init:lang ' + lang)
	else:
		#logger.debug('settings:init:fsl settings json does not exists')
		lang = 'en'

	if def_vers == '':
		layout = [	[sg.Button('LS19', key = '-LS19-', size = (14, 1)), sg.Button('LS22', key = '-LS22-', size = (14, 1))],
					[sg.Checkbox(tr.getTrans('remember', lang), key = '-SET_DEF_LS-')],
					[sg.Button('Exit', key = '-EXIT-', size = (30, 1))],
				]
		window = sg.Window('Version', layout, finalize = True, location = (50, 50), element_justification = 'c')
		#logger.debug('settings:init:version dialog opened')

		while True:
			event, values = window.read()
			#print(event, values)
			if event == sg.WIN_CLOSED:
				break
			elif event == '-LS19-':
				vers = 'fs19'
				if values['-SET_DEF_LS-']:
					def_vers = vers
				break
			elif event == '-LS22-':
				vers = 'fs22'
				if values['-SET_DEF_LS-']:
					def_vers = vers
				break
			elif event == '-EXIT-':
				ret = False
				break
		window.close()
	else:
		#logger.debug('settings:init:set def vers for global use')
		vers = def_vers
	
	#logger.debug('settings:init:vers ' + vers)

	if os.path.exists(fsl_config_path + 'games_ls19.json'):
		os.rename(fsl_config_path + 'games_ls19.json', fsl_config_path + 'games_fs19.json')
	if os.path.exists(fsl_config_path + 'games_ls22.json'):
		os.rename(fsl_config_path + 'games_ls22.json', fsl_config_path + 'games_fs22.json')

	games_json = fsl_config_path + 'games_' + vers + '.json'
	# replace map names for internal maps
	for key, value in fs19_internal_maps.items():
		TinyDB(games_json).update({'map': value}, Query().map == key)
	for key, value in fs22_internal_maps.items():
		TinyDB(games_json).update({'map': value}, Query().map == key)

	#logger.debug('settings:init:games_json ' + games_json)
#	if os.path.exists(games_json):
#		with open(games_json, 'r') as f:
#			logger.debug('setting:init:games_json ' + f.readline())

	if os.path.exists(fsl_config_path + 'settings_ls19.json'):
		os.rename(fsl_config_path + 'settings_ls19.json', fsl_config_path + 'settings_fs19.json')
	if os.path.exists(fsl_config_path + 'settings_ls22.json'):
		os.rename(fsl_config_path + 'settings_ls22.json', fsl_config_path + 'settings_fs22.json')

	settings_json = fsl_config_path + 'settings_' + vers + '.json'
	#logger.debug('settings:init:settings_json ' + settings_json)
#	if os.path.exists(settings_json):
#		with open(settings_json, 'r') as f:
#			logger.debug('setting:init: ' + f.readline())

	if not os.path.exists(fsl_config_path) and ret == True:
		#logger.debug('settings:init:create fsl config folder')
		os.makedirs(fsl_config_path)
	
	return ret

def checkPath(p1, p2):
	p2 = p2.replace('\\', '/').split('/')
	p_temp = ''
	for i, v in enumerate(p2):
		p_temp = p_temp + v + os.sep
		try:
			if os.path.samefile(p_temp, p1) and p2[i + 1] == 'mods':
				return True
		except FileNotFoundError:
			pass
	return False


def saveSettings(values):
	db = TinyDB(settings_json)
	if values['-FS_PATH-'] == '':
		sg.popup_error(tr.getTrans('empty_fs_path', values['-COMBO-']), title = 'miss_path', location = (50, 50))
		return False
	if not os.path.exists(values['-FS_PATH-']):
		sg.popup_error(tr.getTrans('exe_not_found', values['-COMBO-']).format(values['-FS_PATH-']), title = tr.getTrans('miss_path'), line_width = 100, location = (50, 50))
		return False
	if values['-FS_GAME_DATA_PATH-'] == '':
		sg.popup_error(tr.getTrans('empty_fs_gd_path', values['-COMBO-']), title = 'miss_path', location = (50, 50))
		return False
	if not os.path.exists(values['-FS_GAME_DATA_PATH-']):
		sg.popup_error(tr.getTrans('not_found_folder', values['-COMBO-']).format(values['-FS_GAME_DATA_PATH-']), title = tr.getTrans('miss_path'), line_width = 100, location = (50, 50))
		return False
	if values['-ALL_MODS_PATH-'] == '':
		sg.popup_error(tr.getTrans('empty_all_mods_path', values['-COMBO-']), title = 'miss_path', location = (50, 50))
		return False
	elif checkPath(values['-FS_GAME_DATA_PATH-'], values['-ALL_MODS_PATH-']):
		sg.popup_error(tr.getTrans('illegal_path', values['-COMBO-']).format(values['-FS_GAME_DATA_PATH-']), title = 'miss_path', location = (50, 50))
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
	#logger.debug('settings:saveSattings: fs_path: ' + values['-FS_PATH-'] + ' ;fs_game_data_path:' + values['-FS_GAME_DATA_PATH-'] + ' ;all_mods_path:' + all_mods_path + ' ;set_def_vers: ' + str(values['-SET_DEF_LS-']))
	db.update({'fs_path': values['-FS_PATH-'], 'fs_game_data_path': values['-FS_GAME_DATA_PATH-'], 'all_mods_path': all_mods_path}, doc_ids = [1])
	TinyDB(fsl_settings_json).update({'language': values['-COMBO-']}, doc_ids = [1])
	if values['-SET_DEF_LS-']:
		TinyDB(fsl_settings_json).update({'def_vers': vers}, doc_ids = [1])
	else:
		TinyDB(fsl_settings_json).update({'def_vers': ''}, doc_ids = [1])
	return True

def getInternalMaps():
	if vers == 'fs22':
		return fs22_internal_maps
	elif vers == 'fs19':
		return fs19_internal_maps

def getSettings(key):
	db = TinyDB(settings_json)
	q = Query()
	settings = db.get(doc_id = 1)
	return settings[key]
	
def getFslSettings(key):
	db = TinyDB(fsl_settings_json)
	q = Query()
	settings = db.get(doc_id = 1)
	return settings[key]

def checkInit(lang, init):
	if init:
		#logger.debug('settings:checkInit: create default settings')
		db = TinyDB(settings_json)
		if platform.system() == 'Windows':
			db.insert({'fs_path': 'C:/Program Files (x86)', 'fs_game_data_path': os.path.expanduser('~').replace('\\', '/') + '/Documents/My Games', 'all_mods_path': os.path.expanduser('~').replace('\\', '/') + '/Documents/My Games', 'last_sg': '', 'sg_hash': '', 'sgb_hash': '', 'mods_hash': ''})
		elif platform.system() == 'Darwin':
			db.insert({'fs_path': '/Applications', 'fs_game_data_path': os.path.expanduser('~') + '/Library/Application Support/', 'all_mods_path': os.path.expanduser('~') + '/Library/Application Support/', 'last_sg': '', 'sg_hash': '', 'sgb_hash': '', 'mods_hash': ''})
		if not os.path.exists(fsl_settings_json):
			TinyDB(fsl_settings_json).insert({'language': lang, 'def_vers': ''})

def guiSettings(lang, init = False):
	io = True
	checkInit(lang, init)
	p = getSettings('fs_path').split(os.sep)
	fs = getSettings('fs_path')
	gd = getSettings('fs_game_data_path')
	am = getSettings('all_mods_path')
	lang = getFslSettings('language')

	if def_vers != '':
		set_def_check = True
	else:
		set_def_check = False

	if vers == 'fs19':
		def_fs_text = tr.getTrans('def_fs19')
		def_fs_steam_text = tr.getTrans('def_fs19_steam')
		def_sg_fs_text = tr.getTrans('def_sg_fs19')
	else:
		def_fs_text = tr.getTrans('def_fs22')
		def_fs_steam_text = tr.getTrans('def_fs22_steam')
		def_sg_fs_text = tr.getTrans('def_sg_fs22')

	layout = [	[sg.Text(tr.getTrans('set_lang'), key = '-SET_LANG-')],
				[sg.Combo(values = tr.getLangs(), size = (98,5), default_value = lang, key = '-COMBO-', enable_events = True)],
				[sg.Checkbox(tr.getTrans('remember'), key = '-SET_DEF_LS-', default = set_def_check)],
				[sg.Text(tr.getTrans('get_fs_path'), key = '-FS_PATH_TEXT-')], 
				[sg.Input(fs, key = '-FS_PATH-', size = (100, 1))], 
				[sg.FileBrowse(initial_folder = fs, target = '-FS_PATH-'), sg.Button(def_fs_text, key = '-DEF_FS-', size = (30,1)), sg.Button(def_fs_steam_text, key = '-DEF_FS_STEAM-', size = (30,1)), ],
				[sg.Text(tr.getTrans('get_fs_game_data_path'), key = '-FS_GAME_DATA_PATH_TEXT-')], 
				[sg.Input(gd, key = '-FS_GAME_DATA_PATH-', size = (100, 1))],
				[sg.FolderBrowse(initial_folder = gd, target = '-FS_GAME_DATA_PATH-'), sg.Button(def_sg_fs_text, key = '-DEF_SG_FS-', size = (30,1))],
				[sg.Text(tr.getTrans('get_all_mods_path'), key = '-ALL_MODS_PATH_TEXT-')], 
				[sg.Input(am, key = '-ALL_MODS_PATH-', size = (100, 1))],
				[sg.FolderBrowse(initial_folder = am, target = '-ALL_MODS_PATH-')],
				[	sg.Button(tr.getTrans('save'), key = '-SAVE-', size = (14, 1)),
					sg.Button(tr.getTrans('exit'), key = '-EXIT-', size = (14, 1))
				]
			]

	window = sg.Window(tr.getTrans('settings'), layout, finalize = True, location = (50, 50))
		
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
			window['-SET_DEF_LS-'].update(text = tr.getTrans('remember', values['-COMBO-']))
			if vers == 'fs19':
				window['-DEF_FS-'].update(tr.getTrans('def_fs19', values['-COMBO-']))
				window['-DEF_SG_FS-'].update(tr.getTrans('def_sg_fs19', values['-COMBO-']))
			else:
				window['-DEF_SG_FS-'].update(tr.getTrans('def_sg_fs22', values['-COMBO-']))
				window['-DEF_FS-'].update(tr.getTrans('def_fs22', values['-COMBO-']))
		elif event == '-IMPORT-':
			window.Hide()
			im.guiImportMods()
			window.UnHide()
		elif event == '-DEF_FS-' and vers == 'fs19':
			if platform.system() == 'Windows':
				window['-FS_PATH-'].update('C:/Program Files (x86)/Farming Simulator 2019/FarmingSimulator2019.exe')
			elif platform.system() == 'Darwin':
				window['-FS_PATH-'].update('/Applications/Farming Simulator 2019.app/Contents/MacOS/FarmingSimulator2019Game')
		elif event == '-DEF_FS-'  and vers == 'fs22':
			if platform.system() == 'Windows':
				window['-FS_PATH-'].update('C:/Program Files (x86)/Farming Simulator 2022/FarmingSimulator2022.exe')
			elif platform.system() == 'Darwin':
				window['-FS_PATH-'].update('/Applications/Farming Simulator 2022.app/Contents/MacOS/FarmingSimulator2022Game')
		elif event == '-DEF_FS_STEAM-' and vers == 'fs19':
			if platform.system() == 'Windows':
				window['-FS_PATH-'].update('C:/Program Files (x86)/Steam/SteamApps/Common/Farming Simulator 19/FarmingSimulator2019.exe')
			elif platform.system() == 'Darwin':
				window['-FS_PATH-'].update(os.path.expanduser('~') + '/Library/Application Support/Steam/SteamApps/common/Farming Simulator 19/Farming Simulator 2019.app/Contents/MacOS/FarmingSimulator2019Game')
		elif event == '-DEF_FS_STEAM-'  and vers == 'fs22':
			if platform.system() == 'Windows':
				window['-FS_PATH-'].update('C:/Program Files (x86)/Steam/SteamApps/Common/Farming Simulator 22/Farmingsimulator2022.exe')
			elif platform.system() == 'Darwin':
				window['-FS_PATH-'].update(os.path.expanduser('~') + '/Library/Application Support/Steam/SteamApps/common/Farming Simulator 19/Farming Simulator 2022.app/Contents/MacOS/FarmingSimulator2022Game')
		elif event == '-DEF_SG_FS-' and vers == 'fs19':
			if platform.system() == 'Windows':
				window['-FS_GAME_DATA_PATH-'].update(os.path.expanduser('~').replace('\\', '/') + '/Documents/My Games/FarmingSimulator2019')
			elif platform.system() == 'Darwin':
				window['-FS_GAME_DATA_PATH-'].update(os.path.expanduser('~') + '/Library/Application Support/FarmingSimulator2019')
		elif event == '-DEF_SG_FS-' and vers == 'fs22':
			if platform.system() == 'Windows':
				window['-FS_GAME_DATA_PATH-'].update(os.path.expanduser('~').replace('\\', '/') + '/Documents/My Games/FarmingSimulator2022')
			elif platform.system() == 'Darwin':
				window['-FS_GAME_DATA_PATH-'].update(os.path.expanduser('~') + '/Library/Application Support/FarmingSimulator2022')
	window.close()
	return io