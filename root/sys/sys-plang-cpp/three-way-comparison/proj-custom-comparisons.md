# ⚙️ Практикум: реалізація порівнянь для складних структур

Автоматична генерація операторів порівняння через директиву `= default` вирішує більшість повсякденних задач, коли природний порядок оголошення полів у структурі повністю збігається з бажаним порядком їхнього сортування. Проте в реальних інженерних системах розробник регулярно стикається з архітектурними та алгоритмічними обмеженнями, де стандартне почленне порівняння є або недостатнім, або призводить до серйозних втрат продуктивності.

До таких нетривіальних випадків належать оптимізація швидкодії рядкових структур, робота з числами з плаваючою комою за наявності нечислових значень, регістронезалежність, ієрархічні моделі даних з пріоритетним сортуванням, кешування хешів у великих документах, рекурсивні дерева виразів, часові мітки `std::chrono`, глибокі розумні вказівники, створення ітераторів діапазонів C++20, проекції в алгоритмах пошуку та прозорий гетерогенний пошук в асоціативних контейнерах без виділення динамічної пам'яті.

Розглянемо практичні сценарії проектування, реалізації, верифікації, оптимізації та профілювання користувацьких порівнянь у стандарті C++20.

---

## Сценарій 1. Ієрархічний запис і налаштування пріоритету бізнес-полів

У високонавантажених системах зберігання даних фізичне розташування полів у структурі підпорядковується вимогам вирівнювання пам'яті (Memory Alignment) та мінімізації міжбайтових проміжків (Padding). Водночас бізнес-логіка аналітичних звітів та інтерфейсів користувача вимагає зовсім іншої ієрархії сортування.

### Архітектурна проблема

Уявімо структуру облікового запису працівника `Employee`, яка успадковує базову сутність `BaseEntity`. З міркувань щільності розміщення в пам'яті 64-бітний числовий ідентифікатор стоїть першим, далі йдуть динамічні рядки, а дрібні поля (`uint32_t`, `uint16_t`, `uint8_t`) згруповані наприкінці.

Якби ми використали `= default`, компілятор згенерував би порівняння, де першим критерієм сортування став би технічний числовий ідентифікатор `entity_id`. Проте для генерації штатного розкладу записи повинні групуватися спочатку за номером відділу (`department_id`), потім упорядковуватися за спаданням стажу (`seniority_years`, де досвідченіші працівники йдуть першими), далі — за алфавітом прізвища (`last_name`), імені (`first_name`), і лише за умови повного збігу попередніх критеріїв — за табельним номером `entity_id`.

Крім того, оскільки табельний номер `entity_id` є гарантовано унікальним первинним ключем запису, перевірка двох об'єктів на повну рівність (`==`) може бути виконана миттєво лише за цим одним числовим полем, без потреби читати рядки з динамічної пам'яті.

### Реалізація з розділенням операцій

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <compare>
#include <cstdint>

struct BaseEntity {
    uint64_t entity_id{0};

    // Базовий оператор для ізольованого порівняння ідентифікаторів
    friend constexpr auto operator<=>(const BaseEntity&, const BaseEntity&) = default;
};

class Employee : public BaseEntity {
public:
    // Розташування полів оптимізовано для щільності пакування в пам'яті
    std::string last_name;
    std::string first_name;
    uint32_t    department_id{0};
    uint16_t    seniority_years{0};
    uint8_t     access_level{0};

    Employee(uint64_t id, std::string last, std::string first,
             uint32_t dept, uint16_t seniority, uint8_t access)
        : BaseEntity{id},
          last_name(std::move(last)),
          first_name(std::move(first)),
          department_id(dept),
          seniority_years(seniority),
          access_level(access) {}

    // 1. Оптимізована швидка рівність: унікальний первинний ключ гарантує тотожність
    bool operator==(const Employee& other) const noexcept {
        return entity_id == other.entity_id;
    }

