class AVLNode:
    def __init__(self, board_state, value_q):
        self.board_state = board_state  # tupla que representa al estado del tablero
        self.value_q = value_q  # Diccionario que mapea el movimiento con las tablas Q
        self.height = 1
        self.left = None
        self.right = None