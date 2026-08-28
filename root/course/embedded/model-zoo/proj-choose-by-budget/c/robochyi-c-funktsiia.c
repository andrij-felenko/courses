// Результат вибору: або обраний варіант, або причина відмови.
typedef enum {
    PICK_OK = 0,           // знайшли прохідний варіант
    PICK_NONE_FITS_TIME,   // навіть найменший не вкладається в дедлайн
    PICK_NONE_FITS_MEM,    // у дедлайн лізе, але в пам'ять — ні
    PICK_EMPTY_TABLE,      // таблиця порожня або не залита
} PickStatus;

typedef struct {
    const ModelVariant* chosen;   // NULL, якщо не обрано
    PickStatus          status;
} PickResult;

// Обрати НАЙБІЛЬШИЙ варіант, що влазить у дедлайн, Flash і арену.
// budget_us    — бюджет латентності на кадр (мкс), з теми про бенчмаркінг.
// free_flash_b — вільний Flash під модель (байтів).
// free_ram_b   — вільна RAM під тензорну арену (байтів).
PickResult pick_model(uint32_t budget_us,
                      uint32_t free_flash_b,
                      uint32_t free_ram_b)
{
    PickResult r = { NULL, PICK_EMPTY_TABLE };
    if (kFamilyCount == 0) return r;

    // Прапорці причини: чи бодай хтось проходив окремі ворота.
    bool any_fits_time = false;

    // Таблиця вже відсортована від найбільшого до найменшого, тож ПЕРШИЙ,
    // що проходить усі ворота, і є найбільшим прохідним — його й беремо.
    for (int i = 0; i < kFamilyCount; ++i) {
        const ModelVariant* v = &kFamily[i];

        if (v->model_data == NULL)            // варіант не залитий у Flash
            continue;                         // пропускаємо, не вважаємо за збій

        // Ворота 1: ВИМІРЯНИЙ час ≤ дедлайн.
        if (v->latency_us > budget_us)
            continue;                         // занадто повільний — далі (швидші)
        any_fits_time = true;

        // Ворота 2: ваги int8-моделі ≤ вільний Flash.
        if (v->model_bytes > free_flash_b)
            continue;

        // Ворота 3: тензорна арена ≤ вільна RAM.
        if (v->arena_bytes > free_ram_b)
            continue;

        // Пройшов усі три — і він найбільший із прохідних. Готово.
        r.chosen = v;
        r.status = PICK_OK;
        return r;
    }

    // Нікого. Розрізняємо ДВІ дуже різні причини відмови.
    r.status = any_fits_time ? PICK_NONE_FITS_MEM : PICK_NONE_FITS_TIME;
    return r;
}
