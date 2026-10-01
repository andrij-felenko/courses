#ifndef CSV_PARSER_H
#define CSV_PARSER_H

#include <stddef.h>
#include <stdbool.h>

// Максимальна довжина шляху до файла або текстового рядка
#define MAX_LINE_LEN 256
#define MAX_SAMPLES 4096

// Структура точкового вимірювання сигналів двох каналів (CH1 - вхід, CH2 - вихід)
typedef struct {
    double time_sec;     // Часова позначка від початку кадру (секунди)
    double ch1_volts;    // Напруга каналу CH1 (Вхід, В)
    double ch2_volts;    // Напруга каналу CH2 (Вихід, В)
} WaveformPoint;

// Структура характеристики одного вимірювання АЧХ на заданій частоті
typedef struct {
    double frequency_hz; // Частота тестового сигналу DDS (Гц)
    double v_pp_in;      // Піковий розмах вхідного сигналу (В)
    double v_pp_out;     // Піковий розмах вихідного сигналу (В)
    double gain_db;      // Розрахований коефіцієнт підсилення в дБ: 20 * log10(V_out / V_in)
} BodePoint;

// Зчитування CSV-файлу експорту FNIRSI 2C53T
// Повертає кількість зчитаних точок або -1 у разі помилки відкриття/розбору
int parse_waveform_csv(const char *filepath, WaveformPoint *out_points, size_t max_points);

// Обчислення пікового розмаху V_pp (різниця між максимум і мінімум)
double calculate_peak_to_peak(const double *volts_array, size_t count);

// Обчислення підсилення в децибелах (20 * log10(v_out / v_in))
double compute_gain_db(double v_in, double v_out);

// Автоматичний пошук частоти зрізу АЧХ за рівнем -3 дБ
// Повертає true, якщо частоту зрізу знайдено в масиві точок BodePoint
bool find_cutoff_frequency(const BodePoint *bode_points, size_t count, double *out_cutoff_hz);

#endif // CSV_PARSER_H
