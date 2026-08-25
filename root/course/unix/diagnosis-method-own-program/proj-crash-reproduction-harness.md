# ⚙️ Стенд відтворення крашів та автоматизованого аналізу дампів

Цей практичний проект містить автономний стенд для контрольованого відтворення найпоширеніших типів апаратних та системних аварій (розіменування нульових вказівників, запис у захищені сегменти пам'яті `.rodata`, порушення вирівнювання векторних інструкцій, усічення файлів у відображеній пам'яті `mmap`, арифметичні збої та пошкодження купи `use-after-free`), а також сценарій автоматизованого захоплення та аналізу згенерованих дампів пам'яті (ELF Core Dumps) через пакетний режим відлагоджувача GDB.

---

## 1. Архітектура та мета стенду

Під час розробки високонавантаженого системного програмного забезпечення інженери часто стикаються з проблемою непередбачуваної поведінки процесів під час виникнення критичних помилок. Щоб перевірити працездатність системного моніторингу, коректність конфігурації генерації дампів пам'яті ядра Linux та надійність конвеєра посмертного аналізу без ризику для виробничих серверів, необхідна синтетична програма-мішень, здатна на вимогу детерміновано емулювати кожен із фундаментальних типів системних збоїв.

Стенд складається з двох взаємопов'язаних модулів:
1. **Програма-мішень (`crash_target`):** Консольний бінарний застосунок, написаний мовами C та C++, який приймає числовий аргумент командного рядка та виконує точну послідовність низькорівневих операцій для виклику конкретного системного сигналу (`SIGSEGV`, `SIGBUS`, `SIGABRT`, `SIGFPE`).
2. **Конвеєр автоматичного тріажу (`auto_triage.sh`):** Командний сценарій оболонки POSIX, який налаштовує системні ліміти розміру дампів (`ulimit -c unlimited`), запускає цільовий бінарник, фіксує код завершення ядра, вилучає збережений знімок пам'яті через утиліту `coredumpctl` або файлову систему, виконує серію діагностичних команд у пакетному режимі GDB (`batch mode`) та генерує структурований інженерний звіт про місце аварії.

---

## 2. Реалізація програми-мішені з різними типами крашів

Програма реалізує сім типових сценаріїв аварійного завершення, кожен з яких ілюструє окремий механізм взаємодії апаратного забезпечення процесора, блоку керування пам'яттю (MMU) та ядра операційної системи:

- `1` — `SIGSEGV` через розіменування нульового вказівника (`SEGV_MAPERR`): процесор намагається звернутися за адресою `0x0`, яка заблокована ядром через параметр `vm.mmap_min_addr`.
- `2` — `SIGSEGV` через спробу запису в константний сегмент `.rodata` (`SEGV_ACCERR`): віртуальна сторінка існує в адресному просторі процесу, проте в таблиці сторінок відсутній біт дозволу на запис `PROT_WRITE`.
- `3` — `SIGBUS` через читання за межами фізично усіченого файлу `mmap()` (`BUS_OBJERR`): файл на диску обрізано через `ftruncate()`, тому ядро не може завантажити сторінку з накопичувача при виникненні Page Fault.
- `4` — `SIGBUS` через апаратну невідповідність вирівнювання пам'яті (`BUS_ADRALN`): виконання векторної інструкції SSE `movdqa` (Aligned Data Movement) за адресою, некратною 16 байтам.
- `5` — `SIGABRT` через порушення логічного інваріанта макроса `assert()` та виклик бібліотечної функції `abort()`.
- `6` — `SIGFPE` через цілочисельне ділення на нуль або знакове переповнення `INT_MIN / -1` на інструкції `idiv` (`FPE_INTDIV` / `FPE_INTOVF`).
- `7` — `SIGSEGV` / пошкодження купи через звернення до пам'яті після звільнення (`Use-After-Free`).

:::tabs
@tab C
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <limits.h>
#include <assert.h>

static void trigger_null_dereference(void) {
    volatile int *ptr = NULL;
    *ptr = 42;
}

static void trigger_rodata_write(void) {
    const char *ro_str = "Read-only literal string";
    char *writable = (char *)ro_str;
    writable[0] = 'W';
}

