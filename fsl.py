# In Progress
# import bestehender spielstände 

# hilfe / anleitung in translations eintragen
# tooltips hinzufügen zu feldern
# mac support
# pyinstaller
# parameter übergabe anpassen zb se.getSetting(lang) statt param lang
# link zu buymeacoffe
# check new release
# spielstandname in careerSavegame.xml vor spielstart
# laden alter spielstände
# mods ordner prüfen ob neue mods eingefügt wurden
# import savegame statt _fsl_bak
# ordern all_mods anlegen
# teilen sg's

# LOW PRIO
# bilder bei mod auswahl
# verwalten mehrerer versionen eines mods

# release
# import mods / sg
# anleitung
# link buymeacoffee
# translation / beschriftung sauber


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

import xml.etree.ElementTree as ET

import PySimpleGUI as sg

import translation as tr
import settings as se
import newgame as ng
import import_ls as im

window_size = (800, 350)

from tinydb import TinyDB, Query

db = TinyDB('games.json')

fs_path = ''
fs_game_data_folder = ''
all_mods_folder = ''

lang = ''

# call inital settings
# Backup mods and savegame1 folder 
def checkFirstRun():
	ret = True
	if not os.path.exists('settings.json'):
		ret = se.guiSettings('en', True)
		if ret:
			mods_imported = True # TODO False after testing
			mods_path = se.getSettings('fs_game_data_path') + os.sep + 'mods'
			fs_game_data_path = se.getSettings('fs_game_data_path')
			savegameBackup_path = se.getSettings('fs_game_data_path') + os.sep + 'savegameBackup'
			lang = se.getSettings('language')
			try:
				if len(os.listdir(mods_path)) > 0:
					if sg.popup_yes_no(tr.getTrans('import_mods_init').format(mods_path), title = 'import') == 'Yes':
						im.importMods(mods_path, True)
						mods_imported = True
					else:
						sg.popup_ok(tr.getTrans('backup_folder_text').format(mods_path, mods_path), title = tr.getTrans('backup_folders_title'), line_width = 100)
						os.rename(mods_path, mods_path + '_fsl_bak')
			except FileNotFoundError:
				pass
			except FileExistsError:
				ret = False
				sg.popup_error(mods_path + tr.getTrans('fsl_bak_exists'))
			
			if mods_imported:
				f = "savegame[0-9]"
				for folder in os.listdir(fs_game_data_path):
					if re.search(f, folder):
						if sg.popup_yes_no(tr.getTrans('import_sg_init').format(folder, fs_game_data_path), title = 'import') == 'Yes':
							ret = im.guiImportSG(fs_game_data_path + os.sep + folder, True)
							if ret:
								shutil.rmtree(fs_game_data_path + os.sep + folder)
						else:
							sg.popup_ok(tr.getTrans('backup_folder_text').format(fs_game_data_path + os.sep + folder, fs_game_data_path + os.sep + folder), title = tr.getTrans('backup_folders_title'), line_width = 100)
							os.rename(fs_game_data_path + os.sep + folder, fs_game_data_path + os.sep + folder + '_fsl_bak')
							if not os.path.exists(savegameBackup_path + '_fsl_bak'):
								os.makedirs(savegameBackup_path + '_fsl_bak')
							for backup_file in os.listdir(savegameBackup_path):
								if re.search(folder, backup_file):
									shutil.move(savegameBackup_path + os.sep + backup_file, savegameBackup_path + '_fsl_bak' + os.sep + backup_file)
			try:
				shutil.rmtree(savegameBackup_path)
			except FileNotFoundError:
				pass
		else:
			sg.popup_ok('Quit FarmingSimulatorLauncher', title = 'Quit')
		if ret == False:
			try:
				os.remove('settings.json')
			except FileNotFoundError:
				pass
	return ret

