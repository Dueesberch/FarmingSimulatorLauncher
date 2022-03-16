<img src="../src/logo.png" width="40"/>

# FarmingSimulatorLauncher

Der FarmingSimulatorLauncher (FSL) soll das Verwalten der verschiedenen Spielstände und Mods vereinfachen und flexibler gestalten.  
  
Zur Verwaltung der Mods legt FSL einen eigenen Ordner an, in dem alle Mods, inkl. Mod-Maps, gespeichert werden.  
Es ist Möglich, von einem Mod oder einer Map mehrere Versionen in FSL zu importieren und in unterschiedlichen Savegames unterschiedliche Versionen zu nutzen.  
<span style="color:red">!!! Es ist aber weiterhin nicht möglich in einem Savegame unterschiedliche Versionen des selben Mods zu verwenden. !!!</span>  
FSL erzeugt für jedes Savegame einen eigenen Ordner und einen dazugehörigen Backup Ordner. Somit gibt es, im Unterschied zum Landwirtschaftssimulator mehrere Backupordner.  

Er funktioniert sowohl mit dem LS19 als auch mit dem LS22 und es kann die Giants oder Steam Version genutzt werden. FSL läuft auf Windows PC's und MacOS.  

Beim Start eines Savegames, aus FSL heraus, wird das savegame1 angelegt und alle benötigten Mods in den LS-Modsordner verlinkt. Somit sind für LS nur die benötigten Mods sichtbar und es werden zum Beispiel nicht alle Skript Mods geladen.  
Nach dem Spielstart läuft FSL im Hintergrund weiter und syncronisiert die Savegame- und Backup-Ordner kontinuierlich.  
  
Ich habe versucht FSL, bzw. das Savegame- / Modhandling so stabil und sicher wie möglich zu machen.  
Am sichersten ist es, um zu spielen, Savegames zu verwalten und Mods hinzuzufügen, immer FSL zu nutzen. Sollte es trotzdem mal vorkommen, dass LS ohne FSL benutzt / gespielt wird, sollte FSL dies beim nächsten Start erkennen und versuchen die Änderungen zu importieren oder zu sichern.

<span style="color:red">**Ich übernehme ausdrücklich keine Gewähr für verloren gegangene / kaputte Savegame und / oder Mods.**  
Bitte sichert eure LS Savegames / Mods vor dem ersten Start von FSL.</span>

Der FSL ist kein Designglanzstück. Ich habe mehr Wert auf die Funktionalität gelegt. Besonders unter MacOS fällt dies auf.
<div style="page-break-after: always;"></div>  

## Allgemein
Beim Start erscheint zuerst die Auswahl, welche LS Version benutzt werden soll.  
<img src="../images/select_version_german.png" width="400"/>  
Sollte nur eine Version installiert sein oder soll nur eine Version von FSL verwaltet werden, kann, bevor die Version ausgewählt wird, der Haken bei "Immer die gewählte LS Version benutzen?" gesetzt werden. Dadurch erscheint der Auswahldialog zukünftig nicht mehr.  
Dies kann auch später in den Einstellungen eingestellt werden.  
Wenn der erste Start (Siehe *Erster Start*) erfolgreich durchlaufen wurde öffnet sich das Hauptfenster.  
<img src="../images/main_german.png" width="800"/>  
Im Dropdownmenü können die in FSL gespeicherten Savegames ausgewählt werden. Diese müssen vorher aus bestehenden Savegames importiert oder neu angelegt werden. Die Einträge im Dropdownmenü setzen sich dabei aus dem Savegamenamen und der verwendeten Map zusammen.  
Unter Beschreibung wird die während des Anlegens des Savegames eingetragene Beschreibung angezeigt.
### Tasten
#### ***Neu***
Anlegen einen neuen Savegames. Siehe *Savegame anlegen*
#### ***Importieren***
Importieren eines vorhanden Savegames. Siehe *Savegame importieren*
<div style="page-break-after: always;"></div>  

