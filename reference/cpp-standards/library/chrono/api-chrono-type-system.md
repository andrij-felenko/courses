# 📋 Специфікація типів та інтерфейсу std::chrono

Інтерфейс заголовочного файла `<chrono>` (простір імен `std::chrono`) надає широкий набір шаблонів класів, типів годинників, календарних структур та функцій форматування для роботи з часом як на етапі компіляції, так і під час виконання програми. Головна мета цього інтерфейсу — гарантувати математичну та фізичну коректність операцій над часовими величинами через строгу типізацію. Ниже наведено повну технічну специфікацію типів, сигнатур, контрактів та механізмів їхньої взаємодії.

## 1. Шаблон тривалості std::chrono::duration та метапрограмування раціональних чисел

Класовий шаблон `duration` представляє часовий інтервал (скалярну величину), що складається з лічильника тиків `Rep` та описувача періоду тику `Period`, вираженого через шаблон статичних раціональних чисел `std::ratio`.

```cpp
template <class Rep, class Period = std::ratio<1>>
class duration;
```

### Параметри шаблону та фундаментальні контракти

Параметр `Rep` описує числовий тип, який зберігає кількість виміряних тиків. Це може бути цілочисельний тип зі знаком чи без (наприклад, `int64_t`, `int32_t`) або тип із плаваючою точкою (`double`, `float`). Якщо `Rep` є типом із плаваючою точкою, тривалість може зберігати дробові частини тиків, і всі перетворення між різними періодами дозволяються неявно без ризику втрати точності. Якщо `Rep` є цілим числом, арифметика виконується за правилами цілочисельної алгебри з можливим переповненням або усіченням дробової частини.

Параметр `Period` описує тривалість одного тику у секундах і повинен бути інстанціацією шаблону `std::ratio<Num, Denom>`, де `Num` та `Denom` — константи типу `std::intmax_t`. Наприклад, `std::ratio<1, 1000>` означає, що один тик дорівнює 1/1000 секунди (мілісекунда), а `std::ratio<60, 1>` вказує на тик тривалістю 60 секунд (хвилина). Меташаблон `std::ratio` автоматично скорочує дріб на етапі компіляції за допомогою алгоритму Евкліда для пошуку наибольшого спільного дільника (НСД/GCD), запобігаючи переповненню типів при множенні та діленні масштабних коефіцієнтів.

### Механіка неявних конверсій та std::common_type

Система типів `std::chrono` розрізняє безпечні та потенційно небезпечні перетворення тривалостей. Неявне перетворення з джерельного типу `duration<Rep1, Period1>` у цільовий тип `duration<Rep2, Period2>` дозволяється компілятором лише за виконання двох умов:
1. Цільовий тип `Rep2` є типом із плаваючою точкою, АБО джерельний тип `Rep1` НЕ є типом із плаваючою точкою І період `Period1` націло ділиться на період `Period2` (тобто `Period1::num * Period2::den` ділиться без залишку на `Period1::den * Period2::num`).
2. Внаслідок цього перетворення не відбувається втрати точності дробової частини. Наприклад, перетворення з `seconds` у `milliseconds` є неявним та безпечним, оскільки 1 секунда точно дорівнює 1000 мілісекундам. Зворотне перетворення з `milliseconds` у `seconds` не є неявним, оскільки 1500 мілісекунд у цілочисельному вираженні секунд призведе до втрати 500 мілісекунд.

При виконанні бінарних арифметичних операцій (наприклад, додавання двох тривалостей різного типу `d1 + d2`) результат автоматично приводиться до спільного типу через спеціалізацію шаблону `std::common_type`. Для двох тривалостей `std::common_type_t<duration<R1, P1>, duration<R2, P2>>` обирає спільний тип лічильника та найменший спільний дільник двох періодів `P1` та `P2`. Це гарантує, що при додаванні `seconds` та `milliseconds` результатом буде `milliseconds`, що запобігає втраті точності обчислень.

### Двовимірна арифметика ділення та залишку тривалостей

