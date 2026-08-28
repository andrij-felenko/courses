#include <liburing.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#define QUEUE_DEPTH 4
#define BLOCK_SIZE 4096

int main(void) {
    struct io_uring ring;
    int fd;
    char buffer[BLOCK_SIZE];
    struct io_uring_sqe *sqe;
    struct io_uring_cqe *cqe;
    int ret;

    /* 1. Ініціалізація кільцевих буферів io_uring у ядрі */
    ret = io_uring_queue_init(QUEUE_DEPTH, &ring, 0);
    if (ret < 0) {
        fprintf(stderr, "Помилка ініціалізації io_uring: %s\n", strerror(-ret));
        return 1;
    }

    fd = open("test.txt", O_RDONLY);
    if (fd < 0) {
        perror("Помилка відкриття файлу");
        io_uring_queue_exit(&ring);
        return 1;
    }

    /* 2. Отримання вільної комірки SQE та підготовка запиту читання */
    sqe = io_uring_get_sqe(&ring);
    if (!sqe) {
        fprintf(stderr, "Черга SQ переповнена\n");
        close(fd);
        io_uring_queue_exit(&ring);
        return 1;
    }

    /* Заповнення полів SQE: read(fd, buffer, BLOCK_SIZE, offset=0) */
    io_uring_prep_read(sqe, fd, buffer, BLOCK_SIZE, 0);
    
    /* Маркування запиту унікальним ідентифікатором (user_data) */
    io_uring_sqe_set_data64(sqe, 42);

    /* 3. Подання запиту в ядро (виклик io_uring_enter) */
    ret = io_uring_submit(&ring);
    if (ret < 0) {
        fprintf(stderr, "Помилка подання SQE: %s\n", strerror(-ret));
        close(fd);
        io_uring_queue_exit(&ring);
        return 1;
    }

    /* 4. Блокуюче очікування результату в черзі CQ */
    ret = io_uring_wait_cqe(&ring, &cqe);
    if (ret < 0) {
        fprintf(stderr, "Помилка очікування CQE: %s\n", strerror(-ret));
        close(fd);
        io_uring_queue_exit(&ring);
        return 1;
    }

    /* Перевірка коду повернення асинхронної операції */
    if (cqe->res < 0) {
        fprintf(stderr, "Асинхронне читання завершилося з помилкою: %s\n", strerror(-cqe->res));
    } else {
        printf("Успішно прочитано %d байтів. Маркер user_data: %llu\n",
               cqe->res, (unsigned long long)io_uring_cqe_get_data64(cqe));
    }

    /* 5. Сповіщення ядра про зчитування CQE (зсув вказівника head у CQ) */
    io_uring_cqe_seen(&ring, cqe);

    close(fd);
    io_uring_queue_exit(&ring);
    return 0;
}
