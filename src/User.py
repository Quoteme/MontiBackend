from __future__ import annotations
import pandas as pd
from typing import Literal, Optional

UserRolle = Literal['benutzer', 'administrator']

class User:
    """
    Datentyp für Benutzer
    """
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

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

    @staticmethod
    def is_valid(username: str, password: str) -> bool:
        db = pd.read_csv('./cfg/user.csv')
        return db[["user", "password"]].isin([username, password]).any().all()

class Administrator(User):
    """
    Ein Administrator kann Studien erstellen, bearbeiten, löschen und einsehen.
    """

class Benutzer(User):
    """
    Ein Benutzer kann nur Studien einsehen.
    """
