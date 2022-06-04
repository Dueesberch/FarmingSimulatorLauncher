import zipfile
import os
import shutil
from pathlib import Path
import hashlib
import subprocess
import platform
import datetime

import PySimpleGUI as sg
from tinydb import TinyDB, Query
from tinydb.operations import delete
import translation as tr
import settings as se
import logging as log
import re
from random import randint

import xml.etree.ElementTree as ET

from PIL import Image

mods = {}
maps = {}

required_files = [	'densityMap_fruits.gdm',
					'densityMap_ground.gdm',
					'densityMap_height.gdm',
					'densityMap_stones.gdm',
					'densityMap_weed.gdm',
					'infoLayer_limeLevel.grle',
					'infoLayer_placementCollisionGenerated.grle',
					'infoLayer_plowLevel.grle',
					'infoLayer_rollerLevel.grle',
					'infoLayer_sprayLevel.grle',
					'infoLayer_stubbleShredLevel.grle',
					'infoLayer_tipCollisionGenerated.grle',
					'infoLayer_weed.grle']

fruits = ['WHEAT', 'MAIZE', 'SUGARBEET', 'BARLEY', 'OAT', 'CANOLA', 'SUNFLOWER', 'SOYBEAN', 'SORGHUM', 'POTATO']

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

def removeSaveGame(title, request = True):
	q = Query()
	exists = TinyDB(se.games_json).get((q.name == title.split(' : ')[0].rstrip()))
	if not request or sg.popup_yes_no(tr.getTrans('delete'), title = tr.getTrans('remove'), location = (50, 50)) == "Yes":
		TinyDB(se.games_json).remove(doc_ids = [exists.doc_id])
		if os.path.exists(se.getSettings('fs_game_data_path') + os.sep + exists['folder']):
			shutil.rmtree(se.getSettings('fs_game_data_path') + os.sep + exists['folder'])
		if os.path.exists(se.getSettings('fs_game_data_path') + os.sep + exists['folder'] + '_Backup'):
			shutil.rmtree(se.getSettings('fs_game_data_path') + os.sep + exists['folder'] + '_Backup')
	return

def createFarmlandXML(farmland_xml, game_path, level):
	farmlands = farmland_xml.find('farmlands')
	root = ET.Element('farmlands')
	for land in farmlands:
		default = 'false'
		if level == 'nf' or level == 'c_w':
			try:
				default = land.attrib['defaultFarmProperty']
				ET.SubElement(root, 'farmland', id = land.attrib['id'], farmId = '1')
			except KeyError:
				ET.SubElement(root, 'farmland', id = land.attrib['id'], farmId = '0')
				pass
		else:
			ET.SubElement(root, 'farmland', id = land.attrib['id'], farmId = '0')
	tree = ET.ElementTree(root)
	ET.indent(tree)
	tree.write(game_path + os.sep + 'farmland.xml', xml_declaration = True, encoding = "UTF-8")

def createVehiclesXML(vehicles_xml, dem_file, game_path, level):
	root = ET.Element('vehicles')
	c = 1
	for v in vehicles_xml:
		if v.tag == 'vehicle' and 'defaultFarmProperty' in v.attrib and level != 'nf' and level != 'c_w':
			continue
		elif v.tag == 'vehicle' and not 'train' in v.attrib['filename']:
			try:
				xPosition = v.attrib['xPosition']
				zPosition = v.attrib['zPosition']
				yOffset = v.attrib['yOffset']
				child = ET.SubElement(root, 'vehicle', filename = v.attrib['filename'], id = str(c), isAbsolute = 'true', age = "0.000000", farmId = v.attrib['farmId'], propertyState = '1', operatingTime = "0.000000")
				with Image.open(dem_file, 'r') as im:
					w, h = im.size
					png_x = (float(w) / 2) + (float(xPosition) / 2)
					png_y = (float(h) / 2) + (float(zPosition) / 2)
					map_h = im.getpixel((png_x, png_y)) / 256 + float(yOffset)
					pos = xPosition + ' ' + str(map_h) + ' ' + zPosition
					rot = '0 ' + v.attrib['yRotation'] + ' 0'
					ET.SubElement(child, 'component', index = '1', position = pos, rotation = rot)
				for v_child in v:
					child.append(v_child)
			except KeyError:
				child = ET.SubElement(root, 'vehicle', filename = v.attrib['filename'], id = str(c), isAbsolute = v.attrib['isAbsolute'], age = "0.000000", farmId = v.attrib['farmId'], propertyState = v.attrib['propertyState'], operatingTime = "0.000000")
				for com in v:
					if com.tag == 'component':
						ET.SubElement(child, 'component', index = com.attrib['index'], position = com.attrib['position'], rotation = com.attrib['rotation'])
			c = c + 1
	tree = ET.ElementTree(root)
	ET.indent(tree)
	tree.write(game_path + os.sep + 'vehicles.xml', xml_declaration = True, encoding = "UTF-8")

