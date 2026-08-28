#include <stdexcept>
#include <vector>
#include <span>

void copy_file_data(const char* src_path, const char* dst_path) {
    // 1. Захоплення першого ресурсу
    UniqueFd in_fd(::open(src_path, O_RDONLY));
    if (!in_fd) {
        throw std::runtime_error("Не вдалося відкрити вхідний файл");
    }

    // 2. Захоплення другого ресурсу (якщо тут станеться виняток — in_fd закриється автоматично)
    UniqueFd out_fd(::open(dst_path, O_WRONLY | O_CREAT | O_TRUNC, 0644));
    if (!out_fd) {
        throw std::runtime_error("Не вдалося створити вихідний файл");
    }

    std::vector<char> buffer(4096);
    while (true) {
        ssize_t bytes_read = ::read(in_fd.get(), buffer.data(), buffer.size());
        if (bytes_read < 0) {
            throw std::runtime_error("Помилка читання даних");
        }
        if (bytes_read == 0) {
            break; // Досягнуто кінця файлу
        }

        ssize_t bytes_written = ::write(out_fd.get(), buffer.data(), static_cast<size_t>(bytes_read));
        if (bytes_written != bytes_read) {
            throw std::runtime_error("Помилка запису даних");
        }
    }

    // При виході з функції обидва дескриптори гарантовано закриваються в порядку:
    // 1. out_fd
    // 2. in_fd
}
