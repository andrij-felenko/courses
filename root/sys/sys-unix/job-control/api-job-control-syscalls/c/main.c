struct termios {
    tcflag_t c_iflag;      /* Прапорці вхідного режиму */
    tcflag_t c_oflag;      /* Прапорці вихідного режиму */
    tcflag_t c_cflag;      /* Прапорці керування лінією */
    tcflag_t c_lflag;      /* Прапорці локального режиму */
    cc_t      c_line;       /* Дисципліна лінії */
    cc_t      c_cc[NCCS];   /* Масив управляючих символів */
    speed_t   c_ispeed;     /* Вхідна швидкість передачі */
    speed_t   c_ospeed;     /* Вихідна швидкість передачі */
};
