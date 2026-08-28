#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define MAX_STATIONS       32
#define MAX_BACKOFF_EXP    10
#define MAX_ATTEMPTS       16
#define SLOT_TIME_US       51.2
#define FRAME_SLOTS_MIN    1   /* 64 байти = 1 слот (51.2 мкс) */
#define FRAME_SLOTS_MAX    24  /* 1518 байтів ≈ 24 слоти */

typedef enum {
    STATE_IDLE = 0,
    STATE_SENSING,
    STATE_TRANSMITTING,
    STATE_JAMMING,
    STATE_BACKOFF
} station_state_t;

typedef struct {
    uint32_t id;
    station_state_t state;
    uint32_t attempts;
    uint32_t backoff_slots_left;
    uint32_t frame_slots_left;
    uint32_t current_frame_len_slots;
    
    /* Статистика станції */
    uint64_t frames_sent_ok;
    uint64_t frames_dropped;
    uint64_t collisions_total;
    uint64_t total_wait_slots;
} station_t;

typedef struct {
    uint32_t num_stations;
    station_t stations[MAX_STATIONS];
    uint32_t active_transmitters;
    uint64_t current_slot;
    uint64_t total_sim_slots;
    double packet_arrival_prob;
    
    /* Глобальна статистика шини */
    uint64_t bus_idle_slots;
    uint64_t bus_success_slots;
    uint64_t bus_collision_slots;
    uint64_t total_successful_frames;
} ethernet_bus_t;

static void bus_init(ethernet_bus_t *bus, uint32_t num_stations, double load_prob, uint64_t sim_slots) {
    memset(bus, 0, sizeof(*bus));
    bus->num_stations = (num_stations > MAX_STATIONS) ? MAX_STATIONS : num_stations;
    bus->packet_arrival_prob = load_prob;
    bus->total_sim_slots = sim_slots;
    
    for (uint32_t i = 0; i < bus->num_stations; ++i) {
        bus->stations[i].id = i;
        bus->stations[i].state = STATE_IDLE;
    }
}

static uint32_t calculate_backoff(uint32_t attempts) {
    uint32_t k = (attempts > MAX_BACKOFF_EXP) ? MAX_BACKOFF_EXP : attempts;
    uint32_t max_slots = (1U << k);
    return (uint32_t)(rand() % max_slots);
}

static void simulate_slot(ethernet_bus_t *bus) {
    /* 1. Генерація нового трафіку для станцій у стані IDLE */
    for (uint32_t i = 0; i < bus->num_stations; ++i) {
        station_t *st = &bus->stations[i];
        if (st->state == STATE_IDLE) {
            double r = (double)rand() / (double)RAND_MAX;
            if (r < bus->packet_arrival_prob) {
                st->state = STATE_SENSING;
                st->attempts = 0;
                /* Випадковий розмір кадру від 1 до 24 слотів */
                st->current_frame_len_slots = 1 + (rand() % (FRAME_SLOTS_MAX - FRAME_SLOTS_MIN + 1));
            }
        }
    }

    /* 2. Підрахунок кількості станцій, які бажають передавати на цьому слоті */
    uint32_t transmitting_now = 0;
    for (uint32_t i = 0; i < bus->num_stations; ++i) {
        station_t *st = &bus->stations[i];
        if (st->state == STATE_TRANSMITTING || st->state == STATE_JAMMING) {
            transmitting_now++;
        } else if (st->state == STATE_SENSING) {
            /* 1-persistent: якщо шина була вільна, починаємо передачу */
            if (bus->active_transmitters == 0) {
                st->state = STATE_TRANSMITTING;
                st->frame_slots_left = st->current_frame_len_slots;
                transmitting_now++;
            }
        }
    }

    /* 3. Оновлення стану шини та аналіз колізій */
    if (transmitting_now == 0) {
        bus->bus_idle_slots++;
    } else if (transmitting_now == 1) {
        bus->bus_success_slots++;
    } else {
        bus->bus_collision_slots++;
    }
    bus->active_transmitters = transmitting_now;

    /* 4. Обробка автоматів кожної станції */
    for (uint32_t i = 0; i < bus->num_stations; ++i) {
        station_t *st = &bus->stations[i];
        
        switch (st->state) {
        case STATE_IDLE:
            break;
            
        case STATE_SENSING:
            st->total_wait_slots++;
            break;
            
        case STATE_TRANSMITTING:
            if (transmitting_now > 1) {
                /* Колізія виявлена під час передачі */
                st->collisions_total++;
                st->state = STATE_JAMMING;
            } else {
                /* Успішне просування передачі кадру */
                st->frame_slots_left--;
                if (st->frame_slots_left == 0) {
                    st->frames_sent_ok++;
                    bus->total_successful_frames++;
                    st->state = STATE_IDLE;
                    st->attempts = 0;
                }
            }
            break;
            
        case STATE_JAMMING:
            /* Після відправки Jam переходимо у відкат BEB */
            st->attempts++;
            if (st->attempts > MAX_ATTEMPTS) {
                /* Перевищено 16 спроб — скидання кадру */
                st->frames_dropped++;
                st->state = STATE_IDLE;
                st->attempts = 0;
            } else {
                st->backoff_slots_left = calculate_backoff(st->attempts);
                st->state = STATE_BACKOFF;
            }
            break;
            
        case STATE_BACKOFF:
            st->total_wait_slots++;
            if (st->backoff_slots_left == 0) {
                st->state = STATE_SENSING;
            } else {
                st->backoff_slots_left--;
            }
            break;
        }
    }
    bus->current_slot++;
}

