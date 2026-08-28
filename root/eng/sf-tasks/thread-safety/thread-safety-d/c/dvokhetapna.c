/* ІСТОРИЧНО ЗЛАМАНА РЕАЛІЗАЦІЯ ДВОХЕТАПНОЇ ІНІЦІАЛІЗАЦІЇ */
typedef struct {
    int data;
} Resource;

static Resource *g_resource = NULL;
static pthread_mutex_t g_init_lock = PTHREAD_MUTEX_INITIALIZER;

Resource *get_resource_broken(void) {
    if (g_resource == NULL) {
        pthread_mutex_lock(&g_init_lock);
        if (g_resource == NULL) {
            Resource *res = (Resource *)malloc(sizeof(Resource));
            res->data = 42; // Ініціалізація полів
            g_resource = res; // Публікація вказівника
        }
        pthread_mutex_unlock(&g_init_lock);
    }
    return g_resource;
}
