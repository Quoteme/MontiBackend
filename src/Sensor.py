from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import importlib, inspect

@dataclass
class Sensor:
    """
    Ein Sensor zeichnet stetig Daten auf, welche automatisch an den Server
    übermittelt werden.
    """
    timestamp: datetime

    def __str__(self):
        return self.name()

    def __repr__(self):
        return f"{str(self)} : {self.timestamp}"

    @staticmethod
    def name() -> str:
        return "Sensor"

    @staticmethod
    def description() -> str:
        return "Ein Sensor zeichnet stetig Daten auf, welche automatisch an den Server übermittelt werden."

    @staticmethod
    def list_all_sensors() -> list[Sensor]:
        """
        Liefert eine Liste aller verfügbaren Sensoren.
        """
        return [ obj for name, obj in inspect.getmembers(importlib.import_module("Sensor")) if inspect.isclass(obj) and issubclass(obj, Sensor) and obj != Sensor ]
            
    
    @staticmethod
    def from_name(name: str) -> Sensor:
        match name:
            case "MobileAccelerometer":
                return MobileAccelerometer(None)
            case "MobileGyroscope":
                return MobileGyroscope(None)
            case "MobileMagnetometer":
                return MobileMagnetometer(None)
            case "CorsanoMetricPPG":
                return CorsanoMetricPPG(None)
            case _:
                return Sensor(None)


@dataclass
class MobileAccelerometer(Sensor):
    """
    Ein MobileAccelerometer zeichnet die Beschleunigung auf, welche ein
    Smartphone aufweist.
    """
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    @staticmethod
    def name() -> str:
        return "MobileAccelerometer"

    @staticmethod
    def description() -> str:
        return "Ein MobileAccelerometer zeichnet die Beschleunigung auf, welche ein Smartphone aufweist."

@dataclass
class MobileGyroscope(Sensor):
    """
    Ein MobileGyroscope zeichnet die Drehung auf, welche ein Smartphone aufweist.
    """
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    @staticmethod
    def name() -> str:
        return "MobileGyroscope"

    @staticmethod
    def description() -> str:
        return "Ein MobileGyroscope zeichnet die Drehung auf, welche ein Smartphone aufweist."

@dataclass
class MobileMagnetometer(Sensor):
    """
    Ein MobileMagnetometer zeichnet die Magnetfeldstärke auf, welche ein
    Smartphone aufweist. Wichtig für die Kompassfunktion.
    """
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    @staticmethod
    def name() -> str:
        return "MobileMagnetometer"

    @staticmethod
    def description() -> str:
        return "Ein MobileMagnetometer zeichnet die Magnetfeldstärke auf, welche ein Smartphone aufweist. Wichtig für die Kompassfunktion."

@dataclass
class CorsanoMetricPPG(Sensor):
    """
    Ein CorsanoMetricPPG zeichnet die Herzfrequenz auf, welche ein
    Corsano-Messgerät aufweist.
    """
    acc: int  = 0
    ppg: int  = 0
    bpm: int  = 0
    bpmQ: int = 0
    crc: int  = 0
    accX: int = 0
    accY: int = 0
    accZ: int = 0

    @staticmethod
    def name() -> str:
        return "CorsanoMetricPPG"

    @staticmethod
    def description() -> str:
        return "Ein CorsanoMetricPPG zeichnet die Herzfrequenz auf, welche ein Corsano-Messgerät aufweist."
