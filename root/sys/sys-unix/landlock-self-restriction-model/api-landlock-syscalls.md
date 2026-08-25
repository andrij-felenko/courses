# 📋 Контракт Landlock: три виклики, права, коди помилок

Це повний перелік того, чим із Landlock розмовляють: три системні виклики, три структури, два типи правил, два десятки прав із позначкою, з якої версії кожне існує, і дві таблиці помилок — окремо для того, хто зачиняє пісочницю, і окремо для того, хто в ній уже живе. Числа звірено з `include/uapi/linux/landlock.h`, `security/landlock/` та сторінками `man 2 landlock_*`. Саме числа тут і важать: набір прав росте майже з кожним другим випуском ядра, а одне невідоме ядру право перетворює виклик на `EINVAL` — і пісочниці не буде взагалі жодної, бо єдиний спосіб її поставити щойно провалився.

## Три виклики

```c
#include <linux/landlock.h>
#include <sys/syscall.h>
#include <unistd.h>

/* обгорток у glibc немає — лише через syscall(2) */
int syscall(SYS_landlock_create_ruleset,          /* 444 */
            const struct landlock_ruleset_attr *attr, size_t size, __u32 flags);
int syscall(SYS_landlock_add_rule,                /* 445 */
            int ruleset_fd, enum landlock_rule_type rule_type,
            const void *rule_attr, __u32 flags);
int syscall(SYS_landlock_restrict_self,           /* 446 */
            int ruleset_fd, __u32 flags);
```

Номери 444–446 з'явилися в 5.13 разом із самим механізмом. Обгорток немає й досі, тож звертатися доводиться [номером виклику](root:sys-unix/syscall-mechanics) через `syscall(2)`. Перший виклик при успіху повертає **дескриптор набору правил**, два інші — нуль; при невдачі всі троє повертають `-1`.

## Набір правил: оголошення юрисдикції

```c
struct landlock_ruleset_attr {
    __u64 handled_access_fs;    /* ABI 1  — права, які набір бере на себе */
    __u64 handled_access_net;   /* ABI 4 */
    __u64 scoped;               /* ABI 6 */
    __u64 quiet_access_fs;      /* ABI 10 — з яких відмов не робити записів */
    __u64 quiet_access_net;     /* ABI 10 */
    __u64 quiet_scoped;         /* ABI 10 */
};
```

`size` — це `sizeof` тієї структури, яку знають **ваші** заголовки, і ядро звіряє її зі своєю. Менша за ядрову означає стару програму на новому ядрі: бракуючі поля ядро вважає нульовими й працює далі. Більша дозволена лише доти, доки зайвий хвіст занулений, — інакше `E2BIG`. Замала (менша за найпершу версію структури) — `EINVAL`.

## Спитати ядро, а не вгадати

```c
int abi = syscall(SYS_landlock_create_ruleset, NULL, 0,
                  LANDLOCK_CREATE_RULESET_VERSION);   /* 1 << 0 → 1, 2, 3, … */
int fixed = syscall(SYS_landlock_create_ruleset, NULL, 0,
                    LANDLOCK_CREATE_RULESET_ERRATA);  /* 1 << 1 → бітова маска */
```

З цими двома прапорцями `attr` мусить бути `NULL`, а `size` — нулем; будь-що інше дає `EINVAL`. Перший повертає найвищу версію ABI, яку вміє це ядро, другий — маску виправлених хиб для чинної версії: біт N виставлено, коли хибу за номером N у цьому ядрі вже полагоджено. Давніші ядра прапорця `ERRATA` не знають і відповідають `EINVAL` — це водночас і спосіб дізнатися, що його там нема.

| ABI | ядро | що з'явилося |
|---|---|---|
| 1 | 5.13 | тринадцять прав `LANDLOCK_ACCESS_FS_*`, обидва інші виклики |
| 2 | 5.19 | `LANDLOCK_ACCESS_FS_REFER` |
| 3 | 6.2 | `LANDLOCK_ACCESS_FS_TRUNCATE` |
| 4 | 6.7 | `handled_access_net`, `LANDLOCK_RULE_NET_PORT`, обидва права TCP |
| 5 | 6.10 | `LANDLOCK_ACCESS_FS_IOCTL_DEV` |
| 6 | 6.12 | `scoped`, обидва `LANDLOCK_SCOPE_*` |
| 7 | 6.15 | три прапорці `LANDLOCK_RESTRICT_SELF_LOG_*` |
| 8 | 7.0 | `LANDLOCK_RESTRICT_SELF_TSYNC` |
| 9 | 7.1 | `LANDLOCK_ACCESS_FS_RESOLVE_UNIX` |
| 10 | 7.2 | обидва права UDP, поля `quiet_*` і `LANDLOCK_ADD_RULE_QUIET` |

