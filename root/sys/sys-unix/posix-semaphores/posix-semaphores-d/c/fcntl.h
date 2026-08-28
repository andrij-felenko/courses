#include <fcntl.h>
#include <semaphore.h>
#include <sys/mman.h>
#include <unistd.h>

struct region {
    sem_t filled;                    /* скільки кадрів готово */
    sem_t free_slots;                /* скільки місць вільно */
    unsigned char frame[4][6220800];
};

int fd = shm_open("/frames", O_CREAT | O_RDWR, 0600);
ftruncate(fd, sizeof(struct region));
struct region *r = mmap(NULL, sizeof *r, PROT_READ | PROT_WRITE,
                        MAP_SHARED, fd, 0);
close(fd);

sem_init(&r->filled, 1, 0);          /* 1 — «між процесами» */
sem_init(&r->free_slots, 1, 4);      /* стільки, скільки слотів */
