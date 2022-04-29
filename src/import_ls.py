import PySimpleGUI as sg
import settings as se
import translation as tr
import game as ga

import os
import zipfile
import xml.etree.ElementTree as ET
import shutil
from tinydb import TinyDB, Query
from tinydb.operations import delete
import logging as log
import pysed
import hashlib
import pathlib
existing_mods = {}

def importAllMods(path, rem = False):
	files = os.listdir(path)
	all_mods = se.getSettings('all_mods_path')
	for i in files:
		if i.endswith('.zip'):
			with zipfile.ZipFile(path + os.sep + i) as z:
				try:
					moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8').strip())
					version = moddesc.find('version')
					shutil.copyfile(path + os.sep + i, all_mods + os.sep + 'fsl_' + version.text + '!' + i)
				except ET.ParseError:
					sg.popup_error(tr.getTrans('import_failed').format(i), title=tr.getTrans('error'), location = (50, 50))
					pass
	if rem == True or sg.popup_yes_no(tr.getTrans('remove_src_folder').format(path), title = tr.getTrans('remove_title'), location = (50, 50)) == 'Yes':
		try:
			shutil.rmtree(path)
		except FileNotFoundError:
			pass

def getMods(path):
	mods = []
	all_mods = os.listdir(se.getSettings('all_mods_path'))
	try:
		files = os.listdir(path)
		for i in files:
			if i.endswith('.zip'):
				with zipfile.ZipFile(path + os.sep + i) as z:
					try:
						moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8').strip())
						version = moddesc.find('version')
						descV = int(moddesc.attrib['descVersion'])
						f_name = 'fsl_' + version.text + '!' + i
						if f_name in all_mods:
							moddesc = None
						if se.vers == 'fs19' and int(descV / 10) >= 6:
							moddesc = None
						if se.vers == 'fs22' and int(descV / 10) < 6:
							moddesc = None
					except FileNotFoundError:
						moddesc = None
						pass
					except KeyError:
						moddesc = None
						pass
					except ET.ParseError:
						sg.popup_error(tr.getTrans('import_failed').format(i), title=tr.getTrans('error'), location = (50, 50))
						moddesc = None
						pass
					if moddesc:
						mods.append(i)
	except FileNotFoundError:
		pass
	if not mods:
		sg.popup_ok(tr.getTrans('no_mod_found'), title = '')
	return mods

def getSaveGames():
	""" get stored save games
	read the according games_lsxx.json and extract maps
	"""
	all_mods_folder = se.getSettings('all_mods_path') + os.sep
	q = Query()
	all = TinyDB(se.games_json).all()
	l = []
	for i in all:
		n = i['name']
		m = i['map']
		if i['map'] not in se.getInternalMaps().values():
			try:
				with zipfile.ZipFile(all_mods_folder + m) as z:
					moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8').strip())
					m = moddesc.find('maps/map/title/en')
					if m != None:
						l.append(n + ' : ' + m.text)
			except FileNotFoundError:
				l.append(n + ' : ' + tr.getTrans('ghostmap'))
				pass
		else:
			m = list(se.getInternalMaps().keys())[list(se.getInternalMaps().values()).index(m)]
			l.append(n + ' : ' + m)
	return l

def updateSGS(sgs, mod):
	name = mod.split('!')[1]
	for sg in sgs:
		add = True
		dataset = TinyDB(se.games_json).get((Query().name == sg.split(' : ')[0]))
		mods = dataset['mods']
		for i in mods.items():
			if name in i[1]:
				add = False
				mods.update({i[0]: mod})
				break
		if add:
			mods.update({str(len(mods)): mod})
		TinyDB(se.games_json).update({"mods": mods}, doc_ids = [dataset.doc_id])
		if sg.popup_yes_no(tr.getTrans('exportsg')) == 'Yes':
			ga.exportSGC(sg.split(' : ')[0])
		# TODO map update
	return

def importMods(path, mods, updateSGs):
	all_mods = se.getSettings('all_mods_path')
	for i in mods:
		with zipfile.ZipFile(path + os.sep + i) as z:
			moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8').strip())
			version = moddesc.find('version')
			new_name = 'fsl_' + version.text + '!' + i	
			shutil.copyfile(path + os.sep + i, all_mods + os.sep + new_name)
			if moddesc.find('maps/map/title/en') != None:
				break
			else:
				if updateSGs:
					layout = [	[sg.Text(tr.getTrans('select_sgs').format(i))],
								[sg.Listbox(getSaveGames(),  key = '-SGS-', size = (108, 10), select_mode = 'extended')],
								[sg.Button('Ok', key = '-OK-', size = (14, 1))]
					]
					window = sg.Window(tr.getTrans('import'), layout, finalize = True, location = (50, 50), disable_close = True)

					while True:
						event, values = window.read()
						#print(event, values)
						if event == '-OK-':
							if len(values['-SGS-']) > 0:
								updateSGS(values['-SGS-'], new_name)
							window.close()
							break