Окрім додавання та віднімання, шаблон `duration` підтримує бінарні операції ділення та взяття залишку за модулем:
- Ділення тривалості на скалярний тип `Rep` (`d / s`) повертає нову тривалість того самого типу.
- Ділення двох тривалостей однакового чи сумісного періоду (`d1 / d2`) повертає скалярне число спільного типу `std::common_type_t<Rep1, Rep2>`, яке означає, скільки разів тривалість `d2` вміщується у тривалості `d1`.
- Операція залишку від ділення `d1 % d2` повертає нову тривалість спільного типу, яка описує лишок після цілочисельного ділення.

```cpp
using namespace std::chrono;
milliseconds ms{2500};
seconds s{1};

// Скалярне ділення двох тривалостей: 2500 ms / 1000 ms = 2 (скалярне ціле)
auto count_ratio = ms / s; 

// Операція залишку: 2500 ms % 1000 ms = 500 ms (тривалість)
milliseconds remainder = ms % s; 
```

### Стандартні псевдоніми типів тривалості

Стандарт C++ надає набір готових псевдонімів типів у просторі імен `std::chrono`:

```cpp
using nanoseconds  = duration<std::int_least64_t, std::nano>;
using microseconds = duration<std::int_least64_t, std::micro>;
using milliseconds = duration<std::int_least64_t, std::milli>;
using seconds      = duration<std::int_least64_t>;
using minutes      = duration<std::int_least32_t, std::ratio<60>>;
using hours        = duration<std::int_least32_t, std::ratio<3600>>;
using days         = duration<std::int_least32_t, std::ratio<86400>>;
using weeks        = duration<std::int_least32_t, std::ratio<604800>>;
using months       = duration<std::int_least32_t, std::ratio<2629746>>;
using years        = duration<std::int_least32_t, std::ratio<31556952>>;
```

### Публічний інтерфейс та методи класу duration

```cpp
template <class Rep, class Period>
class duration {
public:
    using rep = Rep;
    using period = typename Period::type;

    // Конструктори
    constexpr duration() = default;
    template <class Rep2>
    explicit constexpr duration(const Rep2& r);
    template <class Rep2, class Period2>
    constexpr duration(const duration<Rep2, Period2>& d);

    // Селектори
    constexpr rep count() const { return r_; }

    // Статичні межові методи
    static constexpr duration zero() noexcept { return duration(Rep(0)); }
    static constexpr duration min() noexcept  { return duration(std::numeric_limits<Rep>::lowest()); }
    static constexpr duration max() noexcept  { return duration(std::numeric_limits<Rep>::max()); }

    // Унарні оператори
    constexpr duration operator+() const { return *this; }
    constexpr duration operator-() const { return duration(-r_); }

    // Інкремент та декремент
    constexpr duration& operator++() { ++r_; return *this; }
    constexpr duration operator++(int) { return duration(r_++); }
    constexpr duration& operator--() { --r_; return *this; }
    constexpr duration operator--(int) { return duration(r_--); }

    // Составні оператори присвоєння
    constexpr duration& operator+=(const duration& d) { r_ += d.count(); return *this; }
    constexpr duration& operator-=(const duration& d) { r_ -= d.count(); return *this; }
    constexpr duration& operator*=(const rep& rhs)   { r_ *= rhs; return *this; }
    constexpr duration& operator/=(const rep& rhs)   { r_ /= rhs; return *this; }
    constexpr duration& operator%=(const rep& rhs)   { r_ %= rhs; return *this; }
    constexpr duration& operator%=(const duration& d) { r_ %= d.count(); return *this; }
private:
    rep r_;
};
```

### Явні функції явного приведення тривалостей

Для перетворення тривалостей із більшого періоду у менший або при цілочисельному відтинанні використовуються спеціальні допоміжні функції явного приведення:

