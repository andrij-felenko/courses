#include <pthread.h>
#include <stdlib.h>

/* КОРЕКТНА ІНІЦІАЛІЗАЦІЯ ЧЕРЕЗ pthread_once */
static pthread_once_t g_init_once = PTHREAD_ONCE_INIT;
static Resource *g_safe_resource = NULL;

static void init_resource_routine(void) {
    g_safe_resource = (Resource *)malloc(sizeof(Resource));
    g_safe_resource->data = 42;
}

Resource *get_resource_safe(void) {
    pthread_once(&g_init_once, init_resource_routine);
    return g_safe_resource;
}
