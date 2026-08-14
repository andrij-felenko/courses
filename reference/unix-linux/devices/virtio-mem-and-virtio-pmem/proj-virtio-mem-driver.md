# ⚙️ Реалізація керування блоками пам'яті virtio-mem та обробки флаш-запитів virtio-pmem

У цьому практичному проєкті розробляється демо-модель підсистеми керування блоками динамічної пам'яті `virtio-mem` та обробки примусових скидань кешу (flush) для `virtio-pmem`. Наведено порівняльні ідіоматичні реалізації мовами C та C++ з детальним розбором алгоритмів, структур даних, синхронізації та обробки крайових випадків.

---

## Архітектура та алгоритм керування суб-блоками пам'яті

Драйвер `virtio-mem` підтримує внутрішній стан зарезервованого вікна адрес (Guest Physical Address, GPA) у вигляді масиву або бітової карти (bitmap) станів суб-блоків. Коли гіпервізор змінює параметр `requested_size`, обробник драйвера обчислює різницю між поточним обсягом `plugged_size` та бажаним `requested_size`.

### Послідовність дій при розширенні пам'яті (Plug Operation)

Коли господар надсилає запит на збільшення пам'яті (`requested_size > plugged_size`), драйвер гостя запускає процес виділення ресурсів:

1. **Сканування бітової карти:** Драйвер проходить масив суб-блоків від початку регіону адресації до кінця в пошуках елементів у стані `BLOCK_STATE_UNPLUGGED`.
2. **Формування запиту virtqueue:** Для кожного вільного суб-обсягу драйвер заповнює структуру `struct virtio_mem_req` з типом `VIRTIO_MEM_REQ_PLUG`, вказуючи початкову адресу GPA та кількість суб-блоків.
3. **Очікування відповіді хоста:** Драйвер додає буфер у доступне кільце (avail ring), робить «кік» у регістр сповіщення PCI/MMIO і очікує переривання.
4. **Інтеграція з підсистемою пам'яті ядра:** Після отримання підтвердження `VIRTIO_MEM_RESP_ACK` від QEMU, драйвер викликає внутрішні функції ядра Linux `add_memory_driver_managed()` та `online_pages()`. Це реєструє нові фізичні кадри в Buddy Allocator (переважно в зоні `ZONE_MOVABLE`).
5. **Оновлення стану:** Драйвер переводить стан блоку в `BLOCK_STATE_PLUGGED` та збільшує лічильник `plugged_size`.

### Послідовність дій при вилученні пам'яті (Flexible Unplug Operation)

Коли господар вимагає зменшення пам'яті (`requested_size < plugged_size`), драйвер запускає алгоритм гнучкого вилучення:

1. **Реверсивне сканування:** Драйвер сканує суб-блоки від кінця адресної зони до початку. Це оптимізує неперервність залишкової пам'яті.
2. **Ізоляція сторінок ядра:** Для кожного підключеного блоку драйвер кличе `alloc_contig_range()` або `offline_pages()`. Ядро намагається перемістити анонімні сторінки та кеш сторінок диска в інші зони пам'яті за допомогою `migrate_pages()`.
3. **Обробка непереміщуваних сторінок (Unmovable Pages):** Якщо всередині суб-блоку виявлено сторінку ядра, виділену без прапорця `__GFP_MOVABLE` (наприклад, DMA-буфер мережевої карти або таблицю сторінок PTE), спроба ізоляції повертає помилку `-EBUSY`. Драйвер позначає цей суб-блок як `BLOCK_STATE_UNMOVABLE`, **пропускає його** і продовжує аналіз сусідніх суб-блоків.
4. **Повернення фізичних сторінок хосту:** Для всіх успішно вивільнених суб-блоків драйвер надсилає запит `VIRTIO_MEM_REQ_UNPLUG` у віртчергу, змінює стан на `BLOCK_STATE_UNPLUGGED` і зменшує `plugged_size`. Гіпервізор повертає фізичні кадри хосту через `madvise(MADV_DONTNEED)`.

Нижче наведено робочі моделі цієї логіки двома мовами.

