import tkinter as tk
from tkinter import font as tkfont
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Callable
import operator
import re


@dataclass(frozen=True)
class ThemeColors:
    background: str = "#1a1a2e"
    display_bg: str = "#16213e"
    display_text: str = "#eef2f5"
    number_btn: str = "#0f3460"
    number_hover: str = "#1a4a7a"
    operator_btn: str = "#e94560"
    operator_hover: str = "#ff6b6b"
    equals_btn: str = "#00d9ff"
    equals_hover: str = "#5ce1e6"
    clear_btn: str = "#ff6b35"
    clear_hover: str = "#ff8c5a"
    text_light: str = "#ffffff"
    history_bg: str = "#0d1b2a"
    history_text: str = "#8892b0"


class ButtonType(Enum):
    NUMBER = "number"
    OPERATOR = "operator"
    EQUALS = "equals"
    CLEAR = "clear"
    FUNCTION = "function"


class SafeExpressionEvaluator:
    OPERATORS: dict[str, Callable[[float, float], float]] = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
    }
    
    PRECEDENCE: dict[str, int] = {'+': 1, '-': 1, '*': 2, '/': 2}
    
    @classmethod
    def evaluate(cls, expression: str) -> float:
        tokens = cls._tokenize(expression)
        if not tokens:
            raise ValueError("Empty expression")
        return cls._parse_expression(tokens)
    
    @classmethod
    def _tokenize(cls, expression: str) -> List[str]:
        expression = expression.replace(" ", "")
        tokens: List[str] = []
        current_number = ""
        
        for i, char in enumerate(expression):
            if char.isdigit() or char == '.':
                current_number += char
            elif char in cls.OPERATORS:
                if char == '-' and (not tokens or tokens[-1] in cls.OPERATORS):
                    current_number += char
                else:
                    if current_number:
                        tokens.append(current_number)
                        current_number = ""
                    tokens.append(char)
            else:
                raise ValueError(f"Invalid character: {char}")
        
        if current_number:
            tokens.append(current_number)
            
        return tokens
    
    @classmethod
    def _parse_expression(cls, tokens: List[str]) -> float:
        output_queue: List[float] = []
        operator_stack: List[str] = []
        
        for token in tokens:
            if token not in cls.OPERATORS:
                output_queue.append(float(token))
            else:
                while (operator_stack and 
                       operator_stack[-1] in cls.OPERATORS and
                       cls.PRECEDENCE[operator_stack[-1]] >= cls.PRECEDENCE[token]):
                    cls._apply_operator(output_queue, operator_stack.pop())
                operator_stack.append(token)
        
        while operator_stack:
            cls._apply_operator(output_queue, operator_stack.pop())
        
        if len(output_queue) != 1:
            raise ValueError("Invalid expression")
            
        return output_queue[0]
    
    @classmethod
    def _apply_operator(cls, output: List[float], op: str) -> None:
        if len(output) < 2:
            raise ValueError("Invalid expression")
        b, a = output.pop(), output.pop()
        output.append(cls.OPERATORS[op](a, b))


class CalculatorButton:
    def __init__(
        self,
        parent: tk.Frame,
        text: str,
        button_type: ButtonType,
        theme: ThemeColors,
        command: Callable[[], None],
        row: int,
        column: int,
        columnspan: int = 1
    ) -> None:
        self.theme = theme
        self.bg_color, self.hover_color = self._get_colors(button_type)
        
        self.widget = tk.Button(
            parent,
            text=text,
            font=("SF Pro Display", 22, "bold"),
            bg=self.bg_color,
            fg=theme.text_light,
            activebackground=self.hover_color,
            activeforeground=theme.text_light,
            border=0,
            cursor="hand2",
            command=command
        )
        
        self.widget.grid(
            row=row, 
            column=column, 
            columnspan=columnspan,
            padx=3, 
            pady=3, 
            sticky="nsew"
        )
        
        self._bind_hover_events()
    
    def _get_colors(self, button_type: ButtonType) -> tuple[str, str]:
        color_map = {
            ButtonType.NUMBER: (self.theme.number_btn, self.theme.number_hover),
            ButtonType.OPERATOR: (self.theme.operator_btn, self.theme.operator_hover),
            ButtonType.EQUALS: (self.theme.equals_btn, self.theme.equals_hover),
            ButtonType.CLEAR: (self.theme.clear_btn, self.theme.clear_hover),
            ButtonType.FUNCTION: (self.theme.operator_btn, self.theme.operator_hover),
        }
        return color_map.get(button_type, (self.theme.number_btn, self.theme.number_hover))
    
    def _bind_hover_events(self) -> None:
        self.widget.bind("<Enter>", lambda e: self.widget.configure(bg=self.hover_color))
        self.widget.bind("<Leave>", lambda e: self.widget.configure(bg=self.bg_color))


