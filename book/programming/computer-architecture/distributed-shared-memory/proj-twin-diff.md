# ⚙️ Реалізація механізму Twin-and-Diff та захисту сторінок у Software DSM

Цей практичний розбір демонструє, як у просторі користувача операційної системи реалізувати повний контур сторінкового захисту пам'яті, створення тіньового двійника (Twin) при перехопленні апаратного виключення запису та алгоритм обчислення компактного журналу відмінностей (Diff) для безконфліктного злиття паралельних модифікацій.

## Задача та архітектурна ідея

У класичній багатопотоковій програмі, коли кілька обчислювальних вузлів паралельно модифікують власні незалежні змінні, розташовані в межах однієї й тієї самої сторінки розміром 4096 байтів, виникає руйнівне хибне спільне використання (англ. *false sharing*). Протокол з одним записувачем (Single-Writer) змушений безперервно відбирати виключне право запису, ганяючи всю 4-кілобайтну сторінку туди й назад мережею (сторінковий пінг-понг).

Протокол множинних записувачів (англ. *Multiple-Writer Protocol*) розв'язує цю проблему через конструювання трьох послідовних програмних фаз:

1. **Перехоплення першого запису (Write Trap):** Спільна сторінка спочатку захищена від запису через системний виклик `mprotect(addr, PAGE_SIZE, PROT_READ)`. Перша ж спроба потоку виконати машинну інструкцію запису (`mov [rdi], rax` або `str x0, [x1]`) генерує апаратне виключення процесора Page Fault. Ядро операційної системи перехоплює це виключення й доставляє процесу сигнал порушення захисту пам'яті `SIGSEGV`.
2. **Створення тіньового двійника (Twin Creation):** Обробник сигналу у просторі користувача визначає базову адресу сторінки, виділяє буфер пам'яті такого самого розміру (4096 байтів) і копіює в нього поточний чистий стан сторінки. Після цього сторінці надаються повні права `PROT_READ | PROT_WRITE`, і виконання перерваної інструкції процесора відновлюється без виходу з ладу програми.
3. **Обчислення та накладання різниці (Diff Computation and Merge):** Під час досягнення точки синхронізації (виклику `Release` або передачі замка) середовище виконання DSM порівнює змінену робочу сторінку з її двійником. Усі виявлені невідповідності кодуються у компактний список дескрипторів `(offset, length, bytes)`. Тільки цей журнал відмінностей передається мережею, а вузол-одержувач накладає його на свою локальну копію сторінки, не затираючи при цьому власні паралельні зміни в інших байтах тієї самої сторінки.

## Повний робочий код реалізації

Нижче наведено самодостатню реалізацію протоколу Twin-and-Diff мовами C та C++ з використанням стандартних системних викликів POSIX.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/mman.h>

#define PAGE_SIZE 4096
#define MAX_DIFF_ENTRIES 64

typedef struct {
    uint32_t offset;
    uint32_t length;
    uint8_t  data[PAGE_SIZE];
} DiffEntry;

typedef struct {
    size_t count;
    DiffEntry entries[MAX_DIFF_ENTRIES];
} DiffLog;

static void *g_shared_page = NULL;
static void *g_twin_page   = NULL;
static volatile sig_atomic_t g_is_dirty = 0;

static void sigsegv_handler(int sig, siginfo_t *info, void *ucontext) {
    (void)sig;
    (void)ucontext;
    uintptr_t fault_addr = (uintptr_t)info->si_addr;
    uintptr_t page_base  = (uintptr_t)g_shared_page;

    /* Перевіряємо, чи адреса збою належить нашій спільній DSM-сторінці */
    if (fault_addr >= page_base && fault_addr < page_base + PAGE_SIZE) {
        if (!g_twin_page) {
            g_twin_page = malloc(PAGE_SIZE);
            if (!g_twin_page) {
                _exit(EXIT_FAILURE);
            }
        }
        /* Фіксуємо чистий еталонний стан сторінки перед записом */
        memcpy(g_twin_page, g_shared_page, PAGE_SIZE);
        g_is_dirty = 1;

        /* Відкриваємо права на запис для повтору машинної інструкції */
        if (mprotect(g_shared_page, PAGE_SIZE, PROT_READ | PROT_WRITE) != 0) {
            _exit(EXIT_FAILURE);
        }
    } else {
        /* Збій поза межами керованої DSM-пам'яті: фатальна помилка */
        _exit(139);
    }
}

