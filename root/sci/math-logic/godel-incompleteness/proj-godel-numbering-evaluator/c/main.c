#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

// Алфавітний код базових синтаксичних токенів
typedef enum {
    TOK_ZERO = 1,
    TOK_SUCC = 2,
    TOK_PLUS = 3,
    TOK_MULT = 4,
    TOK_EQ   = 5,
    TOK_NOT  = 6,
    TOK_IMPL = 7,
    TOK_EX   = 8,
    TOK_VAR  = 9,
    TOK_LPAR = 10,
    TOK_RPAR = 11
} TokenType;

// Прості числа для Ґеделевої нумерації
static const uint64_t PRIMES[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47};
static const size_t MAX_PRIMES = sizeof(PRIMES) / sizeof(PRIMES[0]);

// Швидке піднесення до степеня uint64_t
static uint64_t power_uint64(uint64_t base, uint64_t exp) {
    uint64_t res = 1;
    while (exp > 0) {
        if (exp & 1) res *= base;
        base *= base;
        exp >>= 1;
    }
    return res;
}

// Кодування послідовності токенів у Ґеделів номер
uint64_t encode_tokens(const uint32_t* tokens, size_t count) {
    if (count > MAX_PRIMES) return 0; // Переповнення списку простих чисел
    uint64_t godel_num = 1;
    for (size_t i = 0; i < count; ++i) {
        godel_num *= power_uint64(PRIMES[i], tokens[i]);
    }
    return godel_num;
}

// Декодування Ґеделевого номера у показники степенів простих множників
bool decode_godel_number(uint64_t godel_num, uint32_t* out_tokens, size_t* out_count) {
    if (godel_num == 0) return false;
    size_t idx = 0;
    uint64_t temp = godel_num;

    while (temp > 1 && idx < MAX_PRIMES) {
        uint32_t exp = 0;
        while (temp % PRIMES[idx] == 0) {
            exp++;
            temp /= PRIMES[idx];
        }
        out_tokens[idx] = exp;
        idx++;
    }
    *out_count = idx;
    return (temp == 1);
}

// Структурне представлення кроку доведення
typedef struct {
    uint32_t tokens[16];
    size_t token_count;
    uint64_t godel_id;
} ProofStep;

// Проста перевірка правила Modus Ponens: чи є step3 наслідком step1 та step2 (step2 ≡ step1 -> step3)
bool check_modus_ponens(const ProofStep* s1, const ProofStep* s2, const ProofStep* s3) {
    // Перевіряємо, чи s2 має вигляд (s1 IMPL s3)
    if (s2->token_count != (s1->token_count + s3->token_count + 1)) {
        return false;
    }
    // Перевірка відповідності токенів префікса s1
    for (size_t i = 0; i < s1->token_count; ++i) {
        if (s2->tokens[i] != s1->tokens[i]) return false;
    }
    // Токен імпликації
    if (s2->tokens[s1->token_count] != TOK_IMPL) return false;
    // Перевірка відповідності суфікса s3
    for (size_t j = 0; j < s3->token_count; ++j) {
        if (s2->tokens[s1->token_count + 1 + j] != s3->tokens[j]) return false;
    }
    return true;
}

int main(void) {
    printf("--- Демонстрація кодування Ґеделя мовою C ---\n");

    // Формула: ¬ ( x = 0 )
    uint32_t formula_tokens[] = {TOK_NOT, TOK_LPAR, TOK_VAR, TOK_EQ, TOK_ZERO, TOK_RPAR};
    size_t count = sizeof(formula_tokens) / sizeof(formula_tokens[0]);

    uint64_t godel_num = encode_tokens(formula_tokens, count);
    printf("Формула: NOT ( VAR EQ ZERO )\n");
    printf("Обчислений Ґеделів номер: %llu\n", (unsigned long long)godel_num);

    uint32_t decoded[16] = {0};
    size_t dec_count = 0;
    if (decode_godel_number(godel_num, decoded, &dec_count)) {
        printf("Декодовані показники простих множників: ");
        for (size_t i = 0; i < dec_count; ++i) {
            printf("%u ", decoded[i]);
        }
        printf("\n");
    }

    return 0;
}
