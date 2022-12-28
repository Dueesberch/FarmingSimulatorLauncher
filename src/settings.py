import os
import sys
import ctypes
import platform
import PySimpleGUI as sg
import translation as tr
import import_ls as im
import logging as log
import zipfile
import xml.etree.ElementTree as ET
import hashlib
import pathlib
import shutil
import re
from PIL import Image
from tinydb import TinyDB, Query
from BetterJSONStorage import BetterJSONStorage
from pathlib import Path
import traceback
import json
import blosc2

fsl_config_path = ''
settings_json = ''
games_json = ''
vers = ''
def_vers = ''
logger = None
fs19_internal_maps = {'Ravenport': 'MapUS', 'Felsbrunn': 'MapEU'}
fs22_internal_maps = {'Elmcreek': 'MapUS', 'Haut-Beyleron': 'MapFR', 'Erlengrat': 'mapAlpine'}
logo = ''
langs = ['', 'en', 'de', 'fr', 'ru']


def resource_path(relative_path):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
	return os.path.join(base_path, relative_path)

def getLangs():
	return langs

def init():
	global settings_json
	global fsl_config_path
	global games_json
	global vers
	global def_vers
	global fsl_settings_json
	global logger
	global logo

	if platform.system() == 'Darwin':
		fsl_config_path = os.path.expanduser('~') + '/Library/Application Support/FarmingSimulatorLauncher/'
	elif platform.system() == 'Windows':
		if not ctypes.windll.shell32.IsUserAnAdmin():
			sg.popup_error('FSL must be run with administrator rights.')
			return False
		fsl_config_path = os.path.expanduser('~').replace('\\', '/') + '/AppData/Roaming/FarmingSimulatorLauncher/'
		logo = resource_path("logo.ico")
	else:
		sg.popup_error('Unsupported operating system.')
		return False

	sg.set_options(icon = logo)
		
	fsl_settings_json = fsl_config_path + 'fsl_settings.json'

	if os.path.exists(fsl_settings_json):
		with TinyDB(pathlib.Path(fsl_settings_json), storage=BetterJSONStorage) as db_fsl_settings:
			def_vers = db_fsl_settings.get(doc_id = 1)['def_vers']
			lang = db_fsl_settings.get(doc_id = 1)['language']
	else:
		lang = 'en'

	if def_vers == '':
		layout = [	[sg.Button('FS19', key = '-FS19-', size = (14, 1)), sg.Button('FS22', key = '-FS22-', size = (14, 1))],
					[sg.Checkbox(tr.getTrans('remember', lang), key = '-SET_DEF_FS-')],
					[sg.Button('Exit', key = '-EXIT-', size = (30, 1))],
				]
		window = sg.Window('Version', layout, finalize = True, location = (50, 50), element_justification = 'c')

		while True:
			event, values = window.read()
			#print(event, values)
			if event == sg.WIN_CLOSED:
				break
			elif event == '-FS19-':
				vers = 'fs19'
				if values['-SET_DEF_FS-']:
					def_vers = vers
				break
			elif event == '-FS22-':
				vers = 'fs22'
				if values['-SET_DEF_FS-']:
					def_vers = vers
				break
			elif event == '-EXIT-':
				break
		window.close()
	else:
		vers = def_vers

	if not os.path.exists(fsl_config_path):
		os.makedirs(fsl_config_path)
		settings_json = fsl_config_path + 'settings_' + vers + '.json'
		games_json = fsl_config_path + 'games_' + vers + '.json'
		return True

	settings_json = fsl_config_path + 'settings_' + vers + '.json'
	games_json = fsl_config_path + 'games_' + vers + '.json'

	# add keys mode, direct_start to game_json
	
	# add key intro to settings
	
	# replace map names for internal maps
	#if vers == 'fs19':
	#	for key, value in fs19_internal_maps.items():
	#		games_json_obj.update({'map': value}, Query()['map'] == key)
	#if vers == 'fs22':
	#	for key, value in fs22_internal_maps.items():
	#		games_json_obj.update({'map': value}, Query()['map'] == key)

	if os.path.exists(settings_json):
		all_mods_path = getSettings('all_mods_path')
		if (os.path.exists(all_mods_path) and not os.path.exists(all_mods_path + os.sep + 'mods_db.json')) or (os.path.exists(all_mods_path) and os.stat(all_mods_path + os.sep + 'mods_db.json').st_size == 0):
			w = sg.Window('', no_titlebar = True, layout = [[sg.Text('Create mods database. Please wait')]], finalize = True, location = (50, 50))
			for f in os.listdir(all_mods_path):
				try:
					if not f.startswith('fsl_'):
						continue
					elif f.endswith('.zip'):
						f_hash = hashlib.md5(pathlib.Path(all_mods_path + os.sep + f).read_bytes()).hexdigest()
						with TinyDB(pathlib.Path(all_mods_path + os.sep + 'mods_db.json'), access_mode = "r+", storage = BetterJSONStorage) as db_mods:
							with zipfile.ZipFile(all_mods_path + os.sep + f) as z:
								moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8').strip())
								if moddesc.find('title/' + lang) != None:
									name = moddesc.find('title/' + lang)
									mod_lang = lang
								elif moddesc.find('title/en') != None:
									name = moddesc.find('title/en')
									mod_lang = 'en'
								elif moddesc.find('title') != None:
									name = moddesc.find('title')[0]
									mod_lang = moddesc.find('title')[0].tag
								if name != None:
									img_name = hashlib.md5(f.split('!')[1].split('.zip')[0].encode()).hexdigest()
								d = db_mods.get(Query().name == name.text)
								if moddesc.find('maps/map/title/en') != None:
									mod_type = 'map'
								else:
									mod_type = 'mod'
								dependencies = []
								if moddesc.find('dependencies') != None:
									for i in moddesc.find('dependencies'):
										dependencies.append(i.text)
								if d == None:
									db_mods.insert({'name': name.text, 'mod_type': mod_type, 'lang': mod_lang, 'img': img_name, 'files': {f: [f_hash, dependencies]}})
								else:
									d['files'][f] = [f_hash, dependencies]
									db_mods.update({'files': d['files']}, doc_ids = [d.doc_id])
							if not os.path.exists(all_mods_path + os.sep + 'images' + os.sep + img_name + '.png'):
								try:
									icon = moddesc.find('iconFilename').text
									try:
										z.extract(icon, all_mods_path + os.sep + 'images' + os.sep + 'tmp')
									except KeyError:
										if '.png' in icon:
											icon = icon.replace('.png', '.dds')
											z.extract(icon, all_mods_path + os.sep + 'images' + os.sep + 'tmp')
											pass
									im = Image.open(all_mods_path + os.sep + 'images' + os.sep + 'tmp' + os.sep + icon)
									size = 256, 256
									im.thumbnail(size, Image.ANTIALIAS)
									im.save(all_mods_path + os.sep + 'images' + os.sep + img_name + '.png')
								except Exception:
									pass
							if os.path.exists(all_mods_path + os.sep + 'images' + os.sep + 'tmp'):
								shutil.rmtree(all_mods_path + os.sep + 'images' + os.sep + 'tmp')
				except Exception:
					sg.popup_error('Problem with mod \"{}\" \n\n{}'.format(f, traceback.format_exc(), title = 'Error', location = (50, 50)))
			w.close()

		# remove links from mods folder
		if os.path.exists(getSettings('fs_game_data_path') + os.sep + 'mods'):
			p = getSettings('fs_game_data_path') + os.sep + 'mods'
			for i in os.listdir(p):
				if Path(p + os.sep + i).is_symlink():
					os.remove(p + os.sep + i)

	if not os.path.exists(fsl_config_path):
		os.makedirs(fsl_config_path)

	return True

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
		except IndexError:
			pass
	return False

