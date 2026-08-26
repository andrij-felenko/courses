# ⚙️ Практична реалізація регулярних виразів: POSIX C API та RAII-обгортка в C++

Робота з регулярними виразами на системному рівні вимагає суворого контролю за виділенням пам'яті, часом компіляції шаблонів та коректною адресацією захоплених груп. У високорівневих мовах програмування компіляція шаблону та його виконання часто приховані за єдиним викликом функції, що маскує витрати на виділення динамічної пам'яті. У системному програмуванні на C та C++ розуміння розділення життєвого циклу регулярного виразу на етап компіляції та етап зіставлення є ключем до побудови високопродуктивних і безпечних парсерів.

Стандартний системний заголовок POSIX `<regex.h>` надає прямий інтерфейс до автоматного рушія операційної системи. Нижче розглянуто поетапний процес роботи з цим інтерфейсом, побудову безпечної RAII-обгортки сучасною мовою C++20, вимірювання продуктивності та захист від атак типу «Відмова в обслуговуванні» (ReDoS).

## Життєвий цикл регулярного виразу та адресація груп

Життєвий цикл регулярного виразу в POSIX C API складається з трьох обов'язкових фаз:

1. **Фаза компіляції (`regcomp`):** текстовий рядок шаблону перетворюється на внутрішній граф переходів скінченного автомата. Структура `regex_t` виділяє внутрішні таблиці станів у динамічній пам'яті. Оскільки вартість компіляції виразу в сотні разів перевищує вартість зіставлення з одним коротким рядком, скомпільований об'єкт `regex_t` створюється один раз під час ініціалізації модуля і використовується повторно для всіх наступних перевірок.
2. **Фаза зіставлення (`regexec`):** скомпільований автомат зчитує цільовий рядок і знаходить межі відповідності шаблону. Якщо вираз містить круглі дужки для виділення підгруп, функція заповнює переданий користувачем масив структур `regmatch_t`.
3. **Фаза звільнення ресурсів (`regfree`):** очищає внутрішні динамічні таблиці автомата. Якщо програма перезаписує змінну `regex_t` новим викликом `regcomp` без попереднього виклику `regfree`, виникає безповоротний витік системної пам'яті.

Масив `regmatch_t` адресизує підрядки за допомогою двох цілочисельних полів типу `regoff_t`:
- `rm_so` (*start offset*) — байтове зміщення першого символу збігу від початку вхідного рядка;
- `rm_eo` (*end offset*) — байтове зміщення позиції одразу за останнім символом збігу.

Довжина знайденого фрагмента в байтах обчислюється як різниця `rm_eo - rm_so`. Нульовий елемент `matches[0]` завжди відповідає збігу всього виразу, а елементи `matches[1]`..`matches[N-1]` відповідають послідовним відкриваючим круглим дужкам у виразі зліва направо. Якщо певна група не брала участі у збігу (наприклад, перебувала у невибраній гілці чергування `(a)|(b)`), її поля `rm_so` та `rm_eo` встановлюються у значення `-1`.

Нижче наведено повноцінний приклад розбору записів системних журналів за шаблоном `^([A-Z]+) \[([0-9]{4}-[0-9]{2}-[0-9]{2})\] (.+)$` мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <regex.h>

#define MAX_GROUPS 4

void parse_log_line(const char *pattern, const char *line) {
    regex_t regex;
    regmatch_t matches[MAX_GROUPS];
    char err_buf[256];

    /* Компіляція розширеного регулярного виразу (ERE) */
    int ret = regcomp(&regex, pattern, REG_EXTENDED);
    if (ret != 0) {
        regerror(ret, &regex, err_buf, sizeof(err_buf));
        fprintf(stderr, "Помилка компіляції виразу: %s\n", err_buf);
        return;
    }

    /* Виконання зіставлення з вхідним рядком */
    ret = regexec(&regex, line, MAX_GROUPS, matches, 0);
    if (ret == 0) {
        printf("Збіг знайдено для рядка: %s\n", line);
        for (int i = 0; i < MAX_GROUPS; i++) {
            if (matches[i].rm_so == -1) {
                printf("  Група %d: [не брала участі у збігу]\n", i);
                continue;
            }
            int len = matches[i].rm_eo - matches[i].rm_so;
            printf("  Група %d: %.*s (байти %d..%d)\n",
                   i, len, line + matches[i].rm_so,
                   (int)matches[i].rm_so, (int)matches[i].rm_eo);
        }
    } else if (ret == REG_NOMATCH) {
        printf("Збігу немає для рядка: %s\n", line);
    } else {
        regerror(ret, &regex, err_buf, sizeof(err_buf));
        fprintf(stderr, "Помилка виконання regexec: %s\n", err_buf);
    }

    /* Обов'язкове звільнення внутрішніх таблиць автомата */
    regfree(&regex);
}

