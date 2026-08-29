# ⚙️ Реалізація спрощеного потокового редактора на C та C++

Архітектура класичного потокового редактора `sed` базується на системній моделі однопрохідної потокової обробки: поєднанні двох динамічних буферів (`Pattern Space` та `Hold Space`), адресного фільтра та інтерпретатора ланцюжка команд. Для глибокого розуміння того, як ядро `sed` взаємодіє з дескрипторами вводу-виводу, динамічною пам'яттю процесу та скінченними автоматами регулярних виразів, нижче розібрано повну інженерну реалізацію емулятора потокового редактора на мовах C та C++.

Концептуальні основи та системний контекст потокової фільтрації викладено у статті [sed: архітектура потокового редактора та механіка трансформації тексту](root:sys-unix/sed), а повний реєстр опцій та кодів виклику наведено у [📋 Повному довіднику команд, адрес та прапорців потокового редактора sed](root:sys-unix/sed/api-sed-command-reference.md).

---

## Двобуферна архітектура: робочий простір та регістр утримання

Потоковий редактор не завантажує весь вхідний файл у пам'ять і не будує дерев документа. Натомість його пам'ять розділена на дві ізольовані області в адресному просторі процесу:

```
                  ┌────────────────────────────────────────┐
  Вхідний потік ──►  Pattern Space (Робочий простір)       ├──► Вихідний потік
     (stdin)      │  - містить поточний активний рядок     │      (stdout)
                  │  - приймає мутації s///, p, d          │
                  └───────────▲────────────────┬───────────┘
                              │     h / H      │
                        g / G │  (копіювання   │
                  (відновлення│  /додавання)   │
                              │                │
                  ┌───────────┴────────────────▼───────────┐
                  │   Hold Space (Регістр утримання)       │
                  │   - зберігає дані між циклами читання  │
                  │   - пасивний накопичувач контексту     │
                  └────────────────────────────────────────┘
```

1. **Pattern Space (простір шаблону):** Основний робочий буфер процесу. Сюди поміщається зчитаний з вхідного дескриптора рядок тексту (зі знятим кінцевим роздільником `\n`). Усі регулярні вирази, фільтри та команди заміни `s///` працюють виключно над цим буфером. Наприкінці циклу його вміст за замовчуванням виводиться в стандартний вивід.
2. **Hold Space (простір утримання / допоміжний регістр):** Резервний акумулятор стану. Його вміст **зберігається між циклами зчитування рядків**. Поки `Pattern Space` перезаписується на кожній ітерації новим рядком із входу, `Hold Space` тримає раніше збережені байти, доки сценарій явно не перезапише або не допише в нього нові дані.

Така двобуферна модель дозволяє розв'язувати задачі, що вимагають збереження контексту між рядками (наприклад, інверсія порядку рядків, накопичення багаторядкових логів або перестановка блоків), зберігаючи просторову складність програми рівною `O(L)`, де `L` — максимальна довжина накопиченого фрагмента, незалежно від гігабайтного чи терабайтного розміру вхідного потоку.

---

## Керування динамічною пам'яттю та стратегія росту буферів

У перших реалізаціях Version 7 Unix розмір буферів `sed` обмежувався фіксованим масивом у 4000 байтів. Рядки, що перевищували цей поріг, або аварійно завершували процес, або обрізалися. В емуляторі застосовано динамічну модель пам'яті GNU sed, де кожен буфер інкапсулює покажчик на виділену пам'ять, поточну зайняту довжину (`len`) та загальну виділену ємність (`cap`).

Стан рушія інкапсулює обидва буфери, лічильник зчитаних записів, прапорець останнього рядка потоку та прапорці виконання:

:::tabs
```c
typedef struct {
    char *pattern_space;
    size_t pattern_len;
    size_t pattern_cap;

    char *hold_space;
    size_t hold_len;
    size_t hold_cap;

    size_t line_number;
    bool is_last_line;      /* Прапорець настання EOF для адреси $ */
    bool quiet_mode;        /* Режим -n (заборона автодруку) */
    bool deleted;           /* Рядок відкинуто командою d або D */
    bool subst_success;     /* Прапорець успіху заміни для t/T */
} SedEngine;
```
```cpp
class SedEngine {
public:
    explicit SedEngine(bool quiet = false) : quiet_mode_(quiet) {}
    void process_stream(std::istream& in, const std::vector<SedCommand>& commands);

    [[nodiscard]] size_t line_number() const noexcept { return line_number_; }
    [[nodiscard]] bool is_last_line() const noexcept { return is_last_line_; }

private:
    void execute_command(SedCommand& cmd, std::istream& in);

    std::string pattern_space_;
    std::string hold_space_;
    size_t line_number_{0};
    bool is_last_line_{false};
    bool quiet_mode_{false};
    bool deleted_{false};
    bool subst_success_{false};
};
```
:::

### Політика геометричного розширення

Операції копіювання та конкатенації викликають допоміжні функції `buf_set` та `buf_append`. Щоб уникнути квадратичної деградації продуктивності `O(N^2)` при частих конкатенаціях, виділення пам'яті виконується з надлишковим запасом:

