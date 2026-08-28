#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>
#include <inttypes.h>

#define MAX_PAYLOAD_SIZE   512
#define MAX_BUS_NAME_LEN    32
#define MAX_HOPS             3
#define BUFFER_CAPACITY     16
#define HIGH_WATERMARK      12
#define LOW_WATERMARK        4

/* Статуси операцій мосту */
typedef enum {
    BRIDGE_OK = 0,
    BRIDGE_ERR_BUFFER_FULL,
    BRIDGE_ERR_CORRUPTED_PAYLOAD,
    BRIDGE_ERR_LOOP_DETECTED,
    BRIDGE_ERR_EGRESS_FAILED
} BridgeStatus;

/* Структура повідомлення з метаданими трасування */
typedef struct {
    uint64_t msg_id;
    uint32_t hop_count;
    char     origin_bus[MAX_BUS_NAME_LEN];
    char     payload[MAX_PAYLOAD_SIZE];
    size_t   payload_len;
    uint64_t ingress_delivery_tag; /* Ідентифікатор квитанції у вхідній шині */
} BridgeMessage;

/* Потокобезпечний кільцевий буфер Store-and-Forward */
typedef struct {
    BridgeMessage   slots[BUFFER_CAPACITY];
    size_t          head;
    size_t          tail;
    size_t          count;
    bool            paused;
    pthread_mutex_t lock;
    pthread_cond_t  not_empty;
    pthread_cond_t  not_full;
} ResilientRingBuffer;

/* Контекст мосту шин */
typedef struct {
    char                current_bus_name[MAX_BUS_NAME_LEN];
    ResilientRingBuffer queue;
    bool                running;
    uint64_t            forwarded_count;
    uint64_t            quarantine_count;
    pthread_t           worker_thread;
} MessageBusBridge;

/* Ініціалізація буфера */
static void ring_buffer_init(ResilientRingBuffer *rb) {
    rb->head = 0;
    rb->tail = 0;
    rb->count = 0;
    rb->paused = false;
    pthread_mutex_init(&rb->lock, NULL);
    pthread_cond_init(&rb->not_empty, NULL);
    pthread_cond_init(&rb->not_full, NULL);
}

/* Знищення ресурсів буфера */
static void ring_buffer_destroy(ResilientRingBuffer *rb) {
    pthread_mutex_destroy(&rb->lock);
    pthread_cond_destroy(&rb->not_empty);
    pthread_cond_destroy(&rb->not_full);
}

/* Додавання повідомлення до буфера мосту (Ingress Stage) */
static BridgeStatus bridge_enqueue(MessageBusBridge *bridge, const BridgeMessage *msg) {
    pthread_mutex_lock(&bridge->queue.lock);

    /* Перевірка на зациклення перед збереженням у пам'ять */
    if (msg->hop_count >= MAX_HOPS || strcmp(msg->origin_bus, bridge->current_bus_name) == 0) {
        pthread_mutex_unlock(&bridge->queue.lock);
        return BRIDGE_ERR_LOOP_DETECTED;
    }

    /* Очікування вільного місця у разі переповнення */
    while (bridge->queue.count == BUFFER_CAPACITY && bridge->running) {
        pthread_cond_wait(&bridge->queue.not_full, &bridge->queue.lock);
    }

    if (!bridge->running) {
        pthread_mutex_unlock(&bridge->queue.lock);
        return BRIDGE_ERR_EGRESS_FAILED;
    }

    /* Запис у кільцевий буфер */
    bridge->queue.slots[bridge->queue.head] = *msg;
    bridge->queue.head = (bridge->queue.head + 1) % BUFFER_CAPACITY;
    bridge->queue.count++;

    /* Контроль протитиску за високим водяним знаком */
    if (bridge->queue.count >= HIGH_WATERMARK && !bridge->queue.paused) {
        bridge->queue.paused = true;
        printf("[ПРОТИТИСК] Буфер досяг %zu/%d. Призупинено вичитування з входу.\n",
               bridge->queue.count, BUFFER_CAPACITY);
    }

    pthread_cond_signal(&bridge->queue.not_empty);
    pthread_mutex_unlock(&bridge->queue.lock);
    return BRIDGE_OK;
}

