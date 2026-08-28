#define _GNU_SOURCE
#include <pwd.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

/* 1 — знайшли, 0 — такого користувача нема, -1 — спитати не вдалося. */
int lookup_user(const char *name, uid_t *out_uid)
{
    size_t len = 1024;                  /* стартовий розмір буфера */
    char *buf = NULL;

    for (;;) {
        char *nb = realloc(buf, len);
        if (!nb) { free(buf); return -1; }
        buf = nb;

        struct passwd pw;
        struct passwd *res = NULL;
        int rc = getpwnam_r(name, &pw, buf, len, &res);

        if (rc == ERANGE) {             /* буфер малий — подвоїти й повторити */
            len *= 2;
            continue;
        }
        if (rc != 0) {                  /* джерело не змогло відповісти */
            free(buf);
            errno = rc;
            return -1;
        }
        if (res == NULL) {              /* відповідь є: такого запису нема */
            free(buf);
            return 0;
        }
        *out_uid = res->pw_uid;         /* поля дійсні, доки живий buf */
        free(buf);
        return 1;
    }
}
