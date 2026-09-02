#pragma once

// Тонка обгортка над тими місцями POSIX, де C віддає пару "-1 і errno".
//
// Далі по коду перевірок на -1 майже немає: невдача або перетворюється на
// виняток, або лишається всередині кроку, який рахує свої невдачі сам.
// Заголовок навмисно суцільно inline: окремої одиниці трансляції тут нема
// на що витрачати.

#include <cerrno>
#include <cstring>
#include <filesystem>
#include <iostream>
#include <string>
#include <string_view>
#include <system_error>
#include <utility>

#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

namespace boot {

// Пара "-1 і errno" стає винятком: жодна гілка не поїде далі мовчки.
[[noreturn]] inline void fail(std::string what)
{
    throw std::system_error(errno, std::system_category(), std::move(what));
}

inline void checked(int rc, std::string what)
{
    if (rc < 0)
        fail(std::move(what));
}

// Некритична невдача: сказати вголос і йти далі. Виштовхуємо одразу —
// консоль і пам'ять під буфером можуть зникнути наступним кроком.
inline void warn(std::string_view what)
{
    std::cerr << "switch_root: " << what << '\n' << std::flush;
}

// errno викликач читає САМ, першим ділом після невдалого виклику: побудова
// повідомлення для першого аргументу має право його зіпсувати.
inline void warn(std::string_view what, int err)
{
    std::cerr << "switch_root: " << what << ": " << std::strerror(err) << '\n'
              << std::flush;
}

inline struct ::stat lstat_of(const std::filesystem::path& path)
{
    struct ::stat st {};
    if (::lstat(path.c_str(), &st) != 0)
        fail("lstat " + path.string());
    return st;
}

// Дескриптор, який закривається сам. Обхід дерева ми ведемо не шляхами, а
// дескрипторами (openat/unlinkat): шлях під нами міг би підмінити симвлінк,
// а дескриптор указує на конкретний inode — і гілок виходу тут стільки,
// що ручний close колись та й загубився б.
class UniqueFd {
public:
    UniqueFd() = default;
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(std::exchange(other.fd_, -1)) {}

    UniqueFd& operator=(UniqueFd&& other) noexcept
    {
        if (this != &other) {
            reset();
            fd_ = std::exchange(other.fd_, -1);
        }
        return *this;
    }

    ~UniqueFd() { reset(); }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    explicit operator bool() const noexcept { return valid(); }

    void reset() noexcept
    {
        if (fd_ >= 0) {
            // Закриття тут — прибирання: скаржитися нікому, а кидати
            // з деструктора не можна.
            ::close(fd_);
            fd_ = -1;
        }
    }

    // Віддати володіння тому, хто закриє дескриптор сам (fdopendir, ядро
    // після execve, стандартні потоки процесу).
    [[nodiscard]] int release() noexcept { return std::exchange(fd_, -1); }

private:
    int fd_ = -1;
};

// Каталог для обходу: без переходу за симвлінками й без успадкування
// дескриптора наступним execve.
[[nodiscard]] inline UniqueFd open_dir(int at, const char* name)
{
    return UniqueFd(
        ::openat(at, name, O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC));
}

}  // namespace boot
