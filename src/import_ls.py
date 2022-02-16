import PySimpleGUI as sg
import settings as se
import translation as tr
import game as ga

import os
import zipfile
import xml.etree.ElementTree as ET
import shutil
from tinydb import TinyDB, Query

existing_mods = {}

def importAllMods(path, rem = False):
	files = os.listdir(path)
	all_mods = se.getSettings('all_mods_path')
	for i in files:
		if i.endswith('.zip'):
			with zipfile.ZipFile(path + os.sep + i) as z:
				moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8'))
				version = moddesc.find('version')
				shutil.copyfile(path + os.sep + i, all_mods + os.sep + 'fsl_' + version.text + '!' + i)
	if rem == True or sg.popup_yes_no(tr.getTrans('remove_src_folder').format(path), title = tr.getTrans('remove_title'), location = (50, 50), icon = 'logo.ico') == 'Yes':
		try:
			shutil.rmtree(path)
		except FileNotFoundError:
			pass

def getMods(path):
	mods = []
	files = os.listdir(path)
	for i in files:
		if i.endswith('.zip'):
			with zipfile.ZipFile(path + os.sep + i) as z:
				try:
					moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8'))
				except FileNotFoundError:
					pass
				if moddesc:
					mods.append(i)
	return mods

def importMods(path, mods):
	all_mods = se.getSettings('all_mods_path')
	for i in mods:
		with zipfile.ZipFile(path + os.sep + i) as z:
			moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8'))
			version = moddesc.find('version')
			shutil.copyfile(path + os.sep + i, all_mods + os.sep + 'fsl_' + version.text + '!' + i)

def removeMods(mods):
	all_mods = se.getSettings('all_mods_path')
	for i, val in enumerate(mods):
		os.remove(all_mods + os.sep + existing_mods[val])

def getAllMods():
	global existing_mods
	m = ga.getMods(False)
	existing_mods = m[0]
	existing_mods.update(m[1])
	del existing_mods['Standard']
	return list(existing_mods.keys())

def guiImportMods():
	layout =    [	[sg.Text(tr.getTrans('get_mod_path'))],
					[sg.Input('', key = '-MOD_PATH-', enable_events=True, size = (108, 1))],
					[sg.FolderBrowse(initial_folder = se.getSettings('fs_game_data_path'), target = '-MOD_PATH-')],
					[sg.Text(tr.getTrans('importable_mods'))],
					[sg.Listbox('',  key = '-MODS-', size = (108, 10), select_mode = 'extended')],
					[sg.Button(tr.getTrans('import'), key = '-IMPORT-', size = (96, 1))],
					[sg.Text(tr.getTrans('existing_mods'))],
					[sg.Listbox(getAllMods(),  key = '-MODS_INST-', size = (108, 10), select_mode = 'extended')],
					[sg.Button(tr.getTrans('remove'), key = '-REMOVE-', size = (96, 1))],
					[sg.Text('')],
					[sg.Button(tr.getTrans('exit'), key = '-EXIT-', size = (14, 1))]
				]

	window = sg.Window(tr.getTrans('import'), layout, finalize = True, location = (50, 50), icon = 'logo.ico')

	while True:
		event, values = window.read()
		if event == sg.WIN_CLOSED or event=="-EXIT-":
			break
		elif event == "-IMPORT-":
			if len(values['-MODS-']) == len(getMods(values['-MOD_PATH-'])):
				importAllMods(values['-MOD_PATH-'])
			else:
				importMods(values['-MOD_PATH-'], values['-MODS-'])
			window['-MOD_PATH-'].update('')
			window['-MODS-'].update(values = '')
			window['-MODS_INST-'].update(getAllMods())
		elif event == '-MOD_PATH-':
			window['-MODS-'].update(values = getMods(values['-MOD_PATH-']))
		elif event == '-REMOVE-':
			removeMods(values['-MODS_INST-'])
			window['-MODS_INST-'].update(getAllMods())
	window.close()
	return

