// ==================== C ABI (Opaque Pointer) ====================
// engine.h (Публічний API заголовка)
#ifndef ENGINE_H
#define ENGINE_H

#include <stddef.h>

// Непрозорий тип: клієнт бачить лише ім'я структури
typedef struct NetworkEngine NetworkEngine;

NetworkEngine* network_engine_create(const char* host, int port);
void network_engine_destroy(NetworkEngine* engine);
int network_engine_send(NetworkEngine* engine, const void* data, size_t len);

#endif // ENGINE_H

// engine.c (Файл реалізації всередині бібліотеки)
#include "engine.h"
#include <stdlib.h>
#include <string.h>

struct NetworkEngine {
    char host[128];
    int port;
    // Нові поля версії 2.0 додаються сюди абсолютно безпечно!
    int timeout_ms;
    unsigned long packets_sent;
};

NetworkEngine* network_engine_create(const char* host, int port) {
    NetworkEngine* engine = (NetworkEngine*)malloc(sizeof(NetworkEngine));
    if (!engine) return NULL;
    strncpy(engine->host, host, sizeof(engine->host) - 1);
    engine->port = port;
    engine->timeout_ms = 5000;
    engine->packets_sent = 0;
    return engine;
}

void network_engine_destroy(NetworkEngine* engine) {
    free(engine);
}

int network_engine_send(NetworkEngine* engine, const void* data, size_t len) {
    if (!engine) return -1;
    engine->packets_sent++;
    return 0; // Імітація успішної відправки
}
