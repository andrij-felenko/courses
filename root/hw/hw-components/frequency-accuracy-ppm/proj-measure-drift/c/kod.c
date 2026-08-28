#include <stdint.h>

#define F_NOMINAL 16000000UL    // паспортний номінал кварцу, Гц

// Вільний 32-розрядний таймер тактується власним кварцом; вхід 1 PPS
// заведено на канал input capture, тож лічильник фіксується АПАРАТНО
// по фронту опорної секунди — обробник лише читає готовий регістр.
volatile uint32_t g_capture;     // останнє апаратно захоплене значення таймера
volatile uint32_t g_pps_count;   // лічильник опорних секунд (фронтів 1 PPS)

void TIMER_CAPTURE_IRQ(void)     // переривання по фронту 1 PPS
{
    g_capture = TIM_CCR;         // зафіксоване залізом значення лічильника
    g_pps_count++;
}

// Метод A — частота кварцу, усереднена за вікно gate_seconds опорних секунд.
double measure_ppm_gated(uint32_t gate_seconds)
{
    uint32_t t0 = g_pps_count;
    while (g_pps_count == t0) { }            // дочекатися першого фронту 1 PPS
    uint32_t n_start = g_capture;            // такти на початку вікна
    uint32_t t_start = g_pps_count;

    while (g_pps_count - t_start < gate_seconds) { }   // рівно gate_seconds секунд
    uint32_t n_end = g_capture;              // такти в кінці вікна

    // Беззнакове віднімання коректно переступає ОДНЕ переповнення лічильника.
    uint32_t dN = n_end - n_start;

    double f_meas = (double)dN / gate_seconds;              // Гц, усереднено
    return (f_meas - (double)F_NOMINAL) / F_NOMINAL * 1e6;  // ppm
}
