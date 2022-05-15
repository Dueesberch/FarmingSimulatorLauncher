""" main python file

"""

import os
import sys
import subprocess
import time
import logging as log
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
import hashlib
import pathlib

FSL_Version = 'v1.1.3'

logger = None
def checkFirstRun():
	""" check if fsl is called first time
	check if savegame1 and / or mods folder where changed after last usage
	"""
	ret = True
	#logger.debug('main:checkFirstRun:check if first run')
	if not os.path.exists(se.settings_json):
		if sg.popup_yes_no('Did you backup your savegames and mods? After successful setup FSL you can delete your backups.', title = 'Backup', location = (50, 50)) == 'No':
			sg.popup_ok('Quit FarmingSimulatorLauncher', title = 'Quit', location = (50, 50))
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
					if sg.popup_yes_no(tr.getTrans('import_mods_init').format(mods_path), title = 'import', location = (50, 50)) == 'Yes':
						#logger.debug('fsl:checkFirstRun: mods folder found > go to import')
						w = sg.Window('', no_titlebar = True, layout = [[sg.Text(tr.getTrans('wait_for_import'))]], finalize = True, location = (50, 50))
						im.importAllMods(mods_path, True)
						w.close()
						if sg.popup_yes_no(tr.getTrans('import_more_mods'), title = tr.getTrans('import'), line_width = 100, location = (50, 50)) == 'Yes':
							#logger.debug('fsl:checkFirstRun: import from additional mods folder')
							im.guiImportMods(False)
						mods_imported = True
					else:
						#logger.debug('fsl:checkFirstRun: mods folder found > go to backup')
						sg.popup_ok(tr.getTrans('backup_folder_text').format(mods_path, mods_path), title = tr.getTrans('backup_folders_title'), line_width = 100, location = (50, 50))
						os.rename(mods_path, mods_path + '_fsl_bak')
#				else:
#					logger.debug('fsl:checkFirstRun: NO mods folder found')
			except FileNotFoundError:
				pass
			except FileExistsError:
				ret = False
				#logger.debug('fsl:checkFirstRun: mods_fsl_backup already exists')
				sg.popup_error(mods_path + tr.getTrans('fsl_bak_exists'), location = (50, 50))
			
			if ret:
				f = "^savegame[0-99]$"
				for folder in os.listdir(fs_game_data_path):
					if re.search(f, folder):
						if  os.path.exists(fs_game_data_path + os.sep + folder + os.sep + 'careerSavegame.xml'):
							if sg.popup_yes_no(tr.getTrans('import_sg_init').format(folder, fs_game_data_path), title = 'import', location = (50, 50)) == 'Yes':
								#logger.debug('fsl:checkFirstRun: valid savegame folder ' + folder + ' found > go to import')
								ret = im.guiImportSG(fs_game_data_path + os.sep + folder, True)
								if not ret:
									#logger.debug('fsl:checkFirstRun: import canceled')
									sg.popup_ok(tr.getTrans('backup_folder_text').format(fs_game_data_path + os.sep + folder, fs_game_data_path + os.sep + folder), title = tr.getTrans('backup_folders_title'), line_width = 100, location = (50, 50))
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
								#logger.debug('fsl:checkFirstRun: valid savegame folder ' + folder + ' found > go to backup')
								sg.popup_ok(tr.getTrans('backup_folder_text').format(fs_game_data_path + os.sep + folder, fs_game_data_path + os.sep + folder), title = tr.getTrans('backup_folders_title'), line_width = 100, location = (50, 50))
								os.rename(fs_game_data_path + os.sep + folder, fs_game_data_path + os.sep + folder + '_fsl_bak')
								if not os.path.exists(savegameBackup_path + '_fsl_bak'):
									os.makedirs(savegameBackup_path + '_fsl_bak')
								try:
									for backup_file in os.listdir(savegameBackup_path):
										if re.search(folder, backup_file):
											shutil.move(savegameBackup_path + os.sep + backup_file, savegameBackup_path + '_fsl_bak' + os.sep + backup_file)
								except FileNotFoundError:
									pass
			try:
				shutil.rmtree(savegameBackup_path)
			except FileNotFoundError:
				pass
		
		if ret == False:
			try:
				#logger.debug('fsl:checkFirstRun: firstRun failed > quit FSL')
				sg.popup_ok('Quit FarmingSimulatorLauncher', title = 'Quit', location = (50, 50))
				os.remove(se.settings_json)
			except FileNotFoundError:
				pass
	return ret

