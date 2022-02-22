""" main python file

"""
# In Progress
# mac version
# steam version

# FUTURE
# tooltips hinzufügen zu feldern
# pyinstaller
# laden alter spielstände
# teilen sg's
# remove mods chcek if mod is used
# find unused mods
# check ls version at mod import, list only valid versions

# LOW PRIO
# bilder bei mod auswahl

# RELEASE v1.0.0
# anleitung
# translation / beschriftung sauber
# translation deutsch, englisch, französisch
# bei anlegen von datein / Ordnern immmer prüfen ob schon vorhanden

import os
import sys
import subprocess
import time
from dirsync import sync
import psutil
import shutil
import zipfile
import checksumdir
import re
import datetime
import webbrowser
import requests
import xml.etree.ElementTree as ET
import PySimpleGUI as sg
import translation as tr
import settings as se
import game as ga
import import_ls as im
from tinydb import TinyDB, Query
import json
from packaging import version

FSL_Version = 'v1.0.0'

def checkFirstRun():
	""" check if fsl is called first time
	check if savegame1 and / or mods folder where changed after last usage
	"""
	ret = True
	if not os.path.exists(se.settings_json):
		if sg.popup_yes_no('Did you backup your savegames and mods? After succesful setup FSL you can delete your backups.', title = 'Backup', location = (50, 50), icon = 'logo.ico') == 'No':
			sg.popup_ok('Quit FarmingSimulatorLauncher', title = 'Quit', location = (50, 50), icon = 'logo.ico')
			return False
		ret = se.guiSettings('en', True)
		if ret:
			mods_imported = False
			mods_path = se.getSettings('fs_game_data_path') + os.sep + 'mods'
			fs_game_data_path = se.getSettings('fs_game_data_path')
			savegameBackup_path = se.getSettings('fs_game_data_path') + os.sep + 'savegameBackup'
			lang = se.getFslSettings('language')
			try:
				if len(os.listdir(mods_path)) > 0 and ret:
					if sg.popup_yes_no(tr.getTrans('import_mods_init').format(mods_path), title = 'import', location = (50, 50), icon = 'logo.ico') == 'Yes':
						w = sg.Window('', no_titlebar = True, layout = [[sg.Text(tr.getTrans('wait_for_import'))]], finalize = True, location = (50, 50), icon = 'logo.ico')
						im.importAllMods(mods_path, True)
						w.close()
						if sg.popup_yes_no(tr.getTrans('import_more_mods'), title = tr.getTrans('import'), line_width = 100, location = (50, 50), icon = 'logo.ico') == 'Yes':
							im.guiImportMods()
						mods_imported = True
					else:
						sg.popup_ok(tr.getTrans('backup_folder_text').format(mods_path, mods_path), title = tr.getTrans('backup_folders_title'), line_width = 100, location = (50, 50), icon = 'logo.ico')
						os.rename(mods_path, mods_path + '_fsl_bak')
			except FileNotFoundError:
				pass
			except FileExistsError:
				ret = False
				sg.popup_error(mods_path + tr.getTrans('fsl_bak_exists'), location = (50, 50), icon = 'logo.ico')
			
			if ret:
				f = "^savegame[0-99]$"
				for folder in os.listdir(fs_game_data_path):
					if re.search(f, folder):
						if  os.path.exists(fs_game_data_path + os.sep + folder + os.sep + 'careerSavegame.xml'):
							if sg.popup_yes_no(tr.getTrans('import_sg_init').format(folder, fs_game_data_path), title = 'import', location = (50, 50), icon = 'logo.ico') == 'Yes':
								ret = im.guiImportSG(fs_game_data_path + os.sep + folder, True)
								if not ret:
									sg.popup_ok(tr.getTrans('backup_folder_text').format(fs_game_data_path + os.sep + folder, fs_game_data_path + os.sep + folder), title = tr.getTrans('backup_folders_title'), line_width = 100, location = (50, 50), icon = 'logo.ico')
									os.rename(fs_game_data_path + os.sep + folder, fs_game_data_path + os.sep + folder + '_fsl_bak')
									if not os.path.exists(savegameBackup_path + '_fsl_bak'):
										os.makedirs(savegameBackup_path + '_fsl_bak')
									try:
										for backup_file in os.listdir(savegameBackup_path):
											if re.search(folder, backup_file):
												shutil.move(savegameBackup_path + os.sep + backup_file, savegameBackup_path + '_fsl_bak' + os.sep + backup_file)
									except FileNotFoundError:
										pass
									ret = True
							else:
								sg.popup_ok(tr.getTrans('backup_folder_text').format(fs_game_data_path + os.sep + folder, fs_game_data_path + os.sep + folder), title = tr.getTrans('backup_folders_title'), line_width = 100, location = (50, 50), icon = 'logo.ico')
								os.rename(fs_game_data_path + os.sep + folder, fs_game_data_path + os.sep + folder + '_fsl_bak')
								if not os.path.exists(savegameBackup_path + '_fsl_bak'):
									os.makedirs(savegameBackup_path + '_fsl_bak')
								try:
									for backup_file in os.listdir(savegameBackup_path):
										if re.search(folder, backup_file):
											shutil.move(savegameBackup_path + os.sep + backup_file, savegameBackup_path + '_fsl_bak' + os.sep + backup_file)
								except FileNotFoundError:
									pass
