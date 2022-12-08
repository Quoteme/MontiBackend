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
    `User.user_file()`, bzw. `./cfg/user.csv` gespeichert.
    """
    username: str = ""
    password: str = ""

    @staticmethod
    def user_file() -> str:
        """
        Liefere den Pfad zur Datei, in der die Benutzer gespeichert sind.
        """
        return './cfg/user.csv'

    def __str__(self) -> str:
        return self.username

    @staticmethod
    def parse(username: str, password: str) -> Optional[User]:
        """
        Wird ein username und ein password gegeben, so prüfe ob diese
        Kombination in unserer Datenbank vorhanden ist.
        Wenn nein: gib nichts zurück
        Wenn ja: gib ein Administrator/Benutzer/...-Objekt zurück
        """
        if User(username, password).is_valid():
            match User.find_role(username):
                case "guest":
                    return Guest(username, password)
                case "administrator":
                    return Administrator(username, password)

    @staticmethod
    def find_role(username: str) -> Optional[UserRolle]:
        """
        Finde die Benutzerrolle, nur von dem Namen eines potenziellen Benutzers
        """
        db = pd.read_csv(User.user_file())
        userdata = db[db["user"] == username]
        if userdata.size > 0:
            return userdata["userrole"][0]

    def is_valid(self) -> bool:
        """
        Prüfe, ob die Kombination aus username und password in der
        Datenbank vorhanden ist.
        """
        db = pd.read_csv(User.user_file())
        return db[["user", "password"]].isin([self.username, self.password]).any().all()

class Administrator(User):
    """
    Ein Administrator kann Studien erstellen, bearbeiten, löschen und einsehen.
    """

class Guest(User):
    """
    Dieser Benutzertyp ist für Gäste gedacht, welche nur beschränkt Zugriff auf die Website haben.
    """
