<img src="src/logo.png" width="40"/>

# FarmingSimulatorLauncher

Der FarmingSimulatorLauncher (FSL) soll das Verwalten der verschiedenen Spielstände und Mods vereinfachen.  
Er funktioniert sowohl mit dem LS19 als auch mit dem LS22 und es kann die Giants oder Steam Version genutzt werden. FSL läuft auf PC und MacOS.  
  
Zur Verwaltung der Mods legt FSL einen eigenen Ordner an, in dem alle Mods, inkl. Mod-Maps, gespeichert werden.  
Es ist Möglich, von einem Mod oder einer Map mehrere Versionen in FSL zu importieren und in unterschiedlichen Savegames unterschiedliche Versionen zu nutzen.  
!!! Es ist aber weiterhin nicht möglich in einem Savegame unterschiedliche Versionen des selben Mods zu verwenden. !!!  
Weiterhin erzeugt FSL für jedes Savegame einen eigenen Ordner und einen dazugehörigen Backup Ordner. Somit gibt es, im Unterschied zum Landwirtschaftssimulator mehrere Backupordner.  
Beim Start eines Savegames, aus FSL heraus, wird das savegame1 angelegt und alle benötigten Mods in den LS-Modsordner verlinkt. Somit sind für LS nur die benötigten Mods sichtbar.  
Nach dem Spielstart läuft FSL im Hintergrund weiter und syncronisiert die Savegame- und Backup-Ordner kontinuierlich.  
  
Ich habe versucht FSL, bzw. das Savegame- / Modhandling so stabil und sicher wie möglich zu machen.  
Der sicherste Weg ist es immer FSL zu nutzen, um zu spielen, Savegames zu verwalten und Mods hinzuzufügen. Sollte es vorkommen, dass LS ohne FSL benutzt / gespielt wird, sollte FSL dies beim nächsten Start erkennen und versuchen die Änderungen zu importieren oder zu sichern.

**Ich übernehme ausdrücklich keine Gewähr für verloren gegangene / kaputte Savegame und / oder Mods.**
Bitte sichert eure Savegames / Mods vor dem ersten Start von FSL.

Der FSL ist kein Designglanzstück. Ich habe mehr Wert auf die Funktionalität gelegt. Besonders unter MacOS fällt dies auf, da MacOS der GUI-Entwicklung nicht viele Möglichkeiten bietet.


## FSL Tests
* Windows 10, lokale Installation, LS19 - 
* Windows 10, Steam Installation, LS19 - 
* Windows 10, lokale Installation, LS22 - 
* Windows 10, Steam Installation, LS22 - <span style="color:blue">ungetestet</span>
* MacOS Catalina, lokale Installation, LS19 - 
* MacOS Catalina, Steam Installation, LS19 - 
* MacOS Catalina, lokale Installation, LS22 - <span style="color:blue">ungetestet</span>
* MacOS Catalina, lokale Installation, LS22 - <span style="color:blue">ungetestet</span>

Fehler bitte über [GitHub](https://github.com/Dueesberch/FarmingSimulatorLauncher/issues/new) melden und Label *bug* auswählen.

## Geplante Erweiterungen (Backlog)
* Tooltips zu Feldern hinzufügen
* Laden alter Spielstände
* Savegames teilen
* Prüfen ob ein Mod von einem Savegame benutzt wird beim Löschen
* Unbenutzte Mods finden
* Beim Import von Mods prüfen ob diese zur gewählten Version passen
* Beim Anlegen eines neuen Savegames den savegame Ordner mit default Dateien erstellen
* Verwalten von Ordnern wie modsettings etc.
* Mods (Qelldatei) nach import Moddatei löschen anstatt gesamten Ordner
* Mod Updates verwalten
* Einstellung LS Vorspann abschalten
* Einstellung savegame direkt starten in LS
* Mods in careerSavegame.xml entsprechend der Konfuguration setzen
* Karte updaten
* Savegame kopieren

Gewünschte Erweiterungen bitte über [GitHub](https://github.com/Dueesberch/FarmingSimulatorLauncher/issues/new) melden und Label *feature request* auswählen.  
  
## Falls du mich und meine Arbeit unterstützen möchtest > [Spende](https://www.paypal.com/donate/?hosted_button_id=ZR4EGNDAVD4Q4)  
