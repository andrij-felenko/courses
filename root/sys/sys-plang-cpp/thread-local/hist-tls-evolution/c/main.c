#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

static pthread_key_t thread_log_key;
static pthread_once_t key_once = PTHREAD_ONCE_INIT;

static void destroy_log_buffer(void* buf) {
    free(buf);
}

static void init_log_key(void) {
    pthread_key_create(&thread_log_key, destroy_log_buffer);
}

void append_log(const char* msg) {
    pthread_once(&key_once, init_log_key);
    char* buf = (char*)pthread_getspecific(thread_log_key);
    if (!buf) {
        buf = (char*)malloc(1024);
        pthread_setspecific(thread_log_key, buf);
    }
    snprintf(buf, 1024, "Log: %s\n", msg);
}
