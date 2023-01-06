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
    question: str
    answer: str
    type = "PatientReportedOutcomeQuestion"

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
        return PatientReportedOutcomeQuestion.from_type(**json.loads(json_string))

    @staticmethod
    def from_type(question: str, answer: str, type: str):
        """
        Erzeuge eine neue Instanz einer Unterklasse von PatientReportedOutcomeQuestion mit dem angegebenen Typ.
        """
        match type:
            case PatientReportedOutcomeQuestion.type:
                return PatientReportedOutcomeQuestion(question, answer)
            case YesNoQuestion.type:
                return YesNoQuestion(question, answer)
            case OneToFiveQuestion.type:
                return OneToFiveQuestion(question, answer)
            case OneToTenQuestion.type:
                return OneToTenQuestion(question, answer)
            case TextQuestion.type:
                return TextQuestion(question, answer)


# A subclass of PatientReportedOutcomeQuestion for the "yes/no" questions
@dataclass
class YesNoQuestion(PatientReportedOutcomeQuestion):
    question: str
    answer: str
    type = "YesNoQuestion"

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
    question: str
    answer: str
    type = "OneToFiveQuestion"

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
    question: str
    answer: str
    type = "OneToTenQuestion"

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
    question: str
    answer: str
    type = "TextQuestion"

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