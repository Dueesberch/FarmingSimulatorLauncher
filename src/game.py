import zipfile
import os
import shutil
from pathlib import Path
import hashlib
import subprocess
import platform

import PySimpleGUI as sg
from tinydb import TinyDB, Query
from tinydb.operations import delete
import translation as tr
import settings as se
import logging as log

import xml.etree.ElementTree as ET

mods = {}
maps = {}

def getMods(l = True):
	global mods
	global maps
	files = []
	try:
		files = os.listdir(se.getSettings('all_mods_path'))
	except FileNotFoundError:
		pass
	maps = se.getInternalMaps().copy()
	mods = {}

	maps_data = TinyDB(se.getSettings('all_mods_path') + os.sep + 'mods_db.json').search(Query().mod_type == 'map')
	for m in maps_data:
		for v in m['files']:
			with zipfile.ZipFile(se.getSettings('all_mods_path') + os.sep + v) as z:
				moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8').strip())
				title = moddesc.find('maps/map/title/' + se.getFslSettings('language'))
			if title != None:
				key = title.text + ' - ' + v.split('!')[0].split('_')[1]
			else:
				key = m['name'] + ' - ' + v.split('!')[0].split('_')[1]
			maps[key] = v
	
	mods_data = TinyDB(se.getSettings('all_mods_path') + os.sep + 'mods_db.json').search(Query().mod_type == 'mod')
	for m in mods_data:
		for v in m['files']:
			with zipfile.ZipFile(se.getSettings('all_mods_path') + os.sep + v) as z:
				moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8').strip())
				title = moddesc.find('title/' + se.getFslSettings('language'))
			if title != None:
				key = title.text + ' - ' + v.split('!')[0].split('_')[1]
			else:
				key = m['name'] + ' - ' + v.split('!')[0].split('_')[1]
			mods[key] = v

	files = []
	try:
		files = os.listdir(se.getSettings('fs_game_data_path') + os.sep + 'pdlc')
	except FileNotFoundError:
		pass
	for i in files:
		if i.endswith('.dlc'):
			key = 'DLC ' + i.replace('.dlc', '')
			mods[key] = i
	if l:
		return list(sorted(maps.keys())), list(sorted(mods.keys()))
	else:
		return maps, mods

def removeSaveGame(title):
	q = Query()
	exists = TinyDB(se.games_json).get((q.name == title.split(' : ')[0].rstrip()))
	if sg.popup_yes_no(tr.getTrans('delete'), title = tr.getTrans('remove'), location = (50, 50)) == "Yes":
		TinyDB(se.games_json).remove(doc_ids = [exists.doc_id])
		if os.path.exists(se.getSettings('fs_game_data_path') + os.sep + exists['folder']):
			shutil.rmtree(se.getSettings('fs_game_data_path') + os.sep + exists['folder'])
		if os.path.exists(se.getSettings('fs_game_data_path') + os.sep + exists['folder'] + '_Backup'):
			shutil.rmtree(se.getSettings('fs_game_data_path') + os.sep + exists['folder'] + '_Backup')
	return

