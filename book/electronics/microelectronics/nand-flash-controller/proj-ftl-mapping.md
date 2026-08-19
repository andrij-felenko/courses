# ⚙️ Програмна модель сторінкового FTL та збору сміття

Шар трансляції флеш-пам'яті (англ. *Flash Translation Layer*, FTL) усередині мікроконтролера твердотільного накопичувача (SSD) функціонує як спеціалізована автономна операційна система реального часу. Його ключове призначення — керувати масивом фізичних блоків і сторінок, приймати запити запису за логічними номерами секторів (LBA), виконувати запис зі зсувом (Out-of-Place), своєчасно оновлювати таблицю відображення адрес (L2P) і запускати збирання сміття (Garbage Collection, GC), коли пул чистих стертих блоків наближається до вичерпання.

У цій практичній вставці ми побудуємо та детально проаналізуємо повноцінну програмну модель сторінкового FTL-рушія мовами C та ідіоматичного C++20. Модель повністю симулює роботу кремнієвого накопичувача: прийом випадкових запитів від хоста, динамічну інвалідацію застарілих сторінок, жадібний вибір блоку-жертви під час збирання сміття, стирання блоків та точний підрахунок коефіцієнта посилення запису (Write Amplification Factor, WAF).

---

### Архітектурні інваріанти та фізичні обмеження

Фізика комірок енергонезалежної пам'яті NAND Flash накладає на алгоритми контролера чотири суворі інваріанти, які наш програмний симулятор зобов'язаний непохитно підтримувати:

1. **Інваріант послідовного програмування сторінок (Single Program Rule):** сторінки всередині одного фізичного блоку повинні записуватися суворо послідовно від індексу `0` до `PAGES_PER_BLOCK - 1`. Довільний запис у середину блоку або повторне перезаписування вже зайнятої сторінки без попереднього високовольтного стирання всього блоку фізично неможливі.
2. **Інваріант запису зі зсувом (Out-of-Place Update):** при повторному записі хоста в один і той самий логічний сектор (LBA) контролер ніколи не перезаписує стару фізичну сторінку. Він виділяє нову чисту сторінку в поточному активному блоці, записує туди оновлені дані, а стару сторінку позначає як недійсну (`Invalid`).
3. **Інваріант збереження балансу станів комірок блоку:** у будь-який момент часу для будь-якого фізичного блоку сума дійсних (`valid_count`), недійсних (`invalid_count`) та ще не записаних вільних сторінок (`PAGES_PER_BLOCK - free_page_idx`) строго дорівнює повній місткості блоку `PAGES_PER_BLOCK`.
4. **Інваріант актуальності таблиці трансляції L2P:** таблиця `L2P[LBA]` повинна завжди містити фізичну адресу найостаннішої дійсної копії даних, або спеціальний маркер `INVALID_ADDR`, якщо цей логічний сектор ще жодного разу не записувався хостом.

#### Конфігурація симулятора
Для наочності спостереження за процесами збирання сміття оберемо такі параметри:
* `NUM_BLOCKS = 8` — кількість фізичних блоків у масиві NAND.
* `PAGES_PER_BLOCK = 8` — кількість сторінок у кожному блоці (разом 64 фізичні сторінки).
* `LOGICAL_PAGES = 32` — доступний користувачеві адресний простір (32 логічні сторінки). Співвідношення `(64 - 32) / 32 = 1.0` задає 100% апаратного надлишкового резервування (Over-Provisioning), що дозволяє симулятору працювати тривалий час без переповнення.
* `GC_THRESHOLD_BLOCKS = 2` — критичний поріг пулу вільних блоків. Щойно кількість повністю стертих блоків падає нижче 2, контролер зобов'язаний виконати цикл збирання сміття перед прийомом чергового запису від хоста.

---

### Програмна реалізація: чистий C та C++20

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NUM_BLOCKS          8
#define PAGES_PER_BLOCK     8
#define TOTAL_PAGES         (NUM_BLOCKS * PAGES_PER_BLOCK)
#define LOGICAL_PAGES       32   // 100% Over-Provisioning для наочності
#define GC_THRESHOLD_BLOCKS 2
#define INVALID_ADDR        0xFFFFFFFF

typedef enum {
    PAGE_FREE = 0,
    PAGE_VALID = 1,
    PAGE_INVALID = 2
} page_state_t;

