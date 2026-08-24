# ⚙️ Власний модуль PAM: пароль плюс контрольне запитання

Модуль на C, що додає до пароля друге запитання й впускає лише за двох правильних відповідей — сотня рядків, на яких видно весь інтерфейс модуля: як бібліотека знаходить ваші функції, як спитати людину, не знаючи, де вона сидить, і чому половина роботи — це вибір коду повернення.

## Задача

В установі роздали паперові конверти з контрольним словом. Вимога: на серверах, крім пароля, питати ще й це слово, а впускати лише тоді, коли правильні обидві відповіді. Ані `sshd`, ані `login`, ані `sudo` не переписуємо й не перезбираємо.

## Що саме бібліотека шукає у вашому файлі

Модуль — звичайний спільний об'єкт. `libpam` відкриває його через `dlopen()` і бере з нього функції за іменем — тим самим механізмом, яким будь-яка програма дістає символ із підвантаженої бібліотеки ([динамічний завантажувач](topic:unix-linux/dynamic-loader) знаходить символ у таблиці за іменем уже під час роботи). Ніякої таблиці реєстрації, ніякого «головного» символу немає: імена жорстко домовлені, і кожне обслуговує свій тип стеку.

| тип стеку | символи, які шукає бібліотека |
|---|---|
| `auth` | `pam_sm_authenticate` **і** `pam_sm_setcred` |
| `account` | `pam_sm_acct_mgmt` |
| `password` | `pam_sm_chauthtok` |
| `session` | `pam_sm_open_session` і `pam_sm_close_session` |

Символа немає — виклик не провалюється тихо: бібліотека повертає для цього рядка `PAM_MODULE_UNKNOWN`. Звідси перша пастка новачка, і вона коштує вечора: пишуть саму лише `pam_sm_authenticate`, пароль сходиться, а `login` усе одно відмовляє — бо після вдалої автентифікації він викликає `pam_setcred()`, і в цьому стеку ваш модуль виглядає зламаним.

Підпис в усіх однаковий:

```c
int pam_sm_authenticate(pam_handle_t *pamh, int flags, int argc, const char **argv);
```

`argv` — це **ваші** аргументи з рядка `/etc/pam.d`, уже порізані на слова. Вони належать бібліотеці: не міняти й не звільняти.

## Розподіл роботи

Пароль наш модуль не перевіряє, і це принципово. Хеш лежить у `/etc/shadow`, доступному тільки `root`, а модуль виконується з правами того процесу, що його покликав, — заставка робочого столу таких прав не має. Тому робимо так: наш модуль питає пароль, кладе його в елемент `PAM_AUTHTOK` і питає контрольне слово, яке звіряє сам; звіряння пароля лишається наступному рядку стеку. Кон'юнкція «і те, і те» пишеться не в C, а у файлі служби — двома `required`.

```c
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
```

## Чотири коди повернення, і жоден не зайвий

Найважча частина модуля — не код, а рішення, що саме сказати назовні. Кожен код означає різне питання до адміністратора, і плутанина тут дорого коштує.

`PAM_AUTH_ERR` — «я перевірив і не сходиться». `PAM_USER_UNKNOWN` — «я про цю людину нічого не знаю»; він відрізняється від попереднього тим, що перевірки не було взагалі. `PAM_CRED_INSUFFICIENT` — «перевірити не вдалося, бо в самого процесу бракує прав»: рівно наш випадок, коли файл конвертів `0640 root:root`, а модуль викликали з-під заставки. Адміністратор може написати `[cred_insufficient=ignore]` і свідомо дозволити графічному розблокуванню обійтися без другого запитання, а для `sshd` лишити суворо.

Окремо стоїть `PAM_IGNORE`, і плутають його саме з `PAM_SUCCESS`. Він не означає «добре» — він означає «не рахуйте мене»: бібліотека викидає цей результат зі зведення, ніби рядка не було. Різниця стає видимою в крайньому випадку: якщо **всі** модулі стеку відповіли `PAM_IGNORE`, зводити нема чого, і `libpam` повертає `PAM_PERM_DENIED`. Тобто мовчання всього стеку — це відмова, а не згода. Модуль, який у сумнівному випадку повертає `PAM_SUCCESS` замість `PAM_IGNORE`, тихо перетворює «мене це не стосується» на «я за нього ручаюся» — і сам стає єдиною підставою впустити.

