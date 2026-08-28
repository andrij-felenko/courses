#include <iostream>
#include <array>
#include <string>
#include <cmath>

// 1. Представлення базового трита
enum class Trit : int8_t {
    Minus = -1,
    Zero = 0,
    Plus = 1
};

// 2. Представлення 9-тритного машинного слова
class TritWord {
public:
    std::array<Trit, 9> trits;

    TritWord() {
        trits.fill(Trit::Zero);
    }

    // Ініціалізація з десяткового числа (алгоритм балансування)
    explicit TritWord(int value) {
        trits.fill(Trit::Zero);
        if (value < -9841 || value > 9841) {
            std::cerr << "Переповнення: число поза межами 9 тритів.\n";
            return;
        }
        
        for (int i = 0; i < 9; ++i) {
            int remainder = value % 3;
            value /= 3;
            
            // Збалансування залишку: якщо залишок 2, переносимо одиницю в наступний розряд
            if (remainder == 2) {
                remainder = -1;
                value += 1;
            } else if (remainder == -2) {
                remainder = 1;
                value -= 1;
            }
            
            trits[i] = static_cast<Trit>(remainder);
        }
    }

    // Декодування назад у десятковий формат для перевірки
    int toInt() const {
        int result = 0;
        int power = 1;
        for (int i = 0; i < 9; ++i) {
            result += static_cast<int>(trits[i]) * power;
            power *= 3;
        }
        return result;
    }

    // Вивід у вигляді рядка з символів -, 0, + (починаючи зі старшого розряду)
    std::string toString() const {
        std::string s = "";
        for (int i = 8; i >= 0; --i) {
            if (trits[i] == Trit::Minus) s += "-";
            else if (trits[i] == Trit::Plus) s += "+";
            else s += "0";
        }
        return s;
    }
};

// 3. Структура результату повного суматора
struct AddResult {
    Trit sum;
    Trit carry;
};

// 4. Логіка трійкового повного суматора
AddResult fullAdder(Trit a, Trit b, Trit carryIn) {
    // В апаратному забезпеченні тут була б система логічних вентилів,
    // але для емуляції ми використовуємо звичайне цілочисельне додавання станів.
    int sum = static_cast<int>(a) + static_cast<int>(b) + static_cast<int>(carryIn);
    Trit carryOut = Trit::Zero;
    
    // Якщо сума перевищує допустимі межі трита (+1 або -1), генеруємо перенесення
    if (sum > 1) {
        sum -= 3;
        carryOut = Trit::Plus;
    } else if (sum < -1) {
        sum += 3;
        carryOut = Trit::Minus;
    }
    
    return {static_cast<Trit>(sum), carryOut};
}

// 5. Модуль АЛУ
class TernaryALU {
public:
    // Інверсія всього машинного слова
    static TritWord negate(const TritWord& a) {
        TritWord result;
        for (int i = 0; i < 9; ++i) {
            result.trits[i] = static_cast<Trit>(-static_cast<int>(a.trits[i]));
        }
        return result;
    }

    // Порозрядне додавання з передачею перенесення
    static TritWord add(const TritWord& a, const TritWord& b) {
        TritWord result;
        Trit carry = Trit::Zero;
        for (int i = 0; i < 9; ++i) {
            AddResult ar = fullAdder(a.trits[i], b.trits[i], carry);
            result.trits[i] = ar.sum;
            carry = ar.carry;
        }
        return result;
    }

    // Віднімання — це просто додавання інверсії
    static TritWord subtract(const TritWord& a, const TritWord& b) {
        return add(a, negate(b));
    }
};

int main() {
    TritWord a(15);  // Очікуваний результат: + - - 0 (27 - 9 - 3 + 0)
    TritWord b(24);  // Очікуваний результат: + 0 - 0 (27 - 3)
    
    std::cout << "A (15)  = " << a.toString() << "\n";
    std::cout << "B (24)  = " << b.toString() << "\n";
    
    TritWord sum = TernaryALU::add(a, b);
    std::cout << "A + B   = " << sum.toString() << " (" << sum.toInt() << ")\n";
    
    TritWord diff = TernaryALU::subtract(a, b);
    std::cout << "A - B   = " << diff.toString() << " (" << diff.toInt() << ")\n";
    
    return 0;
}
