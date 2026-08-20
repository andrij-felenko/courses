# ⚙️ Універсальна RAII-обгортка для системних ресурсів

Низькорівневі системні інтерфейси ядра операційної системи та бібліотеки C оперують числовими дескрипторами (`int fd`, `HANDLE`, `SOCKET`) або нетипізованими вказівниками. Якщо для кожного такого ресурсу писати окремий клас-обгортку вручну, проєкт швидко наповнюється однотипним кодом, де легко помилитися в реалізації семантики переміщення чи забути позначити деструктор як `noexcept`.

Нижче побудовано універсальний, повністю узагальнений шаблонний RAII-клас `UniqueHandle`, який інкапсулює будь-який системний дескриптор, унеможливлює подвійне звільнення, підтримує безпечну передачу власності та повністю розчиняється компілятором у машинному коді без жодних накладних витрат.

## Задача й архітектурні вимоги

Системні ресурси принципово відрізняються від звичайної пам'яті в купі кількома властивостями:
- **Різні недійсні значення (sentinels):** для файлового дескриптора POSIX помилковим станом є `-1`; для покажчика `FILE*` — `NULL` (або `nullptr`); для дескриптора файлу Windows `HANDLE` помилкою є `INVALID_HANDLE_VALUE` (що дорівнює `(HANDLE)-1`), тоді як для дескрипторів подій чи потоків Windows тим самим sentinel є `NULL`.
- **Різні функції закриття:** `close(fd)`, `fclose(fp)`, `CloseHandle(h)`, `closesocket(s)` або специфічні бібліотечні функції на зразок `pcap_close()`.

Обгортка для системного ресурсу зобов'язана виконувати п'ять непорушних контрактів:

1. **Ексклюзивне володіння (Move-only):** конструктор копіювання та оператор копіювального присвоєння мають бути видалені (`= delete`), щоб два об'єкти не могли володіти одним дескриптором водночас і не спричинили подвійне закриття.
2. **Безпечне переміщення:** конструктор переміщення та оператор переміщувального присвоєння забирають ресурс у джерела, переводячи джерело у відповідне недійсне значення.
3. **Деструктор без винятків:** деструктор зобов'язаний бути позначений `noexcept` і викликати функцію очищення лише тоді, коли об'єкт реально володіє валідним дескриптором.
4. **Контрольоване скидання та відчуження:** метод `.reset()` детерміновано закриває старий дескриптор і приймає новий; метод `.release()` розриває зв'язок об'єкта з ресурсом без його закриття (для передачі у володіння сторонньому C API).
5. **Нульові витрати:** розмір екземпляра класу в пам'яті має дорівнювати розміру сирого дескриптора (наприклад, 4 байти для `int` або 8 байтів для покажчика), а методи мають повністю вбудовуватися (inline).

## Реалізація узагальненого шаблону на C++

Для гнучкості відокремимо поведінку конкретного ресурсу (недійсне значення та спосіб закриття) у структуру властивостей (*traits*). Це дозволяє використовувати один і той самий шаблонний клас `UniqueHandle` для файлів POSIX, сокетів, дескрипторів Windows API та графічних контекстів.

:::tabs
```cpp
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
```
```c
/* Порівняння: у чистому C доводиться писати явні функції 
   ініціалізації, перевірки та ручного виклику cleanup */
#include <unistd.h>
#include <fcntl.h>
#include <stdbool.h>

typedef struct {
    int fd;
} UniqueFdC;

static inline UniqueFdC fd_wrap(int fd) {
    UniqueFdC h = { fd };
    return h;
}

static inline void fd_close(UniqueFdC* h) {
    if (h && h->fd >= 0) {
        close(h->fd);
        h->fd = -1;
    }
}

static inline bool fd_is_valid(const UniqueFdC* h) {
    return h && h->fd >= 0;
}
```
:::

Зверніть увагу на використання `std::exchange(handle_, Traits::invalid())`. Ця стандартна функція атомарно для поточного потоку присвоює члену класу недійсне значення й повертає його старий стан. Це надійно захищає від повторного входу або помилок під час подвійного очищення.

Окрему увагу приділено методу `.put()`. У багатьох системних API (наприклад, `pipe(int pipefd[2])` або викликах Windows API) функція приймає покажчик на дескриптор і записує туди нове значення. Якщо викликати таку функцію над уже відкритим об'єктом без виклику `.reset()`, старий дескриптор тихо витече. Метод `.put()` спочатку звільняє попередній ресурс і лише потім віддає адресу внутрішнього поля.

## Розширення трейтів: підтримка Windows HANDLE

Завдяки відокремленню поведінки у структуру властивостей той самий шаблон `UniqueHandle` без жодних змін адаптується для роботи з системними дескрипторами Windows.

:::tabs
```cpp
#ifdef _WIN32
#include <windows.h>

// Трейт для дескрипторів файлів Windows
struct Win32FileHandleTraits {
    using HandleType = HANDLE;
    static HandleType invalid() noexcept { return INVALID_HANDLE_VALUE; }
    static void close(HandleType h) noexcept {
        if (h != INVALID_HANDLE_VALUE && h != NULL) {
            ::CloseHandle(h);
        }
    }
};

using UniqueWin32File = UniqueHandle<Win32FileHandleTraits>;
#endif
```
```c
#ifdef _WIN32
#include <windows.h>

typedef struct {
    HANDLE handle;
} UniqueWin32FileC;

static inline void win32_close(UniqueWin32FileC* h) {
    if (h && h->handle != INVALID_HANDLE_VALUE && h->handle != NULL) {
        CloseHandle(h->handle);
        h->handle = INVALID_HANDLE_VALUE;
    }
}
#endif
```
:::

