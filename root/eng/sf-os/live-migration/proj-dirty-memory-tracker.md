# ⚙️ Трекер модифікації сторінок і симулятор ітеративної міграції

Будь-який гіпервізор (KVM, QEMU, Xen чи VMware ESXi) під час живої міграції віртуальної машини стикається з однаковою інженерною задачею: як відстежити змінені гостем 4-кілобайтні сторінки пам'яті в реальному часі, скопіювати їх по мережі швидше за темп їхнього оновлення та скоординовано зупинити процесорні потоки рівно в ту мить, коли залишок брудної пам'яті дозволить вкластися у встановлений дедлайн SLA.

Нижче наведено повноцінний симулятор підсистеми відстеження брудних сторінок та ітеративного координатора міграції, реалізований мовами C та C++, а також детальний розбір архітектурних рішень, бар'єрів пам'яті, низькорівневих інтерфейсів ядра Linux та типових помилок багатопотокової синхронізації.

## Архітектурний дизайн та компоненти симулятора

Симулятор моделює повний життєвий цикл ітеративного попереднього копіювання (Pre-Copy) пам'яті між двома віртуальними хостами:

1. **Арена пам'яті (Guest Physical RAM):** Виділений безперервний масив пам'яті розміром 64 МБ (16 384 сторінки по 4096 байтів). У реальних системах ця ділянка виділяється через системний виклик `mmap()` із прапорцями анонімного відображення `MAP_ANONYMOUS | MAP_PRIVATE` або через спільну пам'ять `memfd_create()` з підтримкою прозорих великих сторінок HugePages (2 МБ / 1 ГБ).
2. **Атомарна бітова маска модифікацій (Dirty Bitmap):** Масив 64-бітних слів (`uint64_t`), де кожен біт однозначно відповідає одній 4 КБ сторінці. Біт зі значенням `1` сигналізує, що відповідна сторінка була змінена гостем з моменту останнього скидання маски.
3. **Емуляція гостьового робочого навантаження (Guest vCPU):** Окремий потік виконання, що імітує поведінку транзакційної СУБД: 80% операцій запису концентруються у перших 20% адресного простору (гарячий робочий набір), тоді як решта 20% записів рівномірно розподіляється по всій пам'яті.
4. **Атомарний збір маски (Bitmap Harvesting):** Процедура неподільного вилучення поточного зліпка брудних сторінок та очищення бітової маски за допомогою атомарних інструкцій обміну, що запобігає втраті сторінок, які записуються гостем у мить зчитування.
5. **Ітеративний цикл копіювання:** Координатор у циклі копіює змінені сторінки у цільову арену пам'яті, вимірює тривалість раунду та оцінює швидкість генерації брудних сторінок.
6. **Адаптивний тротлінг (Auto-Converge):** Якщо залишок брудної пам'яті не зменшується протягом двох раундів поспіль (стагнація збіжності), координатор підвищує коефіцієнт тротлінгу, штучно вставляючи мікропаузи в роботу гостьового процесора.
7. **Фінальний Stop-and-Copy та серіалізація пристроїв:** Коли кількість брудних сторінок падає нижче порогового значення, гостьовий потік призупиняється, передається фінальний залишок сторінок і стан віртуальних регістрів, після чого здійснюється побайтова верифікація цілісності пам'яті.

## Реалізація симулятора мовами C та C++

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>
#include <stdatomic.h>

#define PAGE_SIZE          4096
#define TOTAL_PAGES        16384     /* 64 МБ емульованої пам'яті гостя */
#define TOTAL_MEMORY_BYTES (TOTAL_PAGES * PAGE_SIZE)
#define BITMAP_WORDS       (TOTAL_PAGES / 64)
#define DOWNTIME_THRESHOLD_PAGES 64  /* Поріг Stop-and-Copy: 256 КБ */

/* Стан віртуального процесора та апаратних таймерів */
typedef struct {
    uint64_t vcpu_rip;
    uint64_t vcpu_rsp;
    uint64_t vcpu_cr3;
    uint32_t apic_timer_count;
    uint64_t tsc_offset;
} VirtualDeviceState;

/* Глобальний контекст віртуальної машини та міграції */
typedef struct {
    uint8_t *source_ram;
    uint8_t *target_ram;
    atomic_uint_fast64_t dirty_bitmap[BITMAP_WORDS];
    
    atomic_bool vm_running;
    atomic_bool migration_completed;
    atomic_int  cpu_throttle_percent; /* Рівень пригнічення vCPU: 0..95 % */
    
    pthread_t writer_thread;
    pthread_mutex_t vcpu_mutex;
    VirtualDeviceState dev_state;
} VMSimulator;

/* Отримання поточного монотонного часу в мілісекундах */
static double get_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1000.0 + (double)ts.tv_nsec / 1000000.0;
}

/* Позначення сторінки як брудної в атомарній бітовій масці */
static inline void mark_page_dirty(VMSimulator *vm, size_t page_idx) {
    size_t word_idx = page_idx / 64;
    uint64_t bit_mask = 1ULL << (page_idx % 64);
    atomic_fetch_or_explicit(&vm->dirty_bitmap[word_idx], bit_mask, memory_order_relaxed);
}