    // 2. Власне тричленне впорядкування за бізнес-пріоритетами
    std::strong_ordering operator<=>(const Employee& other) const noexcept {
        // Крок 1: Групування за відділом (за зростанням номера)
        if (auto cmp = department_id <=> other.department_id; cmp != 0) {
            return cmp;
        }

        // Крок 2: Сортування за стажем (за спаданням: більший стаж іде раніше)
        if (auto cmp = other.seniority_years <=> seniority_years; cmp != 0) {
            return cmp;
        }

        // Крок 3: Алфавітне впорядкування за прізвищем
        if (auto cmp = last_name <=> other.last_name; cmp != 0) {
            return cmp;
        }

        // Крок 4: Алфавітне впорядкування за ім'ям
        if (auto cmp = first_name <=> other.first_name; cmp != 0) {
            return cmp;
        }

        // Крок 5: Остаточний тайбрейкер за унікальним ID
        return entity_id <=> other.entity_id;
    }
};
```

### Покроковий розбір виконання

1. **Миттєвий вихід з перевірки рівності:** Виклик `emp1 == emp2` транслюється в одну машинну інструкцію `cmp` над 64-бітними регістрами. Компілятор навіть не звертається до вказівників на динамічні буфери рядків `last_name` та `first_name`, що запобігає зайвим зверненням до оперативної пам'яті та кеш-промахам.
2. **Сортування за спаданням без створення обгорток:** У кроці 2 вираз `other.seniority_years <=> seniority_years` міняє місцями лівий та правий операнди. Якщо у поточного об'єкта стаж становить 10 років, а в іншого — 3 роки, вираз обчислює `3 <=> 10`, що повертає `std::strong_ordering::less`. Це змушує алгоритм `std::sort` вважати поточний об'єкт меншим (тобто ставити його попереду), забезпечуючи правильне сортування за спаданням без використання громіздких числових інверсій зі зміною знаку.
3. **Раннє переривання обчислення:** Шаблонний ланцюжок `if (auto cmp = ...; cmp != 0) return cmp;` гарантує, що наступні поля аналізуються лише тоді, коли всі попередні виявилися еквівалентними. Якщо два співробітники працюють у різних відділах, порівняння завершується на першому ж кроці за один такт процесора.

---

## Сценарій 2. Регістронезалежний оптимізований рядок (std::weak_ordering)

При обробці текстових протоколів Інтернету (заголовки протоколу HTTP/2, DNS-запити, адреси електронної пошти) порівняння рядків зобов'язане ігнорувати регістр символів ASCII.

### Архітектурна проблема

Звичайний клас `std::string` забезпечує сильний порядок (`std::strong_ordering`). Проте для регістронезалежного рядка два об'єкти з різними байтовими послідовностями (наприклад, `"Authorization"` та `"authorization"`) повинні вважатися еквівалентними при пошуку в таблицях маршрутизації.

Це класичний приклад слабкого порядку: об'єкти займають однакову позицію при сортуванні, але їхній внутрішній стан різниться (наприклад, функція взяття першого символу поверне велику літеру в одному випадку і малу в іншому).

Крім того, перевірка рівності повинна працювати максимально швидко: якщо довжини двох заголовків відрізняються, результат `false` має повертатися миттєво без посимвольного сканування.

### Реалізація класу CiString

```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <cctype>
#include <cstring>
#include <compare>
#include <algorithm>

class CiString {
    std::string str;

    // Швидке посимвольне порівняння без урахування регістру ASCII
    static int char_case_cmp(char a, char b) noexcept {
        auto ua = static_cast<unsigned char>(a);
        auto ub = static_cast<unsigned char>(b);
        int ca = std::tolower(ua);
        int cb = std::tolower(ub);
        return (ca > cb) - (ca < cb);
    }

public:
    CiString() = default;
    CiString(std::string s) : str(std::move(s)) {}
    CiString(const char* s) : str(s) {}

    const std::string& get() const noexcept { return str; }
    std::string_view view() const noexcept { return str; }
    size_t size() const noexcept { return str.size(); }

    // 1. Оптимізована перевірка рівності: O(1) за розміром, далі O(N)
    bool operator==(const CiString& other) const noexcept {
        if (str.size() != other.str.size()) {
            return false;
        }
        for (size_t i = 0; i < str.size(); ++i) {
            if (std::tolower(static_cast<unsigned char>(str[i])) !=
                std::tolower(static_cast<unsigned char>(other.str[i]))) {
                return false;
            }
        }
        return true;
    }

