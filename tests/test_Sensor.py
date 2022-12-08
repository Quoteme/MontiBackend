import src.Sensor


def test_sensor_can_be_created():
    sensor = src.Sensor.Sensor()
    assert sensor is not None

def test_sensor_can_be_created_with_data():
    sensor = src.Sensor.Sensor(
        name="Sensor",
        description="Beschreibung",
    )
    assert sensor is not None