/* Емуляція гостьового робочого навантаження (потік vCPU) */
static void *guest_writer_worker(void *arg) {
    VMSimulator *vm = (VMSimulator *)arg;
    unsigned int seed = 42;
    
    while (atomic_load_explicit(&vm->vm_running, memory_order_relaxed)) {
        pthread_mutex_lock(&vm->vcpu_mutex);
        
        /* 80% записів у перші 20% сторінок (гарячий набір СУБД) */
        size_t page_idx;
        if (rand_r(&seed) % 100 < 80) {
            page_idx = rand_r(&seed) % (TOTAL_PAGES / 5);
        } else {
            page_idx = rand_r(&seed) % TOTAL_PAGES;
        }
        
        /* Модифікація випадкового байта всередині сторінки */
        size_t offset = page_idx * PAGE_SIZE + (rand_r(&seed) % PAGE_SIZE);
        uint8_t val = (uint8_t)(rand_r(&seed) & 0xFF);
        vm->source_ram[offset] = val;
        
        /* Апаратний перехоплювач KVM/PML виставляє біт модифікації */
        mark_page_dirty(vm, page_idx);
        
        /* Оновлення внутрішніх регістрів гостьового процесора */
        vm->dev_state.vcpu_rip += 4;
        vm->dev_state.apic_timer_count++;
        
        pthread_mutex_unlock(&vm->vcpu_mutex);
        
        /* Облік адаптивного процесорного тротлінгу (Auto-Converge) */
        int throttle = atomic_load_explicit(&vm->cpu_throttle_percent, memory_order_relaxed);
        if (throttle > 0) {
            useconds_t delay_us = (useconds_t)(throttle * 5);
            usleep(delay_us);
        } else {
            /* Базова мінімальна затримка між інтенсивними циклами запису */
            usleep(20);
        }
    }
    return NULL;
}

/* Атомарне зчитування та очищення брудної маски (Bitmap Harvesting) */
static size_t harvest_dirty_bitmap(VMSimulator *vm, uint64_t *local_copy) {
    size_t dirty_count = 0;
    for (size_t i = 0; i < BITMAP_WORDS; ++i) {
        /* Атомарно забираємо поточні брудні біти та скидаємо їх у 0 */
        local_copy[i] = atomic_exchange_explicit(&vm->dirty_bitmap[i], 0ULL, memory_order_acq_rel);
        if (local_copy[i] != 0) {
            dirty_count += (size_t)__builtin_popcountll(local_copy[i]);
        }
    }
    return dirty_count;
}

/* Симуляція мережевої передачі брудних сторінок на цільовий хост */
static void transfer_dirty_pages(VMSimulator *vm, const uint64_t *bitmap) {
    for (size_t w = 0; w < BITMAP_WORDS; ++w) {
        uint64_t word = bitmap[w];
        while (word != 0) {
            int bit = __builtin_ctzll(word);
            size_t page_idx = w * 64 + (size_t)bit;
            
            /* Побайтове копіювання 4 КБ сторінки у цільову пам'ять */
            memcpy(vm->target_ram + page_idx * PAGE_SIZE,
                   vm->source_ram + page_idx * PAGE_SIZE,
                   PAGE_SIZE);
            
            /* Емуляція затримки передачі пакета по мережі (~3 мкс на 4КБ) */
            usleep(3);
            
            word &= ~(1ULL << bit);
        }
    }
}

