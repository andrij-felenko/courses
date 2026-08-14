# 📋 Інструменти та синтаксис версіонування символів

Цей довідник надає вичерпний опис інтерфейсів, синтаксису скриптів компонувальника GNU `ld`, директив препроцесора та компілятора GCC/Clang, утиліт низькорівневого аналізу бінарних файлів ELF та C/C++ API для управління версіонуванням спільних бібліотек.

Управління бінарним інтерфейсом (ABI) у світі Linux здійснюється на кількох рівнях: під час збирання бібліотеки розробник описує граф версій у спеціальному скрипті компонувальника та маркує вихідний код, під час інспектування адміністратор перевіряє структуру секцій ELF за допомогою CLI-утиліт, а під час виконання розробник додатків може використовувати системний API завантажувача `ld.so` для точкового виклику потрібних версій функцій.

## 1. Синтаксис скрипту версіонування компонувальника (Version Script)

Скрипт версіонування (зазвичай називається `libfoo.map` або `versions.map`) передається компонувальнику `ld` під час створення спільної бібліотеки через прапорці компілятора `gcc -Wl,--version-script=libfoo.map`.

Цей файл виконує дві критичні функції: він будує граф версійних вузлів у секції `.gnu.version_d` і жорстко контролює видимість символів, приховуючи внутрішні функції бібліотеки від зовнішніх додатків.

### Структура та блоки файлу версій

Файл версій складається з послідовності версійних вузлів (Version Nodes). Кожен вузол має унікальне текстове ім'я, яке за конвенцією пишеться великими літерами з вказуванням мажорного та мінорного номера (наприклад, `LIBFOO_1.0`, `GLIBC_2.34`).

```text
LIBFOO_1.0 {
    global:
        foo_init;
        foo_process;
        foo_cleanup;
    local:
        *;  /* Приховує всі інші символи, не вказані у блоці global */
};

LIBFOO_1.1 {
    global:
        foo_configure;
} LIBFOO_1.0; /* Успадкування від версії 1.0 */

LIBFOO_2.0 {
    global:
        foo_process;       /* Оновлена сигнатура відомої функції */
        foo_async_submit;  /* Нова функція для версії 2.0 */
} LIBFOO_1.1; /* Успадкування від версії 1.1 */
```

### Деталізація ключових слів та директив синтаксису:

- **`global:`** 
  Скціонує список назв функцій та глобальних змінних, які мусять бути експортовані у динамічну таблицю символів `.dynsym` і бути доступними для зв'язування з іншими бінарними файлами. Усередині блоку `global:` дозволено використовувати шаблони пошуку (wildcards), такі як `foo_*` або `extern "C++" { ... }`.
- **`local:`** 
  Визначає список символів, які мусять бути приховані у підсумковій бібліотеці. Символи, що потрапляють у блок `local:`, вилучаються з таблиці `.dynsym` і розміщуються виключно у локальній таблиці `.symtab`, унеможливлюючи виклик цих процедур із зовнішніх додатків.
- **Спеціальний шаблон `local: *;`:** 
  Призначений для приховування абсолютно всіх символів бібліотеки, які не були явно вказані у блоках `global:`. Використання `local: *;` є найкращою практикою конструювання бінарних бібліотек, оскільки воно фундаментально запобігає «забрудненню» глобального простору імен (Symbol Pollution) внутрішніми службовими функціями і суттєво прискорює завантаження додатка.
- **Ієрархічне успадкування вузлів (`} LIBFOO_1.0;`):**
  Назва батьківського вузла, вказана після закриваючої фігурної дужки, будує спрямований ациклічний граф залежностей версій. Динамічний завантажувач `ld.so` використовує цей граф для перевірки того, що бібліотека підтримує всю лінійку еволюції ABI.

### Прапорці компонувальника `ld` для роботи зі скриптами

Під час збирання бібліотеки разом із `--version-script` використовують додаткові прапорці `ld`:
- `-Wl,--version-script=libfoo.map` — вказує шлях до файлу скрипту.
- `-Wl,--no-undefined-version` — вимагає від компонувальника видати помилку збірки, якщо у скрипті вказано символ, якого немає в об'єктних файлах.
- `-Wl,--default-symver` — примусово створює версіонований символ для кожного експортованого символу, навіть якщо не використовується директива `.symver`.

