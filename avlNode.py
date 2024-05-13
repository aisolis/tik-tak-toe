class AVLNode:
    def __init__(self, board_state, value_q):
        self.board_state = board_state  # Tuple representation of the board
        self.value_q = value_q  # Dictionary mapping from move to Q-value
        self.height = 1
        self.left = None
        self.right = None