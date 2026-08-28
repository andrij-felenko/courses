#include <sys/uio.h>
#include <unistd.h>
#include <cerrno>
#include <span>
#include <expected>
#include <system_error>

std::expected<size_t, std::error_code> copy_from_process(
    pid_t pid, std::span<std::byte> local_buf, uintptr_t remote_addr) 
{
    struct iovec local_iov{
        .iov_base = local_buf.data(),
        .iov_len = local_buf.size()
    };
    struct iovec remote_iov{
        .iov_base = reinterpret_cast<void*>(remote_addr),
        .iov_len = local_buf.size()
    };

    ssize_t nread = process_vm_readv(pid, &local_iov, 1, &remote_iov, 1, 0);
    if (nread < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return static_cast<size_t>(nread);
}
