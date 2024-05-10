import tkinter as tk
from tkinter import messagebox, Toplevel, Menu, Label, Button, ttk, simpledialog
from PIL import Image, ImageTk, ImageGrab
from avlNode import AVLNode, AVLTree
import numpy as np
import random
import os
import datetime


class TicTacToeApp:
    def __init__(self, root, avl_tree):
        self.root = root
        self.avl_tree = avl_tree  # Instancia del árbol AVL
        self.root.title("Juego de Totito")
        self.reset_game()
        self.create_widgets()
        self.create_menu()

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

    def reset_game(self, silent=False):
        self.turn = 'X'  # Iniciar siempre con el jugador humano
        if not silent:
            # Reset the AVL tree only if it's a full reset, not during training
            self.avl_tree.root = None
        if hasattr(self, 'buttons'):
            for btn in self.buttons:
                btn.config(text='')
        if not silent:
            self.score_x = getattr(self, 'score_x', 0)
            self.score_o = getattr(self, 'score_o', 0)
            self.draws = getattr(self, 'draws', 0)
            self.update_scores()


    def on_button_press(self, index, pvpMode=True):
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
                self.update_score(winner) if pvpMode else None
                messagebox.showinfo("Juego Terminado", f"El ganador es {winner}!") if pvpMode else None
                self.save_screenshot() 
                self.reset_game()
            elif '' not in [btn['text'] for btn in self.buttons]:  # Comprobar si el tablero está lleno
                self.draws += 1 if pvpMode else None
                messagebox.showinfo("Juego Terminado", "¡Es un empate!") if pvpMode else None
                self.save_screenshot() 
                self.reset_game()
            else:
                # Cambiar el turno
                self.turn = 'O' if self.turn == 'X' else 'X'
                self.update_scores() if pvpMode else None
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
            self.execute_move(chosen_index, 'O', False)

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

    def execute_move(self, index, player, pvpMode=True):
        if self.buttons[index]['text'] == '' and self.winner() is None:
            self.buttons[index]['text'] = player
            # Forzar actualización inmediata de la GUI
            winner = self.winner()
            if winner or all(btn['text'] != '' for btn in self.buttons):
                # self.update_score(winner)
                self.update_score(winner) if winner and pvpMode else None
                messagebox.showinfo("Juego Terminado", f"El ganador es {winner}!") if pvpMode else None
                self.save_screenshot() if pvpMode else None
                self.reset_game()
                return  # Detener la ejecución si el juego ha terminado
            elif '' not in [btn['text'] for btn in self.buttons]:  # Comprobar si el tablero está lleno
                self.draws += 1 if pvpMode else None
                messagebox.showinfo("Juego Terminado", "¡Es un empate!")  if pvpMode else None
                self.save_screenshot() if pvpMode else None
                self.reset_game()
            else:
                # Cambia el turno al jugador humano
                if pvpMode is True:
                    self.turn = 'X'
                    self.update_scores() 

    def create_menu(self):
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)

        # Adding a 'File' menu
        file_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Juego", menu=file_menu)
        file_menu.add_command(label="Mostrar historial", command=self.show_history)
        file_menu.add_command(label="Entrenar modelo", command=self.ask_training_games)

    def save_screenshot(self):
        # Ensure the 'history' directory exists
        os.makedirs('history', exist_ok=True)

        # Get the bounding box of the game board
        x0 = self.root.winfo_rootx() + self.buttons[0].winfo_x()
        y0 = self.root.winfo_rooty() + self.buttons[0].winfo_y()
        x1 = x0 + 3 * self.buttons[0].winfo_width()
        y1 = y0 + 3 * self.buttons[0].winfo_height()

        # Capture and save the screenshot
        img = ImageGrab.grab(bbox=(x0, y0, x1, y1))
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        img.save(f'history/game_{timestamp}.png')
        print(f"Saved screenshot as 'history/game_{timestamp}.png'")

    def show_history(self):
        # Open a new window to show the history of games
        history_window = Toplevel()
        history_window.title("Historial de Partidas")

        # Use a scrollbar on the canvas
        canvas = tk.Canvas(history_window)
        scrollbar = tk.Scrollbar(history_window, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        # Configure canvas and scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        game_files = sorted([f for f in os.listdir('history') if f.endswith('.png')], reverse=True)
        for i, filename in enumerate(game_files, start=1):
            image_path = os.path.join('history', filename)
            img = Image.open(image_path)
            img.thumbnail((150, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            label_image = Label(scrollable_frame, image=photo)
            label_image.image = photo  # Keep a reference!
            label_image.grid(row=i, column=0, padx=10, pady=10)

            # Display dummy Q-values or load real Q-values if you have them
            # Example with dummy values:
            q_values_text = "Q-values: " + ", ".join(f"{k}: {v:.2f}" for k, v in enumerate(np.random.rand(9)))
            label_q_values = Label(scrollable_frame, text=f"Partida {i}: {q_values_text}", font=("Arial", 10))
            label_q_values.grid(row=i, column=1, sticky="w", padx=10)

        # Pack and place the canvas and scrollbar in the window
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)


    def train_model(self, N=100):
        training_window = Toplevel()
        training_window.title("Training in Progress")
        ttk.Label(training_window, text="Training... Please wait").pack(padx=10, pady=10)

        progress = ttk.Progressbar(training_window, orient="horizontal", length=200, mode='determinate')
        progress.pack(padx=10, pady=10)
        training_window.pack_slaves()

        def update_progress_bar(current, total):
            progress['value'] = (current / total) * 100
            self.root.update_idletasks()

        def train():
            use_x = True
            best_q_value_before = self.get_best_q_value()  # Obtiene el mejor valor Q antes del entrenamiento
            self.reset_game(False)
            for i in range(N):
                self.root.after(500, self.simulate_game(use_x))                
                use_x = not use_x
                update_progress_bar(i + 1, N)
            training_window.destroy()

            best_q_value_after = self.get_best_q_value()  # Obtiene el mejor valor Q después del entrenamiento
            improvement = best_q_value_after
            messagebox.showinfo("Entrenamiento Completo", f"Entrenamiento completado. Mejora del valor Q: {improvement:.2f}")

        tk.Button(training_window, text="Cancel", command=training_window.destroy).pack(padx=10, pady=10)

        self.root.after(100, train)

    def simulate_game(self, use_x):
        self.reset_game(silent=True)  # Asegurarse de no reiniciar el árbol AVL
        self.turn = 'X' if use_x else 'O'
        move_count = 0  # Contador para verificar cantidad de movimientos y prevenir bucle infinito

        while move_count < 9:  # Hay un máximo de 9 movimientos en un tablero 3x3
            current_state = self.get_board_state()
            empty_indices = [i for i, btn in enumerate(self.buttons) if btn['text'] == '']
            if not empty_indices:
                break  # Salir si no hay casillas vacías

            move_index = self.choose_best_move(current_state, empty_indices)
            self.execute_move(move_index, self.turn, False)

            winner = self.winner()
            if winner or '' not in [btn['text'] for btn in self.buttons]:
                break  # Salir si hay un ganador o no quedan movimientos

            self.turn = 'O' if self.turn == 'X' else 'X'  # Alternar turno
            move_count += 1

        self.reset_game(silent=True)  # Reiniciar el juego de forma silenciosa para la siguiente simulación


    def ask_training_games(self):
        try:
            N = simpledialog.askinteger("Entrenamiento", "Ingresa el número de juegos para entrenar:", minvalue=1, maxvalue=20)
            if N is not None:
                self.train_model(N)
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingresa un número entero válido.")

    def get_best_q_value(self):
        all_values = [node.value_q for node in self.avl_tree.get_all_nodes() if node.value_q]
        if not all_values:  # Comprobar si la lista está vacía
            return 0  # O el valor por defecto que consideres apropiado
        return max(max(values.values()) for values in all_values if values)


if __name__ == "__main__":
    root = tk.Tk()
    avl_tree = AVLTree()  # Asegúrate de que AVLTree esté correctamente definido
    app = TicTacToeApp(root, avl_tree)
    root.mainloop()