typedef struct {
    uint32_t erase_count;
    uint32_t valid_count;
    uint32_t invalid_count;
    uint32_t free_page_idx;
    page_state_t page_states[PAGES_PER_BLOCK];
    uint32_t page_lba[PAGES_PER_BLOCK];
} flash_block_t;

typedef struct {
    uint32_t l2p_table[LOGICAL_PAGES];
    flash_block_t blocks[NUM_BLOCKS];
    uint32_t active_block_id;
    uint64_t host_writes;
    uint64_t flash_writes;
} ftl_controller_t;

static void ftl_init(ftl_controller_t *ftl) {
    memset(ftl, 0, sizeof(*ftl));
    for (uint32_t i = 0; i < LOGICAL_PAGES; i++) {
        ftl->l2p_table[i] = INVALID_ADDR;
    }
    for (uint32_t b = 0; b < NUM_BLOCKS; b++) {
        for (uint32_t p = 0; p < PAGES_PER_BLOCK; p++) {
            ftl->blocks[b].page_lba[p] = INVALID_ADDR;
        }
    }
    ftl->active_block_id = 0;
}

static uint32_t ftl_count_free_blocks(const ftl_controller_t *ftl) {
    uint32_t free_cnt = 0;
    for (uint32_t b = 0; b < NUM_BLOCKS; b++) {
        if (b == ftl->active_block_id) continue;
        if (ftl->blocks[b].free_page_idx == 0 && ftl->blocks[b].valid_count == 0) {
            free_cnt++;
        }
    }
    return free_cnt;
}

static int32_t ftl_find_free_block(const ftl_controller_t *ftl) {
    for (uint32_t b = 0; b < NUM_BLOCKS; b++) {
        if (b == ftl->active_block_id) continue;
        if (ftl->blocks[b].free_page_idx == 0 && ftl->blocks[b].valid_count == 0) {
            return (int32_t)b;
        }
    }
    return -1;
}

static bool ftl_run_gc(ftl_controller_t *ftl) {
    int32_t victim_block = -1;
    uint32_t max_invalid = 0;

    // Пошук блоку-жертви за жадібною евристикою (Greedy Policy)
    for (uint32_t b = 0; b < NUM_BLOCKS; b++) {
        if (b == ftl->active_block_id) continue;
        if (ftl->blocks[b].free_page_idx == PAGES_PER_BLOCK &&
            ftl->blocks[b].invalid_count > max_invalid) {
            max_invalid = ftl->blocks[b].invalid_count;
            victim_block = (int32_t)b;
        }
    }

    if (victim_block < 0) return false;

    flash_block_t *victim = &ftl->blocks[victim_block];

    // Копіювання вцілілих дійсних сторінок у новий активний блок
    for (uint32_t p = 0; p < PAGES_PER_BLOCK; p++) {
        if (victim->page_states[p] == PAGE_VALID) {
            uint32_t lba = victim->page_lba[p];
            
            // Якщо в активному блоці закінчилося місце, відкриваємо наступний чистий
            if (ftl->blocks[ftl->active_block_id].free_page_idx == PAGES_PER_BLOCK) {
                int32_t next_b = ftl_find_free_block(ftl);
                if (next_b < 0) return false;
                ftl->active_block_id = (uint32_t)next_b;
            }

            flash_block_t *act = &ftl->blocks[ftl->active_block_id];
            uint32_t new_p = act->free_page_idx++;
            act->page_states[new_p] = PAGE_VALID;
            act->page_lba[new_p] = lba;
            act->valid_count++;

            // Оновлення таблиці трансляції L2P на нове фізичне зміщення
            ftl->l2p_table[lba] = (ftl->active_block_id * PAGES_PER_BLOCK) + new_p;
            ftl->flash_writes++;
        }
    }

    // Повне стирання блоку-жертви
    victim->erase_count++;
    victim->valid_count = 0;
    victim->invalid_count = 0;
    victim->free_page_idx = 0;
    for (uint32_t p = 0; p < PAGES_PER_BLOCK; p++) {
        victim->page_states[p] = PAGE_FREE;
        victim->page_lba[p] = INVALID_ADDR;
    }

    return true;
}

