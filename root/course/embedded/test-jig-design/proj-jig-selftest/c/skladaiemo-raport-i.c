#include <stdio.h>
#include <string.h>

// XOR усіх байтів у діапазоні [begin, end) — та сама сума, що в рядках NMEA.
static uint8_t xor_checksum(const char *begin, const char *end) {
    uint8_t cs = 0;
    for (const char *p = begin; p < end; p++) cs ^= (uint8_t)*p;
    return cs;
}

void build_and_send_report(const char *serial) {
    rails_t rails;
    read_rails(&rails);
    bool gpio_ok = check_all_loops();

    bool imu_ok, baro_ok;
    uint8_t imu_id  = sensor_probe(&sensors[0], &imu_ok);
    uint8_t baro_id = sensor_probe(&sensors[1], &baro_ok);
    (void)baro_ok;  // сам байт baro_id уже все скаже судді

    int16_t tempC_x10 = read_die_temperature_x10();  // температура кристала ×10

    char body[160];
    // Тіло — між '$RPT;' і '*'. Суму рахуємо саме від нього.
    int n = snprintf(body, sizeof(body),
        "$RPT;SN=%s;V33=%u;V5=%u;VREF=%u;GPIO=%s;IMU=0x%02X;BARO=0x%02X;TEMP=%d;*",
        serial,
        rails.v33_mv, rails.v5_mv, rails.vref_measured_mv,
        gpio_ok ? "OK" : "FAIL",
        imu_id, baro_id,
        tempC_x10);

    if (n < 0 || n >= (int)sizeof(body)) {
        uart_puts("$RPT;ERR=OVERFLOW\r\n");  // рядок не вліз — чесно скажи, не бреши
        return;
    }

    // XOR рахуємо від '$' до '*' включно з '*'? — ні, за конвенцією NMEA:
    // від першого символу ПІСЛЯ '$' до символу ПЕРЕД '*'. Знайдемо межі.
    const char *cs_begin = body + 1;                 // одразу після '$'
    const char *cs_end   = strchr(body, '*');        // до '*'
    uint8_t cs = xor_checksum(cs_begin, cs_end);

    uart_puts(body);
    char tail[8];
    snprintf(tail, sizeof(tail), "%02X\r\n", cs);
    uart_puts(tail);
}
