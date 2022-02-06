import PySimpleGUI as sg
import settings as se
import translation as tr
import newgame as ne

import os
import zipfile
import xml.etree.ElementTree as ET
import shutil
from tinydb import TinyDB, Query

window_size = (800, 350)

def importMods(path, rem = False):
	files = os.listdir(path)
	all_mods = se.getSettings('all_mods_path')
	for i in files:
		if i.endswith('.zip'):
			with zipfile.ZipFile(path + os.sep + i) as z:
				moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8'))
				version = moddesc.find('version')
				shutil.copyfile(path + os.sep + i, all_mods + os.sep + 'fsl_' + version.text + '!' + i)
	if rem == True or sg.popup_yes_no(tr.getTrans('remove_src_folder').format(path), title = tr.getTrans('remove_title')) == 'Yes':
		try:
			shutil.rmtree(path)
		except FileNotFoundError:
			pass

def guiImportMods():
	layout =    [	[sg.Text(tr.getTrans('get_mod_path'))], 
					[sg.Input('', key = '-MOD_PATH-'), sg.FolderBrowse(initial_folder = se.getSettings('fs_game_data_path'))],
					[	sg.Button(tr.getTrans('import'), key = '-IMPORT-'),
						sg.Button(tr.getTrans('exit'), key = '-EXIT-')
					]
				]

	window = sg.Window(tr.getTrans('import_mods'), layout, size = window_size)

	while True:
		event, values = window.read()
		if event == sg.WIN_CLOSED or event=="-EXIT-":
			break
		elif event == "-IMPORT-":
			importMods(values['-MOD_PATH-'])
			window['-MOD_PATH-'].update('')

	window.close()
	return

def importSavegame(values, rem):
	all_maps, all_mods = ne.getMods(False)
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
				sg.popup_ok(tr.getTrans('missing_map').format(i.attrib['title'], vers))
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
			elif len(mods_tmp) == 0:
				mods.append('fsl_' + vers + '!' + name)
				sg.popup_ok(tr.getTrans('missing_mod').format(i.attrib['title'], vers))

	
	if ':' in values['-TITLE-']:
		sg.popup(tr.getTrans('ssg_wrong_char'), title = tr.getTrans('ssg_title_char'))
		return False
	if values['-TITLE-'] == 'savegame1':
		sg.popup(tr.getTrans('ssg_wrong_title'), title = tr.getTrans('ssg_title_title'))
		return False
	if TinyDB('games.json').get((Query().name == values['-TITLE-'])):
		sg.popup(tr.getTrans('ssg_exists'), title = tr.getTrans('ssg_title'))
		return False
	if values['-TITLE-'] == '':
		sg.popup(tr.getTrans('ssg_name_empty'), title = tr.getTrans('ssg_title_empty'))
		return False

	print(mods)
	modstoadd = {}
	for i, val in enumerate(mods):
		modstoadd[str(i)] = mods[i]

	TinyDB('games.json').insert({"name": values['-TITLE-'], "desc": values['-DESC-'], "map": maps[0], "mods": modstoadd})

	os.mkdir(se.getSettings('fs_game_data_path') + os.sep + values['-TITLE-'])
	for i in os.listdir(values['-SG_PATH-']):
		shutil.move(values['-SG_PATH-'] + os.sep + i, se.getSettings('fs_game_data_path') + os.sep + values['-TITLE-'])
	bak_path = se.getSettings('fs_game_data_path') + os.sep + 'savegameBackup'
	sg_title = values['-SG_PATH-'].split(os.sep)[-1]
	for i in os.listdir(bak_path):
		if sg_title in i:
			try:
				os.mkdir(se.getSettings('fs_game_data_path') + os.sep + values['-TITLE-'] + ' Backup') 
			except FileExistsError:
				pass
			shutil.move(bak_path + os.sep + i, se.getSettings('fs_game_data_path') + os.sep + values['-TITLE-'] + ' Backup')
	return True

def guiImportSG(path = '', rem = False):
	ret = True
	if path == '':
		path = se.getSettings('fs_game_data_path')

		layout =    [	[sg.Text(tr.getTrans('sg_title'), size = (window_size[0]-10, 1))],
						[sg.Input(key = '-TITLE-', size = (window_size[0]-10, 1))],
						[sg.Text(tr.getTrans('description'), size = (window_size[0]-10, 1))],
						[sg.Input(key = '-DESC-', size = (window_size[0]-10, 1))],
						[sg.Text(tr.getTrans('get_sg_path'))],
						[sg.Input('', key = '-SG_PATH-'), sg.FolderBrowse(initial_folder = path)],
						[	sg.Button(tr.getTrans('import'), key = '-IMPORT-'),
							sg.Button(tr.getTrans('exit'), key = '-EXIT-')
						]
					]
	else:
		layout =	[	[sg.Text(tr.getTrans('sg_title'), size = (window_size[0]-10, 1))],
						[sg.Input(key = '-TITLE-', size = (window_size[0]-10, 1))],
						[sg.Text(tr.getTrans('description'), size = (window_size[0]-10, 1))],
						[sg.Input(key = '-DESC-', size = (window_size[0]-10, 1))],
						[sg.Input(path, key = '-SG_PATH-', size = (window_size[0]-10, 1), readonly = True)],
						[	sg.Button(tr.getTrans('import'), key = '-IMPORT-'),
							sg.Button(tr.getTrans('exit'), key = '-EXIT-')
						]
					]

	window = sg.Window(tr.getTrans('import_mods'), layout, size = window_size, finalize = True)

	while True:
		event, values = window.read()
		if event == sg.WIN_CLOSED or event=="-EXIT-":
			ret = False
			break
		elif event == "-IMPORT-":
			if importSavegame(values, rem):
				break
	window.close()
	return ret