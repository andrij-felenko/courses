# ⚙️ Обхід дерева за тотожністю inode

Це програма на C, яка обходить дерево каталогів і чесно каже, скільки місця воно займає, — тобто рахує кожен файл рівно один раз, скільки б імен на нього не вело. Усе цікаве тут крутиться навколо однієї операції: перш ніж додати чиїсь блоки до підсумку, треба спитати «а це, бува, не той самий об'єкт, що я вже бачив?» — і відповісти на це питання правильно можна лише парою `(st_dev, st_ino)`. Побічно вийде інструмент, який показує групи жорстких посилань, знаходить розріджені файли й не бреше, коли частина дерева виявилася недоступною.

## Що саме треба порахувати

Слово «розмір» приховує три різні числа, і плутати їх — найшвидший спосіб отримати неправильний підсумок.

```
номінальний обсяг = Σ st_size          скільки байтів видно програмі, що читає файл
реальний обсяг    = Σ st_blocks · 512  скільки блоків носія під це віддано
наївний підсумок  = Σ по ІМЕНАХ        те саме, але з подвійним обліком
```

Перше й друге розходяться в обидва боки. Файл із дірами займає менше, ніж показує `st_size`; файл із непрямими блоками або з майже порожнім хвостовим блоком займає більше. Третє відрізняється від другого рівно на те, заради чого й писано цю програму: якщо просто йти по іменах і додавати, то файл із десятьма [жорсткими посиланнями](topic:unix-linux/hard-and-symbolic-links) — тобто десятьма записами в каталогах, які ведуть до одного inode, — додасться десять разів.

Одиниця `st_blocks` заслуговує на окреме речення, бо вона не така очевидна, як здається. У Linux вона зафіксована й дорівнює **512 байтам** незалежно від того, який розмір блока має файлова система і що каже `st_blksize`. POSIX цю одиницю навмисно не визначає: у тексті стандарту сказано лише «кількість блоків, виділених цьому об'єктові», а в поясненнях — що одиниця не встановлена й «у деяких реалізаціях це 512 байтів». Тому множник `512` у переносному коді доводиться або тримати як припущення про Linux, або питати систему іншим способом; у нашій програмі це припущення, і воно чесно винесене в одну константу.

Що ж до того, який підсумок «правильний», — правильні обидва, просто вони відповідають на різні питання. Реальний обсяг каже, скільки місця звільниться, якщо дерево стерти. Номінальний каже, скільки байтів доведеться передати, якщо дерево скопіювати наївним читанням. `du` типово друкує перший, а з `--apparent-size` — другий; і в його ж документації прямо сказано, що номінальний обсяг «зазвичай менший, але може бути й більшим через діри в розріджених файлах, внутрішню фрагментацію, непрямі блоки тощо».

## Чим ходити по дереву

Найкоротший шлях — `nftw`: одна функція, зворотний виклик на кожен об'єкт, прапорці `FTW_PHYS` («не йти за символьними посиланнями») і `FTW_MOUNT` («не перетинати межі монтування»). Для одноразового скрипта цього досить, і в документації навіть стоїть підказка про `FTW_PHYS`: «це те, чого ви хочете».

Ми напишемо обхід руками, і не з любові до довгого коду, а через три речі, яких `nftw` не дає.

По-перше, зворотний виклик `nftw` не має параметра для власних даних — усе, що обхід накопичує, доводиться тримати в глобальних змінних. Для програми, яка збирає таблицю на мільйон записів, це не стиль, а обмеження: два дерева паралельно вже не порахуєш.

По-друге, `nftw` розпитує систему про кожен об'єкт **за повним шляхом**. Кожен такий `stat` заново розбирає весь шлях від кореня, а між розбором каталогу й розбором файлу в ньому хтось міг перейменувати проміжний каталог — і `stat` потрапить не туди, куди ми дивилися. Виклики [сімейства `*at`](topic:unix-linux/at-family-syscalls) знімають цю проблему: `fstatat(dfd, "name", …)` відлічує ім'я від **уже відкритого дескриптора каталогу**, тож проміжні складники шляху взагалі не беруть участі — вони вже розібрані один раз і зафіксовані в дескрипторі.

По-третє, `nftw` тримає ті самі відкриті каталоги, що й ми, тільки ховає це за параметром `nopenfd`: коли глибина перевищує вказану кількість, він, за словами документації, «стає повільнішим, бо каталоги доводиться закривати й відкривати наново». Перевідкриття каталогу — це знову розбір шляху, тобто знову те саме вікно для підміни, і воно з'являється тим частіше, чим глибше дерево.

