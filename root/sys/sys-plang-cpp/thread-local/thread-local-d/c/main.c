/* Динамічне завантаження плагіна з TLS на мові C */
#include <dlfcn.h>
#include <stdio.h>

typedef void (*process_fn)(void);

void load_and_run(const char* lib_path) {
    void* handle = dlopen(lib_path, RTLD_NOW);
    if (!handle) {
        fprintf(stderr, "dlopen error: %s\n", dlerror());
        return;
    }
    process_fn fn = (process_fn)dlsym(handle, "process_event");
    if (fn) fn();
    dlclose(handle);
}