def saveSaveGame(values, update):
	global maps
	global mods
	db = TinyDB(se.games_json)
	if ':' in values['-TITLE-']:
		sg.popup(tr.getTrans('ssg_wrong_char'), title = tr.getTrans('ssg_title_char'), location = (50, 50))
		return False
	if update == -1 and db.get((Query().name == values['-TITLE-'])):
		sg.popup(tr.getTrans('ssg_exists'), title = tr.getTrans('ssg_title'), location = (50, 50))
		return False
	if values['-TITLE-'] == '':
		sg.popup(tr.getTrans('ssg_name_empty'), title = tr.getTrans('ssg_title_empty'), location = (50, 50))
		return False
	if values['-MAP-'] == '':
		sg.popup(tr.getTrans('ssg_map_empty'), title = tr.getTrans('ssg_title_empty'), location = (50, 50))
		return False
	modstoadd = {}
	check = {}
	dupes = []
	for i, val in enumerate(values['-MODS-']):
		if not val.startswith('DLC'):
			check[mods[val]] = mods[val].split('!')[1]
	seen = set()
	for x in list(check.values()):
		if x in seen:
			dupes.append(x)
		else:
			seen.add(x)
	for j, v in enumerate(dupes):
		for i in check:
			if check[i] == v:
				dupes[j] = i
				break
	if dupes != []:
		f = ''
		for dupe in dupes:
			for key, value in mods.items():
				if value == dupe:
					f = f + key.split(' - ')[0] + '\n'
		sg.popup_ok(tr.getTrans('dupes_found').format(f), title = tr.getTrans('dupes_title'), location = (50, 50))
		return False

	for i, val in enumerate(values['-MODS-']):
		modstoadd[str(i)] = mods[val]

	if update == -1:
		try:
			folder_name = hashlib.md5(values['-TITLE-'].encode()).hexdigest()
			p = se.getSettings('fs_game_data_path') + os.sep + folder_name
			os.mkdir(p)			
			os.mkdir(p + '_Backup')
			db.insert({"name": values['-TITLE-'], "folder": folder_name, "desc": values['-DESC-'], "map": maps[values['-MAP-']], "mods": modstoadd})
		except FileExistsError:
			sg.popup(str(se.getSettings('fs_game_data_path') + os.sep) + values['-TITLE-'] + '\n' + tr.getTrans('ssg_folder_exists'), title = tr.getTrans('ssg_title'), location = (50, 50))
			return False
	else:
		folder_name = hashlib.md5(values['-TITLE-'].encode()).hexdigest()
		data = db.get(doc_id = update)
		db.update({"name": values['-TITLE-'], "folder": folder_name, "desc": values['-DESC-'], "map": maps[values['-MAP-']], "mods": modstoadd}, doc_ids = [update])
		if data['name'] != se.getSettings('fs_game_data_path') + os.sep + values['-TITLE-']:
			os.rename(se.getSettings('fs_game_data_path') + os.sep + data['folder'], se.getSettings('fs_game_data_path') + os.sep + folder_name)
			os.rename(se.getSettings('fs_game_data_path') + os.sep + data['folder'] + '_Backup', se.getSettings('fs_game_data_path') + os.sep + folder_name + '_Backup')
	if sg.popup_yes_no(tr.getTrans('exportsg')) == 'Yes':
		exportSGC(values['-TITLE-'])
	return True

def addMissingMods(title):
	dataset = TinyDB(se.games_json).get((Query().name == title))['mods']
	mods = list(getMods(False)[1].values())
	missing = []
	for key, value in dataset.items():
		if not value in mods:
			f = value.split('!')[1]
			v = value.split('!')[0][4:]
			missing.append(f + ' : ' + v)
	return missing

def markMods(window, title):
		data = TinyDB(se.games_json).search((Query().name == title))
		window['-TITLE-'].update(title)
		window['-DESC-'].update(data[0]['desc'])
		if data[0]['map'] not in se.getInternalMaps().values():
			window['-MAP-'].update(tr.getTrans('map_not_found').format(data[0]['map'].split('!')[1], data[0]['map'].split('!')[0].split('_')[1]))
		for key, val in maps.items():
			if val == data[0]['map']:
				window['-MAP-'].update(key)
				break
		#window['-MAP-'].update(sg_map)
		selected = []
		for i in data[0]['mods']:
			for key, val in mods.items():
				if val == data[0]['mods'][i]:
					selected.append(key)
					break
		window.Element('-MODS-').SetValue(selected)
		update_sg = TinyDB(se.games_json).get((Query().name == title)).doc_id

def remMissingMods(values):
	dataset = TinyDB(se.games_json).get((Query().name == values['-TITLE-']))
	sg_mods = dict(dataset['mods'])
	miss_mods = []
	for i in values['-MISS-']:
		miss_mods.append('fsl_' + i.split(':')[1].strip() + '!' + i.split(':')[0].rstrip())
	for key, value in dataset['mods'].items():
		if value in miss_mods:
			del(sg_mods[key])
	TinyDB(se.games_json).update({'mods': sg_mods}, doc_ids = [dataset.doc_id])

def exportSGC(title):
	data = TinyDB(se.games_json).get(Query().name == title)
	path = sg.popup_get_folder(tr.getTrans('sgc_export'), title = tr.getTrans('storeat'), default_path = se.getSettings('fs_game_data_path'))
	try:
		path = path + os.sep + ''.join(e for e in title if e.isalnum()) + '.fsl_sgc'
		TinyDB(path).insert(data)
	except AssertionError:
		TinyDB(path).update(data)
	except TypeError:
		pass
	#create mods folder to upload to server
	if sg.popup_yes_no(tr.getTrans('create_upload_folder'), title = '') == 'Yes':
		path = sg.popup_get_folder(tr.getTrans('sgc_mods_export'), title = tr.getTrans('storeat'), default_path = se.getSettings('fs_game_data_path'))
		try:
			path = path + os.sep + ''.join(e for e in title if e.isalnum())
			if os.path.exists(path):
				shutil.rmtree(path)
			os.mkdir(path)
		except TypeError:
			return
		missing = False
		for key, value in data['mods'].items():
			try:
				shutil.copyfile(se.getSettings('all_mods_path') + os.sep + value, path + os.sep + value.split('!')[1])
			except FileNotFoundError:
				missing = True
				pass
		if missing:
			sg.popup_ok(tr.getTrans('sgc_mods_export_missing'), title = tr.getTrans('error'))

