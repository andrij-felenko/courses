# ⚙️ Ключ у роботі: покласти, добути помічником, втратити тримання

Сотня рядків на C, після яких три речі перестають бути теорією: як секрет потрапляє в ядро, як ядро саме́ йде по ключ у простір користувача, коли ключа немає, і як той самий процес під тим самим UID за одну дію втрачає право на власний ключ. Програма справжня — збирається й запускається на звичайному Linux, і перші два кроки не потребують прав `root`.

## Збірка й обстановка

Обгорток для `add_key`, `request_key` і `keyctl` у glibc немає — рідкісний випадок, коли [стандартна бібліотека C](root:sys-unix/libc-as-gateway), що зазвичай прикриває кожен системний виклик однойменною функцією, цього не робить, і йти до ядра треба або самотужки через `syscall()`, або чужою бібліотекою. Беремо другий шлях, бо `libkeyutils` заодно дає зручні `keyctl_*`-обгортки з виділенням буфера:

```
Debian/Ubuntu:  apt install libkeyutils-dev keyutils
Fedora/RHEL:    dnf install keyutils-libs-devel keyutils

cc -Wall -O2 keydemo.c -o keydemo -lkeyutils
```

Запускати краще так: `keyctl session - ./keydemo`. Це створює безіменне кільце сеансу лише на час прогону — інакше, якщо у вашому вході не спрацював `pam_keyinit`, «кільцем сеансу» виявиться спільне кільце користувача, і демонстраційні ключі житимуть далі в усіх ваших терміналах.

## Програма

```c
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
```

Два місця тут неочевидні. Перше — `keyctl_link` на початку третього кроку: він не для краси. Ключ живе, доки на нього веде хоч одне посилання, а ми зараз покинемо єдине кільце, яке його тримає; без посилання на кільце користувача ключ став би нічийним і третій крок показав би нудне «немає такого» замість цікавої відмови. Друге — `callout_info == NULL` у повторному `request_key`: із таким аргументом виклик назовні заборонено, тож якщо ключ знайдено, то знайдено на кільці, а не добуто вдруге.

## Помічник, якого кличе ядро

Другий крок сам не працює: `demo:remote` ніхто не створював, і добути його ядро не вміє. Коли пошук не дає нічого, ядро запускає `/sbin/request-key` — шлях зашитий у код, `PATH` тут ні до чого, — а той за конфігурацією добирає обробника. Досить одного рядка в окремому файлі-вкладці:

```
# /etc/request-key.d/demo.conf
create user demo:* * /usr/local/sbin/demo-handler %k %d %c %S
```

Колонки: операція · тип ключа · шаблон опису · шаблон даних виклику · програма й аргументи. Підстановки `%k`, `%d`, `%c`, `%S` — номер незаповненого ключа, його опис, дані виклику від того, хто просив, і кільце сеансу замовника.

```c
/* demo-handler.c — cc -Wall -O2 demo-handler.c -o demo-handler -lkeyutils
   кладеться в /usr/local/sbin; запускає його request-key від імені root */
#include <keyutils.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[])
{
    if (argc != 5) {
        fprintf(stderr, "usage: %s <key> <desc> <callout> <ring>\n", argv[0]);
        return 2;
    }
    key_serial_t key  = (key_serial_t)strtol(argv[1], NULL, 10);
    const char  *desc = argv[2];
    key_serial_t ring = (key_serial_t)strtol(argv[4], NULL, 10);

    /* повноваження рівно на цей один ключ; без них ядро відповість EPERM */
    if (keyctl_assume_authority(key) < 0) { perror("assume_authority"); return 1; }

    if (strstr(desc, "forbidden")) {           /* добувати нема чого */
        keyctl_reject(key, 60, ENOKEY, ring);  /* від'ємне наповнення на 60 с */
        return 0;
    }

    char payload[128];
    int n = snprintf(payload, sizeof payload, "material:%s", desc);
    if (n < 0 || n >= (int)sizeof payload) return 1;

    if (keyctl_instantiate(key, payload, n, ring) < 0) { perror("instantiate"); return 1; }
    return 0;
}
```

У справжньому помічнику на місці `snprintf` була б розмова з мережею, читання конфігурації, криптографія — усе те, чого в ядрі бути не повинно. Форма ж лишається та сама: спершу взяти повноваження, потім або наповнити, або чесно відмовити.

`keyctl_assume_authority` робить дві роботи одразу, і другу легко проґавити. Крім права наповнити цей ключ, вона додає до шляху пошуку **кільця замовника** з його UID і GID — саме звідти справжній помічник дістає квиток чи пароль, з якого робить матеріал. Без цього виклику помічник — просто чужий процес, і `keyctl_instantiate` поверне `EPERM`.

Відмова теж має форму: `keyctl_reject(key, 60, ENOKEY, ring)` наповнює ключ від'ємно на шістдесят секунд. Усі звертання за цей час дістануть `ENOKEY` одразу, не породжуючи процесу; після шістдесяти секунд помічника спитають знову.

## Прогін

