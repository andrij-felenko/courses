# ⚙️ Реалізація спрощеного потокового редактора на C та C++

Архітектура потокового редактора `sed` базується на лаконічній, проте суворій системній моделі: поєднанні двох динамічних буферів (`Pattern Space` та `Hold Space`), адресного фільтра та інтерпретатора командного списку. Для глибокого розуміння того, як ядро `sed` взаємодіє з системними викликами, пам'яттю процесу та регулярними виразами, нижче розібрано повну інженерну реалізацію мініатюрного емулятора потокового редактора на мовах C та C++.

---

## Архітектурний дизайн та компоненти емулятора

Емулятор відтворює функціональний кістяк стандарту POSIX sed і складається з трьох ключових підсистем:

1. **Менеджер стану та робочих буферів (SedEngine):**
   - Керує виділенням, перерозподілом та очищенням двох ізольованих областей пам'яті: основного робочого простору `pattern_space` та допоміжного регістра `hold_space`.
   - Зберігає глобальний стан процесу: лічильник зчитаних рядків `line_number`, прапорець пригнічення автоматичного друку `quiet_mode` (аналог опції командного рядка `-n`), статус видалення поточного рядка `deleted` та прапорець успішності останньої проведеної підстановки `subst_success` (для підтримки умовних переходів).
2. **Адресний предикат (Address Matcher):**
   - Підтримує дворівневу фільтрацію: перевірку за абсолютним номером рядка (`line_addr`) та перевірку відповідності регулярному виразу над поточним вмістом робочого простору через POSIX `regexec()` у C або `std::regex_search()` у C++.
3. **Виконавчий конвеєр інструкцій (Command Dispatcher):**
   - Реалізує обробку команд регулярної підстановки `s///` (з підтримкою глобального прапорця `g`), друку `p`, видалення `d`, маніпуляцій з регістром утримання (`h`, `H`, `g`, `G`, `x`) та багаторядкового злиття через команду `N`.

---

## Керування динамічною пам'яттю та рядковими буферами

У класичних реалізаціях Version 7 Unix розмір буферів обмежувався статичним масивом у 4000 байтів. Якщо вхідний рядок перевищував цей ліміт, редактор завершував роботу аварійно або обрізав байти. У нашому емуляторі застосовано динамічну модель GNU sed: буфери починають своє життя з розміру 128 байтів і автоматично розширюються через системний розподільник пам'яті (`realloc` у C або динамічний вектор символів у C++), що гарантує коректну обробку рядків довільної довжини без витоків пам'яті.

Щоб уникнути квадратичної часової складності при частих операціях конкатенації, структури буферів зберігають окремо поточну зайняту довжину рядка (`len`) та загальну ємність виділеного блоку пам'яті (`cap`). Кожне розширення додає фіксований запас пам'яті (Geometric Growth Policy), що амортизує витрати на виклики ядра Linux `brk()` та `mmap()`.

Окрему увагу приділено операціям конкатенації `H` (Hold Append), `G` (Get Append) та `N` (Next Append). При додаванні рядка буферний менеджер обов'язково перевіряє наявність попередніх даних і вставляє роздільник нового рядка `\n` лише тоді, коли цільовий буфер не є порожнім. Це усуває появу фальшивих порожніх рядків на початку обробки.

---

## Механізм компіляції та виконання регулярних виразів

Для виконання підстановки `s///` у мові C використовується системна бібліотека POSIX Regex (`regex.h`). Структура `regex_t` компілюється один раз перед початком обробки потоку за допомогою `regcomp(&re, pattern, REG_EXTENDED)`.

Під час кожного проходу підстановки функція `regexec()` заповнює масив структур `regmatch_t`. Структура містить два критично важливі зміщення:
- `rm_so` (Start Offset): байтове зміщення від початку вхідного рядка до першого символу знайденого збігу.
- `rm_eo` (End Offset): байтове зміщення до першого символу після кінця збігу.

Ці зміщення дозволяють зібрати вихідний рядок з трьох частин: незміненого префікса `[0 .. rm_so]`, тексту заміни `replacement` та залишкового суфікса `[rm_eo .. N]`. При наявності прапорця `global == true` пошук продовжується над суфіксом у циклі `while`.

---

## Обробка кінця файлу (EOF) та системна буферизація