:::tabs
```c
static void buf_set(char **buf, size_t *len, size_t *cap, const char *src) {
    size_t slen = strlen(src);
    if (slen + 1 > *cap) {
        *cap = slen + 64;
        *buf = (char *)realloc(*buf, *cap);
    }
    memcpy(*buf, src, slen + 1);
    *len = slen;
}

static void buf_append(char **buf, size_t *len, size_t *cap, char sep, const char *src) {
    size_t slen = strlen(src);
    size_t needed = *len + (sep ? 1 : 0) + slen + 1;
    if (needed > *cap) {
        *cap = needed + 64;
        *buf = (char *)realloc(*buf, *cap);
    }
    if (sep && *len > 0) {
        (*buf)[(*len)++] = sep;
    }
    memcpy(*buf + *len, src, slen + 1);
    *len += slen;
}
```
```cpp
// У C++ клас std::string інкапсулює ємність і динамічне розширення автоматично:
void buf_set(std::string& dest, const std::string& src) {
    dest = src;
}

void buf_append(std::string& dest, char sep, const std::string& src) {
    if (sep != '\0' && !dest.empty()) {
        dest += sep;
    }
    dest += src;
}
```
:::

- При повному перезаписі (`buf_set`) нова ємність розраховується як `slen + 64` байти.
- При конкатенації (`buf_append`) резервується `needed + 64` байти, де `needed = current_len + (sep ? 1 : 0) + src_len + 1`.
- Завдяки використанню `memcpy` замість `strcat`, функція не витрачає час на повторне сканування рядка від початку, зберігаючи складність додавання `O(M)`, де `M` — довжина приєднуваного фрагмента.

Це мінімізує кількість звернень до системного розподільника пам'яті (`malloc`/`realloc`) і знижує навантаження на системні виклики ядра Linux `brk()` та `mmap()`.

### Інваріант нульового роздільника

Усі буферні операції гарантують наявність кінцевого байта `\0` після корисної довжини `*len`. Це дозволяє передавати покажчик `eng->pattern_space` безпосередньо у виклики `puts()` та POSIX `regexec()` без попереднього копіювання чи виділення проміжних масивів.

---

## Внутрішній устрій Hold Space та команди обміну: `h`, `H`, `g`, `G`, `x`

П'ять інструкцій взаємодії між регістрами забезпечують повний контроль над даними в пам'яті процесу. Їхня системна семантика базується на копіюванні, конкатенації та нуль-копійному обміні дескрипторами буферів:

| Команда | Назва операції | Системна дія в C | Семантика в C++ |
|---|---|---|---|
| `h` | Hold Copy | `buf_set(&hold, &len, &cap, pattern)` | `hold_space_ = pattern_space_;` |
| `H` | Hold Append | `buf_append(&hold, &len, &cap, '\n', pattern)` | `if (!hold.empty()) hold += '\n'; hold += pattern;` |
| `g` | Get Copy | `buf_set(&pattern, &len, &cap, hold)` | `pattern_space_ = hold_space_;` |
| `G` | Get Append | `buf_append(&pattern, &len, &cap, '\n', hold)` | `if (!pattern.empty()) pattern += '\n'; pattern += hold;` |
| `x` | Exchange | Обмін вказівниками та полями `len`/`cap` | `std::swap(pattern_space_, hold_space_);` |

### Механіка динамічного конкатенування з роздільником `\n`

Команди додавання `H` та `G` реалізують специфічну логіку вставки роздільника нового рядка:

1. **Семантика розділення:** Якщо цільовий буфер уже містить байти (`len > 0`), перед копіюванням джерела вставляється рівно один символ `\n`. Якщо ж буфер порожній, джерело копіюється без початкового перенесення рядка.
2. **Гарантія розміщення:** Функція заздалегідь перевіряє сумарну потребу в пам'яті:
   `needed = len_dst + (sep != 0 ? 1 : 0) + len_src + 1`
   Якщо `needed > cap_dst`, виконується перерозподіл пам'яті `realloc` із запасом у 64 байти, після чого дані копіюються через `memcpy`.
3. **Відмінність стандарту POSIX від емулятора:** За суворим стандартом POSIX sed, регістр `Hold Space` на старті процесу вважається таким, що містить порожній рядок. Тому виконання `H` на першому рядку в строгому POSIX-режимі призводить до утворення рядка `\n<текст_рядка>`. В інженерній практиці скрипти часто обходять цю поведінку ідіомою `1h; 1!H`. Наш емулятор на рівні `buf_append` реалізує безпечну поведінку: роздільник додається лише тоді, коли буфер фактично не є порожнім.

### Нуль-копійний обмін `x` (Exchange) за час O(1)

Команда `x` (`CMD_EXCHANGE`) реалізована без жодного виділення пам'яті та без копіювання рядкових байтів. Вона просто міняє місцями адреси буферів та їхні розмірні поля:

:::tabs
```c
char *tmp_buf = eng->pattern_space;
size_t tmp_len = eng->pattern_len;
size_t tmp_cap = eng->pattern_cap;

eng->pattern_space = eng->hold_space;
eng->pattern_len = eng->hold_len;
eng->pattern_cap = eng->hold_cap;

eng->hold_space = tmp_buf;
eng->hold_len = tmp_len;
eng->hold_cap = tmp_cap;
```
```cpp
std::swap(pattern_space_, hold_space_);
```
:::

У C++ виклик `std::swap(pattern_space_, hold_space_)` аналогічно обмінює три внутрішні покажчики об'єктів `std::string` (покажчик на буфер, розмір і місткість), забезпечуючи виконання за константний час `O(1)`.

---

## Адресний фільтр: одиночні предикати, діапазони `/addr1/,/addr2/` та розпізнавання `$`

