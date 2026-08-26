# ⚙️ Дослідження, відтворення та усунення витоків пам'яті

Витік динамічної пам'яті рідко з'являється як банально пропущений виклик `free()` у простому лінійному коді. На практиці більшість витоків маскується у неочевидних архітектурних конструкціях: поліморфних класах із невіртуальними деструкторами, неперехоплених виняткових станах під час виділення ресурсів, взаємних циклічних залежностях розумних покажчиків або прихованих витоках у вбудованих системах без підтримки повноцінних операційних систем.

Нижче розглянуто, як відтворити кожен із цих дефектів на практиці, проаналізувати механізм їхнього виникнення на рівні пам'яті та асемблерних інструкцій, побудувати власний трекер алокацій, зафіксувати витоки за допомогою LeakSanitizer та надійно усунути їх із застосуванням ідіом RAII.

### Пастка 1: Невіртуальний деструктор у поліморфній ієрархії

Коли об'єкт похідного класу створюється в динамічній пам'яті через оператор `new`, а керування ним передається покажчику на базовий тип `Base*`, перед програмою постає задача коректного вивільнення всієї ієрархії ресурсів під час виконання `delete ptr`. Якщо деструктор базового класу оголошено без специфікатора `virtual`, компілятор застосовує статичне зв'язування виклику функцій.

На рівні асемблерного коду архітектури x86_64 компілятор генерує пряму інструкцію виклику `call Base::~Base()`, орієнтуючись виключно на статичний тип покажчика. Звернення до вказівника на таблицю віртуальних методів (`vptr`), розташованого за нульовим зміщенням всередині об'єкта, не відбувається. У результаті деструктор похідного класу `Derived::~Derived()` оминається, а всі виділені ним динамічні буфери, сокети чи структури даних залишаються заблокованими в купі назавжди.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Симуляція поліморфізму мовою C через таблицю функцій */
typedef struct Base Base;
typedef struct BaseVTable {
    void (*destroy)(Base *self);
} BaseVTable;

struct Base {
    const BaseVTable *vptr;
    int id;
};

typedef struct Derived {
    Base base;
    char *payload; /* Динамічний буфер */
} Derived;

void base_destroy(Base *self) {
    /* Базовий деструктор не знає про payload нащадка */
    printf("[C Base] Звільнення базової частини id=%d\n", self->id);
    free(self);
}

void derived_destroy(Base *self) {
    Derived *d = (Derived *)self;
    printf("[C Derived] Звільнення буфера payload\n");
    free(d->payload);
    free(d);
}

const BaseVTable base_vtable = { base_destroy };
const BaseVTable derived_vtable = { derived_destroy };

Base *create_derived(int id, const char *text) {
    Derived *d = (Derived *)malloc(sizeof(Derived));
    if (!d) return NULL;
    d->base.vptr = &derived_vtable;
    d->base.id = id;
    d->payload = (char *)malloc(strlen(text) + 1);
    if (!d->payload) { free(d); return NULL; }
    strcpy(d->payload, text);
    return (Base *)d;
}

int main(void) {
    Base *obj = create_derived(101, "Поліморфне повідомлення");
    
    /* ПОМИЛКА: прямий виклик base_destroy замість диспетчеризації через vptr */
    base_destroy(obj); /* d->payload витікає! */
    return 0;
}
```
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <vector>

/* Демонстрація помилки та виправлення в C++ */
class BadBase {
public:
    int id{0};
    ~BadBase() { std::cout << "[BadBase] Деструктор базового класу\n"; }
};

class BadDerived : public BadBase {
public:
    std::vector<int> data;
    BadDerived() : data(10000, 42) {}
    ~BadDerived() { std::cout << "[BadDerived] Деструктор нащадка\n"; }
};

class GoodBase {
public:
    int id{0};
    /* Віртуальний деструктор гарантує виклик деструктора нащадка */
    virtual ~GoodBase() = default;
};

class GoodDerived : public GoodBase {
public:
    std::vector<int> data;
    GoodDerived() : data(10000, 42) {}
    ~GoodDerived() override { std::cout << "[GoodDerived] Деструктор нащадка (очищено 40 KB)\n"; }
};

int main() {
    std::cout << "--- Тест 1: Невіртуальний деструктор (витік) ---\n";
    BadBase *bad = new BadDerived();
    delete bad; // ВИКЛИКАЄТЬСЯ лише ~BadBase()! data витікає.

    std::cout << "\n--- Тест 2: Віртуальний деструктор + RAII (безпечно) ---\n";
    std::unique_ptr<GoodBase> good = std::make_unique<GoodDerived>();
    // Автоматично і коректно викличе ~GoodDerived(), а потім ~GoodBase()
    return 0;
}
```
:::

