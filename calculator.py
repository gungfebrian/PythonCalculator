import tkinter as tk

class Colors:
    BACKGROUND = "#1a1a2e"
    DISPLAY_BG = "#16213e"
    DISPLAY_TEXT = "#eef2f5"
    NUMBER = "#0f3460"
    NUMBER_HOVER = "#1a4a7a"
    OPERATOR = "#e94560"
    OPERATOR_HOVER = "#ff6b6b"
    EQUALS = "#00d9ff"
    EQUALS_HOVER = "#5ce1e6"
    CLEAR = "#ff6b35"
    CLEAR_HOVER = "#ff8c5a"
    TEXT_LIGHT = "#ffffff"


class Calculator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("🧮 Modern Calculator")
        self.window.geometry("350x500")
        self.window.resizable(False, False)
        self.window.configure(bg=Colors.BACKGROUND)
        
        self.current_input = ""
        self.display_text = tk.StringVar()
        self.display_text.set("0")
        
        self._create_display()
        self._create_buttons()
        
    def _create_display(self):
        display_frame = tk.Frame(self.window, bg=Colors.DISPLAY_BG, pady=20)
        display_frame.pack(fill="x", padx=10, pady=(20, 10))
        
        display_label = tk.Label(
            display_frame,
            textvariable=self.display_text,
            font=("SF Pro Display", 40, "bold"),
            bg=Colors.DISPLAY_BG,
            fg=Colors.DISPLAY_TEXT,
            anchor="e",
            padx=20
        )
        display_label.pack(fill="both", expand=True)
        
    def _create_buttons(self):
        button_frame = tk.Frame(self.window, bg=Colors.BACKGROUND)
        button_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        button_layout = [
            [("C", Colors.CLEAR, Colors.CLEAR_HOVER),
             ("±", Colors.OPERATOR, Colors.OPERATOR_HOVER),
             ("%", Colors.OPERATOR, Colors.OPERATOR_HOVER),
             ("÷", Colors.OPERATOR, Colors.OPERATOR_HOVER)],
            [("7", Colors.NUMBER, Colors.NUMBER_HOVER),
             ("8", Colors.NUMBER, Colors.NUMBER_HOVER),
             ("9", Colors.NUMBER, Colors.NUMBER_HOVER),
             ("×", Colors.OPERATOR, Colors.OPERATOR_HOVER)],
            [("4", Colors.NUMBER, Colors.NUMBER_HOVER),
             ("5", Colors.NUMBER, Colors.NUMBER_HOVER),
             ("6", Colors.NUMBER, Colors.NUMBER_HOVER),
             ("−", Colors.OPERATOR, Colors.OPERATOR_HOVER)],
            [("1", Colors.NUMBER, Colors.NUMBER_HOVER),
             ("2", Colors.NUMBER, Colors.NUMBER_HOVER),
             ("3", Colors.NUMBER, Colors.NUMBER_HOVER),
             ("+", Colors.OPERATOR, Colors.OPERATOR_HOVER)],
            [("0", Colors.NUMBER, Colors.NUMBER_HOVER),
             (".", Colors.NUMBER, Colors.NUMBER_HOVER),
             ("⌫", Colors.CLEAR, Colors.CLEAR_HOVER),
             ("=", Colors.EQUALS, Colors.EQUALS_HOVER)],
        ]
        
        for i in range(5):
            button_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            button_frame.grid_columnconfigure(i, weight=1)
        
        for row_idx, row in enumerate(button_layout):
            for col_idx, (text, bg_color, hover_color) in enumerate(row):
                self._create_button(button_frame, text, bg_color, hover_color, row_idx, col_idx)
    
    def _create_button(self, parent, text, bg_color, hover_color, row, col):
        button = tk.Button(
            parent,
            text=text,
            font=("SF Pro Display", 22, "bold"),
            bg=bg_color,
            fg=Colors.TEXT_LIGHT,
            activebackground=hover_color,
            activeforeground=Colors.TEXT_LIGHT,
            border=0,
            cursor="hand2",
            command=lambda t=text: self._on_button_click(t)
        )
        
        button.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
        
        def on_enter(event):
            button.configure(bg=hover_color)
            
        def on_leave(event):
            button.configure(bg=bg_color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def _on_button_click(self, button_text):
        if button_text == "C":
            self._clear()
        elif button_text == "=":
            self._calculate()
        elif button_text == "⌫":
            self._backspace()
        elif button_text == "±":
            self._toggle_sign()
        elif button_text == "%":
            self._percentage()
        else:
            self._append_to_input(button_text)
    
    def _clear(self):
        self.current_input = ""
        self.display_text.set("0")
    
    def _backspace(self):
        self.current_input = self.current_input[:-1]
        if self.current_input == "":
            self.display_text.set("0")
        else:
            self.display_text.set(self.current_input)
    
    def _toggle_sign(self):
        if self.current_input and self.current_input != "0":
            if self.current_input.startswith("-"):
                self.current_input = self.current_input[1:]
            else:
                self.current_input = "-" + self.current_input
            self.display_text.set(self.current_input)
    
    def _percentage(self):
        try:
            expression = self._prepare_expression()
            if expression:
                result = eval(expression) / 100
                self.current_input = str(result)
                self.display_text.set(self._format_result(result))
        except:
            pass
    
    def _append_to_input(self, char):
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
    
    def _prepare_expression(self):
        expression = self.current_input
        expression = expression.replace("÷", "/")
        expression = expression.replace("×", "*")
        expression = expression.replace("−", "-")
        return expression
    
    def _calculate(self):
        try:
            expression = self._prepare_expression()
            if not expression:
                return
            
            result = eval(expression)
            formatted = self._format_result(result)
            self.current_input = str(result)
            self.display_text.set(formatted)
            
        except ZeroDivisionError:
            self.display_text.set("Error: ÷ by 0")
            self.current_input = ""
        except Exception:
            self.display_text.set("Error")
            self.current_input = ""
    
    def _format_result(self, result):
        if isinstance(result, float):
            if result == int(result):
                return str(int(result))
            else:
                return str(round(result, 8))
        return str(result)
    
    def run(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.window.mainloop()


if __name__ == "__main__":
    calculator = Calculator()
    calculator.run()
