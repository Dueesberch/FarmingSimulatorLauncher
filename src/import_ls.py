import PySimpleGUI as sg
import settings as se
import translation as tr
import game as ga
from PIL import Image
import os
import zipfile
import xml.etree.ElementTree as ET
import shutil
from tinydb import TinyDB, Query
from tinydb.operations import delete
from BetterJSONStorage import BetterJSONStorage
import logging as log
import pysed
import hashlib
import pathlib

existing_mods = {}

def importAllMods(path, rem = False):
	files = os.listdir(path)
	importMods(path, files, False)
	if rem or sg.popup_yes_no(tr.getTrans('remove_src_folder').format(path), title = tr.getTrans('remove_title'), location = (50, 50)) == 'Yes':
		try:
			shutil.rmtree(path)
		except FileNotFoundError:
			pass

def createEmptyModsFolder():
	with TinyDB(pathlib.Path(se.getSettings('all_mods_path') + os.sep + 'mods_db.json'), access_mode = "r+", storage = BetterJSONStorage) as db_mods:
		db_mods.all()
		
def getMods(path):
	mods = []
	all_mods = os.listdir(se.getSettings('all_mods_path'))
	try:
		for i in os.listdir(path):
			if i.endswith('.zip'):
				with zipfile.ZipFile(path + os.sep + i) as z:
					try:
						moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8').strip())
						version = moddesc.find('version')
						descV = int(moddesc.attrib['descVersion'])
						icon = moddesc.find('iconFilename').text
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
					if moddesc:
						try:
							z.extract(icon, se.getSettings('all_mods_path') + os.sep + 'images' + os.sep + 'tmp')
						except KeyError:
							if '.png' in icon:
								icon = icon.replace('.png', '.dds')
								z.extract(icon, se.getSettings('all_mods_path') + os.sep + 'images' + os.sep + 'tmp')
								pass						
						mods.append(i)
						try:
							im = Image.open(se.getSettings('all_mods_path') + os.sep + 'images' + os.sep + 'tmp' + os.sep + icon)
							size = 256, 256
							im.thumbnail(size, Image.ANTIALIAS)
							im.save(se.getSettings('all_mods_path') + os.sep + 'images' + os.sep + 'tmp' + os.sep + i.split('/')[-1] + '.png')
						except NotImplementedError:
							pass
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
	with TinyDB(pathlib.Path(se.games_json), storage = BetterJSONStorage) as db_games:
		all = db_games.all()
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
			l.append(n + ' : ' + m)
	return l

def updateSGS(sgs, mod, deps):
	name = mod.split('!')[1]
	if deps:
		ret = ga.select_dependencies([], deps)
		dep_mods = []
		for idx, dep in enumerate(ret):
			dep_file = ('fsl_' + dep.split(' - ')[1] + '!' + deps[idx] + '.zip')
			
			with TinyDB(pathlib.Path(se.getSettings('all_mods_path') + os.sep + 'mods_db.json'), storage=BetterJSONStorage) as db_mods:
				for datasets in db_mods.all():
					for files in datasets['files'].keys():
						if dep_file in files:
							updateSGS(sgs, dep_file, datasets['files'][files][1])
		
	with TinyDB(pathlib.Path(se.games_json), access_mode = "r+", storage = BetterJSONStorage) as db_games:
		for sg in sgs:
			add = True
			dataset = db_games.get((Query().name == sg.split(' : ')[0]))
			mods = dataset['mods']
			for i in mods.items():
				if name in i[1]:
					add = False
					mods.update({i[0]: mod})
					break
			if add:
				mods.update({str(len(mods)): mod})
			db_games.update({"mods": mods}, doc_ids = [dataset.doc_id])

