/* Спрощена концептуальна схема в ядрі n_tty.c */
if (L_ISIG(tty)) {
    if (c == INTR_CHAR(tty)) {
        isig(SIGINT, tty);
        return;
    }
    if (c == SUSP_CHAR(tty)) {
        isig(SIGTSTP, tty);
        return;
    }
}

static void isig(int sig, struct tty_struct *tty) {
    struct pid *pgrp = tty->pgrp;
    if (pgrp) {
        kill_pgrp(pgrp, sig, 1);
    }
}
