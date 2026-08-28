/* nss_demo.c — джерело облікових записів із /etc/demo-users (ім'я:uid:gid) */
#include <nss.h>
#include <pwd.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>

#define SOURCE "/etc/demo-users"

/* Копіює рядок у буфер викликача й посуває курсор. NULL — місця забракло. */
static char *pack(const char *s, char **cur, char *end)
{
    size_t n = strlen(s) + 1;
    if ((size_t)(end - *cur) < n)
        return NULL;
    char *dst = *cur;
    memcpy(dst, s, n);
    *cur += n;
    return dst;
}

static enum nss_status fill(struct passwd *pw, const char *name,
                            uid_t uid, gid_t gid,
                            char *buf, size_t buflen, int *errnop)
{
    char *cur = buf, *end = buf + buflen;
    char home[256];
    snprintf(home, sizeof home, "/srv/proj/%s", name);

    pw->pw_name   = pack(name, &cur, end);
    pw->pw_passwd = pack("*", &cur, end);      /* паролем сюди не заходять */
    pw->pw_gecos  = pack("", &cur, end);
    pw->pw_dir    = pack(home, &cur, end);
    pw->pw_shell  = pack("/usr/sbin/nologin", &cur, end);

    if (!pw->pw_name || !pw->pw_passwd || !pw->pw_gecos
        || !pw->pw_dir || !pw->pw_shell) {
        *errnop = ERANGE;                      /* буфер малий — і тільки це */
        return NSS_STATUS_TRYAGAIN;            /* покличуть ще раз, з більшим */
    }
    pw->pw_uid = uid;                          /* числа лежать у структурі */
    pw->pw_gid = gid;
    return NSS_STATUS_SUCCESS;
}

/* key_name != NULL — шукаємо за іменем, інакше за числом. */
static enum nss_status find(const char *key_name, uid_t key_uid,
                            struct passwd *pw,
                            char *buf, size_t buflen, int *errnop)
{
    FILE *f = fopen(SOURCE, "re");             /* 'e' — O_CLOEXEC, див. нижче */
    if (f == NULL) {
        *errnop = errno;
        return NSS_STATUS_UNAVAIL;             /* джерела тут нема взагалі */
    }

    char line[512];
    enum nss_status st = NSS_STATUS_NOTFOUND;
    while (fgets(line, sizeof line, f)) {
        if (!strchr(line, '\n') && !feof(f)) { /* рядок довший за буфер: */
            int c;                             /* відкинути хвіст цілком,  */
            while ((c = fgetc(f)) != '\n' && c != EOF) { }
            continue;                          /* інакше він стане записом */
        }
        char name[128];
        unsigned long uid, gid;
        if (sscanf(line, "%127[^:]:%lu:%lu", name, &uid, &gid) != 3)
            continue;                          /* коментарі й сміття — повз */
        int hit = key_name ? strcmp(name, key_name) == 0
                           : (uid_t)uid == key_uid;
        if (!hit)
            continue;
        st = fill(pw, name, (uid_t)uid, (gid_t)gid, buf, buflen, errnop);
        break;
    }
    fclose(f);
    if (st == NSS_STATUS_NOTFOUND)
        *errnop = ENOENT;
    return st;
}

enum nss_status _nss_demo_getpwnam_r(const char *name, struct passwd *pw,
                                     char *buf, size_t buflen, int *errnop)
{
    return find(name, 0, pw, buf, buflen, errnop);
}

enum nss_status _nss_demo_getpwuid_r(uid_t uid, struct passwd *pw,
                                     char *buf, size_t buflen, int *errnop)
{
    return find(NULL, uid, pw, buf, buflen, errnop);
}