    // 2. Тричленне порівняння слабкого порядку
    std::weak_ordering operator<=>(const CiString& other) const noexcept {
        size_t min_len = std::min(str.size(), other.str.size());
        for (size_t i = 0; i < min_len; ++i) {
            int diff = char_case_cmp(str[i], other.str[i]);
            if (diff < 0) return std::weak_ordering::less;
            if (diff > 0) return std::weak_ordering::greater;
        }
        // Якщо спільний префікс збігся, коротший рядок іде раніше
        return str.size() <=> other.str.size();
    }
};
```

### Поглиблений аналіз різниці між == та <=>

Розглянемо, як процесор виконує операції над рядками різної довжини:

```cpp
CiString a = "Content-Length";  // довжина 14
CiString b = "Host";            // довжина 4
```

1. **Вираз `a == b`:**
   Перший рядок оператора перевіряє `str.size() != other.str.size()`. Оскільки `14 != 4`, функція негайно повертає `false`. Жоден символ із пам'яті не читається, перетворення `std::tolower` не викликається. Часова складність становить `O(1)`.
2. **Вираз `a <=> b`:**
   Оператор визначає мінімальну довжину `min_len = 4` і починає посимвольне порівняння. На першому ж символі `'C'` проти `'H'` (у нижньому регістрі `'c'` проти `'h'`) обчислюється різниця кодів, і повертається `std::weak_ordering::less`.
3. **Вираз `CiString("abc") <=> CiString("ABCDEF")`:**
   Перші три символи еквівалентні. Цикл завершується, після чого виконується фінальний рядок `str.size() <=> other.str.size()`, який повертає `3 <=> 6`, тобто `std::weak_ordering::less`.

Цей приклад наочно демонструє, чому C++20 не генерує `==` через виклик `<=> == 0`: швидка перевірка довжини в `operator==` забезпечує багаторазове прискорення роботи контейнерів та асоціативних масивів.

---

## Сценарій 3. Геометричні координати з NaN і адаптер тотального порядку

Обчислення у графічних рушіях, системах комп'ютерного зору та фізичних симуляторах оперують числами з плаваючою комою. Некоректні операції (ділення нуля на нуль, взяття кореня з від'ємного числа) призводять до виникнення спеціальних нечислових значень `NaN` (Not-a-Number).

### Проблема падіння стандартних контейнерів із частковим порядком

Стандартний оператор `<=>` для типу `double` повертає `std::partial_ordering`. Якщо координата містить `NaN`, результат будь-якого реляційного порівняння дорівнює `std::partial_ordering::unordered`.

Проте стандартні алгоритми та контейнери C++ — такі як `std::sort`, `std::set` та `std::map` — спираються на концепцію строгого слабкого порядку (Strict Weak Ordering). Головна вимога цієї концепції полягає в тому, що відношення еквівалентності повинно бути транзитивним, а значення не можуть бути незрівнюваними самі з собою.

Якщо помістити структуру з частковим порядком і значенням `NaN` у стандартний `std::set` або викликати для неї `std::sort`, компаратор поверне `false` для виразів `a < b` та `b < a`, хибно вважаючи їх рівними, але водночас відмовиться визнавати `NaN == NaN`. Це призводить до порушення інваріантів червоно-чорного дерева, зациклення алгоритму швидкого сортування introsort або виходу за межі виділеної пам'яті (Heap Buffer Overflow).

### Реалізація структури Point3D та безпечного адаптера

```cpp
#include <iostream>
#include <cmath>
#include <compare>
#include <set>
#include <limits>

// Базова геометрична точка: природний частковий порядок
struct Point3D {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    // Автоматично виводить std::partial_ordering через double
    constexpr auto operator<=>(const Point3D&) const = default;
};

// Адаптер тотального порядку для безпечного використання в контейнерах і сортуванні
struct TotalOrderPoint3D {
    Point3D pt;

    // Явне використання стандартного CPO std::strong_order
    std::strong_ordering operator<=>(const TotalOrderPoint3D& other) const noexcept {
        if (auto cmp = std::strong_order(pt.x, other.pt.x); cmp != 0) {
            return cmp;
        }
        if (auto cmp = std::strong_order(pt.y, other.pt.y); cmp != 0) {
            return cmp;
        }
        return std::strong_order(pt.z, other.pt.z);
    }

