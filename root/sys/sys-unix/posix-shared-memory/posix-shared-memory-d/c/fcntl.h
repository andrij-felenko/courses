#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stdlib.h>

struct region {
    _Atomic unsigned long seq;   /* лічильник версій кадру */
    unsigned char frame[6220800];
};

struct region *r;
int fd = shm_open("/telemetry", O_CREAT | O_RDWR, 0600);
if (fd < 0) exit(1);
if (ftruncate(fd, sizeof *r) < 0) exit(1);          /* задати розмір */
r = mmap(NULL, sizeof *r, PROT_READ | PROT_WRITE,
         MAP_SHARED, fd, 0);
if (r == MAP_FAILED) exit(1);
close(fd);                                           /* більше не потрібен */
