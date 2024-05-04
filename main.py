import tkinter as tk
from tkinter import messagebox

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        
        self.current_player = 'X'
        self.game_count = 0
        self.x_wins = 0
        self.o_wins = 0
        self.draws = 0

        self.initialize_scoreboard()  # Inicializa el marcador antes del juego
        self.initialize_game()

    def initialize_scoreboard(self):
        # Configuración inicial del marcador
        self.label_score = tk.Label(self.root, text=f"Juego: {self.game_count} - X ganadas: {self.x_wins} - O ganadas: {self.o_wins} - Empates: {self.draws}", font=('Helvetica', 14))
        self.label_score.grid(row=3, column=0, columnspan=3, sticky="ew")

    def initialize_game(self):
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                if self.buttons[i][j] is not None:
                    self.buttons[i][j].destroy()
                btn = tk.Button(self.root, text='', font=('Helvetica', 20), height=3, width=6,
                                command=lambda row=i, col=j: self.click_button(row, col))
                btn.grid(row=i, column=j)
                self.buttons[i][j] = btn

    def click_button(self, row, col):
        button = self.buttons[row][col]
        if button['text'] == "" and self.current_player:
            button['text'] = self.current_player
            if self.check_winner():
                if self.current_player == 'X':
                    self.x_wins += 1
                else:
                    self.o_wins += 1
                messagebox.showinfo("Game Over", f"Player {self.current_player} wins!")
                self.game_count += 1
                self.initialize_game()
                self.update_scoreboard()
            elif all(self.buttons[i][j]['text'] != "" for i in range(3) for j in range(3)):
                self.draws += 1
                messagebox.showinfo("Game Over", "It's a draw!")
                self.game_count += 1
                self.initialize_game()
                self.update_scoreboard()
            else:
                self.current_player = 'X' if self.current_player == 'O' else 'O'

    def check_winner(self):
        for n in range(3):
            if (self.buttons[n][0]['text'] == self.buttons[n][1]['text'] == self.buttons[n][2]['text'] != "") or \
               (self.buttons[0][n]['text'] == self.buttons[1][n]['text'] == self.buttons[2][n]['text'] != ""):
                return True
        if (self.buttons[0][0]['text'] == self.buttons[1][1]['text'] == self.buttons[2][2]['text'] != "") or \
           (self.buttons[0][2]['text'] == self.buttons[1][1]['text'] == self.buttons[2][0]['text'] != ""):
            return True
        return False

    def update_scoreboard(self):
        # Actualiza el marcador después de cada juego
        self.label_score.config(text=f"Juego: {self.game_count} - X ganadas: {self.x_wins} - O ganadas: {self.o_wins} - Empates: {self.draws}")

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
