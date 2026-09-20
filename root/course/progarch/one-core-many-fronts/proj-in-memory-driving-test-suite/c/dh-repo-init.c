#ifndef DH_MEMORY_DOUBLES_H
#define DH_MEMORY_DOUBLES_H

#include <string.h>
#include <stdbool.h>

#define DH_MAX_ZONES 16
#define DH_MAX_EVENTS 32

typedef struct {
    char id[32];
    char pin_code[16];
    bool has_open_sensors;
    bool is_armed;
} DhSecurityZone;

typedef struct {
    DhSecurityZone items[DH_MAX_ZONES];
    int count;
} DhInMemoryZoneRepository;

static inline void dh_repo_init(DhInMemoryZoneRepository* repo) {
    repo->count = 0;
}

static inline bool dh_repo_save(DhInMemoryZoneRepository* repo, const DhSecurityZone* zone) {
    for (int i = 0; i < repo->count; ++i) {
        if (strcmp(repo->items[i].id, zone->id) == 0) {
            repo->items[i] = *zone;
            return true;
        }
    }
    if (repo->count < DH_MAX_ZONES) {
        repo->items[repo->count++] = *zone;
        return true;
    }
    return false;
}

typedef struct {
    char events[DH_MAX_EVENTS][64];
    int count;
} DhActuatorEventSpy;

static inline void dh_spy_init(DhActuatorEventSpy* spy) {
    spy->count = 0;
}

static inline void dh_spy_record(DhActuatorEventSpy* spy, const char* event_name) {
    if (spy->count < DH_MAX_EVENTS) {
        strncpy(spy->events[spy->count++], event_name, 63);
    }
}

#endif
