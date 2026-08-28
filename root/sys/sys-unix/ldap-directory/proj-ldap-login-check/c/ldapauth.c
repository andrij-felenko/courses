// ldapauth.c — перевірка логіна й пароля через каталог LDAP.
// cc -O2 -Wall -o ldapauth ldapauth.c -lldap -llber

#define _GNU_SOURCE
#include <ldap.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>

typedef enum {
    AUTH_OK,          /* пароль правильний                        */
    AUTH_DENIED,      /* запис є, пароль не підійшов              */
    AUTH_NO_ENTRY,    /* такого логіна в каталозі немає           */
    AUTH_AMBIGUOUS,   /* логін збігся з кількома записами         */
    AUTH_UNAVAILABLE  /* каталог не відповів — це НЕ відмова      */
} auth_result;

static char *const URI     = "ldap://ldap.corp.example";
static char *const CA_FILE = "/etc/ssl/certs/corp-ca.pem";
static char *const BASE_DN = "ou=people,dc=corp,dc=example";
static char *const SVC_DN  = "cn=login-check,ou=services,dc=corp,dc=example";

/* RFC 4515: у значенні фільтра ці п'ять октетів мусять їхати як \XX.
   Працюємо з байтами й явною довжиною — усередині UTF-8 їх не буває. */
static char *filter_escape(const char *s, size_t n)
{
    char *out = malloc(n * 3 + 1);
    if (!out) return NULL;
    size_t j = 0;
    for (size_t i = 0; i < n; i++) {
        unsigned char c = (unsigned char)s[i];
        if (c == '*' || c == '(' || c == ')' || c == '\\' || c == '\0')
            j += (size_t)sprintf(out + j, "\\%02x", c);
        else
            out[j++] = (char)c;
    }
    out[j] = '\0';
    return out;
}

/* Спільна частина обох з'єднань. */
static int open_tls(LDAP **out)
{
    LDAP *ld = NULL;
    int rc = ldap_initialize(&ld, URI);   /* сокета ще немає: лише дескриптор */
    if (rc != LDAP_SUCCESS) return rc;

    int ver = LDAP_VERSION3;
    ldap_set_option(ld, LDAP_OPT_PROTOCOL_VERSION, &ver);

    /* Referral під час bind відправив би пароль серверу, якого ми не вибирали. */
    ldap_set_option(ld, LDAP_OPT_REFERRALS, LDAP_OPT_OFF);

    struct timeval net = { .tv_sec = 5, .tv_usec = 0 };  /* connect            */
    struct timeval op  = { .tv_sec = 5, .tv_usec = 0 };  /* синхронні виклики  */
    ldap_set_option(ld, LDAP_OPT_NETWORK_TIMEOUT, &net);
    ldap_set_option(ld, LDAP_OPT_TIMEOUT, &op);

    int require = LDAP_OPT_X_TLS_HARD;   /* сертифікат обов'язковий і має сходитись */
    ldap_set_option(ld, LDAP_OPT_X_TLS_CACERTFILE, CA_FILE);
    ldap_set_option(ld, LDAP_OPT_X_TLS_REQUIRE_CERT, &require);
    int newctx = 0;   /* без цього рядка два попередні лишаться в старому
                         TLS-контексті й на це з'єднання не вплинуть */
    ldap_set_option(ld, LDAP_OPT_X_TLS_NEWCTX, &newctx);

    rc = ldap_start_tls_s(ld, NULL, NULL);   /* саме тут відбувається connect */
    if (rc != LDAP_SUCCESS) {
        ldap_unbind_ext_s(ld, NULL, NULL);
        return rc;
    }
    *out = ld;
    return LDAP_SUCCESS;
}

static int simple_bind(LDAP *ld, const char *dn, const char *pw, size_t pwlen)
{
    struct berval cred = { .bv_len = pwlen, .bv_val = (char *)pw };
    return ldap_sasl_bind_s(ld, dn, LDAP_SASL_SIMPLE, &cred, NULL, NULL, NULL);
}

