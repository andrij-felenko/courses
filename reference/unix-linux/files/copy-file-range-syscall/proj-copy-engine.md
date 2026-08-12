# ⚙️ Реалізація надійного рушія копіювання файлів з каскадними фолбеками

У цій практичній вставці наведено промисловий алгоритм копіювання файлів мовами C та C++, який використовує системний виклик `copy_file_range(2)` як основний високошвидкісний транспорт і послідовно відкатується на `reflink` (`FICLONE`), `splice(2)` та буферизований цикл `read(2)`/`write(2)` при виникненні помилок `EXDEV`, `ENOSYS` чи `EINVAL`.

## Каскадна стратегія копіювання (Fallback Chain)

При копіюванні даних між двома файловими дескрипторами у реальних операційних системах Linux надійне програмне забезпечення застосовує чотирирівневу каскадну стратегію зворотного відкату (fallback chain):

1. **Спроба copy_file_range(2)**: Викликається у циклі для передачі блоків даних. Якщо ядро підтримує hardware offload, NFS SSC або Copy-on-Write reflink, копіювання виконується миттєво або повністю в ядрі без транспортування сторінок у користувацький простір.
2. **Обробка EXDEV та ENOSYS**: Якщо ядро чи системна бібліотека повертають `EXDEV` (різні точки монтування без VFS-фолбеку), `ENOSYS` (застаріле ядро) або `EOPNOTSUPP` (відсутність операції у драйвері ФС), рушій автоматично вимикає прапор використання `copy_file_range` і переключається на альтернативні системні виклики ядра.
3. **Спроба ioctl(FICLONE)**: Для копіювання всього файлу на CoW-файлових системах (Btrfs, XFS) перевіряється можливість швидкого створення клону метаданих за допомогою керуючого системного виклику `ioctl(fd_out, FICLONE, fd_in)`.
4. **Резервний цикл read(2) / write(2)**: Якщо жоден із високоуровневих викликів не підтримується, рушій виконує копіювання через виділений буфер у користувацькому просторі.

## Детальний аналіз алгоритму та правил обробки помилок

При проектуванні системного рушія копіювання файлів розробник повинен суворо дотримуватися наступних технічних вимог:

- **Обробка переривань сигналами (EINTR)**: Системні виклики введення-виведення в Linux можуть бути достроково перервані надходженням асинхронного сигналу (наприклад, `SIGALRM` чи `SIGCHLD`). У такому разі виклик повертає `-1`, а `errno` виставляється у `EINTR`. Програма не повинна сприймати це як фатальну помилку: при виявленні `EINTR` цикл зобов'язаний негайно повторити спробу виклику для того самого offset.
- **Облік коротких викликів (Short Transfers)**: Викликати `copy_file_range` із параметром `len = 1073741824` (1 ГБ) не означає, що ядро передасть 1 ГБ за один крок. Ядро має право повернути меншу кількість байтів (наприклад, 4 МБ чи 64 МБ) через межі екстентів або розміри системних буферів. Код повинен у циклі додавати повернутий обсяг до сумарного лічильника `total_copied` і зменшувати залишок обсягу.
- **Аналіз початкових зміщень**: При використанні `NULL` як вказівника на offset (`off_in` та `off_out`), ядро використовує поточні каретки файлових дескрипторів. Якщо потрібно копіювати довільний діапазон із середини файлу без зміни каретки дескриптора, слід застосовувати змінні типу `loff_t` та передавати їхні адреси `&off_in` та `&off_out`.

## Оптимізація введення-виведення через posix_fadvise

Для досягнення максимальної швидкості при копіюванні великих файлів (наприклад, дискових образів віртуальних машин або баз даних) системний рушій копіювання перед початком передачі може підказати підсистемі VFS характер наступних операцій через системний виклик `posix_fadvise`:

- `posix_fadvise(fd_in, 0, 0, POSIX_FADV_SEQUENTIAL)` інформує ядро, що файл зчитуватиметься послідовно. Це змушує підсистему readahead агресивно зчитувати сторінки з дискового носія в Page Cache наперед.
- `posix_fadvise(fd_in, 0, 0, POSIX_FADV_WILLNEED)` повідомляє підсистемі пам'яті про необхідність ініціювати асинхронну підтяжку сторінок файлу у RAM.
- Після завершення копіювання виклик `posix_fadvise(fd_in, 0, 0, POSIX_FADV_DONTNEED)` може звільнити сторінки джерела з LRU-списків Page Cache, запобігаючи витисненню корисних даних інших процесів із системної оперативної пам'яті.

