from __future__ import annotations
import pandas as pd
from typing import Literal, Optional
from dataclasses import dataclass

UserRolle = Literal['benutzer', 'administrator']

@dataclass
class User:
    """
    Datentyp für Benutzer der Website.
    Verschiedene Benutzer haben unterschiedliche Rechte.
    Nur mit einem Benutzer kann man sich auf der Website einloggen.
    Welche Konten und mit welchem Passwort existieren, wird in der Datei
    `cfg/user.csv` gespeichert.
    """
    username: str = ""
    password: str = ""

    def __str__(self) -> str:
        return self.username

    @staticmethod
    def parse(username: str, password: str) -> Optional[User]:
        """
        Wird ein username und ein password gegeben, so prüfe ob diese
        Kombination in unserer Datenbank vorhanden ist.
        Wenn nein: gib nichts zurück
        Wenn ja:   gib ein Administrator/Benutzer/...-Objekt zurück
        """
        match User.find_role(username):
            case "benutzer":
                return Benutzer(username, password)
            case "administrator":
                return Administrator(username, password)

    @staticmethod
    def find_role(username: str) -> Optional[UserRolle]:
        """
        Finde die Benutzerrolle, nur von dem Namen eines potentiellen Benutzers
        """
        db = pd.read_csv('./cfg/user.csv')
        userdata = db[db["user"] == username]
        if userdata.size > 0:
            return userdata["userrole"][0]

    def is_valid(self) -> bool:
        db = pd.read_csv('./cfg/user.csv')
        return db[["user", "password"]].isin([self.username, self.password]).any().all()

class Administrator(User):
    """
    Ein Administrator kann Studien erstellen, bearbeiten, löschen und einsehen.
    """

class Benutzer(User):
    """
    Ein Benutzer kann nur Studien einsehen.
    """