def createItemsXML(items_xml, game_path, level):
	root = ET.Element('items')
	c = 0
	for i in items_xml:
		ET.dump(i)
		c = c + 1
	tree = ET.ElementTree(root)
	ET.indent(tree)
	tree.write(game_path + os.sep + 'items.xml', xml_declaration = True, encoding = "UTF-8")

def createPlaceablesXML(placeables_xml, game_path, level, map = None):
	root = ET.Element('placeables')
	c = 1
	if map != None:
		map = map.split('!')[1].replace('.zip', '') 
	for p in placeables_xml:
		attribs = {}
		filename = p.attrib['filename']
		if map == None or not '$mapdir$' in filename:
			attribs['filename'] = p.attrib['filename']
		else:
			attribs['modName'] = map
			attribs['filename'] = filename.replace('$mapdir$', '$moddir$' + map)
		attribs['id'] = str(c)
		attribs['position'] = p.attrib['position']
		attribs['rotation'] = p.attrib['rotation']
		attribs['age'] = "0.000000"
		if 'mapBoundId' in p.attrib:
			attribs['mapBoundId'] = p.attrib['mapBoundId']
		if 'farmId' in p.attrib:
			attribs['farmId'] = p.attrib['farmId']
		child = ET.SubElement(root, 'placeable')
		for at, val in attribs.items():
			child.set(at, val)
		for subchild in p:
			child.append(subchild)
		c = c + 1
	tree = ET.ElementTree(root)
	ET.indent(tree)
	tree.write(game_path + os.sep + 'placeables.xml', xml_declaration = True, encoding = "UTF-8")

def createFarmXML(game_path, money, nick):
	root = ET.Element('farms')
	farm = ET.SubElement(root, 'farm', farmId = "1", name = nick + " Farm", color = "1", loan = "0.000000", money = money)
	players = ET.SubElement(farm, 'players')
	ET.SubElement(players, 'player', uniqueUserId = "player", farmManager = "true", lastNickname = nick, buyVehicle = "true", sellVehicle = "true", buyPlaceable = "true",\
		sellPlaceable = "true", manageContracts = "true", tradeAnimals = "true", createFields = "true", landscaping = "true", hireAssistant="true", resetVehicle="true",\
		manageProductions = "true", manageRights = "true", transferMoney = "true", updateFarm = "true", manageContracting = "true")
	tree = ET.ElementTree(root)
	ET.indent(tree)
	tree.write(game_path + os.sep + 'farms.xml', xml_declaration = True, encoding = "UTF-8")

def createFieldsXML(map_i3d, game_path):
	root = ET.Element('fields')
	m = re.findall('TransformGroup name="field[0-9]+', map_i3d)
	for field in range(1, len(m) + 1):
		ET.SubElement(root, 'field', id = str(field), plannedFruit = fruits[randint(0, len(fruits) - 1)])
	ET.SubElement(root, 'lastHandledFieldIndex').text = str(randint(0, len(fruits) - 1))
	tree = ET.ElementTree(root)
	ET.indent(tree)
	tree.write(game_path + os.sep + 'fields.xml', xml_declaration = True, encoding = "UTF-8")

