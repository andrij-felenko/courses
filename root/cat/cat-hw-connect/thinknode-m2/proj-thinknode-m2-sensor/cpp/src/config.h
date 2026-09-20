#pragma once

#include <cstdint>

namespace config {
    // Піни підключення радіомодуля SX1262 до ESP32-S3 (приклад для типової плати)
    constexpr int pin_lora_cs   = 10;
    constexpr int pin_lora_dio1 = 15;
    constexpr int pin_lora_rst  = 14;
    constexpr int pin_lora_busy = 9;

    // Параметри радіоканалу LoRa
    constexpr float frequency_mhz = 868.0;
    constexpr int tx_power_dbm = 22;
    constexpr float bandwidth_khz = 125.0;
    constexpr int spreading_factor = 7;
    constexpr int coding_rate = 5;

    // Тривалість глибокого сну (у мікросекундах)
    constexpr uint64_t deep_sleep_duration_us = 60ULL * 1000000ULL; // 60 секунд
}
