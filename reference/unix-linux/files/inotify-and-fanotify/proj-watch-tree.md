# ⚙️ Спостерігач за деревом каталогів

Робоча програма мовою C, яка отримує шлях і друкує потік змін усередині цілого піддерева — з правильними повними шляхами й без мовчазних пропусків. Уся суть задачі — у системних викликах і в розкладці структур, які вони віддають, тож і працюємо на тому рівні, де ці структури видно.

Інтерфейс inotify виглядає як три виклики, тож перша реалізація зазвичай має тридцять рядків і працює на демонстрації. Ламається вона не від навантаження, а від звичайних дій: `mv` каталогу в середині дерева, `npm install`, `git checkout` між гілками. Причина в тому, що працездатний спостерігач — це не обгортка над `read()`, а чотири окремі механізми: обхід із правильним порядком двох викликів, карта `wd` → шлях, що переживає перейменування, склеювання половинок переїзду за `cookie` і повне відновлення після втрати картини. Кожен існує через власну вузьку причину, і жоден не виводиться з інтерфейсу — його треба вивести із задачі.

## Що саме має вміти програма

Без записаного контракту неможливо сказати, коли реалізація правильна, а коли просто не спіймана на брехні. Програма друкує рядки:

```
RESYNC              — усе, що ви знали, недійсне; далі йде повний перелік
= <шлях>            — існує (побачено обходом)
+ <шлях>            — з'явилося
- <шлях>            — зникло
w <шлях>            — закрито після запису
> <старий> <новий>  — перейменовано
READY <n>           — обхід закінчено, далі самі події
```

Дві вимоги до цього потоку. Перша: **жодна зміна не зникає мовчки** — якщо спостерігач утратив картину, він каже про це `RESYNC`, а не вдає, що все гаразд. Друга: **дублікати дозволені**. Друга вимога виглядає як поступка якості, а насправді вона й тримає першу: повнота й неповторність у цій задачі несумісні, і вибирати доводиться повноту.

## Порядок обходу: щілину не прибрати, її можна лише переоцінити

Стеження прив'язане до одного inode, тож на дерево з тисячі каталогів треба тисячу окремих стежень, і розставляє їх обхід. Обхід кожного каталогу складається з двох дій: поставити стеження й прочитати вміст. Між ними минає час, і за цей час хтось інший може створити файл. Порядок цих двох дій вирішує все.

Якщо спершу прочитати вміст, а потім поставити стеження, то файл, створений у проміжку, не потрапив у перелік (його ще не було) і не дасть події (стеження ще не стояло). Він для програми не існує — і не існуватиме, доки хтось не зробить повний обхід наново. Це втрата без сліду.

Якщо спершу поставити стеження, а потім прочитати вміст, той самий файл дасть подію (стеження вже стоїть), а ще може потрапити в перелік (якщо `readdir` дійде до нього пізніше). Тобто про нього стане відомо один раз або двічі — але **не нуль разів**.

![Дві часові лінії: у першій між readdir і inotify_add_watch губиться створений файл, у другій між inotify_add_watch і readdir той самий файл приходить двічі](/reference/unix-linux/files/inotify-and-fanotify/img/walk-order-gap.svg)

*Порядок не прибирає щілини — він міняє її наслідок з утрати на дублікат.*

Ось звідки друга вимога контракту. Дублікати — не недогляд реалізації, а **ціна повноти**: щілина між двома незалежними системними викликами не закривається жодним порядком, і єдиний вибір — чим за неї платити. Практичний наслідок для того, хто споживає потік: кожен обробник має бути ідемпотентним. Складальник, який перезбирає файл за шляхом, ідемпотентний природно; лічильник змін — ні, і його на цьому потоці будувати не можна.

Той самий порядок діє й пізніше, не лише на старті. Прийшла подія `IN_CREATE` з бітом `IN_ISDIR` — усередині нового каталогу вже могли щось створити, доки подія лежала в черзі. Тому щойно доглянутий каталог **перечитують завжди**, навіть якщо він щойно народився порожнім.

Ціле піддерево, утім, двічі не обходиться, і розпізнавач для цього дає саме ядро: якщо той самий inode уже під наглядом, `inotify_add_watch()` не заводить нового стеження, а повертає **той самий `wd`**, що й перше. Тобто перевірка «чи є вже такий `wd` у моїй карті» надійно ловить повторний захід у ту саму гілку — і повторне перечитування, і другий запис у карті відпадають самі.

## Від `wd` до шляху

У події немає шляху. Є `wd` того каталогу, у якому щось сталося, і `name` — ім'я запису всередині нього. Щоб надрукувати `/srv/app/src/ui/main.c`, програма мусить сама тримати відображення `wd` → каталог.

