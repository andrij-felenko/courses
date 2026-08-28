#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <time.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Номінальні рівні напруги PAM4: L0=-3, L1=-1, L2=+1, L3=+3
static const double PAM4_LEVELS[4] = { -3.0, -1.0, 1.0, 3.0 };

// Таблиці перетворення бітів (значення 0..3) у номер рівня L0..L3 (0..3)
// Код Грея: 00(0)->L0(0), 01(1)->L1(1), 10(2)->L3(3), 11(3)->L2(2)
static const uint8_t GRAY_MAP[4] = { 0, 1, 3, 2 };
// Зворотне перетворення Грея: індекс рівня L0..L3 -> вихідні біти
static const uint8_t GRAY_DEMAP[4] = { 0, 1, 3, 2 };

// Натуральний двійковий код: 00->0, 01->1, 10->2, 11->3
static const uint8_t BINARY_MAP[4] = { 0, 1, 2, 3 };
static const uint8_t BINARY_DEMAP[4] = { 0, 1, 2, 3 };

// Генератор гаусового білого шуму методом Бокса-Мюллера
static double generate_gaussian_noise(double std_dev)
{
    double u1 = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    double u2 = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    double z0 = sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
    return z0 * std_dev;
}

// Трипороговий компаратор (слайсер): розбиває неперервну напругу на 4 дискретні рівні
static uint8_t pam4_slice_level(double voltage)
{
    if (voltage < -2.0) return 0; // L0 (-3.0 В)
    if (voltage < 0.0)  return 1; // L1 (-1.0 В)
    if (voltage < 2.0)  return 2; // L2 (+1.0 В)
    return 3;                     // L3 (+3.0 В)
}

// Підрахунок відстані Геммінга (кількості бітових відмінностей) між двома числами
static uint32_t calculate_bit_errors(uint8_t a, uint8_t b)
{
    uint8_t diff = a ^ b;
    uint32_t count = 0;
    while (diff > 0) {
        count += (diff & 1);
        diff >>= 1;
    }
    return count;
}

// Структура для накопичення статистики випробувань
typedef struct {
    double snr_db;
    uint64_t total_symbols;
    uint64_t sym_errors_gray;
    uint64_t bit_errors_gray;
    uint64_t sym_errors_bin;
    uint64_t bit_errors_bin;
} SimulationResult;

// Прогін симуляції для заданого відношення сигнал/шум
static SimulationResult run_pam4_monte_carlo(double snr_db, uint64_t num_symbols)
{
    SimulationResult res = { 0 };
    res.snr_db = snr_db;
    res.total_symbols = num_symbols;

    // Середня енергія символу Es = (9 + 1 + 1 + 9)/4 = 5.0 В^2
    const double es = 5.0;
    double snr_linear = pow(10.0, snr_db / 10.0);
    double noise_sigma = sqrt(es / (2.0 * snr_linear));

    for (uint64_t i = 0; i < num_symbols; ++i) {
        // Генеруємо 2 випадкові інформаційні біти (значення від 0 до 3)
        uint8_t tx_bits = (uint8_t)(rand() % 4);

        // 1. Модуляція та передача кодом Грея
        uint8_t level_idx_gray = GRAY_MAP[tx_bits];
        double tx_volts_gray = PAM4_LEVELS[level_idx_gray];
        double rx_volts_gray = tx_volts_gray + generate_gaussian_noise(noise_sigma);
        uint8_t rx_level_gray = pam4_slice_level(rx_volts_gray);
        uint8_t rx_bits_gray = GRAY_DEMAP[rx_level_gray];

        if (rx_level_gray != level_idx_gray) {
            res.sym_errors_gray++;
            res.bit_errors_gray += calculate_bit_errors(tx_bits, rx_bits_gray);
        }

        // 2. Модуляція та передача натуральним двійковим кодом
        uint8_t level_idx_bin = BINARY_MAP[tx_bits];
        double tx_volts_bin = PAM4_LEVELS[level_idx_bin];
        double rx_volts_bin = tx_volts_bin + generate_gaussian_noise(noise_sigma);
        uint8_t rx_level_bin = pam4_slice_level(rx_volts_bin);
        uint8_t rx_bits_bin = BINARY_DEMAP[rx_level_bin];

        if (rx_level_bin != level_idx_bin) {
            res.sym_errors_bin++;
            res.bit_errors_bin += calculate_bit_errors(tx_bits, rx_bits_bin);
        }
    }

    return res;
}

int main(void)
{
    srand((unsigned int)time(NULL));

    const uint64_t SYMBOL_COUNT = 2000000; // 2 мільйони символів (4 мільйони бітів)
    const double SNR_POINTS[] = { 10.0, 12.0, 14.0, 16.0, 18.0, 20.0 };
    const size_t NUM_POINTS = sizeof(SNR_POINTS) / sizeof(SNR_POINTS[0]);

    printf("=== Симуляція тракту PAM4 SerDes у каналі AWGN ===\n");
    printf("Обсяг вибірки на точку: %llu символів (4.00 млн бітів)\n\n", (unsigned long long)SYMBOL_COUNT);
    printf(" SNR(дБ) | SER (Gray)  | BER (Gray)  | BER (Binary)| Співвідношення BER_Bin/BER_Gray\n");
    printf("---------+-------------+-------------+-------------+--------------------------------\n");

    for (size_t i = 0; i < NUM_POINTS; ++i) {
        SimulationResult r = run_pam4_monte_carlo(SNR_POINTS[i], SYMBOL_COUNT);

        double ser_gray = (double)r.sym_errors_gray / (double)r.total_symbols;
        double ber_gray = (double)r.bit_errors_gray / (double)(2 * r.total_symbols);
        double ber_bin  = (double)r.bit_errors_bin  / (double)(2 * r.total_symbols);
        double ratio = (ber_gray > 0.0) ? (ber_bin / ber_gray) : 1.0;

        printf(" %6.1f  | %11.4e | %11.4e | %11.4e |            %6.3f\n",
               r.snr_db, ser_gray, ber_gray, ber_bin, ratio);
    }

    return 0;
}
