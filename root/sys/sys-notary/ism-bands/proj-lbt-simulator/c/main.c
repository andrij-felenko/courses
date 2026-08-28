#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

#define DUTY_CYCLE_LIMIT_MS 36000U  // 1% від 1 години (36 000 мс)
#define WINDOW_ONE_HOUR_MS   3600000U // 1 година в мілісекундах
#define RSSI_THRESHOLD_DBM   -85     // Поріг вільного каналу в dBm
#define LBT_SAMPLE_COUNT     5       // Кількість замірів RSSI

typedef struct {
    uint32_t total_tx_time_ms;
    uint32_t window_start_ms;
} duty_cycle_tracker_t;

// Ініціалізація трекера робочого циклу
void duty_cycle_init(duty_cycle_tracker_t *tracker, uint32_t current_time_ms) {
    tracker->total_tx_time_ms = 0;
    tracker->window_start_ms = current_time_ms;
}

// Оновлення часового вікна та перевірка доступності бюджету часу
bool duty_cycle_can_transmit(duty_cycle_tracker_t *tracker, uint32_t current_time_ms, uint32_t packet_toa_ms) {
    // Якщо минула година, скидаємо лічильник мовлення
    if (current_time_ms - tracker->window_start_ms >= WINDOW_ONE_HOUR_MS) {
        tracker->total_tx_time_ms = 0;
        tracker->window_start_ms = current_time_ms;
    }
    
    return (tracker->total_tx_time_ms + packet_toa_ms) <= DUTY_CYCLE_LIMIT_MS;
}

// Запис витраченого часу передачі
void duty_cycle_record_tx(duty_cycle_tracker_t *tracker, uint32_t packet_toa_ms) {
    tracker->total_tx_time_ms += packet_toa_ms;
}

// Симуляція вимірювання RSSI приймачем (у реальності — зчитування з регістру трансивера)
int16_t radio_read_rssi(void) {
    // Демонстраційне значення: -92 dBm (ефір вільний)
    return -92;
}

// Слухання ефіру перед передачею (Listen Before Talk)
bool lbt_is_channel_clear(int16_t threshold_dbm, uint8_t samples) {
    for (uint8_t i = 0; i < samples; i++) {
        int16_t rssi = radio_read_rssi();
        if (rssi > threshold_dbm) {
            return false; // Канал зайнятий іншим пристроєм
        }
    }
    return true; // Канал чистий
}

// Головна функція спроби передачі пакета
bool ism_transmit_packet(duty_cycle_tracker_t *tracker, uint32_t current_time_ms, uint32_t packet_toa_ms) {
    // 1. Перевірка обмеження Duty Cycle
    if (!duty_cycle_can_transmit(tracker, current_time_ms, packet_toa_ms)) {
        printf("[ISM Error] Перевищено ліміт Duty Cycle (1%%)! Передачу блоковано.\n");
        return false;
    }

    // 2. Перевірка чистоти ефіру за допомогою LBT
    if (!lbt_is_channel_clear(RSSI_THRESHOLD_DBM, LBT_SAMPLE_COUNT)) {
        printf("[ISM Warning] Канал зайнятий (LBT fail). Застосовуємо backoff.\n");
        return false;
    }

    // 3. Виконання передачі
    printf("[ISM Tx] Канал чистий. Передача пакета тривалістю %u мс...\n", packet_toa_ms);
    duty_cycle_record_tx(tracker, packet_toa_ms);
    printf("[ISM Status] Витрачено бюджету: %u / %u мс на годину.\n",
           tracker->total_tx_time_ms, DUTY_CYCLE_LIMIT_MS);
    
    return true;
}