/* Імітація публікації у вихідну шину з підтвердженням (Egress Stage) */
static bool mock_egress_publish(const char *target_bus, const BridgeMessage *msg) {
    /* Імітація мережевої затримки транзиту */
    usleep(15000); /* 15 мс */

    /* Імітація збою у разі спеціального маркера або помилки валідації */
    if (strstr(msg->payload, "CORRUPT") != NULL) {
        return false;
    }

    printf("[EGRESS -> %s] Успішно записано msg_id=%" PRIu64 " (hops=%u, payload=\"%s\")\n",
           target_bus, msg->msg_id, msg->hop_count + 1, msg->payload);
    return true;
}

/* Імітація підтвердження у вхідній черзі (Ingress Commit) */
static void mock_ingress_commit(uint64_t delivery_tag) {
    printf("[INGRESS-ACK] Квитанція delivery_tag=%" PRIu64 " успішно підтверджена у вхідній шині.\n",
           delivery_tag);
}

/* Імітація відправки у мертву чергу (Quarantine DLQ) */
static void mock_quarantine_dlq(const BridgeMessage *msg, const char *reason) {
    printf("[МЕРТВА ЧЕРГА / DLQ] Ізольовано msg_id=%" PRIu64 ", причина: %s\n",
           msg->msg_id, reason);
}

/* Робочий потік обробки конвеєра мосту */
static void* bridge_worker_routine(void *arg) {
    MessageBusBridge *bridge = (MessageBusBridge*)arg;

    while (bridge->running) {
        BridgeMessage msg;

        pthread_mutex_lock(&bridge->queue.lock);
        while (bridge->queue.count == 0 && bridge->running) {
            pthread_cond_wait(&bridge->queue.not_empty, &bridge->queue.lock);
        }

        if (!bridge->running && bridge->queue.count == 0) {
            pthread_mutex_unlock(&bridge->queue.lock);
            break;
        }

        /* Вилучення повідомлення з кільцевого буфера */
        msg = bridge->queue.slots[bridge->queue.tail];
        bridge->queue.tail = (bridge->queue.tail + 1) % BUFFER_CAPACITY;
        bridge->queue.count--;

        /* Зняття протитиску при досягненні низького водяного знака */
        if (bridge->queue.count <= LOW_WATERMARK && bridge->queue.paused) {
            bridge->queue.paused = false;
            printf("[ПРОТИТИСК] Буфер розвантажено до %zu/%d. Відновлено прийом з входу.\n",
                   bridge->queue.count, BUFFER_CAPACITY);
        }

        pthread_cond_signal(&bridge->queue.not_full);
        pthread_mutex_unlock(&bridge->queue.lock);

        /* Модифікація службових метаданих трасування */
        msg.hop_count++;

        /* Спроба публікації з семантикою Dual-Ack */
        bool published = mock_egress_publish("Cloud_Kafka_Cluster", &msg);
        if (published) {
            /* Подвійне підтвердження: коміт у джерело ЛИШЕ після успіху на виході */
            mock_ingress_commit(msg.ingress_delivery_tag);
            bridge->forwarded_count++;
        } else {
            /* Відправка в DLQ у разі неотримання Egress-ACK */
            mock_quarantine_dlq(&msg, "Egress broker reject / network timeout");
            /* Підтверджуємо джерелу, щоб уникнути блокування вхідної черги */
            mock_ingress_commit(msg.ingress_delivery_tag);
            bridge->quarantine_count++;
        }
    }
    return NULL;
}

