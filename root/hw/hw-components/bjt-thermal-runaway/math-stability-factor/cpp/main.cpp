// Повний температурний дрейф колекторного струму через три чинники стійкості.
// Порівнюємо фіксований струм бази (RE=0) з жорстким подільником (RB мале, RE є).
// ΔIc = S·ΔICO + S_VBE·ΔVBE + S_β·Δβ  — повний диференціал рівняння кола.
// Знаменник кола den = RB + (β+1)·RE  — саме (β+1)·RE, а не β·RE (точний Ie).
#include <stdio.h>
#include <math.h>

// Один чинник-розрахунок для заданих RB, RE
static void drift(const char *name, float RB, float RE,
                  float beta, float Ic, float ICO, float dT) {
    float den   = RB + (beta + 1.0f) * RE;     // спільний знаменник кола

    // три чинники стійкості з виведення
    float S     = (beta + 1.0f) * (RB + RE) / den;      // за витоком
    float S_vbe = -beta / den;                          // за порогом (А/В)
    float S_b   = Ic * (RB + RE) / (beta * den);        // за β (наближено, А/од.)

    // три теплові поштовхи за нагрів dT
    float dICO  = ICO * (powf(2.0f, dT / 10.0f) - 1.0f);   // витік подвоюється/10°C
    float dVBE  = -0.002f * dT;                            // −2 мВ/°C
    float dBeta = beta * 0.008f * dT;                      // β росте 0.8 %/°C

    // три внески й сума
    float dIc_ico = S     * dICO;
    float dIc_vbe = S_vbe * dVBE;
    float dIc_b   = S_b   * dBeta;
    float dIc     = dIc_ico + dIc_vbe + dIc_b;

    printf("%s:  S=%.1f  S_VBE=%.4f A/B  S_b=%.2e A/od.\n", name, S, S_vbe, S_b);
    printf("   dIc(вит)=%.3f  dIc(VBE)=%.3f  dIc(b)=%.3f  ->  dIc=%.3f мА (%.0f%%)\n\n",
           dIc_ico*1e3f, dIc_vbe*1e3f, dIc_b*1e3f, dIc*1e3f, 100.0f*dIc/Ic);
}

int main(void) {
    const float beta = 150.0f;     // β при 25 °C
    const float Ic   = 0.002f;     // робочий струм 2 мА
    const float ICO  = 50e-9f;     // витік 50 нА при 25 °C
    const float dT   = 50.0f;      // нагрів на 50 °C

    // Схема А: фіксований струм бази — RE=0, базовий резистор великий
    drift("Схема А (фікс. Ib)", 100000.0f, 0.0f, beta, Ic, ICO, dT);
    // Схема Б: жорсткий подільник + RE — RB мале (паралель), RE = 470 Ом
    drift("Схема Б (подільник+RE)", 4700.0f, 470.0f, beta, Ic, ICO, dT);
    return 0;
}
