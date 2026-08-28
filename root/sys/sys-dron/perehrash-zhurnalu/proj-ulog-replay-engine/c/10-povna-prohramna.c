#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ULOG_MAGIC_SIZE 8
#define ULOG_MAX_FORMATS 128
#define ULOG_MAX_SUBSCRIPTIONS 256
#define ULOG_MAX_NAME_LEN 64
#define REPLAY_QUEUE_CAPACITY 2048

/* Магічна сигнатура початку файлу ULog */
static const uint8_t ULOG_MAGIC_HEADER[ULOG_MAGIC_SIZE] = {
    0x55, 0x4C, 0x6F, 0x67, 0x01, 0x12, 0x35, 0x00
};

/* Коди типів секцій повідомлень ULog */
typedef enum {
    ULOG_MSG_FLAG_BITS      = 'B',
    ULOG_MSG_FORMAT         = 'F',
    ULOG_MSG_INFO           = 'I',
    ULOG_MSG_INFO_MULTIPLE  = 'M',
    ULOG_MSG_PARAMETER      = 'P',
    ULOG_MSG_ADD_LOGGED_MSG = 'A',
    ULOG_MSG_REMOVE_LOGGED  = 'R',
    ULOG_MSG_DATA           = 'D',
    ULOG_MSG_DROPOUT        = 'S',
    ULOG_MSG_LOG_MESSAGE    = 'L'
} ulog_message_type_t;

/* Опис зареєстрованого формату повідомлення ('F') */
typedef struct {
    char name[ULOG_MAX_NAME_LEN];
    char fields[512];
    uint16_t message_size;
} ulog_format_t;

/* Опис активної підписки на топік ('A') */
typedef struct {
    uint16_t msg_id;
    uint8_t multi_id;
    int format_index;
} ulog_subscription_t;

/* Структура кадру телеметрії в черзі переграшу */
typedef struct {
    uint64_t timestamp_us;
    uint16_t msg_id;
    uint8_t multi_id;
    char name[ULOG_MAX_NAME_LEN];
    uint16_t size;
    uint8_t payload[256];
} replay_frame_t;

/* Пріоритетна черга на базі двійкової мінімальної купи (Min-Heap) */
typedef struct {
    replay_frame_t frames[REPLAY_QUEUE_CAPACITY];
    size_t count;
} replay_priority_queue_t;

/* Тип зворотного виклику під час диспетчеризації кадру */
typedef void (*replay_dispatch_cb_t)(uint64_t t_sim, const char *topic, 
                                     uint8_t instance, const uint8_t *data, 
                                     uint16_t size, void *user_data);

/* Контекст рушія переграшу ULog */
typedef struct {
    FILE *file_handle;
    uint64_t start_time_us;
    uint64_t current_sim_time_us;
    
    ulog_format_t formats[ULOG_MAX_FORMATS];
    size_t format_count;
    
    ulog_subscription_t subscriptions[ULOG_MAX_SUBSCRIPTIONS];
    size_t subscription_count;
    
    replay_priority_queue_t queue;
    
    replay_dispatch_cb_t callback;
    void *callback_user_data;
    
    uint64_t total_data_messages_parsed;
    uint64_t total_dropouts_count;
    uint64_t total_dropout_duration_ms;
} ulog_replay_engine_t;

/* ------------------- Операції з чергою пріоритетів (Min-Heap) ------------------- */

static void pq_init(replay_priority_queue_t *pq) {
    pq->count = 0;
}

static bool pq_push(replay_priority_queue_t *pq, const replay_frame_t *frame) {
    if (pq->count >= REPLAY_QUEUE_CAPACITY) {
        return false;
    }
    size_t i = pq->count++;
    while (i > 0) {
        size_t parent = (i - 1) / 2;
        if (pq->frames[parent].timestamp_us <= frame->timestamp_us) {
            break;
        }
        pq->frames[i] = pq->frames[parent];
        i = parent;
    }
    pq->frames[i] = *frame;
    return true;
}