:::tabs
```c
/* virtio_mem_mgr.c — Ідіоматична реалізація мовою C (стандарт C11) */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define SUBBLOCK_SIZE_BYTES (2 * 1024 * 1024ULL) /* 2 МБ суб-блок */
#define MAX_SUBBLOCKS 64                       /* Вікно 128 МБ */

typedef enum {
    BLOCK_STATE_UNPLUGGED = 0,
    BLOCK_STATE_PLUGGED   = 1,
    BLOCK_STATE_UNMOVABLE = 2
} block_state_t;

typedef struct {
    uint64_t gpa_start;
    uint64_t requested_size;
    uint64_t plugged_size;
    uint32_t block_count;
    block_state_t blocks[MAX_SUBBLOCKS];
} virtio_mem_device_t;

void virtio_mem_init(virtio_mem_device_t *dev, uint64_t base_gpa, uint32_t count) {
    if (!dev || count > MAX_SUBBLOCKS) return;
    dev->gpa_start = base_gpa;
    dev->requested_size = 0;
    dev->plugged_size = 0;
    dev->block_count = count;
    for (uint32_t i = 0; i < count; i++) {
        dev->blocks[i] = BLOCK_STATE_UNPLUGGED;
    }
}

/* Симуляція підключення суб-блоків */
int virtio_mem_plug_blocks(virtio_mem_device_t *dev, uint64_t target_bytes) {
    if (!dev) return -1;
    uint32_t plugged_now = 0;

    for (uint32_t i = 0; i < dev->block_count; i++) {
        if (dev->plugged_size >= target_bytes) break;

        if (dev->blocks[i] == BLOCK_STATE_UNPLUGGED) {
            /* Симуляція надсилання VIRTIO_MEM_REQ_PLUG хосту */
            dev->blocks[i] = BLOCK_STATE_PLUGGED;
            dev->plugged_size += SUBBLOCK_SIZE_BYTES;
            plugged_now++;
            printf("[virtio-mem C] Блок #%u (GPA: 0x%lx) -> PLUGGED\n",
                   i, dev->gpa_start + (i * SUBBLOCK_SIZE_BYTES));
        }
    }
    return (int)plugged_now;
}

/* Симуляція гнучкого вилучення суб-блоків (flexible unplug) */
int virtio_mem_unplug_blocks(virtio_mem_device_t *dev, uint64_t target_bytes) {
    if (!dev) return -1;
    uint32_t unplugged_now = 0;

    /* Скануємо з кінця для оптимізації неперервності */
    for (int32_t i = (int32_t)dev->block_count - 1; i >= 0; i--) {
        if (dev->plugged_size <= target_bytes) break;

        if (dev->blocks[(uint32_t)i] == BLOCK_STATE_PLUGGED) {
            /* Симуляція спроби offline_pages() */
            dev->blocks[(uint32_t)i] = BLOCK_STATE_UNPLUGGED;
            dev->plugged_size -= SUBBLOCK_SIZE_BYTES;
            unplugged_now++;
            printf("[virtio-mem C] Блок #%d (GPA: 0x%lx) -> UNPLUGGED\n",
                   i, dev->gpa_start + ((uint32_t)i * SUBBLOCK_SIZE_BYTES));
        } else if (dev->blocks[(uint32_t)i] == BLOCK_STATE_UNMOVABLE) {
            printf("[virtio-mem C] Блок #%d містить unmovable pages -> Пропущено\n", i);
        }
    }
    return (int)unplugged_now;
}

int main(void) {
    virtio_mem_device_t dev;
    virtio_mem_init(&dev, 0x100000000ULL, 16); /* 32 МБ вікно з 0x100000000 */

    printf("--- Запит на підключення 16 МБ ---\n");
    virtio_mem_plug_blocks(&dev, 16 * 1024 * 1024ULL);

    /* Імітуємо, що блок #3 зайнятий непереміщуваними даними ядра */
    dev.blocks[3] = BLOCK_STATE_UNMOVABLE;

    printf("\n--- Запит на зменшення до 4 МБ (Unplug 12 МБ) ---\n");
    virtio_mem_unplug_blocks(&dev, 4 * 1024 * 1024ULL);

    printf("\nПідсумковий plugged_size: %lu МБ\n", dev.plugged_size / (1024 * 1024));
    return 0;
}
```
```cpp
// virtio_mem_mgr.cpp — Ідіоматична реалізація мовою C++ (C++20)
#include <iostream>
#include <vector>
#include <cstdint>
#include <optional>
#include <expected>
#include <format>
#include <span>

constexpr uint64_t kSubblockSize = 2 * 1024 * 1024ULL; // 2 МБ

enum class BlockState : uint8_t {
    Unplugged,
    Plugged,
    Unmovable
};

struct MemBlock {
    uint64_t gpa;
    BlockState state{BlockState::Unplugged};
};

class VirtioMemDevice {
public:
    explicit VirtioMemDevice(uint64_t base_gpa, size_t block_count)
        : base_gpa_(base_gpa) {
        blocks_.reserve(block_count);
        for (size_t i = 0; i < block_count; ++i) {
            blocks_.push_back(MemBlock{base_gpa + (i * kSubblockSize), BlockState::Unplugged});
        }
    }

    // Регулювання розміру пам'яті (RAII та безпечна обробка помилок)
    size_t adjust_size(uint64_t target_bytes) {
        if (target_bytes > plugged_size_) {
            return plug_until(target_bytes);
        } else if (target_bytes < plugged_size_) {
            return unplug_until(target_bytes);
        }
        return 0;
    }

    void mark_unmovable(size_t index) {
        if (index < blocks_.size()) {
            blocks_[index].state = BlockState::Unmovable;
        }
    }

    [[nodiscard]] uint64_t plugged_size() const noexcept { return plugged_size_; }
    [[nodiscard]] std::span<const MemBlock> blocks() const noexcept { return blocks_; }

private:
    size_t plug_until(uint64_t target_bytes) {
        size_t count = 0;
        for (auto& block : blocks_) {
            if (plugged_size_ >= target_bytes) break;
            if (block.state == BlockState::Unplugged) {
                block.state = BlockState::Plugged;
                plugged_size_ += kSubblockSize;
                ++count;
                std::cout << std::format("[virtio-mem C++] GPA 0x{:x} -> PLUGGED\n", block.gpa);
            }
        }
        return count;
    }

    size_t unplug_until(uint64_t target_bytes) {
        size_t count = 0;
        for (auto it = blocks_.rbegin(); it != blocks_.rend(); ++it) {
            if (plugged_size_ <= target_bytes) break;
            if (it->state == BlockState::Plugged) {
                it->state = BlockState::Unplugged;
                plugged_size_ -= kSubblockSize;
                ++count;
                std::cout << std::format("[virtio-mem C++] GPA 0x{:x} -> UNPLUGGED\n", it->gpa);
            } else if (it->state == BlockState::Unmovable) {
                std::cout << std::format("[virtio-mem C++] GPA 0x{:x} UNMOVABLE, skipping\n", it->gpa);
            }
        }
        return count;
    }

    uint64_t base_gpa_;
    uint64_t plugged_size_{0};
    std::vector<MemBlock> blocks_;
};

int main() {
    VirtioMemDevice dev(0x100000000ULL, 16);

    std::cout << "--- C++: Запит на 16 МБ ---\n";
    dev.adjust_size(16 * 1024 * 1024ULL);

    dev.mark_unmovable(3);

    std::cout << "\n--- C++: Зменшення до 4 МБ ---\n";
    dev.adjust_size(4 * 1024 * 1024ULL);

    std::cout << std::format("\nC++ Plugged size: {} МБ\n", dev.plugged_size() / (1024 * 1024));
    return 0;
}
```
:::