def setSavegameSettings():
	layout = [	[	sg.Radio(tr.getTrans('new_farmer'), '-LEVEL-', key = '-NEW_FARMER-', default = True, enable_events = True),
					sg.Radio(tr.getTrans('farm_manager'), '-LEVEL-', key = '-FARM_MANAGER-', default = False, enable_events = True),
					sg.Radio(tr.getTrans('at_null'), '-LEVEL-', key = '-AT_NULL-', default = False, enable_events = True),
					sg.Radio(tr.getTrans('custom'), '-LEVEL-', key = '-CUSTOM-', default = False, enable_events = True),
					sg.Checkbox(tr.getTrans('start_vehicles'), key = '-STARTVEHICLES-', disabled = True)
				],
				[	sg.Text(tr.getTrans('start_stop')),
					sg.Radio(tr.getTrans('yes'), '-STARTSTOP-', key = '-STARTSTOP_Y-', default = True, enable_events = True),
					sg.Radio(tr.getTrans('no'), '-STARTSTOP-', key = '-STARTSTOP_N-', default = False, enable_events = True)],
				[	sg.Text(tr.getTrans('auto_motor')),
					sg.Radio(tr.getTrans('yes'), '-AUTOMOTOR-', key = '-AUTOMOTOR_Y-', default = True, enable_events = True),
					sg.Radio(tr.getTrans('no'), '-AUTOMOTOR-', key = '-AUTOMOTOR_N-', default = False, enable_events = True)],
				[	sg.Text(tr.getTrans('plowing_requ')),
					sg.Radio(tr.getTrans('yes'), '-PLOWREQU-', key = '-PLOWREQU_Y-', default = False, enable_events = True),
					sg.Radio(tr.getTrans('no'), '-PLOWREQU-', key = '-PLOWREQU_N-', default = True, enable_events = True)],
				[	sg.Text(tr.getTrans('fuel_use')),
					sg.Radio(tr.getTrans('less'), '-FUELUSE-', key = '-FUELUSE_L-', default = True, enable_events = True),
					sg.Radio(tr.getTrans('normal'), '-FUELUSE-', key = '-FUELUSE_N-', default = False, enable_events = True),
					sg.Radio(tr.getTrans('many'), '-FUELUSE-', key = '-FUELUSE_H-', default = False, enable_events = True)],
				[	sg.Text(tr.getTrans('helper_fuel')),
					sg.Radio(tr.getTrans('yes'), '-H_FUEL-', key = '-H_FUEL_Y-', default = True, enable_events = True),
					sg.Radio(tr.getTrans('no'), '-H_FUEL-', key = '-H_FUEL_N-', default = False, enable_events = True)],
				[	sg.Text(tr.getTrans('helper_seeds')),
					sg.Radio(tr.getTrans('yes'), '-H_SEED-', key = '-H_SEED_Y-', default = True, enable_events = True),
					sg.Radio(tr.getTrans('no'), '-H_SEED-', key = '-H_SEED_N-', default = False, enable_events = True)],
				[	sg.Text(tr.getTrans('helper_fertilizer')),
					sg.Radio(tr.getTrans('yes'), '-H_FERTI-', key = '-H_FERTI_Y-', default = True, enable_events = True),
					sg.Radio(tr.getTrans('no'), '-H_FERTI-', key = '-H_FERTI_N-', default = False, enable_events = True)],
				[	sg.Text(tr.getTrans('helper_slurry')),
					sg.Radio(tr.getTrans('no'), '-H_SLURRY-', key = '-H_SLURRY_1-', default = False, enable_events = True),
					sg.Radio(tr.getTrans('yes'), '-H_SLURRY-', key = '-H_SLURRY_2-', default = True, enable_events = True)],
				[	sg.Text(tr.getTrans('helper_manure')),
					sg.Radio(tr.getTrans('no'), '-H_MANURE-', key = '-H_MANURE_1-', default = False, enable_events = True),
					sg.Radio(tr.getTrans('yes'), '-H_MANURE-', key = '-H_MANURE_2-', default = True, enable_events = True)],
				[	sg.Text(tr.getTrans('difficulty')),
					sg.Radio(tr.getTrans('simple'), '-DIFFI-', key = '-DIFFI_S-', default = True, enable_events = True),
					sg.Radio(tr.getTrans('normal'), '-DIFFI-', key = '-DIFFI_N-', default = False, enable_events = True),
					sg.Radio(tr.getTrans('hard'), '-DIFFI-', key = '-DIFFI_H-', default = False, enable_events = True)],
				[	sg.Text(tr.getTrans('eco_difficulty')),
					sg.Radio(tr.getTrans('simple'), '-ECO-', key = '-ECO_S-', default = True, enable_events = True),
					sg.Radio(tr.getTrans('normal'), '-ECO-', key = '-ECO_N-', default = False, enable_events = True),
					sg.Radio(tr.getTrans('hard'), '-ECO-', key = '-ECO_H-', default = False, enable_events = True)],
				[	sg.Text(tr.getTrans('money')),
					sg.Input('100000', key = '-MONEY-', enable_events = True)],
				[	sg.Text(tr.getTrans('playername')),
					sg.Input('Horst', key = '-NICK-')],
				[	sg.Button(tr.getTrans('done'), key = '-SAVE-')]
	]
	sg_settings = {}

	window = sg.Window('FarmingSimulatorLauncher', layout, finalize = True, location = (50, 50), disable_close = True)

	while True:
		event, values = window.read()
		#print(event, values)
		if event == sg.WIN_CLOSED or event == '-EXIT-':
			sg_settings = {}
			break
		elif event == '-NEW_FARMER-':
			window['-STARTVEHICLES-'].update(disabled = True)
			window['-STARTVEHICLES-'].update(False)			
			
			window['-STARTSTOP_Y-'].update(value = True)
			window['-AUTOMOTOR_Y-'].update(value = True)
			window['-PLOWREQU_N-'].update(value = True)
			window['-FUELUSE_L-'].update(value = True)
			window['-H_FUEL_Y-'].update(value = True)
			window['-H_SEED_Y-'].update(value = True)
			window['-H_FERTI_Y-'].update(value = True)
			window['-H_SLURRY_2-'].update(value = True)
			window['-H_MANURE_2-'].update(value = True)
			window['-DIFFI_N-'].update(value = True)
			window['-ECO_N-'].update(value = True)
			window['-MONEY-'].update(value = '100000')

		elif event == '-FARM_MANAGER-':
			window['-STARTVEHICLES-'].update(disabled = True)
			window['-STARTVEHICLES-'].update(False)

			window['-STARTSTOP_Y-'].update(value = True)
			window['-AUTOMOTOR_Y-'].update(value = True)
			window['-PLOWREQU_Y-'].update(value = True)
			window['-FUELUSE_N-'].update(value = True)
			window['-H_FUEL_Y-'].update(value = True)
			window['-H_SEED_Y-'].update(value = True)
			window['-H_FERTI_Y-'].update(value = True)
			window['-H_SLURRY_2-'].update(value = True)
			window['-H_MANURE_2-'].update(value = True)
			window['-DIFFI_N-'].update(value = True)
			window['-ECO_N-'].update(value = True)
			window['-MONEY-'].update(value = '1500000')

		elif event == '-AT_NULL-':
			window['-STARTVEHICLES-'].update(disabled = True)
			window['-STARTVEHICLES-'].update(False)

			window['-STARTSTOP_N-'].update(value = True)
			window['-AUTOMOTOR_N-'].update(value = True)
			window['-PLOWREQU_Y-'].update(value = True)
			window['-FUELUSE_H-'].update(value = True)
			window['-H_FUEL_N-'].update(value = True)
			window['-H_SEED_N-'].update(value = True)
			window['-H_FERTI_N-'].update(value = True)
			window['-H_SLURRY_1-'].update(value = True)
			window['-H_MANURE_1-'].update(value = True)
			window['-DIFFI_H-'].update(value = True)
			window['-ECO_H-'].update(value = True)
			window['-MONEY-'].update(value = '500000')

		elif event == '-SAVE-':
			if values['-NEW_FARMER-']:
				sg_settings['level'] = 'nf'
			elif values['-FARM_MANAGER-']:
				sg_settings['level'] = 'fm'
			elif values['-AT_NULL-']:
				sg_settings['level'] = 'an'
			else:
				if values['-STARTVEHICLES-']:
					sg_settings['level'] = 'c_w'
				else:
					sg_settings['level'] = 'c_wo'

			if values['-STARTSTOP_Y-']:
				sg_settings['stopAndGoBraking'] = 'true'
			else:
				sg_settings['stopAndGoBraking'] = 'false'

			if values['-AUTOMOTOR_Y-']:
				sg_settings['automaticMotorStartEnabled'] = 'true'
			else:
				sg_settings['automaticMotorStartEnabled'] = 'false'

			if values['-PLOWREQU_Y-']:
				sg_settings['plowingRequiredEnabled'] = 'true'
			else:
				sg_settings['plowingRequiredEnabled'] = 'false'

			if values['-FUELUSE_L-']:
				sg_settings['fuelUsage'] = '1'
			elif values['-FUELUSE_L-']:
				sg_settings['fuelUsage'] = '2'
			else:
				sg_settings['fuelUsage'] = '3'

			if values['-H_FUEL_Y-']:
				sg_settings['helperBuyFuel'] = 'true'
			else:
				sg_settings['helperBuyFuel'] = 'false'

			if values['-H_SEED_Y-']:
				sg_settings['helperBuySeeds'] = 'true'
			else:
				sg_settings['helperBuySeeds'] = 'false'

			if values['-H_FERTI_Y-']:
				sg_settings['helperBuyFertilizer'] = 'true'
			else:
				sg_settings['helperBuyFertilizer'] = 'false'

			if values['-H_SLURRY_1-']:
				sg_settings['helperSlurrySource'] = '1'
			elif values['-H_SLURRY_2-']:
				sg_settings['helperSlurrySource'] = '2'
			else:
				sg_settings['helperSlurrySource'] = '3'

			if values['-H_MANURE_1-']:
				sg_settings['helperManureSource'] = '1'
			elif values['-H_SLURRY_2-']:
				sg_settings['helperManureSource'] = '2'
			else:
				sg_settings['helperManureSource'] = '3'

			if values['-DIFFI_S-']:
				sg_settings['difficulty'] = '1'
			elif values['-DIFFI_N-']:
				sg_settings['difficulty'] = '2'
			else:
				sg_settings['difficulty'] = '3'

			if values['-ECO_S-']:
				sg_settings['economicDifficulty'] = '1'
			elif values['-ECO_N-']:
				sg_settings['economicDifficulty'] = '2'
			else:
				sg_settings['economicDifficulty'] = '3'

			sg_settings['money'] = values['-MONEY-']
			sg_settings['nick'] = values['-NICK-']
			break
		else:
			window['-CUSTOM-'].update(value = True)
			window['-STARTVEHICLES-'].update(disabled = False)
	window.close()
	return sg_settings

