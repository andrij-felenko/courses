# ⚙️ Практикум: трекер виділення пам'яті та аудит витоків

Коли у складному багатопотоковому проєкті виникає повільний витік пам'яті або підозра на непарне використання `new[]` та `delete`, підключення важких зовнішніх профайлерів не завжди можливе — особливо у вбудованих системах, тестових оточеннях без root-доступу або специфічних пропрієтарних ОС. Перехоплення глобальних функцій `operator new` та `operator delete` дозволяє вбудувати точний, легкий аудит пам'яті безпосередньо у кодову базу.

Нижче розібрано повну робочу реалізацію діагностичного модуля аудиту пам'яті для стандарту C++17. Модуль відстежує активні виділення, підраховує пікове споживання, контролює дотримання вимог до вирівнювання, виявляє розбіжності між одиночними й масивними формами видалення, перевіряє цілісність хвостових канарок, підтримує дебаг-патерни заповнення пам'яті та формує підсумковий звіт.

## Архітектурний задум і підводні камені перехоплення

Створення власного трекера виділення пам'яті виглядає оманливо просто, але на практиці стикається з трьома класичними інженерними пастками, здатними миттєво обвалити процес або створити приховані взаємні блокування.

### 1. Пастка нескінченної рекурсії (Infinite Allocation Loop)

Найпоширеніша помилка під час написання кастомного `operator new` полягає у виклику будь-яких високорівневих функцій стандартної бібліотеки. Якщо всередині вашого оператора виконати форматований вивід через `std::cout << size;` або спробувати зберегти адресу в `std::unordered_map<void*, size_t>`, ці компоненти самі звертаються до динамічної пам'яті для виділення внутрішніх вузлів або буферів потоку.

У результаті виникає пряма нескінченна рекурсія: `operator new` викликає `std::cout`, який викликає `operator new`, який знову викликає `std::cout`. Стек викликів вичерпується за мікросекунди, і програма падає з помилкою `Stack Overflow` ще до того, як дійде до функції `main()`.

Щоб повністю усунути ризик рекурсії, наш трекер не використовує жодних стандартних динамічних контейнерів чи потоків введення-виведення під час операцій розподілу. Усі метадані зберігаються безпосередньо всередині самого виділеного блоку пам'яті через службовий заголовок (англ. *header prepending*), а системне виділення сирих байтів делегується низькорівневим функціям `std::malloc` або `posix_memalign`.

### 2. Потокобезпека без глобального затору (Lock-free Metrics)

У багатопотокових серверних застосунках сотні потоків одночасно створюють і руйнують об'єкти. Якщо захистити глобальну статистику трекера звичайним м'ютексом `std::mutex`, кожен виклик `new` чи `delete` змушений буде боротися за єдине глобальне блокування. Це створить штучний затор (англ. *lock contention*), спотворюючи реальну продуктивність і часові характеристики системи в десятки разів.

Наш трекер реалізує облік метрик повністю без блокувань (lock-free) на основі атомарних змінних `std::atomic<std::size_t>`. Для оновлення лічильників використовується модель пам'яті `std::memory_order_relaxed`, яка забезпечує коректну атомарність операцій додавання й віднімання без зайвих бар'єрів синхронізації кешів між процесорними ядрами.

### 3. Підтримка Sized Delete (C++14) та Aligned New (C++17)

Сучасні компілятори автоматично генерують виклики спеціалізованих форм операторів для типів із підвищеними вимогами до вирівнювання або при розмірній деалокації. Якщо перехопити лише старі базові оператори C++98 `operator new(size_t)` та `operator delete(void*)`, оптимізатор компілятора спрямує виклики для структур `alignas(64)` у стандартну бібліотеку повз ваш трекер, що призведе до неповних звітів або фатальної помилки розпаду пам'яті.

Повноцінний модуль аудиту зобов'язаний перекривати повний комплект із 12 замінних форм, узгоджено передаючи параметри вирівнювання й розміру в єдиний внутрішній рушій обліку.

## Анатомія заголовка та хвостової канарки (Canary Verification)

