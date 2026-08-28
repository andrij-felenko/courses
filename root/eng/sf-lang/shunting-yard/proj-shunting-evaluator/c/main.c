#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include <stdbool.h>

#define MAX_TOKENS 512
#define MAX_STACK  256

typedef enum {
    TOK_NUMBER,
    TOK_OP,
    TOK_UNARY_MINUS,
    TOK_FUNCTION,
    TOK_LPAREN,
    TOK_RPAREN,
    TOK_COMMA,
    TOK_EOF
} TokenType;

typedef enum {
    ASSOC_NONE,
    ASSOC_LEFT,
    ASSOC_RIGHT
} Associativity;

typedef struct {
    TokenType type;
    double number_value;
    char op_symbol;
    char func_name[32];
    int arg_count;
} Token;

typedef struct {
    int precedence;
    Associativity associativity;
} OpInfo;

static OpInfo get_op_info(char op) {
    OpInfo info = {0, ASSOC_NONE};
    switch (op) {
        case '+':
        case '-':
            info.precedence = 1;
            info.associativity = ASSOC_LEFT;
            break;
        case '*':
        case '/':
            info.precedence = 2;
            info.associativity = ASSOC_LEFT;
            break;
        case '^':
            info.precedence = 3;
            info.associativity = ASSOC_RIGHT;
            break;
        default:
            break;
    }
    return info;
}

/* ── 1. Лексичний аналіз (Лексер) ── */
typedef struct {
    const char *source;
    size_t cursor;
    TokenType prev_token_type;
} Lexer;

static void lexer_init(Lexer *lex, const char *src) {
    lex->source = src;
    lex->cursor = 0;
    lex->prev_token_type = TOK_EOF;
}

static Token lexer_next(Lexer *lex) {
    while (lex->source[lex->cursor] && isspace((unsigned char)lex->source[lex->cursor])) {
        lex->cursor++;
    }

    Token tok;
    memset(&tok, 0, sizeof(Token));

    char c = lex->source[lex->cursor];
    if (c == '\0') {
        tok.type = TOK_EOF;
        lex->prev_token_type = TOK_EOF;
        return tok;
    }

    /* Числові літерали (цілі та дробові) */
    if (isdigit((unsigned char)c) || c == '.') {
        char *end_ptr = NULL;
        tok.number_value = strtod(&lex->source[lex->cursor], &end_ptr);
        tok.type = TOK_NUMBER;
        lex->cursor = (size_t)(end_ptr - lex->source);
        lex->prev_token_type = TOK_NUMBER;
        return tok;
    }

    /* Ідентифікатори: виклики функцій (sin, cos, max, pow, sqrt) */
    if (isalpha((unsigned char)c)) {
        size_t start = lex->cursor;
        while (isalnum((unsigned char)lex->source[lex->cursor]) || lex->source[lex->cursor] == '_') {
            lex->cursor++;
        }
        size_t len = lex->cursor - start;
        if (len >= sizeof(tok.func_name)) len = sizeof(tok.func_name) - 1;
        strncpy(tok.func_name, &lex->source[start], len);
        tok.func_name[len] = '\0';
        tok.type = TOK_FUNCTION;
        tok.arg_count = 1;
        lex->prev_token_type = TOK_FUNCTION;
        return tok;
    }

    /* Дужки та роздільники */
    if (c == '(') {
        tok.type = TOK_LPAREN;
        lex->cursor++;
        lex->prev_token_type = TOK_LPAREN;
        return tok;
    }
    if (c == ')') {
        tok.type = TOK_RPAREN;
        lex->cursor++;
        lex->prev_token_type = TOK_RPAREN;
        return tok;
    }
    if (c == ',') {
        tok.type = TOK_COMMA;
        lex->cursor++;
        lex->prev_token_type = TOK_COMMA;
        return tok;
    }

    /* Розрізнення унарного та бінарного мінуса */
    if (c == '-') {
        bool is_unary = (lex->prev_token_type == TOK_EOF ||
                         lex->prev_token_type == TOK_OP ||
                         lex->prev_token_type == TOK_UNARY_MINUS ||
                         lex->prev_token_type == TOK_LPAREN ||
                         lex->prev_token_type == TOK_COMMA);
        lex->cursor++;
        if (is_unary) {
            tok.type = TOK_UNARY_MINUS;
            tok.op_symbol = '~'; /* внутрішній символ для унарного мінуса */
            lex->prev_token_type = TOK_UNARY_MINUS;
        } else {
            tok.type = TOK_OP;
            tok.op_symbol = '-';
            lex->prev_token_type = TOK_OP;
        }
        return tok;
    }

    /* Бінарні оператори (+, *, /, ^) */
    if (strchr("+*/^", c) != NULL) {
        tok.type = TOK_OP;
        tok.op_symbol = c;
        lex->cursor++;
        lex->prev_token_type = TOK_OP;
        return tok;
    }

    fprintf(stderr, "Помилка лексера: невідомий символ '%c'\n", c);
    tok.type = TOK_EOF;
    return tok;
}

