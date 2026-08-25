# ⚙️ Надійний потоковий парсер конфігурацій та записів

Цей практичний проект демонструє побудову відмовостійкого потокового процесора структурованих текстових даних (файлів конфігурацій, системних логів аудиту або потоків метрик моніторингу). У ньому реалізовано вирішення класичних системних проблем потокової обробки: захист від спотворення зворотних слешів, запобігання втраті провідних пробілів через роздільник полів `IFS`, коректне читання фінального рядка без завершального символу `\n`, запобігання витоку стану при роботі з подоболонками (subshells) та валідацію полів за допомогою регулярних виразів.

---

## 1. Постановка завдання та системні вимоги

Потоковий обробник отримує на вхід файл конфігурації або потік даних зі стандартного введення `stdin`, де кожен непорожній рядок описує мережевий вузол у форматі із роздільником «двокрапка»:
`service_name : ip_address : port : status`

### Ключові інженерні вимоги:
1. **Ігнорування службових рядків**: Усі коментарі (рядки, що починаються із символу `#`, можливо з попередніми пробілами) та повністю порожні рядки повинні відфільтровуватися на рівні парсера без створення зайвих дочірніх процесів.
2. **Очищення пробілів довкола роздільників**: Пробіли та знаки табуляції довкола символу двокрапки `:` мають бути видалені, проте пробіли всередині значень мають залишатися недоторканими.
3. **Строга валідація полів**:
   - `service_name` — дозволені лише літери латинського алфавіту, цифри, символи дефісу та підкреслення (`^[a-zA-Z0-9_-]+$`).
   - `ip_address` — коректна адреса протоколу IPv4, де кожне з чотирьох чисел перебуває в діапазоні від `0` до `255`.
   - `port` — ціле число у діапазоні від `1` до `65535`.
   - `status` — фіксоване значення зі списку дозволених станів: `ENABLED`, `DISABLED` або `MAINTENANCE`.
4. **Обробка потоку без завершального нового рядка**: Обробник зобов'язаний вичитати та валідувати фінальний рядок файлу навіть у тому випадку, якщо файл не закінчується символом переводу рядка `\n` (типова поведінка багатьох мережевих потоків і текстових редакторів).
5. **Збереження лічильників стану**: Підсумкова статистика (кількість оброблених, валідних та помилкових записів) повинна збиратися в основному процесі скрипту без втрати даних через ізоляцію адресної пам'яті субшелів.

---

## 2. Покроковий розбір архітектури парсера Bash

У сценарії Bash реалізовано комплекс інженерних рішень, що гарантують надійність обробки:

