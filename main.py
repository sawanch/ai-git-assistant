#!/usr/bin/env python3
import math
import random
import logging
from typing import Optional, Union, List, Callable

# Configure logging
logging.basicConfig(
    filename="calculator.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

Number = Union[int, float]


class Calculator:
    def __init__(self):
        self.history: List[str] = []
        self.memory: Optional[Number] = None
        self.last_result: Optional[Number] = None
        self.history_file = "calc_history.txt"
        self.load_history()

        # Map operators to functions
        self.operations: dict[str, Callable[[Number, Number], Union[Number, str]]] = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: "Error: Divide by zero" if b == 0 else a / b,
            "**": lambda a, b: a ** b,
            "%": lambda a, b: a % b,
            "//": lambda a, b: "Error: Divide by zero" if b == 0 else a // b,
        }

    def load_history(self):
        try:
            with open(self.history_file, "r") as f:
                self.history = f.read().splitlines()
        except FileNotFoundError:
            self.history = []

    def save_history(self):
        with open(self.history_file, "w") as f:
            f.writelines(h + "\n" for h in self.history)

    def run(self):
        print("Welcome to Production-Ready Calculator 🚀")
        while True:
            try:
                op = input(
                    "\nEnter operator (h=history, q=quit, conv=unit conversion): "
                ).strip()

                if op == "q":
                    print("Exiting calculator. Goodbye! 👋")
                    self.save_history()
                    break
                elif op == "h":
                    self._print_history()
                    continue
                elif op == "conv":
                    self._unit_conversion()
                    continue

                num1 = self._get_number("Enter first number (blank = last result): ")
                num2 = self._get_number("Enter second number (blank = last result): ")

                if op == "m+":
                    self.memory = num1 + num2
                    print("Saved to memory:", self.memory)
                    continue
                elif op == "mr":
                    print("Memory:", self.memory if self.memory is not None else "Empty")
                    continue
                elif op in self.operations:
                    result = self.operations[op](num1, num2)
                else:
                    result = self._scientific_operations(op, num1)

                self._handle_result(op, num1, num2, result)

            except ValueError:
                print("Invalid input. Please enter valid numbers.")
                logging.warning("Invalid numeric input")
            except Exception as e:
                print("Unexpected error:", str(e))
                logging.exception("Unhandled exception")

    def _get_number(self, prompt: str) -> Number:
        user_input = input(prompt).strip()
        if user_input == "" and self.last_result is not None:
            print("Using last result:", self.last_result)
            return self.last_result
        return float(user_input)

    def _scientific_operations(self, op: str, num1: Number) -> Union[Number, str, None]:
        if op == "sqrt":
            return math.sqrt(num1) if num1 >= 0 else "Error: Negative input"
        elif op == "sin":
            return math.sin(math.radians(num1))
        elif op == "cos":
            return math.cos(math.radians(num1))
        elif op == "tan":
            return math.tan(math.radians(num1))
        elif op == "rand":
            return random.random()
        return None

    def _unit_conversion(self):
        print("\nUnit Conversion Options:")
        print("1. Kilometers → Miles")
        print("2. Miles → Kilometers")
        print("3. Celsius → Fahrenheit")
        print("4. Fahrenheit → Celsius")
        print("5. Kilograms → Pounds")
        print("6. Pounds → Kilograms")

        choice = input("Choose an option (1-6): ").strip()
        try:
            value = float(input("Enter value to convert: "))

            conversions = {
                "1": (lambda v: v * 0.621371, "miles"),
                "2": (lambda v: v / 0.621371, "km"),
                "3": (lambda v: (v * 9 / 5) + 32, "°F"),
                "4": (lambda v: (v - 32) * 5 / 9, "°C"),
                "5": (lambda v: v * 2.20462, "lbs"),
                "6": (lambda v: v / 2.20462, "kg"),
            }

            if choice in conversions:
                func, unit = conversions[choice]
                result = func(value)
                print(f"Converted: {result:.4f} {unit}")
                record = f"Conversion {value} -> {result:.4f} {unit}"
                self.history.append(record)
                logging.info(record)
            else:
                print("Invalid choice")
        except ValueError:
            print("Invalid number for conversion")

    def _handle_result(self, op: str, num1: Number, num2: Number, result: Union[Number, str, None]):
        if result is None:
            print("Invalid operator")
            return
        print("Result:", result)
        if not isinstance(result, str):
            record = f"{num1} {op} {num2 if op not in ['sqrt','sin','cos','tan','rand'] else ''} = {result}"
            self.history.append(record)
            self.last_result = result
            logging.info("Calculated: %s", record)

    def _print_history(self):
        if self.history:
            print("\nCalculation History:")
            for h in self.history:
                print(h)
        else:
            print("History is empty")


if __name__ == "__main__":
    calc = Calculator()
    calc.run()
