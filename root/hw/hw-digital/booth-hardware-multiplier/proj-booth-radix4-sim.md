# ⚙️ C++17 симулятор Radix-4 множника Бута

Класична симуляція алгоритму Бута демонструє обробку одного біта за такт. Проте реальні процесори використовують модифікований алгоритм **Radix-4 Booth**, який аналізує перекривні трійки бітів та зсуває акумулятор одразу на два біти. Це зменшує кількість ітерацій удвічі (з N до N/2).

Нижче наведено робочий C++17 симулятор 16-бітного Radix-4 множника, побудований за 5-компонентною апаратною схемою ALU.

```cpp
#include <iostream>
#include <cstdint>
#include <iomanip>

// 1. Генератор кратностей: створює M, -M, 2M, -2M у знакових 32-бітних операндах
struct MultiplicandGen {
    int32_t M;
    int32_t negM;
    int32_t twoM;
    int32_t negTwoM;

    explicit MultiplicandGen(int16_t m) : M(m) {
        negM = -M;
        twoM = M << 1;
        negTwoM = -twoM;
    }

    int32_t select(int factor) const {
        switch (factor) {
            case  1: return M;
            case  2: return twoM;
            case -1: return negM;
            case -2: return negTwoM;
            default: return 0;
        }
    }
};

// 2. Енкодер Бута (Radix-4 Booth Encoder): декодує трійку бітів y_{i+1}, y_i, y_{i-1}
int booth_encode_radix4(uint8_t triplet) {
    switch (triplet & 0x07) {
        case 0b001: case 0b010: return  1; // +M
        case 0b011:             return  2; // +2M
        case 0b100:             return -2; // -2M
        case 0b101: case 0b110: return -1; // -M
        default:                return  0; // 0 (0b000 або 0b111)
    }
}

// Повний 5-компонентний симулятор Radix-4
int32_t multiply_radix4(int16_t multiplicand, int16_t multiplier) {
    MultiplicandGen gen(multiplicand); // Компонент 1: Генератор кратностей
    int16_t A = 0;                    // Компонент 3: Акумулятор (16 біт, зі знаком)
    uint16_t Q = static_cast<uint16_t>(multiplier); // Компонент 4: Регістр множника
    uint8_t q_minus_1 = 0;            // Додатковий біт для трійки

    // 8 ітерацій для 16-бітних чисел (16 / 2)
    for (int step = 0; step < 8; ++step) {
        // Компонент 2: Селектор трійки бітів (y_{i+1}, y_i, y_{i-1})
        uint8_t y_prev = q_minus_1;
        uint8_t y_curr = Q & 1;
        uint8_t y_next = (Q >> 1) & 1;
        uint8_t triplet = (y_next << 2) | (y_curr << 1) | y_prev;

        int factor = booth_encode_radix4(triplet);
        int32_t partial = gen.select(factor);

        // Додаємо частковий добуток до акумулятора (АЛП)
        int32_t new_A = static_cast<int32_t>(A) + partial;

        // Компонент 5: Арифметичний зсув регістра [A, Q, q_minus_1] вправо на 2 біти
        q_minus_1 = (Q >> 1) & 1; // Новий q_minus_1 — це передостанній біт Q
        
        // Переносимо 2 молодші біти від розширеного Акумулятора в старші біти Q
        uint16_t low_A_bits = static_cast<uint16_t>(new_A & 0x0003) << 14;
        Q = (Q >> 2) | low_A_bits;

        // Арифметичний зсув акумулятора A вправо на 2 з збереженням знака
        A = static_cast<int16_t>(new_A >> 2);
    }

    // Збираємо 32-бітний результат із регістрів [A, Q]
    return (static_cast<int32_t>(A) << 16) | Q;
}

int main() {
    int16_t m = -12345;
    int16_t y = 5432;

    int32_t result = multiply_radix4(m, y);
    int32_t expected = static_cast<int32_t>(m) * y;

    std::cout << "Множення: " << m << " * " << y << "\n";
    std::cout << "Результат Radix-4: " << result << "\n";
    std::cout << "Очікуваний (*):    " << expected << "\n";
    std::cout << "Статус: " << (result == expected ? "УСПІХ" : "ПОМИЛКА") << "\n";

    return 0;
}
```

### Архітектура та 5-компонентний розбір

Код моделює фізичні блоки апаратного Radix-4 множника ALU:

1. **Генератор кратностей (`MultiplicandGen`):** Попередньо обчислює операнди `+M`, `-M`, `+2M` (`M << 1`) та `-2M`. Оскільки множення на 2 — це простий лівий зсув провідників, а заперечення — доповняльний код (`~X + 1`), ці значення готуються за один крок без арифметичних затримок.
2. **Енкодер Бута (`booth_encode_radix4`):** Приймає 3-бітне вікно `(y_{i+1}, y_i, y_{i-1})` і перетворює його на коефіцієнт multiplier `{-2, -1, 0, +1, +2}`.
3. **Акумулятор (`A`):** Зберігає поточний частковий підсумок. На кожному кроці додає вибрану кратність множеного.
4. **Регістр множника (`Q` + `q_minus_1`):** Висуває біти множника праворуч по 2 за такт і приймає висунуті молодші біти з акумулятора `A`.
5. **Блок арифметичного зсуву (Shift 2):** Зсуває здвоєну паралельну шину `[A, Q]` вправо на 2 позиції. Використовує знакове розширення (знаковий біт `A` дублюється в два найстарші розряди), що гарантує коректне множення від'ємних чисел без додаткових інверсій результату.
