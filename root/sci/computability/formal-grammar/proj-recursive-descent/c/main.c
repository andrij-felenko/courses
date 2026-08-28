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
