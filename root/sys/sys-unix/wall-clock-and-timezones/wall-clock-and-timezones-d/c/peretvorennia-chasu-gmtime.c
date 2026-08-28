#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <time.h>

int main(void) {
    time_t now = time(NULL);
    struct tm tm_utc, tm_local;

    gmtime_r(&now, &tm_utc);
    localtime_r(&now, &tm_local);

    char buf_utc[64], buf_local[64];
    strftime(buf_utc, sizeof(buf_utc), "%Y-%m-%d %H:%M:%S %Z", &tm_utc);
    strftime(buf_local, sizeof(buf_local), "%Y-%m-%d %H:%M:%S %Z (UTC%z)", &tm_local);

    printf("time_t          : %ld\n", (long)now);
    printf("UTC час         : %s\n", buf_utc);
    printf("Локальний час   : %s\n", buf_local);
    printf("Літній час (DST): %s\n", tm_local.tm_isdst > 0 ? "ТАК" : "НІ");
    return 0;
}
