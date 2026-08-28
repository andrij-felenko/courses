#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include <signal.h>
#include <unistd.h>
#include <errno.h>
#include <sys/timex.h>

#define SECONDS_PER_DAY 86400.0
#define PI 3.14159265358979323846
#define LOOP_INTERVAL_NS 500000000L // 500 мілісекунд

static volatile sig_atomic_t g_running = 1;

// Обробник сигналів завершення для безпечного виходу
static void handle_signal(int sig) {
    (void)sig;
    g_running = 0;
}

// Повернення зміщення частоти ядра в 0
static void reset_frequency(void) {
    struct timex tx;
    memset(&tx, 0, sizeof(tx));
    tx.modes = ADJ_FREQUENCY;
    tx.freq = 0;
    if (adjtimex(&tx) < 0) {
        perror("Помилка скидання частоти в adjtimex");
    } else {
        printf("\n[Система] Частоту годинника успішно відновлено до номіналу.\n");
    }
}

// Розрахунок поточної поправки частоти в ppm
static double compute_smear_ppm(double elapsed_sec, double total_window_sec, 
                                double leap_sec, bool use_cosine) {
    if (elapsed_sec < 0.0 || elapsed_sec >= total_window_sec) {
        return 0.0;
    }
    if (!use_cosine) {
        // Лінійний профіль: y = - ΔΦ / T
        return - (leap_sec / total_window_sec) * 1e6;
    } else {
        // Косинусний профіль: y = - (ΔΦ / T) * (1 - cos(2*pi*t / T))
        double factor = 1.0 - cos(2.0 * PI * elapsed_sec / total_window_sec);
        return - (leap_sec / total_window_sec) * factor * 1e6;
    }
}

int main(int argc, char **argv) {
    bool use_cosine = true;
    double duration_sec = 86400.0; // 24 години
    double leap_sec = 1.0;         // +1 секунда

    if (argc > 1 && strcmp(argv[1], "--linear") == 0) {
        use_cosine = false;
    }

    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_signal;
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    printf("=== Демон розмазування високосної секунди (Linux C) ===\n");
    printf("Профіль: %s\n", use_cosine ? "Гладкий піднесений косинус (Google Smooth)" : "Лінійний (Linear)");
    printf("Тривалість вікна: %.0f секунд (24 год)\n", duration_sec);
    printf("Величина корекції: %+.1f с\n\n", leap_sec);

    struct timespec start_ts, next_wakeup;
    clock_gettime(CLOCK_MONOTONIC, &start_ts);
    next_wakeup = start_ts;

    while (g_running) {
        struct timespec now_ts;
        clock_gettime(CLOCK_MONOTONIC, &now_ts);

        double elapsed = (double)(now_ts.tv_sec - start_ts.tv_sec) +
                         (double)(now_ts.tv_nsec - start_ts.tv_nsec) * 1e-9;

        if (elapsed >= duration_sec) {
            printf("\nВікно розмазування повністю вичерпано.\n");
            break;
        }

        double ppm = compute_smear_ppm(elapsed, duration_sec, leap_sec, use_cosine);
        long raw_freq = (long)(ppm * 65536.0);

        struct timex tx;
        memset(&tx, 0, sizeof(tx));
        tx.modes = ADJ_FREQUENCY;
        tx.freq = raw_freq;

        if (adjtimex(&tx) < 0) {
            if (errno == EPERM) {
                fprintf(stderr, "Помилка: потрібні права CAP_SYS_TIME (sudo) для керування частотою ядра!\n");
                return EXIT_FAILURE;
            }
            perror("Помилка виклику adjtimex");
            break;
        }

        printf("\rЧас: %6.1f с / %6.0f с | Поправка: %8.4f ppm (raw: %10ld) | Статус: 0x%04x",
               elapsed, duration_sec, ppm, raw_freq, tx.status);
        fflush(stdout);

        // Розраховуємо абсолютний час наступного пробудження без дрейфу
        next_wakeup.tv_nsec += LOOP_INTERVAL_NS;
        if (next_wakeup.tv_nsec >= 1000000000L) {
            next_wakeup.tv_sec += 1;
            next_wakeup.tv_nsec -= 1000000000L;
        }
        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next_wakeup, NULL);
    }

    reset_frequency();
    return EXIT_SUCCESS;
}