int main(void) {
    const char *pattern = "^([A-Z]+) \\[([0-9]{4}-[0-9]{2}-[0-9]{2})\\] (.+)$";
    const char *log1 = "ERROR [2026-08-26] Disk array degraded on node-04";
    const char *log2 = "invalid line format";

    parse_log_line(pattern, log1);
    parse_log_line(pattern, log2);
    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <vector>
#include <memory>
#include <stdexcept>
#include <regex.h>

// Безпечна RAII-обгортка для керування ресурсами regex_t у C++20
class PosixRegex {
public:
    explicit PosixRegex(std::string_view pattern, int flags = REG_EXTENDED) {
        // POSIX C API вимагає нуль-термінованого рядка
        std::string null_terminated_pat(pattern);
        int ret = regcomp(&regex_, null_terminated_pat.c_str(), flags);
        if (ret != 0) {
            char err_buf[256];
            regerror(ret, &regex_, err_buf, sizeof(err_buf));
            throw std::runtime_error(std::string("Помилка компіляції regex: ") + err_buf);
        }
    }

    ~PosixRegex() noexcept {
        regfree(&regex_);
    }

    // Заборона копіювання для запобігання подвійному виклику regfree
    PosixRegex(const PosixRegex&) = delete;
    PosixRegex& operator=(const PosixRegex&) = delete;

    // Дозвіл семантики переміщення
    PosixRegex(PosixRegex&& other) noexcept {
        regex_ = other.regex_;
        other.regex_ = {};
    }

    PosixRegex& operator=(PosixRegex&& other) noexcept {
        if (this != &other) {
            regfree(&regex_);
            regex_ = other.regex_;
            other.regex_ = {};
        }
        return *this;
    }

    // Пошук з поверненням легких зрізів std::string_view без зайвих копіювань
    std::vector<std::string_view> match(std::string_view text, size_t max_groups = 8) const {
        std::vector<regmatch_t> pmatch(max_groups);
        std::string null_terminated_text(text);

        int ret = regexec(&regex_, null_terminated_text.c_str(), max_groups, pmatch.data(), 0);
        if (ret == REG_NOMATCH) {
            return {};
        }
        if (ret != 0) {
            char err_buf[256];
            regerror(ret, &regex_, err_buf, sizeof(err_buf));
            throw std::runtime_error(std::string("Помилка виконання regex: ") + err_buf);
        }

        std::vector<std::string_view> results;
        results.reserve(max_groups);

        for (size_t i = 0; i < max_groups; ++i) {
            if (pmatch[i].rm_so == -1) {
                results.emplace_back(""); // Група не брала участі у збігу
            } else {
                size_t start = static_cast<size_t>(pmatch[i].rm_so);
                size_t len = static_cast<size_t>(pmatch[i].rm_eo - pmatch[i].rm_so);
                results.emplace_back(text.substr(start, len));
            }
        }
        return results;
    }

private:
    regex_t regex_{};
};

int main() {
    try {
        PosixRegex re("^([A-Z]+) \\[([0-9]{4}-[0-9]{2}-[0-9]{2})\\] (.+)$");
        std::string_view log1 = "ERROR [2026-08-26] Disk array degraded on node-04";

        auto groups = re.match(log1, 4);
        if (!groups.empty()) {
            std::cout << "Повний збіг: " << groups[0] << "\n";
            std::cout << "Рівень: " << groups[1] << "\n";
            std::cout << "Дата: " << groups[2] << "\n";
            std::cout << "Повідомлення: " << groups[3] << "\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
    }
    return 0;
}
```
:::

## Стійкість до ReDoS: лінійні автомати проти бектрекінгу з таймаутом

При обробці вхідних даних від зовнішніх клієнтів (веб-форми, заголовки HTTP-пакетів, конфігураційні файли) вибір рушія регулярних виразів є критичним фактором кібербезпеки.

Якщо в системі використовується рушій із поверненням (наприклад, стандартний `std::regex` у C++ або рушії Python/JavaScript), шаблон із вкладеними квантифікаторами виду `^(a+)+$` спричиняє експоненційний перебір гілок при отриманні рядка `"aaaa...!"`. На кожному кроці невідповідності кінцевого знака `!` рушій повертається назад і перебирає всі можливі варіанти розбиття символів `'a'` між зовнішнім і внутрішнім квантифікаторами, що вимагає `2^(N-1)` ітерацій. Для рядка довжиною 30 символів це понад 536 мільйонів рекурсивних викликів.

На відміну від бектрекінгу, автоматний рушій POSIX `regexec` будує недетермінований або детермінований автомат Томпсона і паралельно відстежує множину активних станів, гарантуючи завершення за час `O(N)` незалежно від структури виразу.

У наведеному нижче прикладі порівнюється поведінка автоматного виклику на C та механізм захисту від зависання через асинхронний таймаут у C++.

:::tabs
```c
#include <stdio.h>
#include <time.h>
#include <regex.h>

/* Безпечний лінійний виклик: автомат POSIX гарантує лінійний час виконання O(N) */
int match_linear_safe(const char *pattern, const char *input) {
    regex_t reg;
    clock_t start = clock();

    if (regcomp(&reg, pattern, REG_EXTENDED | REG_NOSUB) != 0) {
        return -1;
    }

    int res = regexec(&reg, input, 0, NULL, 0);
    regfree(&reg);

    clock_t end = clock();
    double cpu_ms = ((double)(end - start)) / CLOCKS_PER_SEC * 1000.0;
    printf("POSIX лінійний час виконання: %.4f мс (результат: %s)\n",
           cpu_ms, res == 0 ? "MATCH" : "NO MATCH");
    return res == 0;
}

int main(void) {
    /* Небезпечний вираз із вкладеним квантифікатором */
    const char *redos_pattern = "^(a+)+$";
    /* Рядок, що провокує експоненційний перебір гілок */
    const char *evil_input = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!";

    printf("Перевірка вразливого виразу через лінійний автомат POSIX:\n");
    match_linear_safe(redos_pattern, evil_input);
    return 0;
}
```
```cpp
#include <iostream>
#include <chrono>
#include <string>
#include <string_view>
#include <future>
#include <regex>

// Захист від зависання бектрекінг-рушія шляхом контролю таймауту в C++
bool match_with_timeout(std::string_view pattern_str, std::string_view input_str,
                        std::chrono::milliseconds timeout) {
    std::string pat(pattern_str);
    std::string text(input_str);

    // Запуск зіставлення в окремому асинхронному потоці
    auto task = std::async(std::launch::async, [pat, text]() {
        try {
            std::regex re(pat, std::regex::ECMAScript);
            return std::regex_match(text, re);
        } catch (const std::exception&) {
            return false;
        }
    });

    std::chrono::steady_clock::time_point start = std::chrono::steady_clock::now();
    std::future_status status = task.wait_for(timeout);

    if (status == std::future_status::ready) {
        auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(
            std::chrono::steady_clock::now() - start).count();
        std::cout << "std::regex завершився за " << elapsed << " мкс\n";
        return task.get();
    } else {
        std::cout << "УВАГА: Спрацював таймаут! Виявлено катастрофічний бектрекінг (ReDoS).\n";
        return false;
    }
}

int main() {
    std::string_view redos_pattern = "^(a+)+$";
    std::string_view evil_input = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!";

    std::cout << "Тестування std::regex під захисним таймаутом 200 мс:\n";
    match_with_timeout(redos_pattern, evil_input, std::chrono::milliseconds(200));
    return 0;
}
```
:::

## Інженерні правила та аналіз типових помилок

1. **Керування пам'яттю та RAII-інваріанти:**
   У чистому C функція `regcomp` алокує структури даних у внутрішніх полях `regex_t`. Виклик `regfree` повинен відбуватися на кожному шляху виходу з функції, включаючи блоки обробки помилок. У C++ обгортка завжди повинна реалізовувати правило п'яти (*Rule of 5*): забороняти конструктор копіювання і копіююче присвоєння (або виконувати глибоку рекомпіляцію) та явно реалізовувати переміщення (*move semantics*), щоб уникнути виклику `regfree` над чужим вказівником.

2. **Нуль-термінація та безпека меж буфера:**
   Інтерфейси POSIX `<regex.h>` розроблені для традиційних C-рядків і очікують обов'язкового кінцевого байта `\0`. Передача вказівника на внутрішній буфер `std::string_view` або масиву байтів без кінцевого нуля призводить до читання неініціалізованої пам'яті (*out-of-bounds read*). Перед викликом `regcomp` або `regexec` рядок необхідно гарантовано нуль-термінувати.

3. **Багатопоточність та реентрабельність:**
   Структура `regex_t` після завершення компіляції є константною та потокобезпечною: декілька паралельних потоків виконання можуть одночасно викликати `regexec` з тим самим об'єктом `regex_t`, за умови, що кожен потік передає власний незалежний масив `pmatch`. Проте виклики `regcomp` та `regfree` над одним і тим самим об'єктом не є потокобезпечними і вимагають синхронізації м'ютексом.

4. **Розмір масиву зіставлень `pmatch`:**
   Кількість елементів у масиві `pmatch` повинна дорівнювати кількості очікуваних підгруп плюс один (для нульової групи повного збігу). Якщо передати `nmatch = 0` та `pmatch = NULL`, функція `regexec` виконає перевірку значно швидше, оскільки рушію не потрібно обчислювати та зберігати точні індекси меж підрядків у пам'яті.
