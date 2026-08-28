#include <stdio.h>

static char outbuf[8192];      /* статична пам'ять: живе рівно стільки, скільки потік */

int main(void)
{
    if (setvbuf(stdout, outbuf, _IOLBF, sizeof outbuf) != 0) {
        perror("setvbuf");     /* режим лишився типовим — далі про це знаємо */
        return 1;
    }
    printf("цей рядок вийде негайно, куди б не вів stdout\n");
    return 0;
}