1. `std::chrono::duration_cast<ToDuration>(d)`: здійснює примусове перетворення до типу `ToDuration` із відтинанням дробової частини в напрямку до нуля (аналогічно до `static_cast` для цілих чисел).
2. `std::chrono::floor<ToDuration>(d)` (C++17): здійснює округлення тривалості донизу, у бік мінус нескінченності. Це корисно при обчисленні календарних сіток, щоб від'ємні тривалості округлялися коректно.
3. `std::chrono::ceil<ToDuration>(d)` (C++17): здійснює округлення тривалості догори, у бік плюс нескінченності. Використовується при розрахунку таймаутів ожидання, щоб запобігти передчасному розблокуванню потоків.
4. `std::chrono::round<ToDuration>(d)` (C++17): здійснює округлення до найближчого значення. Якщо тривалість знаходиться точно посередині між двома значеннями, округлення виконується до найближчого парного числа.
5. `std::chrono::abs(d)` (C++17): повертає абсолютне значення тривалості.

```cpp
using namespace std::chrono;
milliseconds ms{1599};

// duration_cast відтинає дробову частину: отримуємо 1 секунду
seconds s1 = duration_cast<seconds>(ms); 

// floor округлює донизу: отримуємо 1 секунду
seconds s2 = floor<seconds>(ms); 

// ceil округлює догори: отримуємо 2 секунди
seconds s3 = ceil<seconds>(ms); 

// round округлює до найближчого: отримуємо 2 секунди
seconds s4 = round<seconds>(ms); 
```

## 2. Шаблон точки часу std::chrono::time_point та інтеграція з потоками

Класовий шаблон `time_point` описує конкретний момент часу відносно епохи певного годинника `Clock`.

```cpp
template <class Clock, class Duration = typename Clock::duration>
class time_point;
```

### Контракти та афінна арифметика точок часу

Точка часу концептуально є елементом афінного простору. Вона не підтримує операцію додавання двох точок часу (`tp1 + tp2` є невалідним виразом і викликає помилку компіляції), але підтримує такі операції:
- Віднімання двох точок часу одного годинника `tp2 - tp1` повертає тип тривалості `Duration`.
- Додавання тривалості до точки часу `tp + d` або `d + tp` повертає нову точку часу `time_point`.
- Віднімання тривалості від точки часу `tp - d` повертає нову точку часу `time_point`.

```cpp
template <class Clock, class Duration>
class time_point {
public:
    using clock = Clock;
    using duration = Duration;
    using rep = typename duration::rep;
    using period = typename duration::period;

    // Конструктори
    constexpr time_point(); // Ініціалізує точку часу значенням duration::zero() (Епоха)
    explicit constexpr time_point(const duration& d); // Точка часу зі зсувом d від епохи
    template <class Duration2>
    constexpr time_point(const time_point<clock, Duration2>& t);

    // Отримання тривалості від початку епохи
    constexpr duration time_since_epoch() const { return d_; }

    // Составні оператори
    constexpr time_point& operator+=(const duration& d) { d_ += d; return *this; }
    constexpr time_point& operator-=(const duration& d) { d_ -= d; return *this; }

    // Статичні межі
    static constexpr time_point min() noexcept { return time_point(duration::min()); }
    static constexpr time_point max() noexcept { return time_point(duration::max()); }
private:
    duration d_;
};
```

Для перетворення `time_point` з однієї роздільностей тривалості в іншу використовується шаблон `std::chrono::time_point_cast<ToDuration>(tp)`. Він виконує `duration_cast` над внутрішнім значенням `time_since_epoch()` і повертає новий об'єкт `time_point`.

### Блокування потоків та синхронізація часу у std::this_thread

Типи `std::chrono` тісно інтегровані з бібліотекою багатопотоковості C++. Засоби затримки потоків надають дві фундаментальні функції у просторі імен `std::this_thread`:

1. `std::this_thread::sleep_for(const duration<Rep, Period>& rel_time)`: блокує виконання поточного потоку щонайменше на відносний часовий інтервал `rel_time`.
2. `std::this_thread::sleep_until(const time_point<Clock, Duration>& abs_time)`: блокує виконання поточного потоку до досягнення абсолютної точки часу `abs_time`.

Використання `sleep_until` із монотонним годинником `steady_clock` гарантує стійкість до ручного переведення системного стінного годинника операційної системи. Якщо потік очікує абсолютну точку часу на `system_clock`, коригування часу в ОС через NTP може призвести до негайного дострокового розблокування або надмірно тривалого занепаду потоку в сон.

