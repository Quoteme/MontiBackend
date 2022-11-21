from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from Sensor import Sensor
from Participant import Participant
import hashlib
import os
import json
import shutil

@dataclass
class Study:
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
        return [Participant.from_json(f"./data/{self.id}/pariticpants/{f}/participant.json")
                for f in os.listdir(f"./data/{self.id}/pariticpants")]

    def create(self):
        """
        Erstelle diese Studie in der Datenbank
        """
        os.mkdir(f"./data/{self.id}")
        with open(f"./data/{self.id}/study.json", "w") as f:
            f.write(self.to_json())

    @staticmethod
    def from_id(id: str) -> Study:
        """
        Liefere die Studie mit der angegebenen ID.
        Dafür wird die Studie aus der Datenbank gelesen.
        Wir suchen den Ordner mit der ID und lesen die Studie aus der
        Datei `study.json` aus.
        """
        return Study.read_from_file(f"./data/{id}/study.json")

    @staticmethod
    def read_from_file(url: str):
        """
        Lese eine Studie aus der Datenbank
        """
        with open(url, "r") as f:
            return Study.from_json(f.read())

    def delete(self):
        """
        Lösche diese Studie aus der Datenbank
        """
        shutil.rmtree(f"./data/{self.id}")

    def update(self):
        """
        Aktualisiere diese Studie in der Datenbank
        """
        pass

    def to_json(self):
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
    def from_json(jsondata):
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
