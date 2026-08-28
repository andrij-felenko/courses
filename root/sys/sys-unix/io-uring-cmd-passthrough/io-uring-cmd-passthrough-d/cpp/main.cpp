// Приклад на C++: Ідіоматична реєстрація буфера з перевіркою помилок
#include <span>
#include <system_error>
#include <liburing.h>

std::error_code register_fixed_buffer(struct io_uring& ring, std::span<std::byte> buffer) {
    struct iovec iov{
        .iov_base = buffer.data(),
        .iov_len = buffer.size()
    };
    int ret = ::io_uring_register_buffers(&ring, &iov, 1);
    if (ret < 0) {
        return std::error_code(-ret, std::generic_category());
    }
    return {};
}