def importMods(path, mods, updateSGs, rem = False):
	changed_sgs = []
	update_possible = []
	all_mods = se.getSettings('all_mods_path')
	all_new_dependencies = []
	for i in mods:
		with zipfile.ZipFile(path + os.sep + i) as z:
			moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8').strip())
			version = moddesc.find('version')
			new_name = 'fsl_' + version.text + '!' + i
			
			moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8').strip())
			icon = moddesc.find('iconFilename').text
			try:
				z.extract(icon, all_mods + os.sep + 'images' + os.sep + 'tmp')
			except KeyError:
				if '.png' in icon:
					icon = icon.replace('.png', '.dds')
					z.extract(icon, all_mods + os.sep + 'images' + os.sep + 'tmp')
					pass
			if moddesc.find('title/' + se.getFslSettings('language')) != None:
				name = moddesc.find('title/' + se.getFslSettings('language'))
				mod_lang = se.getFslSettings('language')
			elif moddesc.find('title/en') != None:
				name = moddesc.find('title/en')
				mod_lang = 'en'
			elif moddesc.find('title') != None:
				name = moddesc.find('title')[0]
				mod_lang = moddesc.find('title')[0].tag
			img_name = hashlib.md5(i.split('.zip')[0].encode()).hexdigest()
			
			if moddesc.find('maps/map/title/en') != None:
				mod_type = 'map'
			else:
				mod_type = 'mod'
			dependencies = []
			dep_fullfilled = True
			if moddesc.find('dependencies') != None:
				for idx in moddesc.find('dependencies'):
					not_imported_yet = True
					with TinyDB(pathlib.Path(se.getSettings('all_mods_path') + os.sep + 'mods_db.json'), storage=BetterJSONStorage) as db_mods:
						for datasets in db_mods.all():
							for files in datasets['files'].keys():
								if '!' + idx.text + '.zip' in files:
									not_imported_yet = False
					if not_imported_yet:
						sg.popup_ok(tr.getTrans('missing_dep').format(idx.text), title = tr.getTrans('missing'))
						dep_fullfilled = False
					else:
						dependencies.append(idx.text)
			if dep_fullfilled:
				shutil.copyfile(path + os.sep + i, all_mods + os.sep + new_name)
				f_hash = hashlib.md5(pathlib.Path(all_mods + os.sep + new_name).read_bytes()).hexdigest()
				with TinyDB(pathlib.Path(se.getSettings('all_mods_path') + os.sep + 'mods_db.json'), access_mode = "r+", storage = BetterJSONStorage) as db_mods:
					d = db_mods.get(Query().name == name.text)
					if d == None:
						db_mods.insert({'name': name.text, 'mod_type': mod_type, 'lang': mod_lang, 'img': img_name, 'files': {new_name: [f_hash, dependencies]}})
					else:
						for idx in d['files'].keys():
							with TinyDB(pathlib.Path(se.games_json), storage = BetterJSONStorage) as db_games:
								for game in db_games.all():
									if idx in game['mods'].values():
										if not game['name'] in update_possible:
											update_possible.append(game['name'])
						d['files'][new_name] = [f_hash, dependencies]
						db_mods.update({'files': d['files']}, doc_ids = [d.doc_id])
			else:
				break
			try:
				im = Image.open(all_mods + os.sep + 'images' + os.sep + 'tmp' + os.sep + icon)
				size = 256, 256
				im.thumbnail(size, Image.ANTIALIAS)
				im.save(all_mods + os.sep + 'images' + os.sep + img_name + '.png')
			except NotImplementedError:
				pass
		
			if moddesc.find('maps/map/title/en') != None:
				continue
			else:
				if updateSGs:
					sgs = getSaveGames()
					for idx, sgame in enumerate(sgs):
						if sgame.split(':')[0].rstrip() in update_possible:
							sgs[idx] = sgame + ' - ' + tr.getTrans('updatable')
					layout = [	[sg.Text(tr.getTrans('select_sgs').format(i))],
								[sg.Listbox(sgs,  key = '-SGS-', size = (108, 10), select_mode = 'extended')],
								[sg.Button('Ok', key = '-OK-', size = (14, 1))]
					]
					window = sg.Window(tr.getTrans('import'), layout, finalize = True, location = (50, 50), disable_close = True)

					while True:
						event, values = window.read()
						#print(event, values)
						if event == '-OK-':
							if len(values['-SGS-']) > 0:
								updateSGS(values['-SGS-'], new_name, dependencies)
								for idx in values['-SGS-']:
									title = idx.split(':')[0].rstrip()
									if not title in changed_sgs:
										changed_sgs.append(title)
							window.close()
							break
		if rem and sg.popup_yes_no(tr.getTrans('rem_source').format(path + os.sep + i), title = tr.getTrans('remove_title'), location = (50, 50)) == 'Yes':
			os.remove(path + os.sep +i)
	
#	for new_depend in all_new_dependencies:
#		not_imported_yet = True
#		with TinyDB(pathlib.Path(se.getSettings('all_mods_path') + os.sep + 'mods_db.json'), storage=BetterJSONStorage) as db_mods:
#			for datasets in db_mods.all():
#				for files in datasets['files'].keys():
#					if '!' + new_depend + '.zip' in files:
#						not_imported_yet = False
#						break
#		if not_imported_yet:
#			sg.popup_ok(tr.getTrans('missing_dep').format(new_depend), title = tr.getTrans('missing'))

	for idx in changed_sgs:
		if sg.popup_yes_no(tr.getTrans('exportsg').format(idx)) == 'Yes':
			ga.exportSGC(idx)

