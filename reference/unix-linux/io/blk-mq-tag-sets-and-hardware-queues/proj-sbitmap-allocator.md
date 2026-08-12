# ⚙️ Аллокатор тегів sbitmap: алгоритм та моделювання бітової карти

Вставка деталізує математичні принципи, структуру даних та практичну реалізацію масштабованого бітового аллокатора `sbitmap` (Scalable Bitmap), який використовується в блоковому шарі `blk-mq` ядра Linux. У ній розглядається проблема конкуренції за кеш-лінії на багатоядерних системах, алгоритм атомарного пошуку з per-CPU підказками, механізм розподілених черг очікування (`sbitmap_queue`) та наведено повноцінний, робочий приклад симулятора двома мовами (C та C++) для аналізу вистави та пасток паралелізму.

---

## 1. Архітектурна проблема монолітних бітових карт

При обробці мільйонів операцій вводу-виводу на секунду (IOPS) кожна операція вимагає виділення унікального числового тегу (індексу слота від `0` до `queue_depth - 1`) перед відправкою команди в пристрій та його повернення при отриманні переривання завершення.

Якщо реалізувати аллокатор тегів через монолітний масив бітів із єдиним глобальним блокуванням (`spinlock_t`), усі процесорні ядра багатпотокового сервера починають змагатися за один ресурс. У результаті виникає ефект "серфінгу кеш-ліній" (cache-line bouncing):
- Коли CPU 0 виконує атомарну операцію `lock bts` (Bit Test and Set) над словоподібним значенням бітової карти, шина когерентності кешу (протокол MESI/MOESI) змушена інвалідувати цю кеш-лінію у всіх інших L1/L2 кешах процесорних ядер (стан *Invalid*).
- Коли CPU 1 намагається прочитати або змінити сусідній біт у тому ж 64-бітному слові, він отримує промах кешу (cache miss) і змушений чекати на перезавантаження кеш-лінії з L3-кешу або RAM.
- При 64+ ядрах накладні витрати на синхронізацію кешів починають перевищувати час виконання самого вводу-виводу.

---

## 2. Масштабований підхід `sbitmap`

Аллокатор `sbitmap` докорінно вирішує цю проблему за допомогою трьох ключових рішень:

### 1. Просторова фрагментація (Word Array)
Замість одного великого бітового масиву, `sbitmap` розбиває загальну глибину черги на масив окремих структур `struct sbitmap_word`. Кожна структура містить 64-бітну змінну `word` та глибину `depth` (кількість активних бітів у цьому слові). Кожне слово вирівнюється на межу кеш-лінії процесора (`____cacheline_aligned_in_smp`), усуваючи так зване фальшиве спільне використання (false sharing).

### 2. Локальні per-CPU орієнтири (`alloc_hint`)
Для кожного логічного CPU ядро підтримує локальну змінну `alloc_hint` (індекс тегу, який було успішно виділено минулого разу). 
Коли процес на CPU 0 намагається виділити тег, алгоритм починає пошук не з нульового біта першого слова, а з біта `alloc_hint % BITS_PER_WORD` у слові `alloc_hint / BITS_PER_WORD`. 
Це гарантує, що різні процесорні ядра шукають вільні біти в різних частинах бітової карти і не конфліктують за однакові слова пам'яті.

### 3. Безблоковий атомарний цикл (Lock-Free CAS Loop)
Виділення біта виконується без виклику спінлоків за допомогою низькорівневої атомарної інструкції `compare-and-swap` (CAS або `lock cmpxchg` на x86):
1. Зчитати поточне значення слова `val` у процесорний регістр (з Relaxed-семантикою).
2. За допомогою апаратної інструкції `ctz` (Count Trailing Zeros) знайти індекс першого нульового (вільного) біта в інвертованому значенні `~val`.
3. Сформувати маску `1ULL << bit`.
4. Спробувати атомарно замінити `val` на `val | mask`. Якщо інше ядро встигло змінити це слово раніше, CAS-операція повертає помилку, і ядро повторює спробу або переходить до наступного слова в масиві.

---

## 3. Обробка вичерпання ресурсів: `sbitmap_queue`

Коли пристрій повністю завантажений і всі теги виділені, спроба виділення повертає негативний результат. Щоб процеси не витрачали цикли CPU в марному опитуванні (busy loop), ядро огортає `sbitmap` у надбудову `sbitmap_queue`.

`sbitmap_queue` містить масив черг очікування `struct sbq_wait_state`. Якщо виділення тегу не вдалося:
1. Процес обчислює хеш від свого ID або номера CPU і вибирає одну з черг очікування `sbq_wait_state`.
2. Переходить у стан сну (`TASK_UNINTERRUPTIBLE`), додаючи свій потік до черги очікування.
3. Коли інший процес або обробник переривання повертає тег (`sbitmap_queue_clear`), він перевіряє лічильники очікування і викликає розбудження (`wake_up_nr`).
4. Для запобігання ефекту "шторму пробуджень" (*thundering herd problem*), ядро використовує порційне пробудження (`wake_batch`): сповіщення надсилається лише точній кількості процесів, яка відповідає кількості звільнених тегів.