/* ── 2. Алгоритм сортувальної станції (Infix -> RPN) ── */
typedef struct {
    Token tokens[MAX_TOKENS];
    int count;
} TokenList;

static bool shunting_yard_to_rpn(const char *expr, TokenList *output_rpn) {
    output_rpn->count = 0;

    Token op_stack[MAX_STACK];
    int op_top = -1;

    int arg_counts[MAX_STACK];
    int func_top = -1;

    Lexer lex;
    lexer_init(&lex, expr);

    Token tok;
    while ((tok = lexer_next(&lex)).type != TOK_EOF) {
        if (tok.type == TOK_NUMBER) {
            output_rpn->tokens[output_rpn->count++] = tok;
        }
        else if (tok.type == TOK_FUNCTION) {
            op_stack[++op_top] = tok;
            arg_counts[++func_top] = 1; /* мінімум 1 аргумент за замовчуванням */
        }
        else if (tok.type == COMMA_TOKEN_SKIP_UNUSED) {
            /* захист */
        }
        else if (tok.type == TOK_COMMA) {
            /* Виштовхуємо до найближчої '(' */
            while (op_top >= 0 && op_stack[op_top].type != TOK_LPAREN) {
                output_rpn->tokens[output_rpn->count++] = op_stack[op_top--];
            }
            if (op_top < 0) {
                fprintf(stderr, "Синтаксична помилка: кома поза дужками виклику функції\n");
                return false;
            }
            if (func_top >= 0) {
                arg_counts[func_top]++;
            }
        }
        else if (tok.type == TOK_UNARY_MINUS) {
            /* Унарний мінус правоасоціативний із високим пріоритетом 4 */
            op_stack[++op_top] = tok;
        }
        else if (tok.type == TOK_OP) {
            OpInfo in_info = get_op_info(tok.op_symbol);
            while (op_top >= 0) {
                Token top = op_stack[op_top];
                if (top.type == TOK_FUNCTION || top.type == TOK_UNARY_MINUS) {
                    output_rpn->tokens[output_rpn->count++] = op_stack[op_top--];
                    continue;
                }
                if (top.type == TOK_OP) {
                    OpInfo top_info = get_op_info(top.op_symbol);
                    if (top_info.precedence > in_info.precedence ||
                       (top_info.precedence == in_info.precedence && in_info.associativity == ASSOC_LEFT)) {
                        output_rpn->tokens[output_rpn->count++] = op_stack[op_top--];
                        continue;
                    }
                }
                break;
            }
            op_stack[++op_top] = tok;
        }
        else if (tok.type == TOK_LPAREN) {
            op_stack[++op_top] = tok;
        }
        else if (tok.type == TOK_RPAREN) {
            while (op_top >= 0 && op_stack[op_top].type != TOK_LPAREN) {
                output_rpn->tokens[output_rpn->count++] = op_stack[op_top--];
            }
            if (op_top < 0) {
                fprintf(stderr, "Синтаксична помилка: непарна закриваюча дужка ')'\n");
                return false;
            }
            op_top--; /* скидаємо '(' */

            /* Якщо над '(' була функція, виштовхуємо її */
            if (op_top >= 0 && op_stack[op_top].type == TOK_FUNCTION) {
                Token func_tok = op_stack[op_top--];
                func_tok.arg_count = arg_counts[func_top--];
                output_rpn->tokens[output_rpn->count++] = func_tok;
            }
        }
    }

    /* Виштовхуємо залишки зі стека */
    while (op_top >= 0) {
        if (op_stack[op_top].type == TOK_LPAREN || op_stack[op_top].type == TOK_RPAREN) {
            fprintf(stderr, "Синтаксична помилка: незакрита кругла дужка '('\n");
            return false;
        }
        output_rpn->tokens[output_rpn->count++] = op_stack[op_top--];
    }

    return true;
}

