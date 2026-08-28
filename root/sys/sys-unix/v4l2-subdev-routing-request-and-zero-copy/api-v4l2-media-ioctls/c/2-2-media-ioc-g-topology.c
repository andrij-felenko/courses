#include <linux/media.h>
#include <sys/ioctl.h>
#include <stdlib.h>
#include <string.h>

struct media_v2_topology top;
memset(&top, 0, sizeof(top));

/* 1. Перший виклик з нульовими масивами для вирахування кількості елементів */
if (ioctl(media_fd, MEDIA_IOC_G_TOPOLOGY, &top) < 0) {
    perror("MEDIA_IOC_G_TOPOLOGY count failed");
    return -1;
}

struct media_v2_entity *entities = calloc(top.num_entities, sizeof(*entities));
struct media_v2_pad *pads = calloc(top.num_pads, sizeof(*pads));
struct media_v2_link *links = calloc(top.num_links, sizeof(*links));

top.ptr_entities = (uintptr_t)entities;
top.ptr_pads = (uintptr_t)pads;
top.ptr_links = (uintptr_t)links;

/* 2. Другий виклик для заповнення виділеної пам'яті */
if (ioctl(media_fd, MEDIA_IOC_G_TOPOLOGY, &top) < 0) {
    perror("MEDIA_IOC_G_TOPOLOGY fetch failed");
    free(entities); free(pads); free(links);
    return -1;
}
