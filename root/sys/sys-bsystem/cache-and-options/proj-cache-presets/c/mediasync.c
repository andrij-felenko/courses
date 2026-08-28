/* src/mediasync.c — чиста реалізація мовою C11 */
#include "mediasync_config.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    size_t buffer_capacity;
    char network_backend[32];
    int vaapi_enabled;
    int metrics_port;
} MediaSyncCore;

MediaSyncCore* mediasync_create_instance(void) {
    MediaSyncCore* core = (MediaSyncCore*)malloc(sizeof(MediaSyncCore));
    if (!core) {
        return NULL;
    }

    core->buffer_capacity = MEDIASYNC_BUFFER_SIZE;
    core->metrics_port = MEDIASYNC_DEFAULT_PORT;
    
    strncpy(core->network_backend, MEDIASYNC_NETWORK_BACKEND, sizeof(core->network_backend) - 1);
    core->network_backend[sizeof(core->network_backend) - 1] = '\0';

#ifdef MEDIASYNC_USE_VAAPI
    core->vaapi_enabled = 1;
#else
    core->vaapi_enabled = 0;
#endif

#ifdef MEDIASYNC_ENABLE_LOGGING
    printf("[mediasync-C] Ініціалізація v%s | Бекенд: %s | Буфер: %zu байт | VA-API: %s\n",
           MEDIASYNC_VERSION_STRING,
           core->network_backend,
           core->buffer_capacity,
           core->vaapi_enabled ? "АКТИВНО" : "ВИМКНЕНО");
#endif

    return core;
}

void mediasync_destroy_instance(MediaSyncCore* core) {
    if (core) {
        free(core);
    }
}
