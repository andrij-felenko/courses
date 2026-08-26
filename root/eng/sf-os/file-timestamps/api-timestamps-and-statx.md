# 📋 Інтерфейс системних викликів statx, utimensat та часових структур

Системні виклики `statx()` та `utimensat()` складають сучасний стандартизований контракт ядра Linux для читання та модифікації наносекундних часових позначок файлових об'єктів. Цей довідник містить точні сигнатури функцій, бітові маски, внутрішню будову структур даних ядра, порівняння з застарілими інтерфейсами POSIX та правила обробки крайових випадків у просторі користувача.

---

### 1. Системний виклик statx() та еволюція інтерфейсів зчитування

Історично операційні системи сімейства Unix використовували системний виклик `stat()`, який повертав фіксовану структуру `struct stat`. Зі збільшенням розрядності процесорів та появою нових функцій у сучасних файлових системах (таких як час народження файлу `btime` або специфічні прапорці монтування) класичний виклик вичерпав можливості розширення без порушення двійкової сумісності (ABI). 

Виклик `statx()` (впроваджений у ядрі Linux 4.11 та підтримуваний бібліотекою glibc, починаючи з версії 2.28) вирішує цю проблему за допомогою гнучкого механізму масок запиту: клієнтський процес явно вказує ядру, які саме поля метаданих йому необхідні. Якщо запитуються лише часові позначки, ядра мережевих або розподілених файлових систем можуть пропустити важкі дискові чи мережеві операції опитування розміру або списків контролю доступу (ACL).

#### Сигнатура та заголовочні файли

```c
#define _GNU_SOURCE
#include <fcntl.h>           /* Константи AT_* */
#include <sys/stat.h>        /* Структура struct statx та константи STATX_* */
#include <unistd.h>

int statx(int dirfd, const char *pathname, int flags,
          unsigned int mask, struct statx *statxbuf);
```

#### Параметри виклику

- `dirfd`: файловий дескриптор каталогу, відносно якого обчислюється відносний шлях у `pathname`. Якщо шлях є абсолютним, цей параметр ігнорується. Передача спеціальної константи `AT_FDCWD` вказує ядру використовувати поточний робочий каталог процесу.
- `pathname`: вказівник на рядок із шляхом до файлу. Якщо застосунок передає порожній рядок `""` і встановлює прапорець `AT_EMPTY_PATH` у параметрі `flags`, операція виконується безпосередньо над дескриптором `dirfd` (аналог `fstat`).
- `flags`: комбінація бітових прапорців, що контролюють процес обходу шляху та взаємодію з мережевими кешами.
- `mask`: бітова маска, за допомогою якої застосунок інформує ядро про необхідні поля. Ядро заповнює лише підтримувані ним поля та повертає результуючу маску в `statxbuf->stx_mask`.
- `statxbuf`: вказівник на структуру у просторі пам'яті користувача, куди ядро записує результат виклику.

#### Прапорці поведінки обходу та синхронізації (flags)

- `AT_SYMLINK_NOFOLLOW`: якщо кінцевий компонент шляху є символічним посиланням, виклик повертає метадані самого посилання, а не об'єкта, на який воно вказує (аналог застарілого `lstat`).
- `AT_EMPTY_PATH`: дозволяє передавати порожній рядок у `pathname`, що дає змогу опитати статус відкритого файлового дескриптора `dirfd`. Вимагає наявності прав доступу або прапорця `O_PATH` під час відкриття дескриптора.
- `AT_NO_AUTOMOUNT`: забороняє автоматичне монтування каталогів точок монтування на вимогу (autofs) під час резолюції шляху.
- `AT_STATX_SYNC_AS_STAT`: типовий режим узгодження метаданих. Для локальних файлових систем не створює накладних витрат; для мережевих файлових систем (NFS, CephFS, SMB) використовує стандартні інтервали валідації кешу атрибутів.
- `AT_STATX_FORCE_SYNC`: змушує драйвер мережевої файлової системи ігнорувати локальний кеш атрибутів та виконати синхронний RPC-запит до віддаленого сервера для отримання найсвіжіших позначок часу.
- `AT_STATX_DONT_SYNC`: вимагає від ядра повернути виключно локально кешовані атрибути без виконання будь-яких мережевих операцій, навіть якщо термін придатності кешу минув. Якщо атрибути відсутні в кеші, повертаються наявні значення або помилка.

#### Бітові маски запиту атрибутів (mask)

