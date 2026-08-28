/* atomic-modeset.c — від вузла пристрою до анімації, без нічого зайвого. */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <signal.h>
#include <sys/mman.h>
#include <xf86drm.h>
#include <xf86drmMode.h>
#include <drm_fourcc.h>

static volatile sig_atomic_t stop;
static void on_int(int sig) { (void)sig; stop = 1; }

/* rc усюди тримаємо в одному вигляді — від'ємне −errno. */
static void die(const char *what, int rc)
{
    fprintf(stderr, "%s: %s\n", what, strerror(-rc));
    exit(1);
}

/* Номер властивості за іменем; заразом віддає поточне значення. */
static uint32_t prop_of(int fd, uint32_t obj, uint32_t type,
                        const char *name, uint64_t *value)
{
    drmModeObjectProperties *props = drmModeObjectGetProperties(fd, obj, type);
    uint32_t id = 0;
    if (!props)
        return 0;
    for (uint32_t i = 0; i < props->count_props && !id; i++) {
        drmModePropertyRes *p = drmModeGetProperty(fd, props->props[i]);
        if (!p)
            continue;
        if (!strcmp(p->name, name)) {
            id = p->prop_id;
            if (value)
                *value = props->prop_values[i];
        }
        drmModeFreeProperty(p);
    }
    drmModeFreeObjectProperties(props);
    return id;
}
