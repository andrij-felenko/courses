#include <sys/prctl.h>
#include <stdio.h>

int make_subreaper(void) {
    /* Оголошуємо поточний процес прибирачем усіх сиріт у своєму піддереві */
    if (prctl(PR_SET_CHILD_SUBREAPER, 1, 0, 0, 0) == -1) {
        perror("prctl PR_SET_CHILD_SUBREAPER");
        return -1;
    }
    return 0;
}