1. **Канонічний цикл читання**:
   Конструкція `while IFS= read -r raw_line || [ -n "$raw_line" ]` вирішує одразу три системні проблеми. По-перше, префікс `IFS=` очищає роздільник полів для вбудованої команди `read`, запобігаючи автоматичному відтинанню початкових відступів і пробілів. По-друге, опція `-r` перемикає читання в необроблений режим (raw mode), гарантуючи, що зворотні слеші `\` не будуть вилучені як символи екранування. По-третє, запобіжник `|| [ -n "$raw_line" ]` рятує останній рядок файлу, якщо той не містить кінцевого `\n`: системний виклик повертає статус `1` (EOF), але буфер містить рядок, який успішно передається в тіло циклу.

2. **Нативне очищення пробілів (Trim)**:
   Замість виклику зовнішніх важких утиліт `sed` або `awk`, які створюють новий процес на кожен рядок (`fork()` + `exec()`), застосовано вбудоване розгортання параметрів оболонки:
   - `${raw_line#"${raw_line%%[![:space:]]*}"}` — видаляє найдовший префікс із пробілів.
   - `${line%"${line##*[![:space:]]}"}` — видаляє найдовший суфікс із пробілів.
   Це пришвидшує обробку великих файлів у десятки разів, оскільки всі маніпуляції зі строковими буферами відбуваються в оперативній пам'яті самого процесу Bash.

3. **Розбір полів за роздільником без субшелу**:
   Команда `IFS=':' read -r name ip port status <<< "$line"` використовує конструкцію `here-string` (`<<<`). Вона розбиває очищений рядок на чотири змінні за символом двокрапки, не створюючи дочірнього процесу конвеєра.

4. **Пряме перенаправлення дескриптора файлу**:
   Конструкція `done < "$input_file"` перенаправляє файловий дескриптор `stdin` безпосередньо у вхідний потік циклу. Це критично відрізняється від антипатерну `cat "$input_file" | while ...`, де права частина пайпа породжує окрему подоболонку (subshell). У нашому варіанті лічильники `total_records`, `valid_records` та `invalid_records` змінюються в основному адресному просторі процесу і залишаються доступними після виходу з циклу.

```bash
#!/usr/bin/env bash
set -euo pipefail

# Лічильники стану основного процесу
total_records=0
valid_records=0
invalid_records=0

# Регулярні вирази для перевірки формату
readonly IP_REGEX='^([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$'
readonly NAME_REGEX='^[a-zA-Z0-9_-]+$'

# Функція валідації октету IPv4
validate_ip() {
    local ip="$1"
    if [[ "$ip" =~ $IP_REGEX ]]; then
        local o1="${BASH_REMATCH[1]}"
        local o2="${BASH_REMATCH[2]}"
        local o3="${BASH_REMATCH[3]}"
        local o4="${BASH_REMATCH[4]}"
        
        # Перевірка діапазону 0..255 для кожного октету
        if (( o1 <= 255 && o2 <= 255 && o3 <= 255 && o4 <= 255 )); then
            return 0
        fi
    fi
    return 1
}

# Обробка потоку даних
process_stream() {
    local input_file="${1:-/dev/stdin}"
    
    if [[ ! -r "$input_file" ]]; then
        printf "Помилка: файл '%s' недоступний для читання\n" "$input_file" >&2
        return 2
    fi

    # Канонічний патерн: IFS= захищає від обрізання пробілів, -r захищає від \
    # || [ -n "$line" ] рятує останній рядок без \n
    while IFS= read -r raw_line || [ -n "$raw_line" ]; do
        # 1. Нативне видалення початкових і кінцевих пробілів без виклику зовнішніх утиліт
        local line="${raw_line#"${raw_line%%[![:space:]]*}"}"
        line="${line%"${line##*[![:space:]]}"}"

        # 2. Фільтрація коментарів та порожніх рядків через оператор case
        case "$line" in
            ""|\#*)
                continue
                ;;
        esac

        (( total_records++ ))

        # 3. Розбір запису на окремі поля за роздільником ':'
        # Тимчасово перевизначаємо IFS для read без впливу на решту скрипту
        local name="" ip="" port="" status=""
        IFS=':' read -r name ip port status <<< "$line"

        # Очищення пробілів у кожному витягнутому полі
        name="${name#"${name%%[![:space:]]*}"}"
        name="${name%"${name##*[![:space:]]}"}"
        ip="${ip#"${ip%%[![:space:]]*}"}"
        ip="${ip%"${ip##*[![:space:]]}"}"
        port="${port#"${port%%[![:space:]]*}"}"
        port="${port%"${port##*[![:space:]]}"}"
        status="${status#"${status%%[![:space:]]*}"}"
        status="${status%"${status##*[![:space:]]}"}"

        # 4. Комплексна перевірка валідності полів
        local is_valid=1

        # Перевірка імені
        if [[ ! "$name" =~ $NAME_REGEX ]]; then
            is_valid=0
        fi

        # Перевірка IP-адреси
        if ! validate_ip "$ip"; then
            is_valid=0
        fi

        # Перевірка порту (1..65535)
        if ! [[ "$port" =~ ^[0-9]+$ ]] || (( port < 1 || port > 65535 )); then
            is_valid=0
        fi

        # Перевірка статусу через case
        case "$status" in
            ENABLED|DISABLED|MAINTENANCE)
                ;;
            *)
                is_valid=0
                ;;
        esac

        # 5. Вивід результату та оновлення статистики
        if (( is_valid == 1 )); then
            (( valid_records++ ))
            printf "[OK] Сервіс: %-15s | Адреса: %-15s:%-5d | Стан: %s\n" \
                "$name" "$ip" "$port" "$status"
        else
            (( invalid_records++ ))
            printf "[ПОМИЛКА] Некоректний запис: '%s'\n" "$raw_line" >&2
        fi

    # Перенаправлення вводу безпосередньо у цикл:
    # Змінні total_records/valid_records лишаються доступними після завершення циклу
    done < "$input_file"

    printf "\n=== Підсумок обробки ===\n"
    printf "Усього записів:   %d\n" "$total_records"
    printf "Валідних:         %d\n" "$valid_records"
    printf "Невалідних:       %d\n" "$invalid_records"
}

# Запуск з переданим аргументом або через стандартний потік
process_stream "${1:-/dev/stdin}"
```

---

## 3. Системний еквівалент на мовах C та C++

Для детального аналізу того, які саме низькорівневі операції виконуються ядром Linux та системними бібліотеками під час потокового читання файлу, нижче наведено дві повнофункціональні реалізації:
1. **Мова C**: використання POSIX-функції `getline(3)` для динамічного виділення рядкових буферів, потокобезпечної функції токенізації `strtok_r` та компіляції регулярних виразів `regcomp(3)`.
2. **Мова C++**: ідіоматичний системний код із застосуванням неблокуючих зрізів пам'яті `std::string_view`, швидкого перетворення чисел `std::from_chars` (без накладних витрат на локалі `locale`) та автоматичного закриття дескрипторів за принципом RAII.

### Порівняння системних викликів та профілю пам'яті

* **Буферизація введення-виведення**: У варіанті на C функція `getline()` використовує внутрішній буфер стандартної бібліотеки libc розміром 4 КБ або 8 КБ. Вона зчитує дані великими блоками через системний виклик `read(2)`, мінімізуючи перемикання контексту між простором користувача та ядром. На відміну від неї, вбудована команда Bash `read` при читанні з небуферизованого пайпа змушена читати потік по одному байту за раз, щоб не вичитати зайві дані, призначені для наступних команд конвеєра.
* **Управління динамічною пам'яттю**: `getline()` автоматично перевиділяє буфер пам'яті через `realloc()` у разі виявлення рядка довільної довжини, запобігаючи переповненню буфера. У варіанті на C++ об'єкт `std::string` та легковажні зрізи пам'яті `std::string_view` дозволяють аналізувати підрядки без жодного додаткового виділення динамічної пам'яті у купі (zero-allocation parsing).

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <regex.h>
#include <stdbool.h>

static char *trim_whitespace(char *str) {
    while (isspace((unsigned char)*str)) str++;
    if (*str == 0) return str;
    char *end = str + strlen(str) - 1;
    while (end > str && isspace((unsigned char)*end)) end--;
    end[1] = '\0';
    return str;
}

static bool validate_ipv4(const char *ip_str) {
    int o1, o2, o3, o4;
    char extra;
    if (sscanf(ip_str, "%d.%d.%d.%d%c", &o1, &o2, &o3, &o4, &extra) != 4) {
        return false;
    }
    return (o1 >= 0 && o1 <= 255) &&
           (o2 >= 0 && o2 <= 255) &&
           (o3 >= 0 && o3 <= 255) &&
           (o4 >= 0 && o4 <= 255);
}

int main(int argc, char *argv[]) {
    const char *filepath = (argc > 1) ? argv[1] : "/dev/stdin";
    FILE *fp = fopen(filepath, "r");
    if (!fp) {
        perror("fopen");
        return 1;
    }

    regex_t name_regex;
    if (regcomp(&name_regex, "^[a-zA-Z0-9_-]+$", REG_EXTENDED | REG_NOSUB) != 0) {
        fprintf(stderr, "Помилка компіляції регулярного виразу\n");
        fclose(fp);
        return 1;
    }

    char *line = NULL;
    size_t len = 0;
    ssize_t nread;
    int total = 0, valid = 0, invalid = 0;

    /* getline автоматично виділяє пам'ять та зчитує рядок до \n або EOF */
    while ((nread = getline(&line, &len, fp)) != -1) {
        /* Видалення завершального переходу рядка */
        if (nread > 0 && line[nread - 1] == '\n') {
            line[nread - 1] = '\0';
        }

        char *trimmed = trim_whitespace(line);
        if (*trimmed == '\0' || *trimmed == '#') {
            continue;
        }

        total++;

        /* Розбиття на поля за двокрапкою за допомогою безпечної функції strtok_r */
        char *saveptr;
        char *name_token   = strtok_r(trimmed, ":", &saveptr);
        char *ip_token     = strtok_r(NULL, ":", &saveptr);
        char *port_token   = strtok_r(NULL, ":", &saveptr);
        char *status_token = strtok_r(NULL, ":", &saveptr);

        if (!name_token || !ip_token || !port_token || !status_token) {
            invalid++;
            fprintf(stderr, "[ПОМИЛКА] Неповний запис: '%s'\n", line);
            continue;
        }

        char *name   = trim_whitespace(name_token);
        char *ip     = trim_whitespace(ip_token);
        char *port_s = trim_whitespace(port_token);
        char *status = trim_whitespace(status_token);

        bool is_valid = true;

        /* Перевірка імені через POSIX regex */
        if (regexec(&name_regex, name, 0, NULL, 0) != 0) is_valid = false;

        /* Перевірка октетів IP-адреси */
        if (!validate_ipv4(ip)) is_valid = false;

        /* Перевірка діапазону порту */
        int port = atoi(port_s);
        if (port < 1 || port > 65535) is_valid = false;

        /* Перевірка дозволених статусів */
        if (strcmp(status, "ENABLED") != 0 &&
            strcmp(status, "DISABLED") != 0 &&
            strcmp(status, "MAINTENANCE") != 0) {
            is_valid = false;
        }

        if (is_valid) {
            valid++;
            printf("[OK] Сервіс: %-15s | Адреса: %-15s:%-5d | Стан: %s\n",
                   name, ip, port, status);
        } else {
            invalid++;
            fprintf(stderr, "[ПОМИЛКА] Невалідні дані: '%s'\n", line);
        }
    }

    free(line);
    regfree(&name_regex);
    fclose(fp);

    printf("\n=== Підсумок обробки ===\n");
    printf("Усього: %d, Валідних: %d, Невалідних: %d\n", total, valid, invalid);
    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <regex>
#include <charconv>

namespace {

// Очищення пробілів через створення підрядка без копіювання пам'яті
std::string_view trim(std::string_view sv) {
    const auto start = sv.find_first_not_of(" \t\r\n");
    if (start == std::string_view::npos) return {};
    const auto end = sv.find_last_not_of(" \t\r\n");
    return sv.substr(start, end - start + 1);
}

// Розбиття рядка за роздільником без алокації динамічної пам'яті під токени
std::vector<std::string_view> split(std::string_view sv, char delim) {
    std::vector<std::string_view> tokens;
    size_t pos = 0;
    while (pos < sv.size()) {
        const auto next = sv.find(delim, pos);
        if (next == std::string_view::npos) {
            tokens.push_back(sv.substr(pos));
            break;
        }
        tokens.push_back(sv.substr(pos, next - pos));
        pos = next + 1;
    }
    return tokens;
}

// Швидка валідація IPv4 через std::from_chars без виклику regex
bool validate_ipv4(std::string_view ip) {
    const auto octets = split(ip, '.');
    if (octets.size() != 4) return false;

    for (const auto& octet_sv : octets) {
        if (octet_sv.empty() || octet_sv.size() > 3) return false;
        int val = 0;
        const auto [ptr, ec] = std::from_chars(octet_sv.data(), octet_sv.data() + octet_sv.size(), val);
        if (ec != std::errc{} || ptr != octet_sv.data() + octet_sv.size() || val < 0 || val > 255) {
            return false;
        }
    }
    return true;
}

} // namespace

int main(int argc, char* argv[]) {
    const std::string filename = (argc > 1) ? argv[1] : "";
    std::ifstream file_stream;
    std::istream* input = &std::cin;

    // Автоматичне керування життєвим циклом файлового потоку (RAII)
    if (!filename.empty() && filename != "-") {
        file_stream.open(filename);
        if (!file_stream) {
            std::cerr << "Помилка відкриття файлу: " << filename << '\n';
            return 1;
        }
        input = &file_stream;
    }

    const std::regex name_regex("^[a-zA-Z0-9_-]+$");
    int total = 0, valid = 0, invalid = 0;
    std::string line;

    // std::getline безпечно зчитує потік рядок за рядком до символу \n або EOF
    while (std::getline(*input, line)) {
        std::string_view sv = trim(line);
        if (sv.empty() || sv.front() == '#') {
            continue;
        }

        total++;
        const auto parts = split(sv, ':');
        if (parts.size() != 4) {
            invalid++;
            std::cerr << "[ПОМИЛКА] Некоректна кількість полів: '" << line << "'\n";
            continue;
        }

        const auto name   = trim(parts[0]);
        const auto ip     = trim(parts[1]);
        const auto port_s = trim(parts[2]);
        const auto status = trim(parts[3]);

        bool is_valid = true;

        // Перевірка імені регулярним виразом
        if (!std::regex_match(name.begin(), name.end(), name_regex)) {
            is_valid = false;
        }

        // Перевірка октетів IP-адреси
        if (!validate_ipv4(ip)) {
            is_valid = false;
        }

        // Перевірка числового значення порту через std::from_chars
        int port = 0;
        const auto [ptr, ec] = std::from_chars(port_s.data(), port_s.data() + port_s.size(), port);
        if (ec != std::errc{} || ptr != port_s.data() + port_s.size() || port < 1 || port > 65535) {
            is_valid = false;
        }

        // Перевірка дозволених статусів
        if (status != "ENABLED" && status != "DISABLED" && status != "MAINTENANCE") {
            is_valid = false;
        }

        if (is_valid) {
            valid++;
            std::cout << "[OK] Сервіс: " << name
                      << " | Адреса: " << ip << ':' << port
                      << " | Стан: " << status << '\n';
        } else {
            invalid++;
            std::cerr << "[ПОМИЛКА] Невалідні дані запису: '" << line << "'\n";
        }
    }

    std::cout << "\n=== Підсумок обробки ===\n";
    std::cout << "Усього: " << total << ", Валідних: " << valid << ", Невалідних: " << invalid << '\n';
    return 0;
}
```
:::