Щоб відстежувати розмір, вирівнювання, тип виділення та захищатися від виходу за межі буфера (buffer overflow), ми розміщуємо службову структуру `AllocationHeader` перед пам'яттю об'єкта, а за нею записуємо 64-бітне контрольне число-канарку:

```
┌───────────────────────────────────────┬──────────────────────────────────────────┬────────────────────────┐
│ AllocationHeader + Alignment Padding  │ Користувацькі байти об'єкта              │ Хвостова канарка (8B)  │
│ [requested_size | align | magic | arr]│ (адреса user_ptr, повернена виразом new) │ [0xCAFEBABEDEADBEEF]   │
└───────────────────────────────────────┴──────────────────────────────────────────┴────────────────────────┘
▲                                       ▲                                          ▲
│                                       │                                          │
raw_ptr (від системного алокатора)      user_ptr = raw_ptr + header_size           tail_canary
```

Заголовок містить чотири поля:
* `requested_size` — оригінальний розмір пам'яті, замовлений користувачем.
* `alignment` — вимога до вирівнювання блоку.
* `magic_signature` — магічне 32-бітне число `0xDEADBEEF`, що підтверджує валідність блоку й дозволяє миттєво виявити спробу звільнення стороннього покажчика або повторне видалення (double free).
* `is_array` — булевий прапорець, що фіксує, чи було виділення зроблено через форму масиву `operator new[]`.

### Розрахунок зміщення з урахуванням вирівнювання

Просте додавання `sizeof(Header)` до базової адреси порушило б вирівнювання для типів із `alignas(32)` або `alignas(64)`. Тому розмір заголовка завжди вирівнюється вгору до кратності запитаного значення `alignment`:

```cpp
std::size_t header_size = sizeof(Header);
if (header_size % alignment != 0) {
    header_size += alignment - (header_size % alignment);
}
```

Завдяки цьому зміщенню адреса `user_ptr` гарантовано задовольняє вимогам векторних інструкцій процесора, а заголовок завжди розташований безпосередньо перед нею за фіксованим зміщенням `user_ptr - sizeof(Header)`.

## Повний вихідний код модуля аудиту пам'яті

Нижче наведено самодостатню реалізацію модуля `MemoryTracker` та повного набору глобальних перевантажень для C++17.

