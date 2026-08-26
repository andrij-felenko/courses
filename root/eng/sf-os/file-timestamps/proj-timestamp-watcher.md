# ⚙️ Практикум: моніторинг часових позначок та емуляція рушія збирання

Системи автоматизованого збирання програмного забезпечення (такі як Make, Ninja, Tup або Bazel) безпосередньо спираються на часові позначки модифікації файлів (`mtime`) для визначення того, які проміжні артефакти проекту застаріли і потребують термінової перекомпіляції. Якщо джерельний файл з кодом було змінено пізніше, ніж створено відповідний об'єктний файл, рушій збирання запускає команду компілятора. У цьому практичному проекті ми реалізуємо повнофункціональну утиліту аналізу графа залежностей, яка використовує системний виклик `statx()` для наносекундного порівняння часу, виявляє ризики одночасних правок у межах одного секундного вікна та безпечно оновлює цільові артефакти за допомогою `utimensat()`.

---

### Інженерна постановка задачі

Для надійного збирання програмних комплексів у сучасних середовищах паралельного виконання рушій повинен подолати три фундаментальні архітектурні виклики:

1. **Прецизійна точність:** відрізняти модифікацію джерела від створення об'єктного файлу, навіть якщо обидві операції відбулися в межах одного такту таймера планувальника або кількох сотень мікросекунд на багатоядерній системі. Класичні виклики родини `stat()` з 1-секундною роздільністю призводили до того, що файл, відредагований через 200 мілісекунд після компіляції, мав однаковий час із цільовим бінарником, і система збирання ігнорувала зміни.
2. **Виявлення крайових гонок часу (race conditions):** ідентифікувати ситуації, коли файлова система носія інформації не підтримує наносекундну точність (наприклад, змонтований розділ FAT/VFAT, стара версія NFS або tmpfs із застарілими налаштуваннями ядра). У такому разі утиліта повинна явно попереджати розробника про ризик пропуску компіляції.
3. **Атомарність та селективність оновлення:** коректно змінювати часові мітки вихідних артефактів без спотворення часу доступу (`atime`) та без необхідності перевідкриття файлу на запис, використовуючи спеціальні прапорці ядра `UTIME_OMIT` та `UTIME_NOW`.

---

### Архітектура утиліти та послідовність операцій

Утиліта аналізує пару файлів — вихідне джерело (`source`) та скомпільований артефакт (`target`) — проходячи три послідовні фази виконання:

1. **Фаза інспекції метаданих:** для кожного файлу викликається `statx()` з маскою `STATX_MTIME | STATX_BTIME` та прапорцем `AT_SYMLINK_NOFOLLOW`. Це дозволяє уникнути випадкового опитування цілі символічного посилання та отримує як час модифікації даних `mtime`, так і час створення `btime` (якщо він підтримується файловою системою).
2. **Фаза резолюції залежностей:** виконується лексикографічне порівняння часових кортежів `(tv_sec, tv_nsec)`:
   - Якщо `tv_sec(src) > tv_sec(tgt)` або `(tv_sec(src) == tv_sec(tgt) && tv_nsec(src) > tv_nsec(tgt))`, ціль вважається застарілою, і планується перезбірка;
   - Якщо секунди та наносекунди повністю збігаються, утиліта перевіряє, чи не дорівнюють наносекунди нулю в обох файлах. Рівність нулеві зазвичай свідчить про штучне усічення точності файловою системою;
   - Якщо `mtime(src) <= mtime(tgt)`, ціль вважається актуальною.
3. **Фаза емуляції збірки та фіксації:** у разі необхідності перезбірки створюється або перезаписується цільовий файл, після чого системний виклик `utimensat()` фіксує точний системний час ядра для `mtime`, залишаючи `atime` незмінним.

---

### Реалізація на мовах C та C++

Нижче наведено самодостатні реалізації аналізатора на мовах C та C++20. Обидві програми виконують прямі системні виклики до ядра Linux, повністю контролюють виділення ресурсів та реалізують строгу обробку системних помилок.

