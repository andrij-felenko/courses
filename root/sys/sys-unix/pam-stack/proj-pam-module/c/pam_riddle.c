/* pam_riddle.c — друге запитання поверх пароля.
 *   cc -O2 -Wall -Wextra -fPIC -shared -o pam_riddle.so pam_riddle.c -lpam
 *   install -m 0644 pam_riddle.so /usr/lib/x86_64-linux-gnu/security/   # Debian
 *   install -m 0644 pam_riddle.so /usr/lib64/security/                  # Fedora
 */
#define _GNU_SOURCE
#include <security/pam_modules.h>
#include <security/pam_ext.h>      /* pam_syslog() — розширення Linux-PAM */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <syslog.h>

/* --- запитати людину, не знаючи, хто й де вона -------------------------- */
static int ask(pam_handle_t *pamh, const char *prompt, char **out)
{
    const void *item = NULL;
    const struct pam_conv *conv;
    struct pam_message msg;
    const struct pam_message *pmsg = &msg;
    struct pam_response *resp = NULL;
    int rc;

    *out = NULL;
    rc = pam_get_item(pamh, PAM_CONV, &item);
    conv = item;
    if (rc != PAM_SUCCESS || conv == NULL || conv->conv == NULL)
        return PAM_CONV_ERR;

    msg.msg_style = PAM_PROMPT_ECHO_OFF;   /* спитай і не показуй набране */
    msg.msg = prompt;

    rc = conv->conv(1, &pmsg, &resp, conv->appdata_ptr);
    if (rc != PAM_SUCCESS || resp == NULL)
        return PAM_CONV_ERR;
    if (resp[0].resp == NULL) {            /* порожня відповідь */
        free(resp);
        return PAM_CONV_ERR;
    }
    *out = resp[0].resp;   /* рядок забираємо собі — звільнимо потім */
    free(resp);            /* масив звільняємо тут і зараз */
    return PAM_SUCCESS;
}

static void wipe(char **s)
{
    if (*s == NULL)
        return;
    explicit_bzero(*s, strlen(*s));   /* memset() компілятор має право викинути */
    free(*s);
    *s = NULL;
}

/* Порівняння без залежності часу від змісту: цикл однакової довжини,
   без раннього виходу на першому розбіжному байті. */
static int same_secret(const char *a, const char *b)
{
    size_t la = strlen(a), lb = strlen(b), n = la < lb ? la : lb, i;
    unsigned char diff = (la != lb);

    for (i = 0; i < n; i++)
        diff |= (unsigned char)a[i] ^ (unsigned char)b[i];
    return diff == 0;
}

/* Рядок файлу: <користувач>:<запитання>:<слово>
   Повертає 0 — знайдено, -1 — запису немає, -2 — файл недоступний. */
static int lookup(const char *path, const char *user,
                  char *q, size_t qn, char *a, size_t an)
{
    char line[512], *nl, *c1, *c2;
    int found = -1;
    /* 'e' — O_CLOEXEC: процес, у якому ми виконуємось, зараз піде в exec(),
       і відкритий дескриптор до файлу секретів дістався б чужій оболонці. */
    FILE *f = fopen(path, "re");

    if (f == NULL)
        return -2;
    while (fgets(line, sizeof line, f) != NULL) {
        if ((nl = strchr(line, '\n')) != NULL) *nl = '\0';
        if ((c1 = strchr(line, ':')) == NULL) continue;
        *c1 = '\0';
        if (strcmp(line, user) != 0) continue;
        if ((c2 = strchr(c1 + 1, ':')) == NULL) break;
        *c2 = '\0';
        snprintf(q, qn, "%s", c1 + 1);
        snprintf(a, an, "%s", c2 + 1);
        found = 0;
        break;
    }
    explicit_bzero(line, sizeof line);
    fclose(f);
    return found;
}

int pam_sm_authenticate(pam_handle_t *pamh, int flags, int argc, const char **argv)
{
    const char *path = "/etc/security/riddle.conf";
    const char *user = NULL;
    const void *item = NULL;
    char question[256], expected[256], prompt[320];
    char *pw = NULL, *answer = NULL;
    int soft = 0, rc, i;

    (void)flags;
    for (i = 0; i < argc; i++) {          /* власні аргументи з рядка налаштувань */
        if (strncmp(argv[i], "answers=", 8) == 0)  path = argv[i] + 8;
        else if (strcmp(argv[i], "soft") == 0)     soft = 1;
        else pam_syslog(pamh, LOG_WARNING, "невідомий аргумент «%s»", argv[i]);
    }

    rc = pam_get_user(pamh, &user, NULL);
    if (rc != PAM_SUCCESS || user == NULL || *user == '\0')
        return PAM_USER_UNKNOWN;

    switch (lookup(path, user, question, sizeof question,
                   expected, sizeof expected)) {
    case 0:
        break;
    case -1:                                    /* конверта цій людині не давали */
        return soft ? PAM_IGNORE : PAM_USER_UNKNOWN;
    default:                                    /* файл є, а прав його читати — нема */
        pam_syslog(pamh, LOG_ERR, "%s: %m", path);
        return PAM_CRED_INSUFFICIENT;
    }

    /* Пароль: якщо його вже спитав попередній модуль — беремо готовий. */
    rc = pam_get_item(pamh, PAM_AUTHTOK, &item);
    if (rc == PAM_SUCCESS && item != NULL) {
        if ((pw = strdup(item)) == NULL) { rc = PAM_BUF_ERR; goto out; }
    } else {
        if ((rc = ask(pamh, "Password: ", &pw)) != PAM_SUCCESS)
            goto out;
        /* Кладемо наступним. libpam робить власну копію — наша лишається наша. */
        pam_set_item(pamh, PAM_AUTHTOK, pw);
    }

    snprintf(prompt, sizeof prompt, "%s: ", question);
    if ((rc = ask(pamh, prompt, &answer)) != PAM_SUCCESS)
        goto out;

    if (!same_secret(answer, expected)) {
        pam_syslog(pamh, LOG_NOTICE, "хибне контрольне слово, користувач %s", user);
        rc = PAM_AUTH_ERR;
        goto out;
    }
    rc = PAM_SUCCESS;   /* пароль звірить наступний рядок стеку */
out:
    wipe(&pw);
    wipe(&answer);
    explicit_bzero(expected, sizeof expected);
    return rc;
}

/* Другий обов'язковий символ auth-стеку. Облікових даних ми не видаємо —
   але мовчати не можна, бо відсутній символ читається як зламаний модуль. */
int pam_sm_setcred(pam_handle_t *pamh, int flags, int argc, const char **argv)
{
    (void)pamh; (void)flags; (void)argc; (void)argv;
    return PAM_SUCCESS;
}
