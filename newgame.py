import zipfile
import os
from pathlib import Path

import PySimpleGUI as sg
from tinydb import TinyDB, Query
import translation as tr
import settings as se

import xml.etree.ElementTree as ET

window_size = (800, 500)
mods = {}
maps = {}

def getMods(l = True):
	global mods
	global maps
	files = os.listdir(se.getSettings('all_mods_path'))
	maps = {} #TODO map nicht als mod zb felsbrunn etc
	mods = {}
	for i in files:
		if i.endswith('.zip'):
			with zipfile.ZipFile(se.getSettings('all_mods_path') + os.sep + i) as z:
				moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8'))
				m = moddesc.find('maps/map/title/en')
				if m != None:
					key = m.text + ' - ' + i.split('!')[0][3:]
					maps[key] = i
				else:
					m = moddesc.find('title/en')
					key = m.text + ' - ' + i.split('!')[0][3:]
					mods[key] = [i]
	if l:
		return list(sorted(maps.keys())), list(sorted(mods.keys()))
	else:
		return maps, mods


def saveSaveGame(values, update):
	global maps
	global mods
	db = TinyDB('games.json')
	if ':' in values['-TITLE-']:
		sg.popup(tr.getTrans('ssg_wrong_char'), title = tr.getTrans('ssg_title_char'))
		return False
	if values['-TITLE-'] == 'savegame1':
		sg.popup(tr.getTrans('ssg_wrong_title'), title = tr.getTrans('ssg_title_title'))
		return False
	if update == -1 and db.get((Query().name == values['-TITLE-'])):
		sg.popup(tr.getTrans('ssg_exists'), title = tr.getTrans('ssg_title'))
		return False
	if values['-TITLE-'] == '':
		sg.popup(tr.getTrans('ssg_name_empty'), title = tr.getTrans('ssg_title_empty'))
		return False
	if values['-MAP-'] == '':
		sg.popup(tr.getTrans('ssg_map_empty'), title = tr.getTrans('ssg_title_empty'))
		return False
	modstoadd = {}
	check = {}
	dupes = []
	for i, val in enumerate(values['-MODS-']):
		check[mods[val][0]] = mods[val][0].split('!')[1]
	seen = set()
	for x in list(check.values()):
		if x in seen:
			dupes.append(x)
		else:
			seen.add(x)
	for j, v in enumerate(dupes):
		for i in check:
			if check[i] == v:
				print('found')
				dupes[j] = i
				break
	if dupes != []:
		f = ''
		for i in dupes:
			with zipfile.ZipFile(se.getSettings('all_mods_path') + os.sep + i) as z:
				moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8'))
				m = moddesc.find('title/en')
				f = f + m.text + '\n'
		sg.popup_ok(tr.getTrans('found_dupes').format(f), title = tr.getTrans('dupes_title'))
		return False
	if update == -1:
		try:
			p = se.getSettings('fs_game_data_path') + os.sep + values['-TITLE-']
			os.mkdir(p)
		except FileExistsError:
			sg.popup(str(se.getSettings('fs_game_data_path') + os.sep) + values['-TITLE-'] + '\n' + tr.getTrans('ssg_folder_exists'), title = tr.getTrans('ssg_title'))
			return False
		try:
			p = se.getSettings('fs_game_data_path') + os.sep + values['-TITLE-'] + ' Backup'
		except FileExistsError:
			sg.popup(str(se.getSettings('fs_game_data_path') + os.sep) + values['-TITLE-'] + '\n' + tr.getTrans('ssg_backup_folder_exists'), title = tr.getTrans('ssg_title'))
			return False

	for i, val in enumerate(values['-MODS-']):
		modstoadd[str(i)] = mods[val][0]

	if update == -1:
		db.insert({"name": values['-TITLE-'], "desc": values['-DESC-'], "map": maps[values['-MAP-']], "mods": modstoadd})
	else:
		data = db.get(doc_id = update)
		if data['name'] != se.getSettings('fs_game_data_path') + os.sep + values['-TITLE-'] and TinyDB('games.json').get((Query().name == values['-TITLE-'])) == None:
			db.update({"name": values['-TITLE-'], "desc": values['-DESC-'], "map": maps[values['-MAP-']], "mods": modstoadd}, doc_ids = [update])
		else:
			sg.popup(tr.getTrans('ssg_exists'), title = tr.getTrans('ssg_title'))
			return False
		if data['name'] != se.getSettings('fs_game_data_path') + os.sep + values['-TITLE-']:
			os.rename(se.getSettings('fs_game_data_path') + os.sep + data['name'], se.getSettings('fs_game_data_path') + os.sep + values['-TITLE-'])
			os.rename(se.getSettings('fs_game_data_path') + os.sep + data['name'] + ' Backup', se.getSettings('fs_game_data_path') + os.sep + values['-TITLE-'] + ' Backup')
	return True

def guiNewSaveGame(title = None):
	global maps
	global mods
	maps_keys, mods_keys = getMods()
	layout = [  [sg.Text(tr.getTrans('sg_title'), size = (window_size[0]-10, 1))],
				[sg.Input(key = '-TITLE-', size = (window_size[0]-10, 1))],
				[sg.Text(tr.getTrans('description'), size = (window_size[0]-10, 1))],
				[sg.Input(key = '-DESC-', size = (window_size[0]-10, 1))],
				[sg.Text('Map')],
				[sg.Combo(maps_keys, key = '-MAP-', size = (window_size[0]-10, 1))],
				[sg.Text('Mods')],
				[sg.Listbox(mods_keys, key = '-MODS-',size = (window_size[0]-10, 15), select_mode = 'extended')],
				[	sg.Button(tr.getTrans('save'), key = '-SAVE-'),
					sg.Button(tr.getTrans('exit'), key = '-EXIT-')
				]
	]
	
	window = sg.Window('Farming Simulator SaveGames', layout, finalize = True, size = window_size, location = (50, 50))
	window['-MODS-'].bind('<FocusIn>', 'click')

	update_sg = -1
	if title != None:
		data = TinyDB('games.json').search((Query().name == title))
		window['-TITLE-'].update(title)
		window['-DESC-'].update(data[0]['desc'])
		for key, val in maps.items():
			if val == data[0]['map']:
				sg_map = key
				break
		window['-MAP-'].update(sg_map)
		selected = []
		for i in data[0]['mods']:
			for key, val in mods.items():
				if val[0] == data[0]['mods'][i]:
					selected.append(key)
					break
		window.Element('-MODS-').SetValue(selected)
		update_sg = TinyDB('games.json').get((Query().name == title)).doc_id

	while True:
		event, values = window.read()
		#print(event, values)
		if event == sg.WIN_CLOSED or event == '-EXIT-':
			break
		elif event == '-SAVE-':
			if saveSaveGame(values, update_sg):
				break
		elif event == '-MODS-click':
			#handlePicture(values['-MODS-'])
			window['-SAVE-'].SetFocus(True)
		
	window.close()

