# Erklärung TM Paket

# Table of Contents
1.[Generell](#generell)\
2.[Generator](#1Generator)\
3.[Konfliktmengen](#2konfliktmengen)\
4.[Recovery](3#recovery)\
5.[Scheduling](#4scheduling)

# Generell
Diese Datei soll einen Überblick über alle Methoden im Transaktionsmanagement geben. Hier sind sowohl alte als auch neue Methoden hinterlegt und kurz zusammengefasst.

Zu den folgenden Kategorien verfügt das TM Paket auch über 2 Parsing Funktionen:
- ``parse_schedule (schedule_str: str) -> tuple[Schedule, str]``
    - Diese Funktion parsed einen String zu einem Schedule. Gibt gegebenenfalls einen Error-String zurück.
- ``parse_string (cls, schedule: Schedule) -> tuple[str, str]``
    - Diese Funktion parsed ein Schedule zu einem String. Gibt gegebenenfalls einen Error-String zurück.

# Aufgabenerstellung
## Übungsblätter
Es existiert eine Datei: _Generate_Tasks.py_ welche eine Infrastruktur bereitstellt um Aufgaben für die Übungsblätter zu erstellen. Ein Beispiel der Funktionsweise ist in _playground.py_ hinterlegt. Die erzeugten Schedules müssen dann nur noch in das Übungsblatt eingefügt werden. Es lohnt sich diese Aufgaben an einem Ort abzuspeichern, da die Erzeugung jedes Mal neu passiert und somit keine Aufgabe genauso nochmal erzeugt werden kann.

**Bitte auch auf Textänderungen achten die eventuell entstehen müssen.**\
In diesem Datensatz sind auch die Lösungen enthalten, für die Erstellung einer Muserlösung.

``get_tasks()`` gibt eine Liste von Listen zurück. \
In der **ersten** Liste sind die Aufgaben zur **Serialisierbarkeit**. Die Liste ist folgendermaßen aufgebaut:

    [[Aufgabe-a, Lösung-a], [Aufgabe-b, Lösung-b]]
- _Aufgabe-a_: [schedule1: String, schedule2: String]
- _Lösung-a_: [conflictset1: List, conflictset2: List]
- _Aufgabe-b_: [schedule3: String, conflictset3: List, schedule4: String, conflictset4: List]
- _Lösung-b_: [serilizability3: bool, graph3: ConflictGraph, serilizability4: bool, graph4: ConflictGraph]\

In der **zweiten** Liste sind die Aufgaben und Lösungen zu **Recovery**:

    [[Aufgabe-a, Lösung-a], [Aufgabe-b, Lösung-b],[Aufgabe-c, Lösung-c]]
- _Aufgabe-a_: [Klasse: char, schedule1: String]
- _Lösung-a_: [[in_rc: Bool, in_aca: Bool, in_s: Bool],[proof_rc: List, proof_aca: List, proof_s: List]]
- _Aufgabe-b_: [Klasse: char, schedule1: String]
- _Lösung-b_: [[in_rc: Bool, in_aca: Bool, in_s: Bool],[proof_rc: List, proof_aca: List, proof_s: List]]
- _Aufgabe-c_: [Klasse: char, schedule1: String]
- _Lösung-c_: [[in_rc: Bool, in_aca: Bool, in_s: Bool],[proof_rc: List, proof_aca: List, proof_s: List]]\
In der **dritten** Liste sind die Aufgaben und Lösungen zum **Scheduling**:

        [[Aufgabe-a, Lösung-a], [Aufgabe-b, Lösung-b],[Aufgabe-c, Lösung-c]]
- _Aufgabe-a_: [schedule1: String, klasse: char]
- _Lösung-a_: [performed-schedule: schedule]
- _Aufgabe-b_: [schedule1: String, klasse: char]
- _Lösung-b_: [performed-schedule: schedule]
- _Aufgabe-c_: [schedule1: String, klasse: char]
- _Lösung-c_: [performed-schedule: schedule]

## Klausuraufgaben
Für Klausuraufgaben ist auch eine Beispielerzeugung in _playground.py_ hinderlegt. Dort wird eine Auswahl an Schedules erzeugt. Diese können in die Dynaxite logik eingefügt werden und somit eine zufälligere Aufgabenverteilung ermöglichen. Es existiert eine Beispielaufgabe in Dynaxite, aber es gibt sicherlich noch mehr Anwendungsmöglichkeiten.
# 1.Generator
**Neu**
Der Generator kann drei unterschiedliche Arten von Schedules erzeugen:
1. Zufällige Schedules
2. Schedules mit Deadlockangabe
3. Schedules in den verschiedenen Recoveryklassen

Die Generator Funktion liegt in der Datei _Generate.py_ und heißt _generate\_schedule_. Sie ist wie folgt aufgebaut:

## Die Funktion
`generate (transactions: int, resources: list[str], deadlock (optional): bool, recovery (optional): str)-> tuple[Schedule, str]`

**Es ist nicht möglich eine Angabe zu deadlcok und recovery zu machen!**  In diesem Fall wird ein Error geworfen.
- _transactions_: Anzahl an zu erzeugenden Transaktionen [t_1,...]. Die Transaktionen sind immer von 1 bis m durchnummeriert.   
    - Beispiel Eingabe: 3 
- _resources_: Name der Ressourcen. Erwartet eine Liste an chars.        
    - Beispiel Eingabe: ['a','b','c']
- _deadlock_: Optional. Erwartet einen Bool. Erzeugt dann ein Schedule mit/ohne Deadlock. Ohne Deadlock funktioniert nicht immer. In dem Fall das es nicht funktioniert wird ein entsprechender String zurückgegeben.
- _recovery_: Optional. Erwartet einen Char: 'r','a','s'. 
    - 'r': Erzeugt einen Schedule in der Klasse Recovery.
    - 'a': Erzeugt einen Schedule der in der Klasse Avoids Cascading Aborts ist.
    - 's': Erzeugt einen Schedule der in der Klasse Strict ist.

Zurückgegeben wird der Schedule.

## Beispielanfragen:
- Erzeugen eines zufälligen Schedules mit 3 Transaktionen und den Ressourcen 'a', 'b', 'c':
    - generate(3, ['a','b','c'])
- Erzeugen eines Schedules mit Deadlock:
    - generate(3, ['a','b','c'], deadlock = True)
- Erzeugen eines Schedules ohne Deadlock: **Fuktioniert nicht immer**
    - generate(3, ['a','b','c'], deadlock = False)
- Erzeugen eines Schedules in der Klasse 'Recovery' aber nicht in Avoids cascading aborts und Strict:
    - generate(3, ['a','b','c'], recovery = 'r')
- Erzeugen eines Schedules in der Klasse Avoids cascading aborts aber nicht in Strict:
    - generate(3, ['a','b','c'], recovery = 'a')
- Erzeugen eines Schedules in der Klasse Strict:
    - generate(3, ['a','b','c'], recovery = 's')

# 2.Konfliktmengen
Die Funktionen liegen in den Dateien _TM.py_ und _Solution\_generator.py_.

## TM.py
In der Datei _TM.py_ liegen die Funktionen in der Klasse _Serializability_. Hier gibt es folgende Funktionen:
- `` is_serializable (schedule[Schedule,str])-> tuple[bool, dict]``
    - Prüft ob der Schedule serialisierbar ist.
- ``build_graphviz_object (graph: dict)-> Digraph``
    - Erzeugt den Konfliktgraph
    - Für genauere Informationen zu Graphenerzeugung in Doku-Transaktionsmanagement gucken.

**Neu:**
## Solution_generator.py
In der Datei _Solution\_generator.py_ sind die Funktionen in der Klasse _Perform\_conflictgraph_. Dort gibt es folgende Funktionen:
- `` compute_conflict_quantity (cls, schedule: Schedule) -> list``
    - Erzeugt aus einem gegebenen Schedule eine Konfliktgraphen. Dieser wird nur als Liste zurückgegeben, angelehnt an der Schreibweise in Doku-Transaktionsmanagement.
- ``compute_conflictgraph(cls,conflict_list: dict) -> ConflictGraph``
    - Erzeugt den Graph zu einem gegebenem dict ( is_serializable(schedule)[1]). Der Graph kann angezeigt werden mit: graph.get_graphviz_graph().


# 3. Recovery
Die Funktionen können prüfen ob ein Schedule in der gegebenen Klasse ist.

## TM.py
Die Funktionen liegen in der Datei _TM.py_ in der Klasse _Recovery_. Folgende Funktionen sind dort zu finden:
- ``is_recoverable (schedule: Union[Schedule, str]) -> tuple[bool, set[tuple[int, str, int, bool]]]``
    - Prüft ob ein gegebener Schedule in der Klasse 'Recovery' ist. Nimmt sowohl ein Schedule als auch den String eines Schedules. Gibt einen Bool zurück und entweder einen Beweis oder ein Gegebneispiel.
- ``avoids_cascading_aborts (schedule: Union[Schedule, str]) -> tuple[bool, set[tuple[int, str, int, bool]]]``
    - Prüft ob ein gegebener Schedule in der Klasse 'Avoids Cascading Aborts' ist. Nimmt sowohl ein Schedule als auch den String eines Schedules. Gibt einen Bool zurück und entweder einen Beweis oder ein Gegebneispiel.
- ``is_strict (schedule: Union[Schedule, str]) -> tuple[bool, set[tuple[str, str, bool, bool]]]``
    - Prüft ob ein gegebener Schedule in der Klasse 'Strict' ist. Nimmt sowohl ein Schedule als auch den String eines Schedules. Gibt einen Bool zurück und entweder einen Beweis oder ein Gegenbeispiel.

# 4.Scheduling
Diese Funktionen können prüfen ob ein Schedule in den jeweiligen Klassen ist, sowie die jeweiligen Schedules ausführen und prüfen ob ein Deadlock vorliegt.

## TM.py
Die Funktionen in der Datei _TM.py_ sind in der Klasse _Scheduling_:
- ``is_2PL (schedule: Union[Schedule, str]) -> tuple[bool, list[str]]``
    - Prüft ob der Schedule in 2PL Form ist. Gibt einen Bool zurück un gegebenenfalls die Fehler.
- ``is_C2PL (schedule: Union[Schedule, str]) -> tuple[bool, list[str]]``
    - Prüft ob der Schedule in C2PL Form ist. Gibt einen Bool zurück un gegebenenfalls die Fehler.
- ``is_S2PL (schedule: Union[Schedule, str]) -> tuple[bool, list[str]]``
    - Prüft ob der Schedule in S2PL Form ist. Gibt einen Bool zurück un gegebenenfalls die Fehler.
- ``is_SS2PL (schedule: Union[Schedule, str]) -> tuple[bool, list[str]]``
    - Prüft ob der Schedule in SS2PL Form ist. Gibt einen Bool zurück un gegebenenfalls die Fehler.
-  ``is_operations_same(schedule: Union[Schedule, str], mod_schedule: Union[Schedule, str]) -> bool``
    - Prüft ob zwei gegebene Schedules die selben Operationen besitzen.

**Neu** 
## Solution_generator.py
Die Funktionen in der Datei _Solution\_generator.py_ sind in der Klasse _Perform_scheduling_. Dort sind forgende Funktionen:
- ``perform_S2PL (schedule: Schedule)-> tuple[Schedule, str]``
    - Führt für den gegebenen Schedule ein S2PL aus. Gibt den Schedule nach dem Ausführen des lockings aus und gegebenenfalls einen String falls ein Deadlock vorliegt. Das Ausführen des S2PL ist auch nicht möglich, wenn ein Deadlock vorliegt.
- ``perform_SS2PL (schedule: Schedule)-> tuple[Schedule, str]``
    - Führt für den gegebenen Schedule ein SS2PL aus. Gibt den Schedule nach dem Ausführen des lockings aus und gegebenenfalls einen String falls ein Deadlock vorliegt. Das Ausführen des SS2PL ist auch nicht möglich, wenn ein Deadlock vorliegt.
- ``perform_C2PL (schedule: Schedule)-> Schedule``
    - Führt für den gegebenen Schedule ein C2PL aus. Gibt den Schedule nach dem Ausführen des lockings aus.
- ``predict_deadlock (schedule: Schedule)-> bool``:
    - Prüft ob ein gegebener Schedule einen Deadlock enthält. Dies passiert durch den Versuch ein SS2PL vorzunehmen.
