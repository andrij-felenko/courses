# 📋 Системні інтерфейси POSIX: wordexp(3), glob(3) та fnmatch(3)

Ця вставка містить вичерпний системний довідник з програмного інтерфейсу POSIX C та C++ для виконання розгортання слів (`wordexp`), глобінгу імен файлів (`glob`) та зіставлення масок (`fnmatch`) у системному програмуванні без безпосереднього виклику командної оболонки.

## 1. Розгортання слів: wordexp(3) та wordfree(3)

Бібліотечна функція `wordexp(3)` реалізує повний конвеєр розгортання POSIX-оболонки над довільним текстовим рядком. Це включає розгортання тильди, параметрів, підстановку команд, арифметичні вирази, поділ на слова, глобінг та видалення лапок.

Заголовочний файл POSIX: `<wordexp.h>`

### Опис структури wordexp_t

Структура `wordexp_t` використовується для повернення результатів розгортання та збереження внутрішнього стану виділеної пам'яті.

:::tabs
```c
#include <wordexp.h>

/* Опис структури wordexp_t у POSIX C */
typedef struct {
    size_t we_wordc;  /* Кількість розгорнутих слів у масиві */
    char **we_wordv;  /* Масив покажчиків на рядки, завершений NULL */
    size_t we_offs;   /* Кількість зарезервованих елементів на початку */
} wordexp_t;
```
```cpp
#include <wordexp.h>

// У C++ використовуються ті ж поля POSIX C-структури wordexp_t,
// але звернення до них зазвичай загортається у RAII-обгортки.
// we_wordc — кількість слів (std::size_t)
// we_wordv — масив покажчиків на рядки (char**)
// we_offs  — зарезервовані початкові слоти
```
:::

Поля структури детально:

- `size_t we_wordc` — кількість розгорнутих слів, розміщених у масиві `we_wordv`. Якщо під час розгортання не було згенеровано жодного слова, поле дорівнює 0.
- `char **we_wordv` — масив покажчиків на null-terminated рядки. Елементи з `we_wordv[0]` по `we_wordv[we_wordc - 1]` містять розгорнуті слова. Елемент `we_wordv[we_wordc]` завжди містить покажчик `NULL`, що робить цей масив повністю сумісним зі структурою `argv[]` для системного виклику `execve(2)`.
- `size_t we_offs` — кількість зарезервованих порожніх слотів у початку масиву `we_wordv`. Поле використовується лише тоді, коли у функцію передано прапор `WRDE_DOOFFS`. Перші `we_offs` елементів масиву заповнюються покажчиками `NULL`, а розгорнуті слова розміщуються починаючи з індексу `we_offs`. Це дозволяє розробникам формувати вектор `argv`, залишаючи перші елементи для імені виконуваної програми та прапорів.

### Сигнатура та прапори функцій

Розгортання здійснюється викликом `wordexp`, а звільнення пам'яті — викликом `wordfree`.

:::tabs
```c
int wordexp(const char *restrict s, wordexp_t *restrict p, int flags);
void wordfree(wordexp_t *p);
```
```cpp
int wordexp(const char *s, wordexp_t *p, int flags);
void wordfree(wordexp_t *p);
```
:::

Параметр `flags` формується бітовим АБО (`|`) з наступних системних констант:

- `WRDE_DOOFFS` — враховувати значення поля `p->we_offs`. На початку масиву `we_wordv` буде виділено `we_offs` покажчиків `NULL`.
- `WRDE_NOCMD` — **критичний прапор безпеки**. Повністю забороняє виконання підстановки команд (`$(command)` та `` `command` ``). Якщо переданий рядок містить спробу виконання команди, `wordexp` негайно перериває роботу і повертає код помилки `WRDE_CMDSUB`. Цей прапор є обов'язковим при обробці будь-якого тексту, отриманого з неконтрольованих джерел.
- `WRDE_REUSE` — вказує бібліотеці, що структура `p` є результатом попереднього успішного виклику `wordexp`. Функція повторно використає раніше виділену буферну пам'ять замість виклику `malloc`, що підвищує продуктивність при циклічній обробці рядків. При цьому перед повторним викликом `wordexp` з прапором `WRDE_REUSE` не потрібно викликати `wordfree`.
- `WRDE_SHOWERR` — дозволяє вивід синтаксичних повідомлень про помилки у стандартний потік помилок `stderr`. За замовчуванням `wordexp` пригнічує повідомлення про помилки під час аналізу рядка.
- `WRDE_UNDEF` — вимагає перевірки наявності всіх змінних оточення. Якщо рядок звертається до змінної, яка не існує у `environ`, функція перериває розгортання та повертає помилку `WRDE_BADVAL`.
- `WRDE_APPEND` — додає розгорнуті слова в кінець існуючого списку в структурі `p`. Попередня кількість слів у `p->we_wordc` зберігається, а нові слова дописуються після них.

