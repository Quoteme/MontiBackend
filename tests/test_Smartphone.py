from src.Smartphone import Smartphone


def test_smartphone_can_be_created():
    smartphone = Smartphone()
    assert smartphone is not None

