#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

// Повний набір інтерпретованих даних моніторингу SFF-8472
typedef struct {
    float temperature_c;       // Температура модуля (°C)
    float vcc_volts;           // Напруга живлення VCC (В)
    float tx_bias_ma;          // Струм зміщення лазерного діода (мА)
    float tx_power_mw;         // Вихідна потужність передавача (мВт)
    float tx_power_dbm;        // Вихідна потужність передавача (дБм)
    float rx_power_mw;         // Вхідна потужність приймача (мВт)
    float rx_power_dbm;        // Вхідна потужність приймача (дБм)
    bool data_ready;           // Прапорець готовності АЦП (Byte 110 Bit 0)
    bool rx_los;               // Сигнал втрати оптичного сигналу RX LOS
    bool tx_fault;             // Сигнал апаратної аварії лазера TX Fault
} sff8472_telemetry_t;

// Декодування 10-байтового телеметричного блоку (реєстри 96..105)
// та статусних байтів (110, 112)
bool parse_sff8472_page_a2(const uint8_t page_a2_bytes[128], sff8472_telemetry_t *out) {
    if (!page_a2_bytes || !out) return false;

    // 1. Температура: 16-бітний int зі знаком (MSB=Byte 96, LSB=Byte 97)
    int16_t raw_temp = (int16_t)((page_a2_bytes[96] << 8) | page_a2_bytes[97]);
    out->temperature_c = (float)raw_temp / 256.0f;

    // 2. Напруга живлення VCC: 16-бітний uint (Byte 98, 99)
    uint16_t raw_vcc = (uint16_t)((page_a2_bytes[98] << 8) | page_a2_bytes[99]);
    out->vcc_volts = (float)raw_vcc / 10000.0f;

    // 3. Струм зміщення лазера: 16-бітний uint (Byte 100, 101)
    uint16_t raw_bias = (uint16_t)((page_a2_bytes[100] << 8) | page_a2_bytes[101]);
    out->tx_bias_ma = (float)raw_bias / 500.0f;

    // 4. Оптична потужність TX: 16-бітний uint (Byte 102, 103)
    uint16_t raw_tx = (uint16_t)((page_a2_bytes[102] << 8) | page_a2_bytes[103]);
    out->tx_power_mw = (float)raw_tx / 10000.0f;
    if (out->tx_power_mw > 0.00001f) {
        out->tx_power_dbm = 10.0f * log10f(out->tx_power_mw);
    } else {
        out->tx_power_dbm = -40.0f; // Відсутність генерації світла
    }

    // 5. Оптична потужність RX: 16-бітний uint (Byte 104, 105)
    uint16_t raw_rx = (uint16_t)((page_a2_bytes[104] << 8) | page_a2_bytes[105]);
    out->rx_power_mw = (float)raw_rx / 10000.0f;
    if (out->rx_power_mw > 0.00001f) {
        out->rx_power_dbm = 10.0f * log10f(out->rx_power_mw);
    } else {
        out->rx_power_dbm = -40.0f; // Відсутність оптичного сигналу (LOS)
    }

    // 6. Аналіз статусних прапорців у Байтах 110 та 112
    uint8_t status_byte_110 = page_a2_bytes[110];
    out->data_ready = (status_byte_110 & 0x01) == 0; // Bit 0 == 0 означає Data Ready

    uint8_t flags_byte_112 = page_a2_bytes[112];
    out->tx_fault = (flags_byte_112 & (1 << 2)) != 0; // Bit 2 — TX Fault Alarm
    out->rx_los   = (flags_byte_112 & (1 << 1)) != 0; // Bit 1 — RX LOS Alarm

    return true;
}

int main(void) {
    // Тестовий масив пам'яті A2h (128 байт), згенерований SFP+ 10G-LR модулем
    uint8_t page_a2[128] = {0};

    // Заповнюємо значення реального часу (Byte 96..105)
    page_a2[96] = 0x23; page_a2[97] = 0x00; // Temp = 35.0 °C
    page_a2[98] = 0x81, page_a2[99] = 0x48; // VCC  = 3.31 В
    page_a2[100] = 0x24; page_a2[101] = 0x40; // Bias = 18.5 мА
    page_a2[102] = 0x31; page_a2[103] = 0x34; // TX   = 1.26 мВт (+1.0 дБм)
    page_a2[104] = 0x00; page_a2[105] = 0xC8; // RX   = 0.02 мВт (-17.0 дБм)

    sff8472_telemetry_t dom;
    if (parse_sff8472_page_a2(page_a2, &dom)) {
        printf("=== ТЕЛЕМЕТРІЯ ОПТИЧНОГО ТРАНСИВЕРА (SFF-8472) ===\n");
        printf("Готовність датчиків: %s\n", dom.data_ready ? "ГОТОВО" : "ОНОВЛЕННЯ");
        printf("Температура модуля:  %.2f °C\n", dom.temperature_c);
        printf("Напруга живлення:    %.2f В\n", dom.vcc_volts);
        printf("Струм зміщення TX:   %.2f мА\n", dom.tx_bias_ma);
        printf("Вихідна потужність:  %.3f мВт (%.2f дБм)\n", dom.tx_power_mw, dom.tx_power_dbm);
        printf("Приймана потужність: %.4f мВт (%.2f дБм)\n", dom.rx_power_mw, dom.rx_power_dbm);
        printf("Статус RX LOS:       %s\n", dom.rx_los ? "АВАРІЯ (НЕМАЄ СВІТЛА)" : "НОРМА (СИГНАЛ Є)");
        printf("Статус TX Fault:     %s\n", dom.tx_fault ? "АВАРІЯ ЛАЗЕРА" : "НОРМА");
    }

    return 0;
}