def init():
	global lang
	global fs_game_data_folder
	global all_mods_folder
	global fs_path
	lang = se.getSettings('language')
	fs_path = se.getSettings('fs_path')
	fs_game_data_folder = se.getSettings('fs_game_data_path') + os.sep
	all_mods_folder = se.getSettings('all_mods_path') + os.sep
	#TODO files in allmods start with fsl
	if os.path.exists(fs_game_data_folder + 'mods'):
		if checksumdir.dirhash(fs_game_data_folder + 'mods') == TinyDB('settings.json').get(doc_id = 1)['mods_hash']:
			shutil.rmtree(fs_game_data_folder + 'mods')
		else:
			print('mods folder differnt')
			return False
	if os.path.exists(fs_game_data_folder + 'savegame1'):
		if checksumdir.dirhash(fs_game_data_folder + 'savegame1') == TinyDB('settings.json').get(doc_id = 1)['sg_hash']:
			shutil.rmtree(fs_game_data_folder + 'savegame1')
		else:
			print('sg folder differnt')
			return False
	if os.path.exists(fs_game_data_folder + 'savegameBackup'):
		if checksumdir.dirhash(fs_game_data_folder + 'savegameBackup') == TinyDB('settings.json').get(doc_id = 1)['sgb_hash']:
			shutil.rmtree(fs_game_data_folder + 'savegameBackup')
		else:
			print('sgb folder differnt')
			return False
	return True

def getSaveGames():
	q = Query()
	all = db.all()
	l = []
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
			sg.popup_error(tr.getTrans('filenotfound'), title = tr.getTrans('filenotfound'))
			pass
	return l

def startSaveGame(name):
	os.makedirs(fs_game_data_folder + 'mods' + os.sep)
	q = Query()
	map = db.get((q.name == name))['map']
	os.link(all_mods_folder + map, fs_game_data_folder + 'mods' + os.sep + map)
	mods = db.get((q.name == name))['mods']
	for i in mods:
		try:
			os.link(all_mods_folder + mods[i], fs_game_data_folder + 'mods' + os.sep + mods[i])
		except FileNotFoundError:
			if sg.popup_yes_no(tr.getTrans('mod_not_found').format(mods[i], all_mods_folder), title = tr.getTrans('ssg_title_empty')) == 'No':
				shutil.rmtree(fs_game_data_folder + 'mods' + os.sep)
				return False
	savegame = db.get((q.name == name))['name']
	if os.path.exists(fs_game_data_folder + savegame + os.sep + 'careerSavegame.xml'):
		ET.parse(fs_game_data_folder + savegame + os.sep + 'careerSavegame.xml').find('settings/savegameName').text = savegame
	shutil.copytree(fs_game_data_folder + savegame, fs_game_data_folder + 'savegame1')
	shutil.copytree(fs_game_data_folder + savegame + ' Backup', fs_game_data_folder + 'savegameBackup')
	TinyDB('settings.json').update({'last_sg': name, 'sg_hash': '', 'sgb_hash': '', 'mods_hash': checksumdir.dirhash(fs_game_data_folder + 'mods')}, doc_ids = [1])
	subprocess.run(fs_path, shell = True)
	p_name = (str(se.getSettings('fs_path').split('/')[-1].split('.')[0])).lower()
	p_name_child = (str(se.getSettings('fs_path').split('/')[-1].split('.')[0]) + 'Game.exe').lower()
	loop = True
	while loop:
		time.sleep(10)
		TinyDB('settings.json').update({'sg_hash': checksumdir.dirhash(fs_game_data_folder + 'savegame1')}, doc_ids = [1])
		sync(fs_game_data_folder + 'savegame1', fs_game_data_folder + savegame, 'sync')
		TinyDB('settings.json').update({'sgb_hash': checksumdir.dirhash(fs_game_data_folder + 'savegameBackup')}, doc_ids = [1])
		sync(fs_game_data_folder + 'savegameBackup', fs_game_data_folder + savegame + ' Backup', 'sync')
		loop = False
		for p in psutil.process_iter(attrs=['pid', 'name']):
			if p_name_child in (p.info['name']).lower():
				loop = True
				break
	return True
	