## Реалізація еквівалентної безпечної обгортки в Rust

У мові Rust завдяки системі власності та вбудованому типажу `Drop` реалізація виглядає ще компактнішою. Оскільки в Rust усі типи є move-by-default (переміщуються за замовчуванням), розробнику не потрібно вручну писати конструктори переміщення та видаляти копіювання — компілятор робить це автоматично.

```rust
use std::os::raw::c_int;

// Власний безпечний дескриптор
pub struct SafeFd {
    fd: c_int,
}

impl SafeFd {
    pub const INVALID: c_int = -1;

    // Створення обгортки з перевіркою валідності
    pub fn new(fd: c_int) -> Option<Self> {
        if fd >= 0 {
            Some(Self { fd })
        } else {
            None
        }
    }

    // Доступ до сирого дескриптора без передачі власності
    pub fn raw(&self) -> c_int {
        self.fd
    }

    // Відчуження дескриптора (передача сирого значення без виклику Drop)
    pub fn into_raw(mut self) -> c_int {
        let fd = self.fd;
        self.fd = Self::INVALID;
        std::mem::forget(self); // скасовує виклик Drop
        fd
    }
}

// Реалізація RAII-очищення через типаж Drop
impl Drop for SafeFd {
    fn drop(&mut self) {
        if self.fd >= 0 {
            unsafe {
                libc::close(self.fd);
            }
        }
    }
}
```

## Практичне застосування та координація кількох ресурсів

Погляньмо, як використання `UniqueFd` радикально спрощує код роботи з кількома файлами або каналами (`pipe`) у порівнянні з традиційним C-кодом, перевантаженим блоками `goto`.

Уявімо задачу: відкрити вхідний файл, створити вихідний файл і скопіювати дані блоками. У мові C у разі помилки на другому кроці розробник зобов'язаний пам'ятати закрити перший файл. Якщо додається третій ресурс — кількість гілок помилок зростає лавиноподібно.

:::tabs
```cpp
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
```
```c
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <stdio.h>

int copy_file_data_c(const char* src_path, const char* dst_path) {
    int in_fd = -1;
    int out_fd = -1;
    char* buffer = NULL;
    int status = -1;

    in_fd = open(src_path, O_RDONLY);
    if (in_fd < 0) {
        goto cleanup;
    }

    out_fd = open(dst_path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (out_fd < 0) {
        goto cleanup;
    }

    buffer = (char*)malloc(4096);
    if (!buffer) {
        goto cleanup;
    }

    while (1) {
        ssize_t bytes_read = read(in_fd, buffer, 4096);
        if (bytes_read < 0) {
            goto cleanup;
        }
        if (bytes_read == 0) {
            break;
        }

        ssize_t bytes_written = write(out_fd, buffer, (size_t)bytes_read);
        if (bytes_written != bytes_read) {
            goto cleanup;
        }
    }

    status = 0; // Успіх

cleanup:
    // Ручне розмотування ресурсів у зворотному порядку
    if (buffer) {
        free(buffer);
    }
    if (out_fd >= 0) {
        close(out_fd);
    }
    if (in_fd >= 0) {
        close(in_fd);
    }
    return status;
}
```
:::

## Крайові випадки: помилки під час закриття та EINTR

Низькорівневе закриття дескрипторів має тонку системну пастку, про яку часто забувають. Системний виклик `close()` у POSIX-системах може повернути помилку `-1` із кодом `EINTR` (переривання виклику сигналом).

У старих підручниках іноді рекомендували повторювати виклик `close()` у циклі `while (close(fd) == -1 && errno == EINTR)`. Проте в сучасному ядрі Linux та більшості Unix-подібних ОС дескриптор **звільняється таблицею процесу ще до повернення помилки**. Якщо повторити виклик `close()` для того самого дескриптора, можна випадково закрити абсолютно інший файл, який інший потік програми встиг відкрити в цей самий мілісекундний проміжок (класична гонка дескрипторів — *fd reuse race*).

Тому правильна системна реалізація в `PosixFdTraits` викликає `::close(fd)` рівно один раз і ігнорує повернений статус, що бездоганно узгоджується з вимогою `noexcept` для деструкторів.

## Аналіз машинного коду та оптимізацій

Поширена хибна думка полягає в тому, що додатковий клас-обгортка з конструкторами й деструкторами сповільнює виконання порівняно з рукописним викликом `close()`.

Якщо скомпілювати наведений C++ приклад компілятором GCC або Clang з увімкненою оптимізацією (`-O2`):
1. **Інлайнінг:** Усі методи `get()`, `release()`, `reset()` та деструктор `~UniqueHandle()` повністю вбудовуються в місце виклику.
2. **Відсутність структури в пам'яті:** Компілятор не виділяє під об'єкт окреме місце в оперативній пам'яті; дескриптор живе виключно в регістрі процесора (наприклад, у регістрі `%edi` для архітектури x86-64).
3. **Прямі інструкції:** Код виходу з функції зводиться до прямої інструкції перевірки регістра на `-1` (`test %edi, %edi`) та асемблерного переходу на системну функцію `call close`.

Таким чином, узагальнений клас `UniqueHandle` реалізує фундаментальний принцип C++: безпека досягається на етапі компіляції, а згенерований машинний код виявляється настільки ж швидким і компактним, як і бездоганно написаний низькорівневий код на C.
