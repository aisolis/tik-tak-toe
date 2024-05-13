import tkinter as tk
from tkinter import messagebox, Toplevel, Menu, Label, simpledialog
from PIL import Image, ImageTk
import os
import numpy as np

from utilities import GameUtilities
from machineAI import MachineIa
from avlTree import AVLTree

class BoardManager:

    def __init__(self):
        root = tk.Tk()
        self.avl_tree = AVLTree()  # Asegúrate de que AVLTree esté correctamente definido
        root.title("Juego de Totito")
        self.gameUtilities = GameUtilities(self)
        self.root = root


    def init_Ia(self, new_self):
        self.machineIa = MachineIa(new_self)
    
        

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
            #self.avl_tree.root = None
            print("tried to restart avl node")
        if hasattr(self, 'buttons'):
            for btn in self.buttons:
                btn.config(text='')
        if not silent:
            self.score_x = getattr(self, 'score_x', 0)
            self.score_o = getattr(self, 'score_o', 0)
            self.draws = getattr(self, 'draws', 0)
            self.update_scores()

    def update_score(self, winner):
        if winner == 'X':
            self.score_x += 1
        elif winner == 'O':
            self.score_o += 1

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
    
    def create_menu(self):
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)

        # Adding a 'File' menu
        file_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Juego", menu=file_menu)
        file_menu.add_command(label="Mostrar historial", command=self.show_history)
        file_menu.add_command(label="Entrenar modelo", command=self.ask_training_games)
        file_menu.add_command(label="Generar diagrama de evolucion", command=self.show_avl_tree)
        file_menu.add_command(label="Integrantes del grupo", command=self.show_group_information)
        self.init_Ia(self)

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

    def show_avl_tree(self):
        self.avl_tree.visualize_tree()

    
    def show_group_information(self):
            informacion_grupo = "Integrantes del grupo:\n\n" \
                                "- Cristhian Sebastián Rodas Arriola, 9490-22-523, Sección A\n" \
                                "- Alder Isaac Solis De León, 9490-22-227, Sección A\n" \
                                "- Angel Emilio Méndez Muralles, 9490-22-5851, Sección A\n" \
                                "- Abner Salvador Cancinos Cabrera, 9490-22-2101, Sección A\n"\
                                "- Joshua Iván Mendez Vasquez, 9490-22-4032, Sección A\n"
            messagebox.showinfo("Información del grupo", informacion_grupo)

    def on_button_press(self, index, pvpMode=True):
        if self.buttons[index]['text'] == '' and self.winner() is None:
            self.buttons[index]['text'] = self.turn
            #current_state = self.get_board_state()

            # Actualizar el árbol AVL con el nuevo estado del juego
            # Nota: Deberías definir cómo calcular el valor Q para el nuevo estado aquí
            # Por simplicidad, se usa un valor Q dummy
            #dummy_value_q = {i: 0 for i in range(9) if self.buttons[i]['text'] == ''}
            #self.avl_tree.root = self.avl_tree.insert(self.avl_tree.root, current_state, dummy_value_q)

            # Verificar si hay un ganador
            winner = self.winner()
            if winner:
                self.update_score(winner) if pvpMode else None
                messagebox.showinfo("Juego Terminado", f"El ganador es {winner}!") if pvpMode else None
                self.gameUtilities.save_screenshot() 
                self.reset_game()
            elif '' not in [btn['text'] for btn in self.buttons]:  # Comprobar si el tablero está lleno
                self.draws += 1 if pvpMode else None
                messagebox.showinfo("Juego Terminado", "¡Es un empate!") if pvpMode else None
                self.gameUtilities.save_screenshot() 
                self.reset_game()
            else:
                # Cambiar el turno
                self.turn = 'O' if self.turn == 'X' else 'X'
                self.update_scores() if pvpMode else None
                # Si es el turno de la máquina, realizar el movimiento
                if self.turn == 'O':
                    self.avl_tree.remove_duplicates()
                    self.root.after(500, self.machineIa.machine_move(True))
    
    def get_board_state(self):
        # Convertir el estado del tablero a una tupla para ser hashable
        return tuple(btn['text'] for btn in self.buttons)
    
    def ask_training_games(self):
        try:
            N = simpledialog.askinteger("Entrenamiento", "Ingresa el número de juegos para entrenar:", minvalue=1, maxvalue=100)
            if N is not None:
                self.machineIa.train_model(N)
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingresa un número entero válido.")