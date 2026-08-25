# ⚙️ Практика: побудова детектора інтерфейсів та умовного серіалізатора

У системному програмуванні, розробці високопродуктивних мережевих протоколів та рушіїв збереження стану виникає потреба в універсальному модулі серіалізації даних. Складність полягає в тому, що різні типи представляють свій внутрішній стан по-різному:
- Складні бізнес-об'єкти надають власний метод `serialize(Buffer&)`;
- Сторонні структури даних підтримують вільну функцію `serialize(Buffer&, const T&)` через механізм ADL (Argument-Dependent Lookup);
- Контейнери підтримують ітерацію через методи `.begin()` та `.end()`;
- Прості скалярні типи (цілі числа, числа з плаваючою крапкою) копіюються як сирі байти безпосередньо у вихідний потік пам'яті.

Якщо спробувати реалізувати таку логіку через звичайні шаблони без обмежень, компілятор спробує скомпілювати гілку `val.serialize(buf)` для звичайного числа `int`, що призведе до аварійного завершення компіляції. Нижче наведено повне інженерне проектування системи виявлення інтерфейсів (Detection Idiom) через SFINAE у C++17, каскадну диспетчеризацію за пріоритетами, аналіз вартості виконання та сучасну реалізацію на базі концептів C++20.

## Проектування ідіоми виявлення на базі std::void_t

Для перевірки наявності довільного синтаксичного виразу в типі `T` ми використовуємо шаблонний детектор на базі `std::void_t`. Ідея полягає у створенні первинного шаблону, який завжди повертає `std::false_type`, та часткової спеціалізації, яка перевіряє валідність виразу в аргументі `std::void_t`.

Розглянемо, як правильно будувати такі предикати з урахуванням константності та категорій значень.

### 1. Детектор членського методу serialize

Коли ми перевіряємо, чи має об'єкт метод `obj.serialize(buf)`, об'єкт повинен бути доступний за константним посиланням `const T&`, оскільки серіалізація не повинна змінювати стан об'єкта. Буфер навпаки передається за неконстантним посиланням `Buffer&`:

```cpp
#include <type_traits>
#include <utility>
#include <vector>
#include <string>
#include <iostream>
#include <cstring>
#include <cstdint>

using Buffer = std::vector<uint8_t>;

// 1. Первинний шаблон: за замовчуванням метод відсутній
template<typename T, typename = void>
struct has_member_serialize : std::false_type {};

// 2. Часткова спеціалізація для валідного виразу
template<typename T>
struct has_member_serialize<T, std::void_t<
    decltype(std::declval<const T&>().serialize(std::declval<Buffer&>()))
>> : std::true_type {};

template<typename T>
inline constexpr bool has_member_serialize_v = has_member_serialize<T>::value;
```

Якщо тип `T` має відкритий метод `serialize(Buffer&)`, вираз всередині `decltype` успішно формується, `std::void_t` перетворює його на тип `void`, і компілятор обирає часткову спеціалізацію з `std::true_type`. Якщо методу немає або він приватний, підстановка у спеціалізацію зазнає помилки SFINAE, і компілятор тихо обирає первинний шаблон з `std::false_type`.

### 2. Детектор вільної функції через ADL

Часто сторонні бібліотечні типи не мають методів-членів, але надають зовнішню функцію `serialize(buf, obj)` у своєму просторі імен. Для її виявлення ми оголошуємо детектор, який активує пошук Кеніга:

```cpp
// Допоміжний простір імен для ізоляції перевірки ADL
namespace adl_detection {
    // Фіктивні оголошення, щоб компілятор знав ім'я serialize під час первинного розбору
    void serialize();

    template<typename T, typename = void>
    struct has_adl_serialize : std::false_type {};

    template<typename T>
    struct has_adl_serialize<T, std::void_t<
        decltype(serialize(std::declval<Buffer&>(), std::declval<const T&>()))
    >> : std::true_type {};
}

template<typename T>
inline constexpr bool has_adl_serialize_v = adl_detection::has_adl_serialize<T>::value;
```