def copySG(title):
	title = title.split(':')[0].rstrip()
	new_title = title + ' ' + tr.getTrans('copy')
	base = TinyDB(se.games_json).get(Query().name == title)
	folder = hashlib.md5(new_title.encode()).hexdigest()
	TinyDB(se.games_json).insert({'name': new_title, 'folder': folder, 'desc': base['desc'], 'map': base['map'], 'mods': base['mods']})
	shutil.copytree(se.getSettings('fs_game_data_path') + os.sep + base['folder'], se.getSettings('fs_game_data_path') + os.sep + folder)
	shutil.copytree(se.getSettings('fs_game_data_path') + os.sep + base['folder'] + '_Backup', se.getSettings('fs_game_data_path') + os.sep + folder + '_Backup')

def getFolder(title):
	return TinyDB(se.games_json).search(Query().name == title)[0]['folder']

def guiNewSaveGame(title = None):
	global maps
	global mods
	exp = True
	maps_keys, mods_keys = getMods()
	layout = [  [sg.Text(tr.getTrans('sg_title'), size = (90, 1))],
				[sg.Input(key = '-TITLE-', size = (100, 1), enable_events = True)],
				[sg.Text(tr.getTrans('description'), size = (90, 1))],
				[sg.Input(key = '-DESC-', size = (100, 1), enable_events = True)],
				[sg.Text(tr.getTrans('map'))],
				[sg.Combo(maps_keys, key = '-MAP-', size = (98, 1))],
				[sg.Text('Mods')],
				[sg.Listbox(mods_keys, key = '-MODS-',size = (98, 15), select_mode = 'extended', tooltip = tr.getTrans('tt_gaLbMods'), enable_events = True)],
				[	sg.Button(tr.getTrans('export'), key = '-EXPORT_SAVE-', size = (14, 1)),
					sg.Button(tr.getTrans('select_mods'), key = '-SEL_MOD-', size = (20, 1), visible = False)
				],
				[sg.Text(tr.getTrans('missing'), key = '-MISS_TITLE-', visible = False)],
				[sg.Listbox('', key = '-MISS-', size = (98, 3), select_mode = 'extended', visible = False)],
				[sg.Text('', visible = False)],
				[sg.Button(tr.getTrans('remove'), key = '-REM_MOD-', size = (87, 1), visible = False)],
				[sg.Text(tr.getTrans('folder'), key = '-FOLDER_TEXT-', visible = False), sg.Button('', key = '-FOLDER-', visible = False)],
				[sg.Button(tr.getTrans('cancel'), key = '-EXIT-', size = (14, 1))]
	]
	
	window = sg.Window('FarmingSimulatorLauncher', layout, finalize = True, location = (50, 50))

	update_sg = -1
	if title != None:
		update_sg = TinyDB(se.games_json).get((Query().name == title)).doc_id
		window['-MISS_TITLE-'].update(visible = True)
		window['-SEL_MOD-'].update(visible = True)
		window['-REM_MOD-'].update(visible = True)
		window['-MISS-'].update(values = addMissingMods(title), visible = True)
		window['-MAP-'].update(disabled = True)
		window['-FOLDER-'].update(getFolder(title), visible = True)
		window['-FOLDER_TEXT-'].update(visible = True)
		markMods(window, title)

	while True:
		event, values = window.read()
		#print(event, values)
		if event == sg.WIN_CLOSED or event == '-EXIT-':
			break
		elif event == '-EXPORT_SAVE-':
			if exp:
				exportSGC(values['-TITLE-'])
			else:
				if saveSaveGame(values, update_sg):
					break
		elif event == '-SEL_MOD-':
			markMods(window, title)
		elif event == '-REM_MOD-':
			remMissingMods(values)
			window['-MISS-'].update(addMissingMods(title))
		elif event == '-MODS-' or event == '-TITLE-' or event == '-DESC-':
			window['-EXPORT_SAVE-'].update(tr.getTrans('save'))
			exp = False
		elif event == '-FOLDER-':
			if platform.system() == 'Windows':
				subprocess.run([os.path.join(os.getenv('WINDIR'), 'explorer.exe'), os.path.normpath(se.getSettings('fs_game_data_path') + os.sep + getFolder(title))])
			elif platform.system() == 'Darwin':
				subprocess.run(["/usr/bin/open", os.path.normpath(se.getSettings('fs_game_data_path') + os.sep + getFolder(title))])
		
	window.close()

