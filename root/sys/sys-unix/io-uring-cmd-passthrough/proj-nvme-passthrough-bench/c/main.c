#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <liburing.h>
#include <linux/nvme_ioctl.h>

#define ALIGNMENT 4096
#define READ_SIZE 4096

int main(int argc, char *argv[]) {
    const char *dev_path = (argc > 1) ? argv[1] : "/dev/ng0n1";
    struct io_uring ring;
    int fd;
    void *buffer;
    struct io_uring_sqe *sqe;
    struct io_uring_cqe *cqe;
    struct nvme_uring_cmd *cmd;
    int ret;

    /* Відкриваємо символьний пристрій NVMe generic character device */
    fd = open(dev_path, O_RDWR);
    if (fd < 0) {
        perror("Помилка відкриття NVMe символьного пристрою");
        return 1;
    }

    /* Виділяємо вирівняну пам'ять для DMA (4096 байт) */
    ret = posix_memalign(&buffer, ALIGNMENT, READ_SIZE);
    if (ret != 0) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        close(fd);
        return 1;
    }
    memset(buffer, 0, READ_SIZE);

    /* Ініціалізуємо io_uring з глибиною черги 32.
       NVMe passthrough вимагає 128-байтових SQE: struct nvme_uring_cmd
       займає 72 байти, а у звичайному 64-байтовому SQE під sqe->cmd
       лишається лише 16. Без IORING_SETUP_SQE128 драйвер відхилить команду.
       CQE32 потрібен, щоб отримати cdw0 у cqe->big_cqe[0]. */
    struct io_uring_params params;
    memset(&params, 0, sizeof(params));
    params.flags = IORING_SETUP_SQE128 | IORING_SETUP_CQE32;

    ret = io_uring_queue_init_params(32, &ring, &params);
    if (ret < 0) {
        fprintf(stderr, "Помилка ініціалізації io_uring: %s\n", strerror(-ret));
        free(buffer);
        close(fd);
        return 1;
    }

    /* Отримуємо вільний елемент черги подачі SQE */
    sqe = io_uring_get_sqe(&ring);
    if (!sqe) {
        fprintf(stderr, "Не вдалося отримати SQE з кільця\n");
        io_uring_queue_exit(&ring);
        free(buffer);
        close(fd);
        return 1;
    }

    /* Налаштовуємо операцію IORING_OP_URING_CMD */
    io_uring_prep_rw(IORING_OP_URING_CMD, sqe, fd, NULL, 0, 0);
    sqe->cmd_op = NVME_URING_CMD_IO;

    /* Заповнюємо специфічну структуру команди NVMe */
    cmd = (struct nvme_uring_cmd *)sqe->cmd;
    memset(cmd, 0, sizeof(*cmd));
    cmd->opcode = 0x02; /* NVMe I/O Read opcode */
    cmd->nsid = 1;      /* Namespace ID 1 */
    cmd->addr = (__u64)buffer;
    cmd->data_len = READ_SIZE;
    cmd->cdw10 = 0;     /* LBA 0 (нижні 32 біти) */
    cmd->cdw11 = 0;     /* LBA 0 (верхні 32 біти) */
    cmd->cdw12 = 0;     /* 1 блок (0-based значення: 0 відповідає 1 LBA) */

    sqe->user_data = 0x42;

    /* Відправляємо команду в ядро */
    ret = io_uring_submit(&ring);
    if (ret < 0) {
        fprintf(stderr, "Помилка відправлення SQE: %s\n", strerror(-ret));
        io_uring_queue_exit(&ring);
        free(buffer);
        close(fd);
        return 1;
    }

    /* Очікуємо завершення виконання у CQE */
    ret = io_uring_wait_cqe(&ring, &cqe);
    if (ret < 0) {
        fprintf(stderr, "Помилка очікування CQE: %s\n", strerror(-ret));
        io_uring_queue_exit(&ring);
        free(buffer);
        close(fd);
        return 1;
    }

    if (cqe->res == 0) {
        printf("NVMe Read успішно виконано! Прочитано %d байт з LBA 0.\n", READ_SIZE);
    } else {
        fprintf(stderr, "NVMe Read завершився з помилкою res = %d\n", cqe->res);
    }

    io_uring_cqe_seen(&ring, cqe);
    io_uring_queue_exit(&ring);
    free(buffer);
    close(fd);
    return 0;
}
