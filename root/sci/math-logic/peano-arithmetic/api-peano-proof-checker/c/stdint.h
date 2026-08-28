#include <stdint.h>
#include <stdbool.h>

/* Перевірка одного кроку доведення */
PaStatusCode pa_verify_step(
    const PaProofContext* ctx,
    size_t current_step_idx
);

/* Повна перевірка всього масиву кроків доведення */
PaStatusCode pa_verify_proof(
    const PaProofContext* ctx,
    uint32_t* failed_step_id
);

/* Синтаксичний аналізатор відповідності схемі індукції */
bool pa_is_induction_instance(
    const void* formula_ast,
    const char* var_name
);
