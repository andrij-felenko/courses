#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

class SeekableTail {
public:
    static constexpr size_t kChunkSize = 4096;

    static bool print_tail(std::string_view filepath, size_t target_lines) {
        int fd = ::open(filepath.data(), O_RDONLY);
        if (fd < 0) {
            std::cerr << "Не вдалося відкрити файл\n";
            return false;
        }

        // Автоматичне закриття дескриптора при виході (RAII)
        struct FdCloser {
            int fd;
            ~FdCloser() { if (fd >= 0) ::close(fd); }
        } closer{fd};

        off_t file_size = ::lseek(fd, 0, SEEK_END);
        if (file_size == static_cast<off_t>(-1) || file_size == 0) {
            return true;
        }

        off_t pos = file_size;
        size_t lines_found = 0;
        std::vector<char> buffer(kChunkSize);
        off_t print_start_pos = 0;

        while (pos > 0 && lines_found <= target_lines) {
            size_t bytes_to_read = (pos >= static_cast<off_t>(kChunkSize)) 
                                   ? kChunkSize : static_cast<size_t>(pos);
            pos -= bytes_to_read;

            if (::lseek(fd, pos, SEEK_SET) == static_cast<off_t>(-1)) {
                return false;
            }

            ssize_t n_read = ::read(fd, buffer.data(), bytes_to_read);
            if (n_read <= 0) break;

            std::span<const char> chunk{buffer.data(), static_cast<size_t>(n_read)};

            for (ssize_t i = n_read - 1; i >= 0; --i) {
                if (pos + i == file_size - 1 && chunk[i] == '\n') {
                    continue; // Пропускаємо фінальний перевод рядка
                }

                if (chunk[i] == '\n') {
                    ++lines_found;
                    if (lines_found == target_lines) {
                        print_start_pos = pos + i + 1;
                        goto do_output;
                    }
                }
            }
        }

    do_output:
        if (::lseek(fd, print_start_pos, SEEK_SET) == static_cast<off_t>(-1)) {
            return false;
        }

        ssize_t bytes_in = 0;
        while ((bytes_in = ::read(fd, buffer.data(), buffer.size())) > 0) {
            if (::write(STDOUT_FILENO, buffer.data(), bytes_in) < 0) {
                return false;
            }
        }

        return true;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <файл> [рядків]\n";
        return 1;
    }
    size_t lines = (argc > 2) ? std::stoul(argv[2]) : 10;
    return SeekableTail::print_tail(argv[1], lines) ? 0 : 1;
}
