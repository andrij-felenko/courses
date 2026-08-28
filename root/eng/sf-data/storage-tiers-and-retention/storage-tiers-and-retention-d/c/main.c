#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>

typedef enum { TIER_HOT, TIER_WARM, TIER_COLD } tier_t;
typedef enum { STATE_ONLINE, STATE_MIGRATING } state_t;

typedef struct {
    uint64_t chunk_id;
    tier_t current_tier;
    state_t state;
    uint32_t checksum;
    pthread_rwlock_t lock;
} chunk_descriptor_t;

// Атомарна підміна ярусу після завершення фонового копіювання
bool commit_chunk_migration(chunk_descriptor_t *chunk, tier_t new_tier, uint32_t verified_crc) {
    pthread_rwlock_wrlock(&chunk->lock);
    
    // Перевірка інваріантів перед фіксацією
    if (chunk->state != STATE_MIGRATING || chunk->checksum != verified_crc) {
        chunk->state = STATE_ONLINE; // Відкат стану при невідповідності
        pthread_rwlock_unlock(&chunk->lock);
        return false;
    }
    
    chunk->current_tier = new_tier;
    chunk->state = STATE_ONLINE;
    pthread_rwlock_unlock(&chunk->lock);
    return true;
}