Версія ядра тут довідкова: дистрибутиви залюбки переносять зміни в старі гілки, тож єдина чесна відповідь — та, яку повернув сам виклик.

## Права до файлової системи

| право | біт | ABI | що судить |
|---|---|---|---|
| `LANDLOCK_ACCESS_FS_EXECUTE` | `1 << 0` | 1 | виконати файл: `execve`, завантаження бібліотеки |
| `LANDLOCK_ACCESS_FS_WRITE_FILE` | `1 << 1` | 1 | відкрити файл на запис |
| `LANDLOCK_ACCESS_FS_READ_FILE` | `1 << 2` | 1 | відкрити файл на читання |
| `LANDLOCK_ACCESS_FS_READ_DIR` | `1 << 3` | 1 | перелічити вміст каталогу |
| `LANDLOCK_ACCESS_FS_REMOVE_DIR` | `1 << 4` | 1 | `rmdir` запису **в цьому** каталозі |
| `LANDLOCK_ACCESS_FS_REMOVE_FILE` | `1 << 5` | 1 | `unlink` запису в цьому каталозі |
| `LANDLOCK_ACCESS_FS_MAKE_CHAR` | `1 << 6` | 1 | створити символьний пристрій |
| `LANDLOCK_ACCESS_FS_MAKE_DIR` | `1 << 7` | 1 | створити підкаталог |
| `LANDLOCK_ACCESS_FS_MAKE_REG` | `1 << 8` | 1 | створити звичайний файл |
| `LANDLOCK_ACCESS_FS_MAKE_SOCK` | `1 << 9` | 1 | прив'язати [сокет домену Unix](root:sys-unix/unix-domain-sockets) до імені |
| `LANDLOCK_ACCESS_FS_MAKE_FIFO` | `1 << 10` | 1 | створити іменований канал |
| `LANDLOCK_ACCESS_FS_MAKE_BLOCK` | `1 << 11` | 1 | створити блоковий пристрій |
| `LANDLOCK_ACCESS_FS_MAKE_SYM` | `1 << 12` | 1 | створити символьне посилання |
| `LANDLOCK_ACCESS_FS_REFER` | `1 << 13` | 2 | `rename` і `link` між різними ієрархіями |
| `LANDLOCK_ACCESS_FS_TRUNCATE` | `1 << 14` | 3 | `truncate`, `ftruncate`, `open` з `O_TRUNC`, `creat` |
| `LANDLOCK_ACCESS_FS_IOCTL_DEV` | `1 << 15` | 5 | [`ioctl`](root:sys-unix/ioctl-interface) над файлом пристрою |
| `LANDLOCK_ACCESS_FS_RESOLVE_UNIX` | `1 << 16` | 9 | підключитися до сокета домену Unix за шляхом |

Дві межі в цій таблиці варто прочитати уважно. Усі `MAKE_*` і `REMOVE_*` — це права **каталогу**, у якому з'являється чи зникає запис, а не самого об'єкта: щоб вилучити `/tmp/a`, право треба на `/tmp`. І навпаки, `READ_DIR` потрібне лише для того, щоб дізнатися вміст каталогу; пройти крізь нього до глибшого файлу можна й без нього.

Третя тонкість коштує найбільше часу на налагодження. Право `TRUNCATE` відокремили від `WRITE_FILE` лише в третій версії, і судять його рівно тоді, коли набір узяв його в `handled_access_fs`. Тому спотикається саме та програма, що оголошує всі відомі їй права, а в масках правил лишає самий `WRITE_FILE`: перший же `open` з `O_TRUNC` дістане `EACCES` — тоді як на ядрі, яке `TRUNCATE` ще не знає, той самий набір (уже без цього біта) обрізання не судив зовсім.

## Мережа й межа домену

| право / прапорець | біт | ABI | що судить |
|---|---|---|---|
| `LANDLOCK_ACCESS_NET_BIND_TCP` | `1 << 0` | 4 | `bind` сокета TCP на цей порт |
| `LANDLOCK_ACCESS_NET_CONNECT_TCP` | `1 << 1` | 4 | `connect` TCP на цей порт |
| `LANDLOCK_ACCESS_NET_BIND_UDP` | `1 << 2` | 10 | `bind` сокета UDP на цей порт |
| `LANDLOCK_ACCESS_NET_CONNECT_SEND_UDP` | `1 << 3` | 10 | `connect` і надсилання UDP на цей порт |
| `LANDLOCK_SCOPE_ABSTRACT_UNIX_SOCKET` | `1 << 0` | 6 | підключення до абстрактних сокетів **поза** власним доменом |
| `LANDLOCK_SCOPE_SIGNAL` | `1 << 1` | 6 | надсилання сигналів процесам поза власним доменом |