    bool operator==(const TotalOrderPoint3D& other) const noexcept {
        return (*this <=> other) == 0;
    }
};
```

### Порівняльний експеримент і верифікація

```cpp
void run_floating_point_experiment() {
    double nan1 = std::numeric_limits<double>::quiet_NaN();
    double nan2 = std::numeric_limits<double>::quiet_NaN();

    Point3D raw_p1{nan1, 0.0, 0.0};
    Point3D raw_p2{nan2, 0.0, 0.0};

    // 1. Поведінка звичайного часткового порядку
    auto partial_cmp = (raw_p1 <=> raw_p2);
    std::cout << "Raw points equal: " << (raw_p1 == raw_p2) << "\n"; // false (NaN != NaN)
    std::cout << "Is unordered: "
              << (partial_cmp == std::partial_ordering::unordered) << "\n"; // true

    // 2. Поведінка адаптера тотального порядку
    TotalOrderPoint3D safe_p1{raw_p1};
    TotalOrderPoint3D safe_p2{raw_p2};

    auto total_cmp = (safe_p1 <=> safe_p2);
    std::cout << "Safe points equal: " << (safe_p1 == safe_p2) << "\n"; // true!
    std::cout << "Is strong equal: "
              << (total_cmp == std::strong_ordering::equal) << "\n"; // true

    // 3. Безпечна робота з std::set: дедуплікація та відсутність невизначеної поведінки
    std::set<TotalOrderPoint3D, std::less<>> safe_set;
    safe_set.insert(safe_p1);
    safe_set.insert(safe_p2);

    std::cout << "Set size with NaN duplicates: " << safe_set.size() << "\n"; // Рівно 1!
}
```

Об'єкт `std::strong_order` розглядає бітове представлення чисел із плаваючою комою за стандартом IEEE 754-2008, чітко позиціонуючи всі можливі види `NaN` на єдиній числовій прямій. Це дозволяє гарантувати детерміновану роботу асоціативних контейнерів у будь-яких крайових умовах.

---

## Сценарій 4. Прозорий гетерогенний пошук без виділення пам'яті

Класична проблема продуктивності під час використання стандартних асоціативних контейнерів `std::set<Record>` або `std::map<Key, Value>` полягає у вимушеному створенні тимчасових об'єктів під час пошуку.

### Архітектурна проблема

Якщо ключем запису є `std::string`, виклик `records_set.find("admin")` у стандартах до C++14 змушений був неявно викликати конструктор `std::string("admin")`, що призводило до динамічного виділення пам'яті в купі та наступного виклику деструктора.

У C++20 завдяки концептам та переписаним кандидатам оператора тричленного порівняння гетерогенний пошук стає максимально простим у реалізації та повністю симетричним.

### Реалізація класу UserRecord з гетерогенними операторами

```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <set>
#include <compare>

class UserRecord {
    uint64_t    id{0};
    std::string username;
    std::string department;

public:
    UserRecord(uint64_t uid, std::string name, std::string dept)
        : id(uid), username(std::move(name)), department(std::move(dept)) {}

    uint64_t get_id() const noexcept { return id; }
    std::string_view get_username() const noexcept { return username; }

    // 1. Однорідне порівняння двох повноцінних об'єктів UserRecord
    friend auto operator<=>(const UserRecord& a, const UserRecord& b) noexcept {
        return a.username <=> b.username;
    }
    friend bool operator==(const UserRecord& a, const UserRecord& b) noexcept {
        return a.username == b.username;
    }

    // 2. Гетерогенне порівняння з невласницьким видом std::string_view
    friend auto operator<=>(const UserRecord& a, std::string_view sv) noexcept {
        return a.username <=> sv;
    }
    friend bool operator==(const UserRecord& a, std::string_view sv) noexcept {
        return a.username == sv;
    }

    // 3. Гетерогенне порівняння з числовим первинним ключем ID
    friend auto operator<=>(const UserRecord& a, uint64_t target_id) noexcept {
        return a.id <=> target_id;
    }
    friend bool operator==(const UserRecord& a, uint64_t target_id) noexcept {
        return a.id == target_id;
    }
};
```

### Застосування у прозорих контейнерах

Для того щоб увімкнути підтримку гетерогенного пошуку, другим шаблонним параметром контейнера `std::set` вказується прозорий компаратор `std::less<>` (із порожніми кутовими дужками). Цей компаратор містить внутрішній маркерний псевдонім типу `using is_transparent = void;`.

```cpp
using namespace std::string_view_literals;

void demonstrate_zero_allocation_lookup() {
    std::set<UserRecord, std::less<>> user_directory;

    user_directory.emplace(1001, "artem_s", "Core-Engineering");
    user_directory.emplace(1002, "diana_v", "Security-Ops");
    user_directory.emplace(1003, "ivan_k", "Infrastructure");

    // Пошук за string_view: жодного виділення пам'яті в купі!
    std::string_view target_user = "diana_v"sv;
    auto it = user_directory.find(target_user);

    if (it != user_directory.end()) {
        std::cout << "Знайдено користувача ID: " << it->get_id() << "\n";
    }

    // Демонстрація симетрії C++20:
    // Вираз target_user == *it автоматично перетворюється компілятором
    // у виклик дружньої функції *it == target_user без необхідності
    // писати дзеркальне перевантаження operator==(std::string_view, const UserRecord&)!
    if (target_user == *it) {
        std::cout << "Симетрична перевірка рівності успішна.\n";
    }
}
```

---

## Сценарій 5. Користувацький ітератор довільного доступу (Random Access Iterator)

У C++20 концепція ітераторів довільного доступу (`std::random_access_iterator`) вимагає наявності оператора `<=>`.

### Архітектурна проблема

До появи стандарту C++20 автор власного ітератора довільного доступу мусив оголошувати шість операторів порівняння (`==`, `!=`, `<`, `<=`, `>`, `>=`), а також перевантажувати їх для константних та неконстантних пар ітераторів (`Iterator` та `ConstIterator`). Це вимагало написання понад 12 однакових шаблонних функцій.

У C++20 завдяки тричленному порівнянню та синтезу переписаних кандидатів достатньо реалізувати всього один дружній оператор `<=>` і один `operator==`.

### Реалізація компактного ітератора

```cpp
#include <iterator>
#include <compare>
#include <cstddef>
#include <type_traits>

