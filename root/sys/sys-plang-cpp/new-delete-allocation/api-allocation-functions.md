# 📋 Повна довідка сигнатур operator new і operator delete

Коли низькорівнева бібліотека або системний сервіс перехоплює виділення пам'яті в C++, помилка у сигнатурі хоча б однієї форми оператора виділення призводить до того, що частина запитів піде повз власний розподільник, а виклики звільнення спричинять пошкодження пам'яті. Стандарт C++ визначає розгалужену родину глобальних та класових функцій розподілу й деалокації, що еволюціонувала від трьох базових пар у C++98 до понад двох десятків спеціалізованих версій у C++17 та C++20.

Нижче наведено вичерпний контракт усіх стандартних функцій розподілу пам'яті: їхні точні сигнатури, правила заміни користувачем, гарантії вирівнювання, специфікації винятків, C++20 destroying delete, прапори компіляції, взаємодію з санітайзерами (ASan/Valgrind), зв'язок із концепцією PMR та взаємодію з підсистемами багатопотоковості.

## Систематизація форм виділення та звільнення

Усі функції сімейства `operator new` та `operator delete` поділяються на шість функціональних груп:

1. **Замінні глобальні функції за замовчуванням (Replaceable Global Defaults)** — реалізації, які стандартна бібліотека надає автоматично і які будь-яка програма може перекрити власним визначенням без порушення ODR (One Definition Rule).
2. **Форми без викидання винятків (Non-throwing Overloads, std::nothrow)** — версії, що замість `std::bad_alloc` повертають нульовий покажчик `nullptr` у разі вичерпання пам'яті.
3. **Розмірне звільнення (Sized Deallocation, C++14)** — функції деалокації, що отримують точний розмір типу об'єкта під час знищення.
4. **Вирівняне виділення (Aligned Allocation, C++17)** — функції для типів із вирівнюванням, що перевищує базове значення платформового алокатора (`alignof(T) > __STDCPP_DEFAULT_NEW_ALIGNMENT__`).
5. **Знищувальне звільнення (Destroying Delete, C++20)** — функції класової деалокації, які перебирають на себе виклик деструктора об'єкта.
6. **Незмінні функції розміщення (Placement New/Delete)** — вбудовані форми, які не виділяють і не звільняють байти, а лише передають адресу; їхнє перевантаження користувачем прямо заборонено стандартом.

## 1. Базові замінні глобальні оператори (C++98 / C++11)

Ці вісім функцій складають історичний фундамент динамічного виділення в C++. Якщо програма замінює одну з них, компонувальник підставляє користувацьку версію для всього двійкового модуля.

### Сигнатури виділення пам'яті для одиночних об'єктів та масивів

```cpp
// Звичайне виділення одиночного об'єкта (викидає std::bad_alloc)
void* operator new(std::size_t size);

// Звичайне виділення масиву (викидає std::bad_alloc)
void* operator new[](std::size_t size);

// Non-throwing версія для одиночного об'єкта (повертає nullptr при помилці)
void* operator new(std::size_t size, const std::nothrow_t&) noexcept;

// Non-throwing версія для масиву (повертає nullptr при помилці)
void* operator new[](std::size_t size, const std::nothrow_t&) noexcept;
```

### Сигнатури звільнення пам'яті

```cpp
// Звичайне звільнення одиночного об'єкта
void operator delete(void* ptr) noexcept;

// Звичайне звільнення масиву
void operator delete[](void* ptr) noexcept;

// Non-throwing парний деалокатор одиночного об'єкта
void operator delete(void* ptr, const std::nothrow_t&) noexcept;

// Non-throwing парний деалокатор масиву
void operator delete[](void* ptr, const std::nothrow_t&) noexcept;
```

### Контракт виконання та вимоги стандарту

