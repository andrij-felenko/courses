#include <stdbool.h>

#define MAX_SIGNING_STREAMS 16

typedef struct {
    uint8_t  sysid;
    uint8_t  compid;
    uint8_t  link_id;
    bool     active;
    uint64_t last_timestamp;
} signing_stream_entry_t;

typedef struct {
    signing_stream_entry_t entries[MAX_SIGNING_STREAMS];
} stream_table_t;

void stream_table_init(stream_table_t *table) {
    memset(table, 0, sizeof(stream_table_t));
}

// Пошук або виділення слота для вхідного потоку
signing_stream_entry_t* stream_table_get(stream_table_t *table, uint8_t sysid, uint8_t compid, uint8_t link_id) {
    // 1. Пошук існуючого активного потоку
    for (size_t i = 0; i < MAX_SIGNING_STREAMS; ++i) {
        if (table->entries[i].active &&
            table->entries[i].sysid == sysid &&
            table->entries[i].compid == compid &&
            table->entries[i].link_id == link_id) {
            return &table->entries[i];
        }
    }

    // 2. Виділення першого вільного слота для нового відправника
    for (size_t i = 0; i < MAX_SIGNING_STREAMS; ++i) {
        if (!table->entries[i].active) {
            table->entries[i].sysid = sysid;
            table->entries[i].compid = compid;
            table->entries[i].link_id = link_id;
            table->entries[i].active = true;
            table->entries[i].last_timestamp = 0;
            return &table->entries[i];
        }
    }

    return NULL; // Таблиця заповнена (захист від вичерпання пам'яті)
}