def validateModsFolder(fs_game_data_folder):
	if checksumdir.dirhash(fs_game_data_folder + 'mods') != TinyDB(se.settings_json).get(doc_id = 1)['mods_hash'] and TinyDB(se.settings_json).get(doc_id = 1)['mods_hash'] != '':
		#logger.debug('fsl:checkChanges:mods folder changed')
		mods = {}
		db = TinyDB(se.getSettings('all_mods_path') + os.sep + 'mods_db.json')
		#logger.debug('fsl:checkChanges:existing mods ' + str(all_mods))
		path = fs_game_data_folder + 'mods'
		for i in os.listdir(path):
			if i.endswith('.zip') and not os.path.islink(fs_game_data_folder + 'mods' + os.sep + i):
				with zipfile.ZipFile(path + os.sep + i) as z:
					try:
						moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8').strip())
					except ET.ParseError:
						sg.popup_error(tr.getTrans('import_failed').format(i), title=tr.getTrans('error'), location = (50, 50))
						try:
							os.mkdir(fs_game_data_folder + 'mods_fsl_bak')
						except FileExistsError:
							pass
						shutil.copyfile(path + os.sep + i, fs_game_data_folder + 'mods_fsl_bak' + os.sep + i)
						sg.popup_ok(tr.getTrans('moved').format(fs_game_data_folder + 'mods_fsl_bak'), title = tr.getTrans('error'), location = (50, 50))
						continue
					version = moddesc.find('version')
					for l in se.langs:
						name = moddesc.find('title/' + l)
						#lang = l
						if name != None:
							break
					d = db.get(Query().name == name.text)
					if d == None or not hashlib.md5(pathlib.Path(path + os.sep + i).read_bytes()).hexdigest() in d['files'].values():
						#logger.debug('fsl:checkChanges:changed / new mod ' + i + ' ' + version.text + ' ' + k)
						mods[i] = version.text
			else:
				continue
		for i in mods:
			if sg.popup_yes_no(tr.getTrans('found_new_mod').format(i), location = (50, 50), title = tr.getTrans('new_mod')) == 'Yes':
				#logger.debug('fsl:checkChanges:import mod ' + i + ' ' + mods[i])
				im.importMods(path, [i], True)
			else:
				try:
					os.mkdir(fs_game_data_folder + 'mods_fsl_bak')
				except FileExistsError:
					pass
				shutil.copyfile(path + os.sep + i, fs_game_data_folder + 'mods_fsl_bak' + os.sep + i)

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
		validateModsFolder(fs_game_data_folder)
		shutil.rmtree(fs_game_data_folder + 'mods')

	if os.path.exists(fs_game_data_folder + 'savegame1'):
		if checksumdir.dirhash(fs_game_data_folder + 'savegame1') != TinyDB(se.settings_json).get(doc_id = 1)['sg_hash'] and TinyDB(se.settings_json).get(doc_id = 1)['sg_hash'] != '':
			#logger.debug('fsl:checkChanges:savegame folder changed')
			date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
			layout = [	[sg.Text(tr.getTrans('sg_changed').format(date))],
						[	sg.Button(tr.getTrans('new'), size = (14, 1), key = '-NEW-'),
							sg.Button(tr.getTrans('backup'), size = (14, 1), key = '-BACKUP-'), 
							sg.Button(tr.getTrans('overwrite'), size = (14, 1), key = '-OVERWRITE-'), 
							sg.Button(tr.getTrans('remove'), size = (14, 1), key = '-REMOVE-'), 
							sg.Button(tr.getTrans('cancel'), size = (14, 1), key = '-CANCEL-')]
					]
			window = sg.Window(tr.getTrans('different'), layout, finalize = True, location = (50, 50), disable_close = True)
			while True:
				event, values = window.read()
				if event == '-CANCEL-':
					window.close()
					return False
					break
				elif event == '-NEW-':
					ret = im.guiImportSG(fs_game_data_folder + 'savegame1', True)
					#logger.debug('fsl:checkChanges:add savegame as new ' + str(ret))
					if ret == False:
						window.close()
						return ret
				elif event == '-BACKUP-':
					#logger.debug('fsl:checkChanges:backup savegame')
					shutil.copytree(fs_game_data_folder + 'savegame1', fs_game_data_folder + 'savegame1_' + date)
					if os.path.exists(fs_game_data_folder + 'savegameBackup'):
						if checksumdir.dirhash(fs_game_data_folder + 'savegameBackup') != TinyDB(se.settings_json).get(doc_id = 1)['sgb_hash'] and TinyDB(se.settings_json).get(doc_id = 1)['sgb_hash'] != '':
							#logger.debug('fsl:checkChanges:savegame Backup changed')
							shutil.copytree(fs_game_data_folder + 'savegameBackup', fs_game_data_folder + 'savegameBackup_' + date)
						shutil.rmtree(fs_game_data_folder + 'savegameBackup')
					break
				elif event == '-OVERWRITE-':
					#logger.debug('fsl:checkChanges:overwrite existing savegame')
					saved = False
					window.Hide()
					layout2 = [ [sg.Text(tr.getTrans('sg_title'))],
								[sg.Combo(getSaveGames(), size = (125,10), key = '-COMBO-', enable_events = True)],
								[sg.Button(tr.getTrans('sg_overwrite'), size = (14, 1), key = '-SAVE-'), sg.Button(tr.getTrans('cancel'), size = (14, 1), key = '-CANCEL-')]
					]
					window2 = sg.Window(tr.getTrans('overwrite'), layout2, finalize = True, location = (50, 50), disable_close = True)
					while True:
						event, values = window2.read()
						if event == '-SAVE-':
							n = values['-COMBO-'].split(':')[0].strip()
							if os.path.exists(fs_game_data_folder + n):
								shutil.rmtree(fs_game_data_folder + n)
							shutil.copytree(fs_game_data_folder + 'savegame1', fs_game_data_folder + n)
							if os.path.exists(fs_game_data_folder + 'savegameBackup'):
								if checksumdir.dirhash(fs_game_data_folder + 'savegameBackup') != TinyDB(se.settings_json).get(doc_id = 1)['sgb_hash'] and TinyDB(se.settings_json).get(doc_id = 1)['sgb_hash'] != '':
									#logger.debug('fsl:checkChanges:savegame Backup changed')
									old = set(os.listdir(fs_game_data_folder + n + '_Backup'))
									changed = set(os.listdir(fs_game_data_folder + 'savegameBackup'))
									new = (changed.difference(old))
									for i in new:
										shutil.copytree(fs_game_data_folder + 'savegameBackup' + os.sep + i, fs_game_data_folder + n + '_Backup' + os.sep + i)
									shutil.move(fs_game_data_folder + 'savegameBackup' + os.sep + 'savegame1_backupLatest.txt', fs_game_data_folder + n + '_Backup' + os.sep + 'savegame1_backupLatest.txt')
							saved = True
							break
						elif event == '-CANCEL-':
							break
					window2.close()
					if saved:
						break
					window.UnHide()
				elif event == '-REMOVE-':
					break
			window.close()
	if os.path.exists(fs_game_data_folder + 'savegameBackup'):
		shutil.rmtree(fs_game_data_folder + 'savegameBackup')
	if os.path.exists(fs_game_data_folder + 'savegame1'):
		shutil.rmtree(fs_game_data_folder + 'savegame1')

	data = TinyDB(se.games_json).all()
	for i in data:
		try:
			path = i['imported']['path']
			hash_n = hashlib.md5(pathlib.Path(path).read_bytes()).hexdigest()
			if os.path.exists(path) and hash_n != i['imported']['hash']:
				if sg.popup_yes_no(tr.getTrans('import_sgc_init').format(i['name'], path), title = 'import', location = (50, 50)) == 'Yes':
					im.importSGC(path, i['name'])
		except KeyError:
			pass
	return True

