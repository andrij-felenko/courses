#define _GNU_SOURCE          /* process_vm_readv оголошено лише під цим макросом */
#include <sys/uio.h>
#include <unistd.h>
#include <stdio.h>

ssize_t copy_from_process(pid_t pid, void *dest, const void *src, size_t len) {
    struct iovec local[1];
    struct iovec remote[1];

    local[0].iov_base = dest;
    local[0].iov_len = len;

    remote[0].iov_base = (void *)src;
    remote[0].iov_len = len;

    /* Копіює весь блок пам'яті за ОДИН системний виклик */
    return process_vm_readv(pid, local, 1, remote, 1, 0);
}
