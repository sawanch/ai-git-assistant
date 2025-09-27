def calculator():
    print("Welcome to Simple Calculator")

    while True:
        try:
            num1 = float(input("\nEnter first number: "))
            num2 = float(input("Enter second number: "))

            print("\nChoose operation:")
            print("+  → Addition")
            print("-  → Subtraction")
            print("*  → Multiplication")
            print("/  → Division")
            print("** → Power")
            print("%  → Modulus")
            print("// → Floor Division")
            print("q  → Quit")

            op = input("\nEnter operator: ")

            if op == "q":
                print("Exiting calculator. Goodbye! 👋")
                break

            if op == "+":
                print("Result:", num1 + num2)
            elif op == "-":
                print("Result:", num1 - num2)
            elif op == "*":
                print("Result:", num1 * num2)
            elif op == "/":
                if num2 == 0:
                    print("Error: Cannot divide by zero.")
                else:
                    print("Result:", num1 / num2)
            elif op == "**":
                print("Result:", num1 ** num2)
            elif op == "%":
                print("Result:", num1 % num2)
            elif op == "//":
                if num2 == 0:
                    print("Error: Cannot floor divide by zero.")
                else:
                    print("Result:", num1 // num2)
            else:
                print(" Invalid operator.")
        except ValueError:
            print(" Invalid input. Please enter numbers only.")

if __name__ == "__main__":
    calculator()