---

## Детальний розбір реалізацій та порівняльний аналіз

Кожна мова демонструє свій підхід до виділення ресурсів, безпеки типів та обробки помилок у низькорівневих драйверах.

### 1. Керування пам'яттю та динамічне виділення
* **C-версія:** Використовує стасуваний або статично зарезервований масив станів усередині структури `virtio_mem_device_t`. Це підхід, ідентичний реальному коду ядра Linux `drivers/virtio/virtio_mem.c`. Динамічне виділення пам'яті через `kmalloc` усередині обробника переривань є небажаним, тому стан заздалегідь розраховується на весь `region_size`.
* **C++20 версія:** Застосовує `std::vector<MemBlock>` з попереднім резервуванням пам'яті `reserve()`. Об'єкт гарантує RAII-збереження ресурсів: при знищенні екземпляра `VirtioMemDevice` вектор автоматично вивільняє пам'ять без ризику витоків.

### 2. Ітератори та алгоритми сканування
* **C-версія:** Ітерація при вилученні виконується через зворотний цикл зі знаковим лічильником `int32_t i = block_count - 1`. Це вимагає обережності при приведенні типів до `uint32_t`, щоб уникнути від'ємного зсуву масиву.
* **C++20 версія:** Використовує безпечні реверсивні ітератори `blocks_.rbegin()` та `blocks_.rend()`. Це робить намір коду «сканувати з кінця» виразним та унеможливлює помилки виходу за межі масиву (out-of-bounds).

