#include <stdio.h>
#include <stdint.h>

void log_telemetry_c(uint32_t timestamp, float current, float voltage) {
    char buffer[64];
    /* Безпечне форматування у фіксований стек-буфер */
    int len = snprintf(buffer, sizeof(buffer), "[%lu ms] I=%.2f A, U=%.2f V\r\n", 
                       (unsigned long)timestamp, (double)current, (double)voltage);
    if (len > 0) {
        /* Прямий вивід у дескриптор stdout */
        fwrite(buffer, 1, (size_t)len, stdout);
    }
}