def saveSaveGame(values, update, money):
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

			# create / add files to sg folder
			""" sg_settings = setSavegameSettings()

			if values['-MAP-'] in se.getInternalMaps():
				base_path = se.getSettings('fs_path').replace('FarmingSimulator2022.exe', '').replace('FarmingSimulator2019.exe', '')
				data_path = base_path + 'data/maps/' + maps[values['-MAP-']] + '/'
				for f in required_files:
					shutil.copyfile(data_path + 'data' + os.sep + f, p + os.sep + f)
				
				dem_file = data_path + 'data/map_dem.png'

				defaultvehicles_xml = data_path + 'vehicles.xml'
				createVehiclesXML(ET.parse(defaultvehicles_xml).findall('vehicle'), dem_file, p, sg_settings['level'])
				
				defaultplaceables_xml = data_path + 'placeables.xml'
				createPlaceablesXML(ET.parse(defaultplaceables_xml).findall('placeable'), p, sg_settings['level'])
				
				defaultitems_xml = data_path + 'items.xml'
				createItemsXML(ET.parse(defaultitems_xml).findall('item'), p, sg_settings['level'])
				
				defaultfarmlands_xml = data_path + 'farmlands.xml'
				createFarmlandXML(ET.parse(defaultfarmlands_xml), p, sg_settings['level'])

				map_i3d_str = ''
				with open(data_path + 'map.i3d', 'r') as f:
					map_i3d_str = f.read().rstrip()
				createFieldsXML(map_i3d_str, p)

				mapId = maps[values['-MAP-']]

			else:
				with zipfile.ZipFile(se.getSettings('all_mods_path') + os.sep + maps[values['-MAP-']]) as z:
					moddesc_xml = ET.fromstring(z.read('modDesc.xml').decode('utf8').strip())
					map_xml_path = moddesc_xml.find('maps/map').attrib['configFilename']
					data_path = os.path.split(map_xml_path)[0] + '/'
					for f in required_files:
						try:
							with open(p + os.sep + f, 'wb') as out:
								out.write(z.read(data_path + 'data/' + f))
						except KeyError:
							os.remove(p + os.sep + f)
					
					map_i3d = ET.fromstring(z.read(map_xml_path)).find('filename').text
					i3d_files = ET.fromstring(z.read(map_i3d)).find('Files')
					for f in i3d_files:
						if f.attrib['fileId'] == '1':
							dem_file = f.attrib['filename']
							break
					
					defaultvehicles_xml = moddesc_xml.find('maps/map').attrib['defaultVehiclesXMLFilename']
					dem_png_extracted = z.extract(data_path + dem_file, path = se.fsl_config_path)
					try:
						createVehiclesXML(ET.fromstring(z.read(defaultvehicles_xml).decode('utf8').strip()), se.fsl_config_path + os.sep + data_path + os.sep + dem_file, p, sg_settings['level'])
					except ET.ParseError:
						sg.popup(tr.getTrans('broken_map').format(values['-MAP-']), title = tr.getTrans('broken_map_title'), location = (50, 50))
						shutil.rmtree(p)
						shutil.rmtree(p + '_Backup')
						removeSaveGame(values['-TITLE-'], False)
						return False
					
					defaultplaceables_xml = moddesc_xml.find('maps/map').attrib['defaultPlaceablesXMLFilename']
					try:
						createPlaceablesXML(ET.fromstring(z.read(defaultplaceables_xml).decode('utf8').strip()), p, sg_settings['level'], maps[values['-MAP-']])
					except ET.ParseError:
						sg.popup(tr.getTrans('broken_map').format(values['-MAP-']), title = tr.getTrans('broken_map_title'), location = (50, 50))
						shutil.rmtree(p)
						shutil.rmtree(p + '_Backup')
						removeSaveGame(values['-TITLE-'], False)
						return False
					
					defaultitems_xml= moddesc_xml.find('maps/map').attrib['defaultItemsXMLFilename']
					try:
						createItemsXML(ET.fromstring(z.read(defaultitems_xml).decode('utf8').strip()), p, sg_settings['level'])
					except ET.ParseError:
						sg.popup(tr.getTrans('broken_map').format(values['-MAP-']), title = tr.getTrans('broken_map_title'), location = (50, 50))
						shutil.rmtree(p)
						shutil.rmtree(p + '_Backup')
						removeSaveGame(values['-TITLE-'], False)
						return False
					
					defaultfarmlands_xml = ET.fromstring(z.read(data_path + 'map.xml').decode('utf8').strip()).find('farmlands').attrib['filename']
					try:
						createFarmlandXML(ET.fromstring(z.read(defaultfarmlands_xml).decode('utf8').strip()), p, sg_settings['level'])
					except ET.ParseError:
						sg.popup(tr.getTrans('broken_map').format(values['-MAP-']), title = tr.getTrans('broken_map_title'), location = (50, 50))
						shutil.rmtree(p)
						shutil.rmtree(p + '_Backup')
						removeSaveGame(values['-TITLE-'], False)
						return False

					createFieldsXML(z.read(data_path + 'map.i3d').decode('utf8').strip(), p)

					mapId = maps[values['-MAP-']].split('!')[1].replace('.zip', '.SampleModMap')

			createFarmXML(p, sg_settings['money'], sg_settings['nick'])

			shutil.copyfile(se.resource_path('careerSavegame.xml'), p + os.sep + 'careerSavegame.xml')
			careersavegame = ET.parse(p + os.sep + 'careerSavegame.xml')
			careersavegame.find('settings/savegameName').text = values['-TITLE-']
			careersavegame.find('settings/creationDate').text = datetime.datetime.now().strftime('%Y-%m-%d')
			careersavegame.find('settings/saveDate').text = datetime.datetime.now().strftime('%Y-%m-%d')
			careersavegame.find('settings/saveDateFormatted').text = datetime.datetime.now().strftime('%d.%m.%Y')
			careersavegame.find('settings/mapId').text = mapId
			careersavegame.find('settings/mapTitle').text = values['-MAP-']
			careersavegame.find('settings/stopAndGoBraking').text = sg_settings['stopAndGoBraking']
			careersavegame.find('settings/automaticMotorStartEnabled').text = sg_settings['automaticMotorStartEnabled']
			careersavegame.find('settings/plowingRequiredEnabled').text = sg_settings['plowingRequiredEnabled']
			careersavegame.find('settings/fuelUsage').text = sg_settings['fuelUsage']
			careersavegame.find('settings/helperBuyFuel').text = sg_settings['helperBuyFuel']
			careersavegame.find('settings/helperBuySeeds').text = sg_settings['helperBuySeeds']
			careersavegame.find('settings/helperBuyFertilizer').text = sg_settings['helperBuyFertilizer']
			careersavegame.find('settings/helperSlurrySource').text = sg_settings['helperSlurrySource']
			careersavegame.find('settings/helperManureSource').text = sg_settings['helperManureSource']
			careersavegame.find('settings/difficulty').text = sg_settings['difficulty']
			careersavegame.find('settings/economicDifficulty').text = sg_settings['economicDifficulty']
			careersavegame.find('statistics/money').text = sg_settings['money']
			careersavegame.find('statistics/playTime').text = '0.100000'
			careersavegame.find('slotSystem').attrib['slotUsage'] = '1161'
			careersavegame.write(p + os.sep + 'careerSavegame.xml', xml_declaration = True, encoding = "UTF-8")"""
		except FileExistsError:
			sg.popup(str(se.getSettings('fs_game_data_path') + os.sep) + values['-TITLE-'] + '\n' + tr.getTrans('ssg_folder_exists'), title = tr.getTrans('ssg_title'), location = (50, 50))
			return False
	else:
		folder_name = hashlib.md5(values['-TITLE-'].encode()).hexdigest()
		data = db.get(doc_id = update)
		path = se.getSettings('fs_game_data_path') + os.sep + data['folder'] + os.sep + 'farms.xml'
		farms = ET.parse(path)
		for farm_l, m in money.items():
			for farm in farms.getroot():
				if farm.attrib['name'] == farm_l:
					farm.set('money', values[farm_l])
		with open(path, 'wb') as f:
			farms.write(f, xml_declaration = True, encoding = "UTF-8")
		db.update({"name": values['-TITLE-'], "folder": folder_name, "desc": values['-DESC-'], "map": maps[values['-MAP-']], "mods": modstoadd}, doc_ids = [update])
		if data['name'] != se.getSettings('fs_game_data_path') + os.sep + values['-TITLE-']:
			os.rename(se.getSettings('fs_game_data_path') + os.sep + data['folder'], se.getSettings('fs_game_data_path') + os.sep + folder_name)
			os.rename(se.getSettings('fs_game_data_path') + os.sep + data['folder'] + '_Backup', se.getSettings('fs_game_data_path') + os.sep + folder_name + '_Backup')
	if sg.popup_yes_no(tr.getTrans('exportsg').format(values['-TITLE-'])) == 'Yes':
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