Інструкція `sed` виконується лише тоді, коли поточний рядок задовольняє вказаній адресі. Адреса може бути числовою, регулярним виразом, спеціальним маркером фіналу потоку `$` або діапазоном з двох адрес.

### Структури представлення адрес

Для підтримки повної матриці адресних специфікацій кожна адреса описується дискретним типом:

:::tabs
```c
typedef enum {
    ADDR_NONE,          /* Безумовне виконання для всіх рядків */
    ADDR_NUM,           /* Адресація за абсолютним номером рядка (напр., 5) */
    ADDR_REGEX,         /* Адресація за регулярним виразом /шаблон/ */
    ADDR_LAST           /* Адресація за символом $ (останній рядок потоку) */
} AddressType;

typedef struct {
    AddressType type;
    size_t line_num;
    regex_t regex;
    bool regex_compiled;
} SingleAddress;

typedef struct {
    bool is_range;
    SingleAddress addr1;
    SingleAddress addr2;
    bool in_range;      /* Стан тригера діапазону (Flip-Flop) */
    bool invert;        /* Модифікатор інверсії ! */
} CommandAddress;
```
```cpp
enum class AddressKind {
    None,
    LineNumber,
    Regex,
    LastLine
};

struct SingleAddress {
    AddressKind kind{AddressKind::None};
    size_t line_num{0};
    std::optional<std::regex> regex_pattern;
};

struct CommandAddress {
    bool is_range{false};
    SingleAddress addr1;
    SingleAddress addr2;
    bool in_range{false};
    bool invert{false};
};
```
:::

### Автомат станів адресного діапазону (Flip-Flop State Machine)

Коли задано дві адреси `addr1,addr2`, виконання вмикається при першому збігу з `addr1` і триває доти, доки рядок не збіжиться з `addr2`:

```
                 addr1 збігся (in_range -> true)
Вхідний потік ───────────────▼──────────────────────────
[неактивно]          [активна зона виконання]
─────────────────────────────────▲──────────────────────
                 addr2 збігся (in_range -> false)
```

Логіка автомата має важливий системний крайовий випадок:
1. Якщо `in_range == false`: рушій перевіряє лише `addr1`. Якщо рядок відповідає `addr1`, стан перемикається: `in_range = true`.
2. Якщо `addr2` є **числовим номером рядка**, меншим або рівним поточному номеру, діапазон схлопується негайно (команда виконується рівно один раз на поточному рядку, а `in_range` скидається в `false`).
3. Якщо `addr2` є **регулярним виразом**, стандарт POSIX вимагає **не перевіряти `addr2` на тому ж самому рядку**, де збіглася `addr1`. Перевірка на закриття діапазону починається лише з наступного зчитаного рядка. Це гарантує, що вираз `/START/,/END/` не закриється на першому ж рядку, якщо він випадково містить обидва слова.
4. Якщо рядок відкрив діапазон, поточна команда виконується. Наступні рядки виконують команду безумовно, доки черговий рядок не задовольнить умові `addr2`. На рядку закриття команда виконується востаннє, після чого `in_range = false`.

### Розв'язання проблеми останнього рядка `$`: дворядковий Lookahead-буфер

У потоковому конвеєрі стандартний ввід `stdin` передається через анонімний пайп (`pipe`). Рушій не може заздалегідь знати загальну кількість рядків у файлі. Коли системний виклик `getline()` повертає черговий рядок, невідомо, чи є він останнім, чи за ним слідують інші байти.

Якщо перевіряти кінець файлу лише після виклику `getline()`, прапорець `is_last_line` стане істинним лише тоді, коли `getline()` поверне `-1` (EOF). Але в цей момент рядок уже завершив свій життєвий цикл і був виведений у `stdout`. Команда `$p` або `$d` просто не встигне спрацювати.

Для коректної ідентифікації адреси `$` головний цикл емулятора реалізує **однокроковий lookahead (випереджальне читання)**:

```
Ітерація N:
[ Попередній рядок ] ──► Обробляється рушієм (is_last_line = false)
[ Lookahead рядок ]  ──► Зчитано з дескриптора наперед

Ітерація N+1 (getline повернув EOF):
[ Попередній рядок ] ──► Обробляється рушієм (is_last_line = true, бо наступного немає!)
```

:::tabs
```c
static bool check_single_addr(SedEngine *eng, SingleAddress *addr) {
    switch (addr->type) {
        case ADDR_NONE:  return true;
        case ADDR_NUM:   return eng->line_number == addr->line_num;
        case ADDR_LAST:  return eng->is_last_line;
        case ADDR_REGEX:
            return regexec(&addr->regex, eng->pattern_space, 0, NULL, 0) == 0;
    }
    return false;
}

bool matches_address(SedEngine *eng, SedCommand *cmd) {
    bool match = false;
    CommandAddress *ca = &cmd->address;

    if (!ca->is_range) {
        match = check_single_addr(eng, &ca->addr1);
    } else {
        if (!ca->in_range) {
            if (check_single_addr(eng, &ca->addr1)) {
                ca->in_range = true;
                match = true;
                /* Числовий діапазон 5,3 схлопується негайно */
                if (ca->addr2.type == ADDR_NUM && ca->addr2.line_num <= eng->line_number) {
                    ca->in_range = false;
                }
            }
        } else {
            match = true;
            /* Закриття діапазону */
            if (check_single_addr(eng, &ca->addr2)) {
                ca->in_range = false;
            }
        }
    }

    return ca->invert ? !match : match;
}
```
```cpp
bool check_single_addr(const SedEngine& eng, const SingleAddress& addr, const std::string& pattern_space) {
    switch (addr.kind) {
        case AddressKind::None: return true;
        case AddressKind::LineNumber: return eng.line_number() == addr.line_num;
        case AddressKind::LastLine: return eng.is_last_line();
        case AddressKind::Regex:
            return addr.regex_pattern.has_value() && 
                   std::regex_search(pattern_space, *addr.regex_pattern);
    }
    return false;
}

bool matches_address(SedEngine& eng, SedCommand& cmd, const std::string& pattern_space) {
    auto& ca = cmd.address;
    bool match = false;

    if (!ca.is_range) {
        match = check_single_addr(eng, ca.addr1, pattern_space);
    } else {
        if (!ca.in_range) {
            if (check_single_addr(eng, ca.addr1, pattern_space)) {
                ca.in_range = true;
                match = true;
                if (ca.addr2.kind == AddressKind::LineNumber && ca.addr2.line_num <= eng.line_number()) {
                    ca.in_range = false;
                }
            }
        } else {
            match = true;
            if (check_single_addr(eng, ca.addr2, pattern_space)) {
                ca.in_range = false;
            }
        }
    }

    return ca.invert ? !match : match;
}
```
:::

