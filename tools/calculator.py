import re

def calculate(expression: str) -> str:
    if not re.match(r"^[0-9+\-*/(). ]+$", expression):
        return "Invalid expression"

    try:
        return str(eval(expression))
    except:
        return "Calculation error"