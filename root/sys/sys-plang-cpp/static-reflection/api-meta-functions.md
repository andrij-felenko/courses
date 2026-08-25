# 📋 Довідник інтерфейсу std::meta: дескриптор info, предикати та метафункції

Бібліотека статичної рефлексії C++26 у просторі назв `std::meta` надає стандартизований програмний інтерфейс для інтроспекції та аналізу структури типів, функцій, просторів назв, змінних і констант безпосередньо під час компіляції. До появи цієї специфікації розробники на C++ були змушені будувати складні шаблонні конструкції з рекурсивним інстанціюванням або використовувати зовнішні кодогенератори, оскільки компілятор знищував усю семантичну інформацію про структуру коду після завершення синтаксичного аналізу. Стандарт C++26 закріплює значеннєву модель рефлексії (англ. *value-based reflection*), у якій будь-яка сутність програми відображається у скалярне значення непрозорого літерального типу `std::meta::info`.

У цьому довіднику зібрано повну специфікацію типу `info`, операторів зв'язування `^^` та `[: :]`, стандартних запитів, класифікаційних предикатів, функцій трансформації та інстанціювання, механізму призначених для користувача анотацій, засобів генерації діагностичних повідомлень, а також правила обробки помилок і граничних випадків відповідно до робочого документа C++26 (технічна специфікація P2996R5 та узгоджені рішення комітету WG21).

---

## 1. Архітектурна модель та фундаментальний тип std::meta::info

Основою статичної рефлексії є повна відмова від кодування метаданих у системі типів. У класичному шаблонному метапрограмуванні кожен крок інспекції чи фільтрації змушував компілятор створювати новий допоміжний тип, що призводило до швидкого вичерпання таблиці символів, розростання пам'яті компілятора та сповільнення збірки складних проектів. У моделі C++26 усі метадані існують як звичайні константні значення.

Тип `std::meta::info` є скалярним літеральним типом, який компілятор використовує для представлення прямого дескриптора внутрішнього вузла свого абстрактного синтаксичного дерева (AST).

```cpp
namespace std::meta {
    // Непрозорий скалярний літеральний тип для представлення сутностей AST
    using info = /* compiler-internal scalar literal type */;
}
```

### Фундаментальні інваріанти типу info

1. **Літеральність та робота в consteval:** Об'єкти типу `std::meta::info` є повноцінними літеральними значеннями. Їх можна оголошувати зі специфікатором `constexpr` або `consteval`, передавати за значенням у функції, повертати як результати обчислень, використовувати як нетипові параметри шаблонів (NTTP), зберігати в масивах `std::array` та динамічних контейнерах `std::vector` у контексті константних обчислень.
2. **Відсутність сліду під час виконання (Zero Runtime Footprint):** Значення `info` існують суто в оперативній пам'яті компілятора під час трансляції вихідного файлу. Вони не мають розміру, вирівнювання чи адресного представлення в готовому машинному коді. Спроба використати змінну типу `info` у звичайному коді часу виконання призводить до помилки компіляції. Якщо інформацію необхідно перенести у фазу виконання, її явно перетворюють на звичайні типи даних — наприклад, отримують рядок `std::string_view` через функцію `name_of` або числове значення через шаблонну функцію `extract`.
3. **Семантика рівності та впорядкування:** Для дескрипторів `info` реалізовано оператори рівності `==`, `!=` та оператор тричленного порівняння `<=>`. Два значення типу `info` є повністю рівними тоді й лише тоді, коли вони посилаються на одну й ту саму сутність у таблиці символів компілятора. Це дозволяє здійснювати точне порівняння типів, функцій чи полів без небезпеки плутанини через однакові назви в різних областях видимості.
4. **Хешування під час компіляції:** Стандартна бібліотека містить спеціалізацію `std::hash<std::meta::info>`, придатну для виклику в `constexpr`. Це уможливлює використання дескрипторів як ключів у хеш-таблицях часу компіляції для усунення дублікатів та швидкого пошуку сутностей за O(1).

---

## 2. Мовні оператори: підйом (^^) та сплайсинг ([: :])

Взаємодія між текстом програми та простором значень метаінформації здійснюється через два симетричні оператори мови C++. Оператор підйому переводить сутність коду у значення `info`, а оператор сплайсингу повертає значення `info` назад у синтаксичну структуру програми.

