#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define MAX_SPECTRUM_POINTS 2048

typedef enum {
    TEST_PASS = 0,
    FAIL_BAND_EDGE_LOW,
    FAIL_BAND_EDGE_HIGH,
    FAIL_RESTRICTED_BAND,
    FAIL_ETSI_SPURIOUS_SUB1G,
    FAIL_ETSI_SPURIOUS_ABOVE1G
} SpectrumTestStatus;

typedef struct {
    double freq_hz;
    double power_dbm;
} SpectrumPoint;

typedef struct {
    double fundamental_freq_hz;
    double fundamental_peak_dbm;
    double worst_band_edge_margin_db;
    double worst_spurious_freq_hz;
    double worst_spurious_power_dbm;
    SpectrumTestStatus status;
} ValidationReport;

/* Перевірка, чи потрапляє частота у смугу обмеженого використання FCC §15.205 */
static bool is_fcc_restricted_band(double f_hz) {
    if (f_hz >= 2310.0e6 && f_hz <= 2390.0e6) return true;
    if (f_hz >= 2483.5e6 && f_hz <= 2500.0e6) return true;
    if (f_hz >= 4800.0e6 && f_hz <= 4960.0e6) return true; // 2-га гармоніка
    if (f_hz >= 7200.0e6 && f_hz <= 7440.0e6) return true; // 3-тя гармоніка
    return false;
}

ValidationReport validate_spectrum(const SpectrumPoint* points, size_t count, double band_start_hz, double band_end_hz) {
    ValidationReport rep = {
        .fundamental_freq_hz = 0.0,
        .fundamental_peak_dbm = -1000.0,
        .worst_band_edge_margin_db = 1000.0,
        .worst_spurious_freq_hz = 0.0,
        .worst_spurious_power_dbm = -1000.0,
        .status = TEST_PASS
    };

    if (!points || count == 0) return rep;

    /* Крок 1: Пошук піку основної несучої частоти всередині робочої смуги */
    for (size_t i = 0; i < count; ++i) {
        if (points[i].freq_hz >= band_start_hz && points[i].freq_hz <= band_end_hz) {
            if (points[i].power_dbm > rep.fundamental_peak_dbm) {
                rep.fundamental_peak_dbm = points[i].power_dbm;
                rep.fundamental_freq_hz = points[i].freq_hz;
            }
        }
    }

    const double band_edge_limit_dbm = rep.fundamental_peak_dbm - 20.0; // ліміт 20 dBc

    /* Крок 2: Перевірка країв смуг, Restricted Bands та побічних випромінювань */
    for (size_t i = 0; i < count; ++i) {
        double f = points[i].freq_hz;
        double p = points[i].power_dbm;

        /* Ігноруємо сам активний робочий канал (In-Band) */
        if (f >= band_start_hz && f <= band_end_hz) {
            continue;
        }

        /* 2.1. Перевірка смуг обмеженого використання FCC Part 15.205 */
        if (is_fcc_restricted_band(f)) {
            const double fcc_restricted_limit_dbm = -41.2;
            if (p > fcc_restricted_limit_dbm) {
                rep.status = FAIL_RESTRICTED_BAND;
                rep.worst_spurious_freq_hz = f;
                rep.worst_spurious_power_dbm = p;
                return rep;
            }
        }

        /* 2.2. Перевірка безпосередніх країв смуги (Band Edges: спадання 20 dBc) */
        if ((f >= band_start_hz - 20.0e6 && f < band_start_hz) ||
            (f > band_end_hz && f <= band_end_hz + 20.0e6)) {
            double margin = band_edge_limit_dbm - p;
            if (margin < rep.worst_band_edge_margin_db) {
                rep.worst_band_edge_margin_db = margin;
            }
            if (p > band_edge_limit_dbm) {
                rep.status = (f < band_start_hz) ? FAIL_BAND_EDGE_LOW : FAIL_BAND_EDGE_HIGH;
                rep.worst_spurious_freq_hz = f;
                rep.worst_spurious_power_dbm = p;
                return rep;
            }
        }

        /* 2.3. Перевірка загальних побічних випромінювань за нормами ETSI EN 300 328 */
        if (f < 1.0e9) {
            if (p > -36.0) {
                rep.status = FAIL_ETSI_SPURIOUS_SUB1G;
                rep.worst_spurious_freq_hz = f;
                rep.worst_spurious_power_dbm = p;
                return rep;
            }
        } else {
            if (p > -30.0) {
                rep.status = FAIL_ETSI_SPURIOUS_ABOVE1G;
                rep.worst_spurious_freq_hz = f;
                rep.worst_spurious_power_dbm = p;
                return rep;
            }
        }

        /* Відстеження найвищого позасмугового піку */
        if (p > rep.worst_spurious_power_dbm) {
            rep.worst_spurious_power_dbm = p;
            rep.worst_spurious_freq_hz = f;
        }
    }

    return rep;
}
