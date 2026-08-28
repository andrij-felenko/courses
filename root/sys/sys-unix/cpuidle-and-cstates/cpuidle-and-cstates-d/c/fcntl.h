#include <fcntl.h>
#include <stdint.h>
#include <unistd.h>

/* Поки цей дескриптор відкрито, жоден керувальник на машині
   не вибере стану, вихід із якого довший за 50 мкс. */
int fd = open("/dev/cpu_dma_latency", O_WRONLY);
int32_t limit_us = 50;

write(fd, &limit_us, sizeof(limit_us));

/* ... робота, критична за затримкою ... */

close(fd);   /* вимогу знято, глибокі стани знову дозволені */
