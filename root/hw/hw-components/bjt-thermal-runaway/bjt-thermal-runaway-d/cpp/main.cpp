// Як тепло зрушує робочу точку BJT у двох схемах зміщення.
// Схема А (фіксований Ib): струм бази закріплений, Ic = β·Ib пливе разом з β.
// Схема Б (подільник + RE): база при сталому потенціалі, RE гасить дрейф.
#include <stdio.h>

int main(void) {
    const float Vbb     = 1.59f;     // потенціал бази від подільника (схема Б), В
    const float RE      = 470.0f;    // емітерний резистор (схема Б), Ом
    const float beta25  = 150.0f;    // β при 25 °C
    const float Ic25    = 0.002f;    // цільовий струм при 25 °C, А

    // струм бази, закріплений у схемі А раз і назавжди при 25 °C
    const float Ib_fixed = Ic25 / beta25;

    float T[2] = {25.0f, 75.0f};
    for (int k = 0; k < 2; k++) {
        float dT   = T[k] - 25.0f;
        float beta = beta25 * (1.0f + 0.008f * dT);      // β росте 0.8 %/°C
        float Vbe  = 0.65f - 0.002f * dT;                // VBE спадає 2 мВ/°C

        // Схема А: Ib зафіксований → Ic просто слідує за β
        float IcA = beta * Ib_fixed;

        // Схема Б: подільник тримає Vbb, RE гальмує.
        // Ic·RE + Vbe ≈ Vbb  →  Ic ≈ (Vbb − Vbe) / RE  (струм бази нехтуємо)
        float IcB = (Vbb - Vbe) / RE;

        printf("T=%2.0f C:  схема А Ic = %.2f мА   схема Б Ic = %.2f мА\n",
               T[k], IcA * 1000.0f, IcB * 1000.0f);
    }
    return 0;
}
