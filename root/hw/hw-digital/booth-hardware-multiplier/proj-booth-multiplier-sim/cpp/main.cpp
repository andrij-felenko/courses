#include <iostream>
#include <cstdint>
#include <iomanip>

// Допоміжна функція для друку бінарного представлення
void print_binary(const std::string& label, uint32_t val, int bits) {
    std::cout << label << " ";
    for (int i = bits - 1; i >= 0; --i) {
        std::cout << ((val >> i) & 1);
        if (i % 4 == 0) std::cout << " ";
    }
    std::cout << "\n";
}

int32_t booth_multiply_16bit(int16_t multiplicand, int16_t multiplier) {
    uint16_t M = multiplicand;
    uint16_t A = 0;
    uint16_t Q = multiplier;
    uint8_t Q_minus_1 = 0;

    std::cout << "Ініціалізація:\n";
    print_binary("M (Множене):", M, 16);
    print_binary("A (Акумулятор):", A, 16);
    print_binary("Q (Множник):", Q, 16);
    std::cout << "Q-1: " << (int)Q_minus_1 << "\n\n";

    for (int step = 0; step < 16; ++step) {
        std::cout << "--- Крок " << (step + 1) << " ---\n";
        
        uint8_t Q0 = Q & 1;
        
        // Крок 1: Аналіз пари бітів (Q0, Q_minus_1) та операція над A
        if (Q0 == 1 && Q_minus_1 == 0) {
            std::cout << "  Дія: A = A - M (виявлено 10)\n";
            A = A - M; // Додавання доповняльного коду
        } else if (Q0 == 0 && Q_minus_1 == 1) {
            std::cout << "  Дія: A = A + M (виявлено 01)\n";
            A = A + M;
        } else {
            std::cout << "  Дія: Тільки зсув (виявлено " << (int)Q0 << (int)Q_minus_1 << ")\n";
        }
        
        print_binary("  A після AL-операції:", A, 16);

        // Крок 2: Арифметичний зсув вправо [A, Q, Q_minus_1]
        // Спочатку зберігаємо старший біт A (знаковий біт) для розширення знака
        uint16_t sign_A = A & 0x8000; 
        
        // Зберігаємо біт, що випаде з A і стане старшим бітом Q
        uint16_t bit_A_to_Q = (A & 1) << 15;
        
        // Зберігаємо біт, що випаде з Q і стане Q_minus_1
        uint8_t bit_Q_to_Q_minus_1 = Q & 1;
        
        // Виконуємо зсуви
        A = (A >> 1) | sign_A; // Арифметичний зсув A
        Q = (Q >> 1) | bit_A_to_Q; // Логічний зсув Q з перенесенням біта з A
        Q_minus_1 = bit_Q_to_Q_minus_1;
        
        std::cout << "  Після зсуву:\n";
        print_binary("  A:", A, 16);
        print_binary("  Q:", Q, 16);
        std::cout << "  Q-1: " << (int)Q_minus_1 << "\n\n";
    }

    // Комбінуємо A та Q в єдиний 32-бітний результат
    int32_t result = (static_cast<uint32_t>(A) << 16) | Q;
    return result;
}

int main() {
    int16_t m = -12345;
    int16_t y = 5432;
    
    std::cout << "Множимо " << m << " на " << y << "\n\n";
    
    int32_t result = booth_multiply_16bit(m, y);
    int32_t expected = static_cast<int32_t>(m) * y;
    
    std::cout << "========================================\n";
    std::cout << "Результат симуляції Бута: " << result << "\n";
    std::cout << "Очікуваний результат (*): " << expected << "\n";
    
    if (result == expected) {
        std::cout << "УСПІХ: Результати збігаються.\n";
    } else {
        std::cout << "ПОМИЛКА: Розбіжність у результатах!\n";
    }
    
    return 0;
}
