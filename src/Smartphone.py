from __future__ import annotations
from dataclasses import dataclass
import json


@dataclass
class Smartphone:
    """
    Ein Teilnehmer einer Studie kann sich mit einem Smartphone registrieren.
    Daten wie:
        - Marke
        - Softwareversion
        - ID
        - ...
    Werden in dieser Klasse gespeichert.
    Das wichtigste ist die ID, da diese zur Authentifizierung des Teilnehmers
    verwendet wird.
    Es dürfen somit nicht zwei Smartphones mit der gleichen ID registriert
    werden können.
    """
    brand: str = ""
    model: str = ""
    software_version: str = ""
    id: str = ""

    def to_json(self) -> str:
        """
        Liefere eine JSON-Repräsentation dieses Smartphones
        """
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(json_string: str) -> Smartphone:
        """
        Erstelle ein Smartphone aus einer JSON-Repräsentation
        """
        return Smartphone(**json.loads(json_string))