### 2.1. Оператор підйому ^^ (Reflection Lift Operator)

Оператор `^^` є унарним префіксним оператором. Його операндом може бути практично будь-яка іменована або типізована конструкція мови C++.

```cpp
// Підйом типів даних
constexpr std::meta::info int_ref   = ^^int;
constexpr std::meta::info str_ref   = ^^std::string;

// Підйом членів класу
struct Account {
    std::string login;
    int balance;
};
constexpr std::meta::info field_ref = ^^Account::login;

// Підйом просторів назв, шаблонів та констант
constexpr std::meta::info ns_ref    = ^^std;
constexpr std::meta::info tmpl_ref  = ^^std::vector;
```

Особливості роботи оператора `^^`:
- Підйом типу повертає унікальний дескриптор, канонічний для даної комбінації типу та його cv-кваліфікаторів (наприклад, `^^const int` та `^^int` дають різні дескриптори, але `type_of` дозволяє простежити їхній зв'язок).
- Підйом виразу `^^(expr)` повертає дескриптор синтаксичного вузла виразу, зберігаючи його тип та категорію значення (lvalue, prvalue, xvalue).
- Підйом шаблону `^^std::vector` повертає дескриптор первинного шаблону, а не його спеціалізації.

### 2.2. Оператор сплайсингу [: ... :] (Splicer Operator)

Оператор сплайсингу `[: expr :]` приймає вираз `expr`, який має бути константним виразом типу `std::meta::info`, та замінює собою відповідний синтаксичний елемент у точці використання.

Граматика C++26 виділяє п'ять фундаментальних контекстів застосування сплайсера:

1. **Контекст визначення типу (Type Splice):**
   Якщо дескриптор посилається на тип даних, сплайсер дозволяє вказати цей тип під час оголошення змінних, повертаних значень функцій або в списках `using`.
   ```cpp
   constexpr std::meta::info target_type = ^^double;
   [: target_type :] current_speed = 95.5; // розгортається у: double current_speed = 95.5;
   using DynamicArray = [: ^^std::vector<int> :];
   ```

2. **Контекст доступу до члена об'єкта (Member Access Splice):**
   Якщо дескриптор посилається на нестатичне поле даних класу, сплайсер після оператора крапки або стрілки звертається до цього конкретного поля зазначеного екземпляра.
   ```cpp
   Account acc{"admin", 5000};
   constexpr std::meta::info member_info = ^^Account::balance;
   acc.[: member_info :] += 1000; // розгортається у пряме звернення: acc.balance += 1000;
   ```

3. **Контекст простору назв (Namespace Qualifier Splice):**
   Якщо дескриптор представляє простір імен, сплайсер може виступати префіксом для пошуку вкладених сутностей.
   ```cpp
   constexpr std::meta::info std_ns = ^^std;
   [: std_ns :]::vector<int> values{1, 2, 3};
   ```

4. **Контекст аргументу шаблона (Template Argument Splice):**
   Дескриптор типу або значення може передаватися безпосередньо у кутові дужки списку параметрів шаблона.
   ```cpp
   constexpr std::meta::info type_a = ^^int;
   constexpr std::meta::info type_b = ^^std::string;
   std::pair<[: type_a :], [: type_b :]> entry{1, "first"};
   ```

5. **Контекст специфікатора базового класу (Base Class Splice):**
   Сплайсер дозволяє обчислювати батьківський клас структури або класу динамічно під час компіляції.
   ```cpp
   constexpr std::meta::info chosen_base = ^^std::enable_shared_from_this<Account>;
   struct ManagedAccount : public [: chosen_base :] {
       // тіло класу
   };
   ```

---

## 3. Селектори структури: дослідження вмісту сутностей

Для детального аналізу внутрішньої будови класів, переліків і просторів назв бібліотека `std::meta` надає набір функцій-селекторів. Усі вони оголошені зі специфікатором `consteval` і повертають послідовності дескрипторів у вигляді стандартного контейнера `std::vector<std::meta::info>`.

```cpp
namespace std::meta {
    // Повний список усіх членів класу або простору назв
    consteval auto members_of(info type_or_ns) -> std::vector<info>;

    // Нестатичні поля даних екземпляра класу
    consteval auto nonstatic_data_members_of(info class_type) -> std::vector<info>;

    // Статичні змінні-члени класу
    consteval auto static_data_members_of(info class_type) -> std::vector<info>;

    // Усі функції-члени класу (методи, конструктори, деструктори, оператори)
    consteval auto member_functions_of(info class_type) -> std::vector<info>;

    // Вкладені типи (структури, класи, об'єднання, переліки, псевдоніми using)
    consteval auto member_types_of(info class_type) -> std::vector<info>;

    // Специфікатори безпосередніх базових класів
    consteval auto bases_of(info class_type) -> std::vector<info>;

    // Усі константи переліку (для enum та enum class)
    consteval auto enumerators_of(info enum_type) -> std::vector<info>;
}
```

### Правила виконання та гарантії селекторів:

- **Лексичний порядок оголошення:** Селектори `members_of` та `nonstatic_data_members_of` повертають елементи строго в тому порядку, у якому вони записані у вихідному коді класу. Це критично важливо для алгоритмів серіалізації, структурного гешування та генерації структур із фіксованим двійковим розміщенням.
- **Вимога повноти типу:** Виклик будь-якого селектора структури для неповного типу (наприклад, випереджального оголошення `class Widget;`) призводить до негайної зупинки компіляції з помилкою. Тип повинен бути повністю визначеним перед точкою виклику інтроспекції.
- **Спадкування:** Селектор `nonstatic_data_members_of` повертає поля лише безпосередньо оголошеного класу. Поля базових класів не включаються автоматично; для їхнього аналізу метапрограма повинна рекурсивно обійти дескриптори, отримані з `bases_of`.

---

## 4. Запити властивостей, імен та розташування

Для кожної відрефлексованої сутності можна отримати її символьні назви, асоційовані типи даних, область видимості та файлові координати оголошення.

```cpp
namespace std::meta {
    // Базове некваліфіковане ім'я сутності (наприклад, "login" або "vector")
    consteval auto name_of(info entity) -> std::string_view;

    // Символьний ідентифікатор мови (повертає порожній рядок для безіменних сутностей)
    consteval auto identifier_of(info entity) -> std::string_view;

    // Повне форматоване найменування з просторами назв та шаблонними параметрами
    consteval auto display_name_of(info entity) -> std::string_view;

    // Тип сутності (для змінних, полів даних, параметрів, функцій)
    consteval auto type_of(info entity) -> info;

    // Батьківська область видимості (клас або простір назв, у якому оголошено сутність)
    consteval auto parent_of(info entity) -> info;

    // Базовий цілочисельний тип переліку (підлеглий тип для enum)
    consteval auto underlying_type_of(info enum_type) -> info;

    // Точні координати оголошення сутності у файлі коду
    consteval auto source_location_of(info entity) -> std::source_location;
}
```

### Відмінності між функціями найменування:

- `name_of(entity)` повертає рядок `std::string_view`, що містить пряме локальне ім'я. Для анонімних об'єднань, безіменних параметрів чи бітових полів без назви повертається порожній рядок `""`.
- `display_name_of(entity)` генерує детальний строковий опис із повним списком аргументів шаблонів та просторів імен, що є незамінним для генерації інформативних повідомлень у діагностиках та компіляторних логах.
- `source_location_of(entity)` повертає стандартну структуру `std::source_location`, з якої можна вилучити номер рядка, стовпця та назву файлу, де визначено сутність.

---

## 5. Предикати класифікації сутностей та специфікаторів

Предикати повертають логічне значення `bool` під час компіляції. Вони дозволяють будувати виразні умови фільтрації для вибірки полів, перевірки доступу та інспекції поведінкових характеристик сутностей.

### 5.1. Предикати категорії сутності

```cpp
namespace std::meta {
    consteval auto is_type(info entity) -> bool;
    consteval auto is_variable(info entity) -> bool;
    consteval auto is_function(info entity) -> bool;
    consteval auto is_namespace(info entity) -> bool;
    consteval auto is_template(info entity) -> bool;
    consteval auto is_concept(info entity) -> bool;
    consteval auto is_enumerator(info entity) -> bool;
    consteval auto is_nonstatic_data_member(info entity) -> bool;
    consteval auto is_static_data_member(info entity) -> bool;
    consteval auto is_base(info entity) -> bool;
    consteval auto is_bit_field(info entity) -> bool;
}
```

### 5.2. Предикати специфікаторів доступу

```cpp
namespace std::meta {
    consteval auto is_public(info member) -> bool;
    consteval auto is_protected(info member) -> bool;
    consteval auto is_private(info member) -> bool;

    // Перевірка доступності члена в заданому контексті рефлексії
    consteval auto is_accessible(info member, info context = ^^void) -> bool;
}
```

### 5.3. Предикати характеристик функцій та методів

```cpp
namespace std::meta {
    consteval auto is_static(info entity) -> bool;
    consteval auto is_virtual(info entity) -> bool;
    consteval auto is_pure_virtual(info entity) -> bool;
    consteval auto is_override(info entity) -> bool;
    consteval auto is_final(info entity) -> bool;
    consteval auto is_constexpr(info entity) -> bool;
    consteval auto is_consteval(info entity) -> bool;
    consteval auto is_noexcept(info entity) -> bool;
    consteval auto is_deleted(info entity) -> bool;
    consteval auto is_defaulted(info entity) -> bool;
    consteval auto is_explicit(info entity) -> bool;
    consteval auto is_inline(info entity) -> bool;
}
```

### 5.4. Предикати властивостей типів та перевірка повноти

```cpp
namespace std::meta {
    consteval auto is_class(info type) -> bool;
    consteval auto is_struct(info type) -> bool;
    consteval auto is_union(info type) -> bool;
    consteval auto is_enum(info type) -> bool;
    consteval auto is_scoped_enum(info type) -> bool;
    consteval auto is_complete_type(info type) -> bool;
    consteval auto is_abstract(info type) -> bool;
    consteval auto is_polymorphic(info type) -> bool;
    consteval auto is_aggregate(info type) -> bool;
    consteval auto is_trivial(info type) -> bool;
    consteval auto is_standard_layout(info type) -> bool;
    consteval auto is_empty_class(info type) -> bool;
}
```

Предикат `is_complete_type` розв'язує давню проблему мови C++: він дозволяє безпечно перевірити, чи завершено визначення класу, без виклику аварійної зупинки компіляції на випереджальних оголошеннях. У класичному C++ спроба перевірити повноту типу через вираз `sizeof(T)` призводила до жорсткої помилки замість м'якого відхилення гілки SFINAE. У C++26 рефлексивний запит `std::meta::is_complete_type(^^T)` повертає чисте логічне значення `false` для неповного типу, що дозволяє організовувати умовну компіляцію для взаємозалежних рекурсивних структур даних.

---

## 6. Кваліфікатори cv, посилання та операції над типами

Під час обробки сигнатур методів та типів полів критично важливо правильно розрізняти модифікатори константності, волатильності та категорії посилань. Бібліотека `std::meta` надає набір функцій для перевірки та модифікації кваліфікаторів безпосередньо над дескрипторами `info`:

```cpp
namespace std::meta {
    // Предикати перевірки кваліфікаторів
    consteval auto is_const(info type) -> bool;
    consteval auto is_volatile(info type) -> bool;
    consteval auto is_lvalue_reference(info type) -> bool;
    consteval auto is_rvalue_reference(info type) -> bool;
    consteval auto is_pointer(info type) -> bool;
    consteval auto is_array(info type) -> bool;

    // Трансформації кваліфікаторів типу
    consteval auto remove_cv(info type) -> info;
    consteval auto remove_reference(info type) -> info;
    consteval auto remove_cvref(info type) -> info;
    consteval auto add_lvalue_reference(info type) -> info;
    consteval auto add_rvalue_reference(info type) -> info;
    consteval auto add_pointer(info type) -> info;
    consteval auto remove_pointer(info type) -> info;
}
```

### Порівняння з бібліотекою type_traits:

На відміну від заголовочного файлу `<type_traits>`, де кожна операція на кшталт `std::remove_cvref_t<T>` вимагала інстанціювання шаблонного типу, функції в `std::meta` виконуються як звичайні процедурні виклики над значеннями `info`. Це не створює нових записів у таблиці типів компілятора доти, доки результат не буде явно передано в оператор сплайсингу `[: :]`.

---

## 7. Інспекція конструкторів, деструкторів та параметрів функцій

Для повноцінної генерації фабричних методів, серіалізаторів та проксі-обгорток рефлексія C++26 надає можливість досліджувати спеціальні функції-члени та сигнатури виклику:

```cpp
namespace std::meta {
    // Спеціальні функції-члени
    consteval auto is_constructor(info entity) -> bool;
    consteval auto is_destructor(info entity) -> bool;
    consteval auto is_copy_constructor(info entity) -> bool;
    consteval auto is_move_constructor(info entity) -> bool;
    consteval auto is_assignment_operator(info entity) -> bool;

    // Інспекція параметрів функцій
    consteval auto parameters_of(info function_entity) -> std::vector<info>;
    consteval auto return_type_of(info function_entity) -> info;
}
```

Дескриптори параметрів, отримані через `parameters_of`, підтримують стандартні запити `type_of` та `name_of`, що дозволяє автоматично зіставляти аргументи конструктора з іменами ключів у форматах серіалізації (наприклад, для десеріалізації незмінних структур без конструктора за замовчуванням).

---

## 8. Метафункції трансформації, підстановки та геометричних параметрів

Ця група функцій дозволяє створювати нові дескриптори типів, інстанціювати шаблони, розгортати псевдоніми та вимірювати фізичні параметри розміщення об'єктів у пам'яті.

```cpp
namespace std::meta {
    // Інстанціювання первинного шаблону переданим списком дескрипторів аргументів
    consteval auto substitute(info template_entity, std::span<const info> args) -> info;

    // Отримання дескриптора первинного шаблону для інстанційованого типу
    consteval auto template_of(info instantiated_type) -> info;

    // Отримання списку аргументів шаблону для інстанційованого типу
    consteval auto template_arguments_of(info instantiated_type) -> std::vector<info>;

    // Зняття шарів псевдонімів using та typedef до вихідного типу
    consteval auto dealias(info entity) -> info;

    // Перетворення значення часу компіляції у дескриптор info
    template <typename T>
    consteval auto reflect_value(const T& value) -> info;

    // Вилучення типізованого значення з дескриптора константи
    template <typename T>
    consteval auto extract(info value_entity) -> T;

    // Перевірка, чи несе дескриптор дійсне константне значення
    consteval auto has_value(info entity) -> bool;

    // Геометричні параметри пам'яті (розмір, вирівнювання, зміщення в байтах)
    consteval auto size_of(info type_entity) -> size_t;
    consteval auto alignment_of(info type_entity) -> size_t;
    consteval auto offset_of(info member_entity) -> size_t;
    consteval auto bit_size_of(info bitfield_entity) -> size_t;
}
```

### Механізм роботи функції substitute:

Функція `substitute` замінює класичний шаблонний синтаксис інстанціювання `Template<Args...>` на процедурний виклик під час компіляції. Це дозволяє формувати списки параметрів шаблонів динамічно через фільтрацію чи конкатенацію масивів `std::vector<std::meta::info>`.

```cpp
// Динамічне створення типу std::map<std::string, double> через масив дескрипторів
constexpr auto map_tmpl = ^^std::map;
constexpr std::array args = { ^^std::string, ^^double };
constexpr auto generated_map_type = std::meta::substitute(map_tmpl, args);

// Створення екземпляра згенерованого типу через сплайсинг
[: generated_map_type :] price_table;
price_table["server_cpu"] = 1250.0;
```

---

## 9. Робота з константними значеннями: reflect_value та extract

Під час написання кодогенераторів виникає потреба передавати не лише типи чи назви функцій, а й конкретні значення, обчислені в процесі компіляції. Функція `reflect_value` виконує підйом значення літерального типу у простір метаданих, а функція `extract` здійснює зворотне вилучення.

```cpp
// Підйом скалярного значення в дескриптор
constexpr int max_retries = 5;
constexpr auto value_ref = std::meta::reflect_value(max_retries);

// Перевірка наявності значення та вилучення
static_assert(std::meta::has_value(value_ref));
constexpr int extracted_retries = std::meta::extract<int>(value_ref);
static_assert(extracted_retries == 5);
```

Функція `extract<T>` перевіряє сумісність збереженого значення із цільовим типом `T`. Якщо збережене значення має інший тип (наприклад, спроба вилучити `double` із дескриптора рядкового літералу), компілятор зупиняє виконання `consteval`-виразу з помилкою невідповідності типів.

---

## 10. Інспекція бітових полів та пам'яті

Для низькорівневих протоколів передачі даних, драйверів апаратних пристроїв та мережевих стеків критичним є знання точного розміщення бітів у структурах. Бібліотека рефлексії дозволяє аналізувати зміщення, вирівнювання та довжину бітових полів без ручного підрахунку байтів:

```cpp
struct NetworkHeader {
    uint8_t  version : 4;
    uint8_t  ihl     : 4;
    uint8_t  tos;
    uint16_t total_length;
};

consteval auto inspect_layout(std::meta::info type_info) {
    for (auto field : std::meta::nonstatic_data_members_of(type_info)) {
        if (std::meta::is_bit_field(field)) {
            // Отримання розрядності бітового поля
            size_t bits = std::meta::bit_size_of(field);
        } else {
            // Отримання байтового зміщення та розміру
            size_t byte_offset = std::meta::offset_of(field);
            size_t byte_size   = std::meta::size_of(std::meta::type_of(field));
        }
    }
}
```

---

## 11. Дослідження поліморфних ієрархій та віртуальних методів

Рефлексія C++26 надає повний доступ до аналізу таблиць віртуальних методів (vtable) та базових класів без необхідності запуску програми чи звернення до механізму RTTI.

Предикат `is_polymorphic(type)` повідомляє, чи містить клас віртуальні функції або чи успадковує він їх від базових класів. Функція `bases_of(type)` дозволяє обійти дерево успадкування, а предикат `is_virtual_base` у комбінації з `is_virtual` на функціях-членах дозволяє автоматично виявляти абстрактні інтерфейси та генерувати класи-реалізації або проксі-обгортки.

```cpp
consteval auto count_pure_virtual_methods(std::meta::info class_info) -> size_t {
    size_t count = 0;
    for (auto method : std::meta::member_functions_of(class_info)) {
        if (std::meta::is_pure_virtual(method)) {
            count++;
        }
    }
    return count;
}
```

---

## 12. Інспекція шаблонів, спеціалізацій та кваліфікаторів

Під час аналізу складних узагальнених бібліотек часто виникає потреба розрізняти первинні шаблони, явні спеціалізації та розбирати їхні аргументи на складові частини.

### Робота з аргументами шаблонів

Для будь-якого інстанційованого типу функція `template_of` повертає дескриптор його первинного шаблону, а `template_arguments_of` — вектор дескрипторів переданих параметрів:

```cpp
using ContainerType = std::vector<int>;
constexpr auto cont_info = ^^ContainerType;

constexpr auto primary_tmpl = std::meta::template_of(cont_info); // повертає ^^std::vector
constexpr auto tmpl_args     = std::meta::template_arguments_of(cont_info);
// tmpl_args містить дескриптори [ ^^int, ^^std::allocator<int> ]
```

Це дозволяє узагальненому коду перепаковувати контейнери — наприклад, замінювати тип елемента `int` на `double` без явного знання структури самого контейнера:

```cpp
consteval auto rebind_container_element(std::meta::info container_type, std::meta::info new_elem_type) -> std::meta::info {
    auto tmpl = std::meta::template_of(container_type);
    auto args = std::meta::template_arguments_of(container_type);
    args[0] = new_elem_type; // замінюємо перший аргумент шаблону
    return std::meta::substitute(tmpl, args);
}
```

---

## 13. Призначені для користувача анотації та атрибути

Стандарт C++26 розширює систему атрибутів можливістю прикріплювати до полів, класів та функцій структуровані константні значення — анотації (англ. *annotations*), які зчитуються через рефлексію:

```cpp
namespace std::meta {
    // Отримання списку дескрипторів усіх анотацій, прикріплених до сутності
    consteval auto annotations_of(info entity) -> std::vector<info>;

    // Перевірка наявності анотації заданого типу
    template <typename AnnotationType>
    consteval auto has_annotation(info entity) -> bool;

    // Вилучення екземпляра анотації заданого типу
    template <typename AnnotationType>
    consteval auto get_annotation(info entity) -> std::optional<AnnotationType>;
}
```

### Застосування анотацій у моделях даних:

```cpp
struct JsonKey {
    std::string_view name;
};

struct IgnoreInSerialization {};

struct UserProfile {
    [[=JsonKey{"user_identifier"}]]
    int id;

    [[=IgnoreInSerialization{}]]
    std::string internal_token;
};
```

Під час ітерації полях серіалізатор перевіряє `has_annotation<IgnoreInSerialization>(field)` і пропускає позначені поля, або викликає `get_annotation<JsonKey>(field)` для підстановки кастомного імені в JSON-об'єкт.

---

## 14. Генерація нових структур: data_member_spec та define_class

У специфікаціях розширення статичної рефлексії (пропозиції P2996 та P3294 щодо ін'єкції токенів та генерації типів) бібліотека `std::meta` надає механізм для програмного синтезу нових класів безпосередньо в процесі компіляції.

Синтез структури здійснюється шляхом опису її полів через структуру `std::meta::data_member_spec` із подальшим викликом функції генерації `std::meta::define_class`:

```cpp
namespace std::meta {
    // Параметри опису нового поля структури
    struct data_member_spec {
        info type;                          // дескриптор типу поля
        std::string_view name;              // ім'я поля
        size_t alignment = 0;               // вирівнювання (0 — стандартне)
        bool is_bitfield = false;           // чи є поле бітовим
        size_t bit_width = 0;               // ширина бітового поля
    };

    // Синтез нового типу класу на основі списку специфікаторів полів
    consteval auto define_class(std::span<const data_member_spec> members) -> info;
}
```

### Приклад створення структури на льоту:

```cpp
// Функція створює тип структури, що містить дзеркальні поля двох інших типів
consteval auto create_combined_struct(std::meta::info type_a, std::meta::info type_b) -> std::meta::info {
    std::vector<std::meta::data_member_spec> specs;

    for (auto f : std::meta::nonstatic_data_members_of(type_a)) {
        specs.push_back({
            .type = std::meta::type_of(f),
            .name = std::meta::name_of(f)
        });
    }
    for (auto f : std::meta::nonstatic_data_members_of(type_b)) {
        specs.push_back({
            .type = std::meta::type_of(f),
            .name = std::meta::name_of(f)
        });
    }

    return std::meta::define_class(specs);
}
```

Цей механізм дозволяє реалізовувати такі патерни, як автоматична трансформація масиву структур у структуру масивів (AoS в SoA для оптимізації SIMD), генерація об'єктів перенесення даних (DTO) та автоматичне створення мок-класів для тестування без використання препроцесора.

---

## 15. Компільовані діагностики та обробка помилок

Бібліотека рефлексії надає засоби для генерації інформативних помилок компіляції та попереджень безпосередньо з тіла `consteval`-метафункцій:

```cpp
namespace std::meta {
    // Зупинка компіляції з користувацьким повідомленням про помилку
    consteval void report_error(std::string_view message, std::source_location loc = std::source_location::current());

    // Вивід попередження компілятора
    consteval void report_warning(std::string_view message, std::source_location loc = std::source_location::current());
}
```

### Приклад верифікації структури під час збірки:

```cpp
template <typename T>
consteval void verify_serializable() {
    constexpr auto type_info = ^^T;
    if (!std::meta::is_class(type_info)) {
        std::meta::report_error("Серіалізація підтримується лише для класів та структур");
    }

    for (auto field : std::meta::nonstatic_data_members_of(type_info)) {
        if (std::meta::is_private(field)) {
            std::meta::report_error("Клас містить приватні поля, що унеможливлює пряму серіалізацію");
        }
    }
}
```

---

## 16. Зведена таблиця поведінки при некоректних викликах

| Сценарій некоректного виклику | Реакція метафункції | Результат для компілятора |
| :--- | :--- | :--- |
| `members_of(^^int)` | Виклик для простого скалярного типу | Помилка `consteval`: тип не є класом або простором назв |
| `nonstatic_data_members_of(^^Incomplete)` | Виклик для неповного типу | Помилка збірки: тип повинен бути повністю визначеним |
| `name_of` для неіменованого бітового поля | Повертає порожній рядок `""` | Успішне виконання без помилки |
| `[: r :]` де `r` є дескриптором поля поза екземпляром | Помилка синтаксичного аналізу | "non-static member splice requires instance: obj.[: r :]" |
| `extract<int>(^^"invalid")` | Невідповідність типу у вилученні | Помилка `consteval`: неможливо вилучити int із рядка |
| `substitute` з невірною кількістю аргументів | Помилка відповідності шаблону | Помилка збірки: "template argument count mismatch" |
| `offset_of` для статичної змінної | Помилка семантики | Помилка `consteval`: статичні члени не мають зміщення |
| `define_class` із двома однаковими іменами полів | Помилка верифікації структури | Помилка компіляції: повторне оголошення ідентифікатора |
| `report_error("message")` | Виклик функції звітування про помилку | Негайна зупинка компіляції із зазначеним текстом |
