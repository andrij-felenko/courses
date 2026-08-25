# ⚙️ Перевірка логіна й пароля через каталог: код, у якому порожній пароль не проходить

Функція, яка на пару «логін і пароль» питає каталог LDAP, вміщається у сто п'ятдесят рядків — і рівно в цих рядках живуть чотири місця, де недбалість перетворює перевірку на її імітацію: bind, який сервер вважає успішним, хоч пароля не бачив; фільтр, у який вводом можна дописати своє; кілька записів на один логін; і мовчанка мережі, порахована за «пароль неправильний». Нижче — робочий код і кожне з цих місць окремо.

## Функція, яка повертає не «так чи ні»

Перше рішення ухвалюється ще до першого рядка — яким буде тип відповіді. Спокуса написати `bool` коштує дорого, бо `false` склеює докупи речі, які поводяться геть по-різному: «пароль не той» — це відмова людині, а «каталог не відповів» — це збій служби, після якого не можна ні впустити, ні впевнено відмовити. Склеївши їх, ви дістаєте систему, у якій обрив мережі виглядає як масова спроба зламу, а спроба зламу тоне серед мережевих збоїв.

Тому відповідей п'ять: пароль правильний; запис є, але пароль не підійшов; такого логіна немає; логін збігся з кількома записами; каталог недосяжний. Останні три — не варіації відмови, це різні події з різними наслідками для того, хто цю функцію викликав.

> 🔧 **Навіщо це.** Саме розрізнення «немає такого» і «не спитали» шар NSS у Linux несе окремими статусами, а не одним нулем. Клієнт, що не вміє його зробити, обвалює систему в найгіршу мить: каталог зник — і машина відповідає, що користувачів не існує.

## Три речі, які роблять до того, як торкнутися мережі

**Порожній пароль треба відкинути самому.** Simple bind із непорожнім DN і паролем **нульової довжини** — це, за протоколом, не помилка й не спроба з хибним секретом. RFC 4513 (червень 2006) називає таке в §5.1.2 неавтентифікованим механізмом простого прив'язування й прямо каже, що ім'я в такому запиті «не автентифікується й не перевіряється» і для авторизації не годиться — ні прямо, ні опосередковано. Той самий розділ радить клієнтам не пускати порожній пароль далі поля вводу, а серверам — типово відповідати на такий bind кодом `unwillingToPerform`. Слово «типово» тут не гарантія: код, який покладеться на сервер, працює доти, доки хтось не змінить налаштування. Перевірка коштує пару рядків і мусить стояти в клієнті — і на пароль людини, і на пароль службового запису, бо порожній службовий пароль так само мовчки перетворює всю подальшу роботу на анонімну; відповідь на нього тільки інша — це не відмова людині, а несправність служби.

**Логін не можна класти у фільтр як є.** Фільтр — це рядок із власним синтаксисом, і `uid=` в ньому лише частина виразу. Логін `*` перетворює `(uid=*)` на «будь-хто», а логін `andrij)(uid=root` розриває дужки й дописує свою умову. RFC 4515 (червень 2006) визначає, що п'ять октетів у значенні мусять їхати екранованими: `*` → `\2a`, `(` → `\28`, `)` → `\29`, `\` → `\5c` і NUL → `\00`. Екранування робиться над **байтами**, а не над символами, і саме тому воно безпечне для UTF-8: жоден із цих п'яти октетів не трапляється всередині багатобайтового символу.

**Тайм-аути ставлять руками.** Каталог — це мережа, а в сокеті немає такої речі, як тайм-аут на з'єднання: `connect(2)` або блокує до відповіді ядра, або його роблять неблокуючим і чекають окремо. Бібліотека робить саме друге: `LDAP_OPT_NETWORK_TIMEOUT` — це час, після якого `poll(2)` за неблокуючим [connect](root:sys-unix/socket-api-linux) здається, а `LDAP_OPT_TIMEOUT` обмежує синхронні виклики. Без них перевірка логіна успадковує тайм-аути TCP і вміє висіти хвилинами.

## Код

Один і той самий алгоритм: спільна частина з'єднання (тайм-аути, StartTLS із перевіркою сертифіката), службовий bind, пошук за екранованим фільтром, DN — і другий bind на **окремому** з'єднанні. Двох опцій навколо сертифіката тут не уникнути: [шифрування](root:sf-security/tls) без звіряння підпису віддає пароль будь-кому, хто став на місце сервера, а звіряння підпису без звіряння імені пускає будь-який чесний сертифікат — байдуже, кому виданий.

:::tabs

```c
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
```

