import json
import random
import numpy as np
import os

class TicTacToeAI:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.9  # Probabilidad inicial de exploración
        self.min_epsilon = 0.01
        self.epsilon_decay = 0.995
        self.q_table = {}
        self.load_winning_combinations()
        self.initialize_q_table()

    def load_winning_combinations(self):
        try:
            with open(self.json_file_path, 'r') as file:
                self.winning_combinations = json.load(file)
        except FileNotFoundError:
            self.winning_combinations = []
            print("No winning combinations file found.")

    def initialize_q_table(self):
        """ Inicializa la Q-table considerando todos los posibles estados del tablero. """
        # Considera todas las combinaciones de 'X', 'O' y espacios en blanco en un tablero de 3x3
        from itertools import product
        states = product('XO ', repeat=9)  # Product cartesian de 'X', 'O', ' ' para cada posición del tablero 3x3
        for state in states:
            board = [state[i * 3:(i + 1) * 3] for i in range(3)]
            board_tuple = tuple(tuple(row) for row in board)
            self.q_table[board_tuple] = {}
            for move in self.possible_moves(board_tuple):
                self.q_table[board_tuple][move] = 0.0

    def possible_moves(self, state):
        """ Retorna una lista de movimientos posibles para el estado dado """
        return [(row, col) for row in range(3) for col in range(3) if state[row][col] == ' ']
    

    def select_move(self, state):
        state_tuple = tuple(tuple(row) for row in state)
        moves = self.possible_moves(state_tuple)

        # # Imprimir state_tuple
        # print("State Tuple:")
        # for row in state_tuple:
        #     print(row)

        # # Imprimir moves
        # print("\nPossible Moves:")
        # for move in moves:
        #     print(move)

        # print(self.q_table)
        if moves:
            print("hay movimientos")
            if random.random() < self.epsilon:
                print("random menor que epsilon")
                return random.choice(moves)
            else:
                possible_moves = self.q_table.get(state_tuple, {})
                print("random mayor que epsilon")
                if possible_moves:
                    return max(possible_moves, key=possible_moves.get)
        return None



    def update_q_table(self, old_state, action, reward, new_state):
        """ Actualiza la Q-table usando la fórmula de Q-learning """
        old_state_tuple = tuple(tuple(row) for row in old_state)
        new_state_tuple = tuple(tuple(row) for row in new_state)
        old_value = self.q_table.get(old_state_tuple, {}).get(action, 0.0)
        next_max = max(self.q_table.get(new_state_tuple, {}).values(), default=0)

        # Fórmula de actualización Q-learning
        new_value = old_value + self.learning_rate * (reward + self.discount_factor * next_max - old_value)
        if old_state_tuple not in self.q_table:
            self.q_table[old_state_tuple] = {}
        self.q_table[old_state_tuple][action] = new_value
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)  # Decaimiento de epsilon

    def assign_rewards(self):
        """ Asigna recompensas y penalizaciones basadas en la proximidad a victorias o derrotas. """
        for state_key in self.q_table:
            for move in self.q_table[state_key]:
                new_state = list(list(row) for row in state_key)
                new_state[move[0]][move[1]] = 'O'  # Suponiendo que 'O' es la IA
                if self.is_winning_state(new_state, 'O'):
                    self.q_table[state_key][move] += 1.0  # Recompensa por ganar
                elif self.is_winning_state(new_state, 'X'):
                    self.q_table[state_key][move] -= 1.0  # Penalización por permitir una victoria del oponente

    def is_winning_state(self, state, player):
        """ Comprueba si el estado dado es un estado ganador para el jugador especificado. """
        winning_positions = [
            [(0, 0), (0, 1), (0, 2)], [(1, 0), (1, 1), (1, 2)], [(2, 0), (2, 1), (2, 2)],
            [(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 1), (2, 1)], [(0, 2), (1, 2), (2, 2)],
            [(0, 0), (1, 1), (2, 2)], [(0, 2), (1, 1), (2, 0)]
        ]
        for positions in winning_positions:
            if all(state[row][col] == player for row, col in positions):
                return True
        return False

if __name__ == "__main__":
    ai = TicTacToeAI('winning_combinations.json')
    # Aquí iría el loop del juego o la simulación para entrenar la IA
