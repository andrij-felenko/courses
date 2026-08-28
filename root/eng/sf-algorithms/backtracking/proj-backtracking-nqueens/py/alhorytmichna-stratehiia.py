from typing import List

class SudokuSolver:
    SIZE = 9

    def _is_valid(self, board: List[List[int]], row: int, col: int, num: int) -> bool:
        """Перевірка обмежень для рядка, стовпчика та підсітки 3x3."""
        for i in range(self.SIZE):
            # Перевірка рядка та стовпчика
            if board[row][i] == num or board[i][col] == num:
                return False
            
            # Перевірка квадратного блоку 3x3
            box_row = 3 * (row // 3) + i // 3
            box_col = 3 * (col // 3) + i % 3
            if board[box_row][box_col] == num:
                return False
        return True

    def solve(self, board: List[List[int]]) -> bool:
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                if board[row][col] == 0:
                    for num in range(1, 10):
                        if self._is_valid(board, row, col, num):
                            # 1. CHOOSE
                            board[row][col] = num

                            # 2. EXPLORE
                            if self.solve(board):
                                return True

                            # 3. UNCHOOSE (Backtrack)
                            board[row][col] = 0

                    # Жодне число не підійшло — відступаємо назад
                    return False
        return True

def print_board(board: List[List[int]]) -> None:
    for r in range(9):
        if r > 0 and r % 3 == 0:
            print("-" * 21)
        row_str = ""
        for c in range(9):
            if c > 0 and c % 3 == 0:
                row_str += "| "
            row_str += str(board[r][c]) + " "
        print(row_str)

if __name__ == "__main__":
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]

    solver = SudokuSolver()
    if solver.solve(puzzle):
        print("Успішно розв'язане Судоку:\n")
        print_board(puzzle)
    else:
        print("Розв'язку не існує.")
