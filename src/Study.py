from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from werkzeug.datastructures import FileStorage

from PatientReportedOutcome import PatientReportedOutcome
from Sensor import Sensor
from Participant import Participant
import hashlib
import os
import json
import shutil
import qrcode
import io
import base64
import flask

from Smartphone import Smartphone


@dataclass
class Study:
    """
    Eine Studie kann erzeugt werden um Daten mehrerer Teilnehmer zu sammeln.

    Einige Fragen die durch eine Studie beantwortet werden sind:
    - Wessen...
    - Welche...
    - Von wan bis wann...
    - Wie oft...
    ... Daten werden gesammelt?
    """
    name: str
    description: str
    start: datetime
    end: datetime
    sensors: list[Sensor]
    _id: str = ""

    def __str__(self):
        return self.name

    @property
    def id(self) -> str:
        """
        Die ID einer Studie ist der Namen der Studie gefolgt von einem
        hash-Wert. Dieser hash-Wert wird aus dem Namen, der Beschreibung,
        dem Start- und Endzeitpunkt sowie den Sensoren berechnet.
        Dieser Wert wird in der `_id` Variable gechached.
        """
        if self._id == "":
            return hashlib.sha256(
                    f'{self.name}{self.description}{self.start}{self.end}{self.sensors}'
                    .encode('utf-8')
                ).hexdigest()
        else:
            return self._id

    @id.setter
    def id(self, value: str):
        self._id = value

    def tracks_sensor(self, sensor: Sensor) -> bool:
        """
        Prüfe, ob diese Studie den Sensor `sensor` trackt
        """
        return sensor.name in [s.name for s in self.sensors]

    @property
    def storage_directory(self):
        """
        Liefere den Speicherort dieser Studie
        """
        return f"./data/{self.id}"

    @property
    def list_all_patient_reported_outcomes(self):
        """
        Liefere eine Liste aller Patient Reported Outcomes (PROs)
        Die PROs befinden sich in `
        TODO: Implementieren
        """
        directory = PatientReportedOutcome.directory(self)
        # finde alle json Dateien in dem Ordner
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith(".json")]
        # lese die Dateien ein und erstelle daraus PatientReportedOutcome Objekte
        return [PatientReportedOutcome.from_file(os.path.join(directory, f)) for f in files]

    @staticmethod
    def list_all_studies() -> list[Study]:
        """
        Liefere eine Liste aller Studien in der Datenbank
        """
        if not os.path.exists("./data"):
            os.mkdir("./data")
        return [Study.read_from_file(f"./data/{f}/study.json") for f in os.listdir('./data') if os.path.isdir(f"./data/{f}")]

    @staticmethod
    def list_all_current_studies() -> list[Study]:
        """
        Liefere eine Liste aller laufenden Studien
        """
        return [s for s in Study.list_all_studies() if s.start < datetime.now() and s.end > datetime.now()]

    @staticmethod
    def list_all_pending_studies() -> list[Study]:
        """
        Liefere eine Liste aller Studien, die noch nicht gestartet haben
        """
        return [s for s in Study.list_all_studies() if s.start > datetime.now()]

    @staticmethod
    def list_all_ended_studies() -> list[Study]:
        """
        Liefere eine Liste aller Studien, die bereits beendet sind
        """
        return [s for s in Study.list_all_studies() if s.end < datetime.now()]

    @property
    def participants(self) -> list[Participant]:
        """
        Liefere eine Liste aller Teilnehmer dieser Studie
        """
        if not os.path.exists(f"{self.storage_directory}/participants"):
            return []
        else:
            return [Participant.from_file(f"{self.storage_directory}/participants/{f}/participant.json")
                    for f in os.listdir(f"{self.storage_directory}/participants")]
    
    def get_participant(self, participant_id: str) -> Participant:
        """
        Liefere den Teilnehmer mit der ID `participant_id`
        """
        return Participant.from_file(f"{self.storage_directory}/participants/{participant_id}/participant.json")

    def get_participant_last_database_modification(self, participant: Participant) -> Optional[datetime]:
        """
        Liefere das Datum der letzten Änderung der Datenbank des Teilnehmers `participant`
        """
        return participant.last_database_modification(f"{self.storage_directory}/participants")

    def get_participant_sensor_data_files(self, participant: Participant) -> list[str]:
        """
        Liefere eine Liste aller Dateien mit Sensordaten des Teilnehmers `participant`
        """
        return participant.get_all_sensor_data_files(f"{self.storage_directory}/participants")

    def get_participant_sleep_data_files(self, participant: Participant) -> list[str]:
        """
        Liefere eine Liste aller Dateien mit Schlafdaten des Teilnehmers `participant`
        """
        return participant.get_all_sleep_data_files(f"{self.storage_directory}/participants")

    def get_participant_ppg2_data_files(self, participant: Participant) -> list[str]:
        """
        Liefere eine Liste aller Dateien mit PPG2-Daten des Teilnehmers `participant`
        """
        return participant.get_all_ppg2_data_files(f"{self.storage_directory}/participants")

    def get_participant_acc_data_files(self, participant: Participant) -> list[str]:
        """
        Liefere eine Liste aller Dateien mit Accelerometer-Daten des Teilnehmers `participant`
        """
        return participant.get_all_acc_data_files(f"{self.storage_directory}/participants")

    def get_participant_sleep_directory(self, participant: Participant) -> str:
        """
        Liefere das Verzeichnis mit den Sleep Daten des Teilnehmers `participant`
        """
        return participant.get_sleep_database_directory(f"{self.storage_directory}/participants")

    def get_participant_ppg2_directory(self, participant: Participant) -> str:
        """
        Liefere das Verzeichnis mit den PPG2 Daten des Teilnehmers `participant`
        """
        return participant.get_ppg2_database_directory(f"{self.storage_directory}/participants")

    def get_participant_acc_directory(self, participant: Participant) -> str:
        """
        Liefere das Verzeichnis mit den Accelerometer Daten des Teilnehmers `participant`
        """
        return participant.get_acc_database_directory(f"{self.storage_directory}/participants")

    def get_participant_database_directory(self, participant: Participant):
        """
        Liefere den Speicherort der Datenbank des Teilnehmers `participant`
        """
        return participant.get_database_directory(f"{self.storage_directory}/participants")

    def upload_participant_sensor_data(self, participant: Participant, file: FileStorage, date: datetime):
        """
        Lade die Sensordaten `data` des Sensors `sensor` für den Teilnehmer `participant` hoch
        """
        participant.upload_sensor_data(f"{self.storage_directory}/participants", file, date)

    def add_participant(self, participant: Participant):
        """
        Füge einen Teilnehmer dieser Studie hinzu
        """
        if not os.path.exists(f"{self.storage_directory}/participants"):
            os.mkdir(f"{self.storage_directory}/participants")
        participant.create(f"{self.storage_directory}/participants")

    def register_smartphone_to_participant(self, participant: Participant, smartphone: Smartphone):
        """
        Registriere das Smartphone `smartphone` für den Teilnehmer `participant`
        """
        participant.register_smartphone(f"{self.storage_directory}/participants", smartphone)

    def update_participant(self, participant: Participant):
        """
        Aktualisiere den Teilnehmer `participant` in der Datenbank
        """
        if not os.path.exists(f"{self.storage_directory}/participants"):
            os.mkdir(f"{self.storage_directory}/participants")
        participant.update(f"{self.storage_directory}/participants")

    def delete_participant(self, participant: Participant):
        """
        Lösche den Teilnehmer `participant` aus der Datenbank
        """
        participant.delete(f"{self.storage_directory}/participants")

    def add_sensor_data_to_participant(self, participant: Participant, data: Sensor):
        """
        Füge die Sensordaten `data` für den Teilnehmer `participant` hinzu.
        `data` muss ein Sensor-Objekt sein, welches die Sensordaten enthält.
        """
        participant.add_sensor_data(f"{self.storage_directory}/participants", data)

    def qrcode_participant_login(self, participant: Participant) -> str:
        """
        Liefere den QR-Code für einen Teilnehmer `participant`.
        Hiermit kann sich der Teilnehmer in der App einloggen.
        Der QR-Code wird als base64-String zurückgegeben.
        """
        # return f"study://{self.id}/participant/{participant.id}"
        data = json.dumps({
            "study": json.loads(self.to_json()),
            "participant": json.loads(participant.to_json()),
            "address": flask.request.host_url
        })
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def create(self):
        """
        Erstelle diese Studie in der Datenbank
        """
        os.mkdir(f"{self.storage_directory}")
        with open(f"{self.storage_directory}/study.json", "w") as f:
            f.write(self.to_json())

    @staticmethod
    def from_id(id: str) -> Optional[Study]:
        """
        Liefere die Studie mit der angegebenen ID.
        Dafür wird die Studie aus der Datenbank gelesen.
        Wir suchen den Ordner mit der ID und lesen die Studie aus der
        Datei `study.json` aus.
        Falls keine Studie mit der ID gefunden wird, wird `None` zurückgegeben.
        """
        return Study.read_from_file(f"./data/{id}/study.json")

    @staticmethod
    def read_from_file(url: str) -> Optional[Study]:
        """
        Lese eine Studie aus der Datenbank.
        Sollte die Studie nicht existieren, wird `None` zurückgegeben.
        """
        if os.path.exists(url):
            with open(url, "r") as f:
                return Study.from_json(f.read())
        else:
            return None

    def delete(self):
        """
        Lösche diese Studie aus der Datenbank
        """
        shutil.rmtree(f"{self.storage_directory}")

    def update(self):
        """
        Aktualisiere diese Studie in der Datenbank
        """
        with open(f"{self.storage_directory}/study.json", "w") as f:
            f.write(self.to_json())

    def to_json(self) -> str:
        """
        Konvertiere diese Studie in ein JSON-Objekt
        """
        return json.dumps({
            "name": self.name,
            "description": self.description,
            "start": str(self.start),
            "end": str(self.end),
            "sensors": str([str(s) for s in self.sensors]),
            "_id": self.id
        })

    @staticmethod
    def from_json(jsondata) -> Study:
        """
        Erstelle eine Studie aus einem JSON-Objekt
        """
        data = json.loads(jsondata)
        return Study(
            name=data["name"],
            description=data["description"],
            start=datetime.strptime(data["start"], "%Y-%m-%d %H:%M:%S"),
            end=datetime.strptime(data["end"], "%Y-%m-%d %H:%M:%S"),
            sensors=[Sensor.from_name(s) for s in json.loads(data["sensors"].replace("'", '"'))],
            _id=data["_id"]
        )

    def upload_participant_sleep_data(self, participant: Participant, file: FileStorage):
        """
        Lade die Schlafdaten für den Teilnehmer `participant` hoch.
        """
        participant.upload_sleep_data(f"{self.storage_directory}/participants", file)

    def upload_participant_ppg2_data(self, participant: Participant, file: FileStorage):
        """
        Lade die PPG2-Daten für den Teilnehmer `participant` hoch.
        """
        participant.upload_ppg2_data(f"{self.storage_directory}/participants", file)

    def upload_participant_acc_data(self, participant: Participant, file: FileStorage):
        """
        Lade die ACC-Daten für den Teilnehmer `participant` hoch.
        """
        participant.upload_acc_data(f"{self.storage_directory}/participants", file)