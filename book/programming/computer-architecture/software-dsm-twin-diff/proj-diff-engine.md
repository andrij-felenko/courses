# ⚙️ Програмна реалізація рушія Twin-and-Diff для сторінкової DSM

Перехоплення звернень до пам'яті без модифікації компілятора спирається на взаємодію трьох компонентів операційної системи: виділення анонімної пам'яті через `mmap()`, динамічної зміни прав сторінок через `mprotect()` та обробки сигналів порушення захисту `SIGSEGV` через `sigaction()` із розширеним контекстом `SA_SIGINFO`. Рушій Twin-and-Diff координує ці примітиви, автоматично виділяючи двійники сторінок при першому записі та обчислюючи компактні дельти змін перед відправкою у мережу.

## Архітектурний дизайн та структури даних

Для ефективної роботи рушія у просторі користувача необхідно мінімізувати накладні витрати на виділення динамічної пам'яті під час обробки сторінкового збою. Оскільки системний обробник сигналу виконується безпосередньо в контексті того самого потоку процесора, який спричинив виключення, виклик стандартних бібліотечних функцій динамічної пам'яті типу `malloc()` або `free()` усередині обробника може призвести до мертвого взаємного блокування (Deadlock), якщо збій стався під час утримання внутрішнього системного замка купи (heap mutex).

З цієї причини рушій реалізує такі архітектурні рішення:

1. **Пул попередньо виділених двійників (Twin Buffer Pool):** Усі 4096-байтні буфери для збереження тіньових копій виділяються заздалегідь під час ініціалізації середовища через системний виклик `mmap()`, повністю усуваючи будь-яку динамічну алокацію пам'яті в обробнику `SIGSEGV`.
2. **Таблиця дескрипторів сторінок (Page State Table):** Для кожної спільної сторінки підтримується компактна структура, яка зберігає поточний стан доступу (`PAGE_STATE_READ_ONLY`, `PAGE_STATE_DIRTY_TWINNED`, `PAGE_STATE_INVALID`), вказівник на активний буфер двійника та прапорець модифікації.
3. **Компактне кодування серій змін (Run-Length Diff Encoding):** Журнал різниці формується як неперервний потік дескрипторів `(offset, length)` із наступними байтами нових даних. Це дозволяє об'єднувати суміжні змінені байти в один блок і стискати розріджені оновлення до мінімального розміру без надлишкових бітових масок.

## Повний робочий код рушія мовами C та C++

Нижче наведено самодостатню реалізацію рушія Twin-and-Diff, що демонструє повний життєвий цикл сторінки: виділення вирівняного адресного простору, перехоплення першого запису через `sigaction`, нативне виконання користувацького коду в оперативній пам'яті, формування бінарного Diff шляхом пословного сканування та безконфліктне злиття на віддаленій сторінці.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/mman.h>

#define PAGE_SIZE 4096
#define MAX_PAGES 16
#define MAX_DIFF_BYTES 4096

typedef enum {
    PAGE_STATE_INVALID = 0,
    PAGE_STATE_READ_ONLY,
    PAGE_STATE_DIRTY_TWINNED
} PageState;

typedef struct {
    uint16_t offset;
    uint16_t length;
} __attribute__((packed)) DiffChunkHeader;

typedef struct {
    uint8_t *virtual_addr;
    uint8_t *twin_buffer;
    PageState state;
    bool is_dirty;
} PageDescriptor;

typedef struct {
    uint8_t *shared_region;
    size_t num_pages;
    PageDescriptor pages[MAX_PAGES];
    uint8_t twin_pool[MAX_PAGES][PAGE_SIZE];
} DsmEngine;

static DsmEngine g_dsm;