def removeMods(mods):
	all_mods = se.getSettings('all_mods_path')
	datasets = TinyDB(se.games_json).all()
	for i, val in enumerate(mods):
		unused = True
		for i in range(len(datasets)):
			if existing_mods[val] in list(datasets[i]['mods'].values()) or existing_mods[val] in datasets[i]['map']:
				sg.popup_ok(tr.getTrans('cant_rem_mod').format(existing_mods[val], datasets[i]['name']), title = tr.getTrans('error'))
				unused = False
				break
		if unused:
			os.remove(all_mods + os.sep + existing_mods[val])

def getAllMods():
	global existing_mods
	m = ga.getMods(False)
	existing_mods = m[0]
	existing_mods.update(m[1])
	for i in list(se.getInternalMaps()):
		del existing_mods[i]
	return list(sorted(existing_mods.keys()))

def guiImportMods(updateSGs = True):
	layout =    [	[sg.Text(tr.getTrans('get_mod_path'))],
					[sg.Input('', key = '-MOD_PATH-', size = (110, 1), enable_events = True)],
					[sg.FolderBrowse(initial_folder = se.getSettings('fs_game_data_path'), target = '-MOD_PATH-', size = (96,1))],
					[sg.Text(tr.getTrans('importable_mods'))],
					[sg.Listbox('',  key = '-MODS-', size = (108, 10), select_mode = 'extended')],
					[sg.Button(tr.getTrans('import'), key = '-IMPORT-', size = (96, 1))],
					[sg.Text(tr.getTrans('existing_mods'))],
					[sg.Listbox(getAllMods(),  key = '-MODS_INST-', size = (108, 10), select_mode = 'extended')],
					[sg.Button(tr.getTrans('remove'), key = '-REMOVE-', size = (96, 1))],
					[sg.Text('')],
					[sg.Button(tr.getTrans('exit'), key = '-EXIT-', size = (14, 1))]
				]

	window = sg.Window(tr.getTrans('import'), layout, finalize = True, location = (50, 50))

	while True:
		event, values = window.read()
		#print(event, values)
		if event == sg.WIN_CLOSED or event=="-EXIT-":
			break
		elif event == "-IMPORT-":
			#window.Hide()
			importMods(values['-MOD_PATH-'], values['-MODS-'], updateSGs)
			#window.UnHide()
			window['-MOD_PATH-'].update('')
			window['-MODS-'].update(values = '')
			window['-MODS_INST-'].update(getAllMods())
		elif event == '-REMOVE-':
			removeMods(values['-MODS_INST-'])
			window['-MODS_INST-'].update(getAllMods())
		elif event == '-MOD_PATH-':
			window['-MODS-'].update(values = getMods(values['-MOD_PATH-']))
	window.close()
	return