#				while True:
#					if sg.popup_yes_no(tr.getTrans('import_more_sg'), title = tr.getTrans('import'), line_width = 100, location = (50, 50), icon = 'logo.ico') == 'Yes':
#						im.guiImportSG()
#					else:
#						break
			try:
				shutil.rmtree(savegameBackup_path)
			except FileNotFoundError:
				pass
		
		if ret == False:
			try:
				sg.popup_ok('Quit FarmingSimulatorLauncher', title = 'Quit', location = (50, 50), icon = 'logo.ico')
				os.remove(se.settings_json)
			except FileNotFoundError:
				pass
	return ret

def checkChanges():
	""" check if game data changed
	check if savegame1 and / or mods folder where changed after last usage
	if so, import is tried or backup if not possible
	"""
	lang = se.getFslSettings('language')
	fs_path = se.getSettings('fs_path')
	fs_game_data_folder = se.getSettings('fs_game_data_path') + os.sep
	all_mods_folder = se.getSettings('all_mods_path') + os.sep
	if os.path.exists(fs_game_data_folder + 'mods'):
		if checksumdir.dirhash(fs_game_data_folder + 'mods') != TinyDB(se.settings_json).get(doc_id = 1)['mods_hash'] :
			all_mods = os.listdir(se.getSettings('all_mods_path'))
			mods = {}
			path = fs_game_data_folder + 'mods'
			for i in os.listdir(path):
				if i.endswith('.zip'):
					with zipfile.ZipFile(path + os.sep + i) as z:
						moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8'))
						version = moddesc.find('version')
						k = 'fsl_' + version.text + '!' + i
				else:
					continue
				found = False
				for j in all_mods:
					if k == j:
						found = True
						break
				if found == False:
					mods[i] = version.text
			for i in mods:
				if sg.popup_yes_no(tr.getTrans('found_new_mod').format(i), location = (50, 50), title = tr.getTrans('new_mod'), icon = 'logo.ico') == 'Yes':
					shutil.copyfile(path + os.sep + i, se.getSettings('all_mods_path') + os.sep + 'fsl_' + version.text + '!' + i)
				else:
					try:
						os.mkdir(fs_game_data_folder + 'mods_fsl_bak')
					except FileExistsError:
						pass
					shutil.copyfile(path + os.sep + i, fs_game_data_folder + 'mods_fsl_bak' + os.sep + i)
		shutil.rmtree(fs_game_data_folder + 'mods')

	if os.path.exists(fs_game_data_folder + 'savegame1'):
		if checksumdir.dirhash(fs_game_data_folder + 'savegame1') != TinyDB(se.settings_json).get(doc_id = 1)['sg_hash']:
			date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
			#TODO auswahl neu, bak, bestehend überschreiben
			layout = [	[sg.Text(tr.getTrans('sg_changed').format(date))],
						[sg.Button(tr.getTrans('new'), size = (14, 1), key = '-NEW-'), sg.Button(tr.getTrans('backup'), size = (14, 1), key = '-BACKUP-'), sg.Button(tr.getTrans('overwrite'), size = (14, 1), key = '-OVERWRITE-'), sg.Button(tr.getTrans('cancel'), size = (14, 1), key = '-CANCEL-')]
					]
			window = sg.Window(tr.getTrans('different'), layout, finalize = True, location = (50, 50), icon = 'logo.ico', disable_close = True)
			while True:
				event, values = window.read()
				if event == '-CANCEL-':
					window.close()
					return False
					break
				elif event == '-NEW-':
					ret = im.guiImportSG(fs_game_data_folder + 'savegame1', True)
					if ret == False:
						window.close()
						return ret
				elif event == '-BACKUP-':
					shutil.copytree(fs_game_data_folder + 'savegame1', fs_game_data_folder + 'savegame1_' + date)
					break
				elif event == '-OVERWRITE-':
					saved = False
					window.Hide()
					layout2 = [ [sg.Text(tr.getTrans('sg_title'))],
								[sg.Combo(getSaveGames(), size = (125,10), key = '-COMBO-', enable_events = True)],
								[sg.Button(tr.getTrans('sg_overwrite'), size = (14, 1), key = '-SAVE-'), sg.Button(tr.getTrans('cancel'), size = (14, 1), key = '-CANCEL-')]
					]
					window2 = sg.Window(tr.getTrans('overwrite'), layout2, finalize = True, location = (50, 50), icon = 'logo.ico', disable_close = True)
					while True:
						event, values = window2.read()
						if event == '-SAVE-':
							n = values['-COMBO-'].split(':')[0].strip()
							if os.path.exists(fs_game_data_folder + n):
								shutil.rmtree(fs_game_data_folder + n)
							shutil.copytree(fs_game_data_folder + 'savegame1', fs_game_data_folder + n)
							saved = True
							break
						elif event == '-CANCEL-':
							break
					window2.close()
					if saved:
						break
					window.UnHide()
			window.close()
		shutil.rmtree(fs_game_data_folder + 'savegame1')

	if os.path.exists(fs_game_data_folder + 'savegameBackup'):
		if checksumdir.dirhash(fs_game_data_folder + 'savegameBackup') != TinyDB(se.settings_json).get(doc_id = 1)['sgb_hash']:
			date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
			sg.popup_ok(tr.getTrans('sgb_changed').format(date), location = (50, 50), icon = 'logo.ico')
			shutil.copytree(fs_game_data_folder + 'savegameBackup', fs_game_data_folder + 'savegameBackup_' + date)
		shutil.rmtree(fs_game_data_folder + 'savegameBackup')
	return True

