#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Ідентифікатори аксіом та правил виведення PA */
typedef enum {
    PA_RULE_AXIOM_EQUALITY = 101,  /* Аксіоми рівності (=) */
    PA_RULE_AXIOM_PEANO_1  = 102,  /* ¬(S(x) = 0) */
    PA_RULE_AXIOM_PEANO_2  = 103,  /* S(x) = S(y) → x = y */
    PA_RULE_AXIOM_ADD_BASE = 104,  /* x + 0 = x */
    PA_RULE_AXIOM_ADD_SUCC = 105,  /* x + S(y) = S(x + y) */
    PA_RULE_AXIOM_MUL_BASE = 106,  /* x · 0 = 0 */
    PA_RULE_AXIOM_MUL_SUCC = 107,  /* x · S(y) = (x · y) + x */
    PA_RULE_SCHEME_INDUCTION = 108,/* Схема індукції */
    
    PA_RULE_MODUS_PONENS   = 201,  /* З A та A → B виводиться B */
    PA_RULE_GENERALIZATION = 202   /* З A(x) виводиться ∀x A(x) */
} PaRuleType;

/* Коди повернення та статусів верифікації */
typedef enum {
    PA_SUCCESS               = 0,
    PA_ERR_INVALID_STEP_ID   = 1001,
    PA_ERR_NOT_AN_AXIOM      = 1002,
    PA_ERR_MP_MISMATCH       = 1003,
    PA_ERR_INDUCTION_SCHEMA  = 1004,
    PA_ERR_UNBOUND_VARIABLE  = 1005,
    PA_ERR_CIRCULAR_PROOF    = 1006
} PaStatusCode;

/* Структура одного кроку доведення */
typedef struct PaProofStep {
    uint32_t step_id;           /* Унікальний номер кроку (1-indexed) */
    const void* formula_ast;    /* Указник на синтаксичне дерево формули */
    PaRuleType rule;            /* Обґрунтування кроку */
    uint32_t ref_step_1;        /* Посилання на 1-й крок (0, якщо немає) */
    uint32_t ref_step_2;        /* Посилання на 2-й крок (0, якщо немає) */
} PaProofStep;

/* Контекст верифікації формального доведення */
typedef struct PaProofContext {
    const PaProofStep* steps;   /* Масив кроків доведення */
    size_t step_count;          /* Загальна кількість кроків */
    uint32_t flags;             /* Прапорці налаштувань */
} PaProofContext;