* **Параметр `size`:** кількість байтів для виділення. Якщо `size == 0`, функція зобов'язана виділити блок ненульового розміру (щонайменше 1 байт), щоб повернути валідну, унікальну адресу, відмінну від будь-якого іншого активного покажчика. Це необхідно для коректного порівняння покажчиків на порожні об'єкти (Empty Base Optimization).
* **Повернене значення:** вказівник на перший байт виділеної ділянки пам'яті, вирівняний щонайменше за значенням `alignof(std::max_align_t)` (зазвичай 8 байтів на 32-бітних і 16 байтів на 64-бітних архітектурах).
* **Параметр `ptr`:** адреса, раніше отримана від відповідної функції `operator new`. Якщо `ptr == nullptr`, функція деалокації зобов'язана негайно повернути керування без виконання жодних дій.
* **Цикл виділення та new-handler:** при невдалій спробі отримати пам'ять звичайна версія зобов'язана викликати поточний `std::new_handler` у циклі. Якщо обробник не встановлено, функція генерує виняток `std::bad_alloc`. Версія `nothrow` перехоплює `std::bad_alloc` і повертає `nullptr`.

## 2. Оператори розмірного звільнення (Sized Deallocation, C++14)

Стандарт C++14 стандартизував передачу розміру блоку у функцію звільнення. Це дозволило розподільникам пам'яті миттєво знаходити потрібний пул розмірного класу без читання службових заголовків із пам'яті.

### Сигнатури Sized Delete

```cpp
// Розмірне звільнення одиночного об'єкта (C++14)
void operator delete(void* ptr, std::size_t size) noexcept;

// Розмірне звільнення масиву (C++14)
void operator delete[](void* ptr, std::size_t size) noexcept;
```

### Правила вибору компілятором та поведінковий контракт

* **Пріоритет виклику:** якщо в програмі визначено як нерозмірну форму `operator delete(void*)`, так і розмірну форму `operator delete(void*, std::size_t)`, компілятор C++14 і новіших стандартів надає безумовну перевагу розмірній формі, коли розмір типу відомий під час компіляції.
* **Поліморфне знищення:** якщо базовий клас має віртуальний деструктор, точне значення `size` обчислюється динамічно на основі таблиці віртуальних методів найпохіднішого типу (most derived type). Якщо віртуальний деструктор відсутній, компілятор передасть розмір базового класу `sizeof(Base)`, що спричинить розпад пулу алокатора, якщо реальний об'єкт належав похідному класу `Derived`.
* **Вимога сумісності:** кастомна реалізація розмірного видалення зобов'язана коректно звільняти пам'ять, навіть якщо переданий аргумент `size` використовується лише для верифікації (наприклад, через `assert(size == expected)`).

## 3. Оператори вирівняного виділення (Aligned Allocation, C++17)

До появи C++17 типи з вирівнюванням, більшим за стандартне (`alignas(32)`, `alignas(64)` для векторних регістрів SSE/AVX/NEON), не могли безпечно розміщуватися у динамічній пам'яті через стандартний `new`. C++17 ввів спеціальний тип-перелік `std::align_val_t`, який передає вимогу до кратності адреси безпосередньо у функцію виділення.

### Сигнатури вирівняного виділення

```cpp
#include <new>

// Вирівняне виділення одиночного об'єкта (викидає std::bad_alloc)
void* operator new(std::size_t size, std::align_val_t alignment);

// Вирівняне виділення масиву (викидає std::bad_alloc)
void* operator new[](std::size_t size, std::align_val_t alignment);

// Вирівняне non-throwing виділення одиночного об'єкта
void* operator new(std::size_t size, std::align_val_t alignment, const std::nothrow_t&) noexcept;

// Вирівняне non-throwing виділення масиву
void* operator new[](std::size_t size, std::align_val_t alignment, const std::nothrow_t&) noexcept;
```

### Сигнатури вирівняного звільнення пам'яті

```cpp
// Звичайне вирівняне звільнення одиночного об'єкта
void operator delete(void* ptr, std::align_val_t alignment) noexcept;

// Звичайне вирівняне звільнення масиву
void operator delete[](void* ptr, std::align_val_t alignment) noexcept;

// Non-throwing вирівняне звільнення одиночного об'єкта
void operator delete(void* ptr, std::align_val_t alignment, const std::nothrow_t&) noexcept;

// Non-throwing вирівняне звільнення масиву
void operator delete[](void* ptr, std::align_val_t alignment, const std::nothrow_t&) noexcept;

// Розмірне вирівняне звільнення одиночного об'єкта (C++17)
void operator delete(void* ptr, std::size_t size, std::align_val_t alignment) noexcept;

// Розмірне вирівняне звільнення масиву (C++17)
void operator delete[](void* ptr, std::size_t size, std::align_val_t alignment) noexcept;
```