static void trigger_mmap_truncate(void) {
    char filename[] = "/tmp/crash_mmap_XXXXXX";
    int fd = mkstemp(filename);
    if (fd < 0) return;

    size_t page_size = 4096;
    if (ftruncate(fd, page_size) != 0) {
        close(fd);
        unlink(filename);
        return;
    }

    char *mapped = mmap(NULL, page_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (mapped == MAP_FAILED) {
        close(fd);
        unlink(filename);
        return;
    }

    mapped[0] = 'A';
    /* Усікаємо файл до 0 байтів, залишаючи сторінку у VMA */
    if (ftruncate(fd, 0) != 0) {
        /* Ігноруємо помилку усічення */
    }

    /* Читання сторінки викликає Page Fault, ядро не знаходить блоку -> SIGBUS */
    volatile char val = mapped[128];
    (void)val;

    munmap(mapped, page_size);
    close(fd);
    unlink(filename);
}

static void trigger_unaligned_access(void) {
#if defined(__x86_64__) || defined(_M_X64)
    /* Вирівняне читання SSE інструкцією movdqa на невирівняну адресу */
    char buffer[64];
    char *unaligned_ptr = buffer + 1; /* Зсув на 1 байт порушує кратність 16 */
    __asm__ volatile (
        "movdqa (%0), %%xmm0"
        :
        : "r" (unaligned_ptr)
        : "xmm0"
    );
#else
    volatile char buffer[16];
    volatile long *ptr = (volatile long *)(buffer + 1);
    *ptr = 0xDEADBEEF;
#endif
}

static void trigger_abort_assert(void) {
    int invariant = 0;
    assert(invariant == 1);
}

static void trigger_divide_by_zero(int mode) {
    if (mode == 0) {
        volatile int zero = 0;
        volatile int result = 100 / zero;
        (void)result;
    } else {
        volatile int min_val = INT_MIN;
        volatile int divisor = -1;
        volatile int result = min_val / divisor;
        (void)result;
    }
}

static void trigger_use_after_free(void) {
    char *chunk = (char *)malloc(128);
    if (!chunk) return;
    strcpy(chunk, "Active memory chunk");
    free(chunk);
    /* Запис у звільнений блок пам'яті */
    chunk[0] = 'X';
    printf("Read after free: %s\n", chunk);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <1-7>\n", argv[0]);
        fprintf(stderr, " 1: SIGSEGV (NULL dereference)\n");
        fprintf(stderr, " 2: SIGSEGV (Write to .rodata)\n");
        fprintf(stderr, " 3: SIGBUS  (mmap truncate)\n");
        fprintf(stderr, " 4: SIGBUS  (unaligned SSE load)\n");
        fprintf(stderr, " 5: SIGABRT (assert failure)\n");
        fprintf(stderr, " 6: SIGFPE  (divide by zero / overflow)\n");
        fprintf(stderr, " 7: Use-After-Free\n");
        return 1;
    }

    int choice = atoi(argv[1]);
    switch (choice) {
        case 1: trigger_null_dereference(); break;
        case 2: trigger_rodata_write(); break;
        case 3: trigger_mmap_truncate(); break;
        case 4: trigger_unaligned_access(); break;
        case 5: trigger_abort_assert(); break;
        case 6: trigger_divide_by_zero(0); break;
        case 7: trigger_use_after_free(); break;
        default:
            fprintf(stderr, "Невідомий сценарій: %d\n", choice);
            return 1;
    }
    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <string_view>
#include <memory>
#include <vector>
#include <span>
#include <cstring>
#include <climits>
#include <cassert>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>

namespace crash_harness {

void trigger_null_dereference() {
    volatile int* ptr = nullptr;
    *ptr = 42;
}

void trigger_rodata_write() {
    constexpr std::string_view ro_str = "Read-only literal string";
    auto* writable = const_cast<char*>(ro_str.data());
    writable[0] = 'W';
}

void trigger_mmap_truncate() {
    char filename[] = "/tmp/crash_mmap_cpp_XXXXXX";
    int fd = mkstemp(filename);
    if (fd < 0) return;

    constexpr size_t page_size = 4096;
    if (ftruncate(fd, page_size) != 0) {
        close(fd);
        unlink(filename);
        return;
    }

    auto* mapped = static_cast<char*>(mmap(nullptr, page_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0));
    if (mapped == MAP_FAILED) {
        close(fd);
        unlink(filename);
        return;
    }

    mapped[0] = 'A';
    if (ftruncate(fd, 0) != 0) {
        /* Ігноруємо усічення */
    }

    volatile char val = mapped[128];
    (void)val;

    munmap(mapped, page_size);
    close(fd);
    unlink(filename);
}

void trigger_unaligned_access() {
#if defined(__x86_64__) || defined(_M_X64)
    alignas(64) char buffer[64]{};
    char* unaligned_ptr = buffer + 1;
    __asm__ volatile (
        "movdqa (%0), %%xmm0"
        :
        : "r" (unaligned_ptr)
        : "xmm0"
    );
#else
    char buffer[16]{};
    auto* ptr = reinterpret_cast<volatile long*>(buffer + 1);
    *ptr = 0xDEADBEEF;
#endif
}

void trigger_abort_assert() {
    int invariant = 0;
    assert(invariant == 1);
}

void trigger_divide_by_zero(int mode) {
    if (mode == 0) {
        volatile int zero = 0;
        volatile int result = 100 / zero;
        (void)result;
    } else {
        volatile int min_val = INT_MIN;
        volatile int divisor = -1;
        volatile int result = min_val / divisor;
        (void)result;
    }
}

void trigger_use_after_free() {
    auto chunk = std::make_unique<std::vector<int>>(100, 42);
    int* dangling_ref = &(*chunk)[0];
    chunk.reset(); /* Звільняємо пам'ять вектора */
    *dangling_ref = 999; /* Звернення після звільнення */
    std::cout << "Dangling value: " << *dangling_ref << "\n";
}

} // namespace crash_harness

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <1-7>\n"
                  << " 1: SIGSEGV (NULL dereference)\n"
                  << " 2: SIGSEGV (Write to .rodata)\n"
                  << " 3: SIGBUS  (mmap truncate)\n"
                  << " 4: SIGBUS  (unaligned SSE load)\n"
                  << " 5: SIGABRT (assert failure)\n"
                  << " 6: SIGFPE  (divide by zero / overflow)\n"
                  << " 7: Use-After-Free\n";
        return 1;
    }

    int choice = std::stoi(argv[1]);
    switch (choice) {
        case 1: crash_harness::trigger_null_dereference(); break;
        case 2: crash_harness::trigger_rodata_write(); break;
        case 3: crash_harness::trigger_mmap_truncate(); break;
        case 4: crash_harness::trigger_unaligned_access(); break;
        case 5: crash_harness::trigger_abort_assert(); break;
        case 6: crash_harness::trigger_divide_by_zero(0); break;
        case 7: crash_harness::trigger_use_after_free(); break;
        default:
            std::cerr << "Невідомий сценарій: " << choice << "\n";
            return 1;
    }
    return 0;
}
```
:::

---

## 3. Скрипт автоматичного збору та тріажу дампів

Наведений нижче bash-скрипт `auto_triage.sh` компілює тестовий бінарник із символами DWARF (`-g -O1`), вмикає необмежений ліміт генерації дампів `ulimit -c unlimited`, запускає програму-мішень, перехоплює код аварії та генерує повний звіт за допомогою GDB у неінтерактивному пакетному режимі (`batch mode`).

```bash
#!/usr/bin/env bash
set -euo pipefail