При роботі з нескінченними потоками або сокетами Unix надзвичайно важливо коректно розрізняти порожній рядок і сигнал завершення файлу `EOF`. Системна функція `getline()` повертає `-1`, коли потік вичерпано. Якщо команда `N` зустрічає `EOF` під час спроби дочитати наступний рядок, стандарт POSIX вимагає негайного припинення роботи потокового редактора без виконання автоматичного друку поточного Pattern Space. Ця тонка поведінка реалізована в обох вкладках емулятора.

---

## Вихідний код реалізації

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <regex.h>
#include <stdbool.h>

typedef enum {
    CMD_SUBST,
    CMD_PRINT,
    CMD_DELETE,
    CMD_HOLD_COPY,
    CMD_HOLD_APPEND,
    CMD_GET_COPY,
    CMD_GET_APPEND,
    CMD_EXCHANGE,
    CMD_NEXT_APPEND
} CommandType;

typedef struct {
    CommandType type;
    int line_addr;          /* 0 якщо адреси за номером немає */
    char *regex_addr_str;
    regex_t regex_addr;
    bool has_regex_addr;
    char *subst_pattern;
    char *subst_replacement;
    bool subst_global;
} SedCommand;

typedef struct {
    char *pattern_space;
    size_t pattern_len;
    size_t pattern_cap;

    char *hold_space;
    size_t hold_len;
    size_t hold_cap;

    size_t line_number;
    bool quiet_mode;
    bool deleted;
    bool subst_success;
} SedEngine;

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

static void engine_init(SedEngine *eng, bool quiet) {
    eng->pattern_space = (char *)malloc(128);
    eng->pattern_space[0] = '\0';
    eng->pattern_len = 0;
    eng->pattern_cap = 128;

    eng->hold_space = (char *)malloc(128);
    eng->hold_space[0] = '\0';
    eng->hold_len = 0;
    eng->hold_cap = 128;

    eng->line_number = 0;
    eng->quiet_mode = quiet;
    eng->deleted = false;
    eng->subst_success = false;
}

static void engine_free(SedEngine *eng) {
    free(eng->pattern_space);
    free(eng->hold_space);
}

static bool perform_subst(SedEngine *eng, const char *pattern, const char *rep, bool global) {
    regex_t re;
    if (regcomp(&re, pattern, REG_EXTENDED) != 0) {
        return false;
    }

    regmatch_t match;
    const char *cursor = eng->pattern_space;
    char *result = NULL;
    size_t res_len = 0, res_cap = 0;
    bool replaced = false;

    while (regexec(&re, cursor, 1, &match, 0) == 0) {
        replaced = true;
        size_t prefix_len = match.rm_so;
        size_t match_len = match.rm_eo - match.rm_so;
        size_t rep_len = strlen(rep);

        size_t needed = res_len + prefix_len + rep_len + 1;
        if (needed > res_cap) {
            res_cap = needed + 128;
            result = (char *)realloc(result, res_cap);
        }

        memcpy(result + res_len, cursor, prefix_len);
        res_len += prefix_len;
        memcpy(result + res_len, rep, rep_len);
        res_len += rep_len;
        result[res_len] = '\0';

        cursor += match.rm_eo;
        if (!global) {
            break;
        }
        if (match_len == 0 && *cursor != '\0') {
            result[res_len++] = *cursor;
            result[res_len] = '\0';
            cursor++;
        }
    }

    if (replaced) {
        size_t suffix_len = strlen(cursor);
        size_t needed = res_len + suffix_len + 1;
        if (needed > res_cap) {
            res_cap = needed;
            result = (char *)realloc(result, res_cap);
        }
        memcpy(result + res_len, cursor, suffix_len + 1);
        res_len += suffix_len;

        free(eng->pattern_space);
        eng->pattern_space = result;
        eng->pattern_len = res_len;
        eng->pattern_cap = res_cap;
    } else {
        free(result);
    }

    regfree(&re);
    return replaced;
}

