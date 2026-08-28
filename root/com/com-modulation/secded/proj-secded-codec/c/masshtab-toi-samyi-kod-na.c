#include <stdint.h>
#include <string.h>

#define N_DATA  64          /* біти даних                                  */
#define N_HAM    7          /* контролі Геммінга: позиції 1,2,4,8,16,32,64 */
#define N_POS   71          /* усі позиції слова Геммінга: 1..71           */

static uint64_t MASK[N_HAM];       /* MASK[j] — які біти даних входять у контроль j */
static int8_t   POS_OF[N_DATA];    /* POS_OF[i] — позиція i-го біта даних у слові    */
static int8_t   SYN_TO_DATA[128];  /* синдром → індекс біта даних, або −1 / −2       */

static int is_pow2(int p) { return (p & (p - 1)) == 0; }

void secded72_init(void)
{
    int p, j, i = 0;

    memset(SYN_TO_DATA, -1, sizeof SYN_TO_DATA);   /* −1: синдром не вказує НІКУДИ */
    for (j = 0; j < N_HAM; j++) MASK[j] = 0;

    for (p = 1; p <= N_POS; p++) {
        if (is_pow2(p)) {                  /* позиція контрольного біта Геммінга */
            SYN_TO_DATA[p] = -2;           /* −2: збій самого контролю — дані цілі */
            continue;
        }
        POS_OF[i] = (int8_t)p;             /* решта позицій — дані */
        SYN_TO_DATA[p] = (int8_t)i;
        for (j = 0; j < N_HAM; j++)
            if ((p >> j) & 1) MASK[j] |= (uint64_t)1 << i;
        i++;                               /* на виході i == 64: 71 позиція − 7 контролів */
    }
}

static int par64(uint64_t x) { return __builtin_parityll(x); }

uint8_t secded72_encode(uint64_t data)
{
    uint8_t c = 0;
    int j;
    for (j = 0; j < N_HAM; j++)
        c |= (uint8_t)(par64(data & MASK[j]) << j);

    /* P₀ закриває ВСІ 71 біт слова: 64 даних + 7 щойно порахованих контролів */
    c |= (uint8_t)((par64(data) ^ __builtin_parity(c)) << 7);
    return c;
}
