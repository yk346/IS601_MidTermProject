# Module 5: Advanced Design Patterns and Data Management with pandas in Python

[module contents](module_contents.md)
## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/kaw393939/module5_is601.git
   cd calculator
   ```

2. Set up the virtual environment and install dependencies:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. To set up the environment variables, create a `.env` file in the project root:

   ```env
   CALCULATOR_MAX_HISTORY_SIZE=100
   CALCULATOR_AUTO_SAVE=true
   CALCULATOR_DEFAULT_ENCODING=utf-8
   ```

4. Run the program:

   ```bash
   python3 main.py
   ```

## Usage

The calculator supports the following commands in its REPL interface:

- **Basic Operations**:
  - `add`, `subtract`, `multiply`, `divide`
- **Advanced Operations**:
  - `power`, `root`
- **History Commands**:
  - `history` - Shows all past calculations
  - `clear` - Clears the calculation history
  - `undo`, `redo` - Undo/redo last operation
- **File Operations**:
  - `save`, `load` - Save/load calculation history to/from file
  - `exit` - Exit the calculator

## Configuration

The calculator's behavior can be customized through either environment variables or directly in the `CalculatorConfig` class. Available settings include:

- `CALCULATOR_BASE_DIR`: Base directory for saving logs and history files.
- `CALCULATOR_MAX_HISTORY_SIZE`: Maximum size of the calculation history.
- `CALCULATOR_AUTO_SAVE`: Automatically save history after each operation.
- `CALCULATOR_PRECISION`: Decimal precision of results.
- `CALCULATOR_MAX_INPUT_VALUE`: Maximum allowable input value.
- `CALCULATOR_DEFAULT_ENCODING`: Default encoding for files.

## Testing

To run the unit tests for this calculator:

```bash
pytest
```

Code coverage reports are generated and stored in the `htmlcov` directory.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for more details.
