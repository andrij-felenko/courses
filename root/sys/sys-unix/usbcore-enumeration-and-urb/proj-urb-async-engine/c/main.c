#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/poll.h>
#include <linux/usbdevice_fs.h>

#define NUM_URBS 4
#define BUFFER_SIZE 64
#define ENDPOINT_IN 0x81

struct async_transfer {
    struct usbdevfs_urb urb;
    unsigned char buffer[BUFFER_SIZE];
    int id;
};

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s /dev/bus/usb/001/002\n", argv[0]);
        return EXIT_FAILURE;
    }

    int fd = open(argv[1], O_RDWR);
    if (fd < 0) {
        perror("Не вдалося відкрити пристрій USB");
        return EXIT_FAILURE;
    }

    /* Запитуємо володіння інтерфейсом 0 у usbcore */
    int interface_num = 0;
    if (ioctl(fd, USBDEVFS_CLAIMINTERFACE, &interface_num) < 0) {
        perror("Помилка захоплення інтерфейсу USBDEVFS_CLAIMINTERFACE");
        close(fd);
        return EXIT_FAILURE;
    }

    struct async_transfer transfers[NUM_URBS];
    memset(transfers, 0, sizeof(transfers));

    /* Ініціалізація та асинхронна відправка пакетів URB */
    for (int i = 0; i < NUM_URBS; ++i) {
        transfers[i].id = i;
        transfers[i].urb.type = USBDEVFS_URB_TYPE_BULK;
        transfers[i].urb.endpoint = ENDPOINT_IN;
        transfers[i].urb.buffer = transfers[i].buffer;
        transfers[i].urb.buffer_length = BUFFER_SIZE;
        transfers[i].urb.usercontext = &transfers[i];

        if (ioctl(fd, USBDEVFS_SUBMITURB, &transfers[i].urb) < 0) {
            perror("Помилка відправки USBDEVFS_SUBMITURB");
            goto release_and_close;
        }
        printf("[+] Асинхронний URB #%d успішно відправлено до usbcore\n", i);
    }

    /* Головний цикл обробки результатів */
    int completed_urbs = 0;
    struct pollfd pfd = { .fd = fd, .events = POLLOUT };

    while (completed_urbs < NUM_URBS) {
        int poll_ret = poll(&pfd, 1, 2000);
        if (poll_ret < 0) {
            perror("Помилка виклику poll()");
            break;
        } else if (poll_ret == 0) {
            fprintf(stderr, "Таймаут очікування завершення URB\n");
            break;
        }

        struct usbdevfs_urb *reaped_urb = NULL;
        while (ioctl(fd, USBDEVFS_REAPURBNDELAY, &reaped_urb) == 0) {
            struct async_transfer *st = (struct async_transfer *)reaped_urb->usercontext;
            printf("[✓] URB #%d завершено: статус=%d, отримано=%d байтів\n",
                   st->id, reaped_urb->status, reaped_urb->actual_length);
            completed_urbs++;
        }
    }

release_and_close:
    ioctl(fd, USBDEVFS_RELEASEINTERFACE, &interface_num);
    close(fd);
    return EXIT_SUCCESS;
}
