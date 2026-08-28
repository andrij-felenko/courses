#include <pthread.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char database_url[128];
    int max_pool_size;
} ConfigurationTable;

typedef struct {
    ConfigurationTable* config;
    pthread_mutex_t mutex;
} ServiceGatewayC;

void init_gateway(ServiceGatewayC* gw) {
    gw->config = NULL;
    pthread_mutex_init(&gw->mutex, NULL);
}

const ConfigurationTable* get_configuration_c(ServiceGatewayC* gw) {
    pthread_mutex_lock(&gw->mutex);
    if (gw->config == NULL) {
        ConfigurationTable* cfg = (ConfigurationTable*)malloc(sizeof(ConfigurationTable));
        if (cfg) {
            strncpy(cfg->database_url, "postgres://cluster.prod:5432/primary", 127);
            cfg->max_pool_size = 256;
            gw->config = cfg;
        }
    }
    pthread_mutex_unlock(&gw->mutex);
    return gw->config;
}
