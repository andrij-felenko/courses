#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <errno.h>
#include <sys/timex.h>

static int64_t ts_to_ns(const struct timespec *ts) {
    return (int64_t)ts->tv_sec * 1000000000LL + ts->tv_nsec;
}

static void print_status_flags(int status) {
    printf("  Прапорці стану (status=0x%04X):\n", status);
    if (status & STA_PLL)       printf("    [+] STA_PLL       (контур фазового автопідстроювання активний)\n");
    if (status & STA_FLL)       printf("    [+] STA_FLL       (контур частотного автопідстроювання активний)\n");
    if (status & STA_UNSYNC)    printf("    [!] STA_UNSYNC    (ГОДИННИК НЕ СИНХРОНІЗОВАНО! Запис у RTC вимкнено)\n");
    if (status & STA_PPSSIGNAL) printf("    [+] STA_PPSSIGNAL (сигнал точного часу PPS виявлено)\n");
    if (status & STA_NANO)      printf("    [+] STA_NANO      (роздільність зсуву в наносекундах)\n");
    if (status & STA_INS)       printf("    [!] STA_INS       (заплановано додавання секунди координації)\n");
    if (status & STA_DEL)       printf("    [!] STA_DEL       (заплановано віднімання секунди координації)\n");
}

static void decode_adjtimex_state(void) {
    struct timex tx;
    memset(&tx, 0, sizeof(tx));
    tx.modes = 0; // Режим лише для зчитування

    int state = adjtimex(&tx);
    if (state == -1) {
        perror("adjtimex");
        return;
    }

    printf("=== СТАН ЯДЕРНОГО СИНХРОНІЗАТОРА TIMEKEEPING ===\n");
    printf("  Код повернення Leap State : %d ", state);
    switch (state) {
        case TIME_OK:    printf("(TIME_OK: час синхронізовано)\n"); break;
        case TIME_INS:   printf("(TIME_INS: вставка leap second)\n"); break;
        case TIME_DEL:   printf("(TIME_DEL: видалення leap second)\n"); break;
        case TIME_OOP:   printf("(TIME_OOP: leap second у процесі)\n"); break;
        case TIME_WAIT:  printf("(TIME_WAIT: leap second завершено)\n"); break;
        case TIME_ERROR: printf("(TIME_ERROR: помилка синхронізації / STA_UNSYNC)\n"); break;
        default:         printf("(невідомий стан)\n"); break;
    }

    // tx.freq зберігається у масштабі 2^16 = 65536 на 1 ppm
    double freq_ppm = (double)tx.freq / 65536.0;
    double max_err_ms = (double)tx.maxerror / 1000.0;
    double est_err_ms = (double)tx.esterror / 1000.0;

    printf("  Частотна корекція (freq)  : %.4f ppm (сире значення: %ld)\n", freq_ppm, tx.freq);
    printf("  Фазовий зсув (offset)     : %ld %s\n", tx.offset, (tx.status & STA_NANO) ? "нс" : "мкс");
    printf("  Максимальна похибка       : %.3f мс\n", max_err_ms);
    printf("  Оцінена похибка           : %.3f мс\n", est_err_ms);
    printf("  Постійна часу контуру PLL : %ld\n", tx.constant);
    printf("  Тривалість тика ядра      : %ld мкс\n", tx.tick);

    print_status_flags(tx.status);
}

static void sample_clock_divergence(void) {
    struct timespec ts_real, ts_mono, ts_raw, ts_boot;

    clock_gettime(CLOCK_REALTIME, &ts_real);
    clock_gettime(CLOCK_MONOTONIC, &ts_mono);
    clock_gettime(CLOCK_MONOTONIC_RAW, &ts_raw);
    clock_gettime(CLOCK_BOOTTIME, &ts_boot);

    int64_t ns_real = ts_to_ns(&ts_real);
    int64_t ns_mono = ts_to_ns(&ts_mono);
    int64_t ns_raw  = ts_to_ns(&ts_raw);
    int64_t ns_boot = ts_to_ns(&ts_boot);

    printf("\n=== ЗРІЗ СИСТЕМНИХ ГОДИННИКІВ ===\n");
    printf("  CLOCK_REALTIME      : %lld.%09ld с\n", (long long)ts_real.tv_sec, ts_real.tv_nsec);
    printf("  CLOCK_MONOTONIC     : %lld.%09ld с\n", (long long)ts_mono.tv_sec, ts_mono.tv_nsec);
    printf("  CLOCK_MONOTONIC_RAW : %lld.%09ld с\n", (long long)ts_raw.tv_sec, ts_raw.tv_nsec);
    printf("  CLOCK_BOOTTIME      : %lld.%09ld с\n", (long long)ts_boot.tv_sec, ts_boot.tv_nsec);

    int64_t raw_vs_mono = ns_mono - ns_raw;
    int64_t boot_vs_mono = ns_boot - ns_mono;

    printf("  Різниця NTP Slew (MONO - RAW)     : %+lld нс (%+.3f мс)\n",
           (long long)raw_vs_mono, (double)raw_vs_mono / 1000000.0);
    printf("  Час у сні/гібернації (BOOT - MONO): %+lld нс (%+.3f с)\n",
           (long long)boot_vs_mono, (double)boot_vs_mono / 1000000000.0);
}

int main(int argc, char **argv) {
    int duration_sec = 2;
    if (argc > 1) {
        duration_sec = atoi(argv[1]);
        if (duration_sec < 1) duration_sec = 1;
    }

    decode_adjtimex_state();
    sample_clock_divergence();

    printf("\n=== ВИМІРЮВАННЯ ВЛАСНОГО АПАРАТНОГО ДРЕЙФУ (%d с) ===\n", duration_sec);
    struct timespec mono_start, raw_start;
    clock_gettime(CLOCK_MONOTONIC, &mono_start);
    clock_gettime(CLOCK_MONOTONIC_RAW, &raw_start);

    sleep((unsigned int)duration_sec);

    struct timespec mono_end, raw_end;
    clock_gettime(CLOCK_MONOTONIC, &mono_end);
    clock_gettime(CLOCK_MONOTONIC_RAW, &raw_end);

    int64_t d_mono = ts_to_ns(&mono_end) - ts_to_ns(&mono_start);
    int64_t d_raw  = ts_to_ns(&raw_end) - ts_to_ns(&raw_start);

    int64_t drift_ns = d_mono - d_raw;
    double drift_ppm = ((double)drift_ns / (double)d_raw) * 1e6;

    printf("  Тривалість за CLOCK_MONOTONIC     : %.6f с\n", (double)d_mono / 1e9);
    printf("  Тривалість за CLOCK_MONOTONIC_RAW : %.6f с\n", (double)d_raw / 1e9);
    printf("  Накопичений зсув контуру NTP      : %+lld нс\n", (long long)drift_ns);
    printf("  Миттєва швидкість компенсації     : %+.4f ppm\n", drift_ppm);

    return 0;
}