TARGET_SRC="crash_target.c"
TARGET_BIN="./crash_target_bin"
CORE_FILE="./core"
REPORT_FILE="crash_triage_report.txt"

SCENARIO="${1:-1}"

echo "=== [1/4] Компіляція бінарника з DWARF символами ==="
gcc -g -O1 -fno-omit-frame-pointer "${TARGET_SRC}" -o "${TARGET_BIN}"

echo "=== [2/4] Налаштування оточення для фіксації Core Dump ==="
ulimit -c unlimited

# Видаляємо старий дамп, якщо існував
rm -f "${CORE_FILE}" "${REPORT_FILE}"

echo "=== [3/4] Запуск програми-мішені зі сценарієм ${SCENARIO} ==="
set +e
"${TARGET_BIN}" "${SCENARIO}"
EXIT_CODE=$?
set -e

echo "Процес завершився з кодом: ${EXIT_CODE}"
if [ "${EXIT_CODE}" -le 128 ]; then
    echo "Помилка: Програма завершилася штатно або без сигналу."
    exit 1
fi

SIGNAL=$((EXIT_CODE - 128))
echo "Зафіксовано сигнал-вбивцю: ${SIGNAL}"

# Перевіряємо локальний core або шукаємо через coredumpctl
if [ ! -f "${CORE_FILE}" ]; then
    if command -v coredumpctl &>/dev/null; then
        echo "Локальний core не знайдено, витягуємо останній знімок через coredumpctl..."
        coredumpctl dump "${TARGET_BIN}" -o "${CORE_FILE}" || true
    fi
fi

if [ ! -f "${CORE_FILE}" ]; then
    echo "Увага: Файл Core Dump не згенеровано. Перевірте /proc/sys/kernel/core_pattern."
    exit 1
fi

