#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>

#define TOTAL_CHANNELS 8
#define HOP_PERIOD_US  2000
#define GUARD_TIME_US  150
#define DRIFT_PPM      30
#define MAX_MISSED_HOPS 5

typedef enum {
    FSM_SEARCHING,
    FSM_LOCKING,
    FSM_TRACKING,
    FSM_LOST_SYNC
} SyncState;

typedef struct {
    uint16_t lfsr_state;
    uint32_t current_hop;
} Transmitter;

typedef struct {
    SyncState state;
    uint16_t lfsr_state;
    uint32_t current_hop;
    int32_t  timer_offset_us;
    uint8_t  scan_channel;
    uint8_t  missed_count;
} Receiver;

/* Генератор псевдовипадкових чисел (8-бітний LFSR) */
static uint8_t lfsr_next(uint16_t *state) {
    uint16_t bit = ((*state >> 0) ^ (*state >> 2) ^ (*state >> 3) ^ (*state >> 5)) & 1;
    *state = (*state >> 1) | (bit << 7);
    return (uint8_t)(*state % TOTAL_CHANNELS);
}

void tx_init(Transmitter *tx, uint16_t seed) {
    tx->lfsr_state = seed;
    tx->current_hop = 0;
}

uint8_t tx_step(Transmitter *tx) {
    tx->current_hop++;
    return lfsr_next(&tx->lfsr_state);
}

void rx_init(Receiver *rx) {
    rx->state = FSM_SEARCHING;
    rx->lfsr_state = 0;
    rx->current_hop = 0;
    rx->timer_offset_us = 0;
    rx->scan_channel = 3; /* Фіксований канал сканування */
    rx->missed_count = 0;
}

void rx_process_hop(Receiver *rx, uint8_t tx_channel, uint16_t tx_seed, uint32_t tx_hop, int32_t drift_us) {
    rx->timer_offset_us += drift_us;

    switch (rx->state) {
        case FSM_SEARCHING: {
            printf("[SEARCH] Rx чекає на каналі %d... Tx випромінює на %d\n", rx->scan_channel, tx_channel);
            if (tx_channel == rx->scan_channel) {
                rx->state = FSM_LOCKING;
                rx->lfsr_state = tx_seed;
                rx->current_hop = tx_hop;
                rx->timer_offset_us = 0;
                rx->missed_count = 0;
                printf("  -> [EVENT] Преамбулу знайдено! Перехід у LOCKING (Hop=%u)\n", tx_hop);
            }
            break;
        }

        case FSM_LOCKING: {
            rx->state = FSM_TRACKING;
            printf("  -> [FSM] Таймери узгоджено. Перехід у TRACKING\n");
            break;
        }

        case FSM_TRACKING: {
            rx->current_hop++;
            uint8_t expected_ch = lfsr_next(&rx->lfsr_state);

            /* Перевірка попадання у вікно прийому з урахуванням дрейфу */
            bool time_ok = (abs(rx->timer_offset_us) <= GUARD_TIME_US);
            bool ch_ok = (expected_ch == tx_channel);

            if (time_ok && ch_ok) {
                printf("[TRACKING] Hop %u: Канал %d OK (Дрейф: %d us)\n", 
                       rx->current_hop, expected_ch, rx->timer_offset_us);
                /* Ранньо-пізня корекція: зрізаємо 50% накопиченого дрейфу */
                rx->timer_offset_us /= 2;
                rx->missed_count = 0;
            } else {
                rx->missed_count++;
                printf("[TRACKING] Hop %u: Пропуск кадру! (ChOK=%d, TimeOK=%d, Missed=%d/%d)\n",
                       rx->current_hop, ch_ok, time_ok, rx->missed_count, MAX_MISSED_HOPS);

                if (rx->missed_count >= MAX_MISSED_HOPS) {
                    rx->state = FSM_LOST_SYNC;
                }
            }
            break;
        }

        case FSM_LOST_SYNC: {
            printf("  -> [ALERT] Втрата синхронізму! Скидання у SEARCHING\n");
            rx_init(rx);
            break;
        }
    }
}

int main(void) {
    Transmitter tx;
    Receiver rx;

    uint16_t initial_seed = 0xACE1;
    tx_init(&tx, initial_seed);
    rx_init(&rx);

    printf("=== СИМУЛЯЦІЯ FHSS СИНХРОНІЗАЦІЇ ===\n");
    printf("Каналів: %d, Захисний інтервал: %d us, Дрейф: %d ppm\n\n", 
           TOTAL_CHANNELS, GUARD_TIME_US, DRIFT_PPM);

    for (int step = 0; step < 20; step++) {
        uint16_t seed_before = tx.lfsr_state;
        uint8_t tx_ch = tx_step(&tx);

        /* Симульований накопичений дрейф +45 мкс на кожен стрибок */
        int32_t simulated_drift = 45;

        rx_process_hop(&rx, tx_ch, seed_before, tx.current_hop, simulated_drift);
    }

    return 0;
}
