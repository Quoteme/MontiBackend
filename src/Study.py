from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from Sensor import Sensor
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

    def __str__(self):
        return self.name

    def id(self) -> str:
        """
        Die ID einer Studie ist der Namen der Studie gefolgt von einem
        hash-Wert. Dieser hash-Wert wird aus dem Namen, der Beschreibung,
        dem Start- und Endzeitpunkt sowie den Sensoren berechnet.
        """
        hashstr = hashlib.sha256(
                f'{self.name}{self.description}{self.start}{self.end}{self.sensors}'
                .encode('utf-8')
            ).hexdigest()
        return f"{self.name}-{hashstr}"

    @staticmethod
    def list_all_studies() -> list[Study]:
        """
        Liefere eine Liste aller Studien in der Datenbank
        """
        return [Study.read_from_file(f"./data/{f}/study.json") for f in os.listdir('./data')]

    def create(self):
        """
        Erstelle diese Studie in der Datenbank
        """
        os.mkdir(f"./data/{self.id()}")
        with open(f"./data/{self.id()}/study.json", "w") as f:
            f.write(self.to_json())

    @staticmethod
    def read_from_file(url: str):
        """
        Lese eine Studie aus der Datenbank
        """
        with open(f"./data/{url}/study.json", "r") as f:
            return Study.from_json(f.read())

    def delete(self):
        """
        Lösche diese Studie aus der Datenbank
        """
        shutil.rmtree(f"./data/{self.id()}")

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
            "sensors": str([str(s) for s in self.sensors])
        })

    @staticmethod
    def from_json(jsondata):
        """
        Erstelle eine Studie aus einem JSON-Objekt
        """
        return Study(
            name=jsondata["name"],
            description=jsondata["description"],
            start=datetime.strptime(jsondata["start"], "%Y-%m-%d %H:%M:%S.%f"),
            end=datetime.strptime(jsondata["end"], "%Y-%m-%d %H:%M:%S.%f"),
            sensors=[Sensor.from_name(s) for s in jsondata["sensors"]]
        )