/* ── 3. Стек-орієнтоване обчислення RPN ── */
static bool evaluate_rpn(const TokenList *rpn, double *result) {
    double eval_stack[MAX_STACK];
    int top = -1;

    for (int i = 0; i < rpn->count; i++) {
        const Token *tok = &rpn->tokens[i];
        if (tok->type == TOK_NUMBER) {
            eval_stack[++top] = tok->number_value;
        }
        else if (tok->type == TOK_UNARY_MINUS) {
            if (top < 0) {
                fprintf(stderr, "Помилка обчислення: недостатньо операндів для унарного мінуса\n");
                return false;
            }
            eval_stack[top] = -eval_stack[top];
        }
        else if (tok->type == TOK_OP) {
            if (top < 1) {
                fprintf(stderr, "Помилка обчислення: недостатньо операндів для оператора '%c'\n", tok->op_symbol);
                return false;
            }
            double b = eval_stack[top--];
            double a = eval_stack[top--];
            double res = 0.0;
            switch (tok->op_symbol) {
                case '+': res = a + b; break;
                case '-': res = a - b; break;
                case '*': res = a * b; break;
                case '/':
                    if (b == 0.0) {
                        fprintf(stderr, "Помилка обчислення: ділення на нуль\n");
                        return false;
                    }
                    res = a / b;
                    break;
                case '^': res = pow(a, b); break;
                default: return false;
            }
            eval_stack[++top] = res;
        }
        else if (tok->type == TOK_FUNCTION) {
            if (strcmp(tok->func_name, "sin") == 0) {
                if (top < 0) return false;
                eval_stack[top] = sin(eval_stack[top]);
            }
            else if (strcmp(tok->func_name, "cos") == 0) {
                if (top < 0) return false;
                eval_stack[top] = cos(eval_stack[top]);
            }
            else if (strcmp(tok->func_name, "sqrt") == 0) {
                if (top < 0 || eval_stack[top] < 0.0) return false;
                eval_stack[top] = sqrt(eval_stack[top]);
            }
            else if (strcmp(tok->func_name, "max") == 0) {
                if (top < 1) return false;
                double b = eval_stack[top--];
                double a = eval_stack[top--];
                eval_stack[++top] = (a > b) ? a : b;
            }
            else if (strcmp(tok->func_name, "pow") == 0) {
                if (top < 1) return false;
                double b = eval_stack[top--];
                double a = eval_stack[top--];
                eval_stack[++top] = pow(a, b);
            }
        }
    }

    if (top != 0) {
        fprintf(stderr, "Помилка обчислення: невідповідність кількості операндів та операторів\n");
        return false;
    }

    *result = eval_stack[top];
    return true;
}

int main(void) {
    const char *expr = "3 + 4 * 2 / ( 1 - 5 ) ^ 2 + max(10, 20)";
    printf("Вхідний вираз: %s\n", expr);

    TokenList rpn;
    if (shunting_yard_to_rpn(expr, &rpn)) {
        printf("RPN (Постфікс): ");
        for (int i = 0; i < rpn.count; i++) {
            if (rpn.tokens[i].type == TOK_NUMBER) {
                printf("%.2f ", rpn.tokens[i].number_value);
            } else if (rpn.tokens[i].type == TOK_OP) {
                printf("%c ", rpn.tokens[i].op_symbol);
            } else if (rpn.tokens[i].type == TOK_UNARY_MINUS) {
                printf("neg ");
            } else if (rpn.tokens[i].type == TOK_FUNCTION) {
                printf("%s/%d ", rpn.tokens[i].func_name, rpn.tokens[i].arg_count);
            }
        }
        printf("\n");

        double res = 0.0;
        if (evaluate_rpn(&rpn, &res)) {
            printf("Результат обчислення: %.4f\n", res);
        }
    }
    return 0;
}
