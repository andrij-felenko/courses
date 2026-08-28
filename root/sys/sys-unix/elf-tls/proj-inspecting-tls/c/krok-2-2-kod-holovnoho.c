#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <pthread.h>

typedef void (*plugin_func_t)(void);

void* thread_routine(void* arg) {
    const char* lib_path = (const char*)arg;
    
    printf("--> [Worker Thread] Завантаження %s через dlopen()...\n", lib_path);
    void* handle = dlopen(lib_path, RTLD_NOW);
    if (!handle) {
        fprintf(stderr, "dlopen error: %s\n", dlerror());
        return NULL;
    }

    plugin_func_t func = (plugin_func_t)dlsym(handle, "plugin_print_tls");
    if (func) {
        /* Перший виклик розвертає ліниву алокацію в DTV через __tls_get_addr */
        func();
    }

    dlclose(handle);
    return NULL;
}

int main(int argc, char** argv) {
    const char* plugin_path = (argc > 1) ? argv[1] : "./libplugin.so";

    pthread_t thread;
    pthread_create(&thread, NULL, thread_routine, (void*)plugin_path);
    pthread_join(thread, NULL);

    return 0;
}