echo "=== [4/4] Автоматичний аналіз у GDB Batch Mode ==="
gdb -batch \
    -ex "echo \n--- [СТЕК ВИКЛИКІВ З ЛОКАЛЬНИМИ ЗМІННИМИ] ---\n" \
    -ex "bt full" \
    -ex "echo \n--- [РЕГІСТРИ ПРОЦЕСОРА] ---\n" \
    -ex "info registers" \
    -ex "echo \n--- [ПАМ'ЯТЬ ВЕРШИНИ СТЕКА] ---\n" \
    -ex "x/16gx \$rsp" \
    -ex "echo \n--- [ДИЗАСЕМБЛЮВАННЯ НАВКОЛО ВКАЗІВНИКА ІНСТРУКЦІЙ] ---\n" \
    -ex "disassemble \$rip-16, \$rip+16" \
    "${TARGET_BIN}" "${CORE_FILE}" > "${REPORT_FILE}"

echo "Аналіз успішно завершено. Звіт збережено у: ${REPORT_FILE}"
echo "=========================================================="
head -n 25 "${REPORT_FILE}"
```

---

## 4. Порівняння результату: Core Dump проти AddressSanitizer

Для оцінки ефективності діагностики скомпілюємо той самий код із прапорцями інструментації AddressSanitizer та UndefinedBehaviorSanitizer:

```bash
gcc -fsanitize=address,undefined -g -O1 "${TARGET_SRC}" -o crash_target_asan
./crash_target_asan 7
```

При спробі звернення до звільненої пам'яті (`Use-After-Free`) AddressSanitizer миттєво перехоплює звернення до червоної зони (`0xfd`) і друкує структурований звіт:

```text
=================================================================
==18420==ERROR: AddressSanitizer: heap-use-after-free on address 0x60f000000040 at pc 0x00000040132b bp 0x7ffd5a987040 sp 0x7ffd5a987038
WRITE of size 1 at 0x60f000000040 thread T0
    #0 0x40132a in trigger_use_after_free crash_target.c:98
    #1 0x40141f in main crash_target.c:122
    #2 0x7f3e82029d8f in __libc_start_call_main ../sysdeps/nptl/libc_start_call_main.h:58

0x60f000000040 is located 0 bytes inside of 128-byte region [0x60f000000040,0x60f0000000c0)
freed by thread T0 here:
    #0 0x7f3e82498527 in __interceptor_free ../../../../src/libsanitizer/asan/asan_malloc_linux.cpp:127
    #1 0x401318 in trigger_use_after_free crash_target.c:96

previously allocated by thread T0 here:
    #0 0x7f3e82498867 in __interceptor_malloc ../../../../src/libsanitizer/asan/asan_malloc_linux.cpp:145
    #1 0x4012e8 in trigger_use_after_free crash_target.c:93
=================================================================
```

Звіт ASan надає повну тріаду фактів: де пам'ять було виділено, де її було звільнено, і який рядок коду здійснив несанкціоноване звернення. У поєднанні з посмертним аналізом Core Dump у GDB це забезпечує повне закриття всіх класів несправностей пам'яті.

---

## 5. Безпека та керування дампами в інфраструктурі CI/CD

Під час впровадження автоматизованого збору дампів пам'яті в конвеєри безперервної інтеграції (CI/CD) та на серверах тестування необхідно враховувати три критичні інженерні фактори:

1. **Керування дисковим простором і ротація:** Файли дампів пам'яті процесів із великими адресними просторами (наприклад, баз даних або кеш-серверів) можуть досягати десятків гігабайтів. Якщо конвеєр тестів генерує десятки аварій, дисковий розділ `/var/lib/systemd/coredump` швидко переповниться, блокуючи роботу операційної системи. Необхідно налаштовувати ліміти збереження у файлі `/etc/systemd/coredump.conf`:
   ```ini
   [Coredump]
   Storage=external
   Compress=yes
   MaxUse=2G
   KeepFree=5G
   ```
2. **Очищення конфіденційних даних (Data Sanitization):** Файл ELF Core Dump містить повний зліпок віртуальних сторінок пам'яті процесу. Якщо програма обробляла приватні ключі TLS, паролі автентифікації користувачів, банківські картки або персональні дані, усі ці байти потрапляють у відкритому вигляді у файл дампу. Для захисту конфіденційних буферів розробники повинні використовувати системні виклики `madvise(buffer, size, MADV_DONTDUMP)`, які явно забороняють ядру Linux включати вказані діапазони пам'яті до складу аварійного зліпка.
3. **Збереження збігів версій бінарників та налагоджувальних символів:** Аналіз дампа в GDB повністю спирається на наявність точного виконуваного файлу, що згенерував цей знімок. Якщо в системі відбулося оновлення бінарника до нової версії, старий core dump більше не зможе коректно зіставити адреси інструкцій зі зневаджувальними таблицями DWARF. Тому в інфраструктурі автоматизованого тріажу разом із файлом дампу завжди зберігають відповідний Build ID бінарника (`readelf -n ./app | grep "Build ID"`), а символьні файли завантажують із централізованого сервера `debuginfod`.
