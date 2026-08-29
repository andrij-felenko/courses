#include "track_pool.h"

#include <stddef.h>

void tracker_pool_init(TrackerFilterPool *pool) {
    if (pool == NULL) {
        return;
    }
    for (int i = 0; i < MAX_TRACKED_OBJECTS; ++i) {
        pool->in_use[i] = false;
        pool->track_ids[i] = -1;
        pool->filters[i].cfg = NULL;
    }
}

int tracker_pool_find(const TrackerFilterPool *pool, int track_id) {
    if (pool == NULL) {
        return -1;
    }
    for (int i = 0; i < MAX_TRACKED_OBJECTS; ++i) {
        if (pool->in_use[i] && pool->track_ids[i] == track_id) {
            return i;
        }
    }
    return -1;
}

ConfidenceFilter *tracker_pool_track(TrackerFilterPool *pool,
                                     int track_id,
                                     const ConfidenceFilterConfig *cfg,
                                     uint32_t now_ms) {
    if (pool == NULL) {
        return NULL;
    }

    const int existing = tracker_pool_find(pool, track_id);
    if (existing >= 0) {
        return &pool->filters[existing];
    }

    for (int i = 0; i < MAX_TRACKED_OBJECTS; ++i) {
        if (pool->in_use[i]) {
            continue;
        }
        /* Слот міг лишитися з чужою історією від попереднього треку —
         * заводимо його з нуля, інакше новий об'єкт успадкував би тривогу. */
        if (!confidence_filter_init(&pool->filters[i], cfg, now_ms)) {
            return NULL; /* Конфігурація непридатна: слот не займаємо. */
        }
        pool->track_ids[i] = track_id;
        pool->in_use[i] = true;
        return &pool->filters[i];
    }

    return NULL; /* Пул вичерпано. */
}

bool tracker_pool_release(TrackerFilterPool *pool, int track_id) {
    const int slot = tracker_pool_find(pool, track_id);
    if (slot < 0) {
        return false;
    }
    pool->in_use[slot] = false;
    pool->track_ids[slot] = -1;
    pool->filters[slot].cfg = NULL;
    return true;
}

unsigned tracker_pool_sweep(TrackerFilterPool *pool, uint32_t timeout_ms, uint32_t now_ms) {
    if (pool == NULL) {
        return 0U;
    }
    unsigned dropped = 0U;
    for (int i = 0; i < MAX_TRACKED_OBJECTS; ++i) {
        if (!pool->in_use[i]) {
            continue;
        }
        if (confidence_filter_idle_ms(&pool->filters[i], now_ms) >= timeout_ms) {
            pool->in_use[i] = false;
            pool->track_ids[i] = -1;
            pool->filters[i].cfg = NULL;
            ++dropped;
        }
    }
    return dropped;
}

bool tracker_pool_any_active(const TrackerFilterPool *pool) {
    if (pool == NULL) {
        return false;
    }
    for (int i = 0; i < MAX_TRACKED_OBJECTS; ++i) {
        if (pool->in_use[i] && confidence_filter_active(&pool->filters[i])) {
            return true;
        }
    }
    return false;
}

unsigned tracker_pool_size(const TrackerFilterPool *pool) {
    if (pool == NULL) {
        return 0U;
    }
    unsigned used = 0U;
    for (int i = 0; i < MAX_TRACKED_OBJECTS; ++i) {
        if (pool->in_use[i]) {
            ++used;
        }
    }
    return used;
}