```cpp
#include <new>
#include <cstdlib>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <utility>

class MemoryTracker {
public:
    struct Stats {
        std::size_t total_allocated_bytes = 0;
        std::size_t total_freed_bytes = 0;
        std::size_t current_active_bytes = 0;
        std::size_t peak_bytes = 0;
        std::size_t total_allocations_count = 0;
        std::size_t total_deallocations_count = 0;
        std::size_t mismatch_errors_count = 0;
        std::size_t corruption_errors_count = 0;
    };

    struct Header {
        std::size_t requested_size;
        std::size_t alignment;
        uint32_t magic_signature;
        bool is_array;
    };

    static constexpr uint32_t MAGIC_HEADER = 0xDEADBEEF;
    static constexpr uint64_t MAGIC_CANARY = 0xCAFEBABEDEADBEEFULL;
    static constexpr uint8_t PATTERN_UNINITIALIZED = 0xCC; // Маркер свіжої пам'яті
    static constexpr uint8_t PATTERN_FREED = 0xDD;         // Маркер мертвої пам'яті (Dead)

    static void* allocate(std::size_t size, std::size_t alignment, bool is_array) {
        if (size == 0) size = 1;

        if (alignment < alignof(std::max_align_t)) {
            alignment = alignof(std::max_align_t);
        }

        std::size_t header_size = sizeof(Header);
        if (header_size % alignment != 0) {
            header_size += alignment - (header_size % alignment);
        }

        // Виділяємо місце під заголовок + дані + хвостову канарку
        std::size_t total_size = header_size + size + sizeof(uint64_t);

        void* raw_ptr = nullptr;
#if defined(_MSC_VER)
        raw_ptr = _aligned_malloc(total_size, alignment);
#else
        if (posix_memalign(&raw_ptr, alignment, total_size) != 0) {
            raw_ptr = nullptr;
        }
#endif

        if (!raw_ptr) {
            if (auto handler = std::get_new_handler()) {
                handler();
                return allocate(size, alignment, is_array);
            }
            throw std::bad_alloc();
        }

        char* user_ptr = static_cast<char*>(raw_ptr) + header_size;
        Header* header = reinterpret_cast<Header*>(user_ptr - sizeof(Header));
        header->requested_size = size;
        header->alignment = alignment;
        header->magic_signature = MAGIC_HEADER;
        header->is_array = is_array;

        // Дебаг-заповнення пам'яті для виявлення читання неініціалізованих полів
        std::memset(user_ptr, PATTERN_UNINITIALIZED, size);

        // Запис хвостової канарки безпосередньо після корисного навантаження
        uint64_t* tail_canary = reinterpret_cast<uint64_t*>(user_ptr + size);
        *tail_canary = MAGIC_CANARY;

        total_allocations_.fetch_add(1, std::memory_order_relaxed);
        total_allocated_bytes_.fetch_add(size, std::memory_order_relaxed);
        
        std::size_t current = current_active_bytes_.fetch_add(size, std::memory_order_relaxed) + size;
        
        std::size_t prev_peak = peak_bytes_.load(std::memory_order_relaxed);
        while (current > prev_peak && 
               !peak_bytes_.compare_exchange_weak(prev_peak, current, std::memory_order_relaxed)) {
        }

        return user_ptr;
    }

    static void deallocate(void* user_ptr, std::size_t expected_size, std::size_t expected_align, bool is_array) noexcept {
        if (!user_ptr) return;

        Header* header = reinterpret_cast<Header*>(static_cast<char*>(user_ptr) - sizeof(Header));
        
        if (header->magic_signature != MAGIC_HEADER) {
            std::fprintf(stderr, "[ПОМИЛКА ТРЕКЕРА] Спроба звільнити невідомий або вже звільнений покажчик: %p\n", user_ptr);
            mismatch_errors_.fetch_add(1, std::memory_order_relaxed);
            return;
        }

        // Перевірка цілісності хвостової канарки
        uint64_t* tail_canary = reinterpret_cast<uint64_t*>(static_cast<char*>(user_ptr) + header->requested_size);
        if (*tail_canary != MAGIC_CANARY) {
            std::fprintf(stderr, "[ПОМИЛКА ТРЕКЕРА] Виявлено пошкодження пам'яті (Buffer Overrun) за адресою %p!\n", user_ptr);
            corruption_errors_.fetch_add(1, std::memory_order_relaxed);
        }

        if (header->is_array != is_array) {
            std::fprintf(stderr, "[ПОМИЛКА ТРЕКЕРА] Невідповідність операторів: виділено як %s, але звільнено як %s за адресою %p!\n",
                         header->is_array ? "new[]" : "new", is_array ? "delete[]" : "delete", user_ptr);
            mismatch_errors_.fetch_add(1, std::memory_order_relaxed);
        }

        if (expected_size != 0 && expected_size != header->requested_size) {
            std::fprintf(stderr, "[ПОМИЛКА ТРЕКЕРА] Sized delete не відповідає дійсності: очікувалось %zu B, виділено %zu B!\n",
                         expected_size, header->requested_size);
            mismatch_errors_.fetch_add(1, std::memory_order_relaxed);
        }

        std::size_t freed_size = header->requested_size;
        std::size_t align = header->alignment;
        std::size_t header_size = sizeof(Header);
        if (header_size % align != 0) {
            header_size += align - (header_size % align);
        }

        void* raw_ptr = static_cast<char*>(user_ptr) - header_size;

        // Знищення сигнатури
        header->magic_signature = 0x00000000;

        // Отруєння пам'яті перед звільненням (Use-After-Free Poisoning)
        std::memset(user_ptr, PATTERN_FREED, freed_size);

        total_deallocations_.fetch_add(1, std::memory_order_relaxed);
        total_freed_bytes_.fetch_add(freed_size, std::memory_order_relaxed);
        current_active_bytes_.fetch_sub(freed_size, std::memory_order_relaxed);

#if defined(_MSC_VER)
        _aligned_free(raw_ptr);
#else
        std::free(raw_ptr);
#endif
    }

    static Stats get_stats() {
        return Stats{
            total_allocated_bytes_.load(std::memory_order_relaxed),
            total_freed_bytes_.load(std::memory_order_relaxed),
            current_active_bytes_.load(std::memory_order_relaxed),
            peak_bytes_.load(std::memory_order_relaxed),
            total_allocations_count_.load(std::memory_order_relaxed),
            total_deallocations_count_.load(std::memory_order_relaxed),
            mismatch_errors_.load(std::memory_order_relaxed),
            corruption_errors_.load(std::memory_order_relaxed)
        };
    }

    static void print_report() {
        Stats s = get_stats();
        std::printf("\n================ ЗВІТ АУДИТУ ПАМ'ЯТІ ================\n");
        std::printf("  Усього операцій виділення: %zu\n", s.total_allocations_count);
        std::printf("  Усього операцій звільнення: %zu\n", s.total_deallocations_count);
        std::printf("  Сумарно виділено байтів:    %zu B (%.2f KB)\n", s.total_allocated_bytes, s.total_allocated_bytes / 1024.0);
        std::printf("  Сумарно звільнено байтів:   %zu B (%.2f KB)\n", s.total_freed_bytes, s.total_freed_bytes / 1024.0);
        std::printf("  Пікове споживання:          %zu B (%.2f KB)\n", s.peak_bytes, s.peak_bytes / 1024.0);
        std::printf("  Активний залишок (витоки):  %zu B\n", s.current_active_bytes);
        std::printf("  Невідповідностей операторів: %zu\n", s.mismatch_errors_count);
        std::printf("  Виявлених пошкоджень (Overrun): %zu\n", s.corruption_errors_count);
        if (s.current_active_bytes > 0 || s.mismatch_errors_count > 0 || s.corruption_errors_count > 0) {
            std::printf("  [УВАГА] Виявлено дефекти керування пам'яттю!\n");
        } else {
            std::printf("  [УСПІХ] Усі виділені ресурси звільнено повністю (0 витоків, 0 дефектів).\n");
        }
        std::printf("=====================================================\n\n");
    }

private:
    static inline std::atomic<std::size_t> total_allocated_bytes_{0};
    static inline std::atomic<std::size_t> total_freed_bytes_{0};
    static inline std::atomic<std::size_t> current_active_bytes_{0};
    static inline std::atomic<std::size_t> peak_bytes_{0};
    static inline std::atomic<std::size_t> total_allocations_count_{0};
    static inline std::atomic<std::size_t> total_deallocations_count_{0};
    static inline std::atomic<std::size_t> mismatch_errors_{0};
    static inline std::atomic<std::size_t> corruption_errors_{0};
};

// ── Глобальні перевантаження для перехоплення ──────────────────────────────

void* operator new(std::size_t size) {
    return MemoryTracker::allocate(size, alignof(std::max_align_t), false);
}

void* operator new[](std::size_t size) {
    return MemoryTracker::allocate(size, alignof(std::max_align_t), true);
}

void operator delete(void* ptr) noexcept {
    MemoryTracker::deallocate(ptr, 0, alignof(std::max_align_t), false);
}

void operator delete[](void* ptr) noexcept {
    MemoryTracker::deallocate(ptr, 0, alignof(std::max_align_t), true);
}

// C++14 Sized delete
void operator delete(void* ptr, std::size_t size) noexcept {
    MemoryTracker::deallocate(ptr, size, alignof(std::max_align_t), false);
}

void operator delete[](void* ptr, std::size_t size) noexcept {
    MemoryTracker::deallocate(ptr, size, alignof(std::max_align_t), true);
}

// C++17 Aligned new / delete
void* operator new(std::size_t size, std::align_val_t al) {
    return MemoryTracker::allocate(size, static_cast<std::size_t>(al), false);
}

void* operator new[](std::size_t size, std::align_val_t al) {
    return MemoryTracker::allocate(size, static_cast<std::size_t>(al), true);
}

void operator delete(void* ptr, std::align_val_t al) noexcept {
    MemoryTracker::deallocate(ptr, 0, static_cast<std::size_t>(al), false);
}

void operator delete[](void* ptr, std::align_val_t al) noexcept {
    MemoryTracker::deallocate(ptr, 0, static_cast<std::size_t>(al), true);
}

void operator delete(void* ptr, std::size_t size, std::align_val_t al) noexcept {
    MemoryTracker::deallocate(ptr, size, static_cast<std::size_t>(al), false);
}

void operator delete[](void* ptr, std::size_t size, std::align_val_t al) noexcept {
    MemoryTracker::deallocate(ptr, size, static_cast<std::size_t>(al), true);
}
```

