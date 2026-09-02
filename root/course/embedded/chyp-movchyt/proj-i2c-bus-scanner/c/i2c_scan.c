#include "i2c_scan.h"

#include <stdio.h>

i2c_scan_report_t i2c_scan_range(void) {
    i2c_scan_report_t report;
    uint8_t addr;

    report.found_count = 0;
    report.nack_count = 0;
    report.error_count = 0;
    report.last_error = I2C_OK;

    printf("Сканування 0x%02X..0x%02X...\n", I2C_FIRST_ADDR, I2C_LAST_ADDR);

    for (addr = I2C_FIRST_ADDR; addr <= I2C_LAST_ADDR; ++addr) {
        i2c_status_t st = i2c_probe(addr);

        if (st == I2C_OK) {
            report.found[report.found_count++] = addr;
            printf("  ACK: 7-бітна адреса 0x%02X (байт запису 0x%02X, байт читання 0x%02X)\n",
                   addr, (uint8_t)(addr << 1), (uint8_t)((addr << 1) | 1u));
        } else if (st == I2C_NACK) {
            report.nack_count++;
        } else {
            report.error_count++;
            report.last_error = st;
        }
    }

    printf("Підсумок: вузлів %u, NACK %u, помилок шини %u\n",
           (unsigned)report.found_count, (unsigned)report.nack_count, (unsigned)report.error_count);
    return report;
}

i2c_verdict_t i2c_classify(const i2c_scan_report_t *report, uint8_t expected_addr) {
    uint8_t i;

    /* Сто дванадцять "пристроїв" — це не сто дванадцять мікросхем, а нуль на SDA:
       апаратний блок читає притиснуту лінію на дев'ятому такті як ACK. */
    if (report->found_count >= I2C_ADDR_SPACE) {
        return VERDICT_PHANTOM_ALL_ACK;
    }
    if (report->found_count == 0 && report->error_count > 0) {
        return VERDICT_LINES_BROKEN;
    }
    if (report->found_count == 0) {
        return VERDICT_SILENT_BUT_HEALTHY;
    }
    for (i = 0; i < report->found_count; ++i) {
        if (report->found[i] == expected_addr) {
            return VERDICT_DEVICE_AS_EXPECTED;
        }
    }
    return VERDICT_ADDRESS_MISMATCH;
}

static const char *verdict_advice(i2c_verdict_t verdict) {
    switch (verdict) {
    case VERDICT_DEVICE_AS_EXPECTED:
        return "Шина справна, вузол відповідає за очікуваною адресою.\n"
               "  Далі має сенс читати регістр ідентифікації (WHO_AM_I).";
    case VERDICT_ADDRESS_MISMATCH:
        return "Пристрій на шині є, але не за тією адресою, яку обіцяв даташит.\n"
               "  Перевір потенціал на виводі AD0 / ADDR: підтяжка до живлення замість землі\n"
               "  або взагалі непідключений вивід, що ловить потенціал сусідньої доріжки.";
    case VERDICT_PHANTOM_ALL_ACK:
        return "Відповіли всі адреси діапазону — стільки мікросхем на платі немає.\n"
               "  SDA притиснута до землі: коротке замикання, пробитий захисний діод\n"
               "  або зависла мікросхема, яку не витягли дев'ять тактів відновлення.";
    case VERDICT_SILENT_BUT_HEALTHY:
        return "Лінії електрично здорові (підтяжки є, такти проходять), але не відповів ніхто.\n"
               "  Перевір V_DD на веденому чіпі, рівень на nRST (він active-low)\n"
               "  і чи не переплутані SDA та SCL між мікроконтролером і модулем.";
    case VERDICT_LINES_BROKEN:
        return "Транзакції не починаються взагалі: лінії не виходять у високий рівень.\n"
               "  Найімовірніше немає резисторів підтяжки (типово 4.7 кОм до V_DD)\n"
               "  або на шину не подано живлення.";
    }
    return "невідомий вердикт";
}

static uint8_t bit_count(uint8_t value) {
    uint8_t bits = 0;

    while (value != 0u) {
        bits += (uint8_t)(value & 1u);
        value >>= 1;
    }
    return bits;
}

void i2c_print_report(const i2c_scan_report_t *report, uint8_t expected_addr, i2c_verdict_t verdict) {
    uint8_t i;

    if (report->error_count > 0) {
        printf("Остання помилка шини: %s\n", i2c_status_text(report->last_error));
    }
    printf("Вердикт:\n  %s\n", verdict_advice(verdict));

    if (verdict == VERDICT_ADDRESS_MISMATCH) {
        for (i = 0; i < report->found_count; ++i) {
            uint8_t diff = (uint8_t)(report->found[i] ^ expected_addr);

            /* Один-два різні біти в молодшій частині — це майже завжди
               адресні перемички AD0/AD1, а не інша мікросхема. */
            if (bit_count(diff) <= 2u && diff < 0x08u) {
                printf("  0x%02X відрізняється від очікуваної 0x%02X лише молодшими бітами"
                       " — дивись адресні перемички.\n",
                       report->found[i], expected_addr);
            }
        }
    }
}
