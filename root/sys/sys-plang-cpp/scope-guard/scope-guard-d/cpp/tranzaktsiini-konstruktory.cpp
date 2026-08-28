class NetworkService {
    int socket_fd_{-1};
    void* buffer_{nullptr};

public:
    NetworkService(const char* host, int port) {
        socket_fd_ = ::open_socket(host, port);
        // Охоронець закриє сокет, якщо наступний крок викине виняток:
        auto socket_rollback = ScopeGuard([this] noexcept {
            if (socket_fd_ >= 0) ::close(socket_fd_);
        });

        buffer_ = ::allocate_huge_buffer(); // може викинути виняток!

        // Все успішно: об'єкт повністю сконструйований, відкат скасовуємо
        socket_rollback.dismiss();
    }

    ~NetworkService() {
        if (buffer_) ::free_huge_buffer(buffer_);
        if (socket_fd_ >= 0) ::close(socket_fd_);
    }
};
