# ⚙️ Пул фіксованих об'єктів: розділення алокації та виклику конструкторів

У системах високої частоти оновлення (HFT-трейдинг, фізичні рушії відеоігор, мережеві комутатори пакетів на рівні ядра) стандартне динамічне виділення та видалення об'єктів через глобальну купу (`malloc` / `free` у C або оператори `new` / `delete` у C++) є головним джерелом непередбачуваних затримок. Кожне звернення до загального алокатора тягне за собою пошук вільного чанка в структурах купового дерева, потенційну фрагментацію адресного простору та неминучу синхронізацію між потоками (блокування глобальних м'ютексів арени пам'яті). Крім того, розкидані по всій купі об'єкти спричиняють масові промахи кешу процесора (англ. *CPU cache misses*).

Розв'язанням цієї задачі є **пул об'єктів** (англ. *object pool*): суцільний заздалегідь виділений блок сирої пам'яті, розбитий на слоти фіксованого розміру під конкретний тип `T`. У такій архітектурі алокація сирої пам'яті виконується один раз під час запуску системи, а створення та знищення конкретних сутностей відбувається на місці за гарантований час `O(1)`.

Для побудови пулу необхідно розділити життєвий цикл сутності на дві незалежні операції:
1. Керування адресами сирої пам'яті за допомогою інвазивного вільного списку (англ. *intrusive free-list*).
2. Явний виклик конструктора на отриманій сирій адресі через розміщувальне створення (*placement new*) та явний виклик деструктора перед поверненням слота в пул.

## Архітектура та організація інвазивного списку

Найбільш ефективний спосіб організації пулу полягає у використанні пам'яті самих вільних слотів для зберігання зв'язків списку. Поки слот не містить живого об'єкта, його перші 8 байтів розглядаються як покажчик `next` на наступний вільний слот. Щойно клієнт запитує об'єкт, цей самий буфер перетворюється на живий екземпляр типу `T`. Така техніка не вимагає жодного додаткового байта службової пам'яті на метадані елементів.

Нижче наведено повну реалізацію пулу з підтримкою передачі довільних аргументів конструктора та автоматичною RAII-обгорткою `std::unique_ptr` із власним делетером.