def saveSettings(values, rebuild_mod_db):
	if values['-N_KEEP-'] == '':
		values['-N_KEEP-'] = '0'
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
	if not os.path.exists(values['-FS_GAME_DATA_PATH-'] + os.sep + 'game.xml'):
		sg.popup_error(tr.getTrans('invalid_path', values['-COMBO-']).format(values['-FS_GAME_DATA_PATH-']), title = tr.getTrans('miss_path'), line_width = 100, location = (50, 50))
		return False
	if values['-ALL_MODS_PATH-'] == '':
		sg.popup_error(tr.getTrans('empty_all_mods_path', values['-COMBO-']), title = 'miss_path', location = (50, 50))
		return False
	elif checkPath(values['-FS_GAME_DATA_PATH-'], values['-ALL_MODS_PATH-']):
		sg.popup_error(tr.getTrans('illegal_path', values['-COMBO-']).format(values['-FS_GAME_DATA_PATH-']), title = 'miss_path', location = (50, 50))
		return False
	elif not values['-N_KEEP-'].isnumeric():
		sg.popup_error(tr.getTrans('numeric'), title = tr.getTrans('error'), location = (50, 50))
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
	
	with TinyDB(pathlib.Path(fsl_settings_json), access_mode = "r+", storage = BetterJSONStorage) as db_fsl_settings:
		db_fsl_settings.update({'language': values['-COMBO-']}, doc_ids = [1])
		if values['-SET_DEF_FS-']:
			db_fsl_settings.update({'def_vers': vers}, doc_ids = [1])
		else:
			db_fsl_settings.update({'def_vers': ''}, doc_ids = [1])

	with TinyDB(pathlib.Path(settings_json), access_mode = "r+", storage = BetterJSONStorage) as db_settings:
		db_settings.update({'fs_path': values['-FS_PATH-'], 'fs_game_data_path': values['-FS_GAME_DATA_PATH-'], 'all_mods_path': all_mods_path, 'backups': int(values['-N_KEEP-'])}, doc_ids = [1])
		if values['-SKIP-']:
			db_settings.update({'intro': 'skip'}, doc_ids = [1])
		else:
			db_settings.update({'intro': 'run'}, doc_ids = [1])

	if rebuild_mod_db:
		try:
			os.remove(all_mods_path + '/mods_db.json')
			init()
		except FileNotFoundError:
			pass
	return True