def getMoney(title):
	path = se.getSettings('fs_game_data_path') + os.sep + getFolder(title) + os.sep + 'farms.xml'
	try:
		farms = ET.parse(path).getroot()
		money = {}
		for farm in farms:
			money[farm.attrib['name']] = int(float(farm.attrib['money']))
	except FileNotFoundError:
		money = {'no data': 0}
	return money

def guiNewSaveGame(title = None):
	global maps
	global mods
	exp = True
	maps_keys, mods_keys = getMods()
	money_layout = []
	money = {}
	if title != None:
		money = getMoney(title)
		if list(money.keys())[0] == 'no data':
			money_layout.append([sg.Text('')])
		else:
			for farm, m in money.items():
				money_layout.append([sg.Text(farm, size = (20,1)), sg.Input(m, size = (50,1), key = farm, enable_events = True)])

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
				[money_layout],
				[sg.Text(tr.getTrans('folder'), key = '-FOLDER_TEXT-', visible = False), sg.Button('', key = '-FOLDER-', visible = False)],
				[sg.Button(tr.getTrans('cancel'), key = '-EXIT-', size = (14, 1))]
	]
	
	window = sg.Window('FarmingSimulatorLauncher', layout, finalize = True, location = (50, 50))

	update_sg = -1
	if title != None:
		update_sg = TinyDB(se.games_json).get(Query().name == title).doc_id
		window['-MISS_TITLE-'].update(visible = True)
		window['-SEL_MOD-'].update(visible = True)
		window['-REM_MOD-'].update(visible = True)
		window['-MISS-'].update(values = addMissingMods(title), visible = True)
		window['-MAP-'].update(disabled = True)
		window['-FOLDER_TEXT-'].update(visible = True)
		window['-FOLDER-'].update(getFolder(title), visible = True)
		markMods(window, title)
	else:
		window['-EXPORT_SAVE-'].update(tr.getTrans('save'))
		exp = False

	while True:
		event, values = window.read()
		#print(event, values)
		if event == sg.WIN_CLOSED or event == '-EXIT-':
			break
		elif event == '-EXPORT_SAVE-':
			if exp:
				exportSGC(values['-TITLE-'])
			else:
				window.Hide()
				if saveSaveGame(values, update_sg, money):
					break
				window.UnHide()
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
		else:
			window['-EXPORT_SAVE-'].update(tr.getTrans('save'))
			exp = False
		
	window.close()

