from __future__ import annotations
from dataclasses import dataclass
from Sensor import Sensor
from typing import List
import json

@dataclass
class Participant:
    """
    Datentyp für Teilnehmer von Studien
    """
    name: str = ""
    age: int = 0

    @staticmethod
    def from_json(url: str) -> Participant:
        """
        Lade einen Teilnehmer aus einer JSON-Datei
        """
        with open(url, 'r') as f:
            data = json.load(f)
            return Participant(
                name=data['name'],
                age=data['age']
            )

    def to_json(self) -> str:
        """
        Konvertiere diesen Teilnehmer in ein JSON-Objekt
        """
        return json.dumps({
            "name": self.name,
            "age": self.age
        })
