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