---

## Механізм регулярної підстановки `s///` та контекстні прапорці `g`, `p`, `w`

Підстановка `s/pattern/replacement/flags` реалізована у функції `perform_subst()`. Вона виконує компіляцію виразу за допомогою POSIX `regcomp(&re, pattern, REG_EXTENDED)` та здійснює ітеративний пошук збігів через `regexec()`.

```
Вхідний рядок:  [  Префікс  |  Збіг (rm_so..rm_eo)  |  Суфікс  ]
                                       ▼
Результуючий:   [  Префікс  |      Заміна           |  Суфікс  ]
```

### Трьохсегментна збірка рядка

Для кожного знайденого збігу структура `regmatch_t` надає зміщення початку `match.rm_so` та кінця `match.rm_eo` відносно поточного вказівника `cursor`. Новий рядок збирається з трьох фрагментів:
1. **Префікс:** Байти `cursor[0 .. match.rm_so - 1]`, що передують знайденому патерну.
2. **Заміна:** Вміст рядка `replacement`.
3. **Суфікс:** Залишок вхідного рядка `cursor + match.rm_eo`.

При активному прапорці `subst_global` (`g`) пошук продовжується у циклі `while`, зміщуючи `cursor += match.rm_eo`. Після завершення циклу до результату дописується фінальний суфікс, старий `pattern_space` звільняється викликом `free()`, а покажчик перенаправляється на новостворений буфер `result`.

Одночасно виставляється прапорець успішності: `eng->subst_success = true`.

### Захист від зациклення на нульових збігах (Zero-Length Matches)

Коли регулярний вираз зіставляється з нульовою кількістю байтів (наприклад, метасимволи початку `^` або кінця рядка `$`, вираз `a*` на тексті `bbb` або порожній патерн), `match.rm_so == match.rm_eo`, тобто довжина збігу `match_len == 0`.

Якщо просто виконати `cursor += match.rm_eo`, вказівник не зрушить з місця. На наступній ітерації `regexec()` знову знайде той самий нульовий збіг на тій самій позиції, і програма впаде в нескінченний цикл, невпинно нарощуючи результуючий буфер до аварійного вичерпання пам'яті (OOM).

Для запобігання цій аварії в емуляторі передбачено захисний механізм:

:::tabs
```c
if (match_len == 0 && *cursor != '\0') {
    result[res_len++] = *cursor;
    result[res_len] = '\0';
    cursor++;
}
```
```cpp
// У C++ std::regex_replace стандартної бібліотеки містить внутрішню перевірку нульових зсувів:
auto flags = cmd.subst_global 
    ? std::regex_constants::match_default 
    : std::regex_constants::format_first_only;
pattern_space_ = std::regex_replace(pattern_space_, re, cmd.subst_replacement, flags);
```
:::

Якщо знайдено нульовий збіг, рушій примусово копіює один символ під курсором у вихідний результат і зсуває `cursor` на 1 байт уперед, гарантуючи завершення циклу за лінійний час `O(N)` відносно довжини рядка.

### Прапорці заміни: `g`, `p`, `w` та робота з дескрипторами

Поведінка команди заміни після успішної трансформації залежить від встановлених суфіксних прапорців:

1. **Глобальна заміна `g`:** Без прапорця `g` цикл підстановки переривається після першого знайденого збігу (`break`). З прапорцем `g` пошук триває вздовж усього рядка.
2. **Умовний друк `p` (Print on Match):** Якщо заміна фактично змінила рядок (`subst_success == true`), змінений `Pattern Space` негайно відправляється у стандартний вивід `stdout`. Це дозволяє використовувати ідіому `sed -n 's/pattern/replacement/p'`, де друкуються виключно рядки, що зазнали мутації.
3. **Запис у файл через дескриптор `w <шлях>` (Write on Match):**
   - **Життєвий цикл файлових дескрипторів:** За стандартом POSIX, файл, вказаний у команді `w` або прапорці `s///w`, відкривається на запис (`fopen(path, "w")` або `open(path, O_WRONLY|O_CREAT|O_TRUNC, 0666)`) **один раз на етапі компіляції сценарію**, до початку читання першого рядка вхідного потоку. Навіть якщо жоден рядок не збігся із шаблоном, цільовий файл буде створений з нульовим розміром.
   - **Управління дескрипторами:** Структура команди зберігає відкритий покажчик `FILE *w_file` (або `std::shared_ptr<std::ofstream>` у C++). При кожній успішній підстановці результуючий рядок записується у відкритий дескриптор:

:::tabs
```c
if (cmd->type == CMD_SUBST) {
    bool replaced = perform_subst(eng, cmd->subst_pattern, cmd->subst_replacement, cmd->subst_global);
    if (replaced) {
        eng->subst_success = true;
        if (cmd->subst_print) {
            puts(eng->pattern_space);
        }
        if (cmd->w_file != NULL) {
            fputs(eng->pattern_space, cmd->w_file);
            fputc('\n', cmd->w_file);
            fflush(cmd->w_file);
        }
    }
}
```
```cpp
if (cmd.type == CommandType::Subst) {
    std::regex re(cmd.subst_pattern);
    auto flags = cmd.subst_global 
        ? std::regex_constants::match_default 
        : std::regex_constants::format_first_only;
    
    std::string result = std::regex_replace(pattern_space_, re, cmd.subst_replacement, flags);
    if (result != pattern_space_) {
        pattern_space_ = std::move(result);
        subst_success_ = true;
        if (cmd.subst_print) {
            std::cout << pattern_space_ << '\n';
        }
        if (cmd.w_stream && cmd.w_stream->is_open()) {
            (*cmd.w_stream) << pattern_space_ << '\n';
            cmd.w_stream->flush();
        }
    }
}
```
:::

Усі відкриті дескриптори закриваються функцією `fclose()` / закриттям файлового потоку лише під час фінальної деініціалізації рушія (`engine_free()`), що мінімізує накладні витрати на відкриття та закриття файлів у ядрі ОС.

---

## Виконання зовнішніх команд: розширення GNU sed `e` (Execute)

Утиліта GNU sed містить розширення `e` (Execute), яке дозволяє викликати зовнішні системні утиліти та передавати їхній вивід безпосередньо у робочий буфер редактора. Воно підтримується у двох синтаксичних формах:

1. **Окрема команда `[адреса]e [команда_оболонки]`:**
   - Якщо аргумент задано (наприклад, `e date`), рушій виконує зазначену команду через системну оболонку `/bin/sh` і відправляє її стандартний вивід у вихідний потік.
   - Якщо аргумент відсутній (`e`), рушій бере **поточний вміст Pattern Space як текст команди**, передає його на виконання оболонці, зчитує вивід процесу і **повністю заміщує вміст Pattern Space отриманим результатом** (зі зняттям кінцевого `\n`).
2. **Прапорець заміни `s/regex/replacement/e`:**
   - Рушій виконує регулярну підстановку над рядком.
   - Результуючий рядок передається оболонці як виконавча команда.
   - Вивід дочірнього процесу заміщує вміст `Pattern Space`.

### Системна механіка взаємодії процесів через пайпи

Для реалізації команди `e` емулятор застосовує POSIX-інтерфейс `popen()` та `pclose()`:

```
  SedEngine (батьківський процес)
       │
       ├─► pipe() ──► fork() ──► execve("/bin/sh", "-c", cmd) [дочірній процес]
       │                                │
       ▼ (читання з дескриптора)        ▼ (stdout дочірнього процесу)
  Зчитування виводу ◄─────── [Анонімний пайп ядра]
       │
  Pattern Space = вивід (без кінцевого \n)
       │
  pclose() ──► waitpid() [синхронізація завершення]
```

:::tabs
```c
static void execute_shell_command(SedEngine *eng, const char *cmd_override) {
    const char *cmd_to_run = (cmd_override && *cmd_override) ? cmd_override : eng->pattern_space;
    if (!cmd_to_run || *cmd_to_run == '\0') {
        return;
    }

    FILE *pipe_fp = popen(cmd_to_run, "r");
    if (!pipe_fp) {
        return;
    }

    char chunk[256];
    char *output = NULL;
    size_t out_len = 0, out_cap = 0;

    while (fgets(chunk, sizeof(chunk), pipe_fp) != NULL) {
        size_t clen = strlen(chunk);
        if (out_len + clen + 1 > out_cap) {
            out_cap = out_len + clen + 128;
            output = (char *)realloc(output, out_cap);
        }
        memcpy(output + out_len, chunk, clen);
        out_len += clen;
        output[out_len] = '\0';
    }

    pclose(pipe_fp);

    if (output) {
        /* Зняття кінцевого роздільника \n з виводу команди */
        if (out_len > 0 && output[out_len - 1] == '\n') {
            output[--out_len] = '\0';
        }
        free(eng->pattern_space);
        eng->pattern_space = output;
        eng->pattern_len = out_len;
        eng->pattern_cap = out_cap;
    } else {
        buf_set(&eng->pattern_space, &eng->pattern_len, &eng->pattern_cap, "");
    }
}
```
```cpp
void execute_shell_command(const std::string& cmd_override = "") {
    std::string cmd_to_run = cmd_override.empty() ? pattern_space_ : cmd_override;
    if (cmd_to_run.empty()) {
        return;
    }

    std::unique_ptr<FILE, decltype(&pclose)> pipe_fp(popen(cmd_to_run.c_str(), "r"), pclose);
    if (!pipe_fp) {
        return;
    }

    char buffer[256];
    std::string result;
    while (fgets(buffer, sizeof(buffer), pipe_fp.get()) != nullptr) {
        result += buffer;
    }

    if (!result.empty() && result.back() == '\n') {
        result.pop_back();
    }
    pattern_space_ = std::move(result);
}
```
:::