def importSavegame(values):
	if not os.path.exists(values['-SG_PATH-'] + os.sep + 'careerSavegame.xml'):
		sg.popup_ok(tr.getTrans('no_savegame_files'), title = tr.getTrans('missing'), location = (50, 50))
		return False
	all_maps, all_mods = ga.getMods(False)
	map_title = ET.parse(values['-SG_PATH-'] + os.sep + 'careerSavegame.xml').find('settings/mapTitle').text
	modFromXML = ET.parse(values['-SG_PATH-'] + os.sep + 'careerSavegame.xml').findall('mod')
	mods = []
	missing_mods = False
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
				sg.popup_ok(tr.getTrans('missing_map').format(i.attrib['title'], vers), title = tr.getTrans('missing'), location = (50, 50))
		else:
			mods_tmp = []
			for key, val in all_mods.items():
				if vers + '!' + name in val:
					mods_tmp.append('fsl_' + vers + '!' + name)
			if len(mods_tmp) > 1:
				#TODO select version
				print('select version')
			elif len(mods_tmp) == 1:
				mods.append(mods_tmp[0])
			elif len(mods_tmp) == 0 and not name.startswith('pdlc'):
				mods.append('fsl_' + vers + '!' + name)
				missing_mods = True
	
	if ':' in values['-TITLE-']:
		sg.popup(tr.getTrans('ssg_wrong_char'), title = tr.getTrans('ssg_title_char'), location = (50, 50))
		return False
	#if values['-TITLE-'] == 'savegame1':
	#	sg.popup(tr.getTrans('ssg_wrong_title'), title = tr.getTrans('ssg_title_title'), location = (50, 50))
	#	return False
	if values['-TITLE-'] == '':
		sg.popup(tr.getTrans('ssg_name_empty'), title = tr.getTrans('ssg_title_empty'), location = (50, 50))
		return False
	if TinyDB(se.games_json).get((Query().name == values['-TITLE-'])) or os.path.exists(se.getSettings('fs_game_data_path') + os.sep + values['-TITLE-']):
		sg.popup(tr.getTrans('ssg_exists'), title = tr.getTrans('ssg_title'), location = (50, 50))
		return False

	modstoadd = {}
	for i, val in enumerate(mods):
		modstoadd[str(i)] = mods[i]

	if len(maps) == 0:
		maps.append(map_title)
	folder_name = hashlib.md5(values['-TITLE-'].encode()).hexdigest()
	TinyDB(se.games_json).insert({"name": values['-TITLE-'], "folder": folder_name, "desc": values['-DESC-'], "map": maps[0], "mods": modstoadd})

	os.mkdir(se.getSettings('fs_game_data_path') + os.sep + folder_name)
	for i in os.listdir(values['-SG_PATH-']):
		shutil.move(values['-SG_PATH-'] + os.sep + i, se.getSettings('fs_game_data_path') + os.sep + folder_name)
	try:
		os.mkdir(se.getSettings('fs_game_data_path') + os.sep + folder_name + '_Backup') 
	except FileExistsError:
		pass
	if not '-SGB_PATH-' in values:
		bak_path = se.getSettings('fs_game_data_path') + os.sep + 'savegameBackup'
		sg_title = values['-SG_PATH-'].split(os.sep)[-1]
		try:
			for i in os.listdir(bak_path):
				if sg_title in i:
					src = bak_path + os.sep + i
					if os.path.isdir(src):
						dest = se.getSettings('fs_game_data_path') + os.sep + folder_name + '_Backup' + os.sep + 'savegame1_' + i.split('_')[1] + '_' + i.split('_')[2]
						shutil.copytree(src, dest)
						shutil.rmtree(src)
					else:
						dest = se.getSettings('fs_game_data_path') + os.sep + folder_name + '_Backup' + os.sep + 'savegame1_backupLatest.txt'
						shutil.copyfile(src, dest)
						pysed.replace(sg_title, 'savegame1', dest)
						os.remove(src)
			if len(os.listdir(bak_path)) == 0:
				shutil.rmtree(bak_path)
		except FileNotFoundError:
			pass
	else:
		for i in values['-SGB-']:
			src = values['-SGB_PATH-'] + os.sep + i
			if os.path.isdir(src):
				dest = se.getSettings('fs_game_data_path') + os.sep + folder_name + '_Backup' + os.sep + 'savegame1_' + i.split('_')[1] + '_' + i.split('_')[2]
				shutil.copytree(src, dest)
				shutil.rmtree(src)
			else:
				dest = se.getSettings('fs_game_data_path') + os.sep + folder_name + '_Backup' + os.sep + 'savegame1_backupLatest.txt'
				shutil.copyfile(src, dest)
				pysed.replace(i.split('_')[0], 'savegame1', dest)
				os.remove(src)
		if values['-SGB_PATH-'] != '' and len(os.listdir(values['-SGB_PATH-'])) == 0:
			shutil.rmtree(values['-SGB_PATH-'])
	shutil.rmtree(values['-SG_PATH-'])
	if missing_mods:
		sg.popup_ok(tr.getTrans('missing_mod'), title = tr.getTrans('missing'), location = (50, 50))
	return True

def getBackupFolder(path):
	l = []
	if path != '':
		for i in os.listdir(path):
			l.append(i)
	return l

def importSGC(path, title):
	new = TinyDB(path).all()[0]
	fdata = {"hash": hashlib.md5(pathlib.Path(path).read_bytes()).hexdigest(), "path": path}
	if TinyDB(se.games_json).get(Query().name == title):
		doc_id = TinyDB(se.games_json).get(Query().name == TinyDB(path).all()[0]['name']).doc_id
		TinyDB(se.games_json).update({"name": title, "folder": new['folder'], "desc": new['desc'], "map": new['map'], "mods": new['mods'], "imported": fdata}, doc_ids = [doc_id])
	else:
		try:
			os.mkdir(se.getSettings('fs_game_data_path') + os.sep + new['folder'])
			os.mkdir(se.getSettings('fs_game_data_path') + os.sep + new['folder'] + '_Backup')
		except FileExistsError:
			pass
		TinyDB(se.games_json).insert({"name": title, "folder": new['folder'], "desc": new['desc'], "map": new['map'], "mods": new['mods']})

