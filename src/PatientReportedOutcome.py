import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import List

from PatientReportedOutcomeQuestion import PatientReportedOutcomeQuestion

try:
    from Study import Study
except ImportError:
    import sys
    Study = sys.modules[__package__ + 'Study']


@dataclass
class PatientReportedOutcome:
    """
    Diese Klasse stellt ein Patient-reported-outcome (PRO) dar.
    Ein Patient-reported-outcome ist ein Quiz, das von einem Patienten
    ausgefüllt wird. Dieses Quiz wird in der Studie `study` durchgeführt
    und jeder Patient kann es nur einmal ausfüllen.
    """
    name: str
    study: Study
    questions: List[PatientReportedOutcomeQuestion]
    start_date: datetime
    end_date: datetime

    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        return self.name

    @property
    def id(self) -> str:
        """
        Die ID eines Patient Reported Outcome ist der Name der Studie
        gefolgt von einem hash-Wert. Dieser hash-Wert wird aus dem Namen
        der Studie und den Fragen berechnet.
        """
        return hashlib.sha256(
            f'{self.study.name}{self.questions}'.encode('utf-8')
        ).hexdigest()

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "study_id": self.study.id,
            "questions": [question.__dict__ for question in self.questions],
            "start_date": self.start_date.timestamp(),
            "end_date": self.end_date.timestamp(),
        })

    @staticmethod
    def from_json(json_string: str):
        data = json.loads(json_string)
        from Study import Study
        study = Study.from_id(data["study_id"])
        return PatientReportedOutcome(
            data["name"],
            Study.from_id(data["study_id"]),
            [PatientReportedOutcomeQuestion.from_json(str(question).replace("'", '"')) for question in data["questions"]],
            datetime.fromtimestamp(data["start_date"]),
            datetime.fromtimestamp(data["end_date"]),
        )

    @staticmethod
    def from_file(path: str):
        """
        Lese ein Patient Reported Outcome aus einer JSON Datei.
        """
        with open(path, "r") as file:
            return PatientReportedOutcome.from_json(file.read())

    @staticmethod
    def directory(study):
        """
        Gibt den Ordner zurück, in dem die Patient Reported Outcomes gespeichert werden.
        """
        # stelle sicher, dass der Ordner existiert
        if not os.path.exists(f"{ study.storage_directory }/patient_reported_outcomes"):
            os.mkdir(f"{ study.storage_directory }/patient_reported_outcomes")
        return f"{study.storage_directory}/patient_reported_outcomes/"

    def save(self):
        """
        Speichert das Patient Reported Outcome in der Datenbank.
        """
        # prüfe, ob der Ordner für die Studie und der Ordner für PROs existiert
        with open(f"{PatientReportedOutcome.directory(self.study)}/{self.id}.json", "w") as file:
            file.write(self.to_json())