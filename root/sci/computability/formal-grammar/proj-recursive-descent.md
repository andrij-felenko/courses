# ⚙️ Синтаксичний аналізатор арифметичних виразів: рекурсивний спуск на основі BNF

Синтаксичний аналіз (парсинг) перетворює плоский одномірний потік лексем на структуроване ієрархічне дерево або безпосередній обчислений результат. Серед усіх методів ручної побудови компіляторів та інтерпретаторів найпопулярнішим, найшвидшим та найбільш підтримуваним є **метод рекурсивного спуску** (англ. *recursive descent parsing*).

Архітектура рекурсивного спуску прямо й однозначно відображає правила форми Бекуса–Наура (BNF) у вихідний код програми:
- Кожен нетермінальний символ граматики стає окремою функцією (процедурою) у коді.
- Входження іншого нетермінала в тілі правила перетворюється на виклик відповідної підпрограми.
- Альтернативи через вертикальну риску `|` реалізуються через умовні оператори `if` або `switch`, які аналізують поточний символ вхідного потоку (lookahead token).
- Повторення `{...}` у нотації EBNF трансформуються в цикли `while`.

## Граматика арифметичних виразів без лівої рекурсії

Класична математична граматика арифметичних виразів із пріоритетом операцій у теоретичному вигляді містить ліву рекурсію (`E → E + T`). Якщо таку граматику закодувати буквально:

:::tabs
```c
double parse_expr(void) {
    double left = parse_expr(); /* Негайний рекурсивний виклик до читання токена */
    /* ... */
    return left;
}
```
```cpp
double parse_expr() {
    double left = parse_expr(); // Негайний рекурсивний виклик до читання токена
    // ...
    return left;
}
```
:::

функція викличе саму себе до зчитування першого токена з входу, що спричинить миттєве нескінченне зациклення та переповнення стека (stack overflow).

Щоб зробити граматику придатною для детермінованого низхідного парсера класу `LL(1)`, ліву рекурсію усувають, перетворюючи правила на ітеративну форму Бекуса–Наура (EBNF):

```bnf
<Expr>   ::= <Term> { ("+" | "-") <Term> }
<Term>   ::= <Factor> { ("*" | "/") <Factor> }
<Factor> ::= <Number> | "(" <Expr> ")" | "-" <Factor>
<Number> ::= [0-9]+ ( "." [0-9]+ )?
```

### Рівні синтаксичної ієрархії

Ця граматика будує три чіткі рівні пріоритету:
1. `<Expr>` (Вираз) відповідає за операції додавання та віднімання, які мають найнижчий пріоритет.
2. `<Term>` (Терм / Доданок) відповідає за множення та ділення, які мають вищий пріоритет.
3. `<Factor>` (Фактор / Множник) відповідає за неподільні атомарні величини (числа), унарний мінус та вирази у круглих дужках, які мають найвищий пріоритет.

Оскільки функція `parse_expr` спочатку викликає `parse_term`, а та, своєю чергою, викликає `parse_factor`, вузли множення утворюються глибше на стеку викликів. Це гарантує, що операція `*` буде виконана раніше за `+`, що відповідає стандартній математичній семантиці.

## Повна реалізація аналізатора та інтерпретатора

Нижче наведено дві повноцінні, автономні реалізації парсера арифметичних виразів: мовою C та ідіоматичною мовою C++23. Програма виконує лексичний аналіз, будує виведення за правилами BNF, обчислює результат та забезпечує детальну діагностику синтаксичних і семантичних помилок (непарні дужки, неочікувані символи, ділення на нуль).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <stdbool.h>

typedef enum {
    TOK_EOF = 0,
    TOK_NUMBER,
    TOK_PLUS,
    TOK_MINUS,
    TOK_STAR,
    TOK_SLASH,
    TOK_LPAREN,
    TOK_RPAREN,
    TOK_ERROR
} TokenType;

typedef struct {
    TokenType type;
    double value;
} Token;

typedef struct {
    const char *src;
    size_t pos;
    Token current;
    bool has_error;
    char error_msg[128];
} Parser;