:::tabs
```cpp
#include <cstddef>
#include <new>
#include <utility>
#include <memory>
#include <string>
#include <iostream>
#include <cstdint>
#include <stdexcept>

template <typename T, std::size_t Capacity>
class ObjectPool {
public:
    ObjectPool() : free_head_(nullptr) {
        // Формуємо однозв'язний список вільних слотів усередині статичного масиву
        for (std::size_t i = 0; i < Capacity; ++i) {
            auto* node = reinterpret_cast<FreeNode*>(&storage_[i]);
            node->next = free_head_;
            free_head_ = node;
        }
    }

    // Забороняємо копіювання пулу (він володіє унікальним буфером)
    ObjectPool(const ObjectPool&) = delete;
    ObjectPool& operator=(const ObjectPool&) = delete;

    ~ObjectPool() {
        // Пул звільняє саму пам'ять (storage_ знищується автоматично).
        // Усі активні об'єкти мали бути знищені клієнтом перед смертю пулу.
    }

    template <typename... Args>
    T* create(Args&&... args) {
        if (!free_head_) {
            return nullptr; // Пул повністю вичерпано
        }

        // 1. Вилучаємо перший вільний слот із голови списку (O(1))
        FreeNode* node = free_head_;
        free_head_ = node->next;
        void* raw_memory = static_cast<void*>(node);

        // 2. Фаза народження: placement new викликає конструктор T на сирій адресі
        try {
            return ::new (raw_memory) T(std::forward<Args>(args)...);
        } catch (...) {
            // Гарантія безпеки винятків: якщо конструктор T викинув виняток,
            // повертаємо сирий слот назад у список, щоб уникнути витоку пам'яті
            node->next = free_head_;
            free_head_ = node;
            throw;
        }
    }

    void destroy(T* obj) noexcept {
        if (!obj) return;

        // 1. Фаза смерті: явний виклик деструктора (звільняє внутрішні ресурси T)
        std::destroy_at(obj); // Еквівалент obj->~T() у C++17/20

        // 2. Повернення слота сирої пам'яті назад у вільний список (O(1), без виклику free)
        auto* node = reinterpret_cast<FreeNode*>(obj);
        node->next = free_head_;
        free_head_ = node;
    }

    // RAII-делетер для безпечного автоматичного повернення об'єкта в пул
    struct Deleter {
        ObjectPool* pool;
        void operator()(T* ptr) const noexcept {
            if (pool) pool->destroy(ptr);
        }
    };
    using UniquePtr = std::unique_ptr<T, Deleter>;

    template <typename... Args>
    UniquePtr acquire(Args&&... args) {
        T* raw = create(std::forward<Args>(args)...);
        if (!raw) {
            throw std::bad_alloc();
        }
        return UniquePtr(raw, Deleter{this});
    }

    std::size_t capacity() const noexcept { return Capacity; }

private:
    union FreeNode {
        FreeNode* next;
        // Гарантуємо правильне вирівнювання та розмір під тип T
        alignas(alignof(T)) std::byte data[sizeof(T)];
    };

    // Суцільний масив сирої пам'яті без виклику конструкторів T під час старту
    alignas(alignof(T)) FreeNode storage_[Capacity];
    FreeNode* free_head_;
};

// Демонстраційний клас із внутрішніми динамічними ресурсами
class Session {
public:
    Session(uint64_t id, std::string token)
        : id_(id), token_(std::move(token)) {
        std::cout << "  [+] Session #" << id_ << " створено (токен: " << token_ << ")\n";
    }

    ~Session() {
        std::cout << "  [-] Session #" << id_ << " знищено (пам'ять токена звільнено)\n";
    }

    void ping() const {
        std::cout << "  [*] Session #" << id_ << " активна\n";
    }

private:
    uint64_t id_;
    std::string token_;
};

int main() {
    ObjectPool<Session, 2> pool;

    std::cout << "1. Створення об'єктів у пулі через RAII acquire:\n";
    {
        auto s1 = pool.acquire(101ULL, "tok_auth_abc");
        auto s2 = pool.acquire(102ULL, "tok_auth_xyz");

        s1->ping();
        s2->ping();

        std::cout << "2. Вихід із внутрішньої області видимості:\n";
    } // s1 і s2 виходять зі scope: деструктори Session викликаються автоматично,
      // а слоти повертаються назад у free_head_ пулу

    std::cout << "3. Повторне використання слотів без жодної алокації в купі:\n";
    auto s3 = pool.acquire(103ULL, "tok_auth_reused");
    s3->ping();

    return 0;
}
```
```c
#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>

// Елемент вільного списку із суворим вирівнюванням
typedef union SlotNode {
    union SlotNode* next;
    _Alignas(max_align_t) char raw_bytes[64]; // Буфер під структуру фіксованого розміру
} SlotNode;

typedef struct {
    SlotNode* storage;
    SlotNode* free_head;
    size_t capacity;
    size_t item_size;
} ObjectPoolC;

// Демонстраційна сутність у стилі C
typedef struct {
    uint64_t id;
    char* token; // Динамічний ресурс, що вимагає ручного звільнення
} SessionC;

// Явний аналог конструктора
int session_construct(SessionC* s, uint64_t id, const char* token) {
    s->id = id;
    size_t len = strlen(token) + 1;
    s->token = (char*)malloc(len);
    if (!s->token) {
        return -1;
    }
    memcpy(s->token, token, len);
    printf("  [+] C Session #%llu створено (токен: %s)\n", (unsigned long long)s->id, s->token);
    return 0;
}

// Явний аналог деструктора
void session_destruct(SessionC* s) {
    printf("  [-] C Session #%llu знищено (пам'ять токена звільнено)\n", (unsigned long long)s->id);
    free(s->token);
    s->token = NULL;
}

int pool_init(ObjectPoolC* pool, size_t capacity, size_t item_size) {
    if (item_size > sizeof(SlotNode)) {
        return -1; // Структура занадто велика для наявного розміру слота
    }
    pool->capacity = capacity;
    pool->item_size = item_size;
    pool->storage = (SlotNode*)malloc(capacity * sizeof(SlotNode));
    if (!pool->storage) return -1;

    pool->free_head = NULL;
    for (size_t i = 0; i < capacity; ++i) {
        pool->storage[i].next = pool->free_head;
        pool->free_head = &pool->storage[i];
    }
    return 0;
}

void* pool_alloc_raw(ObjectPoolC* pool) {
    if (!pool->free_head) return NULL;
    SlotNode* node = pool->free_head;
    pool->free_head = node->next;
    return (void*)node;
}

void pool_free_raw(ObjectPoolC* pool, void* ptr) {
    if (!ptr) return;
    SlotNode* node = (SlotNode*)ptr;
    node->next = pool->free_head;
    pool->free_head = node;
}

void pool_destroy(ObjectPoolC* pool) {
    free(pool->storage);
    pool->storage = NULL;
    pool->free_head = NULL;
}

int main(void) {
    ObjectPoolC pool;
    if (pool_init(&pool, 2, sizeof(SessionC)) != 0) {
        return 1;
    }

    printf("1. Ручне виділення сирої адреси та ініціалізація:\n");
    SessionC* s1 = (SessionC*)pool_alloc_raw(&pool);
    session_construct(s1, 101, "tok_auth_abc");

    SessionC* s2 = (SessionC*)pool_alloc_raw(&pool);
    session_construct(s2, 102, "tok_auth_xyz");

    printf("2. Ручне знищення полів та повернення слота в пул:\n");
    session_destruct(s1);
    pool_free_raw(&pool, s1);

    session_destruct(s2);
    pool_free_raw(&pool, s2);

    printf("3. Повторне використання пам'яті без звернення до malloc:\n");
    SessionC* s3 = (SessionC*)pool_alloc_raw(&pool);
    session_construct(s3, 103, "tok_auth_reused");

    session_destruct(s3);
    pool_free_raw(&pool, s3);

    pool_destroy(&pool);
    return 0;
}
```
:::

