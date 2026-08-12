# ⚙️ Практикум: інспектування атрибутів файлу через statx у C та C++

Ця практична вставка демонструє розробку утиліти системного інспектування файлів з використанням розширеного системного виклику `statx(2)`. Приклад розбирає маскове узгодження полів (`stx_mask`), безпечне читання часу створення файлу (`btime`), визначення вимог вирівнювання для режиму `O_DIRECT` (`STATX_DIOALIGN`), перевірку розширених атрибутів `stx_attributes` та обробку ситуацій, коли системний виклик не підтримується ядром.

## Постановка задачі та архітектурні вимоги

При розробці системних утиліт, високопродуктивних баз даних або засобів резервного копіювання виникає потреба отримати розширену інформацію про файл без виконання серії коштовних системних викликів `ioctl` або `getsockopt`. 

Наша задача — створити консольну утиліту інспектування файлів, яка за один системний виклик `statx` здатна виконати наступний комплекс операцій:

1. **Запит розширеної маски:** Сформувати маску виклику, яка включає стандартні атрибути `STATX_BASIC_STATS`, час створення `STATX_BTIME` та параметри вирівнювання `STATX_DIOALIGN`.
2. **Безпечна перевірка повернутої маски:** Перевірити `stx.stx_mask` перед читанням будь-яких необов'язкових полів. Якщо файлова система не підтримує `btime` або ядро не підтримує `STATX_DIOALIGN`, утиліта повинна вивести зрозуміле повідомлення про відсутність підтримки, а не користуватися невизначеними даними з пам'яті.
3. **Двокомпонентний аналіз атрибутів:** Перевірити маску підтримуваних атрибутів `stx_attributes_mask` та зчитати прапорці з `stx_attributes` (захист від зміни `immutable`, режим дописування `append-only`, стиснення, шифрування, `fs-verity` та `DAX`).
4. **Визначення геометрії вводу/виводу:** Вивести необхідні параметри вирівнювання адреси буфера пам'яті та зміщення у файлі для прямого вводу/виводу `O_DIRECT`.
5. **Обробка зворотної сумісності:** Корректно обробити випадок відсутності системного виклику `statx` у застарілих ядрах (помилка `ENOSYS`) або його блокування секірніми фільтрами `seccomp` у контейнерах Docker/LXC.

---

## Реалізація утиліти інспектування

Нижче наведено паралельні реалізації утиліти мовами C та C++. Реалізація C++ використовує концепцію RAII, обгортку типів, безпечне представлення рядків `std::string_view`, строгу обробку помилок через `std::system_error` та форматування потоків виводу.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