/* Лексичний сканер (зчитування наступного неподільного токена) */
static void next_token(Parser *p) {
    while (p->src[p->pos] && isspace((unsigned char)p->src[p->pos])) {
        p->pos++;
    }

    char c = p->src[p->pos];
    if (c == '\0') {
        p->current.type = TOK_EOF;
        return;
    }

    if (isdigit((unsigned char)c) || c == '.') {
        char *end_ptr = NULL;
        p->current.value = strtod(&p->src[p->pos], &end_ptr);
        p->current.type = TOK_NUMBER;
        p->pos = (size_t)(end_ptr - p->src);
        return;
    }

    p->pos++;
    switch (c) {
        case '+': p->current.type = TOK_PLUS; break;
        case '-': p->current.type = TOK_MINUS; break;
        case '*': p->current.type = TOK_STAR; break;
        case '/': p->current.type = TOK_SLASH; break;
        case '(': p->current.type = TOK_LPAREN; break;
        case ')': p->current.type = TOK_RPAREN; break;
        default:
            p->current.type = TOK_ERROR;
            p->has_error = true;
            snprintf(p->error_msg, sizeof(p->error_msg), "Невідомий символ у позиції %zu: '%c'", p->pos, c);
            break;
    }
}

static void parser_init(Parser *p, const char *src) {
    p->src = src;
    p->pos = 0;
    p->has_error = false;
    p->error_msg[0] = '\0';
    next_token(p);
}

static double parse_expr(Parser *p);

/* <Factor> ::= <Number> | "(" <Expr> ")" | "-" <Factor> */
static double parse_factor(Parser *p) {
    if (p->has_error) return 0.0;

    /* Обробка унарного мінуса */
    if (p->current.type == TOK_MINUS) {
        next_token(p);
        return -parse_factor(p);
    }

    /* Числовий термінал */
    if (p->current.type == TOK_NUMBER) {
        double val = p->current.value;
        next_token(p);
        return val;
    }

    /* Вкладений вираз у дужках */
    if (p->current.type == TOK_LPAREN) {
        next_token(p);
        double val = parse_expr(p);
        if (p->current.type != TOK_RPAREN) {
            p->has_error = true;
            snprintf(p->error_msg, sizeof(p->error_msg), "Синтаксична помилка: очікувалася закриваюча дужка ')'");
            return 0.0;
        }
        next_token(p);
        return val;
    }

    p->has_error = true;
    snprintf(p->error_msg, sizeof(p->error_msg), "Синтаксична помилка: очікувалося число або '('");
    return 0.0;
}

/* <Term> ::= <Factor> { ("*" | "/") <Factor> } */
static double parse_term(Parser *p) {
    double left = parse_factor(p);

    while (!p->has_error && (p->current.type == TOK_STAR || p->current.type == TOK_SLASH)) {
        TokenType op = p->current.type;
        next_token(p);
        double right = parse_factor(p);

        if (op == TOK_STAR) {
            left *= right;
        } else {
            if (right == 0.0) {
                p->has_error = true;
                snprintf(p->error_msg, sizeof(p->error_msg), "Арифметична помилка: ділення на нуль");
                return 0.0;
            }
            left /= right;
        }
    }
    return left;
}

/* <Expr> ::= <Term> { ("+" | "-") <Term> } */
static double parse_expr(Parser *p) {
    double left = parse_term(p);

    while (!p->has_error && (p->current.type == TOK_PLUS || p->current.type == TOK_MINUS)) {
        TokenType op = p->current.type;
        next_token(p);
        double right = parse_term(p);

        if (op == TOK_PLUS) {
            left += right;
        } else {
            left -= right;
        }
    }
    return left;
}