def getInternalMaps():
	if vers == 'fs22':
		return fs22_internal_maps
	elif vers == 'fs19':
		return fs19_internal_maps

def updateSettings(settings_list):
	with TinyDB(pathlib.Path(settings_json), access_mode = "r+", storage = BetterJSONStorage) as db:
		db.update(settings_list, doc_ids = [1])

def getSettings(key):
	with TinyDB(pathlib.Path(settings_json), storage = BetterJSONStorage) as db_settings:
		settings = db_settings.get(doc_id = 1)[key]
	return settings

def updateFSLSettings(fsl_settings_list):
	with TinyDB(pathlib.Path(fsl_settings_json), access_mode = "r+", storage = BetterJSONStorage) as db_fsl_settings:
		db_fsl_settings.update(fsl_settings_list, doc_ids = [1])

def getFslSettings(key):
	with TinyDB(pathlib.Path(fsl_settings_json), storage = BetterJSONStorage) as db_fsl_settings:
		fsl_setting = db_fsl_settings.get(doc_id = 1)[key]
	return fsl_setting

def checkInit(lang, init):
	if init:
		with TinyDB(pathlib.Path(settings_json), access_mode = "r+", storage = BetterJSONStorage) as db_settings:
			if platform.system() == 'Windows':
				db_settings.insert({'fs_path': 'C:/Program Files (x86)', 'fs_game_data_path': os.path.expanduser('~').replace('\\', '/') + '/Documents/My Games', 'all_mods_path': os.path.expanduser('~').replace('\\', '/') + '/Documents/My Games', 'last_sg': '', 'sg_hash': '', 'sgb_hash': '', 'mods_hash': '', 'intro': 'run', 'backups': 10})
			elif platform.system() == 'Darwin':
				db_settings.insert({'fs_path': '/Applications', 'fs_game_data_path': os.path.expanduser('~') + '/Library/Application Support/', 'all_mods_path': os.path.expanduser('~') + '/Library/Application Support/', 'last_sg': '', 'sg_hash': '', 'sgb_hash': '', 'mods_hash': '', 'intro': 'run', 'backups': 10})
		if not os.path.exists(fsl_settings_json):
			with TinyDB(pathlib.Path(fsl_settings_json), access_mode = "r+", storage=BetterJSONStorage) as db_fsl_settings:
				db_fsl_settings.insert({'language': lang, 'def_vers': ''})