### Правила активації Aligned Forms

Компілятор обирає вирівняні форми автоматично тоді й лише тоді, коли вирівнювання типу `T` строго перевищує константу `__STDCPP_DEFAULT_NEW_ALIGNMENT__`:

```cpp
alignas(64) struct CacheLineAlignedData {
    float values[16];
};

// Компілятор транслює у: operator new(sizeof(CacheLineAlignedData), std::align_val_t(64))
CacheLineAlignedData* data = new CacheLineAlignedData();

// Компілятор транслює у: operator delete(data, sizeof(CacheLineAlignedData), std::align_val_t(64))
delete data;
```

Якщо тип має вирівнювання, менше або рівне за замовчуванням, використання `std::align_val_t` не активується, і компілятор генерує звичайний виклик `operator new(size)`.

## 4. Знищувальне звільнення: std::destroying_delete_t (C++20)

У стандартних виразах `delete ptr` компілятор завжди виконує дві жорстко зв'язані фази: спочатку генерує виклик деструктора `ptr->~T()`, а потім викликає `operator delete`. Проте існують архітектурні патерни, де об'єкт повинен сам керувати моментом знищення власних полів або знищувати хвостові дані змінної довжини (Flexible Array Members / tail allocation).

Стандарт C++20 ввів механізм **destroying delete**, що дозволяє класу перехопити керування деструкцією:

```cpp
#include <new>
#include <cstddef>
#include <iostream>

struct VariableSizedNode {
    std::size_t payload_size;

    // Класова функція деалокації зі спеціальним маркером destroying_delete_t
    static void operator delete(VariableSizedNode* ptr, std::destroying_delete_t) noexcept {
        std::cout << "Перехоплено знищення: розмір корисного навантаження = " << ptr->payload_size << '\n';
        
        // Розробник САМ зобов'язаний явно викликати деструктор!
        std::size_t total_bytes = sizeof(VariableSizedNode) + ptr->payload_size;
        ptr->~VariableSizedNode();

        // Звільнення блоку пам'яті потрібного динамічного розміру
        ::operator delete(static_cast<void*>(ptr), total_bytes);
    }
};
```

Коли для класу з таким методом виконується вираз `delete ptr;`, компілятор **не викликає деструктор автоматично**, а одразу передає типізований покажчик `VariableSizedNode*` у функцію `operator delete`. Відповідальність за явний виклик `ptr->~T()` повністю покладається на розробника функції.

## 5. Вбудовані функції Placement New (Незмінні)

Форми розміщення визначені в стандартному заголовку `<new>` як інлайн-функції. Їхнє перевантаження у глобальному просторі імен є помилкою компіляції або призводить до невизначеної поведінки.

```cpp
// Placement new для одиночного об'єкта
void* operator new(std::size_t size, void* ptr) noexcept;

// Placement new для масиву
void* operator new[](std::size_t size, void* ptr) noexcept;

// Placement delete для одиночного об'єкта (викликається лише при винятку в конструкторі)
void operator delete(void* ptr, void* place) noexcept;

// Placement delete для масиву (викликається лише при винятку в конструкторі)
void operator delete[](void* ptr, void* place) noexcept;
```

Реалізація цих функцій тривіальна: вони просто повертають параметр `ptr`, не виконуючи жодних звернень до розподільника пам'яті. Відповідні функції `operator delete` мають порожнє тіло: вони існують виключно для того, щоб компілятор міг виконати парний відкат у разі виникнення винятку в конструкторі під час виконання виразу placement new.

## 6. Перевантаження операторів на рівні класу

Класи мають право визначати власні статичні функції розподілу й звільнення. Вони мають вищий пріоритет видимості над глобальними операторами.

### Допустимі сигнатури всередині класу

```cpp
class CustomNode {
public:
    // Одиночні форми виділення
    static void* operator new(std::size_t size);
    static void* operator new(std::size_t size, const std::nothrow_t&) noexcept;
    static void* operator new(std::size_t size, std::align_val_t align);

    // Масивні форми виділення
    static void* operator new[](std::size_t size);
    static void* operator new[](std::size_t size, std::align_val_t align);

    // Одиночні форми звільнення
    static void operator delete(void* ptr) noexcept;
    static void operator delete(void* ptr, std::size_t size) noexcept;
    static void operator delete(void* ptr, std::align_val_t align) noexcept;
    static void operator delete(void* ptr, std::size_t size, std::align_val_t align) noexcept;

    // Масивні форми звільнення
    static void operator delete[](void* ptr) noexcept;
    static void operator delete[](void* ptr, std::size_t size) noexcept;
};
```