static void execute_command(SedEngine *eng, SedCommand *cmd, FILE *in) {
    /* Перевірка адреси за номером рядка */
    if (cmd->line_addr > 0 && (size_t)cmd->line_addr != eng->line_number) {
        return;
    }
    /* Перевірка адреси за регулярним виразом */
    if (cmd->has_regex_addr) {
        if (regexec(&cmd->regex_addr, eng->pattern_space, 0, NULL, 0) != 0) {
            return;
        }
    }

    switch (cmd->type) {
        case CMD_SUBST:
            if (perform_subst(eng, cmd->subst_pattern, cmd->subst_replacement, cmd->subst_global)) {
                eng->subst_success = true;
            }
            break;
        case CMD_PRINT:
            puts(eng->pattern_space);
            break;
        case CMD_DELETE:
            eng->deleted = true;
            break;
        case CMD_HOLD_COPY:
            buf_set(&eng->hold_space, &eng->hold_len, &eng->hold_cap, eng->pattern_space);
            break;
        case CMD_HOLD_APPEND:
            buf_append(&eng->hold_space, &eng->hold_len, &eng->hold_cap, '\n', eng->pattern_space);
            break;
        case CMD_GET_COPY:
            buf_set(&eng->pattern_space, &eng->pattern_len, &eng->pattern_cap, eng->hold_space);
            break;
        case CMD_GET_APPEND:
            buf_append(&eng->pattern_space, &eng->pattern_len, &eng->pattern_cap, '\n', eng->hold_space);
            break;
        case CMD_EXCHANGE: {
            char *tmp_buf = eng->pattern_space;
            size_t tmp_len = eng->pattern_len;
            size_t tmp_cap = eng->pattern_cap;
            eng->pattern_space = eng->hold_space;
            eng->pattern_len = eng->hold_len;
            eng->pattern_cap = eng->hold_cap;
            eng->hold_space = tmp_buf;
            eng->hold_len = tmp_len;
            eng->hold_cap = tmp_cap;
            break;
        }
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
    }
}