## 2. Директиви вихідного коду (.symver та атрибути)

Для прив'язки конкретних вихідних C/C++ функцій до відповідних версійних вузлів використовуються низькорівневі інструкції компілятора.

### Класичний синтаксис інструкції `.symver`

Синтаксис інструкції має вигляд `.symver C_symbol_name, ELF_symbol_name@VERSION_NODE`.

Розглянемо прив'язку двох версій у мовах C та C++:

:::tabs
```c
// foo_ver.c — Застосування .symver у C
int foo_process_v1(int arg) {
    return arg * 2;
}
__asm__(".symver foo_process_v1, foo_process@LIBFOO_1.0");

int foo_process_v2(int arg, int flags) {
    return arg * flags;
}
__asm__(".symver foo_process_v2, foo_process@@LIBFOO_2.0");
```
```cpp
// foo_ver.cpp — Застосування .symver у C++ з обгорткою extern "C"
extern "C" {

int foo_process_v1(int arg) {
    return arg * 2;
}
__asm__(".symver foo_process_v1, foo_process@LIBFOO_1.0");

int foo_process_v2(int arg, int flags) {
    return arg * flags;
}
__asm__(".symver foo_process_v2, foo_process@@LIBFOO_2.0");

}
```
:::

- **Один собачка `@`:** застаріла/прихована версія символу `foo_process@LIBFOO_1.0`. Використовується лише вже скомпільованими бінарними файлами.
- **Два собачки `@@`:** дефолтна версія `foo_process@@LIBFOO_2.0`. Усі нові програми під час компіляції з прапорцем `-lfoo` будуть автоматично зв'язуватися з цією реалізацією `foo_process_v2`.

### Сучасний атрибут GCC 10+ та Clang 13+

Для того щоб уникнути прямих асемблерних вставок, які можуть викликати проблеми при декоруванні імен у C++ (C++ Name Mangling), сучасні компілятори ввели спеціальний атрибут `symver`:

:::tabs
```c
// foo_attr.c — Застосування атрибута symver у C
__attribute__((symver("foo_process@LIBFOO_1.0")))
int foo_process_v1(int arg) {
    return arg * 2;
}

__attribute__((symver("foo_process@@LIBFOO_2.0")))
int foo_process_v2(int arg, int flags) {
    return arg * flags;
}
```
```cpp
// foo_attr.cpp — Застосування атрибута symver у C++
extern "C" {

__attribute__((symver("foo_process@LIBFOO_1.0")))
int foo_process_v1(int arg) {
    return arg * 2;
}

__attribute__((symver("foo_process@@LIBFOO_2.0")))
int foo_process_v2(int arg, int flags) {
    return arg * flags;
}

}
```
:::

У мові C++ при використанні версіонування символів для функцій з перевантаженням чи у просторах імен (`namespaces`) обов'язково використовується блок `extern "C"`, щоб уникнути викривлення імені компонувальником, або використовується опис C++ декорованого імені у скрипті версій через блочну інструкцію `extern "C++"`.

## 3. Команди аналізу та інспектування бінарних файлів

Для низькорівневого аналізу секцій версіонування ELF-файлів використовується стандартний набір інструментів GNU binutils (`readelf`, `objdump`, `nm`).

### Використання утиліти `readelf`

Утиліта `readelf` є найбільш точним інструментом, оскільки вона напряму інтерпретує структури даних заголовків ELF без використання системних бібліотек.

1. **Перевірка тегів `.dynamic` (`readelf -d`):**
   ```bash
   $ readelf -d libfoo.so.1.2.0 | grep -E "SONAME|NEEDED"
    0x000000000000000e (SONAME)             Library soname: [libfoo.so.1]
    0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
   ```
   Команда виводить список усіх залежностей `DT_NEEDED` та власне значення `DT_SONAME` бібліотеки.