### Ціна продуктивності та межі безпеки

1. **Накладні витрати ядра ОС:** Кожен виклик команди `e` породжує новий процес через системні виклики `fork()` (або `clone()`) та `execve()`, виділяє анонімний пайп та таблицю дескрипторів, а потім очікує завершення процесу через `waitpid()`. Виконання команди `e` на потоці з мільйона рядків сповільнить обробку на кілька порядків порівняно з чистими рядковими операціями в пам'яті процесу.
2. **Вразливість довільного виконання коду (Shell Injection):** Якщо вміст `Pattern Space` формується з неперевірених вхідних даних (наприклад, заголовки HTTP-запитів чи поля поштових повідомлень), використання команди `e` або прапорця `s///e` створює пряму загрозу виконання шкідливих команд через підстановку метасимволів оболонки (`; rm -rf /`, `$(curl ...)`).

---

## Керування потоком виконання: мітки `:label` та переходи `b`, `t`, `T`

У повному інтерпретаторі `sed` сценарій компілюється у вектор інструкцій, а мітки `:label` транслюються в таблицю переходів за індексами командного масиву.

```
       ┌────────────────────────────────────────────────────────┐
       │                 Сценарій команд sed                    │
       │                                                        │
       │  0: :loop ◄─────────────────────────────────────────┐  │
       │  1: s/<[^>]*>//g  ──(успішна заміна)──► [set dirty] │  │
       │  2: /</ {                                           │  │
       │  3:     N                                           │  │
       │  4:     b loop ─────────────────────────────────────┘  │
       │  5: }                                                  │
       │  6: t loop ──(якщо dirty == true, скинути й стрибнути) │
       └────────────────────────────────────────────────────────┘
```

Інтерпретатор виконує інструкції за допомогою покажчика поточної команди `ip` (Instruction Pointer):

:::tabs
```c
size_t ip = 0;
while (ip < command_count && !eng->deleted && !restart_cycle) {
    SedCommand *cmd = &commands[ip];
    // Оцінка адреси рядка або regex...
    if (!matches_address(eng, cmd)) {
        ip++;
        continue;
    }
    // Виконання команди та оновлення ip
    execute_command_step(eng, cmd, &ip, commands, command_count, in);
}
```
```cpp
size_t ip = 0;
while (ip < commands.size() && !deleted_ && !restart_cycle) {
    const auto& cmd = commands[ip];
    if (!matches_address(cmd)) {
        ip++;
        continue;
    }
    execute_command_step(cmd, ip, commands, in);
}
```
:::

### 1. Безумовний перехід `b [label]` (Branch)

- **Перехід за міткою:** Встановлює `ip = target_ip`, де `target_ip` — індекс команди, що йде безпосередньо за оголошенням мітки `:label`.
- **Порожній перехід (`b` без мітки):** Переносить `ip = command_count`, тобто негайно спрямовує виконання в кінець командного списку. Це завершує обробку поточного рядка, запускає автоматичний друк (якщо не активовано `-n`) і починає наступну ітерацію циклу `getline()`.

### 2. Умовний перехід за успіхом заміни `t [label]` (Test on Success)

- Перевіряє брудний біт успішності підстановки `eng->subst_success`.
- Якщо хоча б одна попередня команда `s///` виконала успішну заміну з моменту зчитування поточного рядка або з моменту попереднього виклику команди перевірки `t`/`T`, керування передається на цільову мітку: `ip = target_ip`.
- **Критичний інваріант скидання:** Виконання команди `t` (незалежно від того, чи відбувся стрибок, чи умова виявилася хибною) обов'язково **скидає** прапорець:

:::tabs
```c
bool jump = eng->subst_success;
eng->subst_success = false;
if (jump) {
    *ip = target_ip;
    return;
}
(*ip)++;
```
```cpp
bool jump = subst_success_;
subst_success_ = false;
if (jump) {
    ip = target_ip;
    return;
}
ip++;
```
:::

Це виключає повторні хибні переходи на наступних ітераціях командного списку.

### 3. Умовний перехід за невдачею заміни `T [label]` (Test on Failure, GNU sed)

- Здійснює перехід на мітку виключно тоді, коли жодна команда `s///` не зробила заміни (`!eng->subst_success`).
- Так само обов'язково скидає прапорець `eng->subst_success = false`.

:::tabs
```c
bool jump = !eng->subst_success;
eng->subst_success = false;
if (jump) {
    *ip = target_ip;
    return;
}
(*ip)++;
```
```cpp
bool jump = !subst_success_;
subst_success_ = false;
if (jump) {
    ip = target_ip;
    return;
}
ip++;
```
:::

Завдяки наявності буфера `Hold Space`, багаторядкових операцій та умовних переходів `t`/`b`, командна мова `sed` є повною за Тьюрінгом і дозволяє реалізовувати довільні кінцеві автомати, лічильники та парсери в межах єдиного потокового проходу.

---

## Багаторядковий конвеєр та ковзне вікно: команди `N`, `P`, `D`

Стандартний життєвий цикл `sed` працює строго з одним фізичним рядком. Для аналізу контексту, що перетинає межі рядків (наприклад, багаторядкові теги XML/HTML, сигнатури функцій у C чи розриви стек-трейсів логів), використовується трійка багаторядкових інструкцій:

```
Потік: [ Рядок 1 ] \n [ Рядок 2 ] \n [ Рядок 3 ]
              ▲
              │
1. Читання:   Pattern Space = "Рядок 1"
2. Виклик N:  Pattern Space = "Рядок 1\nРядок 2"
3. Виклик P:  stdout <── "Рядок 1"
4. Виклик D:  Pattern Space = "Рядок 2"  ──► [Перезапуск сценарію БЕЗ читання]
5. Виклик N:  Pattern Space = "Рядок 2\nРядок 3"
6. Виклик P:  stdout <── "Рядок 2"
7. Виклик D:  Pattern Space = "Рядок 3"  ──► [Перезапуск сценарію БЕЗ читання]
```

### 1. Дописування наступного рядка: `N` (`CMD_NEXT_APPEND`)

Команда `N` вичитує черговий рядок із вхідного дескриптора за допомогою `getline()`, знімає кінцевий `\n` та додає його до поточного `pattern_space` через вставку символу нового рядка `\n`. Одночасно інкрементується лічильник рядків `line_number`, щоб наступні перевірки адрес за номерами залишалися синхронізованими з фізичним файлом.

:::tabs
```c
case CMD_NEXT_APPEND: {
    char *next_line = NULL;
    size_t ncap = 0;
    ssize_t nread = getline(&next_line, &ncap, in);
    if (nread > 0) {
        if (next_line[nread - 1] == '\n') next_line[--nread] = '\0';
        buf_append(&eng->pattern_space, &eng->pattern_len, &eng->pattern_cap, '\n', next_line);
        eng->line_number++;
    }
    free(next_line);
    break;
}
```
```cpp
case CommandType::NextAppend: {
    std::string next_line;
    if (std::getline(in, next_line)) {
        line_number_++;
        if (!pattern_space_.empty()) {
            pattern_space_ += '\n';
        }
        pattern_space_ += next_line;
    }
    break;
}
```
:::

> ⚠️ **Крайовий випадок POSIX при EOF:** Якщо під час виконання команди `N` досягнуто кінець файлу (EOF), стандарт POSIX sed вимагає негайно завершити роботу процесу **без виконання автоматичного друку** накопиченого `pattern_space`. У GNU sed за замовчуванням (без прапорця `--posix`) вміст виводиться перед виходом.

### 2. Багаторядковий друк: `P` (Print First Segment)

Друкує вміст `pattern_space` від початку до першого знайденого символу `\n`. Якщо символу нового рядка в буфері немає, команда `P` поводиться ідентично до стандартного `p`, виводячи весь буфер:

:::tabs
```c
case CMD_PRINT_FIRST: {
    char *nl = memchr(eng->pattern_space, '\n', eng->pattern_len);
    if (nl != NULL) {
        fwrite(eng->pattern_space, 1, nl - eng->pattern_space, stdout);
        putchar('\n');
    } else {
        puts(eng->pattern_space);
    }
    break;
}
```
```cpp
case CommandType::PrintFirst: {
    auto pos = pattern_space_.find('\n');
    if (pos != std::string::npos) {
        std::cout << pattern_space_.substr(0, pos) << '\n';
    } else {
        std::cout << pattern_space_ << '\n';
    }
    break;
}
```
:::

### 3. Багаторядкове видалення та перезапуск циклу: `D` (Delete First Segment)

Команда `D` є основою для побудови конвеєра з ковзним вікном (Sliding Window):
- Вона знаходить перший символ `\n` у `pattern_space` і видаляє початковий фрагмент разом із цим роздільником за допомогою `memmove()`, зміщуючи залишок у початок буфера.
- **Головна відмінність від `d`:** Команда `d` повністю очищає буфер і переходить до зчитування нового рядка з входу. Команда `D` **не зчитує новий рядок**, а негайно **перезапускає виконання сценарію з найпершої команди (`ip = 0`) над залишком буфера**.
- Якщо ж у `pattern_space` немає жодного `\n`, команда `D` очищає весь буфер і починає звичайний новий цикл читання, як і `d`.

:::tabs
```c
case CMD_DELETE_FIRST: {
    char *nl = memchr(eng->pattern_space, '\n', eng->pattern_len);
    if (nl != NULL) {
        size_t skip = (nl - eng->pattern_space) + 1;
        size_t rem = eng->pattern_len - skip;
        memmove(eng->pattern_space, nl + 1, rem);
        eng->pattern_space[rem] = '\0';
        eng->pattern_len = rem;
        // Перезапуск циклу команд над залишком буфера без виклику getline()
        restart_cycle = true;
    } else {
        eng->deleted = true;
    }
    break;
}
```
```cpp
case CommandType::DeleteFirst: {
    auto pos = pattern_space_.find('\n');
    if (pos != std::string::npos) {
        pattern_space_.erase(0, pos + 1);
        restart_cycle = true;
    } else {
        deleted_ = true;
    }
    break;
}
```
:::

Цей механізм дозволяє обробляти нескінченні потоки даних у вікні довільної ширини (наприклад, перевірка пар рядків, зшивання розірваних записів логів), споживаючи строго фіксований обсяг оперативної пам'яті `O(W)`, де `W` — максимальний розмір вікна.

---

## Вихідний код реалізації

Нижче наведено робочі реалізації емулятора потокового редактора: низькорівнева версія на чистому C (стандарт C11 з POSIX regex) та ідіоматична версія на C++ (стандарт C++20 з RAII, `std::regex` та `std::optional`).