#### ***Ändern***
Ändern des ausgewählten Savegames. Taste wird eingeschaltet wenn ein Savegame ausgewählt wurde. Siehe *Savegame ändern*
#### ***Löschen***
Löschen des ausgewählten Savegames. Taste wird eingeschaltet wenn ein Savegame ausgewählt wurde. Siehe *Savegame löschen*
#### ***Mods***
Öffnet die Modverwaltung. Siehe *Mods*
#### ***Einstellungen***
Öffnet das Einstellungsmenü für FSL. Siehe *FSL Einstellungen*
#### ***Beenden***
Beendet FSL
#### ***Start***
Startet das ausgewähle Savegame. Taste wird eingeschaltet wenn ein Savegame ausgewählt wurde. Siehe *Savegame starten*
#### ***Update***
Öffnet die Webseite mit dem letzten FSL Release. Taste nur verfügbar wenn es eine neuere Version als die Benutzte gibt.
#### ***Spende***
Wenn man mich und meine Arbeit unterstützen möchte ... ;)

## Erster Start
Beim ersten Start müssen zuerst die Pfade gesetzt werden. Siehe hierzu *FSL Einstellungen*.  
Danach sucht FSL im angegebenen Ordner nach dem `mods`-Ordner. Dieser kann dann importiert werden. 
Wird der Import durchgeführt werden zuerst die Mods aus dem `mods` Ordner in den FSL Alle-Mods-Ordner importiert.  
<span style="color:red"> !!! Der orginale `mods` Ordner wird nach dem Import gelöscht. Dies ist nötig, da FSL bei jedem Spielstart einen mods Ordner erzeugt, der nur die benötigten Mods enthält !!!</span>  
Danach können weitere Mods aus anderen Ordnern importiert werden. Siehe *Mods importieren*  

Falls der Import abgelehnt wird, wird der `mods`-Ordner nach `mods_fsl_bak` verschoben.  
Danach sucht FSL im angegebenen Ordner nach savegame-Ordnern. Werden Entsprechende gefunden, können Diese ebenfalls importiert werden.  
Soll der Import durchgeführt werden öffnet sich für jedes Savegame das Importfenster. Der Titel ist ein Vorschlag und kann geändert werden. Der Ordnerpfad ist hier fest. Weiters siehe *Savegame importieren*.  
Falls der Import abgelehnt wird, werden die  entsprechenden `savegame`-Ordner und der `savegameBackup`-Ordner nach `savegameX_fsl_bak` bzw. `savegameBackup_fsl_bak` verschoben.  
Sollten Savegame- und / oder Modordner von FSL nicht automatisch erkannt werden, können Diese später auch manuell importiert werden. Siehe hierfür *Savegame importieren* bzw. *Mods importieren*  
Ist der Import abgeschlossen, öffnet sich das Hauptfenster und die importierten Savegames, sind im Dropdown verfügbar. Wurde zu einem Savegame keine Mapdatei gefunden, wird für den Kartennamen in der Dropdownliste "Geisterkarte" gesetzt. Welche Karte exakt fehlt kann über Ändern herausgefunden werden und unter Mods importiert werden.  

FSL legt seine Konfigurationsdateien auf Windows unter `~/AppData/Roaming/FarmingSimulatorLauncher/` bzw. auf MacOS unter `~/Library/Application Support/FarmingSimulatorLauncher/` ab.

## Savegame
### Savegame anlegen
Hierüber werden neue Savegames angelegt. Dabei wird aber nur ein FSL internes Savegame erzeugt, welches beim ersten Start im LS mit Daten gefüllt wird.  
  
<img src="../images/new_sg_german.png" width="800"/>  

Der *FSL Savegame Titel* muss gesetzt werden. Unter diesem Titel werden die Einträge in der FSL Konfiguration erzeugt und die entsprechenden Ordner angelegt.  
Nicht erlaubt ist hier der Doppelpunkt.  
Das Feld *Beschreibung* ist optional.  
Es muss unter *Karte* eine Map ausgewählt werden.  
Aus der Liste der verfügbaren *Mods* werden diejenigen ausgewählt, welche für das Savegame verwendet werden sollen.  
Die Auswhal erfolgt über die Tastenkombinationen:  
#### ***Mausklick***  
Es wird lediglich der angeklickte Eintrag ausgewählt. Andere bereits ausgewählte Einträge werden abgewählt.
#### ***Strg + Mausklick***  
Es wird der angeklickte Eintrag zusätzlich zu den bereits ausgwählten ebenfalls ausgewählt.  
Wird mit dieser Kombination auf einen bereits ausgewählten Eintrag geklickt, wird die Auswahl für diesen Eintrag aufgehoben.
#### ***Shift + Mausklick***  
Alle Einträge zwischen dem zuletzt ausgewähltem Eintrag und dem aktuell angeklickten Eintrag werden ausgewählt.
  
