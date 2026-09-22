"""A small Tkinter calculator that runs in its own desktop window."""

import ast
import operator
import tkinter as tk
from typing import Callable


class Calculator:
    """Interactive calculator window."""

    OPERATORS: dict[type[ast.operator], Callable[[float, float], float]] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.master.title("Calculator")
        self.master.resizable(False, False)
        self.master.configure(padx=12, pady=12)

        self.result_var = tk.StringVar()
        self.result_entry = tk.Entry(
            master,
            textvariable=self.result_var,
            justify="right",
            font=("Arial", 20),
            width=16,
            relief="solid",
            bd=1,
        )
        self.result_entry.grid(row=0, column=0, columnspan=4, padx=4, pady=(0, 12))
        self.result_entry.focus_set()

        buttons = (
            ("C", 1, 0, self.clear),
            ("⌫", 1, 1, self.backspace),
            ("(", 1, 2, lambda: self.append("(")),
            (")", 1, 3, lambda: self.append(")")),
            ("7", 2, 0, lambda: self.append("7")),
            ("8", 2, 1, lambda: self.append("8")),
            ("9", 2, 2, lambda: self.append("9")),
            ("÷", 2, 3, lambda: self.append("/")),
            ("4", 3, 0, lambda: self.append("4")),
            ("5", 3, 1, lambda: self.append("5")),
            ("6", 3, 2, lambda: self.append("6")),
            ("×", 3, 3, lambda: self.append("*")),
            ("1", 4, 0, lambda: self.append("1")),
            ("2", 4, 1, lambda: self.append("2")),
            ("3", 4, 2, lambda: self.append("3")),
            ("−", 4, 3, lambda: self.append("-")),
            ("0", 5, 0, lambda: self.append("0")),
            (".", 5, 1, lambda: self.append(".")),
            ("=", 5, 2, self.calculate),
            ("+", 5, 3, lambda: self.append("+")),
        )

        for label, row, column, command in buttons:
            tk.Button(
                master,
                text=label,
                command=command,
                width=4,
                height=2,
                font=("Arial", 14),
            ).grid(row=row, column=column, padx=4, pady=4)

        self.master.bind("<Return>", lambda _event: self.calculate())
        self.master.bind("<Escape>", lambda _event: self.clear())
        self.master.bind("<BackSpace>", lambda _event: self.backspace())

    def append(self, value: str) -> None:
        """Add a button value to the expression."""
        if self.result_var.get() == "Error":
            self.clear()
        self.result_entry.insert(tk.END, value)

    def clear(self) -> None:
        self.result_var.set("")

    def backspace(self) -> None:
        value = self.result_var.get()
        if value != "Error":
            self.result_var.set(value[:-1])

    def calculate(self) -> None:
        expression = self.result_var.get().strip()
        try:
            result = self._evaluate(expression)
        except (ArithmeticError, SyntaxError, ValueError):
            self.result_var.set("Error")
            return

        self.result_var.set(str(result))

    @classmethod
    def _evaluate(cls, expression: str) -> float:
        if not expression:
            raise ValueError("An expression is required")

        tree = ast.parse(expression, mode="eval")
        return cls._evaluate_node(tree.body)

    @classmethod
    def _evaluate_node(cls, node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)

        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = cls._evaluate_node(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value

        if isinstance(node, ast.BinOp) and type(node.op) in cls.OPERATORS:
            left = cls._evaluate_node(node.left)
            right = cls._evaluate_node(node.right)
            return cls.OPERATORS[type(node.op)](left, right)

        raise ValueError("Unsupported expression")


def launch() -> None:
    """Open the calculator outside the terminal."""
    root = tk.Tk()
    Calculator(root)
    root.mainloop()


if __name__ == "__main__":
    launch()
