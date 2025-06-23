import datetime
from pathlib import Path
import pandas as pd
import pytest
from unittest.mock import Mock, patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver
from app.operations import OperationFactory

# Fixture for Calculator instance with temp dirs
@pytest.fixture
def calculator():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:
            
            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"
            
            yield Calculator(config=config)

# Fixture for Add operation
@pytest.fixture
def add_operation():
    return OperationFactory.create_operation('add')

# --- Initialization Tests ---

def test_calculator_initialization(calculator):
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.operation_strategy is None

# --- Logging Tests ---

@patch('app.calculator.logging.info')
def test_logging_setup(logging_info_mock):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:
        mock_log_dir.return_value = Path('/tmp/logs')
        mock_log_file.return_value = Path('/tmp/logs/calculator.log')
        Calculator(CalculatorConfig())
        logging_info_mock.assert_any_call("Calculator initialized with configuration")

# --- Observer Tests ---

def test_add_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers

def test_remove_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    calculator.remove_observer(observer)
    assert observer not in calculator.observers

def test_notify_observers_called(calculator, add_operation):
    calculator.set_operation(add_operation)
    observer = Mock()
    calculator.add_observer(observer)
    calculator.perform_operation(2, 3)
    observer.update.assert_called_once()

# --- Operation Tests ---

def test_set_operation(calculator, add_operation):
    calculator.set_operation(add_operation)
    assert calculator.operation_strategy == add_operation

@pytest.mark.parametrize(
    "a,b,expected",
    [
        (2, 3, Decimal('5')),
        ('10', '5', Decimal('15'))
    ]
)
def test_perform_operation_addition(calculator, add_operation, a, b, expected):
    calculator.set_operation(add_operation)
    result = calculator.perform_operation(a, b)
    assert result == expected

def test_perform_operation_validation_error(calculator, add_operation):
    calculator.set_operation(add_operation)
    with pytest.raises(ValidationError):
        calculator.perform_operation('invalid', 3)

def test_perform_operation_operation_error(calculator):
    with pytest.raises(OperationError, match="No operation set"):
        calculator.perform_operation(2, 3)

# --- Undo/Redo Tests ---

def test_undo(calculator, add_operation):
    calculator.set_operation(add_operation)
    calculator.perform_operation(2, 3)
    assert calculator.undo()
    assert calculator.history == []
    assert not calculator.undo()  # Nothing left to undo

def test_redo(calculator, add_operation):
    calculator.set_operation(add_operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    assert calculator.redo()
    assert len(calculator.history) == 1
    assert not calculator.redo()  # Nothing left to redo

# --- History Size Limit Test ---

def test_history_max_size(calculator, add_operation):
    calculator.set_operation(add_operation)
    for i in range(calculator.config.max_history_size + 5):
        calculator.perform_operation(i, i)
    assert len(calculator.history) <= calculator.config.max_history_size

# --- History Management ---

@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator, add_operation):
    calculator.set_operation(add_operation)
    calculator.perform_operation(2, 3)
    calculator.save_history()
    mock_to_csv.assert_called_once()

@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history(mock_exists, mock_read_csv, calculator):
    mock_read_csv.return_value = pd.DataFrame({
        'operation': ['Addition'],
        'operand1': ['2'],
        'operand2': ['3'],
        'result': ['5'],
        'timestamp': [datetime.datetime.now().isoformat()]
    })

    try:
        calculator.load_history()
        assert len(calculator.history) == 1
        assert calculator.history[0].operation == "Addition"
        assert calculator.history[0].operand1 == Decimal("2")
        assert calculator.history[0].operand2 == Decimal("3")
        assert calculator.history[0].result == Decimal("5")
    except OperationError:
        pytest.fail("Loading history failed due to OperationError")

# --- Clear History ---

def test_clear_history(calculator, add_operation):
    calculator.set_operation(add_operation)
    calculator.perform_operation(2, 3)
    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []


# Test logging during initialization
@patch('app.calculator.logging.info')
def test_calculator_initialization_logging(logging_info_mock):
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)
        calculator = Calculator(config=config)

        # Check if the initialization log is present
        logging_info_mock.assert_any_call("Calculator initialized with configuration")

@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history_empty_file(mock_exists, mock_read_csv, calculator):
    # Mock empty CSV data
    mock_read_csv.return_value = pd.DataFrame()

    # Test the load_history functionality with an empty history
    try:
        calculator.load_history()
        assert len(calculator.history) == 0  # Ensure history is empty
        assert calculator.history == []  # Explicit check for empty history
    except OperationError:
        pytest.fail("Loading empty history failed unexpectedly")

def test_undo_empty_stack(calculator):
    # No operations performed, the undo stack should be empty
    result = calculator.undo()
    assert not result  # Should return False
    assert calculator.history == []  # History should remain empty
    assert calculator.undo_stack == []  # Undo stack should remain empty

def test_undo_full_stack(calculator):
    # Perform an operation and add to history
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    result = calculator.perform_operation(2, 3)

    # Ensure history is populated and undo stack has 1 memento
    assert len(calculator.history) == 1  # History should contain one entry
    assert len(calculator.undo_stack) == 1  # Undo stack should have 1 memento

    # Now, perform the undo operation
    undo_result = calculator.undo()

    # Assert that the undo operation returned True (indicating success)
    assert undo_result
    assert calculator.history == []  # History should be empty after undo
    assert len(calculator.undo_stack) == 0  # Undo stack should be empty after undo
    assert len(calculator.redo_stack) == 1  # Redo stack should now contain the previous history state

def test_redo_empty_stack(calculator):
    # No operations performed, redo stack should be empty
    result = calculator.redo()
    assert not result  # Should return False

def test_redo_after_undo(calculator):
    # Perform operation and undo
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    
    # Redo should restore the previous state
    result = calculator.redo()
    assert result
    assert len(calculator.history) == 1  # History should be restored

def undo(self) -> bool:
    """
    Undo the last operation.
    """
    if not self.undo_stack:
        return False

    memento = self.undo_stack.pop()
    logging.debug(f"Undoing: Restoring history from memento, history size: {len(memento.history)}")

    self.redo_stack.append(CalculatorMemento(self.history.copy()))
    self.history = memento.history.copy()

    logging.debug(f"Undo complete: history size after undo: {len(self.history)}")
    return True