Beim *Speichern* wird geprüft, ob der Titel in Ordnung ist und noch nicht benutzt wird und ob eine Karte ausgewählt wurde. Weitherin wird geprüft, dass die ausgewählten Mods nicht kollidieren. Eine Auswahl des selben Mods in unterschiedlichen Versionen ist nicht möglich. Ist alles in Ordnung wird das Savegame gespeichert und das Fenster geschlossen.  
*Abbrechen* verlässt das Fenster ohne einen neues Savegame anzulegen.

### Savegame importieren
Hierüber können bereits vorhanden Savegames aus dem LS in den FSL importiert werden.  

<img src="../images/import_sg_german.png" width="800"/>
  
<span style="color:red">Achtung:</span> Bei einem Multiplayerspiel wird im LS für den Client kein Savegame erzeugt. Somit kann natürlich auch keines importiert werden. FSL benötigt aber die Angabe, welche Mods für das Spiel zur Verfügung gestellt werden sollen. Es muss also ein neues Savegame angelegt werden. Siehe *Savegame anlegen*

Zuerst muss der LS Savegame Ordner ausgewählt werden, der importiert werden soll.  
Danach kann der Ordner mit den Backups angegeben werden und dann ausgewählt werden welche Backups übernommen werrden sollen.  
Die Auswhal erfolgt über die Tastenkombinationen:  
#### ***Mausklick***  
Es wird lediglich der angeklickte Eintrag ausgewählt. Andere bereits ausgewählte Einträge werden abgewählt.
#### ***Strg + Mausklick***  
Es wird der angeklickte Eintrag zusätzlich zu den bereits ausgwählten ebenfalls ausgewählt.  
Wird mit dieser Kombination auf einen bereits ausgewählten Eintrag geklickt, wird die Auswahl für diesen Eintrag aufgehoben.
#### ***Shift + Mausklick***  
Alle Einträge zwischen dem zuletzt ausgewähltem Eintrag und dem aktuell angeklickten Eintrag werden ausgewählt.
Der *FSL Savegame Titel* muss gesetzt werden. Unter diesem Titel werden entsprechende Einträge in der FSL Konfiguration erzeugt und die passenden Ordner angelegt.  
Nicht erlaubt ist hier der Doppelpunkt.  
Das Feld *Beschreibung* ist optional.  

Beim *Importieren* wird geprüft, ob der Titel in Ordnung ist und noch nicht benutzt wird. Ist alles in Ordnung wird das Savegame importiert. Der Savegameordner wird hierbei mit dem vergebenen Titel umbenannt und ggf. vorhandene LS Backup in den FSL savegame Backupordner verschoben.  
Außerdem prüft FSL ob die im Savegame verwendeten Mods bereits in FSL importiert wurden. Werden Mods gefunden, die noch nicht importiert wurden, weißt FSL darauf hin. Die Liste der fehlenden Mods kann dann unter Savegame *Ändern* im Hauptfenster angezeigt werden und ggf. aus dem Savegame gelöscht werden.  
Anschließend wird das Fenster geschlossen.  

*Abbrechen* verlässt das Importfenster ohne Import.

### Savegame ändern
Hierüber können bereits vorhanden FSL Savegames angepasst werden.
  
<img src="../images/change_sg_german.png" width="800"/>  
  
Der *FSL Savegame Titel* kann verändert werden, muss aber gesetzt sein.
Nicht erlaubt ist hier der Doppelpunkt.  

Das Feld *Beschreibung* ist optional. Es kann eine neue Beschreibung eingetragen, die vorhandene geändert oder gelöscht werden.  

Die *Karte* ist nicht änderbar.  
Sollte die Datei zur Karte in FSL noch fehlen, "Geisterkarte", wird ind diesem Feld der Kartenname und die entsprechende Version angezeigt. Diese kann dann importiert werden. Siehe *Mods importieren*

