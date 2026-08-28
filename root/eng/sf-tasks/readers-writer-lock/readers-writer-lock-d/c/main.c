#include <pthread.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ROUTES 256
#define IP_LEN     16

typedef struct {
    char subnet[IP_LEN];
    char gateway[IP_LEN];
} route_entry_t;

typedef struct {
    pthread_rwlock_t rwlock;
    route_entry_t    routes[MAX_ROUTES];
    size_t           count;
} routing_table_t;

int routing_table_init(routing_table_t *table) {
    table->count = 0;
    return pthread_rwlock_init(&table->rwlock, NULL);
}

void routing_table_destroy(routing_table_t *table) {
    pthread_rwlock_destroy(&table->rwlock);
}

// Операція читання: багато потоків шукають маршрути одночасно
bool routing_table_lookup(routing_table_t *table, const char *subnet, char *out_gateway, size_t max_len) {
    pthread_rwlock_rdlock(&table->rwlock); // Вхід у спільний режим (Shared)

    bool found = false;
    for (size_t i = 0; i < table->count; ++i) {
        if (strcmp(table->routes[i].subnet, subnet) == 0) {
            strncpy(out_gateway, table->routes[i].gateway, max_len - 1);
            out_gateway[max_len - 1] = '\0';
            found = true;
            break;
        }
    }

    pthread_rwlock_unlock(&table->rwlock); // Звільнення блокування
    return found;
}

// Операція запису: монопольний доступ для додавання або зміни маршруту
bool routing_table_add(routing_table_t *table, const char *subnet, const char *gateway) {
    pthread_rwlock_wrlock(&table->rwlock); // Вхід у монопольний режим (Exclusive)

    if (table->count >= MAX_ROUTES) {
        pthread_rwlock_unlock(&table->rwlock);
        return false;
    }

    // Перевірка на існування або оновлення
    for (size_t i = 0; i < table->count; ++i) {
        if (strcmp(table->routes[i].subnet, subnet) == 0) {
            strncpy(table->routes[i].gateway, gateway, IP_LEN - 1);
            table->routes[i].gateway[IP_LEN - 1] = '\0';
            pthread_rwlock_unlock(&table->rwlock);
            return true;
        }
    }

    // Додавання нового запису
    strncpy(table->routes[table->count].subnet, subnet, IP_LEN - 1);
    table->routes[table->count].subnet[IP_LEN - 1] = '\0';
    strncpy(table->routes[table->count].gateway, gateway, IP_LEN - 1);
    table->routes[table->count].gateway[IP_LEN - 1] = '\0';
    table->count++;

    pthread_rwlock_unlock(&table->rwlock);
    return true;
}
