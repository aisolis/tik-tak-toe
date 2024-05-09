import tkinter as tk
from tkinter import messagebox
from avlNode import AVLNode, AVLTree
import numpy as np
import random


class TicTacToeApp:
    def __init__(self, root, avl_tree):
        self.root = root
        self.avl_tree = avl_tree  # Instancia del árbol AVL
        self.root.title("Juego de Totito")
        self.reset_game()
        self.create_widgets()

    def create_widgets(self):
        self.buttons = []
        for i in range(9):
            btn = tk.Button(self.root, text='', font=('Arial', 24), height=3, width=6,
                            command=lambda i=i: self.on_button_press(i))
            btn.grid(row=i//3, column=i%3)
            self.buttons.append(btn)
        
        self.reset_button = tk.Button(self.root, text='Reiniciar Juego', command=self.reset_game)
        self.reset_button.grid(row=3, column=0, columnspan=3)
        self.update_scores()

    def update_scores(self):
        score_text = f"Victorias (X): {self.score_x}  Victorias (O): {self.score_o}  Empates: {self.draws}"
        if hasattr(self, 'score_label'):
            self.score_label.config(text=score_text)
        else:
            self.score_label = tk.Label(self.root, text=score_text)
            self.score_label.grid(row=4, column=0, columnspan=3)

    def winner(self):
        # Definir todas las combinaciones posibles para ganar en un tablero 3x3
        lines = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # líneas horizontales
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # líneas verticales
            (0, 4, 8), (2, 4, 6)             # diagonales
        ]
        # Revisar cada combinación para ver si hay una línea ganadora
        for a, b, c in lines:
            if self.buttons[a]['text'] == self.buttons[b]['text'] == self.buttons[c]['text'] != '':
                return self.buttons[a]['text']
        # Si no hay ganador, devuelve None
        return None


    def update_score(self, winner):
        if winner == 'X':
            self.score_x += 1
        elif winner == 'O':
            self.score_o += 1

    def reset_game(self):
        self.turn = 'X'
        if hasattr(self, 'buttons'):
            for btn in self.buttons:
                btn.config(text='')
        self.score_x = getattr(self, 'score_x', 0)
        self.score_o = getattr(self, 'score_o', 0)
        self.draws = getattr(self, 'draws', 0)
        self.update_scores()

    def create_widgets(self):
        self.buttons = []
        for i in range(9):
            btn = tk.Button(self.root, text='', font=('Arial', 24), height=3, width=6,
                            command=lambda i=i: self.on_button_press(i))
            btn.grid(row=i//3, column=i%3)
            self.buttons.append(btn)
        
        self.reset_button = tk.Button(self.root, text='Reiniciar Juego', command=self.reset_game)
        self.reset_button.grid(row=3, column=0, columnspan=3)
        self.update_scores()

    def reset_game(self):
        self.turn = 'X'  # Iniciar siempre con el jugador humano
        self.avl_tree.root = None  # Reiniciar el árbol AVL
        if hasattr(self, 'buttons'):
            for btn in self.buttons:
                btn.config(text='')
        self.score_x = getattr(self, 'score_x', 0)
        self.score_o = getattr(self, 'score_o', 0)
        self.draws = getattr(self, 'draws', 0)
        self.update_scores()

    def on_button_press(self, index):
        if self.buttons[index]['text'] == '' and self.winner() is None:
            self.buttons[index]['text'] = self.turn
            current_state = self.get_board_state()

            # Actualizar el árbol AVL con el nuevo estado del juego
            # Nota: Deberías definir cómo calcular el valor Q para el nuevo estado aquí
            # Por simplicidad, se usa un valor Q dummy
            dummy_value_q = {i: 0 for i in range(9) if self.buttons[i]['text'] == ''}
            self.avl_tree.root = self.avl_tree.insert(self.avl_tree.root, current_state, dummy_value_q)

            # Verificar si hay un ganador
            winner = self.winner()
            if winner:
                self.update_score(winner)
                messagebox.showinfo("Juego Terminado", f"El ganador es {winner}!")
                self.reset_game()
            elif '' not in [btn['text'] for btn in self.buttons]:  # Comprobar si el tablero está lleno
                self.draws += 1
                messagebox.showinfo("Juego Terminado", "¡Es un empate!")
                self.reset_game()
            else:
                # Cambiar el turno
                self.turn = 'O' if self.turn == 'X' else 'X'
                self.update_scores()
                # Si es el turno de la máquina, realizar el movimiento
                if self.turn == 'O':
                    self.root.after(500, self.machine_move)

    def get_board_state(self):
        # Convertir el estado del tablero a una tupla para ser hashable
        return tuple(btn['text'] for btn in self.buttons)

    def update_q_values(self, state, action_index, reward, is_diagonal_move=False, blocked_opponent=False, gamma=0.9):
        # Search for the node with the current state in the AVL tree
        node = self.avl_tree.search(self.avl_tree.root, state)
        
        # If the node doesn't exist, create a new node with initial Q values
        if not node:
            new_q_values = {i: 0 for i in range(9) if self.buttons[i]['text'] == ''}
            node = AVLNode(state, new_q_values)
            self.avl_tree.root = self.avl_tree.insert(self.avl_tree.root, state, new_q_values)
            node.value_q[action_index] = reward  # Initialize with given reward
            
        # Calculate the reward adjusted for special moves
        adjusted_reward = reward
        if is_diagonal_move:
            adjusted_reward += 0.5
        if blocked_opponent:
            adjusted_reward += 0.3
        
        # Calculate the best future Q value from this state
        if node.value_q:
            future_q = max(node.value_q.values())
        else:
            future_q = 0
        
        # Update the Q value using the Q-learning formula
        updated_q = adjusted_reward + gamma * future_q
        
        # Update the Q value for the given action
        node.value_q[action_index] = updated_q


    def machine_move(self):
        current_state = self.get_board_state()
        empty_indices = [i for i, btn in enumerate(self.buttons) if btn['text'] == '']
        print("machine turn")
        if empty_indices:
            # Decidir entre explorar o explotar
            epsilon = 0.1  # Probabilidad de exploración
            if np.random.random() < epsilon:
                chosen_index = random.choice(empty_indices)  # Exploración: movimiento aleatorio
                print("machine exploration")
            else:
                # Verifica si necesita bloquear una jugada ganadora del humano
                chosen_index = self.block_opponent_win(current_state, empty_indices)
                if chosen_index is None:
                    # Si no hay jugada de bloqueo necesaria, explotar basado en Q-values
                    print("machine explore")
                    chosen_index = self.choose_best_move(current_state, empty_indices)

            # Ejecuta el movimiento seleccionado para la máquina
            self.execute_move(chosen_index, 'O')

            # Evaluar el resultado del movimiento después de que se ha ejecutado
            reward, is_diagonal, blocked_opponent = self.evaluate_move_result(chosen_index)

            # Actualizar los valores Q con la nueva información
            self.update_q_values(current_state, chosen_index, reward, is_diagonal, blocked_opponent)
            print("imprimiendo q values")
            # Verificar el estado del juego y cambiar el turno si es necesario
            if not self.winner() and '' in [btn['text'] for btn in self.buttons]:
                self.turn = 'X'  # Devolver el turno al jugador humano
                self.update_scores()
                print("devolviendo turno")
            print("fin")

    def block_opponent_win(self, state, empty_indices):
        opponent = 'X' if self.turn == 'O' else 'O'
        for index in empty_indices:
            self.buttons[index]['text'] = opponent  # Simula el movimiento del oponente
            if self.winner() == opponent:
                print("machine detect a losse probably")
                self.buttons[index]['text'] = ''  # Limpia la simulación
                return index  # Devuelve este índice para bloquear la jugada ganadora
            self.buttons[index]['text'] = ''  # Limpia la simulación
        return None


    def evaluate_diagonal(self, state, index):
        # Esta función debería evaluar si el movimiento es diagonal y si bloquea al oponente
        # Implementación específica dependiendo de cómo defines un movimiento diagonal y bloqueo
        is_diagonal = index in [0, 2, 4, 6, 8]  # Índices de las posiciones diagonales en un tablero 3x3
        blocked_opponent = False  # Evaluar si este movimiento bloquea al oponente
        return is_diagonal, blocked_opponent

    def choose_best_move(self, state, possible_moves):
        node = self.avl_tree.search(self.avl_tree.root, state)
        if node and node.value_q:
            # Incorporar una pequeña probabilidad de elegir un movimiento aleatorio incluso durante la explotación
            if np.random.random() < 0.05:  # 5% de probabilidad de movimiento aleatorio
                return random.choice(possible_moves)

            # Elegir el índice con el máximo valor Q entre los posibles movimientos
            max_q_value = max(node.value_q.get(index, 0) for index in possible_moves)
            best_moves = [index for index in possible_moves if node.value_q.get(index, 0) == max_q_value]
            print("machine choose a best movement")
            return random.choice(best_moves)  # Para evitar sesgos si hay múltiples mejores movimientos
        return random.choice(possible_moves)


    def evaluate_move_result(self, index):
        # Establece recompensas base
        reward = 0
        is_diagonal = False
        blocked_opponent = False

        # Verifica si el movimiento es diagonal
        is_diagonal = index in [0, 2, 4, 6, 8]

        # Guarda el estado original del botón para restaurarlo después de la evaluación
        original_text = self.buttons[index]['text']

        # Actualiza el tablero temporalmente para la evaluación
        self.buttons[index]['text'] = self.turn
        winner = self.winner()

        if winner:
            # Si el jugador actual gana con este movimiento
            reward = 1 if winner == self.turn else -1
        else:
            # Evaluar si el movimiento bloquea al oponente
            opponent = 'X' if self.turn == 'O' else 'O'
            for a, b, c in [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                            (0, 3, 6), (1, 4, 7), (2, 5, 8),
                            (0, 4, 8), (2, 4, 6)]:
                if {self.buttons[a]['text'], self.buttons[b]['text'], self.buttons[c]['text']} == {opponent, self.turn, ''}:
                    blocked_opponent = True
                    reward += 0.3  # Agrega una recompensa pequeña por bloquear una jugada ganadora

        # Restaura el estado original del tablero
        self.buttons[index]['text'] = original_text

        return reward, is_diagonal, blocked_opponent

    def execute_move(self, index, player):
        if self.buttons[index]['text'] == '' and self.winner() is None:
            self.buttons[index]['text'] = player
            # Forzar actualización inmediata de la GUI
            winner = self.winner()
            if winner:
                self.update_score(winner)
                messagebox.showinfo("Juego Terminado", f"El ganador es {winner}!")
                self.reset_game()
            elif '' not in [btn['text'] for btn in self.buttons]:  # Comprobar si el tablero está lleno
                self.draws += 1
                messagebox.showinfo("Juego Terminado", "¡Es un empate!")
                self.reset_game()
            else:
                # Cambia el turno al jugador humano
                self.turn = 'X'
                self.update_scores()
                # self.x


if __name__ == "__main__":
    root = tk.Tk()
    avl_tree = AVLTree()  # Asegúrate de que AVLTree esté correctamente definido
    app = TicTacToeApp(root, avl_tree)
    root.mainloop()
