# 📋 Довідка std::allocator_traits та std::pmr

Повний інтерфейсний контракт моделі пам'яті C++ визначається двома взаємопов'язаними шарами стандарту: узагальненим адаптером типів `std::allocator_traits` для статичних алокаторів та поліморфним сімейством класів `std::pmr` для динамічного виділення пам'яті під час виконання.

## 1. Структура `std::allocator_traits<Alloc>`

Шаблон `std::allocator_traits<Alloc>` визначено у заголовному файлі `<memory>`. Він є єдиною стандартизованою точкою входу для контейнерів стандартної бібліотеки до функціональності алокатора. Його головне призначення полягає в автоматичному наданні значень за замовчуванням для всіх типів і методів, які розробник власного алокатора вирішив не реалізовувати вручну.

### Вкладені типи даних та правила виведення

Кожен тип у `std::allocator_traits` перевіряється на етапі компіляції за допомогою механізмів виявлення типів (SFINAE / концептів):

| Тип у `allocator_traits` | Правило виведення за замовчуванням | Семантика та призначення |
| :--- | :--- | :--- |
| `allocator_type` | `Alloc` | Тип самого алокатора, переданого у шаблон traits. |
| `value_type` | `Alloc::value_type` | Тип елемента, під який виділяється пам'ять. Це єдиний обов'язковий вкладений тип, який розробник зобов'язаний оголосити у власному алокаторі. |
| `pointer` | `Alloc::pointer` або `value_type*` | Тип адреси елемента в пам'яті. Якщо алокатор не оголошує власний розумний покажчик (fancy pointer), використовується звичайний сирий покажчик на `value_type`. |
| `const_pointer` | `Alloc::const_pointer` або `std::pointer_traits<pointer>::rebind<const value_type>` | Тип константного вказівника на елемент. |
| `void_pointer` | `Alloc::void_pointer` або `std::pointer_traits<pointer>::rebind<void>` | Нетипізований покажчик на сиру пам'ять, сумісний із типом `pointer`. |
| `const_void_pointer` | `Alloc::const_void_pointer` або `std::pointer_traits<pointer>::rebind<const void>` | Константний нетипізований покажчик на неініціалізовану пам'ять. |
| `difference_type` | `Alloc::difference_type` або `std::pointer_traits<pointer>::difference_type` | Знаковий цілочисельний тип, здатний зберігати відстань між двома покажчиками (за замовчуванням `std::ptrdiff_t`). |
| `size_type` | `Alloc::size_type` або `std::make_unsigned_t<difference_type>` | Беззнаковий цілий тип для представлення розмірів блоків і кількості елементів (за замовчуванням `std::size_t`). |
| `propagate_on_container_copy_assignment` | `Alloc::propagate_on_container_copy_assignment` або `std::false_type` | Ознака, що вказує, чи потрібно копіювати алокатор під час копіювального присвоєння контейнера `c1 = c2`. |
| `propagate_on_container_move_assignment` | `Alloc::propagate_on_container_move_assignment` або `std::false_type` | Ознака, що вказує, чи потрібно переміщувати алокатор під час переміщувального присвоєння контейнера `c1 = std::move(c2)`. |
| `propagate_on_container_swap` | `Alloc::propagate_on_container_swap` або `std::false_type` | Ознака, що визначає можливість взаємного обміну алокаторів під час операції `swap(c1, c2)`. |
| `is_always_equal` | `Alloc::is_always_equal` або `std::is_empty<Alloc>::type` | Ознака безстатусності алокатора. Для порожніх структур без полів даних автоматично повертає `true`. |
| `rebind_alloc<T>` | `Alloc::rebind<T>::other` або `Alloc<T, Args...>` | Псевдонім типу алокатора, адаптованого для нового цільового типу `T`. |
| `rebind_traits<T>` | `std::allocator_traits<rebind_alloc<T>>` | Повний екземпляр traits для перевизначеного типу алокатора. |

### Підтримка нестандартних покажчиків (Fancy Pointers)