## Збірка й прогін, який не замикає вас іззовні

Пробувати одразу на `/etc/pam.d/sshd` — найкоротший шлях лишитися без сервера. Правильно завести окрему службу, якою не входять нікуди:

```
# /etc/security/riddle.conf   (chown root:root, chmod 0640)
alice:Вулиця з дитинства:каштанова

# /etc/pam.d/riddle-test
auth  required  pam_riddle.so answers=/etc/security/riddle.conf
auth  required  pam_unix.so   use_first_pass
```

```
$ cc -O2 -Wall -Wextra -fPIC -shared -o pam_riddle.so pam_riddle.c -lpam
$ sudo install -m 0644 pam_riddle.so /usr/lib/x86_64-linux-gnu/security/
$ sudo pamtester -v riddle-test alice authenticate
```

`pamtester` (однойменний пакунок) робить рівно те, що робив би `login`: відкриває розмову за іменем служби, сам малює запити в терміналі й друкує підсумковий код. Служба окрема, тож зіпсований модуль не чіпає вхід у систему. Другий прогін — **без** `sudo`: ви маєте побачити не «пароль хибний», а саме `PAM_CRED_INSUFFICIENT`, бо файл конвертів звичайному користувачеві не читається. Це не поразка, це перевірка того, що модуль чесно розрізняє «не сходиться» і «не зміг». Свої рядки `pam_syslog()` дивіться в [журналі](topic:unix-linux/journald-logging): `journalctl -f`.

Коли модуль справді має працювати й без прав, шлях один — маленька програма-помічник із [бітом підвищення прав](topic:unix-linux/setuid-and-privilege), яка читає секрет і віддає назовні один біт «сходиться / ні». Саме так влаштований `unix_chkpwd`, і саме тому він існує окремо від `pam_unix.so`.

## Пастки

**Розмовник, а не термінал.** Усе, що людина набирає, приходить через `conv` — модуль не має ані `stdin`, ані права відкрити `/dev/tty`. Наслідок стосується й виводу: `printf()` із модуля всередині `sshd` пише в дескриптор, яким іде сам протокол, і псує з'єднання. Для діагностики є `pam_syslog()`, і тільки він. Симетрично: `conv` цілком законно повертає `PAM_CONV_ERR`, коли співрозмовника немає взагалі (задача з `cron`) — це не привід уважати відповідь порожньою й пускати далі.

**Чекання без стелі.** Наш модуль читає локальний файл, але щойно другий чинник поїде в мережу, зависання перетвориться на зависання **програми входу** — рятувати нікому. Ставте явний строк на сокеті чи в `poll()` ([читання з обмеженням часу](topic:unix-linux/blocking-and-nonblocking)) і ніколи не чіпайте з модуля `alarm()` чи `signal()`: [диспозиція сигналів](topic:unix-linux/signal-disposition) належить програмі-господарю, і збита нею вона лишиться збитою після вашого повернення.

**Пам'ять.** Масив `pam_response` і кожен рядок у ньому виділив розмовник, а звільняє їх модуль — інших власників немає. У коді вище на кожній гілці виходу стоїть `wipe()`, і саме тому там `goto out`, а не десяток окремих `return`. Витік у пів кілобайта здається дрібницею, поки модуль живе в короткому `sudo`; у заставці, яку не перезапускають тижнями й смикають на кожне розблокування, він назбирується. Дешева перевірка — `valgrind --leak-check=full pamtester …`.

**Стале порівняння.** `strcmp()` виходить на першому розбіжному байті, тож час відповіді підказує, скільки початкових літер вгадано, — за цим слово добирається за десятки спроб замість мільйонів ([атака за часом](topic:programming/timing-attack)). `same_secret()` вище лишає назовні тільки довжину.

**Ціна помилки.** Модуль виконується всередині чужого процесу, часто з правами `root`: розіменований нульовий вказівник тут — не падіння вашої програми, а падіння `login` або `sshd`. Тому кожен `pam_get_item()` перевіряється на `NULL`, а невідомий стан завершується відмовою — ніколи `PAM_SUCCESS`.
