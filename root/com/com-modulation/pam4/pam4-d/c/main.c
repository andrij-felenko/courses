#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Номінальні напруги для 4 рівнів PAM4 (L0..L3)
static const double PAM4_VOLTAGE[4] = { -3.0, -1.0, 1.0, 3.0 };

// Таблиця кодування Грея: 2 вхідні біти (0..3) -> індекс рівня L0..L3
// 00 -> L0(-3), 01 -> L1(-1), 11 -> L2(+1), 10 -> L3(+3)
static const uint8_t GRAY_ENCODER[4] = { 0, 1, 3, 2 };

// Таблиця зворотного демапування: індекс рівня 0..3 -> 2 біти даних
static const uint8_t GRAY_DECODER[4] = { 0, 1, 3, 2 };

// Модулятор: перетворює 2 біти даних на аналогову напругу в лінії
double pam4_modulate_gray(uint8_t dibit)
{
    uint8_t level_index = GRAY_ENCODER[dibit & 0x03];
    return PAM4_VOLTAGE[level_index];
}

// Трипороговий слайсер приймача: квантує напругу на 4 дискретні рівні
uint8_t pam4_slice_voltage(double rx_voltage)
{
    // Поріг 0: -2.0 В (розділяє L0=-3 та L1=-1)
    if (rx_voltage < -2.0) return 0;
    // Поріг 1:  0.0 В (розділяє L1=-1 та L2=+1)
    if (rx_voltage < 0.0)  return 1;
    // Поріг 2: +2.0 В (розділяє L2=+1 та L3=+3)
    if (rx_voltage < 2.0)  return 2;
    // Напруга вище верхнього порогу -> рівень L3
    return 3;
}

// Демодулятор: відновлює 2 біти з квантованого рівня слайсера
uint8_t pam4_demodulate_gray(double rx_voltage)
{
    uint8_t sliced_level = pam4_slice_voltage(rx_voltage);
    return GRAY_DECODER[sliced_level];
}

// Генератор гаусового шуму з нульовим середнім та заданим стандартним відхиленням
double generate_awgn_noise(double sigma)
{
    double u1 = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    double u2 = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    return sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2) * sigma;
}

int main(void)
{
    // Тестова послідовність із чотирьох можливих дибітів
    const uint8_t test_dibits[4] = { 0x00, 0x01, 0x03, 0x02 }; // 00, 01, 11, 10
    const double noise_sigma = 0.35; // помірний шум

    printf("=== Демонстрація модулятора та слайсера PAM4 (C) ===\n\n");
    printf(" Вхідні біти | Рівень | Напруга TX | Напруга RX | Зчитано | Вихідні біти | Стан\n");
    printf("-------------+--------+------------+------------+---------+--------------+------\n");

    for (int i = 0; i < 4; ++i) {
        uint8_t tx_bits = test_dibits[i];
        double tx_v = pam4_modulate_gray(tx_bits);
        double rx_v = tx_v + generate_awgn_noise(noise_sigma);
        uint8_t rx_level = pam4_slice_voltage(rx_v);
        uint8_t rx_bits = GRAY_DECODER[rx_level];

        printf("   «%d%d» (%u)   |   L%u   |  %+6.2f В  |  %+6.2f В  |   L%u   |   «%d%d» (%u)   |  %s\n",
               (tx_bits >> 1) & 1, tx_bits & 1, tx_bits,
               GRAY_ENCODER[tx_bits], tx_v, rx_v, rx_level,
               (rx_bits >> 1) & 1, rx_bits & 1, rx_bits,
               (tx_bits == rx_bits) ? "OK" : "ПОМИЛКА");
    }

    return 0;
}
