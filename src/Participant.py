from __future__ import annotations

import multiprocessing
import subprocess
from dataclasses import dataclass

from werkzeug.datastructures import FileStorage

from Sensor import Sensor
from Smartphone import Smartphone
from typing import List, Optional
import json
import uuid
import os
import shutil
from datetime import datetime
from typing import Literal

Gender = Literal['male', 'female', 'other']

@dataclass
class Participant:
    """
    Datentyp für Teilnehmer von Studien.
    Ein Teilnehmer wird immer in einer Studie erstellt.
    Studien werden als Ordner unter dem Ordner `data/` gespeichert.
    Genau so, werden Teilnehmer in Unterordnern von Studien gespeichert.
    Der zugehörige Ordnername ist die ID des Teilnehmers.
    In diesem Ordner befindet sich auch eine Datei `participant.json`,
    welche feste Daten des Teilnehmers enthält (siehe: Geburtsdatum, ...).

    Der QR-Code zum Registrieren eines Teilnehmers wird von der Studie
    generiert. Wenn sich ein Teilnehmer registriert, wird sein Smartphone
    mit dem Konto verknüft. Aus Sicherheitsgründen kann nur ein Smartphone
    pro Teilnehmer registriert werden.
    """
    surname: str = ""
    forename: str = ""
    birthday: datetime = datetime.now()
    gender: Gender = 'other'
    smartphone: Optional[Smartphone] = None
    _id: str = ""

    def __str__(self) -> str:
        return f"{self.forename} {self.surname} {self.birthday.strftime('%d.%m.%Y')}"

    def __repr__(self) -> str:
        return str(self)

    @property
    def id(self) -> str:
        """
        Liefere die ID dieses Teilnehmers
        Die ID ist eine UUID, die beim Erstellen des Teilnehmers generiert wird
        und danach nicht mehr verändert wird. Sie dient als eindeutige Kennung
        und da nur der Partizipant selbst, sowie Administratoren diese
        kennen, ist sie auch zur Authentifizierung sicher.
        """
        if self._id != "":
            return self._id
        else:
            self._id = uuid.uuid4().hex
            return self._id

    @property
    def name(self) -> str:
        """
        Liefere den vollständigen Namen des Teilnehmers
        """
        return f"{self.forename} {self.surname}"

    @property
    def age(self) -> int:
        """
        Liefere das Alter des Teilnehmers
        """
        return (datetime.now() - self.birthday).days // 365

    @property
    def is_registered(self) -> bool:
        """
        Liefere, ob dieser Teilnehmer mit einem Smartphone registriert ist
        """
        return self.smartphone is not None

    def register_smartphone(self, url, smartphone: Smartphone) -> None:
        """
        Registriere ein Smartphone für diesen Teilnehmer
        """
        self.smartphone = smartphone
        self.update(url)

    def last_database_modification(self, url: str) -> Optional[datetime]:
        """
        Liefere das Datum der letzten Änderung an der Datenbank für diesen Teilnehmer
        """
        # prüfe ob der Teilnehmer eine Sensordatenbank hat
        if not os.path.exists(self.get_database_directory(url)):
            return None
        # Liste alle Dateien in dem sensor_data Ordner auf
        files = os.listdir(self.get_database_directory(url))
        # wenn keine Dateien vorhanden sind, ist die letzte Änderung auch None
        if len(files) == 0:
            return None
        # Ordne diese Dateien nach dem Datum der letzten Änderung
        files.sort(key=lambda x: os.path.getmtime(f"{self.get_database_directory(url)}/{x}"))
        # Liefere das Datum der letzten Änderung
        return datetime.fromtimestamp(os.path.getmtime(f"{self.get_database_directory(url)}/{files[-1]}"))

    def get_all_sensor_data_files(self, url: str) -> list[str]:
        """
        Liefere alle hochgeladenen Sensordaten-Datein, welche zum Beispiel als `.realm` Dateien gespeichert sind, dieses Teilnehmers.
        Gesammelte Daten sind keine Ordner
        """
        # prüfe ob der Teilnehmer eine Sensordatenbank hat
        if not os.path.exists(self.get_database_directory(url)):
            # wenn nicht, erstelle einen leeren Ordner
            os.makedirs(self.get_database_directory(url))
        # die Dateinamen müssen mit `.realm` enden
        # der Dateiname darf nicht mit `backup.realm` enden
        list_of_files = [file
            for file in os.listdir(self.get_database_directory(url))
            if not os.path.isdir(f"{self.get_database_directory(url)}/{file}")
            and file.endswith(".realm")
            and not file.endswith("backup.realm")]
        list_of_files.sort()
        return list_of_files

    def get_all_sleep_data_files(self, url: str) -> List[str]:
        """
        Liefere alle hochgeladenen Sleep-Datein, welche als `.wiff` Dateien gespeichert sind, dieses Teilnehmers.
        """
        # prüfe ob der Teilnehmer eine Sleep Datenbank hat
        if not os.path.exists(self.get_sleep_database_directory(url)):
            # wenn nicht, erstelle einen leeren Ordner
            os.makedirs(self.get_sleep_database_directory(url))
        # die Dateinamen müssen mit `.wiff` enden
        list_of_files = [file
            for file in os.listdir(self.get_sleep_database_directory(url))
            if not os.path.isdir(f"{self.get_sleep_database_directory(url)}/{file}")
            and file.endswith(".wiff")]
        list_of_files.sort()
        return list_of_files

    def get_all_ppg2_data_files(self, url: str) -> List[str]:
        """
        Liefere alle hochgeladenen PPG2-Datein, welche als `.wiff` Dateien gespeichert sind, dieses Teilnehmers.
        """
        # prüfe ob der Teilnehmer eine Sleep Datenbank hat
        if not os.path.exists(self.get_ppg2_database_directory(url)):
            # wenn nicht, erstelle einen leeren Ordner
            os.makedirs(self.get_ppg2_database_directory(url))
        # die Dateinamen müssen mit `.wiff` enden
        list_of_files = [file
            for file in os.listdir(self.get_ppg2_database_directory(url))
            if not os.path.isdir(f"{self.get_ppg2_database_directory(url)}/{file}")
            and file.endswith(".wiff")]
        list_of_files.sort()
        return list_of_files

    def get_all_acc_data_files(self, url: str) -> List[str]:
        """
        Liefere alle hochgeladenen Accelerometer-Datein, welche als `.wiff` Dateien gespeichert sind, dieses Teilnehmers.
        """
        # prüfe ob der Teilnehmer eine Sleep Datenbank hat
        if not os.path.exists(self.get_acc_database_directory(url)):
            # wenn nicht, erstelle einen leeren Ordner
            os.makedirs(self.get_acc_database_directory(url))
        # die Dateinamen müssen mit `.wiff` enden
        list_of_files = [file
            for file in os.listdir(self.get_acc_database_directory(url))
            if not os.path.isdir(f"{self.get_acc_database_directory(url)}/{file}")
            and file.endswith(".wiff")]
        list_of_files.sort()
        return list_of_files

    def get_database_directory(self, url: str) -> str:
        """
        Liefere den Ordner, in dem die Sensordaten dieses Teilnehmers gespeichert sind
        """
        return f"{url}/{self.id}/sensor_data"

    def get_sleep_database_directory(self, url: str) -> str:
        """
        Liefere den Ordner, in dem die Schlafdaten dieses Teilnehmers gespeichert sind
        """
        return f"{url}/{self.id}/sleep_data"

    def get_ppg2_database_directory(self, url: str) -> str:
        """
        Liefere den Ordner, in dem die PPG2 Daten dieses Teilnehmers gespeichert sind
        """
        return f"{url}/{self.id}/ppg2_data"

    def get_acc_database_directory(self, url: str) -> str:
        """
        Liefere den Ordner, in dem die ACC Daten dieses Teilnehmers gespeichert sind
        """
        return f"{url}/{self.id}/acc_data"

    def get_pro_data_directory(self, url: str) -> str:
        """
        Liefere den Ordner, in dem die Patient reported outcomes dieses Teilnehmers gespeichert sind
        """
        return f"{url}/{self.id}/patient_reported_outcomes"

    def upload_sensor_data(self, url: str, file: FileStorage, date: datetime) -> None:
        """
        Lade die Sensordaten dieses Teilnehmers für das Datum `date` hoch
        """
        # Prüfe ob der Ordner für die Sensordaten existiert
        directory = self.get_database_directory(url)
        if not os.path.exists(directory):
            # Erstelle den Ordner, falls er nicht existiert
            os.makedirs(directory)

        # get the absolute path to our current pwd
        base_path = os.path.abspath('.') # example /home/user/MontiBackend

        # prüfe ob der exportordner existiert
        export_directory = f"{base_path}/{directory}/json_export-{date.strftime('%Y-%m-%d-%H-%M-%S-%f')}/"
        if not os.path.exists(export_directory):
            # erstelle den exportordner
            os.makedirs(export_directory)

        # Speichere die Datei in den Teilnehmer-sensor-Ordner
        filename = f"{base_path}/{directory}/database-{date.strftime('%Y-%m-%d-%H-%M-%S-%f')}.realm"
        file.save(filename)
        process = multiprocessing.Process(target=self.convert_realm_to_json, args=(filename, export_directory))
        process.start()
        # self.convert_realm_to_json(filename, export_directory)

    def convert_realm_to_json(self, realmfile: str, outfile: str) -> None:
        """
        Konvertiere die Sensordaten dieses Teilnehmers für das Datum `date` in JSON
        """
        # get the absolute path to our current pwd
        base_path = os.path.abspath('.')

        # Konvertiere die Sensordaten in JSON
        # verwende dafür das programm `corsano-realm-convert`, welches in javascript geschrieben ist
        # os.system(f"npm run start --prefix {base_path}/submodules/corsano-realm-converter {base_path}/{directory}/database-{datetime}.realm {base_path}/{directory}/json_export-{date.strftime('%Y-%m-%d')}/")

        # Konvertiere die Sensordaten in JSON
        # TODO: momentan wird NPM nicht gefunden
        # TODO: Wechsel auf eine schnellere Sprache als Javascript
        try:
            cmd = [
                "npm",
                "run "
                "start "
                "--prefix "
                f"{base_path}/submodules/corsano-realm-converter ",
                realmfile+" ",
                outfile+" "
            ]
            sp = subprocess.check_call(' '.join(cmd), shell=True)
            # sp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={'PATH': os.getenv('PATH')}, shell=True)
            # stdout, stderr = sp.communicate()
            # print(stdout)
        except Exception as e:
            print(e)

    def add_sensor_data(self, url: str, sensor: Sensor) -> None:
        """
        Füge Sensordaten zu diesem Teilnehmer hinzu.
        In dem übergebenen Sensor `sensor` sind die Sensordaten enthalten.
        """
        # Falls der Ordner für die Sensordaten noch nicht existiert, erstelle ihn
        directory = f"{url}/{self.id}/{sensor.name}"
        if not os.path.exists(directory):
            # Create the directory
            os.makedirs(directory)
        # Schreibe die Sensordaten in eine Datei
        # Wir können annehmen, dass mindestens ein Wert in den Sensordaten ist.
        # Daher können wir den Timestamp des ersten Wertes verwenden, um die datei zu benennen.
        # Sollte kein erster Wert vorhanden sein, muss auch nichts gespeichert werden.
        filename = f"{datetime.fromtimestamp(sensor.data[0].timestamp//1000).strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        with open(f"{url}/{self.id}/{sensor.name}/{filename}", "w") as f:
            f.write(sensor.to_csv())

    def update(self, url: str) -> None:
        """
        Aktualisiere diesen Teilnehmer in der Datenbank
        """
        with open(f"{url}/{self.id}/participant.json", "w") as f:
            f.write(self.to_json())

    def delete(self, url: str) -> None:
        """
        Lösche diesen Teilnehmer aus der Datenbank
        """
        shutil.rmtree(f"{url}/{self.id}")

    def create(self, url: str) -> None:
        """
        Erstelle einen neuen Teilnehmer.
        Nachdem ein Participant erstellt wurde, kann er mittels `from_file`
        wiederhergestellt werden.
        """
        os.mkdir(f"{url}/{self.id}")
        with open(f"{url}/{self.id}/participant.json", "w") as f:
            f.write(self.to_json())

    @staticmethod
    def from_file(url: str) -> Optional[Participant]:
        """
        Lade einen Teilnehmer aus einer JSON-Datei.
        Sollte die Datei nicht existieren, wird `None` zurückgegeben.
        """
        if os.path.exists(f"{url}"):
            with open(url, 'r') as f:
                return Participant.from_json(f.read())
        else:
            return None

    @staticmethod
    def from_json(json_string: str) -> Participant:
        """
        Erstelle einen Teilnehmer aus einem JSON-Objekt
        """
        data = json.loads(json_string)
        try:
            birthday = datetime.strptime(data.get("birthday"), "%Y-%m-%d")
        except ValueError:
            birthday = datetime.fromtimestamp(0)
        return Participant(
            surname=data.get("surname"),
            forename=data.get("forename"),
            birthday=birthday,
            gender=data.get("gender"),
            _id=data.get("id"),
            smartphone=Smartphone.from_json(data.get("smartphone")) if data.get("smartphone") else None
        )

    def to_json(self) -> str:
        """
        Konvertiere diesen Teilnehmer in ein JSON-Objekt
        """
        return json.dumps({
            "surname": self.surname,
            "forename": self.forename,
            "birthday": self.birthday.strftime("%Y-%m-%d"),
            "gender": self.gender,
            "id": self.id,
            "smartphone": self.smartphone.to_json() if self.smartphone else None
        })

    def upload_sleep_data(self, url: str, file: FileStorage):
        """
        Lade Schlafdaten zu diesem Teilnehmer hoch.
        """
        # Prüfe, ob der `sleep` Ordner unter `url` existiert
        if not os.path.exists(self.get_sleep_database_directory(url)):
            os.mkdir(self.get_sleep_database_directory(url))
        # Speichere die Datei unter `self.get_sleep_database_directory(url)/file.filename`
        # sollte die datei schon existieren, speichere die datei mit dem timestamp als suffix
        if os.path.exists(f"{self.get_sleep_database_directory(url)}/{file.filename}"):
            file.filename = f"{file.filename}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        file.save(f"{self.get_sleep_database_directory(url)}/{file.filename}")

    def upload_ppg2_data(self, url: str, file: FileStorage):
        """
        Lade PPG2 Daten zu diesem Teilnehmer hoch.
        """
        # Prüfe, ob der `ppg2` Ordner unter `url` existiert
        if not os.path.exists(self.get_ppg2_database_directory(url)):
            os.mkdir(self.get_ppg2_database_directory(url))
        # Speichere die Datei unter `self.get_ppg2_database_directory(url)/file.filename`
        # sollte die datei schon existieren, speichere die datei mit dem timestamp als suffix
        if os.path.exists(f"{self.get_sleep_database_directory(url)}/{file.filename}"):
            file.filename = f"{file.filename}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        file.save(self.get_ppg2_database_directory(url) + "/" + file.filename)

    def upload_acc_data(self, url: str, file: FileStorage):
        """
        Lade ACC Daten zu diesem Teilnehmer hoch.
        """
        # Prüfe, ob der `acc` Ordner unter `url` existiert
        if not os.path.exists(self.get_acc_database_directory(url)):
            os.mkdir(self.get_acc_database_directory(url))
        # Speichere die Datei unter `self.get_acc_database_directory(url)/file.filename`
        # sollte die datei schon existieren, speichere die datei mit dem timestamp als suffix
        if os.path.exists(f"{self.get_sleep_database_directory(url)}/{file.filename}"):
            file.filename = f"{file.filename}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        file.save(self.get_acc_database_directory(url) + "/" + file.filename)

    def upload_patient_reported_outcome(self, url: str, pro: src.PatientReportedOutcome, json):
        """
        Lade Patient Reported Outcome Daten zu diesem Teilnehmer hoch.
        """
        pass
