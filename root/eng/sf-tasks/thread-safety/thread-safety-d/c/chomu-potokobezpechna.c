#include <pthread.h>
#include <stdio.h>

static pthread_mutex_t g_log_lock = PTHREAD_MUTEX_INITIALIZER;

void log_message_safe(const char *msg) {
    pthread_mutex_lock(&g_log_lock);
    /* Критична секція запису в лог */
    printf("[LOG]: %s\n", msg);
    pthread_mutex_unlock(&g_log_lock);
}
