# Емулятор 16-бітного паралельного суматора CLA на C++

Для глибокого розуміння того, як працює паралельний перенос, найкраще реалізувати його логіку програмно, імітуючи роботу реальних апаратних вентилів. Нижче наведено код на C++17, який емулює 16-бітний суматор із паралельним переносом (Carry-Lookahead Adder). Програма не використовує вбудовану операцію додавання `+`, натомість вона побітово моделює вентилі AND, OR та XOR, розраховуючи сигнали Generate (G) та Propagate (P), а також обчислюючи префіксні переноси з логуванням затримок.

Структура емулятора складається з п'яти основних компонентів:
1. **Генерація P та G (Рівень 1):** Обчислення P_i та G_i для кожного біта паралельно (1 умовний такт затримки).
2. **Блоки Lookahead Carry (Рівень 2):** Логіка обчислення переносів C_i всередині 4-бітних блоків (2 умовні такти затримки).
3. **Блок Block Carry-Lookahead (Рівень 3):** Глобальний блок, який бере групові P і G від кожного з чотирьох 4-бітних блоків для обчислення міжблочних переносів (2 умовні такти затримки).
4. **Обчислення суми (Рівень 4):** Фінальний XOR між P_i та C_i (1 умовний такт затримки).
5. **Тестбенч (Testbench):** Головна функція для подачі тестових векторів та виведення логів затримки.

```cpp
#include <iostream>
#include <vector>
#include <bitset>
#include <cstdint>
#include <iomanip>

struct CLAResult {
    uint16_t sum;
    bool carry_out;
    int gate_delays;
};

// Емуляція 16-бітного CLA з 4-бітними блоками
CLAResult simulateCLA16(uint16_t A, uint16_t B, bool Cin) {
    std::vector<bool> a(16), b(16), p(16), g(16), c(17);
    std::vector<bool> P_block(4), G_block(4), C_block(5);
    int delays = 0;

    // Розпакування бітів
    for (int i = 0; i < 16; ++i) {
        a[i] = (A >> i) & 1;
        b[i] = (B >> i) & 1;
    }
    
    c[0] = Cin;
    C_block[0] = Cin;

    // Рівень 1: Обчислення P та G (1 вентиль: XOR, AND)
    for (int i = 0; i < 16; ++i) {
        p[i] = a[i] ^ b[i]; // Propagate: A XOR B
        g[i] = a[i] & b[i]; // Generate: A AND B
    }
    delays += 1;

    // Рівень 2: Групові P та G для 4-бітних блоків (2 вентилі: AND, OR)
    for (int j = 0; j < 4; ++j) {
        int i = j * 4;
        P_block[j] = p[i] & p[i+1] & p[i+2] & p[i+3];
        G_block[j] = g[i+3] | (p[i+3] & g[i+2]) | 
                     (p[i+3] & p[i+2] & g[i+1]) | 
                     (p[i+3] & p[i+2] & p[i+1] & g[i]);
    }
    delays += 2;

    // Рівень 3: Глобальний Lookahead (між блоками) (2 вентилі)
    for (int j = 0; j < 4; ++j) {
        C_block[j+1] = G_block[j] | (P_block[j] & C_block[j]);
        // Розгорнута логіка для C_block аналогічна до рівня бітів
    }
    C_block[1] = G_block[0] | (P_block[0] & C_block[0]);
    C_block[2] = G_block[1] | (P_block[1] & G_block[0]) | (P_block[1] & P_block[0] & C_block[0]);
    C_block[3] = G_block[2] | (P_block[2] & G_block[1]) | (P_block[2] & P_block[1] & G_block[0]) | (P_block[2] & P_block[1] & P_block[0] & C_block[0]);
    C_block[4] = G_block[3] | (P_block[3] & C_block[3]); 
    delays += 2;

    // Рівень 4: Обчислення внутрішніх переносів у блоках (2 вентилі)
    for (int j = 0; j < 4; ++j) {
        int i = j * 4;
        c[i] = C_block[j];
        c[i+1] = g[i] | (p[i] & c[i]);
        c[i+2] = g[i+1] | (p[i+1] & g[i]) | (p[i+1] & p[i] & c[i]);
        c[i+3] = g[i+2] | (p[i+2] & g[i+1]) | (p[i+2] & p[i+1] & g[i]) | (p[i+2] & p[i+1] & p[i] & c[i]);
    }
    delays += 2;

    // Рівень 5: Обчислення кінцевої суми (1 вентиль: XOR)
    uint16_t sum = 0;
    for (int i = 0; i < 16; ++i) {
        bool s = p[i] ^ c[i];
        if (s) sum |= (1 << i);
    }
    delays += 1;

    return {sum, C_block[4], delays};
}

int main() {
    uint16_t A = 0b1100110011001100;
    uint16_t B = 0b1010101010101010;
    
    CLAResult res = simulateCLA16(A, B, false);
    
    std::cout << "A:      " << std::bitset<16>(A) << "\n";
    std::cout << "B:      " << std::bitset<16>(B) << "\n";
    std::cout << "Sum:    " << std::bitset<16>(res.sum) << "\n";
    std::cout << "C_out:  " << res.carry_out << "\n";
    std::cout << "Delays: " << res.gate_delays << " gate levels\n";
    
    // Для порівняння, Ripple-Carry мав би 16 * 2 = 32 levels of delay
    
    return 0;
}
```

Цей код демонструє, як за допомогою дворівневої ієрархії (спочатку 4-бітні блоки, потім глобальний блок на 4 входи) ми зменшуємо кількість рівнів затримки до 8 логічних вентилів, тоді як звичайний Ripple-Carry суматор потребував би 32 послідовних кроків (по два вентилі на кожен з 16 бітів). Саме цей принцип блочного групування дозволяє маштабувати паралельні суматори на 32 та 64 біти з мінімальним збільшенням часу виконання.
