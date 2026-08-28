#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>
#include <linux/blkzoned.h>
#include <pthread.h>
#include <errno.h>

#define SECTOR_SIZE 512
#define NUM_THREADS 4
#define WRITES_PER_THREAD 8
#define BLOCK_SIZE 4096

typedef struct {
    int fd;
    uint64_t zslba;
    int thread_id;
} thread_arg_t;

/* Виконання апаратної команди Zone Append через ioctl */
static uint64_t zns_zone_append(int fd, uint32_t nsid, uint64_t zslba, void *buffer, size_t len) {
    uint32_t nlb = len / SECTOR_SIZE;
    struct nvme_passthru_cmd cmd;
    memset(&cmd, 0, sizeof(cmd));

    cmd.opcode      = 0x7d; /* nvme_zns_cmd_append */
    cmd.nsid        = nsid;
    cmd.addr        = (uint64_t)(uintptr_t)buffer;
    cmd.data_len    = len;
    cmd.cdw10       = (uint32_t)(zslba & 0xFFFFFFFF);
    cmd.cdw11       = (uint32_t)(zslba >> 32);
    cmd.cdw12       = nlb - 1; /* 0-based NLB */
    cmd.timeout_ms  = 2000;

    if (ioctl(fd, NVME_IOCTL_IO_CMD, &cmd) < 0) {
        perror("ioctl(NVME_IOCTL_IO_CMD - Zone Append) failed");
        return (uint64_t)-1;
    }

    /* cmd.result містить виділений LBA у 64-бітному результаті CQE */
    return cmd.result;
}

/* Робоча функція паралельного потоку (без локів!) */
static void *worker_thread(void *arg) {
    thread_arg_t *targ = (thread_arg_t *)arg;
    void *buffer = NULL;

    /* Потрібне вирівнювання пам'яті для Direct I/O */
    if (posix_memalign(&buffer, 4096, BLOCK_SIZE) != 0) {
        perror("posix_memalign failed");
        pthread_exit(NULL);
    }

    memset(buffer, 0xAA + targ->thread_id, BLOCK_SIZE);

    for (int i = 0; i < WRITES_PER_THREAD; i++) {
        uint64_t allocated_lba = zns_zone_append(targ->fd, 1, targ->zslba, buffer, BLOCK_SIZE);
        if (allocated_lba == (uint64_t)-1) {
            fprintf(stderr, "[Thread %d] Append failed at iteration %d\n", targ->thread_id, i);
            break;
        }
        printf("[Thread %d] Appended block %d -> Allocated LBA: 0x%lx\n",
               targ->thread_id, i, allocated_lba);
    }

    free(buffer);
    pthread_exit(NULL);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s /dev/nvmeXnY\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *devpath = argv[1];
    int fd = open(devpath, O_RDWR | O_DIRECT);
    if (fd < 0) {
        perror("Failed to open device");
        return EXIT_FAILURE;
    }

    /* 1. Скидання першої зони (ZSLBA = 0) */
    struct blk_zone_range range = {
        .sector = 0,
        .nr_sectors = 262144 /* 128 MB у 512B секторах */
    };

    printf("Resetting zone at sector 0...\n");
    if (ioctl(fd, BLKRESETZONE, &range) < 0) {
        perror("ioctl(BLKRESETZONE) failed");
        close(fd);
        return EXIT_FAILURE;
    }
    printf("Zone reset successful.\n");

    /* 2. Запуск паралельних потоків дозапису */
    pthread_t threads[NUM_THREADS];
    thread_arg_t args[NUM_THREADS];

    for (int i = 0; i < NUM_THREADS; i++) {
        args[i].fd = fd;
        args[i].zslba = 0; /* Вказуємо початковий LBA зони */
        args[i].thread_id = i;
        if (pthread_create(&threads[i], NULL, worker_thread, &args[i]) != 0) {
            perror("pthread_create failed");
        }
    }

    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    close(fd);
    printf("All parallel lockless appends completed successfully.\n");
    return EXIT_SUCCESS;
}