def importSavegame(values, rem):
	all_maps, all_mods = ga.getMods(False)
	map_title = ET.parse(values['-SG_PATH-'] + os.sep + 'careerSavegame.xml').find('settings/mapTitle').text
	modFromXML = ET.parse(values['-SG_PATH-'] + os.sep + 'careerSavegame.xml').findall('mod')
	mods = []
	maps = []
	for i in modFromXML:
		name = i.attrib['modName'] + '.zip'
		requ = i.attrib['required']
		vers = i.attrib['version']
		if requ == "true":
			maps_tmp = []
			# mod is map ?
			for key, val in all_maps.items():
				if vers + '!' + name in val:
					maps_tmp.append('fsl_' + vers + '!' + name)
			if len(maps_tmp) > 1:
				#TODO select version
				print('select version')
			elif len(maps_tmp) == 1:
				maps.append(maps_tmp[0])
			elif len(maps_tmp) == 0:
				maps.append('fsl_' + vers + '!' + name)
				sg.popup_ok(tr.getTrans('missing_map').format(i.attrib['title'], vers), location = (50, 50), icon = 'logo.ico')
		else:
			mods_tmp = []
			for key, val in all_mods.items():
				if vers + '!' + name in val[0]:
					mods_tmp.append('fsl_' + vers + '!' + name)
			if len(mods_tmp) > 1:
				#TODO select version
				print('select version')
			elif len(mods_tmp) == 1:
				mods.append(mods_tmp[0])
			elif len(mods_tmp) == 0 and not name.startswith('pdlc') and values['-IGN_MISS-']:
				mods.append('fsl_' + vers + '!' + name)
				sg.popup_ok(tr.getTrans('missing_mod').format(i.attrib['title'], vers), location = (50, 50), icon = 'logo.ico')

	
	if ':' in values['-TITLE-']:
		sg.popup(tr.getTrans('ssg_wrong_char'), title = tr.getTrans('ssg_title_char'), location = (50, 50), icon = 'logo.ico')
		return False
	if values['-TITLE-'] == 'savegame1':
		sg.popup(tr.getTrans('ssg_wrong_title'), title = tr.getTrans('ssg_title_title'), location = (50, 50), icon = 'logo.ico')
		return False
	if TinyDB(se.games_json).get((Query().name == values['-TITLE-'])) or os.path.exists(se.getSettings('fs_game_data_path') + os.sep + values['-TITLE-']):
		sg.popup(tr.getTrans('ssg_exists'), title = tr.getTrans('ssg_title'), location = (50, 50), icon = 'logo.ico')
		return False
	if values['-TITLE-'] == '':
		sg.popup(tr.getTrans('ssg_name_empty'), title = tr.getTrans('ssg_title_empty'), location = (50, 50), icon = 'logo.ico')
		return False

	modstoadd = {}
	for i, val in enumerate(mods):
		modstoadd[str(i)] = mods[i]

	if len(maps) == 0:
		maps.append('fs_internal')
	TinyDB(se.games_json).insert({"name": values['-TITLE-'], "desc": values['-DESC-'], "map": maps[0], "mods": modstoadd})

	os.mkdir(se.getSettings('fs_game_data_path') + os.sep + values['-TITLE-'])
	for i in os.listdir(values['-SG_PATH-']):
		shutil.move(values['-SG_PATH-'] + os.sep + i, se.getSettings('fs_game_data_path') + os.sep + values['-TITLE-'])
	bak_path = se.getSettings('fs_game_data_path') + os.sep + 'savegameBackup'
	sg_title = values['-SG_PATH-'].split(os.sep)[-1]
	try:
		os.mkdir(se.getSettings('fs_game_data_path') + os.sep + values['-TITLE-'] + ' Backup') 
	except FileExistsError:
		pass
	try:
		for i in os.listdir(bak_path):
			if sg_title in i:
				shutil.move(bak_path + os.sep + i, se.getSettings('fs_game_data_path') + os.sep + values['-TITLE-'] + ' Backup')
	except FileNotFoundError:
		pass
	shutil.rmtree(values['-SG_PATH-'])
	return True

def guiImportSG(path = '', rem = False):
	ret = True
	if path == '':
		path = se.getSettings('fs_game_data_path')

		layout =    [	[sg.Text(tr.getTrans('sg_title'), size = (60, 1))],
						[sg.Input(key = '-TITLE-', size = (92, 1))],
						[sg.Text(tr.getTrans('description'), size = (60, 1))],
						[sg.Input(key = '-DESC-', size = (92, 1))],
						[sg.Text(tr.getTrans('get_sg_path'))],
						[sg.Input('', key = '-SG_PATH-', size = (92, 1))],
						[sg.FolderBrowse(initial_folder = path, target = '-SG_PATH-')],
						[sg.Checkbox(tr.getTrans('ignore_missing_mods'), key = '-IGN_MISS-', default = True)],
						[	sg.Button(tr.getTrans('import'), key = '-IMPORT-', size = (14, 1)),
							sg.Button(tr.getTrans('exit'), key = '-EXIT-', size = (14, 1))
						]
					]
	else:
		sg_title = 'SG' + path.split('savegame')[1]
		layout =	[	[sg.Text(tr.getTrans('sg_title'), size = (92, 1))],
						[sg.Input(sg_title, key = '-TITLE-', size = (92, 1))],
						[sg.Text(tr.getTrans('description'), size = (92, 1))],
						[sg.Input(key = '-DESC-', size = (92, 1))],
						[sg.Input(path, key = '-SG_PATH-', size = (92, 1), readonly = True)],
						[sg.Checkbox(tr.getTrans('ignore_missing_mods'), key = '-IGN_MISS-', default = True)],
						[sg.Text('')],
						[	sg.Button(tr.getTrans('import'), key = '-IMPORT-', size = (14, 1)),
							sg.Button(tr.getTrans('exit'), key = '-EXIT-', size = (14, 1))
						]
					]

	window = sg.Window(tr.getTrans('import'), layout, finalize = True, location = (50, 50), icon = 'logo.ico')

	while True:
		event, values = window.read()
		if event == sg.WIN_CLOSED or event=="-EXIT-":
			ret = False
			break
		elif event == "-IMPORT-":
			w = sg.Window('', no_titlebar = True, layout = [[sg.Text(tr.getTrans('wait_for_import'))]], finalize = True, location = (50, 50), icon = 'logo.ico')
			if importSavegame(values, rem):
				break
			w.close()
	window.close()
	return ret