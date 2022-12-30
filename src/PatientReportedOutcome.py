import hashlib
import json
import os
from dataclasses import dataclass
from typing import List

from Study import Study


@dataclass
class PatientReportedOutcomeQuestion:
    """
    Diese Klasse repräsentiert eine Frage eines Patient Reported Outcome (PRO).
    Ein Patient-reported outcome besteht aus mehreren Fragen, die der Patient beantworten muss.
    Eine Frage, wie sie hier definiert ist, besteht aus:
    - einem Fragetext
    - einer Antwortmöglichkeit (z.B. Ja/Nein, 1-5, etc.)
    """
    question: str
    answer: str

    @property
    def __dict__(self):
        return {
            "question": self.question,
            "answer": self.answer,
        }

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(json_string: str):
        return PatientReportedOutcomeQuestion(**json.loads(json_string))


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
            "questions": [question.to_json() for question in self.questions],
        })

    @staticmethod
    def from_json(json_string: str):
        data = json.loads(json_string)
        return PatientReportedOutcomeQuestion(
            data["name"],
            Study.from_id(data["study_id"]),
            [PatientReportedOutcomeQuestion.from_json(question) for question in data["questions"]],
        )

    def save(self):
        """
        Speichert das Patient Reported Outcome in der Datenbank.
        """
        # prüfe, ob der Ordner für die Studie und der Ordner für PROs existiert
        if not os.path.exists(f"{ self.study.storage_directory }/patient_reported_outcomes"):
            os.mkdir(f"{ self.study.storage_directory }/patient_reported_outcomes")

        with open(f"{self.study.storage_directory}/patient_reported_outcomes/{self.id}.json", "w") as file:
            file.write(self.to_json())