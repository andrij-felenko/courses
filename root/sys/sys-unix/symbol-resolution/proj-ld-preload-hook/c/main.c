#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <unistd.h>
#include <string.h>

/* Вказівники на оригінальні функції libc */
static void *(*real_malloc)(size_t size) = NULL;
static void (*real_free)(void *ptr) = NULL;

/* Статичний буфер для фази ініціалізації (bootstrap) */
#define BOOTSTRAP_CAPACITY (64 * 1024)
static char bootstrap_buffer[BOOTSTRAP_CAPACITY];
static size_t bootstrap_used = 0;
static int inside_init = 0;

/* Низькорівневий вивід числа у STDERR_FILENO без виділення пам'яті */
static void write_hex(size_t val) {
    char buf[20];
    char hex[] = "0123456789abcdef";
    int idx = 18;
    buf[19] = '\n';
    if (val == 0) {
        buf[idx--] = '0';
    } else {
        while (val > 0 && idx >= 2) {
            buf[idx--] = hex[val % 16];
            val /= 16;
        }
    }
    buf[idx--] = 'x';
    buf[idx] = '0';
    write(STDERR_FILENO, &buf[idx], 20 - idx);
}

static void write_msg(const char *msg) {
    write(STDERR_FILENO, msg, strlen(msg));
}

static void init_hooks(void) {
    inside_init = 1;
    real_malloc = (void *(*)(size_t))dlsym(RTLD_NEXT, "malloc");
    real_free = (void (*)(void *))dlsym(RTLD_NEXT, "free");
    inside_init = 0;

    if (!real_malloc || !real_free) {
        write_msg("myhook: FATAL - failed to resolve libc symbols\n");
        _exit(1);
    }
}

void *malloc(size_t size) {
    /* Якщо dlsym викликає malloc під час ініціалізації */
    if (inside_init) {
        if (bootstrap_used + size > BOOTSTRAP_CAPACITY) {
            write_msg("myhook: bootstrap buffer exhausted\n");
            return NULL;
        }
        void *ptr = &bootstrap_buffer[bootstrap_used];
        bootstrap_used += (size + 7) & ~7; /* вирівнювання на 8 байтів */
        return ptr;
    }

    if (!real_malloc) {
        init_hooks();
    }

    void *ptr = real_malloc(size);

    write_msg("myhook: malloc(");
    write_hex(size);
    write_msg(") = ");
    write_hex((size_t)ptr);

    return ptr;
}

void free(void *ptr) {
    if (!ptr) return;

    /* Ігноруємо звільнення з статичного bootstrap-буфера */
    if (ptr >= (void *)bootstrap_buffer && ptr < (void *)(bootstrap_buffer + BOOTSTRAP_CAPACITY)) {
        return;
    }

    if (!real_free) {
        init_hooks();
    }

    write_msg("myhook: free(");
    write_hex((size_t)ptr);

    real_free(ptr);
}