/* Координатор ітеративної живої міграції */
void run_live_migration(VMSimulator *vm) {
    uint64_t local_bitmap[BITMAP_WORDS];
    size_t round = 0;
    size_t total_transferred_pages = 0;
    size_t prev_dirty_count = TOTAL_PAGES;
    
    printf("[MIGRATION] === Старт ітеративної живої міграції (RAM: %zu МБ) ===\n", TOTAL_MEMORY_BYTES / (1024 * 1024));
    double start_time = get_time_ms();
    
    /* Ітерація 0: Початкове повне копіювання всієї RAM */
    printf("[MIGRATION] Раунд 0 (Повний дамп): передача %d сторінок...\n", TOTAL_PAGES);
    double r0_start = get_time_ms();
    for (size_t i = 0; i < TOTAL_PAGES; ++i) {
        memcpy(vm->target_ram + i * PAGE_SIZE, vm->source_ram + i * PAGE_SIZE, PAGE_SIZE);
    }
    total_transferred_pages += TOTAL_PAGES;
    printf("[MIGRATION] Раунд 0 завершено за %.2f мс.\n", get_time_ms() - r0_start);
    
    /* Ітеративний цикл передачі брудних сторінок */
    while (true) {
        round++;
        double round_start = get_time_ms();
        
        /* Збір брудних сторінок, накопичених за попередній раунд */
        size_t dirty_count = harvest_dirty_bitmap(vm, local_bitmap);
        
        printf("[MIGRATION] Раунд %zu: виявлено %zu брудних сторінок (%.2f МБ)...\n",
               round, dirty_count, (double)(dirty_count * PAGE_SIZE) / (1024.0 * 1024.0));
        
        /* Перевірка умови досягнення порогу збіжності для Stop-and-Copy */
        if (dirty_count <= DOWNTIME_THRESHOLD_PAGES) {
            printf("[MIGRATION] >>> Збіжність досягнута! Залишок %zu сторінок <= порогу %d. <<<\n",
                   dirty_count, DOWNTIME_THRESHOLD_PAGES);
            break;
        }
        
        /* Детекція стагнації: якщо брудна пам'ять не зменшується — активуємо тротлінг */
        if (dirty_count >= prev_dirty_count * 0.90) {
            int cur_throttle = atomic_load_explicit(&vm->cpu_throttle_percent, memory_order_relaxed);
            int new_throttle = cur_throttle + 20;
            if (new_throttle > 90) new_throttle = 90;
            atomic_store_explicit(&vm->cpu_throttle_percent, new_throttle, memory_order_relaxed);
            printf("[AUTO-CONVERGE] Стагнація збіжності! Підвищення тротлінгу vCPU до %d%%\n", new_throttle);
        }
        prev_dirty_count = dirty_count;
        
        /* Передача накопичених сторінок */
        transfer_dirty_pages(vm, local_bitmap);
        total_transferred_pages += dirty_count;
        
        double round_duration = get_time_ms() - round_start;
        printf("[MIGRATION] Раунд %zu завершено за %.2f мс.\n", round, round_duration);
    }
    
    /* ФАЗА STOP-AND-COPY: Зупинка vCPU гостя */
    printf("[STOP-AND-COPY] Зупинка vCPU гостя (початок Downtime)...\n");
    double downtime_start = get_time_ms();
    
    /* 1. Блокуємо та зупиняємо виконання гостьових потоків */
    pthread_mutex_lock(&vm->vcpu_mutex);
    atomic_store_explicit(&vm->vm_running, false, memory_order_relaxed);
    
    /* 2. Фінальний збір залишку брудних сторінок */
    size_t final_dirty = harvest_dirty_bitmap(vm, local_bitmap);
    transfer_dirty_pages(vm, local_bitmap);
    total_transferred_pages += final_dirty;
    
    /* 3. Серіалізація та копіювання стану віртуальних пристроїв */
    VirtualDeviceState target_dev_state = vm->dev_state;
    target_dev_state.tsc_offset += 1000; /* Корекція таймера */
    
    double downtime_ms = get_time_ms() - downtime_start;
    pthread_mutex_unlock(&vm->vcpu_mutex);
    
    printf("[STOP-AND-COPY] Фінал Stop-and-Copy: передано %zu сторінок + стан пристроїв.\n", final_dirty);
    printf("[STOP-AND-COPY] >>> Реальний час простою гостя (Downtime): %.2f мс <<<\n", downtime_ms);
    
    double total_time_ms = get_time_ms() - start_time;
    printf("[MIGRATION] === Міграція успішно завершена за %.2f мс ===\n", total_time_ms);
    printf("[MIGRATION] Сумарно передано сторінок: %zu (%.2f МБ, надлишковість: %.2f x)\n",
           total_transferred_pages,
           (double)(total_transferred_pages * PAGE_SIZE) / (1024.0 * 1024.0),
           (double)total_transferred_pages / (double)TOTAL_PAGES);
}

int main(void) {
    VMSimulator vm;
    memset(&vm, 0, sizeof(vm));
    
    /* Виділення пам'яті для вихідного та цільового хостів */
    vm.source_ram = (uint8_t *)calloc(TOTAL_PAGES, PAGE_SIZE);
    vm.target_ram = (uint8_t *)calloc(TOTAL_PAGES, PAGE_SIZE);
    if (!vm.source_ram || !vm.target_ram) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return 1;
    }
    
    /* Початкове заповнення пам'яті тестовими даними */
    for (size_t i = 0; i < TOTAL_PAGES; ++i) {
        memset(vm.source_ram + i * PAGE_SIZE, (int)(i & 0xFF), PAGE_SIZE);
    }
    
    atomic_store(&vm.vm_running, true);
    atomic_store(&vm.cpu_throttle_percent, 0);
    pthread_mutex_init(&vm.vcpu_mutex, NULL);
    
    /* Запуск гостьового робочого навантаження */
    if (pthread_create(&vm.writer_thread, NULL, guest_writer_worker, &vm) != 0) {
        fprintf(stderr, "Помилка створення потоку vCPU!\n");
        return 1;
    }
    
    /* Даємо гостю попрацювати 50 мс перед міграцією */
    usleep(50000);
    
    /* Запуск координатора міграції */
    run_live_migration(&vm);
    
    pthread_join(vm.writer_thread, NULL);
    
    /* Верифікація побайтової ідентичності пам'яті */
    printf("[VERIFICATION] Перевірка цілісності оперативної пам'яті між джерелом і ціллю...\n");
    if (memcmp(vm.source_ram, vm.target_ram, TOTAL_MEMORY_BYTES) == 0) {
        printf("[VERIFICATION] УСПІХ: Пам'ять цільового вузла 100%% ідентична джерелу!\n");
    } else {
        printf("[VERIFICATION] ПОМИЛКА: Виявлено розходження вмісту сторінок!\n");
    }
    
    pthread_mutex_destroy(&vm.vcpu_mutex);
    free(vm.source_ram);
    free(vm.target_ram);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <atomic>
#include <thread>
#include <mutex>
#include <chrono>
#include <random>
#include <cstring>
#include <span>
#include <memory>
#include <bit>
#include <algorithm>

