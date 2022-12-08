from src.Smartphone import Smartphone


def test_smartphone_can_be_created():
    smartphone = Smartphone()
    assert smartphone is not None


def test_smartphone_can_be_created_with_data():
    smartphone = Smartphone(
        brand="Apple",
        model="iPhone 11",
        operating_system="iOS 14.1",
        monti_version="1.0.0",
    )
    assert smartphone is not None


def test_smartphone_creates_valid_json():
    smartphone = Smartphone(
        brand="Apple",
        model="iPhone 11",
        operating_system="iOS 14.1",
        monti_version="1.0.0",
    )
    assert smartphone.to_json() == '{"brand": "Apple", "model": "iPhone 11", "operating_system": "iOS 14.1", "monti_version": "1.0.0", "id": ""}'


def test_smartphone_can_be_created_from_json():
    smartphone = Smartphone.from_json(
        '{"brand": "Apple", "model": "iPhone 11", "operating_system": "iOS 14.1", "monti_version": "1.0.0", "id": ""}')
    assert smartphone is not None