def guiImportSG(path = '', rem = False, overwrite = False):
	ret = True
	if path == '':
		path = se.getSettings('fs_game_data_path')

		layout1 =   [	[sg.Text(tr.getTrans('get_sg_path'))],
						[sg.Input('', key = '-SG_PATH-', size = (92, 1))],
						[sg.FolderBrowse(initial_folder = path, target = '-SG_PATH-', key = '-SG_SELECT-')],
						[sg.Text(tr.getTrans('get_sgb_path'))],
						[sg.Input('', key = '-SGB_PATH-', size = (92, 1), enable_events = True)],
						[sg.FolderBrowse(initial_folder = path, target = '-SGB_PATH-')],
						[sg.Text(tr.getTrans('sgb_title'), size = (60, 1))],
						[sg.Listbox('',  key = '-SGB-', size = (92, 10), select_mode = 'extended')],
						[sg.Text(tr.getTrans('sg_title'), size = (60, 1))],
						[sg.Input(key = '-TITLE-', size = (92, 1))],
						[sg.Text(tr.getTrans('description'), size = (60, 1))],
						[sg.Input(key = '-DESC-', size = (92, 1))],
						[	sg.Button(tr.getTrans('import'), key = '-IMPORT-', size = (14, 1)),
							sg.Button(tr.getTrans('cancel'), key = '-EXIT_1-', size = (14, 1))
						]
					]
		layout2 = 	[	[sg.Text(tr.getTrans('sgc_file'))],
						[sg.Input('', key = '-SGC_PATH-', size = (92,1), enable_events = True)],
						[sg.FileBrowse(file_types = (('Text Files', '*.fsl_sgc'),), target = '-SGC_PATH-', key = '-SGC_SELECT-')],
						[sg.Text(tr.getTrans('sg_title'))],
						[sg.Input('', key = '-I_TITLE-', enable_events = True), sg.Text(tr.getTrans('exists')), sg.Text('', key = '-EXISTS-')],
						[	sg.Button(tr.getTrans('import'), key = '-IMPORT_SGC-', size = (14, 1)),
							sg.Button(tr.getTrans('cancel'), key = '-EXIT_2-', size = (14, 1))
						]
					]
		layout = 	[	[sg.TabGroup(	[	[sg.Tab(tr.getTrans('sg_import_tab'), layout1)],
											[sg.Tab(tr.getTrans('sgc_import_tab'), layout2)]
										]
									)]	
					]
	else:
		sg_title = 'SG' + path.split('savegame')[1]
		layout =	[	[sg.Text(tr.getTrans('sg_title'), size = (92, 1))],
						[sg.Input(sg_title, key = '-TITLE-', size = (92, 1))],
						[sg.Text(tr.getTrans('description'), size = (92, 1))],
						[sg.Input(key = '-DESC-', size = (92, 1))],
						[sg.Input(path, key = '-SG_PATH-', size = (92, 1), readonly = True)],
						[sg.Text('')],
						[	sg.Button(tr.getTrans('import'), key = '-IMPORT-', size = (14, 1)),
							sg.Button(tr.getTrans('cancel'), key = '-EXIT-', size = (14, 1))
						]
					]
	
	window = sg.Window(tr.getTrans('import'), layout, finalize = True, location = (50, 50))

	while True:
		event, values = window.read()
		#print(event, values)
		if event == sg.WIN_CLOSED or event=="-EXIT_1-" or event=="-EXIT_2-":
			ret = False
			break
		elif event == '-SGB_PATH-':
			window['-SGB-'].update(values = getBackupFolder(values['-SGB_PATH-']))
		elif event == "-IMPORT-":
			w = sg.Window('', no_titlebar = True, layout = [[sg.Text(tr.getTrans('wait_for_import'))]], finalize = True, location = (50, 50))
			if importSavegame(values):
				break
			w.close()
		elif event == '-IMPORT_SGC-':
			importSGC(values['-SGC_PATH-'], values['-I_TITLE-'])
			break
		elif event == '-SGC_PATH-':
			window['-I_TITLE-'].update(TinyDB(values['-SGC_PATH-']).all()[0]['name'])
			if TinyDB(se.games_json).get(Query().name == TinyDB(values['-SGC_PATH-']).all()[0]['name']):
				window['-EXISTS-'].update(tr.getTrans('yes'), background_color = 'red')
			else:
				window['-EXISTS-'].update(tr.getTrans('no'), background_color = 'green')
		elif event == '-I_TITLE-':
			if TinyDB(se.games_json).get(Query().name == values['-I_TITLE-']):
				window['-EXISTS-'].update(tr.getTrans('yes'), background_color = 'red')
			else:
				window['-EXISTS-'].update(tr.getTrans('no'), background_color = 'green')
			
	window.close()
	return ret