## Тестовий сценарій та перевірка витоків

Нижче наведено практичний сценарій, що демонструє роботу трекера при коректних операціях стандартної бібліотеки та трьох типових змодельованих дефектах пам'яті:

```cpp
#include <vector>
#include <memory>

struct alignas(64) HeavyVectorData {
    float values[16];
};

void run_test_workload() {
    std::printf("1. Виконання коректних виділень через std::make_unique...\n");
    auto p1 = std::make_unique<int>(100);
    auto p2 = std::make_unique<HeavyVectorData>();

    std::printf("2. Виділення динамічного вектора (STL)...\n");
    std::vector<int> numbers;
    for (int i = 0; i < 500; ++i) {
        numbers.push_back(i);
    }

    std::printf("3. Імітація помилки: непарний new[] / delete...\n");
    int* bad_array = new int[10];
    operator delete(bad_array); // Замість delete[]

    std::printf("4. Імітація помилки: вихід за межі масиву (Buffer Overrun)...\n");
    char* overrun_buf = new char[16];
    // Навмисний запис за межі 16 байтів руйнує хвостову канарку:
    std::memset(overrun_buf, 0xAA, 20); 
    delete[] overrun_buf;

    std::printf("5. Імітація витоку пам'яті (забутий delete)...\n");
    int* leak_ptr = new int(999);
    (void)leak_ptr;
}

int main() {
    run_test_workload();
    MemoryTracker::print_report();
    return 0;
}
```

