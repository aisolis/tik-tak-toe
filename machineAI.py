import tkinter as tk
from tkinter import messagebox, Toplevel, ttk
from avlNode import AVLNode
import numpy as np
import random

from utilities import GameUtilities

class MachineIa:

    def __init__(self, boardContext):
        self.boardContext = boardContext
        self.avl_tree = boardContext.avl_tree
        self.gameUtilities = GameUtilities(boardContext)

    def machine_move(self, pvpMode=False):
        print("machine turn")
        empty_indices = [i for i, btn in enumerate(self.boardContext.buttons) if btn['text'] == '']
        if empty_indices:
            current_state = self.boardContext.get_board_state()
            chosen_index = self.block_opponent_win(empty_indices, current_state)
            # Ejecuta el movimiento seleccionado para la máquina
            self.execute_move(chosen_index, 'O', pvpMode)
            # Evaluar el resultado del movimiento después de que se ha ejecutado
            reward, is_diagonal, blocked_opponent = self.evaluate_move_result(chosen_index)
            # Actualizar los valores Q con la nueva información
            self.update_q_values(current_state, chosen_index, reward, is_diagonal, blocked_opponent)
            print("imprimiendo q values")
            # Verificar el estado del juego y cambiar el turno si es necesario
            if not self.boardContext.winner() and '' in [btn['text'] for btn in self.boardContext.buttons]:
                self.boardContext.turn = 'X'  # Devolver el turno al jugador humano
                self.boardContext.update_scores()
                print("devolviendo turno")
            print("fin")



    def execute_move(self, index, player, pvpMode=True):
        if self.boardContext.buttons[index]['text'] == '' and self.boardContext.winner() is None:
            self.boardContext.buttons[index]['text'] = player
            self.boardContext.root.update_idletasks()  # Forzar actualización inmediata de la GUI

            # Evaluar el resultado del movimiento después de que se ha ejecutado
            reward, is_diagonal, blocked_opponent = self.evaluate_move_result(index)

            # Actualizar los valores Q con la nueva información
            current_state = self.boardContext.get_board_state()  # Obtener estado actual después del movimiento
            self.update_q_values(current_state, index, reward, is_diagonal, blocked_opponent)

            winner = self.boardContext.winner()
            if winner or all(btn['text'] != '' for btn in self.boardContext.buttons):
                if pvpMode:
                    self.boardContext.update_score(winner) if winner else None
                    messagebox.showinfo("Juego Terminado", f"El ganador es {winner}!") if winner else None
                    self.gameUtilities.save_screenshot() if winner else None
                self.boardContext.reset_game()
                return  # Detener la ejecución si el juego ha terminado
            elif '' not in [btn['text'] for btn in self.boardContext.buttons]:  # Comprobar si el tablero está lleno
                if pvpMode:
                    self.boardContext.draws += 1
                    messagebox.showinfo("Juego Terminado", "¡Es un empate!")
                    self.gameUtilities.save_screenshot()
                self.boardContext.reset_game()
            else:
                # Cambia el turno al jugador humano si es PvP
                if pvpMode:
                    self.boardContext.turn = 'X'
                    self.boardContext.update_scores()

    def update_q_values(self, state, action_index, reward, is_diagonal_move=False, blocked_opponent=False, gamma=0.9):
        # Busca el nodo con el estado actual del tablero
        node = self.avl_tree.search(self.avl_tree.root, state)
        
        # Si no existe un nodo, entonces crea uno nuevo y lo inicializa con valores Q
        if not node:
            new_q_values = {i: 0 for i in range(9) if self.boardContext.buttons[i]['text'] == ''}
            node = AVLNode(state, new_q_values)
            self.avl_tree.root = self.avl_tree.insert(self.avl_tree.root, state, new_q_values)
            node.value_q[action_index] = reward  # Se brinda una recompensa inicial
            
        # Calcula la recompensa, premiando si son movimientos dificiles de bloquear
        adjusted_reward = reward
        if is_diagonal_move:
            adjusted_reward += 0.5
        if blocked_opponent:
            adjusted_reward += 0.3
        
        # Calcula el mejor valor Q futuro para este estado
        if node.value_q:
            future_q = max(node.value_q.values())
        else:
            future_q = 0
        
        # Actualiza el valor q, usando la formula de recompensas para valores Q
        updated_q = adjusted_reward + gamma * future_q
        print(updated_q)
        # Actualiza el valor del nodo en base al valor q actualizado
        node.value_q[action_index] = updated_q


    def block_opponent_win(self, empty_indices, current_state):
        current_player = self.boardContext.turn
        opponent = 'X' if current_player == 'O' else 'O'

        # Primero, intenta ganar
        for index in empty_indices:
            self.boardContext.buttons[index]['text'] = current_player  # Simula el movimiento del jugador actual
            if self.boardContext.winner() == current_player:
                self.boardContext.buttons[index]['text'] = ''  # Limpia la simulación
                print("Machine detect a winning move")
                return index  # Devuelve este índice para hacer la jugada ganadora
            self.boardContext.buttons[index]['text'] = ''  # Limpia la simulación

        # Si no puede ganar, intenta bloquear al oponente
        for index in empty_indices:
            self.boardContext.buttons[index]['text'] = opponent  # Simula el movimiento del oponente
            if self.boardContext.winner() == opponent:
                print("Machine detect a loss possibility")
                self.boardContext.buttons[index]['text'] = ''  # Limpia la simulación
                return index  # Devuelve este índice para bloquear la jugada ganadora
            self.boardContext.buttons[index]['text'] = ''  # Limpia la simulación

        epsilon = 0.1  # Probabilidad de exploración
        if np.random.random() < epsilon:
            print("machine exploration")
            return random.choice(empty_indices)  # Exploración: movimiento aleatorio
        else:
            # Si no hay jugada de bloqueo necesaria, explotar basado en Q-values
            print("machine explote")
            return self.choose_best_move(current_state, empty_indices)
        



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
        original_text = self.boardContext.buttons[index]['text']

        # Actualiza el tablero temporalmente para la evaluación
        self.boardContext.buttons[index]['text'] = self.boardContext.turn
        winner = self.boardContext.winner()

        if winner:
            # Si el jugador actual gana con este movimiento
            reward = 1 if winner == self.boardContext.turn else -1
        else:
            # Evaluar si el movimiento bloquea al oponente
            opponent = 'X' if self.boardContext.turn == 'O' else 'O'
            for a, b, c in [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                            (0, 3, 6), (1, 4, 7), (2, 5, 8),
                            (0, 4, 8), (2, 4, 6)]:
                if {self.boardContext.buttons[a]['text'], self.boardContext.buttons[b]['text'], self.boardContext.buttons[c]['text']} == {opponent, self.boardContext.turn, ''}:
                    blocked_opponent = True
                    reward += 0.3  # Agrega una recompensa pequeña por bloquear una jugada ganadora

        # Restaura el estado original del tablero
        self.boardContext.buttons[index]['text'] = original_text

        return reward, is_diagonal, blocked_opponent
    

    def train_model(self, N=100):
        self.boardContext.reset_game(False)
        training_window = Toplevel()
        training_window.title("Training in Progress")
        ttk.Label(training_window, text="Training... Please wait").pack(padx=10, pady=10)

        progress = ttk.Progressbar(training_window, orient="horizontal", length=200, mode='determinate')
        progress.pack(padx=10, pady=10)
        training_window.pack_slaves()

        def update_progress_bar(current, total):
            progress['value'] = (current / total) * 100
            self.boardContext.root.update_idletasks()

        def train():
            use_x = True
            best_q_value_before = self.get_best_q_value()  # Obtiene el mejor valor Q antes del entrenamiento
            for i in range(N):
                self.boardContext.root.after(500, self.simulate_game(use_x))                
                use_x = not use_x
                update_progress_bar(i + 1, N)
            training_window.destroy()

            best_q_value_after = self.get_best_q_value()  # Obtiene el mejor valor Q después del entrenamiento
            improvement = best_q_value_after - best_q_value_before
            messagebox.showinfo("Entrenamiento Completo", f"Entrenamiento completado. Mejora del valor Q: {improvement:.2f}")

        tk.Button(training_window, text="Cancel", command=training_window.destroy).pack(padx=10, pady=10)

        self.boardContext.root.after(100, train)

    def simulate_game(self, use_x):
        self.boardContext.reset_game(silent=True)  # Asegurarse de no reiniciar el árbol AVL
        self.boardContext.turn = 'X' if use_x else 'O'
        move_count = 0  # Contador para verificar cantidad de movimientos y prevenir bucle infinito

        while move_count < 9:  # Hay un máximo de 9 movimientos en un tablero 3x3
            current_state = self.boardContext.get_board_state()
            empty_indices = [i for i, btn in enumerate(self.boardContext.buttons) if btn['text'] == '']
            if not empty_indices:
                break  # Salir si no hay casillas vacías

            move_index = self.choose_best_move(current_state, empty_indices)
            self.execute_move(move_index, self.boardContext.turn, False)

            winner = self.boardContext.winner()
            if winner or '' not in [btn['text'] for btn in self.boardContext.buttons]:
                break  # Salir si hay un ganador o no quedan movimientos

            self.boardContext.turn = 'O' if self.boardContext.turn == 'X' else 'X'  # Alternar turno
            move_count += 1

        self.boardContext.reset_game(silent=True)  # Reiniciar el juego de forma silenciosa para la siguiente simulación


    def get_best_q_value(self):
        
        all_values = [node.value_q for node in self.avl_tree.get_all_nodes() if node.value_q]
        if not all_values:  # Comprobar si la lista está vacía
            return 0  # O el valor por defecto que consideres apropiado
        return max(max(values.values()) for values in all_values if values)