### 3. Строгість типів та форматування
* **C-версія:** Тип `block_state_t` є звичайним enum, який може неявно приводитися до цілих чисел `int`. Вивід повідомлень виконується через `printf` із макросами форматування специфікаторів адрес `0x%lx`.
* **C++20 версія:** Використовує `enum class BlockState : uint8_t`, що забезпечує повну ізоляцію типів. Для форматування застосовано бібліотеку `std::format` із типами `0x{:x}`, що є безпечнішим за варіативні аргументи `printf`.

---

## Модуль обробки флаш-запитів virtio-pmem

У пристроях перзистентної пам'яті `virtio-pmem` операції читання та запису проходять через прямо відображені сторінки BAR (DAX). Проте операції забезпечення стійкості (durability) надсилаються через віртчергу. Обробник хоста (QEMU) повинен викликати системний виклик `fdatasync()` для примусового збереження даних на фізичному диску.

:::tabs
```c
/* virtio_pmem_flush.c — Обробник флаш-запитів мовою C */
#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>

#define VIRTIO_PMEM_REQ_TYPE_FLUSH 0

struct virtio_pmem_req {
    uint32_t type;
};

struct virtio_pmem_resp {
    int32_t status;
};

int handle_virtio_pmem_request(int backend_fd, const struct virtio_pmem_req *req, struct virtio_pmem_resp *resp) {
    if (!req || !resp || backend_fd < 0) return -1;

    if (req->type == VIRTIO_PMEM_REQ_TYPE_FLUSH) {
        /* Примусовий виклик fdatasync для гарантії запису на флеш/диск хоста */
        if (fdatasync(backend_fd) == 0) {
            resp->status = 0; /* Успіх */
            printf("[virtio-pmem host C] fdatasync успішно виконано\n");
        } else {
            resp->status = -errno; /* Збереження коду помилки I/O */
            perror("[virtio-pmem host C] fdatasync error");
        }
    } else {
        resp->status = -EINVAL; /* Невідома команда */
    }
    return 0;
}
```
```cpp
// virtio_pmem_flush.cpp — Обробник флаш-запитів мовою C++ (RAII + expected)
#include <iostream>
#include <cstdint>
#include <expected>
#include <system_error>
#include <unistd.h>

enum class PmemReqType : uint32_t {
    Flush = 0
};

struct PmemReq {
    PmemReqType type;
};

struct PmemResp {
    int32_t status{0};
};

class HostBackendFile {
public:
    explicit HostBackendFile(int fd) noexcept : fd_(fd) {}

    [[nodiscard]] std::expected<void, std::error_code> sync_data() const noexcept {
        if (fd_ < 0) {
            return std::unexpected(std::make_error_code(std::errc::bad_file_descriptor));
        }
        if (::fdatasync(fd_) != 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }

private:
    int fd_{-1};
};

PmemResp process_pmem_request(const HostBackendFile& backend, const PmemReq& req) {
    PmemResp resp;
    if (req.type == PmemReqType::Flush) {
        auto result = backend.sync_data();
        if (result) {
            resp.status = 0;
            std::cout << "[virtio-pmem C++ host] DAX Sync OK\n";
        } else {
            resp.status = -result.error().value();
            std::cerr << "[virtio-pmem C++ host] Sync Error: " << result.error().message() << "\n";
        }
    } else {
        resp.status = -EINVAL;
    }
    return resp;
}
```
:::

---

## Обробка крайніх випадків та системні ризики

При розробці системних обробників пам'яті у віртуалізації необхідно враховувати набір крайових ситуацій:

1. **Сигнали та переривання виклику `fdatasync()`:** Системний виклик `fdatasync()` на боці хоста може бути перерваний сигналом (помилка `EINTR`). Драйвер або процес хоста зобов'язаний виконувати повторний виклик у циклі `do { res = fdatasync(fd); } while (res == -1 && errno == EINTR);`.
2. **Аварійний стан файлової системи хоста (`EIO` / `EROFS`):** У разі збою фізичного накопичувача хоста файлова система переходить у стан read-only. Помилка виклику `fdatasync()` транслюється у `resp.status = -EIO`. Драйвер `virtio_pmem.ko` повинен передати цю помилку підсистемі VFS гостя, щоб програма отримала сповіщення про неможливість гарантувати перзистентність.
3. **Групування запитів (Flush Coalescing):** Якщо десятки потоків гостя одночасно викликають `fsync()`, відправлення десятків окремих команд `VIRTIO_PMEM_REQ_TYPE_FLUSH` може перевантажити віртчергу. Драйвер гостя або бекенд QEMU реалізують об'єднання запитів: якщо один `fdatasync()` виконується в момент надходження нових команд, їх можна завершити одним спільним викликом синхронізації.
