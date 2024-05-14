from board import BoardManager


class TicTacToeApp:
    def __init__(self):
        self.board = BoardManager()    
        self.board.reset_game(False)
        self.board.create_widgets()
        self.board.create_menu()
        self.board.root.mainloop()

if __name__ == "__main__":
    app = TicTacToeApp()
