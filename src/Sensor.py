from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import importlib, inspect
from typing import List

@dataclass
class SensorData:
    """
    Ein SensorData-Objekt enthält die Daten eines Sensors.
    """
    timestamp: datetime = datetime.now()

    def to_csv(self) -> str:
        """
        Liefere eine CSV-Repräsentation dieses SensorData-Objekts
        """
        raise NotImplementedError

@dataclass
class Sensor:
    """
    Ein Sensor zeichnet stetig Daten auf, welche automatisch an den Server
    übermittelt werden.
    Genauere Informationen und die Implementation wie diese Daten übermittelt
    werden finden sich in den Unterklassen dieser Klasse.
    """

    name: str = "Sensor"
    description: str = "Ein Sensor zeichnet stetig Daten auf, welche automatisch an den Server übermittelt werden."
    data: List[SensorData] = field(default_factory=list)

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def parse_csv(self, csv: str):
        """
        Parse CSV-String zu SensorData.
        Diese Methode muss in den Unterklassen implementiert werden.
        """
        raise NotImplementedError

    def to_csv(self) -> str:
        """
        Liefere eine CSV-Repräsentation dieses Sensors
        """
        raise NotImplementedError

    @staticmethod
    def list_all_sensors() -> list[Sensor]:
        """
        Liefert eine Liste aller verfügbaren Sensoren.
        """
        return [ obj for name, obj in inspect.getmembers(importlib.import_module("Sensor")) if inspect.isclass(obj) and issubclass(obj, Sensor) and obj != Sensor ]
            
    
    @staticmethod
    def from_name(name: str) -> Sensor:
        match name:
            case "MobileAccelerometerSensor":
                return MobileAccelerometerSensor()
            case "MobileGyroscopeSensor":
                return MobileGyroscopeSensor()
            case "MobileMagnetometerSensor":
                return MobileMagnetometerSensor()
            case "CorsanoMetricPPGSensor":
                return CorsanoMetricPPGSensor()
            case _:
                return Sensor()

@dataclass
class MobileAccelerometerSensorData(SensorData):
    """
    Beschleinigungssensor rohdaten
    """
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

@dataclass
class MobileAccelerometerSensor(Sensor):
    """
    Ein MobileAccelerometer zeichnet die Beschleunigung auf, welche ein
    Smartphone aufweist.
    """
    name: str = "MobileAccelerometerSensor"
    description: str = "Ein MobileAccelerometer zeichnet die Beschleunigung auf, welche ein Smartphone aufweist."
    data: List[MobileAccelerometerSensorData] = field(default_factory=list)

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

@dataclass
class MobileGyroscopeSensorData(SensorData):
    """
    Gyroskopsensor rohdaten
    """
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

@dataclass
class MobileGyroscopeSensor(Sensor):
    """
    Ein MobileGyroscope zeichnet die Drehung auf, welche ein Smartphone aufweist.
    """
    name: str = "MobileGyroscopeSensor"
    description: str = "Ein MobileGyroscope zeichnet die Drehung auf, welche ein Smartphone aufweist."
    data: List[MobileGyroscopeSensorData] = field(default_factory=list)

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)


@dataclass
class MobileMagnetometerSensorData(SensorData):
    """
    Magnetometer rohdaten.
    Wichtig für Kompass
    """
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

@dataclass
class MobileMagnetometerSensor(Sensor):
    """
    Ein MobileMagnetometer zeichnet die Magnetfeldstärke auf, welche ein
    Smartphone aufweist. Wichtig für die Kompassfunktion.
    """
    name: str = "MobileMagnetometerSensor"
    description: str = "Ein MobileMagnetometer zeichnet die Magnetfeldstärke auf, welche ein Smartphone aufweist. Wichtig für die Kompassfunktion."
    data: List[MobileMagnetometerSensorData] = field(default_factory=list)

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)


@dataclass
class CorsanoMetricPPGSensorData(SensorData):
    """
    Pulsdaten
    """
    acc: int  = 0
    ppg: int  = 0
    bpm: int  = 0
    bpmQ: int = 0
    crc: int  = 0
    accX: int = 0
    accY: int = 0
    accZ: int = 0

    def to_csv(self) -> str:
        """
        Liefere eine CSV-Repräsentation dieses SensorData-Objekts.
        Diese Methode wird von der Methode to_csv() der Klasse MetricPPGSensor verwendet.
        Hiermit wird jeweils eine Zeile der CSV-Datei erzeugt.
        """
        return f"{self.timestamp},{self.acc},{self.ppg},{self.bpm},{self.bpmQ},{self.crc},{self.accX},{self.accY},{self.accZ}"

@dataclass
class CorsanoMetricPPGSensor(Sensor):
    """
    Ein CorsanoMetricPPG zeichnet die Herzfrequenz auf, welche ein
    Corsano-Messgerät aufweist.
    """
    name: str = "CorsanoMetricPPGSensor"
    description: str = "Ein CorsanoMetricPPGSensor zeichnet die Herzfrequenz auf, welche ein Corsano-Messgerät aufweist."
    data: List[CorsanoMetricPPGSensorData] = field(default_factory=list)

    def __str__(self):
        return self.name

    def __repr__(self):
        print(self)
        return str(self)

    def parse_csv(self, csv: str):
        """
        Parst einen CSV-String und fügt die Daten dem Sensor hinzu.
        Die Daten der CSV Datei müssen dabei in folgendem Format vorliegen:

        ```
        timestamp,acc,ppg,bpm,bpmQ,crc,accX,accY,accZ
        ```

        Beispiel:
        ```
        1671562522897,18,12431,170,1,0,124,132,-176
        1671562522937,9,12412,170,1,0,128,140,-168
        1671562522977,12,12428,170,1,0,136,136,-168
        1671562523017,12,12434,170,1,0,140,124,-160
        ```
        """
        lines = csv.splitlines()
        for line in lines:
            if line == "":
                continue
            values = line.split(b",")
            self.data.append(CorsanoMetricPPGSensorData(
                timestamp=int(values[0]),
                acc=int(values[1]),
                ppg=int(values[2]),
                bpm=int(values[3]),
                bpmQ=int(values[4]),
                crc=int(values[5]),
                accX=int(values[6]),
                accY=int(values[7]),
                accZ=int(values[8])
            ))

    def to_csv(self) -> str:
        """
        Gibt die Daten des Sensors als CSV-String zurück.
        Dies ist komplett analog zur Methode `parse_csv`.
        """
        csv = ""
        for data in self.data:
            csv += data.to_csv() + "\n"
        return csv