### Коди повернення та обробка помилок

Функція `wordexp` повертає `0` при успішному завершенні. У разі виникнення помилки повертається одне з наступних цілочисельних значень:

- `WRDE_BADVAL` — спроба звернення до невизначеної змінної оточення при встановленому прапорі `WRDE_UNDEF`.
- `WRDE_BADCHAR` — у рядку виявлено неприпустимий спеціальний символ (наприклад, некерований символ переведення рядка або вертикальну риску outside quotes).
- `WRDE_CMDSUB` — виявлено підстановку команд при встановленому прапорі `WRDE_NOCMD`.
- `WRDE_NOSPACE` — не вдалося виділити оперативну пам'ять через `malloc(3)`. Масив `we_wordv` може бути частково сформований.
- `WRDE_SYNTAX` — синтаксична помилка у командному рядку (наприклад, незбалансовані подвійні лапки, некеровані фігурні дужки або дужки арифметичного виразу).

Звільнення пам'яті:
Після завершення роботи з результатами розгортання необхідно обов'язково викликати `wordfree(p)`. Ця функція звільняє пам'ять, виділену для кожного окремого слова у `we_wordv`, та сам масив покажчиків. Спроба звільнити структуру `wordexp_t` через звичайний `free()` призведе до витоку пам'яті (memory leak).

### Приклади використання wordexp у C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <wordexp.h>

int safe_tokenize(const char *input_str) {
    wordexp_t p;
    /* Резервуємо 1 слот на початку для імені бінарника в argv */
    p.we_offs = 1;
    int flags = WRDE_NOCMD | WRDE_UNDEF | WRDE_DOOFFS;

    int status = wordexp(input_str, &p, flags);
    if (status != 0) {
        switch (status) {
            case WRDE_CMDSUB:
                fprintf(stderr, "Помилка безпеки: підстановка команд заборонена!\n");
                break;
            case WRDE_BADVAL:
                fprintf(stderr, "Помилка: звернення до невідомої змінної оточення.\n");
                break;
            case WRDE_SYNTAX:
                fprintf(stderr, "Синтаксична помилка у рядку вводу.\n");
                break;
            default:
                fprintf(stderr, "Помилка розгортання: код %d\n", status);
                break;
        }
        return -1;
    }

    /* Заповнюємо зарезервований argv[0] */
    p.we_wordv[0] = "/usr/bin/custom_tool";

    printf("Успішно сформовано argv (всього елементів: %zu):\n", p.we_wordc + p.we_offs);
    for (size_t i = 0; i < p.we_wordc + p.we_offs; i++) {
        printf("  argv[%zu] = %s\n", i, p.we_wordv[i]);
    }

    /* Очищаємо лише динамічні ресурси wordexp. 
       ПРИМІТКА: p.we_wordv[0] не звільняється wordfree, оскільки це літерал */
    wordfree(&p);
    return 0;
}

int main(void) {
    return safe_tokenize("$HOME/*.txt \"аргумент з пробілами\"");
}
```
```cpp
#include <iostream>
#include <string_view>
#include <vector>
#include <stdexcept>
#include <wordexp.h>

class WordExpander {
public:
    explicit WordExpander(std::string_view expr, bool allow_cmd = false) {
        int flags = WRDE_UNDEF;
        if (!allow_cmd) {
            flags |= WRDE_NOCMD;
        }

        std::string null_term_expr(expr);
        int res = wordexp(null_term_expr.c_str(), &p_, flags);
        if (res != 0) {
            handle_error(res);
        }
    }

    ~WordExpander() noexcept {
        wordfree(&p_);
    }

    WordExpander(const WordExpander&) = delete;
    WordExpander& operator=(const WordExpander&) = delete;
    WordExpander(WordExpander&& other) noexcept : p_(other.p_) {
        other.p_ = wordexp_t{};
    }
    WordExpander& operator=(WordExpander&& other) noexcept {
        if (this != &other) {
            wordfree(&p_);
            p_ = other.p_;
            other.p_ = wordexp_t{};
        }
        return *this;
    }

    [[nodiscard]] std::size_t size() const noexcept {
        return p_.we_wordc;
    }

    [[nodiscard]] std::string_view operator[](std::size_t idx) const {
        if (idx >= p_.we_wordc) {
            throw std::out_of_range("Індекс за межами масиву розгорнутих слів");
        }
        return p_.we_wordv[idx];
    }