class Calculator:
    SYMBOL_MAP: dict[str, str] = {"÷": "/", "×": "*", "−": "-"}
    REVERSE_SYMBOL_MAP: dict[str, str] = {v: k for k, v in SYMBOL_MAP.items()}
    
    KEY_BINDINGS: dict[str, str] = {
        "0": "0", "1": "1", "2": "2", "3": "3", "4": "4",
        "5": "5", "6": "6", "7": "7", "8": "8", "9": "9",
        ".": ".", "+": "+", "-": "−", "*": "×", "/": "÷",
        "Return": "=", "equal": "=", "BackSpace": "⌫",
        "Escape": "C", "c": "C", "Delete": "C",
        "percent": "%", "p": "%",
    }
    
    def __init__(self, theme: Optional[ThemeColors] = None) -> None:
        self.theme = theme or ThemeColors()
        self.current_input: str = ""
        self.history: List[str] = []
        self.history_index: int = -1
        
        self._setup_window()
        self._setup_variables()
        self._create_display()
        self._create_history_display()
        self._create_buttons()
        self._bind_keyboard()
    
    def _setup_window(self) -> None:
        self.window = tk.Tk()
        self.window.title("🧮 Modern Calculator")
        self.window.geometry("350x550")
        self.window.resizable(False, False)
        self.window.configure(bg=self.theme.background)
        
        try:
            self.window.iconname("Calculator")
        except tk.TclError:
            pass
    
    def _setup_variables(self) -> None:
        self.display_text = tk.StringVar(value="0")
        self.history_text = tk.StringVar(value="")
    
    def _create_display(self) -> None:
        display_frame = tk.Frame(
            self.window, 
            bg=self.theme.display_bg, 
            pady=15
        )
        display_frame.pack(fill="x", padx=10, pady=(15, 5))
        
        self.display_label = tk.Label(
            display_frame,
            textvariable=self.display_text,
            font=("SF Pro Display", 42, "bold"),
            bg=self.theme.display_bg,
            fg=self.theme.display_text,
            anchor="e",
            padx=20
        )
        self.display_label.pack(fill="both", expand=True)
    
    def _create_history_display(self) -> None:
        history_frame = tk.Frame(self.window, bg=self.theme.history_bg)
        history_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        history_label = tk.Label(
            history_frame,
            textvariable=self.history_text,
            font=("SF Pro Display", 14),
            bg=self.theme.history_bg,
            fg=self.theme.history_text,
            anchor="e",
            padx=20,
            pady=5
        )
        history_label.pack(fill="both")
    
    def _create_buttons(self) -> None:
        button_frame = tk.Frame(self.window, bg=self.theme.background)
        button_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        layout: List[List[tuple[str, ButtonType]]] = [
            [("C", ButtonType.CLEAR), ("±", ButtonType.FUNCTION), 
             ("%", ButtonType.FUNCTION), ("÷", ButtonType.OPERATOR)],
            [("7", ButtonType.NUMBER), ("8", ButtonType.NUMBER), 
             ("9", ButtonType.NUMBER), ("×", ButtonType.OPERATOR)],
            [("4", ButtonType.NUMBER), ("5", ButtonType.NUMBER), 
             ("6", ButtonType.NUMBER), ("−", ButtonType.OPERATOR)],
            [("1", ButtonType.NUMBER), ("2", ButtonType.NUMBER), 
             ("3", ButtonType.NUMBER), ("+", ButtonType.OPERATOR)],
            [("0", ButtonType.NUMBER), (".", ButtonType.NUMBER), 
             ("⌫", ButtonType.CLEAR), ("=", ButtonType.EQUALS)],
        ]
        
        for i in range(5):
            button_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            button_frame.grid_columnconfigure(i, weight=1)
        
        for row_idx, row in enumerate(layout):
            for col_idx, (text, btn_type) in enumerate(row):
                CalculatorButton(
                    parent=button_frame,
                    text=text,
                    button_type=btn_type,
                    theme=self.theme,
                    command=lambda t=text: self._on_button_click(t),
                    row=row_idx,
                    column=col_idx
                )
    
    def _bind_keyboard(self) -> None:
        self.window.bind("<Key>", self._on_key_press)
        self.window.bind("<Return>", lambda e: self._on_button_click("="))
        self.window.bind("<BackSpace>", lambda e: self._on_button_click("⌫"))
        self.window.bind("<Escape>", lambda e: self._on_button_click("C"))
        self.window.bind("<Up>", lambda e: self._navigate_history(-1))
        self.window.bind("<Down>", lambda e: self._navigate_history(1))
    
    def _on_key_press(self, event: tk.Event) -> None:
        key = event.keysym if len(event.keysym) > 1 else event.char
        if key in self.KEY_BINDINGS:
            self._on_button_click(self.KEY_BINDINGS[key])
        elif key.isdigit():
            self._on_button_click(key)
    
    def _navigate_history(self, direction: int) -> None:
        if not self.history:
            return
        
        new_index = self.history_index + direction
        if 0 <= new_index < len(self.history):
            self.history_index = new_index
            self.current_input = self.history[self.history_index]
            self.display_text.set(self.current_input)
    
    def _on_button_click(self, button_text: str) -> None:
        handlers: dict[str, Callable[[], None]] = {
            "C": self._clear,
            "=": self._calculate,
            "⌫": self._backspace,
            "±": self._toggle_sign,
            "%": self._percentage,
        }
        
        if button_text in handlers:
            handlers[button_text]()
        else:
            self._append_to_input(button_text)
    
    def _clear(self) -> None:
        self.current_input = ""
        self.display_text.set("0")
        self.history_text.set("")
        self.history_index = -1
    
    def _backspace(self) -> None:
        self.current_input = self.current_input[:-1]
        self.display_text.set(self.current_input if self.current_input else "0")
    
    def _toggle_sign(self) -> None:
        if not self.current_input or self.current_input == "0":
            return
        
        if self.current_input.startswith("-"):
            self.current_input = self.current_input[1:]
        else:
            self.current_input = "-" + self.current_input
        
        self.display_text.set(self.current_input)
    
    def _percentage(self) -> None:
        if not self.current_input:
            return
        
        try:
            expression = self._to_internal_format(self.current_input)
            result = SafeExpressionEvaluator.evaluate(expression) / 100
            self.current_input = str(result)
            self.display_text.set(self._format_result(result))
        except (ValueError, ZeroDivisionError):
            pass
    
    def _append_to_input(self, char: str) -> None:
        operators = "÷×−+."
        
        if char in operators and self.current_input:
            if self.current_input[-1] in operators:
                return
        
        if char == ".":
            parts = self.current_input
            for op in "÷×−+":
                parts = parts.replace(op, " ")
            last_number = parts.split()[-1] if parts.split() else ""
            if "." in last_number:
                return
        
        self.current_input += char
        self.display_text.set(self.current_input)
    
    def _to_internal_format(self, expression: str) -> str:
        for display_sym, internal_sym in self.SYMBOL_MAP.items():
            expression = expression.replace(display_sym, internal_sym)
        return expression
    
    def _calculate(self) -> None:
        if not self.current_input:
            return
        
        expression = self.current_input
        internal_expr = self._to_internal_format(expression)
        
        try:
            result = SafeExpressionEvaluator.evaluate(internal_expr)
            formatted = self._format_result(result)
            
            self.history_text.set(f"{expression} =")
            self.history.append(expression)
            self.history_index = len(self.history)
            
            self.current_input = str(result)
            self.display_text.set(formatted)
            
        except ZeroDivisionError:
            self.display_text.set("Error: ÷ by 0")
            self.current_input = ""
        except ValueError:
            self.display_text.set("Error")
            self.current_input = ""
    
    def _format_result(self, result: float) -> str:
        if isinstance(result, float) and result == int(result):
            return str(int(result))
        
        formatted = f"{result:.10g}"
        return formatted
    
    def run(self) -> None:
        self.window.update_idletasks()
        
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
        self.window.mainloop()


if __name__ == "__main__":
    calculator = Calculator()
    calculator.run()
