// C++ Implementation: Ідіоматичний C++20 із RAII та std::span

#include <iostream>
#include <string_view>
#include <span>
#include <system_error>
#include <memory>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <cstring>

namespace {
    constexpr std::string_view p2p_dev_path = "/dev/p2pmem0";
    constexpr size_t test_size = 4096;

    // RAII обгортка для файлового дескриптора
    class ScopedFd {
        int m_fd{-1};
    public:
        explicit ScopedFd(int fd) : m_fd(fd) {}
        ~ScopedFd() {
            if (m_fd >= 0) {
                ::close(m_fd);
            }
        }
        ScopedFd(const ScopedFd&) = delete;
        ScopedFd& operator=(const ScopedFd&) = delete;
        [[nodiscard]] int get() const noexcept { return m_fd; }
        [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }
    };

    // RAII обгортка для mmap відображення P2P пам'яті
    class P2PBufferMapping {
        void* m_addr{MAP_FAILED};
        size_t m_size{0};
    public:
        P2PBufferMapping(int fd, size_t size) : m_size(size) {
            m_addr = ::mmap(nullptr, m_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
            if (m_addr == MAP_FAILED) {
                throw std::system_error(errno, std::generic_category(), "Не вдалося виконати mmap P2P буфера");
            }
        }
        ~P2PBufferMapping() {
            if (m_addr != MAP_FAILED) {
                ::munmap(m_addr, m_size);
            }
        }
        P2PBufferMapping(const P2PBufferMapping&) = delete;
        P2PBufferMapping& operator=(const P2PBufferMapping&) = delete;

        [[nodiscard]] std::span<char> as_span() noexcept {
            return std::span<char>{static_cast<char*>(m_addr), m_size};
        }
    };
}

int main() {
    try {
        std::cout << "[C++] Відкриття P2PMEM пристрою: " << p2p_dev_path << "\n";
        ScopedFd dev_file{::open(p2p_dev_path.data(), O_RDWR)};
        if (!dev_file.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити пристрій");
        }

        P2PBufferMapping mapping{dev_file.get(), test_size};
        auto buffer = mapping.as_span();

        std::cout << "[C++] Успішно замаповано P2P буфер за адресою "
                  << static_cast<void*>(buffer.data()) << "\n";

        constexpr std::string_view payload = "P2PDMA C++20 idiomatic payload";
        std::ranges::copy(payload, buffer.begin());
        buffer[payload.size()] = '\0';

        std::cout << "[C++] Зчитано з P2P буфера: '" << buffer.data() << "'\n";
        std::cout << "[C++] Роботу з P2P буфером завершено чисто за допомогою RAII.\n";

    } catch (const std::exception& ex) {
        std::cerr << "[C++] Помилка виконання: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
