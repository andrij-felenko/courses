#include "../include/csv_parser.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int parse_waveform_csv(const char *filepath, WaveformPoint *out_points, size_t max_points) {
    if (!filepath || !out_points || max_points == 0) {
        return -1;
    }

    FILE *file = fopen(filepath, "r");
    if (!file) {
        perror("Помилка відкриття CSV-файлу");
        return -1;
    }

    char line[MAX_LINE_LEN];
    size_t count = 0;

    // Пропуск заголовочного рядка CSV
    if (fgets(line, sizeof(line), file) == NULL) {
        fclose(file);
        return -1;
    }

    while (fgets(line, sizeof(line), file) != NULL && count < max_points) {
        line[strcspn(line, "\r\n")] = 0;
        if (strlen(line) == 0) {
            continue;
        }

        double t = 0.0, v1 = 0.0, v2 = 0.0;
        if (sscanf(line, "%lf,%lf,%lf", &t, &v1, &v2) == 3 ||
            sscanf(line, "%lf;%lf;%lf", &t, &v1, &v2) == 3) {
            out_points[count].time_sec = t;
            out_points[count].ch1_volts = v1;
            out_points[count].ch2_volts = v2;
            count++;
        }
    }

    fclose(file);
    return (int)count;
}

double calculate_peak_to_peak(const double *volts_array, size_t count) {
    if (!volts_array || count == 0) {
        return 0.0;
    }

    double min_v = volts_array[0];
    double max_v = volts_array[0];

    for (size_t i = 1; i < count; ++i) {
        if (volts_array[i] < min_v) {
            min_v = volts_array[i];
        }
        if (volts_array[i] > max_v) {
            max_v = volts_array[i];
        }
    }

    return (max_v - min_v);
}

double compute_gain_db(double v_in, double v_out) {
    if (v_in <= 1e-9) {
        return -100.0;
    }
    if (v_out <= 1e-9) {
        return -100.0;
    }
    return 20.0 * log10(v_out / v_in);
}

bool find_cutoff_frequency(const BodePoint *bode_points, size_t count, double *out_cutoff_hz) {
    if (!bode_points || count < 2 || !out_cutoff_hz) {
        return false;
    }

    double max_gain_db = bode_points[0].gain_db;
    for (size_t i = 1; i < count; ++i) {
        if (bode_points[i].gain_db > max_gain_db) {
            max_gain_db = bode_points[i].gain_db;
        }
    }

    double threshold_db = max_gain_db - 3.0;

    for (size_t i = 0; i < count - 1; ++i) {
        double g1 = bode_points[i].gain_db;
        double g2 = bode_points[i + 1].gain_db;

        if ((g1 >= threshold_db && g2 <= threshold_db) || 
            (g1 <= threshold_db && g2 >= threshold_db)) {
            
            double f1 = bode_points[i].frequency_hz;
            double f2 = bode_points[i + 1].frequency_hz;

            if (fabs(g2 - g1) > 1e-6) {
                *out_cutoff_hz = f1 + (threshold_db - g1) * (f2 - f1) / (g2 - g1);
            } else {
                *out_cutoff_hz = (f1 + f2) / 2.0;
            }
            return true;
        }
    }

    return false;
}