static void dsm_sigsegv_handler(int sig, siginfo_t *info, void *ucontext) {
    (void)sig;
    (void)ucontext;
    uintptr_t fault_addr = (uintptr_t)info->si_addr;
    uintptr_t base_addr = (uintptr_t)g_dsm.shared_region;
    uintptr_t limit_addr = base_addr + (g_dsm.num_pages * PAGE_SIZE);

    if (fault_addr < base_addr || fault_addr >= limit_addr) {
        /* Адреса не належить керованому простору DSM — аварійне завершення */
        const char msg[] = "Fatal: Unhandled SIGSEGV outside DSM region\n";
        write(STDERR_FILENO, msg, sizeof(msg) - 1);
        _exit(EXIT_FAILURE);
    }

    size_t page_idx = (fault_addr - base_addr) / PAGE_SIZE;
    PageDescriptor *desc = &g_dsm.pages[page_idx];

    if (desc->state == PAGE_STATE_READ_ONLY) {
        /* Перший запис у сторінку: створюємо двійник і відкриваємо права */
        memcpy(desc->twin_buffer, desc->virtual_addr, PAGE_SIZE);

        if (mprotect(desc->virtual_addr, PAGE_SIZE, PROT_READ | PROT_WRITE) != 0) {
            const char err[] = "Fatal: mprotect failed in signal handler\n";
            write(STDERR_FILENO, err, sizeof(err) - 1);
            _exit(EXIT_FAILURE);
        }

        desc->state = PAGE_STATE_DIRTY_TWINNED;
        desc->is_dirty = true;
    } else {
        const char unk[] = "Fatal: Unexpected page state on fault\n";
        write(STDERR_FILENO, unk, sizeof(unk) - 1);
        _exit(EXIT_FAILURE);
    }
}