Отже, схема обходу така: тримаємо дескриптор поточного каталогу, читаємо з нього імена, кожне ім'я перевіряємо через `fstatat` відносно того самого дескриптора, у підкаталоги спускаємося через `openat` відносно нього ж. Ім'я живе в [каталозі як відображення «ім'я → номер»](topic:unix-linux/directory-as-mapping), і ми жодного разу не збираємо з імен рядок, який довелося б розбирати наново, — повний шлях будуємо тільки для друку.

## Таблиця тотожності — і чому вона мала

Ядро задачі: перед тим як додати блоки, спитати, чи ми вже бачили цей inode. Питання ставиться мільйони разів, тож структура має відповідати за сталий час — це класична [хеш-таблиця](topic:algorithms/hash-table) з ключем `(st_dev, st_ino)`.

Наївна реалізація кладе в таблицю **кожен** зустрінутий файл. На дереві з мільйона файлів це мільйон записів по кілька десятків байтів плюс збережені шляхи — сотні мегабайтів заради того, щоб кілька тисяч разів відповісти «так, бачив».

Тепер придивімося до `st_nlink`. Це лічильник імен, які ведуть до inode. Якщо він дорівнює одиниці, файл має рівно одне ім'я в усій файловій системі — а отже, **фізично не може трапитися нам удруге**, і класти його в таблицю немає жодного сенсу. У звичайному дереві таких файлів зазвичай понад 99 %. Одна перевірка `st_nlink <= 1` зрізає таблицю з мільйона записів до кількох тисяч.

Каталоги теж не потрапляють у таблицю, але з іншої причини. У них `st_nlink` завжди більший за одиницю (`.` усередині себе, `..` у кожному підкаталозі), проте жорстко зв'язати каталоги не можна — Linux на `link()` для каталогу віддає `EPERM`, — а наш обхід і так заходить у кожен каталог рівно раз. Тримати їх у таблиці означало б роздути її назад і ще й отримати фальшиві «групи посилань».

> 🔧 **Навіщо це.** Коли файл уже в таблиці, поряд з ним безкоштовно лежить друге, значно корисніше число: скільки його імен ми зустріли **всередині дерева**. Порівняння цього лічильника з `st_nlink` відповідає на питання, яке інакше вимагає обходу всієї файлової системи: «якщо стерти це дерево, місце звільниться чи ні?» Якщо ми бачили всі 9 імен із 9 — так, звільниться. Якщо 4 з 7 — ні: три імені живуть десь поза деревом, і після видалення блоки лишаться зайнятими. Саме тут ламається звична інтуїція «видалив теку — звільнив стільки, скільки показав `du`».

## Код

Програма — один файл. Збирається без жодних залежностей:

```sh
cc -Wall -Wextra -O2 -o inodesum inodesum.c
./inodesum /var/backup
./inodesum -x /                 # не перетинати межі монтування
```

Почнімо з каркаса, дрібних помічників і структур. Дві речі тут варті погляду: обгортки з повтором на `EINTR` і буфер шляху, який росте, а не обрізає імена.

:::tabs
```c
/* inodesum.c — облік місця в дереві за тотожністю inode.
 *
 *   cc -Wall -Wextra -O2 -o inodesum inodesum.c
 *
 * POSIX.1-2008 (openat/fstatat/fdopendir). Одиниця st_blocks — 512 Б: це
 * правда для Linux, POSIX її не фіксує.
 */
#define _POSIX_C_SOURCE 200809L

#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#define BLOCK_UNIT   512      /* одиниця st_blocks у Linux */
#define SPARSE_TOP   5        /* скільки найдірявіших файлів показати */

/* Локальні ФС переривань зазвичай не віддають, а от FUSE і мережеві —
 * цілком. Повторюємо самі: перерваний виклик не є помилкою. */
static int fstatat_retry(int dfd, const char *name, struct stat *st, int flags)
{
    int r;
    do { r = fstatat(dfd, name, st, flags); } while (r != 0 && errno == EINTR);
    return r;
}

static int openat_retry(int dfd, const char *name, int flags)
{
    int fd;
    do { fd = openat(dfd, name, flags); } while (fd < 0 && errno == EINTR);
    return fd;
}

/* ── шлях, який росте ────────────────────────────────────────────────── */

struct pathbuf { char *s; size_t len, cap; };

static int path_reserve(struct pathbuf *p, size_t need)
{
    if (need <= p->cap) return 1;
    size_t cap = p->cap ? p->cap : 256;
    while (cap < need) cap *= 2;
    char *s = realloc(p->s, cap);
    if (s == NULL) return 0;
    p->s = s; p->cap = cap;
    return 1;
}

static int path_set(struct pathbuf *p, const char *s)
{
    size_t n = strlen(s);
    if (!path_reserve(p, n + 1)) return 0;
    memcpy(p->s, s, n + 1);
    p->len = n;
    return 1;
}

/* Дописує "/ім'я". Викликач запам'ятовує p->len ДО виклику і відновлює
 * його після — це і є вихід із підкаталогу. */
static int path_push(struct pathbuf *p, const char *name)
{
    size_t n = strlen(name);
    if (!path_reserve(p, p->len + 1 + n + 1)) return 0;
    if (p->len > 0 && p->s[p->len - 1] != '/')
        p->s[p->len++] = '/';
    memcpy(p->s + p->len, name, n + 1);
    p->len += n;
    return 1;
}

/* ── список імен одного каталогу ─────────────────────────────────────── */

struct namelist { char **v; size_t n, cap; };

static int names_push(struct namelist *l, const char *name)
{
    if (l->n == l->cap) {
        size_t cap = l->cap ? l->cap * 2 : 64;
        char **v = realloc(l->v, cap * sizeof *v);
        if (v == NULL) return 0;
        l->v = v; l->cap = cap;
    }
    char *copy = strdup(name);
    if (copy == NULL) return 0;
    l->v[l->n++] = copy;
    return 1;
}

static void names_free(struct namelist *l)
{
    for (size_t i = 0; i < l->n; i++) free(l->v[i]);
    free(l->v);
    memset(l, 0, sizeof *l);
}

static int cmp_name(const void *a, const void *b)
{
    return strcmp(*(char *const *)a, *(char *const *)b);
}
```
```cpp
// У C++ ручне керування пам'яттю для шляхів та списків імен замінюють стандартом C++17/20
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <algorithm>
#include <unordered_map>
#include <memory>
#include <system_error>
#include <dirent.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

constexpr uintmax_t BLOCK_UNIT = 512;
constexpr size_t SPARSE_TOP = 5;

inline int fstatat_retry(int dfd, const char *name, struct stat *st, int flags) {
    int r;
    do { r = ::fstatat(dfd, name, st, flags); } while (r != 0 && errno == EINTR);
    return r;
}

inline int openat_retry(int dfd, const char *name, int flags) {
    int fd;
    do { fd = ::openat(dfd, name, flags); } while (fd < 0 && errno == EINTR);
    return fd;
}

// Замість ручних struct pathbuf та struct namelist у C++ використовують std::string та std::vector<std::string>:
// Додавання елементів до шляху стає розширенням рядка std::string, а список імен у каталозі сортується через std::sort.
```
:::

Далі — таблиця тотожності. Ключ складений із двох чисел, і обидва погано перемішані самі по собі: номери inode в одному каталозі часто йдуть майже підряд, а `st_dev` у типовому дереві взагалі одне-два значення. Узяти залишок від такого ключа — це покласти всі файли каталогу в сусідні комірки й перетворити лінійне пробування на лінійний пошук. Тому ключ спершу проганяємо крізь відомий 64-бітний перемішувач із MurmurHash3 (`h ^= h >> 33; h *= …` тричі): він саме для того й зроблений, щоб підняти ентропію слабко перемішаного значення.

:::tabs
```c
/* ── таблиця тотожності (dev, ino) ───────────────────────────────────── */

struct node {
    dev_t     dev;
    ino_t     ino;
    uintmax_t nlink;       /* скільки імен має файл за словами inode */
    uintmax_t seen;        /* скільки з них ми зустріли в цьому дереві */
    uintmax_t size;
    uintmax_t real;        /* st_blocks · 512 */
    char     *first_path;  /* перше ім'я — щоб було що показати у звіті */
};

struct table { struct node *slot; size_t cap, used; };

/* seen == 0 означає «комірка вільна»: будь-який вставлений запис має
 * seen >= 1, тож окремий прапорець не потрібен. */

static uint64_t mix64(uint64_t h)
{
    h ^= h >> 33;
    h *= UINT64_C(0xff51afd7ed558ccd);
    h ^= h >> 33;
    h *= UINT64_C(0xc4ceb9fe1a85ec53);
    h ^= h >> 33;
    return h;
}

static uint64_t key_hash(dev_t dev, ino_t ino)
{
    return mix64((uint64_t)ino ^ mix64((uint64_t)dev));
}

static int table_init(struct table *t, size_t cap)   /* cap — степінь двійки */
{
    t->slot = calloc(cap, sizeof *t->slot);
    if (t->slot == NULL) return 0;
    t->cap = cap; t->used = 0;
    return 1;
}

static void table_put_raw(struct table *t, struct node n)
{
    size_t mask = t->cap - 1;
    size_t i = (size_t)key_hash(n.dev, n.ino) & mask;
    while (t->slot[i].seen != 0)
        i = (i + 1) & mask;
    t->slot[i] = n;
}

static int table_grow(struct table *t)
{
    struct table nt;
    if (!table_init(&nt, t->cap * 2)) return 0;
    for (size_t i = 0; i < t->cap; i++)
        if (t->slot[i].seen != 0)
            table_put_raw(&nt, t->slot[i]);
    nt.used = t->used;
    free(t->slot);
    *t = nt;
    return 1;
}

/* Повертає 1, якщо цей (dev, ino) трапився вперше — отже, його блоки
 * треба додати до підсумку; 0 — якщо це ще одне ім'я вже порахованого. */
static int table_first_time(struct table *t, const struct stat *st, const char *path)
{
    if ((t->used + 1) * 10 > t->cap * 7 && !table_grow(t))
        return 1;                       /* пам'ять скінчилася — рахуємо як нове */

    size_t mask = t->cap - 1;
    size_t i = (size_t)key_hash(st->st_dev, st->st_ino) & mask;
    while (t->slot[i].seen != 0) {
        if (t->slot[i].dev == st->st_dev && t->slot[i].ino == st->st_ino) {
            t->slot[i].seen++;
            return 0;
        }
        i = (i + 1) & mask;
    }

    t->slot[i].dev        = st->st_dev;
    t->slot[i].ino        = st->st_ino;
    t->slot[i].nlink      = (uintmax_t)st->st_nlink;
    t->slot[i].seen       = 1;
    t->slot[i].size       = (uintmax_t)st->st_size;
    t->slot[i].real       = (uintmax_t)st->st_blocks * BLOCK_UNIT;
    t->slot[i].first_path = strdup(path);   /* NULL тут не смертельний */
    t->used++;
    return 1;
}
```
```cpp
// У C++ замість відкритої адресації та ручного виділення пам'яті використовують std::unordered_map:
struct dev_ino_pair {
    dev_t dev;
    ino_t ino;
    bool operator==(const dev_ino_pair& o) const noexcept {
        return dev == o.dev && ino == o.ino;
    }
};

struct dev_ino_hash {
    std::size_t operator()(const dev_ino_pair& p) const noexcept {
        auto mix = [](uint64_t h) {
            h ^= h >> 33;
            h *= UINT64_C(0xff51afd7ed558ccd);
            h ^= h >> 33;
            h *= UINT64_C(0xc4ceb9fe1a85ec53);
            h ^= h >> 33;
            return h;
        };
        return mix(static_cast<uint64_t>(p.ino) ^ mix(static_cast<uint64_t>(p.dev)));
    }
};

struct node_info {
    uintmax_t nlink{0};
    uintmax_t seen{0};
    uintmax_t size{0};
    uintmax_t real{0};
    std::string first_path;
};

using identity_table = std::unordered_map<dev_ino_pair, node_info, dev_ino_hash>;

bool table_first_time(identity_table& table, const struct stat& st, const std::string& path) {
    dev_ino_pair key{st.st_dev, st.st_ino};
    auto [it, inserted] = table.try_emplace(key, node_info{
        static_cast<uintmax_t>(st.st_nlink), 1,
        static_cast<uintmax_t>(st.st_size),
        static_cast<uintmax_t>(st.st_blocks) * BLOCK_UNIT,
        path
    });
    if (!inserted) {
        it->second.seen++;
        return false;
    }
    return true;
}
```
:::

Тепер облік одного об'єкта — місце, де сходиться вся ідея. Зверніть увагу, що каталог і файл із єдиним іменем ідуть повз таблицю, а `shared_bytes` збирає саме те, що додав би наївний облік: це не «зекономлене місце», а «уникнутий обман».

:::tabs
```c
/* ── контекст обходу ─────────────────────────────────────────────────── */

struct sparse_hit { char *path; uintmax_t gap, size, real; };

struct ctx {
    struct table seen;
    int          one_fs;
    dev_t        root_dev;

    uintmax_t dirs, files, symlinks, others;
    uintmax_t real_bytes, apparent_bytes, shared_bytes;
    uintmax_t errors, vanished, crossings, sparse_count;

    struct sparse_hit sparse[SPARSE_TOP];
};

static void warn_at(struct ctx *c, const char *path, const char *what)
{
    c->errors++;
    fprintf(stderr, "inodesum: %s: %s: %s\n", path, what, strerror(errno));
}

/* Розрив між номінальним і реальним обсягом — ознака дір. Саме ознака,
 * а не доказ: стиснення на рівні ФС дає такий самий розрив. */
static void note_sparse(struct ctx *c, const struct stat *st, const char *path)
{
    if (!S_ISREG(st->st_mode) || st->st_size <= 0)
        return;

    uintmax_t size = (uintmax_t)st->st_size;
    uintmax_t real = (uintmax_t)st->st_blocks * BLOCK_UNIT;
    if (real >= size / 2 || size - real < ((uintmax_t)1 << 20))
        return;                     /* менш ніж половина дір або менш ніж МіБ */

    uintmax_t gap = size - real;
    c->sparse_count++;

    size_t worst = 0;
    for (size_t i = 1; i < SPARSE_TOP; i++)
        if (c->sparse[i].gap < c->sparse[worst].gap) worst = i;
    if (c->sparse[worst].gap >= gap)
        return;

    free(c->sparse[worst].path);
    c->sparse[worst].path = strdup(path);
    c->sparse[worst].gap  = gap;
    c->sparse[worst].size = size;
    c->sparse[worst].real = real;
}

static void account(struct ctx *c, const struct stat *st, const char *path)
{
    uintmax_t real = (uintmax_t)st->st_blocks * BLOCK_UNIT;
    uintmax_t size = (uintmax_t)st->st_size;

    if (S_ISDIR(st->st_mode)) {
        c->dirs++;
        c->real_bytes     += real;      /* каталог теж займає блоки */
        c->apparent_bytes += size;
        return;                         /* жорстко зв'язати каталог не можна */
    }

    if      (S_ISREG(st->st_mode)) c->files++;
    else if (S_ISLNK(st->st_mode)) c->symlinks++;
    else                           c->others++;

    /* Єдине ім'я — файл не може трапитися вдруге, у таблицю не кладемо.
     * Саме це рішення тримає таблицю в тисячах записів, а не в мільйонах. */
    if (st->st_nlink <= 1 || table_first_time(&c->seen, st, path)) {
        c->real_bytes     += real;
        c->apparent_bytes += size;
        note_sparse(c, st, path);
    } else {
        c->shared_bytes += real;        /* стільки додав би наївний обхід */
    }
}
```
```cpp
// У C++ структури описуються з ініціалізаторами за замовчуванням, а помилки — через std::system_category:
struct sparse_hit {
    std::string path;
    uintmax_t gap{0}, size{0}, real{0};
};

struct context {
    identity_table seen;
    bool one_fs{false};
    dev_t root_dev{0};

    uintmax_t dirs{0}, files{0}, symlinks{0}, others{0};
    uintmax_t real_bytes{0}, apparent_bytes{0}, shared_bytes{0};
    uintmax_t errors{0}, vanished{0}, crossings{0}, sparse_count{0};

    std::vector<sparse_hit> sparse;
};

void warn_at(context& c, const std::string& path, std::string_view what) {
    c.errors++;
    std::cerr << "inodesum: " << path << ": " << what << ": "
              << std::system_category().message(errno) << "\n";
}

void account(context& c, const struct stat& st, const std::string& path) {
    uintmax_t real = static_cast<uintmax_t>(st.st_blocks) * BLOCK_UNIT;
    uintmax_t size = static_cast<uintmax_t>(st.st_size);

    if (S_ISDIR(st.st_mode)) {
        c.dirs++;
        c.real_bytes += real;
        c.apparent_bytes += size;
        return;
    }

    if      (S_ISREG(st.st_mode)) c.files++;
    else if (S_ISLNK(st.st_mode)) c.symlinks++;
    else                          c.others++;

    if (st.st_nlink <= 1 || table_first_time(c.seen, st, path)) {
        c.real_bytes += real;
        c.apparent_bytes += size;
    } else {
        c.shared_bytes += real;
    }
}
```
:::

І сам обхід. Три оборонні деталі тут не прикраса: знімок імен, `AT_SYMLINK_NOFOLLOW` у `fstatat` і перевірка тотожності після `openat`.

:::tabs
```c
static void walk(int dfd, struct pathbuf *p, struct ctx *c)
{
    DIR *d = fdopendir(dfd);            /* DIR забирає дескриптор собі */
    if (d == NULL) {
        warn_at(c, p->s, "fdopendir");
        close(dfd);
        return;
    }

    /* 1. Знімок імен. Каталог живий, поки ми по ньому ходимо; знімок
     *    звужує вікно, у якому чужі зміни плутають нам перелік. */
    struct namelist names;
    memset(&names, 0, sizeof names);

    for (;;) {
        errno = 0;                      /* інакше NULL не відрізнити від кінця */
        struct dirent *e = readdir(d);
        if (e == NULL) {
            if (errno != 0) warn_at(c, p->s, "readdir");
            break;
        }
        if (e->d_name[0] == '.' && (e->d_name[1] == '\0' ||
            (e->d_name[1] == '.' && e->d_name[2] == '\0')))
            continue;                   /* "." і ".." — ми вже тут */
        if (!names_push(&names, e->d_name)) {
            warn_at(c, p->s, "malloc");
            break;
        }
    }

    /* Упорядкування дає передбачуваний вивід і дозволяє викинути сусідні
     * однакові імена: у каталозі на хеш-дереві поняття «зсуву» умовне, тож
     * getdents на каталозі, який змінюють просто зараз, може віддати той
     * самий запис двічі. */
    qsort(names.v, names.n, sizeof *names.v, cmp_name);

    int fd = dirfd(d);                  /* потрібен для fstatat/openat */

    for (size_t i = 0; i < names.n; i++) {
        if (i > 0 && strcmp(names.v[i], names.v[i - 1]) == 0)
            continue;

        const char *name = names.v[i];
        size_t saved = p->len;
        if (!path_push(p, name)) { warn_at(c, p->s, "realloc"); break; }

        struct stat st;
        /* 2. Саме lstat-семантика: символьне посилання описуємо як
         *    посилання. Інакше ціль порахувалася б удруге, а посилання на
         *    каталог відправило б обхід у нескінченну петлю. */
        if (fstatat_retry(fd, name, &st, AT_SYMLINK_NOFOLLOW) != 0) {
            if (errno == ENOENT) c->vanished++;   /* зникло між знімком і stat */
            else                 warn_at(c, p->s, "fstatat");
            goto next;
        }

        account(c, &st, p->s);

        if (S_ISDIR(st.st_mode)) {
            if (c->one_fs && st.st_dev != c->root_dev) {
                c->crossings++;
                goto next;
            }

            int sub = openat_retry(fd, name,
                                   O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
            if (sub < 0) { warn_at(c, p->s, "openat"); goto next; }

            /* 3. Те саме питання тотожності, тільки в ролі охорони: чи це
             *    той самий об'єкт, який ми щойно розглядали? Між fstatat і
             *    openat ім'я могли перевісити на інший каталог. */
            struct stat sst;
            if (fstat(sub, &sst) != 0 ||
                sst.st_dev != st.st_dev || sst.st_ino != st.st_ino) {
                fprintf(stderr, "inodesum: %s: підмінено між stat і open\n", p->s);
                c->errors++;
                close(sub);
                goto next;
            }

            walk(sub, p, c);            /* walk забирає дескриптор собі */
        }
    next:
        p->len = saved;                 /* вихід із підкаталогу */
        p->s[saved] = '\0';
    }

    names_free(&names);
    closedir(d);                        /* закриває й сам дескриптор */
}
```
```cpp
// У C++ обхід реалізують із використанням RAII для DIR* та std::vector<std::string>:
struct unique_dir {
    DIR* d{nullptr};
    explicit unique_dir(DIR* dir) : d(dir) {}
    ~unique_dir() { if (d) ::closedir(d); }
    unique_dir(const unique_dir&) = delete;
    unique_dir& operator=(const unique_dir&) = delete;
    DIR* get() const { return d; }
    explicit operator bool() const { return d != nullptr; }
};

void walk(int dfd, std::string& path, context& c) {
    unique_dir dir{::fdopendir(dfd)};
    if (!dir) {
        warn_at(c, path, "fdopendir");
        ::close(dfd);
        return;
    }

    std::vector<std::string> names;
    for (;;) {
        errno = 0;
        struct dirent *e = ::readdir(dir.get());
        if (!e) {
            if (errno != 0) warn_at(c, path, "readdir");
            break;
        }
        if (e->d_name[0] == '.' && (e->d_name[1] == '\0' || 
            (e->d_name[1] == '.' && e->d_name[2] == '\0')))
            continue;
        names.emplace_back(e->d_name);
    }

    std::sort(names.begin(), names.end());
    int fd = ::dirfd(dir.get());

    for (size_t i = 0; i < names.size(); ++i) {
        if (i > 0 && names[i] == names[i - 1]) continue;

        const auto& name = names[i];
        size_t saved_len = path.length();
        if (!path.empty() && path.back() != '/') path += '/';
        path += name;

        struct stat st{};
        if (fstatat_retry(fd, name.c_str(), &st, AT_SYMLINK_NOFOLLOW) != 0) {
            if (errno == ENOENT) c.vanished++;
            else warn_at(c, path, "fstatat");
            path.resize(saved_len);
            continue;
        }

        account(c, st, path);

        if (S_ISDIR(st.st_mode)) {
            if (c.one_fs && st.st_dev != c.root_dev) {
                c.crossings++;
                path.resize(saved_len);
                continue;
            }

            int sub = openat_retry(fd, name.c_str(), O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
            if (sub < 0) { warn_at(c, path, "openat"); path.resize(saved_len); continue; }

            struct stat sst{};
            if (::fstat(sub, &sst) != 0 || sst.st_dev != st.st_dev || sst.st_ino != st.st_ino) {
                warn_at(c, path, "підмінено між stat і open");
                ::close(sub);
                path.resize(saved_len);
                continue;
            }

            walk(sub, path, c);
        }
        path.resize(saved_len);
    }
}
```
:::

Лишився звіт і точка входу. Таблиця тут працює вдруге — уже не як фільтр, а як джерело даних про групи посилань.

:::tabs
```c
/* ── звіт ────────────────────────────────────────────────────────────── */

static const char *human(uintmax_t bytes, char *buf, size_t n)
{
    static const char *unit[] = { "Б", "КіБ", "МіБ", "ГіБ", "ТіБ", "ПіБ" };
    double v = (double)bytes;
    size_t u = 0;
    while (v >= 1024.0 && u + 1 < sizeof unit / sizeof *unit) { v /= 1024.0; u++; }
    if (u == 0) snprintf(buf, n, "%ju Б", bytes);
    else        snprintf(buf, n, "%.1f %s", v, unit[u]);
    return buf;
}

static int cmp_group(const void *a, const void *b)
{
    const struct node *x = a, *y = b;
    uintmax_t wx = (x->seen - 1) * x->real, wy = (y->seen - 1) * y->real;
    return wx < wy ? 1 : (wx > wy ? -1 : 0);
}

static void report(struct ctx *c)
{
    char b[4][32];

    size_t ng = 0;
    for (size_t i = 0; i < c->seen.cap; i++)
        if (c->seen.slot[i].seen > 1) ng++;

    printf("\n──── підсумок ────\n");
    printf("каталогів               : %ju\n", c->dirs);
    printf("звичайних файлів        : %ju\n", c->files);
    printf("символьних посилань     : %ju\n", c->symlinks);
    printf("інших об'єктів          : %ju\n", c->others);
    printf("реальний обсяг          : %s   (Σ st_blocks·512, кожен inode раз)\n",
           human(c->real_bytes, b[0], sizeof b[0]));
    printf("номінальний обсяг       : %s   (Σ st_size)\n",
           human(c->apparent_bytes, b[1], sizeof b[1]));
    printf("подвійного обліку уникнуто: %s у %zu групах посилань\n",
           human(c->shared_bytes, b[2], sizeof b[2]), ng);
    if (c->crossings)  printf("меж монтування пропущено: %ju\n", c->crossings);
    if (c->vanished)   printf("зникло під час обходу   : %ju\n", c->vanished);
    if (c->errors)     printf("!! помилок              : %ju — підсумок НЕПОВНИЙ\n",
                              c->errors);

    if (ng > 0) {
        struct node *g = malloc(ng * sizeof *g);
        if (g != NULL) {
            size_t k = 0;
            for (size_t i = 0; i < c->seen.cap; i++)
                if (c->seen.slot[i].seen > 1) g[k++] = c->seen.slot[i];
            qsort(g, ng, sizeof *g, cmp_group);

            printf("\n──── найбільші групи посилань (імен у дереві / усього) ────\n");
            for (size_t i = 0; i < ng && i < 10; i++) {
                printf("  %10s  ×%ju/%ju  %s%s\n",
                       human((g[i].seen - 1) * g[i].real, b[3], sizeof b[3]),
                       g[i].seen, g[i].nlink,
                       g[i].first_path ? g[i].first_path : "(шлях не збережено)",
                       g[i].seen < g[i].nlink ? "   ← є імена ПОЗА деревом" : "");
            }
            free(g);
        }
    }

    if (c->sparse_count > 0) {
        printf("\n──── найдірявіші файли (%ju знайдено) ────\n", c->sparse_count);
        for (size_t i = 0; i < SPARSE_TOP; i++) {
            if (c->sparse[i].path == NULL) continue;
            printf("  розрив %s   номінально %s, реально %s\n  %s\n",
                   human(c->sparse[i].gap,  b[0], sizeof b[0]),
                   human(c->sparse[i].size, b[1], sizeof b[1]),
                   human(c->sparse[i].real, b[2], sizeof b[2]),
                   c->sparse[i].path);
        }
    }
}

int main(int argc, char **argv)
{
    struct ctx c;
    memset(&c, 0, sizeof c);
    if (!table_init(&c.seen, 1024)) { perror("calloc"); return 2; }

    int argi = 1;
    if (argi < argc && strcmp(argv[argi], "-x") == 0) { c.one_fs = 1; argi++; }
    if (argi >= argc) {
        fprintf(stderr, "вжиток: inodesum [-x] шлях...\n");
        return 2;
    }

    struct pathbuf p;
    memset(&p, 0, sizeof p);

    /* Таблиця одна на всі аргументи: інакше файл, зв'язаний із двох
     * названих дерев, порахувався б двічі. */
    for (; argi < argc; argi++) {
        if (!path_set(&p, argv[argi])) { perror("realloc"); return 2; }

        struct stat st;
        if (fstatat_retry(AT_FDCWD, p.s, &st, AT_SYMLINK_NOFOLLOW) != 0) {
            warn_at(&c, p.s, "fstatat");
            continue;
        }
        c.root_dev = st.st_dev;
        account(&c, &st, p.s);

        if (S_ISDIR(st.st_mode)) {
            int fd = openat_retry(AT_FDCWD, p.s, O_RDONLY | O_DIRECTORY | O_CLOEXEC);
            if (fd < 0) { warn_at(&c, p.s, "openat"); continue; }
            walk(fd, &p, &c);
        }
    }

    report(&c);
    free(p.s);
    return c.errors > 0 ? 1 : 0;
}
```
```cpp
// У C++ вивід форматують через std::cout та std::string, а пам'ять контейнерів звільняється автоматично:
std::string human(uintmax_t bytes)
{
    static const char *unit[] = { "Б", "КіБ", "МіБ", "ГіБ", "ТіБ", "ПіБ" };
    double v = static_cast<double>(bytes);
    size_t u = 0;
    while (v >= 1024.0 && u + 1 < sizeof(unit) / sizeof(*unit)) { v /= 1024.0; u++; }
    char buf[64];
    if (u == 0) std::snprintf(buf, sizeof(buf), "%ju Б", bytes);
    else        std::snprintf(buf, sizeof(buf), "%.1f %s", v, unit[u]);
    return buf;
}

void report(const context& c)
{
    size_t ng = 0;
    for (const auto& [key, info] : c.seen)
        if (info.seen > 1) ng++;

    std::cout << "\n──── підсумок ────\n";
    std::cout << "каталогів               : " << c.dirs << "\n";
    std::cout << "звичайних файлів        : " << c.files << "\n";
    std::cout << "символьних посилань     : " << c.symlinks << "\n";
    std::cout << "інших об'єктів          : " << c.others << "\n";
    std::cout << "реальний обсяг          : " << human(c.real_bytes) << "   (Σ st_blocks·512, кожен inode раз)\n";
    std::cout << "номінальний обсяг       : " << human(c.apparent_bytes) << "   (Σ st_size)\n";
    std::cout << "подвійного обліку уникнуто: " << human(c.shared_bytes) << " у " << ng << " групах посилань\n";
    if (c.crossings) std::cout << "меж монтування пропущено: " << c.crossings << "\n";
    if (c.vanished)  std::cout << "зникло під час обходу   : " << c.vanished << "\n";
    if (c.errors)    std::cout << "!! помилок              : " << c.errors << " — підсумок НЕПОВНИЙ\n";
}

int main(int argc, char **argv)
{
    context c;
    int argi = 1;
    if (argi < argc && std::string_view(argv[argi]) == "-x") { c.one_fs = true; argi++; }
    if (argi >= argc) {
        std::cerr << "вжиток: inodesum [-x] шлях...\n";
        return 2;
    }

    std::string path;
    for (; argi < argc; argi++) {
        path = argv[argi];

        struct stat st{};
        if (fstatat_retry(AT_FDCWD, path.c_str(), &st, AT_SYMLINK_NOFOLLOW) != 0) {
            warn_at(c, path, "fstatat");
            continue;
        }
        c.root_dev = st.st_dev;
        account(c, st, path);

        if (S_ISDIR(st.st_mode)) {
            int fd = openat_retry(AT_FDCWD, path.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC);
            if (fd < 0) { warn_at(c, path, "openat"); continue; }
            walk(fd, path, c);
        }
    }

    report(c);
    return c.errors > 0 ? 1 : 0;
}
```
:::

## Що воно друкує

На дереві добових резервних копій, де незмінені файли не копіюють, а лише додають їм ще одне ім'я, вивід має такий вигляд:

```
inodesum: /var/backup/lost+found: fdopendir: Permission denied

──── підсумок ────
каталогів               : 8312
звичайних файлів        : 203118
символьних посилань     : 2664
інших об'єктів          : 3
реальний обсяг          : 5.4 ГіБ   (Σ st_blocks·512, кожен inode раз)
номінальний обсяг       : 6.9 ГіБ   (Σ st_size)
подвійного обліку уникнуто: 3.6 ГіБ у 41208 групах посилань
!! помилок              : 1 — підсумок НЕПОВНИЙ

──── найбільші групи посилань (імен у дереві / усього) ────
       1.8 ГіБ  ×9/9   /var/backup/2026-07-28/opt/models/base.bin
     612.0 МіБ  ×4/7   /var/backup/2026-07-30/srv/media/lecture.mkv   ← є імена ПОЗА деревом
     204.7 МіБ  ×8/8   /var/backup/2026-07-28/usr/lib/libbig.so.3

──── найдірявіші файли (1 знайдено) ────
  розрив 1.4 ГіБ   номінально 1.5 ГіБ, реально 96.4 МіБ
  /var/backup/2026-07-28/var/lib/vm/disk.img
```

Три рядки тут кажуть більше, ніж уся решта.

Різниця між реальним і номінальним обсягом (5.4 проти 6.9 ГіБ) — це майже цілком діри одного образу віртуальної машини: файл, який виглядає на півтора гігабайти, віддано лише сотню мегабайтів. Рядок «уникнуто 3.6 ГіБ» каже, наскільки збрехав би підрахунок за іменами: він видав би 9.0 ГіБ замість 5.4, тобто на дві третини більше за правду, — і кожен зайвий байт там є той самий байт, показаний із різних дат. А позначка «є імена ПОЗА деревом» на `lecture.mkv` каже, що з семи його імен чотири тут, а три десь іще: видалення всієї теки резервних копій не поверне з цього файлу жодного байта, хоч у підсумку він і врахований.

## Скільки це коштує

```
викликів getdents  ≈ D · (записів_у_каталозі / записів_у_буфері)
викликів fstatat   = N
викликів openat    = D
пам'ять таблиці    ≈ M · (56 Б + довжина шляху)
пам'ять знімків    ≈ Σ по поточній гілці (записів у каталозі · довжина імені)
відкритих fd       = глибина поточної гілки

   N — усіх записів у дереві, D — каталогів, M — файлів із st_nlink > 1
```

Обчислювальна частина тут майже безкоштовна: одне перемішування ключа й одне-два звертання в масив на файл. Час з'їдають системні виклики й носій. На теплому кеші `fstatat` коштує близько мікросекунди, тож мільйон файлів — це секунди; на холодному все впирається в те, як швидко ФС віддає inode, і різниця буває стократною.

Пам'ять — той випадок, коли одна перевірка вирішує все. Мільйон файлів, із яких 40 тисяч зв'язані:

```
таблиця на все        : 1 000 000 · ≈100 Б ≈ 100 МБ
таблиця лише nlink > 1:    40 000 · ≈100 Б ≈   4 МБ
```

Рекурсія глибиною в гілку — теж не безкоштовна: кожен рівень тримає відкритий каталог. На типовому дереві глибина рідко переходить за кілька десятків, але штучно глибоке дерево впреться в `RLIMIT_NOFILE`, і `openat` поверне `EMFILE`. Наша програма тоді сумлінно поскаржиться й пропустить гілку, позначивши підсумок неповним; `nftw` у такому разі закриває й перевідкриває каталоги, платячи за це повторним розбором.

## Пастки

- **`stat` замість `lstat` — дві помилки одразу.** Символьне посилання на файл усередині дерева додасть ті самі блоки вдруге (в inode цілі `st_nlink` не збільшується від символьних посилань, тож наша таблиця його навіть не спіймає). А посилання на каталог-предка перетворить обхід на нескінченний спуск. У `fstatat` це прапорець `AT_SYMLINK_NOFOLLOW`, у `nftw` — `FTW_PHYS`, у `du` — типова поведінка `-P`.
- **Без `st_dev` облік ламається мовчки.** Номер inode унікальний лише всередині своєї файлової системи, і на двох змонтованих носіях легко трапляються однакові числа. Порівнюючи самі номери, ви ототожните два непов'язані файли й **недорахуєте** обсяг — помилка тихіша й підступніша за подвійний облік, бо підсумок просто трохи менший, ніж мав би бути.
- **`-x` не ловить bind-монтування.** Ознака «інший `st_dev`» відповідає на питання «інша файлова система?», а не «інше монтування?». Bind-монтування ділить суперблок із джерелом, тож `st_dev` у нього той самий — і обхід спокійно зайде туди вдруге. Ті файли, що мають `st_nlink > 1`, таблиця врятує; решта порахується двічі. Точну відповідь дає `statx` із маскою `STATX_MNT_ID` (Linux 5.8) або `STATX_MNT_ID_UNIQUE` (Linux 6.8), про яке в документації сказано, що воно «гарантовано не перевикористовується, поки система працює». Ширший контекст — у [дереві монтувань](topic:unix-linux/mount-model).
- **Повторне використання номерів робить кеш між запусками непридатним.** Щойно inode звільнено, його номер повертається у вільний запас, і наступний створений файл цілком може дістати те саме число. Усередині одного обходу це майже нешкідливо (потрібно, щоб файл зник і новий народився саме між двома нашими `fstatat`), але зберегти пару `(dev, ino)` в базі й порівнювати з нею завтра — гарантований спосіб переплутати два різні файли.
- **Розрив між `st_size` і `st_blocks` — ознака дір, а не доказ.** Такий самий розрив дає прозоре стиснення (Btrfs, ZFS) і вбудовування дрібного файлу просто в inode. І навпаки: `st_blocks` може перевищити `st_size`, бо непрямі блоки теж займають місце. Чесна відповідь про діри — `lseek` із `SEEK_HOLE`/`SEEK_DATA` (Linux 3.1, у ext4 з 3.8), і навіть там треба пам'ятати, що в кінці будь-якого файлу є неявна діра. Механіка — у [розріджених файлах](topic:unix-linux/sparse-files).
- **Спільні екстенти таблиця не бачить взагалі.** Копія, зроблена через reflink, — це **інший** inode, що вказує на **ті самі** блоки. Пара `(dev, ino)` в них різна, обидва порахуються повністю, і сума вийде більшою за реально зайняте місце. Це не хиба програми, а межа моделі: тотожність inode відповідає на питання «це той самий файл?», а не «це ті самі блоки?». Докладніше — у [копіях із поділом блоків](topic:unix-linux/reflink-copies).
- **`readdir` повертає `NULL` і в кінці, і при помилці.** Розрізнити їх можна лише так, як каже документація: обнулити `errno` перед викликом і перевірити його, коли повернувся `NULL`. Обхід, який цього не робить, на пошкодженому каталозі тихо звітує «тут порожньо».
- **Ім'я між `readdir` і `fstatat` може зникнути або змінити власника.** `ENOENT` тут — не аномалія, а норма на живій системі, і зупиняти через нього обхід не можна. Гірший варіант — коли за іменем опинився інший об'єкт: від цього рятує не повтор, а перевірка тотожності після відкриття, як у нашому `walk`. Загальна форма цієї помилки — [гонка між перевіркою й використанням](topic:programming/toctou-race).
- **Перелік записів каталогу — не знімок.** Каталог, збудований на хеш-дереві, перебудовується від додавань і видалень, тож «зсув», яким `readdir` продовжує читання після попереднього виклику, має умовний сенс. Якщо каталог змінюють просто зараз, перебір може віддати запис двічі або пропустити його — це не гіпотеза, а клас реальних помилок, які ловили і виправляли в самому ext4. Файл із кількома іменами таблиця врятує від подвійного обліку; файл із єдиним іменем — ні, тому сусідні однакові імена ми викидаємо самі, а на повну надійність не розраховуємо.
- **`d_type` не можна вважати відповіддю.** Поле швидке, але повне його підтримання є не в усіх файлових систем — документація прямо вимагає, щоб кожна програма вміла обробити `DT_UNKNOWN`. Нам це байдуже, бо `st_blocks` усе одно доводиться питати в `fstatat`, але обхід, який вирішує «заходити чи ні» за `d_type`, на XFS без `ftype` просто не побачить каталогів.
- **`EINTR` приходить не звідти, звідки чекаєш.** На локальній ФС `fstatat` практично не переривається, а на FUSE чи NFS — цілком. Обгортка з повтором коштує три рядки, а її відсутність дає обхід, який іноді «не бачить» файлів, коли програмі приходить сигнал; про сам механізм — у [перерваних викликах і перезапуску](topic:unix-linux/eintr-and-restart).
- **Часткова відповідь, подана як повна, гірша за помилку.** Каталог без прав на читання, знята посеред обходу тека, вичерпані дескриптори — усе це залишає підсумок меншим за правду. Тому програма друкує кількість помилок, пише «підсумок НЕПОВНИЙ» і виходить із ненульовим кодом: той, хто викликає її зі скрипта, має мати змогу відрізнити «дерево справді маленьке» від «половину дерева не прочитано».
- **Кілька аргументів — одна таблиця.** Якщо порахувати два дерева окремими запусками й додати числа, файл, зв'язаний із обох, увійде двічі. Це та сама причина, через яку окремі рядки `du` для кількох тек кожен правильний, а їхня сума — ні.
