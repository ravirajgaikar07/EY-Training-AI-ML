try:
    value = int(input("Enter a number: "))
    print(10/value)
except ValueError:
    print("Please enter a valid number")
except ZeroDivisionError:
    print("Cannot divide by zero!")
finally:
    print("Execution completed")