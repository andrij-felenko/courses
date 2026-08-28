#include <iostream>
#include <cstdint>
#include <cstring>
#include <vector>
#include <span>
#include <system_error>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <fcntl.h>

namespace jit {

/**
 * @brief Безпечний клас подвійного JIT-буфера з автоматичним керуванням життєвим циклом (RAII).
 */
class DualMappedBuffer {
public:
    explicit DualMappedBuffer(size_t requested_size) {
        long page_size = ::sysconf(_SC_PAGESIZE);
        size_ = (requested_size + page_size - 1) & ~(page_size - 1);

        /* 1. Створення анонімного файлового об'єкта */
        fd_ = ::memfd_create("jit_cpp_dual_mapped", MFD_CLOEXEC);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "memfd_create failed");
        }

        /* 2. Встановлення ємності буфера */
        if (::ftruncate(fd_, static_cast<off_t>(size_)) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "ftruncate failed");
        }

        /* 3. Створення відображення запису (RW) */
        void *w_ptr = ::mmap(nullptr, size_, PROT_READ | PROT_WRITE, MAP_SHARED, fd_, 0);
        if (w_ptr == MAP_FAILED) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "mmap RW failed");
        }
        write_view_ = static_cast<uint8_t *>(w_ptr);

        /* 4. Створення відображення виконання (RX) */
        void *x_ptr = ::mmap(nullptr, size_, PROT_READ | PROT_EXEC, MAP_SHARED, fd_, 0);
        if (x_ptr == MAP_FAILED) {
            ::munmap(write_view_, size_);
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "mmap RX failed");
        }
        exec_view_ = x_ptr;
    }

    ~DualMappedBuffer() noexcept {
        if (exec_view_ && exec_view_ != MAP_FAILED) {
            ::munmap(exec_view_, size_);
        }
        if (write_view_ && write_view_ != MAP_FAILED) {
            ::munmap(write_view_, size_);
        }
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    /* Семантика переміщення з передачею володіння дескрипторами */
    DualMappedBuffer(const DualMappedBuffer &) = delete;
    DualMappedBuffer &operator=(const DualMappedBuffer &) = delete;

    DualMappedBuffer(DualMappedBuffer &&other) noexcept
        : fd_(other.fd_), size_(other.size_),
          write_view_(other.write_view_), exec_view_(other.exec_view_) {
        other.fd_ = -1;
        other.size_ = 0;
        other.write_view_ = nullptr;
        other.exec_view_ = nullptr;
    }

    DualMappedBuffer &operator=(DualMappedBuffer &&other) noexcept {
        if (this != &other) {
            this->~DualMappedBuffer();
            fd_ = other.fd_;
            size_ = other.size_;
            write_view_ = other.write_view_;
            exec_view_ = other.exec_view_;
            other.fd_ = -1;
            other.size_ = 0;
            other.write_view_ = nullptr;
            other.exec_view_ = nullptr;
        }
        return *this;
    }

    /**
     * @brief Запис скомпільованого машинного коду через безпечний span.
     */
    void emit_code(std::span<const uint8_t> code, size_t offset = 0) {
        if (offset + code.size() > size_) {
            throw std::out_of_range("JIT buffer capacity exceeded");
        }
        std::memcpy(write_view_ + offset, code.data(), code.size());
        __builtin___clear_cache(reinterpret_cast<char *>(write_view_ + offset),
                                reinterpret_cast<char *>(write_view_ + offset + code.size()));
    }

    /**
     * @brief Отримання типізованого покажчика на скомпільовану функцію.
     */
    template <typename FuncSig>
    [[nodiscard]] FuncSig get_function(size_t offset = 0) const noexcept {
        const uint8_t *entry = static_cast<const uint8_t *>(exec_view_) + offset;
        return reinterpret_cast<FuncSig>(const_cast<uint8_t *>(entry));
    }

    [[nodiscard]] const void *exec_address() const noexcept { return exec_view_; }
    [[nodiscard]] const void *write_address() const noexcept { return write_view_; }

private:
    int fd_{-1};
    size_t size_{0};
    uint8_t *write_view_{nullptr};
    void *exec_view_{nullptr};
};

} // namespace jit

int main() {
    try {
        jit::DualMappedBuffer jit_buf(4096);

        std::cout << "[+] JIT RAII Buffer створено:\n"
                  << "    Write view (RW): " << jit_buf.write_address() << "\n"
                  << "    Exec view  (RX): " << jit_buf.exec_address() << "\n";

        /* Машинні інструкції x86-64 для f(a, b) = a * 3 + b + 7 */
        const std::vector<uint8_t> code = {
            0x48, 0x8d, 0x04, 0x7f, /* lea rax, [rdi + rdi*2] */
            0x48, 0x01, 0xf0,       /* add rax, rsi           */
            0x48, 0x83, 0xc0, 0x07, /* add rax, 0x07          */
            0xc3                    /* ret                    */
        };

        jit_buf.emit_code(code);

        using JITSignature = int64_t (*)(int64_t, int64_t);
        auto calculate = jit_buf.get_function<JITSignature>();

        int64_t a = 10;
        int64_t b = 5;
        int64_t res = calculate(a, b);

        std::cout << "[+] Результат виконання: calculate(" << a << ", " << b << ") = " << res << "\n";
        if (res == 42) {
            std::cout << "[✓] C++ JIT-тест пройдено успішно!\n";
        }
    } catch (const std::exception &ex) {
        std::cerr << "[-] Помилка JIT: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