namespace migration {

inline constexpr size_t kPageSize = 4096;
inline constexpr size_t kTotalPages = 16384; // 64 МБ
inline constexpr size_t kTotalBytes = kTotalPages * kPageSize;
inline constexpr size_t kBitmapWords = kTotalPages / 64;
inline constexpr size_t kDowntimeThresholdPages = 64;

struct VirtualDeviceState {
    uint64_t vcpu_rip{0x1000};
    uint64_t vcpu_rsp{0x7FFF0000};
    uint64_t vcpu_cr3{0x200000};
    uint32_t apic_timer_count{0};
    uint64_t tsc_offset{0};
};

class VMSimulator {
public:
    VMSimulator()
        : source_ram_(std::make_unique<uint8_t[]>(kTotalBytes)),
          target_ram_(std::make_unique<uint8_t[]>(kTotalBytes)) {
        for (auto& word : dirty_bitmap_) {
            word.store(0ULL, std::memory_order_relaxed);
        }
        // Ініціалізація вихідного стану пам'яті
        for (size_t i = 0; i < kTotalPages; ++i) {
            std::memset(source_ram_.get() + i * kPageSize, static_cast<int>(i & 0xFF), kPageSize);
        }
    }

    void mark_page_dirty(size_t page_idx) noexcept {
        size_t word_idx = page_idx / 64;
        uint64_t bit_mask = 1ULL << (page_idx % 64);
        dirty_bitmap_[word_idx].fetch_or(bit_mask, std::memory_order_relaxed);
    }

    size_t harvest_dirty_bitmap(std::span<uint64_t, kBitmapWords> local_copy) noexcept {
        size_t dirty_count = 0;
        for (size_t i = 0; i < kBitmapWords; ++i) {
            local_copy[i] = dirty_bitmap_[i].exchange(0ULL, std::memory_order_acq_rel);
            if (local_copy[i] != 0) {
                dirty_count += static_cast<size_t>(std::popcount(local_copy[i]));
            }
        }
        return dirty_count;
    }

    void run_migration() {
        std::array<uint64_t, kBitmapWords> local_bitmap{};
        size_t round = 0;
        size_t total_transferred_pages = 0;
        size_t prev_dirty_count = kTotalPages;

        std::cout << "[MIGRATION] === Старт C++20 ітеративної живої міграції (RAM: "
                  << kTotalBytes / (1024 * 1024) << " МБ) ===\n";
        auto start_time = std::chrono::steady_clock::now();

        // Ітерація 0: Повний дамп усієї оперативної пам'яті
        std::cout << "[MIGRATION] Раунд 0: Початковий повний дамп " << kTotalPages << " сторінок...\n";
        auto r0_start = std::chrono::steady_clock::now();
        std::memcpy(target_ram_.get(), source_ram_.get(), kTotalBytes);
        total_transferred_pages += kTotalPages;
        auto r0_dur = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - r0_start);
        std::cout << "[MIGRATION] Раунд 0 завершено за " << r0_dur.count() << " мс.\n";

        // Цикл попереднього копіювання брудної пам'яті
        while (true) {
            round++;
            auto round_start = std::chrono::steady_clock::now();

            size_t dirty_count = harvest_dirty_bitmap(local_bitmap);
            double dirty_mb = static_cast<double>(dirty_count * kPageSize) / (1024.0 * 1024.0);
            std::cout << "[MIGRATION] Раунд " << round << ": виявлено "
                      << dirty_count << " брудних сторінок (" << dirty_mb << " МБ)...\n";

            if (dirty_count <= kDowntimeThresholdPages) {
                std::cout << "[MIGRATION] >>> Збіжність досягнута! Залишок " << dirty_count
                          << " <= порогу " << kDowntimeThresholdPages << " <<<\n";
                break;
            }

            if (dirty_count >= static_cast<size_t>(prev_dirty_count * 0.90)) {
                int cur_th = cpu_throttle_percent_.load(std::memory_order_relaxed);
                int new_th = std::min(cur_th + 20, 90);
                cpu_throttle_percent_.store(new_th, std::memory_order_relaxed);
                std::cout << "[AUTO-CONVERGE] Стагнація! Тротлінг vCPU підвищено до " << new_th << "%\n";
            }
            prev_dirty_count = dirty_count;

            transfer_pages(local_bitmap);
            total_transferred_pages += dirty_count;

            auto round_dur = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - round_start);
            std::cout << "[MIGRATION] Раунд " << round << " завершено за " << round_dur.count() << " мс.\n";
        }

        // Фаза Stop-and-Copy: Зупинка vCPU та фінальна синхронізація
        std::cout << "[STOP-AND-COPY] Зупинка vCPU гостя (початок Downtime)...\n";
        auto downtime_start = std::chrono::steady_clock::now();

        {
            std::lock_guard<std::mutex> lock(vcpu_mutex_);
            vm_running_.store(false, std::memory_order_relaxed);

            size_t final_dirty = harvest_dirty_bitmap(local_bitmap);
            transfer_pages(local_bitmap);
            total_transferred_pages += final_dirty;

            // Серіалізація стану віртуальних пристроїв
            target_dev_state_ = dev_state_;
            target_dev_state_.tsc_offset += 1000;
        }