| Константа маски | Числове значення | Призначення поля |
|---|---|---|
| `STATX_TYPE` | `0x00000001U` | Тип файлу (доступний через `stx_mode & S_IFMT`) |
| `STATX_MODE` | `0x00000002U` | Права доступу файлу (`stx_mode & ~S_IFMT`) |
| `STATX_NLINK` | `0x00000004U` | Кількість жорстких посилань (`stx_nlink`) |
| `STATX_UID` | `0x00000008U` | Числовий UID користувача-власника (`stx_uid`) |
| `STATX_GID` | `0x00000010U` | Числовий GID групи-власника (`stx_gid`) |
| `STATX_ATIME` | `0x00000020U` | Час останнього доступу (`stx_atime`) |
| `STATX_MTIME` | `0x00000040U` | Час останньої модифікації вмісту (`stx_mtime`) |
| `STATX_CTIME` | `0x00000080U` | Час останньої зміни метаданих інода (`stx_ctime`) |
| `STATX_INO` | `0x00000100U` | Номер інода файлової системи (`stx_ino`) |
| `STATX_SIZE` | `0x00000200U` | Загальний розмір файлу в байтах (`stx_size`) |
| `STATX_BLOCKS` | `0x00000400U` | Кількість виділених 512-байтних блоків (`stx_blocks`) |
| `STATX_BASIC_STATS` | `0x000007ffU` | Комбінація всіх стандартних полів класичного `stat` |
| `STATX_BTIME` | `0x00000800U` | Час створення або народження файлу (`stx_btime`) |
| `STATX_MNT_ID` | `0x00001000U` | Числовий унікальний ідентифікатор точки монтування |
| `STATX_ALL` | `0x00000fffU` | Запит усіх підтримуваних ядром полів метаданих |

---

### 2. Структура struct statx та struct statx_timestamp

Структура `struct statx` розроблена з урахуванням суворого вирівнювання полів по 64-бітній межі та фіксованого загального розміру 256 байтів. Це гарантує стабільність бінарного інтерфейсу (ABI) між 32-бітними та 64-бітними архітектурами і залишає вільні байти для розширення ядра в майбутньому.

Кожна часова позначка всередині `struct statx` представлена окремою підструктурою `struct statx_timestamp`:

```c
struct statx_timestamp {
    __s64 tv_sec;        /* Кількість секунд від 1 січня 1970 00:00:00 UTC */
    __u32 tv_nsec;       /* Кількість наносекунд (діапазон 0 .. 999 999 999) */
    __s32 __reserved;    /* Резервне поле для вирівнювання пам'яті (завжди 0) */
};
```

Повне визначення структури `struct statx` містить такі групи полів:

```c
struct statx {
    __u32 stx_mask;             /* Маска реально заповнених ядром полів */
    __u32 stx_blksize;          /* Оптимальний розмір блоку вводу-виводу */
    __u64 stx_attributes;       /* Спеціальні атрибути файлу (chattr) */
    __u32 stx_nlink;            /* Кількість жорстких посилань на інод */
    __u32 stx_uid;              /* Числовий UID власника */
    __u32 stx_gid;              /* Числовий GID групи */
    __u16 stx_mode;             /* Тип файлу та маска прав доступу */
    __u16 __spare0[1];          /* Резерв вирівнювання */
    __u64 stx_ino;              /* Номер інода */
    __u64 stx_size;             /* Фізичний розмір даних у байтах */
    __u64 stx_blocks;           /* Кількість виділених 512-байтних блоків */
    __u64 stx_attributes_mask;  /* Маска підтримуваних атрибутів файлу */
    
    struct statx_timestamp stx_atime;  /* Час останнього доступу */
    struct statx_timestamp stx_btime;  /* Час створення (birth time) */
    struct statx_timestamp stx_ctime;  /* Час зміни статусу інода */
    struct statx_timestamp stx_mtime;  /* Час модифікації вмісту */

    __u32 stx_rdev_major;       /* Старший номер пристрою (для спецфайлів) */
    __u32 stx_rdev_minor;       /* Молодший номер пристрою */
    __u32 stx_dev_major;        /* Старший номер пристрою файлової системи */
    __u32 stx_dev_minor;        /* Молодший номер пристрою файлової системи */
    __u64 stx_mnt_id;           /* Унікальний ID точки монтування */
    __u64 __spare2[13];         /* Резерв для майбутніх полів ядра */
};
```

Поле `stx_attributes` надає прямий доступ до прапорців файлової системи без необхідності викликати `ioctl(FS_IOC_GETFLAGS)`:
- `STATX_ATTR_COMPRESSED`: файл стиснуто засобами файлової системи (Btrfs, ZFS, F2FS);
- `STATX_ATTR_IMMUTABLE`: файл захищено від будь-яких змін (еквівалент `chattr +i`);
- `STATX_ATTR_APPEND`: дозволено лише дописування в кінець файлу (`chattr +a`);
- `STATX_ATTR_NODUMP`: файл виключено з резервного копіювання утилітою dump (`chattr +d`);
- `STATX_ATTR_ENCRYPTED`: вміст інода зашифровано на рівні файлової системи (fscrypt).