void dsm_init(void) {
    /* Виділяємо пам'ять, строго вирівняну за межею апаратної сторінки 4096 байтів */
    if (posix_memalign(&g_shared_page, PAGE_SIZE, PAGE_SIZE) != 0) {
        perror("posix_memalign");
        exit(EXIT_FAILURE);
    }

    /* Заповнюємо початковим шаблоном даних */
    memset(g_shared_page, 0xAA, PAGE_SIZE);

    /* Встановлюємо початковий захист: лише для читання */
    if (mprotect(g_shared_page, PAGE_SIZE, PROT_READ) != 0) {
        perror("mprotect");
        exit(EXIT_FAILURE);
    }

    /* Реєструємо розширений обробник сигналу SIGSEGV */
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_flags = SA_SIGINFO;
    sa.sa_sigaction = sigsegv_handler;
    sigemptyset(&sa.sa_mask);

    if (sigaction(SIGSEGV, &sa, NULL) != 0) {
        perror("sigaction");
        exit(EXIT_FAILURE);
    }
}

void dsm_compute_diff(DiffLog *log) {
    log->count = 0;
    if (!g_is_dirty || !g_twin_page) {
        return;
    }

    const uint8_t *curr = (const uint8_t *)g_shared_page;
    const uint8_t *twin = (const uint8_t *)g_twin_page;
    size_t i = 0;

    /* Сканування відмінностей між робочою сторінкою та двійником */
    while (i < PAGE_SIZE) {
        if (curr[i] != twin[i]) {
            size_t start = i;
            while (i < PAGE_SIZE && curr[i] != twin[i]) {
                i++;
            }
            size_t len = i - start;
            if (log->count < MAX_DIFF_ENTRIES) {
                DiffEntry *entry = &log->entries[log->count++];
                entry->offset = (uint32_t)start;
                entry->length = (uint32_t)len;
                memcpy(entry->data, &curr[start], len);
            }
        } else {
            i++;
        }
    }
}

void dsm_apply_diff(void *dest_page, const DiffLog *log) {
    uint8_t *dest = (uint8_t *)dest_page;
    for (size_t k = 0; k < log->count; ++k) {
        const DiffEntry *e = &log->entries[k];
        memcpy(dest + e->offset, e->data, e->length);
    }
}

void dsm_cleanup(void) {
    if (g_shared_page) {
        mprotect(g_shared_page, PAGE_SIZE, PROT_READ | PROT_WRITE);
        free(g_shared_page);
        g_shared_page = NULL;
    }
    if (g_twin_page) {
        free(g_twin_page);
        g_twin_page = NULL;
    }
}

