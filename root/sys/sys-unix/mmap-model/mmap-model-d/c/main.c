#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

int main(void)
{
    int fd = open("/var/data/huge.bin", O_RDONLY);   /* файл на 40 ГіБ */
    struct stat st;
    fstat(fd, &st);

    unsigned char *p = mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (p == MAP_FAILED) { perror("mmap"); return 1; }
    close(fd);                       /* дескриптор більше не потрібен */

    printf("%u\n", p[3000000000ULL]);    /* ось тут станеться перший збій */

    munmap(p, st.st_size);
    return 0;
}
