#include <stdint.h>

#define M_P1  0x55u   /* позиції 1,3,5,7 */
#define M_P2  0x66u   /* позиції 2,3,6,7 */
#define M_P4  0x78u   /* позиції 4,5,6,7 */

/* data: чотири біти D1 D2 D3 D4 у бітах 3..0 */
uint8_t secded_encode(uint8_t data)
{
    uint8_t w = (uint8_t)((((data >> 3) & 1u) << 2)    /* D1 → позиція 3 */
                        | (((data >> 2) & 1u) << 4)    /* D2 → позиція 5 */
                        | (((data >> 1) & 1u) << 5)    /* D3 → позиція 6 */
                        | (((data >> 0) & 1u) << 6));  /* D4 → позиція 7 */

    w |= (uint8_t)(parity8(w & M_P1) << 0);   /* P1 → позиція 1 */
    w |= (uint8_t)(parity8(w & M_P2) << 1);   /* P2 → позиція 2 */
    w |= (uint8_t)(parity8(w & M_P4) << 3);   /* P4 → позиція 4 */

    w |= (uint8_t)(parity8(w) << 7);          /* P₀ = XOR УСІХ СЕМИ бітів слова */
    return w;
}