Особливе місце в моделі `std::allocator_traits` посідає підтримка нестандартних типів покажчиків (так званих fancy pointers). Якщо алокатор оперує адресами у сегменті спільної пам'яті (shared memory), звичайний 64-бітний покажчик `T*` виявляється недійсним, оскільки різні процеси операційної системи можуть відображати один і той самий сегмент пам'яті за різними базовими віртуальними адресами.

У такому випадку алокатор оголошує тип `pointer` як спеціальний відносний покажчик (наприклад, `boost::interprocess::offset_ptr<T>`), який зберігає не абсолютну адресу, а різницю між адресою самого покажчика та адресою цільового об'єкта.

Завдяки посередництву `std::pointer_traits<pointer>` узагальнений шар `std::allocator_traits` автоматично виводить:
* `const_pointer` як `std::pointer_traits<pointer>::template rebind<const value_type>`;
* `void_pointer` як `std::pointer_traits<pointer>::template rebind<void>`;
* `const_void_pointer` як `std::pointer_traits<pointer>::template rebind<const void>`.

У C++20 для отримання сирої адреси з довільного fancy pointer стандартизовано функцію `std::to_address(p)`.

### Статичні методи та їхні контракти

Усі операції з пам'яттю та об'єктами здійснюються через статичні функції-члени `allocator_traits`:

```cpp
// 1. Виділення сирої пам'яті
[[nodiscard]] static pointer allocate(Alloc& a, size_type n);
[[nodiscard]] static pointer allocate(Alloc& a, size_type n, const_void_pointer hint);

// 2. Виділення пам'яті з інформацією про надлишкову ємність (C++23)
[[nodiscard]] static std::allocation_result<pointer, size_type>
allocate_at_least(Alloc& a, size_type n);

// 3. Звільнення сирої пам'яті
static void deallocate(Alloc& a, pointer p, size_type n);

// 4. Ініціалізація та конструювання об'єкта
template <class T, class... Args>
static void construct(Alloc& a, T* p, Args&&... args);

// 5. Знищення об'єкта
template <class T>
static void destroy(Alloc& a, T* p);

// 6. Теоретичний ліміт виділення
static size_type max_size(const Alloc& a) noexcept;

// 7. Створення алокатора для копійованого контейнера
static Alloc select_on_container_copy_construction(const Alloc& a);
```

#### Детальний аналіз поведінки кожного методу:

* **`allocate(Alloc& a, size_type n)`:**
  * Викликає метод `a.allocate(n)`.
  * Повертає вказівник на неініціалізований блок пам'яті, достатній для зберігання масиву з `n` об'єктів типу `value_type`.
  * Пам'ять зобов'язана бути належним чином вирівняна за межею `alignof(value_type)`.
  * Параметр `hint` (якщо присутній) передається алокатору як підказка про бажане місце розміщення блоку для покращення просторової локальності даних у кеші процесора.
  * У разі неможливості виділити пам'ять метод зобов'язаний кинути виняток `std::bad_alloc` або похідний від нього. Повернення `nullptr` стандартом суворо заборонено.

* **`allocate_at_least(Alloc& a, size_type n)` (введено в C++23):**
  * Якщо користувацький алокатор реалізує метод `a.allocate_at_least(n)`, викликає його; інакше повертає структуру `{ a.allocate(n), n }`.
  * Дозволяє низькорівневому алокатору повідомити контейнеру про фактичний обсяг виділеного сховища. Наприклад, якщо алокатор округлює запити до розміру сторінки операційної системи (4096 байтів), контейнер `std::vector` одразу встановлює ємність `capacity()` у фактично виділену кількість елементів, що усуває непотрібні повторні виділення.

* **`deallocate(Alloc& a, pointer p, size_type n)`:**
  * Викликає метод `a.deallocate(p, n)`.
  * Звільняє блок пам'яті, попередньо отриманий через виклик `allocate(n)`.
  * Деструктори об'єктів усередині цього блоку не викликаються — контейнер зобов'язаний самостійно знищити всі живі об'єкти перед звільненням пам'яті.
  * Метод не повинен кидати винятків (`noexcept`).

