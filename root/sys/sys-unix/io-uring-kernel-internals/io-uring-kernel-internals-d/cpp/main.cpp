#include <liburing.h>
#include <fcntl.h>
#include <unistd.h>
#include <iostream>
#include <vector>
#include <span>
#include <system_error>
#include <memory>

// RAII обгортка для файлового дескриптора
class FileDescriptor {
    int fd_ = -1;
public:
    explicit FileDescriptor(int fd) noexcept : fd_(fd) {}
    ~FileDescriptor() { if (fd_ >= 0) ::close(fd_); }
    
    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;
    
    FileDescriptor(FileDescriptor&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    FileDescriptor& operator=(FileDescriptor&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
    
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

// RAII обгортка для екземпляра io_uring
class UringRing {
    struct io_uring ring_{};
    bool initialized_ = false;
public:
    explicit UringRing(unsigned int entries, unsigned int flags = 0) {
        int ret = io_uring_queue_init(entries, &ring_, flags);
        if (ret < 0) {
            throw std::system_error(-ret, std::generic_category(), "io_uring_queue_init failed");
        }
        initialized_ = true;
    }

    ~UringRing() {
        if (initialized_) {
            io_uring_queue_exit(&ring_);
        }
    }

    UringRing(const UringRing&) = delete;
    UringRing& operator=(const UringRing&) = delete;

    [[nodiscard]] struct io_uring* get() noexcept { return &ring_; }

    void submit_read(int fd, std::span<char> buffer, uint64_t offset, uint64_t user_data) {
        struct io_uring_sqe* sqe = io_uring_get_sqe(&ring_);
        if (!sqe) {
            throw std::runtime_error("Submission Queue is full");
        }
        io_uring_prep_read(sqe, fd, buffer.data(), static_cast<unsigned int>(buffer.size()), offset);
        io_uring_sqe_set_data64(sqe, user_data);
        
        int ret = io_uring_submit(&ring_);
        if (ret < 0) {
            throw std::system_error(-ret, std::generic_category(), "io_uring_submit failed");
        }
    }

    struct io_uring_cqe* wait_cqe() {
        struct io_uring_cqe* cqe = nullptr;
        int ret = io_uring_wait_cqe(&ring_, &cqe);
        if (ret < 0) {
            throw std::system_error(-ret, std::generic_category(), "io_uring_wait_cqe failed");
        }
        return cqe;
    }

    void cqe_seen(struct io_uring_cqe* cqe) noexcept {
        io_uring_cqe_seen(&ring_, cqe);
    }
};

int main() {
    constexpr unsigned int queue_depth = 4;
    constexpr size_t block_size = 4096;

    try {
        UringRing ring(queue_depth);
        FileDescriptor fd(::open("test.txt", O_RDONLY));
        
        if (!fd.valid()) {
            std::cerr << "Помилка відкриття файлу test.txt\n";
            return 1;
        }

        std::vector<char> buffer(block_size);
        constexpr uint64_t request_id = 1001;

        // Подання асинхронного запиту через безпечну C++ обгортку
        ring.submit_read(fd.get(), buffer, 0, request_id);

        // Очікування результату
        struct io_uring_cqe* cqe = ring.wait_cqe();

        if (cqe->res < 0) {
            std::cerr << "Помилка читання: " << std::generic_category().message(-cqe->res) << "\n";
        } else {
            std::cout << "Успішно прочитано " << cqe->res << " байтів."
                      << " Request ID: " << io_uring_cqe_get_data64(cqe) << "\n";
        }

        ring.cqe_seen(cqe);
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