:::tabs
:::code proj-stream-editor-emulator/c/main.c
:::code proj-stream-editor-emulator/cpp/main.cpp
:::

---

## Інженерний аналіз: порівняння C та C++, безпека та крайові випадки

### 1. Стратегії роботи з пам'яттю: C проти C++20

| Критерій | Реалізація на C (POSIX C11) | Реалізація на C++ (C++20) |
|---|---|---|
| **Керування пам'яттю** | Ручне виділення (`malloc`, `realloc`, `free`). Структура `SedEngine` потребує явної ініціалізації (`engine_init`) та вивільнення ресурсів через `engine_free()`. | Автоматичне керування за принципом RAII. Клас `SedEngine` автоматично звільняє всі буфери у деструкторі без ризику витоків. |
| **Оптимізація малих рядків (SSO)** | Відсутня. Будь-який буфер створюється через динамічну алокацію в купі (початковий розмір 128 байтів). | Працює автоматично в `std::string`. Рядки довжиною до 15–22 байтів зберігаються безпосередньо в тілі структури без звернення до купи (heap). |
| **Регулярні вирази** | POSIX `regex.h` (`regcomp`, `regexec`, `regfree`). Швидка компіляція NFA/DFA автоматів, мінімальний overhead за пам'яттю. | `std::regex` та `std::regex_replace`. Висока виразність, але більший час ініціалізації автомата та потенційні винятки `std::regex_error`. |
| **Безпека типів адрес** | Структура `SingleAddress` з перерахуванням `AddressType` та полями `line_num`/`regex`. | Безпечний тип `std::optional<std::regex>`, що унеможливлює розіменування неініціалізованого автомата. |
| **Обмін буферами `x`** | Обмін 3 скалярних полів (`pattern_space`, `len`, `cap`) за час `O(1)`. | `std::swap(pattern_space_, hold_space_)` обмінює внутрішні покажчики за час `O(1)`. |
| **Управління I/O та процесами** | Ручний контроль дескрипторів файлів (`fopen`/`fclose`) та каналів (`popen`/`pclose`). | Автоматичне звільнення дескрипторів через `std::ofstream` та розумні покажчики `std::unique_ptr<FILE, decltype(&pclose)>`. |

### 2. Запобігання витокам пам'яті та ресурсів ОС

- **Пам'ять підстановок:** У мові C функція `perform_subst()` виділяє новий динамічний буфер `result`. У разі успішної заміни старий буфер `eng->pattern_space` обов'язково звільняється викликом `free()`, після чого покажчик перенаправляється на `result`. Якщо збігів не знайдено, функція негайно звільняє виділений `result`, запобігаючи накопиченню сміття в купі процесу.
- **Вивільнення автоматів Regex:** Після завершення пошуку компільований регулярний вираз обов'язково вивантажується через `regfree(&re)`, що очищає внутрішні таблиці станів скінченного автомата.
- **Дескриптори вихідних файлів (`w`):** Файли відкриваються один раз при старті процесу. У разі аварійного завершення або штатного виходу всі відкриті покажчики `FILE *` мають бути закриті через `fclose()` для скидання внутрішніх буферів користувацького простору ядра на диск.
- **Дочірні процеси (`e`):** Виклик `pclose(pipe_fp)` є обов'язковим, оскільки закриття кінця каналу без `pclose()` призведе до появи процесів-зомбі (Zombie Processes) у таблиці процесів ядра Linux.

### 3. Обробка відмов системних викликів та дескрипторів потоку

При вичерпанні оперативної пам'яті виклик `realloc()` у C повертає `NULL`. У продакшн-коді обробники пам'яті повинні перевіряти результат перерозподілу через тимчасовий покажчик (`char *new_ptr = realloc(*buf, *cap);`), щоб уникнути витоку вихідного буфера при аварії. У C++ нестача пам'яті генерує виняток `std::bad_alloc`, який перехоплюється на рівні головного циклу обробки потоку.

При досягненні кінця потоку (`EOF`) або помилці читання дескриптора системна функція `getline()` повертає значення `-1`. Завдяки дворядковому механізму lookahead рушій коректно завершує цикл обробки без звернення до неініціалізованого буфера, звільняє пам'ять викликом `free(line)` та повертає код успіху `0`.

---

## Компіляція, тестування та верифікація поведінки

Для компіляції обох версій емулятора використовуються стандартні інструменти GNU Toolchain або Clang:

```bash
# 1. Збірка версії на мові C (стандарт C11 з оптимізацією O2 та попередженнями):
gcc -std=c11 -O2 -Wall -Wextra proj-stream-editor-emulator/c/main.c -o mini-sed-c

# 2. Збірка версії на мові C++ (стандарт C++20):
g++ -std=c++20 -O2 -Wall -Wextra proj-stream-editor-emulator/cpp/main.cpp -o mini-sed-cpp
```

### Верифікація роботи конвеєра підстановки

Перевірка базової заміни слів та адресного фільтра:

```bash
# Тестовий потік даних:
printf "INFO: initialization completed\nWARN: disk space low\nERROR: timeout occurred\n" | ./mini-sed-c
```

**Очікуваний вивід:**
```text
INFO: initialization completed
ALERT: disk space low
ALERT: disk space low
ERROR: timeout occurred
```

Рядок із попередженням `WARN` був трансформований командою `s/WARN/ALERT/g`, надрукований явною командою `p`, після чого автоматично виведений ще раз наприкінці життєвого циклу рядка, що повністю відповідає специфікації поведінки POSIX sed.