:::tabs
```c
/* build_checker.c — Аналізатор залежностей на базі statx та utimensat */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <time.h>
#include <errno.h>

typedef struct {
    long long sec;
    unsigned int nsec;
    bool has_btime;
    long long btime_sec;
    unsigned int btime_nsec;
} FileMeta;

static int fetch_file_meta(const char *path, FileMeta *meta) {
    struct statx stx;
    memset(&stx, 0, sizeof(stx));

    if (statx(AT_FDCWD, path, AT_SYMLINK_NOFOLLOW, STATX_MTIME | STATX_BTIME, &stx) != 0) {
        return -1;
    }

    meta->sec = (long long)stx.stx_mtime.tv_sec;
    meta->nsec = stx.stx_mtime.tv_nsec;

    if (stx.stx_mask & STATX_BTIME) {
        meta->has_btime = true;
        meta->btime_sec = (long long)stx.stx_btime.tv_sec;
        meta->btime_nsec = stx.stx_btime.tv_nsec;
    } else {
        meta->has_btime = false;
    }

    return 0;
}

static int compare_timestamps(const FileMeta *a, const FileMeta *b) {
    if (a->sec != b->sec) {
        return (a->sec > b->sec) ? 1 : -1;
    }
    if (a->nsec != b->nsec) {
        return (a->nsec > b->nsec) ? 1 : -1;
    }
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <source_file> <target_file>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *src_path = argv[1];
    const char *tgt_path = argv[2];

    FileMeta src_meta, tgt_meta;

    if (fetch_file_meta(src_path, &src_meta) != 0) {
        fprintf(stderr, "Помилка читання джерела %s: %s\n", src_path, strerror(errno));
        return EXIT_FAILURE;
    }

    bool target_exists = (fetch_file_meta(tgt_path, &tgt_meta) == 0);

    printf("=== Аналіз часових позначок збірки ===\n");
    printf("Джерело: %s -> mtime = %lld.%09u с\n", src_path, src_meta.sec, src_meta.nsec);

    if (!target_exists) {
        printf("Ціль:    %s [відсутня, потрібна початкова збірка]\n", tgt_path);
    } else {
        printf("Ціль:    %s -> mtime = %lld.%09u с\n", tgt_path, tgt_meta.sec, tgt_meta.nsec);
    }

    bool need_rebuild = false;

    if (!target_exists) {
        need_rebuild = true;
    } else {
        int cmp = compare_timestamps(&src_meta, &tgt_meta);
        if (cmp > 0) {
            printf("Статус:  Ціль застаріла (джерело новіше за артефакт).\n");
            need_rebuild = true;
        } else if (cmp == 0) {
            printf("УВАГА:   Позначки збігаються з точністю до наносекунд!\n");
            if (src_meta.nsec == 0 && tgt_meta.nsec == 0) {
                printf("ПОПЕРЕДЖЕННЯ: Файлова система має лише 1-секундну точність!\n");
            }
            need_rebuild = false;
        } else {
            printf("Статус:  Ціль актуальна (перезбірка не потрібна).\n");
            need_rebuild = false;
        }
    }

    if (need_rebuild) {
        printf("\nВиконується збірка артефакту...\n");
        int fd = open(tgt_path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
        if (fd < 0) {
            fprintf(stderr, "Не вдалося створити ціль: %s\n", strerror(errno));
            return EXIT_FAILURE;
        }
        dprintf(fd, "Compiled artifact at %ld\n", time(NULL));
        close(fd);

        /* Фіксуємо новий час через utimensat */
        struct timespec ts[2];
        ts[0].tv_sec = 0;
        ts[0].tv_nsec = UTIME_OMIT; /* atime не чіпаємо */
        ts[1].tv_sec = 0;
        ts[1].tv_nsec = UTIME_NOW;  /* mtime = поточний час */

        if (utimensat(AT_FDCWD, tgt_path, ts, 0) != 0) {
            fprintf(stderr, "Помилка оновлення позначки: %s\n", strerror(errno));
            return EXIT_FAILURE;
        }
        printf("Збірку завершено успішно. Часову позначку оновлено.\n");
    }

    return EXIT_SUCCESS;
}
```
```cpp
// build_checker.cpp — Об'єктно-орієнтований аналізатор на C++20
#include <iostream>
#include <string_view>
#include <chrono>
#include <optional>
#include <system_error>
#include <fstream>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

class TimestampEngine {
public:
    struct Timestamp {
        std::chrono::seconds sec{0};
        std::chrono::nanoseconds nsec{0};

        auto operator<=>(const Timestamp&) const = default;
    };

    struct FileInfo {
        Timestamp mtime;
        std::optional<Timestamp> btime;
    };

    [[nodiscard]] static std::error_code get_info(std::string_view path,
                                                  FileInfo& info) noexcept {
        struct statx stx{};
        if (statx(AT_FDCWD, path.data(), AT_SYMLINK_NOFOLLOW,
                  STATX_MTIME | STATX_BTIME, &stx) != 0) {
            return std::error_code(errno, std::generic_category());
        }

        info.mtime = {
            std::chrono::seconds(stx.stx_mtime.tv_sec),
            std::chrono::nanoseconds(stx.stx_mtime.tv_nsec)
        };

        if (stx.stx_mask & STATX_BTIME) {
            info.btime = Timestamp{
                std::chrono::seconds(stx.stx_btime.tv_sec),
                std::chrono::nanoseconds(stx.stx_btime.tv_nsec)
            };
        } else {
            info.btime = std::nullopt;
        }

        return {};
    }

    [[nodiscard]] static std::error_code touch_target_mtime(std::string_view path) noexcept {
        struct timespec ts[2];
        ts[0].tv_sec = 0;
        ts[0].tv_nsec = UTIME_OMIT;
        ts[1].tv_sec = 0;
        ts[1].tv_nsec = UTIME_NOW;

        if (utimensat(AT_FDCWD, path.data(), ts, 0) != 0) {
            return std::error_code(errno, std::generic_category());
        }
        return {};
    }
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <source_file> <target_file>\n";
        return 1;
    }

    const std::string_view src_path = argv[1];
    const std::string_view tgt_path = argv[2];

    TimestampEngine::FileInfo src_info{};
    if (auto ec = TimestampEngine::get_info(src_path, src_info); ec) {
        std::cerr << "Помилка читання джерела: " << ec.message() << "\n";
        return 1;
    }

    TimestampEngine::FileInfo tgt_info{};
    bool target_exists = !TimestampEngine::get_info(tgt_path, tgt_info);

    std::cout << "=== Аналіз часових позначок (C++20 Engine) ===\n";
    std::cout << "Джерело: " << src_path << " -> "
              << src_info.mtime.sec.count() << "."
              << src_info.mtime.nsec.count() << " s\n";

    if (!target_exists) {
        std::cout << "Ціль:    " << tgt_path << " [відсутня]\n";
    } else {
        std::cout << "Ціль:    " << tgt_path << " -> "
                  << tgt_info.mtime.sec.count() << "."
                  << tgt_info.mtime.nsec.count() << " s\n";
    }

    if (!target_exists || src_info.mtime > tgt_info.mtime) {
        std::cout << "Рішення: Потрібна перекомпіляція артефакту.\n";
        
        {
            std::ofstream out(tgt_path.data(), std::ios::trunc);
            out << "Compiled binary data\n";
        }

        if (auto ec = TimestampEngine::touch_target_mtime(tgt_path); ec) {
            std::cerr << "Помилка оновлення часу: " << ec.message() << "\n";
            return 1;
        }
        std::cout << "Артефакт успішно зібрано та оновлено.\n";
    } else {
        std::cout << "Рішення: Ціль актуальна, збірку пропущено.\n";
    }

    return 0;
}
```
:::