        auto downtime_dur = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - downtime_start);
        std::cout << "[STOP-AND-COPY] >>> Реальний час простою гостя: " << downtime_dur.count() << " мс <<<\n";

        auto total_dur = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - start_time);
        std::cout << "[MIGRATION] === Міграція успішно завершена за " << total_dur.count() << " мс ===\n";
        std::cout << "[MIGRATION] Сумарно передано: " << total_transferred_pages
                  << " сторінок (надлишковість: "
                  << static_cast<double>(total_transferred_pages) / static_cast<double>(kTotalPages) << " x)\n";
    }

    void start_guest_workload() {
        writer_thread_ = std::jthread([this](std::stop_token st) {
            std::mt19937 rng(42);
            std::uniform_int_distribution<size_t> dist_pct(0, 99);
            std::uniform_int_distribution<size_t> dist_hot(0, kTotalPages / 5 - 1);
            std::uniform_int_distribution<size_t> dist_all(0, kTotalPages - 1);
            std::uniform_int_distribution<size_t> dist_offset(0, kPageSize - 1);

            while (!st.stop_requested() && vm_running_.load(std::memory_order_relaxed)) {
                {
                    std::lock_guard<std::mutex> lock(vcpu_mutex_);
                    size_t page_idx = (dist_pct(rng) < 80) ? dist_hot(rng) : dist_all(rng);
                    size_t offset = page_idx * kPageSize + dist_offset(rng);
                    source_ram_[offset] = static_cast<uint8_t>(rng() & 0xFF);

                    mark_page_dirty(page_idx);
                    dev_state_.vcpu_rip += 4;
                    dev_state_.apic_timer_count++;
                }

                int throttle = cpu_throttle_percent_.load(std::memory_order_relaxed);
                if (throttle > 0) {
                    std::this_thread::sleep_for(std::chrono::microseconds(throttle * 5));
                } else {
                    std::this_thread::sleep_for(std::chrono::microseconds(20));
                }
            }
        });
    }

    [[nodiscard]] bool verify_integrity() const noexcept {
        return std::memcmp(source_ram_.get(), target_ram_.get(), kTotalBytes) == 0;
    }

    void stop_guest() {
        vm_running_.store(false, std::memory_order_relaxed);
        if (writer_thread_.joinable()) {
            writer_thread_.request_stop();
            writer_thread_.join();
        }
    }

private:
    void transfer_pages(std::span<const uint64_t, kBitmapWords> bitmap) {
        for (size_t w = 0; w < kBitmapWords; ++w) {
            uint64_t word = bitmap[w];
            while (word != 0) {
                int bit = std::countr_zero(word);
                size_t page_idx = w * 64 + static_cast<size_t>(bit);

                std::memcpy(target_ram_.get() + page_idx * kPageSize,
                            source_ram_.get() + page_idx * kPageSize,
                            kPageSize);

                // Емуляція затримки передачі пакета по мережі
                std::this_thread::sleep_for(std::chrono::microseconds(3));
                word &= ~(1ULL << bit);
            }
        }
    }

    std::unique_ptr<uint8_t[]> source_ram_;
    std::unique_ptr<uint8_t[]> target_ram_;
    std::array<std::atomic<uint64_t>, kBitmapWords> dirty_bitmap_{};

    std::atomic<bool> vm_running_{true};
    std::atomic<int>  cpu_throttle_percent_{0};

    std::mutex vcpu_mutex_;
    VirtualDeviceState dev_state_{};
    VirtualDeviceState target_dev_state_{};
    std::jthread writer_thread_;
};

} // namespace migration