* **`construct(Alloc& a, T* p, Args&&... args)`:**
  * Якщо алокатор визначає власний метод `a.construct(p, std::forward<Args>(args)...)`, викликає його (що дозволяє алокаторам відстежувати створення об'єктів або передавати контексти вкладеним контейнерам).
  * Якщо користувацького методу немає, викликає глобальний розміщувальний new: `::new (static_cast<void*>(p)) T(std::forward<Args>(args)...)`.
  * Починає час життя об'єкта типу `T` за адресою `p`.

* **`destroy(Alloc& a, T* p)`:**
  * Якщо існує метод `a.destroy(p)`, викликає його; інакше викликає явний деструктор об'єкта `p->~T()`.
  * Завершує час життя об'єкта без вивільнення сирої пам'яті.

* **`max_size(const Alloc& a)`:**
  * Повертає максимальну кількість елементів типу `value_type`, яку теоретично здатний виділити алокатор.
  * Якщо `a.max_size()` відсутній, повертає значення `std::numeric_limits<size_type>::max() / sizeof(value_type)`.

* **`select_on_container_copy_construction(const Alloc& a)`:**
  * Викликається конструктором копіювання контейнера для створення нового екземпляра алокатора для створюваної копії.
  * Якщо метод не визначено, за замовчуванням повертає точну копію вихідного алокатора `a`.

---

## 2. Конструкція з передачею алокатора (Uses-allocator Construction)

У складних ієрархіях структур даних (наприклад, вектор рядків `std::vector<std::string>` або відображення векторів `std::map<int, std::vector<double>>`) виникає вимога: внутрішні контейнери повинні автоматично отримувати той самий екземпляр алокатора, що й зовнішній контейнер-власник.

Стандарт C++ формалізує цю поведінку за допомогою концепції `uses-allocator construction` (конструювання з використанням алокатора).

Тип `T` вважається таким, що використовує алокатор типу `Alloc`, якщо шаблонний предикат `std::uses_allocator_v<T, Alloc>` дорівнює `true` (що зазвичай означає наявність вкладеного типу `T::allocator_type`, до якого може бути перетворено `Alloc`).

Під час виклику `std::allocator_traits::construct` розрізняють три варіанти конструювання об'єкта:
1. **Провідний алокатор (Leading Allocator Convention):** Конструктор типу `T` приймає спеціальний тег `std::allocator_arg_t` першим параметром, а сам алокатор — другим:
   ```cpp
   Widget(std::allocator_arg_t, const Alloc& a, int x, double y);
   ```
2. **Завершальний алокатор (Trailing Allocator Convention):** Конструктор приймає алокатор останнім аргументом у списку:
   ```cpp
   Widget(int x, double y, const Alloc& a);
   ```
3. **Об'єкт не використовує алокатор:** Алокатор ігнорується, і конструктор викликається лише зі звичайними параметрами користувача.

Для глибокого багаторівневого прокидання алокаторів стандарт надає адаптер `std::scoped_allocator_adaptor`.

---

## 3. Інтерфейс `std::pmr::memory_resource`

Абстрактний клас `std::pmr::memory_resource` визначено у заголовному файлі `<memory_resource>`. Він реалізує ідіому невіртуального інтерфейсу (NVI): відкриті публічні методи виконують попередню перевірку аргументів та перенаправляють виклик до захищених чистих віртуальних методів.

```cpp
namespace std::pmr {

class memory_resource {
public:
    virtual ~memory_resource() = default;

    // Публічний невіртуальний інтерфейс
    [[nodiscard]] void* allocate(std::size_t bytes, std::size_t alignment = alignof(std::max_align_t)) {
        return do_allocate(bytes, alignment);
    }

    void deallocate(void* p, std::size_t bytes, std::size_t alignment = alignof(std::max_align_t)) {
        do_deallocate(p, bytes, alignment);
    }

    bool is_equal(const memory_resource& other) const noexcept {
        return do_is_equal(other);
    }

protected:
    // Чисті віртуальні методи, які зобов'язана реалізувати конкретна стратегія пам'яті
    virtual void* do_allocate(std::size_t bytes, std::size_t alignment) = 0;
    virtual void do_deallocate(void* p, std::size_t bytes, std::size_t alignment) = 0;
    virtual bool do_is_equal(const memory_resource& other) const noexcept = 0;
};

// Оператори рівності
inline bool operator==(const memory_resource& a, const memory_resource& b) noexcept {
    return &a == &b || a.is_equal(b);
}

inline bool operator!=(const memory_resource& a, const memory_resource& b) noexcept {
    return !(a == b);
}

} // namespace std::pmr
```

### Контракти віртуальних методів `memory_resource`:

* **`do_allocate(std::size_t bytes, std::size_t alignment)`:**
  * Виділяє блок пам'яті розміром не менше ніж `bytes`.
  * Початкова адреса блоку зобов'язана бути кратною значенню `alignment`. Значення `alignment` має бути коректним вирівнюванням, підтримуваним апаратурою (степенем двійки).
  * Якщо пам'ять не може бути виділена, метод зобов'язаний кинути виняток `std::bad_alloc`. Повернення `nullptr` заборонено стандартом.

* **`do_deallocate(void* p, std::size_t bytes, std::size_t alignment)`:**
  * Звільняє пам'ять, на яку вказує покажчик `p`.
  * Параметри `bytes` та `alignment` повинні точно збігатися зі значеннями, які передавалися під час відповідного виклику `do_allocate`.
  * Метод не повинен генерувати винятків.

* **`do_is_equal(const memory_resource& other) const noexcept`:**
  * Повертає `true`, якщо цей ресурс пам'яті та ресурс `other` є взаємозамінними (тобто блок пам'яті, виділений цим ресурсом, може бути без наслідків звільнений через `other.deallocate`).
  * Для ресурсів зі станом перевіряється фізична тотожність екземплярів: `this == &other`.

