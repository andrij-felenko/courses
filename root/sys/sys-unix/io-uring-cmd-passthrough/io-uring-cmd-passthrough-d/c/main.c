/* Приклад на C: Попередня реєстрація буферів у io_uring */
struct iovec iov;
iov.iov_base = dma_buffer;
iov.iov_len = 4096 * 1024;

/* Реєструємо масив буферів у ядрі один раз при старті програми */
int ret = io_uring_register_buffers(&ring, &iov, 1);
if (ret < 0) {
    perror("Помилка io_uring_register_buffers");
}