template <class T>
class CompactSpanIterator {
    T* ptr{nullptr};

public:
    using iterator_concept  = std::contiguous_iterator_tag;
    using iterator_category = std::random_access_iterator_tag;
    using value_type        = std::remove_cv_t<T>;
    using difference_type   = std::ptrdiff_t;
    using pointer           = T*;
    using reference         = T&;

    constexpr CompactSpanIterator() noexcept = default;
    constexpr explicit CompactSpanIterator(T* p) noexcept : ptr(p) {}

    // Конвертація з non-const у const ітератор
    template <class U>
        requires std::is_convertible_v<U*, T*>
    constexpr CompactSpanIterator(const CompactSpanIterator<U>& other) noexcept
        : ptr(other.base()) {}

    constexpr T* base() const noexcept { return ptr; }
    constexpr reference operator*() const noexcept { return *ptr; }
    constexpr pointer operator->() const noexcept { return ptr; }

    constexpr CompactSpanIterator& operator++() noexcept { ++ptr; return *this; }
    constexpr CompactSpanIterator operator++(int) noexcept { auto tmp = *this; ++ptr; return tmp; }
    constexpr CompactSpanIterator& operator--() noexcept { --ptr; return *this; }
    constexpr CompactSpanIterator operator--(int) noexcept { auto tmp = *this; --ptr; return tmp; }

    constexpr CompactSpanIterator& operator+=(difference_type n) noexcept { ptr += n; return *this; }
    constexpr CompactSpanIterator& operator-=(difference_type n) noexcept { ptr -= n; return *this; }
    constexpr reference operator[](difference_type n) const noexcept { return ptr[n]; }

    friend constexpr difference_type operator-(const CompactSpanIterator& a, const CompactSpanIterator& b) noexcept {
        return a.ptr - b.ptr;
    }
    friend constexpr CompactSpanIterator operator+(CompactSpanIterator it, difference_type n) noexcept {
        return it += n;
    }
    friend constexpr CompactSpanIterator operator+(difference_type n, CompactSpanIterator it) noexcept {
        return it += n;
    }
    friend constexpr CompactSpanIterator operator-(CompactSpanIterator it, difference_type n) noexcept {
        return it -= n;
    }

    // Усі 6 операторів порівняння синтезуються з цих двох рядків!
    friend constexpr std::strong_ordering operator<=>(
        const CompactSpanIterator& a, const CompactSpanIterator& b) noexcept
    {
        return a.ptr <=> b.ptr;
    }

    friend constexpr bool operator==(
        const CompactSpanIterator& a, const CompactSpanIterator& b) noexcept
    {
        return a.ptr == b.ptr;
    }
};
```

Цей ітератор автоматично задовольняє всім концептам `std::contiguous_iterator`, `std::random_access_iterator` та `std::three_way_comparable`, коректно підтримуючи змішані порівняння між `CompactSpanIterator<int>` та `CompactSpanIterator<const int>`.

---

## Сценарій 6. Кешування хешів та порівняння великих документів

У текстових редакторах, парсерах коду та системах обробки великих наборів даних об'єкти документів містять тисячі рядків. Порівняння двох документів на рівність є надзвичайно частою операцією (наприклад, під час перевірки потреби оновлення дерева відображення).

### Архітектурна проблема

Для прискорення перевірки рівності документи часто обчислюють 64-бітний хеш вмісту `content_hash` під час створення.
- **Для перевірки рівності (`==`):** спершу перевіряються вказівники на об'єкти (`this == &other`), далі порівнюються числові хеші `content_hash` (одна машинна інструкція `cmp`). Лише при колізії хешів виконується повнотекстове порівняння вмісту.
- **Для тричленного порядку (`<=>`):** числові хеші **не мають права використовуватися для визначення порядку**, оскільки хеш-функція навмисно перемішує біти й не зберігає лексикографічний алфавітний порядок слів! Якщо документ `"Apple"` має хеш `0xFF`, а `"Banana"` — `0x01`, порівняння за хешем призведе до хибного висновку, що `"Apple" > "Banana"`.

Тому `operator<=>` зобов'язаний виконувати справжнє лексикографічне сканування рядків.

### Реалізація класу ImmutableDocument

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <compare>
#include <algorithm>
#include <cstdint>

class ImmutableDocument {
    uint64_t                 content_hash{0};
    std::vector<std::string> lines;

    static uint64_t compute_hash(const std::vector<std::string>& lns) noexcept {
        uint64_t h = 14695981039346656037ULL; // FNV-1a offset basis
        for (const auto& line : lns) {
            for (char c : line) {
                h ^= static_cast<unsigned char>(c);
                h *= 1099511628211ULL; // FNV-1a prime
            }
        }
        return h;
    }

public:
    ImmutableDocument(std::vector<std::string> lns)
        : content_hash(compute_hash(lns)), lines(std::move(lns)) {}

    // 1. Оптимізована рівність: адреса -> хеш -> повний вміст
    bool operator==(const ImmutableDocument& other) const noexcept {
        // Рівень 1: Тотожність адреси в пам'яті (O(1))
        if (this == &other) {
            return true;
        }
        // Рівень 2: Збіг предобчисленого 64-бітного хешу (O(1))
        if (content_hash != other.content_hash) {
            return false;
        }
        // Рівень 3: Повний захист від колізій хешу (O(N))
        return lines == other.lines;
    }

    // 2. Лексикографічний порядок: винятково через вміст
    std::strong_ordering operator<=>(const ImmutableDocument& other) const noexcept {
        if (this == &other) {
            return std::strong_ordering::equal;
        }
        return std::lexicographical_compare_three_way(
            lines.begin(), lines.end(),
            other.lines.begin(), other.lines.end()
        );
    }
};
```