Поле `scoped` влаштоване інакше, ніж обидва `handled_*`, і в цьому легко спіткнутися. Для нього немає правил: оголосити межу означає одразу її зачинити. Домен просто перестає дотягуватися назовні — до процесів, які не є ним самим або його нащадками, — і жодним `add_rule` виняток не проб'єш.

## Одне правило

```c
enum landlock_rule_type {
    LANDLOCK_RULE_PATH_BENEATH = 1,
    LANDLOCK_RULE_NET_PORT     = 2,   /* ABI 4 */
};

struct landlock_path_beneath_attr {
    __u64 allowed_access;
    __s32 parent_fd;                  /* зазвичай open(path, O_PATH | O_CLOEXEC) */
} __attribute__((packed));            /* рівно 12 байтів, без вирівнювання */

struct landlock_net_port_attr {
    __u64 allowed_access;
    __u64 port;                       /* порядок байтів вузла, 0…65535 */
};
```

`packed` тут не косметика: структура має рівно дванадцять байтів, а не шістнадцять, тож власноруч обчислені зсуви й `memcpy` в буфер розміром `sizeof` без цього атрибута дадуть ядру сміття в полі дескриптора.

Порт передають у порядку байтів **вузла**, а не мережі. Звичка писати `htons(443)` скрізь, де йдеться про порт, тут дає інше число й найтихішу з можливих помилок: правило успішно додається — просто не на той порт.

`allowed_access` мусить бути підмножиною відповідного `handled_*` набору, інакше `EINVAL`. Прапорці четвертого аргументу — нулі; єдиний, який там буває, — `LANDLOCK_ADD_RULE_QUIET` (`1 << 0`, ABI 10): він позначає цей об'єкт як тихий, і відмови, що збіглися з масками `quiet_*` набору, не потраплять до журналу.

## Накладення

| прапорець `restrict_self` | біт | ABI | що робить |
|---|---|---|---|
| `LANDLOCK_RESTRICT_SELF_LOG_SAME_EXEC_OFF` | `1 << 0` | 7 | не записувати відмови, доки потік виконує той самий образ |
| `LANDLOCK_RESTRICT_SELF_LOG_NEW_EXEC_ON` | `1 << 1` | 7 | записувати відмови й **після** `execve` |
| `LANDLOCK_RESTRICT_SELF_LOG_SUBDOMAINS_OFF` | `1 << 2` | 7 | не записувати відмови вкладених доменів |
| `LANDLOCK_RESTRICT_SELF_TSYNC` | `1 << 3` | 8 | накласти домен **на всі потоки** процесу, неподільно |

Типова поведінка [аудиту](root:sys-unix/audit-framework) дзеркальна до перших двох прапорців: відмови того коду, який сам себе обмежив, у журнал ідуть, а після `execve` — уже ні. Логіка проста: перше — це майже завжди недогляд у власних правилах, друге — очікувана робота пісочниці над чужою програмою, і саме воно залило б журнал.

`TSYNC` варто прочитати як виправлення давньої пастки: без нього домен лягає на **той самий потік**, який викликав, а решта [потоків](root:sys-unix/threads-as-tasks) процесу лишається необмеженою. У багатопотоковій програмі, що обмежує себе не в самому початку, це діра завширшки з увесь механізм.

## Помилки на етапі налаштування

| errno | де | коли |
|---|---|---|
| `ENOSYS` | `create` | ядро зібрано без `CONFIG_SECURITY_LANDLOCK` — виклику просто нема |
| `EOPNOTSUPP` | усі три | Landlock зібрано, але не ввімкнено при завантаженні (`lsm=`) |
| `EINVAL` | `create` | невідомий прапорець, право чи біт `scoped`; замалий `size`; `VERSION`/`ERRATA` з ненульовим `attr` або `size` |
| `E2BIG` | `create` | `size` більший за структуру ядра, а зайві байти ненульові |
| `ENOMSG` | `create` | усі поля `handled_*` і `scoped` нульові — набір ні про що |
| `EINVAL` | `add_rule` | `flags` не з дозволених; `allowed_access` не підмножина оголошеного; каталожні права на звичайному файлі; `port` більший за 65535 |
| `ENOMSG` | `add_rule` | `allowed_access` дорівнює нулю |
| `EAFNOSUPPORT` | `add_rule` | правило `NET_PORT` на ядрі, зібраному без підтримки TCP |
| `EBADF` | `add_rule`, `restrict_self` | `ruleset_fd` або `parent_fd` — не дескриптор цього потоку |
| `EBADFD` | `add_rule`, `restrict_self` | дескриптор є, але не того роду: не набір правил або не той тип файлу |
| `EPERM` | `add_rule` | у набір нема права записувати |
| `EPERM` | `restrict_self` | не виставлено `no_new_privs` і немає [можливості](root:sys-unix/capabilities) `CAP_SYS_ADMIN` у своєму просторі імен користувачів; або в набір нема права читати |
| `E2BIG` | `restrict_self` | сімнадцятий шар: `LANDLOCK_MAX_NUM_LAYERS` дорівнює 16 |
| `EFAULT` | `create`, `add_rule` | структура лежить за межами адресного простору |

