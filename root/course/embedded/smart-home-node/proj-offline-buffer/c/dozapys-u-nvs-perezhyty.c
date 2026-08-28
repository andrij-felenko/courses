#include "nvs.h"

#define EVNVS_NS  "evq"        // окремий простір імен під журнал подій

// Записати одну подію в NVS-слот, що відповідає її позиції в кільці.
static void evq_persist_one(const event_t *e) {
    nvs_handle_t h;
    if (nvs_open(EVNVS_NS, NVS_READWRITE, &h) != ESP_OK) return;

    char key[8];
    // Слот у флеші = позиція перед head (куди щойно поклали в RAM-кільці).
    uint16_t slot = (g_evq.head + EVQ_CAP - 1) % EVQ_CAP;
    snprintf(key, sizeof key, "ev%u", slot);

    nvs_set_blob(h, key, e, sizeof(*e));         // сам запис події
    nvs_set_u32(h, "seq", g_evq.next_seq);       // докуди дійшли номери
    nvs_commit(h);                                // без commit — лишиться в RAM-кеші
    nvs_close(h);
}
