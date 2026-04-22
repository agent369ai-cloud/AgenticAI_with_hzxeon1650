def extract_expression(text: str) -> str:
    return "".join([c for c in text if c in "0123456789+-*/(). "])