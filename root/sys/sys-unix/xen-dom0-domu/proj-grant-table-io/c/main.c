/* Dom0 Backend Mapper у стилі C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <errno.h>

#include <xen/gntdev.h>
#include <xen/evtchn.h>

#define PAGE_SIZE 4096

int process_remote_grant(uint32_t remote_domid, uint32_t gref, uint32_t remote_port) {
    int gntdev_fd = -1;
    int evtchn_fd = -1;
    void *mapped_page = MAP_FAILED;
    int ret = 0;

    /* 1. Відкриття пристрою gntdev */
    gntdev_fd = open("/dev/xen/gntdev", O_RDWR);
    if (gntdev_fd < 0) {
        perror("Не вдалося відкрити /dev/xen/gntdev");
        return -1;
    }

    /* 2. Підготовка структури для відображення grant reference */
    struct ioctl_gntdev_map_grant_ref map_req;
    memset(&map_req, 0, sizeof(map_req));
    map_req.count = 1;
    map_req.refs[0].domid = remote_domid;
    map_req.refs[0].ref = gref;

    if (ioctl(gntdev_fd, IOCTL_GNTDEV_MAP_GRANT_REF, &map_req) < 0) {
        perror("Помилка ioctl IOCTL_GNTDEV_MAP_GRANT_REF");
        close(gntdev_fd);
        return -1;
    }

    /* 3. Отримання вказівника на пам'ять через mmap() за отриманим зміщенням */
    mapped_page = mmap(NULL, PAGE_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED,
                       gntdev_fd, map_req.index);
    if (mapped_page == MAP_FAILED) {
        perror("Помилка mmap для сторінки гранту");
        ret = -1;
        goto out_unmap_ioctl;
    }

    /* Сторінка належить чужому домену й може не містити термінального нуля,
       тому обмежуємо друк розміром сторінки. */
    printf("[Dom0] Успішно замаплено сторінку DomU (MFN через gref %u): \"%.*s\"\n",
           gref, (int)strnlen((char *)mapped_page, PAGE_SIZE), (char *)mapped_page);

    /* 4. Відкриття пристрою event channel та надсилання сповіщення */
    evtchn_fd = open("/dev/xen/evtchn", O_RDWR);
    if (evtchn_fd >= 0) {
        struct ioctl_evtchn_notify notify;
        notify.port = remote_port;
        if (ioctl(evtchn_fd, IOCTL_EVTCHN_NOTIFY, &notify) < 0) {
            perror("Помилка надсилання сповіщення Event Channel");
        } else {
            printf("[Dom0] Надіслано upcall у порт Event Channel %u\n", remote_port);
        }
        close(evtchn_fd);
    }

out_unmap_ioctl:
    /* 5. Звільнення mmap та розмапування через ioctl */
    if (mapped_page != MAP_FAILED) {
        munmap(mapped_page, PAGE_SIZE);
    }

    struct ioctl_gntdev_unmap_grant_ref unmap_req;
    unmap_req.index = map_req.index;
    unmap_req.count = 1;
    ioctl(gntdev_fd, IOCTL_GNTDEV_UNMAP_GRANT_REF, &unmap_req);

    close(gntdev_fd);
    return ret;
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Використання: %s <domid> <gref> <evtchn_port>\n", argv[0]);
        return 1;
    }

    uint32_t domid = (uint32_t)atoi(argv[1]);
    uint32_t gref = (uint32_t)atoi(argv[2]);
    uint32_t port = (uint32_t)atoi(argv[3]);

    return process_remote_grant(domid, gref, port) == 0 ? 0 : 1;
}
