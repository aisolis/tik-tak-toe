import json
import random
from graphviz import Digraph
from itertools import product
import os

class TicTacToeAI:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.9  # Inicial exploración
        self.min_epsilon = 0.01
        self.epsilon_decay = 0.995
        self.q_table = {}
        self.load_winning_combinations()
        self.initialize_q_table()
        self.q_table_history = []  # Para guardar el estado de la Q-table periódicamente
        self.winning_combinations_buffer = []


    def load_winning_combinations(self):
        """Carga o inicializa y crea un archivo de combinaciones ganadoras si no existe."""
        try:
            # Intentar abrir el archivo existente para leer las combinaciones ganadoras
            with open(self.json_file_path, 'r') as file:
                self.winning_combinations = json.load(file)
        except FileNotFoundError:
            # Si el archivo no existe, crear uno nuevo con una lista vacía
            self.winning_combinations = []
            with open(self.json_file_path, 'w') as file:
                json.dump(self.winning_combinations, file)
            print("No winning combinations file found. A new file has been created.")



    def initialize_q_table(self):
        """ Inicializa la Q-table considerando todos los posibles estados del tablero. """
        states = product('XO ', repeat=9)  # Producto cartesiano de 'X', 'O', ' ' para cada posición del tablero 3x3
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
        if moves:
            if random.random() < self.epsilon:
                return random.choice(moves)
            else:
                possible_moves = self.q_table.get(state_tuple, {})
                if possible_moves:
                    return max(possible_moves, key=possible_moves.get)
        return None

    def update_q_table(self, old_state, action, reward, new_state):
        """ Actualiza la Q-table usando la fórmula de Q-learning """
        old_state_tuple = tuple(tuple(row) for row in old_state)
        new_state_tuple = tuple(tuple(row) for row in new_state)
        old_value = self.q_table.get(old_state_tuple, {}).get(action, 0.0)
        next_max = max(self.q_table.get(new_state_tuple, {}).values(), default=0)
        new_value = old_value + self.learning_rate * (reward + self.discount_factor * next_max - old_value)
        if old_state_tuple not in self.q_table:
            self.q_table[old_state_tuple] = {}
        self.q_table[old_state_tuple][action] = new_value
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

        # Registrar cambio en Q-table para análisis
        self.q_table_history.append((old_state_tuple, action, new_value))

        # Asegúrate de actualizar epsilon también si es parte del proceso
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    # def save_q_table_history(self):
    #     with open("q_table_history.json", "w") as file:
    #         json.dump(self.q_table_history, file, indent=4)
    def save_q_table_history(self, file_path="q_table_history.json"):
        with open(file_path, "w") as file:
            json.dump(self.q_table_history, file, indent=4)

    def is_winning_state(self, state, player):
        """ Comprueba si el estado dado es un estado ganador para el jugador especificado. """
        winning_positions = [
            [(0, 0), (0, 1), (0, 2)], [(1, 0), (1, 1), (1, 2)], [(2, 0), (2, 1), (2, 2)],
            [(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 1), (2, 1)], [(0, 2), (1, 2), (2, 2)],
            [(0, 0), (1, 1), (2, 2)], [(0, 2), (1, 1), (2, 0)]
        ]
        return any(all(state[row][col] == player for row, col in positions) for positions in winning_positions)
    
    def create_q_table_graph(self, q_table_history, folder_name='graphvizTrainingModel', filename='q_table_history'):
        """
        Crea un gráfico de la evolución de la Q-Table usando Graphviz y lo guarda en un archivo.

        Args:
        q_table_history (list): Historial de actualizaciones de la Q-table.
        folder_name (str): Nombre de la carpeta donde se guardará el archivo.
        filename (str): Nombre base del archivo a guardar.
        """
        # Asegurar que la carpeta exista
        os.makedirs(folder_name, exist_ok=True)
        file_path = os.path.join(folder_name, filename)

        # Crear el gráfico
        dot = Digraph(comment='Evolución de la Q-Table')

        # Añadir nodos y arcos
        for index, (state, action, q_value) in enumerate(q_table_history):
            # Formatear el estado y la acción para el etiquetado del nodo
            state_label = self.format_state(state)
            action_label = f'Action: {action}, Q-value: {q_value:.2f}'
            node_label = f'{state_label}\n{action_label}'
            dot.node(str(index), label=node_label)

            # Conectar este nodo con el anterior
            if index > 0:
                dot.edge(str(index - 1), str(index))

        # Renderizar y guardar el gráfico
        dot.render(f'{file_path}.gv', view=True)

    def format_state(self, state):
        """ Formatea el estado de la Q-table para ser usado como etiqueta en el gráfico. """
        return '\n'.join(''.join(row) for row in state)


    def train(self, num_games):
        for _ in range(num_games):
            self.play_self_game()

    def play_self_game(self):
        state = tuple(tuple(' ' for _ in range(3)) for _ in range(3))  # Estado inicial del tablero
        player = 'X'  # Comienza el jugador 'X'
        
        game_over = False
        move_history = []
        
        while not game_over:
            move = self.select_move(state)
            if move is None:
                break  # No hay movimientos posibles, empate
            
            # Aplicar movimiento
            new_state = self.apply_move(state, move, player)
            move_history.append((state, move, player))
            
            # Verificar si hay ganador
            if self.is_winning_state(new_state, player):
                # Terminar el juego y aplicar recompensas
                game_over = True
                self.apply_rewards(move_history, player)
                # Extraer las coordenadas de los movimientos ganadores
                winning_coords = [(move[1][0], move[1][1]) for move in move_history if move[2] == player]
                # Guardar la combinación ganadora si es que hay ganador
                self.save_winning_combination(winning_coords)
            elif all(new_state[row][col] != ' ' for row in range(3) for col in range(3)):
                # Tablero lleno, es un empate
                game_over = True
                self.apply_rewards(move_history, None)
            
            # Alternar jugador
            player = 'O' if player == 'X' else 'X'
            state = new_state

    # def save_winning_combination(self, move_history, winner, winning_state):
    #     """Guarda la combinación ganadora en el archivo JSON."""
    #     if winner:
    #         # Extraer los movimientos ganadores del histórico
    #         winning_moves = [(state, move) for state, move, player in move_history if player == winner]
    #         winning_positions = [move for _, move in winning_moves]

    #         try:
    #             # Cargar el archivo JSON de combinaciones ganadoras si existe
    #             if os.path.exists(self.json_file_path):
    #                 with open(self.json_file_path, 'r') as file:
    #                     data = json.load(file)
    #             else:
    #                 data = []

    #             # Agregar la nueva combinación ganadora
    #             data.append({"winner": winner, "winning_positions": winning_positions})

    #             # Guardar el archivo JSON actualizado
    #             with open(self.json_file_path, 'w') as file:
    #                 json.dump(data, file, indent=4)

    #         except Exception as e:
    #             print(f"Error al guardar la combinación ganadora: {e}")

    def save_winning_combination(self, winning_coords):
        """Guarda la combinación ganadora en el archivo JSON en el formato específico."""
        try:
            # Verificar si el archivo existe y cargar los datos, de lo contrario inicializa un arreglo vacío
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, 'r') as file:
                    data = json.load(file)
            else:
                data = []

            # Calcula el nuevo ID como el siguiente en la secuencia
            new_id = len(data) + 1

            # Formatear la combinación ganadora como una lista de diccionarios con 'row' y 'col'
            win_combination = [{"row": coord[0], "col": coord[1]} for coord in winning_coords]

            # Agrega la nueva combinación ganadora al arreglo de datos
            data.append({"id": new_id, "winCombination": win_combination})

            # Escribe los datos actualizados de vuelta al archivo JSON
            with open(self.json_file_path, 'w') as file:
                json.dump(data, file, indent=4)

        except Exception as e:
            print(f"Error saving to JSON: {e}")


    def flush_winning_combinations(self):
        """Escribe el buffer de combinaciones ganadoras al archivo JSON."""
        try:
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, 'r') as file:
                    data = json.load(file)
            else:
                data = []
            data.extend(self.winning_combinations_buffer)
            with open(self.json_file_path, 'w') as file:
                json.dump(data, file, indent=4)
            self.winning_combinations_buffer = []
        except Exception as e:
            print(f"Error al guardar las combinaciones ganadoras: {e}")

    def apply_move(self, state, move, player):
        """Aplica el movimiento al estado actual del tablero y retorna el nuevo estado."""
        state_list = [list(row) for row in state]
        state_list[move[0]][move[1]] = player
        return tuple(tuple(row) for row in state_list)

    def apply_rewards(self, move_history, winner):
        """Aplica las recompensas o penalizaciones dependiendo del resultado del juego, con énfasis en las jugadas diagonales."""
        reverse = True if winner is None else False
        # Aplicar reverse basado en la condición de empate o victoria
        if reverse:
            move_history = reversed(move_history)
        else:
            move_history = move_history  # Si no es empate, se usa el orden normal

        for state, move, player in move_history:
            # Comprobar si el movimiento es parte de una diagonal ganadora
            if self.is_diagonal_move(move):
                print("se recompenso una jugada diagonal")
                diagonal_bonus = 2.0  # Incrementar la recompensa para movimientos diagonales
            else:
                print("jugada normal")
                diagonal_bonus = 1.0  # Sin bonificación para movimientos no diagonales
            
            if winner:
                # Aplicar bonificación diagonal solo si el movimiento contribuyó a la victoria
                reward = diagonal_bonus if player == winner else -1 * diagonal_bonus
            else:
                print("es un empate")
                reward = 0  # Empate, recompensa neutral

            action = move
            new_state = self.apply_move(state, action, player)
            self.update_q_table(state, action, reward, new_state)

    def is_diagonal_move(self, move):
        """Determina si un movimiento es parte de una diagonal en un tablero de Tic-Tac-Toe 3x3."""
        diagonal_moves = {(0, 0), (0, 2), (2, 0), (2, 2), (1, 1)}
        return move in diagonal_moves


if __name__ == "__main__":
    ai = TicTacToeAI('winning_combinations.json')
    # Aquí iría el loop del juego o la simulación para entrenar la IA