Ключ — маленьке додатне число, але не щільне: ядро роздає `wd` через `idr` і **перевикористовує звільнені номери**. Масив за індексом `wd` тому не годиться (дірки й повторне заселення), а лінійний пошук по тисячах записів на кожну подію з'їв би весь виграш від сповіщень. Природний вибір — [хеш-таблиця](book:algorithms/hash-table) з ланцюжками: сталий час на пошук, ключ — саме число `wd`.

Лишається питання, **що** класти в комірку. Очевидний варіант — повний рядок шляху. Він і ламається першим.

`mv src lib` у корені проєкту — це одна пара подій. Але каталог `src` міг мати сотні нащадків, і кожен з них зберігає рядок, що починається з `/srv/app/src/…`. Усі ці рядки миттєво стали брехнею. Полагодити їх можна лише перебравши **всю** таблицю в пошуках префікса, з хірургією над кожним знайденим рядком. Одна дешева операція користувача коштує обходу всіх стежень — а на дереві з `node_modules` це десятки тисяч.

Правильна комірка зберігає не шлях, а **ланку**: `wd` батька плюс власне ім'я в цьому батькові. Тоді повний шлях узагалі ніде не лежить — його будують на вимогу, підіймаючись до кореня й склеюючи імена у зворотному порядку.

![Дві таблиці: у лівій із повними рядками перейменування псує три рядки з чотирьох, у правій із ланками на батька — рівно одну комірку](/reference/unix-linux/files/inotify-and-fanotify/img/wd-path-map.svg)

*Перейменування каталогу в середині дерева міняє один запис — шляхи цілої гілки стають правильними самі, бо їх ніде не зберігали.*

Заплатили за це підйомом до кореня на кожну подію — це рівно глибина дерева, тобто одиниці чи десятки кроків, кожен зі сталим часом. За можливість не переписувати десятки тисяч рядків на кожен `mv` — угода очевидна.

Ланка на батька дає й другу зручність задарма. Якщо в комірці тримати ще й список дітей, то за парою «`wd` батька + ім'я» знаходиться вузол самого підкаталогу (перебором дітей одного каталогу, а не всієї таблиці), а обхід цього списку вглиб дає все піддерево — саме те, що треба, коли гілку виносять за межі дерева й з неї треба знімати стеження.

## Склеювання пари за `cookie`

`rename()` у ядрі перетворюється на дві події: `IN_MOVED_FROM` у старому каталозі й `IN_MOVED_TO` у новому. Обидві несуть однакове ненульове число в полі `cookie` — це єдине, що їх пов'язує.

Половинка без пари — не помилка, а звичайна річ: об'єкт міг переїхати з-під нагляду назовні (буде тільки `MOVED_FROM`) або ззовні під нагляд (буде тільки `MOVED_TO`). Тому чекати пару вічно не можна: непарний `MOVED_FROM` треба через якийсь час визнати видаленням, а непарний `MOVED_TO` — появою.

Скільки чекати? Обидві половинки народжуються всередині одного `rename()`, тож нормально вони лежать у черзі поруч і склеюються в одному батчі. Затримка потрібна лише на випадок, коли читання розсікло чергу між ними. Сотні мілісекунд вистачає з великим запасом; це і є затримка, з якою програма повідомляє про переїзд за межі дерева. Відлічувати її треба [монотонним годинником](book:programming/monotonic-vs-wall-time) — настінний час стрибає від NTP, і на стрибку назад половинки зависли б назавжди.

## Один цикл на всі джерела

Дескриптор групи inotify читається звичайним `read()`, тому його кладуть в [epoll](book:unix-linux/select-poll-epoll) поряд із рештою: сокетом керування, `signalfd`, `timerfd`. Ніякого окремого потоку для стеження не потрібно.

Дві дрібниці, на яких спотикаються. Перша: буфер для `read()` мусить умістити щонайменше один запис максимальної довжини — інакше з ядра 2.6.21 виклик повертає `EINVAL`, а не короткий запис. Мінімум — `sizeof(struct inotify_event) + NAME_MAX + 1`; на практиці беруть десятки кілобайтів, щоб забирати події пачками. Друга: буфер має бути вирівняний під `struct inotify_event`, бо по ньому йдуть арифметикою вказівника — записи змінної довжини лежать упритул. І, звісно, `read()` [переривається сигналом](book:unix-linux/eintr-and-restart), тож `EINTR` треба перезапускати.

Тайм-аут `epoll_wait()` рахують від найближчого дедлайну незакритої половинки переїзду: поки нема чого чекати — блокуємось без обмеження, є половинка — прокидаємось рівно тоді, коли її час вийшов.

## Код

Далі — програма цілком, розбита на частини в порядку складання. Збірка: `cc -O2 -Wall -Wextra -o watchtree watchtree.c`.

**Каркас, маска подій і вузол карти.**