int main(void) {
    dsm_init();

    printf("DSM ініціалізовано. Спроба запису в захищену сторінку...\n");

    /* Змінні розташовані в різних ділянках однієї сторінки (False Sharing) */
    uint32_t *var_a = (uint32_t *)((uintptr_t)g_shared_page + 16);
    uint32_t *var_b = (uint32_t *)((uintptr_t)g_shared_page + 2048);

    /* Ці інструкції викликають SIGSEGV, обробник створює Twin і дозволяє запис */
    *var_a = 0x12345678;
    *var_b = 0x9ABCDEF0;

    printf("Запис виконано прозоро: var_a = 0x%X, var_b = 0x%X\n", *var_a, *var_b);

    /* Генерація журналу відмінностей */
    DiffLog log;
    dsm_compute_diff(&log);

    printf("Згенеровано блоків відмінностей: %zu\n", log.count);
    for (size_t i = 0; i < log->count; ++i) {
        printf("  Блок %zu: зсув %u, розмір %u байтів\n",
               i, log.entries[i].offset, log.entries[i].length);
    }

    /* Симуляція віддаленого вузла: накладання Diff на чисту копію сторінки */
    void *remote_page = NULL;
    if (posix_memalign(&remote_page, PAGE_SIZE, PAGE_SIZE) == 0) {
        memset(remote_page, 0xAA, PAGE_SIZE);
        dsm_apply_diff(remote_page, &log);

        uint32_t *rem_a = (uint32_t *)((uintptr_t)remote_page + 16);
        uint32_t *rem_b = (uint32_t *)((uintptr_t)remote_page + 2048);
        printf("Результат на віддаленому вузлі: rem_a = 0x%X, rem_b = 0x%X\n", *rem_a, *rem_b);
        free(remote_page);
    }

    dsm_cleanup();
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <cstdint>
#include <cstring>
#include <csignal>
#include <sys/mman.h>
#include <unistd.h>

constexpr size_t PAGE_SIZE = 4096;

struct DiffEntry {
    uint32_t offset{0};
    std::vector<uint8_t> data;
};

class DsmPageManager {
public:
    static DsmPageManager& instance() {
        static DsmPageManager mgr;
        return mgr;
    }

    void init() {
        void* ptr = nullptr;
        if (posix_memalign(&ptr, PAGE_SIZE, PAGE_SIZE) != 0) {
            throw std::bad_alloc();
        }
        shared_page_ = static_cast<uint8_t*>(ptr);
        std::memset(shared_page_, 0xAA, PAGE_SIZE);

        if (mprotect(shared_page_, PAGE_SIZE, PROT_READ) != 0) {
            throw std::runtime_error("mprotect failed");
        }

        struct sigaction sa{};
        sa.sa_flags = SA_SIGINFO;
        sa.sa_sigaction = &DsmPageManager::handle_sigsegv;
        sigemptyset(&sa.sa_mask);

        if (sigaction(SIGSEGV, &sa, nullptr) != 0) {
            throw std::runtime_error("sigaction failed");
        }
    }

    [[nodiscard]] uint8_t* page_ptr() noexcept { return shared_page_; }

    [[nodiscard]] std::vector<DiffEntry> compute_diff() const {
        std::vector<DiffEntry> diffs;
        if (!is_dirty_ || twin_page_.empty()) {
            return diffs;
        }

        size_t i = 0;
        while (i < PAGE_SIZE) {
            if (shared_page_[i] != twin_page_[i]) {
                size_t start = i;
                while (i < PAGE_SIZE && shared_page_[i] != twin_page_[i]) {
                    ++i;
                }
                size_t len = i - start;
                DiffEntry entry{
                    .offset = static_cast<uint32_t>(start),
                    .data = std::vector<uint8_t>(shared_page_ + start, shared_page_ + start + len)
                };
                diffs.push_back(std::move(entry));
            } else {
                ++i;
            }
        }
        return diffs;
    }

    static void apply_diff(std::span<uint8_t, PAGE_SIZE> dest, const std::vector<DiffEntry>& diffs) {
        for (const auto& entry : diffs) {
            std::memcpy(dest.data() + entry.offset, entry.data.data(), entry.data.size());
        }
    }

    ~DsmPageManager() {
        if (shared_page_) {
            mprotect(shared_page_, PAGE_SIZE, PROT_READ | PROT_WRITE);
            std::free(shared_page_);
            shared_page_ = nullptr;
        }
    }

private:
    DsmPageManager() = default;

    static void handle_sigsegv(int sig, siginfo_t* info, void* ucontext) {
        (void)sig;
        (void)ucontext;
        auto& mgr = instance();
        auto fault_addr = reinterpret_cast<uintptr_t>(info->si_addr);
        auto page_base  = reinterpret_cast<uintptr_t>(mgr.shared_page_);

        if (fault_addr >= page_base && fault_addr < page_base + PAGE_SIZE) {
            if (mgr.twin_page_.empty()) {
                mgr.twin_page_.resize(PAGE_SIZE);
            }
            std::memcpy(mgr.twin_page_.data(), mgr.shared_page_, PAGE_SIZE);
            mgr.is_dirty_ = true;

            if (mprotect(mgr.shared_page_, PAGE_SIZE, PROT_READ | PROT_WRITE) != 0) {
                _exit(EXIT_FAILURE);
            }
        } else {
            _exit(139);
        }
    }

    uint8_t* shared_page_{nullptr};
    std::vector<uint8_t> twin_page_;
    volatile sig_atomic_t is_dirty_{false};
};

int main() {
    auto& dsm = DsmPageManager::instance();
    dsm.init();

    std::cout << "DSM ініціалізовано. Запис у захищену пам'ять C++..." << std::endl;

    auto* var_a = reinterpret_cast<uint32_t*>(dsm.page_ptr() + 16);
    auto* var_b = reinterpret_cast<uint32_t*>(dsm.page_ptr() + 2048);

    *var_a = 0x12345678;
    *var_b = 0x9ABCDEF0;

    std::cout << "Запис завершено: var_a = 0x" << std::hex << *var_a
              << ", var_b = 0x" << *var_b << std::dec << std::endl;

    const auto diffs = dsm.compute_diff();
    std::cout << "Згенеровано блоків відмінностей: " << diffs.size() << std::endl;

    for (size_t i = 0; i < diffs.size(); ++i) {
        std::cout << "  Блок " << i << ": зсув " << diffs[i].offset
                  << ", розмір " << diffs[i].data.size() << " байтів" << std::endl;
    }

    alignas(PAGE_SIZE) uint8_t remote_page[PAGE_SIZE];
    std::memset(remote_page, 0xAA, PAGE_SIZE);

    DsmPageManager::apply_diff(std::span<uint8_t, PAGE_SIZE>(remote_page), diffs);

    auto* rem_a = reinterpret_cast<uint32_t*>(remote_page + 16);
    auto* rem_b = reinterpret_cast<uint32_t*>(remote_page + 2048);

    std::cout << "Дані на віддаленій сторінці: rem_a = 0x" << std::hex << *rem_a
              << ", rem_b = 0x" << *rem_b << std::dec << std::endl;

    return 0;
}
```
:::

## Покроковий розбір системних механізмів

### 1. Вирівнювання пам'яті та системний виклик `mprotect()`
Апаратний блок MMU процесора оперує пам'яттю виключно кратно розміру фізичної сторінки. У системних архітектурах x86-64 та ARMv8 молодші 12 бітів віртуальної адреси визначають зсув усередині сторінки (`4096 = 2¹²`). Системний виклик `mprotect(void *addr, size_t len, int prot)` вимагає, щоб вхідний покажчик `addr` був строго вирівняний за адресою, кратною 4096 (тобто молодші 12 бітів адреси мають дорівнювати нулю `addr & 0xFFF == 0`).

Звичайний виклик `malloc()` не гарантує сторінкового вирівнювання (він вирівнює пам'ять за межею 8 або 16 байтів). Спроба викликати `mprotect()` для невирівняної адреси завершується системною помилкою `EINVAL` (Invalid argument). Саме тому для розподілу пам'яті DSM використовується функція `posix_memalign()` або безпосередній виклик `mmap()` з прапорцями `MAP_ANONYMOUS | MAP_PRIVATE`.

### 2. Архітектура доставки сигналів та структура `siginfo_t`
Коли процесор намагається виконати запис у сторінку з бітами `PROT_READ`, контролер MMU фіксує порушення привілеїв доступу і генерує внутрішнє переривання `#PF` (Page Fault Exception). Процесор зберігає адресу пам'яті, що викликала збій, у спеціальному службовому регістрі керування `CR2` (на архітектурі x86) або `FAR_EL1` (на архітектурі ARM64).

Ядро операційної системи Linux перехоплює це переривання, знаходить структуру керування віртуальною пам'яттю процесу (`vm_area_struct`) і бачить, що доступ заборонено. Ядро формує сигнал `SIGSEGV` і створює структуру даних `siginfo_t`, записуючи збережене значення з регістра `CR2` у поле `si_addr`.

Використання прапорця `SA_SIGINFO` під час виклику `sigaction()` є критично важливим: воно змушує ядро передавати в обробник розширений триаргументний прототип `void (*sa_sigaction)(int, siginfo_t *, void *)`. Без цього прапорця обробник отримав би лише номер сигналу (число 11) без інформації про те, яка саме адреса викликала збій.

### 3. Оптимізація сканування: побайтове порівняння проти 64-бітного та SIMD
У наведеному навчальному прикладі функція `dsm_compute_diff()` виконує побайтове порівняння масивів. Для сторінки розміром 4096 байтів це займає 4096 ітерацій циклу.

У високопродуктивних виробничих системах (як-от TreadMarks) використовується дворівневе сканування:
- **64-бітне сканування слів:** Пам'ять переглядається як масив 64-розрядних цілих чисел `uint64_t`. Порівняння `curr_u64[i] ^ twin_u64[i]` займає лише 512 ітерацій на 4-кілобайтну сторінку. Якщо результат побітового XOR дорівнює нулю, весь 8-байтовий блок пропускається за один такт процесора.
- **Векторизація SIMD (AVX2 / AVX-512):** За допомогою векторних інструкцій `_mm256_loadu_si256` та `_mm256_cmpeq_epi8` процесор порівнює 32 байти пам'яті за одну інструкцію. Маска невідповідностей генерується через `_mm256_movemask_epi8`. Це скорочує час обчислення Diff для 4КБ сторінки до менш ніж 150 наносекунд.

:::tabs
```c
/* Оптимізоване 64-бітне сканування сторінки мовою C */
void dsm_compute_diff_fast(const uint64_t *curr, const uint64_t *twin, DiffLog *log) {
    size_t words = PAGE_SIZE / sizeof(uint64_t);
    for (size_t w = 0; w < words; ++w) {
        if (curr[w] != twin[w]) {
            uint32_t byte_offset = (uint32_t)(w * sizeof(uint64_t));
            const uint8_t *c_bytes = (const uint8_t *)&curr[w];
            const uint8_t *t_bytes = (const uint8_t *)&twin[w];
            for (size_t b = 0; b < 8; ++b) {
                if (c_bytes[b] != t_bytes[b]) {
                    /* Запис зміненого байта в журнал відмінностей */
                }
            }
        }
    }
}
```
```cpp
/* Оптимізоване 64-бітне сканування сторінки мовою C++ */
void compute_diff_fast(std::span<const uint64_t, PAGE_SIZE / sizeof(uint64_t)> curr,
                       std::span<const uint64_t, PAGE_SIZE / sizeof(uint64_t)> twin,
                       std::vector<DiffEntry>& diffs) {
    for (size_t w = 0; w < curr.size(); ++w) {
        if (curr[w] != twin[w]) {
            auto c_bytes = std::as_bytes(curr.subspan(w, 1));
            auto t_bytes = std::as_bytes(twin.subspan(w, 1));
            for (size_t b = 0; b < 8; ++b) {
                if (c_bytes[b] != t_bytes[b]) {
                    /* Запис зміненого байта в контейнер відмінностей */
                }
            }
        }
    }
}
```
:::

## Інженерні пастки та межі безпеки

### 1. Асинхронна безпека сигналів (Async-Signal-Safety)
Сигнал `SIGSEGV` є синхронним (він генерується самим потоком під час виконання інструкції), але його обробник виконується на стеку перерваного потоку.

Стандартні функції керування динамічною пам'яттю `malloc()` та `free()` використовують внутрішні м'ютекси для захисту структур купи (heap). Якщо потік викликав `malloc()`, захопив внутрішній замок купи, і в цей момент отримав `SIGSEGV` через доступ до DSM-сторінки, повторний виклик `malloc()` всередині обробника сигналу призведе до **миттєвого взаємного блокування (Deadlock)** самого на себе.

**Правильне інженерне рішення:** Пул сторінок-двійників виділяється заздалегідь під час ініціалізації середовища DSM (`dsm_init`). Обробник сигналу не викликає `malloc()`, а бере готовий вільний буфер із безблокувального пулу (Lock-Free Page Pool).

### 2. Поведінка при багатопотоковості всередині одного вузла
Якщо процес містить кілька потоків POSIX (pthreads), що виконуються на різних ядрах одного процесора, зміна прав сторінки через `mprotect()` впливає на **всі потоки процесу одночасно**, оскільки таблиця сторінок є спільною для процесу.

Коли потік 0 викликає `SIGSEGV` і знімає захист зі сторінки через `mprotect(PROT_WRITE)`, потік 1 на сусідньому ядрі процесора може почати записувати в ту саму сторінку до того, як потік 0 завершить копіювання двійника. Це спричиняє пошкодження еталонного стану Twin. Для запобігання цьому доступ до створення двійника має захищатися внутрішнім атомарним спінлоком вузла.

### 3. Гарантії коректності при злитті (Data-Race-Free Contract)
Протокол Twin-and-Diff гарантує математично коректне злиття змін лише для програм, що відповідають контракту **DRF (Data-Race-Free)**: якщо паралельні потоки пишуть у різні змінні, їхні адреси не перетинаються за байтовими зсувами.

Якщо два віддалені вузли одночасно змінять одне й те саме 32-бітне поле без використання м'ютекса, накладання їхніх журналів Diff створить недетермінований конфлікт: результат залежатиме від того, чий мережний пакет прибув останнім (Last-Writer-Wins). DSM-системи не виправляють помилки гонок даних у програмах користувача — вони забезпечують коректність лише для належно синхронізованого паралельного коду.

## Покроковий аналіз виконання та геометрія пам'яті

Розглянемо стан пам'яті під час виконання тестового сценарію нашого коду:

1. **Початковий стан:**
   Пам'ять за базовою адресою `g_shared_page` заповнена байтами `0xAA` (бітовий патерн `10101010`).
   Права доступу: `PROT_READ`.
   Тіньовий покажчик: `g_twin_page == NULL`.
   Прапорець: `g_is_dirty == 0`.

2. **Перший запис за адресою `page_base + 16`:**
   Процесор намагається записати 4 байти `0x12345678` (у порядку Little-Endian у пам'яті це байти `78 56 34 12`).
   Апаратний збій викликає `sigsegv_handler`.
   Обробник копіює 4096 байтів чистого масиву `0xAA` у `g_twin_page`, виставляє `g_is_dirty = 1` та відкриває права `PROT_READ | PROT_WRITE`.
   Ядро ОС повертає керування інструкції запису, яка тепер успішно розміщує байти `78 56 34 12` за зсувом 16.

3. **Другий запис за адресою `page_base + 2048`:**
   Процесор записує значення `0x9ABCDEF0` (байти `F0 DE BC 9A`) за зсувом 2048. Оскільки сторінка вже має права на запис, ця інструкція виконується напряму без виклику обробника сигналу.

4. **Генерація Diff:**
   Сканер `dsm_compute_diff()` порівнює `g_shared_page` та `g_twin_page`.
   - Зсуви 0..15: байти ідентичні (`0xAA`).
   - Зсуви 16..19: знайдено розбіжність. Формується `DiffEntry { offset: 16, length: 4, data: [0x78, 0x56, 0x34, 0x12] }`.
   - Зсуви 20..2047: байти ідентичні (`0xAA`).
   - Зсуви 2048..2051: знайдено розбіжність. Формується `DiffEntry { offset: 2048, length: 4, data: [0xF0, 0xDE, 0xBC, 0x9A] }`.
   - Зсуви 2052..4095: байти ідентичні (`0xAA`).

5. **Злиття на віддаленому вузлі:**
   Віддалений вузол отримує список із двох дескрипторів і застосовує функцію `dsm_apply_diff()`.
   Він записує 4 байти за зсувом 16 та 4 байти за зсувом 2048, залишаючи решту 4088 байтів своєї сторінки недоторканими.
   Сумарний обсяг переданих корисних даних склав лише 8 байтів замість пересилання 4096 байтів.

## Низькорівневий механізм повернення з обробника (`sigreturn`)

Коли обробник сигналу `sigsegv_handler` завершує виконання, відбувається спеціальний системний перехід:
- Ядро ОС створює на стеку структуру кадру сигналу (Signal Frame), що містить копію всіх регістрів процесора (`RAX`, `RBX`, `RCX`, `RSP`, `RIP`, `RFLAGS` тощо) у мить виникнення помилки.
- Повернення з обробника викликає системний виклик `sigreturn()` (на x86-64 це реалізується через повернення в трамплінний код `__restore_rt` у стандартній бібліотеці C).
- Ядро повністю відновлює значення всіх регістрів зі збереженого кадру, включаючи покажчик поточної інструкції `RIP`.
- Оскільки права сторінки в таблиці MMU вже змінені на `PROT_READ | PROT_WRITE`, процесор знову виконує ту саму інструкцію за адресою `RIP`, яка цього разу завершується за один такт.

## Групування суміжних модифікацій (Run-Length Encoding)

У наведеному алгоритмі `dsm_compute_diff()` реалізовано критично важливий принцип кодування неперервних блоків (Run-Length Encoding).

Якщо програма послідовно змінює масив структур (наприклад, 100 елементів по 8 байтів кожен), просте побайтове кодування згенерувало б 800 окремих дескрипторів `DiffEntry`. Кожен дескриптор додає 8 байтів службових даних (4 байти зсуву та 4 байти довжини), що призвело б до роздування службового оверхеду до `800 · 8 = 6400` байтів — більше за сам розмір сторінки!

Алгоритм сканування розв'язує цю проблему за один прохід:
- Внутрішній цикл `while (i < PAGE_SIZE && curr[i] != twin[i])` продовжує накопичувати індекс `i` доти, доки триває неперервна серія розбіжних байтів.
- Увесь діапазон із 800 змінених байтів пакується в **один єдиний дескриптор** `DiffEntry { offset: start, length: 800 }`.
- Службові витрати на заголовок становлять лише 8 байтів на весь 800-байтовий масив, забезпечуючи коефіцієнт стиснення журналу змін понад 99%.

## Векторизація порівняння через інструкції SIMD AVX-512

Для високопродуктивних вузлів із підтримкою векторного розширення AVX-512 операція порівняння 4096-байтної сторінки може виконуватися паралельно по 64 байти за одну машинну команду:

:::tabs
```c
/* Концептуальний векторний сканер AVX-512 мовою C */
void dsm_scan_avx512(const uint8_t *curr, const uint8_t *twin) {
    for (size_t offset = 0; offset < PAGE_SIZE; offset += 64) {
        /* Завантаження 64 байтів із робочої сторінки та двійника */
        __m512i v_curr = _mm512_loadu_si512((const void *)(curr + offset));
        __m512i v_twin = _mm512_loadu_si512((const void *)(twin + offset));

        /* Побайтове порівняння на рівність генерує 64-бітну маску */
        __mmask64 mask = _mm512_cmpeq_epi8_mask(v_curr, v_twin);

        /* Якщо всі 64 байти однакові, маска дорівнює ~0ULL (усі одиниці) */
        if (mask != ~0ULL) {
            /* Інвертуємо маску: одиничні біти позначають змінені байти */
            uint64_t diff_mask = ~mask;
            while (diff_mask != 0) {
                /* Пошук індексу першого зміненого байта через інструкцію CTZ */
                int bit_pos = __builtin_ctzll(diff_mask);
                /* Обробка зміни за зсувом: offset + bit_pos */
                diff_mask &= diff_mask - 1; /* Скидання молодшого біта */
            }
        }
    }
}
```
```cpp
/* Концептуальний векторний сканер AVX-512 мовою C++ */
void scan_avx512(std::span<const uint8_t, PAGE_SIZE> curr,
                 std::span<const uint8_t, PAGE_SIZE> twin) {
    for (size_t offset = 0; offset < PAGE_SIZE; offset += 64) {
        auto v_curr = _mm512_loadu_si512(reinterpret_cast<const void*>(curr.data() + offset));
        auto v_twin = _mm512_loadu_si512(reinterpret_cast<const void*>(twin.data() + offset));

        __mmask64 mask = _mm512_cmpeq_epi8_mask(v_curr, v_twin);

        if (mask != ~0ULL) {
            uint64_t diff_mask = ~mask;
            while (diff_mask != 0) {
                int bit_pos = __builtin_ctzll(diff_mask);
                // Обробка зміни за зсувом: offset + bit_pos
                diff_mask &= diff_mask - 1;
            }
        }
    }
}
```
:::

Використання апаратної інструкції `_mm512_cmpeq_epi8_mask` дозволяє перевірити всю сторінку розміром 4096 байтів лише за 64 векторні операції, знижуючи час створення Diff до кількох десятків наносекунд.

## Динамічний перехід на повну передачу сторінки (Dynamic Fallback)

Хоча диференційний механізм Twin-and-Diff мінімізує мережний трафік для більшості паралельних програм, існує граничний випадок: якщо потік виконує хаотичні дрібні записи по всій площі сторінки (наприклад, змінює кожен парний байт), кількість дескрипторів `DiffEntry` перевищує встановлений ліміт `MAX_DIFF_ENTRIES`, або розмір службових заголовків перевищує розмір самої сторінки.

Коли сумарний розмір згенерованого журналу `DiffLog` перевищує поріг ефективності:
```
Size(DiffLog) = count · (sizeof(uint32_t) · 2) + sum(lengths) > PAGE_SIZE
```
диференційне кодування втрачає будь-який математичний сенс.

У таких ситуаціях виробничі системи DSM застосовують динамічний відкат (Dynamic Fallback):
- Сканер зупиняє генерацію дескрипторів і позначає сторінку службовим прапорцем `DSM_FULL_PAGE_UPDATE`.
- Замість передачі масиву дескрипторів вузол пакує в мережний пакет монолітний сирий буфер розміром 4096 байтів.
- Вузол-одержувач виконує швидкий блоковий `memcpy()` всієї сторінки, минаючи поелементний розбір списку зсувів.

## Апаратне скидання TLB у багатоядерних системах (TLB Shootdown)

У багатоядерних процесорах зміна прав доступу до сторінки через `mprotect()` створює серйозний апаратний оверхед, відомий як **TLB Shootdown** (міжпроцесорне знеправлення буфера трансляції адрес):

1. Кожне процесорне ядро має власний локальний апаратний кеш трансляції віртуальних адрес у фізичні — **TLB** (Translation Lookaside Buffer).
2. Коли ядро 0 викликає `mprotect()`, воно оновлює запис у спільній таблиці сторінок процесу в оперативній пам'яті.
3. Проте ядра 1, 2 та 3 можуть зберігати застарілий запис TLB із правами `PROT_READ` у своїх локальних апаратних кешах.
4. Ядро 0 змушене згенерувати міжпроцесорне переривання (IPI, англ. *Inter-Processor Interrupt*) усім іншим ядрам процесора.
5. Усі сусідні ядра призупиняють виконання поточного коду, входять у контекст обробника переривання ядра ОС, виконують інструкцію скидання локального TLB (`invlpg` на x86-64) і надсилають підтвердження назад ядру 0.

Цей процес займає від 1.5 до 4 мікросекунд на сучасних 64-ядерних серверних процесорах. Саме тому моделі слабкої узгодженості (як-от Lazy Release Consistency) є критично важливими: вони мінімізують частоту викликів `mprotect()`, виконуючи зміну прав лише на глобальних бар'єрах синхронізації, а не на кожній операції запису.

## Взаємодія з оптимізаціями компілятора та бар'єри пам'яті

Під час компіляції з увімкненими рівнями оптимізації `-O2` або `-O3` компілятори GCC та Clang можуть виконувати агресивне перевпорядкування інструкцій (Instruction Reordering), винесення інваріантів за межі циклів (Loop-Invariant Code Motion) та кешування значень у регістрах.

У контексті сторінкового DSM це створює специфічні ризики:
- Якщо цикл модифікує значення за вказівником у захищеній пам'яті, компілятор може спробувати закешувати вказівник або завантажити значення в регістр до перевірки прав.
- Після повернення з обробника сигналу `sigsegv_handler` стан пам'яті змінюється (права відкриваються), але процесорні регістри та конвеєр мають бачити точний стан пам'яті.
- Щоб запобігти передчасному спекулятивному читанню та утриманню застарілих значень у регістрах, критичні змінні стану середовища оголошуються як `volatile sig_atomic_t`, а на межах викликів синхронізації `Acquire` та `Release` вставляються апаратні бар'єри пам'яті (`std::atomic_thread_fence(std::memory_order_seq_cst)` у C++ або `__atomic_thread_fence(__ATOMIC_SEQ_CST)` у C).

## Життєвий цикл стану сторінки

Повний автомат станів сторінки у вузлі DSM описується наступною послідовністю переходів:

1. `UNTOUCHED (PROT_NONE)`: Сторінка зареєстрована у віртуальному просторі, але не виділена у фізичній RAM. Читання або запис генерує сторінковий збій із мережним запитом свіжого вмісту.
2. `CLEAN_READ (PROT_READ)`: Сторінка містить актуальні дані. Читання виконується процесором за 1 нс. Перший запис генерує збій.
3. `TWINNED_DIRTY (PROT_READ | PROT_WRITE)`: Двійник створено у тіньовій пам'яті. Дозволено довільні локальні модифікації на повній швидкості RAM.
4. `DIFF_COMPUTED`: У точці синхронізації виконано сканування та згенеровано дескриптори відмінностей.
5. `SYNCHRONIZED`: Журнал Diff передано зацікавленим вузлам або домашньому каталогу, тіньовий двійник звільнено, сторінка повертається у стан `CLEAN_READ`.

Ця безшовна взаємодія між апаратним блоком MMU, ядром ОС та обробником у просторі користувача робить усю розподілену природу DSM абсолютно невидимою для коду прикладної програми.
