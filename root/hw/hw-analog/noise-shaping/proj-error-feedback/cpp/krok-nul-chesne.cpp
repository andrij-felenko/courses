#include <cstdint>

constexpr int32_t PWM_TOP =   500;     // період таймера: рівні шпаруватості 0..500
constexpr int32_t IN_MAX  = 65535;     // повний розмах 16-бітного входу

// Формувач шуму 1-го порядку. Викликати на КОЖЕН звуковий відлік.
// err зберігає похибку між викликами (звідси static), у масштабі ВХОДУ.
uint16_t shape1(uint16_t sample) {
    static int32_t err = 0;              // борг попереднього відліку

    int32_t u = (int32_t)sample + err;   // додаємо борг у масштабі входу

    // квантуємо u (0..IN_MAX) у рівень 0..PWM_TOP з округленням до найближчого:
    //   level = round(u * PWM_TOP / IN_MAX)
    int32_t level = (u * PWM_TOP + IN_MAX / 2) / IN_MAX;

    // насичення: борг не має права виштовхнути нас за межі виходу
    if (level < 0)       level = 0;
    if (level > PWM_TOP) level = PWM_TOP;

    // назад у масштаб входу — що ми РЕАЛЬНО віддали цим рівнем
    int32_t y = (level * IN_MAX + PWM_TOP / 2) / PWM_TOP;

    err = u - y;                         // нова похибка = скільки не влізло

    return (uint16_t)level;              // це й вантажимо в регістр порівняння таймера
}