У коректному варіанті оголошення `virtual ~GoodBase() = default;` створює запис у таблиці віртуальних функцій класу. Коли виконується знищення об'єкта, середовище виконання зчитує адресу віртуальної таблиці за вказівником `vptr` у заголовку об'єкта, з'ясовує його реальний тип `GoodDerived` і викликає деструктор нащадка. Після очищення динамічного масиву `data` автоматично викликається деструктор базового класу, забезпечуючи повне каскадне звільнення пам'яті.

---

### Пастка 2: Витік через винятки та перехід на RAII

Якщо між виділенням сирої динамічної пам'яті та її звільненням виникає помилка, генерація винятку або виклик `longjmp`, нормальний потік виконання переривається. Під час розгортання стека локальні змінні-покажчики знищуються без виклику будь-якого очищення, перетворюючи виділену пам'ять на недосяжні втрачені блоки.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

int process_data(const int *buf, size_t size) {
    if (size == 0) return -1; /* Помилка вхідних даних */
    int sum = 0;
    for (size_t i = 0; i < size; ++i) sum += buf[i];
    return sum;
}

int calculate(size_t n) {
    int *buffer = (int *)malloc(n * sizeof(int));
    if (!buffer) return -1;

    /* Імітація обробки даних */
    for (size_t i = 0; i < n; ++i) buffer[i] = (int)(i * 2);

    int result = process_data(buffer, 0); // Повертає -1 (помилка)
    if (result < 0) {
        /* ПОМИЛКА: Раннє повернення без виклику free(buffer) */
        return -1; 
    }

    free(buffer);
    return result;
}

int main(void) {
    int res = calculate(1024);
    printf("Результат: %d (пам'ять 4 KB витекла через ранній return)\n", res);
    return 0;
}
```
```cpp
#include <iostream>
#include <memory>
#include <vector>
#include <stdexcept>

void risky_operation(const std::vector<int> &vec) {
    if (vec.empty() || vec[0] == 0) {
        throw std::runtime_error("Критична помилка вхідного масиву");
    }
}

void safe_calculate(size_t n) {
    /* Автоматичне керування пам'яттю через std::vector (RAII) */
    std::vector<int> buffer(n, 0);
    
    /* Навіть якщо функція згенерує виняток, деструктор std::vector
       гарантовано поверне всю пам'ять купі під час розкрутки стека */
    risky_operation(buffer);
}

