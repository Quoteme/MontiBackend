import json
from dataclasses import dataclass


@dataclass
class PatientReportedOutcomeQuestion:
    """
    Diese Klasse repräsentiert eine Frage eines Patient Reported Outcome (PRO).
    Ein Patient-reported outcome besteht aus mehreren Fragen, die der Patient beantworten muss.
    Eine Frage, wie sie hier definiert ist, besteht aus:
    - einem Fragetext
    - einer Antwortmöglichkeit (z.B. Ja/Nein, 1-5, etc.)
    """
    type = "PatientReportedOutcomeQuestion"
    question: str
    answer: str

    @property
    def __dict__(self):
        return {
            "question": self.question,
            "type": self.type,
            "answer": self.answer,
        }

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(json_string: str):
        return PatientReportedOutcomeQuestion(**json.loads(json_string))


# A subclass of PatientReportedOutcomeQuestion for the "yes/no" questions
@dataclass
class YesNoQuestion(PatientReportedOutcomeQuestion):
    type = "Ja oder Nein Frage"
    def __init__(self, question: str, answer: bool):
        super().__init__(question, answer)

    @property
    def __dict__(self):
        return {
            "question": self.question,
            "type": self.type,
            "answer": "yes" if self.answer else "no",
        }

    @staticmethod
    def from_json(json_string: str):
        data = json.loads(json_string)
        return YesNoQuestion(data["question"], data["answer"] == "yes")

    def to_json(self):
        return json.dumps(self.__dict__)

# A subclass of PatientReportedOutcomeQuestion for the "1-5" questions
@dataclass
class OneToFiveQuestion(PatientReportedOutcomeQuestion):
    type = "1-5 Frage"
    def __init__(self, question: str, answer: int):
        super().__init__(question, answer)

    @property
    def __dict__(self):
        return {
            "question": self.question,
            "type": self.type,
            "answer": self.answer,
        }

    @staticmethod
    def from_json(json_string: str):
        data = json.loads(json_string)
        return OneToFiveQuestion(data["question"], data["answer"])

    def to_json(self):
        return json.dumps(self.__dict__)

# A subclass of PatientReportedOutcomeQuestion for the "1-10" questions
@dataclass
class OneToTenQuestion(PatientReportedOutcomeQuestion):
    type = "1-10 Frage"
    def __init__(self, question: str, answer: int):
        super().__init__(question, answer)

    @property
    def __dict__(self):
        return {
            "question": self.question,
            "type": self.type,
            "answer": self.answer,
        }

    @staticmethod
    def from_json(json_string: str):
        data = json.loads(json_string)
        return OneToTenQuestion(data["question"], data["answer"])

    def to_json(self):
        return json.dumps(self.__dict__)

# A subclass of PatientReportedOutcomeQuestion for the text questions
@dataclass
class TextQuestion(PatientReportedOutcomeQuestion):
    type = "Text Frage"
    def __init__(self, question: str, answer: str):
        super().__init__(question, answer)

    @property
    def __dict__(self):
        return {
            "question": self.question,
            "type": self.type,
            "answer": self.answer,
        }

    @staticmethod
    def from_json(json_string: str):
        data = json.loads(json_string)
        return TextQuestion(data["question"], data["answer"])

    def to_json(self):
        return json.dumps(self.__dict__)