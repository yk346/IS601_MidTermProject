########################
# Operation Classes    #
########################

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict
from app.exceptions import ValidationError


class Operation(ABC):
    """Abstract base class for calculator operations."""
    
    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Execute the operation.
        
        Args:
            a: First operand
            b: Second operand
            
        Returns:
            Decimal: Result of operation
            
        Raises:
            OperationError: If operation fails
        """
        pass

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """
        Validate operands before execution.
        
        Args:
            a: First operand
            b: Second operand
            
        Raises:
            ValidationError: If operands are invalid
        """
        pass

    def __str__(self) -> str:
        """Return operation name for display."""
        return self.__class__.__name__

class Addition(Operation):
    """Addition operation implementation."""
    
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Add two numbers."""
        self.validate_operands(a, b)
        return a + b

class Subtraction(Operation):
    """Subtraction operation implementation."""
    
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Subtract b from a."""
        self.validate_operands(a, b)
        return a - b

class Multiplication(Operation):
    """Multiplication operation implementation."""
    
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Multiply two numbers."""
        self.validate_operands(a, b)
        return a * b

class Division(Operation):
    """Division operation implementation."""
    
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """Validate operands, checking for division by zero."""
        super().validate_operands(a, b)
        if b == 0:
            raise ValidationError("Division by zero is not allowed")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Divide a by b."""
        self.validate_operands(a, b)
        return a / b

class Power(Operation):
    """Power (exponentiation) operation implementation."""
    
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """Validate operands for power operation."""
        super().validate_operands(a, b)
        if b < 0:
            raise ValidationError("Negative exponents not supported")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Calculate a raised to power b."""
        self.validate_operands(a, b)
        return Decimal(pow(float(a), float(b)))

class Root(Operation):
    """Root operation implementation."""
    
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """Validate operands for root operation."""
        super().validate_operands(a, b)
        if a < 0:
            raise ValidationError("Cannot calculate root of negative number")
        if b == 0:
            raise ValidationError("Zero root is undefined")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Calculate the b-th root of a."""
        self.validate_operands(a, b)
        return Decimal(pow(float(a), 1/float(b)))

########################
# Factory Pattern      #
########################

class OperationFactory:
    """Factory class for creating operation instances."""
    
    _operations: Dict[str, type] = {
        'add': Addition,
        'subtract': Subtraction,
        'multiply': Multiplication,
        'divide': Division,
        'power': Power,
        'root': Root
    }

    @classmethod
    def register_operation(cls, name: str, operation_class: type) -> None:
        """
        Register a new operation type.
        
        Args:
            name: Operation identifier
            operation_class: Operation class to register
        """
        if not issubclass(operation_class, Operation):
            raise TypeError("Operation class must inherit from Operation")
        cls._operations[name.lower()] = operation_class

    @classmethod
    def create_operation(cls, operation_type: str) -> Operation:
        """
        Create operation instance.
        
        Args:
            operation_type: Type of operation to create
            
        Returns:
            Operation instance
            
        Raises:
            ValueError: If operation type is unknown
        """
        operation_class = cls._operations.get(operation_type.lower())
        if not operation_class:
            raise ValueError(f"Unknown operation: {operation_type}")
        return operation_class()
