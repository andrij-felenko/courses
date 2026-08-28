/* latency-hold.c — тримає вимогу, доки жива програма.  cc -o latency-hold latency-hold.c */
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char **argv)
{
        int32_t want = (argc > 1) ? atoi(argv[1]) : 0;   /* мкс; 0 — «без сну взагалі» */
        int32_t effective;

        int fd = open("/dev/cpu_dma_latency", O_RDWR);
        if (fd < 0) { perror("open"); return 1; }

        if (write(fd, &want, sizeof want) != sizeof want) { perror("write"); return 1; }

        if (read(fd, &effective, sizeof effective) == sizeof effective)
                printf("чинна межа на машині: %d мкс\n", effective);

        pause();          /* вимога чинна рівно доти, доки відкрито fd */
        close(fd);
        return 0;
}