static bool pq_pop(replay_priority_queue_t *pq, replay_frame_t *out_frame) {
    if (pq->count == 0) return false;
    *out_frame = pq->frames[0];
    replay_frame_t last = pq->frames[--pq->count];
    if (pq->count == 0) return true;

    size_t i = 0;
    while (i * 2 + 1 < pq->count) {
        size_t left = i * 2 + 1;
        size_t right = left + 1;
        size_t smallest = left;
        if (right < pq->count && pq->frames[right].timestamp_us < pq->frames[left].timestamp_us) {
            smallest = right;
        }
        if (last.timestamp_us <= pq->frames[smallest].timestamp_us) {
            break;
        }
        pq->frames[i] = pq->frames[smallest];
        i = smallest;
    }
    pq->frames[i] = last;
    return true;
}

/* ------------------- Реалізація парсера ULog ------------------- */

bool ulog_engine_init(ulog_replay_engine_t *engine, const char *filepath, 
                      replay_dispatch_cb_t cb, void *user_data) {
    memset(engine, 0, sizeof(*engine));
    pq_init(&engine->queue);
    engine->callback = cb;
    engine->callback_user_data = user_data;

    engine->file_handle = fopen(filepath, "rb");
    if (!engine->file_handle) {
        fprintf(stderr, "[ULog Engine] Помилка: не вдалося відкрити файл %s\n", filepath);
        return false;
    }

    /* Зчитування та валідація 16-байтного заголовка */
    uint8_t header[16];
    if (fread(header, 1, 16, engine->file_handle) != 16) {
        fprintf(stderr, "[ULog Engine] Помилка: файл занадто малий для заголовка ULog\n");
        fclose(engine->file_handle);
        return false;
    }

    if (memcmp(header, ULOG_MAGIC_HEADER, 7) != 0) {
        fprintf(stderr, "[ULog Engine] Помилка: невірна магічна сигнатура ULog\n");
        fclose(engine->file_handle);
        return false;
    }

    memcpy(&engine->start_time_us, &header[7], sizeof(uint64_t));
    engine->current_sim_time_us = engine->start_time_us;
    printf("[ULog Engine] Успішна ініціалізація. Час старту: %llu мкс\n", 
           (unsigned long long)engine->start_time_us);

    return true;
}

static void ulog_handle_format(ulog_replay_engine_t *engine, const uint8_t *payload, uint16_t size) {
    if (engine->format_count >= ULOG_MAX_FORMATS) return;
    char buffer[1024];
    uint16_t copy_len = size < sizeof(buffer) - 1 ? size : sizeof(buffer) - 1;
    memcpy(buffer, payload, copy_len);
    buffer[copy_len] = '\0';

    char *colon = strchr(buffer, ':');
    if (!colon) return;

    *colon = '\0';
    ulog_format_t *fmt = &engine->formats[engine->format_count];
    strncpy(fmt->name, buffer, ULOG_MAX_NAME_LEN - 1);
    strncpy(fmt->fields, colon + 1, sizeof(fmt->fields) - 1);
    engine->format_count++;
}

static void ulog_handle_subscription(ulog_replay_engine_t *engine, const uint8_t *payload, uint16_t size) {
    if (size < 4 || engine->subscription_count >= ULOG_MAX_SUBSCRIPTIONS) return;
    uint8_t multi_id = payload[0];
    uint16_t msg_id = payload[1] | ((uint16_t)payload[2] << 8);
    const char *name = (const char *)&payload[3];

    int fmt_idx = -1;
    for (size_t i = 0; i < engine->format_count; i++) {
        if (strcmp(engine->formats[i].name, name) == 0) {
            fmt_idx = (int)i;
            break;
        }
    }

    if (fmt_idx >= 0) {
        ulog_subscription_t *sub = &engine->subscriptions[engine->subscription_count++];
        sub->msg_id = msg_id;
        sub->multi_id = multi_id;
        sub->format_index = fmt_idx;
    }
}

