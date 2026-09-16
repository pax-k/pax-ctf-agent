PROGRAM = [("PUSH", 7), ("PUSH", 6), ("MUL", None), ("PUSH", 1), ("ADD", None)]


def run(program):
    stack = []
    for opcode, value in program:
        if opcode == "PUSH":
            stack.append(value)
        elif opcode == "MUL":
            stack.append(stack.pop() * stack.pop())
        elif opcode == "ADD":
            stack.append(stack.pop() + stack.pop())
    return stack[-1]


if __name__ == "__main__":
    print(run(PROGRAM))