```c
#define _GNU_SOURCE
#include <sys/inotify.h>
#include <sys/epoll.h>
#include <sys/stat.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define NBUCKET   (1u << 16)     /* 512 КіБ вказівників — вистачає на мільйон стежень */
#define MAXDEPTH  256
#define MOVE_SLOTS 64
#define TODO_MAX   4096
#define MOVE_TIMEOUT_MS 200

/* IN_ONLYDIR    — стежимо лише за каталогами; файл дасть ENOTDIR замість тихої дурниці
   IN_DONT_FOLLOW — символьне посилання не розкриваємо, інакше вийдемо з дерева
   IN_EXCL_UNLINK — не сповіщати про дітей, уже від'єднаних від каталогу */
static const uint32_t WATCH_MASK =
      IN_CREATE | IN_DELETE | IN_MOVED_FROM | IN_MOVED_TO | IN_CLOSE_WRITE
    | IN_DELETE_SELF | IN_MOVE_SELF
    | IN_ONLYDIR | IN_DONT_FOLLOW | IN_EXCL_UNLINK;

struct node {
    int wd, parent;             /* parent == -1 лише в кореня */
    char *name;                 /* базове ім'я в батькові; у кореня — увесь шлях */
    struct node *hnext;         /* ланцюжок кошика хеш-таблиці */
    struct node *child, *sib;   /* дерево: перша дитина й наступний брат */
};

struct ctx {
    int ifd, ep;
    const char *root;
    char *buf;                  /* робочий буфер шляху завдовжки PATH_MAX */
    int rebuild;                /* прапорець «картина втрачена, почати спочатку» */
};

static void *xmalloc(size_t n)
{
    void *p = malloc(n);
    if (!p) { perror("malloc"); exit(1); }
    return p;
}

static char *xstrdup(const char *s)
{
    char *p = strdup(s);
    if (!p) { perror("strdup"); exit(1); }
    return p;
}
```

**Карта `wd` → вузол і побудова шляху.** Хешування — множення на просте число з подальшим узяттям старших бітів: молодші біти `wd` майже послідовні, і брати їх напряму означало б заселяти кошики підряд.

```c
static struct node *tab[NBUCKET];
static size_t nwatch;

static unsigned slot(int wd)
{
    return (((unsigned) wd * 2654435761u) >> 16) & (NBUCKET - 1);
}

static struct node *map_get(int wd)
{
    if (wd < 0) return NULL;
    for (struct node *n = tab[slot(wd)]; n; n = n->hnext)
        if (n->wd == wd) return n;
    return NULL;
}

static struct node *map_add(int wd, int parent, const char *name)
{
    struct node *n = xmalloc(sizeof *n);
    n->wd = wd;
    n->parent = parent;
    n->name = xstrdup(name);
    n->child = NULL;

    unsigned s = slot(wd);
    n->hnext = tab[s];
    tab[s] = n;

    struct node *p = map_get(parent);          /* у кореня — NULL */
    n->sib = p ? p->child : NULL;
    if (p) p->child = n;

    nwatch++;
    return n;
}

static void unlink_hash(struct node *n)
{
    for (struct node **pp = &tab[slot(n->wd)]; *pp; pp = &(*pp)->hnext)
        if (*pp == n) { *pp = n->hnext; return; }
}

static void unlink_sib(struct node *n)
{
    struct node *p = map_get(n->parent);
    if (!p) return;
    for (struct node **pp = &p->child; *pp; pp = &(*pp)->sib)
        if (*pp == n) { *pp = n->sib; return; }
}

static struct node *child_of(int parent_wd, const char *name)
{
    struct node *p = map_get(parent_wd);
    if (!p) return NULL;
    for (struct node *n = p->child; n; n = n->sib)
        if (strcmp(n->name, name) == 0) return n;
    return NULL;
}

/* Повний шлях будуємо на вимогу: підіймаємось до кореня, збираючи імена,
   і склеюємо їх у зворотному порядку. Жодного повного рядка ніде не лежить. */
static int path_of(int wd, char *out, size_t cap)
{
    const char *part[MAXDEPTH];
    int k = 0;
    for (int cur = wd; cur >= 0; ) {
        struct node *n = map_get(cur);
        if (!n || k == MAXDEPTH) return -1;
        part[k++] = n->name;
        cur = n->parent;
    }
    size_t len = 0;
    for (int i = k - 1; i >= 0; i--) {
        size_t nl = strlen(part[i]);
        int sep = (len > 0 && out[len - 1] != '/');
        if (len + sep + nl + 1 > cap) return -1;
        if (sep) out[len++] = '/';
        memcpy(out + len, part[i], nl);
        len += nl;
    }
    out[len] = '\0';
    return (int) len;
}

static void emit(const char *what, int dir_wd, const char *name)
{
    char path[PATH_MAX];
    int len = path_of(dir_wd, path, sizeof path);
    if (len < 0) return;                       /* каталог уже зник — нема про що казати */
    printf("%s %s%s%s\n", what, path,
           (len && path[len - 1] == '/') ? "" : "/", name);
}
```