---

## 4. Демонстраційний код симулятора `sbitmap`

Нижче наведено робочий симулятор аллокатора тегів `sbitmap`, реалізований мовами C (C11) та C++ (C++20). Модель імітує паралельну роботу декількох потоків, які активно виділяють та звільняють теги з per-thread підказками.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <pthread.h>

#define BITS_PER_WORD 64
#define NUM_WORDS     4
#define TOTAL_TAGS    (BITS_PER_WORD * NUM_WORDS)
#define NUM_THREADS   4
#define OPS_PER_THREAD 100000

/* Структура одного слова бітової карти sbitmap */
typedef struct {
    _Atomic uint64_t map;
} sbitmap_word_t;

/* Головна структура масштабованої бітової карти */
typedef struct {
    sbitmap_word_t words[NUM_WORDS];
    size_t depth;
} sbitmap_t;

static void sbitmap_init(sbitmap_t *sb, size_t depth) {
    sb->depth = depth;
    for (size_t i = 0; i < NUM_WORDS; i++) {
        atomic_init(&sb->words[i].map, 0);
    }
}

/* 
 * Атомарне виділення тегу з використанням локальної підказки (hint).
 * Повертає номер тегу (0..TOTAL_TAGS-1) або -1, якщо всі теги зайняті.
 */
static int sbitmap_get(sbitmap_t *sb, unsigned int *hint) {
    size_t start_word = (*hint / BITS_PER_WORD) % NUM_WORDS;
    
    for (size_t i = 0; i < NUM_WORDS; i++) {
        size_t w_idx = (start_word + i) % NUM_WORDS;
        sbitmap_word_t *w = &sb->words[w_idx];
        
        uint64_t val = atomic_load_explicit(&w->map, memory_order_relaxed);
        while (val != ~0ULL) {
            /* Пошук першого нульового біта через інструкцію ctz */
            int bit = __builtin_ctzll(~val);
            if (bit >= BITS_PER_WORD) break;
            
            uint64_t mask = 1ULL << bit;
            if (!(val & mask)) {
                /* Атомарна спроба забронювати біт з Acquire-семантикою */
                if (atomic_compare_exchange_weak_explicit(&w->map, &val, val | mask,
                                                           memory_order_acquire,
                                                           memory_order_relaxed)) {
                    unsigned int tag = (unsigned int)(w_idx * BITS_PER_WORD + bit);
                    *hint = tag + 1; /* Оновлюємо локальну підказку */
                    return tag;
                }
            }
        }
    }
    return -1; /* Всі теги вичерпано */
}

/* 
 * Повернення тегу у пул із Release-семантикою 
 */
static void sbitmap_clear(sbitmap_t *sb, unsigned int tag) {
    size_t w_idx = tag / BITS_PER_WORD;
    unsigned int bit = tag % BITS_PER_WORD;
    uint64_t mask = ~(1ULL << bit);
    
    atomic_fetch_and_explicit(&sb->words[w_idx].map, mask, memory_order_release);
}

typedef struct {
    sbitmap_t *sb;
    int thread_id;
} worker_args_t;

static void *worker_func(void *arg) {
    worker_args_t *wargs = (worker_args_t *)arg;
    sbitmap_t *sb = wargs->sb;
    unsigned int hint = wargs->thread_id * 16;
    size_t allocated_count = 0;

    for (int i = 0; i < OPS_PER_THREAD; i++) {
        int tag = sbitmap_get(sb, &hint);
        if (tag >= 0) {
            allocated_count++;
            /* Імітація передачі команди та виконання I/O */
            sbitmap_clear(sb, (unsigned int)tag);
        }
    }
    printf("Потік C [%d] успішно обробив %zu операцій тегування.\n", wargs->thread_id, allocated_count);
    return NULL;
}

