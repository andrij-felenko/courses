#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>

#define MAX_ITEMS 8
#define NAME_LEN  32

typedef struct {
    char     name[NAME_LEN];
    uint32_t priority;
} ServiceEndpoint;

typedef struct {
    ServiceEndpoint endpoints[MAX_ITEMS];
    size_t          count;
    unsigned int    rng_seed;
    int             randomize_order; /* 1 = увімкнути захисну дедетермінізацію */
} EndpointRegistry;

void endpoint_registry_init(EndpointRegistry *reg, int randomize_order) {
    if (!reg) return;
    reg->count = 0;
    reg->rng_seed = (unsigned int)time(NULL);
    reg->randomize_order = randomize_order;
}

int endpoint_registry_add(EndpointRegistry *reg, const char *name, uint32_t priority) {
    if (!reg || !name || reg->count >= MAX_ITEMS) return -1;
    strncpy(reg->endpoints[reg->count].name, name, NAME_LEN - 1);
    reg->endpoints[reg->count].name[NAME_LEN - 1] = '\0';
    reg->endpoints[reg->count].priority = priority;
    reg->count++;
    return 0;
}

/* Отримання списку ендпоінтів із захисним перемішуванням Фішера — Єйтса */
size_t endpoint_registry_fetch(EndpointRegistry *reg, ServiceEndpoint *out_buf, size_t max_len) {
    if (!reg || !out_buf || max_len == 0) return 0;

    size_t n = (reg->count < max_len) ? reg->count : max_len;
    for (size_t i = 0; i < n; i++) {
        out_buf[i] = reg->endpoints[i];
    }

    /* Якщо активний захисний режим, перемішуємо елементи */
    if (reg->randomize_order && n > 1) {
        for (size_t i = n - 1; i > 0; i--) {
            size_t j = (size_t)(rand_r(&reg->rng_seed) % (i + 1));
            ServiceEndpoint tmp = out_buf[i];
            out_buf[i] = out_buf[j];
            out_buf[j] = tmp;
        }
    }
    return n;
}
