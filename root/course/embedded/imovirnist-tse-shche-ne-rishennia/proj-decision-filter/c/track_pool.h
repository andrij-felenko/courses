#ifndef TRACK_POOL_H
#define TRACK_POOL_H

#include "confidence_filter.h"

/* Скільки одночасних треків веде супровід. Пам'ять під пул виділяється статично:
 * malloc у контурі реального часу заборонений (MISRA, DO-178C). */
#define MAX_TRACKED_OBJECTS 32

typedef struct {
    ConfidenceFilter filters[MAX_TRACKED_OBJECTS];
    int              track_ids[MAX_TRACKED_OBJECTS];
    bool             in_use[MAX_TRACKED_OBJECTS];
} TrackerFilterPool;

/* Позначити всі слоти вільними. */
void tracker_pool_init(TrackerFilterPool *pool);

/* Знайти слот за ідентифікатором треку; -1, якщо такого треку в пулі немає. */
int tracker_pool_find(const TrackerFilterPool *pool, int track_id);

/* Фільтр для треку: наявний або щойно заведений у вільному слоті.
 * NULL означає, що пул вичерпано — виклик мусить це обробити, бо мовчазна
 * втрата треку в системі гальмування коштує дорожче за пропущений кадр. */
ConfidenceFilter *tracker_pool_track(TrackerFilterPool *pool,
                                     int track_id,
                                     const ConfidenceFilterConfig *cfg,
                                     uint32_t now_ms);

/* Звільнити слот вручну (супровід сам оголосив трек закінченим). */
bool tracker_pool_release(TrackerFilterPool *pool, int track_id);

/* Звільнити слоти, які не оновлювалися довше за timeout_ms.
 * Повертає кількість прибраних треків. */
unsigned tracker_pool_sweep(TrackerFilterPool *pool, uint32_t timeout_ms, uint32_t now_ms);

/* Зведена команда на виконавчі органи: тривога хоча б за одним треком —
 * тривога для всього апарата. */
bool tracker_pool_any_active(const TrackerFilterPool *pool);

/* Скільки слотів зайнято. */
unsigned tracker_pool_size(const TrackerFilterPool *pool);

#endif /* TRACK_POOL_H */