```
$ keyctl session - ./keydemo
Joined session keyring: 596244341
[1] створено 384162009  user;1000;1000;3f010000;demo:token
[1] прочитано 12 Б: s3cr3t-token
[2] помічник дав 92710455, 20 Б: material:demo:remote
[2] удруге: 92710455
[2] demo:forbidden -> Required key not available
[3] новий сеанс 1057188623, uid лишився 1000
[3] describe -> user;1000;1000;3f010000;demo:token
[3] read     -> Permission denied
[3] search   -> Required key not available
```

Останні три рядки й варті всієї програми. Номер ключа той самий, UID той самий, маска та сама `3f010000` — і три різні відповіді. `describe` проходить, бо байт користувача дає `view`. `read` дістає `EACCES`, бо права на читання в байті користувача немає, а тримачем ми більше не є. `search` каже, що ключа взагалі немає, — і з погляду нового сеансу це правда. Ключ висить на кільці користувача, а воно в шлях пошуку не входить: посилання на нього кладе в кільце сеансу `pam_keyinit` під час входу, наше ж кільце сеансу зроблене голими руками й порожнє.

Тобто дозвіл забрала не зміна особи, а зміна досяжності. Той самий ефект у зворотний бік дає `keyctl_link(k, KEY_SPEC_SESSION_KEYRING)` — почепіть ключ назад, і `read` знову спрацює.

## Те саме без компілятора

Перший і третій кроки повторюються командою `keyctl`, і повторити їх варто хоча б раз — бо на цьому місці ховається пастка, через яку більшість спроб «перевірити руками» дають неправильний висновок:

```
$ k=$(keyctl add user demo:token s3cr3t-token @s)
$ keyctl print $k
s3cr3t-token
$ keyctl link $k @u
$ keyctl session - sh -c "keyctl describe $k; keyctl print $k; keyctl search @s user demo:token"
Joined session keyring: 704912233
384162009: user: demo:token
keyctl_read_alloc: Permission denied
keyctl_search: Required key not available
```

Пастка — у рядку з `keyctl session -`. Здавалося б, простіше піти з сеансу окремою командою `keyctl new_session`, а тоді спокійно робити `keyctl print`. Не вийде: кільця лежать в облікових даних, а облікові дані змінюються тільки в того, хто викликав, — команда `keyctl new_session` покине старий сеанс у власному короткому житті й помре, а ваша оболонка лишиться там, де була. Тому й потрібна форма `keyctl session - …`, яка створює безіменний сеанс і **всередині нього** запускає команду. Із тієї ж причини третій крок у програмі — не окремий процес, а функція.

## Ціна й підводні камені

Перший `request_key` коштує запуску процесу: `/sbin/request-key`, потім ваш помічник, потім чекання на наповнення — мілісекунди, іноді десятки. Кожне наступне влучання — пошук у дереві всередині ядра, тобто мікросекунди. Уся конструкція має сенс саме через цю різницю в тисячу разів, і від'ємне наповнення потрібне рівно з тієї ж причини.

- **Помічник біжить у початкових просторах імен.** Ядро запускає його від `root` поза вашим контекстом, тому в контейнері він не побачить ані вашого кореня файлової системи, ані вашої мережі; для тих, хто вважає [простори імен](root:sys-unix/namespaces) — механізм, що дає групі процесів власне бачення монтувань, мережі й PID — надійною межею, це щоразу несподіванка. Конфігурацію він теж читає з `/etc` головної системи, а не з вашої.
- **Конфігурацію можна перевірити, нічого не чіпаючи.** У `request-key` є режим налагодження `-d`: до ключів він не звертається й помічника не запускає, лише каже, який рядок збігся і що́ запустилося б. Пробний опис ключа підставляють ключем `-D` у форматі `тип;uid;gid;маска;опис` — наприклад `-D "user;0;0;1f0000;demo:remote"`.
- **`user` — не для секретів.** Замініть тип на `logon`, і той самий `keyctl_read` поверне `EOPNOTSUPP`: у типу просто немає операції читання, і маска тут нічого не вирішує. Опис тоді зобов'язаний мати вигляд `служба:ім'я`.
- **Квота б'є тихо.** Двісті ключів і 20 000 байтів на UID — цикл, що додає ключі в тесті, впирається в `EDQUOT` швидше, ніж здається. Дивитися — у `/proc/key-users`, самі ключі — у `/proc/keys`; обидва файли живуть у [файловій системі `/proc`](root:sys-unix/proc-reading-process-and-kernel-state), яку ядро малює на льоту з власних структур, тож бачите ви там рівно те, що вам дозволено бачити.
- **Ключ без посилання приречений.** Прибрали останнє — і збирач сміття забере його; типова затримка `gc_delay` — 300 секунд, але покладатися на неї не можна.
- **Сеанс міняється в однієї нитки.** Облікові дані в Linux свої на кожну нитку, і `keyctl_join_session_keyring` перепише їх лише тій, що викликала. У багатопотоковій програмі решта ниток лишаться в старому сеансі з усіма правами тримача — скидання повноважень таким способом працює тільки в однонитковій програмі або до того, як нитки запущено.
- **Помилки нетипові для `errno`.** `ENOKEY`, `EKEYEXPIRED`, `EKEYREVOKED`, `EKEYREJECTED` — окремі коди, і `perror` друкує їх зрозуміло, тож не гребуйте ним на користь «щось пішло не так».
