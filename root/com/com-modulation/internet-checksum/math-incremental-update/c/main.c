#include <stdint.h>

// RFC 1624 [Eqn. 3]:  HC' = ~(~HC + ~m + m'),  де + — обернене додавання.
// hc — стара контрольна сума з пакета; old/new — старе й нове 16-бітні поля.
uint16_t csum_patch(uint16_t hc, uint16_t old_field, uint16_t new_field) {
    uint32_t sum = (uint16_t)~hc;           // ~HC = C: повертаємось в область суми
    sum += (uint16_t)~old_field;            // + ~m  — прибрати старе поле
    sum += new_field;                       // + m'  — додати нове поле
    while (sum >> 16)                        // загорнути перенос, доки він є
        sum = (sum & 0xFFFF) + (sum >> 16);
    return (uint16_t)~sum;                   // ЄДИНА фінальна інверсія: −0 → +0
}