def getSaveGames():
	""" get stored save games
	read the according games_lsxx.json and extract maps
	"""
	all_mods_folder = se.getSettings('all_mods_path') + os.sep
	q = Query()
	all = TinyDB(se.games_json).all()
	l = ['']
	for game in all:
		if game['map'] not in se.getInternalMaps().values():
			try:
				with zipfile.ZipFile(all_mods_folder + game['map']) as z:
					moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8').strip())
					t = moddesc.find('maps/map/title/' + se.getFslSettings('language'))
					if t == None:
						d = TinyDB(all_mods_folder + os.sep + 'mods_db.json').search(Query().mod_type == 'map')
						for m in d:
							if game['map'] in m['files']:
								t = m['name']
					else:
						t = t.text
					l.append(game['name'] + ' : ' + t)
			except FileNotFoundError:
				l.append(game['name'] + ' : ' + tr.getTrans('ghostmap'))
				pass
		else:
			l.append(game['name'] + ' : ' + list(se.getInternalMaps().keys())[list(se.getInternalMaps().values()).index(game['map'])])
	return l

def startSaveGame(name):
	""" start selected savegame
	link required mods into mods folder
	copy fsl savegame and fsl savegame backup folder to savegam1 and savegameBackup folder
	start FS
	keep fsl folder in sync
	"""
	fs_game_data_folder = se.getSettings('fs_game_data_path') + os.sep
	all_mods_folder = se.getSettings('all_mods_path') + os.sep
	os.makedirs(fs_game_data_folder + 'mods' + os.sep)
	q = Query()
	sg_map = TinyDB(se.games_json).get((q.name == name))['map']
	xml_map = None
	if sg_map not in se.getInternalMaps().values():
		os.symlink(all_mods_folder + sg_map, fs_game_data_folder + 'mods' + os.sep + sg_map.split('!')[-1])
		with zipfile.ZipFile(all_mods_folder + sg_map) as z:
				moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8').strip())
				v = moddesc.find('version').text
				try:
					t = moddesc.find('maps/map/title/' + se.getFslSettings('language')).text
				except AttributeError:
					print('error')
					d = TinyDB(all_mods_folder + os.sep + 'mods_db.json').search(Query().mod_type == 'map')
					for map in d:
						if sg_map in map['files']:
							t = map['name']
					pass
		# change careersavegame.xml mod list
		xml_map = ET.Element('mod', modName = sg_map.split('!')[-1].replace('.zip', ''), title = t, version = v, required="true", fileHash="0")
	mods = TinyDB(se.games_json).get((q.name == name))['mods']
	xml_mods = []
	for i in mods:
		if os.path.exists(all_mods_folder + mods[i]):
			os.symlink(all_mods_folder + mods[i], fs_game_data_folder + 'mods' + os.sep + mods[i].split('!')[-1])
			with zipfile.ZipFile(all_mods_folder + mods[i]) as z:
				moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8').strip())
				v = moddesc.find('version').text
				try:
					t = moddesc.find('title/' + se.getFslSettings('language')).text
				except AttributeError:
					d = TinyDB(all_mods_folder + os.sep + 'mods_db.json').all()
					for mod in d:
						if mods[i] in mod['files']:
							t = mod['name']
					pass
			# change careersavegame.xml mod list
			xml_mods.append(ET.Element('mod', modName = mods[i].split('!')[-1].replace('.zip', ''), title = t, version = v, required = "false", fileHash = '0'))
		elif mods[i].endswith('.dlc'):
			xml_mods.append(ET.Element('mod', modName = 'pdlc_' + mods[i].replace('.dlc', ''), title = '', version = '', required = "false", fileHash = '0'))
		else:
			if sg.popup_yes_no(tr.getTrans('mod_not_found').format(mods[i], all_mods_folder), title = tr.getTrans('ssg_title_empty'), location = (50, 50)) == 'No':
				shutil.rmtree(fs_game_data_folder + 'mods' + os.sep)
				return False
	savegame = TinyDB(se.games_json).get((q.name == name))['folder']
	if os.path.exists(fs_game_data_folder + savegame + os.sep + 'careerSavegame.xml'):
		tree = ET.parse(fs_game_data_folder + savegame + os.sep + 'careerSavegame.xml')
		tree.find('settings/savegameName').text = name
		xml_mods_old = tree.findall('mod')
		for i in xml_mods_old:
			tree.getroot().remove(i)
		if xml_map != None:
			tree.getroot().append(xml_map)
		for i in xml_mods:
			tree.getroot().append(i)
		with open(fs_game_data_folder + savegame + os.sep + 'careerSavegame.xml', 'wb') as f:
			tree.write(f)
	shutil.copytree(fs_game_data_folder + savegame, fs_game_data_folder + 'savegame1')
	shutil.copytree(fs_game_data_folder + savegame + '_Backup', fs_game_data_folder + 'savegameBackup')
	TinyDB(se.settings_json).update({'last_sg': name, 'sg_hash': '', 'sgb_hash': '', 'mods_hash': checksumdir.dirhash(fs_game_data_folder + 'mods')}, doc_ids = [1])
	skipStartVideos  = ''
	direct = ''
	if se.getSettings('intro') == 'skip':
		skipStartVideos  = ' -skipStartVideos'
	if TinyDB(se.games_json).get((q.name == name))['mode'] == "sp" and TinyDB(se.games_json).get((q.name == name))['direct_start'] == "yes":
		direct = ' -autoStartSavegameId 1'
	fs_path = "\"" + os.path.normpath(se.getSettings('fs_path')) + "\"" + skipStartVideos  + direct
	subprocess.call(fs_path, shell = True)
	p_name = (str(fs_path.split('\\')[-1].split('.')[0])).lower()
	loop = True
	steam_check = True
	while loop:
		time.sleep(3)
		for i in range(3):	# try 3 times to sync
			try:
				TinyDB(se.settings_json).update({'sg_hash': checksumdir.dirhash(fs_game_data_folder + 'savegame1')}, doc_ids = [1])
				sync(fs_game_data_folder + 'savegame1', fs_game_data_folder + savegame, 'sync')
				TinyDB(se.settings_json).update({'sgb_hash': checksumdir.dirhash(fs_game_data_folder + 'savegameBackup')}, doc_ids = [1])
				sync(fs_game_data_folder + 'savegameBackup', fs_game_data_folder + savegame + '_Backup', 'sync')
				break
			except PermissionError:
				time.sleep(0.5)
				pass
			except TypeError:
				time.sleep(0.5)
				pass
			except FileNotFoundError:
				time.sleep(0.5)
				pass
		loop = False
		for p in psutil.process_iter(attrs=['name']):
			if p_name in (p.info['name']).lower():
				loop = True
				steam_check = False
				break
			if 'steam' in (p.info['name']).lower() and steam_check:
				loop = True
	validateModsFolder(fs_game_data_folder)
	return True

