from graphviz import Digraph

from avlNode import AVLNode

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

    def visualize_tree(self, filename='avl_tree'):
        dot = Digraph(comment='AVL Tree')
        if not self.root:
            dot.node('None', 'Empty Tree')
            dot.render(filename, view=True)
            return
        self._add_nodes(dot, self.root)
        dot.render(filename, view=True)  # Guarda y muestra el gráfico automáticamente

    def _add_nodes(self, dot, node):
        if node:
            # Simplificamos la etiqueta para mostrar solo el mejor valor Q
            best_q_value = max(node.value_q.values()) if node.value_q else 'No Q-values'
            label = f"Q: {best_q_value}"
            dot.node(str(id(node)), label)
            self._add_edges(dot, node)
            self._add_nodes(dot, node.left)
            self._add_nodes(dot, node.right)

    def _add_edges(self, dot, node):
        if node and node.left:
            dot.edge(str(id(node)), str(id(node.left)))
        if node and node.right:
            dot.edge(str(id(node)), str(id(node.right)))

    def delete_node(self, node, board_state):
        if not node:
            return node

        if board_state < node.board_state:
            node.left = self.delete_node(node.left, board_state)
        elif board_state > node.board_state:
            node.right = self.delete_node(node.right, board_state)
        else:
            if not node.left:
                temp = node.right
                node = None
                return temp
            elif not node.right:
                temp = node.left
                node = None
                return temp

            temp = self.get_min_value_node(node.right)
            node.board_state, node.value_q = temp.board_state, temp.value_q
            node.right = self.delete_node(node.right, temp.board_state)

        if not node:
            return node

        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        balance = self.get_balance(node)

        if balance > 1 and self.get_balance(node.left) >= 0:
            return self.rotate_right(node)
        if balance > 1 and self.get_balance(node.left) < 0:
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)
        if balance < -1 and self.get_balance(node.right) <= 0:
            return self.rotate_left(node)
        if balance < -1 and self.get_balance(node.right) > 0:
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)

        return node

    def get_min_value_node(self, node):
        if node is None or node.left is None:
            return node
        return self.get_min_value_node(node.left)

    def remove_duplicates(self):
        def in_order_collect(node, seen, duplicates):
            if not node:
                return
            in_order_collect(node.left, seen, duplicates)
            max_q_value = max(node.value_q.values(), default=None)
            if max_q_value in seen:
                duplicates.append(node.board_state)
            else:
                seen.add(max_q_value)
            in_order_collect(node.right, seen, duplicates)

        seen = set()
        duplicates = []
        in_order_collect(self.root, seen, duplicates)

        for board_state in duplicates:
            self.root = self.delete_node(self.root, board_state)