    [[nodiscard]] char** data() noexcept {
        return p_.we_wordv;
    }

private:
    static void handle_error(int code) {
        switch (code) {
            case WRDE_CMDSUB:
                throw std::invalid_argument("Безпека: виконання команд у wordexp заборонено");
            case WRDE_BADVAL:
                throw std::invalid_argument("Невизначена змінна оточення");
            case WRDE_SYNTAX:
                throw std::invalid_argument("Синтаксична помилка у рядку");
            case WRDE_NOSPACE:
                throw std::bad_alloc();
            default:
                throw std::runtime_error("Помилка розгортання рядка");
        }
    }

    wordexp_t p_{};
};

int main() {
    try {
        WordExpander expander("$HOME/*.log \"file with space.txt\"");
        std::cout << "Отримано слів: " << expander.size() << '\n';
        for (std::size_t i = 0; i < expander.size(); ++i) {
            std::cout << "  [" << i << "] " << expander[i] << '\n';
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

## 2. Глобінг імен файлів: glob(3) та globfree(3)

Якщо програмі потрібно виконувати виключно пошук файлів за маскою (без обробки змінних, підстановки команд та розгортання тильди), застосовується спеціалізований POSIX API `glob(3)`.

Заголовочний файл: `<glob.h>`

### Опис структури glob_t

:::tabs
```c
#include <glob.h>

/* Опис структури glob_t у POSIX C */
typedef struct {
    size_t gl_pathc; /* Кількість знайдених шляхів */
    char **gl_pathv; /* Масив покажчиків на знайдені шляхи, завершений NULL */
    size_t gl_offs;  /* Кількість зарезервованих слотів на початку */
} glob_t;
```
```cpp
#include <glob.h>

// У C++ використовуються ті ж поля структури glob_t:
// gl_pathc — кількість знайдених шляхів у файловій системі
// gl_pathv — масив покажчиків на рядки (char**)
// gl_offs  — зарезервована кількість початкових покажчиків
```
:::

### Сигнатури функцій glob(3)

Сигнатура функції генерації шляхів та звільнення пам'яті:

:::tabs
```c
int glob(const char *restrict pattern, int flags,
         int (*errfunc)(const char *epath, int eerrno),
         glob_t *restrict pglob);
void globfree(glob_t *pglob);
```
```cpp
int glob(const char *pattern, int flags,
         int (*errfunc)(const char *epath, int eerrno),
         glob_t *pglob);
void globfree(glob_t *pglob);
```
:::

### Основні прапори керування glob(3)

- `GLOB_ERR` — зупинити обхід файлової системи при виникненні будь-якої помилки читання каталогу (наприклад, відсутність прав доступу `EACCES`). За замовчуванням `glob` ігнорує каталоги, які не вдалося відкрити, і продовжує пошук.
- `GLOB_MARK` — додавати підсумковий символ косого слеша `/` до кожного знайденого шляху, який є каталогом. Це дозволяє легко відрізняти каталоги від звичайних файлів без додаткових системних викликів `stat(2)`.
- `GLOB_NOSORT` — не сортувати знайдені шляхи за алфавітом. За замовчуванням `glob` сортує вихідний масив `gl_pathv` відповідно до поточної локалі `LC_COLLATE`. Вимкнення сортування суттєво прискорює роботу на великих файлових системах.
- `GLOB_NOCHECK` — якщо за вказаним шаблоном `pattern` не знайдено жодного файла, повертати сам вихідний шаблон як єдиний результат у `gl_pathv[0]` (поведінка оболонки POSIX за замовчуванням).
- `GLOB_TILDE` — розгортати символ тильди `~` або `~user` на початку шаблону у відповідний домашній каталог.
- `GLOB_DOOFFS` — використовувати значення поля `pglob->gl_offs` для резервування початкових порожніх слотів у `gl_pathv`.
- `GLOB_APPEND` — додавати нові знайдені шляхи в кінець масиву `gl_pathv`, заповненого під час попереднього виклику `glob`.
- `GLOB_PERIOD` — дозволити зірочці `*` та знаку питання `?` відповідати провідній крапці `.` у прихованих файлах.

### Обробка помилок та функція errfunc

Параметр `errfunc` дозволяє передати вказівник на функцію зворотного виклику для обробки помилок читання каталогів:

:::tabs
```c
#include <stdio.h>

int my_errfunc(const char *epath, int eerrno) {
    fprintf(stderr, "Помилка доступу до каталогу %s: errno %d\n", epath, eerrno);
    /* Повернення 0 вказує glob продовжувати пошук; 
       повернення не-нульового значення перериває glob з кодом GLOB_ABORTED */
    return 0;
}
```
```cpp
#include <iostream>
#include <cerrno>

extern "C" int my_cpp_errfunc(const char *epath, int eerrno) {
    std::cerr << "Помилка доступу до каталогу " << epath << ": errno " << eerrno << '\n';
    return 0;
}
```
:::

Якщо `errfunc` дорівнює `NULL`, помилки читання каталогів ігноруються, якщо не встановлено прапор `GLOB_ERR`.

### Приклади використання glob у C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <glob.h>

void list_log_files(const char *pattern) {
    glob_t gstruct;
    int flags = GLOB_MARK | GLOB_TILDE;

    int res = glob(pattern, flags, NULL, &gstruct);
    if (res == 0) {
        printf("Знайдено файлів: %zu\n", gstruct.gl_pathc);
        for (size_t i = 0; i < gstruct.gl_pathc; i++) {
            printf("  [%zu] %s\n", i, gstruct.gl_pathv[i]);
        }
        globfree(&gstruct);
    } else if (res == GLOB_NOMATCH) {
        printf("Файлів за маскою '%s' не знайдено.\n", pattern);
    } else {
        fprintf(stderr, "Помилка глобінгу: %d\n", res);
    }
}

int main(void) {
    list_log_files("/var/log/*.log");
    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <vector>
#include <stdexcept>
#include <glob.h>

class PathGlobber {
public:
    explicit PathGlobber(std::string_view pattern, int flags = GLOB_MARK | GLOB_TILDE) {
        std::string null_term_pat(pattern);
        int status = glob(null_term_pat.c_str(), flags, nullptr, &gstruct_);
        if (status != 0 && status != GLOB_NOMATCH) {
            throw std::runtime_error("Помилка виконання глобінгу шляхів");
        }
    }

    ~PathGlobber() noexcept {
        globfree(&gstruct_);
    }

    PathGlobber(const PathGlobber&) = delete;
    PathGlobber& operator=(const PathGlobber&) = delete;

    [[nodiscard]] std::size_t size() const noexcept {
        return gstruct_.gl_pathc;
    }

    [[nodiscard]] std::string_view operator[](std::size_t i) const {
        if (i >= gstruct_.gl_pathc) {
            throw std::out_of_range("Індекс шляху за межами масиву");
        }
        return gstruct_.gl_pathv[i];
    }

private:
    glob_t gstruct_{};
};

int main() {
    try {
        PathGlobber globber("/var/log/*.log");
        std::cout << "Знайдено шляхів: " << globber.size() << '\n';
        for (std::size_t i = 0; i < globber.size(); ++i) {
            std::cout << "  " << globber[i] << '\n';
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

## 3. Зіставлення масок у пам'яті: fnmatch(3)

Якщо потрібно перевірити, чи відповідає текстовий рядок масці глобінгу (без звернення до файлової системи VFS), POSIX надає функцію `fnmatch(3)`.

Заголовочний файл: `<fnmatch.h>`

### Сигнатура fnmatch

:::tabs
```c
int fnmatch(const char *pattern, const char *string, int flags);
```
```cpp
int fnmatch(const char *pattern, const char *string, int flags);
```
:::

### Прапори fnmatch

- `FNM_PATHNAME` — символ косого слеша `/` у рядку `string` повинен явно збігатися з `/` у шаблоні `pattern`. Зірочка `*` та знак питання `?` не можуть відповідати слешу.
- `FNM_PERIOD` — провідна крапка `.` на початку рядка або одразу після косого слеша (при `FNM_PATHNAME`) повинна явно відповідати крапці у шаблоні.
- `FNM_NOESCAPE` — забороняє використовувати зворотний слеш `\` як екрануючий символ. Слеш трактується як звичайний символ.
- `FNM_CASEFOLD` — розширення GNU: виконувати зіставлення без урахування регістру символів.

### Коди повернення

- `0` — рядок відповідає масці.
- `FNM_NOMATCH` — рядок не відповідає масці.
- Інше не-нульове значення — виникла помилка.

Зіставлення маски у C та C++:

:::tabs
```c
#include <stdio.h>
#include <fnmatch.h>

int check_filename(const char *filename) {
    const char *pattern = "*.tar.gz";
    int flags = FNM_PATHNAME | FNM_PERIOD;

    if (fnmatch(pattern, filename, flags) == 0) {
        printf("Файл '%s' відповідає архіву tar.gz\n", filename);
        return 1;
    } else {
        printf("Файл '%s' НЕ відповідає масці\n", filename);
        return 0;
    }
}
```
```cpp
#include <iostream>
#include <string_view>
#include <fnmatch.h>

bool matches_pattern(std::string_view filename, std::string_view pattern) {
    std::string null_file(filename);
    std::string null_pat(pattern);
    return fnmatch(null_pat.c_str(), null_file.c_str(), FNM_PATHNAME | FNM_PERIOD) == 0;
}

int main() {
    std::cout << std::boolalpha;
    std::cout << matches_pattern("backup.tar.gz", "*.tar.gz") << '\n'; // true
    std::cout << matches_pattern(".hidden.tar.gz", "*.tar.gz") << '\n'; // false (FNM_PERIOD)
    return 0;
}
```
:::
