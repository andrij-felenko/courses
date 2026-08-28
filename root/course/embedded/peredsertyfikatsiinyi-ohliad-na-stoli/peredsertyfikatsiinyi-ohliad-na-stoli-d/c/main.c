#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define MAX_BINS 1024
#define MAX_PEAKS 64
#define MAX_SOURCES 8

typedef struct {
    double freq_hz;
    double power_dbm;
} SpectrumBin;

typedef struct {
    double freq_hz;
    double power_dbm;
    double delta_over_floor_db;
    const char* matched_source;
    int harmonic_order;
} DetectedPeak;

typedef struct {
    const char* name;
    double fund_freq_hz;
    double tolerance_hz;
} KnownSource;

/* Знаходження ковзної підлоги шуму та локальних піків */
int detect_emc_peaks(const SpectrumBin* bins, int num_bins,
                     int window_half_width, double threshold_delta_db,
                     const KnownSource* sources, int num_sources,
                     DetectedPeak* out_peaks, int max_out_peaks) {
    int peak_count = 0;

    for (int i = window_half_width; i < num_bins - window_half_width; ++i) {
        /* Локальний максимум: точка вища за найближчих сусідів */
        if (bins[i].power_dbm <= bins[i - 1].power_dbm ||
            bins[i].power_dbm <= bins[i + 1].power_dbm) {
            continue;
        }

        /* Обчислення локального середнього рівня шуму навколо піку */
        double sum_power = 0.0;
        int count = 0;
        for (int w = -window_half_width; w <= window_half_width; ++w) {
            if (w >= -1 && w <= 1) continue; /* пропускаємо саму вершину */
            sum_power += bins[i + w].power_dbm;
            count++;
        }
        double local_floor = (count > 0) ? (sum_power / count) : bins[i].power_dbm;
        double delta = bins[i].power_dbm - local_floor;

        if (delta >= threshold_delta_db) {
            if (peak_count >= max_out_peaks) break;

            DetectedPeak* p = &out_peaks[peak_count++];
            p->freq_hz = bins[i].freq_hz;
            p->power_dbm = bins[i].power_dbm;
            p->delta_over_floor_db = delta;
            p->matched_source = "Невідоме джерело";
            p->harmonic_order = 0;

            /* Ідентифікація за гармонійними сітками */
            for (int s = 0; s < num_sources; ++s) {
                double ratio = p->freq_hz / sources[s].fund_freq_hz;
                int n = (int)(ratio + 0.5);
                if (n >= 1) {
                    double expected_freq = n * sources[s].fund_freq_hz;
                    if (fabs(p->freq_hz - expected_freq) <= sources[s].tolerance_hz) {
                        p->matched_source = sources[s].name;
                        p->harmonic_order = n;
                        break;
                    }
                }
            }
        }
    }
    return peak_count;
}
