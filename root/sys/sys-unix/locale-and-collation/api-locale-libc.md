# 📋 Системний інтерфейс libc та POSIX locale API

Системні функції C-бібліотеки (`libc`) та стандарту POSIX.1-2008 визначають точний контракт для управління локаллю процесів, роботи з багатобайтовими кодуваннями та порівняння рядків. Фундаментом цього системного API виступають класичний глобальний інтерфейс `setlocale()`, його потокобезпечна альтернатива `uselocale()`, функції зіставлення рядків `strcoll()` та `strxfrm()`, засоби роботи з каталогами повідомлень `catopen()`, а також відповідні ідіоматичні обгортки у мові C++.

## 1. Класичний глобальний інтерфейс: setlocale та localeconv

Класичний POSIX API покладається на глобальний стан локалі в межах усього процесу. Зміна локалі через `setlocale()` впливає на всі потоки виконання процесу одночасно.

### Функція setlocale()

:::tabs
```c
/* POSIX.1-2001 C оголошення у <locale.h> */
#include <locale.h>

char *setlocale(int category, const char *locale);
```
```cpp
// ISO C++11 оголошення у <clocale>
#include <clocale>

char *std::setlocale(int category, const char *locale);
```
:::

#### Параметри:
- `category`: Цілочисельна константа макросу, що визначає підмножину правил:
  - `LC_ALL`: Застосувати локаль до всіх категорій.
  - `LC_CTYPE`: Класифікація та перетворення символів (`isalpha`, `toupper`, багатобайтові межі).
  - `LC_COLLATE`: Порядок зіставлення та порівняння рядків (`strcoll`, `strxfrm`).
  - `LC_MESSAGES`: Мова системних повідомлень (`catopen`, `gettext`, `strerror`).
  - `LC_NUMERIC`: Символ десяткового роздільника та групування триад чисел.
  - `LC_TIME`: Форматування дати й часу (`strftime`).
  - `LC_MONETARY`: Форматування грошових величин.
- `locale`: Вказівник на рядок із назвою локалі:
  - `""` (порожній рядок): Інструктує `libc` зчитати налаштування зі змінних оточення процесу у порядку пріоритету (`LC_ALL` → `LC_<CATEGORY>` → `LANG`).
  - `"C"` або `"POSIX"`: Базова двійкова ASCII-локаль за замовчуванням.
  - `"uk_UA.UTF-8"`, `"en_US.UTF-8"`: Конкретні ідентифікатори локалей системи.
  - `NULL`: Запит поточного значення локалі без її зміни.

#### Повертане значення:
- Вказівник на рядок, що містить поточне або нове значення локалі для вказаної категорії.
- `NULL` у разі помилки (якщо запитана локаль не встановлена в системі або непідтримувана).

#### Критична зауваження щодо потікобезпеки:
Функція `setlocale()` **не є потікобезпечною** (not thread-safe). Виклик `setlocale()` в одному потоці під час роботи інших потоків, які використовують `strcoll`, `printf` чи `regexec`, призводить до стану ґонки (data race) та невизначеної поведінки (undefined behavior).

---

### Функція localeconv()

:::tabs
```c
/* Повертає структуру з числовими та грошовими параметрами */
#include <locale.h>

struct lconv *localeconv(void);
```
```cpp
#include <clocale>

std::lconv *std::localeconv();
```
:::

Повертає вказівник на статичну структуру `struct lconv`, яка містить параметри форматування чисел та грошей:
- `decimal_point`: Символ десяткового роздільника (наприклад, `"."` для `"C"` або `","` для `"uk_UA.UTF-8"`).
- `thousands_sep`: Символ-розділювач тисяч.
- `grouping`: Масив із розмірами груп цифр.
- `currency_symbol`: Символ валюти (наприклад, `"грн"` або `"$"`).

---

### Функція nl_langinfo()

:::tabs
```c
#include <langinfo.h>

char *nl_langinfo(nl_item item);
```
```cpp
#include <langinfo.h>

extern "C" char *nl_langinfo(nl_item item);
```
:::