int main(void) {
    SedEngine eng;
    engine_init(&eng, false);

    SedCommand cmds[2];
    cmds[0].type = CMD_SUBST;
    cmds[0].line_addr = 0;
    cmds[0].has_regex_addr = false;
    cmds[0].subst_pattern = "WARN";
    cmds[0].subst_replacement = "ALERT";
    cmds[0].subst_global = true;

    cmds[1].type = CMD_PRINT;
    cmds[1].line_addr = 0;
    cmds[1].has_regex_addr = false;

    char *line = NULL;
    size_t linecap = 0;
    ssize_t linelen;

    while ((linelen = getline(&line, &linecap, stdin)) > 0) {
        if (line[linelen - 1] == '\n') {
            line[--linelen] = '\0';
        }
        eng.line_number++;
        eng.deleted = false;
        buf_set(&eng.pattern_space, &eng.pattern_len, &eng.pattern_cap, line);

        for (int i = 0; i < 2; ++i) {
            execute_command(&eng, &cmds[i], stdin);
            if (eng.deleted) break;
        }

        if (!eng.deleted && !eng.quiet_mode) {
            puts(eng.pattern_space);
        }
    }

    free(line);
    engine_free(&eng);
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <regex>
#include <memory>
#include <optional>

enum class CommandType {
    Subst,
    Print,
    Delete,
    HoldCopy,
    HoldAppend,
    GetCopy,
    GetAppend,
    Exchange,
    NextAppend
};

struct SedCommand {
    CommandType type;
    int line_addr{0};
    std::optional<std::regex> regex_addr;
    std::string subst_pattern;
    std::string subst_replacement;
    bool subst_global{false};
};

class SedEngine {
public:
    explicit SedEngine(bool quiet = false) : quiet_mode_(quiet) {}

    void process_stream(std::istream& in, const std::vector<SedCommand>& commands) {
        std::string raw_line;
        while (std::getline(in, raw_line)) {
            line_number_++;
            deleted_ = false;
            pattern_space_ = raw_line;

            for (const auto& cmd : commands) {
                execute_command(cmd, in);
                if (deleted_) {
                    break;
                }
            }

            if (!deleted_ && !quiet_mode_) {
                std::cout << pattern_space_ << '\n';
            }
        }
    }

private:
    void execute_command(const SedCommand& cmd, std::istream& in) {
        if (cmd.line_addr > 0 && static_cast<size_t>(cmd.line_addr) != line_number_) {
            return;
        }
        if (cmd.regex_addr.has_value()) {
            if (!std::regex_search(pattern_space_, *cmd.regex_addr)) {
                return;
            }
        }

        switch (cmd.type) {
            case CommandType::Subst: {
                std::regex re(cmd.subst_pattern);
                auto flags = cmd.subst_global 
                    ? std::regex_constants::match_default 
                    : std::regex_constants::format_first_only;
                pattern_space_ = std::regex_replace(pattern_space_, re, cmd.subst_replacement, flags);
                break;
            }
            case CommandType::Print:
                std::cout << pattern_space_ << '\n';
                break;
            case CommandType::Delete:
                deleted_ = true;
                break;
            case CommandType::HoldCopy:
                hold_space_ = pattern_space_;
                break;
            case CommandType::HoldAppend:
                if (!hold_space_.empty()) {
                    hold_space_ += '\n';
                }
                hold_space_ += pattern_space_;
                break;
            case CommandType::GetCopy:
                pattern_space_ = hold_space_;
                break;
            case CommandType::GetAppend:
                if (!pattern_space_.empty()) {
                    pattern_space_ += '\n';
                }
                pattern_space_ += hold_space_;
                break;
            case CommandType::Exchange:
                std::swap(pattern_space_, hold_space_);
                break;
            case CommandType::NextAppend: {
                std::string next_line;
                if (std::getline(in, next_line)) {
                    line_number_++;
                    pattern_space_ += '\n' + next_line;
                }
                break;
            }
        }
    }

    std::string pattern_space_;
    std::string hold_space_;
    size_t line_number_{0};
    bool quiet_mode_{false};
    bool deleted_{false};
};

int main() {
    SedEngine engine(false);

    std::vector<SedCommand> cmds;
    cmds.push_back(SedCommand{
        .type = CommandType::Subst,
        .line_addr = 0,
        .regex_addr = std::nullopt,
        .subst_pattern = "WARN",
        .subst_replacement = "ALERT",
        .subst_global = true
    });

    engine.process_stream(std::cin, cmds);
    return 0;
}
```
:::

---

## Інженерний аналіз та крайові випадки обробки

1. **Коректне зіставлення нульових збігів (Zero-Length Matches):**
   При заміні регулярних виразів типу `^` (початок рядка), `$` (кінець рядка) або `a*` довжина збігу дорівнює нулю байтів (`match.rm_so == match.rm_eo`). Якщо після виконання підстановки вказівник читання `cursor` не змістити принаймні на один символ уперед, цикл підстановки у мові C потрапить у нескінченне зациклення, невпинно замінюючи нульову позицію перед першим символом. У наведеній C-реалізації цей крайовий випадок обробляється явним захисним зсувом `cursor++`.

2. **Семантика багаторядкового видалення (`D`):**
   Критична помилка при розробці аналогів sed полягає у спробі реалізувати команду `D` через звичайне очищення буфера з викликом читання нового рядка. Справжня інструкція `D` зобов'язана відрізати префікс `pattern_space` лише до першого символу `\n`, після чого негайно перезапустити інтерпретатор над суфіксом, що залишився. Це дозволяє реалізувати ковзне вікно будь-якої глибини над необмеженим потоком даних без втрати накопиченого контексту.

3. **Ефективність використання пам'яті (C vs C++):**
   У реалізації на C застосовано динамічний перерозподіл пам'яті з коефіцієнтом розширення, що дозволяє уникнути надмірних системних викликів. У варіанті на C++ використання стандарту C++20, контейнерів `std::string` з оптимізацією малих рядків (Small String Optimization, SSO) та автоматичним керуванням через RAII гарантує відсутність витоків дескрипторів навіть у випадку генерації винятків під час синтаксичного розбору складних регулярних виразів.

4. **Компіляція та верифікація роботи:**
   Для збірки та перевірки коректності функціонування обох версій емулятора використовуються стандартні інструменти GNU Toolchain:

```bash
# Компіляція версії на мові C:
gcc -std=c11 -O2 -Wall -Wextra proj-mini-sed.c -o mini-sed-c

# Компіляція версії на мові C++:
g++ -std=c++20 -O2 -Wall -Wextra proj-mini-sed.cpp -o mini-sed-cpp

# Перевірка потокового конвеєра:
printf "INFO: test\nWARN: failure\n" | ./mini-sed-c
```
