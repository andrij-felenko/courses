#include <algorithm>
#include <iostream>
#include <string>
#include <span>
#include <memory>
#include <stdexcept>
#include <system_error>
#include <cstddef>
#include <cstdlib>
#include <fcntl.h>
#include <unistd.h>

// RAII Обгортка для безпечної роботи із зонованими файлами у zonefs
class ZonedFile {
private:
    int m_fd{-1};

public:
    explicit ZonedFile(const std::string& path) {
        // Режим O_APPEND гарантує використання команди Zone Append у ядрі
        m_fd = ::open(path.c_str(), O_WRONLY | O_APPEND | O_DIRECT);
        if (m_fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити файл зони");
        }
    }

    ~ZonedFile() {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
    }

    // Забороняємо копіювання файлового дескриптора
    ZonedFile(const ZonedFile&) = delete;
    ZonedFile& operator=(const ZonedFile&) = delete;

    // Дозволяємо переміщення (Move semantics)
    ZonedFile(ZonedFile&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }

    ZonedFile& operator=(ZonedFile&& other) noexcept {
        if (this != &other) {
            if (m_fd >= 0) ::close(m_fd);
            m_fd = other.m_fd;
            other.m_fd = -1;
        }
        return *this;
    }

    // Атомарне скидання зони у стан Empty (Reset Write Pointer)
    void reset() {
        if (::ftruncate(m_fd, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка скидання зони через ftruncate");
        }
    }

    // Безаварійний запис буфера даних через Zone Append
    std::size_t append(std::span<const std::byte> data) {
        if (data.size() % 512 != 0) {
            throw std::invalid_argument("Буфер даних повинен бути вирівняний на 512 байтів");
        }

        ssize_t written = ::write(m_fd, data.data(), data.size());
        if (written < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка виконання Zone Append");
        }
        return static_cast<std::size_t>(written);
    }
};

// Спеціалізований виділювач вирівняної пам'яті для O_DIRECT I/O
template <typename T>
struct AlignedDeleter {
    void operator()(T* ptr) const {
        ::free(ptr);
    }
};

template <typename T>
using UniqueAlignedPtr = std::unique_ptr<T[], AlignedDeleter<T>>;

template <typename T>
UniqueAlignedPtr<T> make_aligned_buffer(std::size_t alignment, std::size_t count) {
    void* ptr = nullptr;
    if (::posix_memalign(&ptr, alignment, count * sizeof(T)) != 0) {
        throw std::bad_alloc();
    }
    return UniqueAlignedPtr<T>(static_cast<T*>(ptr));
}

int main() {
    try {
        constexpr std::size_t alignment = 4096;
        constexpr std::size_t buffer_size = 4096;

        auto buffer = make_aligned_buffer<std::byte>(alignment, buffer_size);
        std::fill_n(buffer.get(), buffer_size, std::byte{0x7E});

        ZonedFile zone("/mnt/zonefs/seq/0");
        zone.reset();

        std::span<const std::byte> payload(buffer.get(), buffer_size);
        std::size_t bytes_written = zone.append(payload);

        std::cout << "[C++] Успішно записано " << bytes_written << " байтів у zonefs (RAII)\n";

    } catch (const std::exception& ex) {
        std::cerr << "[C++] Помилка виконання ZBD операції: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
