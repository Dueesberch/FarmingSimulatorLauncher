""" 
	main python file
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
from BetterJSONStorage import BetterJSONStorage
import json
from packaging import version
import hashlib
import pathlib
import datetime
import pathlib
import blosc2

FSL_Version = 'v1.1.4'

logger = None
def checkFirstRun():
	""" check if fsl is called first time
	check if savegame1 and / or mods folder where changed after last usage
	"""
	ret = True
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
				if len(os.listdir(mods_path)) > 0:
					if sg.popup_yes_no(tr.getTrans('import_mods_init').format(mods_path), title = 'import', location = (50, 50)) == 'Yes':
						w = sg.Window('', no_titlebar = True, layout = [[sg.Text(tr.getTrans('wait_for_import'))]], finalize = True, location = (50, 50))
						im.importAllMods(mods_path, True)
						w.close()
						if sg.popup_yes_no(tr.getTrans('import_more_mods'), title = tr.getTrans('import'), line_width = 100, location = (50, 50)) == 'Yes':
							im.guiImportMods(False)
						mods_imported = True
					else:
						sg.popup_ok(tr.getTrans('backup_folder_text').format(mods_path, mods_path), title = tr.getTrans('backup_folders_title'), line_width = 100, location = (50, 50))
						os.rename(mods_path, mods_path + '_fsl_bak')
			except FileNotFoundError:
				im.createEmptyModsFolder()
				pass
			except FileExistsError:
				ret = False
				sg.popup_error(mods_path + tr.getTrans('fsl_bak_exists'), location = (50, 50))
			
			if ret:
				f = "^savegame[0-99]$"
				for folder in os.listdir(fs_game_data_path):
					if re.search(f, folder):
						if  os.path.exists(fs_game_data_path + os.sep + folder + os.sep + 'careerSavegame.xml'):
							if sg.popup_yes_no(tr.getTrans('import_sg_init').format(folder, fs_game_data_path), title = 'import', location = (50, 50)) == 'Yes':
								ret = im.guiImportSG(fs_game_data_path + os.sep + folder, True)
								if not ret:
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
				sg.popup_ok('Quit FarmingSimulatorLauncher', title = 'Quit', location = (50, 50))
				os.remove(se.settings_json)
			except FileNotFoundError:
				pass
	return ret

def validateModsFolder(fs_game_data_folder):
	mods_hash = se.getSettings('mods_hash')
	if checksumdir.dirhash(fs_game_data_folder + 'mods') != mods_hash and mods_hash != '':
		mods = {}
		path = fs_game_data_folder + 'mods'
		if not os.path.exists(path):
			return
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
					
					l = se.getFslSettings('language')
					name = moddesc.find('title/de')

					for l in se.langs:
						name = moddesc.find('title/' + l)
						if name != None:
							break
					with TinyDB(pathlib.Path(se.getSettings('all_mods_path') + os.sep + 'mods_db.json')) as db_mods:
						d = db_mods.get(Query().name == name.text)
						hashes =  []
					if d != None:
						for h_idx in d['files'].values():
							hashes.append(h_idx[0])
					if d == None or not hashlib.md5(pathlib.Path(path + os.sep + i).read_bytes()).hexdigest() in hashes: # TODO [0] geht nicht
						mods[i] = version.text
			else:
				continue
		for i in mods:
			if sg.popup_yes_no(tr.getTrans('found_new_mod').format(i), location = (50, 50), title = tr.getTrans('new_mod')) == 'Yes':
				im.importMods(path, [i], True, True)
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
		sg_hash = se.getSettings('sg_hash')
		if checksumdir.dirhash(fs_game_data_folder + 'savegame1') != sg_hash and sg_hash != '':
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
					if ret == False:
						window.close()
						return ret
				elif event == '-BACKUP-':
					shutil.copytree(fs_game_data_folder + 'savegame1', fs_game_data_folder + 'savegame1_' + date)
					if os.path.exists(fs_game_data_folder + 'savegameBackup'):
						sgb_hash = se.getSettings('sgb_hash')
						if checksumdir.dirhash(fs_game_data_folder + 'savegameBackup') != sgb_hash and sgb_hash != '':
							shutil.copytree(fs_game_data_folder + 'savegameBackup', fs_game_data_folder + 'savegameBackup_' + date)
						shutil.rmtree(fs_game_data_folder + 'savegameBackup')
					break
				elif event == '-OVERWRITE-':
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
							n = hashlib.md5(values['-COMBO-'].split(':')[0].strip().encode()).hexdigest()
							if os.path.exists(fs_game_data_folder + n):
								shutil.rmtree(fs_game_data_folder + n)
							shutil.copytree(fs_game_data_folder + 'savegame1', fs_game_data_folder + n)
							if os.path.exists(fs_game_data_folder + 'savegameBackup'):
								sgb_hash = se.getSettings('sgb_hash')
								if checksumdir.dirhash(fs_game_data_folder + 'savegameBackup') != se.sgb_hash and sgb_hash != '':
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
		try:
			shutil.rmtree(fs_game_data_folder + 'savegame1')
		except PermissionError:
			pass

	with TinyDB(pathlib.Path(se.games_json), access_mode = "r+") as db_games:
		all_games = db_games.all()
	for i in all_games:
		try:
			path = i['imported']['path']
			hash_n = hashlib.md5(pathlib.Path(path).read_bytes()).hexdigest()
			if os.path.exists(path) and hash_n != i['imported']['hash']:
				if sg.popup_yes_no(tr.getTrans('import_sgc_init').format(i['name'], path), title = 'Import', location = (50, 50)) == 'Yes':
					im.importSGC(path, i['name'])
		except KeyError:
			pass
		except FileNotFoundError:
			pass
	return True

def error_mods_db():
	all_mods_folder = se.getSettings('all_mods_path') + os.sep
	sg.popup_ok(tr.getTrans('mods_db_broken'), title = 'DB broken', location = (50, 50))
	os.remove(all_mods_folder + os.sep + 'mods_db.json')
	os.startfile(sys.argv[0])
	sys.exit()

def getSaveGames():
	""" get stored save games
	read the according games_lsxx.json and extract maps
	"""
	all_mods_folder = se.getSettings('all_mods_path') + os.sep
	q = Query()
	l = ['']
	with TinyDB(pathlib.Path(se.games_json)) as db_games:
		for game in db_games.all():
			if game['map'] not in se.getInternalMaps().values():
				try:
					with zipfile.ZipFile(all_mods_folder + game['map']) as z:
						moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8').strip())
						t = moddesc.find('maps/map/title/' + se.getFslSettings('language'))
						if t == None:
							try:
								with open(all_mods_folder + os.sep + 'mods_db.json', 'rb') as f:
									json.loads(f.read().decode())
								with TinyDB(pathlib.Path(se.getSettings('all_mods_path') + os.sep + 'mods_db.json')) as db_mods:
									for m in db_mods.search(Query().mod_type == 'map'):
										if game['map'] in m['files']:
											t = m['name']
							except json.decoder.JSONDecodeError:
								f.close()
								error_mods_db()
								pass
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
	with TinyDB(pathlib.Path(se.games_json)) as db_games:
		sg_map = db_games.get((q.name == name))['map']
		mods = db_games.get((q.name == name))['mods']
		savegame = db_games.get((q.name == name))['folder']
	xml_map = None
	if sg_map not in se.getInternalMaps().values():
		os.symlink(all_mods_folder + sg_map, fs_game_data_folder + 'mods' + os.sep + sg_map.split('!')[-1])
		with zipfile.ZipFile(all_mods_folder + sg_map) as z:
				moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8').strip())
				v = moddesc.find('version').text
				try:
					t = moddesc.find('maps/map/title/' + se.getFslSettings('language')).text
				except AttributeError:
					with TinyDB(pathlib.Path(se.getSettings('all_mods_path') + os.sep + 'mods_db.json')) as db_mods:
						for map in db_mods.search(Query().mod_type == 'map'):
							if sg_map in map['files']:
								t = map['name']
					pass
		# change careersavegame.xml mod list
		xml_map = ET.Element('mod', modName = sg_map.split('!')[-1].replace('.zip', ''), title = t, version = v, required="true", fileHash="0")

	
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
					with TinyDB(pathlib.Path(se.getSettings('all_mods_path') + os.sep + 'mods_db.json')) as db_mods:
						for mod in db_mods.all():
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
			tree.write(f, xml_declaration = True, encoding = "UTF-8")
	shutil.copytree(fs_game_data_folder + savegame, fs_game_data_folder + 'savegame1')
	shutil.copytree(fs_game_data_folder + savegame + '_Backup', fs_game_data_folder + 'savegameBackup')
	se.updateSettings({'last_sg': name, 'sg_hash': '', 'sgb_hash': '', 'mods_hash': checksumdir.dirhash(fs_game_data_folder + 'mods')})
	skipStartVideos  = ''
	direct = ''
	if se.getSettings('intro') == 'skip':
		skipStartVideos  = ' -skipStartVideos'
	fs_path = "\"" + os.path.normpath(se.getSettings('fs_path')) + "\"" + skipStartVideos  + direct
	subprocess.call(fs_path, shell = True)
	p_name = (str(fs_path.split('\\')[-1].split('.')[0])).lower()
	loop = True
	steam_check = True
	while loop:
		time.sleep(3)
		for i in range(3):	# try 3 times to sync
			try:
				se.updateSettings({'sg_hash': checksumdir.dirhash(fs_game_data_folder + 'savegame1')})
				sync(fs_game_data_folder + 'savegame1', fs_game_data_folder + savegame, 'sync')
				se.updateSettings({'sgb_hash': checksumdir.dirhash(fs_game_data_folder + 'savegameBackup')})
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
	window['-BACKUPS-'].update(visible = False)
	window['-T_BACKUPS-'].update(visible = False)

def getBackups(title):
	bak_folder = ga.get_sg_by_title(title)['folder'] + '_Backup'
	backups = sorted(os.listdir(se.getSettings('fs_game_data_path') + os.sep + bak_folder))
	c = se.getSettings('backups')
	if c > 0:
		to_rem = len(backups) - c - 1
		backups = backups[:to_rem]
		# cleanup backupfolder
		for i in backups:
			shutil.rmtree(se.getSettings('fs_game_data_path') + os.sep + bak_folder + os.sep + i)
	backups = []
	for i in os.listdir(se.getSettings('fs_game_data_path') + os.sep + bak_folder):
		if os.path.isdir(se.getSettings('fs_game_data_path') + os.sep + bak_folder + os.sep + i):
			date = i.split('backup')[1].split('_')[0]
			time = i.split('backup')[1].split('_')[1].replace('-', ':')
			backups.append(date + ' ' + time)
	backups = sorted(backups, reverse = True)
	backups.insert(0, '')
	return backups

def setBackupAsCurrent(title, backup):
	folder = ga.get_sg_by_title(title)['folder']
	# check if mods available
	src_path = se.getSettings('fs_game_data_path') + os.sep + folder + '_Backup' + os.sep + 'savegame1_backup' + backup.split(' ')[0] + '_' + backup.split(' ')[1].replace(':', '-')
	tree = ET.parse(src_path + os.sep + 'careerSavegame.xml')
	xml_mods_old = tree.findall('mod')
	mods = {}
	for n, i in enumerate(xml_mods_old):
		name = i.attrib['modName']
		if name.startswith('pdlc'):
			continue
		vers = i.attrib['version']
		f_name = 'fsl_' + vers + '!' + name + '.zip'
		if f_name != data[0]['map']:
			mods[n] = f_name
		#if not os.path.exists(se.getSettings('all_mods_path') + os.sep + f_name) and sg.popup_yes_no(tr.getTrans('mod_not_found').format(f_name, se.getSettings('all_mods_path')), title = tr.getTrans('ssg_title_empty'), location = (50, 50)) == 'No':
		#	return False
	# backup current
	date = datetime.datetime.now()
	date_str = date.strftime('%Y') + '-' + date.strftime('%m') + '-' + date.strftime('%d') + '_' + date.strftime('%H') + '-' + date.strftime('%M')
	dst_path = se.getSettings('fs_game_data_path') + os.sep + folder + '_Backup' + os.sep + 'savegame1_backup' + date_str
	os.mkdir(dst_path)
	src_path = se.getSettings('fs_game_data_path') + os.sep + folder
	for i in os.listdir(src_path):
		shutil.copy(src_path + os.sep + i, dst_path)
	# set backup as current
	src_path = se.getSettings('fs_game_data_path') + os.sep + folder + '_Backup' + os.sep + 'savegame1_backup' + backup.split(' ')[0] + '_' + backup.split(' ')[1].replace(':', '-')
	dst_path = se.getSettings('fs_game_data_path') + os.sep + folder
	for i in os.listdir(src_path):
		shutil.copy(src_path + os.sep + i, dst_path)
	# replace mods in games_json to old version
	with TinyDB(pathlib.Path(se.games_json)) as db_games:
		db_games.update({'mods': mods}, doc_ids = [data[0].doc_id])
	if sg.popup_yes_no(tr.getTrans('exportsg')) == 'Yes':
		ga.exportSGC(title)
	return True

def main():
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

	sg.popup_quick_message(tr.getTrans('fsl_init'), auto_close = True, auto_close_duration = 5, location = (50, 50))

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
				[sg.Text('Backups', size = (111,1), key = '-T_BACKUPS-', visible = False)],
				[sg.Combo('', size = (125,10), key = '-BACKUPS-', enable_events = True, visible = False)],
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
			with TinyDB(pathlib.Path(se.games_json)) as db_games:
				window['-DESC-'].update(value = db_games.search(Query().name == values['-COMBO-'].split(':')[0].rstrip())[0]['desc'])
			window['-NEW-'].update(tr.getTrans('copy'))
			window['-BACKUPS-'].update(value = '', values = getBackups(values['-COMBO-']), visible = True)
			window['-T_BACKUPS-'].update(visible = True)
		elif event == '-COMBO-' and values['-COMBO-'] == '':
			disableButtons(window)
			window['-DESC-'].update(value = '')
		elif event == '-START-':
			window.Hide()
			ret = True
			if values['-BACKUPS-'] != '':
				# copy backup to sg folder
				if sg.popup_yes_no(tr.getTrans('sure_start_backup'), title = 'Start backup', location = (50, 50)) == 'Yes':
					ret = setBackupAsCurrent(values['-COMBO-'], values['-BACKUPS-'])
				else:
					ret = False
			if ret:
				if startSaveGame(values['-COMBO-'].split(':')[0].rstrip()):
					break
			window.UnHide()
		elif event == '-CHANGE-':
			window.Hide()
			ga.guiNewSaveGame(values['-COMBO-'])
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
				window.Hide()
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
