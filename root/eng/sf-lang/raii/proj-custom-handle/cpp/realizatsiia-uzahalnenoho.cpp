#include <utility>
#include <unistd.h>
#include <fcntl.h>
#include <iostream>

// Трейт для POSIX файлових дескрипторів
struct PosixFdTraits {
    using HandleType = int;
    static constexpr HandleType invalid() noexcept { return -1; }
    static void close(HandleType fd) noexcept {
        if (fd >= 0) {
            ::close(fd);
        }
    }
};

// Універсальна RAII-обгортка для будь-якого ресурсу
template <typename Traits>
class UniqueHandle {
public:
    using HandleType = typename Traits::HandleType;

    // Конструктор за замовчуванням створює недійсний дескриптор
    constexpr UniqueHandle() noexcept : handle_(Traits::invalid()) {}

    // Конструктор захоплює переданий сирий дескриптор
    explicit UniqueHandle(HandleType h) noexcept : handle_(h) {}

    // Деструктор: детерміновано звільняє ресурс
    ~UniqueHandle() noexcept {
        reset();
    }

    // Заборона копіювання: об'єкт володіє ресурсом монопольно
    UniqueHandle(const UniqueHandle&) = delete;
    UniqueHandle& operator=(const UniqueHandle&) = delete;

    // Конструктор переміщення: забирає дескриптор, обнуляючи джерело
    UniqueHandle(UniqueHandle&& other) noexcept 
        : handle_(other.release()) {}

    // Оператор переміщувального присвоєння з захистом від самоприсвоєння
    UniqueHandle& operator=(UniqueHandle&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    // Перевірка валідності в умовах if (handle)
    explicit operator bool() const noexcept {
        return handle_ != Traits::invalid();
    }

    // Отримання сирого значення для передачі в системні виклики
    [[nodiscard]] HandleType get() const noexcept {
        return handle_;
    }

    // Отримання адреси для функцій, що ініціалізують дескриптор через покажчик
    [[nodiscard]] HandleType* put() noexcept {
        reset();
        return &handle_;
    }

    // Відчуження ресурсу: повертає значення та скидає внутрішній стан без закриття
    HandleType release() noexcept {
        return std::exchange(handle_, Traits::invalid());
    }

    // Скидання: закриває старий ресурс і приймає новий
    void reset(HandleType new_handle = Traits::invalid()) noexcept {
        HandleType old = std::exchange(handle_, new_handle);
        if (old != Traits::invalid()) {
            Traits::close(old);
        }
    }

private:
    HandleType handle_;
};

// Зручний синонім типу для POSIX файлових дескрипторів
using UniqueFd = UniqueHandle<PosixFdTraits>;