static void ulog_handle_data(ulog_replay_engine_t *engine, const uint8_t *payload, uint16_t size) {
    if (size < 10) return; /* msg_id (2) + timestamp (8) */
    uint16_t msg_id = payload[0] | ((uint16_t)payload[1] << 8);

    const ulog_subscription_t *sub = NULL;
    for (size_t i = 0; i < engine->subscription_count; i++) {
        if (engine->subscriptions[i].msg_id == msg_id) {
            sub = &engine->subscriptions[i];
            break;
        }
    }
    if (!sub) return;

    uint64_t timestamp = 0;
    memcpy(&timestamp, &payload[2], sizeof(uint64_t));

    replay_frame_t frame;
    frame.timestamp_us = timestamp;
    frame.msg_id = msg_id;
    frame.multi_id = sub->multi_id;
    strncpy(frame.name, engine->formats[sub->format_index].name, ULOG_MAX_NAME_LEN - 1);
    frame.size = size - 2;
    if (frame.size > sizeof(frame.payload)) {
        frame.size = sizeof(frame.payload);
    }
    memcpy(frame.payload, &payload[2], frame.size);

    if (!pq_push(&engine->queue, &frame)) {
        /* Якщо черга заповнена, скидаємо найстаріший кадр у диспетчер */
        replay_frame_t oldest;
        if (pq_pop(&engine->queue, &oldest)) {
            if (engine->callback) {
                engine->current_sim_time_us = oldest.timestamp_us;
                engine->callback(engine->current_sim_time_us, oldest.name, 
                                oldest.multi_id, oldest.payload, 
                                oldest.size, engine->callback_user_data);
            }
        }
        pq_push(&engine->queue, &frame);
    }
    engine->total_data_messages_parsed++;
}

static void ulog_handle_dropout(ulog_replay_engine_t *engine, const uint8_t *payload, uint16_t size) {
    if (size < 2) return;
    uint16_t duration_ms = payload[0] | ((uint16_t)payload[1] << 8);
    engine->total_dropouts_count++;
    engine->total_dropout_duration_ms += duration_ms;
}

/* Покрокове читання та відтворення файлу до кінця */
void ulog_engine_run(ulog_replay_engine_t *engine) {
    uint8_t chunk_header[3];

    while (fread(chunk_header, 1, 3, engine->file_handle) == 3) {
        uint16_t msg_size = chunk_header[0] | ((uint16_t)chunk_header[1] << 8);
        uint8_t msg_type = chunk_header[2];

        uint8_t *payload = (uint8_t *)malloc(msg_size);
        if (!payload) {
            fprintf(stderr, "[ULog Engine] Помилка виділення пам'яті під payload (%u байтів)\n", msg_size);
            break;
        }

        if (fread(payload, 1, msg_size, engine->file_handle) != msg_size) {
            free(payload);
            break;
        }

        switch (msg_type) {
            case ULOG_MSG_FORMAT:
                ulog_handle_format(engine, payload, msg_size);
                break;
            case ULOG_MSG_ADD_LOGGED_MSG:
                ulog_handle_subscription(engine, payload, msg_size);
                break;
            case ULOG_MSG_DATA:
                ulog_handle_data(engine, payload, msg_size);
                break;
            case ULOG_MSG_DROPOUT:
                ulog_handle_dropout(engine, payload, msg_size);
                break;
            default:
                break;
        }
        free(payload);
    }

    /* Скидання залишкових повідомлень з пріоритетної черги */
    replay_frame_t frame;
    while (pq_pop(&engine->queue, &frame)) {
        if (engine->callback) {
            engine->current_sim_time_us = frame.timestamp_us;
            engine->callback(engine->current_sim_time_us, frame.name, 
                             frame.multi_id, frame.payload, 
                             frame.size, engine->callback_user_data);
        }
    }

    printf("[ULog Engine] Відтворення завершено. Оброблено повідомлень: %llu, Дропаутів: %llu (разом %llu мс)\n",
           (unsigned long long)engine->total_data_messages_parsed,
           (unsigned long long)engine->total_dropouts_count,
           (unsigned long long)engine->total_dropout_duration_ms);

    fclose(engine->file_handle);
    engine->file_handle = NULL;
}