**Обхід.** Стеження — першою дією, читання вмісту — другою; звіт про кожен знайдений запис іде маркером `=`, бо це стан, а не подія.

```c
static void die_enospc(const struct ctx *c);

static void scan(struct ctx *c, size_t len, int parent, const char *base)
{
    int wd = inotify_add_watch(c->ifd, c->buf, WATCH_MASK);
    if (wd < 0) {
        if (errno == ENOSPC) die_enospc(c);
        if (errno != ENOENT && errno != EACCES && errno != ENOTDIR)
            fprintf(stderr, "watchtree: %s: %s\n", c->buf, strerror(errno));
        return;                                /* зник або не наш — просто не покриваємо */
    }
    if (map_get(wd)) return;                   /* цей inode уже в карті: гілку покрито */
    map_add(wd, parent, base);

    DIR *d = opendir(c->buf);                  /* перечитуємо ПІСЛЯ того, як стеження стоїть */
    if (!d) {
        if (errno != ENOENT && errno != EACCES)
            fprintf(stderr, "watchtree: %s: %s\n", c->buf, strerror(errno));
        return;
    }
    for (struct dirent *e; (e = readdir(d)) != NULL; ) {
        if (e->d_name[0] == '.' && (e->d_name[1] == '\0' ||
            (e->d_name[1] == '.' && e->d_name[2] == '\0')))
            continue;

        int isdir;
        if (e->d_type == DT_DIR)          isdir = 1;
        else if (e->d_type != DT_UNKNOWN) isdir = 0;
        else {                                 /* ФС не заповнила d_type — питаємо окремо */
            struct stat st;
            isdir = fstatat(dirfd(d), e->d_name, &st, AT_SYMLINK_NOFOLLOW) == 0
                    && S_ISDIR(st.st_mode);
        }

        printf("= %s/%s\n", c->buf, e->d_name);
        if (!isdir) continue;

        size_t nl = strlen(e->d_name);
        if (len + 1 + nl >= PATH_MAX) continue;
        c->buf[len] = '/';
        memcpy(c->buf + len + 1, e->d_name, nl + 1);
        scan(c, len + 1 + nl, wd, e->d_name);
        c->buf[len] = '\0';                    /* відкотили — знову шлях батька */
    }
    closedir(d);
}
```

**Знімання гілки й забування.** Різниця між двома операціями принципова: коли ядро само зняло стеження (`IN_IGNORED`), кликати `inotify_rm_watch()` уже нема на що, а коли гілку винесли за межі дерева — стеження живі й ядро їх не зніме, поки ми не попросимо.

```c
static void free_node(struct node *n)
{
    unlink_hash(n);
    free(n->name);
    free(n);
    nwatch--;
}

static void forget_rec(struct node *n)
{
    for (struct node *ch = n->child, *next; ch; ch = next) { next = ch->sib; forget_rec(ch); }
    free_node(n);
}

static void forget(struct node *n)          /* стеження вже нема в ядрі */
{
    unlink_sib(n);
    forget_rec(n);
}

static void unwatch_rec(struct ctx *c, struct node *n)
{
    for (struct node *ch = n->child, *next; ch; ch = next) { next = ch->sib; unwatch_rec(c, ch); }
    inotify_rm_watch(c->ifd, n->wd);        /* IN_IGNORED прилетить на вже забутий wd */
    free_node(n);
}

static void unwatch_subtree(struct ctx *c, struct node *n)
{
    unlink_sib(n);
    unwatch_rec(c, n);
}
```

**Відкладені обходи.** Нові стеження ставлять **тільки** після того, як черга спорожніла. Причина вузька, але справжня: `inotify_rm_watch()` одразу звільняє номер, а породжений ним `IN_IGNORED` ще лежить у черзі — постав нове стеження просто зараз, і воно може отримати той самий `wd`, після чого чужий `IN_IGNORED` знищить свіжий запис. Дренаж черги до кінця прибирає цю гонитву цілком.

```c
struct todo { int parent; char name[NAME_MAX + 1]; };
static struct todo todo[TODO_MAX];
static int ntodo;

static void defer_scan(struct ctx *c, int parent, const char *name)
{
    if (ntodo == TODO_MAX) { c->rebuild = 1; return; }   /* не влазить — простіше почати спочатку */
    todo[ntodo].parent = parent;
    snprintf(todo[ntodo].name, sizeof todo[ntodo].name, "%s", name);
    ntodo++;
}

static void run_todo(struct ctx *c)
{
    for (int i = 0; i < ntodo; i++) {
        int len = path_of(todo[i].parent, c->buf, PATH_MAX);
        if (len < 0) continue;                           /* батька вже нема */
        size_t nl = strlen(todo[i].name);
        if ((size_t) len + 1 + nl >= PATH_MAX) continue;
        c->buf[len] = '/';
        memcpy(c->buf + len + 1, todo[i].name, nl + 1);
        scan(c, len + 1 + nl, todo[i].parent, todo[i].name);
    }
    ntodo = 0;
}
```

