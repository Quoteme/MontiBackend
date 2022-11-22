from __future__ import annotations
from dataclasses import dataclass
from Sensor import Sensor
from typing import List
import json
import uuid
import os
import shutil
from datetime import datetime

@dataclass
class Participant:
    """
    Datentyp für Teilnehmer von Studien
    """
    surname: str = ""
    forename: str = ""
    birthday: datetime = datetime.now()
    _id: str = ""

    def __str__(self) -> str:
        return f"{self.forename} {self.surname} {self.birthday.strftime('%d.%m.%Y')}"

    def __repr__(self) -> str:
        return str(self)

    @property
    def id(self) -> str:
        """
        Liefere die ID dieses Teilnehmers
        """
        if self._id != "":
            return self._id
        else:
            self._id = uuid.uuid4().hex
            return self._id

    def create(self, url: str) -> None:
        """
        Erstelle einen neuen Teilnehmer
        """
        os.mkdir(f"{url}/{self.id}")
        with open(f"{url}/{self.id}/participant.json", "w") as f:
            f.write(self.to_json())

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

    @staticmethod
    def from_file(url: str) -> Participant:
        """
        Lade einen Teilnehmer aus einer JSON-Datei
        """
        with open(url, 'r') as f:
            return Participant.from_json(f.read())

    @staticmethod
    def from_json(json_string: str) -> Participant:
        """
        Erstelle einen Teilnehmer aus einem JSON-Objekt
        """
        data = json.loads(json_string)
        return Participant(
                surname = data["surname"],
                forename = data["forename"],
                birthday = datetime.strptime(data["birthday"], "%Y-%m-%d"),
                _id = data["id"]
                )

    def to_json(self) -> str:
        """
        Konvertiere diesen Teilnehmer in ein JSON-Objekt
        """
        return json.dumps({
            "surname": self.surname,
            "forename": self.forename,
            "birthday": self.birthday.strftime("%Y-%m-%d"),
            "id": self.id
        })
