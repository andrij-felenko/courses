typedef __kernel_ulong_t aio_context_t;

int io_setup(unsigned nr_events, aio_context_t *ctx_idp);
int io_submit(aio_context_t ctx_id, long nr, struct iocb **iocbpp);
int io_getevents(aio_context_t ctx_id, long min_nr, long nr,
                 struct io_event *events, struct timespec *timeout);
int io_pgetevents(aio_context_t ctx_id, long min_nr, long nr,   /* ядро 4.18 */
                  struct io_event *events, struct timespec *timeout,
                  const struct __aio_sigset *usig);
int io_cancel(aio_context_t ctx_id, struct iocb *iocb, struct io_event *result);
int io_destroy(aio_context_t ctx_id);