**Половинки переїзду.**

```c
struct pending {
    int used;
    uint32_t cookie;
    int from_parent;        /* wd каталогу, з якого пішло */
    int moved_wd;           /* wd самого об'єкта, якщо це доглянутий каталог; інакше -1 */
    char name[NAME_MAX + 1];
    long deadline;
};
static struct pending moves[MOVE_SLOTS];

static long now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000L + ts.tv_nsec / 1000000L;
}

static void move_out(struct ctx *c, struct node *dir, const char *name,
                     int isdir, uint32_t cookie)
{
    struct node *sub = isdir ? child_of(dir->wd, name) : NULL;
    for (int i = 0; i < MOVE_SLOTS; i++) {
        if (moves[i].used) continue;
        moves[i].used = 1;
        moves[i].cookie = cookie;
        moves[i].from_parent = dir->wd;
        moves[i].moved_wd = sub ? sub->wd : -1;
        snprintf(moves[i].name, sizeof moves[i].name, "%s", name);
        moves[i].deadline = now_ms() + MOVE_TIMEOUT_MS;
        return;
    }
    c->rebuild = 1;         /* стільки незакритих переїздів — картина вже ненадійна */
}

/* Ось воно: перейменування каталогу в середині дерева — один запис у карті. */
static void reparent(struct node *n, int new_parent, const char *new_name)
{
    unlink_sib(n);
    free(n->name);
    n->name = xstrdup(new_name);
    n->parent = new_parent;
    struct node *p = map_get(new_parent);
    n->sib = p ? p->child : NULL;
    if (p) p->child = n;
}

static void move_in(struct ctx *c, struct node *dir, const char *name,
                    int isdir, uint32_t cookie)
{
    for (int i = 0; i < MOVE_SLOTS; i++) {
        if (!moves[i].used || moves[i].cookie != cookie) continue;

        char from[PATH_MAX], to[PATH_MAX];
        if (path_of(moves[i].from_parent, from, sizeof from) >= 0 &&
            path_of(dir->wd, to, sizeof to) >= 0)
            printf("> %s/%s %s/%s\n", from, moves[i].name, to, name);

        struct node *sub = map_get(moves[i].moved_wd);
        if (sub)        reparent(sub, dir->wd, name);
        else if (isdir) defer_scan(c, dir->wd, name);   /* каталог ще не був доглянутий */
        moves[i].used = 0;
        return;
    }
    emit("+", dir->wd, name);                           /* прийшло ззовні дерева */
    if (isdir) defer_scan(c, dir->wd, name);
}

static void expire_moves(struct ctx *c)
{
    long now = now_ms();
    for (int i = 0; i < MOVE_SLOTS; i++) {
        if (!moves[i].used || moves[i].deadline > now) continue;
        emit("-", moves[i].from_parent, moves[i].name); /* пішло за межі дерева */
        struct node *sub = map_get(moves[i].moved_wd);
        if (sub) unwatch_subtree(c, sub);
        moves[i].used = 0;
    }
}

static int next_timeout(void)
{
    long now = now_ms(), best = -1;
    for (int i = 0; i < MOVE_SLOTS; i++) {
        if (!moves[i].used) continue;
        long d = moves[i].deadline - now;
        if (d < 0) d = 0;
        if (best < 0 || d < best) best = d;
    }
    return best < 0 ? -1 : (int) best;
}
```

**Розбір подій і дренаж черги.**

