import pytest
from unittest.mock import patch
from app.calculator_repl import calculator_repl
from app.calculator import Calculator
from app.exceptions import ValidationError


# ----- Test that the help command prints available options -----
@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_repl_help(mock_print, mock_input):
    calculator_repl()
    printed = [call.args[0] for call in mock_print.call_args_list if call.args]
    assert any("Available commands:" in msg for msg in printed), "Help text not printed"

# ----- Test the exit branch (successful history save) -----
@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_repl_exit_success(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history', return_value=None) as mock_save:
        calculator_repl()
        mock_save.assert_called_once()
        printed = " ".join(call.args[0] for call in mock_print.call_args_list if call.args)
        assert "History saved successfully." in printed
        assert "Goodbye!" in printed

# ----- Test history branch when history is empty -----
@patch('app.calculator.Calculator.load_history', return_value=None)
@patch('app.calculator.Calculator.show_history', return_value=[])
@patch('builtins.input', side_effect=['history', 'exit'])
@patch('builtins.print')
def test_repl_history_empty(mock_print, mock_input, mock_show_history, mock_load_history):
    calculator_repl()
    printed = [call.args[0] for call in mock_print.call_args_list if call.args]
    assert any("No calculations in history" in msg for msg in printed), (
        "Expected message for empty history not found"
    )

# ----- Test history branch when history has entries -----
@patch('builtins.input', side_effect=['add', '2', '3', 'history', 'exit'])
@patch('builtins.print')
def test_repl_history_with_entries(mock_print, mock_input):
    calculator_repl()
    printed = "\n".join(call.args[0] for call in mock_print.call_args_list if call.args)
    # The REPL prints a history list containing the calculation's string,
    # such as "Addition(2, 3) = 5"
    assert "Addition(2, 3) = 5" in printed

# ----- Test the clear branch -----
@patch('builtins.input', side_effect=['clear', 'exit'])
@patch('builtins.print')
def test_repl_clear_history(mock_print, mock_input):
    with patch.object(Calculator, 'clear_history') as mock_clear:
        calculator_repl()
        mock_clear.assert_called_once()
        printed = " ".join(call.args[0] for call in mock_print.call_args_list if call.args)
        assert "History cleared" in printed

# ----- Test undo and redo branches when nothing to undo/redo -----
@patch('builtins.input', side_effect=['undo', 'redo', 'exit'])
@patch('builtins.print')
def test_repl_undo_redo_empty(mock_print, mock_input):
    calculator_repl()
    printed = [call.args[0] for call in mock_print.call_args_list if call.args]
    assert any("Nothing to undo" in msg for msg in printed)
    assert any("Nothing to redo" in msg for msg in printed)

# ----- Test unknown command branch -----
@patch('builtins.input', side_effect=['foobar', 'exit'])
@patch('builtins.print')
def test_repl_unknown_command(mock_print, mock_input):
    calculator_repl()
    printed = [call.args[0] for call in mock_print.call_args_list if call.args]
    assert any("Unknown command: 'foobar'" in msg for msg in printed)

# ----- Test save branch error -----
@patch('builtins.input', side_effect=['save', 'exit'])
@patch('builtins.print')
def test_repl_save_error(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history', side_effect=Exception("save failed")) as mock_save:
        calculator_repl()
        # Expect 2 calls: one for the 'save' command and one for the 'exit' branch.
        assert mock_save.call_count == 2
        output = " ".join(call.args[0] for call in mock_print.call_args_list if call.args)
        assert "Error saving history: save failed" in output

# ----- Test successful SAVE command outside of exit branch -----
@patch('builtins.input', side_effect=['save', 'exit'])
@patch('builtins.print')
def test_repl_save_success(mock_print, mock_input):
    # Patch save_history to succeed normally (it returns None)
    with patch('app.calculator.Calculator.save_history', return_value=None) as mock_save:
        calculator_repl()
        # Expect 2 calls: one triggered by 'save' and one triggered by 'exit'
        assert mock_save.call_count == 2
        # Check that the success message is printed
        printed_output = " ".join(call.args[0] for call in mock_print.call_args_list if call.args)
        assert "History saved successfully" in printed_output



# ----- Test arithmetic branch: valid addition -----
@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_repl_addition(mock_print, mock_input):
    calculator_repl()
    # The REPL should print a normalized decimal result (e.g., "5")
    printed = " ".join(call.args[0] for call in mock_print.call_args_list if call.args)
    assert "\nResult: 5" in printed

# ----- Test arithmetic branch: cancel on first number -----
@patch('builtins.input', side_effect=['add', 'cancel', 'exit'])
@patch('builtins.print')
def test_repl_cancel_first_number(mock_print, mock_input):
    calculator_repl()
    assert any("Operation cancelled" in str(call.args[0]) for call in mock_print.call_args_list)

@patch('builtins.input', side_effect=['add', '2', 'cancel', 'exit'])
@patch('builtins.print')
def test_repl_cancel_second_number(mock_print, mock_input):
    calculator_repl()
    assert any("Operation cancelled" in str(call.args[0]) for call in mock_print.call_args_list)


# ----- Test arithmetic branch: known error (simulate ValidationError) -----
@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_repl_arithmetic_error(mock_print, mock_input):
    from app.calculator import Calculator
    # Patch perform_operation to raise a ValidationError so we take the error branch.
    with patch.object(Calculator, 'perform_operation', side_effect=ValidationError("Test error")):
        calculator_repl()
        printed = " ".join(call.args[0] for call in mock_print.call_args_list if call.args)
        assert "Error: Test error" in printed

# ----- Test arithmetic branch: unexpected error -----
@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_repl_arithmetic_unexpected_error(mock_print, mock_input):
    from app.calculator import Calculator
    with patch.object(Calculator, 'perform_operation', side_effect=Exception("Boom")):
        calculator_repl()
        printed = " ".join(call.args[0] for call in mock_print.call_args_list if call.args)
        assert "Unexpected error: Boom" in printed

# ----- Test KeyboardInterrupt handling -----
@patch('builtins.input', side_effect=[KeyboardInterrupt, 'exit'])
@patch('builtins.print')
def test_repl_keyboard_interrupt(mock_print, mock_input):
    # The loop should catch the KeyboardInterrupt and print a cancellation notice.
    calculator_repl()
    printed = " ".join(call.args[0] for call in mock_print.call_args_list if call.args)
    assert "\nOperation cancelled" in printed

# ----- Test EOFError handling -----
@patch('builtins.input', side_effect=EOFError)
@patch('builtins.print')
def test_repl_eof_error(mock_print, mock_input):
    calculator_repl()
    printed = " ".join(call.args[0] for call in mock_print.call_args_list if call.args)
    assert "Input terminated. Exiting..." in printed


# ----- Test load branch error -----
@patch('builtins.input', side_effect=['load', 'exit'])
@patch('builtins.print')
def test_repl_load_error(mock_print, mock_input):
    with patch('app.calculator.Calculator.load_history', side_effect=Exception("load failed")) as mock_load:
        calculator_repl()
        # Expect two calls: one from __init__ and one from the 'load' command.
        assert mock_load.call_count == 2
        output = " ".join(call.args[0] for call in mock_print.call_args_list if call.args)
        assert "Error loading history: load failed" in output

# ----- Test successful LOAD command (no error) -----
@patch('builtins.input', side_effect=['load', 'exit'])
@patch('builtins.print')
def test_repl_load_success(mock_print, mock_input):
    # Patch load_history to succeed normally (it returns None)
    with patch('app.calculator.Calculator.load_history', return_value=None) as mock_load:
        calculator_repl()
        # Expect two calls: one from __init__ and one from the 'load' command.
        assert mock_load.call_count == 2
        printed_output = " ".join(call.args[0] for call in mock_print.call_args_list if call.args)
        assert "History loaded successfully" in printed_output



# ----- Test fatal error during initialization -----
@patch('app.calculator.Calculator.__init__', side_effect=Exception("Initialization failed"))
@patch('builtins.print')
def test_repl_fatal_error(mock_print, mock_init):
    with pytest.raises(Exception, match="Initialization failed"):
        calculator_repl()
    printed_output = " ".join(call.args[0] for call in mock_print.call_args_list if call.args)
    assert "Fatal error: Initialization failed" in printed_output

# ----- Test arithmetic branch: successful operation with normalized Decimal -----
@patch('builtins.input', side_effect=['multiply', '2', '3', 'exit'])
@patch('builtins.print')
def test_repl_multiplication(mock_print, mock_input):
    # This test ensures that a different arithmetic command works, printing, for example, "6"
    calculator_repl()
    printed_output = " ".join(call.args[0] for call in mock_print.call_args_list if call.args)
    # Expect the multiplication result "6" normalized as a Decimal (i.e. "6")
    assert "\nResult: 6" in printed_output

# ----- Test arithmetic branch: error handling for known errors -----
@patch('builtins.input', side_effect=['subtract', '5', '3', 'exit'])
@patch('builtins.print')
def test_repl_arithmetic_known_error(mock_print, mock_input):
    # Force an error in perform_operation (simulate a known error by raising ValidationError)
    with patch.object(Calculator, 'perform_operation', side_effect=ValidationError("Invalid input")):
        calculator_repl()
        printed_output = " ".join(call.args[0] for call in mock_print.call_args_list if call.args)
        assert "Error: Invalid input" in printed_output

# ----- Test arithmetic branch: unexpected error handling -----
@patch('builtins.input', side_effect=['power', '2', '3', 'exit'])
@patch('builtins.print')
def test_repl_arithmetic_unexpected_error(mock_print, mock_input):
    with patch.object(Calculator, 'perform_operation', side_effect=Exception("Boom")):
        calculator_repl()
        printed_output = " ".join(call.args[0] for call in mock_print.call_args_list if call.args)
        assert "Unexpected error: Boom" in printed_output
