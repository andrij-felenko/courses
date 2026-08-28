// Створення io_uring у режимі IOPOLL на C++20 з обробкою помилок
#include <system_error>
#include <liburing.h>

std::expected<struct io_uring, std::error_code> create_iopoll_ring(unsigned entries) {
    struct io_uring ring{};
    struct io_uring_params params{};
    params.flags = IORING_SETUP_IOPOLL | IORING_SETUP_SQE128 | IORING_SETUP_CQE32;

    int ret = ::io_uring_queue_init_params(entries, &ring, &params);
    if (ret < 0) {
        return std::unexpected(std::error_code(-ret, std::generic_category()));
    }
    return ring;
}
