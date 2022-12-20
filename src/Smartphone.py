from __future__ import annotations
from dataclasses import dataclass
import json
from typing import Optional


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
    operating_system: str = ""
    monti_version: str = ""
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

    @staticmethod
    def from_request_form(form: dict) -> Optional[Smartphone]:
        """
        Erstelle ein Smartphone aus einem Formular
        """
        if not "smartphone_brand" in form:
            raise ValueError("Smartphone brand not found in form")
        if not "smartphone_model" in form:
            raise ValueError("Smartphone model not found in form")
        if not "smartphone_operating_system" in form:
            raise ValueError("Smartphone operating system not found in form")
        if not "smartphone_monti_version" in form:
            raise ValueError("Smartphone monti version not found in form")
        if not "smartphone_id" in form:
            raise ValueError("Smartphone ID not found in form")

        return Smartphone(
            brand=form['smartphone_brand'],
            model=form['smartphone_model'],
            operating_system=form['smartphone_operating_system'],
            monti_version=form['smartphone_monti_version'],
            id=form['smartphone_id']
        )
