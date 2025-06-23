import datetime
from decimal import Decimal
from app.calculation import Calculation
from app.calculator_memento import CalculatorMemento

def test_memento_to_dict_and_from_dict():
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))
    original_memento = CalculatorMemento(history=[calc])
    memento_dict = original_memento.to_dict()

    assert 'history' in memento_dict
    assert isinstance(memento_dict['history'], list)
    assert isinstance(memento_dict['timestamp'], str)

    restored = CalculatorMemento.from_dict(memento_dict)
    assert len(restored.history) == 1
    assert restored.history[0] == calc
    assert isinstance(restored.timestamp, datetime.datetime)
