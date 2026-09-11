#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <pthread.h>
#include <time.h>
#include <errno.h>

// Декларативний контракт проєкції полів (FieldMask)
typedef uint32_t FieldMask;

typedef struct {
    uint32_t sensor_id;
    int64_t  timestamp_ns;
    float    temperature_celsius;
    float    battery_voltage;
    uint32_t status_flags;
} SensorReading;

// Функція обробки/відправлення пакунка через межу
typedef void (*FlushCallback)(const SensorReading* batch, size_t count, uint32_t field_mask, void* user_data);

typedef struct {
    SensorReading* active_buffer;
    SensorReading* flush_buffer;
    size_t         capacity;
    size_t         count;
    size_t         max_batch_size;
    long           timeout_ms;
    uint32_t       field_mask;
    bool           enable_conflation;
    bool           running;

    FlushCallback  flush_cb;
    void*          user_data;

    pthread_mutex_t mutex;
    pthread_cond_t  cv_worker;
    pthread_cond_t  cv_producer;
    pthread_t       worker_thread;
} AdaptiveBatcher;

// Допоміжна функція додавання мілісекунд до структури timespec
static void timespec_add_ms(struct timespec* ts, long ms) {
    ts->tv_sec += ms / 1000;
    ts->tv_nsec += (ms % 1000) * 1000000L;
    if (ts->tv_nsec >= 1000000000L) {
        ts->tv_sec += 1;
        ts->tv_nsec -= 1000000000L;
    }
}

// Робочий потік: очікує досягнення ліміту або спливу таймауту
static void* batcher_worker_routine(void* arg) {
    AdaptiveBatcher* b = (AdaptiveBatcher*)arg;

    pthread_mutex_lock(&b->mutex);
    while (b->running) {
        // Якщо буфер порожній, чекаємо появи першого елемента
        while (b->running && b->count == 0) {
            pthread_cond_wait(&b->cv_worker, &b->mutex);
        }
        if (!b->running && b->count == 0) {
            break;
        }

        // Обчислюємо абсолютний дедлайн очікування
        struct timespec deadline;
        clock_gettime(CLOCK_REALTIME, &deadline);
        timespec_add_ms(&deadline, b->timeout_ms);

        // Чекаємо, поки буфер не наповниться до порогу N_batch або не спливе T_wait
        while (b->running && b->count < b->max_batch_size) {
            int res = pthread_cond_timedwait(&b->cv_worker, &b->mutex, &deadline);
            if (res == ETIMEDOUT) {
                break; // Спрацював поріг часу очікування
            }
        }

        if (b->count > 0) {
            // Швидкий обмін буферів (buffer swap) для мінімізації блокування
            SensorReading* temp = b->active_buffer;
            b->active_buffer = b->flush_buffer;
            b->flush_buffer = temp;

            size_t batch_count = b->count;
            b->count = 0;

            // Сповіщаємо виробників про звільнення місця (зворотний тиск спадає)
            pthread_cond_broadcast(&b->cv_producer);

            // Виконуємо відправлення без утримання м'ютекса
            pthread_mutex_unlock(&b->mutex);
            if (b->flush_cb) {
                b->flush_cb(b->flush_buffer, batch_count, b->field_mask, b->user_data);
            }
            pthread_mutex_lock(&b->mutex);
        }
    }
    pthread_mutex_unlock(&b->mutex);
    return NULL;
}

// Ініціалізація шлюзу
AdaptiveBatcher* batcher_create(size_t capacity, size_t max_batch_size, long timeout_ms,
                                uint32_t field_mask, bool enable_conflation,
                                FlushCallback flush_cb, void* user_data) {
    AdaptiveBatcher* b = (AdaptiveBatcher*)malloc(sizeof(AdaptiveBatcher));
    if (!b) return NULL;

    b->capacity = capacity;
    b->max_batch_size = (max_batch_size > capacity) ? capacity : max_batch_size;
    b->timeout_ms = timeout_ms;
    b->field_mask = field_mask;
    b->enable_conflation = enable_conflation;
    b->count = 0;
    b->running = true;
    b->flush_cb = flush_cb;
    b->user_data = user_data;

    b->active_buffer = (SensorReading*)malloc(capacity * sizeof(SensorReading));
    b->flush_buffer = (SensorReading*)malloc(capacity * sizeof(SensorReading));

    pthread_mutex_init(&b->mutex, NULL);
    pthread_cond_init(&b->cv_worker, NULL);
    pthread_cond_init(&b->cv_producer, NULL);

    pthread_create(&b->worker_thread, NULL, batcher_worker_routine, b);
    return b;
}

// Потокобезпечне додавання запису зі згортанням стану та зворотним тиском
bool batcher_push(AdaptiveBatcher* b, const SensorReading* reading) {
    pthread_mutex_lock(&b->mutex);
    if (!b->running) {
        pthread_mutex_unlock(&b->mutex);
        return false;
    }

    // Тактика згортання стану (conflation): оновлюємо наявний запис датчика на місці
    if (b->enable_conflation) {
        for (size_t i = 0; i < b->count; ++i) {
            if (b->active_buffer[i].sensor_id == reading->sensor_id) {
                b->active_buffer[i] = *reading;
                pthread_mutex_unlock(&b->mutex);
                return true;
            }
        }
    }

    // Тактика реактивного зворотного тиску: блокуємо виробника при переповненні
    while (b->running && b->count >= b->capacity) {
        pthread_cond_wait(&b->cv_producer, &b->mutex);
    }
    if (!b->running) {
        pthread_mutex_unlock(&b->mutex);
        return false;
    }

    b->active_buffer[b->count++] = *reading;

    // Якщо досягли стелі N_batch або додали перший елемент — будимо фоновий потік
    if (b->count >= b->max_batch_size || b->count == 1) {
        pthread_cond_signal(&b->cv_worker);
    }

    pthread_mutex_unlock(&b->mutex);
    return true;
}

// Зупинка та вивільнення ресурсів шлюзу
void batcher_destroy(AdaptiveBatcher* b) {
    if (!b) return;

    pthread_mutex_lock(&b->mutex);
    b->running = false;
    pthread_cond_broadcast(&b->cv_worker);
    pthread_cond_broadcast(&b->cv_producer);
    pthread_mutex_unlock(&b->mutex);

    pthread_join(b->worker_thread, NULL);

    pthread_mutex_destroy(&b->mutex);
    pthread_cond_destroy(&b->cv_worker);
    pthread_cond_destroy(&b->cv_producer);

    free(b->active_buffer);
    free(b->flush_buffer);
    free(b);
}