## Покроковий розбір роботи рантайму

Коли клієнтський код викликає метод `pool.create(args...)`, у системі відбувається чітка послідовність низькорівневих кроків:

1. **Отримання адреси без алокації.** Метод забирає покажчик `free_head_` і переставляє його на наступний елемент `node->next`. Це операція читання одного машинного слова з пам'яті (кілька процесорних тактів), на відміну від сотень інструкцій у функціях `malloc`.
2. **Виклик розміщувального new (placement new).** Вираз `::new (raw_memory) T(...)` є вбудованою формою оператора `new`. Він не виділяє пам'ять, а лише передає адресу першим прихованим аргументом `this` у конструктор типу `T`. У машинному коді компілятор генерує пряму інструкцію `call` на тіло конструктора.
3. **Обробка аварійних винятків у конструкторі.** Якщо передані аргументи призводять до винятку (наприклад, `std::bad_alloc` всередині конструктора рядка `token`), об'єкт не вважається створеним. Блок `try-catch` перехоплює аварію, повертає сирий слот назад у список `free_head_` і повторно викидає виняток через `throw;`. Без цього перехоплення слот був би безповоротно втрачений для пулу (*slot leak*).
4. **Явна деструкція перед вивільненням.** Коли об'єкт повертається в пул, виклик `std::destroy_at(obj)` виконує деструктор `~Session()`. Деструктор звільняє пам'ять рядка `token_`. Після цього адреса об'єкта знову інтерпретується як `FreeNode*` і вставляється в голову списку `free_head_`.

## Багатопоточність і масштабування пулу

У багатопотокових середовищах операція отримання слота з одного загального пулу може стати вузьким місцем через блокування синхронізації. Існує два головні інженерні підходи для розв'язання цієї проблеми:

- **Неблокувальний стек (Lock-Free Free-List).** Покажчик `free_head_` замінюється на `std::atomic<FreeNode*>`, а вилучення слота виконується через атомарну операцію `compare_exchange_weak`. Для усунення класичної проблеми ABA (коли потік А зчитує покажчик, потік Б видаляє й повторно повертає той самий слот, вводячи потік А в оману) використовують теговані покажчики (англ. *tagged pointers*) або 128-бітне атомарне порівняння з лічильником покоління на архітектурах x86-64 (`CMPXCHG16B`).
- **Пули на рівні потоків (Thread-Local Pools).** Кожен потік виконання отримує власний екземпляр `ObjectPool`, збережений у змінній зі специфікатором `thread_local`. Це повністю усуває конкуренцію за ресурси пам'яті (міжпотокові блокування дорівнюють нулю) та забезпечує абсолютну локальність даних у кеші першого рівня (L1 Data Cache) конкретного процесорного ядра.

## Підводні камені та типові пастки реалізації

При самостійній розробці пулів пам'яті та ручному керуванні життєвим циклом найчастіше виникають чотири критичні помилки:

1. **Порушення вимог апаратного вирівнювання (`alignment`).** Кожен тип даних має вимогу щодо кратності адреси `alignof(T)`. Якщо розмістити 64-бітне ціле число або тип `double` за адресою, яка не ділиться на 8, на процесорах архітектури ARM64 чи MIPS відбудеться апаратний збій вирівнювання (*Alignment Fault / SIGBUS*). На архітектурі x86-64 процесор виконає операцію, але витратить додаткові такти на читання двох сусідніх кеш-ліній. Тому буфер `storage_` зобов'язаний мати специфікатор `alignas(alignof(T))`.
2. **Повторне використання слота без деструктора.** Якщо покласти покажчик назад у вільний список або виконати новий `placement new` поверх старого слота без попереднього виклику `std::destroy_at(obj)`, усі ресурси, якими володів попередній екземпляр (відкриті мережеві сокети, дескриптори файлів, динамічні буфери), витечуть назавжди.
3. **Виклик глобального `delete obj` замість повернення в пул.** Оператор `delete` не знає, що об'єкт було розміщено в статичному пулі: він викличе деструктор, а потім передасть адресу слота функції `free()`. Оскільки адреса вказує в середину статичного масиву, а не на блок із системним заголовком купи, станеться миттєвий крах процесу (*Heap Corruption / free(): invalid pointer*).
4. **Подвійне повернення об'єкта в пул (Double Free).** Якщо двічі повернути один і той самий покажчик у метод `destroy()`, у вільному списку `free_head_` виникне кільцеве зациклення. Наступні виклики `create()` почнуть видавати одну й ту саму ділянку пам'яті різним потокам, що спричинить невидиме псування даних. Використання RAII-обгортки `UniquePtr` із власним делетером повністю захищає від цієї помилки завдяки семантиці унікального володіння.
