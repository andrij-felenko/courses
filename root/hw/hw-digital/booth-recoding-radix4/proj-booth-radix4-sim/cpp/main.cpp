#include <iostream>
#include <cstdint>
#include <iomanip>

// Витягування 3 бітів (Q_1, Q_0 та Q_minus_1)
uint8_t get_booth_code(int32_t Q, uint8_t Q_minus_1) {
    return ((Q & 0b11) << 1) | Q_minus_1;
}

// Виведення стану регістров у двійковому форматі
void print_state(const std::string& step, int32_t A, int32_t Q, uint8_t Q_minus_1) {
    std::cout << std::left << std::setw(15) << step 
              << "A: " << std::bitset<32>(A) 
              << " Q: " << std::bitset<32>(Q) 
              << " Q_(-1): " << static_cast<int>(Q_minus_1) << "\n";
}

int64_t booth_radix4_multiply(int32_t M, int32_t Q) {
    int32_t A = 0;
    uint8_t Q_minus_1 = 0;
    
    std::cout << "--- Початок множення ---\n";
    print_state("Ініціалізація", A, Q, Q_minus_1);

    // Оскільки обробляємо по 2 біти за крок, кількість кроків = 32 / 2 = 16
    for (int step = 0; step < 16; ++step) {
        uint8_t code = get_booth_code(Q, Q_minus_1);
        
        switch (code) {
            case 0b000: // 0
            case 0b111: // 0
                // Немає дій, лише зсув
                break;
            case 0b001: // +1M
            case 0b010: // +1M
                A += M;
                break;
            case 0b011: // +2M
                A += (M << 1);
                break;
            case 0b100: // -2M
                A -= (M << 1);
                break;
            case 0b101: // -1M
            case 0b110: // -1M
                A -= M;
                break;
        }

        // Арифметичний зсув пари A і Q вправо на 2 розряди
        // Збережемо нові біти для Q та Q_minus_1
        uint8_t next_Q_minus_1 = (Q >> 1) & 1;
        int32_t next_Q = (Q >> 2) & 0x3FFFFFFF; 
        
        // Вставляємо 2 молодші біти A у старші позиції Q
        next_Q |= (A & 0b11) << 30; 
        
        A >>= 2; // Знаковий зсув
        Q = next_Q;
        Q_minus_1 = next_Q_minus_1;
    }
    
    // Результат формується об'єднанням A і Q
    int64_t result = (static_cast<int64_t>(A) << 32) | (static_cast<uint32_t>(Q));
    std::cout << "--- Завершення ---\n";
    std::cout << "Результат: " << result << "\n";
    return result;
}

int main() {
    int32_t M = 15;  // 00..001111
    int32_t Q = -5;  // 11..111011
    booth_radix4_multiply(M, Q);
    return 0;
}
