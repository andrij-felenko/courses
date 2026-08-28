#include <liburing.h>

/* Ініціалізація та знищення кільця */
int io_uring_queue_init(unsigned entries, struct io_uring *ring, unsigned flags);
void io_uring_queue_exit(struct io_uring *ring);

/* Отримання вільного слота в SQ */
struct io_uring_sqe *io_uring_get_sqe(struct io_uring *ring);

/* Підготовка операцій (хелпери ініціалізації полів SQE) */
void io_uring_prep_readv(struct io_uring_sqe *sqe, int fd,
                         const struct iovec *iovecs, unsigned nr_vecs, off_t offset);
void io_uring_prep_writev(struct io_uring_sqe *sqe, int fd,
                          const struct iovec *iovecs, unsigned nr_vecs, off_t offset);
void io_uring_prep_send(struct io_uring_sqe *sqe, int sockfd,
                        const void *buf, size_t len, int flags);
void io_uring_prep_recv(struct io_uring_sqe *sqe, int sockfd,
                        void *buf, size_t len, int flags);
void io_uring_prep_splice(struct io_uring_sqe *sqe, int fd_in, int64_t off_in,
                          int fd_out, int64_t off_out, unsigned int nbytes,
                          unsigned int splice_flags);

/* Відправка завдань ядру */
int io_uring_submit(struct io_uring *ring);
int io_uring_submit_and_wait(struct io_uring *ring, unsigned wait_nr);

/* Обробка результатів CQE */
int io_uring_peek_cqe(struct io_uring *ring, struct io_uring_cqe **cqe_ptr);
int io_uring_wait_cqe(struct io_uring *ring, struct io_uring_cqe **cqe_ptr);
void io_uring_cqe_seen(struct io_uring *ring, struct io_uring_cqe *cqe);
