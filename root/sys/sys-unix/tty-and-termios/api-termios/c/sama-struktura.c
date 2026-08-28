#include <termios.h>

/* glibc, Linux; наведено для довідки — оголошено в заголовку */
#define NCCS 32
struct termios {
    tcflag_t c_iflag;    /* що робити з тим, що прийшло  */
    tcflag_t c_oflag;    /* що робити з тим, що йде       */
    tcflag_t c_cflag;    /* сам канал: кадр, лінії, швидкість */
    tcflag_t c_lflag;    /* робота лінійної дисципліни    */
    cc_t     c_line;     /* номер лінійної дисципліни (не POSIX) */
    cc_t     c_cc[NCCS]; /* особливі символи              */
    speed_t  c_ispeed;   /* швидкість прийому  (glibc ≥ 2.42) */
    speed_t  c_ospeed;   /* швидкість передачі (glibc ≥ 2.42) */
};