def removeMods(mods):
	all_mods = se.getSettings('all_mods_path')
	for i, val in enumerate(mods):
		unused = True
		with TinyDB(pathlib.Path(se.games_json), storage = BetterJSONStorage) as db_games:
			datasets = db_games.all()
		for i in range(len(datasets)):
			if existing_mods[val] in list(datasets[i]['mods'].values()) or existing_mods[val] in datasets[i]['map']:
				sg.popup_ok(tr.getTrans('cant_rem_mod').format(existing_mods[val], datasets[i]['name']), title = tr.getTrans('error'))
				unused = False
		if unused:
			with zipfile.ZipFile(all_mods + os.sep + existing_mods[val]) as z:
				moddesc = ET.fromstring(z.read('modDesc.xml').decode('utf8').strip())
				icon = moddesc.find('iconFilename').text
				for idx, l in enumerate(se.getLangs()):
					if not idx + 1 == len(se.getLangs()):
						name = moddesc.find('title/' + l)
					else:
						name = moddesc.find('title')
					if name != None:
						mod_lang = l
						break
				with TinyDB(pathlib.Path(se.getSettings('all_mods_path') + os.sep + 'mods_db.json'), access_mode = "r+", storage = BetterJSONStorage) as db_mods:
					d = db_mods.get(Query().name == name.text)
					d['files'].pop(existing_mods[val])
					if d['files'] == {}:
						db_mods.remove(doc_ids = [d.doc_id])
					else:
						db_mods.update({'files': d['files']}, doc_ids = [d.doc_id])
			os.remove(all_mods + os.sep + existing_mods[val])

def getAllMods():
	global existing_mods
	m = ga.getMods(False, False)
	existing_mods = m[0]
	existing_mods.update(m[1])
	for i in list(se.getInternalMaps().keys()):
		del existing_mods[i]
	return list(sorted(existing_mods.keys()))

def markUnusedMods(window):
	maps, mods = ga.getMods(False)
	mods.update(maps)
	used = []
	with TinyDB(pathlib.Path(se.games_json), storage=BetterJSONStorage) as db_games:
		datasets = db_games.all() 
	for dataset in datasets:
		used = used + list(dataset['mods'].values())
		used.append(dataset['map'])
	used = list(dict.fromkeys(used))
	all_files = list(mods.values())
	unused = []
	for mod in all_files:
		if not mod in used:
			unused.append(list(mods.keys())[list(mods.values()).index(mod)])
	return unused