Unter *Mods* können die verwendeten Mods angepasst werden. Bereits verwendete Mods werden markiert. Es können Mods hinzugefügt (markiert) und Mods entfernt (Markierung löschen) werden. Der Mod wird nur aus der Savegame Konfiguration entfernt. Bleibt aber im FSL verhanden. Soll der Mod komplett gelöscht werden muss dies über das *Mods* Fenster erfolgen.  
Die Auswhal der Mods erfolgt über die Tastenkombinationen:  
#### ***Mausklick***  
Es wird lediglich der angeklickte Eintrag ausgewählt. Andere bereits ausgewählte Einträge werden abgewählt.
#### ***Strg + Mausklick***  
Es wird der angeklickte Eintrag zusätzlich zu den bereits ausgwählten ebenfalls ausgewählt.  
Wird mit dieser Kombination auf einen bereits ausgewählten Eintrag geklickt, wird die Auswahl für diesen Eintrag aufgehoben.
#### ***Shift + Mausklick***  
Alle Einträge zwischen dem zuletzt angeklickten Eintrag und dem aktuell angeklickten Eintrag werden ausgewählt.  

Über *Benutzte Mods markieren* wird die aktuelle Zuordnung zum Savegame wieder angezeigt.  

Unter *Fehlend* werden die Mods aufgelistet, welche nicht im FSL verfügbar sind. Diese können aus dem Savegame gelöscht werden. Das Importieren ist über Hauptfenster > Mods möglich. Siehe *Mods importieren*  

*Speichern* übernimmt die Änderungen für das Savegame und schliesst das Fenster.  

*Abbrechen* schliesst das Fenster ohne die Änderungen zu übernehmen.
### Savegame löschen
Im Hauptfenster kann das ausgewählte Savegame gelöscht werden.  
<span style="color:orange">Achtung:</span> Dadurch wird die FSL Konfiguration für das Savegame entfernt und die zugehörigen Ordner gelöscht.  

### Savegame starten
Ist ein Savegame im Hautpfenster ausgwählt, kann dieses über die Taste *Starten* gestartet werden.
Das ausgewählte Savegame steht in LS dann unter savegame1 zur Verfügung.  

## Mods
### Mods importieren oder löschen
Hierüber werden die in FSL verfügbaren Mods vewrwaltet. Es können neue Mods importiert werden und bereits importierte wieder entfernt werden.

<img src="../images/import_mods_german.png" width="800"/>

### Import
Über *Browse* wird der Ordner ausgwählt, in dem nach Mods gesucht werden soll.  
*Zum Import* listet alle gefundenen Mods auf. Achtung: Es findet keine Unterscheidung der LS Versionen statt.  
Hierüber werden alle zu importierenden Mods ausgewählt.  
Die Auswhal erfolgt über die Tastenkombinationen:  
#### ***Mausklick***  
Es wird lediglich der angeklickte Eintrag ausgewählt. Andere bereits ausgewählte Einträge werden abgewählt.
#### ***Strg + Mausklick***  
Es wird der angeklickte Eintrag zusätzlich zu den bereits ausgwählten ebenfalls ausgewählt.  
Wird mit dieser Kombination auf einen bereits ausgewählten Eintrag geklickt, wird die Auswahl für diesen Eintrag aufgehoben.
#### ***Shift + Mausklick***  
Alle Einträge zwischen dem zuletzt angeklickten Eintrag und dem aktuell angeklickten Eintrag werden ausgewählt.  
*Importieren* fügt die ausgewählten Mods in den FSL Alle-Mods-Ordner ein.  
FSL bietet an, den Quellordner nach dem Import zu löschen. <span style="color:red">Achtung, es wird der gesamte Ordner gelöscht.</span>
Nach dem Import können die Savegames ausgewählt werden, bei denen die Modversion geändert werden soll oder der Mod hinzugefügt werden soll.
Du Zuordung der Mod Versionen zu den Savegames wird nicht automatisch angepasst.
### Löschen
*Bereits importierte Mods* listet alle in FSL verfügbaren Mods auf. Hierüber können die Mods ausgewählt werden, die gelöscht werden sollen.
*Löschen* entfernt die markierten Mods aus dem FSL Alle-Mods-Ordner.  
*Beenden* schliesst das Fenster.

