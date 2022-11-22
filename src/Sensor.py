from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import importlib, inspect

@dataclass
class SensorData:
    """
    Ein SensorData-Objekt enthält die Daten eines Sensors.
    """
    timestamp: datetime = datetime.now()

@dataclass
class Sensor:
    """
    Ein Sensor zeichnet stetig Daten auf, welche automatisch an den Server
    übermittelt werden.
    """
    timestamp: datetime = datetime.now()

    name: str = "Sensor"
    description: str = "Ein Sensor zeichnet stetig Daten auf, welche automatisch an den Server übermittelt werden."
    data: SensorData = SensorData()

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

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
                return MobileAccelerometerSensor(None)
            case "MobileGyroscopeSensor":
                return MobileGyroscopeSensor(None)
            case "MobileMagnetometerSensor":
                return MobileMagnetometerSensor(None)
            case "CorsanoMetricPPGSensor":
                return CorsanoMetricPPGSensor(None)
            case _:
                return Sensor(None)

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
    data: MobileAccelerometerSensorData = MobileAccelerometerSensorData()

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
    data: MobileGyroscopeSensorData = MobileGyroscopeSensorData()

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
    data: MobileMagnetometerSensorData = MobileMagnetometerSensorData()

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

@dataclass
class CorsanoMetricPPGSensor(Sensor):
    """
    Ein CorsanoMetricPPG zeichnet die Herzfrequenz auf, welche ein
    Corsano-Messgerät aufweist.
    """
    name: str = "CorsanoMetricPPGSensor"
    description: str = "Ein CorsanoMetricPPGSensor zeichnet die Herzfrequenz auf, welche ein Corsano-Messgerät aufweist."
    data: CorsanoMetricPPGSensorData = CorsanoMetricPPGSensorData()

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