int main(void) {
    sbitmap_t sb;
    sbitmap_init(&sb, TOTAL_TAGS);

    pthread_t threads[NUM_THREADS];
    worker_args_t args[NUM_THREADS];

    printf("Запуск sbitmap C-симулятора (%d тегів, %d потоків)...\n", TOTAL_TAGS, NUM_THREADS);

    for (int i = 0; i < NUM_THREADS; i++) {
        args[i].sb = &sb;
        args[i].thread_id = i;
        pthread_create(&threads[i], NULL, worker_func, &args[i]);
    }

    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("Тестування C-аллокатора sbitmap завершено успішно.\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <atomic>
#include <thread>
#include <cstdint>
#include <bit>
#include <optional>

class ScalableBitmap {
public:
    static constexpr size_t BITS_PER_WORD = 64;

    explicit ScalableBitmap(size_t num_words)
        : words_(num_words), total_depth_(num_words * BITS_PER_WORD) {
        for (auto& w : words_) {
            w.store(0, std::memory_order_relaxed);
        }
    }

    /* Безблокова аллокація тегу із записом нової підказки */
    [[nodiscard]] std::optional<unsigned int> allocate_tag(unsigned int& hint) noexcept {
        const size_t num_words = words_.size();
        size_t start_word = (hint / BITS_PER_WORD) % num_words;

        for (size_t i = 0; i < num_words; ++i) {
            size_t w_idx = (start_word + i) % num_words;
            auto& word_atom = words_[w_idx];

            uint64_t val = word_atom.load(std::memory_order_relaxed);
            while (val != ~0ULL) {
                int bit = std::countr_zero(~val);
                if (bit >= static_cast<int>(BITS_PER_WORD)) break;

                uint64_t mask = 1ULL << bit;
                if (!(val & mask)) {
                    if (word_atom.compare_exchange_weak(val, val | mask,
                                                        std::memory_order_acquire,
                                                        std::memory_order_relaxed)) {
                        unsigned int tag = static_cast<unsigned int>(w_idx * BITS_PER_WORD + bit);
                        hint = tag + 1;
                        return tag;
                    }
                }
            }
        }
        return std::nullopt;
    }

    /* Повернення тегу з гарантією впорядкування пам'яті */
    void release_tag(unsigned int tag) noexcept {
        size_t w_idx = tag / BITS_PER_WORD;
        unsigned int bit = tag % BITS_PER_WORD;
        uint64_t mask = ~(1ULL << bit);

        words_[w_idx].fetch_and(mask, std::memory_order_release);
    }

    [[nodiscard]] size_t total_depth() const noexcept { return total_depth_; }

private:
    std::vector<std::atomic<uint64_t>> words_;
    size_t total_depth_;
};

int main() {
    constexpr size_t NUM_WORDS = 4;
    constexpr int NUM_THREADS = 4;
    constexpr int OPS_PER_THREAD = 100000;

    ScalableBitmap sbitmap(NUM_WORDS);
    std::cout << "Запуск C++ sbitmap симулятора (" << sbitmap.total_depth() 
              << " тегів, " << NUM_THREADS << " потоків)...\n";

    std::vector<std::thread> workers;
    workers.reserve(NUM_THREADS);

    for (int t = 0; t < NUM_THREADS; ++t) {
        workers.emplace_back([&sbitmap, t]() {
            unsigned int hint = static_cast<unsigned int>(t * 16);
            size_t allocated = 0;

            for (int i = 0; i < OPS_PER_THREAD; ++i) {
                if (auto tag = sbitmap.allocate_tag(hint)) {
                    ++allocated;
                    sbitmap.release_tag(*tag);
                }
            }
            std::cout << "Потік C++ [" << t << "] обробив " << allocated << " операцій.\n";
        });
    }

    for (auto& th : workers) {
        th.join();
    }

    std::cout << "Тестування C++ sbitmap завершено успішно.\n";
    return 0;
}
```
:::

---

## 5. Пастки алгоритму та системний аналіз

При використанні аллокатора `sbitmap` на реальному апаратному забезпеченні виникають наступні нюанси:

1. **Впорядкування пам'яті (Memory Barriers)**:
   - Операція виділення тегу повинен мати семантику `Acquire`. Це гарантує, що операції ініціалізації структури `request` і підготовки DMA-дескрипторів не пройдуть спекулятивно попереду виділення самого слота тегу.
   - Операція вивільнення тегу повинна мати семантику `Release`. Це гарантує, що всі записи завершених даних I/O скинуто в пам'ять до того, як інший CPU побачить цей тег вільним і перевикористає його.

2. **Деградація при saturation (100% заповненні)**:
   Якщо пристрій досягає межі продуктивності і всі слова бітової карти повністю заповнені (`val == ~0ULL`), алгоритм змушений просканувати весь масив слів `NUM_WORDS` разів, перш ніж переконатися у відсутності тегів. Для виявлення цього стану ядро підтримує атомарний лічильник вільних тегів `sf_map`, що дозволяє відсікати спроби аллокації за `` `O(1)` `` до початку сканування слів.

3. **Локальність NUMA**:
   На двосокетних серверах аллокація тегів з віддаленого NUMA-вузла збільшує latency виклику в 2-3 рази. `blk-mq` вирішує це створенням окремих пулів тегів для кожного NUMA-вузла або динамічним обмеженням мапінгу CPU.

4. **Розмір кеш-ліній та `____cacheline_aligned_in_smp`**:
   Усі елементи масиву `words` підрівнюються під розмір кеш-рядка архітектури (зазвичай 64 байти на x86_64 та ARM64). Без цієї директиви два 64-бітних значення потрапляють у ту саму 64-байтну кеш-лінію, спричиняючи ефект false sharing навіть при використанні per-CPU hints.
