// Викликається апаратно на кожен готовий відлік АЦП (10 кГц).
#define DI_ARC_ADC  40          // поріг стрибка |I[n]-I[n-1]| у кодах АЦП

extern volatile uint32_t g_sum_sq;  // накопичувач для СКЗ (читає автомат)
extern volatile uint32_t g_n;

void ADC_IRQHandler(void) {
    uint16_t i_now = (uint16_t)ADC_DR;      // читання DR знімає прапорець EOC
    static uint16_t i_prev = 0;

    int32_t di = (int32_t)i_now - (int32_t)i_prev;
    if (di < 0) di = -di;

    // Дуга: різкий стрибок — стежимо всю HV-фазу (наростання + витримка).
    // Поріг: перевищення рівня — лише у витримці (сталій напрузі).
    if ((g_arc_armed   && di    > DI_ARC_ADC) ||
        (g_level_armed && i_now > g_i_limit)) {
        hv_off_hard();          // РОЗІРВАТИ HV негайно, прямо з ISR
        g_trip = 1;             // повідомити повільний автомат
    }

    // Накопичити квадрати для СКЗ витоку у витримці (потрібне для змінної проби):
    g_sum_sq += (uint32_t)i_now * i_now;
    g_n++;
    i_prev = i_now;
}
