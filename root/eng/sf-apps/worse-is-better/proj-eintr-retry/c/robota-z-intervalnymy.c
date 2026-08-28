#include <time.h>
#include <errno.h>

// Надійна затримка: досипає рівно залишок часу при перериванні
int sleep_exact_nanos(long sec, long nsec) {
    struct timespec req = { .tv_sec = sec, .tv_nsec = nsec };
    struct timespec rem = { 0, 0 };

    while (nanosleep(&req, &rem) == -1) {
        if (errno == EINTR) {
            // Оновлюємо запит залишком і продовжуємо сон
            req = rem;
            continue;
        }
        // Фатальна помилка (наприклад, некоректні параметри tv_nsec)
        return -1;
    }
    return 0;
}