/* Ініціалізація та запуск мосту */
void bridge_init(MessageBusBridge *bridge, const char *bus_name) {
    strncpy(bridge->current_bus_name, bus_name, MAX_BUS_NAME_LEN - 1);
    bridge->current_bus_name[MAX_BUS_NAME_LEN - 1] = '\0';
    ring_buffer_init(&bridge->queue);
    bridge->running = true;
    bridge->forwarded_count = 0;
    bridge->quarantine_count = 0;
    pthread_create(&bridge->worker_thread, NULL, bridge_worker_routine, bridge);
}

/* Зупинка та звільнення ресурсів */
void bridge_shutdown(MessageBusBridge *bridge) {
    pthread_mutex_lock(&bridge->queue.lock);
    bridge->running = false;
    pthread_cond_broadcast(&bridge->queue.not_empty);
    pthread_cond_broadcast(&bridge->queue.not_full);
    pthread_mutex_unlock(&bridge->queue.lock);

    pthread_join(bridge->worker_thread, NULL);
    ring_buffer_destroy(&bridge->queue);
}

int main(void) {
    printf("=== Запуск тесту відмовостійкого мосту шин повідомлень ===\n\n");
    MessageBusBridge bridge;
    bridge_init(&bridge, "Factory_Floor_Edge_MQTT");

    /* Тест 1: Звичайна успішна доставка */
    BridgeMessage msg1 = {
        .msg_id = 101, .hop_count = 0, .origin_bus = "Factory_Floor_Edge_MQTT",
        .payload = "SensorData{temperature: 24.5C, pressure: 1013hPa}",
        .payload_len = 49, .ingress_delivery_tag = 1
    };
    bridge_enqueue(&bridge, &msg1);

    /* Тест 2: Повідомлення із зацикленням (повернення на ту саму шину) */
    BridgeMessage loop_msg = {
        .msg_id = 102, .hop_count = 2, .origin_bus = "Factory_Floor_Edge_MQTT",
        .payload = "OrderEvent{id: 5541, action: RECHECK}",
        .payload_len = 37, .ingress_delivery_tag = 2
    };
    BridgeStatus st = bridge_enqueue(&bridge, &loop_msg);
    if (st == BRIDGE_ERR_LOOP_DETECTED) {
        printf("[ЗАХИСТ ВІД ЗАЦИКЛЕННЯ] Повідомлення msg_id=102 відхилено через виявлення петлі маршрутизації!\n");
    }

    /* Тест 3: Пошкоджене повідомлення для тесту карантину DLQ */
    BridgeMessage corrupt_msg = {
        .msg_id = 103, .hop_count = 0, .origin_bus = "Substation_AMQP",
        .payload = "TelemetryPacket{CORRUPT_CHECKSUM}",
        .payload_len = 33, .ingress_delivery_tag = 3
    };
    bridge_enqueue(&bridge, &corrupt_msg);

    /* Тест 4: Серія пакетів для перевірки протитиску (Backpressure) */
    for (int i = 0; i < 14; i++) {
        BridgeMessage burst_msg;
        burst_msg.msg_id = 200 + i;
        burst_msg.hop_count = 0;
        snprintf(burst_msg.origin_bus, MAX_BUS_NAME_LEN, "PLC_Node_%d", i % 3);
        snprintf(burst_msg.payload, MAX_PAYLOAD_SIZE, "VibrationEvent{rpm: %d, amp: 0.12}", 1500 + i * 10);
        burst_msg.payload_len = strlen(burst_msg.payload);
        burst_msg.ingress_delivery_tag = 10 + i;
        bridge_enqueue(&bridge, &burst_msg);
    }

    /* Очікування завершення обробки */
    usleep(400000); /* 400 мс */
    bridge_shutdown(&bridge);

    printf("\n=== Результати роботи мосту ===\n");
    printf("Успішно репліковано у вихідну шину: %" PRIu64 "\n", bridge.forwarded_count);
    printf("Ізольовано в карантині (DLQ):      %" PRIu64 "\n", bridge.quarantine_count);
    printf("Конвеєр мосту зупинено коректно.\n");
    return 0;
}
