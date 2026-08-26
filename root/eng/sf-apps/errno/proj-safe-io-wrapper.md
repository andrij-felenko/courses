# ⚙️ Надійна обгортка системного вводу-виводу з обробкою EINTR та errno

Низькорівневий системний ввід-вивід у стандартах POSIX виглядає оманливо простим: виклики `read()` та `write()` приймають числовий дескриптор, вказівник на буфер пам'яті та запитану кількість байтів. Проте в реальному виробничому середовищі прямий виклик `write(fd, buf, len)` без спеціалізованої обгортки містить щонайменше чотири приховані архітектурні вразливості:

1. **Переривання асинхронними сигналами (`EINTR`)**: доставка будь-якого сигналу процесу (наприклад, таймера `SIGALRM`, сигналу зміни геометрії вікна термінала `SIGWINCH`, сигналу завершення нащадка `SIGCHLD` або сигналу профілювання `SIGPROF`) негайно зупиняє системний виклик, що перебуває в стані очікування, повертаючи `-1` із кодом `errno = EINTR`. Якщо прикладний код сприйме це як незворотну помилку й розірве з'єднання, передача даних аварійно зупиниться посеред нормальної роботи.
2. **Частковий запис або читання (Partial I/O)**: ядро операційної системи не зобов'язане передавати весь запитаний обсяг байтів за один виклик. Запит на запис 64 КіБ у сокет чи канал може передати лише 4 КіБ через заповнення буферів TCP-стека, повернути число `4096`, і програма зобов'язана самостійно змістити вказівник на буфер і викликати `write()` знову для решти даних.
3. **Гонтва закриття дескрипторів**: системний виклик `close(fd)` також може бути перерваний сигналом або викликати помилку `EBADF`, якщо дескриптор було помилково закрито двічі або паралельно звільнено в іншій нитці.
4. **Непотокобезпечне форматування помилок**: класична функція `strerror()` повертає вказівник на внутрішній статичний буфер стандартної бібліотеки C. Одночасний виклик `strerror()` із двох паралельних ниток призводить до взаємного пошкодження тексту повідомлень про помилки. Більше того, стандартизована реєнтрантна версія `strerror_r()` має дві несумісні сигнатури в екосистемах POSIX XSI та GNU libc.

Нижче наведено повну реалізацію надійної системи системного вводу-виводу двома мовами: чистою мовою C (стандарт C99/C11) та сучасною ідіоматичною мовою C++ (стандарт C++23).

---

### Порівняльна реалізація обгортки вводу-виводу