---

### 3. Системний виклик utimensat() та встановлення наносекундного часу

Для явного оновлення часових позначок застосовується системний виклик `utimensat()` або його варіант для відкритого файлового дескриптора `futimens()`. Вони повністю замінили застарілі виклики `utime()` (секундна точність) та `utimes()` (мікросекундна точність).

#### Сигнатури функцій

```c
#include <fcntl.h>
#include <sys/stat.h>

int utimensat(int dirfd, const char *pathname,
              const struct timespec times[2], int flags);

int futimens(int fd, const struct timespec times[2]);
```

#### Семантика масиву times та спеціальні значення

Параметр `times` приймає масив із двох структур `struct timespec`:
1. `times[0]` визначає новий час доступу `atime`;
2. `times[1]` визначає новий час модифікації `mtime`.

Поле наносекунд `tv_nsec` може містити не лише точне числове значення від `0` до `999 999 999`, але й спеціальні сигнальні константи:
- `UTIME_NOW` (значення `((1L << 30) - 1L)`): вказує ядру встановити поточний системний час з максимальною доступною наносекундною точністю. Поле `tv_sec` при цьому повністю ігнорується.
- `UTIME_OMIT` (значення `((1L << 30) - 2L)`): вказує ядру залишити відповідну часову позначку без будь-яких змін. Поле `tv_sec` ігнорується.

Якщо замість вказівника на масив передано `NULL`, ядро розглядає це як запит на оновлення обох позначок (`atime` та `mtime`) у поточний системний час (повний еквівалент передачі `UTIME_NOW` для обох елементів).

#### Права доступу та модель безпеки ядра

Ядро Linux застосовує диференційовану модель перевірки прав для операцій зміни часових позначок:

1. **Встановлення поточного часу (`UTIME_NOW` або `times == NULL`):** Процес повинен мати право запису у файл (`write permission`), або його ефективний UID повинен збігатися з UID власника файлу, або процес повинен володіти системною спроможністю `CAP_FOWNER`.
2. **Встановлення довільного часу (явні значення `tv_sec` та `tv_nsec`):** Процес **обов'язково** повинен бути власником файлу (UID процесу дорівнює UID файлу) або володіти спроможністю `CAP_FOWNER`. Наявності звичайних прав на запис недостатньо. Це запобігає фальсифікації часових позначок сторонніми користувачами, які мають доступ на запис.

Важлива архітектурна особливість: користувацький процес не може безпосередньо встановити значення `ctime`. Будь-який успішний виклик `utimensat()`, який змінює `atime` або `mtime`, автоматично оновлює поле `ctime` на поточний системний час ядра, фіксуючи факт модифікації метаданих.

---

### 4. Діагностика помилок та типові коди повернення (errno)

У разі невдалого виконання виклики повертають значення `-1` та встановлюють глобальну змінну `errno`:

| Код помилки | Числове значення | Причина виникнення |
|---|---|---|
| `EACCES` | 13 | Заборонено пошук в одному з каталогів шляху, або здійснено спробу встановити час у `UTIME_NOW` без прав на запис у файл. |
| `EBADF` | 9 | Дескриптор `dirfd` або `fd` не є валідним відкритим файловим дескриптором. |
| `EFAULT` | 14 | Вказівник `pathname`, `times` або `statxbuf` посилається на недійсну адресу пам'яті процесу. |
| `EINVAL` | 22 | Передано невідомі прапорці у `flags`, або значення `tv_nsec` не входить у діапазон `0..999999999` і не дорівнює `UTIME_NOW` чи `UTIME_OMIT`. |
| `ENOENT` | 2 | Файл за вказаним шляхом не існує, або передано порожній рядок шляху без прапорця `AT_EMPTY_PATH`. |
| `ENOTDIR` | 20 | Компонент префікса шляху не є каталогом, або передано відносний шлях, але `dirfd` вказує на звичайний файл. |
| `EPERM` | 1 | Спроба встановити довільні числові позначки часу процесом, який не є власником файлу і не має привілею `CAP_FOWNER`. |
| `EROFS` | 30 | Файлова система змонтована в режимі лише для читання (Read-Only), модифікація метаданих заблокована на рівні VFS. |

---

### 5. Практичні зразки коду на C та C++

Наведені приклади демонструють повний цикл роботи: безпечне опитування наносекундних позначок через `statx()` з перевіркою маски підтримки `btime`, а також точкову модифікацію часу `mtime` зі збереженням незмінності `atime` через `utimensat()`.

