/* C: Виділення шва та канарейковий маршрутизатор з подвійним записом */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

/* Модель телеметрії пристрою */
typedef struct {
    long device_id;
    double temperature;
    double humidity;
    long timestamp;
} telemetry_payload_t;

/* Результат обробки */
typedef struct {
    bool success;
    int status_code;
    char error_msg[64];
} process_result_t;

/* 1. Інтерфейс (шов у коді) через вказівники на функції */
typedef struct telemetry_provider {
    process_result_t (*process)(struct telemetry_provider *self, const telemetry_payload_t *data);
    void (*destroy)(struct telemetry_provider *self);
    void *ctx;
} telemetry_provider_t;

/* --- Стара реалізація (внутрішній модуль моноліта) --- */
typedef struct {
    char db_connection_str[128];
} legacy_monolith_ctx_t;

static process_result_t legacy_process(telemetry_provider_t *self, const telemetry_payload_t *data) {
    legacy_monolith_ctx_t *ctx = (legacy_monolith_ctx_t *)self->ctx;
    process_result_t res = { .success = true, .status_code = 200, .error_msg = "" };
    
    /* Симуляція запису в спільну монолітну БД */
    printf("[LEGACY MONOLITH] Writing to DB (%s): Device=%ld, Temp=%.1f C\n",
           ctx->db_connection_str, data->device_id, data->temperature);
    return res;
}

static void legacy_destroy(telemetry_provider_t *self) {
    if (self) {
        free(self->ctx);
        free(self);
    }
}

telemetry_provider_t *telemetry_provider_create_legacy(const char *db_conn) {
    telemetry_provider_t *p = (telemetry_provider_t *)malloc(sizeof(telemetry_provider_t));
    legacy_monolith_ctx_t *ctx = (legacy_monolith_ctx_t *)malloc(sizeof(legacy_monolith_ctx_t));
    strncpy(ctx->db_connection_str, db_conn, sizeof(ctx->db_connection_str) - 1);
    
    p->process = legacy_process;
    p->destroy = legacy_destroy;
    p->ctx = ctx;
    return p;
}

/* --- Нова реалізація (HTTP/gRPC клієнт до мікросервісу) --- */
typedef struct {
    char service_endpoint[128];
    int timeout_ms;
} remote_service_ctx_t;

static process_result_t remote_process(telemetry_provider_t *self, const telemetry_payload_t *data) {
    remote_service_ctx_t *ctx = (remote_service_ctx_t *)self->ctx;
    process_result_t res = { .success = true, .status_code = 201, .error_msg = "" };
    
    /* Симуляція мережевого RPC-виклику до нового сервісу */
    printf("[NEW MICROSERVICE] POST %s (timeout=%dms): Device=%ld, Temp=%.1f C\n",
           ctx->service_endpoint, ctx->timeout_ms, data->device_id, data->temperature);
    return res;
}

static void remote_destroy(telemetry_provider_t *self) {
    if (self) {
        free(self->ctx);
        free(self);
    }
}

telemetry_provider_t *telemetry_provider_create_remote(const char *endpoint, int timeout_ms) {
    telemetry_provider_t *p = (telemetry_provider_t *)malloc(sizeof(telemetry_provider_t));
    remote_service_ctx_t *ctx = (remote_service_ctx_t *)malloc(sizeof(remote_service_ctx_t));
    strncpy(ctx->service_endpoint, endpoint, sizeof(ctx->service_endpoint) - 1);
    ctx->timeout_ms = timeout_ms;
    
    p->process = remote_process;
    p->destroy = remote_destroy;
    p->ctx = ctx;
    return p;
}

/* --- Strangler Router: Канарейка + Shadow Read + Dual Write --- */
typedef struct {
    telemetry_provider_t *legacy;
    telemetry_provider_t *remote;
    int canary_percent; /* 0..100 */
    bool shadow_read_enabled;
} strangler_router_ctx_t;

static process_result_t strangler_process(telemetry_provider_t *self, const telemetry_payload_t *data) {
    strangler_router_ctx_t *ctx = (strangler_router_ctx_t *)self->ctx;
    
    /* Проста детермінована перевірка канарейки на основі device_id */
    int bucket = (int)(data->device_id % 100);
    bool use_new_service = (bucket < ctx->canary_percent);
    
    if (use_new_service) {
        printf("[ROUTER] Routing Device %ld -> NEW SERVICE (Canary bucket %d < %d%%)\n",
               data->device_id, bucket, ctx->canary_percent);
        process_result_t res = ctx->remote->process(ctx->remote, data);
        
        /* Shadow write/read у старову систему для верифікації якщо увімкнено */
        if (ctx->shadow_read_enabled) {
            printf("[ROUTER] Performing Shadow Write to Legacy for verification...\n");
            ctx->legacy->process(ctx->legacy, data);
        }
        return res;
    } else {
        printf("[ROUTER] Routing Device %ld -> LEGACY MONOLITH (Canary bucket %d >= %d%%)\n",
               data->device_id, bucket, ctx->canary_percent);
        return ctx->legacy->process(ctx->legacy, data);
    }
}

static void strangler_destroy(telemetry_provider_t *self) {
    if (self) {
        strangler_router_ctx_t *ctx = (strangler_router_ctx_t *)self->ctx;
        if (ctx->legacy) ctx->legacy->destroy(ctx->legacy);
        if (ctx->remote) ctx->remote->destroy(ctx->remote);
        free(ctx);
        free(self);
    }
}

telemetry_provider_t *telemetry_provider_create_strangler(
    telemetry_provider_t *legacy,
    telemetry_provider_t *remote,
    int canary_percent,
    bool shadow_read) 
{
    telemetry_provider_t *p = (telemetry_provider_t *)malloc(sizeof(telemetry_provider_t));
    strangler_router_ctx_t *ctx = (strangler_router_ctx_t *)malloc(sizeof(strangler_router_ctx_t));
    ctx->legacy = legacy;
    ctx->remote = remote;
    ctx->canary_percent = canary_percent;
    ctx->shadow_read_enabled = shadow_read;
    
    p->process = strangler_process;
    p->destroy = strangler_destroy;
    p->ctx = ctx;
    return p;
}

int main(void) {
    printf("=== STRANGLER MIGRATION DEMO ===\n");
    
    telemetry_provider_t *legacy = telemetry_provider_create_legacy("postgres://localhost:5432/monolith");
    telemetry_provider_t *remote = telemetry_provider_create_remote("http://telemetry-service.internal/api/v1", 200);
    
    /* Налаштовуємо роутер: 20% трафіку на новий сервіс, з увімкненим shadow-записом */
    telemetry_provider_t *router = telemetry_provider_create_strangler(legacy, remote, 20, true);
    
    telemetry_payload_t batch[] = {
        { .device_id = 105, .temperature = 22.4, .humidity = 45.0, .timestamp = 1700000001 }, /* 5% < 20% -> NEW */
        { .device_id = 142, .temperature = 19.8, .humidity = 50.1, .timestamp = 1700000002 }, /* 42% >= 20% -> LEGACY */
        { .device_id = 119, .temperature = 25.1, .humidity = 40.2, .timestamp = 1700000003 }  /* 19% < 20% -> NEW */
    };
    
    for (size_t i = 0; i < sizeof(batch)/sizeof(batch[0]); i++) {
        router->process(router, &batch[i]);
    }
    
    router->destroy(router);
    return 0;
}