---

### Аналіз системних викликів під час виконання утиліти

Якщо запустити скомпільовану утиліту під трасувальником `strace`, можна наочно простежити точний ланцюжок звернень до підсистем ядра Linux:

```
$ strace -e statx,openat,utimensat ./build_checker main.c app.o
statx(AT_FDCWD, "main.c", AT_SYMLINK_NOFOLLOW, STATX_MTIME|STATX_BTIME, {stx_mask=STATX_BASIC_STATS|STATX_BTIME, stx_mtime={tv_sec=1719398400, tv_nsec=154320987}, ...}) = 0
statx(AT_FDCWD, "app.o", AT_SYMLINK_NOFOLLOW, STATX_MTIME|STATX_BTIME, {stx_mask=STATX_BASIC_STATS|STATX_BTIME, stx_mtime={tv_sec=1719398350, tv_nsec=987654321}, ...}) = 0
openat(AT_FDCWD, "app.o", O_WRONLY|O_CREAT|O_TRUNC, 0644) = 3
utimensat(AT_FDCWD, "app.o", [{tv_sec=0, tv_nsec=UTIME_OMIT}, {tv_sec=0, tv_nsec=UTIME_NOW}], 0) = 0
```

Цей журнал демонструє ключову перевагу сучасного підходу: замість масивного вичитування всіх структур файлу ядро обмежується заповненням структури `struct statx`, а оновлення часу через `utimensat` не виконує повторного відкриття дескриптора на запис, мінімізуючи навантаження на журнали файлових систем `jbd2` (у Ext4) та `xfs_log` (у XFS).

---

### Підводні камені та інженерні пастки

Під час практичної розробки рушіїв збирання слід враховувати такі крайові сценарії:

1. **Атомарне перейменування файлів (`rename`):** коли компілятор записує результат у тимчасовий файл (наприклад, `app.o.tmp.1234`) і потім виконує `rename()` у `app.o`, часова позначка `mtime` залишається моментом відкриття тимчасового файлу, тоді як `ctime` оновлюється на момент виклику `rename()`. Якщо компіляція тривала кілька секунд, `mtime` об'єктного файлу може виявитися ранішим за момент фактичного завершення роботи збірки.
2. **Розсинхронізація годинників у розподілених збірках:** якщо джерельний код монтується через NFS, а компіляція виконується на різних вузлах кластера, розходження системних годинників вузлів навіть у 10 мілісекунд може призвести до циклічного нескінченного збирання або пропуску щойно згенерованих файлів. Сучасні системи (Bazel, Ninja) у таких середовищах доповнюють часові позначки криптографічним хешуванням вмісту (SHA-256).
3. **Усічення наносекунд при архівації:** утиліти архівації (стандартний `tar` без розширень POSIX.1-2001 pax, утиліта `cpio` або zip) обрізають часові позначки до 1 секунди чи навіть 2 секунд (FAT). Розпакування джерельного коду з такого архіву скидає наносекунди в `0`, що створює штучні гонки часу між сусідніми файлами.
4. **Порівняння через тристоронній оператор `<=>` на C++:** обчислення різниці часів через звичайне віднімання `ts1.tv_sec - ts2.tv_sec` небезпечне можливим арифметичним переповненням знакового 64-бітного цілого при роботі з пошкодженими файлами або штучними позначками далекого майбутнього. Використання стандартизованого тристороннього оператора порівняння `operator<=>` або лексикографічного порівняння пар гарантує коректний результат без ризику невизначеної поведінки (Undefined Behavior).
