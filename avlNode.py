class AVLNode:
    def __init__(self, board_state, value_q):
        self.board_state = board_state  # Tuple representation of the board
        self.value_q = value_q  # Dictionary mapping from move to Q-value
        self.height = 1
        self.left = None
        self.right = None

class AVLTree:
    def __init__(self):
        self.root = None
    
    def insert(self, node, board_state, value_q):
        if not node:
            return AVLNode(board_state, value_q)
        elif board_state < node.board_state:
            node.left = self.insert(node.left, board_state, value_q)
        else:
            node.right = self.insert(node.right, board_state, value_q)
        
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        balance = self.get_balance(node)
        
        if balance > 1 and board_state < node.left.board_state:
            return self.rotate_right(node)
        if balance < -1 and board_state > node.right.board_state:
            return self.rotate_left(node)
        if balance > 1 and board_state > node.left.board_state:
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)
        if balance < -1 and board_state < node.right.board_state:
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)
        
        return node

    def get_height(self, node):
        if not node:
            return 0 
        return node.height
    
    def get_balance(self, node):
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)
    
    def rotate_left(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y
    
    def rotate_right(self, z):
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y

    def search(self, node, board_state):
        if not node or node.board_state == board_state:
            return node
        elif board_state < node.board_state:
            return self.search(node.left, board_state)
        else:
            return self.search(node.right, board_state)
        
    def get_all_nodes(self):
        nodes = []
        self._inorder_traverse(self.root, nodes)
        return nodes

    def _inorder_traverse(self, node, nodes):
        if node is not None:
            self._inorder_traverse(node.left, nodes)
            nodes.append(node)
            self._inorder_traverse(node.right, nodes)
