#pragma once

#include <csignal>
#include <cstdint>
#include <expected>
#include <system_error>

#include <termios.h>

namespace tty {

using Status = std::expected<void, std::error_code>;

std::expected<termios, std::error_code> attributes(int fd);

// Профілі беруть копію й повертають змінену: жодних вихідних параметрів
// і жодного стану між викликами.
termios make_sane(termios t) noexcept;
termios make_cooked(termios t) noexcept;
termios make_raw(termios t) noexcept;
termios make_noecho(termios t) noexcept;

// tcsetattr плюс звірка: POSIX вважає успіхом і часткове застосування,
// тож питаємо ядро, що воно взяло насправді.
Status apply_verified(int fd, int optional_actions, const termios& want);

// Скидання модальних регістрів емулятора. Усередині лише write(),
// тож дозволене в обробнику сигналу.
void emulator_reset(int fd) noexcept;

// Сирий режим як ресурс: конструктор перемикає, деструктор повертає —
// хоч по return, хоч по винятку, хоч по сигналу через SignalGuard.
class RawMode {
public:
    explicit RawMode(int fd, std::uint8_t vmin = 1, std::uint8_t vtime = 0);
    ~RawMode();

    RawMode(const RawMode&) = delete;
    RawMode& operator=(const RawMode&) = delete;

    int fd() const noexcept { return fd_; }
    bool active() const noexcept { return active_ != 0; }
    const termios& saved() const noexcept { return saved_; }

    // Обидва — async-signal-safe: усередині тільки tcsetattr і write.
    void restore() noexcept;
    void reapply() noexcept;

private:
    int fd_;
    termios saved_{};
    termios raw_{};
    volatile std::sig_atomic_t active_{0};
};

// Сигнальний протокол сеансу: живе рівно стільки, скільки RawMode.
class SignalGuard {
public:
    explicit SignalGuard(RawMode& mode);
    ~SignalGuard();

    SignalGuard(const SignalGuard&) = delete;
    SignalGuard& operator=(const SignalGuard&) = delete;

    // 1, якщо розмір вікна змінювався; прапорець при цьому скидається.
    static bool window_resized() noexcept;
};

// Читання одного байта з розрізненням EINTR і справжньої помилки.
enum class ReadResult { Byte, Eof, Interrupted, Error };
ReadResult read_byte(int fd, unsigned char& out) noexcept;

}  // namespace tty