def guiImportMods(updateSGs = True):
	selected_MODS = []
	selected_MODS_INST = []

	layout =    [	[sg.Text(tr.getTrans('get_mod_path'))],
					[sg.Input('', key = '-MOD_PATH-', size = (110, 1), enable_events = True)],
					[sg.FolderBrowse(initial_folder = se.getSettings('fs_game_data_path'), target = '-MOD_PATH-', size = (96,1))],
					[sg.Text(tr.getTrans('importable_mods'))],
					[sg.Listbox('',  key = '-MODS-', size = (108, 10), select_mode = 'extended', enable_events = True)],
					[sg.Button(tr.getTrans('import'), key = '-IMPORT-', size = (96, 1))],
					[sg.Text(tr.getTrans('existing_mods'))],
					[sg.Listbox(getAllMods(),  key = '-MODS_INST-', size = (108, 10), select_mode = 'extended', enable_events = True), sg.Image('', key = '-MODS_INST_IMG-', size = (256, 256))],
					[sg.Button(tr.getTrans('unused_mods'), key = '-UNUSED-', size = (47, 1)), sg.Button(tr.getTrans('remove'), key = '-REMOVE-', size = (47, 1))],
					[sg.Text('')],
					[sg.Button(tr.getTrans('exit'), key = '-EXIT-', size = (14, 1))]
				]

	window = sg.Window(tr.getTrans('import'), layout, finalize = True, location = (50, 50))

	while True:
		event, values = window.read()
		#print(event, values)
		if event == sg.WIN_CLOSED or event=="-EXIT-":
			try:
				shutil.rmtree(se.getSettings('all_mods_path') + os.sep + 'images' + os.sep + 'tmp')
			except FileNotFoundError:
				pass
			break
		elif event == "-IMPORT-":
			importMods(values['-MOD_PATH-'], values['-MODS-'], updateSGs)
			window['-MOD_PATH-'].update('')
			window['-MODS-'].update(values = '')
			window['-MODS_INST-'].update(getAllMods())
		elif event == '-REMOVE-':
			removeMods(values['-MODS_INST-'])
			window['-MODS_INST-'].update(getAllMods())
		elif event == '-MOD_PATH-' and not values['-MOD_PATH-'] == '':
			window['-MODS-'].update(values = getMods(values['-MOD_PATH-']))
		elif event == '-UNUSED-':
			unused = markUnusedMods(window)
			window.Element('-MODS_INST-').SetValue(unused)
			selected_MODS_INST = unused
		elif event == '-MODS-':
			for i in values['-MODS-']:
				if not i in selected_MODS:
					try:
						window['-MODS_INST_IMG-'].update(se.getSettings('all_mods_path') + os.sep + 'images' + os.sep + 'tmp' + os.sep + i + '.png', size = (256, 256))
					except Exception:
						pass
			selected_MODS = values['-MODS-']
		elif event == '-MODS_INST-':
			with TinyDB(pathlib.Path(se.getSettings('all_mods_path') + os.sep + 'mods_db.json'), storage = BetterJSONStorage) as db_mods:
				a = set(values['-MODS_INST-'])
				b = set(selected_MODS_INST)
				c = list(a - b)[0]
				mod_name = c.split(' - ')[0]
				try:
					window['-MODS_INST_IMG-'].update(se.getSettings('all_mods_path') + os.sep + 'images' + os.sep + db_mods.get(Query().name == mod_name)['img'] + '.png', size = (256, 256))
				except Exception:
					pass
			selected_MODS_INST = values['-MODS_INST-']
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
	
	with TinyDB(pathlib.Path(se.games_json), access_mode = "r+", storage = BetterJSONStorage) as db_games:
		if db_games.get((Query().name == values['-TITLE-'])) or os.path.exists(se.getSettings('fs_game_data_path') + os.sep + values['-TITLE-']):
			sg.popup(tr.getTrans('ssg_exists'), title = tr.getTrans('ssg_title'), location = (50, 50))
			return False

	modstoadd = {}
	for i, val in enumerate(mods):
		modstoadd[str(i)] = mods[i]

	if len(maps) == 0:
		maps.append(map_title)
	folder_name = hashlib.md5(values['-TITLE-'].encode()).hexdigest()
	
	with TinyDB(pathlib.Path(se.games_json), access_mode = "r+", storage=BetterJSONStorage) as db_games:
		db_games.insert({"name": values['-TITLE-'], "folder": folder_name, "desc": values['-DESC-'], "map": maps[0], "mods": modstoadd})

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
	if path == '':
		return False
	with TinyDB(pathlib.Path(path), access_mode = "r+", storage = BetterJSONStorage) as db_fsl_sgc:
		new = db_fsl_sgc.all()[0]
	fdata = {"hash": hashlib.md5(pathlib.Path(path).read_bytes()).hexdigest(), "path": path}
	
	with TinyDB(pathlib.Path(se.games_json), access_mode = "r+", storage = BetterJSONStorage) as db_games:
		if db_games.get(Query().name == title):
			doc_id = db_games.get(Query().name == new['name']).doc_id
			db_games.update({"name": title, "folder": new['folder'], "desc": new['desc'], "map": new['map'], "mods": new['mods'], "imported": fdata}, doc_ids = [doc_id])
		else:
			try:
				os.mkdir(se.getSettings('fs_game_data_path') + os.sep + new['folder'])
				os.mkdir(se.getSettings('fs_game_data_path') + os.sep + new['folder'] + '_Backup')
			except FileExistsError:
				pass
			db_games.insert({"name": title, "folder": new['folder'], "desc": new['desc'], "map": new['map'], "mods": new['mods'], "imported": fdata})
	return True

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
			if importSGC(values['-SGC_PATH-'], values['-I_TITLE-']):
				break
		elif event == '-SGC_PATH-':
			with TinyDB(pathlib.Path(values['-SGC_PATH-']), storage = BetterJSONStorage) as db_sgc:
				name = db_sgc.all()[0]['name']
				window['-I_TITLE-'].update(name)
				with TinyDB(pathlib.Path(se.games_json), storage = BetterJSONStorage) as db_games:
					if db_games.get(Query().name == name):
						window['-EXISTS-'].update(tr.getTrans('yes'), background_color = 'red')
					else:
						window['-EXISTS-'].update(tr.getTrans('no'), background_color = 'green')
		elif event == '-I_TITLE-':
			with TinyDB(pathlib.Path(se.games_json), storage = BetterJSONStorage) as db_games:
				if db_games.get(Query().name == values['-I_TITLE-']):
					window['-EXISTS-'].update(tr.getTrans('yes'), background_color = 'red')
				else:
					window['-EXISTS-'].update(tr.getTrans('no'), background_color = 'green')
			
	window.close()
	return ret