Цей шаблон демонструє найвищу культуру проектування продуктивного C++20 коду: рівність отримує швидкість `O(1)` завдяки хешуванню, а порядок залишається бездоганно точним та строго детермінованим.

---

## Сценарій 7. Рекурсивне синтаксичне дерево (AST) на основі std::variant

У компіляторах та інтерпретаторах математичних виразів синтаксичні вузли часто представляються як розмічені об'єднання `std::variant`.

### Архітектурна проблема

Розглянемо вузол синтаксичного дерева `ExprNode`, який може містити або цілочисельну константу, або ім'я змінної, або вкладений бінарний вираз у динамічній пам'яті (`std::unique_ptr`).

Стандартний клас `std::variant` у C++20 підтримує `operator<=>`, спочатку порівнюючи дискримінатор активного типу `index()`, а у разі збігу індексів — активні значення альтернатив. Проте `std::unique_ptr` за замовчуванням порівнює числові адреси покажчиків у пам'яті, а не значення під ними.

Для коректного глибокого порівняння синтаксичних дерев розробник зобов'язаний реалізувати оператор розіменування покажчиків всередині компаратора.

### Реалізація глибокого порівняння AST-вузлів

```cpp
#include <iostream>
#include <string>
#include <variant>
#include <memory>
#include <compare>

struct BinaryOp;

using ExprPayload = std::variant<
    int64_t,
    std::string,
    std::unique_ptr<BinaryOp>
>;

struct ExprNode {
    ExprPayload payload;

    // Глибоке тричленне порівняння вузлів дерева
    friend std::strong_ordering operator<=>(const ExprNode& a, const ExprNode& b);
    friend bool operator==(const ExprNode& a, const ExprNode& b);
};

struct BinaryOp {
    char     op{'+'};
    ExprNode left;
    ExprNode right;

    auto operator<=>(const BinaryOp& other) const = default;
};

std::strong_ordering operator<=>(const ExprNode& a, const ExprNode& b) {
    if (a.payload.index() != b.payload.index()) {
        return a.payload.index() <=> b.payload.index();
    }

    return std::visit([&](const auto& valA) -> std::strong_ordering {
        using T = std::decay_t<decltype(valA)>;
        const auto& valB = std::get<T>(b.payload);

        if constexpr (std::is_same_v<T, std::unique_ptr<BinaryOp>>) {
            if (!valA && !valB) return std::strong_ordering::equal;
            if (!valA) return std::strong_ordering::less;
            if (!valB) return std::strong_ordering::greater;
            // Рекурсивне глибоке розіменування
            return *valA <=> *valB;
        } else {
            return valA <=> valB;
        }
    }, a.payload);
}

bool operator==(const ExprNode& a, const ExprNode& b) {
    return (a <=> b) == 0;
}
```

Завдяки патерну `std::visit` та перевірці `if constexpr` рекурсивне синтаксичне дерево отримує повну підтримку тричленного порівняння без витоків пам'яті та з коректною обробкою нульових покажчиків.

---

## Сценарій 8. Гетерогенний бінарний пошук у діапазонах через проекції

У стандартній бібліотеці C++20 алгоритми сімейства `std::ranges` отримали фундаментальну підтримку функцій-проекцій (Projections). Це дозволяє виконувати пошук у відсортованих послідовностях за окремими полями структури без створення тимчасових об'єктів і без написання спеціальних лямбда-компараторів.

