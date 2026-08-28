#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <unistd.h>

#define BUFFER_CAPACITY 512
#define TOPIC_MAX_LEN   128
#define PAYLOAD_MAX_LEN 256
#define PRESSURE_ALARM_THRESHOLD 10.0f

/* Структура одного повідомлення телеметрії */
typedef struct {
    char topic[TOPIC_MAX_LEN];
    char payload[PAYLOAD_MAX_LEN];
    time_t timestamp;
    uint32_t sequence_id;
} telemetry_msg_t;

/* Відмовостійкий кільцевий буфер Store-and-Forward */
typedef struct {
    telemetry_msg_t items[BUFFER_CAPACITY];
    size_t head;
    size_t tail;
    size_t count;
    uint32_t dropped_count;
    pthread_mutex_t lock;
    pthread_cond_t not_empty;
} store_forward_queue_t;

static store_forward_queue_t g_queue;
static bool g_wan_connected = false;
static bool g_running = true;
static uint32_t g_seq_counter = 0;

void queue_init(store_forward_queue_t *q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    q->dropped_count = 0;
    pthread_mutex_init(&q->lock, NULL);
    pthread_cond_init(&q->not_empty, NULL);
}

/* Додавання запису: при переповненні витісняється найстаріший (FIFO Drop) */
bool queue_push(store_forward_queue_t *q, const telemetry_msg_t *msg) {
    pthread_mutex_lock(&q->lock);
    if (q->count >= BUFFER_CAPACITY) {
        /* Витіснення найстарішого елемента для збереження свіжих даних */
        q->tail = (q->tail + 1) % BUFFER_CAPACITY;
        q->count--;
        q->dropped_count++;
    }
    q->items[q->head] = *msg;
    q->head = (q->head + 1) % BUFFER_CAPACITY;
    q->count++;
    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->lock);
    return true;
}

bool queue_pop(store_forward_queue_t *q, telemetry_msg_t *out_msg) {
    pthread_mutex_lock(&q->lock);
    if (q->count == 0) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }
    *out_msg = q->items[q->tail];
    q->tail = (q->tail + 1) % BUFFER_CAPACITY;
    q->count--;
    pthread_mutex_unlock(&q->lock);
    return true;
}

/* Емуляція польового опитування Modbus RTU */
void poll_modbus_pressure(void) {
    /* Симуляція отримання двох 16-бітних регістрів (Float32: 0x41200000 = 10.0f) */
    static float simulated_pressure = 8.5f;
    simulated_pressure += ((rand() % 100) - 45) * 0.05f;

    printf("[MODBUS] Опитано вузол #1: тиск = %.2f bar\n", simulated_pressure);

    /* Локальне правило автономії: пряма реакція на аварію */
    if (simulated_pressure > PRESSURE_ALARM_THRESHOLD) {
        printf("[AUTONOMY ALERT] Тиск %.2f > %.1f bar! "
               "Локальна дія: запис Coil 0x0010 = ON (Аварійне скидання)\n",
               simulated_pressure, PRESSURE_ALARM_THRESHOLD);
    }

    /* Формування MQTT-повідомлення */
    telemetry_msg_t msg;
    msg.timestamp = time(NULL);
    msg.sequence_id = ++g_seq_counter;
    snprintf(msg.topic, sizeof(msg.topic), "plant/unit1/telemetry/pressure");
    snprintf(msg.payload, sizeof(msg.payload),
             "{\"dev\":\"boiler_1\",\"val\":%.2f,\"unit\":\"bar\",\"ts\":%ld,\"seq\":%u}",
             simulated_pressure, msg.timestamp, msg.sequence_id);

    queue_push(&g_queue, &msg);
}

/* Емуляція прийому пакетів від BLE-термометра */
void receive_ble_temperature(void) {
    static float simulated_temp = 42.0f;
    simulated_temp += ((rand() % 100) - 50) * 0.02f;

    telemetry_msg_t msg;
    msg.timestamp = time(NULL);
    msg.sequence_id = ++g_seq_counter;
    snprintf(msg.topic, sizeof(msg.topic), "plant/unit1/telemetry/temperature");
    snprintf(msg.payload, sizeof(msg.payload),
             "{\"dev\":\"ble_sensor_a4\",\"val\":%.2f,\"unit\":\"C\",\"ts\":%ld,\"seq\":%u}",
             simulated_temp, msg.timestamp, msg.sequence_id);

    queue_push(&g_queue, &msg);
}

/* Потік публікації та відкладеного викачування (Store-and-Forward Worker) */
void *mqtt_upstream_worker(void *arg) {
    (void)arg;
    telemetry_msg_t msg;

    while (g_running) {
        if (!g_wan_connected) {
            /* WAN відсутній: накопичуємо в черзі, спимо */
            usleep(200000);
            continue;
        }

        /* WAN активний: викачуємо накопичені повідомлення */
        while (g_wan_connected && queue_pop(&g_queue, &msg)) {
            printf("[MQTT PUB] Успішно відправлено -> %s : %s\n",
                   msg.topic, msg.payload);
            /* Згладжування трафіку (Rate limiting: 20 ms між пакетами) */
            usleep(20000);
        }

        usleep(100000);
    }
    return NULL;
}

int main(void) {
    srand(time(NULL));
    queue_init(&g_queue);

    pthread_t worker_tid;
    pthread_create(&worker_tid, NULL, mqtt_upstream_worker, NULL);

    printf("=== Старт IoT-шлюзу (C-версія) ===\n");

    /* Демонстрація життєвого циклу: Онлайн -> Блекаут -> Відновлення */
    for (int step = 1; step <= 10; step++) {
        printf("\n--- ТАКТ СИСТЕМИ %d ---\n", step);

        /* Моделювання стану каналу WAN: кроки 3..7 — блекаут */
        if (step >= 3 && step <= 7) {
            if (g_wan_connected) {
                printf("[WAN] Зв'язок розірвано! Активовано буфер Store-and-Forward.\n");
                g_wan_connected = false;
            }
        } else {
            if (!g_wan_connected) {
                printf("[WAN] Зв'язок відновлено! Старт дренажу буфера.\n");
                g_wan_connected = true;
            }
        }

        poll_modbus_pressure();
        receive_ble_temperature();

        pthread_mutex_lock(&g_queue.lock);
        printf("[BUFFER STATUS] Елементів у буфері: %zu, Втрачено: %u\n",
               g_queue.count, g_queue.dropped_count);
        pthread_mutex_unlock(&g_queue.lock);

        sleep(1);
    }

    g_running = false;
    pthread_join(worker_tid, NULL);
    pthread_mutex_destroy(&g_queue.lock);
    pthread_cond_destroy(&g_queue.not_empty);
    printf("=== Роботу шлюзу завершено ===\n");
    return 0;
}
