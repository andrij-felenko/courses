/* projectdb.c — служба userdb: реєстр проєктів застосунку як користувачі системи.
 *   зібрати:   gcc -O2 -Wall -o projectdb projectdb.c
 *   запустити: sudo ./projectdb
 *   спитати:   userdbctl user proj-kernel
 *              varlinkctl call /run/systemd/userdb/com.example.Projects \
 *                io.systemd.UserDatabase.GetUserRecord \
 *                '{"userName":"proj-kernel","service":"com.example.Projects"}'
 */
#define _GNU_SOURCE
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/un.h>
#include <unistd.h>

#define SERVICE    "com.example.Projects"
#define SOCKPATH   "/run/systemd/userdb/" SERVICE
#define UID_BASE   55000u      /* діапазон, не виданий на цій машині нікому */
#define DEPLOY_KEY "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIexample ci@build"

/* Реєстр застосунку. У житті — читається з його бази; тут сталий масив. */
static const char *const projects[] = { "kernel", "toolchain", "docs" };
#define N_PROJECTS (sizeof projects / sizeof projects[0])

/* Ім'я ↔ номер: чиста функція в обидва боки, тому розійтися нема чому. */
static long index_by_name(const char *name)
{
    if (strncmp(name, "proj-", 5) != 0) return -1;
    for (size_t i = 0; i < N_PROJECTS; i++)
        if (strcmp(name + 5, projects[i]) == 0) return (long) i;
    return -1;
}
static long index_by_uid(unsigned long long uid)
{
    if (uid < UID_BASE || uid >= UID_BASE + N_PROJECTS) return -1;
    return (long) (uid - UID_BASE);
}

/* ── Вузький вибирач полів верхнього рівня ────────────────────────────────
   Свідоме спрощення прикладу: не розуміє екранованих лапок і вкладеності.
   Служба, яку ставлять у систему, бере повноцінний розбирач JSON — або
   одразу sd-varlink із libsystemd, де розбір і рамка вже написані. */
static const char *field(const char *msg, const char *key)
{
    char pat[64];
    int n = snprintf(pat, sizeof pat, "\"%s\"", key);
    const char *p = strstr(msg, pat);
    if (!p) return NULL;
    p += n;
    while (*p == ' ') p++;
    if (*p++ != ':') return NULL;
    while (*p == ' ') p++;
    return p;
}
static int field_str(const char *msg, const char *key, char *out, size_t n)
{
    const char *p = field(msg, key);
    if (!p || *p != '"') return 0;
    const char *e = strchr(++p, '"');
    if (!e || (size_t) (e - p) >= n) return 0;
    memcpy(out, p, (size_t) (e - p));
    out[e - p] = '\0';
    return 1;
}
static long long field_num(const char *msg, const char *key)
{
    const char *p = field(msg, key);
    return (p && *p >= '0' && *p <= '9') ? strtoll(p, NULL, 10) : -1;
}
static int field_true(const char *msg, const char *key)
{
    const char *p = field(msg, key);
    return p && strncmp(p, "true", 4) == 0;
}

/* ── Надсилання ───────────────────────────────────────────────────────────
   Одне повідомлення Varlink — це об'єкт JSON і нульовий байт-роздільник. */
static int send_msg(int fd, const char *json)
{
    size_t len = strlen(json) + 1;                  /* разом із роздільником */
    for (size_t off = 0; off < len; ) {
        ssize_t k = write(fd, json + off, len - off);
        if (k < 0) { if (errno == EINTR) continue; return -1; }
        off += (size_t) k;
    }
    return 0;
}
static int send_error(int fd, const char *name)
{
    char buf[192];
    snprintf(buf, sizeof buf, "{\"error\":\"%s\",\"parameters\":{}}", name);
    return send_msg(fd, buf);
}

/* Секцію privileged дістає власник запису або root; решті її вирізають —
   і саме тому поруч їде incomplete: «тобі показали не все». */
static int send_user(int fd, size_t i, uid_t peer, int continues)
{
    unsigned uid = (unsigned) (UID_BASE + i);
    int owner = (peer == 0 || peer == (uid_t) uid);
    char buf[1024];
    snprintf(buf, sizeof buf,
        "{\"parameters\":{\"record\":{"
            "\"userName\":\"proj-%s\","
            "\"realName\":\"Проєкт %s\","
            "\"disposition\":\"system\","
            "\"service\":\"" SERVICE "\","
            "\"uid\":%u,\"gid\":%u,"
            "\"homeDirectory\":\"/var/lib/projects/%s\","
            "\"shell\":\"/usr/sbin/nologin\"%s"
        "},\"incomplete\":%s}%s}",
        projects[i], projects[i], uid, uid, projects[i],
        owner ? ",\"privileged\":{\"sshAuthorizedKeys\":[\"" DEPLOY_KEY "\"]}" : "",
        owner ? "false" : "true",
        continues ? ",\"continues\":true" : "");
    return send_msg(fd, buf);
}
static int send_group(int fd, size_t i, int continues)
{
    char buf[512];
    snprintf(buf, sizeof buf,
        "{\"parameters\":{\"record\":{"
            "\"groupName\":\"proj-%s\","
            "\"disposition\":\"system\","
            "\"service\":\"" SERVICE "\","
            "\"gid\":%u"
        "},\"incomplete\":false}%s}",
        projects[i], (unsigned) (UID_BASE + i),
        continues ? ",\"continues\":true" : "");
    return send_msg(fd, buf);
}

