/* audit.c — «бібліотека»: чиста арифметика, жодного вводу-виводу,
   щоб неправильні числа походили ЛИШЕ з двійкової угоди */
#include "audit.h"
#include <stdio.h>
#include <stdint.h>

off_t tail_offset(off_t size, off_t back)
{
    fprintf(stderr, "  [audit.c] sizeof(off_t)=%zu  size=%jd  back=%jd\n",
            sizeof(off_t), (intmax_t)size, (intmax_t)back);
    return size - back;
}

void fill_span(struct span *out)
{
    fprintf(stderr, "  [audit.c] sizeof(struct span)=%zu\n", sizeof(struct span));
    out->start     = 4096;
    out->records   = 7;
    out->truncated = 1;
}
