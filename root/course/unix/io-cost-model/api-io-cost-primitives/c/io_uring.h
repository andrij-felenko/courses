#include <linux/io_uring.h>
#include <sys/syscall.h>
#include <unistd.h>

int io_uring_setup(u32 entries, struct io_uring_params *p);
int io_uring_enter(unsigned int fd, unsigned int to_submit,
                   unsigned int min_complete, unsigned int flags,
                   sigset_t *sig);
int io_uring_register(unsigned int fd, unsigned int opcode,
                      void *arg, unsigned int nr_args);