def removeSaveGame(title):
	q = Query()
	exists = db.get((q.name == title.split(' : ')[0].rstrip()))
	if sg.popup_yes_no(tr.getTrans('delete'), title = tr.getTrans('delete_title')) == "Yes":
		db.remove(doc_ids = [exists.doc_id])
		if os.path.exists(fs_game_data_folder + title.split(' : ')[0].rstrip()):
			shutil.rmtree(fs_game_data_folder + title.split(' : ')[0].rstrip())
		if os.path.exists(fs_game_data_folder + title.split(' : ')[0].rstrip() + ' Backup'):
			shutil.rmtree(fs_game_data_folder + title.split(' : ')[0].rstrip() + ' Backup')
	return

def main():
	if not checkFirstRun():
		sys.exit()

	if not init():
		#TODO popup mit troubleshoot
		print('failed')

	button_layout = [	[sg.Button(button_text = tr.getTrans('new'), key='-NEW-', size=(14, 2)),
						sg.Button(button_text = tr.getTrans('change'), key = '-CHANGE-', size = (14, 2), disabled = True),
						sg.Button(button_text = tr.getTrans('remove'), key='-REMOVE-', size=(14, 2), disabled = True),
						sg.Button(button_text = tr.getTrans('settings'), key='-SET-', size=(14, 2)),
						sg.Button(button_text = tr.getTrans('exit'), key='-EXIT-', size=(14, 2)),
						sg.Button(button_text = tr.getTrans('help'), key='-HELP-', size=(14, 2))
						],
						sg.Button(button_text = tr.getTrans('start'), key = '-START-', size = (window_size[0]-10, 1), disabled = True)
					]
	layout = [	[sg.Combo(getSaveGames(), size = (window_size[0]-10,5), key = '-COMBO-', enable_events = True)],
				[sg.Text(tr.getTrans('description'), size = (window_size[0]-10,1))],
				[sg.Text(size = (window_size[0]-10,1), key = '-DESC-')],
				[button_layout]
			]
			
	window = sg.Window('Farming Simulator SaveGames', layout, finalize = True, size = window_size, location = (50, 50))

	while True:
		event, values = window.read()
		#print(event, values)
		if event == sg.WIN_CLOSED or event == '-EXIT-':
			break
		elif event == '-COMBO-':
			window['-START-'].update(disabled = False)
			window['-CHANGE-'].update(disabled = False)
			window['-REMOVE-'].update(disabled = False)
			data = db.search(Query().name == values['-COMBO-'].split(':')[0].rstrip())
			window['-DESC-'].update(value = data[0]['desc'])
		elif event == '-START-':
			window.Hide()
			if startSaveGame(values['-COMBO-'].split(':')[0].rstrip()):
				break
		elif event == '-CHANGE-':
			window.Hide()
			ng.guiNewSaveGame(values['-COMBO-'].split(' : ')[0].rstrip())
			window['-COMBO-'].update(value = '', values = getSaveGames())
			window['-START-'].update(disabled = True)
			window['-CHANGE-'].update(disabled = True)
			window['-REMOVE-'].update(disabled = True)
			window.UnHide()
		elif event == '-REMOVE-':
			removeSaveGame(values['-COMBO-'])
			window['-COMBO-'].update(value = '', values = getSaveGames())
			window['-START-'].update(disabled = True)
			window['-CHANGE-'].update(disabled = True)
			window['-REMOVE-'].update(disabled = True)
		elif event == '-NEW-':
			window.Hide()
			ng.guiNewSaveGame()
			window['-COMBO-'].update(value = '', values = getSaveGames())
			window['-START-'].update(disabled = True)
			window['-CHANGE-'].update(disabled = True)
			window['-REMOVE-'].update(disabled = True)
			window.UnHide()
		elif event == '-SET-':
			window.Hide()
			se.guiSettings(lang)
			#TODO update text
			window.UnHide()
		elif event == '-HELP-':
			window.Hide()
			sg.popup_ok(tr.getTrans('help_text'), title = tr.getTrans('help'))
			window.UnHide()

if __name__ == '__main__':
	main()