auth_result directory_check_login(const char *login, size_t loginlen,
                                  const char *pw,    size_t pwlen,
                                  const char *svcpw, size_t svcpwlen)
{
    LDAP *ld = NULL, *ld2 = NULL;
    LDAPMessage *res = NULL, *e = NULL;
    char *esc = NULL, *user_dn = NULL;
    char *attrs[] = { LDAP_NO_ATTRS, NULL };   /* потрібен лише DN */
    char filter[512];
    auth_result answer = AUTH_UNAVAILABLE;
    int rc, n;

    /* ПЕРША перевірка — до будь-якої мережі. Порожній пароль у simple bind
       за RFC 4513 §5.1.2 — це неавтентифіковане прив'язування: сервер має
       право відповісти success, не перевіривши нічого. */
    if (svcpwlen == 0) return AUTH_UNAVAILABLE;   /* не відмова людині,
                                                     а несправність служби */
    if (loginlen == 0 || pwlen == 0)
        return AUTH_DENIED;

    if (open_tls(&ld) != LDAP_SUCCESS) return AUTH_UNAVAILABLE;
    if (simple_bind(ld, SVC_DN, svcpw, svcpwlen) != LDAP_SUCCESS)
        goto out;                       /* це наша біда, а не людини */

    esc = filter_escape(login, loginlen);
    if (!esc) goto out;
    n = snprintf(filter, sizeof filter,
                 "(&(objectClass=posixAccount)(uid=%s))", esc);
    if (n < 0 || (size_t)n >= sizeof filter) { answer = AUTH_DENIED; goto out; }

    /* sizelimit = 2: одного запису досить, другий потрібен лише для того,
       щоб побачити неоднозначність, а не вгадувати її. */
    struct timeval tv = { .tv_sec = 5, .tv_usec = 0 };
    rc = ldap_search_ext_s(ld, BASE_DN, LDAP_SCOPE_SUBTREE, filter, attrs, 0,
                           NULL, NULL, &tv, 2, &res);
    if (rc == LDAP_SIZELIMIT_EXCEEDED) { answer = AUTH_AMBIGUOUS; goto out; }
    if (rc != LDAP_SUCCESS)            { answer = AUTH_UNAVAILABLE; goto out; }

    switch (ldap_count_entries(ld, res)) {
    case 0:  answer = AUTH_NO_ENTRY;  goto out;
    case 1:  break;
    default: answer = AUTH_AMBIGUOUS; goto out;
    }

    e = ldap_first_entry(ld, res);
    user_dn = ldap_get_dn(ld, e);           /* DN дає сервер, не ми */
    if (!user_dn) goto out;

    /* Друге з'єднання: цей bind міняє особу сесії, і робити його на робочій
       сесії службового запису не можна. */
    if (open_tls(&ld2) != LDAP_SUCCESS) goto out;
    rc = simple_bind(ld2, user_dn, pw, pwlen);
    if (rc == LDAP_SUCCESS)                  answer = AUTH_OK;
    else if (rc == LDAP_INVALID_CREDENTIALS) answer = AUTH_DENIED;
    else                                     answer = AUTH_UNAVAILABLE;

out:
    if (user_dn) ldap_memfree(user_dn);
    if (res)     ldap_msgfree(res);
    if (esc)     free(esc);
    if (ld2)     ldap_unbind_ext_s(ld2, NULL, NULL);
    if (ld)      ldap_unbind_ext_s(ld, NULL, NULL);
    return answer;
}

int main(int argc, char **argv)
{
    if (argc != 2) { fprintf(stderr, "usage: ldapauth <логін>\n"); return 2; }

    char *pw = NULL, *svc = NULL;
    size_t pcap = 0, scap = 0;
    FILE *f = fopen("/etc/login-check.secret", "r");   /* режим 0600 */
    if (!f) { perror("secret"); return 3; }
    ssize_t slen = getline(&svc, &scap, f);
    fclose(f);
    ssize_t plen = getline(&pw, &pcap, stdin);  /* у справжній програмі —
                                                   без відлуння в терміналі */
    if (plen > 0 && pw[plen - 1]  == '\n') pw[--plen]   = '\0';
    if (slen > 0 && svc[slen - 1] == '\n') svc[--slen]  = '\0';
    if (plen < 0 || slen < 0) return 3;

    auth_result r = directory_check_login(argv[1], strlen(argv[1]),
                                          pw, (size_t)plen,
                                          svc, (size_t)slen);
    explicit_bzero(pw, (size_t)plen);       /* memset тут вирізав би оптимізатор */
    explicit_bzero(svc, (size_t)slen);
    free(pw); free(svc);

    static const char *name[] = { "OK", "DENIED", "NO_ENTRY",
                                  "AMBIGUOUS", "UNAVAILABLE" };
    puts(name[r]);
    return r == AUTH_OK ? 0 : 1;
}
