#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    double bus_capacitance_pf; // Ємність лінії, пФ
    double vdd_volts;          // Напруга живлення, В
    double frequency_hz;       // Тактова частота, Гц
    uint32_t bus_width_bits;   // Розрядність шини
} BusParams;

typedef struct {
    double power_raw_mw;       // Споживання сирої шини, мВт
    double power_encoded_mw;   // Споживання закодованої шини, мВт
    double savings_percent;    // Відсоток економії енергії
    double avg_activity_raw;   // Середній коефіцієнт активності сирої шини
    double avg_activity_enc;   // Середній коефіцієнт активності закодованої шини
} BusPowerResult;

BusPowerResult calculate_bus_power_budget(const BusParams* p, const uint32_t* stream, size_t count) {
    BusPowerResult r = {0.0, 0.0, 0.0, 0.0, 0.0};
    if (count < 2) return r;

    uint64_t raw_transitions = 0;
    uint64_t enc_transitions = 0;
    uint32_t prev_raw = stream[0];
    uint32_t prev_bus = stream[0];
    uint8_t prev_inv = 0;

    for (size_t i = 1; i < count; ++i) {
        uint32_t current = stream[i];

        // 1. Сирий перехід
        uint32_t diff_raw = current ^ prev_raw;
        raw_transitions += (uint64_t)__builtin_popcount(diff_raw);
        prev_raw = current;

        // 2. Bus Invert (побайтно для 4 байтів)
        for (int byte_idx = 0; byte_idx < 4; ++byte_idx) {
            uint8_t cur_byte = (uint8_t)((current >> (byte_idx * 8)) & 0xFF);
            uint8_t p_bus_byte = (uint8_t)((prev_bus >> (byte_idx * 8)) & 0xFF);
            
            uint32_t h = (uint32_t)__builtin_popcount(cur_byte ^ p_bus_byte);
            uint8_t enc_byte;
            uint8_t inv_bit;

            if (h > 4) {
                enc_byte = ~cur_byte;
                inv_bit = 1;
            } else {
                enc_byte = cur_byte;
                inv_bit = 0;
            }

            enc_transitions += (uint64_t)__builtin_popcount(enc_byte ^ p_bus_byte);
            uint8_t prev_inv_bit = (prev_inv >> byte_idx) & 1;
            enc_transitions += (uint64_t)(inv_bit ^ prev_inv_bit);

            prev_bus = (prev_bus & ~(0xFF << (byte_idx * 8))) | ((uint32_t)enc_byte << (byte_idx * 8));
            prev_inv = (prev_inv & ~(1 << byte_idx)) | (inv_bit << byte_idx);
        }
    }

    size_t total_cycles = count - 1;
    // P = (N_trans / N_cycles) * 0.5 * C * V^2 * f  (перехід 0->1 дає 0.5 від усіх змін станів)
    double energy_per_trans_j = 0.5 * (p->bus_capacitance_pf * 1e-12) * (p->vdd_volts * p->vdd_volts);

    r.avg_activity_raw = (double)raw_transitions / (double)(total_cycles * p->bus_width_bits);
    r.avg_activity_enc = (double)enc_transitions / (double)(total_cycles * (p->bus_width_bits + 4));

    r.power_raw_mw = ((double)raw_transitions / (double)total_cycles) * energy_per_trans_j * p->frequency_hz * 1e3;
    r.power_encoded_mw = ((double)enc_transitions / (double)total_cycles) * energy_per_trans_j * p->frequency_hz * 1e3;
    r.savings_percent = (1.0 - (r.power_encoded_mw / r.power_raw_mw)) * 100.0;

    return r;
}
