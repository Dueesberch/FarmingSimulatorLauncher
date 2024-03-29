import settings as se

dictionary = {
    "en": {
        "analyze": "Analyze files for import. Please wait.",
        "at_null": "Start at null",
        "backup": "Backup",
        "backup_folders_title": "Backup Folder",
        "backup_folder_text": "Folder\n \"{}\" \nmoved to\n \"{}_fsl_bak\"\n",
        "cancel": "Cancel",
        "change": "Change",
		"careful": "Be careful to change map. Please check change log of map if new savegame is required. If so, please do not update your map.",
        "create_upload_folder": "Create folder with all required mods for upload? eG dedi server?",
        "cant_rem_mod": "Mod \"{}\" still in use in \"{}\". Can't remove.",
        "copy": "Copy",
        "description": "Description",
        "delete": "Do you really want to remove selected savegame? Savegame and backup folder will be removed.",
        "dupes_found": "The following mods are selected in different versions\n\n{}\nOnly one version is able.",
        "dupes_title": "Found duplicates",
        "duplicate_mod_found": "Duplicated mod \"{}\" found. FSL will fix that.",
        "def_fs19": "Default FS19 path",
        "def_fs22": "Default FS22 path",
        "def_fs19_steam": "Default FS19 Steam path",
        "def_fs22_steam": "Default FS22 Steam path",
        "def_sg_fs19": "Default FS19 savegame folder path",
        "def_sg_fs22": "Default FS22 savegame folder path",
        "def_map": "FS standard map",
        "different": "Different",
        "donate": "If you like my work and wan't to support me - click here",
        "exit": "Exit",
        "empty_fs_path": "Please set farming simulator executable.",
        "empty_fs_gd_path": "Please set farming simulator gaming data folder.",
        "empty_all_mods_path": "Please set all mods folder.",
        "error": "Error",
        "exe_not_found": "{} not found",
        "export": "Export",
        "exportsg": "Export savegame configuration \"{}\"?",
        "existing_mods": "Already imported mods",
        "exists": "Exists",
        "farm_manager": "Farm manager",
        "file_not_found": "File not found",
        "found_new_mod": "New mod \"{}\" found. Import into all mods folder? Otherwise it is moved to mods_fsl_bak.",
        "fsl_bak_exists": "_fsl_bak already exists. Please rename or remove",
        "fsl_init": "Init running. Please wait.",
        "folder": "Folder",
        "get_fs_game_data_path": "Select farming simulator gaming data folder.",
        "get_all_mods_path": "Select folder for all mods",
        "get_fs_path": "Select farming simulator executable.",
        "get_mods": "Look for mods at the selected folder",
        "get_mod_path": "Select mod folder to import from",
        "get_sg_path": "Select savegame folder to import",
        "get_sgb_path": "Select savegame backup folder to import",
        "ghostmap": "Ghostmap",
        "illegal_path": "The fsl_all_mods can't be placed inside the FS mods folder. FS mods will be reset at every FSL start and all mods will be removed.\nPlease choose different one. eg base folder \"{}\"",
        "init_failed": "FSL init failed. Please check trouble shooting section at manual",
        "import": "Import",
        "import_failed": "Moddesc from \"{}\" not okay (not well-formed). Name and version not readable. Import not possible",
        "import_mods_init": "There are already mods in {}\nImport them?",
        "import_more_mods": "Import more mods from different folder?",
        "import_more_sg": "Import additional savegame?",
        "import_sg_init": "There is {} in {}\nImport that?",
        "import_sgc_init": "Change configuration found \"{}\" in \"{}\"\nOverwrite existing?",
        "importable_mods": "Available mods to import",
        "invalid_path": "Invalid path to gaming data folder. No game.xml found",
        "map": "Map",
		"map_change": "Map changed",
        "map_not_found": "Map file \"{}\" in Version \"{}\" not found",
        "miss_path": "Path invalid",
        "mod_not_found": "Mod {} not in {}\nStart anyway?",
        "missing_mod": "There are mods at the savegame which are not imported yet. Please import later. Missing mods listed at 'Change' for the savegame.",
        "missing": "Missing",
        "missing_map": "Map \"{}\" in version \"{}\" not found. Please import later.",
		"missing_dep": "Missing dependency. Please add mod \"{}\" to FSL first.",
        "moved": "Mod moved to \"{}\"",
		"mods_db_broken": "Mods DB is broken. FSL will be restarted to rebuild DB.",
        "new": "New",
        "new_mod": "New mod",
        "new_release": "There is a new version of FarmingSimulatorLauncher. Click here to get.",
        "not_found_folder": "Path \"{}\" not found",
        "no_savegame_files": "No savegame file found.",
        "no": "no",
        "no_mod_found": "None importable mod found. Maybe all already imported or not fitting the FS version.",
        "numeric": "Backups to keep must be an integer.",
        "new_farmer": "New farmer",
        "overwrite": "Overwrite",
        "remove": "Remove",
        "remove_title": "Remove folder",
        "remove_src_folder": "Shall \"{}\" be removed?",
        "remember": "Use always the selected FS version.",
        "rem_source": "Remove source file \"{}\"?",
        "reset_default": "Reset all to default FS.",
        "reset_popup": "Really reset to default mods and savegame folders?",
        "reset_thanks": "Thanks for trying FSL.",
        "start": "Start",
        "settings": "Settings",
        "save": "Save",
        "select_mods": "Mark used mods",
        "select_sgs": "Select savegames, to update or to add mod {}",
        "set_lang": "Select language",
        "sg_title": "FSL savegame title",
        "sgb_title": "Select backups to import",
        "sg_changed": "Savegame1 changed. Import as new FSL savegame or\nmove to \"savegame1_{}\" or\noverwrite existing savegame or\nremove.",
        "sg_overwrite": "Overwrite",
        "sg_type_new_farmer": "New farmer",
        "sg_type_farm_manager": "Farm manager",
        "sg_type_start_at_null": "Start at null",
        "sgb_changed": "SavegameBackup changed. It will be moved to \"savegameBackup_{}\".",
        "ssg_exists": "Savegame title already used. Please choose different one.",
        "ssg_folder_exists": "Savegame folder with that title exists. Please choose different one or remove.",
        "ssg_backup_folder_exists": "Savegame Backup folder with that title exists. Please choose different title, rename folder or remove.",
        "ssg_title": "Title exists",
        "ssg_title_char": "Forbidden character",
        "ssg_wrong_char": "Exclamationmark (!) not allowed at title.",
        "ssg_title_title": "Forbidden title",
        "ssg_wrong_title": "Title savegame1 not allowed.",
        "ssg_name_empty": "Title must be set.",
        "ssg_map_empty": "Map must be set.",
        "ssg_title_empty": "Missing",
        "storeat": "Store at",
        "sure_start_backup": "Are you sure to start an old savegame?", 
        "sg_import_tab": "FS savegame",
        "sgc_file": "FSL configuration file to import",
        "sgc_import_tab": "FSL configuration",
        "sgc_export": "Folder to store export file.",
        "sgc_mods_export": "Folder to store mods for export.",
        "sgc_mods_export_missing": "Some mods can't be prepared for export.\nPlease check \'Missing\'.",
        "skip_intro": "Skip intro at FS start",
        "start_direct": "Start direct into savegame",
        "tt_gaLbMods": "click: select one item | strg + click: multiselect | shift + click: select all between first and second click | strg + click at selected entry to unselect",
        "to_keep": "Backups to keep",
        "unused_mods": "Unused mods",
		"updatable": "updatable",
        "wait_for_import": "Import running. Please wait",
        "yes": "yes",
        "custom": "Custom",
        "start_stop": "TODO: trans",
        "auto_motor": "TODO: trans",
        "plowing_requ": "TODO: trans",
        "fuel_use": "TODO: trans",
        "helper_fuel": "TODO: trans",
        "helper_seeds": "TODO: trans",
        "helper_fertilizer": "TODO: trans",
        "helper_slurry": "TODO: trans",
        "helper_manure": "TODO: trans",
        "difficulty": "TODO: trans",
        "eco_difficulty": "TODO: trans",
        "money": "TODO: trans",
        "less": "Gering",
        "normal": "Normal",
        "many": "Hoch",
        "simple": "Einfach",
        "hard": "Schwierig",
        "start_vehicles": "Start equipment",
        "done": "Done",
        "playername": "Playername",
        "broken_map": "The used map \"{}\" seems to be brocken. You can try to create a new savegame inside FS and import afterwards.",
        "broken_map_title": "Map brocken",
		"version_dep": "Different versions of dependency {}. Which one to use?"
    },
    "de": {
        "analyze": "Suche Dateien für den Import. Einen Moment bitte.",
        "at_null": "Bei Null starten",
        "backup": "Sichern",
        "backup_folders_title": "Backup Ordner",
        "backup_folder_text": "Ordner\n \"{}\" \nverschoben nach\n \"{}_fsl_bak\"\n",
        "cancel": "Abbrechen",
        "change": "Ändern",
		"careful": "Sei vorsichtig. Prüfe den change log der Karte ob ein neues Savegame benötigt wird. Falls ja, solltest du die Karte nicht ändern.",
        "create_upload_folder": "Ordner mit benötigten Mods anlegen für Upload? (zB für Dedi Server)",
        "cant_rem_mod": "Mod \"{}\" wird noch in \"{}\" benutzt. Kann nicht entfernt werden.",
        "copy": "Kopie",
        "description": "Beschreibung",
        "delete": "Möchtest du das ausgewählte Savegame wirklich löschen? Savegame and Backup Ordner werden gelöscht.",
        "dupes_found": "Die folgenden Mods wurden in unterschiedlichen Versionen ausgewählt\n\n{}\nNur eine Version ist möglich.",
        "dupes_title": "Duplicate gefunden",
        "duplicate_mod_found": "Mod \"{}\" ist mehrfach vorhanden. FSL räumt auf.",
        "def_fs19": "Standard LS19 Pfad",
        "def_fs22": "Standard LS22 Pfad",
        "def_fs19_steam": "Standard LS19 Steam Pfad",
        "def_fs22_steam": "Standard LS22 Steam Pfad",
        "def_sg_fs19": "Standard LS19 Savegames Ordner Pfad",
        "def_sg_fs22": "Stardard LS22 savegames Ordner Pfad",
        "def_map": "LS Standard Karte",
        "different": "Unterschiedlich",
        "donate": "Wenn dir meine Arbeit gefällt und du mich unterstützen möchtest - Klicke hier",
        "exit": "Beenden",
        "empty_fs_path": "Bitte Pfad zu Landwirtschaftssimulator Exe setzen.",
        "empty_fs_gd_path": "Bitte Pfad zu Savegames Ordner setzen.",
        "empty_all_mods_path": "Bitte Pfad auswählen in dem FSL alle Mods speichern soll.",
        "error": "Fehler",
        "exe_not_found": "{} nicht gefunden",
        "export": "Export",
        "exportsg": "Savegamekonfiguration \"{}\" exportieren?",
        "exists": "Vorhanden",
        "farm_manager": "Farm manager",
        "file_not_found": "Datei nicht gefunden",
        "found_new_mod": "Neuen Mod \"{}\" gefunden. Importieren? Falls nicht wird er in mods_fsl_bak verschoben und kann später importiert werden.",
        "fsl_bak_exists": "_fsl_bak bereits vorhanden. Bitte umbenennen oder löschen",
        "fsl_init": "Starte FSL. Bitte warten.",
        "folder": "Ordner",
        "get_fs_game_data_path": "Landwirtschaftssimulator Savegames Ordner auswählen.",
        "get_all_mods_path": "Pfad für Alle-Mods-Ordner auswählen.",
        "get_fs_path": "Pfad zu Farmingsimulator exe auswählen",
        "get_mods": "Suche nach mods im angegebenen Ordner",
        "get_mod_path": "Mod Ordner auswählen aus dem importiert werden soll",
        "get_sg_path": "Savegame Ordner auswählen, welcher importiert werden soll",
        "get_sgb_path": "Savegame Backup Ordner auswählen, aus dem importiert werden soll",
        "ghostmap": "Geistermap",
        "illegal_path": "Der fsl_all_mods Ordner kann nicht im LS mods Ordner angelegt werden. LS mods wird bei jedem start zurück gesetzt und alle Mods werden gelöscht.\nBitte anderen Speicherort wählen. zB den Hauptordner \"{}\"",
        "init_failed": "FSL konnte nicht gestartet werden. Bitte Problembehebung in der Anleitung benutzen.",
        "import": "Importieren",
        "import_failed": "Moddesc von \"{}\" nicht in Ordnung (not well-formed). Name und Version kann nicht ausgelesen werden. Mod kann nicht importiert werden.",
        "import_mods_init": "Mods gefunden in {}\nImportieren?",
        "import_more_mods": "Weitere Mods aus anderen Ordnern importieren?",
        "import_more_sg": "Weiteres Savegame importieren?",
        "import_sg_init": "Savegame {} in {} gefunden\nImportieren?",
        "import_sgc_init": "Geänderte Konfiguration für \"{}\" in \"{}\" gefunden. Bestehende überschreiben?",
        "importable_mods": "Zum Import",
        "invalid_path": "Ungültiger Pfad zu Savegamesordnern. Keine game.xml gefunden",
        "existing_mods": "Bereits importierte Mods",
        "map": "Karte",
		"map_change": "Karte geändert",
        "map_not_found": "Karte \"{}\" in Version \"{}\" nicht gefunden",
        "miss_path": "Pfad fehlerhaft",
        "mod_not_found": "Mod {} nicht in {}\nTrotzdem starten?",
        "missing_mod": "Im Savegame verwendete Mods wurden noch nicht importiert. Bitte später importieren. Die fehlenden Mods werden unter 'Ändern' für das Savegame angezeigt.",
        "missing": "Fehlend",
        "missing_map": "Karte \"{}\" in Version \"{}\" nicht gefunden. Bitte später importieren.",
		"missing_dep": "Fehlende Abhängikeit. Bitte importiere mod \"{}\" in FSL zuerst.",
        "moved": "Mod verschoben nach \"{}\"",
		"mods_db_broken": "Mods DB ist fehlerhaft. FSL wird neu gestarted um die DB neu zu bauen.",
        "new_farmer": "Neuer Farmer",
        "new": "Neu",
        "new_mod": "Neuer Mod",
        "new_release": "Neue FarmingSimulatorLauncher Version verfügbar. Hier klicken zum herunterladen.",
        "not_found_folder": "Der angegebene Ordnerpfad \"{}\" wurde nicht gefunden",
        "no_savegame_files": "Der angegebene Ordner enthält keine savegame Dateien.",
        "no": "nein",
        "no_mod_found": "Kein importierbarer Mod gefunden. Entweder sind alle bereits importiert oder passen nicht zur gewählten LS Version.",
        "numeric": "Zu behaltende Backups muss eine Zahl sein.",
        "overwrite": "Überschreiben",
        "remove": "Löschen",
        "remove_title": "Lösche Ordner",
        "remove_src_folder": "Ordner \"{}\" löschen?",
        "remember": "Immer die gewählte LS Version benutzen.",
        "rem_source": "Quelldatei \"{}\" entfernen?",
        "reset_default": "Alles auf Standard LS zurücksetzen.",
        "reset_popup": "Soll der orginale Mods- und die Savegameordner wieder hergestellt werden?",
        "reset_thanks": "Danke, dass du FSL probiert hast.",
        "start": "Start",
        "settings": "Einstellungen",
        "save": "Speichern",
        "select_mods": "Benutzte Mods markieren",
        "select_sgs": "Savegames markieren, die geupdated bzw zu denen der Mod {} hinzugefügt werden soll.",
        "set_lang": "Sprache wählen",
        "sg_title": "FSL Savegame Titel",
        "sgb_title": "Zu importierende Backups wählen",
        "sg_changed": "Der savegame1 Ordner wurde seit dem letzten Mal verändert.\nAls neues FSL Savegame importieren oder\nnach \"savegame1_{}\" verschieben oder\nein bestehendes Savegame überschreiben oder\neinfach Löschen?.",
        "sg_overwrite": "Überschreiben",
        "sg_type_new_farmer": "Neuer Farmer",
        "sg_type_farm_manager": "Farmmanager",
        "sg_type_start_at_null": "Bei Null beginnen",
        "sgb_changed": "SavegameBackup Ordner geändert. Wird nach \"savegameBackup_{}\" verschoben.",
        "ssg_exists": "Savegame Titel bereits verwendet. Bitte einen anderen vergeben.",
        "ssg_folder_exists": "Savegame Ordner mit diesem Titel existiert bereits. Bitte einen anderen Titel verwenden, den Ordner umbenennen oder löschen.",
        "ssg_backup_folder_exists": "Savegame Backup Ordner mit dem Titel existiert bereits. Bitte einen anderen Titel verwenden, den Ordner umbenennen oder löschen.",
        "ssg_title": "Titel bereits verwendet",
        "ssg_title_char": "Zeichen",
        "ssg_wrong_char": "Doppelpunkt (:) ist nicht erlaubt im Titel.",
        "ssg_title_title": "Title",
        "ssg_wrong_title": "Titel savegame1 kann nicht verwendet werden.",
        "ssg_name_empty": "Titel darf nicht leer sein.",
        "ssg_map_empty": "Karte darf nicht leer sein.",
        "ssg_title_empty": "Fehlt",
        "storeat": "Speichern unter",
        "sure_start_backup": "Bist du sicher, dass du einen alten Spielstand laden möchtest?",
        "sg_import_tab": "LS Savegame",
        "sgc_file": "Import FSL Konfigurationsdatei",
        "sgc_import_tab": "FSL Konfiguration",
        "sgc_export": "Ordner in dem die Savegamekonfiguration für den Export gespeichert werden soll.",
        "sgc_mods_export": "Ordner in dem die Mods für den Export gespeichert werden sollen.",
        "sgc_mods_export_missing": "Einer oder mehrere Mods konnten nicht für den Export zur Verfügung gestellt werden.\nBitte \'Fehlend\' prüfen.",
        "skip_intro": "Intro nicht anzeigen beim LS Start",
        "start_direct": "Savegame direkt starten",
        "tt_gaLbMods": "klick: einen Eintrag auswählen, andere abwählen | strg + klick: mehrere Einträge auswählen | shift + klick: alle Einträge zwischen ersten und letzen Ausgewählten markieren | strg + klick auf markierten EIntrag entfernt Selektion",
        "to_keep": "Zu behaltende Backups",
        "unused_mods": "Unbenutze Mods",
		"updatable": "aktualisierbar",
        "wait_for_import": "Importiere. Bitte warten",
        "yes": "ja",
        "custom": "Benutzerdefiniert",
        "start_stop": "Stop-and-Go-Bremsung",
        "auto_motor": "Automatischer Motorstart",
        "plowing_requ": "Pflügen notwendig",
        "fuel_use": "Spritverbrauch",
        "helper_fuel": "Helferbetankung Kraftstoff",
        "helper_seeds": "Helferbetankung Saatgut",
        "helper_fertilizer": "Helferbetankung Dünger",
        "helper_slurry": "Helferbetankung Gülle",
        "helper_manure": "Helferbetankung Mist",
        "difficulty": "Schwierigkeit",
        "eco_difficulty": "Schwierigkeit Wirtschaft",
        "money": "Geld",
        "less": "Gering",
        "normal": "Normal",
        "many": "Hoch",
        "simple": "Einfach",
        "hard": "Schwer",
        "start_vehicles": "Startequipment",
        "done": "Fertig",
        "playername": "Spielername",
        "broken_map": "Die verwendete Map \"{}\" scheint defekte Dateien zu beinhalten. Du kannst versuchen ein neues Spiel direkt in LS zu erzeugen, und dieses dann importieren.",
        "broken_map_title": "Map defekt",
		"version_dep": "Verschiedene Versionen für Abhängigkeit {}. Welche soll benutzt werden?"
    }
}

def getTrans(string, lang = ''):
    if lang == '':
        return dictionary[se.getFslSettings('language')][string]
    else:
        return dictionary[lang][string]

def getLangs():
    return list(dictionary.keys())

def checkDict():
    for i in dictionary['de']:
        if not i in dictionary['en']:
            print(i)
    print('--------------')
    for i in dictionary['en']:
        if not i in dictionary['de']:
            print(i)
