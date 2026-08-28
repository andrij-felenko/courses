/* socktune.c */
#define _GNU_SOURCE
#include <errno.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/time.h>
#include "socktune.h"

static opt_result *slot(sock_report *r, const char *name)
{
    static opt_result sink;          /* якщо звіт переповнено — пишемо в нікуди */
    opt_result *o = &sink;
    if (r->n < SOCK_REPORT_CAP) o = &r->item[r->n++];
    else                        r->overflow++;
    memset(o, 0, sizeof *o);
    o->name = name;
    return o;
}

/* Ставить цілочисельну опцію й ОДРАЗУ читає її назад.
   Повертає 1, якщо це справжня невдача, і 0 в усіх інших випадках. */
static int set_int(int fd, int level, int name, int want,
                   const char *label, sock_report *rep)
{
    opt_result *o = slot(rep, label);
    o->want = want;

    if (setsockopt(fd, level, name, &want, sizeof want) < 0) {
        o->err = errno;
        if (errno == ENOPROTOOPT || errno == EOPNOTSUPP) {
            o->state = OPT_UNSUPPORTED;   /* не помилка: тут такої ручки немає */
            rep->unsupported++;
            return 0;
        }
        o->state = OPT_FAILED;
        rep->failed++;
        return 1;
    }

    int got = 0;
    socklen_t len = sizeof got;
    if (getsockopt(fd, level, name, &got, &len) < 0) {
        o->err = errno;
        o->state = OPT_FAILED;
        rep->failed++;
        return 1;
    }
    o->got = got;

    /* Три відповіді ядра, які означають «прийнято»: те саме число; подвоєне
       (так Linux робить із буферами — половина піде на службові структури);
       будь-яке ненульове там, де просили прапорець. */
    if (got == want || got == 2 * want || (want == 1 && got != 0)) {
        o->state = OPT_OK;
    } else {
        o->state = OPT_CHANGED;
        rep->changed++;
    }
    return 0;
}
