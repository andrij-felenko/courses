// C: Парсинг заголовка асинхронної події +IPD у системному буфері
#include <stdio.h>
#include <string.h>

typedef struct {
    int link_id;
    int data_len;
    char *payload;
} ipd_event_t;

int parse_ipd_header(const char *buffer, ipd_event_t *event) {
    if (strncmp(buffer, "+IPD,", 5) != 0) return -1;
    
    // Перевірка багатоканального режиму (+IPD,id,len:data)
    if (sscanf(buffer, "+IPD,%d,%d:", &event->link_id, &event->data_len) == 2) {
        event->payload = strchr(buffer, ':') + 1;
        return 0;
    }
    // Перевірка одиночного режиму (+IPD,len:data)
    event->link_id = 0;
    if (sscanf(buffer, "+IPD,%d:", &event->data_len) == 1) {
        event->payload = strchr(buffer, ':') + 1;
        return 0;
    }
    return -1;
}
