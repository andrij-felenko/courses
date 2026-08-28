#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include <pthread.h>
#include <unistd.h>

#define MAX_CHUNKS 1024
#define HOT_TIER_CAPACITY_BYTES (1024 * 1024 * 1024ULL) // 1 GiB
#define HIGH_WATERMARK_RATIO 0.85
#define LOW_WATERMARK_RATIO 0.70
#define TEMPERATURE_HALF_LIFE_SEC 3600.0 // 1 година

typedef enum {
    TIER_HOT = 0,
    TIER_WARM = 1,
    TIER_COLD = 2,
    TIER_ARCHIVE = 3
} storage_tier_t;

typedef enum {
    CHUNK_STATE_ONLINE,
    CHUNK_STATE_MIGRATING,
    CHUNK_STATE_DELETED
} chunk_state_t;

typedef struct {
    uint64_t chunk_id;
    size_t size_bytes;
    storage_tier_t current_tier;
    chunk_state_t state;
    
    // Статистика доступу
    double temperature_score;
    time_t last_access_ts;
    uint64_t access_count;
    
    uint32_t checksum;
    pthread_rwlock_t lock;
} chunk_meta_t;

typedef struct {
    chunk_meta_t chunks[MAX_CHUNKS];
    size_t total_chunks;
    
    uint64_t hot_bytes_used;
    pthread_mutex_t engine_mutex;
    bool is_running;
} tier_engine_t;

// Обчислення згасання температури доступу: S(t) = S(t0) * 2^(-dt / T_half)
static double decay_temperature(double current_score, time_t last_ts, time_t now) {
    double dt = difftime(now, last_ts);
    if (dt <= 0.0) return current_score;
    double decay_factor = pow(2.0, -dt / TEMPERATURE_HALF_LIFE_SEC);
    return current_score * decay_factor;
}

// Фіксація звернення до блоку читачем або транзакцією
void tier_engine_record_access(tier_engine_t *engine, uint64_t chunk_id) {
    if (chunk_id >= engine->total_chunks) return;
    chunk_meta_t *c = &engine->chunks[chunk_id];
    
    pthread_rwlock_wrlock(&c->lock);
    time_t now = time(NULL);
    double decayed = decay_temperature(c->temperature_score, c->last_access_ts, now);
    c->temperature_score = decayed + 1.0;
    c->last_access_ts = now;
    c->access_count++;
    pthread_rwlock_unlock(&c->lock);
}

// Імітація безпечного копіювання даних та обчислення контрольної суми
static bool simulate_tier_transfer(uint64_t chunk_id, storage_tier_t src, storage_tier_t dst, uint32_t *out_chk) {
    usleep(5000); // 5 мс затримки I/O
    *out_chk = (uint32_t)(chunk_id ^ 0xDEADBEEF);
    return true;
}

// Атомарний 4-кроковий конвеєр міграції одного чанка
static bool migrate_single_chunk(tier_engine_t *engine, chunk_meta_t *c, storage_tier_t target_tier) {
    pthread_rwlock_wrlock(&c->lock);
    if (c->state != CHUNK_STATE_ONLINE || c->current_tier == target_tier) {
        pthread_rwlock_unlock(&c->lock);
        return false;
    }
    
    storage_tier_t old_tier = c->current_tier;
    size_t chunk_size = c->size_bytes;
    c->state = CHUNK_STATE_MIGRATING;
    pthread_rwlock_unlock(&c->lock);
    
    // Крок 1 і 2: Копіювання у цільовий ярус і верифікація контрольної суми
    uint32_t target_checksum = 0;
    bool copy_ok = simulate_tier_transfer(c->chunk_id, old_tier, target_tier, &target_checksum);
    
    if (!copy_ok || target_checksum != c->checksum) {
        pthread_rwlock_wrlock(&c->lock);
        c->state = CHUNK_STATE_ONLINE; // Відкат стану при збої
        pthread_rwlock_unlock(&c->lock);
        fprintf(stderr, "[ПОМИЛКА] Збій копіювання або невідповідність CRC чанка %lu\n", c->chunk_id);
        return false;
    }
    
    // Крок 3: Атомарна підміна цільового покажчика в метаданих
    pthread_rwlock_wrlock(&c->lock);
    c->current_tier = target_tier;
    c->state = CHUNK_STATE_ONLINE;
    pthread_rwlock_unlock(&c->lock);
    
    // Крок 4: Звільнення дискового простору старого ярусу (blkdiscard / trim)
    if (old_tier == TIER_HOT) {
        pthread_mutex_lock(&engine->engine_mutex);
        if (engine->hot_bytes_used >= chunk_size) {
            engine->hot_bytes_used -= chunk_size;
        } else {
            engine->hot_bytes_used = 0;
        }
        pthread_mutex_unlock(&engine->engine_mutex);
    }
    
    printf("[ТИРУВАННЯ] Чанк %lu успішно переміщено %d -> %d (%zu байтів)\n",
           c->chunk_id, old_tier, target_tier, chunk_size);
    return true;
}

// Робочий цикл фонового планувальника
void* tiering_scheduler_thread(void *arg) {
    tier_engine_t *engine = (tier_engine_t*)arg;
    
    while (engine->is_running) {
        pthread_mutex_lock(&engine->engine_mutex);
        uint64_t used = engine->hot_bytes_used;
        pthread_mutex_unlock(&engine->engine_mutex);
        
        double current_ratio = (double)used / (double)HOT_TIER_CAPACITY_BYTES;
        
        if (current_ratio > HIGH_WATERMARK_RATIO) {
            printf("[УВАГА] Заповненість Hot ярусу %.1f%% > High Watermark (85%%). Початок витіснення.\n",
                   current_ratio * 100.0);
            
            time_t now = time(NULL);
            
            // Пошук найхолоднішого чанка серед активних у гарячому ярусі
            while (current_ratio > LOW_WATERMARK_RATIO && engine->is_running) {
                int64_t coldest_id = -1;
                double min_temp = 1e18;
                
                for (size_t i = 0; i < engine->total_chunks; i++) {
                    chunk_meta_t *c = &engine->chunks[i];
                    pthread_rwlock_rdlock(&c->lock);
                    if (c->state == CHUNK_STATE_ONLINE && c->current_tier == TIER_HOT) {
                        double t = decay_temperature(c->temperature_score, c->last_access_ts, now);
                        if (t < min_temp) {
                            min_temp = t;
                            coldest_id = (int64_t)i;
                        }
                    }
                    pthread_rwlock_unlock(&c->lock);
                }
                
                if (coldest_id == -1) break; // Немає доступних кандидатів
                
                migrate_single_chunk(engine, &engine->chunks[coldest_id], TIER_WARM);
                
                pthread_mutex_lock(&engine->engine_mutex);
                used = engine->hot_bytes_used;
                pthread_mutex_unlock(&engine->engine_mutex);
                current_ratio = (double)used / (double)HOT_TIER_CAPACITY_BYTES;
            }
            
            printf("[ІНФО] Витіснення завершено. Поточна заповненість Hot ярусу: %.1f%%\n",
                   current_ratio * 100.0);
        }
        
        sleep(1); // Період опитування датчика
    }
    return NULL;
}