int main() {
    try {
        safe_calculate(1024);
    } catch (const std::exception &ex) {
        std::cout << "Перехоплено виняток: " << ex.what() 
                  << "\nПам'ять звільнено автоматично без жодного витоку!\n";
    }
    return 0;
}
```
:::

Перехід від сирих покажчиків до стандартних контейнерів `std::vector` або розумних покажчиків `std::unique_ptr` перетворює пам'ять на автоматичний ресурс. Механізм розкрутки стека (Stack Unwinding) гарантує, що деструктори всіх локальних об'єктів на стеку будуть викликані у зворотному порядку їхнього створення незалежно від того, як саме завершилася функція: нормальним поверненням чи генерацією винятку.

---

### Пастка 3: Циклічні посилання та розрив через `std::weak_ptr`

Розумний покажчик `std::shared_ptr` керує життєвим циклом об'єкта через спільний блок керування (Control Block), що містить атомарний лічильник сильних власників (`use_count`). Пам'ять об'єкта звільняється тоді й лише тоді, коли лічильник сильних посилань зменшується до нуля.

Якщо два або більше об'єктів утримують сильні посилання один на одного, виникає циклічна залежність. Кожен об'єкт має щонайменше одного сильного власника в особі свого сусіда по циклу. Навіть коли зовнішні стекові покажчики виходять з області видимості, лічильники кожного вузла залишаються рівними одиниці, унеможливлюючи виклик деструкторів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>

/* Вузли графа з ручним підрахунком посилань */
typedef struct Node Node;
struct Node {
    int value;
    int ref_count;
    Node *neighbor;
};

Node *node_create(int val) {
    Node *n = (Node *)malloc(sizeof(Node));
    if (!n) return NULL;
    n->value = val;
    n->ref_count = 1;
    n->neighbor = NULL;
    return n;
}

void node_release(Node *n) {
    if (!n) return;
    n->ref_count--;
    if (n->ref_count == 0) {
        if (n->neighbor) {
            node_release(n->neighbor);
        }
        printf("[C Node] Звільнено вузол %d\n", n->value);
        free(n);
    }
}

int main(void) {
    Node *a = node_create(1);
    Node *b = node_create(2);

    /* Створення циклічного посилання: A -> B і B -> A */
    a->neighbor = b;
    b->ref_count++;
    b->neighbor = a;
    a->ref_count++;

    /* Спроба звільнення */
    node_release(a);
    node_release(b);
    /* Обидва вузли залишаються з ref_count == 1, пам'ять витекла */
    return 0;
}
```
```cpp
#include <iostream>
#include <memory>

struct BadNode {
    int value;
    std::shared_ptr<BadNode> next;
    ~BadNode() { std::cout << "[BadNode] Знищено " << value << "\n"; }
};

struct GoodNode {
    int value;
    /* Слабке посилання std::weak_ptr не збільшує лічильник сильних власників */
    std::weak_ptr<GoodNode> next;
    ~GoodNode() { std::cout << "[GoodNode] Знищено " << value << "\n"; }
};

int main() {
    std::cout << "--- Циклічне посилання shared_ptr (витік) ---\n";
    {
        auto a = std::make_shared<BadNode>(BadNode{1, nullptr});
        auto b = std::make_shared<BadNode>(BadNode{2, nullptr});
        a->next = b;
        b->next = a; // Цикл! Лічильники обох = 2. При виході з блоку лічильники стануть 1.
    } // Деструктори НЕ викликаються!

    std::cout << "\n--- Розрив циклу через weak_ptr (успішне звільнення) ---\n";
    {
        auto a = std::make_shared<GoodNode>(GoodNode{1, {}});
        auto b = std::make_shared<GoodNode>(GoodNode{2, {}});
        a->next = b;
        b->next = a; // Слабке посилання!
    } // Обидва вузли успішно знищуються автоматично.
    return 0;
}
```
:::

Використання слабкого покажчика `std::weak_ptr` розриває цикл володіння: слабке посилання спостерігає за об'єктом, але збільшує лише окремий допоміжний лічильник `weak_count` у блоці керування. Коли останній `std::shared_ptr` виходить з області видимості, `use_count` падає до нуля, і об'єкт негайно та безпечно знищується.

---

### Пастка 4: Власний трекер алокацій для вбудованих систем

У мікроконтролерах та спеціалізованих операційних системах реального часу (RTOS), де компіляторні санітайзери не підтримуються через обмеженість апаратних ресурсів або відсутність віртуальної пам'яті, застосовують легковагі макроси перехоплення виділень. Розгляньмо базову реалізацію діагностичної таблиці, що записує точку створення кожного блоку за допомогою службових макросів `__FILE__` та `__LINE__` або стандарту C++20 `std::source_location`:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>

typedef struct AllocRecord {
    void *ptr;
    size_t size;
    const char *file;
    int line;
} AllocRecord;

#define MAX_TRACKED_ALLOCS 64
static AllocRecord g_alloc_table[MAX_TRACKED_ALLOCS];
static size_t g_alloc_count = 0;

void *debug_malloc(size_t size, const char *file, int line) {
    void *ptr = malloc(size);
    if (ptr && g_alloc_count < MAX_TRACKED_ALLOCS) {
        g_alloc_table[g_alloc_count++] = (AllocRecord){ ptr, size, file, line };
    }
    return ptr;
}

void debug_free(void *ptr) {
    if (!ptr) return;
    for (size_t i = 0; i < g_alloc_count; ++i) {
        if (g_alloc_table[i].ptr == ptr) {
            g_alloc_table[i] = g_alloc_table[--g_alloc_count];
            break;
        }
    }
    free(ptr);
}