### 3. Детектор стандартних контейнерів та послідовностей

Щоб визначити, чи є тип ітерованою послідовністю (як `std::vector`, `std::list` або `std::string`), ми перевіряємо наявність методів `begin()`, `end()` та наявність вкладеного типу `value_type`:

```cpp
template<typename T, typename = void>
struct is_iterable_container : std::false_type {};

template<typename T>
struct is_iterable_container<T, std::void_t<
    decltype(std::declval<const T&>().begin()),
    decltype(std::declval<const T&>().end()),
    typename T::value_type
>> : std::true_type {};

template<typename T>
inline constexpr bool is_iterable_container_v = is_iterable_container<T>::value;
```

## Каскадна диспетчеризація за пріоритетами (Priority Tag Dispatching)

Що станеться, якщо тип задовольняє одразу дві умови? Наприклад, тип є стандартним контейнером, але водночас автор надав йому спеціалізований метод `.serialize(buf)` для надшвидкого запису.

Якщо ми просто напишемо два незалежні шаблони `enable_if_t`, компілятор зафіксує конфлікт неоднозначності (Ambiguous Call). Щоб встановити строгу ієрархію вибору, використовують патерн **Priority Tag Dispatching**:

```cpp
// Ієрархія пріоритетів через глибину спадкування:
// priority_tag<N> успадковується від priority_tag<N-1>
template<std::size_t N>
struct priority_tag : priority_tag<N - 1> {};

template<>
struct priority_tag<0> {};
```

Під час розв'язання перевантажень компілятор завжди віддає перевагу точному співпадінню типу `priority_tag<3>`, і лише за неможливості спускається до базових класів `priority_tag<2>`, `priority_tag<1>` та `priority_tag<0>`.

Нижче наведено повне порівняння реалізації у C++17 та C++20:

