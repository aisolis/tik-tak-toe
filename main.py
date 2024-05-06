import tkinter as tk
from tkinter import messagebox, Menu, Toplevel, Label, simpledialog
from PIL import ImageGrab
import os

class TicTacToe:
    def __init__(self, master):
        self.master = master
        self.master.title("Tic-Tac-Toe")
        self.players = {'X': 'Jugador 1', 'O': 'Computadora'}
        self.current_player = "X"
        self.is_vs_computer = False
        self.board = [[None, None, None] for _ in range(3)]
        self.scores = {'X': 0, 'O': 0, 'Ties': 0}
        self.movements = []
        self.move_count = 0
        self.create_widgets()
        self.create_menu()
        self.history_folder = "history"
        if not os.path.exists(self.history_folder):
            os.makedirs(self.history_folder)
        self.set_player_names()

    def create_widgets(self):
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.buttons[i][j] = tk.Button(self.master, text='', font=('Arial', 24), width=5, height=2,
                                               command=lambda row=i, col=j: self.on_button_press(row, col))
                self.buttons[i][j].grid(row=i, column=j)

        self.score_label = tk.Label(self.master, text=self.get_score_text(), font=('Arial', 14))
        self.score_label.grid(row=0, column=3, rowspan=3, sticky='n')

        self.game_mode_label = tk.Label(self.master, text='', font=('Arial', 16), fg='blue')
        self.game_mode_label.grid(row=3, column=0, columnspan=3, sticky='n')

        self.reset_button = tk.Button(self.master, text="Reiniciar", command=self.reset_game)
        self.reset_button.grid(row=4, column=0, columnspan=4, sticky='we')

    def create_menu(self):
        menu = Menu(self.master)
        self.master.config(menu=menu)

        game_menu = Menu(menu, tearoff=0)
        menu.add_cascade(label="Juego", menu=game_menu)
        game_menu.add_command(label="Jugar", command=self.reset_game)
        game_menu.add_command(label="Jugar contra Computadora", command=self.play_vs_computer)
        game_menu.add_command(label="Ver Historia", command=self.show_history)
        game_menu.add_command(label="Configurar Jugadores", command=self.configure_players)

    def play_vs_computer(self):
        self.is_vs_computer = True
        self.players['O'] = "Computadora"
        self.reset_game()
        self.update_game_mode_label()

    def set_player_names(self):
        self.players['X'] = simpledialog.askstring("Nombre del Jugador", "Ingresa tu nombre (Jugador X):", parent=self.master) or "Jugador 1"
        self.players['O'] = simpledialog.askstring("Nombre del Jugador", "Ingresa tu nombre (Jugador O):", parent=self.master) or "Jugador 2"
        self.score_label.config(text=self.get_score_text())
        self.is_vs_computer = False
        self.update_game_mode_label()

    def configure_players(self):
        if not self.is_vs_computer:
            for key in self.players:
                self.players[key] = simpledialog.askstring("Nombre del Jugador", f"Nombre para {key}:", parent=self.master)
        else:
            self.players['X'] = simpledialog.askstring("Nombre del Jugador", "Nombre para Jugador 1:", parent=self.master)
        self.score_label.config(text=self.get_score_text())  # Update score label
        self.update_game_mode_label()

    def update_game_mode_label(self):
        mode_text = "Modo: Jugador vs. Computadora" if self.is_vs_computer else "Modo: Jugador vs. Jugador"
        self.game_mode_label.config(text=mode_text)

    def get_score_text(self):
        return f"{self.players['X']}: {self.scores['X']}\n{self.players['O']}: {self.scores['O']}\nEmpates: {self.scores['Ties']}"

    def on_button_press(self, row, col):
        if self.buttons[row][col]['text'] == '' and self.current_player:
            self.buttons[row][col]['text'] = self.current_player
            self.record_move(row, col)  # Record the move
            if self.check_winner(self.current_player):
                messagebox.showinfo("Fin del Juego", f"{self.players[self.current_player]} ha ganado!")
                self.capture_screen()
                self.scores[self.current_player] += 1
                self.print_movements()  # Print all movements
                self.reset_board()
            elif self.is_board_full():
                messagebox.showinfo("Fin del Juego", "Es un empate!")
                self.capture_screen()
                self.scores['Ties'] += 1
                self.print_movements()  # Print all movements
                self.reset_board()
            else:
                self.current_player = "O" if self.current_player == "X" else "X"
            self.score_label.config(text=self.get_score_text())

    def record_move(self, row, col):
        self.move_count += 1
        move_description = f"Movimiento {self.move_count} - Jugador {self.current_player}: [{row}][{col}]"
        self.movements.append(move_description)

    def print_movements(self):
        for move in self.movements:
            print(move)
        self.movements = []  # Clear movements after printing
        self.move_count = 0  # Reset move count

    def check_winner(self, player):
        for i in range(3):
            if all(self.buttons[i][j]['text'] == player for j in range(3)) or \
               all(self.buttons[j][i]['text'] == player for j in range(3)):
                return True
        if self.buttons[0][0]['text'] == self.buttons[1][1]['text'] == self.buttons[2][2]['text'] == player or \
           self.buttons[0][2]['text'] == self.buttons[1][1]['text'] == self.buttons[2][0]['text'] == player:
            return True
        return False

    def is_board_full(self):
        return all(self.buttons[i][j]['text'] != '' for i in range(3) for j in range(3))

    def reset_board(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text='')
        self.current_player = "X"

    def reset_game(self):
        self.reset_board()
        self.scores = {'X': 0, 'O': 0, 'Ties': 0}
        self.score_label.config(text=self.get_score_text())
        self.update_game_mode_label()

    def capture_screen(self):
        x = self.master.winfo_rootx() + self.buttons[0][0].winfo_x()
        y = self.master.winfo_rooty() + self.buttons[0][0].winfo_y()
        x1 = x + 3*self.buttons[0][0].winfo_width()
        y1 = y + 3*self.buttons[0][0].winfo_height()
        ImageGrab.grab().crop((x, y, x1, y1)).save(os.path.join(self.history_folder, f'history_{len(os.listdir(self.history_folder))+1}.png'))

    def show_history(self):
        top = Toplevel(self.master)
        top.title("Historia de Partidas")
        scroll = tk.Scrollbar(top)
        scroll.pack(side="right", fill="y")
        canvas = tk.Canvas(top, yscrollcommand=scroll.set)
        scroll.config(command=canvas.yview)
        frame = tk.Frame(canvas)
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0,0), window=frame, anchor='nw')

        for file_name in os.listdir(self.history_folder):
            path = os.path.join(self.history_folder, file_name)
            img = tk.PhotoImage(file=path)
            label = Label(frame, image=img)
            label.image = img  # keep a reference!
            label.pack()

        frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