Дозволяє витягти специфічні низькорівневі елементи з поточного контексту локалі. Константи `nl_item` оголошені в `<langinfo.h>`:
- `CODESET`: Назва поточного кодування символів (наприклад, `"UTF-8"`, `"ISO-8859-1"`, `"ASCII"`).
- `RADIXCHAR`: Символ десяткової крапки.
- `D_T_FMT`: Рядок формату дати й часу.
- `YESEXPR` / `NOEXPR`: Регулярні вирази для стверджувальної чи заперечної відповіді в терміналі.

:::tabs
```c
/* C приклад отримання кодування через nl_langinfo */
#include <stdio.h>
#include <locale.h>
#include <langinfo.h>

void print_current_codeset(void) {
    setlocale(LC_ALL, "");
    const char *cs = nl_langinfo(CODESET);
    printf("Активне кодування термінала: %s\n", cs);
}
```
```cpp
// C++17 приклад витягування кодування через std::locale
#include <iostream>
#include <locale>
#include <clocale>
#include <langinfo.h>

void print_current_codeset_cpp() {
    std::setlocale(LC_ALL, "");
    const char *cs = nl_langinfo(CODESET);
    std::cout << "Активне кодування термінала (C++): " << cs << "\n";
}
```
:::

---

## 2. Потікобезпечний POSIX.1-2008 API: locale_t та uselocale

Для розв'язання проблеми потікобезпеки у багатотокових серверах (наприклад, веб-серверах або СУБД, які мають обробляти запити від користувачів із різними локалями одночасно) стандарт POSIX.1-2008 ввів тип `locale_t` та функціонал **локалі потоку** (thread-local locale).

### Функції newlocale, duplocale, freelocale

:::tabs
```c
/* POSIX.1-2008 інтерфейс створення та знищення об'єктів locale_t */
#include <locale.h>

locale_t newlocale(int category_mask, const char *locale, locale_t base);
locale_t duplocale(locale_t locobj);
void freelocale(locale_t locobj);
```
```cpp
#include <clocale>

extern "C" {
locale_t newlocale(int category_mask, const char *locale, locale_t base);
locale_t duplocale(locale_t locobj);
void freelocale(locale_t locobj);
}
```
:::

#### Опис сигнатур:
- `newlocale()`: Створює новий об'єкт `locale_t`. `category_mask` — бітова маска категорій (`LC_COLLATE_MASK`, `LC_CTYPE_MASK`, `LC_ALL_MASK`). Якщо `base` не дорівнює `NULL`, модифікується існуючий об'єкт.
- `duplocale()`: Створює глибоку копію існуючого об'єкта `locale_t`.
- `freelocale()`: Звільняє ресурси, виділені під об'єкт `locale_t`.

---

### Функція uselocale()

:::tabs
```c
#include <locale.h>

locale_t uselocale(locale_t newloc);
```
```cpp
#include <clocale>

extern "C" locale_t uselocale(locale_t newloc);
```
:::

Установлює об'єкт `newloc` як **локаль поточного потоку виконання** (thread-local).
- Якщо `newloc == LC_GLOBAL_LOCALE`, потік повертається до використання глобальної локалі процесу.
- Якщо `newloc == (locale_t)0` (`NULL`), функція повертає поточний об'єкт `locale_t` потоку без його зміни.
- Повертає попередній об'єкт `locale_t`, який був активним у даному потоці.

---

## 3. Механіка зіставлення рядків: strcoll, strxfrm та _l варіанти

Стандарт POSIX надає дві фундаментальні функції для порівняння рядків з урахуванням правил `LC_COLLATE`: `strcoll()` та `strxfrm()`.

### Функція strcoll()

:::tabs
```c
#include <string.h>

int strcoll(const char *s1, const char *s2);
int strcoll_l(const char *s1, const char *s2, locale_t loc);
```
```cpp
#include <cstring>
#include <clocale>

int std::strcoll(const char *s1, const char *s2);

extern "C" {
int strcoll_l(const char *s1, const char *s2, locale_t loc);
}
```
:::