def disableButtons(window):
	window['-START-'].update(disabled = True, button_color = ('gray'))
	window['-CHANGE-'].update(disabled = True)
	window['-REMOVE-'].update(disabled = True)
	window['-NEW-'].update(tr.getTrans('new'))

def main():
	#print('rename folder')
	#sys.exit()
	global logger
	#logger = log.getLogger('fsl')
	#logger.setLevel(log.INFO)
	#handler = log.FileHandler('log.txt', mode = 'w')
	#logger.addHandler(handler)
	#logger.debug('fsl:main: FSL version ' + FSL_Version)
	try:
		import pyi_splash
		pyi_splash.update_text('UI Loaded ...')
		pyi_splash.close()
	except:
		pass
	if not se.init():
		sys.exit()

	if not checkFirstRun():
		sys.exit()

	if not checkChanges():
		sg.popup_ok(tr.getTrans('init_failed'), location = (50, 50))
		sys.exit()

	sg.popup_quick_message(tr.getTrans('fsl_init'), auto_close_duration = 5, location = (50, 50))

	new_rel = False
	try:
		response = requests.get('https://api.github.com/repos/Dueesberch/FarmingSimulatorLauncher/releases/latest').json()
		if response['tag_name'] > FSL_Version:
			new_rel = True
	except Exception as e:
		pass

	button_layout = [	[sg.Button(button_text = tr.getTrans('new'), key='-NEW-', size=(14, 1)),
						sg.Button(button_text = tr.getTrans('import'), key='-IMPORT-', size=(14, 1)),
						sg.Button(button_text = tr.getTrans('change'), key = '-CHANGE-', size = (14, 1), disabled = True),
						sg.Button(button_text = tr.getTrans('remove'), key='-REMOVE-', size=(14, 1), disabled = True),
						sg.Button(button_text = 'Mods', key='-MODS-', size=(14, 1)),
						sg.Button(button_text = tr.getTrans('settings'), key='-SET-', size=(14, 1)),
						sg.Button(button_text = tr.getTrans('exit'), key='-EXIT-', size=(14, 1))
						],
						sg.Button(button_text = tr.getTrans('start'), key = '-START-', size = (111, 1), disabled = True, button_color = 'gray')
					]
	layout = [	[sg.Text(tr.getTrans('sg_title'), key = '-TITLE_T-', size = (111,1))],
				[sg.Combo(getSaveGames(), size = (125,10), key = '-COMBO-', enable_events = True)],
				[sg.Text(tr.getTrans('description'), key = '-DESC_T-', size = (111,1))],
				[sg.Text(size = (111,1), key = '-DESC-')],
				[button_layout],
				[sg.Text(size = (111,1))],
				[sg.Text(size = (111,1))],
				[sg.Button(tr.getTrans('new_release'), key = '-RELEASE-', size = (111, 1), visible = new_rel, button_color = ('black', 'lightgreen'))],
				[sg.Button(tr.getTrans('donate'), key = '-DONATE-', size = (111, 1), button_color = ('black', 'yellow'))]
			]
			
	window = sg.Window('FarmingSimulatorLauncher', layout, finalize = True, location = (50, 50), element_justification = 'c')

	while True:
		event, values = window.read()
		#print(event, values)
		if event == sg.WIN_CLOSED or event == '-EXIT-':
			break
		elif event == '-COMBO-' and values['-COMBO-'] != '':
			if values['-COMBO-'].split(':')[1].lstrip() != tr.getTrans('ghostmap'):
				window['-START-'].update(disabled = False, button_color = ('black', 'green'))
			window['-CHANGE-'].update(disabled = False)
			window['-REMOVE-'].update(disabled = False)
			data = TinyDB(se.games_json).search(Query().name == values['-COMBO-'].split(':')[0].rstrip())
			window['-DESC-'].update(value = data[0]['desc'])
			window['-NEW-'].update(tr.getTrans('copy'))
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
			window['-DESC-'].update(value = '')
			disableButtons(window)
			window.UnHide()
		elif event == '-REMOVE-':
			ga.removeSaveGame(values['-COMBO-'])
			window['-COMBO-'].update(value = '', values = getSaveGames())
			window['-DESC-'].update(value = '')
			disableButtons(window)
		elif event == '-NEW-':
			if values['-COMBO-'] != '':
				ga.copySG(values['-COMBO-'])
			else:
				ga.guiNewSaveGame()
			window.Hide()
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
