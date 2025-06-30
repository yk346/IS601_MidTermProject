# 🧮 Colorful CLI Calculator

A powerful command-line calculator built with Python that supports dynamic operations, rich color-coded output, undo/redo functionality, persistent history, and extensibility through design patterns like Factory, Observer, Memento, and Decorator.

---

## 🚀 Features

- Perform operations: addition, subtraction, multiplication, division, power, root, modulus, integer division, percentage, absolute difference
- Undo/Redo previous calculations
- Save/load calculation history
- Color-coded user interface with `colorama`
- Extensible via **Factory Pattern** for operations
- Logging and automatic history persistence
- Unit tested with support for test coverage

---

💡 Supported Commands:

- add           ->  Add two numbers
- subtract      ->  Subtract two numbers
- multiply      ->  Multiply two numbers
- divide        ->  Divide one number by another
- power         ->  Raise one number to the power of another
- root          ->  Take the nth root of a number
- modulus       ->  Modulo operation (a % b)
- intdivision   ->  Floor division (rounds down)
- percentage    ->  (a / b) * 100 rounded to 2 decimals
- absdifference ->  Absolute difference between numbers

- history       ->  Show previous calculations
- undo          ->  Undo last operation
- redo          ->  Redo last undone operation
- save          ->  Save current history
- load          ->  Load saved history
- clear         ->  Clear entire history
- help          ->  Show all available commands
- exit          ->  Exit the calculator

## 🛠️ Installation

### Clone the repository and run the calculator

```bash
git clone https://github.com/yk346/IS601_MidTermProject.git

### Run the calculator
cd IS601_MidTermProject #go to the cloned folder
python3 main.py # run the calculator app