### Атомарні операції над часовими типами (C++20)

З стандарту C++20 дозволено повну спеціалізацію `std::atomic` для екземплярів `std::chrono::duration` та `std::chrono::time_point`. Це дозволяє безпечно обмінюватися часовими мітками між потоками виконання без використання блокуючих примітивів синхронізації (м'ютексів):

```cpp
std::atomic<std::chrono::steady_clock::time_point> last_heartbeat;
std::atomic<std::chrono::milliseconds> current_timeout{std::chrono::milliseconds(500)};
```

## 3. Специфікація стандартизованих годинників

Годинник у `std::chrono` — це тип, який об'єднує точку часу з фізичним або системним джерелом відліку. Кожен годинник повинен задовольняти вимогам концепції `TrivialClock` та метапредикату `std::chrono::is_clock_v<T>` (C++20), надаючи наступні статичні члени та типи:

```cpp
struct ClockConcept {
    using rep = ...;
    using period = ...;
    using duration = std::chrono::duration<rep, period>;
    using time_point = std::chrono::time_point<ClockConcept>;
    static constexpr bool is_steady = ...;
    static time_point now() noexcept;
};
```

### Системний астрономічний годинник std::chrono::system_clock

`system_clock` вимірює реальний календарний час (wall-clock time). Його епоха за стандартом C++20 чітко зафіксована як 1970-01-01 00:00:00 UTC (UNIX Epoch).
- Прапорець `is_steady` має значення `false`, оскільки системний годинник може коригуватися операційною системою, синхронізуватися через NTP або змінюватися користувачем уручну.
- Надає інтерфейс конвертації між C-style часом `std::time_t` та C++ точками часу:
  ```cpp
  static std::time_t to_time_t(const time_point& t) noexcept;
  static time_point from_time_t(std::time_t t) noexcept;
  ```

### Монотонний інтервальний годинник std::chrono::steady_clock

`steady_clock` призначений виключно для вимірювання інтервалів часу, розрахунку затримок та таймаутів.
- Прапорець `is_steady` обов'язково дорівнює `true`. Глибинні системні виклики ядра (наприклад, `clock_gettime(CLOCK_MONOTONIC)` на Linux або `QueryPerformanceCounter` на Windows) гарантують, що значення `steady_clock::now()` монотонно зростає і ніколи не повертає від'ємних різниць або стрибків назад.
- Початкова епоха годинника не визначається стандартом і зазвичай відповідає моменту завантаження ядра операційної системи або старт процесора.

### Годинник найвищої роздільної здатності std::chrono::high_resolution_clock

`high_resolution_clock` представляє годинник з мінімально можливим періодом тику `period` на конкретній платформі. За стандартом цей тип є псевдонімом (`type alias`) до `system_clock` або `steady_clock`. У компіляторах GCC та Clang на Linux `high_resolution_clock` визначено як псевдонім до `steady_clock`, тоді як на деяких застарілих реалізаціях MSVC він збігався з `system_clock`. Через це для портабельного вимірювання інтервалів рекомендується явно використовувати `steady_clock`.

### Спеціалізовані годинники та трансляція доменів (clock_cast у C++20)

C++20 розширив набір системних годинників для підтримки супутникових та астрономічних систем:

1. **`utc_clock`:** вимірює час UTC з підтримкою високосних секунд (leap seconds). Надає функції конвертації `to_sys()` та `from_sys()` для взаємодії з `system_clock`.
2. **`tai_clock`:** вимірює Міжнародний атомний час (International Atomic Time). На відміну від UTC, TAI не має високосних секунд і просувається строго рівномірно. Надає статичні методи `to_utc()` та `from_utc()`.
3. **`gps_clock`:** вимірює супутниковий час GPS. Початкова епоха — неділя 6 січня 1980 року. Зсув відсносно TAI становить фіксовані -19 секунд.
4. **`file_clock`:** використовується у стандартній бібліотеці `std::filesystem::file_time_type` для подання часу модифікації файлів на диску. Надає статичні функції `to_sys()` та `from_sys()`.
5. **`local_t`:** псевдо-годинник, що використовується для опису місцевого стінного часу (local time), який ще не прив'язаний до конкретного часового поясу.

Для трансляції точок часу між різними доменними годинниками (наприклад, перетворення точки часу з `system_clock` у `tai_clock` чи `gps_clock`) C++20 надає універсальний шаблон `std::chrono::clock_cast`:

```cpp
template <class DestClock, class SourceClock, class Duration>
auto clock_cast(const std::chrono::time_point<SourceClock, Duration>& t);
```

Ця функція автоматично враховує таблицю високосних секунд та фіксовані часові зсуви при переході між системами координат часу.

## 4. Календарні типи, дати, декомпозиція hh_mm_ss та 12/24-годинні конверсії у C++20

C++20 ввів повноцінний календарний API у простір імен `std::chrono`, що дозволяє будувати та перевіряти дати без використання C-структур `struct tm`.

### Фундаментальні типи
- `std::chrono::day`: обгортка над цілим числом `[1, 31]`, що відповідає дню місяця.
- `std::chrono::month`: обгортка над порядковим номером місяця `[1, 12]`. Стандарт надає визначені константи `std::chrono::January`, `February`, ..., `December`.
- `std::chrono::year`: обгортка над номером року від `-32767` до `32767`.
- `std::chrono::weekday`: день тижня `[0, 6]`, де 0 відповідає неділі (`Sunday`).

### Складені календарні класи
- `year_month_day`: описує конкретну календарну дату (рік, місяць, день). Містить метод `ok()`, який перевіряє, чи є дата дійсною (наприклад, 29 лютого дійсне лише у високосний рік). Надає неявні перетворення у точку часу `std::chrono::sys_days` (`time_point<system_clock, days>`).
- `year_month_day_last`: описує останній день вказаного місяця та року.

### Розбиття часу за допомогою шаблону hh_mm_ss

Для зручної декомпозиції тривалостей на компоненти (години, хвилини, секунди та дробові частки) C++20 ввів тип `std::chrono::hh_mm_ss`:

```cpp
template <class Duration>
class hh_mm_ss {
public:
    constexpr explicit hh_mm_ss(Duration d);

    constexpr bool is_negative() const noexcept;
    constexpr hours hours() const noexcept;
    constexpr minutes minutes() const noexcept;
    constexpr seconds seconds() const noexcept;
    constexpr precision subseconds() const noexcept;
    constexpr explicit operator precision() const noexcept;
    constexpr precision to_duration() const noexcept;
};
```

Цей тип автоматично розраховує компоненти часу незалежно від роздільної здатності вхідної тривалості (мілісекунди, мікросекунди чи наносекунди).

### Допоміжні функції 12/24-годинного формату

Для обробки 12-годинного та 24-годинного представлення часу C++20 надає наступні вільні функції:
- `constexpr bool is_am(const hours& h) noexcept`: повертає `true`, якщо година знаходиться у діапазоні `[0h, 11h]`.
- `constexpr bool is_pm(const hours& h) noexcept`: повертає `true`, якщо година знаходиться у діапазоні `[12h, 23h]`.
- `constexpr hours make12(const hours& h) noexcept`: конвертує годину 24-годинного формату `[0h, 23h]` у 12-годинний формат `[1h, 12h]`.
- `constexpr hours make24(const hours& h, bool is_pm) noexcept`: конвертує 12-годинне значення та прапорець PM назад у 24-годинну годину `[0h, 23h]`.

### Календарні літерали та оператор /

Для зручного конструювання дат перевантажено оператор `/`:

```cpp
using namespace std::chrono;

// Різні варіанти конструювання year_month_day через оператор /
constexpr year_month_day ymd1 = 2026y / August / 14d;
constexpr year_month_day ymd2 = 14d / August / 2026y;
constexpr year_month_day ymd3 = August / 14d / 2026y;

// Перевірка валідності дати
static_assert(ymd1.ok());

// Отримання останнього дня лютого 2024 року (високосний рік)
constexpr year_month_day_last ymld = 2024y / February / last; // 29 лютого 2024
```

## 5. Робота з часовими поясами та zoned_time у C++20

Для обробки часових поясів C++20 інтегрував базу даних IANA Time Zone Database (TZDB).

### Отримання часових поясів

```cpp
namespace std::chrono {
    // Повертає посилання на поточну базу даних TZDB
    const tzdb& get_tzdb();

    // Знаходить часовий пояс за його назвою в базі IANA (наприклад, "Europe/Kyiv")
    const time_zone* locate_zone(std::string_view tz_name);

    // Повертає поточний системний часовий пояс ОС
    const time_zone* current_zone();
}
```

### Структури системної інформації sys_info та local_info

При виконанні конвертацій між часовими поясами `time_zone` повертає метаінформацію у вигляді структури `sys_info`:
- `sys_seconds begin, end`: часові межі дії поточного часового зміщення.
- `seconds offset`: поточний зсув відносно UTC.
- `minutes save`: зсув літнього часу (DST), який зазвичай дорівнює 0m або 60m.
- `std::string abbrev`: скорочена назва поясу (наприклад, "EEST", "EET", "UTC").

### Класовий шаблон zoned_time та обробка винятків transition-періодів

Класовий шаблон `zoned_time` поєднує астрономічний `time_point` з конкретним часовим поясом `time_zone`, забезпечуючи автоматичний розрахунок літнього/зимового часу (DST — Daylight Saving Time).

```cpp
template <class Duration, class TimeZonePtr = const std::chrono::time_zone*>
class zoned_time {
public:
    zoned_time();
    zoned_time(TimeZonePtr z);
    zoned_time(std::string_view name);
    zoned_time(TimeZonePtr z, const sys_time<Duration>& st);
    zoned_time(std::string_view name, const sys_time<Duration>& st);

    // Методи доступу
    sys_time<Duration> get_sys_time() const;
    local_time<Duration> get_local_time() const;
    TimeZonePtr get_time_zone() const;
    sys_info get_info() const;
};
```

При конвертації `local_time` у `sys_time` під час переходу годинників можливі ситуації невизначеності (коли година дублюється або випадає при переході на літній час). Для вирішення цих колізій бібліотека надає прапорці `choose::earliest` та `choose::latest` або генерує винятки:
- `std::chrono::ambiguous_local_time`: генерується, коли місцевий час трапляється двічі внаслідок переведення годинника назад на 1 годину восени.
- `std::chrono::nonexistent_local_time`: генерується, коли місцевий час не існує в даному поясі внаслідок переведення годинника вперед навесні.

## 6. Специфікація форматування та парсингу

З появою C++20 типи `std::chrono` інтегровано у систему форматування `std::format` (а з C++23 — у `std::print`). Спеціалізація `std::formatter` дозволяє форматувати точки часу, дати та тривалості за допомогою керуючих послідовностей.

### Головні керуючі символи форматування

```cpp
auto now = std::chrono::system_clock::now();
// Форматування в ISO 8601 рядок: "2026-08-14 19:45:00"
std::string formatted_time = std::format("{:%Y-%m-%d %H:%M:%S}", now);
```

- `%Y`: рік як чотиризначне ціле число (наприклад, `2026`).
- `%m`: номер місяця з провідним нулем `[01, 12]`.
- `%d`: день місяця з провідним нулем `[01, 31]`.
- `%H`: година у 24-годинному форматі `[00, 23]`.
- `%M`: хвилини з провідним нулем `[00, 59]`.
- `%S`: секунди з дробовою частиною відповідно до роздільної здатності тривалості.
- `%F`: еквівалент `%Y-%m-%d` (стандартна дата ISO 8601).
- `%T`: еквівалент `%H:%M:%S` (стандартний час ISO 8601).
- `%z`: зсув часового поясу відносно UTC у форматі `+0300`.
- `%Z`: абревіатура часового поясу (наприклад, `EEST` або `UTC`).

Парсинг рядків у календарні об'єкти здійснюється за допомогою функції `std::chrono::parse`, яка зчитує вхідний потік або рядок відповідно до специфікатора формату.
