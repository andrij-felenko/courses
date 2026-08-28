#include <stdio.h>
#include <stdint.h>

typedef struct {
    char host[64];
    uint16_t port;
} database_config_t;

void connect_to_database(database_config_t* config) {
    // Якщо config дорівнює NULL, спроба прочитати config->host викликає SIGSEGV
    printf("Connecting to host: %s\n", config->host);
}

int main(void) {
    database_config_t* cfg = NULL;
    connect_to_database(cfg);
    return 0;
}