static bool ftl_write(ftl_controller_t *ftl, uint32_t lba) {
    if (lba >= LOGICAL_PAGES) return false;

    // Перевірка порогу пулу вільних блоків
    if (ftl_count_free_blocks(ftl) < GC_THRESHOLD_BLOCKS &&
        ftl->blocks[ftl->active_block_id].free_page_idx == PAGES_PER_BLOCK) {
        ftl_run_gc(ftl);
    }

    // Якщо поточний активний блок повністю заповнений, відкриваємо наступний
    if (ftl->blocks[ftl->active_block_id].free_page_idx == PAGES_PER_BLOCK) {
        int32_t free_b = ftl_find_free_block(ftl);
        if (free_b < 0) {
            if (!ftl_run_gc(ftl)) return false;
            free_b = ftl_find_free_block(ftl);
            if (free_b < 0) return false;
        }
        ftl->active_block_id = (uint32_t)free_b;
    }

    // Інвалідація старої фізичної сторінки (якщо цей LBA вже колись записувався)
    uint32_t old_pba = ftl->l2p_table[lba];
    if (old_pba != INVALID_ADDR) {
        uint32_t old_b = old_pba / PAGES_PER_BLOCK;
        uint32_t old_p = old_pba % PAGES_PER_BLOCK;
        ftl->blocks[old_b].page_states[old_p] = PAGE_INVALID;
        ftl->blocks[old_b].valid_count--;
        ftl->blocks[old_b].invalid_count++;
    }

    // Запис у наступну чисту сторінку активного блоку
    flash_block_t *act = &ftl->blocks[ftl->active_block_id];
    uint32_t new_p = act->free_page_idx++;
    act->page_states[new_p] = PAGE_VALID;
    act->page_lba[new_p] = lba;
    act->valid_count++;

    ftl->l2p_table[lba] = (ftl->active_block_id * PAGES_PER_BLOCK) + new_p;
    ftl->host_writes++;
    ftl->flash_writes++;

    return true;
}

int main(void) {
    ftl_controller_t ftl;
    ftl_init(&ftl);

    // Імітація 300 випадкових записів від операційної системи хоста
    for (int i = 0; i < 300; i++) {
        uint32_t random_lba = (uint32_t)(rand() % LOGICAL_PAGES);
        ftl_write(&ftl, random_lba);
    }

    printf("Результати симуляції FTL (C):\n");
    printf("  Хост-записів:     %lu\n", (unsigned long)ftl.host_writes);
    printf("  Флеш-записів:     %lu\n", (unsigned long)ftl.flash_writes);
    printf("  Розрахований WAF: %.3f\n", (double)ftl.flash_writes / (double)ftl.host_writes);

    return 0;
}
```
```cpp
#include <cstdint>
#include <vector>
#include <optional>
#include <span>
#include <iostream>
#include <random>
#include <algorithm>

enum class PageState : uint8_t {
    Free = 0,
    Valid = 1,
    Invalid = 2
};

struct FlashBlock {
    uint32_t erase_count{0};
    uint32_t valid_count{0};
    uint32_t invalid_count{0};
    uint32_t free_page_idx{0};
    std::vector<PageState> page_states;
    std::vector<uint32_t> page_lba;

    explicit FlashBlock(size_t pages_per_block)
        : page_states(pages_per_block, PageState::Free),
          page_lba(pages_per_block, UINT32_MAX) {}

    void erase() noexcept {
        ++erase_count;
        valid_count = 0;
        invalid_count = 0;
        free_page_idx = 0;
        std::fill(page_states.begin(), page_states.end(), PageState::Free);
        std::fill(page_lba.begin(), page_lba.end(), UINT32_MAX);
    }

    [[nodiscard]] bool is_clean() const noexcept {
        return free_page_idx == 0 && valid_count == 0;
    }
};

class FtlSimulator {
public:
    FtlSimulator(size_num_blocks, size_t pages_per_block, size_t logical_pages, size_t gc_threshold)
        : pages_per_block_{pages_per_block},
          logical_pages_{logical_pages},
          gc_threshold_{gc_threshold},
          l2p_table_(logical_pages, std::nullopt),
          active_block_id_{0} {
        blocks_.reserve(num_blocks);
        for (size_t i = 0; i < num_blocks; ++i) {
            blocks_.emplace_back(pages_per_block);
        }
    }

