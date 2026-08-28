/* minisu.c — навчальна su: тільки те, без чого вона не працює.
 *   cc -O2 -Wall -Wextra -o minisu minisu.c -lpam -lpam_misc
 *   sudo chown root:root minisu && sudo chmod 4755 minisu
 * Потрібен власний стек /etc/pam.d/minisu (для проби — копія файлу su).
 * misc_conv і -lpam_misc — розширення Linux-PAM, не переносне.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <grp.h>
#include <pwd.h>
#include <security/pam_appl.h>
#include <security/pam_misc.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

static pam_handle_t *pamh;
static volatile pid_t child = -1;

/* stderr не буферизований, тож _exit безпечний — і саме він потрібен у дитині:
   exit() злив би успадковані від батька буфери stdio вдруге */
static void die(const char *msg)
{
    fprintf(stderr, "minisu: %s: %s\n", msg, strerror(errno));
    _exit(1);
}

static void pam_die(int rc, const char *msg)
{
    fprintf(stderr, "minisu: %s: %s\n", msg, pam_strerror(pamh, rc));
    pam_end(pamh, rc);                  /* модулі мусять прибрати за собою */
    exit(1);
}

/* kill() — з дозволених в обробнику; більше тут нічого й не робиться */
static void forward(int sig)
{
    if (child > 0)
        kill(child, sig);
}

int main(int argc, char **argv)
{
    int login = 0, i = 1;
    if (i < argc && strcmp(argv[i], "-") == 0) { login = 1; i++; }
    if (i != argc - 1) {
        fprintf(stderr, "вжиток: minisu [-] <користувач>\n");
        return 1;
    }

    /* 1. Ціль у базі. Поля копіюємо ОДРАЗУ: getpwnam повертає вказівник на
          статичну область, і будь-який виклик NSS далі — у тому числі
          всередині модулів PAM — перепише її під нами. */
    struct passwd *pw = getpwnam(argv[i]);
    if (!pw) {
        fprintf(stderr, "minisu: немає такого користувача: %s\n", argv[i]);
        return 1;
    }
    uid_t uid = pw->pw_uid;
    gid_t gid = pw->pw_gid;
    char *name  = strdup(pw->pw_name);
    char *home  = strdup(pw->pw_dir);
    char *shell = strdup(pw->pw_shell[0] ? pw->pw_shell : "/bin/sh");
    if (!name || !home || !shell) die("пам'ять");

    /* 2. Стек PAM. Перший аргумент — ім'я СЛУЖБИ, тобто файлу в /etc/pam.d */
    struct pam_conv conv = { misc_conv, NULL };
    int rc = pam_start("minisu", name, &conv, &pamh);
    if (rc != PAM_SUCCESS) { fprintf(stderr, "minisu: pam_start\n"); return 1; }

    rc = pam_authenticate(pamh, 0);          /* уся розмова з паролем — тут */
    if (rc != PAM_SUCCESS) pam_die(rc, "автентифікація");

    rc = pam_acct_mgmt(pamh, 0);             /* запис не заблокований і не прострочений? */
    if (rc == PAM_NEW_AUTHTOK_REQD)
        rc = pam_chauthtok(pamh, PAM_CHANGE_EXPIRED_AUTHTOK);
    if (rc != PAM_SUCCESS) pam_die(rc, "перевірка запису");

    rc = pam_setcred(pamh, PAM_ESTABLISH_CRED);   /* квитки, ключі, членства від модулів */
    if (rc != PAM_SUCCESS) pam_die(rc, "видача облікових даних");

    rc = pam_open_session(pamh, 0);
    if (rc != PAM_SUCCESS) {
        pam_setcred(pamh, PAM_DELETE_CRED);
        pam_die(rc, "відкриття сеансу");
    }
    char **pamenv = pam_getenvlist(pamh);    /* що модулі дописали в оточення */

    /* 3. Сигнали блокуємо ДО fork: інакше SIGINT у щілину між fork і
          встановленням обробника вб'є батька, і сеанс лишиться відкритим */
    sigset_t block, old;
    sigemptyset(&block);
    sigaddset(&block, SIGINT);
    sigaddset(&block, SIGQUIT);
    sigaddset(&block, SIGTERM);
    sigprocmask(SIG_BLOCK, &block, &old);

    child = fork();
    if (child < 0) {                     /* сеанс уже відкритий — закрити більше нікому */
        fprintf(stderr, "minisu: fork: %s\n", strerror(errno));
        pam_close_session(pamh, 0);
        pam_setcred(pamh, PAM_DELETE_CRED);
        pam_end(pamh, PAM_SYSTEM_ERR);
        return 1;
    }

    if (child == 0) {
        /* ---- дитина: до pamh більше не торкається ----
           диспозиції обробників exec скине сам, а от МАСКА сигналів його
           переживає — тому відновлюємо явно */
        sigprocmask(SIG_SETMASK, &old, NULL);

        if (initgroups(name, gid) != 0) die("initgroups");   /* порядок */
        if (setgid(gid) != 0)           die("setgid");       /* незворотний: */
        if (setuid(uid) != 0)           die("setuid");       /* групи → gid → uid */
        if (uid != 0 && setuid(0) != -1) {                   /* доказ, а не віра */
            fprintf(stderr, "minisu: права не знялися\n");
            _exit(1);
        }

        if (login) {                     /* вхідний режим: оточення з нуля */
            char *term = getenv("TERM");
            char *keep = term ? strdup(term) : NULL;
            clearenv();
            if (keep) setenv("TERM", keep, 1);
            setenv("PATH", uid ? "/usr/local/bin:/usr/bin:/bin"
                               : "/usr/local/sbin:/usr/local/bin:/usr/sbin:"
                                 "/usr/bin:/sbin:/bin", 1);
            setenv("HOME", home, 1);
            setenv("SHELL", shell, 1);
            setenv("USER", name, 1);
            setenv("LOGNAME", name, 1);
            if (chdir(home) != 0) die("домівка недоступна");
        } else {                         /* невхідний: чуже оточення лишається */
            setenv("HOME", home, 1);
            setenv("SHELL", shell, 1);
            if (uid != 0) {              /* до root USER і LOGNAME не переносять */
                setenv("USER", name, 1);
                setenv("LOGNAME", name, 1);
            }
        }
        for (char **e = pamenv; e && *e; e++)
            putenv(*e);

        /* дефіс попереду argv[0] — єдиний спосіб сказати оболонці «ти вхідна» */
        char *base = strrchr(shell, '/');
        base = base ? base + 1 : shell;
        char arg0[128];
        snprintf(arg0, sizeof arg0, "%s%s", login ? "-" : "", base);
        char *args[] = { arg0, NULL };
        execv(shell, args);
        die("не запустити оболонку");
    }

    /* ---- батько: лишається root рівно заради прибирання ---- */
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = forward;             /* без SA_RESTART — waitpid дасть EINTR */
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGQUIT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);
    sigprocmask(SIG_SETMASK, &old, NULL);

    int status;
    while (waitpid(child, &status, 0) < 0)
        if (errno != EINTR) die("waitpid");

    pam_close_session(pamh, 0);
    pam_setcred(pamh, PAM_DELETE_CRED);
    pam_end(pamh, PAM_SUCCESS);

    return WIFEXITED(status) ? WEXITSTATUS(status) : 128 + WTERMSIG(status);
}
