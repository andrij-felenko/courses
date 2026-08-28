#include <stdint.h>
#include <string.h>

#define FPX_SW_OFFSET      464
#define FP_XSTATE_MAGIC1   0x46505853U
#define FP_XSTATE_MAGIC2   0x46505845U

struct fpx_sw { uint32_t magic1, extended_size;
                uint64_t xfeatures;
                uint32_t xstate_size, padding[7]; };

static size_t xstate_bytes(ucontext_t *uc)
{
    if (!(uc->uc_flags & UC_FP_XSTATE))          /* крок 1: ядро каже, що є  */
        return 0;

    unsigned char *fp = (unsigned char *)uc->uc_mcontext.fpregs;
    struct fpx_sw *sw = (struct fpx_sw *)(fp + FPX_SW_OFFSET);

    if (sw->magic1 != FP_XSTATE_MAGIC1)          /* крок 2: мітка на початку */
        return 0;

    uint32_t tail;                               /* крок 3: мітка в кінці    */
    memcpy(&tail, fp + sw->extended_size - 4, 4);
    if (tail != FP_XSTATE_MAGIC2)
        return 0;

    return sw->xstate_size;                      /* заголовок XSAVE — з fp+512 */
}