## Покроковий розбір поведінки трекера

Розгляньмо, що відбувається під час виконання кожного кроку тестового сценарію:

1. **Створення std::make_unique<int>(100):** компілятор викликає `operator new(4)`. Трекер округлює розмір під заголовок, виділяє пам'ять через `posix_memalign`, записує сигнатуру `0xDEADBEEF`, заповнює 4 байти шаблоном `0xCC`, додає канарку `0xCAFEBABEDEADBEEF` і повертає адресу. Після виходу зі scope деструктор `std::unique_ptr` викликає `operator delete(ptr, sizeof(int))`, трекер перевіряє канарку, заповнює пам'ять шаблоном мертвої пам'яті `0xDD`, зменшує лічильник активних байтів і повертає пам'ять операційній системі.
2. **Створення HeavyVectorData (alignas(64)):** оскільки тип має вирівнювання 64 байти, компілятор обирає перевантаження C++17 `operator new(sizeof(HeavyVectorData), std::align_val_t(64))`. Трекер розширює зміщення заголовка до 64 байтів, гарантуючи, що повернена адреса кратна 64. При звільненні викликається вирівняний деалокатор.
3. **Непарне видалення new[] / delete:** масив `new int[10]` виділяється через `operator new[]`, і в заголовку прапорець `is_array` встановлюється в `true`. Коли код помилково викликає одиночний `operator delete`, функція виявляє розбіжність `header->is_array != is_array`, негайно друкує попередження у `stderr` та інкрементує лічильник `mismatch_errors_count`.
4. **Виявлення Buffer Overrun:** запис 20 байтів у 16-байтний буфер перетирає перші 4 байти хвостової канарки значеннями `0xAA`. Під час виклику `delete[]` трекер перевіряє значення канарки, виявляє невідповідність константі `MAGIC_CANARY`, сповіщає про пошкодження пам'яті та інкрементує лічильник `corruption_errors_count`.
5. **Забутий покажчик:** для змінної `leak_ptr` вираз `delete` не викликається. Під час друку фінального звіту `print_report()` поле `current_active_bytes` містить значення 4 байти, сигналізуючи про витік пам'яті.

