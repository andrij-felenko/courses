/* keydemo.c — cc -Wall -O2 keydemo.c -o keydemo -lkeyutils */
#include <keyutils.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static void die(const char *what) { perror(what); exit(1); }

/* 1. Кладемо секрет своїми руками. */
static key_serial_t step_add(void)
{
    static const char secret[] = "s3cr3t-token";

    key_serial_t k = add_key("user", "demo:token",
                             secret, sizeof secret - 1,
                             KEY_SPEC_SESSION_KEYRING);
    if (k == -1) die("add_key");

    char *d = NULL;
    if (keyctl_describe_alloc(k, &d) < 0) die("describe");
    printf("[1] створено %d  %s\n", k, d);
    free(d);

    void *buf = NULL;
    long n = keyctl_read_alloc(k, &buf);
    if (n < 0) die("read");
    printf("[1] прочитано %ld Б: %.*s\n", n, (int)n, (char *)buf);
    free(buf);
    return k;
}

/* 2. Ключа немає — хай ядро сходить по нього назовні. */
static void step_request(void)
{
    key_serial_t k = request_key("user", "demo:remote",
                                 "who=demo", KEY_SPEC_SESSION_KEYRING);
    if (k == -1) die("request_key");

    void *buf = NULL;
    long n = keyctl_read_alloc(k, &buf);
    if (n < 0) die("read");
    printf("[2] помічник дав %d, %ld Б: %.*s\n", k, n, (int)n, (char *)buf);
    free(buf);

    /* удруге — уже з кільця; callout_info == NULL забороняє виклик назовні */
    printf("[2] удруге: %d\n",
           request_key("user", "demo:remote", NULL, KEY_SPEC_SESSION_KEYRING));

    /* опис, на який помічник відповідає відмовою */
    if (request_key("user", "demo:forbidden", "who=demo",
                    KEY_SPEC_SESSION_KEYRING) == -1)
        printf("[2] demo:forbidden -> %s\n", strerror(errno));
}

/* 3. Той самий UID, той самий номер — інші права. */
static void step_lose(key_serial_t k)
{
    /* без цього посилання ключ помре разом зі старим кільцем сеансу */
    if (keyctl_link(k, KEY_SPEC_USER_KEYRING) < 0) die("link");

    key_serial_t ses = keyctl_join_session_keyring(NULL);
    if (ses == -1) die("join_session_keyring");
    printf("[3] новий сеанс %d, uid лишився %d\n", ses, (int)getuid());

    char *d = NULL;
    if (keyctl_describe_alloc(k, &d) < 0)
        printf("[3] describe -> %s\n", strerror(errno));
    else { printf("[3] describe -> %s\n", d); free(d); }

    void *buf = NULL;
    if (keyctl_read_alloc(k, &buf) < 0)
        printf("[3] read     -> %s\n", strerror(errno));
    else free(buf);

    if (keyctl_search(KEY_SPEC_SESSION_KEYRING, "user", "demo:token", 0) == -1)
        printf("[3] search   -> %s\n", strerror(errno));
}

int main(void)
{
    key_serial_t k = step_add();
    step_request();
    step_lose(k);
    return 0;
}
