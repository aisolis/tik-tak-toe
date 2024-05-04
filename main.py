import tkinter as tk
from tkinter import messagebox
import numpy as np
import random

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        
        self.current_player = 'X'  # 'X' es el jugador humano por defecto, 'O' será la IA
        self.game_count = 0
        self.x_wins = 0
        self.o_wins = 0
        self.draws = 0
        
        # Parámetros de Q-learning
        self.q_table = {}
        self.learning_rate = 0.5
        self.discount_factor = 0.95
        self.epsilon = 0.1  # Probabilidad de exploración

        self.initialize_scoreboard()
        self.initialize_game()

    def initialize_scoreboard(self):
        self.label_score = tk.Label(self.root, text=f"Juego: {self.game_count} - X ganadas: {self.x_wins} - O ganadas: {self.o_wins} - Empates: {self.draws}", font=('Helvetica', 14))
        self.label_score.grid(row=3, column=0, columnspan=3, sticky="ew")

    def initialize_game(self):
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                btn = tk.Button(self.root, text='', font=('Helvetica', 20), height=3, width=6,
                                command=lambda row=i, col=j: self.click_button(row, col))
                btn.grid(row=i, column=j)
                self.buttons[i][j] = btn
        if self.current_player == 'O':
            self.machine_move()

    def click_button(self, row, col):
        if self.current_player == 'X' and self.buttons[row][col]['text'] == "":
            self.player_move(row, col)
            if not self.check_game_over():
                self.machine_move()

    def player_move(self, row, col):
        self.buttons[row][col]['text'] = 'X'
        self.check_game_over()

    def machine_move(self):
        state = self.state_to_tuple()
        action_type = ""  # Para almacenar si el movimiento es de exploración o explotación

        if random.uniform(0, 1) < self.epsilon:  # Exploración
            empty_positions = [(i, j) for i in range(3) for j in range(3) if self.buttons[i][j]['text'] == ""]
            move = random.choice(empty_positions)
            action_type = "Exploración"
        else:  # Explotación
            q_values = self.q_table.get(state, np.zeros(9))
            idx = np.argmax(q_values)
            move = (idx // 3, idx % 3)
            while self.buttons[move[0]][move[1]]['text'] != "":
                q_values[idx] = -np.inf  # Evita seleccionar posiciones ya ocupadas
                idx = np.argmax(q_values)
                move = (idx // 3, idx % 3)
            action_type = "Explotación"

        self.buttons[move[0]][move[1]]['text'] = 'O'
        print(f"Acción de {action_type}: Posición {move}")  # Log en la consola
        self.check_game_over()


    def state_to_tuple(self):
        return tuple(tuple(btn['text'] for btn in row) for row in self.buttons)

    def check_winner(self):
        for n in range(3):
            if (self.buttons[n][0]['text'] == self.buttons[n][1]['text'] == self.buttons[n][2]['text'] != ""):
                return self.buttons[n][0]['text']
            if (self.buttons[0][n]['text'] == self.buttons[1][n]['text'] == self.buttons[2][n]['text'] != ""):
                return self.buttons[0][n]['text']
        if (self.buttons[0][0]['text'] == self.buttons[1][1]['text'] == self.buttons[2][2]['text'] != ""):
            return self.buttons[0][0]['text']
        if (self.buttons[2][0]['text'] == self.buttons[1][1]['text'] == self.buttons[0][2]['text'] != ""):
            return self.buttons[2][0]['text']
        return None

    def check_game_over(self):
        winner = self.check_winner()
        if winner:
            messagebox.showinfo("Game Over", f"{winner} wins!")
            if winner == 'X':
                self.x_wins += 1
            else:
                self.o_wins += 1
            self.game_count += 1
            self.initialize_game()
            self.update_scoreboard()
            return True
        elif all(self.buttons[i][j]['text'] != "" for i in range(3) for j in range(3)):
            self.draws += 1
            self.game_count += 1
            messagebox.showinfo("Game Over", "It's a draw!")
            self.initialize_game()
            self.update_scoreboard()
            return True
        return False

    def update_scoreboard(self):
        self.label_score.config(text=f"Juego: {self.game_count} - X ganadas: {self.x_wins} - O ganadas: {self.o_wins} - Empates: {self.draws}")

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