2. **Перевірка дампа версійних секцій (`readelf -V` або `readelf --version-info`):**
   ```bash
   $ readelf -V libfoo.so.1.2.0
   ```
   Виводить детальну розшифровку трьох версійних секцій:
   - **Version Definition section (`.gnu.version_d`):** показує список усіх версійних вузлів, згенерованих у даній бібліотеці, із зазначенням прапорців, індексів хешів та батьківських вузлів.
   - **Version Needs section (`.gnu.version_r`):** показує список зовнішніх версій, необхідних бінарному файлу від інших спільних бібліотек (наприклад, `GLIBC_2.2.5` від `libc.so.6`).
   - **Version Symbol section (`.gnu.version`):** виводить таблицю індексів версій для кожного динамічного символу.

### Використання утиліти `objdump`

Утиліта `objdump` дозволяє переглядати таблицю динамічних символів у більш зручному табличному форматі.

```bash
$ objdump -T libfoo.so.1.2.0
```

Приклад виводу утиліти `objdump -T`:
```text
DYNAMIC SYMBOL TABLE:
0000000000001140 g    DF .text  0000000000000018  LIBFOO_1.0  foo_process
0000000000001160 g    DF .text  0000000000000024 (LIBFOO_2.0) foo_process
```

Розшифровка полів виводу:
- `0000000000001140` — віртуальна адреса початку функції у сегменті коду.
- `g` — глобальний символ (`global`).
- `DF` — динамічна функція (`Dynamic Function`).
- `.text` — секція ELF, у якій розміщено машинний код.
- `LIBFOO_1.0` — версія символу. Відсутність дужок означає, що це прихована/застаріла версія (`@`).
- `(LIBFOO_2.0)` — наявність круглих дужок навколо імені версії означає, що це версія за замовчуванням (`@@`).

### Використання утиліти `nm`

Утиліта `nm` відображає символи бінарного файла. Прапорець `-D` вказує зчитувати саме динамічну таблицю `.dynsym`:

```bash
$ nm -D libfoo.so.1.2.0 | grep foo_process
0000000000001140 T foo_process@LIBFOO_1.0
0000000000001160 T foo_process@@LIBFOO_2.0
```
Символ `T` вказує, що функція знаходиться у секції виконання коду (`Text section`).

## 4. C та C++ API для явного версіонованого завантаження (dlvsym)

Стандартний механізм динамічного зв'язування завантажує бібліотеки під час запуску процесу. Проте у складних системах (наприклад, у плагінних архітектурах серверів чи графічних редакторів) виклики бібліотек виконуються динамічно під час виконання за допомогою функції `dlopen()`.

За умовчанням функція `dlsym(handle, "symbol_name")` повертає адреси символів, маркованих як версія за замовчуванням (`@@`). Якщо розробнику необхідно явно отримати доступ до конкретної історичної версії символу (наприклад, `foo_process@LIBFOO_1.0`), стандартний `dlsym()` не допоможе. Для цього використовується спеціальне розширення GNU C Library — функція `dlvsym()`.

### Сигнатура та оголошення `dlvsym` у C та C++

:::tabs
```c
// Оголошення dlvsym у C (вимагає #define _GNU_SOURCE)
#define _GNU_SOURCE
#include <dlfcn.h>

// void *dlvsym(void *handle, const char *symbol, const char *version);
```
```cpp
// Оголошення dlvsym у C++ (з підключенням cstddef)
#define _GNU_SOURCE
#include <dlfcn.h>
#include <cstddef>

// Сигнатура функціонального покажчика dlvsym залишається сумісною з C API:
// extern "C" void *dlvsym(void *handle, const char *symbol, const char *version);
```
:::

Параметри:
- `handle` — покажчик на відкритий дескриптор бібліотеки, отриманий від `dlopen()`.
- `symbol` — текстове ім'я шуканої функції або змінної (наприклад, `"foo_process"`).
- `version` — точна текстова назва версійного вузла (наприклад, `"LIBFOO_1.0"`).

### Повний приклад використання у C та C++

У наведених прикладах показано безпечне динамічне завантаження бібліотеки, явне отримання покажчиків на дві різні версії однієї функції та обробку помилок.

