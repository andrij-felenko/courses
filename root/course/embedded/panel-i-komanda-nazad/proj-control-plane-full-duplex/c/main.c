#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>

#define DEDUP_HISTORY_SIZE 16
#define CMD_ID_MAX_LEN     37

typedef enum {
    CMD_STATE_IDLE,
    CMD_STATE_RECEIVED,
    CMD_STATE_EXECUTING,
    CMD_STATE_COMPLETED,
    CMD_STATE_FAILED
} cmd_exec_state_t;

typedef struct {
    char cmd_id[CMD_ID_MAX_LEN];
    uint32_t timestamp_sec;
} dedup_entry_t;

typedef struct {
    dedup_entry_t history[DEDUP_HISTORY_SIZE];
    uint8_t head;
    uint8_t count;
} dedup_filter_t;

typedef struct {
    char current_cmd_id[CMD_ID_MAX_LEN];
    cmd_exec_state_t state;
    uint32_t start_time_ms;
    uint32_t target_duration_ms;
    int target_value;
    int current_value;
} actuator_worker_t;

static dedup_filter_t s_dedup;
static actuator_worker_t s_worker;

void dedup_init(void) {
    memset(&s_dedup, 0, sizeof(s_dedup));
    s_worker.state = CMD_STATE_IDLE;
    s_worker.current_value = 0;
}

bool dedup_is_duplicate(const char *cmd_id) {
    for (uint8_t i = 0; i < s_dedup.count; ++i) {
        if (strncmp(s_dedup.history[i].cmd_id, cmd_id, CMD_ID_MAX_LEN) == 0) {
            return true;
        }
    }
    return false;
}

void dedup_record(const char *cmd_id, uint32_t now_sec) {
    uint8_t idx = s_dedup.head;
    strncpy(s_dedup.history[idx].cmd_id, cmd_id, CMD_ID_MAX_LEN - 1);
    s_dedup.history[idx].cmd_id[CMD_ID_MAX_LEN - 1] = '\0';
    s_dedup.history[idx].timestamp_sec = now_sec;

    s_dedup.head = (s_dedup.head + 1) % DEDUP_HISTORY_SIZE;
    if (s_dedup.count < DEDUP_HISTORY_SIZE) {
        s_dedup.count++;
    }
}

void publish_ack(const char *cmd_id, const char *status) {
    printf("[MQTT OUT -> devices/zone1/cmd/ack] {\"cmd_id\":\"%s\",\"status\":\"%s\"}\n",
           cmd_id, status);
}

void publish_exec_status(const char *cmd_id, const char *state, int progress, int val, int err) {
    printf("[MQTT OUT -> devices/zone1/cmd/status] {\"cmd_id\":\"%s\",\"state\":\"%s\","
           "\"progress_pct\":%d,\"val\":%d,\"err\":%d}\n",
           cmd_id, state, progress, val, err);
}

void handle_incoming_downlink(const char *cmd_id, int target_pos, uint32_t issued_at,
                              uint16_t ttl_sec, uint32_t now_sec, uint32_t now_ms) {
    // 1. Перевірка строку придатності TTL
    if (now_sec > issued_at + ttl_sec) {
        publish_exec_status(cmd_id, "EXPIRED", 0, s_worker.current_value, 104);
        return;
    }

    // 2. Перевірка ідемпотентності
    if (dedup_is_duplicate(cmd_id)) {
        publish_ack(cmd_id, "ACK_DUPLICATE");
        // Повторюємо останній відомий стан без фізичного смикання приводу
        publish_exec_status(cmd_id, "COMPLETED", 100, s_worker.current_value, 0);
        return;
    }

    // 3. Фіксація в журналі дедуплікації
    dedup_record(cmd_id, now_sec);

    // 4. Фаза 1: миттєве квитування прийому
    publish_ack(cmd_id, "ACK_RECEIVED");

    // 5. Постановка завдання в апаратний воркер
    strncpy(s_worker.current_cmd_id, cmd_id, CMD_ID_MAX_LEN - 1);
    s_worker.current_cmd_id[CMD_ID_MAX_LEN - 1] = '\0';
    s_worker.target_value = target_pos;
    s_worker.start_time_ms = now_ms;
    s_worker.target_duration_ms = 3000; // 3 секунди на плавний поворот
    s_worker.state = CMD_STATE_EXECUTING;

    publish_exec_status(cmd_id, "STARTED", 0, s_worker.current_value, 0);
}

void actuator_poll(uint32_t now_ms) {
    if (s_worker.state != CMD_STATE_EXECUTING) {
        return;
    }

    uint32_t elapsed = now_ms - s_worker.start_time_ms;
    if (elapsed >= s_worker.target_duration_ms) {
        // Завершення фізичної операції
        s_worker.current_value = s_worker.target_value;
        s_worker.state = CMD_STATE_COMPLETED;
        publish_exec_status(s_worker.current_cmd_id, "COMPLETED", 100, s_worker.current_value, 0);
    } else {
        // Проміжний звіт прогресу кожні 500 мс
        static uint32_t last_progress_report = 0;
        if (now_ms - last_progress_report >= 500) {
            last_progress_report = now_ms;
            int progress = (int)((elapsed * 100) / s_worker.target_duration_ms);
            publish_exec_status(s_worker.current_cmd_id, "IN_PROGRESS", progress, s_worker.current_value, 0);
        }
    }
}
