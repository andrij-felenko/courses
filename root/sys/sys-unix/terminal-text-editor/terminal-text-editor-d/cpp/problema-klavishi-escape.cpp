#include <unistd.h>
#include <cerrno>
#include <optional>
#include <stdexcept>

enum class KeyCode : int {
    ArrowLeft = 1000,
    ArrowRight,
    ArrowUp,
    ArrowDown,
    Delete,
    Home,
    End,
    PageUp,
    PageDown,
    Escape = 27
};

class KeyDecoder {
public:
    static int read_key() {
        char c{0};
        while (true) {
            const ssize_t bytes_read = ::read(STDIN_FILENO, &c, 1);
            if (bytes_read == 1) break;
            if (bytes_read == -1 && errno != EAGAIN && errno != EINTR) {
                throw std::runtime_error("Помилка читання дескриптора STDIN_FILENO");
            }
        }

        if (c != '\x1b') {
            return static_cast<unsigned char>(c);
        }

        char seq[3]{};
        if (::read(STDIN_FILENO, &seq[0], 1) != 1) return static_cast<int>(KeyCode::Escape);
        if (::read(STDIN_FILENO, &seq[1], 1) != 1) return static_cast<int>(KeyCode::Escape);

        if (seq[0] == '[') {
            if (seq[1] >= '0' && seq[1] <= '9') {
                if (::read(STDIN_FILENO, &seq[2], 1) != 1) return static_cast<int>(KeyCode::Escape);
                if (seq[2] == '~') {
                    switch (seq[1]) {
                        case '1': return static_cast<int>(KeyCode::Home);
                        case '3': return static_cast<int>(KeyCode::Delete);
                        case '4': return static_cast<int>(KeyCode::End);
                        case '5': return static_cast<int>(KeyCode::PageUp);
                        case '6': return static_cast<int>(KeyCode::PageDown);
                        case '7': return static_cast<int>(KeyCode::Home);
                        case '8': return static_cast<int>(KeyCode::End);
                        default: break;
                    }
                }
            } else {
                switch (seq[1]) {
                    case 'A': return static_cast<int>(KeyCode::ArrowUp);
                    case 'B': return static_cast<int>(KeyCode::ArrowDown);
                    case 'C': return static_cast<int>(KeyCode::ArrowRight);
                    case 'D': return static_cast<int>(KeyCode::ArrowLeft);
                    case 'H': return static_cast<int>(KeyCode::Home);
                    case 'F': return static_cast<int>(KeyCode::End);
                    default: break;
                }
            }
        } else if (seq[0] == 'O') {
            switch (seq[1]) {
                case 'H': return static_cast<int>(KeyCode::Home);
                case 'F': return static_cast<int>(KeyCode::End);
                default: break;
            }
        }
        return static_cast<int>(KeyCode::Escape);
    }
};
