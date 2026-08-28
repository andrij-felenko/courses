// Реальний максимальний симетричний розмах каскаду зі спільним емітером.
// Q поставлено посередині СТАЛОЇ прямої; рахуємо, що дасть СИГНАЛЬНА.
#include <stdio.h>

int main(void) {
    const float Vsupply = 12.0f;   // напруга живлення, В
    const float Rc      = 1000.0f; // колекторний резистор, Ом
    const float Rload   = 1000.0f; // навантаження через конденсатор, Ом

    // Q посередині сталої прямої:
    const float Vceq = 6.0f;                       // напруга спокою, В
    const float Icq  = (Vsupply - Vceq) / Rc;      // струм спокою, А → 6 мА

    // Сигнальний (AC) опір — R_к паралельно R_навант:
    float r_ac = (Rc * Rload) / (Rc + Rload);      // 500 Ом

    // Два плеча розмаху по сигнальній прямій:
    float swing_left  = Vceq;                       // транзистор у насичення
    float swing_right = Icq * r_ac;                 // транзистор у відсічку

    // Симетричний пік — менше з плечей:
    float swing_ac = (swing_left < swing_right) ? swing_left : swing_right;

    // Оманливе число — розмах, прикинутий по сталій прямій:
    float swing_dc_naive = Icq * Rc;                // = Vceq = 6 В (симетрично по DC)

    printf("r_ac (R_к || R_навант) = %.0f Ом\n", r_ac);          // 500
    printf("плече вліво  (насичення) = %.2f В\n", swing_left);    // 6.00
    printf("плече вправо (відсічка)  = %.2f В\n", swing_right);   // 3.00
    printf("РЕАЛЬНИЙ симетричний пік = %.2f В\n", swing_ac);      // 3.00
    printf("оманливий розмах по DC   = %.2f В\n", swing_dc_naive);// 6.00
    return 0;
}