```c
static void on_event(struct ctx *c, const struct inotify_event *e)
{
    if (e->mask & IN_Q_OVERFLOW) { c->rebuild = 1; return; }   /* wd тут -1 */

    struct node *n = map_get(e->wd);
    if (!n) return;                              /* подія зі знятого стеження */

    if (e->mask & IN_IGNORED)    { forget(n); return; }
    if (e->mask & IN_MOVE_SELF)  { if (n->parent < 0) c->rebuild = 1; return; }
    if (e->mask & IN_DELETE_SELF) return;        /* слідом прийде IN_IGNORED */

    if (!e->len) return;                         /* далі потрібне ім'я запису */
    int isdir = (e->mask & IN_ISDIR) != 0;

    if (e->mask & IN_MOVED_FROM)  { move_out(c, n, e->name, isdir, e->cookie); return; }
    if (e->mask & IN_MOVED_TO)    { move_in (c, n, e->name, isdir, e->cookie); return; }
    if (e->mask & IN_CREATE) {
        emit("+", n->wd, e->name);
        if (isdir) defer_scan(c, n->wd, e->name);
        return;
    }
    if (e->mask & IN_DELETE)      { emit("-", n->wd, e->name); return; }
    if (e->mask & IN_CLOSE_WRITE) { emit("w", n->wd, e->name); return; }
}

static void drain(struct ctx *c)
{
    static char buf[64 * 1024]
        __attribute__((aligned(__alignof__(struct inotify_event))));

    for (;;) {
        ssize_t n = read(c->ifd, buf, sizeof buf);
        if (n < 0) {
            if (errno == EINTR)  continue;
            if (errno == EAGAIN) return;         /* черга порожня — батч скінчився */
            perror("read");
            exit(1);
        }
        for (char *p = buf; p < buf + n; ) {
            const struct inotify_event *e = (const struct inotify_event *) p;
            p += sizeof *e + e->len;             /* len — крок до наступного, не довжина імені */
            on_event(c, e);
        }
    }
}
```

**Старт групи, перебудова й головний цикл.**

```c
static long read_long(const char *path)
{
    long v = -1;
    FILE *f = fopen(path, "r");
    if (f) {
        if (fscanf(f, "%ld", &v) != 1) v = -1;
        fclose(f);
    }
    return v;
}

static void die_enospc(const struct ctx *c)
{
    long lim = read_long("/proc/sys/fs/inotify/max_user_watches");
    fprintf(stderr,
        "watchtree: вичерпано ліміт стежень inotify — покриття було б неповним.\n"
        "  поставлено:      %zu стежень\n"
        "  межа на користувача: %ld  (/proc/sys/fs/inotify/max_user_watches)\n"
        "  дерево:          %s\n"
        "  підняти межу:    sudo sysctl -w fs.inotify.max_user_watches=%ld\n"
        "  або виключити важкі гілки: node_modules, .git, target, build\n",
        nwatch, lim, c->root, lim > 0 ? lim * 4 : 65536);
    exit(1);
}

static void start_group(struct ctx *c)
{
    if (c->ifd >= 0) {
        close(c->ifd);              /* група гине з усіма стеженнями; epoll забуде fd сам */
        for (unsigned i = 0; i < NBUCKET; i++)
            for (struct node *n = tab[i], *next; n; n = next) {
                next = n->hnext;
                free(n->name);
                free(n);
            }
        memset(tab, 0, sizeof tab);
        memset(moves, 0, sizeof moves);
        nwatch = 0;
        ntodo = 0;
    }
    c->ifd = inotify_init1(IN_NONBLOCK | IN_CLOEXEC);
    if (c->ifd < 0) { perror("inotify_init1"); exit(1); }

    struct epoll_event ev = { .events = EPOLLIN, .data.fd = c->ifd };
    if (epoll_ctl(c->ep, EPOLL_CTL_ADD, c->ifd, &ev) < 0) { perror("epoll_ctl"); exit(1); }

    c->rebuild = 0;
    printf("RESYNC\n");             /* усе, що споживач знав, — недійсне */
    snprintf(c->buf, PATH_MAX, "%s", c->root);
    scan(c, strlen(c->buf), -1, c->root);
    printf("READY %zu\n", nwatch);
    fflush(stdout);
}

int main(int argc, char **argv)
{
    if (argc != 2) { fprintf(stderr, "вжиток: watchtree <каталог>\n"); return 2; }

    static char root[PATH_MAX];
    if (!realpath(argv[1], root)) { perror(argv[1]); return 1; }

    struct ctx c = { .ifd = -1, .root = root, .buf = xmalloc(PATH_MAX), .rebuild = 0 };
    c.ep = epoll_create1(EPOLL_CLOEXEC);
    if (c.ep < 0) { perror("epoll_create1"); return 1; }

    start_group(&c);

    for (;;) {
        struct epoll_event ev[8];
        int nfd = epoll_wait(c.ep, ev, 8, next_timeout());
        if (nfd < 0) {
            if (errno == EINTR) continue;
            perror("epoll_wait");
            return 1;
        }
        for (int i = 0; i < nfd; i++)
            if (ev[i].data.fd == c.ifd) drain(&c);
        /* сюди ж лягають інші джерела: сокет керування, signalfd, timerfd */

        run_todo(&c);               /* нові стеження — лише після спорожнілої черги */
        expire_moves(&c);
        fflush(stdout);

        if (c.rebuild) start_group(&c);
    }
}
```

## Переповнення: єдина правильна реакція — забути все

Черга групи скінченна (типово 16384 події). Коли вона повна, ядро кладе туди `IN_Q_OVERFLOW` із `wd = -1` і відкидає решту. Спокуса опрацювати цю подію «якось м'якше» велика й хибна: після переповнення невідомо, **що саме** загубилося, а отже недійсна вся картина, а не якась її частина. Локального ремонту не існує.