:::tabs
```c
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

/* Результат операції системного вводу-виводу */
typedef enum {
    IO_SUCCESS = 0,
    IO_EOF     = 1,
    IO_ERROR   = -1
} io_status_t;

/*
 * Потокобезпечне отримання опису помилки.
 * Підтримує як стандартну версію POSIX XSI strerror_r, так і GNU-специфічну.
 */
static void safe_strerror(int errnum, char *buf, size_t buflen) {
    if (buflen == 0) return;
    buf[0] = '\0';

#if defined(_GNU_SOURCE) && !defined(__APPLE__) && !defined(__FreeBSD__)
    /* GNU-версія: повертає char*, який може бути вказівником на статичний рядок */
    char *msg = strerror_r(errnum, buf, buflen);
    if (msg != buf) {
        strncpy(buf, msg, buflen - 1);
        buf[buflen - 1] = '\0';
    }
#else
    /* POSIX XSI-версія: повертає int (0 при успіху або код помилки) */
    if (strerror_r(errnum, buf, buflen) != 0) {
        snprintf(buf, buflen, "Unknown error %d", errnum);
    }
#endif
}

/*
 * Надійний повний запис буфера в дескриптор.
 * Гарантує передачу ВСІХ байтів count або повернення помилки.
 * Автоматично повторює спробу при перериванні сигналом (EINTR).
 */
io_status_t safe_write_all(int fd, const void *buf, size_t count,
                           size_t *bytes_written, int *out_errno) {
    const uint8_t *ptr = (const uint8_t *)buf;
    size_t total_written = 0;

    while (total_written < count) {
        ssize_t n = write(fd, ptr + total_written, count - total_written);
        if (n > 0) {
            total_written += (size_t)n;
            continue;
        }
        if (n == 0) {
            /* Запис 0 байтів при count > 0 свідчить про закриття каналу */
            if (bytes_written) *bytes_written = total_written;
            if (out_errno) *out_errno = EPIPE;
            return IO_ERROR;
        }
        if (n == -1) {
            int err = errno;
            if (err == EINTR) {
                /* Виклик перервано сигналом — повторюємо спробу негайно */
                continue;
            }
            /* Справжня апаратна чи системна помилка */
            if (bytes_written) *bytes_written = total_written;
            if (out_errno) *out_errno = err;
            return IO_ERROR;
        }
    }

    if (bytes_written) *bytes_written = total_written;
    if (out_errno) *out_errno = 0;
    return IO_SUCCESS;
}

/*
 * Надійне повне читання буфера з дескриптора.
 * Читає рівно count байтів, обробляє EINTR та виявляє кінець потоку (EOF).
 */
io_status_t safe_read_exact(int fd, void *buf, size_t count,
                            size_t *bytes_read, int *out_errno) {
    uint8_t *ptr = (uint8_t *)buf;
    size_t total_read = 0;

    while (total_read < count) {
        ssize_t n = read(fd, ptr + total_read, count - total_read);
        if (n > 0) {
            total_read += (size_t)n;
            continue;
        }
        if (n == 0) {
            /* Досягнуто кінця файлу або сокет закрито віддаленою стороною */
            if (bytes_read) *bytes_read = total_read;
            if (out_errno) *out_errno = 0;
            return (total_read == 0) ? IO_EOF : IO_ERROR;
        }
        if (n == -1) {
            int err = errno;
            if (err == EINTR) {
                /* Переривання сигналом — продовжуємо читання */
                continue;
            }
            if (bytes_read) *bytes_read = total_read;
            if (out_errno) *out_errno = err;
            return IO_ERROR;
        }
    }

    if (bytes_read) *bytes_read = total_read;
    if (out_errno) *out_errno = 0;
    return IO_SUCCESS;
}

/*
 * Безпечне закриття дескриптора з обробкою помилок.
 */
int safe_close(int fd, int *out_errno) {
    if (fd < 0) return 0;
    int res = close(fd);
    if (res == -1) {
        int err = errno;
        if (out_errno) *out_errno = err;
        return -1;
    }
    if (out_errno) *out_errno = 0;
    return 0;
}
```
```cpp
#include <cerrno>
#include <cstring>
#include <expected>
#include <memory>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <system_error>
#include <unistd.h>
#include <utility>

namespace sys {

/* Типізована категорія системних помилок POSIX */
class PosixError {
public:
    explicit PosixError(int code) : code_(code) {}

    [[nodiscard]] int code() const noexcept { return code_; }

    [[nodiscard]] std::string message() const {
        char buf[256];
#if defined(_GNU_SOURCE) && !defined(__APPLE__) && !defined(__FreeBSD__)
        char *msg = strerror_r(code_, buf, sizeof(buf));
        return std::string(msg);
#else
        if (strerror_r(code_, buf, sizeof(buf)) == 0) {
            return std::string(buf);
        }
        return "Unknown error " + std::to_string(code_);
#endif
    }

private:
    int code_;
};

/*
 * RAII-обгортка над файловим дескриптором POSIX.
 * Гарантує закриття дескриптора при виході з області видимості,
 * забороняє копіювання та підтримує семантику переміщення.
 */
class FileDescriptor {
public:
    constexpr FileDescriptor() noexcept : fd_(-1) {}
    explicit constexpr FileDescriptor(int fd) noexcept : fd_(fd) {}

    ~FileDescriptor() { reset(); }

    FileDescriptor(const FileDescriptor &) = delete;
    FileDescriptor &operator=(const FileDescriptor &) = delete;

    FileDescriptor(FileDescriptor &&other) noexcept : fd_(other.release()) {}

    FileDescriptor &operator=(FileDescriptor &&other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    explicit operator bool() const noexcept { return valid(); }

    [[nodiscard]] int release() noexcept {
        return std::exchange(fd_, -1);
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_;
};

/*
 * Надійний повний запис послідовності байтів у дескриптор.
 * Повертає std::expected з кількістю записаних байтів або системною помилкою.
 */
[[nodiscard]] inline std::expected<size_t, PosixError>
write_all(int fd, std::span<const std::byte> data) noexcept {
    size_t total_written = 0;

    while (total_written < data.size()) {
        const auto remaining = data.subspan(total_written);
        ssize_t n = ::write(fd, remaining.data(), remaining.size());

        if (n > 0) {
            total_written += static_cast<size_t>(n);
            continue;
        }
        if (n == 0) {
            return std::unexpected(PosixError(EPIPE));
        }
        if (n == -1) {
            int err = errno;
            if (err == EINTR) {
                continue; // Перервано сигналом — повторюємо
            }
            return std::unexpected(PosixError(err));
        }
    }

    return total_written;
}

/*
 * Надійне повне читання буфера з дескриптора.
 * Заповнює весь переданий span або повертає помилку/ознаку передчасного EOF.
 */
[[nodiscard]] inline std::expected<size_t, PosixError>
read_exact(int fd, std::span<std::byte> buffer) noexcept {
    size_t total_read = 0;

    while (total_read < buffer.size()) {
        auto remaining = buffer.subspan(total_read);
        ssize_t n = ::read(fd, remaining.data(), remaining.size());

        if (n > 0) {
            total_read += static_cast<size_t>(n);
            continue;
        }
        if (n == 0) {
            // Передчасний EOF до повного заповнення буфера
            return std::unexpected(PosixError(ECONNABORTED));
        }
        if (n == -1) {
            int err = errno;
            if (err == EINTR) {
                continue; // Перервано сигналом — продовжуємо
            }
            return std::unexpected(PosixError(err));
        }
    }

    return total_read;
}

} // namespace sys
```
:::

