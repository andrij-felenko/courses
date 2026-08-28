#include <sys/types.h>
#include <sys/capsicum.h>
#include <fcntl.h>
#include <unistd.h>

#include <iostream>
#include <span>
#include <vector>
#include <string_view>
#include <system_error>
#include <cerrno>

namespace sandbox {

/* RAII-обгортка над файловим дескриптором з підтримкою Capsicum */
class CapabilityDescriptor {
public:
    explicit CapabilityDescriptor(int fd = -1) noexcept : fd_{fd} {}

    ~CapabilityDescriptor() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    CapabilityDescriptor(const CapabilityDescriptor&) = delete;
    CapabilityDescriptor& operator=(const CapabilityDescriptor&) = delete;

    CapabilityDescriptor(CapabilityDescriptor&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }

    CapabilityDescriptor& operator=(CapabilityDescriptor&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) {
                ::close(fd_);
            }
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }

    template <typename... RightsArgs>
    void limit_rights(RightsArgs... args) {
        cap_rights_t rights;
        ::cap_rights_init(&rights, args..., 0);
        if (::cap_rights_limit(fd_, &rights) < 0) {
            throw std::system_error(errno, std::generic_category(), "cap_rights_limit failed");
        }
    }

private:
    int fd_;
};

void enter_sandbox() {
    if (::cap_enter() < 0) {
        throw std::system_error(errno, std::generic_category(), "cap_enter failed");
    }
}

void transform_data(int fd_in, int fd_out) {
    std::vector<char> buffer(4096);
    while (true) {
        ssize_t bytes_read = ::read(fd_in, buffer.data(), buffer.size());
        if (bytes_read < 0) {
            throw std::system_error(errno, std::generic_category(), "read failed");
        }
        if (bytes_read == 0) {
            break;
        }

        std::span<char> chunk{buffer.data(), static_cast<size_t>(bytes_read)};
        for (char& ch : chunk) {
            if (ch >= 'a' && ch <= 'z') {
                ch = static_cast<char>(ch - 32);
            } else if (ch >= 'A' && ch <= 'Z') {
                ch = static_cast<char>(ch + 32);
            }
        }

        ssize_t bytes_written = ::write(fd_out, chunk.data(), chunk.size());
        if (bytes_written != bytes_read) {
            throw std::system_error(errno, std::generic_category(), "write failed");
        }
    }
}

} // namespace sandbox

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Використання: " << argv[0] << " <input_file> <output_file>\n";
        return 1;
    }

    try {
        int raw_in = ::open(argv[1], O_RDONLY);
        if (raw_in < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to open input file");
        }
        sandbox::CapabilityDescriptor input_fd(raw_in);

        int raw_out = ::open(argv[2], O_WRONLY | O_CREAT | O_TRUNC, 0644);
        if (raw_out < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to open output file");
        }
        sandbox::CapabilityDescriptor output_fd(raw_out);

        /* Фаза звуження: обмежуємо дескриптори за принципом найменших привілеїв */
        input_fd.limit_rights(CAP_READ, CAP_SEEK, CAP_FSTAT);
        output_fd.limit_rights(CAP_WRITE, CAP_SEEK, CAP_FSTAT, CAP_FTRUNCATE);

        /* Фаза ізоляції: перехід у capability mode */
        sandbox::enter_sandbox();

        /* Безпечна потокова обробка */
        sandbox::transform_data(input_fd.native_handle(), output_fd.native_handle());

    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка виконання: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
