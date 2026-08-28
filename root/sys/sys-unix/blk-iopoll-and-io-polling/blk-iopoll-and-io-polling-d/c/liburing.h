#include <liburing.h>

struct io_uring ring;
/* Ініціалізація кільця io_uring з підтримкою IO Polling */
int ret = io_uring_queue_init(128, &ring, IORING_SETUP_IOPOLL);

struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
io_uring_prep_read(sqe, fd, buf, 4096, offset);
io_uring_submit(&ring);

struct io_uring_cqe *cqe;
/* При виклику enter ядро виконує polling у контексті потоку */
io_uring_wait_cqe(&ring, &cqe);
io_uring_cqe_seen(&ring, cqe);
