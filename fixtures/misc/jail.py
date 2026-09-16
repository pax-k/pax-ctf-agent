ALLOWED = {"len": len, "sum": sum, "range": range}
expression = input("expression> ")
print(eval(expression, {"__builtins__": ALLOWED}, {}))