:::tabs
```c
// main.c — Явне завантаження версіонованих символів у C
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

// Оголошення типів покажчиків на функції для двох версій ABI
typedef int (*foo_v1_fn)(int);
typedef int (*foo_v2_fn)(int, int);

void run_dynamic_test(void) {
    // 1. Відкриваємо спільну бібліотеку за допомогою dlopen
    void* handle = dlopen("libfoo.so.1", RTLD_LAZY);
    if (!handle) {
        fprintf(stderr, "Помилка завантаження бібліотеки: %s\n", dlerror());
        return;
    }

    // Очищаємо попередні помилки dlfcn
    dlerror();

    // 2. Отримуємо покажчик на старий ABI v1.0 через dlvsym
    foo_v1_fn func_v1 = (foo_v1_fn)dlvsym(handle, "foo_process", "LIBFOO_1.0");
    char* error = dlerror();
    if (error != NULL) {
        fprintf(stderr, "Помилка отримання символу v1.0: %s\n", error);
    } else {
        int res1 = func_v1(42);
        printf("[C Client] Виклик foo_process@LIBFOO_1.0(42) повернув: %d\n", res1);
    }

    // 3. Отримуємо покажчик на новий ABI v2.0 через dlvsym
    foo_v2_fn func_v2 = (foo_v2_fn)dlvsym(handle, "foo_process", "LIBFOO_2.0");
    error = dlerror();
    if (error != NULL) {
        fprintf(stderr, "Помилка отримання символу v2.0: %s\n", error);
    } else {
        int res2 = func_v2(42, 100);
        printf("[C Client] Виклик foo_process@@LIBFOO_2.0(42, 100) повернув: %d\n", res2);
    }

    // 4. Закриваємо дескриптор бібліотеки
    dlclose(handle);
}
```
```cpp
// main.cpp — Ідіоматична обгортка RAII для dlvsym у C++
#define _GNU_SOURCE
#include <iostream>
#include <memory>
#include <string_view>
#include <stdexcept>
#include <dlfcn.h>

// RAII обгортка для безпечного керування ресурсами dlopen/dlclose
class SharedLibrary {
    void* handle_{nullptr};
public:
    explicit SharedLibrary(std::string_view filepath) {
        handle_ = dlopen(filepath.data(), RTLD_LAZY);
        if (!handle_) {
            throw std::runtime_error(std::string("Не вдалося відкрити бібліотеку: ") + dlerror());
        }
    }

    ~SharedLibrary() {
        if (handle_) {
            dlclose(handle_);
        }
    }

    // Забороняємо копіювання для запобігання подвійному закриттю дескриптора
    SharedLibrary(const SharedLibrary&) = delete;
    SharedLibrary& operator=(const SharedLibrary&) = delete;

    // Шаблонний метод для безпечного отримання версіонованого покажчика
    template<typename FuncSignature>
    FuncSignature get_versioned_symbol(std::string_view symbol, std::string_view version) const {
        dlerror(); // Скидаємо попередній стан помилки
        void* ptr = dlvsym(handle_, symbol.data(), version.data());
        const char* err = dlerror();
        if (err) {
            throw std::runtime_error(std::string("Символ ") + symbol.data() + 
                                     "@" + version.data() + " не знайдено: " + err);
        }
        return reinterpret_cast<FuncSignature>(ptr);
    }
};

void run_dynamic_test() {
    try {
        SharedLibrary lib("libfoo.so.1");

        using func_v1_t = int(*)(int);
        using func_v2_t = int(*)(int, int);

        auto func_v1 = lib.get_versioned_symbol<func_v1_t>("foo_process", "LIBFOO_1.0");
        std::cout << "[C++ Client] Виклик foo_process@LIBFOO_1.0(42) повернув: " 
                  << func_v1(42) << "\n";

        auto func_v2 = lib.get_versioned_symbol<func_v2_t>("foo_process", "LIBFOO_2.0");
        std::cout << "[C++ Client] Виклик foo_process@@LIBFOO_2.0(42, 100) повернув: " 
                  << func_v2(42, 100) << "\n";

    } catch (const std::exception& ex) {
        std::cerr << "[C++ Error] " << ex.what() << "\n";
    }
}
```
:::

Використання `dlvsym()` гарантує точне управління завантаженням реалізацій у складних мультиверсійних середовищах, захищаючи додатки від непередбачуваної поведінки завантажувача.