:::tabs
```cpp
// Реалізація серіалізатора для C++17 (SFINAE + Priority Tag Dispatching)

// 1. Найвищий пріоритет (Tag 3): Власний метод serialize
template<typename T, std::enable_if_t<has_member_serialize_v<T>, int> = 0>
void write_impl(Buffer& buf, const T& obj, priority_tag<3>) {
    std::cout << "[SFINAE: Priority 3] Виклик obj.serialize(buf)\n";
    obj.serialize(buf);
}

// 2. Другий пріоритет (Tag 2): Вільна функція через ADL
template<typename T, std::enable_if_t<has_adl_serialize_v<T>, int> = 0>
void write_impl(Buffer& buf, const T& obj, priority_tag<2>) {
    std::cout << "[SFINAE: Priority 2] Виклик serialize(buf, obj) через ADL\n";
    serialize(buf, obj);
}

// 3. Третій пріоритет (Tag 1): Контейнери та послідовності
template<typename T, std::enable_if_t<is_iterable_container_v<T>, int> = 0>
void write_impl(Buffer& buf, const T& container, priority_tag<1>) {
    std::cout << "[SFINAE: Priority 1] Послідовна серіалізація контейнера\n";
    uint32_t sz = static_cast<uint32_t>(container.size());
    // Рекурсивно записуємо розмір
    const uint8_t* sz_ptr = reinterpret_cast<const uint8_t*>(&sz);
    buf.insert(buf.end(), sz_ptr, sz_ptr + sizeof(sz));
    for (const auto& item : container) {
        write_impl(buf, item, priority_tag<3>{});
    }
}

// 4. Четвертий пріоритет (Tag 0): Сирі тривіально копійовані байти
template<typename T, std::enable_if_t<std::is_trivially_copyable_v<T>, int> = 0>
void write_impl(Buffer& buf, const T& val, priority_tag<0>) {
    std::cout << "[SFINAE: Priority 0] Прямий запис сирих байтів пам'яті\n";
    const uint8_t* ptr = reinterpret_cast<const uint8_t*>(&val);
    buf.insert(buf.end(), ptr, ptr + sizeof(T));
}

// Публічний фасад
template<typename T>
void write_data(Buffer& buf, const T& val) {
    write_impl(buf, val, priority_tag<3>{});
}
```
```cpp
// Сучасна реалізація для C++20 (Concepts & Requires & Subsumption)

// Визначення концептів інтерфейсів
template<typename T>
concept HasMemberSerialize = requires(const T& obj, Buffer& buf) {
    { obj.serialize(buf) } -> std::same_as<void>;
};

template<typename T>
concept HasAdlSerialize = requires(const T& obj, Buffer& buf) {
    { serialize(buf, obj) } -> std::same_as<void>;
};

template<typename T>
concept IterableContainer = requires(const T& c) {
    c.begin();
    c.end();
    typename T::value_type;
};

template<typename T>
concept TriviallyRaw = std::is_trivially_copyable_v<T>;

// 1. Гілка з власним методом
void write_data(Buffer& buf, const HasMemberSerialize auto& obj) {
    std::cout << "[Concept: Member] Виклик obj.serialize(buf)\n";
    obj.serialize(buf);
}

// 2. Гілка з ADL
void write_data(Buffer& buf, const HasAdlSerialize auto& obj) 
    requires (!HasMemberSerialize<decltype(obj)>) 
{
    std::cout << "[Concept: ADL] Виклик serialize(buf, obj)\n";
    serialize(buf, obj);
}

// 3. Гілка контейнерів
void write_data(Buffer& buf, const IterableContainer auto& container)
    requires (!HasMemberSerialize<decltype(container)> && !HasAdlSerialize<decltype(container)>)
{
    std::cout << "[Concept: Container] Серіалізація елементів\n";
    uint32_t sz = static_cast<uint32_t>(container.size());
    const uint8_t* sz_ptr = reinterpret_cast<const uint8_t*>(&sz);
    buf.insert(buf.end(), sz_ptr, sz_ptr + sizeof(sz));
    for (const auto& item : container) {
        write_data(buf, item);
    }
}

// 4. Гілка сирих байтів
void write_data(Buffer& buf, const TriviallyRaw auto& val)
    requires (!HasMemberSerialize<decltype(val)> && 
              !HasAdlSerialize<decltype(val)> && 
              !IterableContainer<decltype(val)>)
{
    std::cout << "[Concept: Raw] Прямий запис байтів\n";
    const uint8_t* ptr = reinterpret_cast<const uint8_t*>(&val);
    buf.insert(buf.end(), ptr, ptr + sizeof(val));
}
```
:::

## Тестування та перевірка відбору перевантажень

Перевіримо роботу диспетчера на різних категоріях типів даних:

```cpp
// 1. Скалярна структура без спеціальних методів
struct SensorHeader {
    uint32_t device_id;
    uint16_t packet_seq;
};

// 2. Клас користувача з власним методом
struct UserProfile {
    uint64_t uid;
    std::string name;

    void serialize(Buffer& buf) const {
        const uint8_t* id_p = reinterpret_cast<const uint8_t*>(&uid);
        buf.insert(buf.end(), id_p, id_p + sizeof(uid));
        uint32_t len = static_cast<uint32_t>(name.size());
        const uint8_t* len_p = reinterpret_cast<const uint8_t*>(&len);
        buf.insert(buf.end(), len_p, len_p + sizeof(len));
        buf.insert(buf.end(), name.begin(), name.end());
    }
};

// 3. Сторонній тип із вільною функцією у власному просторі імен
namespace external_geo {
    struct Coordinates {
        double latitude;
        double longitude;
    };

    void serialize(Buffer& buf, const Coordinates& c) {
        const uint8_t* p = reinterpret_cast<const uint8_t*>(&c);
        buf.insert(buf.end(), p, p + sizeof(c));
    }
}

int main() {
    Buffer stream;

    // Тест 1: Сирі байти
    SensorHeader hdr{101, 42};
    write_data(stream, hdr);

    // Тест 2: Метод-член
    UserProfile profile{99999, "system_admin"};
    write_data(stream, profile);

    // Тест 3: Вільна функція через ADL
    external_geo::Coordinates geo{50.4501, 30.5234};
    write_data(stream, geo);

    // Тест 4: Контейнер
    std::vector<int> numbers = {100, 200, 300};
    write_data(stream, numbers);

    std::cout << "Успішно записано " << stream.size() << " байтів.\n";
    return 0;
}
```

