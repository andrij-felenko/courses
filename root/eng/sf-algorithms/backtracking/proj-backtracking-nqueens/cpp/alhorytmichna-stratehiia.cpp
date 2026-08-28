#include <iostream>
#include <vector>

class SudokuSolver {
private:
    static const int SIZE = 9;

    // Перевірка допустимості розміщення числа num у позиції (row, col)
    bool isValid(const std::vector<std::vector<int>>& board, int row, int col, int num) {
        for (int i = 0; i < SIZE; ++i) {
            // Перевірка горизонтального рядка
            if (board[row][i] == num) return false;
            
            // Перевірка вертикального стовпчика
            if (board[i][col] == num) return false;
            
            // Перевірка квадратного блоку 3x3
            int boxRow = 3 * (row / 3) + i / 3;
            int boxCol = 3 * (col / 3) + i % 3;
            if (board[boxRow][boxCol] == num) return false;
        }
        return true;
    }

public:
    bool solve(std::vector<std::vector<int>>& board) {
        for (int row = 0; row < SIZE; ++row) {
            for (int col = 0; col < SIZE; ++col) {
                // Знайдено не заповнену клітинку
                if (board[row][col] == 0) {
                    for (int num = 1; num <= 9; ++num) {
                        if (isValid(board, row, col, num)) {
                            // 1. CHOOSE: Робимо вибір
                            board[row][col] = num;

                            // 2. EXPLORE: Рекурсивний рух углиб
                            if (solve(board)) {
                                return true; // Розв'язок знайдено повністю
                            }

                            // 3. UNCHOOSE: Скасовуємо вибір (Backtrack)
                            board[row][col] = 0;
                        }
                    }
                    // Якщо жодна цифра 1..9 не підійшла — це глухий кут
                    return false;
                }
            }
        }
        return true; // Порожніх клітинок не залишилося
    }
};

void printBoard(const std::vector<std::vector<int>>& board) {
    for (int r = 0; r < 9; ++r) {
        if (r > 0 && r % 3 == 0) std::cout << "---------------------\n";
        for (int c = 0; c < 9; ++c) {
            if (c > 0 && c % 3 == 0) std::cout << "| ";
            std::cout << board[r][c] << " ";
        }
        std::cout << "\n";
    }
}

int main() {
    std::vector<std::vector<int>> board = {
        {5, 3, 0, 0, 7, 0, 0, 0, 0},
        {6, 0, 0, 1, 9, 5, 0, 0, 0},
        {0, 9, 8, 0, 0, 0, 0, 6, 0},
        {8, 0, 0, 0, 6, 0, 0, 0, 3},
        {4, 0, 0, 8, 0, 3, 0, 0, 1},
        {7, 0, 0, 0, 2, 0, 0, 0, 6},
        {0, 6, 0, 0, 0, 0, 2, 8, 0},
        {0, 0, 0, 4, 1, 9, 0, 0, 5},
        {0, 0, 0, 0, 8, 0, 0, 7, 9}
    };

    SudokuSolver solver;
    if (solver.solve(board)) {
        std::cout << "Успішно розв'язане Судоку:\n\n";
        printBoard(board);
    } else {
        std::cout << "Розв'язку не існує.\n";
    }
    return 0;
}