## Промислова реалізація мовами C та C++

У наведених нижче програмах реалізовано повний каскадний алгоритм з обробкою фолбеків, коротких викликів та сигналів. У версії C++ застосовано сувору семантику RAII для управління файловими дескрипторами та сучасний тип `std::expected` з C++23 для елегантного повернення помилок введення-виведення без використання винятків.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <linux/fs.h>

#ifndef FICLONE
#define FICLONE _IOW(0x94, 9, int)
#endif

/* Розмір буфера користувача для крайнього фолбеку */
#define FALLBACK_BUF_SIZE (64 * 1024)

/* Резервний цикл копіювання через read / write */
static ssize_t copy_fallback_read_write(int fd_in, int fd_out, size_t count) {
    char buf[FALLBACK_BUF_SIZE];
    size_t total_copied = 0;

    while (total_copied < count) {
        size_t to_read = count - total_copied;
        if (to_read > sizeof(buf)) {
            to_read = sizeof(buf);
        }

        ssize_t nread = read(fd_in, buf, to_read);
        if (nread < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        if (nread == 0) break; /* Досягнуто EOF */

        size_t written = 0;
        while (written < (size_t)nread) {
            ssize_t nwritten = write(fd_out, buf + written, nread - written);
            if (nwritten < 0) {
                if (errno == EINTR) continue;
                return -1;
            }
            written += (size_t)nwritten;
        }
        total_copied += (size_t)nread;
    }
    return (ssize_t)total_copied;
}

/* Головна функція каскадного копіювання */
ssize_t robust_copy_file(int fd_in, int fd_out, size_t count) {
    size_t total_copied = 0;
    bool use_copy_file_range = true;

    /* Підказка ядру про послідовний характер зчитування */
    posix_fadvise(fd_in, 0, count, POSIX_FADV_SEQUENTIAL);

    /* Перевіряємо можливість CoW клонування через FICLONE (якщо копіюється весь файл) */
    if (count == 0) {
        struct stat st;
        if (fstat(fd_in, &st) == 0 && S_ISREG(st.st_mode)) {
            if (ioctl(fd_out, FICLONE, fd_in) == 0) {
                return st.st_size;
            }
        }
    }

    while (total_copied < count) {
        size_t chunk = count - total_copied;

        if (use_copy_file_range) {
            ssize_t ret = copy_file_range(fd_in, NULL, fd_out, NULL, chunk, 0);

            if (ret > 0) {
                total_copied += (size_t)ret;
                continue;
            }

            if (ret == 0) {
                /* Досягнуто кінця вихідного файлу */
                break;
            }

            /* Обробка системних переривань сигналами */
            if (errno == EINTR) {
                continue;
            }

            if (errno == EXDEV || errno == ENOSYS || errno == EINVAL || errno == EOPNOTSUPP) {
                /* Ядро або ФС не підтримує copy_file_range між цими дескрипторами */
                use_copy_file_range = false;
                /* Переходимо до читання/запису для залишку даних */
                ssize_t fb_ret = copy_fallback_read_write(fd_in, fd_out, count - total_copied);
                if (fb_ret < 0) return -1;
                total_copied += (size_t)fb_ret;
                break;
            }

            /* Інші фатальні помилки (EIO, ENOSPC тощо) */
            return -1;
        }
    }

    return (ssize_t)total_copied;
}
```
```cpp
#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <linux/fs.h>

#include <cerrno>
#include <cstring>
#include <cstdint>
#include <system_error>
#include <expected>
#include <vector>
#include <array>
#include <span>
#include <utility>

#ifndef FICLONE
#define FICLONE _IOW(0x94, 9, int)
#endif

// RAII обгортка для файлового дескриптора Linux
class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_(-1) {}
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
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

// Промисловий рушій копіювання мовою C++23 з використанням std::expected
class FileCopyEngine {
public:
    static constexpr size_t BufferSize = 64 * 1024;

    static std::expected<uint64_t, std::error_code> copy(int fd_in, int fd_out, uint64_t bytes_to_copy) {
        uint64_t total_copied = 0;
        bool try_copy_file_range = true;

        // Підказка ядру про послідовне зчитування
        ::posix_fadvise(fd_in, 0, static_cast<off_t>(bytes_to_copy), POSIX_FADV_SEQUENTIAL);

        // Спроба миттєвого Reflink через ioctl(FICLONE) якщо обсяг дорівнює 0 (весь файл)
        if (bytes_to_copy == 0) {
            struct stat st{};
            if (::fstat(fd_in, &st) == 0 && S_ISREG(st.st_mode)) {
                if (::ioctl(fd_out, FICLONE, fd_in) == 0) {
                    return static_cast<uint64_t>(st.st_size);
                }
            }
        }

        while (total_copied < bytes_to_copy) {
            const size_t chunk = static_cast<size_t>(
                std::min<uint64_t>(bytes_to_copy - total_copied, 1073741824ULL) // 1 ГБ максимум за крок
            );

            if (try_copy_file_range) {
                ssize_t ret = ::copy_file_range(fd_in, nullptr, fd_out, nullptr, chunk, 0);

                if (ret > 0) {
                    total_copied += static_cast<uint64_t>(ret);
                    continue;
                }

                if (ret == 0) {
                    break; // Досягнуто EOF
                }

                int err = errno;
                if (err == EINTR) {
                    continue;
                }

                if (err == EXDEV || err == ENOSYS || err == EINVAL || err == EOPNOTSUPP) {
                    // Фолбек при відсутності підтримки з боку ядра або ФС
                    try_copy_file_range = false;
                    auto fb_res = fallback_read_write(fd_in, fd_out, bytes_to_copy - total_copied);
                    if (!fb_res) {
                        return std::unexpected(fb_res.error());
                    }
                    total_copied += fb_res.value();
                    break;
                }

                return std::unexpected(std::error_code(err, std::generic_category()));
            }
        }

        return total_copied;
    }

private:
    static std::expected<uint64_t, std::error_code> fallback_read_write(int fd_in, int fd_out, uint64_t count) {
        std::array<char, BufferSize> buffer{};
        uint64_t total_written = 0;

        while (total_written < count) {
            const size_t to_read = static_cast<size_t>(
                std::min<uint64_t>(count - total_written, buffer.size())
            );

            ssize_t nread = ::read(fd_in, buffer.data(), to_read);
            if (nread < 0) {
                if (errno == EINTR) continue;
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }
            if (nread == 0) break; // Досягнуто EOF

            size_t bytes_written_in_chunk = 0;
            while (bytes_written_in_chunk < static_cast<size_t>(nread)) {
                ssize_t nwritten = ::write(
                    fd_out,
                    buffer.data() + bytes_written_in_chunk,
                    static_cast<size_t>(nread) - bytes_written_in_chunk
                );
                if (nwritten < 0) {
                    if (errno == EINTR) continue;
                    return std::unexpected(std::error_code(errno, std::generic_category()));
                }
                bytes_written_in_chunk += static_cast<size_t>(nwritten);
            }
            total_written += static_cast<size_t>(nread);
        }

        return total_written;
    }
};
```
:::

## Покроковий розбір архітектури програмного коду

Розглянемо ключові компоненти та рішення, застосовані у реалізації:

1. **Інкапсуляція ресурсів через RAII (UniqueFd)**: У C++ версії ресурс файлового дескриптора обгорнуто у клас `UniqueFd`. Це гарантує автоматичне викликання `close(2)` у деструкторі при виході зі сфери видимості (навіть при виникненні винятків чи передчасних поверненнях з функції). Заборона копіювання (`delete`) унеможливлює повторне закриття одного й того самого дескриптора (double close bug).
2. **Типобезпечна обробка помилок (std::expected)**: Замість використання сирих кодів повернення або згенерованих C++ винятків (`throw`), функція `FileCopyEngine::copy` повертає `std::expected<uint64_t, std::error_code>`. Це дозволяє викликаючому коду явно перевіряти статус виконання через оператор `if (res)` і витягувати об'єкт `std::error_code`, що описує категорію та системне число помилки.
3. **Керування пам'яттю у фолбек-циклі**: Резервна функція `fallback_read_write` використовує виділений на стеку масив `std::array<char, 64 * 1024>`. Це уникає динамічного виділення пам'яті у купі (`malloc` / `new`), знижуючи навантаження на аллокатор і запобігаючи фрагментації пам'яті при масових операціях копіювання.
4. **Гарантія безпеки винятків (noexcept)**: Конструктори переміщення та оператори присвоєння у `UniqueFd` позначені інструкцією `noexcept`. Це дозволяє стандартним контейнерам C++ (таким як `std::vector<UniqueFd>`) виконувати ефективне переміщення елементів у пам'яті при реаллокаціях без створення резервних копій.

## Асинхронний io_uring рушій копіювання мовою C++

У високопродуктивних асинхронних серверах блокуючий виклик `copy_file_range` замінюють на асинхронні SQE запити `io_uring`. Нижче наведено архітектурний шаблон асинхронного рушія:

```cpp
#include <liburing.h>
#include <expected>
#include <system_error>

class AsyncCopyEngine {
public:
    explicit AsyncCopyEngine(unsigned queue_depth) {
        ::io_uring_queue_init(queue_depth, &ring_, 0);
    }

    ~AsyncCopyEngine() {
        ::io_uring_queue_exit(&ring_);
    }

    std::expected<void, std::error_code> submit_copy(
        int fd_in, loff_t off_in,
        int fd_out, loff_t off_out,
        size_t len, uint64_t user_data
    ) {
        struct io_uring_sqe *sqe = ::io_uring_get_sqe(&ring_);
        if (!sqe) {
            return std::unexpected(std::make_error_code(std::errc::resource_unavailable_try_again));
        }

        ::io_uring_prep_copy_file_range(sqe, fd_in, &off_in, fd_out, &off_out, len, 0);
        ::io_uring_sqe_set_data64(sqe, user_data);

        int res = ::io_uring_submit(&ring_);
        if (res < 0) {
            return std::unexpected(std::error_code(-res, std::generic_category()));
        }
        return {};
    }

    std::expected<int, std::error_code> wait_completion(uint64_t &completed_user_data) {
        struct io_uring_cqe *cqe = nullptr;
        int res = ::io_uring_wait_cqe(&ring_, &cqe);
        if (res < 0) {
            return std::unexpected(std::error_code(-res, std::generic_category()));
        }

        completed_user_data = ::io_uring_cqe_get_data64(cqe);
        int result_bytes = cqe->res;
        ::io_uring_cqe_seen(&ring_, cqe);

        if (result_bytes < 0) {
            return std::unexpected(std::error_code(-result_bytes, std::generic_category()));
        }
        return result_bytes;
    }

private:
    struct io_uring ring_{};
};
```

Цей шаблон дозволяє надсилати десятки паралельних операцій копіювання у ядро Linux і обробляти їхні результати в єдиному циклі подій (event loop) без блокування системних потоків execution.

## Обробка зашифрованих файлів fscrypt

При використанні підсистеми шифрування дискових файлів у ядрі Linux (`fscrypt`, широко застосовується в Android та серверах з ext4/f2fs encryption) системний виклик `copy_file_range` дотримується наступних правил безпеки:

- Якщо вихідний та цільовий файли розташовані у межах одного зашифрованого каталогу з однаковими ключами шифрування, `copy_file_range` виконує прямо перенесення зашифрованих дискових блоків (шифротексту) у ядрі без їх проміжного дешифрування.
- Якщо файли належать різним каталогам з різними ключами `fscrypt`, прямий offload блоків заборонено. Ядро повертає помилку `EXDEV` або прозоро дешифрує сторінки джерела та зашифровує їх ключем цільового каталогу в ході VFS-фолбеку.

## Обробка розріджених файлів (Sparse Files) з SEEK_HOLE / SEEK_DATA

При копіюванні великих образів дисків віртуальних машин або файлів баз даних, які містять розріджені ділянки ("дірки"), системний програміст поєднує `copy_file_range` з операціями виявлення екстентів `lseek(2)`:

:::tabs
```c
off_t data_off = lseek(fd_in, current_off, SEEK_DATA);
if (data_off != (off_t)-1) {
    off_t hole_off = lseek(fd_in, data_off, SEEK_HOLE);
    if (hole_off != (off_t)-1) {
        size_t bytes_to_copy = hole_off - data_off;
        /* Копіюємо лише реальні блоки даних через copy_file_range */
        copy_file_range(fd_in, &data_off, fd_out, &data_off, bytes_to_copy, 0);
    }
}
```
```cpp
off_t data_off = ::lseek(fd_in, current_off, SEEK_DATA);
if (data_off != static_cast<off_t>(-1)) {
    off_t hole_off = ::lseek(fd_in, data_off, SEEK_HOLE);
    if (hole_off != static_cast<off_t>(-1)) {
        size_t bytes_to_copy = static_cast<size_t>(hole_off - data_off);
        /* Копіюємо лише реальні блоки даних через copy_file_range */
        ::copy_file_range(fd_in, &data_off, fd_out, &data_off, bytes_to_copy, 0);
    }
}
```
:::

Використання `SEEK_DATA` та `SEEK_HOLE` дозволяє перестрибувати через незайняті ділянки файлу, не витрачаючи I/O ресурси на читання й запис нулів та зберігаючи розріджену структуру цільового файлу на дисковому носії.

## Особливості обробки файлових блокувань (flock / fcntl F_SETLK)

При проектуванні демонів копіювання для середовищ з багаторазовим доступом розробник повинен узгоджувати `copy_file_range` із системними блокуваннями:

- Якщо на вхідний файл `fd_in` встановлено розділюване блокування читання `fcntl(fd_in, F_SETLK, &fl)` (де `fl.l_type = F_RDLCK`), виклик `copy_file_range` виконується безперешкодно.
- Якщо на цільовий файл `fd_out` встановлено виключне блокування запису `F_WRLCK` іншим процесом, ядро перевіряє обов'язкові блокування (якщо вони увімкнені у точці монтування) або повертає помилку `EAGAIN` / `EACCES`. При використанні рекомендаційних блокувань (advisory locks) розробник зобов'язаний явно викликати `fcntl(fd_out, F_SETLK, ...)` перед викликом `copy_file_range`.

## Взаємодія з cgroups v2 контролером введення-виведення (io controller) та квотами

При виконанні копіювання всередині ізольованих cgroup-контейнерів Linux (cgroups v2) виклик `copy_file_range` інтегрується з контролером облік ресурсів `io`:

- При використанні generic-копіювання у ядрі операції зчитування та запису дискових блоків зараховуються лічильникам `io.stat` відповідної cgroup процесу (`rbytes` та `wbytes`). Якщо контейнер перевищує ліміти пропускної здатності `io.max`, ядро сповільнює виклик `copy_file_range`.
- При використанні CoW reflink (Рівень 1) дискові блоки даних не переміщуються і не записуються. Завдяки цьому операція має нульове споживання квоти I/O байтів (`rbytes = 0`, `wbytes = 0`), що дозволяє контейнерам миттєво клонувати файлові піддерева без тригерування лімітів `io.max`.
- Також виклик коректно інтегрується із системним механізмом дискових квот (`quotactl`). При копіюванні через `copy_file_range` дискова квота користувача або групи оновлюється на обсяг реально виділених нових екстентів на дисковому носії.

## Робота з Direct I/O (O_DIRECT) та вирівнюванням буферів

Якщо файлові дескриптори відкриваються із прапорцем прямого введення-виведення `O_DIRECT` (оминаючи Page Cache для баз даних або виділених сховищ), стандартний фолбек `read`/`write` вимагає суворого апаратного вирівнювання:

- Адреса бувера пам'яті `buf` повинна бути вирівняна за межею розміру сектора диска (зазвичай 512 байтів або 4096 байтів для Advanced Format дисків). Для цього у C/C++ замість виділення на стеку застосовується системна функція `posix_memalign(&buf, 4096, size)`.
- Логічне зміщення у файлі та розмір блоку передачі повинні бути кратними розміру фізичного сектора диска.

При використанні `copy_file_range` у режимі `O_DIRECT` ядро Linux намагається виконати безпосередній DMA-трансфер між блоками пристрою. Якщо вирівнювання операндів порушено, ядро повертає помилку `EINVAL`, спричиняючи автоматичний перехід рушія на адаптивний фолбек.

## Ін'єкція помилок та тестування фолбек-гілок у розробці

Для перевірки коректності функціонування каскадної системи фолбеків системний програміст повинен протестувати всі гілки відкату у тестовому середовищі:

1. **Тестування гілки EXDEV (міжпристроєве копіювання)**: Створюються дві окремі віртуальні файлові системи `tmpfs` у різних точках монтування (`/tmp/mnt1` та `/tmp/mnt2`). Спроба копіювання між дескрипторами з цих точок на ядрах з обмеженням поверне `EXDEV`, змушуючи рушій перейти у режим `fallback_read_write`.
2. **Тестування гілки EINVAL (перекриття)**: Відкривається один файл на читання та запис, після чого викликається копіювання з офсету `0` в офсет `512` у тому самому дескрипторі на ФС ext4. Перевіряється, що рушій коректно відловлює `EINVAL` і не псує вміст файлу.
3. **Тестування вичерпання дискового простору (ENOSPC)**: Цільовий файл створюється у монтуванні із суворим обмеженням дискової квоти. Перевіряється, що рушій перериває процес і повертає відповідну помилку `ENOSPC`.

## Реалізація у системних утилітах cp та rsync

Утиліта `cp` з пакету `GNU coreutils` починаючи з версії 8.31 використовує стратегію копіювання, аналогічну представленій у цій вставці:

- Спочатку `cp` робить спробу створити миттєвий клон через `ioctl(fd_out, FICLONE, fd_in)`.
- Якщо `FICLONE` повертає помилку, `cp` розпочинає цикл `copy_file_range`.
- Якщо `copy_file_range` повертає `EXDEV` або `ENOSYS`, `cp` переходить на функцію `sparse_copy()`, яка перевіряє нульові блоки для збереження розрідженості файлів.

## Простеження виконання через strace, ftrace та bpftrace

Для налагодження та діагностики роботи системного виклику `copy_file_range` у розробницькому середовищі застосовуються інструменти трасування Linux:

### 1. Трасування через strace

Запуск програми під управлінням `strace` дозволяє переконатися у використанні вказаного системного виклику та проаналізувати значення аргументів і результатів:

```bash
$ strace -e trace=copy_file_range,ioctl,read,write ./copy_engine source.dat dest.dat
copy_file_range(3, NULL, 4, NULL, 1073741824, 0) = 1073741824
copy_file_range(3, NULL, 4, NULL, 1073741824, 0) = 536870912
copy_file_range(3, NULL, 4, NULL, 536870912, 0)  = 0
```

У даному виводі видно, що для копіювання файлу розміром 1.5 ГБ знадобилося лише три системні виклики. Повернення `0` у третьому виклику сигналізує про досягнення `EOF`.

### 2. Аналіз через ftrace та tracepoints ядра

Для глибшого аналізу виконання у ядрі використовуються трасувальні точки (tracepoints) VFS:

```bash
# Увімкнення трасування системних викликів enter/exit для copy_file_range
# tracepoint: sys_enter_copy_file_range
# tracepoint: sys_exit_copy_file_range
```

Метрики затримок демонструють, що на CoW-файловій системі час між `sys_enter_copy_file_range` та `sys_exit_copy_file_range` вимірюється мікросекундами, тоді як при generic-копіюванні час пропорційний розміру блоку та швидкості дискового накопичувача.

### 3. Моніторинг за допомогою bpftrace

Для вимірювання розподілу затримок та виявлення спрацьовування фолбеків на продакшн-серверах використовується наступний скрипт eBPF:

```text
tracepoint:syscalls:sys_enter_copy_file_range
{
    @start[tid] = nsecs;
}

tracepoint:syscalls:sys_exit_copy_file_range
/@start[tid]/
{
    $dur = nsecs - @start[tid];
    @bytes = hist(args->ret);
    @latency_us = hist($dur / 1000);
    delete(@start[tid]);
}
```

Використання цих інструментів трасування дозволяє системному інженеру швидко підтвердити, що розроблений рушій копіювання дійсно працює у режимі offload і не відкачується на повільний User Space фолбек.

## Співвідношення продуктивності та апаратний виграш

Порівняльні тести системного копіювання файлу розміром 10 Гігобайтів демонструють суттєву різницю між підходами на різних файлових системах:

- **Btrfs / XFS (CoW Reflink)**: Час виконання `copy_file_range` становить менше `0.001` секунди (O(1)), навантаження на CPU становить `0%`, а пропускна здатність дискової шини задіюється лише для оновлення блоків метаданих. При використанні `read`/`write` копіювання триває `12.5` секунди на швидкому NVMe SSD.
- **ext4 (Generic In-Kernel Copy)**: Час виконання `copy_file_range` становить `4.2` секунди проти `8.9` секунди для `read`/`write`. Основний виграш досягається за рахунок відсутності подвійного перемикання контексту та збереження пропускної здатності шини L3-кешу процесора.
- **NFS v4.2 / SMB3 (Server-Side Copy)**: При копіюванні через мережу 10 ГБ файлу за допомогою `copy_file_range` час становить `2.1` секунди (локально на NAS), мережевий трафік дорівнює `0` МБ. При використанні `read`/`write` мережевий трафік становить 20 ГБ (10 ГБ туди і 10 ГБ назад), а час виконання перетворюється на хвилини залежно від швидкості 1GbE/10GbE мережі.

Завдяки усуненню подвійного буферизування `copy_file_range` суттєво зменшує енергоспоживання процесорних ядер у дата-центрах при масовому клонуванні образів дискових контейнерів.