## Аналіз вартості виконання та оптимізації компілятора

Важливою характеристикою ідіоми відбору перевантажень є її нульова вартість під час виконання (Zero Runtime Overhead).

Оскільки всі перевірки предикатів `has_member_serialize_v`, `is_iterable_container_v` та розв'язання перевантажень виконуються виключно на етапі синтаксичного аналізу:
1. У згенерованому асемблерному коді взагалі відсутні умовні переходи `if-else` або виклики диспетчерів таблиць віртуальних функцій.
2. Для скалярних типів компілятор повністю вбудовує функцію `write_impl(buf, val, priority_tag<0>)` у машинний код: на рівні процесора це перетворюється на одну пряму інструкцію збереження у пам'ять `mov [rdi], eax`.
3. Фіктивні об'єкти `priority_tag<N>{}` мають нульовий розмір пам'яті (Empty Base Optimization) і повністю видаляються оптимізатором компілятора на етапі генерації проміжного представлення LLVM / GCC GIMPLE.

## Аналіз типових пасток та крайових випадків SFINAE

Під час побудови виробничих бібліотек інтроспекції розробники стикаються з п'ятьма типовими дефектами реалізації:

### 1. Дефект оптимізації псевдонімів у компіляторах (CWG Issue 1558)
У стандарті C++14 компілятори Clang та GCC мали право відкидати шаблонні параметри в аліасах, якщо вони не впливали на результуючий тип: `template<typename...> using void_t = void`. Якщо компілятор бачив `void_t<Expr>`, він негайно замінював вираз на `void` без перевірки синтаксичної коректності `Expr`, руйнуючи весь механізм SFINAE!

Щоб змусити компілятор гарантовано обчислювати вирази, стандартні бібліотеки реалізують `void_t` через проміжну структуру:
```cpp
template<typename... Ts>
struct make_void { using type = void; };

template<typename... Ts>
using void_t = typename make_void<Ts...>::type;
```

### 2. Пастка приватних конструкторів та деструкторів
Функція `std::declval<T>()` створює rvalue-посилання `T&&`, тому вона не викликає конструктори об'єкта. Проте якщо клас `T` має **приватний деструктор**, використання `std::declval<T>()` у деяких контекстах виразів призведе до фатальної помилки компіляції прав доступу (Access Control Error), оскільки неявне завершення життя тимчасового об'єкта вимагає доступності деструктора.

### 3. Робота з неповними типами (Incomplete Types)
Спроба передати випереджальне оголошення `class MyClass;` у трейт, який виконує `sizeof(T)` або перевіряє члени типу, призводить до негайного падіння збірки. SFINAE не захищає від використання неповних типів там, де мова вимагає повного визначення класу.

### 4. Конфлікт значень за замовчуванням у перевантаженнях
Спроба записати два перевантаження як:
```cpp
template<typename T, typename = std::enable_if_t<Cond1<T>>>
void dispatch(T val);

template<typename T, typename = std::enable_if_t<Cond2<T>>>
void dispatch(T val); // Redefinition Error!
```
призводить до помилки компіляції, оскільки аргументи за замовчуванням не входять до сигнатури шаблону. Правильним рішенням є використання `std::enable_if_t<Cond, int> = 0` або фільтрація через тип повернення.

### 5. Відсутність короткого замикання в аргументах шаблону
У виразах на зразок `std::enable_if_t<is_class_v<T> && has_method_v<T>>` компілятор зобов'язаний інстанціювати **обидва** трейти `is_class_v<T>` та `has_method_v<T>`. Якщо `has_method_v` не вміє безпечно обробляти примітивні типи, інстанціація другого трейту призведе до жорсткої помилки компіляції. Для безпечної композиції слід використовувати `std::conjunction` (C++17) або концепти `requires` (C++20), які підтримують справжнє ліниве коротке замикання (Short-circuit Evaluation).