def def_check():
	checks = {'remember': False, 'skip_intro': False}
	if def_vers != '':
		checks['remember'] = True
	with TinyDB(pathlib.Path(settings_json), storage = BetterJSONStorage) as db_settings:
		if db_settings.get(doc_id = 1)['intro'] == 'skip':
			checks['skip_intro'] = True
	return checks

def resetFSL():
	if sg.popup_yes_no(tr.getTrans('reset_popup'), title = 'Reset', location = (50, 50)) == 'Yes':
		sg.popup_ok(tr.getTrans('reset_thanks'), title = '', location =(50, 50))
		all_mods_path = getSettings('all_mods_path')

		# move mods - keep latest version
		mods_folder = getSettings('fs_game_data_path') + os.sep + 'mods'
		os.mkdir(mods_folder)

		with TinyDB(pathlib.Path(all_mods_path + os.sep + 'mods_db.json'), storage = BetterJSONStorage) as db_mods:
			for mod in db_mods.all():
				latest = sorted(mod['files'].keys())[-1]
				shutil.move(all_mods_path + os.sep + latest, mods_folder + os.sep + latest.split('!')[1])
		shutil.rmtree(all_mods_path)
		
		# move savegames if not empty
		c = 1
		sgb_folder = getSettings('fs_game_data_path') + os.sep + 'savegameBackups'
		os.mkdir(sgb_folder)
		with TinyDB(pathlib.Path(games_json), storage = BetterJSONStorage) as db_games:
			for sga in db_games.all():
				if len(os.listdir(getSettings('fs_game_data_path') + os.sep + sga['folder'])) != 0:
					while os.path.exists(getSettings('fs_game_data_path') + os.sep + 'savegame' + str(c)):
						c = c + 1
					os.rename(getSettings('fs_game_data_path') + os.sep + sga['folder'], getSettings('fs_game_data_path') + os.sep + 'savegame' + str(c))
					b_folder = getSettings('fs_game_data_path') + os.sep + sga['folder'] + '_Backup'
					for b in os.listdir(b_folder):
						shutil.move(b_folder + os.sep + b, sgb_folder + os.sep + b.replace('savegame1', 'savegame' + str(c)))
					shutil.rmtree(b_folder)
					c = c + 1
		# rm FSL settings for current fs version
		os.remove(fsl_config_path + os.sep + 'games_' + vers + '.json')
		os.remove(fsl_config_path + os.sep + 'settings_' + vers + '.json')

		sys.exit()

def exportRawJson():
	json_pathes = [getSettings('all_mods_path') + '/mods_db.json', settings_json, fsl_settings_json, games_json]
	for json_path in json_pathes:
		json_name = json_path.split('/')[-1]
		with open(json_path, 'rb') as json_file_in:
			if not os.path.exists(os.path.expanduser('~').replace('\\', '/') + '/Desktop/fsl_raw_json'):
				os.mkdir(os.path.expanduser('~').replace('\\', '/') + '/Desktop/fsl_raw_json')
			with open(os.path.expanduser('~').replace('\\', '/') + '/Desktop/fsl_raw_json/' + json_name, "w") as json_file_out:
				data = json.loads(blosc2.decompress2(json_file_in.read()).decode())['_default']
				json.dump(data, json_file_out)