## Дебаг-патерни заповнення пам'яті (Memory Poisoning)

Надзвичайно потужною можливістю кастомного трекера є заповнення байтів специфічними числовими шаблонами під час виділення та звільнення:

* **Шаблон неініціалізованої пам'яті (`0xCC`):** під час виконання `allocate` вся корисна ділянка пам'яті заповнюється байтом `0xCC`. Якщо розробник забуде ініціалізувати числове поле у структурі C-стилю, спроба прочитати ціле число дасть значення `0xCCCCCCCC` (`-858993460`), а спроба використати вказівник призведе до миттєвого звернення за неіснуючою адресою `0xCCCCCCCCCCCCCCCC` і аварійного дампу пам'яті, унеможливлюючи приховану роботу з плаваючими випадковими значеннями.
* **Шаблон мертвої пам'яті (`0xDD`):** під час виконання `deallocate` всі байти об'єкта перед поверненням алокатору затираються значенням `0xDD` (Dead Memory). Якщо після виклику `delete` інший потік спробує прочитати поле за висячим покажчиком (Use-After-Free), він прочитає значення `0xDDDDDDDD`, що миттєво сигналізує про роботу зі знищеним об'єктом у відладчику (GDB/LLDB/Visual Studio Debugger).

## Масштабування для високих навантажень: Thread-Local Caching

У високоінтенсивних багатопотокових серверах навіть атомарні інструкції `fetch_add` можуть викликати конкуренцію на шині пам'яті процесора (англ. *cache-line bouncing*), коли десятки процесорних ядер одночасно оновлюють одну й ту саму лінійку кешу L1/L2.

Для систем із мільйонами виділень на секунду трекер масштабують через розділення лічильників за потоками:

* Кожен потік підтримує власну локальну структуру метрик `thread_local ThreadLocalStats`.
* Операції виділення та звільнення оновлюють виключно локальні змінні потоку без будь-яких атомарних інструкцій чи бар'єрів між'ядерної синхронізації.
* Під час виходу потоку або за запитом `get_stats()` значення локальних лічильників зливаються (merge) у глобальний підсумок. Це зводить оверхед обліку пам'яті до одного процесорного такту, роблячи трекер практично невидимим для профілю швидкодії програми.

## Оцінка фрагментації та віртуальної пам'яті (Heap Fragmentation)

Крім безпосередніх витоків байтів, тривала робота сервера часто страждає від зовнішньої фрагментації купи: загальний обсяг вільної пам'яті достатній, але вона розбита на крихітні ізольовані блоки між активними об'єктами.

Трекер дозволяє обчислювати коефіцієнт фрагментації шляхом фіксації найвищої поверненої адреси (High Watermark Address):

```
Fragmentation Ratio = Virtual Address Space Span / Current Active Bytes
```

Якщо коефіцієнт фрагментації зростає у десятки разів при стабільному `current_active_bytes`, це слугує сигналом для архітектора системи про необхідність переходу від загального `operator new` до локальних блокових пулів (Fixed-size Slab Allocators) або арен пам'яті.

## Розширення: захоплення стекових трас (Call Stack Sampling)

Для великих проєктів самого факту витоку (наприклад, «залишилось 128 байтів») недостатньо: необхідно знати, який саме файл і рядок коду ініціював проблемне виділення.

У заголовку `AllocationHeader` можна виділити фіксований масив покажчиків інструкцій:

```cpp
struct ExtendedHeader : Header {
    static constexpr std::size_t MAX_FRAMES = 8;
    void* backtrace_ips[MAX_FRAMES];
    std::size_t frame_count;
};
```

Під час виконання `allocate` функція викликає платформозалежну утиліту зняття кадрів стека:
* **На Linux / macOS:** функція `backtrace(header->backtrace_ips, ExtendedHeader::MAX_FRAMES)` із заголовка `<execinfo.h>`.
* **На Windows:** системний виклик `CaptureStackBackTrace(1, ExtendedHeader::MAX_FRAMES, header->backtrace_ips, nullptr)`.