int dsm_engine_init(size_t num_pages) {
    if (num_pages > MAX_PAGES || num_pages == 0) {
        return -1;
    }

    g_dsm.num_pages = num_pages;
    size_t total_bytes = num_pages * PAGE_SIZE;

    /* Виділяємо анонімний вирівняний регіон для спільної пам'яті */
    g_dsm.shared_region = (uint8_t*)mmap(NULL, total_bytes, PROT_READ,
                                         MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (g_dsm.shared_region == MAP_FAILED) {
        return -1;
    }

    /* Налаштовуємо дескриптори сторінок */
    for (size_t i = 0; i < num_pages; i++) {
        g_dsm.pages[i].virtual_addr = g_dsm.shared_region + (i * PAGE_SIZE);
        g_dsm.pages[i].twin_buffer = g_dsm.twin_pool[i];
        g_dsm.pages[i].state = PAGE_STATE_READ_ONLY;
        g_dsm.pages[i].is_dirty = false;
        memset(g_dsm.twin_pool[i], 0, PAGE_SIZE);
    }

    /* Реєструємо обробник сигналу SIGSEGV */
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_sigaction = dsm_sigsegv_handler;
    sa.sa_flags = SA_SIGINFO | SA_NODEFER;
    sigemptyset(&sa.sa_mask);

    if (sigaction(SIGSEGV, &sa, NULL) != 0) {
        munmap(g_dsm.shared_region, total_bytes);
        return -1;
    }

    return 0;
}

size_t dsm_compute_page_diff(size_t page_idx, uint8_t *diff_buffer, size_t max_out) {
    if (page_idx >= g_dsm.num_pages) return 0;
    PageDescriptor *desc = &g_dsm.pages[page_idx];

    if (!desc->is_dirty || desc->state != PAGE_STATE_DIRTY_TWINNED) {
        return 0;
    }

    const uint64_t *page_words = (const uint64_t*)desc->virtual_addr;
    const uint64_t *twin_words = (const uint64_t*)desc->twin_buffer;
    size_t total_words = PAGE_SIZE / sizeof(uint64_t);
    size_t out_pos = 0;
    size_t w = 0;

    while (w < total_words) {
        if (page_words[w] == twin_words[w]) {
            w++;
            continue;
        }

        /* Знаходимо точний перший байт розбіжності */
        size_t start_byte = w * sizeof(uint64_t);
        while (start_byte < PAGE_SIZE && desc->virtual_addr[start_byte] == desc->twin_buffer[start_byte]) {
            start_byte++;
        }

        size_t end_byte = (w + 1) * sizeof(uint64_t);
        if (end_byte > PAGE_SIZE) end_byte = PAGE_SIZE;

        while (end_byte < PAGE_SIZE && desc->virtual_addr[end_byte] != desc->twin_buffer[end_byte]) {
            end_byte++;
        }

        size_t chunk_len = end_byte - start_byte;
        if (out_pos + sizeof(DiffChunkHeader) + chunk_len > max_out) {
            break; /* Переповнення вихідного буфера */
        }

        DiffChunkHeader hdr;
        hdr.offset = (uint16_t)start_byte;
        hdr.length = (uint16_t)chunk_len;

        memcpy(&diff_buffer[out_pos], &hdr, sizeof(DiffChunkHeader));
        out_pos += sizeof(DiffChunkHeader);

        memcpy(&diff_buffer[out_pos], &desc->virtual_addr[start_byte], chunk_len);
        out_pos += chunk_len;

        w = (end_byte / sizeof(uint64_t)) + 1;
    }

    return out_pos;
}

void dsm_apply_diff(uint8_t *target_page, const uint8_t *diff_data, size_t diff_size) {
    size_t in_pos = 0;
    while (in_pos + sizeof(DiffChunkHeader) <= diff_size) {
        DiffChunkHeader hdr;
        memcpy(&hdr, &diff_data[in_pos], sizeof(DiffChunkHeader));
        in_pos += sizeof(DiffChunkHeader);

        if (hdr.offset + hdr.length <= PAGE_SIZE && in_pos + hdr.length <= diff_size) {
            memcpy(target_page + hdr.offset, &diff_data[in_pos], hdr.length);
        }
        in_pos += hdr.length;
    }
}

void dsm_end_epoch_page(size_t page_idx) {
    if (page_idx >= g_dsm.num_pages) return;
    PageDescriptor *desc = &g_dsm.pages[page_idx];

    if (desc->state == PAGE_STATE_DIRTY_TWINNED) {
        /* Скидаємо захист назад до PROT_READ */
        mprotect(desc->virtual_addr, PAGE_SIZE, PROT_READ);
        desc->state = PAGE_STATE_READ_ONLY;
        desc->is_dirty = false;
    }
}

void dsm_engine_destroy(void) {
    if (g_dsm.shared_region && g_dsm.shared_region != MAP_FAILED) {
        munmap(g_dsm.shared_region, g_dsm.num_pages * PAGE_SIZE);
        g_dsm.shared_region = NULL;
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <vector>
#include <memory>
#include <expected>
#include <system_error>
#include <array>
#include <unistd.h>
#include <signal.h>
#include <sys/mman.h>

constexpr size_t PageSize = 4096;
constexpr size_t MaxPages = 16;

enum class PageStatus : uint8_t {
    Invalid,
    ReadOnly,
    DirtyTwinned
};

struct alignas(uint16_t) DiffHeader {
    uint16_t offset{0};
    uint16_t length{0};
};

struct DiffEntry {
    uint16_t offset{0};
    std::vector<std::byte> payload;
};

class DsmMemoryEngine {
public:
    DsmMemoryEngine() = default;
    ~DsmMemoryEngine() {
        if (m_sharedMemory != nullptr && m_sharedMemory != MAP_FAILED) {
            munmap(m_sharedMemory, m_pageCount * PageSize);
        }
    }

    DsmMemoryEngine(const DsmMemoryEngine&) = delete;
    DsmMemoryEngine& operator=(const DsmMemoryEngine&) = delete;

    std::expected<void, std::error_code> initialize(size_t pageCount) {
        if (pageCount == 0 || pageCount > MaxPages) {
            return std::unexpected(std::make_error_code(std::errc::invalid_argument));
        }

        m_pageCount = pageCount;
        const size_t totalBytes = m_pageCount * PageSize;

        void* rawMem = mmap(nullptr, totalBytes, PROT_READ,
                            MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (rawMem == MAP_FAILED) {
            return std::unexpected(std::make_error_code(std::errc::not_enough_memory));
        }

        m_sharedMemory = static_cast<std::byte*>(rawMem);
        s_activeInstance = this;

        struct sigaction sa{};
        sa.sa_sigaction = &DsmMemoryEngine::signalTrampoline;
        sa.sa_flags = SA_SIGINFO | SA_NODEFER;
        sigemptyset(&sa.sa_mask);

        if (sigaction(SIGSEGV, &sa, nullptr) != 0) {
            munmap(m_sharedMemory, totalBytes);
            m_sharedMemory = nullptr;
            return std::unexpected(std::make_error_code(std::errc::permission_denied));
        }

        for (size_t i = 0; i < m_pageCount; ++i) {
            m_status[i] = PageStatus::ReadOnly;
            std::memset(m_twinPool[i].data(), 0, PageSize);
        }

        return {};
    }

    [[nodiscard]] std::span<std::byte> getPage(size_t index) noexcept {
        if (index >= m_pageCount || m_sharedMemory == nullptr) {
            return {};
        }
        return {m_sharedMemory + (index * PageSize), PageSize};
    }

    [[nodiscard]] std::vector<DiffEntry> computeDiff(size_t pageIndex) const {
        if (pageIndex >= m_pageCount || m_status[pageIndex] != PageStatus::DirtyTwinned) {
            return {};
        }

        std::vector<DiffEntry> diffs;
        const auto* pagePtr = reinterpret_cast<const uint64_t*>(m_sharedMemory + (pageIndex * PageSize));
        const auto* twinPtr = reinterpret_cast<const uint64_t*>(m_twinPool[pageIndex].data());
        constexpr size_t wordsPerPage = PageSize / sizeof(uint64_t);

        size_t w = 0;
        while (w < wordsPerPage) {
            if (pagePtr[w] == twinPtr[w]) {
                ++w;
                continue;
            }

            size_t startByte = w * sizeof(uint64_t);
            const auto* pageBytes = m_sharedMemory + (pageIndex * PageSize);
            const auto* twinBytes = m_twinPool[pageIndex].data();

            while (startByte < PageSize && pageBytes[startByte] == twinBytes[startByte]) {
                ++startByte;
            }

            size_t endByte = (w + 1) * sizeof(uint64_t);
            if (endByte > PageSize) endByte = PageSize;

            while (endByte < PageSize && pageBytes[endByte] != twinBytes[endByte]) {
                ++endByte;
            }

            DiffEntry entry;
            entry.offset = static_cast<uint16_t>(startByte);
            size_t len = endByte - startByte;
            entry.payload.resize(len);
            std::memcpy(entry.payload.data(), pageBytes + startByte, len);

            diffs.push_back(std::move(entry));
            w = (endByte / sizeof(uint64_t)) + 1;
        }

        return diffs;
    }

    void resetPageProtection(size_t pageIndex) noexcept {
        if (pageIndex < m_pageCount && m_status[pageIndex] == PageStatus::DirtyTwinned) {
            mprotect(m_sharedMemory + (pageIndex * PageSize), PageSize, PROT_READ);
            m_status[pageIndex] = PageStatus::ReadOnly;
        }
    }

    static void applyDiff(std::span<std::byte, PageSize> targetPage,
                          const std::vector<DiffEntry>& diffs) noexcept {
        for (const auto& entry : diffs) {
            if (entry.offset + entry.payload.size() <= PageSize) {
                std::memcpy(targetPage.data() + entry.offset,
                            entry.payload.data(),
                            entry.payload.size());
            }
        }
    }

private:
    static void signalTrampoline(int sig, siginfo_t* info, void* ctx) noexcept {
        if (s_activeInstance != nullptr) {
            s_activeInstance->handleFault(info->si_addr);
        }
    }

    void handleFault(void* faultAddr) noexcept {
        auto addr = reinterpret_cast<uintptr_t>(faultAddr);
        auto base = reinterpret_cast<uintptr_t>(m_sharedMemory);
        auto limit = base + (m_pageCount * PageSize);

        if (addr < base || addr >= limit) {
            const char msg[] = "SIGSEGV outside DSM bounds\n";
            write(STDERR_FILENO, msg, sizeof(msg) - 1);
            _exit(EXIT_FAILURE);
        }

        size_t pageIdx = (addr - base) / PageSize;
        if (m_status[pageIdx] == PageStatus::ReadOnly) {
            std::memcpy(m_twinPool[pageIdx].data(), m_sharedMemory + (pageIdx * PageSize), PageSize);
            if (mprotect(m_sharedMemory + (pageIdx * PageSize), PageSize, PROT_READ | PROT_WRITE) != 0) {
                const char err[] = "mprotect failed\n";
                write(STDERR_FILENO, err, sizeof(err) - 1);
                _exit(EXIT_FAILURE);
            }
            m_status[pageIdx] = PageStatus::DirtyTwinned;
        }
    }

    std::byte* m_sharedMemory{nullptr};
    size_t m_pageCount{0};
    PageStatus m_status[MaxPages]{};
    alignas(64) std::array<std::array<std::byte, PageSize>, MaxPages> m_twinPool{};
    static inline DsmMemoryEngine* s_activeInstance{nullptr};
};
```
:::

## Покроковий розбір виконання та критичні крайові випадки

Щоб зрозуміти внутрішню динаміку роботи рушія, розглянемо послідовність системних дій від моменту виконання команди запису до завершення епохи синхронізації:

1. **Фаза перехоплення збою (Fault Phase):** Потік процесора виконує інструкцію `movq %rax, (%rdi)`, де регістр `%rdi` містить адресу всередині сторінки зі встановленими правами `PROT_READ`. Блок MMU виявляє спробу запису в область лише для читання та генерує апаратне переривання 14 (#PF). Ядро Linux формує сигнал `SIGSEGV` і викликає функцію `dsm_sigsegv_handler`.
2. **Фаза створення двійника (Twinning Phase):** Обробник визначає індекс сторінки, копіює поточні 4096 байтів чистого стану сторінки у виділений слот `g_dsm.twin_pool[page_idx]`, викликає системний виклик `mprotect(..., PROT_READ | PROT_WRITE)` і переводить стан у `PAGE_STATE_DIRTY_TWINNED`.
3. **Фаза прозорого відновлення (Restart Phase):** Обробник завершує виконання. Ядро ОС повертає лічильник команд (Instruction Pointer) на ту саму інструкцію `movq`. Оскільки права на запис уже відкрито в MMU, процесор успішно виконує запис без повторного виклику сигналу.
4. **Фаза сканування та генерації дельт (Diff Generation Phase):** Під час виклику `dsm_end_epoch_page` функція `dsm_compute_page_diff` порівнює 64-бітні слова масиву `virtual_addr` з масивом `twin_buffer`. Знайдені невідповідності групуються в серії `(offset, length, data)`. Після завершення сканування виклик `mprotect(..., PROT_READ)` блокує подальший неконтрольований запис, повертаючи сторінку в чистий стан для нової епохи.

### Особливості багатопотоковості та взаємного блокування

У багатопотокових програмах кілька потоків одного вузла можуть одночасно спробувати записати в одну й ту саму сторінку `PROT_READ`. Обидва потоки згенерують сигнал `SIGSEGV` практично в один і той самий такт процесора.

Для запобігання стану гонитви при створенні двійника реалізація дескриптора сторінки у промислових системах доповнюється атомарним станом (наприклад, `std::atomic<PageState>`). Перший потік, який успішно переводить стан з `ReadOnly` в проміжний стан `TwinningInProgress` за допомогою інструкції `compare_exchange_strong`, бере на себе обов'язок скопіювати двійник та викликати `mprotect()`. Другий потік чекає завершення операції на атомарному спін-локу і після розблокування сторінки просто виходить із сигналу без повторного копіювання двійника.

### Взаємодія з системними викликами вводу-виводу (Syscall Faults)

Якщо програма передає вказівник на сторінку `PROT_READ` як цільовий буфер системного виклику запису з сокета або файлу (наприклад, `read(sockfd, shared_page_ptr, 128)`), ядро операційної системи намагається записати байти з контексту ядра. Оскільки сторінка захищена від запису, ядро не надсилає сигнал `SIGSEGV` процесу, а негайно повертає код помилки `-1` зі встановленням змінної `errno = EFAULT`.

Для коректної роботи з системними викликами середовище DSM вимагає або використання користувацьких обгорток вводу-виводу, які виконують попередній тестовий запис одного байта `*(volatile char*)shared_page_ptr = *(volatile char*)shared_page_ptr;` перед викликом `read()`, або явного переведення цільових сторінок у стан `PAGE_STATE_DIRTY_TWINNED`.

### Вплив процесорного кешування та вирівнювання ліній кешу

Під час створення двійника та сканування відмінностей критичну роль відіграє поведінка ієрархії кеш-пам'яті процесора (L1/L2/L3). Операція `memcpy(twin, page, 4096)` завантажує всі 4 КБ сторінки в кеш даних першого рівня (L1D), витісняючи корисні робочі дані програми.

Щоб зменшити кешове забруднення (Cache Pollution), у високоефективних рушіях копіювання двійника здійснюють за допомогою векторних незберігаючих інструкцій прямого запису (Non-Temporal Streaming Stores, як-от `_mm256_stream_si256`), які записують байти безпосередньо в оперативну пам'ять DRAM, оминаючи кеші процесора. Крім того, вирівнювання базових адрес робочих сторінок та буферів двійників за межами 64 байтів гарантує максимальну пропускну здатність шини контролера пам'яті під час пословного 64-бітного порівняння.
