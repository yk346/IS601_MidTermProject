########################
# Calculator REPL       #
########################

from decimal import Decimal
import logging

from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory
from colorama import init, Fore, Style

init(autoreset=True)

print(Fore.CYAN + Style.BRIGHT + "Welcome to the Colorful Calculator!")
print(Fore.YELLOW + "Type 'exit' to quit.")


def calculator_repl():
    """
    Command-line interface for the calculator.

    Implements a Read-Eval-Print Loop (REPL) that continuously prompts the user
    for commands, processes arithmetic operations, and manages calculation history.
    """
    try:
        # Initialize the Calculator instance
        calc = Calculator()

        # Register observers for logging and auto-saving history
        calc.add_observer(LoggingObserver())
        calc.add_observer(AutoSaveObserver(calc))

        print(Fore.CYAN + "Calculator started. Type 'help' for commands.")

        while True:
            try:
                # Prompt the user for a command
                command = input("\nEnter command: ").lower().strip()

                if command == 'help':
                    # Display available commands
                    print(Fore.CYAN + "\nAvailable commands:")
                    print(Fore.YELLOW + "  add, subtract, multiply, divide, power, root, modulus")
                    print(Fore.YELLOW + "  intdivision - Floor division (integer quotient)")
                    print(Fore.YELLOW + "  percentage - Percent of one number w.r.t. another (rounded to 2 decimals)")
                    print(Fore.YELLOW + "  absdifference - Absolute difference between two numbers")
                    print(Fore.CYAN + "  history - Show calculation history")
                    print(Fore.CYAN + "  clear - Clear calculation history")
                    print(Fore.CYAN + "  undo - Undo the last calculation")
                    print(Fore.CYAN + "  redo - Redo the last undone calculation")
                    print(Fore.CYAN + "  save - Save calculation history to file")
                    print(Fore.CYAN + "  load - Load calculation history from file")
                    print(Fore.RED + "  exit - Exit the calculator")
                    continue

                if command == 'exit':
                    try:
                        calc.save_history()
                        print(Fore.GREEN + "History saved successfully.")
                    except Exception as e:
                        print(Fore.RED + f"Warning: Could not save history: {e}")
                    print(Fore.CYAN + "Goodbye!")
                    break

                if command == 'history':
                    history = calc.show_history()
                    if not history:
                        print(Fore.YELLOW + "No calculations in history.")
                    else:
                        print(Fore.CYAN + "\nCalculation History:")
                        for i, entry in enumerate(history, 1):
                            print(Fore.WHITE + f"{i}. {entry}")
                    continue

                if command == 'clear':
                    calc.clear_history()
                    print(Fore.GREEN + "History cleared.")
                    continue

                if command == 'undo':
                    if calc.undo():
                        print(Fore.GREEN + "Operation undone.")
                    else:
                        print(Fore.YELLOW + "Nothing to undo.")
                    continue

                if command == 'redo':
                    if calc.redo():
                        print(Fore.GREEN + "Operation redone.")
                    else:
                        print(Fore.YELLOW + "Nothing to redo.")
                    continue

                if command == 'save':
                    try:
                        calc.save_history()
                        print(Fore.GREEN + "History saved successfully.")
                    except Exception as e:
                        print(Fore.RED + f"Error saving history: {e}")
                    continue

                if command == 'load':
                    try:
                        calc.load_history()
                        print(Fore.GREEN + "History loaded successfully.")
                    except Exception as e:
                        print(Fore.RED + f"Error loading history: {e}")
                    continue

                if command in ['add', 'subtract', 'multiply', 'divide', 'power', 'root', 'modulus', 'intdivision', 'percentage', 'absdifference']:
                    # Perform the specified arithmetic operation
                    try:
                        print(Fore.YELLOW + "\nEnter numbers (or type 'cancel' to abort):")
                        a = input(Fore.BLUE + "First number: ")
                        if a.lower() == 'cancel':
                            print(Fore.CYAN + "Operation cancelled.")
                            continue
                        b = input(Fore.BLUE + "Second number: ")
                        if b.lower() == 'cancel':
                            print(Fore.CYAN + "Operation cancelled.")
                            continue

                        # Create the appropriate operation instance using the Factory pattern
                        operation = OperationFactory.create_operation(command)
                        calc.set_operation(operation)

                        # Perform the calculation
                        result = calc.perform_operation(a, b)

                        # Normalize the result if it's a Decimal
                        if isinstance(result, Decimal):
                            result = result.normalize()

                        print(f"\nResult: {result}")
                    except (ValidationError, OperationError) as e:
                        # Handle known exceptions related to validation or operation errors
                        print(f"Error: {e}")
                    except Exception as e:
                        # Handle any unexpected exceptions
                        print(f"Unexpected error: {e}")
                    continue

                # Handle unknown commands
                print(Fore.RED + f"Unknown command: '{command}'. Type 'help' for available commands.")


            except KeyboardInterrupt:
                # Handle Ctrl+C interruption gracefully
                print(Fore.CYAN + "\nOperation cancelled by user.")
                continue
            except EOFError:
                # Handle end-of-file (e.g., Ctrl+D) gracefully
                print(Fore.CYAN + "\nInput terminated. Exiting...")
                break
            except Exception as e:
                # Handle any other unexpected exceptions
                print(Fore.RED + f"Unhandled error: {e}")
                continue

    except Exception as e:
        # Handle fatal errors during initialization
        print(Fore.RED + f"Fatal error: {e}")
        logging.error(f"Fatal error in calculator REPL: {e}")
        raise