/* Форматування часової позначки struct statx_timestamp */
static void print_time(const char *label, const struct statx_timestamp *ts) {
    time_t sec = (time_t)ts->tv_sec;
    struct tm tm_buf;
    char time_str[64];
    
    if (localtime_r(&sec, &tm_buf) != NULL) {
        strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", &tm_buf);
        printf("  %-16s: %s.%09u нс\n", label, time_str, ts->tv_nsec);
    } else {
        printf("  %-16s: %lld с, %u нс\n", label, (long long)ts->tv_sec, ts->tv_nsec);
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_файлу>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *path = argv[1];
    struct statx stx;
    memset(&stx, 0, sizeof(stx));

    /* Сформувати маску запиту розширених полів */
    unsigned int request_mask = STATX_BASIC_STATS | STATX_BTIME;
#ifdef STATX_DIOALIGN
    request_mask |= STATX_DIOALIGN;
#endif

    /* Викликати statx з прапорцем невимогливої синхронізації кешу */
    int res = statx(AT_FDCWD, path, AT_SYMLINK_NOFOLLOW | AT_STATX_SYNC_AS_STAT,
                    request_mask, &stx);

    if (res != 0) {
        if (errno == ENOSYS || errno == EOPNOTSUPP) {
            fprintf(stderr, "Помилка: системний виклик statx не підтримується ядром.\n");
        } else {
            perror("Помилка виконання statx");
        }
        return EXIT_FAILURE;
    }

    printf("=== Інспектування файлу: %s ===\n", path);
    printf("Розмір файлу        : %llu байтів\n", (unsigned long long)stx.stx_size);
    printf("Номер Inode         : %llu\n", (unsigned long long)stx.stx_ino);
    printf("Кількість посилань  : %u\n", stx.stx_nlink);
    printf("Права (stx_mode)    : 0%o\n", stx.stx_mode & 07777);

    /* Перевірка наявності часу створення (btime) у повернутій масці */
    printf("\n--- Часові позначки ---\n");
    if (stx.stx_mask & STATX_ATIME) print_time("Доступ (atime)", &stx.stx_atime);
    if (stx.stx_mask & STATX_MTIME) print_time("Модифікація (mtime)", &stx.stx_mtime);
    if (stx.stx_mask & STATX_CTIME) print_time("Зміна inode (ctime)", &stx.stx_ctime);

    if (stx.stx_mask & STATX_BTIME) {
        print_time("Створення (btime)", &stx.stx_btime);
    } else {
        printf("  Створення (btime): [НЕ ПІДТРИМУЄТЬСЯ ФАЙЛОВОЮ СИСТЕМОЮ]\n");
    }

    /* Перевірка прапорців атрибутів файлу */
    printf("\n--- Розширені атрибути (stx_attributes) ---\n");
    uint64_t mask_attr = stx.stx_attributes_mask;
    uint64_t val_attr = stx.stx_attributes;

    if (mask_attr & STATX_ATTR_IMMUTABLE) {
        printf("  Immutable (+i)   : %s\n", (val_attr & STATX_ATTR_IMMUTABLE) ? "ТАК" : "НІ");
    }
    if (mask_attr & STATX_ATTR_APPEND) {
        printf("  Append-only (+a) : %s\n", (val_attr & STATX_ATTR_APPEND) ? "ТАК" : "НІ");
    }
    if (mask_attr & STATX_ATTR_COMPRESSED) {
        printf("  Compressed       : %s\n", (val_attr & STATX_ATTR_COMPRESSED) ? "ТАК" : "НІ");
    }
    if (mask_attr & STATX_ATTR_ENCRYPTED) {
        printf("  Encrypted        : %s\n", (val_attr & STATX_ATTR_ENCRYPTED) ? "ТАК" : "НІ");
    }
#ifdef STATX_ATTR_VERITY
    if (mask_attr & STATX_ATTR_VERITY) {
        printf("  fs-verity        : %s\n", (val_attr & STATX_ATTR_VERITY) ? "ТАК" : "НІ");
    }
#endif
#ifdef STATX_ATTR_DAX
    if (mask_attr & STATX_ATTR_DAX) {
        printf("  DAX (Direct Acc) : %s\n", (val_attr & STATX_ATTR_DAX) ? "ТАК" : "НІ");
    }
#endif

    /* Перевірка параметрів вирівнювання O_DIRECT */
#ifdef STATX_DIOALIGN
    printf("\n--- Параметри вирівнювання O_DIRECT (STATX_DIOALIGN) ---\n");
    if (stx.stx_mask & STATX_DIOALIGN) {
        printf("  Вирівнювання бувера пам'яті : %u байтів\n", stx.stx_dio_mem_align);
        printf("  Вирівнювання зсуву у файлі  : %u байтів\n", stx.stx_dio_offset_align);
    } else {
        printf("  Вирівнювання O_DIRECT       : [НЕ ПІДТРИМУЄТЬСЯ ЯДРОМ ТА ФС]\n");
    }
#endif

    return EXIT_SUCCESS;
}
```
```cpp
#define _GNU_SOURCE
#include <iostream>
#include <string>
#include <string_view>
#include <system_error>
#include <chrono>
#include <iomanip>
#include <ctime>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

namespace fs_inspect {

/* Клас-обгортка над struct statx для ідіоматичного C++ доступу */
class StatxInfo {
public:
    static StatxInfo fetch(std::string_view path, unsigned int extra_mask = 0) {
        StatxInfo info{};
        unsigned int request_mask = STATX_BASIC_STATS | STATX_BTIME | extra_mask;
        
        int res = ::statx(AT_FDCWD, path.data(), AT_SYMLINK_NOFOLLOW | AT_STATX_SYNC_AS_STAT,
                          request_mask, &info.stx_);
        if (res != 0) {
            throw std::system_error(errno, std::generic_category(), 
                                    "Не вдалося виконати statx для: " + std::string(path));
        }
        return info;
    }

    [[nodiscard]] uint64_t size() const noexcept { return stx_.stx_size; }
    [[nodiscard]] uint64_t inode() const noexcept { return stx_.stx_ino; }
    [[nodiscard]] uint32_t nlink() const noexcept { return stx_.stx_nlink; }
    [[nodiscard]] uint16_t permissions() const noexcept { return stx_.stx_mode & 07777; }

    [[nodiscard]] bool has_field(uint32_t flag) const noexcept {
        return (stx_.stx_mask & flag) != 0;
    }

    [[nodiscard]] bool has_attribute_support(uint64_t attr_flag) const noexcept {
        return (stx_.stx_attributes_mask & attr_flag) != 0;
    }

    [[nodiscard]] bool attribute_value(uint64_t attr_flag) const noexcept {
        return (stx_.stx_attributes & attr_flag) != 0;
    }

    void print_timestamp(std::string_view label, const struct statx_timestamp& ts) const {
        std::time_t sec = static_cast<std::time_t>(ts.tv_sec);
        std::tm tm_buf{};
        if (::localtime_r(&sec, &tm_buf) != nullptr) {
            std::cout << "  " << std::left << std::setw(18) << label << ": "
                      << std::put_time(&tm_buf, "%Y-%m-%d %H:%M:%S") << "."
                      << std::setfill('0') << std::setw(9) << ts.tv_nsec << " нс\n"
                      << std::setfill(' ');
        } else {
            std::cout << "  " << label << ": " << ts.tv_sec << " с\n";
        }
    }

    void print_all() const {
        std::cout << "Розмір файлу        : " << size() << " байтів\n";
        std::cout << "Номер Inode         : " << inode() << "\n";
        std::cout << "Кількість посилань  : " << nlink() << "\n";
        std::cout << "Права доступу       : 0" << std::oct << permissions() << std::dec << "\n\n";

        std::cout << "--- Часові позначки ---\n";
        if (has_field(STATX_ATIME)) print_timestamp("Доступ (atime)", stx_.stx_atime);
        if (has_field(STATX_MTIME)) print_timestamp("Модифікація (mtime)", stx_.stx_mtime);
        if (has_field(STATX_CTIME)) print_timestamp("Зміна inode (ctime)", stx_.stx_ctime);

        if (has_field(STATX_BTIME)) {
            print_timestamp("Створення (btime)", stx_.stx_btime);
        } else {
            std::cout << "  Створення (btime): [НЕ ПІДТРИМУЄТЬСЯ ФАЙЛОВОЮ СИСТЕМОЮ]\n";
        }

        std::cout << "\n--- Розширені атрибути (stx_attributes) ---\n";
        check_and_print_attr("Immutable (+i)", STATX_ATTR_IMMUTABLE);
        check_and_print_attr("Append-only (+a)", STATX_ATTR_APPEND);
        check_and_print_attr("Compressed", STATX_ATTR_COMPRESSED);
        check_and_print_attr("Encrypted", STATX_ATTR_ENCRYPTED);
#ifdef STATX_ATTR_VERITY
        check_and_print_attr("fs-verity", STATX_ATTR_VERITY);
#endif
#ifdef STATX_ATTR_DAX
        check_and_print_attr("DAX (Direct Acc)", STATX_ATTR_DAX);
#endif

#ifdef STATX_DIOALIGN
        std::cout << "\n--- Параметри вирівнювання O_DIRECT (STATX_DIOALIGN) ---\n";
        if (has_field(STATX_DIOALIGN)) {
            std::cout << "  Вирівнювання бувера пам'яті : " << stx_.stx_dio_mem_align << " байтів\n";
            std::cout << "  Вирівнювання зсуву у файлі  : " << stx_.stx_dio_offset_align << " байтів\n";
        } else {
            std::cout << "  Вирівнювання O_DIRECT       : [НЕ ПІДТРИМУЄТЬСЯ ЯДРОМ ТА ФС]\n";
        }
#endif
    }

private:
    struct statx stx_{};

    void check_and_print_attr(std::string_view name, uint64_t flag) const {
        if (has_attribute_support(flag)) {
            std::cout << "  " << std::left << std::setw(18) << name << ": "
                      << (attribute_value(flag) ? "ТАК" : "НІ") << "\n";
        }
    }
};

} // namespace fs_inspect

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях_до_файлу>\n";
        return EXIT_FAILURE;
    }

    try {
        unsigned int extra_mask = 0;
#ifdef STATX_DIOALIGN
        extra_mask |= STATX_DIOALIGN;
#endif
        auto info = fs_inspect::StatxInfo::fetch(argv[1], extra_mask);
        std::cout << "=== Інспектування файлу (C++): " << argv[1] << " ===\n";
        info.print_all();
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

---

## Детальний розбір механізмів реалізації

### 1. Формування маски запиту та умовна компіляція

У C-реалізації запитувана маска формується як побітове «АБО» базових констант. Використання макросу директиви препроцесора `#ifdef STATX_DIOALIGN` гарантує, що програма успішно скомпілюється як у середовищах із сучасними заголовочними файлами ядра (Linux 6.1+), так і у більш старих дистрибутивах (наприклад, Ubuntu 20.04 з гладким glibc 2.31), де сталі `STATX_DIOALIGN` ще не було у системних заголовках.

Препроцесорна підготовка гарантує бінарну портабельність коду між різними релізами заголовочних файлів C-бібліотеки.

### 2. Безпека потоків при форматуванні часу

Для форматування 64-бітної часової позначки `struct statx_timestamp` використовується потокобезпечна функція `localtime_r()`. Вона приймає вказівник на локальну змінну буфера `struct tm`, що виключає стан гонитви (race condition) при одночасному виклику форматування часу з декількох потоків виконання (на відміну от старого `localtime()`, який повертає вказівник на спільну статичну пам'ять).

Додатково виконується нульове заповнення наносекунд через специфікатор `%09u`, що дозволяє коректно відображати значення часових позначок у високоточному форматі ISO-8601 (наприклад, `2026-08-12 17:00:00.005000000 нс`).

### 3. C++ RAII та менеджмент помилок через std::system_error

У реалізації мовою C++ уся робота зі структурою `statx` замотана у клас `fs_inspect::StatxInfo`. Статичний фабричний метод `fetch()` повертає готовий екземпляр класу або генерує стандартний виняток `std::system_error`, збагачений кодом системної помилки `errno` та контекстом файлу. Це дозволяє прикладному коду не перевіряти статус виконання після кожного виклику вручну, довіряючи стандартному механізму обробки винятків C++.

Використання `std::string_view` для передачі шляху уникає зайвого виділення пам'яті у купі (heap allocation) при передачі рядкових літералів або аргументів `argv`.

---

## Простеження виконання виклику у внутрішніх структурах ядра

Коли утиліта викликає функцію `statx()`, виконання передається у ядро Linux через обгортку системних викликів. Загальна послідовність проходження запиту виглядає наступним чином:

1. **Точка входу `sys_statx`:** Ядро отримує параметри `dirfd`, `path`, `flags`, `mask` та виділяє внутрішню структуру `struct filename` для розпізнавання шляху.
2. **Перевірка прапорців `AT_STATX_*_SYNC`:** Модуль VFS аналізує передані прапорці кешування. Якщо передано `AT_STATX_FORCE_SYNC`, ядро викликає інвалідацію кешу inode для відповідного з'єднання.
3. **Виклик `vfs_statx()`:** Ядро розпізнає шлях через VFS namei та викликає функцію `vfs_getattr()`.
4. **Звернення до файлової системи `ops->getattr()`:** VFS звертається до методу `getattr` конкретного драйвера (наприклад, `ext4_getattr` або `nfs_getattr`). Драйвер зчитує inode з диска або з кешу та заповнює поля `struct statx`, встановлюючи маску `stx_mask` для тих полів, які він зміг заповнити.
5. **Копіювання у простір користувача `copy_to_user()`:** Ядро копіює 256-байтну структуру `struct statx` у пам'ять процесу користувача та повертає статус `0`.

Утиліти трасування системних викликів `strace` виводять запит і результат `statx` у зрозумілому розгортці полів:

```bash
# Трасування системного виклику statx через strace
strace -e statx ./statx_inspect_c /etc/passwd

# Типовий вивід strace:
# statx(AT_FDCWD, "/etc/passwd", AT_SYMLINK_NOFOLLOW|AT_STATX_SYNC_AS_STAT, STATX_BASIC_STATS|STATX_BTIME, {stx_mask=STATX_BASIC_STATS|STATX_BTIME, stx_blksize=4096, stx_attributes=0, stx_nlink=1, stx_mode=S_IFREG|0644, stx_size=2840, ...}) = 0
```

---

## Використання даних O_DIRECT для виділення вирівняної пам'яті

Отримані значення `stx_dio_mem_align` та `stx_dio_offset_align` дозволяють високопродуктивним програмам правильно налаштувати вирівнювання пам'яті:

:::tabs
```c
void *buffer = NULL;
size_t mem_align = stx.stx_dio_mem_align;
size_t buffer_bytes = 65536; /* 64 КБ */

/* Якщо ядро не надали вирівнювання, беремо стандарний розмір сторінки */
if ((stx.stx_mask & STATX_DIOALIGN) == 0 || mem_align == 0) {
    mem_align = sysconf(_SC_PAGESIZE);
}

/* Виділення пам'яті з точним вирівнюванням під апаратний сектор диска */
if (posix_memalign(&buffer, mem_align, buffer_bytes) != 0) {
    perror("Помилка виділення вирівняної пам'яті через posix_memalign");
    return;
}

/* Пряме читання з файлу з гарантією відсутності помилки EINVAL */
ssize_t bytes_read = pread(fd, buffer, buffer_bytes, aligned_offset);
```
```cpp
size_t mem_align = stx.stx_dio_mem_align;
const size_t buffer_bytes = 65536; // 64 КБ

if ((stx.stx_mask & STATX_DIOALIGN) == 0 || mem_align == 0) {
    mem_align = static_cast<size_t>(::sysconf(_SC_PAGESIZE));
}

// У C++17/C++20 використовується std::aligned_alloc або posix_memalign
void* raw_ptr = nullptr;
if (::posix_memalign(&raw_ptr, mem_align, buffer_bytes) != 0) {
    throw std::bad_alloc();
}
std::unique_ptr<char, decltype(&::free)> buffer(static_cast<char*>(raw_ptr), &::free);

ssize_t bytes_read = ::pread(fd, buffer.get(), buffer_bytes, aligned_offset);
```
:::

Якщо програма виділить буфер через звичайний `malloc()`, адреса буфера може не відповідати вимозі `stx_dio_mem_align`, що при виконанні прямого запису через `write(fd, buffer, bytes)` поверне мовчазну помилку `EINVAL`. Опитування `statx` робить виділення пам'яті повністю адаптивним під будь-який дисковий носій.

На носіях NVMe виділення пам'яті з вирівнюванням `stx_dio_mem_align` дозволяє безпосередньо передавати фізичні адреси сторінок пам'яті контролеру через PRPs (Physical Region Page) або SGLs (Scatter Gather Lists), виключаючи проміжні копіювання даних в ядрі.

---

## Багатопотокове інспектування файлових дерев (Thread Pool Crawler)

При створенні системних індексаторів файлів виклики `statx` об'єднують у багатопотоковий пул робітників (Thread Pool):

1. **Мінімізація маски запиту:** Кожен робітник передає маску `STATX_TYPE | STATX_MODE | STATX_SIZE`, уникаючи обчислень важких часових позначок та блоків.
2. **Прапорець `AT_STATX_DONT_SYNC`:** Для мережевих точок монтування передається `AT_STATX_DONT_SYNC`, що повністю виключає мережеві блокування робітників.
3. **Пакетна обробка:** Дескриптори каталогів `dirfd` відкриваються з прапорцем `O_PATH`, що дозволяє виконувати `statx(dirfd, filename, ...)` без створення повних файлових дескрипторів файлу.

---

## Продуктивне порівняння: statx проти stat та io_uring

При порівняльному аналізі продуктивності опитування великих дерев метаданих системний виклик `statx` демонструє суттєву перевагу перед класичним `stat`:

1. **Сканування локальної ext4 / Btrfs:** При запиті лише `STATX_TYPE` сканування каталогів викликом `statx` випереджає `stat()` на 15–25% за рахунок виключення зчитування важких полів inode у структурі ядра.
2. **Мережеві ФС (NFSv4 / CephFS):** Застосування `statx` з прапорцем `AT_STATX_DONT_SYNC` прискорює сканування метаданих у 10–50 разів на розпилених мережевих сховищах, оскільки сканування не генерує синхронних RPC-запитів до сервера.
3. **Асинхронне виконання в io_uring:** Використання `IORING_OP_STATX` дозволяє відправляти пачки по 64-256 викликів `statx` за один виклик `io_uring_enter()`, що утилізує багатопотокову обробку VFS у ядрі без накладних витрат на регулярні перемикання контексту процесів (context switches).

---

## Простеження траси через bpftrace

Для моніторингу затримок `statx` у продакшн-середовищі використовується скрипт на eBPF (`bpftrace`):

```bash
# Моніторинг системних викликів statx та затримок VFS у мікросекундах
bpftrace -e 'tracepoint:syscalls:sys_enter_statx { @start[tid] = nsecs; } 
             tracepoint:syscalls:sys_exit_statx /@start[tid]/ { 
                 @us = hist((nsecs - @start[tid]) / 1000); 
                 delete(@start[tid]); 
             }'
```

Цей BPF-інструмент створює гістограму затримок виклику `statx`, дозволяючи виявити "повислі" мережеві виклики на NFS-моунтах без модифікації вихідного коду програм.

---

## Застосування statx у контейнерах та віртуалізованих середовищах

При виконанні у контейнерах Docker або підсистемах віртуалізації (virtio-fs, 9p, KVM) використання `statx` дозволяє оптимізувати обмін метаданими між гостьовою системою та хостом:

- **Virtio-fs (QEMU/KVM):** Драйвер `virtio-fs` в ядрі Linux транслює виклик `statx` безпосередньо у протокол FUSE `STATX` (код операції 52), що дозволяє демону `virtiofsd` на хості звертатися лише до кешованих атрибутів викликом `statx(AT_STATX_DONT_SYNC)`.
- **Контейнери LXC/Docker:** Використання `statx` у середовищі контейнера виключає зайві перевірки прав доступу на рівнях неймспейсів користувачів (user namespaces), оскільки `stx_uid` та `stx_gid` конвертуються ядром за один прохід через мапування `uids`/`gids` у `/proc/self/uid_map`.

---

## Автоматизоване тестування та перевірка вирівнювання у CI/CD

У системах автоматизованого тестування (CI/CD) утиліти перевірки вирівнювання дискового вводу/виводу будуються як тести GTest/Catch2:

```cpp
#include <gtest/gtest.h>

TEST(StatxTest, DirectIOAlignmentCheck) {
    auto info = fs_inspect::StatxInfo::fetch("/tmp/test_file.bin", STATX_DIOALIGN);
    if (info.has_field(STATX_DIOALIGN)) {
        EXPECT_GT(info.size(), 0);
        // Перевірка, що вирівнювання є ступенем двійки
        uint32_t align = info.permissions();
        EXPECT_TRUE((align & (align - 1)) == 0);
    }
}
```

Такий модуль тестування гарантує, що розробники не припустяться помилок вирівнювання буферів пам'яті при портуванні системного ПЗ на нові апаратні носії NVMe або обчислювальні вузли у хмарних середовищах AWS/GCP.

---

## Обробка крайніх випадків та специфічних помилок errno

При роботі у складних розподілених середовищах системний виклик `statx` може повертати специфічні коди помилок `errno`, які потребують адаптивного опрацювання:

1. **`ESTALE` (Stale file handle):** Трапляється на мережевих файлових системах NFS/CephFS, коли файл був вилучений на сервері іншим вузлом, але клієнтський VFS кеш зберігає застаріле жорстке посилання inode. При отриманні `ESTALE` програма повинна очистити свій внутрішній кеш шляхів і повторити відкриття файлу від кореневого каталогу.
2. **`ELOOP` (Too many levels of symbolic links):** Повертається при наявності циклічних символьних посилань у шляху. Використання прапорця `AT_SYMLINK_NOFOLLOW` дає змогу зчитати атрибути самого зацикленого посилання без занурення у нескінченний рекурсивний обхід.
3. **`ENAMETOOLONG`:** Вказує, що довжина компонента шляху перевищує `NAME_MAX` (зазвичай 255 байтів) або загальна довжина шляху перевищує `PATH_MAX` (4096 байтів). У цьому разі слід розбити шлях на каталог та файл і використовувати `statx(dirfd, filename, ...)` через файловий дескриптор каталогу.

---

## Архітектура розширення C++20 з використанням Concepts та std::expected

Сучасний C++20/C++23 дозволяє проєктувати типубезпечні інтерфейси для `statx` з компіляційною перевіркою масок та відсутністю винятків (exception-free error handling):

```cpp
#include <concepts>
#include <system_error>

template <typename T>
concept StatxFieldFetcher = requires(T a, std::string_view path) {
    { a.fetch_field(path) } -> std::same_as<void>;
};

// Приклад типубезпечного обгортання маскового запиту
enum class StatxMaskBit : uint32_t {
    Basic = STATX_BASIC_STATS,
    BirthTime = STATX_BTIME,
#ifdef STATX_DIOALIGN
    DirectIO = STATX_DIOALIGN,
#endif
};

constexpr inline StatxMaskBit operator|(StatxMaskBit a, StatxMaskBit b) noexcept {
    return static_cast<StatxMaskBit>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}
```

Застосування строгих типізованих перелічувальних типів (`enum class`) та концептів C++20 виключає випадкову передачу некоректних цілочисельних прапорців у маску системного виклику `statx` на етапі компіляції.

---

## Порівняльна аналітика та підсумкові рекомендації

При розробці нових системних продуктів для сучасного ядра Linux системний виклик `statx` є стандартом де-факто для зчитування метаданих файлів:

1. **Рекомендація 1:** Використовуйте `statx` замість `stat`/`fstatat` у всіх нових проєктах. Це забезпечує повну сумісність із Y2038, підтримку 64-бітних ідентифікаторів `inode`, дату створення `btime` та розширені прапорці inode.
2. **Рекомендація 2:** Завжди перевіряйте повернуту бітову маску `stx_mask` перед читанням необов'язкових атрибутів. Жоден з необов'язкових атрибутів не повинен зчитуватися без попереднього аналізу маски ядра.
3. **Рекомендація 3:** При використанні прямого вводу/виводу `O_DIRECT` запитуйте біт `STATX_DIOALIGN` і виділяйте пам'ять через `posix_memalign()` з вирівнюванням на значення `stx_dio_mem_align`.
4. **Рекомендація 4:** Для прискорення обходу великих мережевих точок монтування передавайте `AT_STATX_DONT_SYNC`, мінімізуючи накладні витрати на мережеві RPC-запити.

Завдяки реалізованому масковому контракту, утиліта стає повністю адаптивною до будь-якої конфігурації ядра Linux та типу підкладкової файлової системи.

---

## Шаблонні патерни C++ для безпечної обробки розширених атрибутів

У сучасних C++20 проєктах розширені атрибути файлу зручно огортати у `std::optional` або тип `std::expected` (C++23) для запобігання помилкам доступу до непідтримуваних полів:

```cpp
#include <optional>

template <typename T>
class CheckedField {
public:
    CheckedField(bool valid, T value) : valid_(valid), value_(value) {}

    [[nodiscard]] bool is_valid() const noexcept { return valid_; }
    [[nodiscard]] T value_or(T fallback) const noexcept {
        return valid_ ? value_ : fallback;
    }
    [[nodiscard]] std::optional<T> to_optional() const noexcept {
        if (valid_) return value_;
        return std::nullopt;
    }

private:
    bool valid_;
    T value_;
};
```

Такий патерн дозволяє проектувати інтерфейси бібліотек системного програмування, де відсутність підтримки поля файловою системою виражається типом `std::nullopt`, підштовхуючи розробника до обробки альтернативного сценарію.

---

## Фолбек на старих ядрах та сумісність із Docker/seccomp

При розробці крос-платформних системних інструментів необхідно передбачити випадок, коли системний виклик `statx` повертає помилку `ENOSYS` або `EPERM`. Це трапляється в двох основних сценаріях:
1. Запуск програми у застарілих дистрибутивах з ядрами Linux старих версій (до 4.11).
2. Запуск програми у контейнерах Docker або Kubernetes із застарілими профілями безпеки `seccomp`, де виклик `statx` не внесений до білого списку дозволених системних викликів.

Приклад ідіоматичного фолбеку з падінням до `fstatat()`:

:::tabs
```c
static int safe_statx_with_fallback(int dirfd, const char *path, int flags,
                                    unsigned int mask, struct statx *stx) {
    int res = statx(dirfd, path, flags, mask, stx);
    if (res == 0) {
        return 0; /* Виклик statx успішно виконано */
    }

    /* Якщо ядро або seccomp блокують statx, робимо фолбек на fstatat */
    if (errno == ENOSYS || errno == EPERM || errno == EACCES) {
        struct stat st;
        int stat_flags = 0;
        if (flags & AT_SYMLINK_NOFOLLOW) stat_flags |= AT_SYMLINK_NOFOLLOW;
        if (flags & AT_EMPTY_PATH) stat_flags |= AT_EMPTY_PATH;

        if (fstatat(dirfd, path, &st, stat_flags) == 0) {
            memset(stx, 0, sizeof(*stx));
            stx->stx_mask = STATX_BASIC_STATS;
            stx->stx_size = st.st_size;
            stx->stx_mode = st.st_mode;
            stx->stx_ino = st.st_ino;
            stx->stx_nlink = st.st_nlink;
            stx->stx_uid = st.st_uid;
            stx->stx_gid = st.st_gid;
            stx->stx_blocks = st.st_blocks;
            stx->stx_blksize = st.st_blksize;
            stx->stx_atime.tv_sec = st.st_atime;
            stx->stx_mtime.tv_sec = st.st_mtime;
            stx->stx_ctime.tv_sec = st.st_ctime;
            return 0;
        }
    }
    return -1;
}
```
```cpp
inline std::expected<struct statx, std::error_code> 
safe_statx_with_fallback(int dirfd, std::string_view path, int flags, unsigned int mask) {
    struct statx stx{};
    int res = ::statx(dirfd, path.data(), flags, mask, &stx);
    if (res == 0) {
        return stx;
    }

    if (errno == ENOSYS || errno == EPERM || errno == EACCES) {
        struct stat st{};
        int stat_flags = 0;
        if (flags & AT_SYMLINK_NOFOLLOW) stat_flags |= AT_SYMLINK_NOFOLLOW;
        if (flags & AT_EMPTY_PATH) stat_flags |= AT_EMPTY_PATH;

        if (::fstatat(dirfd, path.data(), &st, stat_flags) == 0) {
            stx.stx_mask = STATX_BASIC_STATS;
            stx.stx_size = static_cast<uint64_t>(st.st_size);
            stx.stx_mode = static_cast<uint16_t>(st.st_mode);
            stx.stx_ino = static_cast<uint64_t>(st.st_ino);
            stx.stx_nlink = static_cast<uint32_t>(st.st_nlink);
            stx.stx_uid = static_cast<uint32_t>(st.st_uid);
            stx.stx_gid = static_cast<uint32_t>(st.st_gid);
            stx.stx_blocks = static_cast<uint64_t>(st.st_blocks);
            stx.stx_blksize = static_cast<uint32_t>(st.st_blksize);
            stx.stx_atime.tv_sec = st.st_atime;
            stx.stx_mtime.tv_sec = st.st_mtime;
            stx.stx_ctime.tv_sec = st.st_ctime;
            return stx;
        }
    }
    return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
}
```
:::

---

## Підводні камені та практичні пастки

1. **Макрос `_GNU_SOURCE` обов'язковий:** Заголовок `<sys/stat.h>` визначає `struct statx` та сталі `STATX_*` лише тоді, коли увімкнено розширення GNU. Без цього компілятор видасть помилку невідомого типу або відсутності символу `statx`.
2. **Перевірка повернення `errno == ENOSYS`:** У контейнеризованих середовищах (Docker/LXC) зі застарілими профілями `seccomp` системний виклик `statx` може бути заблокований ядерним фільтром або повернути `ENOSYS`. Надійні програми мають будувати фолбек-ланцюжок із використанням `fstatat` при неможливості виклику `statx`.
3. **Різниця між `0` у масці та `0` у значенні:** Якщо `stx_dio_mem_align` дорівнює `0` при відсутності прапорця `STATX_DIOALIGN` у `stx_mask`, це **не означає**, що вирівнювання не вимагається. Це означає лише те, що ядро не надало цих даних. Справжня відсутність вимог вирівнювання повертає `stx_dio_mem_align = 1` при встановленому прапорці `STATX_DIOALIGN`.
4. **Маска символьних посилань `AT_SYMLINK_NOFOLLOW`:** Передача прапорця `AT_SYMLINK_NOFOLLOW` є обов'язковою, якщо утиліта інспектує саме посилання. Без цього прапорця ядро пройде по ланцюжку посилань до кінцевого цільового файлу і поверне його атрибути.

---

## Інструкція з компіляції та запуску

Для компіляції прикладів у дистрибутивах Linux з актуальним інструментарієм GCC або Clang виконайте наступні команди:

```bash
# Компіляція прикладу на C (стандарт C11)
gcc -std=c11 -O2 -Wall -Wextra proj-statx-inspect.c -o statx_inspect_c

# Компіляція прикладу на C++ (стандарт C++20)
g++ -std=c++20 -O2 -Wall -Wextra proj-statx-inspect.cpp -o statx_inspect_cpp

# Запуск інспектування файлу
./statx_inspect_c /etc/passwd
./statx_inspect_cpp /etc/passwd
```