def guiSettings(lang, init = False):
	io = True
	checkInit(lang, init)
	p = getSettings('fs_path').split(os.sep)
	fs = getSettings('fs_path')
	gd = getSettings('fs_game_data_path')
	am = getSettings('all_mods_path')
	lang = getFslSettings('language')
	backups = getSettings('backups')

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
				[sg.Checkbox(tr.getTrans('remember'), key = '-SET_DEF_FS-', default = def_check()['remember']), sg.Input(backups, key = '-N_KEEP-', size = (5,1)), sg.Text(tr.getTrans('to_keep'), key = '-KEEP-')],
				[sg.Checkbox(tr.getTrans('skip_intro'), key = '-SKIP-', default = def_check()['skip_intro'])],
				[sg.Text(tr.getTrans('get_fs_path'), key = '-FS_PATH_TEXT-')], 
				[sg.Input(fs, key = '-FS_PATH-', size = (100, 1))], 
				[sg.FileBrowse(initial_folder = fs, target = '-FS_PATH-'), sg.Button(def_fs_text, key = '-DEF_FS-', size = (30,1)), sg.Button(def_fs_steam_text, key = '-DEF_FS_STEAM-', size = (30,1)), ],
				[sg.Text(tr.getTrans('get_fs_game_data_path'), key = '-FS_GAME_DATA_PATH_TEXT-')], 
				[sg.Input(gd, key = '-FS_GAME_DATA_PATH-', size = (100, 1))],
				[sg.FolderBrowse(initial_folder = gd, target = '-FS_GAME_DATA_PATH-'), sg.Button(def_sg_fs_text, key = '-DEF_SG_FS-', size = (30,1))],
				[sg.Text(tr.getTrans('get_all_mods_path'), key = '-ALL_MODS_PATH_TEXT-')], 
				[sg.Input(am, key = '-ALL_MODS_PATH-', size = (100, 1))],
				[sg.FolderBrowse(initial_folder = am, target = '-ALL_MODS_PATH-')],
				[sg.Button(tr.getTrans('reset_default'), key = '-RESET-', size = (50,1))],
				[sg.Button('Raw Json', key = '-RAW_JSON-', size = (50,1))],
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
			rebuild_mod_db = lang != values['-COMBO-']
			if saveSettings(values, rebuild_mod_db):
				break
		elif event == '-COMBO-':
			window['-SET_LANG-'].update(tr.getTrans('set_lang', values['-COMBO-']))
			window['-FS_PATH_TEXT-'].update(tr.getTrans('get_fs_path', values['-COMBO-']))
			window['-FS_GAME_DATA_PATH_TEXT-'].update(tr.getTrans('get_fs_game_data_path', values['-COMBO-']))
			window['-ALL_MODS_PATH_TEXT-'].update(tr.getTrans('get_all_mods_path', values['-COMBO-']))
			window['-SAVE-'].update(tr.getTrans('save', values['-COMBO-']))
			window['-EXIT-'].update(tr.getTrans('exit', values['-COMBO-']))
			window['-SET_DEF_FS-'].update(text = tr.getTrans('remember', values['-COMBO-']))
			if vers == 'fs19':
				window['-DEF_FS-'].update(tr.getTrans('def_fs19', values['-COMBO-']))
				window['-DEF_SG_FS-'].update(tr.getTrans('def_sg_fs19', values['-COMBO-']))
				window['-DEF_FS_STEAM-'].update(tr.getTrans('def_fs22_steam', values['-COMBO-']))
			else:
				window['-DEF_SG_FS-'].update(tr.getTrans('def_sg_fs22', values['-COMBO-']))
				window['-DEF_FS-'].update(tr.getTrans('def_fs22', values['-COMBO-']))
				window['-DEF_FS_STEAM-'].update(tr.getTrans('def_fs22_steam', values['-COMBO-']))
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
		elif event == '-RESET-':
			resetFSL()
		elif event == '-RAW_JSON-':
			exportRawJson()
			break
	window.close()
	return io