### Архітектурна проблема

Розглянемо великий відсортований вектор записів `std::vector<CompactProduct>`. Нам необхідно знайти перший запис, що належить певному артикулу `sku_code`, використовуючи алгоритм бінарного пошуку `std::ranges::lower_bound`.

У C++17 для цього доводилося або конструювати фіктивний об'єкт `CompactProduct` із заповненим полем артикулу, або передавати спеціальний бінарний предикат `[](const CompactProduct& e, uint32_t sku) { return e.sku_code < sku; }`.

У C++20 алгоритми діапазонів автоматично використовують `operator<=>` через `std::compare_three_way` у поєднанні з покажчиком на член класу як проекцією.

### Реалізація пошуку з проекцією

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <ranges>

struct CompactProduct {
    uint32_t    sku_code{0};
    double      price{0.0};
    std::string title;

    // Стандартне впорядкування за SKU
    auto operator<=>(const CompactProduct& other) const = default;
};

void run_projected_binary_search() {
    std::vector<CompactProduct> catalog = {
        {1010, 19.99, "USB Cable"},
        {1020, 49.50, "Power Adapter"},
        {1030, 99.00, "Wireless Mouse"},
        {1040, 150.0, "Mechanical Keyboard"}
    };

    // 1. Пошук за цілочисельним SKU без створення об'єкта CompactProduct!
    // Покажчик &CompactProduct::sku_code слугує проекцією, а компаратор за замовчуванням
    // використовує тричленне порівняння для uint32_t.
    uint32_t target_sku = 1030;
    auto it = std::ranges::lower_bound(catalog, target_sku, {}, &CompactProduct::sku_code);

    if (it != catalog.end() && it->sku_code == target_sku) {
        std::cout << "Знайдено товар: " << it->title << ", ціна: " << it->price << "\n";
    }

    // 2. Двійковий пошук за діапазоном цін
    double target_price = 49.50;
    bool exists = std::ranges::binary_search(catalog, target_price, {}, &CompactProduct::price);
    std::cout << "Товар із ціною 49.50 існує: " << std::boolalpha << exists << "\n";
}
```

Використання проекцій разом із тричленним порівнянням усуває необхідність ручного написання десятків предикатних функцій і гарантує генерацію найбільш компактного машинного коду бінарного пошуку.

---

## Сценарій 9. Розумний покажчик із глибоким порівнянням (Deep Pointer)

Стандартні розумні вказівники `std::unique_ptr<T>` та `std::shared_ptr<T>` у C++20 надають оператор `<=>`, який порівнює числові адреси покажчиків у пам'яті (Shallow Comparison). Проте в об'єктно-орієнтованих структурах документів та патерні «Міст» (PIMPL) об'єкти вимагають порівняння значень, розташованих під покажчиками (Deep Comparison).

### Реалізація обгортки DeepPtr

```cpp
#include <iostream>
#include <memory>
#include <compare>

template <class T>
class DeepPtr {
    std::unique_ptr<T> ptr;

public:
    DeepPtr() = default;
    explicit DeepPtr(T* p) : ptr(p) {}
    explicit DeepPtr(std::unique_ptr<T> p) : ptr(std::move(p)) {}

    T* get() const noexcept { return ptr.get(); }
    T& operator*() const noexcept { return *ptr; }
    T* operator->() const noexcept { return ptr.get(); }
    explicit operator bool() const noexcept { return static_cast<bool>(ptr); }

    // Глибоке тричленне порівняння з коректною обробкою nullptr
    friend auto operator<=>(const DeepPtr& a, const DeepPtr& b) noexcept(
        noexcept(std::declval<const T&>() <=> std::declval<const T&>()))
    {
        if (a.ptr == b.ptr) return std::strong_ordering::equal;
        if (!a.ptr) return std::strong_ordering::less;
        if (!b.ptr) return std::strong_ordering::greater;
        return *a.ptr <=> *b.ptr;
    }

    friend bool operator==(const DeepPtr& a, const DeepPtr& b) noexcept(
        noexcept(std::declval<const T&>() == std::declval<const T&>()))
    {
        if (a.ptr == b.ptr) return true;
        if (!a.ptr || !b.ptr) return false;
        return *a.ptr == *b.ptr;
    }
};
```

Ця обгортка дозволяє використовувати поліморфні ресурси в структурах, які автоматично генерують `= default` оператори, гарантуючи правильну семантику глибокого копіювання та порівняння.

---

## Сценарій 10. Мережеві пакети з мітками часу std::chrono

У телеметричних системах та високочастотній торгівлі мережеві пакети повинні впорядковуватися за абсолютною часовою міткою прийому (`std::chrono::system_clock::time_point`), потім за числовим рівнем пріоритету `priority` (вищий пріоритет іде раніше), а далі — за послідовним номером `sequence_id`.

```cpp
#include <iostream>
#include <chrono>
#include <compare>
#include <cstdint>

