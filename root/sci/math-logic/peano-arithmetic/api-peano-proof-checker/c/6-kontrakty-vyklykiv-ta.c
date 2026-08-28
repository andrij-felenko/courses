#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

int main(void) {
    printf("=== Перевірка формального доведення через PA Proof Checker API (C) ===\n");

    /* Створення масиву кроків для доведення: ∀x (x + 0 = x) */
    PaProofStep steps[2];

    /* Крок 1: Аксіома додавання бази: x + 0 = x */
    steps[0].step_id = 1;
    steps[0].formula_ast = (const void*)0x1000; /* Умовна адреса AST */
    steps[0].rule = PA_RULE_AXIOM_ADD_BASE;
    steps[0].ref_step_1 = 0;
    steps[0].ref_step_2 = 0;

    /* Крок 2: Узагальнення за x: ∀x (x + 0 = x) */
    steps[1].step_id = 2;
    steps[1].formula_ast = (const void*)0x2000;
    steps[1].rule = PA_RULE_GENERALIZATION;
    steps[1].ref_step_1 = 1;
    steps[1].ref_step_2 = 0;

    PaProofContext ctx;
    ctx.steps = steps;
    ctx.step_count = 2;
    ctx.flags = 0;

    uint32_t failed_step = 0;
    PaStatusCode status = pa_verify_proof(&ctx, &failed_step);

    if (status == PA_SUCCESS) {
        printf("Результат: Формальне доведення УСПІШНО ВЕРИФІКОВАНО (PA_SUCCESS)\n");
    } else {
        printf("Результат: ПОМИЛКА ВЕРИФІКАЦІЇ у кроці %u (Код помилки: %d)\n", failed_step, status);
    }

    return 0;
}
