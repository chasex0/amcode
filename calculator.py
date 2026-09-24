"""A small Tkinter calculator that runs in its own desktop window."""

import ast
import math
import operator
import random
import tkinter as tk
from tkinter import ttk
from typing import Callable


class RoundedButton(tk.Canvas):
    """A compact rounded button that fits the calculator's visual language."""

    def __init__(
        self,
        parent: tk.Misc,
        text: str,
        command: Callable[[], None],
        width: int,
        height: int,
        background: str,
        hover_background: str,
        foreground: str,
        font: tuple[str, int, str] | tuple[str, int],
    ) -> None:
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent.cget("bg"),
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.button_width = width
        self.button_height = height
        self.text = text
        self.command = command
        self.background = background
        self.hover_background = hover_background
        self.foreground = foreground
        self.font = font
        self._draw(background)
        self.bind("<Enter>", lambda _event: self._draw(self.hover_background))
        self.bind("<Leave>", lambda _event: self._draw(self.background))
        self.bind("<Button-1>", lambda _event: self.command())

    def _draw(self, background: str) -> None:
        """Redraw the softly rounded button surface and label."""
        self.delete("all")
        radius = min(12, self.button_height // 2)
        points = (
            radius,
            0,
            self.button_width - radius,
            0,
            self.button_width,
            radius,
            self.button_width,
            self.button_height - radius,
            self.button_width - radius,
            self.button_height,
            radius,
            self.button_height,
            0,
            self.button_height - radius,
            0,
            radius,
        )
        self.create_polygon(points, fill=background, outline=background)
        self.create_text(
            self.button_width / 2,
            self.button_height / 2,
            text=self.text,
            fill=self.foreground,
            font=self.font,
        )

    def set_action(self, text: str, command: Callable[[], None]) -> None:
        """Update the label and callback without replacing the widget."""
        self.text = text
        self.command = command
        self._draw(self.background)


class Calculator:
    """Interactive calculator window."""

    COLORS = {
        "background": "#111827",
        "display": "#1F2937",
        "button": "#263244",
        "button_active": "#34445A",
        "muted": "#9CA9BB",
        "text": "#F8FAFC",
        "accent": "#2DD4BF",
        "accent_active": "#5EEAD4",
        "warning": "#F97316",
        "warning_active": "#FB923C",
    }

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
        self.master.configure(bg=self.COLORS["background"], padx=18, pady=18)

        style = ttk.Style(master)
        style.configure(
            "Modern.TNotebook",
            background=self.COLORS["background"],
            borderwidth=0,
            padding=0,
        )
        style.layout("Modern.TNotebook", [("Notebook.client", {"sticky": "nswe"})])
        style.configure(
            "Modern.TNotebook.Tab",
            background=self.COLORS["background"],
            foreground=self.COLORS["muted"],
            borderwidth=0,
            padding=(14, 7),
        )
        style.map(
            "Modern.TNotebook.Tab",
            background=[("selected", self.COLORS["display"])],
            foreground=[("selected", self.COLORS["accent"])],
        )
        notebook = ttk.Notebook(master, style="Modern.TNotebook")
        notebook.grid(row=0, column=0)
        calculator_tab = tk.Frame(master, bg=self.COLORS["background"])
        graph_tab = tk.Frame(master, bg=self.COLORS["background"])
        notebook.add(calculator_tab, text="Calculator")
        notebook.add(graph_tab, text="Graph")

        tk.Label(
            calculator_tab,
            text="CALC",
            bg=self.COLORS["background"],
            fg=self.COLORS["accent"],
            font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=4, pady=(0, 8))

        self.result_var = tk.StringVar()
        self.result_entry = tk.Entry(
            calculator_tab,
            textvariable=self.result_var,
            justify="right",
            font=("Segoe UI", 26),
            width=15,
            relief="flat",
            bd=0,
            bg=self.COLORS["display"],
            fg=self.COLORS["text"],
            insertbackground=self.COLORS["accent"],
            highlightthickness=0,
        )
        self.result_entry.grid(row=1, column=0, columnspan=4, padx=4, pady=(0, 16), ipady=10)
        self.result_entry.focus_set()

        buttons = (
            ("C", 2, 0, self.clear),
            ("⌫", 2, 1, self.backspace),
            ("(", 2, 2, lambda: self.append("(")),
            (")", 2, 3, lambda: self.append(")")),
            ("7", 3, 0, lambda: self.append("7")),
            ("8", 3, 1, lambda: self.append("8")),
            ("9", 3, 2, lambda: self.append("9")),
            ("÷", 3, 3, lambda: self.append("/")),
            ("4", 4, 0, lambda: self.append("4")),
            ("5", 4, 1, lambda: self.append("5")),
            ("6", 4, 2, lambda: self.append("6")),
            ("×", 4, 3, lambda: self.append("*")),
            ("1", 5, 0, lambda: self.append("1")),
            ("2", 5, 1, lambda: self.append("2")),
            ("3", 5, 2, lambda: self.append("3")),
            ("−", 5, 3, lambda: self.append("-")),
            ("0", 6, 0, lambda: self.append("0")),
            (".", 6, 1, lambda: self.append(".")),
            ("=", 6, 2, self.calculate),
            ("+", 6, 3, lambda: self.append("+")),
        )

        for label, row, column, command in buttons:
            is_action = label in {"C", "⌫", "(", ")"}
            is_operator = label in {"÷", "×", "−", "+"}
            button_color = self.COLORS["button"]
            active_color = self.COLORS["button_active"]
            if is_action:
                button_color = self.COLORS["muted"]
                active_color = self.COLORS["text"]
            elif is_operator:
                button_color = self.COLORS["warning"]
                active_color = self.COLORS["warning_active"]
            if label == "=":
                button_color = self.COLORS["accent"]
                active_color = self.COLORS["accent_active"]
            RoundedButton(
                calculator_tab,
                text=label,
                command=command,
                width=64,
                height=46,
                background=button_color,
                hover_background=active_color,
                foreground=self.COLORS["background"] if is_action else self.COLORS["text"],
                font=("Segoe UI", 14, "bold"),
            ).grid(row=row, column=column, padx=4, pady=4)

        RoundedButton(
            calculator_tab,
            text="game",
            command=self.open_game,
            width=68,
            height=28,
            background=self.COLORS["button"],
            hover_background=self.COLORS["button_active"],
            foreground=self.COLORS["accent"],
            font=("Segoe UI", 9, "bold"),
        ).grid(row=7, column=3, sticky="e", padx=4, pady=(8, 0))

        self._build_graph_tab(graph_tab)

        self.master.bind("<Return>", lambda _event: self.calculate())
        self.master.bind("<Escape>", lambda _event: self.clear())
        self.master.bind("<BackSpace>", lambda _event: self.backspace())

    def _build_graph_tab(self, parent: tk.Frame) -> None:
        """Build the lightweight function plotter tab."""
        tk.Label(
            parent,
            text="GRAPHING CALCULATOR",
            bg=self.COLORS["background"],
            fg=self.COLORS["accent"],
            font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=4, pady=(4, 10))

        tk.Label(
            parent,
            text="y =",
            bg=self.COLORS["background"],
            fg=self.COLORS["muted"],
            font=("Segoe UI", 12),
        ).grid(row=1, column=0, padx=(4, 0), pady=(0, 10))
        self.graph_expression = tk.Entry(
            parent,
            width=28,
            font=("Segoe UI", 12),
            bg=self.COLORS["display"],
            fg=self.COLORS["text"],
            insertbackground=self.COLORS["accent"],
            relief="flat",
            bd=0,
        )
        self.graph_expression.insert(0, "sin(x)")
        self.graph_expression.grid(row=1, column=1, padx=(6, 4), pady=(0, 10), ipady=5)
        self.graph_expression.bind("<Return>", lambda _event: self.plot_graph())

        RoundedButton(
            parent,
            text="Plot",
            command=self.plot_graph,
            width=72,
            height=32,
            background=self.COLORS["accent"],
            hover_background=self.COLORS["accent_active"],
            foreground=self.COLORS["background"],
            font=("Segoe UI", 10, "bold"),
        ).grid(row=2, column=0, columnspan=2, sticky="e", padx=4, pady=(0, 8))

        self.graph_canvas = tk.Canvas(
            parent,
            width=430,
            height=260,
            bg=self.COLORS["display"],
            highlightthickness=0,
        )
        self.graph_canvas.grid(row=3, column=0, columnspan=2, padx=4, pady=(0, 4))
        self.plot_graph()

    def plot_graph(self) -> None:
        """Plot the entered function over the visible x range."""
        expression = self.graph_expression.get().strip()
        canvas = self.graph_canvas
        width = int(canvas.cget("width"))
        height = int(canvas.cget("height"))
        canvas.delete("all")

        x_min, x_max = -10.0, 10.0
        y_min, y_max = -5.0, 5.0
        x_axis = height * y_max / (y_max - y_min)
        y_axis = width * -x_min / (x_max - x_min)
        canvas.create_line(0, x_axis, width, x_axis, fill=self.COLORS["muted"])
        canvas.create_line(y_axis, 0, y_axis, height, fill=self.COLORS["muted"])

        points: list[float] = []
        for index in range(width):
            x = x_min + (x_max - x_min) * index / (width - 1)
            try:
                y = self._evaluate_graph(expression, x)
            except (ArithmeticError, SyntaxError, ValueError):
                points = []
                break
            if not math.isfinite(y) or abs(y) > 1000:
                points.append(float("nan"))
            else:
                points.append(height * (y_max - y) / (y_max - y_min))

        previous: tuple[float, float] | None = None
        for index, y in enumerate(points):
            if math.isnan(y):
                previous = None
                continue
            current = (float(index), y)
            if previous is not None and abs(y - previous[1]) < height * 2:
                canvas.create_line(*previous, *current, fill=self.COLORS["accent"], width=2)
            previous = current

        if not points:
            canvas.create_text(
                width / 2,
                height / 2,
                text="Try an expression like sin(x) or x^2",
                fill=self.COLORS["muted"],
                font=("Segoe UI", 10),
            )

    @staticmethod
    def _evaluate_graph(expression: str, x_value: float) -> float:
        """Evaluate a graph expression using only approved math operations."""
        expression = expression.replace("^", "**")
        tree = ast.parse(expression, mode="eval")
        functions = {name: getattr(math, name) for name in ("sin", "cos", "tan", "sqrt", "log", "exp")}

        def evaluate(node: ast.AST) -> float:
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return float(node.value)
            if isinstance(node, ast.Name) and node.id == "x":
                return x_value
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                value = evaluate(node.operand)
                return value if isinstance(node.op, ast.UAdd) else -value
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
                return evaluate(node.left) ** evaluate(node.right)
            if isinstance(node, ast.BinOp) and type(node.op) in Calculator.OPERATORS:
                return Calculator.OPERATORS[type(node.op)](evaluate(node.left), evaluate(node.right))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in functions:
                if len(node.args) != 1 or node.keywords:
                    raise ValueError("Function requires one argument")
                return functions[node.func.id](evaluate(node.args[0]))
            raise ValueError("Unsupported graph expression")

        return evaluate(tree.body)

    def open_game(self) -> None:
        """Open the guessing game in a separate window."""
        NumberGuessGame(self.master)

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


class NumberGuessGame:
    """A small number guessing game launched from the calculator."""

    def __init__(self, master: tk.Tk) -> None:
        self.window = tk.Toplevel(master)
        self.window.title("Guess the Number")
        self.window.resizable(False, False)
        self.window.configure(bg=Calculator.COLORS["background"], padx=22, pady=22)
        self.secret_number = random.randint(1, 100)
        self.attempts = 0

        tk.Label(
            self.window,
            text="GUESS THE NUMBER",
            bg=Calculator.COLORS["background"],
            fg=Calculator.COLORS["accent"],
            font=("Segoe UI", 13, "bold"),
        ).pack(pady=(0, 4))

        tk.Label(
            self.window,
            text="I am thinking of a number from 1 to 100.",
            bg=Calculator.COLORS["background"],
            fg=Calculator.COLORS["muted"],
            font=("Segoe UI", 10),
        ).pack(pady=(0, 14))

        self.guess_entry = tk.Entry(
            self.window,
            justify="center",
            font=("Segoe UI", 18),
            width=8,
            bg=Calculator.COLORS["display"],
            fg=Calculator.COLORS["text"],
            insertbackground=Calculator.COLORS["accent"],
            relief="flat",
            bd=0,
        )
        self.guess_entry.pack(ipady=6)
        self.guess_entry.focus_set()

        self.message_var = tk.StringVar(value="Make your first guess!")
        tk.Label(
            self.window,
            textvariable=self.message_var,
            bg=Calculator.COLORS["background"],
            fg=Calculator.COLORS["text"],
            font=("Segoe UI", 10),
            width=28,
            wraplength=240,
        ).pack(pady=10)

        self.guess_button = RoundedButton(
            self.window,
            text="Guess",
            command=self.check_guess,
            width=100,
            height=38,
            background=Calculator.COLORS["accent"],
            hover_background=Calculator.COLORS["accent_active"],
            foreground=Calculator.COLORS["background"],
            font=("Segoe UI", 10, "bold"),
        )
        self.guess_button.pack()
        self.window.bind("<Return>", lambda _event: self.check_guess())

    def check_guess(self) -> None:
        """Check the player's current guess and provide a hint."""
        try:
            guess = int(self.guess_entry.get())
        except ValueError:
            self.message_var.set("Enter a whole number between 1 and 100.")
            return

        if not 1 <= guess <= 100:
            self.message_var.set("Keep your guess between 1 and 100.")
            return

        self.attempts += 1
        if guess < self.secret_number:
            self.message_var.set("Too low. Try a bigger number.")
        elif guess > self.secret_number:
            self.message_var.set("Too high. Try a smaller number.")
        else:
            self.message_var.set(f"You got it in {self.attempts} guesses!")
            self.guess_button.set_action("Play again", self.reset)

    def reset(self) -> None:
        """Start a fresh round."""
        self.secret_number = random.randint(1, 100)
        self.attempts = 0
        self.guess_entry.delete(0, tk.END)
        self.message_var.set("Make your first guess!")
        self.guess_button.set_action("Guess", self.check_guess)
        self.guess_entry.focus_set()


def launch() -> None:
    """Open the calculator outside the terminal."""
    root = tk.Tk()
    Calculator(root)
    root.mainloop()


if __name__ == "__main__":
    launch()
