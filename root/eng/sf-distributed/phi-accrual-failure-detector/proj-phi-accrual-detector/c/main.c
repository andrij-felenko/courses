#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <time.h>

#define PHI_DEFAULT_WINDOW_SIZE 1000
#define PHI_DEFAULT_THRESHOLD 8.0
#define PHI_MIN_STD_DEV 0.05
#define PHI_ACCEPTABLE_PAUSE 0.0

typedef struct {
    double *history;
    size_t capacity;
    size_t size;
    size_t head;
    double sum;
    double sum_sq;
    double last_timestamp;
    double threshold;
    double min_std_dev;
} phi_detector_t;

static double get_monotonic_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

phi_detector_t *phi_detector_create(size_t window_size, double threshold, double min_std_dev) {
    phi_detector_t *d = (phi_detector_t *)malloc(sizeof(phi_detector_t));
    if (!d) return NULL;

    d->capacity = (window_size > 0) ? window_size : PHI_DEFAULT_WINDOW_SIZE;
    d->history = (double *)malloc(sizeof(double) * d->capacity);
    if (!d->history) {
        free(d);
        return NULL;
    }

    d->size = 0;
    d->head = 0;
    d->sum = 0.0;
    d->sum_sq = 0.0;
    d->last_timestamp = 0.0;
    d->threshold = (threshold > 0.0) ? threshold : PHI_DEFAULT_THRESHOLD;
    d->min_std_dev = (min_std_dev > 0.0) ? min_std_dev : PHI_MIN_STD_DEV;

    return d;
}

void phi_detector_destroy(phi_detector_t *d) {
    if (d) {
        free(d->history);
        free(d);
    }
}

void phi_detector_heartbeat(phi_detector_t *d, double now_sec) {
    if (now_sec <= 0.0) {
        now_sec = get_monotonic_time_sec();
    }

    if (d->last_timestamp > 0.0) {
        double interval = now_sec - d->last_timestamp;
        if (interval > 0.0) {
            if (d->size < d->capacity) {
                d->history[d->head] = interval;
                d->sum += interval;
                d->sum_sq += interval * interval;
                d->size++;
            } else {
                double old_val = d->history[d->head];
                d->sum = d->sum - old_val + interval;
                d->sum_sq = d->sum_sq - (old_val * old_val) + (interval * interval);
                d->history[d->head] = interval;
            }
            d->head = (d->head + 1) % d->capacity;
        }
    }

    d->last_timestamp = now_sec;
}

double phi_detector_compute_phi(const phi_detector_t *d, double now_sec) {
    if (d->last_timestamp <= 0.0) {
        return 0.0; // Немає жодного сигналу — вузол вважається доступним
    }

    if (now_sec <= 0.0) {
        now_sec = get_monotonic_time_sec();
    }

    double diff = now_sec - d->last_timestamp;
    if (diff <= 0.0) {
        return 0.0;
    }

    // Якщо накопичено менше 2 вибірок, використовуємо значення за замовчуванням
    double mean = 1.0;
    double std_dev = d->min_std_dev;

    if (d->size >= 2) {
        mean = d->sum / (double)d->size;
        double variance = (d->sum_sq / (double)d->size) - (mean * mean);
        if (variance < 0.0) variance = 0.0;
        std_dev = sqrt(variance);
        if (std_dev < d->min_std_dev) {
            std_dev = d->min_std_dev;
        }
    }

    double y = (diff - mean) / std_dev;
    double e = exp(-y * (1.5976 + 0.070566 * y * y));
    
    // Чисельно стійка апроксимація erfc / p_later
    double p_later;
    if (diff > mean) {
        p_later = e / (1.0 + e);
    } else {
        p_later = 1.0 - (1.0 / (1.0 + e));
    }

    if (p_later <= 0.0) {
        // Асимптотичний захист від зникнення порядку при гігантських затримках
        double z = (diff - mean) / (std_dev * 1.41421356237);
        if (z > 3.0) {
            return ((z * z + log(z) + 0.57236) / 2.302585) - 0.30103;
        }
        return 50.0; // Максимальний поріг при критичному перевищенні
    }

    double phi = -log10(p_later);
    return (phi < 0.0) ? 0.0 : phi;
}

bool phi_detector_is_available(const phi_detector_t *d, double now_sec) {
    return phi_detector_compute_phi(d, now_sec) < d->threshold;
}

int main(void) {
    phi_detector_t *det = phi_detector_create(1000, 8.0, 0.05);

    double t = 100.0;
    // Імітація регулярного пульсу (T = 1.0 с) з джиттером ±0.04 с
    for (int i = 0; i < 50; ++i) {
        double jitter = ((double)(i % 5) - 2.0) * 0.02;
        t += 1.0 + jitter;
        phi_detector_heartbeat(det, t);
    }

    printf("Поточний стан після регулярного пульсу:\n");
    printf("Час очікування 1.0с -> Phi = %.4f (Доступний: %s)\n",
           phi_detector_compute_phi(det, t + 1.0),
           phi_detector_is_available(det, t + 1.0) ? "ТАК" : "НІ");

    printf("Час очікування 1.5с -> Phi = %.4f (Доступний: %s)\n",
           phi_detector_compute_phi(det, t + 1.5),
           phi_detector_is_available(det, t + 1.5) ? "ТАК" : "НІ");

    printf("Час очікування 2.5с -> Phi = %.4f (Доступний: %s)\n",
           phi_detector_compute_phi(det, t + 2.5),
           phi_detector_is_available(det, t + 2.5) ? "ТАК" : "НІ");

    phi_detector_destroy(det);
    return 0;
}