```python
# ldapauth.py — той самий алгоритм на ldap3.  pip install ldap3
import ssl
from enum import Enum

from ldap3 import SIMPLE, SUBTREE, Connection, Server, Tls
from ldap3.core.exceptions import (LDAPException, LDAPInvalidCredentialsResult,
                                   LDAPSizeLimitExceededResult)
from ldap3.utils.conv import escape_filter_chars

HOST    = 'ldap.corp.example'
CA_FILE = '/etc/ssl/certs/corp-ca.pem'
BASE_DN = 'ou=people,dc=corp,dc=example'
SVC_DN  = 'cn=login-check,ou=services,dc=corp,dc=example'


class Auth(Enum):
    OK = 'ok'
    DENIED = 'denied'
    NO_ENTRY = 'no-entry'
    AMBIGUOUS = 'ambiguous'
    UNAVAILABLE = 'unavailable'


def _server() -> Server:
    # validate за замовчуванням — ssl.CERT_NONE: сертифікат ніхто не звірятиме,
    # доки цього не написати руками. valid_names — окрема вимога: підпис
    # правильний ще не означає, що це той сервер.
    tls = Tls(validate=ssl.CERT_REQUIRED, ca_certs_file=CA_FILE,
              valid_names=[HOST])
    return Server(HOST, port=389, use_ssl=False, tls=tls, connect_timeout=5)


def _connect(dn: str, password: str) -> Connection:
    conn = Connection(_server(), user=dn, password=password,
                      authentication=SIMPLE, raise_exceptions=True,
                      receive_timeout=5)
    conn.open()        # TCP; тут же спрацює connect_timeout
    conn.start_tls()   # шифрування до того, як на дріт потрапить пароль
    conn.bind()        # і аж тепер пароль
    return conn        # кроки розписані навмисно: auto_bind згортає будь-який
                       # збій в одну помилку, а нам потрібен саме код 49


def check_login(login: str, password: str, svc_password: str) -> Auth:
    # RFC 4513 §5.1.2: порожній пароль — не хибний секрет, а неавтентифіковане
    # прив'язування. Відкидаємо ДО мережі й для обох паролів — але порожній
    # службовий пароль це наша несправність, а не відмова людині.
    if not svc_password:
        return Auth.UNAVAILABLE
    if not login or not password:
        return Auth.DENIED

    query = '(&(objectClass=posixAccount)(uid=%s))' % escape_filter_chars(login)
    try:
        with _connect(SVC_DN, svc_password) as svc:
            svc.search(BASE_DN, query, search_scope=SUBTREE, size_limit=2)
            found = [r for r in (svc.response or [])
                     if r.get('type') == 'searchResEntry']
            if not found:
                return Auth.NO_ENTRY
            if len(found) > 1:
                return Auth.AMBIGUOUS
            user_dn = found[0]['dn']
    except LDAPSizeLimitExceededResult:
        return Auth.AMBIGUOUS
    except LDAPException:            # і недосяжність, і збій TLS, і брак прав
        return Auth.UNAVAILABLE

    try:
        with _connect(user_dn, password):
            return Auth.OK
    except LDAPInvalidCredentialsResult:
        return Auth.DENIED
    except LDAPException:
        return Auth.UNAVAILABLE
```

:::

## Як читати те, що повернув сервер

Відображення кодів на відповідь — це і є місце, де більшість реалізацій втрачає різницю між «ні» і «не знаю».

| Що сталося | Код | Відповідь функції |
|---|---|---|
| другий bind удався | `LDAP_SUCCESS` (0) | `AUTH_OK` |
| другий bind відкинуто | `LDAP_INVALID_CREDENTIALS` (49) | `AUTH_DENIED` |
| пошук повернув нуль записів | `LDAP_SUCCESS` (0) | `AUTH_NO_ENTRY` |
| записів більше одного | `LDAP_SIZELIMIT_EXCEEDED` (4) | `AUTH_AMBIGUOUS` |
| сервер відмовився виконувати | `LDAP_UNWILLING_TO_PERFORM` (53) | `AUTH_UNAVAILABLE` |
| немає з'єднання, немає відповіді | `LDAP_SERVER_DOWN` (−1), `LDAP_TIMEOUT` (−5), `LDAP_CONNECT_ERROR` (−11), `LDAP_UNAVAILABLE` (52), `LDAP_BUSY` (51) | `AUTH_UNAVAILABLE` |

Від'ємні коди — не з протоколу: так OpenLDAP позначає біду на боці клієнта, до якої сервер стосунку не має. Змішувати їх із кодами відповіді не можна саме тому, що вони означають протилежне: код 49 приніс сервер, який нас вислухав, а `−1` означає, що нас ніхто не слухав.

Окремо варто помітити `unwillingToPerform`. Це саме те, чим сервер, налаштований за порадою RFC 4513, відповідає на неавтентифікований bind. Побачивши цей код, ви бачите не пароль користувача, а власну помилку — кудись просочився порожній рядок.

## Чому DN не збирають із логіна