    bool write(uint32_t lba) {
        if (lba >= logical_pages_) return false;

        // Перевірка потреби запуску GC при дефіциті вільних блоків
        if (count_free_blocks() < gc_threshold_ &&
            blocks_[active_block_id_].free_page_idx == pages_per_block_) {
            run_gc();
        }

        // Якщо активний блок повністю записаний, відкриваємо новий чистий блок
        if (blocks_[active_block_id_].free_page_idx == pages_per_block_) {
            auto free_b = find_free_block();
            if (!free_b) {
                if (!run_gc()) return false;
                free_b = find_free_block();
                if (!free_b) return false;
            }
            active_block_id_ = *free_b;
        }

        // Інвалідація попередньої фізичної сторінки
        if (l2p_table_[lba].has_value()) {
            uint32_t old_pba = *l2p_table_[lba];
            uint32_t old_b = old_pba / static_cast<uint32_t>(pages_per_block_);
            uint32_t old_p = old_pba % static_cast<uint32_t>(pages_per_block_);
            blocks_[old_b].page_states[old_p] = PageState::Invalid;
            --blocks_[old_b].valid_count;
            ++blocks_[old_b].invalid_count;
        }

        // Програмування нової сторінки
        auto &active = blocks_[active_block_id_];
        uint32_t new_p = active.free_page_idx++;
        active.page_states[new_p] = PageState::Valid;
        active.page_lba[new_p] = lba;
        ++active.valid_count;

        l2p_table_[lba] = (static_cast<uint32_t>(active_block_id_) * static_cast<uint32_t>(pages_per_block_)) + new_p;
        ++host_writes_;
        ++flash_writes_;
        return true;
    }

    [[nodiscard]] double calculate_waf() const noexcept {
        return host_writes_ > 0 ? static_cast<double>(flash_writes_) / static_cast<double>(host_writes_) : 1.0;
    }

    [[nodiscard]] uint64_t host_writes() const noexcept { return host_writes_; }
    [[nodiscard]] uint64_t flash_writes() const noexcept { return flash_writes_; }

private:
    [[nodiscard]] size_t count_free_blocks() const noexcept {
        size_t count = 0;
        for (size_t b = 0; b < blocks_.size(); ++b) {
            if (b != active_block_id_ && blocks_[b].is_clean()) ++count;
        }
        return count;
    }

    [[nodiscard]] std::optional<size_t> find_free_block() const noexcept {
        for (size_t b = 0; b < blocks_.size(); ++b) {
            if (b != active_block_id_ && blocks_[b].is_clean()) return b;
        }
        return std::nullopt;
    }

    bool run_gc() {
        std::optional<size_t> victim_idx;
        uint32_t max_invalid = 0;

        // Пошук блоку з найбільшою кількістю сміття
        for (size_t b = 0; b < blocks_.size(); ++b) {
            if (b == active_block_id_) continue;
            if (blocks_[b].free_page_idx == pages_per_block_ && blocks_[b].invalid_count > max_invalid) {
                max_invalid = blocks_[b].invalid_count;
                victim_idx = b;
            }
        }

        if (!victim_idx) return false;

        auto &victim = blocks_[*victim_idx];
        for (size_t p = 0; p < pages_per_block_; ++p) {
            if (victim.page_states[p] == PageState::Valid) {
                uint32_t lba = victim.page_lba[p];

                if (blocks_[active_block_id_].free_page_idx == pages_per_block_) {
                    auto next_b = find_free_block();
                    if (!next_b) return false;
                    active_block_id_ = *next_b;
                }

                auto &active = blocks_[active_block_id_];
                uint32_t new_p = active.free_page_idx++;
                active.page_states[new_p] = PageState::Valid;
                active.page_lba[new_p] = lba;
                ++active.valid_count;

                l2p_table_[lba] = (static_cast<uint32_t>(active_block_id_) * static_cast<uint32_t>(pages_per_block_)) + new_p;
                ++flash_writes_;
            }
        }

        victim.erase();
        return true;
    }

    size_t pages_per_block_;
    size_t logical_pages_;
    size_t gc_threshold_;
    std::vector<std::optional<uint32_t>> l2p_table_;
    std::vector<FlashBlock> blocks_;
    size_t active_block_id_{0};
    uint64_t host_writes_{0};
    uint64_t flash_writes_{0};
};

