#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>

#define DEDUP_CAPACITY    16
#define UUID_STR_LEN      37

typedef enum {
    ACTUATOR_IDLE,
    ACTUATOR_BUSY,
    ACTUATOR_ERROR
} actuator_state_t;

typedef struct {
    char cmd_id[UUID_STR_LEN];
    uint32_t seen_time_sec;
} dedup_record_t;

typedef struct {
    dedup_record_t records[DEDUP_CAPACITY];
    uint8_t head;
    uint8_t count;
} dedup_filter_t;

typedef struct {
    actuator_state_t state;
    char active_cmd_id[UUID_STR_LEN];
    uint32_t start_tick_ms;
    uint32_t duration_ms;
    int target_angle_deg;
    int current_angle_deg;
} servo_worker_t;

static dedup_filter_t s_dedup;
static servo_worker_t s_servo;

void dedup_init(void) {
    memset(&s_dedup, 0, sizeof(s_dedup));
    s_servo.state = ACTUATOR_IDLE;
    s_servo.current_angle_deg = 0;
}

bool dedup_check(const char *cmd_id) {
    for (uint8_t i = 0; i < s_dedup.count; ++i) {
        if (strncmp(s_dedup.records[i].cmd_id, cmd_id, UUID_STR_LEN) == 0) {
            return true; // Знайдено дублікат
        }
    }
    return false;
}

void dedup_insert(const char *cmd_id, uint32_t now_sec) {
    uint8_t idx = s_dedup.head;
    strncpy(s_dedup.records[idx].cmd_id, cmd_id, UUID_STR_LEN - 1);
    s_dedup.records[idx].cmd_id[UUID_STR_LEN - 1] = '\0';
    s_dedup.records[idx].seen_time_sec = now_sec;

    s_dedup.head = (s_dedup.head + 1) % DEDUP_CAPACITY;
    if (s_dedup.count < DEDUP_CAPACITY) {
        s_dedup.count++;
    }
}

void net_send_ack(const char *cmd_id, const char *status) {
    printf("--> [PUB devices/gate/cmd/ack] {\"cmd_id\":\"%s\",\"status\":\"%s\"}\n",
           cmd_id, status);
}

void net_send_exec_status(const char *cmd_id, const char *state, int progress, int pos, int err) {
    printf("--> [PUB devices/gate/cmd/status] {\"cmd_id\":\"%s\",\"state\":\"%s\","
           "\"progress_pct\":%d,\"pos\":%d,\"err\":%d}\n",
           cmd_id, state, progress, pos, err);
}

// Викликається з мережевого колбеку при отриманні команди
void on_downlink_received(const char *cmd_id, int target_pos, uint32_t issued_at,
                          uint16_t ttl_sec, uint32_t now_sec, uint32_t now_ms) {
    // 1. Перевірка строку придатності
    if (now_sec > issued_at + ttl_sec) {
        net_send_exec_status(cmd_id, "EXPIRED", 0, s_servo.current_angle_deg, 104);
        return;
    }

    // 2. Фільтрація повторів
    if (dedup_check(cmd_id)) {
        net_send_ack(cmd_id, "ACK_DUPLICATE");
        net_send_exec_status(cmd_id, "COMPLETED", 100, s_servo.current_angle_deg, 0);
        return;
    }

    // 3. Перевірка зайнятості приводу
    if (s_servo.state == ACTUATOR_BUSY) {
        net_send_ack(cmd_id, "ACK_REJECTED");
        net_send_exec_status(cmd_id, "FAILED", 0, s_servo.current_angle_deg, 201); // ERR_DEVICE_BUSY
        return;
    }

    // 4. Фіксація ідентифікатора
    dedup_insert(cmd_id, now_sec);

    // 5. Фаза 1: миттєве транспортне квитування
    net_send_ack(cmd_id, "ACK_RECEIVED");

    // 6. Запуск асинхронного апаратного процесу
    strncpy(s_servo.active_cmd_id, cmd_id, UUID_STR_LEN - 1);
    s_servo.active_cmd_id[UUID_STR_LEN - 1] = '\0';
    s_servo.target_angle_deg = target_pos;
    s_servo.start_tick_ms = now_ms;
    s_servo.duration_ms = 2500; // 2.5 с на поворот сервоприводу
    s_servo.state = ACTUATOR_BUSY;

    net_send_exec_status(cmd_id, "STARTED", 0, s_servo.current_angle_deg, 0);
}

// Викликається на кожному витку швидкого loop()
void servo_worker_poll(uint32_t now_ms) {
    if (s_servo.state != ACTUATOR_BUSY) {
        return;
    }

    uint32_t elapsed = now_ms - s_servo.start_tick_ms;
    if (elapsed >= s_servo.duration_ms) {
        // Завершення операції
        s_servo.current_angle_deg = s_servo.target_angle_deg;
        s_servo.state = ACTUATOR_IDLE;
        net_send_exec_status(s_servo.active_cmd_id, "COMPLETED", 100, s_servo.current_angle_deg, 0);
    } else {
        // Періодичний звіт про прогрес
        static uint32_t last_report_ms = 0;
        if (now_ms - last_report_ms >= 500) {
            last_report_ms = now_ms;
            int progress = (int)((elapsed * 100) / s_servo.duration_ms);
            net_send_exec_status(s_servo.active_cmd_id, "IN_PROGRESS", progress, s_servo.current_angle_deg, 0);
        }
    }
}