---

## 4. Стандартні фабрики та глобальні функції PMR

| Функція | Повертаний тип | Опис поведінки та гарантії |
| :--- | :--- | :--- |
| `std::pmr::new_delete_resource()` | `memory_resource*` | Повертає статичний синглтон, що виділяє пам'ять через глобальні `::operator new` та `::operator delete`. Ресурс існує протягом усього часу виконання процесу. |
| `std::pmr::null_memory_resource()` | `memory_resource*` | Повертає статичний ресурс, кожен виклик `allocate` якого негайно кидає виняток `std::bad_alloc`. Застосовується для жорсткої ізоляції підсистем від використання купи. |
| `std::pmr::get_default_resource()` | `memory_resource*` | Повертає поточний глобальний ресурс пам'яті за замовчуванням (початково вказує на `new_delete_resource()`). Є потокобезпечним. |
| `std::pmr::set_default_resource(r)` | `memory_resource*` | Атомарно встановлює новий глобальний ресурс `r`. Якщо передано `nullptr`, відновлює використання `new_delete_resource()`. Повертає попередній вказівник на ресурс. |

---

## 5. Конкретні класи ресурсів пам'яті PMR

### 5.1. `std::pmr::monotonic_buffer_resource`

Монотонний буферний ресурс забезпечує швидке виділення пам'яті послідовним зсувом покажчика (лінійна арена). Окремі виклики `deallocate` є порожніми операціями (no-op). Вся виділена пам'ять повертається джерелу лише під час виклику методу `release()` або знищення екземпляра класу.

```cpp
class monotonic_buffer_resource : public memory_resource {
public:
    monotonic_buffer_resource();
    explicit monotonic_buffer_resource(memory_resource* upstream);
    explicit monotonic_buffer_resource(std::size_t initial_size);
    monotonic_buffer_resource(std::size_t initial_size, memory_resource* upstream);
    monotonic_buffer_resource(void* buffer, std::size_t buffer_size);
    monotonic_buffer_resource(void* buffer, std::size_t buffer_size, memory_resource* upstream);

    virtual ~monotonic_buffer_resource();

    void release();
    memory_resource* upstream_resource() const;
};
```

### 5.2. `std::pmr::unsynchronized_pool_resource` та `synchronized_pool_resource`

