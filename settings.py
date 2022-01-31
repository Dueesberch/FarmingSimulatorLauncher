import os
import PySimpleGUI as sg
import translation as tr

from tinydb import TinyDB, Query

window_size = (800, 350) 
	
def saveSettings(values):
	db = TinyDB('settings.json')
	if values['-FS_PATH-'] == '':
		sg.popup_error(tr.getTrans(values['-COMBO-'], 'empty_fs_path'), title = 'miss_path')
		return False
	if values['-FS_GAME_DATA_PATH-'] == '':
		sg.popup_error(tr.getTrans(values['-COMBO-'], 'empty_fs_gd_path'), title = 'miss_path')
		return False
	if values['-ALL_MODS_PATH-'] == '':
		sg.popup_error(tr.getTrans(values['-COMBO-'], 'empty_all_mods_path'), title = 'miss_path')
		return False
	db.update({'language': values['-COMBO-'], 'fs_path': values['-FS_PATH-'], 'fs_game_data_path': values['-FS_GAME_DATA_PATH-'], 'all_mods_path': values['-ALL_MODS_PATH-']}, doc_ids = [1])
	return True

def getSettings(key):
	db = TinyDB('settings.json')
	q = Query()
	settings = db.get(doc_id = 1)
	return settings[key]

def checkInit(lang, init):
	if init:
		db = TinyDB('settings.json')
		db.insert({'language': lang, 'fs_path': '', 'fs_game_data_path': '', 'all_mods_path': '', 'last_sg': '', 'sg_hash': '', 'sgb_hash': '', 'mods_hash': ''})

def guiSettings(lang, init = False):
	io = True
	checkInit(lang, init)
	p = getSettings('fs_path').split(os.sep)
	fs = getSettings('fs_path')
	gd = getSettings('fs_game_data_path')
	am = getSettings('all_mods_path')
	lang = getSettings('language')

	layout = [	[sg.Text(tr.getTrans(lang, 'set_lang')), sg.Combo(values = tr.getLangs(), size = (window_size[0]-10,5), default_value = lang, key = '-COMBO-', enable_events = True)],
				[sg.Text(tr.getTrans(lang, 'get_fs_path'))], [sg.Input(fs, key="-FS_PATH-"), sg.FileBrowse(initial_folder = fs)],
				[sg.Text(tr.getTrans(lang, 'get_fs_game_data_path')), sg.Input(gd, key="-FS_GAME_DATA_PATH-"), sg.FolderBrowse(initial_folder = gd)],
				[sg.Text(tr.getTrans(lang, 'get_all_mods_path')), sg.Input(am, key="-ALL_MODS_PATH-"), sg.FolderBrowse(initial_folder = am)],
				[	sg.Button(tr.getTrans(lang, 'save'), key = '-SAVE-'),
					sg.Button(tr.getTrans(lang, 'exit'), key = '-EXIT-')
				]
			]

	window = sg.Window(tr.getTrans(lang, 'settings'), layout, size = window_size)
		
	while True:
		event, values = window.read()
		if event == sg.WIN_CLOSED or event=="-EXIT-":
			if init:
				os.remove('settings.json')
				io = False
			break
		elif event == "-SAVE-":
			if saveSettings(values):
				break
		elif event == '-COMBO-':
			window.Hide()
			sg.popup_ok(tr.getTrans(values['-COMBO-'], 'restart_requ'), title = tr.getTrans(values['-COMBO-'], 'restart_title'))
			window.UnHide()
	window.close()
	return io