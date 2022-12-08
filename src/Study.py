from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

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
            hashstr = hashlib.sha256(
                    f'{self.name}{self.description}{self.start}{self.end}{self.sensors}'
                    .encode('utf-8')
                ).hexdigest()
            return f"{self.name}-{hashstr}"
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

    @staticmethod
    def list_all_studies() -> list[Study]:
        """
        Liefere eine Liste aller Studien in der Datenbank
        """
        return [Study.read_from_file(f"./data/{f}/study.json") for f in os.listdir('./data')]

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
        if not os.path.exists(f"./data/{self.id}/participants"):
            return []
        else:
            return [Participant.from_file(f"./data/{self.id}/participants/{f}/participant.json")
                    for f in os.listdir(f"./data/{self.id}/participants")]
    
    def get_participant(self, participant_id: str) -> Participant:
        """
        Liefere den Teilnehmer mit der ID `participant_id`
        """
        return Participant.from_file(f"./data/{self.id}/participants/{participant_id}/participant.json")

    def add_participant(self, participant: Participant):
        """
        Füge einen Teilnehmer dieser Studie hinzu
        """
        if not os.path.exists(f"./data/{self.id}/participants"):
            os.mkdir(f"./data/{self.id}/participants")
        participant.create(f"./data/{self.id}/participants")

    def update_participant(self, participant: Participant):
        """
        Aktualisiere den Teilnehmer `participant` in der Datenbank
        """
        if not os.path.exists(f"./data/{self.id}/participants"):
            os.mkdir(f"./data/{self.id}/participants")
        participant.update(f"./data/{self.id}/participants")

    def delete_participant(self, participant: Participant):
        """
        Lösche den Teilnehmer `participant` aus der Datenbank
        """
        participant.delete(f"./data/{self.id}/participants")

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
        os.mkdir(f"./data/{self.id}")
        with open(f"./data/{self.id}/study.json", "w") as f:
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
        shutil.rmtree(f"./data/{self.id}")

    def update(self):
        """
        Aktualisiere diese Studie in der Datenbank
        """
        with open(f"./data/{self.id}/study.json", "w") as f:
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