Пули пам'яті організовують виділення за класами фіксованих розмірів (geometric size classes). Це усуває фрагментацію при частому створенні та знищенні дрібних об'єктів.

```cpp
struct pool_options {
    std::size_t max_blocks_per_chunk = 0;        // Максимальна кількість блоків у чанку
    std::size_t largest_required_pool_block = 0; // Поріг розміру: більші запити обходять пул і йдуть в upstream
};

class unsynchronized_pool_resource : public memory_resource {
public:
    explicit unsynchronized_pool_resource(const pool_options& opts = {}, memory_resource* upstream = get_default_resource());
    explicit unsynchronized_pool_resource(memory_resource* upstream);
    virtual ~unsynchronized_pool_resource();

    void release();
    memory_resource* upstream_resource() const;
    pool_options options() const;
};
```

---

## 6. Адаптер `std::pmr::polymorphic_allocator<T>`

Клас `std::pmr::polymorphic_allocator<T>` зв'язує поліморфні ресурси `memory_resource` зі статичними інтерфейсами стандартних контейнерів. Він зберігає всередині лише один покажчик `memory_resource*`.

```cpp
namespace std::pmr {

template <class T = std::byte>
class polymorphic_allocator {
public:
    using value_type = T;

    polymorphic_allocator() noexcept : res_(get_default_resource()) {}
    polymorphic_allocator(memory_resource* r) noexcept : res_(r ? r : get_default_resource()) {}
    polymorphic_allocator(const polymorphic_allocator& other) = default;

    template <class U>
    polymorphic_allocator(const polymorphic_allocator<U>& other) noexcept : res_(other.resource()) {}

    [[nodiscard]] T* allocate(std::size_t n) {
        return static_cast<T*>(res_->allocate(n * sizeof(T), alignof(T)));
    }

    void deallocate(T* p, std::size_t n) noexcept {
        res_->deallocate(p, n * sizeof(T), alignof(T));
    }

    [[nodiscard]] void* allocate_bytes(std::size_t nbytes, std::size_t alignment = alignof(std::max_align_t)) {
        return res_->allocate(nbytes, alignment);
    }

    void deallocate_bytes(void* p, std::size_t nbytes, std::size_t alignment = alignof(std::max_align_t)) noexcept {
        res_->deallocate(p, nbytes, alignment);
    }

    template <class U, class... Args>
    void construct(U* p, Args&&... args);

    template <class U>
    void destroy(U* p) noexcept {
        p->~U();
    }

    memory_resource* resource() const noexcept { return res_; }

    polymorphic_allocator select_on_container_copy_construction() const noexcept {
        return polymorphic_allocator();
    }

private:
    memory_resource* res_;
};

template <class T1, class T2>
bool operator==(const polymorphic_allocator<T1>& a, const polymorphic_allocator<T2>& b) noexcept {
    return *a.resource() == *b.resource();
}

} // namespace std::pmr
```

### Важливі правила роботи `polymorphic_allocator`:
1. **Поведінка при копіюванні контейнера:** Метод `select_on_container_copy_construction` повертає алокатор за замовчуванням (`get_default_resource()`). Якщо ви скопіювали вектор, створений на стеку локальної функції, результуюча копія автоматично виділить пам'ять у системній купі, що запобігає спробам запису у знищений стековий фрейм після виходу з функції.
2. **Автоматична передача вглиб (Uses-allocator Propagation):** Метод `construct` автоматично розпізнає, чи підтримує вкладений тип роботу з алокаторами. Якщо ми додаємо `std::pmr::string` у вектор `std::pmr::vector<std::pmr::string>`, рядок автоматично отримає той самий екземпляр `memory_resource*`, що й сам вектор, без необхідності передавати алокатор вручну в кожному виклику.

---

## 7. Стандартні псевдоніми типів контейнерів PMR

Стандартна бібліотека визначає готові псевдоніми у просторі імен `std::pmr`:

```cpp
namespace std::pmr {
    template <class T>
    using vector = std::vector<T, polymorphic_allocator<T>>;

    template <class charT, class traits = std::char_traits<charT>>
    using basic_string = std::basic_string<charT, traits, polymorphic_allocator<charT>>;

    using string = basic_string<char>;
    using wstring = basic_string<wchar_t>;

    template <class T>
    using list = std::list<T, polymorphic_allocator<T>>;

    template <class Key, class T, class Compare = std::less<Key>>
    using map = std::map<Key, T, Compare, polymorphic_allocator<std::pair<const Key, T>>>;

    template <class Key, class T, class Hash = std::hash<Key>, class KeyEqual = std::equal_to<Key>>
    using unordered_map = std::unordered_map<Key, T, Hash, KeyEqual, polymorphic_allocator<std::pair<const Key, T>>>;
}
```

---

## 8. Адаптер багаторівневих алокаторів `std::scoped_allocator_adaptor`

Шаблон `std::scoped_allocator_adaptor<OuterAlloc, InnerAllocs...>` визначено у заголовному файлі `<scoped_allocator>`. Він призначений для вирішення проблеми прокидання алокатора у вкладені структури даних (наприклад, вектор векторів `std::vector<std::vector<int>>` або відображення рядків).

### Інтерфейс та методи `std::scoped_allocator_adaptor`

```cpp
template <class OuterAlloc, class... InnerAllocs>
class scoped_allocator_adaptor : public OuterAlloc {
public:
    using outer_allocator_type = OuterAlloc;
    using inner_allocator_type = /* наступний рівень або сам scoped_allocator */;

    // Конструктори
    scoped_allocator_adaptor();
    template <class OuterA2>
    explicit scoped_allocator_adaptor(OuterA2&& outerAlloc, const InnerAllocs&... innerAllocs) noexcept;

    // Доступ до алокаторів рівнів
    outer_allocator_type& outer_allocator() noexcept;
    const outer_allocator_type& outer_allocator() const noexcept;
    inner_allocator_type& inner_allocator() noexcept;
    const inner_allocator_type& inner_allocator() const noexcept;

    // Конструювання з автоматичним розгортанням пар і кортежів
    template <class T, class... Args>
    void construct(T* p, Args&&... args);

    template <class T1, class T2, class... Args1, class... Args2>
    void construct(std::pair<T1, T2>* p,
                   std::piecewise_construct_t,
                   std::tuple<Args1...> x,
                   std::tuple<Args2...> y);
};
```

### Механізм конструювання:
* Зовнішній алокатор `OuterAlloc` використовується для виділення пам'яті під сам контейнер верхнього рівня.
* Під час створення внутрішніх елементів метод `construct` перевіряє, чи підтримує створюваний тип `T` використання алокатора (`std::uses_allocator_v<T, inner_allocator_type>`). Якщо так, `inner_allocator()` автоматично передається у відповідний конструктор елемента (або за правилом провідного аргументу `std::allocator_arg_t`, або за правилом завершального аргументу).

---

## 9. Матриця характеристик та гарантій потокобезпеки ресурсів PMR

| Ресурс пам'яті | Підтримка поштучного `deallocate` | Потокобезпека (Thread-Safety) | Поведінка при вичерпанні буфера | Накладні витрати на виділення |
| :--- | :--- | :--- | :--- | :--- |
| `new_delete_resource()` | Повна | Потокобезпечний (блокування всередині runtime ОС) | Кидає `std::bad_alloc` | 50–200 тактів процесора |
| `null_memory_resource()` | Не підтримується | Потокобезпечний | Завжди негайно кидає `std::bad_alloc` | 0 тактів (швидка аварія) |
| `monotonic_buffer_resource` | Порожня операція (no-op) | **Небезпечний** між потоками (вимагає зовнішньої синхронізації або `thread_local`) | Звертається до upstream-ресурсу | 2–5 тактів (зсув вказівника) |
| `unsynchronized_pool_resource` | Повна | **Небезпечний** між потоками (оптимізовано для одного потоку) | Виділяє новий чанк через upstream | 5–15 тактів (пошук у free-list) |
| `synchronized_pool_resource` | Повна | **Потокобезпечний** (внутрішній захист мютексами) | Виділяє новий чанк через upstream | 25–80 тактів (з урахуванням блокування) |

