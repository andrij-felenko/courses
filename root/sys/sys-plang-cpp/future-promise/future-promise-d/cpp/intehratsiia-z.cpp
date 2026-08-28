class AsyncFileReader {
public:
    std::future<ssize_t> read_async(int fd, void* buf, size_t count) {
        auto p = std::make_shared<std::promise<ssize_t>>();
        std::future<ssize_t> f = p->get_future();

        // Подаємо замовлення в ring io_uring
        submit_io_uring_read(fd, buf, count, [p](ssize_t bytes_read) {
            if (bytes_read < 0) {
                p->set_exception(std::make_exception_ptr(
                    std::system_error(-bytes_read, std::generic_category())
                ));
            } else {
                p->set_value(bytes_read);
            }
        });

        return f;
    }
};
