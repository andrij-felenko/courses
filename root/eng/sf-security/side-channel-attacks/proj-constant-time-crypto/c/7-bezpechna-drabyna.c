#include <stdint.h>
#include <stddef.h>

/* Спрощена структура точки на кривій Монтгомері в проективних координатах (X : Z) */
typedef struct {
    uint64_t x;
    uint64_t z;
} CurvePoint;

/* Арифметичний крок драбини: виконує диференційне додавання та подвоєння точок.
   В реальних криптосистемах тут виконуються польові множення та квадратури над GF(2^255 - 19). */
void montgomery_step(CurvePoint *r0, CurvePoint *r1, const CurvePoint *init_p) {
    /* Регулярна послідовність операцій без розгалужень */
    r0->x = r0->x + r1->x;
    r0->z = r0->z * init_p->x;
    r1->x = r1->x * r1->x;
    r1->z = r1->z + init_p->z;
}

/* Скалярне множення постійного часу (Montgomery Ladder) */
CurvePoint montgomery_ladder_ct(const uint8_t *scalar, size_t scalar_bytes, CurvePoint p) {
    CurvePoint r0 = { .x = 1, .z = 0 }; /* Нейтральний елемент (точка на нескінченності) */
    CurvePoint r1 = p;                   /* Початкова точка P */
    uint8_t prev_bit = 0;

    /* Обхід скаляра від старшого біта до молодшого */
    for (int i = (int)scalar_bytes - 1; i >= 0; --i) {
        uint8_t byte = scalar[i];
        for (int b = 7; b >= 0; --b) {
            uint8_t bit = (byte >> b) & 1;
            uint8_t swap = bit ^ prev_bit;

            /* Перестановка регістрів перед обчисленням залежно від зміни біта */
            ct_cswap_arrays(swap, (uint8_t*)&r0, (uint8_t*)&r1, sizeof(CurvePoint));
            montgomery_step(&r0, &r1, &p);

            prev_bit = bit;
        }
    }

    /* Фінальна нормалізуюча перестановка */
    ct_cswap_arrays(prev_bit, (uint8_t*)&r0, (uint8_t*)&r1, sizeof(CurvePoint));
    return r0;
}
