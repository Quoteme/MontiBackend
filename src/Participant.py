from __future__ import annotations
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
        if not os.path.exists(f"{url}/{self.id}/database.realm"):
            return None
        return datetime.fromtimestamp(os.path.getmtime(f"{url}/{self.id}/database.realm"))

    def upload_sensor_data(self, url: str, file: FileStorage, date: datetime) -> None:
        """
        Lade die Sensordaten dieses Teilnehmers für das Datum `date` hoch
        """
        file.save(f"{url}/{self.id}/database.realm")

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
        return Participant(
            surname=data.get("surname"),
            forename=data.get("forename"),
            birthday=datetime.strptime(data.get("birthday"), "%Y-%m-%d"),
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
