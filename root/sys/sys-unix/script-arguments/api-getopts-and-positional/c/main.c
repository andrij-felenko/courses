/* Оголошення інтерфейсу getopt_long у C */
#include <getopt.h>

struct option {
    const char *name;    /* Назва довгої опції, наприклад "file" */
    int         has_arg; /* no_argument (0), required_argument (1), optional_argument (2) */
    int        *flag;    /* Якщо NULL, getopt_long повертає val; інакше записує val у *flag */
    int         val;     /* Значення повернення або значення для запису в *flag */
};

extern char *optarg;
extern int optind, opterr, optopt;

int getopt_long(int argc, char *const argv[],
                const char *optstring,
                const struct option *longopts, int *longindex);