---

### Детальний розбір архітектурних рішень та механізмів

Розглянемо покроково, чому кожен окремий елемент наведеного коду побудовано саме так, які пастки середовища виконання він знешкоджує та як він поводиться в ядрі операційної системи.

#### 1. Апаратна ізоляція побічного стану через локальні змінні
У мові C однією з найпоширеніших помилок є пряме передавання `errno` у функцію логування після виконання проміжного очищення:

:::tabs
```c
int n = write(fd, ptr, len);
if (n == -1) {
    close(temp_fd); /* Цей системний виклик може змінити стан errno */
    log_error(errno); /* Помилка: прочитано статус від close(), а не від write() */
}
```
```cpp
ssize_t n = ::write(fd, ptr, len);
if (n == -1) {
    ::close(temp_fd); // Може перезаписати стан errno
    log_error(errno); // Помилка: втрачено початкову причину збою
}
```
:::

У нашій обгортці значення `errno` фіксується в локальній змінній `int err = errno;` **до** виконання будь-яких додаткових інструкцій або переходів. Локальна змінна розміщується безпосередньо в апаратному регістрі процесора або на фреймі стека поточної функції. Подальші системні виклики, які можуть відбутися всередині функцій очищення ресурсів, модифікують локальну пам'ять нитки (TLS), але не можуть змінити значення на стеку.

#### 2. Поведінка циклу при частковому записі (Partial Write)
Коли програма записує дані у файловий дескриптор, підключений до сокета TCP або міжпроцесного каналу (pipe), розмір буфера передачі ядра обмежений параметром `SO_SNDBUF` (зазвичай від 16 КіБ до кількох мегабайтів). Якщо програма передає буфер розміром 1 Мегабайт, ядро виконує атомарне копіювання лише тієї частини даних, яка поміщається у вільні сокетні буфери `sk_buff`, і негайно повертає фактичну кількість скопійованих байтів (наприклад, 65536).

Якщо викликач не перевіряє повернене число й вважає, що виклик `write()` передав усі дані цілком, хвіст повідомлення губиться. Наша функція `safe_write_all` підтримує інваріант залишкового зміщення:
```
remaining_bytes = count - total_written
current_pointer = ptr + total_written
```
Цикл триває доти, доки `total_written` не зрівняється з `count`, гарантуючи монолітну доставку прикладного кадру.

#### 3. Семантика переміщення та автоматичне керування ресурсами в C++
У реалізації на C++ клас `FileDescriptor` реалізує фундаментальну ідіому RAII (англ. *Resource Acquisition Is Initialization* — захоплення ресурсу є ініціалізацією). Конструктор за замовчуванням створює неініціалізований дескриптор із числовим значенням `-1`. Явний конструктор приймає сирий числовий дескриптор від викликів `open()`, `socket()` або `accept()`.

Конструктори копіювання та оператори присвоєння копіюванням примусово видалено через `= delete`. Це унеможливлює випадкове копіювання об'єкта дескриптора: якби два незалежні C++ об'єкти володіли одним числовим дескриптором `fd = 3`, їхні деструктори викликали б `::close(3)` двічі. Другий виклик закрив би дескриптор, який операційна система вже могла виділити іншій нитці для нового файлу або сокета, спричинивши катастрофічний збій дескрипторної таблиці.

Конструктор переміщення `FileDescriptor(FileDescriptor&& other)` використовує функцію `std::exchange(other.fd_, -1)`, яка атомарно забирає числовий дескриптор у старого об'єкта й записує туди безпечний маркер `-1`. Деструктор старого об'єкта виконує перевірку `if (fd_ >= 0)` і не здійснює жодних системних викликів.

#### 4. Застосування `std::expected` замість винятків на гарячому шляху
Функції `sys::write_all` та `sys::read_exact` використовують шаблон `std::expected<size_t, PosixError>` (введений у C++23). На відміну від механізму винятків (`throw` / `catch`), що вимагає побудови структур розкрутки стека (stack unwinding tables за стандартом Itanium ABI), `std::expected` упаковує результат або об'єкт помилки у компактний тип-суму на стеку. Якщо помилка виникає регулярно (наприклад, `EPIPE` при відключенні клієнтів або `EAGAIN` при спустошенні черг), програма не витрачає тисячі тактів процесора на перехоплення винятків, зберігаючи детермінований час відгуку.
