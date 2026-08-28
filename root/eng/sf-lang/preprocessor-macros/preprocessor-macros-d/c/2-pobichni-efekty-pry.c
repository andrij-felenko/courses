#include <stdio.h>

#define MIN_MACRO(a, b) (((a) < (b)) ? (a) : (b))

static int get_next_val(int* ptr) {
    return (*ptr)++;
}

int main(void) {
    int counter = 0;
    int limit = 5;

    /* get_next_val() викличеться двічі через дублювання аргументу в тілі макросу! */
    int m = MIN_MACRO(get_next_val(&counter), limit);

    printf("m = %d, counter = %d (очікували counter=1)\n", m, counter);
    return 0;
}