static void print_bus_report(const ethernet_bus_t *bus) {
    double total = (double)bus->total_sim_slots;
    double util = ((double)bus->bus_success_slots / total) * 100.0;
    double coll_rate = ((double)bus->bus_collision_slots / total) * 100.0;
    double idle_rate = ((double)bus->bus_idle_slots / total) * 100.0;
    
    printf("=== ЗВІТ СИМУЛЯЦІЇ СЕРЕДОВИЩА CSMA/CD ===\n");
    printf("Загальна кількість слотів:  %llu (%.2f с ефірного часу)\n",
           (unsigned long long)bus->total_sim_slots,
           (bus->total_sim_slots * SLOT_TIME_US) / 1000000.0);
    printf("Кількість станцій:          %u\n", bus->num_stations);
    printf("Корисна утилізація шини:    %.2f%%\n", util);
    printf("Частка колізійних слотів:   %.2f%%\n", coll_rate);
    printf("Частка слотів простою:      %.2f%%\n", idle_rate);
    printf("Успішно доставлено кадрів:  %llu\n", (unsigned long long)bus->total_successful_frames);
    printf("----------------------------------------\n");
    printf("ID   | Успішно  | Скинуто  | Колізій  | Сер. очікування\n");
    for (uint32_t i = 0; i < bus->num_stations; ++i) {
        const station_t *st = &bus->stations[i];
        double avg_wait = st->frames_sent_ok ? ((double)st->total_wait_slots / st->frames_sent_ok) : 0.0;
        printf("#%02u  | %-8llu | %-8llu | %-8llu | %.2f слотів\n",
               st->id,
               (unsigned long long)st->frames_sent_ok,
               (unsigned long long)st->frames_dropped,
               (unsigned long long)st->collisions_total,
               avg_wait);
    }
}

int main(void) {
    srand(42);
    ethernet_bus_t bus;
    uint32_t stations_count = 10;
    double arrival_rate = 0.05;  /* 5% ймовірність генерації кадру за слот на станцію */
    uint64_t sim_steps = 100000; /* 100 000 слотів = 5.12 с роботи 10 Мбіт/с Ethernet */
    
    bus_init(&bus, stations_count, arrival_rate, sim_steps);
    for (uint64_t s = 0; s < sim_steps; ++s) {
        simulate_slot(&bus);
    }
    print_bus_report(&bus);
    return 0;
}
