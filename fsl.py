# verwalten mehrer versionen eines mods
# import bestehender spielstände
# hilfe / anleitung in translations eintragen
# tooltips hinzufügen zu feldern
# default texte löschen wenn sie angeklickt werden
# combo boxen öffnen wenn angeklickt?
# mac support
# bilder bei mod auswahl
# pyinstaller

import os
import sys
import subprocess
import time
from dirsync import sync
import psutil
import shutil
import zipfile
import checksumdir

import xml.etree.ElementTree as ET

import PySimpleGUI as sg

import translation as tr
import settings as se
import newgame as ng

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
			mods_path = se.getSettings('fs_game_data_path') + os.sep + 'mods'
			savegame1_path = se.getSettings('fs_game_data_path') + os.sep + 'savegame1'
			sg.popup_ok('Folder\n' + mods_path + '\nmoved to\n' +  mods_path + '_fsl_bak\nFolder\n' + savegame1_path + '\nmoved to\n' + savegame1_path + '_fsl_bak', title = 'Backup folders')
			try:
				os.rename(mods_path, mods_path + '_fsl_bak')
			except FileNotFoundError:
				pass
			try:
				os.rename(savegame1_path, savegame1_path + '_fsl_bak')
			except FileNotFoundError:
				pass
		else:
			sg.popup_ok('Quit FarmingSimulatorLauncher', title = 'Quit')
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
	if os.path.exists(fs_game_data_folder + 'mods'):
		if checksumdir.dirhash(fs_game_data_folder + 'mods') == TinyDB('settings.json').get(doc_id=1)['mods_hash']:
			shutil.rmtree(fs_game_data_folder + 'mods')
		else:
			print('mods folder differnt')
			return False
	if os.path.exists(fs_game_data_folder + 'savegame1'):
		if checksumdir.dirhash(fs_game_data_folder + 'savegame1') == TinyDB('settings.json').get(doc_id=1)['sg_hash']:
			shutil.rmtree(fs_game_data_folder + 'savegame1')
		else:
			print('sg folder differnt')
			return False
	if os.path.exists(fs_game_data_folder + 'savegameBackup'):
		if checksumdir.dirhash(fs_game_data_folder + 'savegameBackup') == TinyDB('settings.json').get(doc_id=1)['sgb_hash']:
			shutil.rmtree(fs_game_data_folder + 'savegameBackup')
		else:
			print('sgb folder differnt')
			return False
	os.makedirs(fs_game_data_folder + 'mods' + os.sep)
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
			sg.popup_error(tr.getTrans(lang, 'filenotfound'), title = tr.getTrans(lang, 'filenotfound'))
	return l

def startSaveGame(name):
	q = Query()
	map = db.get((q.name == name))['map']
	os.link(all_mods_folder + map, fs_game_data_folder + 'mods' + os.sep + map)
	mods = db.get((q.name == name))['mods']
	for i in mods:
		try:
			os.link(all_mods_folder + mods[i], fs_game_data_folder + 'mods' + os.sep + mods[i])
		except FileNotFoundError:
			#TODO missing mod
			pass
	savegame = db.get((q.name == name))['name']
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
	
def removeSaveGame(lang, title):
	q = Query()
	exists = db.get((q.name == title.split(' : ')[0].rstrip()))
	if sg.popup_yes_no(tr.getTrans(lang, 'delete'), title = tr.getTrans(lang, 'delete_title')) == "Yes":
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

	button_layout = [	[sg.Button(button_text = tr.getTrans(lang,'new'), key='-NEW-', size=(14, 2)),
						sg.Button(button_text = tr.getTrans(lang, 'change'), key = '-CHANGE-', size = (14, 2), disabled = True),
						sg.Button(button_text = tr.getTrans(lang, 'remove'), key='-REMOVE-', size=(14, 2), disabled = True),
						sg.Button(button_text = tr.getTrans(lang, 'settings'), key='-SET-', size=(14, 2)),
						sg.Button(button_text = tr.getTrans(lang, 'exit'), key='-EXIT-', size=(14, 2)),
						sg.Button(button_text = tr.getTrans(lang, 'help'), key='-HELP-', size=(14, 2))
						],
						sg.Button(button_text = tr.getTrans(lang, 'start'), key = '-START-', size = (window_size[0]-10, 1), disabled = True)
					]
	layout = [	[sg.Combo(getSaveGames(), size = (window_size[0]-10,5), key = '-COMBO-', enable_events = True)],
				[sg.Text(tr.getTrans(lang, 'description'), size = (window_size[0]-10,1))],
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
			startSaveGame(values['-COMBO-'].split(':')[0].rstrip())
			break
		elif event == '-CHANGE-':
			window.Hide()
			ng.guiNewSaveGame(lang, values['-COMBO-'].split(' : ')[0].rstrip())
			window['-COMBO-'].update(value = '', values = getSaveGames())
			window['-START-'].update(disabled = True)
			window['-CHANGE-'].update(disabled = True)
			window['-REMOVE-'].update(disabled = True)
			window.UnHide()
		elif event == '-REMOVE-':
			removeSaveGame(lang, values['-COMBO-'])
			window['-COMBO-'].update(value = '', values = getSaveGames())
			window['-START-'].update(disabled = True)
			window['-CHANGE-'].update(disabled = True)
			window['-REMOVE-'].update(disabled = True)
		elif event == '-NEW-':
			window.Hide()
			ng.guiNewSaveGame(lang)
			window['-COMBO-'].update(value = '', values = getSaveGames())
			window['-START-'].update(disabled = True)
			window['-CHANGE-'].update(disabled = True)
			window['-REMOVE-'].update(disabled = True)
			window.UnHide()
		elif event == '-SET-':
			window.Hide()
			se.guiSettings(lang)
			window.UnHide()
		elif event == '-HELP-':
			window.Hide()
			sg.popup_ok(tr.getTrans(lang, 'help_text'), title = tr.getTrans(lang, 'help'))
			window.UnHide()

if __name__ == '__main__':
	main()