def getSaveGames():
	""" get stored save games
	read the according games_lsxx.json and extract maps
	"""
	all_mods_folder = se.getSettings('all_mods_path') + os.sep
	q = Query()
	all = TinyDB(se.games_json).all()
	l = ['']
	for i in all:
		n = i['name']
		m = i['map']
		try:
			with zipfile.ZipFile(all_mods_folder + m) as z:
				moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8'))
				m = moddesc.find('maps/map/title/en')
				if m != None:
					l.append(n + ' : ' + m.text)
		except FileNotFoundError:
			if i['map'] == 'fs_internal':
				l.append(n + ' : ' + tr.getTrans('def_map'))
			else:
				sg.popup_error(tr.getTrans('map_not_found').format(m.split('!')[1], m.split('!')[0][4:]), title = tr.getTrans('file_not_found'), location = (50, 50), icon = 'logo.ico')
			pass
	return l

def startSaveGame(name):
	""" start selcted savegame
	link required mods into mods folder
	copy fsl savegame and fsl savgeme backup folder to savegam1 and savegameBackup folder
	start FS
	keep fsl folder in sync
	"""
	fs_game_data_folder = se.getSettings('fs_game_data_path') + os.sep
	all_mods_folder = se.getSettings('all_mods_path') + os.sep
	os.makedirs(fs_game_data_folder + 'mods' + os.sep)
	q = Query()
	sg_map = TinyDB(se.games_json).get((q.name == name))['map']
	if sg_map != 'fs_internal':
		os.link(all_mods_folder + sg_map, fs_game_data_folder + 'mods' + os.sep + sg_map.split('!')[-1])
	mods = TinyDB(se.games_json).get((q.name == name))['mods']
	for i in mods:
		try:
			os.link(all_mods_folder + mods[i], fs_game_data_folder + 'mods' + os.sep + mods[i].split('!')[-1])
		except FileNotFoundError:
			if sg.popup_yes_no(tr.getTrans('mod_not_found').format(mods[i], all_mods_folder), title = tr.getTrans('ssg_title_empty'), location = (50, 50), icon = 'logo.ico') == 'No':
				shutil.rmtree(fs_game_data_folder + 'mods' + os.sep)
				return False
	savegame = TinyDB(se.games_json).get((q.name == name))['name']
	if os.path.exists(fs_game_data_folder + savegame + os.sep + 'careerSavegame.xml'):
		tree = ET.parse(fs_game_data_folder + savegame + os.sep + 'careerSavegame.xml')
		tree.find('settings/savegameName').text = savegame
		with open(fs_game_data_folder + savegame + os.sep + 'careerSavegame.xml', 'wb') as f:
			tree.write(f)
	shutil.copytree(fs_game_data_folder + savegame, fs_game_data_folder + 'savegame1')
	shutil.copytree(fs_game_data_folder + savegame + ' Backup', fs_game_data_folder + 'savegameBackup')
	TinyDB(se.settings_json).update({'last_sg': name, 'sg_hash': '', 'sgb_hash': '', 'mods_hash': checksumdir.dirhash(fs_game_data_folder + 'mods')}, doc_ids = [1])
	fs_path = se.getSettings('fs_path')
	subprocess.run(fs_path, shell = True)
	p_name = (str(fs_path.split('/')[-1].split('.')[0])).lower()
	p_name_child = (str(fs_path.split('/')[-1].split('.')[0]) + 'Game.exe').lower()
	loop = True
	# TODO check if it is necessary to sync, instead of retry copy after ls closed
	while loop:
		time.sleep(3)
		for i in range(3):	# try 3 times to create sync
			try:
				TinyDB(se.settings_json).update({'sg_hash': checksumdir.dirhash(fs_game_data_folder + 'savegame1')}, doc_ids = [1])
				sync(fs_game_data_folder + 'savegame1', fs_game_data_folder + savegame, 'sync')
				TinyDB(se.settings_json).update({'sgb_hash': checksumdir.dirhash(fs_game_data_folder + 'savegameBackup')}, doc_ids = [1])
				sync(fs_game_data_folder + 'savegameBackup', fs_game_data_folder + savegame + ' Backup', 'sync')
				break
			except PermissionError:
				time.sleep(0.5)
				pass
		loop = False
		for p in psutil.process_iter(attrs=['pid', 'name']):
			if p_name_child in (p.info['name']).lower():
				loop = True
				break
	return True

