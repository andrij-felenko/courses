#include <stdlib.h>
#include <string.h>

#define MAX_DEVICES 64

typedef struct {
    device_t items[MAX_DEVICES];
    size_t count;
} in_memory_device_repo_t;

device_t* in_memory_find_by_id(void* ctx, const char* device_id) {
    in_memory_device_repo_t* repo = (in_memory_device_repo_t*)ctx;
    for (size_t i = 0; i < repo->count; ++i) {
        if (strcmp(repo->items[i].id, device_id) == 0) {
            device_t* copy = malloc(sizeof(device_t));
            memcpy(copy, &repo->items[i], sizeof(device_t));
            return copy;
        }
    }
    return NULL;
}

int in_memory_save(void* ctx, const device_t* device) {
    in_memory_device_repo_t* repo = (in_memory_device_repo_t*)ctx;
    for (size_t i = 0; i < repo->count; ++i) {
        if (strcmp(repo->items[i].id, device->id) == 0) {
            memcpy(&repo->items[i], device, sizeof(device_t));
            return 0;
        }
    }
    if (repo->count < MAX_DEVICES) {
        memcpy(&repo->items[repo->count++], device, sizeof(device_t));
        return 0;
    }
    return -1;
}