Пошук виглядає зайвим кроком: якщо записи лежать у `ou=people`, то DN нібито складається з логіна одним рядком — `uid=andrij,ou=people,dc=corp,dc=example`. Спокуса економить один обмін із сервером і коштує двох речей.

Перша: розкладка каталогу — не ваша власність. Записи можуть лежати в підгілках за підрозділами, ключем може виявитися не `uid`, а `cn` чи `sAMAccountName`, а після злиття двох установ частина людей опиниться в іншому піддереві. Шаблон почне мовчки не знаходити тих, кого каталог знає.

Друга серйозніша. Екранування фільтра тут не працює: DN — це інший синтаксис з іншим набором спецсимволів (кома, знак рівності, плюс, лапки, кутові дужки), і правила його екранування описує окремий документ, RFC 4514. Хто вставив логін у шаблон DN, замість однієї ін'єкції дістав другу, а перевіряє й далі лише від першої. Пошук знімає обидва питання разом: DN приходить від сервера вже готовим і синтаксично правильним — його не треба ні складати, ні екранувати.

Умова `(&(objectClass=posixAccount)…)` у фільтрі — з тієї ж родини обережності. Без неї `uid` збігається з чим завгодно, що має цей атрибут: із записом машини, зі службовим записом, із групою. Одна така знахідка — і людина заходить під записом, який людиною не є.

## Чому bind людини — на окремому з'єднанні

Bind не «перевіряє пароль», а **міняє особу сесії**. Тому другий bind на тому самому дескрипторі знищив би прив'язку службового запису: з'єднання перестало б бути службовим і стало б з'єднанням користувача — або, якщо пароль хибний і сервер це дозволяє, взагалі анонімним. Наступний пошук пішов би вже з іншими правами й тихо повернув би менше, ніж мав.

Звідси й порядок звільнення в коді: спершу друге з'єднання, потім перше. І звідси ж головна ціна цього алгоритму — з'єднань завжди два.

## Скільки це коштує

**Умова.** TLS 1.3, каталог у своїй мережі (RTT ≈ 1 мс) і каталог за океаном (RTT ≈ 40 мс).

```
з'єднання 1: TCP 1 + StartTLS 1 + TLS 1.3 1 + bind 1 + search 1 = 5 RTT
з'єднання 2: TCP 1 + StartTLS 1 + TLS 1.3 1 + bind 1            = 4 RTT
разом                                                           = 9 RTT

своя мережа   9 · 1 мс  =   9 мс
через океан   9 · 40 мс = 360 мс
```

На TLS 1.2 рукостискання коштує два RTT замість одного, і сума росте до одинадцяти. У цій арифметиці немає ще однієї затримки — розв'язання імені `ldap.corp.example`: воно не покривається жодним із двох тайм-аутів бібліотеки й живе за [власними правилами](root:sys-unix/name-resolution-path). Триста шістдесят мілісекунд на кожен `sudo` — це той поріг, за яким кеш перестає бути оптимізацією.

## Чого цей код не робить

**Не вирішує, чи людині можна заходити.** Успішний bind означає рівно одне: пароль правильний. Чи не заблокований запис, чи не сплив термін дії пароля, чи не заборонено вхід у цю годину — окремі питання, і в Linux на них відповідає не автентифікація, а фаза `account` [стеку PAM](root:sys-unix/pam-stack).

**Не рахує спроби.** Функція, яку можна викликати без обмежень, — це онлайновий оракул паролів: зловмиснику не треба красти хеші, коли можна питати. [Обмеження швидкості](root:sf-security/rate-limiting) мусить стояти зовні, і бажано не лише на боці клієнта.

**Розрізняє більше, ніж можна показувати.** `AUTH_NO_ENTRY` і `AUTH_DENIED` потрібні журналу й системі, але не екрану: показавши їх окремо, ви даруєте кожному охочому спосіб перебрати логіни. Різниця в часі відповіді робить те саме тихіше — «немає такого» повертається на цілий bind швидше.

**Не переживає зникнення каталогу.** Кеша тут немає, і машина без мережі не впустить нікого, включно з тим, хто заходив хвилину тому. Саме тому в справжній системі цей код не вбудовують у програму й не чіпляють до `nsswitch.conf` — його вже написали в [SSSD](root:sys-unix/sssd), разом із кешем, повторними спробами й збереженими перевірками входу.

І останнє. Усе вище потрібне тому, що пароль їде дротом. Bind уміє й інакше: механізм SASL із GSSAPI приносить замість пароля [квиток Kerberos](root:sf-security/kerberos-authentication), і тоді питання «чи перевірили ми сертифікат» втрачає гостроту разом із самим паролем — його на дроті просто немає. Але доки в системі є поле для введення пароля, є й ці сто п'ятдесят рядків, і кожен `if` у них стоїть не просто так.