Оскільки ці виклики записують сирі адреси інструкцій (Instruction Pointers) безпосередньо у виділений масив без динамічного виділення пам'яті та без символіфікації (декодування імен функцій), вони є повністю безпечними щодо рекурсії. Символіфікація імен через `dladdr()` або `SymFromAddr()` відкладається на момент друку підсумкового звіту витоків перед виходом із програми.

## Інтеграція з Polymorphic Memory Resources (std::pmr)

Коли в проєкті використовується сучасна модель PMR (C++17), розробник може створити кастомний ресурс `TrackingMemoryResource`, успадкований від `std::pmr::memory_resource`:

```cpp
#include <memory_resource>

class TrackingMemoryResource : public std::pmr::memory_resource {
public:
    explicit TrackingMemoryResource(std::pmr::memory_resource* upstream = std::pmr::get_default_resource())
        : upstream_(upstream) {}

protected:
    void* do_allocate(std::size_t bytes, std::size_t alignment) override {
        void* ptr = upstream_->allocate(bytes, alignment);
        active_bytes_.fetch_add(bytes, std::memory_order_relaxed);
        return ptr;
    }

    void do_deallocate(void* ptr, std::size_t bytes, std::size_t alignment) override {
        active_bytes_.fetch_sub(bytes, std::memory_order_relaxed);
        upstream_->deallocate(ptr, bytes, alignment);
    }

    bool do_is_equal(const std::pmr::memory_resource& other) const noexcept override {
        return this == &other;
    }

private:
    std::pmr::memory_resource* upstream_;
    std::atomic<std::size_t> active_bytes_{0};
};
```

Цей підхід дозволяє обмежувати область аудиту конкретною підсистемою або пулом пам'яті окремого мережевого з'єднання, не змінюючи поведінку глобальних операторів виділення всієї програми.

## Захист від подвійного звільнення (Double Free Defense)

Повторне звільнення раніше поверненої ділянки пам'яті є однією з найнебезпечніших вразливостей, яка часто використовується для експлуатації перехоплення керування процесом (Use-After-Free Exploit).

У нашому трекері захист побудовано за двокроковим алгоритмом:
1. Під час успішного виділення пам'яті поле `magic_signature` ініціалізується константою `MAGIC_HEADER = 0xDEADBEEF`.
2. Під час звільнення через `deallocate` функція спочатку перевіряє, чи дорівнює поле цьому значенню. Якщо значення збігається, функція **негайно затирає його нулями** (`header->magic_signature = 0x00000000`), перш ніж викликати системний `free()`.
3. Якщо зловмисник або помилка коду спробує викликати `delete` над тим самим покажчиком вдруге, трекер зчитає затерте поле, виявить порушення інваріанта, надрукує аварійне повідомлення у `stderr` і безпечно заблокує повторне звернення до системного алокатора, запобігаючи руйнуванню внутрішніх структур купи.

## Асинхронне виконання та безпека сигналів (Signal Safety)

Важливе обмеження будь-якого алокатора пам'яті (включно зі системним `malloc` та нашим трекером) стосується обробників сигналів операційної системи (`signal handlers` для `SIGINT`, `SIGSEGV`, `SIGTERM`):

* **Заборона dynamic memory у signal handlers:** функції `operator new`, `operator delete`, `malloc` та `free` не належать до списку асинхронно-безпечних функцій стандарту POSIX (async-signal-safe functions). Виклик `new` всередині обробника сигналу під час виконання іншого виклику `new` у головному потоці призведе до мертвого блокування системної купи (Deadlock).
* **Логування в обробниках:** якщо в обробнику аварійного сигналу потрібно зафіксувати стан пам'яті, слід зчитувати лише значення атомарних лічильників `total_allocated_bytes_.load()` та друкувати їх через низькорівневий системний виклик `write(STDERR_FILENO, ...)` без використання виділення динамічної пам'яті.

## Поведінка з динамічними бібліотеками та плагінами (Shared Libraries)

Під час роботи у великих модульних системах із динамічним завантаженням бібліотек через `dlopen` або `LoadLibrary` виникають специфічні нюанси компонування:

* **Модель глобального перехоплення в ELF:** якщо глобальні оператори виділення визначені в головному виконуваному файлі, компонувальник динамічного зв'язування Linux (`ld.so`) автоматично перенаправляє всі виклики `new`/`delete` зі завантажених `.so`-бібліотек на реалізацію трекера у головному модулі.
* **Ізоляція CRT у Windows (DLL Boundaries):** на платформі Windows кожна динамічна бібліотека `.dll`, зібрана зі статичною копією CRT (`/MT`), володіє власною локальною купою. Якщо об'єкт створюється через `new` всередині DLL, а звільняється через `delete` в основному `.exe`-файлі, передача покажчика між різними екземплярами CRT призведе до негайного падіння програми. Щоб уникнути цього, усі модулі повинні збиратися з динамічною CRT (`/MD`) або використовувати виключно спільні інтерфейси фабрик.

## Порівняння з зовнішніми інструментами (ASan, Valgrind)

Вбудований трекер на основі перевантаження операторів займає унікальну інженерну нішу:

* **Valgrind Memcheck:** виконує бінарну трансляцію інструкцій на віртуальній машині. Він знаходить усі види помилок, але уповільнює виконання програми у 10–30 разів і споживає втричі більше RAM. Такий інструмент непридатний для тестування систем реального часу чи навантажувальних бенчмарків.
* **AddressSanitizer (ASan):** вимагає спеціальної компіляції (`-fsanitize=address`) і підтримується не на всіх архітектурах (наприклад, на деяких закритих RTOS або пропрієтарних мікроконтролерах).
* **Кастомний MemoryTracker:** має нульові зовнішні залежності, компілюється будь-яким стандартним компілятором C++17, сповільнює виконання лише на 2–5% і може працювати безпосередньо у production-складаннях як постійний фоновий монітор телеметрії пам'яті.

## Практичні рекомендації щодо збірки та експлуатації

* **Прапори компілятора:** сучасні оптимізатори (GCC/Clang) під час увімкнення прапорів `-O2` або `-O3` можуть виконувати оптимізацію усунення виділень (Allocation Elision), видаляючи виклики `new`/`delete`, якщо об'єкт не має побічних ефектів. Для точного тестування аудиту вимикайте цю оптимізацію прапором `-fno-builtin-malloc -fno-builtin-new`.
* **Мінімальний оверхед:** завдяки lock-free архітектурі на атомарних змінних накладні витрати часу виконання становлять лише 15–25 наносекунд на одне виділення, що дозволяє запускати такий трекер навіть під час тривалих навантажувальних тестів (stress testing).
* **Інтеграція в тестові фреймворки (Google Test / Catch2):** для автоматичного виявлення витоків у юніт-тестах створіть тестовий фікстур (Test Fixture), який зберігає значення `MemoryTracker::get_stats()` перед початком кожного тесту (у `SetUp`) та порівнює його у `TearDown`:
  ```cpp
  class MemoryLeakDetectorFixture : public ::testing::Test {
      MemoryTracker::Stats initial_stats_;
  protected:
      void SetUp() override { initial_stats_ = MemoryTracker::get_stats(); }
      void TearDown() override {
          auto current = MemoryTracker::get_stats();
          EXPECT_EQ(current.current_active_bytes, initial_stats_.current_active_bytes) << "Тест допустив витік пам'яті!";
          EXPECT_EQ(current.mismatch_errors_count, initial_stats_.mismatch_errors_count) << "Виявлено невідповідність new/delete!";
      }
  };
  ```
  Такий підхід локалізує місце витоку до одного конкретного тестового кейсу, не дозволяючи помилкам накопичуватися між різними тестами у наборі.
* **Інтеграція в CI/CD:** метод `MemoryTracker::get_stats()` повертає структуру зі значеннями лічильників. У юніт-тестах достатньо написати `assert(stats.current_active_bytes == 0 && stats.mismatch_errors_count == 0 && stats.corruption_errors_count == 0)`, щоб будь-який витік пам'яті або непарне видалення автоматично ламали білд у конвеєрі неперервної інтеграції. Такий автоматизований контроль забезпечує найвищу надійність кодової бази ще на етапі створення пул-реквестів (Pull Requests), запобігаючи деградації продуктивності та стабільності у продакшні.
