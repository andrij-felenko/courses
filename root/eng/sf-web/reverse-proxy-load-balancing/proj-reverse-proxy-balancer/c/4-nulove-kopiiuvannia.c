/* Передача байтів напряму між сокетами через кільцевий буфер ядра (pipe) */
int pipefd[2];
if (pipe(pipefd) == 0) {
    ssize_t bytes = splice(client_fd, NULL, pipefd[1], NULL, 65536, SPLICE_F_MOVE | SPLICE_F_NONBLOCK);
    if (bytes > 0) {
        splice(pipefd[0], NULL, backend_fd, NULL, bytes, SPLICE_F_MOVE | SPLICE_F_NONBLOCK);
    }
    close(pipefd[0]);
    close(pipefd[1]);
}