## FSL Einstellungen
Hierüber werden die FSL Einstellungen verwaltet.

<img src="../images/settings_german.png" width="800"/>  

Bild steht stellvertretend für beide LS Versionen.

Über *Sprache wählen* kann die FSL Sprache ausgewählt werden. Im Dropdownmenü werden alle verfügbaren Sprachen aufgelistet.  
Wird der Haken bei *Immer die gewählte LS Version benutzen* gesetzt, wird die Abfrage zum Programmstart übersprungen.  
Unter *Pfad zu Farmingsimulator exe auswählen* wird der gewählte Pfad zur Farmingsimulator19.exe bzw. Farmingsimulator22.exe für Windows oder FarmingSimulator2019Game bzw. FarmingSimulator2022Game für MacOS angezeigt.
Über *Browse* kann die Datei gesucht werden.  
*Standard LS19 Pfad* setzt  
`C:\Program Files (x86)\Farming Simulator 2019\Farmingsimulator2019.exe`  
unter Windows bzw.  
`/Applications/Farming Simulator 2019.app/Contents/MacOS/FarmingSimulator2019Game`  
unter MacOS ein. Für den LS22 ist die Taste mit *Standard LS22 Pfad* beschriftet und der Pfad wird analog gesetzt.  
*Standard LS19 Steam Pfad* setzt  
`C:/Program Files (x86)/Steam/SteamApps/Common/Farming Simulator 19/FarmingSimulator2019.exe`  
unter Windows bzw.  
`~/Library/Application Support/Steam/SteamApps/common/Farming Simulator 19/Farming Simulator 2019.app/Contents/MacOS/FarmingSimulator2019Game`  
unter MacOS ein. Für den LS22 ist die Taste mit *Standard LS22 Steam Pfad* beschriftet und der Pfad wird analog gesetzt.  
Unter *Landwirtschaftssimulator Savgames Ordner auswählen* wird der Pfad zu den LS Savegames angezeigt.  
Über *Browse* kann der Pfad gesucht werden.  
*Standard LS19 Savegames Ordner Pfad* setzt den Pfad auf  
`C:/Users/USERNAME/Documents/My Games/FarmingSimulator2019`  
für Windows bzw.  
`~/Library/Application Support/FarmingSimulator2019`  
für MacOS gesetzt. Für den LS22 ist die Taste mit *Standard LS22 Savegames Ordner Pfad* beschriftet und der Pfad wird analog gesetzt.  
Der bei *Pfad für Alle-Mods-Ordner auswählen* gesetzte Pfad wird von FSL benutzt um einen all_mods Ordner anzulegen. In diesem werden alle Mods gespeichert die in FSL importiert wurden. Achte daher auf ausreichend Speicherplatz.  
Tipp: Wir haben für unsere Mods einen Cloudserver, welcher im Explorer eingebunden ist. Alle Spieler haben diesen Ordner als Alle-Mods-Ordner gesetzt, wodurch die Möglichkeit besteht, dass der Admin neue Mods einfügt oder auch entfernt und alle immer mit der selben Modbasis arbeiten. Das Herunterladen und Einfügen bei jedem einzelnen entfällt. Aktuell werden aber die FSL Savegames noch nicht geteilt. Somit muss ein neuer Mod zumindest noch für das Savegame ausgewählt werden. Das Teilen von FSL Savegame Konfigurationen ist geplant.
*Speichern* übernimmt die Einstellungen.
*Beenden* verlässt das Fenster ohne zu speichern.
## FSL updaten
FSL prüft bei jedem Start, ob eine neu FSL Version verfügbar ist. Ist dies der Fall wird im Hauptfenster die entsprechende Taste angezeigt. Hierüber wird die Webseite mit der neusten Version geöffnet und die entsprechenden Datei können heruntergeladen und ausgetauscht werden. Ein automatisches ersetzen erfolgt nicht.  

## Problembehebung
### Mods Ordner geändert
### Savegameordner geändert
### Mod importiert, aber im Spiel immer noch alte Modversion