#### Семантика:
Порівнює два рядки `s1` та `s2` з урахуванням правил сортування поточної локалі `LC_COLLATE` (або об'єкта `loc` у `strcoll_l`).

#### Повертане значення:
- Від'ємне число (`< 0`), якщо `s1` передує `s2` за правилами сортування.
- Нуль (`0`), якщо рядки еквівалентні за правилами сортування.
- Додатне число (`> 0`), якщо `s1` слідує після `s2`.

#### Внутрішня складність:
Для кожного виклику `strcoll()` C-бібліотека має динамічно обчислити вагові коефіцієнти обох рядків. Для сортування масиву з `N` рядків виконується `O(N log N)` порівнянь. Якщо кожне порівняння викликає `strcoll()`, загальна складність аналізу вагових таблиць складає `O(N log N)`.

---

### Функція strxfrm()

:::tabs
```c
#include <string.h>

size_t strxfrm(char *dest, const char *src, size_t n);
size_t strxfrm_l(char *dest, const char *src, size_t n, locale_t loc);
```
```cpp
#include <cstring>
#include <clocale>

std::size_t std::strxfrm(char *dest, const char *src, std::size_t n);

extern "C" {
size_t strxfrm_l(char *dest, const char *src, size_t n, locale_t loc);
}
```
:::

#### Семантика:
Перетворює рядок `src` у ключовий байтовий вектор (collation key) і зберігає його у буфері `dest` довжиною `n` байтів.

Сформований ключ володіє фундаментальною властивістю: якщо викликати класичну байтову функцію `strcmp()` на двох трансформованих ключах `dest1` та `dest2`, її результат **ідеально збігається** з результатом виклику `strcoll(s1, s2)`!

```
strcmp(strxfrm(s1), strxfrm(s2)) == strcoll(s1, s2)
```

#### Повертане значення:
- Кількість байтів, необхідна для збереження трансформованого ключа (без урахування завершального `\0`). Якщо повертане значення `≥ n`, буфер `dest` виявився замалим, і ключ був обрізаний.

#### Стратегія використання у сортуванні:
Замість `O(N log N)` дорогих викликів `strcoll()`, програма виконує `O(N)` трансформацій `strxfrm()` на початку, зберігає трансформовані ключі, після чого сортує масив за допомогою надшвидкого `strcmp()` чи `qsort()`. Це дає прискорення у 3–8 разів на великих масивах текстів.

---

## 4. Широкосимвольні розширення (Wide-character API): wcscoll та wcsxfrm

Для систем, що працюють безпосередньо з типом `wchar_t` (широкими символами 32-біт у Linux/glibc), POSIX надає відповідні аналоги для зіставлення:

:::tabs
```c
#include <wchar.h>

int wcscoll(const wchar_t *ws1, const wchar_t *ws2);
size_t wcsxfrm(wchar_t *dest, const wchar_t *src, size_t n);

int wcscoll_l(const wchar_t *ws1, const wchar_t *ws2, locale_t loc);
size_t wcsxfrm_l(wchar_t *dest, const wchar_t *src, size_t n, locale_t loc);
```
```cpp
#include <cwchar>
#include <clocale>

int std::wcscoll(const wchar_t *ws1, const wchar_t *ws2);
std::size_t std::wcsxfrm(wchar_t *dest, const wchar_t *src, std::size_t n);

extern "C" {
int wcscoll_l(const wchar_t *ws1, const wchar_t *ws2, locale_t loc);
size_t wcsxfrm_l(wchar_t *dest, const wchar_t *src, size_t n, locale_t loc);
}
```
:::

---

## 5. Каталоги мовних повідомлень POSIX: catopen, catgets, catclose

Для локалізації повідомлень про помилки та інтерфейсу без використання бібліотеки GNU `gettext`, POSIX визначає стандартний інтерфейс каталогів повідомлень (Message Catalog API):

:::tabs
```c
#include <nl_types.h>

nl_catd catopen(const char *name, int flag);
char *catgets(nl_catd catd, int set_id, int msg_id, const char *s);
int catclose(nl_catd catd);
```
```cpp
#include <nl_types.h>

extern "C" {
nl_catd catopen(const char *name, int flag);
char *catgets(nl_catd catd, int set_id, int msg_id, const char *s);
int catclose(nl_catd catd);
}
```
:::

- `catopen()`: Відкриває каталог бінарних повідомлень `name`. Якщо `flag == NL_CAT_LOCALE`, система використовує категорію `LC_MESSAGES` для пошуку каталогу у файловій системі (`/usr/share/locale/...`).
- `catgets()`: Витягує рядок повідомлення за набором `set_id` та ідентифікатором `msg_id`. Якщо повідомлення не знайдено, повертає фолбек-рядок `s`.
- `catclose()`: Закриває дескриптор каталогу.

---

## 6. Ідіоматичні C та C++ приклади використання

Нижче наведено порівняльний приклад розробки безпечного модуля сортування рядків у C та C++ з використанням потікобезпечного POSIX API та стандартних контейнерів C++.

:::tabs
```c
/* C11 + POSIX.1-2008: Потікобезпечне сортування через strxfrm_l */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <locale.h>

typedef struct {
    char *original;
    char *key;
} StringEntry;

int compare_entries(const void *a, const void *b) {
    const StringEntry *e1 = (const StringEntry *)a;
    const StringEntry *e2 = (const StringEntry *)b;
    return strcmp(e1->key, e2->key);
}

void sort_strings_posix(char **array, size_t count, const char *locale_name) {
    locale_t loc = newlocale(LC_ALL_MASK, locale_name, NULL);
    if (!loc) {
        perror("newlocale failed");
        return;
    }

    StringEntry *entries = malloc(count * sizeof(StringEntry));
    if (!entries) {
        freelocale(loc);
        return;
    }

    for (size_t i = 0; i < count; ++i) {
        entries[i].original = array[i];
        
        // Визначення необхідного розміру ключа
        size_t len = strxfrm_l(NULL, array[i], 0, loc) + 1;
        entries[i].key = malloc(len);
        if (entries[i].key) {
            strxfrm_l(entries[i].key, array[i], len, loc);
        }
    }

    qsort(entries, count, sizeof(StringEntry), compare_entries);

    for (size_t i = 0; i < count; ++i) {
        array[i] = entries[i].original;
        free(entries[i].key);
    }

    free(entries);
    freelocale(loc);
}
```
```cpp
// C++17: Ідіоматичний підхід через std::locale, std::collate та RAII
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <locale>
#include <stdexcept>

class ThreadSafeCollator {
private:
    std::locale loc_;

public:
    explicit ThreadSafeCollator(const std::string& locale_name) 
        : loc_(locale_name) {}

    void sort_strings(std::vector<std::string>& strings) const {
        // Отримання фасету зіставлення std::collate з об'єкта локалі
        const auto& coll = std::use_facet<std::collate<char>>(loc_);

        // Кешування трансформаційних ключів через std::collate::transform
        struct KeyEntry {
            std::string original;
            std::string key;
        };

        std::vector<KeyEntry> entries;
        entries.reserve(strings.size());

        for (const auto& str : strings) {
            std::string key = coll.transform(str.data(), str.data() + str.size());
            entries.push_back({str, std::move(key)});
        }

        // Швидке порівняння преображених ключів
        std::sort(entries.begin(), entries.end(), 
            [](const KeyEntry& a, const KeyEntry& b) {
                return a.key < b.key;
            });

        for (size_t i = 0; i < strings.size(); ++i) {
            strings[i] = std::move(entries[i].original);
        }
    }
};
```
:::

### Пояснення відмінностей C та C++ ідіом:
1. **Керування ресурсами**: У коді C використовується ручне створення та видалення об'єкта `locale_t` через `newlocale()` / `freelocale()`, а також явне виділення пам'яті під ключі `malloc()` / `free()`. У C++ об'єкт `std::locale` є потікобезпечним об'єктом із підрахунком посилань, а RAII-контейнери `std::string` та `std::vector` автоматично очищають ресурси при виході зі області видимості.
2. **Фасети C++ (`std::use_facet`)**: У C++ сортування виконується через фасет `std::collate<char>`, який витягується з об'єкта `std::locale`. Метод `coll.transform()` надає аналог `strxfrm()`, а `coll.compare()` — аналог `strcoll()`.
3. **Потікобезпека**: Обидва варіанти є повністю потікобезпечними (thread-safe), адже вони не змінюють глобальний стан процесу через `setlocale()`, а оперують локальними екземплярами локалі.