### Правила успадкування та приховування імен (Name Hiding)

* **Статичний контекст:** навіть якщо ключове слово `static` пропущене, методи `operator new` і `operator delete` у класі завжди є статичними. Вони не мають доступу до полів `this`.
* **Приховування імен:** якщо клас оголошує хоча б один `operator new`, усі інші глобальні форми (включно з `new[]` та `nothrow`) стають прихованими для цього класу, доки вони не будуть явно відновлені через `using ::operator new;` або перевизначені вручну.
* **Успадкування:** похідні класи успадковують оператори виділення від базового класу. Якщо похідний клас більший за базовий, переданий у `T::operator new(size)` параметр `size` міститиме реальний розмір похідного класу `sizeof(Derived)`.

## 7. Інтерфейс керування помилками: new_handler API

Стандартний заголовок `<new>` надає механізм реєстрації функцій зворотного виклику, що активуються в моменти критичного вичерпання пам'яті.

```cpp
namespace std {
    // Тип функції обробника відмови виділення пам'яті
    using new_handler = void (*)();

    // Встановлює новий обробник і повертає попередній
    new_handler set_new_handler(new_handler new_p) noexcept;

    // Повертає поточний активний обробник (C++11)
    new_handler get_new_handler() noexcept;

    // Базовий виняток відмови виділення пам'яті
    class bad_alloc : public exception {
    public:
        bad_alloc() noexcept;
        bad_alloc(const bad_alloc&) noexcept;
        bad_alloc& operator=(const bad_alloc&) noexcept;
        virtual const char* what() const noexcept override;
    };

    // Виняток невідповідності розміру масиву (C++11)
    class bad_array_new_length : public bad_alloc {
    public:
        bad_array_new_length() noexcept;
        virtual const char* what() const noexcept override;
    };

    // Маркерний тип для non-throwing перевантажень
    struct nothrow_t { explicit nothrow_t() = default; };
    extern const nothrow_t nothrow;

    // Тип-перелік для передачі вирівнювання (C++17)
    enum class align_val_t : size_t {};
}
```

### Контракт поведінки std::new_handler

Коли `operator new` не може задовольнити запит на пам'ять, він виконує цикл:

```cpp
while (true) {
    void* p = try_allocate(size);
    if (p) return p;

    std::new_handler handler = std::get_new_handler();
    if (!handler) {
        throw std::bad_alloc();
    }
    handler(); // Виклик користувацького обробника
}
```

Обробник `std::new_handler` зобов'язаний виконати одну з таких чотирьох дій:
1. **Звільнити пам'ять:** звільнити раніше зарезервовані буфери або кеші й повернути керування, дозволивши циклу в `operator new` повторити спробу.
2. **Встановити наступний обробник:** викликати `std::set_new_handler` з іншою функцією обробки.
3. **Вимкнути обробку:** викликати `std::set_new_handler(nullptr)`, сигналізуючи, що наступна ітерація циклу має негайно згенерувати `std::bad_alloc`.
4. **Завершити виконання або викинути виняток:** викинути `std::bad_alloc` або викликати функцію аварійного завершення `std::terminate()`.

## 8. Від глобальних операторів до PMR та Allocator Traits

У сучасній архітектурі стандартної бібліотеки C++ існує чітке розділення між глобальним виділенням через `operator new` та локалізованими алокаторами контейнерів:

* **Стандартні контейнери STL** (`std::vector`, `std::map`) за замовчуванням використовують шаблон `std::allocator<T>`, який під капотом звертається до глобальних функцій `::operator new` та `::operator delete`.
* **Інтерфейс std::allocator_traits:** абстрагує операції виділення сирої пам'яті (`traits::allocate(alloc, count)`) від конструювання об'єктів (`traits::construct(alloc, ptr, args...)`). Конструювання виконується через placement new безпосередньо у виділених слотах пам'яті.
* **Polymorphic Memory Resources (std::pmr, C++17):** дозволяє контейнерам використовувати динамічно підключені ресурси пам'яті (`std::pmr::memory_resource`) без зміни типу самого контейнера. Базові класи `monotonic_buffer_resource`, `unsynchronized_pool_resource` та `synchronized_pool_resource` виділяють великі сегменти пам'яті через глобальний `operator new`, а потім розподіляють їх між дрібними об'єктами без системних блокувань.