void check_leaks_on_exit(void) {
    if (g_alloc_count == 0) {
        printf("[Аудит] Витоків пам'яті не виявлено.\n");
        return;
    }
    printf("[Аудит ПОМИЛКА] Знайдено %zu незвільнених виділень:\n", g_alloc_count);
    for (size_t i = 0; i < g_alloc_count; ++i) {
        printf("  - %zu байтів за адресою %p у %s:%d\n",
               g_alloc_table[i].size, g_alloc_table[i].ptr,
               g_alloc_table[i].file, g_alloc_table[i].line);
    }
}

#define malloc(s) debug_malloc(s, __FILE__, __LINE__)
#define free(p) debug_free(p)

int main(void) {
    int *p1 = (int *)malloc(64);
    int *p2 = (int *)malloc(128);
    free(p1);
    /* p2 навмисно не звільняється */
    check_leaks_on_exit();
    free(p2);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <source_location>

struct AllocationInfo {
    void *address{nullptr};
    std::size_t bytes{0};
    std::string_view filename;
    std::uint32_t line_number{0};
};

class EmbeddedLeakTracker {
    static inline std::vector<AllocationInfo> records;
public:
    static void *track_alloc(std::size_t size, const std::source_location loc = std::source_location::current()) {
        void *p = std::malloc(size);
        if (p) {
            records.push_back({ p, size, loc.file_name(), loc.line() });
        }
        return p;
    }

    static void track_free(void *p) noexcept {
        if (!p) return;
        for (auto it = records.begin(); it != records.end(); ++it) {
            if (it->address == p) {
                records.erase(it);
                break;
            }
        }
        std::free(p);
    }

    static void report() {
        if (records.empty()) {
            std::cout << "[C++ Трекер] Усі ресурси чисто повернуто.\n";
            return;
        }
        std::cout << "[C++ Трекер] Виявлено " << records.size() << " витоків:\n";
        for (const auto &rec : records) {
            std::cout << "  - " << rec.bytes << " байтів у " 
                      << rec.filename << ":" << rec.line_number << "\n";
        }
    }
};

int main() {
    void *chunk1 = EmbeddedLeakTracker::track_alloc(64);
    void *chunk2 = EmbeddedLeakTracker::track_alloc(128);
    EmbeddedLeakTracker::track_free(chunk1);
    // chunk2 не звільняється
    EmbeddedLeakTracker::report();
    EmbeddedLeakTracker::track_free(chunk2);
    return 0;
}
```
:::

Цей підхід дозволяє перехоплювати розмір, адресу та точне місце виділення кожного блоку в коді. При завершенні тестового сценарію або перед перезапуском сторожового таймера функція аудиту перевіряє залишкову кількість активних записів у таблиці й миттєво локалізує координати забутого виділення.

---

### Автоматична діагностика за допомогою LeakSanitizer

Для промислового виявлення витоків пам'яті під час виконання автоматизованих тестів компілятори Clang та GCC надають високоефективний вбудований санітайзер. Скомпілюйте проект із прапорами `-fsanitize=leak -g -fno-omit-frame-pointer`:

```bash
clang++ -std=c++20 -fsanitize=leak -g -fno-omit-frame-pointer main.cpp -o leak_detector_app
./leak_detector_app
```

Прапор `-fno-omit-frame-pointer` є обов'язковим для точного розгортання стеків: він змушує компілятор зберігати базовий вказівник кадру `rbp` на стеку, що дозволяє санітайзеру миттєво зчитувати послідовність адрес повернення функцій без звернення до важких таблиць розгортання винятків DWARF `.eh_frame`.

Якщо програма містить хоча б один незвільнений блок пам'яті, LeakSanitizer під час виходу з програми автоматично роздрукує звіт про стан пам'яті:

```
=================================================================
==18492==ERROR: LeakSanitizer: detected memory leaks

Direct leak of 40000 byte(s) in 1 object(s) allocated from:
    #0 0x55d21a in operator new(unsigned long)
    #1 0x55d34a in main /src/main.cpp:25:20
    #2 0x7f8a1e in __libc_start_main (/lib/x86_64-linux-gnu/libc.so.6+0x29d90)

SUMMARY: LeakSanitizer: 40000 byte(s) leaked in 1 allocation(s).
```

Звіт містить точний розмір втраченого блоку (40000 байтів) та номер рядка вихідного коду (`/src/main.cpp:25`), де було викликано оператор виділення пам'яті `new`. Це усуває необхідність ручного трасування адрес і дозволяє локалізувати джерело проблеми за лічені секунди.
