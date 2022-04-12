<img src="src/logo.png" width="40"/>

# FarmingSimulatorLauncher
### German

Der FarmingSimulatorLauncher (FSL) soll das Verwalten der verschiedenen Spielstände und Mods vereinfachen und flexibler gestalten.  
  
Zur Verwaltung der Mods legt FSL einen eigenen Ordner an, in dem alle Mods, inkl. Mod-Maps, gespeichert werden.  
Es ist Möglich, von einem Mod oder einer Map mehrere Versionen in FSL zu importieren und in unterschiedlichen Savegames unterschiedliche Versionen zu nutzen.  
<span style="color:red">**!!!** Es ist aber weiterhin nicht möglich in einem Savegame unterschiedliche Versionen des selben Mods zu verwenden. **!!!**</span>  
FSL erzeugt für jedes Savegame eine Konfiguration. Die Konfiguration beinhaltet die verwendete Map, die verwendeten Mods, den Namen des Savegames ()erscheint später auch im LS), den Ordner in dem das Savegame gespeichert wird und die Beschreibung. Weiterhin legt FSL zu einem Savegame einen eigenen Savegameordner und einen eigenen Backup Ordner an. Somit gibt es, im Unterschied zum Landwirtschaftssimulator mehrere Backupordner.  

Er funktioniert sowohl mit dem LS19 als auch mit dem LS22 und es kann die Giants oder Steam Version genutzt werden. FSL läuft auf Windows PC's und MacOS.  

Beim Start eines Savegames, aus FSL heraus, wird das savegame1 angelegt und alle benötigten Mods in den LS-Modsordner verlinkt. Somit sind für LS nur die benötigten Mods sichtbar, es gibt bspw. nur eine Mod Map und es werden auch nur die zum Savegame definierten Skript Mods geladen.  
Nach dem Spielstart läuft FSL im Hintergrund weiter und synchronisiert die Savegame- und Backup-Ordner kontinuierlich.  
  
Ich habe versucht FSL, bzw. das Savegame- / Modhandling so stabil und sicher wie möglich zu machen.  
Am sichersten ist es, um zu spielen, Savegames zu verwalten und Mods hinzuzufügen, immer FSL zu nutzen. Sollte es trotzdem mal vorkommen, dass LS ohne FSL benutzt / gespielt wird, sollte FSL dies beim nächsten Start erkennen und versuchen die Änderungen zu importieren oder zu sichern.

<span style="color:red">**Ich übernehme ausdrücklich keine Gewähr für verloren gegangene / kaputte Savegame und / oder Mods.**  
Bitte sichert eure LS Savegames / Mods vor dem ersten Start von FSL.</span>

Der FSL ist kein Designglanzstück. Ich habe mehr Wert auf die Funktionalität gelegt. Besonders unter MacOS fällt dies auf.
<div style="page-break-after: always;"></div>  

<span style="color:red">**Achtung: Unter Windows muss FSL als Adminstrator gestartet werden, da sonst die Datei- / Ordneroperationen nicht möglich sind.**</span> Siehe **Tipps - Administratorrechte bekommen**

### English

The goal of the FarmingSimulatorLauncher (FSL) is to simplify the savegame and mod management and make it more flexible.  
  
Therefore FSL is creating a special folder to store all mods including mod maps.  
It is possible to import different version of the same mod or map and use that different versions in different savegames. That makes it possible to test mods before change completely.  
<span style="color:red">**!!!** But it is still not possible to use different versions of one mod at the same savegame. **!!!**</span>  
FSL will create a configuration for every savegame. That configuration conatins the used map, the used mods, the name of the savegame (used later inside FS), the folder path where the savegame is stored and the description.
Additionally FSL is creating an own folder and also an own backup folder for every savegame. So there wil be plenty backup folders instead of one for all.  

FSL is working with FS19 and FS22 and can be used with Giants or Steam installation. It is running on Windows PC's and MacOS.  

When Farming Simulator is started by FSL, FSL is creating the savegame1 and links all required mods into the FS mods folder. So only the required mods are visible for FS. There is for example only one map file at the mods folder and not all existing script mods will be loaded by FS, only the required.  
FSL is running in background after game start and is syncing the savegame and backup folder continuously.  

I tried to make FSL as stable and save at possible.
The safest way is to use FSL to start the game, manage savegames and mods. Should it happen that FS is started without FSL, should FSL recognize that at the next start and try to import or backup the changes.

<span style="color:red">**I do not assume responsibility for lost savegames and / or mods.** Please backup your original savegames and mods before you use FSL the first time.</span>

The FSL isn't a design highlight. The focus was mor on functionality. That is mostly visible at MacOS.  
<div style="page-break-after: always;"></div>  

<span style="color:red">**Attention: FSL must be started with administrator rights at windows, otherwise the required file and folder operations aren't possible.**</span> See **Recommendation - Get administrator rights**

## FSL tests
* Windows 10, local Installation, LS19 - <span style="color:green">pass</span>
* Windows 10, Steam Installation, LS19 - <span style="color:green">pass</span>
* Windows 10, local Installation, LS22 - <span style="color:green">pass</span>
* Windows 10, Steam Installation, LS22 - <span style="color:blue">untested</span>
* MacOS Catalina, local Installation, LS19 - <span style="color:green">pass</span>
* MacOS Catalina, Steam Installation, LS19 - <span style="color:green">pass</span>
* MacOS Catalina, local Installation, LS22 - <span style="color:blue">untested</span>
* MacOS Catalina, local Installation, LS22 - <span style="color:blue">untested</span>

Fehler bitte über [GitHub](https://github.com/Dueesberch/FarmingSimulatorLauncher/issues/new) melden und Label *bug* auswählen.
Please report bugs at [GitHub](https://github.com/Dueesberch/FarmingSimulatorLauncher/issues/new) with label *bug*.

## Geplante Erweiterungen / Backlog
* Tooltips zu Feldern hinzufügen / add tooltips to fields
* Laden alter Spielstände / load savegame backups
* Unbenutzte Mods finden / find unused mods
* Beim Import von Mods prüfen ob diese zur gewählten Version passen / check if mod fitting selected FS version
* Beim Anlegen einer neuen Konfiguration den savegame Ordner mit default Dateien erstellen / add default files when new savegame is created
* Verwalten von Ordnern wie modsettings etc. / manage folders like modsettings
* Mod Updates verwalten / mod updates managment
* Einstellung LS Vorspann abschalten / disable FS intro at start by settings
* Einstellung savegame direkt starten in LS (Singleplayer) / start savegame directly (single player)
* Mods in careerSavegame.xml entsprechend der Konfuguration setzen (Einschalten in LS entfällt) / set mods at careersavegame.xml
* Karte updaten / update map
* Konfiguration kopieren / copy configuration
* orginal LS Setup wieder herstellen / remove FSL
* Nur Mods auflisten die noch nicht importiert wurden / list only mods not already imported
* Französische Übersetzung / french translation

Gewünschte Erweiterungen bitte über [GitHub](https://github.com/Dueesberch/FarmingSimulatorLauncher/issues/new) melden und Label *feature request* auswählen.  
Feature requests at [GitHub](https://github.com/Dueesberch/FarmingSimulatorLauncher/issues/new) with label *feature request*
  
## Falls du mich und meine Arbeit unterstützen möchtest > [Spende](https://www.paypal.com/donate/?hosted_button_id=ZR4EGNDAVD4Q4)  
## If you want to donate my work > [Donate](https://www.paypal.com/donate/?hosted_button_id=ZR4EGNDAVD4Q4)
