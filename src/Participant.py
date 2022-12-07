from __future__ import annotations
from dataclasses import dataclass
from Sensor import Sensor
from typing import List
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
                surname = data.get("surname"),
                forename = data.get("forename"),
                birthday = datetime.strptime(data.get("birthday"), "%Y-%m-%d"),
                gender = data.get("gender"),
                _id = data.get("id")
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
            "id": self.id
        })
