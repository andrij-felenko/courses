// Реальний максимальний симетричний розмах каскаду зі спільним емітером.
// Q поставлено посередині СТАЛОЇ прямої; рахуємо, що дасть СИГНАЛЬНА.
#include <algorithm>
#include <iostream>

int main() {
    constexpr float Vsupply = 12.0f;   // напруга живлення, В
    constexpr float Rc      = 1000.0f; // колекторний резистор, Ом
    constexpr float Rload   = 1000.0f; // навантаження через конденсатор, Ом

    // Q посередині сталої прямої:
    constexpr float Vceq = 6.0f;                   // напруга спокою, В
    const float Icq = (Vsupply - Vceq) / Rc;       // струм спокою, А → 6 мА

    // Сигнальний (AC) опір — R_к паралельно R_навант:
    const float r_ac = (Rc * Rload) / (Rc + Rload); // 500 Ом

    // Два плеча розмаху по сигнальній прямій:
    const float swing_left  = Vceq;                 // транзистор у насичення
    const float swing_right = Icq * r_ac;           // транзистор у відсічку

    // Симетричний пік — менше з плечей:
    const float swing_ac = std::min(swing_left, swing_right);

    // Оманливе число — розмах, прикинутий по сталій прямій:
    const float swing_dc_naive = Icq * Rc;          // = Vceq = 6 В (симетрично по DC)

    std::cout << "r_ac (R_к || R_навант) = " << r_ac << " Ом\n";          // 500
    std::cout << "плече вліво  (насичення) = " << swing_left << " В\n";    // 6
    std::cout << "плече вправо (відсічка)  = " << swing_right << " В\n";   // 3
    std::cout << "РЕАЛЬНИЙ симетричний пік = " << swing_ac << " В\n";      // 3
    std::cout << "оманливий розмах по DC   = " << swing_dc_naive << " В\n";// 6
    return 0;
}