## Помилки, які бачить уже обмежена програма

| errno | коли |
|---|---|
| `EACCES` | будь-яка відмова у файловій операції; а також `bind` чи `connect` за мережевим правилом |
| `EXDEV` | `rename` або `link` між ієрархіями без `REFER` — або з ним, коли перенесення дало б об'єктові більше прав, ніж має ціль |
| `EPERM` | сигнал процесові поза доменом при `LANDLOCK_SCOPE_SIGNAL`; підключення чи надсилання в абстрактний сокет поза доменом при `LANDLOCK_SCOPE_ABSTRACT_UNIX_SOCKET` |

`EXDEV` тут не помилка перекладу: це той самий код, яким система відповідає на перейменування між різними монтуваннями, і програми давно вміють на нього переходити до «скопіювати й вилучити».

## Мінімальний робочий виклик

```c
#define _GNU_SOURCE
#include <fcntl.h>
#include <linux/landlock.h>
#include <stdio.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <unistd.h>

/* права, яких давніші ядра не знають, за версією ABI */
static const struct { int abi; __u64 bits; } fs_since[] = {
    { 2, LANDLOCK_ACCESS_FS_REFER },
    { 3, LANDLOCK_ACCESS_FS_TRUNCATE },
    { 5, LANDLOCK_ACCESS_FS_IOCTL_DEV },
};

int main(void)
{
    struct landlock_ruleset_attr rs = {
        .handled_access_fs = LANDLOCK_ACCESS_FS_READ_FILE |
                             LANDLOCK_ACCESS_FS_WRITE_FILE |
                             LANDLOCK_ACCESS_FS_TRUNCATE |
                             LANDLOCK_ACCESS_FS_REFER,
    };
    struct landlock_path_beneath_attr rule = {
        .allowed_access = LANDLOCK_ACCESS_FS_READ_FILE,
    };
    int abi, fd;

    abi = syscall(SYS_landlock_create_ruleset, NULL, 0,
                  LANDLOCK_CREATE_RULESET_VERSION);
    if (abi < 1)
        return perror("landlock"), 1;              /* ENOSYS або EOPNOTSUPP */
    for (unsigned i = 0; i < sizeof fs_since / sizeof *fs_since; i++)
        if (abi < fs_since[i].abi)
            rs.handled_access_fs &= ~fs_since[i].bits;

    fd = syscall(SYS_landlock_create_ruleset, &rs, sizeof rs, 0);
    if (fd < 0)
        return perror("create_ruleset"), 1;

    rule.parent_fd = open("/usr/share", O_PATH | O_CLOEXEC);
    if (rule.parent_fd < 0)
        return perror("/usr/share"), 1;
    if (syscall(SYS_landlock_add_rule, fd, LANDLOCK_RULE_PATH_BENEATH, &rule, 0))
        return perror("add_rule"), 1;
    close(rule.parent_fd);

    prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0);        /* обов'язково ДО restrict_self */
    if (syscall(SYS_landlock_restrict_self, fd, 0))
        return perror("restrict_self"), 1;
    close(fd);

    if (open("/etc/passwd", O_RDONLY) < 0)
        perror("/etc/passwd");                     /* → Permission denied */
    return 0;
}
```

Півсотні рядків показують увесь контракт у зборі. Спершу питають версію й вимикають із наміру те, чого це ядро не знає, — без цього циклу `create_ruleset` на ядрі 5.13 відповів би `EINVAL` через саму лише згадку про `REFER`. Далі `sizeof rs` віддають ядру як є: зайві поля структури заповнені нулями, тому старе ядро мовчки їх пропустить, а нове прочитає. Каталог відкривають із `O_PATH` — це відкриває сам об'єкт, не питаючи права читати його. І `no_new_privs` виставляють **до** накладення, інакше замість пісочниці буде `EPERM`.

Якщо ваші заголовки старіші за ядро, потрібних констант у них просто немає: перевірка версії тоді нічого не врятує, бо код не збереться. Реальні програми або носять власні `#define` для нових бітів, або беруть `linux/landlock.h` з нового ядра — версія заголовків і версія ядра тут узгоджуються окремо одна від одної.
