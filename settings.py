import os
import PySimpleGUI as sg
import translation as tr
import import_ls as im

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
	else:
		all_mods_path = values['-ALL_MODS_PATH-'] + os.sep + 'fsl_all_mods'
		try:
			os.makedirs(all_mods_path)
		except FileExistsError:
			pass
	db.update({'language': values['-COMBO-'], 'fs_path': values['-FS_PATH-'], 'fs_game_data_path': values['-FS_GAME_DATA_PATH-'], 'all_mods_path': all_mods_path}, doc_ids = [1])
	return True

def getSettings(key):
	db = TinyDB('settings.json')
	q = Query()
	settings = db.get(doc_id = 1)
	return settings[key]

def checkInit(lang, init):
	if init:
		db = TinyDB('settings.json')
		db.insert({'language': lang, 'fs_path': 'C:/Program Files (x86)', 'fs_game_data_path': os.path.expanduser('~').replace('\\', '/') + '/Documents/My Games', 'all_mods_path': os.path.expanduser('~').replace('\\', '/') + '/Documents/My Games', 'last_sg': '', 'sg_hash': '', 'sgb_hash': '', 'mods_hash': ''})

def guiSettings(lang, init = False):
	io = True
	checkInit(lang, init)
	p = getSettings('fs_path').split(os.sep)
	fs = getSettings('fs_path')
	gd = getSettings('fs_game_data_path')
	am = getSettings('all_mods_path')
	lang = getSettings('language')

	layout = [	[sg.Text(tr.getTrans('set_lang'), key = '-SET_LANG-'), sg.Combo(values = tr.getLangs(), size = (window_size[0]-10,5), default_value = lang, key = '-COMBO-', enable_events = True)],
				[sg.Text(tr.getTrans('get_fs_path'), key = '-FS_PATH_TEXT-')], 
				[sg.Input(fs, key = '-FS_PATH-', size = (100, 1)), sg.FileBrowse(initial_folder = fs)], 
				[sg.Button(tr.getTrans('def_fs19'), key = '-DEF_FS19-'), sg.Button(tr.getTrans('def_fs22'), key = '-DEF_FS22-')],
				[sg.Text(tr.getTrans('get_fs_game_data_path'), key = '-FS_GAME_DATA_PATH_TEXT-')], 
				[sg.Input(gd, key = '-FS_GAME_DATA_PATH-', size = (100, 1)), sg.FolderBrowse(initial_folder = gd)],
				[sg.Button(tr.getTrans('def_sg_fs19'), key = '-DEF_SG_FS19-'), sg.Button(tr.getTrans('def_sg_fs22'), key = '-DEF_SG_FS22-')],
				[sg.Text(tr.getTrans('get_all_mods_path'), key = '-ALL_MODS_PATH_TEXT-')], 
				[sg.Input(am, key = '-ALL_MODS_PATH-', size = (80, 1)), sg.FolderBrowse(initial_folder = am), sg.Button(tr.getTrans('import_mods'), key = '-IMPORT-')],
				[	sg.Button(tr.getTrans('save'), key = '-SAVE-'),
					sg.Button(tr.getTrans('exit'), key = '-EXIT-')
				]
			]

	window = sg.Window(tr.getTrans('settings'), layout, size = window_size, finalize = True)
	if init:
		window['-IMPORT-'].update(disabled = True)
		
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
			window['-SET_LANG-'].update(tr.getTrans('set_lang', values['-COMBO-']))
			window['-FS_PATH_TEXT-'].update(tr.getTrans('get_fs_path', values['-COMBO-']))
			window['-FS_GAME_DATA_PATH_TEXT-'].update(tr.getTrans('get_fs_game_data_path', values['-COMBO-']))
			window['-ALL_MODS_PATH_TEXT-'].update(tr.getTrans('get_all_mods_path', values['-COMBO-']))
			window['-SAVE-'].update(tr.getTrans('save', values['-COMBO-']))
			window['-EXIT-'].update(tr.getTrans('exit', values['-COMBO-']))
			window['-DEF_FS19-'].update(tr.getTrans('def_fs19', values['-COMBO-']))
			window['-DEF_FS22-'].update(tr.getTrans('def_fs22', values['-COMBO-']))
			window['-DEF_SG_FS19-'].update(tr.getTrans('def_sg_fs19', values['-COMBO-']))
			window['-DEF_SG_FS22-'].update(tr.getTrans('def_sg_fs22', values['-COMBO-']))
		elif event == '-IMPORT-':
			window.Hide()
			im.guiImportMods()
			window.UnHide()
		elif event == '-DEF_FS19-':
			window['-FS_PATH-'].update('C:/Program Files (x86)/Farming Simulator 2019/FarmingSimulator2019.exe')
		elif event == '-DEF_FS22-':
			window['-FS_PATH-'].update('C:/Program Files (x86)/Farming Simulator 2022/FarmingSimulator2022.exe')
		elif event == '-DEF_SG_FS19-':
			window['-FS_GAME_DATA_PATH-'].update(os.path.expanduser('~').replace('\\', '/') + '/Documents/My Games/FarmingSimulator2019')
		elif event == '-DEF_SG_FS22-':
			window['-FS_GAME_DATA_PATH-'].update(os.path.expanduser('~').replace('\\', '/') + '/Documents/My Games/FarmingSimulator2022')
	window.close()
	return io