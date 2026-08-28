#include <linux/media.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <stdio.h>

int req_fd = -1;
if (ioctl(media_fd, MEDIA_IOC_REQUEST_ALLOC, &req_fd) < 0) {
    perror("MEDIA_IOC_REQUEST_ALLOC помилка");
}

/* Відправка запиту у чергу */
if (ioctl(req_fd, MEDIA_REQUEST_IOC_QUEUE) < 0) {
    perror("MEDIA_REQUEST_IOC_QUEUE помилка");
}

/* Скидання стану об'єкта запиту */
ioctl(req_fd, MEDIA_REQUEST_IOC_REINIT);
close(req_fd);
