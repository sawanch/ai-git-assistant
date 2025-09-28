#!/usr/bin/env python3
import math
import random

def calculator():
    print("Welcome to Enhanced Calculator")

    history = []        # Store calculation history
    memory = None       # Store memory value
    last_result = None  # Store last result for reuse

    while True:
        try:
            # Input numbers (allow reuse of last_result if left blank)
            num1_input = input("\nEnter first number (leave blank for last result): ")
            if num1_input.strip() == "" and last_result is not None:
                num1 = last_result
                print("Using last result:", num1)
            else:
                num1 = float(num1_input)

            num2_input = input("Enter second number (leave blank for last result): ")
            if num2_input.strip() == "" and last_result is not None:
                num2 = last_result
                print("Using last result:", num2)
            else:
                num2 = float(num2_input)

            # Menu
            print("\nChoose operation:")
            print("+   → Addition")
            print("-   → Subtraction")
            print("*   → Multiplication")
            print("/   → Division")
            print("**  → Power")
            print("%   → Modulus")
            print("//  → Floor Division")
            print("sqrt → Square Root (uses first number)")
            print("sin  → Sine (first number in degrees)")
            print("cos  → Cosine (first number in degrees)")
            print("tan  → Tangent (first number in degrees)")
            print("rand → Random number [0,1]")
            print("m+   → Store to memory (num1 op num2)")
            print("mr   → Recall from memory")
            print("h    → View History")
            print("q    → Quit")

            op = input("\nEnter operator: ")

            if op == "q":
                print("Exiting calculator. Goodbye! 👋")

                # Save history to file
                with open("calc_history.txt", "w") as f:
                    for h in history:
                        f.write(h + "\n")
                print("History saved to calc_history.txt ✅")
                break

            result = None

            # Basic operations
            if op == "+":
                result = num1 + num2
            elif op == "-":
                result = num1 - num2
            elif op == "*":
                result = num1 * num2
            elif op == "/":
                result = "Error: Divide by zero" if num2 == 0 else num1 / num2
            elif op == "**":
                result = num1 ** num2
            elif op == "%":
                result = num1 % num2
            elif op == "//":
                result = "Error: Divide by zero" if num2 == 0 else num1 // num2

            # Scientific functions
            elif op == "sqrt":
                result = math.sqrt(num1) if num1 >= 0 else "Error: Negative input"
            elif op == "sin":
                result = math.sin(math.radians(num1))
            elif op == "cos":
                result = math.cos(math.radians(num1))
            elif op == "tan":
                result = math.tan(math.radians(num1))

            # Random number
            elif op == "rand":
                result = random.random()

            # Memory functions
            elif op == "m+":
                memory = num1 + num2
                print("Saved to memory:", memory)
                continue
            elif op == "mr":
                if memory is None:
                    print("Memory is empty")
                else:
                    print("Recalled from memory:", memory)
                continue

            # History
            elif op == "h":
                if history:
                    print("\nCalculation History:")
                    for h in history:
                        print(h)
                else:
                    print("History is empty")
                continue

            else:
                print("Invalid operator")
                continue

            # Print and save result
            print("Result:", result)
            if not isinstance(result, str):  # Save only valid results
                history.append(f"{num1} {op} {num2 if op not in ['sqrt','sin','cos','tan','rand'] else ''} = {result}")
                last_result = result

        except ValueError:
            print("Invalid input. Please enter numbers only")

if __name__ == "__main__":
    calculator()