def disableButtons(window):
	window['-START-'].update(disabled = True, button_color = ('gray'))
	window['-CHANGE-'].update(disabled = True)
	window['-REMOVE-'].update(disabled = True)

def main():
	if not se.init():
		sys.exit()

	if not checkFirstRun():
		sys.exit()

	if not checkChanges():
		sg.popup_ok(tr.getTrans('init_failed'), location = (50, 50))
		sys.exit()

	sg.popup_quick_message(tr.getTrans('fsl_init'), auto_close_duration = 5, location = (50, 50), icon = 'logo.ico')

	new_rel = False
	response = requests.get('https://api.github.com/repos/Dueesberch/FarmingSimulatorLauncher/releases/latest').json()
	try:
		if response['tag_name'] > FSL_Version:
			new_rel = True
	except KeyError:
		pass

	button_layout = [	[sg.Button(button_text = tr.getTrans('new'), key='-NEW-', size=(14, 2)),
						sg.Button(button_text = tr.getTrans('import'), key='-IMPORT-', size=(14, 2)),
						sg.Button(button_text = tr.getTrans('change'), key = '-CHANGE-', size = (14, 2), disabled = True),
						sg.Button(button_text = tr.getTrans('remove'), key='-REMOVE-', size=(14, 2), disabled = True),
						sg.Button(button_text = 'Mods', key='-MODS-', size=(14, 2)),
						sg.Button(button_text = tr.getTrans('settings'), key='-SET-', size=(14, 2)),
						sg.Button(button_text = tr.getTrans('exit'), key='-EXIT-', size=(14, 2))
						],
						sg.Button(button_text = tr.getTrans('start'), key = '-START-', size = (111, 2), disabled = True, button_color = 'gray')
					]
	layout = [	[sg.Text(tr.getTrans('sg_title'), key = '-TITLE_T-', size = (111,1))],
				[sg.Combo(getSaveGames(), size = (125,10), key = '-COMBO-', enable_events = True)],
				[sg.Text(tr.getTrans('description'), key = '-DESC_T-', size = (111,1))],
				[sg.Text(size = (111,1), key = '-DESC-')],
				[button_layout],
				[sg.Text(size = (111,1))],
				[sg.Text(size = (111,1))],
				[sg.Button(tr.getTrans('new_release'), key = '-RELEASE-', size = (111, 2), visible = new_rel, button_color = ('black', 'lightgreen'))],
				[sg.Button(tr.getTrans('donate'), key = '-DONATE-', size = (111, 1), button_color = ('black', 'yellow'))]
			]
			
	window = sg.Window('FarmingSimulatorLauncher', layout, finalize = True, location = (50, 50), element_justification = 'c', icon = 'logo.ico')

	while True:
		event, values = window.read()
		#print(event, values)
		if event == sg.WIN_CLOSED or event == '-EXIT-':
			break
		elif event == '-COMBO-' and values['-COMBO-'] != '':
			window['-START-'].update(disabled = False, button_color = ('black', 'green'))
			window['-CHANGE-'].update(disabled = False)
			window['-REMOVE-'].update(disabled = False)
			data = TinyDB(se.games_json).search(Query().name == values['-COMBO-'].split(':')[0].rstrip())
			window['-DESC-'].update(value = data[0]['desc'])
		elif event == '-COMBO-' and values['-COMBO-'] == '':
			disableButtons(window)
			window['-DESC-'].update(value = '')
		elif event == '-START-':
			window.Hide()
			if startSaveGame(values['-COMBO-'].split(':')[0].rstrip()):
				break
			window.UnHide()
		elif event == '-CHANGE-':
			window.Hide()
			ga.guiNewSaveGame(values['-COMBO-'].split(' : ')[0].rstrip())
			window['-COMBO-'].update(value = '', values = getSaveGames())
			disableButtons(window)
			window.UnHide()
		elif event == '-REMOVE-':
			ga.removeSaveGame(values['-COMBO-'])
			window['-COMBO-'].update(value = '', values = getSaveGames())
			disableButtons(window)
		elif event == '-NEW-':
			window.Hide()
			ga.guiNewSaveGame()
			window['-COMBO-'].update(value = '', values = getSaveGames())
			disableButtons(window)
			window.UnHide()
		elif event == '-IMPORT-':
			window.Hide()
			im.guiImportSG()
			window['-COMBO-'].update(value = '', values = getSaveGames())
			disableButtons(window)
			window.UnHide()
		elif event == '-SET-':
			window.Hide()
			se.guiSettings(se.getFslSettings('language'))
			window['-NEW-'].update(tr.getTrans('new'))
			window['-IMPORT-'].update(tr.getTrans('import'))
			window['-CHANGE-'].update(tr.getTrans('change'))
			window['-REMOVE-'].update(tr.getTrans('remove'))
			window['-SET-'].update(tr.getTrans('settings'))
			window['-EXIT-'].update(tr.getTrans('exit'))
			window['-START-'].update(tr.getTrans('start'))
			window['-DESC_T-'].update(tr.getTrans('description'))
			window['-TITLE_T-'].update(tr.getTrans('sg_title'))
			window['-DONATE-'].update(tr.getTrans('donate'))
			window['-RELEASE-'].update(tr.getTrans('new_release'))
			window['-COMBO-'].update(value = '', values = getSaveGames())
			disableButtons(window)
			window.UnHide()
		elif event == '-MODS-':
			window.Hide()
			im.guiImportMods()
			window['-COMBO-'].update(value = '', values = getSaveGames())
			disableButtons(window)
			window.UnHide()
		elif event == '-DONATE-':
			webbrowser.open('https://www.paypal.com/donate/?hosted_button_id=ZR4EGNDAVD4Q4')
		elif event == '-RELEASE-':
			webbrowser.open('https://github.com/Dueesberch/FarmingSimulatorLauncher/releases/latest')
	window.close()

if __name__ == '__main__':
	main()