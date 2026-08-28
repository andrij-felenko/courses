#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_MEMBERS 64
#define K_HELPERS 3
#define PING_TIMEOUT_MS 200
#define SUSPECT_TIMEOUT_MS 1000

typedef enum {
    STATUS_ALIVE = 0,
    STATUS_SUSPECT = 1,
    STATUS_DEAD = 2
} member_status_t;

typedef struct {
    uint32_t id;
    member_status_t status;
    uint32_t incarnation;
    uint64_t state_change_time_ms;
} member_t;

typedef struct {
    uint32_t self_id;
    uint32_t self_incarnation;
    member_t members[MAX_MEMBERS];
    size_t member_count;
    
    // Стан поточного раунду зондування
    uint32_t current_target_id;
    bool ping_in_flight;
    bool ping_req_in_flight;
    uint64_t probe_start_time_ms;
} swim_detector_t;

void swim_init(swim_detector_t* detector, uint32_t self_id) {
    detector->self_id = self_id;
    detector->self_incarnation = 0;
    detector->member_count = 0;
    detector->ping_in_flight = false;
    detector->ping_req_in_flight = false;
}

int find_member_index(const swim_detector_t* detector, uint32_t id) {
    for (size_t i = 0; i < detector->member_count; ++i) {
        if (detector->members[i].id == id) {
            return (int)i;
        }
    }
    return -1;
}

void swim_add_member(swim_detector_t* detector, uint32_t id, uint64_t now_ms) {
    if (detector->member_count >= MAX_MEMBERS || id == detector->self_id) {
        return;
    }
    if (find_member_index(detector, id) != -1) {
        return;
    }
    member_t* m = &detector->members[detector->member_count++];
    m->id = id;
    m->status = STATUS_ALIVE;
    m->incarnation = 0;
    m->state_change_time_ms = now_ms;
}

// Оновлення стану члена за правилами пріоритету інкарнацій
void swim_apply_update(swim_detector_t* detector, uint32_t id, member_status_t new_status, 
                       uint32_t inc, uint64_t now_ms) {
    // Якщо підозра стосується власне нас — спростовуємо її
    if (id == detector->self_id) {
        if (new_status == STATUS_SUSPECT && inc >= detector->self_incarnation) {
            detector->self_incarnation = inc + 1;
            printf("[Node %u] Спростування підозри! Нова інкарнація: %u\n", 
                   detector->self_id, detector->self_incarnation);
        }
        return;
    }

    int idx = find_member_index(detector, id);
    if (idx == -1) {
        return;
    }
    member_t* m = &detector->members[idx];

    // Правило пріоритету SWIM: вища інкарнація завжди перемагає
    if (inc > m->incarnation) {
        m->incarnation = inc;
        m->status = new_status;
        m->state_change_time_ms = now_ms;
    } else if (inc == m->incarnation) {
        // За однакової інкарнації: DEAD > SUSPECT > ALIVE
        if (m->status == STATUS_ALIVE && new_status == STATUS_SUSPECT) {
            m->status = STATUS_SUSPECT;
            m->state_change_time_ms = now_ms;
        } else if (new_status == STATUS_DEAD) {
            m->status = STATUS_DEAD;
            m->state_change_time_ms = now_ms;
        }
    }
}

// Основний тактовий цикл детектора
void swim_tick(swim_detector_t* detector, uint64_t now_ms) {
    // 1. Перевірка таймаутів підозри (Suspect -> Dead)
    for (size_t i = 0; i < detector->member_count; ++i) {
        member_t* m = &detector->members[i];
        if (m->status == STATUS_SUSPECT) {
            if (now_ms - m->state_change_time_ms >= SUSPECT_TIMEOUT_MS) {
                m->status = STATUS_DEAD;
                m->state_change_time_ms = now_ms;
                printf("[Node %u] Вузол %u не надіслав спростування -> СТАТУС DEAD\n", 
                       detector->self_id, m->id);
            }
        }
    }

    // 2. Якщо зонд у польоті, перевіряємо таймаути фаз
    if (detector->ping_in_flight) {
        uint64_t elapsed = now_ms - detector->probe_start_time_ms;
        if (!detector->ping_req_in_flight && elapsed >= PING_TIMEOUT_MS) {
            // Прямий Ping прострочено -> запускаємо непрямий Ping-Req через k помічників
            detector->ping_req_in_flight = true;
            printf("[Node %u] Прямий Ping до %u прострочено -> розсилка Ping-Req через k помічників\n",
                   detector->self_id, detector->current_target_id);
        } else if (detector->ping_req_in_flight && elapsed >= (PING_TIMEOUT_MS * 2)) {
            // Непрямий Ping-Req також прострочено -> переводимо ціль у Suspect
            int idx = find_member_index(detector, detector->current_target_id);
            if (idx != -1) {
                swim_apply_update(detector, detector->current_target_id, STATUS_SUSPECT, 
                                  detector->members[idx].incarnation, now_ms);
                printf("[Node %u] Жоден помічник не відповів -> Вузол %u переведений у SUSPECT\n",
                       detector->self_id, detector->current_target_id);
            }
            detector->ping_in_flight = false;
            detector->ping_req_in_flight = false;
        }
    }
}

// Запуск нового раунду зондування
void swim_start_probe_round(swim_detector_t* detector, uint64_t now_ms) {
    if (detector->member_count == 0 || detector->ping_in_flight) {
        return;
    }
    // Обираємо випадкового живого або підозрюваного члена
    size_t target_idx = (size_t)rand() % detector->member_count;
    if (detector->members[target_idx].status == STATUS_DEAD) {
        return;
    }
    detector->current_target_id = detector->members[target_idx].id;
    detector->ping_in_flight = true;
    detector->ping_req_in_flight = false;
    detector->probe_start_time_ms = now_ms;
    printf("[Node %u] Старт зондування вузла %u (Прямий Ping)\n", 
           detector->self_id, detector->current_target_id);
}

// Обробка отриманого підтвердження Ack від цілі
void swim_on_ack_received(swim_detector_t* detector, uint32_t from_id, uint32_t inc, uint64_t now_ms) {
    if (detector->ping_in_flight && detector->current_target_id == from_id) {
        detector->ping_in_flight = false;
        detector->ping_req_in_flight = false;
        swim_apply_update(detector, from_id, STATUS_ALIVE, inc, now_ms);
        printf("[Node %u] Отримано успішний Ack від вузла %u\n", detector->self_id, from_id);
    }
}