int main(void) {
    const char *test_cases[] = {
        "3 + 4 * 2",
        "(3 + 4) * 2",
        "100 / (2 + 3) * 4 - 5",
        "-5 * (2 + 3)",
        "3 + (4 * 2",         /* помилка: відсутня дужка */
        "10 / 0",              /* помилка: ділення на нуль */
        "42 abc"               /* помилка: зайві символи в кінці */
    };

    for (size_t i = 0; i < sizeof(test_cases) / sizeof(test_cases[0]); ++i) {
        Parser p;
        parser_init(&p, test_cases[i]);
        double result = parse_expr(&p);

        if (!p.has_error && p.current.type == TOK_EOF) {
            printf("[УСПІХ]   \"%s\" = %.6g\n", test_cases[i], result);
        } else {
            printf("[ПОМИЛКА] \"%s\" -> %s\n", test_cases[i], 
                   p.has_error ? p.error_msg : "Неочікувані символи після виразу");
        }
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <charconv>
#include <cctype>
#include <expected>
#include <string>
#include <vector>

enum class TokenType {
    Eof,
    Number,
    Plus,
    Minus,
    Star,
    Slash,
    LParen,
    RParen
};

struct Token {
    TokenType type{TokenType::Eof};
    double value{0.0};
};

class ArithmeticParser {
public:
    explicit ArithmeticParser(std::string_view input) : src_(input) {
        advance();
    }

    std::expected<double, std::string> parse() {
        auto result = parse_expr();
        if (!result) {
            return result;
        }
        if (current_.type != TokenType::Eof) {
            return std::unexpected("Синтаксична помилка: зайві символи після завершення коректного виразу");
        }
        return result;
    }

private:
    std::string_view src_;
    size_t pos_{0};
    Token current_;

    void advance() {
        while (pos_ < src_.size() && std::isspace(static_cast<unsigned char>(src_[pos_]))) {
            pos_++;
        }

        if (pos_ >= src_.size()) {
            current_ = Token{TokenType::Eof, 0.0};
            return;
        }

        char c = src_[pos_];
        if (std::isdigit(static_cast<unsigned char>(c)) || c == '.') {
            const char* start = src_.data() + pos_;
            const char* end = src_.data() + src_.size();
            double val = 0.0;
            auto [ptr, ec] = std::from_chars(start, end, val);
            if (ec == std::errc{}) {
                pos_ += static_cast<size_t>(ptr - start);
                current_ = Token{TokenType::Number, val};
                return;
            }
        }

        pos_++;
        switch (c) {
            case '+': current_ = Token{TokenType::Plus, 0.0}; break;
            case '-': current_ = Token{TokenType::Minus, 0.0}; break;
            case '*': current_ = Token{TokenType::Star, 0.0}; break;
            case '/': current_ = Token{TokenType::Slash, 0.0}; break;
            case '(': current_ = Token{TokenType::LParen, 0.0}; break;
            case ')': current_ = Token{TokenType::RParen, 0.0}; break;
            default:
                current_ = Token{TokenType::Eof, 0.0};
                break;
        }
    }

    // <Factor> ::= <Number> | "(" <Expr> ")" | "-" <Factor>
    std::expected<double, std::string> parse_factor() {
        if (current_.type == TokenType::Minus) {
            advance();
            auto res = parse_factor();
            if (!res) return res;
            return -(*res);
        }

        if (current_.type == TokenType::Number) {
            double val = current_.value;
            advance();
            return val;
        }

        if (current_.type == TokenType::LParen) {
            advance();
            auto expr_res = parse_expr();
            if (!expr_res) return expr_res;

            if (current_.type != TokenType::RParen) {
                return std::unexpected("Синтаксична помилка: очікувалася закриваюча дужка ')'");
            }
            advance();
            return expr_res;
        }

        return std::unexpected("Синтаксична помилка: очікувалося число або '('");
    }

    // <Term> ::= <Factor> { ("*" | "/") <Factor> }
    std::expected<double, std::string> parse_term() {
        auto left_res = parse_factor();
        if (!left_res) return left_res;
        double left = *left_res;

        while (current_.type == TokenType::Star || current_.type == TokenType::Slash) {
            TokenType op = current_.type;
            advance();
            auto right_res = parse_factor();
            if (!right_res) return right_res;
            double right = *right_res;

            if (op == TokenType::Star) {
                left *= right;
            } else {
                if (right == 0.0) {
                    return std::unexpected("Арифметична помилка: ділення на нуль");
                }
                left /= right;
            }
        }
        return left;
    }

    // <Expr> ::= <Term> { ("+" | "-") <Term> }
    std::expected<double, std::string> parse_expr() {
        auto left_res = parse_term();
        if (!left_res) return left_res;
        double left = *left_res;

        while (current_.type == TokenType::Plus || current_.type == TokenType::Minus) {
            TokenType op = current_.type;
            advance();
            auto right_res = parse_term();
            if (!right_res) return right_res;
            double right = *right_res;

            if (op == TokenType::Plus) {
                left += right;
            } else {
                left -= right;
            }
        }
        return left;
    }
};

int main() {
    const std::vector<std::string_view> test_cases = {
        "3 + 4 * 2",
        "(3 + 4) * 2",
        "100 / (2 + 3) * 4 - 5",
        "-5 * (2 + 3)",
        "3 + (4 * 2",
        "10 / 0",
        "42 abc"
    };

    for (const auto& expr : test_cases) {
        ArithmeticParser parser(expr);
        auto result = parser.parse();
        if (result) {
            std::cout << "[УСПІХ]   \"" << expr << "\" = " << *result << '\n';
        } else {
            std::cout << "[ПОМИЛКА] \"" << expr << "\" -> " << result.error() << '\n';
        }
    }
    return 0;
}
```
:::

## Покрокове простеження розбору виразу `(3 + 4) * 2`

Щоб побачити, як граматика керує стеком викликів процесора під час низхідного аналізу, простежимо покроковий стан парсера для виразу `(3 + 4) * 2`:

1. Головна програма викликає функцію `parse_expr()`.
2. `parse_expr()` викликає `parse_term()`, яка, у свою чергу, викликає `parse_factor()`.
3. `parse_factor()` перевіряє поточний токен: це відкриваюча дужка `'('`. Функція зчитує її через `advance()` і рекурсивно викликає новий екземпляр `parse_expr()`.
4. Вкладений виклик `parse_expr()` розбирає доданок `3` (через ланцюжок `parse_term` → `parse_factor`), бачить токен `'+'`, зчитує другий доданок `4` та обчислює суму: `3.0 + 4.0 = 7.0`.
5. Повертаючись у `parse_factor()`, парсер перевіряє наявність закриваючої дужки `')'`. Токен успішно збігається, зчитується, і значення `7.0` повертається на попередній рівень виклику в `parse_term()`.
6. Зовнішній `parse_term()` перевіряє наступний токен: це оператор множення `'*'`. Він зчитує оператор і викликає `parse_factor()` для правого операнда `2`. Отримує значення `2.0` і перемножує: `7.0 * 2.0 = 14.0`.
7. `parse_expr()` переконується у відсутності знаків `+`/`-` і повертає кінцевий результат `14.0`.
8. Головний метод `parse()` перевіряє, що досягнуто кінця вхідного потоку `TOK_EOF`. Розбір успішно завершено без помилок.

## Побудова AST проти прямого обчислення

У наведеному вище коді обчислення значень відбувається «на льоту» під час обходу граматики. Це оптимально для простих інтерпретаторів, калькуляторів або конфігураційних файлів.

Проте в повноцінних компіляторах (GCC, Clang, Rustc) функції парсера повертають не числове значення, а вказівник на вузол **абстрактного синтаксичного дерева** (англ. *Abstract Syntax Tree*, AST). Вузол AST зберігає тип операції, посилання на ліве та праве піддерево, а також координати у вихідному файлі (номер рядка та стовпчика) для генерації якісних повідомлень про помилки та подальших фаз оптимізації коду.

## Інженерні пастки та захисне програмування

1. **Передбачення токенів (Lookahead):** Парсер рекурсивного спуску класу `LL(1)` приймає рішення на основі рівно одного наступного символу. Якщо два правила починаються однаково (наприклад, `A → id "(" ...` та `A → id "=" ...`), граматику необхідно факторизувати: винести спільний префікс `id` в одне місце.
2. **Перевірка завершення вхідного потоку:** Найпоширеніша помилка парсерів-початківців — повертати результат одразу після завершення кореневої функції `parse_expr()`. Якщо вхідний рядок містить `3 + 4 foo bar`, функція успішно розбере `3 + 4` і зупиниться, проігнорувавши хвіст `foo bar`. Обов'язково перевіряйте досягнення маркера кінця файлу (`current.type == TOK_EOF`).
3. **Панічний режим відновлення (Panic Mode Recovery):** У виробничих компіляторах при виявленні синтаксичної помилки парсер не зупиняє роботу, а переходить у режим пропуску токенів до найближчого «синхронізуючого символу» (крапки з комою `;` або закриваючої фігурної дужки `}`). Це дозволяє компілятору повідомити про всі синтаксичні помилки у файлі за один прохід, а не зупинятися на першій же помилці.
4. **Глибина рекурсії:** Занадто глибоко вкладені дужки (наприклад, `((((...10000 разів...))))`) можуть вичерпати розмір системного стека потоку. У захищених середовищах парсери ведуть явний лічильник поточної глибини викликів і генерують контрольовану помилку при перевищенні ліміту.