:::tabs
```c
/* timestamp_api_demo.c — Робота з statx та utimensat на мові C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <time.h>
#include <errno.h>

int print_file_timestamps(const char *filepath) {
    struct statx stx;
    memset(&stx, 0, sizeof(stx));

    /* Запитуємо всі доступні метадані без автоматичного монтування */
    if (statx(AT_FDCWD, filepath, AT_SYMLINK_NOFOLLOW | AT_NO_AUTOMOUNT,
              STATX_BASIC_STATS | STATX_BTIME, &stx) != 0) {
        fprintf(stderr, "Помилка statx для %s: %s\n", filepath, strerror(errno));
        return -1;
    }

    printf("Звіт часових позначок для файлу: %s\n", filepath);
    printf("  atime (доступ):     %lld.%09u с\n",
           (long long)stx.stx_atime.tv_sec, stx.stx_atime.tv_nsec);
    printf("  mtime (вміст):      %lld.%09u с\n",
           (long long)stx.stx_mtime.tv_sec, stx.stx_mtime.tv_nsec);
    printf("  ctime (метадані):   %lld.%09u с\n",
           (long long)stx.stx_ctime.tv_sec, stx.stx_ctime.tv_nsec);

    if (stx.stx_mask & STATX_BTIME) {
        printf("  btime (створення):  %lld.%09u с [підтримується ФС]\n",
               (long long)stx.stx_btime.tv_sec, stx.stx_btime.tv_nsec);
    } else {
        printf("  btime (створення):  [не підтримується драйвером ФС]\n");
    }

    return 0;
}

int touch_modification_only(const char *filepath) {
    struct timespec ts[2];

    /* times[0] = atime: не чіпати */
    ts[0].tv_sec = 0;
    ts[0].tv_nsec = UTIME_OMIT;

    /* times[1] = mtime: встановити точний поточний системний час */
    ts[1].tv_sec = 0;
    ts[1].tv_nsec = UTIME_NOW;

    if (utimensat(AT_FDCWD, filepath, ts, 0) != 0) {
        fprintf(stderr, "Помилка utimensat для %s: %s\n", filepath, strerror(errno));
        return -1;
    }

    printf("Позначку mtime для %s успішно оновлено (atime не змінювався).\n", filepath);
    return 0;
}
```
```cpp
// timestamp_api_demo.cpp — Ідіоматична реалізація на C++20
#include <iostream>
#include <string_view>
#include <system_error>
#include <chrono>
#include <optional>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

class TimestampManager {
public:
    struct FileTimes {
        std::chrono::system_clock::time_point access;
        std::chrono::system_clock::time_point modification;
        std::chrono::system_clock::time_point status_change;
        std::optional<std::chrono::system_clock::time_point> creation;
    };

    [[nodiscard]] static std::error_code get_timestamps(std::string_view path,
                                                        FileTimes& out_times) noexcept {
        struct statx stx{};
        const int res = statx(AT_FDCWD, path.data(),
                              AT_SYMLINK_NOFOLLOW | AT_NO_AUTOMOUNT,
                              STATX_BASIC_STATS | STATX_BTIME, &stx);
        if (res != 0) {
            return std::error_code(errno, std::generic_category());
        }

        out_times.access = convert_statx_ts(stx.stx_atime);
        out_times.modification = convert_statx_ts(stx.stx_mtime);
        out_times.status_change = convert_statx_ts(stx.stx_ctime);

        if (stx.stx_mask & STATX_BTIME) {
            out_times.creation = convert_statx_ts(stx.stx_btime);
        } else {
            out_times.creation = std::nullopt;
        }

        return {};
    }

    [[nodiscard]] static std::error_code update_mtime_now(std::string_view path) noexcept {
        struct timespec ts[2];
        ts[0].tv_sec = 0;
        ts[0].tv_nsec = UTIME_OMIT; // atime без змін
        ts[1].tv_sec = 0;
        ts[1].tv_nsec = UTIME_NOW;  // mtime оновлюється ядром

        if (utimensat(AT_FDCWD, path.data(), ts, 0) != 0) {
            return std::error_code(errno, std::generic_category());
        }
        return {};
    }

private:
    [[nodiscard]] static std::chrono::system_clock::time_point
    convert_statx_ts(const struct statx_timestamp& ts) noexcept {
        using namespace std::chrono;
        const auto total_ns = seconds(ts.tv_sec) + nanoseconds(ts.tv_nsec);
        return system_clock::time_point(duration_cast<system_clock::duration>(total_ns));
    }
};
```
:::