## 9. Взаємодія з інструментами діагностики (ASan, Valgrind)

Інструменти динамічного аналізу пам'яті (AddressSanitizer та Valgrind Memcheck) перехоплюють стандартні оператори виділення та звільнення пам'яті на рівні компілятора та системного завантажувача (через LD_PRELOAD):

* **Тіньова пам'ять (Shadow Memory):** при виклику `operator new` AddressSanitizer виділяє додаткові червоні зони (redzones) навколо отриманого блоку й помічає їх у тіньовій пам'яті як заборонені для читання та запису.
* **Перевірка парності викликів:** ASan відстежує, яка саме функція виділила блок (`operator new` чи `operator new[]`). Якщо блок, виділений через `new[]`, звільняється через `delete`, ASan генерує помилку `alloc-dealloc-mismatch (operator new [] vs operator delete)`.
* **Виявлення висячих покажчиків:** при виклику `operator delete` блок негайно поміщається в карантин (quarantine queue), а його байти помічаються в тіньовій пам'яті як звільнені (poisoned). Будь-яка наступна спроба читання чи запису за цим покажчиком миттєво призводить до зупинки процесу з діагностичним звітом `use-after-free`.

## 10. Статична ініціалізація та життєвий цикл алокатора

Особлива вимога до користувацьких замінних функцій виділення полягає у їхній працездатності під час фази **статичної динамічної ініціалізації** (до виклику функції `main()`):

* **Ініціалізація глобальних об'єктів:** глобальні об'єкти стандартної бібліотеки (зокрема `std::cout`, `std::cin` та структури локалей) можуть виділяти динамічну пам'ять ще до того, як конструктори глобальних змінних користувача почнуть виконуватися.
* **Вимога до простоти стану:** кастомний глобальний `operator new` не повинен покладатися на складні глобальні об'єкти C++ (наприклад, `std::mutex` або потоки `std::ofstream`), якщо вони самі потребують динамічного виділення для власної ініціалізації. Інакше виникає нескінченна рекурсія викликів виділення пам'яті (Deadly Allocation Cycle) до старту програми.
* **Фаза руйнування (Static Destruction):** після виходу з функції `main()` глобальні деструктори продовжують звільняти пам'ять. Кастомний алокатор зобов'язаний залишатися повністю працездатним аж до завершення роботи останнього деструктора середовища виконання C++.

## 11. Прапори компілятора та діагностика виділень

Різні компілятори надають прапори для керування генерацією викликів розмірного та вирівняного виділення:

* **Clang / GCC:**
  * `-fsized-deallocation` — примусово вмикає генерацію викликів `operator delete(void*, std::size_t)` (увімкнено за замовчуванням у C++14).
  * `-fno-sized-deallocation` — вимикає розмірне видалення для сумісності зі застарілими версіями jemalloc або бібліотеками, де розмірний деалокатор не реалізовано.
  * `-faligned-allocation` — активує підтримку `std::align_val_t` (за замовчуванням у C++17).
* **MSVC (Visual C++):**
  * `/Zc:sizedDealloc` — вмикає підтримку sized deallocation у режимі сумісності з C++14.
  * `/Zc:alignedNew` — вмикає вирівняне виділення пам'яті для типів `alignas(N)`.

## 12. Багатопотоковість, символи ABI та компонування

Стандарт C++ накладає строгі вимоги щодо потокобезпеки та компонування на всі глобальні функції виділення та звільнення пам'яті:

* **Відсутність гонок даних (Data Races):** одночасні виклики `operator new` та `operator delete` з різних потоків виконання не повинні призводити до гонок даних. Системний алокатор зобов'язаний самостійно забезпечувати внутрішню синхронізацію.
* **Синхронізація звільнення та повторного виділення:** звільнення пам'яті в одному потоці через `operator delete(p)` синхронізується з наступним успішним виділенням того самого блоку через `operator new` в іншому потоці (happens-before relationship). Це гарантує, що стан пам'яті після деструктора стає видимим для наступного конструктора.
* **Специфікація noexcept:** усі функції сімейства `operator delete` зобов'язані мати специфікатор `noexcept`. Викидання будь-якого винятку з функції деалокації під час розкрутки стека миттєво викликає `std::terminate()`.
* **Символи ABI та компонування:** у форматі ELF (Linux) глобальні оператори виділення позначені як слабкі символи (weak symbols). Якщо застосунок надає власне визначення, компонувальник перекриває ними символи зі стандартної `libstdc++` або `libc++`. На платформі Windows (MSVC) глобальні оператори виділення лінкуються статично в образ CRT, тому їхнє перекриття у DLL вимагає обережності, щоб уникнути виділення пам'яті в одному модулі та звільнення в іншому.

## 13. Шаблон реалізації повного набору замінних операторів

Щоб коректно реалізувати власний трекер або підключити сторонній алокатор, програма повинна надати узгоджений набір усіх 12 замінних форм:

```cpp
#include <new>
#include <cstdlib>

// Базові форми
void* operator new(std::size_t size) {
    if (size == 0) size = 1;
    while (void* p = std::malloc(size)) {
        return p;
    }
    if (auto h = std::get_new_handler()) { h(); return operator new(size); }
    throw std::bad_alloc();
}

void* operator new[](std::size_t size) { return ::operator new(size); }

void operator delete(void* ptr) noexcept { std::free(ptr); }
void operator delete[](void* ptr) noexcept { ::operator delete(ptr); }

// Sized forms (C++14)
void operator delete(void* ptr, std::size_t) noexcept { ::operator delete(ptr); }
void operator delete[](void* ptr, std::size_t) noexcept { ::operator delete[](ptr); }

// Aligned forms (C++17)
void* operator new(std::size_t size, std::align_val_t al) {
    if (size == 0) size = 1;
    std::size_t align = static_cast<std::size_t>(al);
    void* ptr = nullptr;
#if defined(_MSC_VER)
    ptr = _aligned_malloc(size, align);
#else
    if (posix_memalign(&ptr, align, size) != 0) ptr = nullptr;
#endif
    if (ptr) return ptr;
    if (auto h = std::get_new_handler()) { h(); return operator new(size, al); }
    throw std::bad_alloc();
}

void* operator new[](std::size_t size, std::align_val_t al) { return ::operator new(size, al); }

void operator delete(void* ptr, std::align_val_t) noexcept {
#if defined(_MSC_VER)
    _aligned_free(ptr);
#else
    std::free(ptr);
#endif
}

void operator delete[](void* ptr, std::align_val_t al) noexcept { ::operator delete(ptr, al); }
void operator delete(void* ptr, std::size_t, std::align_val_t al) noexcept { ::operator delete(ptr, al); }
void operator delete[](void* ptr, std::size_t, std::align_val_t al) noexcept { ::operator delete[](ptr, al); }
```

## Зведена таблиця пріоритетів вибору deallocation function

Коли компілятор генерує код для виразу `delete ptr`, пошук відповідної функції звільнення виконується за строгою ієрархією пріоритетів:

| Критерій типу об'єкта | Пріоритет 1 (Найвищий) | Пріоритет 2 | Пріоритет 3 |
| :--- | :--- | :--- | :--- |
| **Клас із destroying delete (C++20)** | `T::operator delete(ptr, std::destroying_delete)` | — | — |
| **Клас із власним operator delete** | Член класу `T::operator delete(ptr, size)` | Член класу `T::operator delete(ptr)` | Глобальний `::operator delete` |
| **Over-aligned тип** (`alignof(T) > default`) | `operator delete(ptr, size, align)` (C++17) | `operator delete(ptr, align)` (C++17) | `operator delete(ptr, size)` |
| **Звичайний тип** (`alignof(T) <= default`) | `operator delete(ptr, size)` (C++14) | `operator delete(ptr)` (C++98) | — |
| **Масив об'єктів** (`delete[] arr`) | `operator delete[](ptr, size)` (C++14) | `operator delete[](ptr)` (C++98) | — |

Точне дотримання цих сигнатур та їхніх контрактів гарантує повну сумісність користувацьких алокаторів із оптимізаціями компілятора та запобігає прихованим витокам пам'яті в складних багатопотокових системах.