/* За яким ключем питають: індекс, −1 (такого немає) або −2 (просять перелік). */
static long resolve(const char *msg, const char *name_key, const char *num_key)
{
    char name[128];
    if (field_str(msg, name_key, name, sizeof name)) return index_by_name(name);
    long long n = field_num(msg, num_key);
    if (n >= 0) return index_by_uid((unsigned long long) n);
    return -2;
}

static int serve(int fd)
{
    struct ucred cred;
    socklen_t clen = sizeof cred;
    if (getsockopt(fd, SOL_SOCKET, SO_PEERCRED, &cred, &clen) < 0) return -1;
    uid_t peer = cred.uid;         /* вписало ядро в мить connect(); не підробиш */

    char msg[4096];
    size_t len = 0;
    for (;;) {                     /* читаємо, доки не трапиться роздільник */
        ssize_t k = read(fd, msg + len, sizeof msg - 1 - len);
        if (k <= 0) return -1;
        len += (size_t) k;
        if (memchr(msg, '\0', len)) break;
        if (len == sizeof msg - 1) return -1;      /* завелике повідомлення */
    }

    char method[128], service[128];
    if (!field_str(msg, "method", method, sizeof method))
        return send_error(fd, "org.varlink.service.InvalidParameter");

    /* service обов'язковий і мусить збігтися з іменем нашого сокета: так
       запит, пересланий не туди, помирає одразу, а не відповідає чужим. */
    if (!field_str(msg, "service", service, sizeof service) ||
        strcmp(service, SERVICE) != 0)
        return send_error(fd, "io.systemd.UserDatabase.BadService");

    if (strcmp(method, "io.systemd.UserDatabase.GetUserRecord") == 0) {
        long i = resolve(msg, "userName", "uid");
        if (i == -2) {                       /* ні імені, ні номера — перелік */
            if (!field_true(msg, "more"))    /* одна відповідь його не вмістить */
                return send_error(fd, "org.varlink.service.InvalidParameter");
            for (size_t k = 0; k < N_PROJECTS; k++)
                send_user(fd, k, peer, k + 1 < N_PROJECTS);
            return 0;
        }
        if (i < 0) return send_error(fd, "io.systemd.UserDatabase.NoRecordFound");
        return send_user(fd, (size_t) i, peer, 0);
    }

    if (strcmp(method, "io.systemd.UserDatabase.GetGroupRecord") == 0) {
        long i = resolve(msg, "groupName", "gid");
        if (i == -2) {
            if (!field_true(msg, "more"))
                return send_error(fd, "org.varlink.service.InvalidParameter");
            for (size_t k = 0; k < N_PROJECTS; k++)
                send_group(fd, k, k + 1 < N_PROJECTS);
            return 0;
        }
        if (i < 0) return send_error(fd, "io.systemd.UserDatabase.NoRecordFound");
        return send_group(fd, (size_t) i, 0);
    }

    /* Проєкт сидить лише у власній первинній групі, а первинне членство цим
       викликом не повідомляють. Порожньої вдалої відповіді тут не буває. */
    if (strcmp(method, "io.systemd.UserDatabase.GetMemberships") == 0)
        return send_error(fd, "io.systemd.UserDatabase.NoRecordFound");

    return send_error(fd, "org.varlink.service.MethodNotFound");
}

int main(void)
{
    unlink(SOCKPATH);                       /* лишок від попереднього запуску */

    int srv = socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (srv < 0) { perror("socket"); return 1; }

    struct sockaddr_un a = { .sun_family = AF_UNIX };
    strncpy(a.sun_path, SOCKPATH, sizeof a.sun_path - 1);
    if (bind(srv, (struct sockaddr *) &a, sizeof a) < 0) { perror("bind"); return 1; }

    /* Питати може будь-хто: що саме показати, вирішує не режим файлу,
       а засвідчений UID співрозмовника. */
    if (chmod(SOCKPATH, 0666) < 0) { perror("chmod"); return 1; }
    if (listen(srv, 64) < 0) { perror("listen"); return 1; }

    for (;;) {
        int fd = accept4(srv, NULL, NULL, SOCK_CLOEXEC);
        if (fd < 0) { if (errno == EINTR) continue; perror("accept"); return 1; }
        serve(fd);          /* законно по черзі: жодна гілка нікого не чекає */
        close(fd);
    }
}
