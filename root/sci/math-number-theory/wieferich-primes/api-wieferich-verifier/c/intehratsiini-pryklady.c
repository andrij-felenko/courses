#include <stdio.h>
#include "wieferich_api.h"

int main(void) {
    wieferich_result_t res;
    wieferich_status_t status = wieferich_verify_prime(1093, 2, &res);

    if (status == WIEFERICH_IS_PRIME_WIEFERICH) {
        printf("Число %glu є простим числом Віферіха!\n", res.prime);
        printf("  Остача: %glu, Частка W(p): %glu\n", res.remainder, res.fermat_quotient);
    } else {
        printf("Число не є числом Віферіха. Статус: %d\n", status);
    }
    return 0;
}
