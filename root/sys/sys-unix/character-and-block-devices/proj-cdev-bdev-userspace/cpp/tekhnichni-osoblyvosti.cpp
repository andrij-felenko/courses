#include <iostream>
#include <vector>
#include <iomanip>
#include <span>
#include <system_error>
#include <cstdlib>
#include <cstdint>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>

// Обгортка для безпечного управління файловим дескриптором за допомогою RAII
class CharacterDeviceReader {
    int fd_{-1};

public:
    explicit CharacterDeviceReader(const char* path) {
        fd_ = ::open(path, O_RDONLY);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "Не вдалося відкрити символьний пристрій");
        }
    }

    ~CharacterDeviceReader() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    // Заборона копіювання для запобігання подвійному закриттю дескриптора
    CharacterDeviceReader(const CharacterDeviceReader&) = delete;
    CharacterDeviceReader& operator=(const CharacterDeviceReader&) = delete;

    // Переміщення ресурсу
    CharacterDeviceReader(CharacterDeviceReader&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    std::vector<uint8_t> read_bytes(size_t count) {
        std::vector<uint8_t> buffer(count);
        ssize_t bytes_read = ::read(fd_, buffer.data(), buffer.size());
        
        if (bytes_read < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "Помилка зчитування з символьного пристрою");
        }
        
        buffer.resize(static_cast<size_t>(bytes_read));
        return buffer;
    }
};

int main() {
    try {
        CharacterDeviceReader dev("/dev/urandom");
        auto random_data = dev.read_bytes(64);

        std::cout << "Успішно прочитано " << random_data.size() 
                  << " байтів (C++ RAII):\n";
        
        // Сучасне ітерування по суцільному масиву байтів
        std::span<const uint8_t> data_span{random_data};
        for (size_t i = 0; i < data_span.size(); ++i) {
            std::cout << std::hex << std::setw(2) << std::setfill('0') 
                      << static_cast<int>(data_span[i]) << " ";
            if ((i + 1) % 16 == 0) {
                std::cout << "\n";
            }
        }
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка виконання: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