Тому в коді `IN_Q_OVERFLOW` робить рівно одне — вмикає `c->rebuild`, і головний цикл викликає `start_group()`: закрити дескриптор (з ним гинуть усі стеження), очистити карту, відкрити нову групу, обійти дерево наново. Споживач бачить новий `RESYNC` і знає, що його попередню картину треба викинути.

Той самий шлях умикається ще у двох випадках: переїхав сам корінь (`IN_MOVE_SELF` на кореневому вузлі — усі побудовані шляхи стали брехнею) і переповнилися внутрішні черги програми. Один механізм відновлення на всі втрати картини — це не лінощі, а те, що робить програму придатною для великих дерев: інакше кожен новий різновид втрати вимагав би власного, майже ніколи не випробуваного коду.

## `IN_IGNORED` і `ENOSPC`: два повідомлення, які не можна проковтнути

`IN_IGNORED` означає, що стеження більше нема — ядро зняло його само, бо об'єкт видалили, розмонтували або файлову систему від'єднали. Це остання подія цього `wd`, і після неї номер вільний для перевикористання. Запис із карти прибирають саме тут, і ніде більше; спроба прибирати його «завчасно» на `IN_DELETE_SELF` дає порожні комірки й загублені події.

`ENOSPC` від `inotify_add_watch()` — це вичерпаний `max_user_watches`, а не місце на диску. Найгірше, що з ним можна зробити, — проігнорувати повернене `-1` і поїхати далі: програма тоді працює, але покриває обрізане дерево й мовчить про зміни в решті. Тому в коді це смертельна помилка з повідомленням, у якому є все потрібне: скільки стежень уже поставлено, яка чинна межа, де вона лежить і чим її піднімають. Межа — [звичайний параметр ядра](book:unix-linux/sysctl-tunables), її [видно у /proc](book:unix-linux/proc-filesystem) і крутять `sysctl`.

## Скільки це коштує: дерево з `node_modules`

Тепер порахуймо ціну покриття — і в стеженнях, і в пам'яті ядра.

Кожне стеження — це структура `inotify_inode_mark` у [slab-кеші ядра](book:unix-linux/kernel-memory-slab), спільний на inode `fsnotify_mark_connector`, запис у `idr` і — найдорожче — **утриманий у пам'яті inode**: доки стеження живе, ядро не має права викинути inode з кешу. На ext4 inode загорнутий у більшу структуру `ext4_inode_info`, і саме її розмір визначає ціну.

Ядро рахує ліміт за власною формулою, і її видно в `fs/notify/inotify/inotify_user.c`:

```
INOTIFY_WATCH_COST = sizeof(struct inotify_inode_mark) + 2 · sizeof(struct inode)

на x86-64 з типовою конфігурацією:
  sizeof(struct inotify_inode_mark)  ≈   80 Б   (fsnotify_mark ≈ 72 Б + int wd)
  sizeof(struct inode)               ≈  632 Б
  INOTIFY_WATCH_COST                 ≈ 1344 Б ≈ 1.3 КіБ
```

Подвоєний розмір inode тут — не те, що inotify виділяє, а груба оцінка того, що стеження **не дає звільнити**. Звідси й межа: ядро дозволяє одному користувачеві зайняти під стеження не більше 1 % адресованої пам'яті, затиснувши результат у діапазон [8192, 1048576].

**Умова: проєкт із `node_modules`, 12 000 каталогів; машина з 16 ГіБ пам'яті, корінь на ext4.**

```
каталогів у дереві     = 12000        (find . -type d | wc -l)
стежень                = 12000        (одне на каталог, рекурсії ядро не вміє)

пам'ять на одне стеження:
  inotify_inode_mark            ≈   80 Б
  fsnotify_mark_connector       ≈   32 Б
  запис у idr (амортизовано)    ≈    9 Б
  утриманий inode ext4          ≈ 1100 Б
  ─────────────────────────────────────
  разом                         ≈ 1.2 КіБ

пам'ять ядра на дерево = 12000 · 1.2 КіБ ≈ 14 МіБ   (не витісняється у своп)
списано з ліміту       = 12000 · 1.3 КіБ ≈ 15 МіБ
чинна межа             = (16 ГіБ / 100) / 1344 Б   ≈ 127 800 стежень
межа до ядра 5.11      = 8192 → ENOSPC на 8193-му каталозі
```

Два висновки, і обидва практичні. Перший: на сучасній машині дерево з `node_modules` покривається з десятикратним запасом, а знаменита притча про `ENOSPC` у редакторах — спадок сталої стелі у 8192, яку в ядрі 5.11 (лютий 2021) замінили на частку від пам'яті. Стеля, утім, не зникла: формула бере пам'ять **машини** й рахує її раз, під час завантаження, тож на віртуалці чи вбудованому пристрої з 1 ГіБ вона дає підлогу 8192 — і 2005 рік повертається цілком. Обмеження пам'яті контейнера на це число не впливає взагалі: ядро й межа в нього спільні з хостом.