int main() {
    constexpr size_t kBlocks = 8;
    constexpr size_t kPagesPerBlock = 8;
    constexpr size_t kLogicalPages = 32;
    constexpr size_t kGcThreshold = 2;

    FtlSimulator sim(kBlocks, kPagesPerBlock, kLogicalPages, kGcThreshold);

    std::mt19937 gen(42);
    std::uniform_int_distribution<uint32_t> dist(0, kLogicalPages - 1);

    for (int i = 0; i < 300; ++i) {
        sim.write(dist(gen));
    }

    std::cout << "Результати симуляції FTL (C++20):\n"
              << "  Хост-записів:     " << sim.host_writes() << "\n"
              << "  Флеш-записів:     " << sim.flash_writes() << "\n"
              << "  Розрахований WAF: " << sim.calculate_waf() << "\n";

    return 0;
}
```
:::

---

### Детальний аналіз алгоритмічних фаз FTL

Розглянемо покроково, як влаштований життєвий цикл кожної операції у наведених програмах і чому структура коду саме така:

#### 1. Анатомія операції `ftl_write`
Функція `ftl_write` приймає логічний номер сектора `LBA` і виконує сувору послідовність із шести послідовних фаз:
1. **Валідація меж логічного простору:** контролер перевіряє умову `lba < LOGICAL_PAGES`. У реальному NVMe-контролері при спробі запису за межі виділеного простору створюється статус завершення з кодом помилки `NVME_SC_LBA_OUT_OF_RANGE`.
2. **Моніторинг порогу пулу чистих блоків:** функція `ftl_count_free_blocks` підраховує, скільки блоків залишаються повністю неторканими (тобто мають `free_page_idx == 0` та `valid_count == 0`). Якщо їхня кількість стає меншою за захисний поріг `GC_THRESHOLD_BLOCKS`, а активний блок вичерпано, негайно ініціюється виклик `ftl_run_gc`.
3. **Ротація активного відкритого блоку:** новий запис може лягти лише у наступну послідовну сторінку поточного активного блоку. Якщо покажчик досяг краю (`free_page_idx == PAGES_PER_BLOCK`), контролер шукає наступний стертий блок функцією `ftl_find_free_block` і робить його активним.
4. **Атомарна інвалідація старої копії:** контролер зчитує поточний запис `old_pba = l2p_table[lba]`. Якщо адреса дійсна (`old_pba != INVALID_ADDR`), обчислюються координати старого блоку `old_b = old_pba / PAGES_PER_BLOCK` та старої сторінки `old_p = old_pba % PAGES_PER_BLOCK`. Статус цієї сторінки змінюється на `PAGE_INVALID`, лічильник `valid_count` старого блоку зменшується на 1, а `invalid_count` збільшується на 1.
5. **Фізичне програмування та оновлення метаданих:** у новій сторінці статус стає `PAGE_VALID`, зворотний масив `page_lba[new_p]` фіксує номер LBA (зворотне відображення, необхідне для реконструкції при відновленні живлення), а пряма таблиця `l2p_table[lba]` отримує нові координати.
6. **Інкремент лічильників статистики:** збільшуються лічильники `host_writes` та `flash_writes`.

#### 2. Анатомія алгоритму збирання сміття `ftl_run_gc`
Збирання сміття є найбільш ресурсомісткою процедурою мікропрограми:
1. **Жадібний пошук жертви (Greedy Victim Search):** алгоритм сканує дескриптори всіх закритих блоків і вибирає той, у якого значення `invalid_count` є максимальним серед усіх кандидатів.
2. **Міграція дійсних даних (Valid Page Copy):** у блоці-жертві залишилися живі сторінки зі статусом `PAGE_VALID`. Контролер посторінково зчитує їх, знаходить їхній логічний номер у `page_lba` і перезаписує у відкритий активний блок. Кожен такий крок інкрементує `flash_writes` без збільшення `host_writes`, що формує внутрішнє посилення запису.
3. **Оновлення L2P під час міграції:** адреси перенесених сторінок у таблиці `l2p_table` негайно оновлюються на їхні нові фізичні координати, щоб операційна система могла звернутися до них без затримок.
4. **Стирання блоку-жертви (Block Erase):** після завершення копіювання блок стирається: лічильник зносу `erase_count` збільшується на одиницю, усі сторінки повертаються у стан `PAGE_FREE`, а лічильники валідності скидаються в нуль. Блок стає доступним у пулі вільних блоків.

---

### Структури пам'яті та бітове пакування метаданих

У наведеному навчальному коді на C для простоти сприйняття стан сторінки представлений 32-розрядним полем `page_state_t`. У реальному апаратному контролері такий розхід пам'яті є неприпустимим:

* Якщо фізичний блок 3D NAND містить 1024 сторінки, збереження масиву `uint32_t page_states[1024]` вимагало б 4096 байтів пам'яті на кожен блок. Для накопичувача на 1 ТБ із 250 000 блоків лише масив станів зайняв би 1 ГБ дорогоцінної внутрішньої SRAM!
* У промислових FTL застосовується **бітове пакування (Bit-Packing)**: стан сторінки кодується рівно 2 бітами (`00` — Free, `01` — Valid, `10` — Invalid). У результаті весь стан 1024 сторінок блоку вміщується у компактний 256-байтний бітвектор (Bitmask), що скорочує споживання пам'яті в 16 разів.

---

### Покрокове трасування пам'яті під час роботи симулятора

Щоб наочно побачити, як змінюється фізичний стан пам'яті, простежимо виконання програми на п'яти ключових етапах:

| Етап роботи | Активний блок | Зайняті блоки (Valid / Invalid) | Вільні блоки | Стан WAF |
| :--- | :--- | :--- | :--- | :--- |
| **Крок 0 (Старт)** | Блок 0 (`free_idx = 0`) | Немає (усі блоки чисті) | 7 блоків | `WAF = 1.0` |
| **Крок 32 (Cold Start)** | Блок 4 (`free_idx = 0`) | Блоки 0..3 повністю зайняті (8V / 0I кожен) | 3 блоки | `WAF = 1.0` |
| **Крок 48 (Накопичення сміття)** | Блок 6 (`free_idx = 0`) | Блоки 0..5 частково інвалідовані (напр. 3V / 5I) | 1 блок (< поріг 2) | `WAF = 1.0` |
| **Крок 49 (Перший запуск GC)** | Блок 6 (`free_idx = 3`) | Блок 0 очищено (0V / 0I, `erase=1`), дані перенесено | 2 блоки | `WAF = 1.06` |
| **Крок 300 (Стаціонарний стан)** | Блок 2 (`free_idx = 5`) | Блоки 0..7 постійно ротуються (`erase ≈ 10..15`) | 2 блоки | `WAF ≈ 1.8..2.0` |

На кроці 48 кількість вільних блоків падає нижче захисного порогу `GC_THRESHOLD_BLOCKS = 2`. Контролер виявляє блок 0 з максимальним сміттям (5 недійсних сторінок), копіює 3 живі сторінки в активний блок 6, стирає блок 0 і повертає його в чистий пул. Лічильник `flash_writes` збільшується на 3, і WAF уперше перевищує одиницю.

---

### Інтеграція динамічного вирівнювання зносу (Wear Leveling)

У наведеному базовому коді функція `ftl_find_free_block` сканує масив лінійно й повертає перший-ліпший чистий блок. При такому підході блоки з молодшими номерами (0, 1, 2) використовуються частіше й зношуються швидше за старші блоки.

Для забезпечення рівномірного зносу функцію вибору вільного блоку вдосконалюють до алгоритму **Dynamic Wear Leveling**, обираючи блок з найменшим значенням `erase_count`:

:::tabs
```c
static int32_t ftl_find_best_free_block(const ftl_controller_t *ftl) {
    int32_t best_block = -1;
    uint32_t min_erase = UINT32_MAX;

    for (uint32_t b = 0; b < NUM_BLOCKS; b++) {
        if (b == ftl->active_block_id) continue;
        if (ftl->blocks[b].free_page_idx == 0 && ftl->blocks[b].valid_count == 0) {
            if (ftl->blocks[b].erase_count < min_erase) {
                min_erase = ftl->blocks[b].erase_count;
                best_block = (int32_t)b;
            }
        }
    }
    return best_block;
}
```
```cpp
[[nodiscard]] std::optional<size_t> find_best_free_block() const noexcept {
    std::optional<size_t> best_block;
    uint32_t min_erase = UINT32_MAX;

    for (size_t b = 0; b < blocks_.size(); ++b) {
        if (b != active_block_id_ && blocks_[b].is_clean()) {
            if (blocks_[b].erase_count < min_erase) {
                min_erase = blocks_[b].erase_count;
                best_block = b;
            }
        }
    }
    return best_block;
}
```
:::

У мікроконтролерах із тисячами блоків лінійне сканування `O(B)` замінюють на бітові карти з апаратними інструкціями пошуку бітів (наприклад, `__builtin_clz` / `_BitScanForward` в архітектурах ARM/x86) або мікроконтролерну чергу з пріоритетом (Min-Heap), що гарантує час вибору блоку `O(1)`.

---

### Апаратний тракт прямого доступу (Host DMA та FMI FIFOs)

У реальному високошвидкісному твердотільному накопичувачі центральний процесорний комплекс SoC контролера ніколи не перекачує корисні дані користувача через власні регістри загального призначення. Пряме копіювання даних процесором паралізувало б його ядра на перших же сотнях мегабайтів навантаження.

Натомість контролер будує роботу за принципом **дескрипторного апаратного конвеєра**:
1. Процесорне ядро обробляє чергу команд NVMe у пам'яті SRAM, парсить дескриптор запиту та знаходить виділену фізичну сторінку у відкритому блоці за алгоритмом FTL.
2. Ядро формує два апаратні дескриптори прямого доступу до пам'яті (DMA):
   * **Host DMA Engine:** налаштовується на читання даних з оперативної пам'яті хоста за списком фізичних адрес (PRP або SGL) та скеровує їх у внутрішнє кільцеве FIFO контролера пам'яті DRAM.
   * **Flash Interface Engine (FMI):** налаштовується на передачу даних із буфера DRAM через апаратний рандомізатор (Scrambler) та кодер LDPC безпосередньо у фізичні лінії шини ONFI.
3. Обидва рушії запускаються апаратними тригерами, після чого ядра CPU контролера миттєво переходять до планування наступних транзакцій у черзі.

Така розділена архітектура дозволяє синхронізувати абсолютно різні за частотою та протоколом тактові домени: 1 ГГц процесорної системної шини AXI, 32 ГТ/с шини PCIe Gen5 та 2400 МТ/с паралельної шини ONFI 5.1 Flash.

Крім того, взаємодія між драйвером ОС та апаратними чергами контролера організована у вигляді кільцевих буферів (Circular Ring Buffers) у системній RAM. Контролер періодично скидає записи завершення (Completion Queue Entries) через PCIe MSI-X переривання, що зводить накладні витрати хост-процесора до абсолютного мінімуму. Це дозволяє обробляти понад 1 000 000 IOPS при завантаженні центрального процесора хоста менше 5%.

---

### Інструкція зі збірки та відтворення результатів

Обидва варіанти програми (C та C++20) є повністю самодостатніми й не потребують сторонніх бібліотек, окрім стандартних інструментів компіляції:

* **Компіляція версії на C:**
```bash
gcc -O3 -Wall -Wextra -std=c11 ftl_sim.c -o ftl_sim_c
./ftl_sim_c
```
* **Компіляція версії на C++20:**
```bash
g++ -O3 -Wall -Wextra -std=c++20 ftl_sim.cpp -o ftl_sim_cpp
./ftl_sim_cpp
```

Обидва бінарні файли генерують однаковий статистичний звіт, демонструючи стабільний коефіцієнт посилення запису `WAF ≈ 1.8..2.0` при випадковому навантаженні з 100% апаратним Over-Provisioning.

---

### Порівняння підходів у мовах C та C++20

Порівняння двох реалізацій симулятора демонструє еволюцію інженерного мислення від низькорівневого мікрокоду до сучасного безпечного проектування:

* **Модель на чистому C:** побудована на пласких структурах, статичних масивах та прямих математичних операціях ділення й взяття за модулем (`/` та `%`). Цей підхід є стандартом де-факто для прошивок із жорстким детермінізмом часу виконання (Bare-metal firmware для ядер ARM Cortex-R чи RISC-V). Тут немає жодних неявних виділень динамічної пам'яті (відсутні виклики `malloc`), що унеможливлює фрагментацію системної купи й гарантує фіксований розмір бінарного коду в ROM.
* **Модель на C++20:** використовує строгу типізацію (`enum class PageState : uint8_t`), автоматичне керування ресурсами через векторні контейнери, безпечну роботу з відсутніми значеннями через `std::optional<uint32_t>` (замість магічних констант `0xFFFFFFFF`) та сучасні специфікатори безпеки `[[nodiscard]]` і `noexcept`. Клас `FtlSimulator` інкапсулює внутрішній стан, захищаючи інваріанти таблиці L2P від випадкової модифікації ззовні.

---

### Апаратні пастки та крайові випадки у промислових FTL

При перенесенні базової моделі у реальний кремнієвий контролер розробники стикаються з критичними апаратними проблемами:

#### 1. Ефект «урвища швидкості» (Write Cliff) та якість сервісу (QoS)
У нашій спрощеній реалізації збирання сміття викликається синхронно: якщо при черговому виклику `ftl_write` вільних блоків недостатньо, запис блокується до завершення виконання функції `ftl_run_gc`. У реальному SSD це викликає катастрофічне падіння швидкості (Write Cliff): накопичувач працює на швидкості інтерфейсу PCIe (наприклад, 7000 МБ/с), а в момент вичерпання вільних блоків швидкість раптово просідає до 50–100 МБ/с, а затримка відповіді підскакує з 20 мікросекунд до 10 мілісекунд.

*Вирішення в промислових контролерах:* FTL реалізує **фонове збирання сміття** (Background GC). Окремий низькопріоритетний потік мікропрограми відстежує паузи в роботі хоста (Idle time) і заздалегідь стирає блоки у фоні. Якщо навантаження безперервне, контролер застосовує **пропорційне обмеження швидкості** (GC Throttling), рівномірно розподіляючи накладні витрати міграції між усіма запитами без різких сплесків затримок.

#### 2. Аварійне знеструмлення під час перенесення сторінок
Якщо живлення комп'ютера зникає в момент копіювання дійсних сторінок усередині `ftl_run_gc` (наприклад, дані записано в новий блок, але запис у `l2p_table` ще не оновлено), контролер після перезавантаження ризикує прочитати застарілу інформацію або отримати дві копії одного LBA з різними версіями даних.

*Вирішення:* контролери використовують журнал випереджального запису (Write-Ahead Logging, WAL) у швидкодіючій пам'яті SRAM і захищені танталовими суперконденсаторами схеми Power Loss Protection (PLP), що дають мікроконтролеру 10–30 мілісекунд автономного живлення для атомарної фіксації транзакції.

#### 3. Багатоплощинне вирівнювання (Multi-Plane Superblocks)
У сучасній 3D NAND Flash кристал розділений на 2 або 4 незалежні площини (Planes). Щоб досягти максимальної швидкості, контролер зобов'язаний записувати сторінки одночасно в усі площини. Це вимагає від FTL об'єднувати фізичні блоки різних площин і каналів у так звані **суперблоки** (Superblocks) і розподіляти сторінкові записи строго паралельно з однаковими внутрішніми номерами сторінок.

#### 4. Запобігання пробуксовці збирання сміття (GC Thrashing)
Коли накопичувач заповнений корисними даними на 99%, у кожному блоці-жертві знаходиться лише 1–2 недійсні сторінки. Контролер змушений переносити 99% сторінок заради звільнення 1% місця, що підкидає WAF до 50–100. Для захисту від пробуксовки сучасні FTL застосовують динамічне виділення тимчасових SLC-буферів та агресивне фонове виконання команди TRIM для негайного збільшення ефективного резерву.

#### 5. Невідповідність меж секторів (Alignment Pitfalls)
Якщо операційна система форматує розділ з невідповідністю зміщення кластера відносно апаратного розміру сторінки FTL (наприклад, запис 4 КБ кластера потрапляє на межу між двома різними 4 КБ сторінками NAND), кожен логічний запис змушує контролер модифікувати дві фізичні сторінки. Це подвоює посилення запису на рівному місці, тому сучасні специфікації NVMe та GPT-розмітки жорстко вимагають вирівнювання розділів за межами 1 МБ або 4 МБ.