int main() {
    migration::VMSimulator vm;
    vm.start_guest_workload();

    // Даємо гостю попрацювати 50 мс перед стартом міграції
    std::this_thread::sleep_for(std::chrono::milliseconds(50));

    vm.run_migration();
    vm.stop_guest();

    std::cout << "[VERIFICATION] Перевірка цілісності оперативної пам'яті...\n";
    if (vm.verify_integrity()) {
        std::cout << "[VERIFICATION] УСПІХ: Пам'ять цільового вузла 100% ідентична джерелу!\n";
    } else {
        std::cout << "[VERIFICATION] ПОМИЛКА: Виявлено розходження вмісту сторінок!\n";
        return 1;
    }
    return 0;
}
```
:::

## Поглиблений аналіз підсистем та бар'єрів пам'яті

Розглянемо детально ключові низькорівневі механізми, які забезпечують надійність та коректність роботи симулятора та реальних гіпервізорів.

### 1. Атомарність збору маски та запобігання втраті модифікацій (Lost Dirty Bits)

Найбільш критичною операцією під час попереднього копіювання є вилучення накопиченого бітового зліпка (Bitmap Harvesting).

Якщо інженер реалізує збір маски наївним двокроковим способом:
:::tabs
```c
/* НАЇВНИЙ ПОМИЛКОВИЙ ПІДХІД У C: */
uint64_t bits = vm->dirty_bitmap[i];     /* Крок 1: зчитування слова */
/* <- ТУТ vCPU встигає модифікувати сторінку X і записати новий біт! -> */
vm->dirty_bitmap[i] = 0;                 /* Крок 2: занулення маски (біт X ВТРАЧЕНО!) */
```
```cpp
// НАЇВНИЙ ПОМИЛКОВИЙ ПІДХІД У C++:
uint64_t bits = dirty_bitmap_[i].load(std::memory_order_relaxed); // Крок 1: зчитування
// <- ТУТ vCPU встигає модифікувати сторінку X і записати новий біт! ->
dirty_bitmap_[i].store(0ULL, std::memory_order_relaxed);          // Крок 2: занулення (біт X ВТРАЧЕНО!)
```
:::

Якщо гостьовий vCPU встигне виконати запис у пам'ять між кроком 1 та кроком 2, його інструкція виставить біт у масці, але крок 2 негайно перезапише все слово нулем. У результаті сторінка `X` вважатиметься чистою і ніколи не буде надіслана на цільовий сервер. На новому хості гостьова операційна система прокинеться з тихо пошкодженим вмістом пам'яті (Silent Memory Corruption), що призведе до падіння СУБД або розпаду файлової системи.

**Правильне вирішення:** використання атомарної операції обміну `atomic_exchange` (інструкція `XCHG` на архітектурі x86):
:::tabs
```c
local_copy[i] = atomic_exchange_explicit(&vm->dirty_bitmap[i], 0ULL, memory_order_acq_rel);
```
```cpp
local_copy[i] = dirty_bitmap_[i].exchange(0ULL, std::memory_order_acq_rel);
```
:::

Інструкція `XCHG` є апаратно неподільною на рівні шини процесора. Вона зчитує старе значення та записує нуль за один неподільний такт кеш-когерентності, унеможливлюючи вклинювання стороннього запису.

### 2. Семантика бар'єрів пам'яті (Memory Ordering)

У функції `mark_page_dirty` використовується режим `memory_order_relaxed`, тоді як у `harvest_dirty_bitmap` — режим `memory_order_acq_rel`. Чому обрано саме таке комбінування?

- **Для запису (vCPU):** Позначення біта виконується дуже часто (мільйони разів на секунду). Використання `memory_order_relaxed` мінімізує накладні витрати конвеєра CPU, оскільки нам потрібно лише гарантувати атомарність виставлення біта через `LOCK BTS` / `fetch_or`, без примусового скидання конвеєрних черг.
- **Для збору (Координатор):** Операція `exchange` вимагає `memory_order_acq_rel` (Acquire-Release). Прапорець *Acquire* гарантує, що наступні операції читання оперативної пам'яті (`memcpy` у буфер передачі) не почнуться раніше, ніж завершиться вилучення маски. Прапорець *Release* гарантує, що скидання маски в нуль стане видимим для всіх vCPU до того, як координатор почне читати сторінки для поточної ітерації.

### 3. Швидкісне бітове сканування: O(1) проти O(64)

У функції `transfer_dirty_pages` обхід бітової маски реалізовано через вбудовані апаратні інструкції процесора:
- `__builtin_popcountll()` (`POPCNT` на x86) — підраховує кількість одиничних бітів за 1 такт CPU;
- `__builtin_ctzll()` / `std::countr_zero()` (`TZCNT` або `BSF` на x86) — знаходить індекс молодшого встановленого біта за 1 такт CPU.

Замість наївного циклу на 64 ітерації, який перевіряє кожен біт по черзі (`if (word & (1 << b))`), конструкція:
:::tabs
```c
while (word != 0) {
    int bit = __builtin_ctzll(word);
    /* Обробка сторінки page_idx = w * 64 + bit ... */
    word &= ~(1ULL << bit); /* Очищення обробленого біта */
}
```
```cpp
while (word != 0) {
    int bit = std::countr_zero(word);
    // Обробка сторінки page_idx = w * 64 + bit ...
    word &= ~(1ULL << bit); // Очищення обробленого біта
}
```
:::
виконує рівно стільки ітерацій, скільки брудних сторінок реально містить слово. Якщо в 64-бітному слові змінено лише 2 сторінки, цикл виконає рівно 2 ітерації замість 64, що скорочує час обробки маски на 96%.

## Порівняння програмного симулятора з ядром KVM

У реальному ядрі Linux відстеження брудних сторінок виконується не через ручний виклик `mark_page_dirty`, а одним із двох системних методів:

1. **EPT/NPT Write-Protection (через ioctl `KVM_GET_DIRTY_LOG`):**
   - KVM знімає біт дозволу на запис (`Write=0`) у таблицях EPT для всієї пам'яті гостя.
   - Перша спроба запису гостя викликає апаратне виключення `EPT Violation` (#VMEXIT).
   - Обробник переривання ядра Linux фіксує адресу в бітовій масці слота пам'яті (`kvm_memslots`), повертає біт `Write=1` у запис PTE та виконує `VM-Entry`.
   - QEMU викликає `ioctl(vm_fd, KVM_GET_DIRTY_LOG, &log)`, копіюючи маску ядра в простір користувача, що водночас скидає захист EPT на наступне коло.

2. **KVM Dirty Ring (через ioctl `KVM_DIRTY_LOG_RING` з Linux 5.11):**
   - Кожне віртуальне ядро vCPU отримує власний кільцевий буфер фіксованого розміру (наприклад, 4096 записів структури `kvm_dirty_gfn`).
   - Під час запису мікрокод записує номер сторінки в локальне кільце.
   - Коли кільце заповнюється, vCPU призупиняється з кодом `KVM_EXIT_DIRTY_RING_FULL`, сигналізуючи міграційному потоку QEMU про необхідність вичитати записи.
   - Це повністю усуває блокування глобального м'ютекса слотів пам'яті (`slots_lock`) та виключає явище False Sharing між ядрами.

## Аналіз поведінки під різними робочими навантаженнями

Продуктивність та збіжність алгоритму відстеження залежать від характеру доступу гостьової програми до оперативної пам'яті. Розглянемо три класичні шаблони навантаження:

### 1. Транзакційна база даних (OLTP: PostgreSQL, MySQL, Redis)
- **Шаблон:** Висока часова та просторова локальність (80/20 або 90/10). Гостьовий процес безперервно модифікує індекси B-дерев, сторінки буферного пулу та кільцевий журнал транзакцій WAL.
- **Поведінка трекера:** На перших 2–3 раундах передається основна частина статичної пам'яті (таблиці у стані читання, код гостьового ядра). Починаючи з 4-го раунду, обсяг брудної пам'яті стабілізується на рівні активного робочого набору (Working Set). Якщо швидкість мережі `B` перевищує швидкість генерації WAL та брудних блоків, міграція успішно сходиться за 6–8 раундів. Якщо навантаження пікове — Auto-Converge плавно пригнічує vCPU на 20–40%, забезпечуючи швидкий перехід до Stop-and-Copy.

### 2. Потокова аналітика та генерація звітів (OLAP, ETL, Spark)
- **Шаблон:** Послідовний лінійний прохід по гігабайтних масивах пам'яті з одноразовим записом результатів. Локальність нульова.
- **Поведінка трекера:** Оскільки кожна сторінка записується лише один раз, алгоритм XBZRLE не знаходить збігів, а обсяг брудної пам'яті на кожній ітерації точно дорівнює добутку `D · T_n`. Збіжність досягається лише за умови `D < B`. У разі використання 100 GbE лінку міграція збігається лінійно без потреби у тротлінгу.

### 3. Інтенсивна комп'ютерна графіка та наукові розрахунки (vGPU / CUDA)
- **Шаблон:** Прямий доступ до пам'яті через PCIe DMA повз центральний процесор (Direct Memory Access).
- **Поведінка трекера:** Процесорний трекер KVM не бачить записів, здійснених відеокартою через DMA. Для таких систем потрібна спеціальна апаратна підтримка IOMMU та драйвера VFIO Migration v2, який опитує внутрішні лічильники сторінок графічного контролера.

## Оптимізація нульових сторінок (Zero-Page Optimization)

У реальних хмарних середовищах від 30% до 60% оперативної пам'яті віртуальної машини часто складається з порожніх, неініціалізованих або занулених сторінок (наприклад, щойно виділена пам'ять `calloc` чи анонімний heap, де лежать лише байти `0x00`).

Передавати 4096 нульових байтів через мережу для кожної такої сторінки — вкрай марнотратно. Сучасні гіпервізори перед відправкою сторінки виконують її векторне сканування:

1. **Векторна перевірка на нуль:** За допомогою інструкцій AVX2 (`_mm256_testz_si256`) або AVX-512 процесор перевіряє 4096 байтів за кілька тактів (64 перевірки по 32 байти).
2. **Маркування у протоколі:** Якщо всі 4096 байтів дорівнюють нулю, гіпервізор відправляє у мережу лише короткий заголовок (8 байтів: прапорець `RAM_SAVE_FLAG_ZERO` + номер сторінки `Page_Index`).
3. **Обробка на приймачі:** Цільовий гіпервізор не виконує читання з сокета, а викликає `memset(ptr, 0, 4096)` або використовує системний виклик `madvise(ptr, 4096, MADV_DONTNEED)`, що взагалі звільняє фізичний кадр пам'яті в ядрі Linux до першого звернення.

Це дозволяє передавати початковий нульовий раунд (Раунд 0) для віртуальної машини з 128 ГБ пам'яті за лічені секунди, насичуючи мережу лише метаданими.

## Профілювання та трасування міграції через ftrace та eBPF

Для діагностики поведінки міграції у виробничому середовищі інженери використовують точки трасування ядра Linux (Kernel Tracepoints) у підсистемі KVM.

Ключові трейспоінти ядра:
- `kvm:kvm_exit` — фіксує кожен вихід із гостя з кодом причини (reason: `EPT_VIOLATION`, `PML_FULL`, `IO_INSTRUCTION`);
- `kvm:kvm_entry` — фіксує повернення керування гостьовому процесору;
- `kvm:kvm_dirty_ring_full` — спрацьовує, коли локальне кільце брудних сторінок vCPU переповнюється;
- `kvm:kvm_mmu_get_page` — відображає роботу тіньових таблиць або EPT.

За допомогою однорядкового скрипта `bpftrace` можна виміряти розподіл причин виходів VM-Exit під час міграції:

```bash
bpftrace -e '
tracepoint:kvm:kvm_exit {
    @exits[args->exit_reason] = count();
}
interval:s:1 {
    print(@exits);
    clear(@exits);
}'
```

Під час класичного Pre-Copy без апаратного прискорення категорія `EXIT_REASON_EPT_VIOLATION` (код 48 на x86) зростає до 80 000–150 000 подій на секунду на кожне ядро CPU, що наочно пояснює сповільнення роботи гостьової програми. При увімкненні Intel PML цей лічильник падає майже до нуля, а замість нього з'являється кілька сотень подій `EXIT_REASON_PML_FULL` (код 64), що підтверджує ефективне пакетування записів.

## Збереження топології NUMA та локальності вузлів

У багатопроцесорних серверах (Non-Uniform Memory Access, NUMA) затримка доступу до локальної оперативної пам'яті процесорного сокета (Local Node) у 2–3 рази менша за доступ до пам'яті сусіднього сокета (Remote Node через шину UPI / Infinity Fabric).

Якщо на вихідному хості віртуальна машина мала 2 віртуальних NUMA-вузли (vNUMA), прив'язані до двох фізичних сокетів, випадкове розміщення сторінок на цільовому хості під час міграції зруйнує топологію пам'яті. Для збереження продуктивності координатор міграції виконує **NUMA-Aware Transfer**:

1. **Експорт топології vNUMA:** Перед передачею пам'яті передається карта відповідності гостьових фізичних адрес (GPA) віртуальним вузлам `node_id`.
2. **Цільове виділення:** Цільовий гіпервізор викликає системний виклик `mbind(ptr, len, MPOL_BIND, nodemask, maxnode, MPOL_MF_STRICT)`, виділяючи відповідні кадри пам'яті строго на тому фізичному сокеті цільового сервера, до якого прив'язані відповідні потоки vCPU.
3. **Запобігання деградації після міграції:** Завдяки збереженню топології vNUMA гостьова операційна система після переїзду зберігає високу швидкість обробки транзакцій без виникнення міжсокетних вузьких місць.

## Апаратне надсилання без копіювання (Zero-Copy Network Send)

У традиційній схемі передачі гіпервізор зчитує 4 КБ сторінку з гостьової пам'яті та передає її системному виклику `send()` або `write()`. Це змушує ядро Linux копіювати байти з простору користувача в мережеві буфери ядра `sk_buff` (Socket Buffer), споживаючи пропускну здатність шини пам'яті.

Сучасні гіпервізори використовують прапорець **`MSG_ZEROCOPY`** (починаючи з ядра Linux 4.14) у поєднанні з чергами `io_uring`:
- Ядро Linux закріплює сторінки пам'яті гостя (`pin_user_pages`);
- Мережевий адаптер (NIC) забирає байти безпосередньо з гостьової пам'яті через апаратний DMA;
- Ядро сповіщає гіпервізор про завершення передачі через чергу помилок сокета (`MSG_ERRQUEUE`).
Це знижує навантаження на процесор хоста на 40–50% та дозволяє одному ядру процесора утилізувати повну лінійну швидкість 100 GbE лінку.

## Стійкість до збоїв мережі та відновлення (Migration Recovery)

Що відбувається, якщо посеред процесу передачі даних мережеве з'єднання між хостами розривається?

### У режимі Pre-Copy:
Оскільки гостьова віртуальна машина продовжує повноцінно виконуватися на вихідному вузлі, а цільовий хост отримує лише копії сторінок:
- Стан гостя залишається на 100% консистентним на джерелі;
- Гіпервізор-джерело фіксує помилку TCP сокета (`ECONNRESET` або таймаут `ETIMEDOUT`), скасовує міграцію, очищає структури відстеження брудних сторінок та відновлює звичайний режим роботи гостя;
- Цільовий гіпервізор просто знищує недобудований домен і звільняє пам'ять. Відкат є абсолютно безпечним і безшовним.

### У режимі Post-Copy:
У Post-Copy віртуальна машина вже виконується на цільовому хості, але частина її пам'яті залишилася на джерелі:
- Розрив мережі означає, що при черговому сторінковому збої `userfaultfd` цільовий гіпервізор не зможе завантажити сторінку;
- Гостьовий потік блокується на невизначений час.
- Для запобігання аварійному падінню сучасний протокол QEMU підтримує стан **`postcopy-paused`** та команду **`migrate-recover`**: цільовий та вихідний хости встановлюють нове TCP/TLS підключення, повторно узгоджують список відсутніх сторінок і продовжують фонову докачку без перезапуску віртуальної машини.

## Підсумкові інженерні висновки

1. **Неподільність стану:** Будь-яка схема відстеження пам'яті повинна використовувати атомарний обмін `atomic_exchange` або подвійну буферизацію (Double Buffering), щоб унеможливити втрату брудних бітів у вікні між зчитуванням і очищенням.
2. **Адаптивність до стагнації:** Механізм Auto-Converge є обов'язковим запобіжником проти нескінченних циклів міграції: динамічне уповільнення vCPU на 10–20% після кожної невдалої ітерації гарантує детерміноване завершення міграції навіть під екстремальним навантаженням.
3. **Строга серіалізація Stop-and-Copy:** Порядок операцій у фазі простою — спочатку зупинка vCPU, потім бар'єр пам'яті `smp_mb()`, і лише потім фінальний збір бітової маски — єдиний спосіб уникнути розсинхронізації регістрів процесора та байтів в оперативній пам'яті.