struct TelemetryPacket {
    std::chrono::system_clock::time_point timestamp;
    uint32_t sequence_id{0};
    uint8_t  priority{0};

    // 1. Рівність за унікальним послідовним номером
    bool operator==(const TelemetryPacket& o) const noexcept {
        return sequence_id == o.sequence_id && timestamp == o.timestamp;
    }

    // 2. Впорядкування за хронологією та пріоритетом
    std::strong_ordering operator<=>(const TelemetryPacket& o) const noexcept {
        // Хронологічний порядок часу (раніші пакети йдуть попереду)
        if (auto cmp = timestamp <=> o.timestamp; cmp != 0) {
            return cmp;
        }
        // Вищий пріоритет іде попереду (сортування за спаданням через перестановку операндів)
        if (auto cmp = o.priority <=> priority; cmp != 0) {
            return cmp;
        }
        return sequence_id <=> o.sequence_id;
    }
};
```

---

## Діагностика типових пасток при проектуванні порівнянь

### 1. Пастка рекурсивної неоднозначності при міграції з C++17

Якщо клас містить неявний конструктор з іншого типу або оператор неявного приведення типів, правила генерації перевернутих кандидатів у C++20 можуть перетворити раніше валідний код C++17 на помилку компіляції.

#### Приклад проблеми

```cpp
struct LegacyBuffer {
    const char* data;
    LegacyBuffer(const char* s) : data(s) {}

    // У C++17 цей метод працював лише для викликів buf == "test"
    bool operator==(const char* s) const {
        return std::strcmp(data, s) == 0;
    }
};

void check_buffer(LegacyBuffer buf) {
    // У C++20 цей вираз породжує фатальну неоднозначність (ambiguity):
    // Кандидат 1: неявне приведення "test" до LegacyBuffer і виклик порівняння двох об'єктів.
    // Кандидат 2: переписаний перевернутий виклик buf.operator==("test").
    // if ("test" == buf) { ... } // Помилка компіляції: ambiguous overload!
}
```

#### Спосіб вирішення

1. Оголошувати всі однопараметричні конструктори як `explicit`, запобігаючи небажаним неявним перетворенням типів.
2. Реалізовувати оператори порівняння як дружні приховані функції (`hidden friends`), які приймають обидва операнди симетрично.

### 2. Пастка зрізання стану (Slicing) в поліморфних ієрархіях

Якщо базовий клас визначає `operator<=>(const Base&) const = default;`, а виклик порівняння здійснюється через посилання на базовий тип `const Base&`, компілятор порівняє винятково поля базового класу, повністю проігнорувавши поля похідного об'єкта `Derived`.

Для поліморфних ієрархій рекомендується забороняти відкритий оператор порівняння у базовому класі або реалізовувати віртуальний захищений метод із явною перевіркою динамічного типу об'єкта через `typeid`.

### 3. Пастка випадкового повернення bool з operator<=>

Оператор `<=>` повинен повертати один із типів категорій порівняння (`std::strong_ordering`, `std::weak_ordering`, `std::partial_ordering`) або числовий результат примітивного скалярного порівняння.

Якщо розробник помилково вкаже тип повернення `bool`, компілятор згенерує помилку, оскільки реляційні вирази переписуються у вигляд `(a <=> b) < 0`, а порівняння `bool < int` призводить до некоректної булевої арифметики.

### 4. Відсутність кваліфікатора const у методі-члені

Якщо оператор `<=>` оголошується як метод класу, він обов'язково повинен мати специфікатор `const`:
```cpp
// Помилка: неконстантний метод
std::strong_ordering operator<=>(const MyClass& other);

// Правильно: константний метод
std::strong_ordering operator<=>(const MyClass& other) const;
```
В іншому випадку спроба порівняти константні екземпляри класу або використати об'єкти в контейнерах `std::set` (де всі елементи розглядаються як `const`) призведе до помилки компіляції: компілятор відкине неконстантний кандидат під час розв'язання перевантажень.

### 5. Повернення посилання замість значення категорії

Типи категорій порівняння є легкозважними скалярними об'єктами розміром в один байт. Вони завжди повинні повертатися за значенням, а не за посиланням (`const std::strong_ordering&`). Повернення константного посилання на результат проміжного обчислення у виразі `auto cmp = a.x <=> b.x; return cmp;` створює висяче посилання на локальну змінну, що викликає важковловиму невизначену поведінку (Undefined Behavior) під час виконання програми.
