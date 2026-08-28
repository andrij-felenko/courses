#include "critical_section.h"
#include <string.h>

typedef struct {
    int32_t  latitude;
    int32_t  longitude;
    int32_t  altitude_mm;
    uint64_t timestamp_us;
} navigation_data_t;

static navigation_data_t g_nav_data;

/* Оновлення даних: може викликатися з будь-якого контексту */
void navigation_update(int32_t lat, int32_t lon, int32_t alt, uint64_t ts) {
    critical_section_t cs = critical_section_enter();
    
    g_nav_data.latitude = lat;
    g_nav_data.longitude = lon;
    g_nav_data.altitude_mm = alt;
    g_nav_data.timestamp_us = ts;
    
    critical_section_exit(cs);
}

/* Безпечне копіювання узгодженого знімка структури */
bool navigation_get_snapshot(navigation_data_t *out_data) {
    if (out_data == NULL) {
        return false;
    }
    
    critical_section_t cs = critical_section_enter();
    *out_data = g_nav_data; // Атомарне копіювання всіх полів без ризику розриву
    critical_section_exit(cs);
    
    return true;
}
