#include <iostream>
#include <string>
#include <vector>
#include <optional>
#include <stdexcept>
#include <format>
#include <unistd.h>
#include <termios.h>
#include <sys/ioctl.h>

enum class Key : int {
    ArrowLeft = 1000,
    ArrowRight,
    ArrowUp,
    ArrowDown,
    DeleteKey,
    HomeKey,
    EndKey,
    PageUp,
    PageDown,
    CtrlQ = 17 // 'q' & 0x1f
};

// RAII обгортка для безпечного керування сирим режимом термінала
class TerminalSession {
public:
    TerminalSession() {
        if (tcgetattr(STDIN_FILENO, &orig_termios_) == -1) {
            throw std::runtime_error("Не вдалося отримати параметри termios");
        }

        struct termios raw = orig_termios_;
        raw.c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);
        raw.c_oflag &= ~(OPOST);
        raw.c_cflag |= (CS8);
        raw.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
        raw.c_cc[VMIN] = 0;
        raw.c_cc[VTIME] = 1;

        if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) == -1) {
            throw std::runtime_error("Не вдалося встановити сирий режим термінала");
        }

        // Перемикання в альтернативний екран
        std::cout << "\x1b[?1049h" << std::flush;
    }

    ~TerminalSession() noexcept {
        // Повернення до основного екрана та відновлення канонічного режиму
        std::cout << "\x1b[?1049l\x1b[?25h" << std::flush;
        tcsetattr(STDIN_FILENO, TCSAFLUSH, &orig_termios_);
    }

    TerminalSession(const TerminalSession&) = delete;
    TerminalSession& operator=(const TerminalSession&) = delete;

private:
    struct termios orig_termios_{};
};

class TerminalEditor {
public:
    TerminalEditor() {
        update_window_size();
    }

    void run() {
        while (running_) {
            render();
            process_key();
        }
    }

private:
    int cursor_x_{0};
    int cursor_y_{0};
    int screen_rows_{24};
    int screen_cols_{80};
    bool running_{true};

    void update_window_size() {
        struct winsize ws{};
        if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws) == 0 && ws.ws_col > 0) {
            screen_cols_ = ws.ws_col;
            screen_rows_ = ws.ws_row;
        }
    }

    int read_raw_byte() const {
        char c{0};
        while (true) {
            const ssize_t bytes_read = ::read(STDIN_FILENO, &c, 1);
            if (bytes_read == 1) return static_cast<unsigned char>(c);
            if (bytes_read == -1 && errno != EAGAIN && errno != EINTR) {
                throw std::runtime_error("Помилка читання stdin");
            }
        }
    }

    int read_key() const {
        const int c = read_raw_byte();
        if (c != '\x1b') return c;

        char seq[3]{};
        if (::read(STDIN_FILENO, &seq[0], 1) != 1) return '\x1b';
        if (::read(STDIN_FILENO, &seq[1], 1) != 1) return '\x1b';

        if (seq[0] == '[') {
            if (seq[1] >= '0' && seq[1] <= '9') {
                if (::read(STDIN_FILENO, &seq[2], 1) != 1) return '\x1b';
                if (seq[2] == '~') {
                    switch (seq[1]) {
                        case '1': return static_cast<int>(Key::HomeKey);
                        case '3': return static_cast<int>(Key::DeleteKey);
                        case '4': return static_cast<int>(Key::EndKey);
                        case '5': return static_cast<int>(Key::PageUp);
                        case '6': return static_cast<int>(Key::PageDown);
                        case '7': return static_cast<int>(Key::HomeKey);
                        case '8': return static_cast<int>(Key::EndKey);
                    }
                }
            } else {
                switch (seq[1]) {
                    case 'A': return static_cast<int>(Key::ArrowUp);
                    case 'B': return static_cast<int>(Key::ArrowDown);
                    case 'C': return static_cast<int>(Key::ArrowRight);
                    case 'D': return static_cast<int>(Key::ArrowLeft);
                    case 'H': return static_cast<int>(Key::HomeKey);
                    case 'F': return static_cast<int>(Key::EndKey);
                }
            }
        } else if (seq[0] == 'O') {
            switch (seq[1]) {
                case 'H': return static_cast<int>(Key::HomeKey);
                case 'F': return static_cast<int>(Key::EndKey);
            }
        }
        return '\x1b';
    }

    void render() {
        std::string frame;
        frame.reserve(screen_rows_ * (screen_cols_ + 16));

        // Сховати курсор і скинути координати
        frame += "\x1b[?25l\x1b[H";

        for (int y = 0; y < screen_rows_; ++y) {
            if (y == screen_rows_ / 3) {
                std::string welcome = "C++ Terminal Text Engine -- Ready";
                if (static_cast<int>(welcome.size()) > screen_cols_) {
                    welcome.resize(screen_cols_);
                }
                int padding = (screen_cols_ - static_cast<int>(welcome.size())) / 2;
                if (padding > 0) {
                    frame += "~";
                    --padding;
                }
                frame.append(padding, ' ');
                frame += welcome;
            } else {
                frame += "~";
            }

            frame += "\x1b[K"; // Очистити рядок до кінця
            if (y < screen_rows_ - 1) {
                frame += "\r\n";
            }
        }

        // Позиціонування та відновлення видимості курсора
        frame += std::format("\x1b[{};{}H\x1b[?25h", cursor_y_ + 1, cursor_x_ + 1);

        ::write(STDOUT_FILENO, frame.data(), frame.size());
    }

    void process_key() {
        const int key = read_key();
        if (key == static_cast<int>(Key::CtrlQ)) {
            running_ = false;
            return;
        }

        switch (static_cast<Key>(key)) {
            case Key::ArrowLeft:
                if (cursor_x_ > 0) --cursor_x_;
                break;
            case Key::ArrowRight:
                if (cursor_x_ < screen_cols_ - 1) ++cursor_x_;
                break;
            case Key::ArrowUp:
                if (cursor_y_ > 0) --cursor_y_;
                break;
            case Key::ArrowDown:
                if (cursor_y_ < screen_rows_ - 1) ++cursor_y_;
                break;
            default:
                break;
        }
    }
};

int main() {
    try {
        TerminalSession session;
        TerminalEditor editor;
        editor.run();
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
