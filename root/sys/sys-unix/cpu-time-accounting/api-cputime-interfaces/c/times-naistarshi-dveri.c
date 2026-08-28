#include <sys/times.h>

clock_t times(struct tms *buf);

struct tms {
    clock_t tms_utime;   /* власний час у режимі користувача */
    clock_t tms_stime;   /* власний час у режимі ядра        */
    clock_t tms_cutime;  /* те саме для дочеканих нащадків   */
    clock_t tms_cstime;
};