Другий висновок неприємніший: 14 МіБ — це **пам'ять ядра**, яку не можна ні витіснити у своп, ні відібрати під тиском. Вона змагається за місце зі сторінковим кешем. Десяток інструментів, кожен зі своїм деревом, — і десятки таких мегабайтів осідають назавжди.

Поміряти замість вірити на слово — чотири команди:

```sh
# fdinfo дескриптора inotify має рядок на кожне стеження — рахуємо їх
# по всіх дескрипторах одного процесу
cat /proc/$(pgrep -x watchtree | head -1)/fdinfo/* 2>/dev/null | grep -c '^inotify'

# те саме по всій системі
cat /proc/[0-9]*/fdinfo/* 2>/dev/null | grep -c '^inotify'

# скільки насправді зайнято в ядрі: <active_objs> <num_objs> <objsize>
sudo grep -E '^(inotify_inode_mark|ext4_inode_cache) ' /proc/slabinfo

# чинна межа
cat /proc/sys/fs/inotify/max_user_watches
```

## Складність і пастки

**Складність.** Пам'ять і кількість стежень — лінійні від числа каталогів, `O(D)`. Обробка однієї події — сталий пошук у хеш-таблиці плюс побудова шляху за глибиною дерева, `O(глибина)`. Перейменування каталогу — `O(1)` незалежно від розміру гілки. Повний обхід — `O(D)` викликів `inotify_add_watch` і `readdir`; на дереві з 12 000 каталогів це частки секунди на теплому кеші й помітно довше на холодному.

**Пастки, кожна з яких колись коштувала комусь вечора.**

- **Один inode — один `wd`, скільки б імен на нього не вело.** Каталог, [примонтований через bind у двох місцях](book:unix-linux/mount-model) усередині дерева, дасть той самий `wd`, і в карті лишиться лише один зі шляхів. Події для другого шляху приходитимуть із першим — тихо й неправильно. Ознака в коді — `map_get(wd)` знайшов запис із іншим батьком; чесна реакція — попередити.
- **Межу дерева тримають два прапорці, а не один.** [Символьне посилання](book:unix-linux/hard-and-symbolic-links) на каталог поза деревом ловиться лише парою: `AT_SYMLINK_NOFOLLOW` не дає обхідникові в нього спуститися, `IN_DONT_FOLLOW` не дає `inotify_add_watch()` розкрити посилання, якщо шлях усе ж дійшов до нього. Без них спостерігач тихо виходить за свої межі, а на циклі посилань — зациклюється.
- **`d_type` буває `DT_UNKNOWN`.** Не всі файлові системи заповнюють це поле в `readdir()`. Код, який вірить лише `d_type == DT_DIR`, на такій ФС не спуститься нікуди й покриє один каталог. Запасний шлях — `fstatat()` [від дескриптора каталогу](book:unix-linux/at-family-syscalls), а не `stat()` за склеєним шляхом: другий варіант ще й гониться з перейменуваннями.
- **`ENOENT` під час обходу — норма, а не помилка.** Каталог могли видалити, доки ми до нього йшли; це звичайна робота файлової системи. Друкувати тут попередження означає засипати журнал шумом на кожному `git checkout`.
- **Кількість подій ≠ кількість операцій.** Однакові поспіль події (той самий `wd`, маска, `cookie`, ім'я) ядро зливає в одну, якщо читач не встиг забрати попередню. Будувати на потоці лічильники не можна — лише стан.
- **`IN_MODIFY` — не «файл готовий».** Один запис у кілька системних викликів дасть кілька подій, і читання після кожної половину разів дає недописаний вміст. Межа записаного, яку ядро вміє назвати, — `IN_CLOSE_WRITE`, і саме вона стоїть у масці.
- **`read()` у малий буфер повертає `EINVAL`.** Не короткий запис, не нуль — помилку, і то з ядра 2.6.21. Мінімум — `sizeof(struct inotify_event) + NAME_MAX + 1`.
- **Вирівнювання буфера обов'язкове.** Записи лежать упритул, і по них ходять арифметикою вказівника; невирівняний масив `char` — невизначена поведінка, яка на x86 «працює», а на інших архітектурах ні.
- **Стеження за файлом, а не за каталогом, гине від першого ж збереження.** Обережні редактори пишуть у тимчасовий файл і роблять `rename()` поверх — ім'я веде на новий inode, стеження лишається на старому. Тому в цій програмі стеження ставлять **лише** на каталоги, а про файли дізнаються з подій їхнього каталогу.
