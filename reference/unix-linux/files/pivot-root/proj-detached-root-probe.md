# ⚙️ Дослід із від'єднаним коренем: mountinfo до й після і дескриптор, що лишився дорогою

Це невелика програма мовою C, яка робить підміну кореня власними руками — без рушія контейнерів, без обгорток, самими викликами — і двічі показує дерево монтувань: до й після. Потім вона перевіряє друге, важливіше: чи справді з нового кореня немає ходу назовні. Обидві половини роблять один і той самий код, різниця лише в одному прапорці при відкритті каталогу — і цієї різниці досить, щоб дорога назовні або була, або зникла.

## Що саме міряємо

Три речі, і кожну видно числом, а не на слово.

**Перша: що зробилося з деревом монтувань.** `/proc/self/mountinfo` дає для кожного монтування його номер, пристрій, корінь усередині файлової системи й точку. Якщо надрукувати цей файл до підміни й після, буде видно, що монтування не з'явилося й не зникло: **той самий номер** опиняється в новій точці, а решта рядків зникає з таблиці цілком.

**Друга: чи проходить успадкований [дескриптор](topic:unix-linux/file-descriptor).** Каталог господаря відкриваємо **до** підміни, а торкаємося його **після** — уже з нового кореня, коли жодне ім'я туди не веде. Дескриптор іменем не є, тому питання не риторичне.

**Третя: скільки саме тієї дороги.** Від'єднаний дескриптор дає одну точку входу; далі йдемо `..` вгору, поки номер пристрою й вузла не перестане мінятися, — і дивимося, де саме впираємося в стелю.

Щоб дослід не вимагав root, простір монтувань відгалужуємо разом із власним [простором користувачів](topic:unix-linux/namespaces): у ньому процес має повний набір [можливостей](topic:unix-linux/capabilities), зокрема `CAP_SYS_ADMIN`, хоч ззовні лишається звичайним користувачем.

## Дерево для досліду

Усе живе в `/tmp/pivot-probe`:

```
/tmp/pivot-probe/
├── data/                  ← «господарська» тека; сюди дивиться успадкований дескриптор
│   └── host-secret.txt
└── img/                   ← «образ»: те, що стане коренем
    ├── only-in-image
    ├── proc/              ← порожня тека під власний procfs
    └── probe              ← копія самої програми (потрібна для execve всередині)
```

Копія програми в образі — не примха. Дескриптор із прапорцем `O_CLOEXEC` закривається не сам собою, а рівно в мить [execve](topic:unix-linux/exec-semantics); отже, щоб різниця між двома запусками взагалі проявилася, всередині нового кореня мусить бути що запускати. Рушій контейнерів робить точно те саме: готує простори, а тоді робить `execve` програми з образу.

## Програма

```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <dirent.h>
#include <sched.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <sys/syscall.h>
#include <sys/wait.h>

#define WORK "/tmp/pivot-probe"
#define IMG  WORK "/img"
#define DATA WORK "/data"
#define PROBE_FD 3          /* під цим номером дескриптор або переживе execve, або ні */

static void die(const char *what)
{
    fprintf(stderr, "    %s -> %s\n", what, strerror(errno));
    _exit(1);
}

/* Обгортки в glibc для pivot_root немає — кличемо за номером. */
static int do_pivot_root(const char *new_root, const char *put_old)
{
    return syscall(SYS_pivot_root, new_root, put_old);
}

/* Кілька імен із каталогу: доказ, у якому саме дереві ми стоїмо. */
static void list_dir(const char *label, const char *path)
{
    DIR *d = opendir(path);
    if (!d) { printf("    %s (%s): opendir -> %s\n", label, path, strerror(errno)); return; }
    printf("    %s (%s):", label, path);
    struct dirent *e; int n = 0;
    while ((e = readdir(d)) && n < 6) {
        if (!strcmp(e->d_name, ".") || !strcmp(e->d_name, "..")) continue;
        printf(" %s", e->d_name); n++;
    }
    printf("%s\n", n ? "" : " (порожньо)");
    closedir(d);
}

/* Дерево монтувань очима ядра. needle != NULL — показати лише «/» і цікаві рядки. */
static void show_mounts(const char *label, const char *needle)
{
    FILE *f = fopen("/proc/self/mountinfo", "r");
    if (!f) { printf("  %s: mountinfo -> %s\n", label, strerror(errno)); return; }
    printf("  %s (/proc/self/mountinfo):\n", label);
    char line[4096];
    int total = 0, shown = 0;
    while (fgets(line, sizeof line, f)) {
        int id, parent; char dev[32], root[512], point[512];
        total++;
        /* формат: id parent major:minor корінь точка опції … - тип джерело … */
        if (sscanf(line, "%d %d %31s %511s %511s", &id, &parent, dev, root, point) != 5)
            continue;
        char *sep = strstr(line, " - ");
        const char *type = sep ? strtok(sep + 3, " \n") : NULL;
        if (!type) type = "?";
        if (needle && strcmp(point, "/") && !strstr(point, needle)) continue;
        printf("    id=%-4d %-7s root=%-24s point=%-32s %s\n", id, dev, root, point, type);
        shown++;
    }
    printf("    (усього рядків: %d, показано: %d)\n", total, shown);
    fclose(f);
}

static void write_file(const char *path, const char *data)
{
    int fd = open(path, O_WRONLY);
    if (fd < 0) return;                      /* setgroups на дуже старих ядрах відсутній */
    if (write(fd, data, strlen(data)) < 0) perror("    write");
    close(fd);
}

/* Стати нулем у власному просторі користувачів. Непривілейованому процесу
   дозволено записати рівно один рядок — відображення власного uid. */
static void map_self_to_root(uid_t uid, gid_t gid)
{
    char buf[64];
    write_file("/proc/self/setgroups", "deny");   /* без цього gid_map не приймуть */
    snprintf(buf, sizeof buf, "0 %u 1\n", (unsigned)uid);
    write_file("/proc/self/uid_map", buf);
    snprintf(buf, sizeof buf, "0 %u 1\n", (unsigned)gid);
    write_file("/proc/self/gid_map", buf);
}

/* Уся послідовність рушія контейнерів — від unshare до chdir("/"). */
static void enter_image(uid_t uid, gid_t gid, int cloexec)
{
    if (unshare(CLONE_NEWUSER | CLONE_NEWNS) != 0) die("unshare(NEWUSER|NEWNS)");
    map_self_to_root(uid, gid);

    /* корінь рекурсивно приватний: інакше подія піде в чужі простори */
    if (mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) != 0) die("make-rprivate /");

    /* образ сам до себе: переносити нема чого, потрібен лише об'єкт монтування */
    if (mount(IMG, IMG, NULL, MS_BIND | MS_REC, NULL) != 0) die("bind образу самого до себе");

    /* свій procfs, інакше після підміни дивитися на дерево не буде звідки */
    if (mount("proc", IMG "/proc", "proc", MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL) != 0)
        printf("    (свій /proc не змонтувався: %s)\n", strerror(errno));

    /* дескриптор у господарську теку — відкритий ДО підміни кореня */
    int fd = open(DATA, O_RDONLY | O_DIRECTORY | (cloexec ? O_CLOEXEC : 0));
    if (fd < 0) die("open(" DATA ")");
    if (fd != PROBE_FD) {
        if (dup3(fd, PROBE_FD, cloexec ? O_CLOEXEC : 0) < 0) die("dup3");
        close(fd);
    }

    show_mounts("ДО", "pivot-probe");

    if (chdir(IMG) != 0)               die("chdir(образ)");
    if (do_pivot_root(".", ".") != 0)  die("pivot_root(\".\", \".\")");
    if (umount2(".", MNT_DETACH) != 0) die("umount2(\".\", MNT_DETACH)");
    if (chdir("/") != 0)               die("chdir(\"/\")");
}

/* Підйом «..», доки пристрій і вузол не перестануть мінятися. */
static void climb(void)
{
    struct stat prev, cur;
    if (stat(".", &prev) != 0) { perror("    stat(.)"); return; }
    for (int i = 1; i <= 8; i++) {
        if (chdir("..") != 0) { printf("    крок %d вгору -> %s\n", i, strerror(errno)); return; }
        if (stat(".", &cur) != 0) { perror("    stat(.)"); return; }
        printf("    крок %d вгору: %u:%u ino=%lu%s\n", i,
               major(cur.st_dev), minor(cur.st_dev), (unsigned long)cur.st_ino,
               (cur.st_dev == prev.st_dev && cur.st_ino == prev.st_ino) ? " — не змінилось, стеля" : "");
        if (cur.st_dev == prev.st_dev && cur.st_ino == prev.st_ino) { list_dir("стеля", "."); return; }
        prev = cur;
    }
}

/* Те, що виконується вже ПІСЛЯ execve — усередині нового кореня. */
static void payload(void)
{
    list_dir("корінь контейнера", "/");
    show_mounts("ПІСЛЯ", NULL);

    if (fchdir(PROBE_FD) != 0) {
        printf("    fchdir(%d) -> %s — дороги у від'єднане дерево немає\n",
               PROBE_FD, strerror(errno));
        return;
    }
    printf("    fchdir(%d) -> успіх: поточний каталог у від'єднаному дереві\n", PROBE_FD);
    list_dir("під дескриптором", ".");
    climb();
}

static void run(const char *title, int cloexec, uid_t uid, gid_t gid)
{
    printf("== %s ==\n", title);
    fflush(stdout);
    pid_t p = fork();
    if (p == 0) {
        enter_image(uid, gid, cloexec);
        char *av[] = { (char *)"/probe", (char *)"--payload", NULL };
        fflush(NULL);            /* інакше буфер stdout загине разом зі старим образом пам'яті */
        execv("/probe", av);
        die("execv(/probe)");
    }
    waitpid(p, NULL, 0);
    putchar('\n');
}

/* Свідомо зіпсований запуск: кожна пропущена дія дає свій код помилки. */
static void attempt(const char *title, int own_userns, int do_private, int do_bind,
                    int alien_userns, uid_t uid, gid_t gid)
{
    pid_t p = fork();
    if (p != 0) { waitpid(p, NULL, 0); return; }

    printf("  %s\n", title);
    int flags = CLONE_NEWNS | (own_userns ? CLONE_NEWUSER : 0);
    if (unshare(flags) != 0) { printf("    unshare -> %s\n", strerror(errno)); _exit(1); }
    if (own_userns) map_self_to_root(uid, gid);
    if (do_private && mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) != 0) die("make-rprivate");
    if (do_bind && mount(IMG, IMG, NULL, MS_BIND, NULL) != 0) die("bind");
    /* другий простір користувачів: простір монтувань лишається за першим,
       а можливостей у ньому в нас уже немає */
    if (alien_userns && unshare(CLONE_NEWUSER) != 0) die("другий unshare(NEWUSER)");

    if (chdir(IMG) != 0) die("chdir(образ)");
    if (do_pivot_root(".", ".") != 0) printf("    pivot_root -> %s\n", strerror(errno));
    else                              printf("    pivot_root -> несподіваний успіх\n");
    _exit(0);
}

static void copy_self(const char *dst)
{
    int in = open("/proc/self/exe", O_RDONLY);
    int out = open(dst, O_WRONLY | O_CREAT | O_TRUNC, 0755);
    if (in < 0 || out < 0) die("копіювання probe в образ");
    char buf[65536]; ssize_t n;
    while ((n = read(in, buf, sizeof buf)) > 0)
        if (write(out, buf, n) != n) die("write");
    close(in); close(out);
}

int main(int argc, char **argv)
{
    if (argc > 1 && !strcmp(argv[1], "--payload")) { payload(); return 0; }

    /* ДО unshare: після нього getuid() дасть 65534, бо наш uid ще не відображено */
    uid_t uid = getuid();
    gid_t gid = getgid();

    mkdir(WORK, 0755); mkdir(IMG, 0755); mkdir(IMG "/proc", 0755); mkdir(DATA, 0755);
    close(open(DATA "/host-secret.txt", O_CREAT | O_WRONLY, 0644));
    close(open(IMG  "/only-in-image",   O_CREAT | O_WRONLY, 0644));
    copy_self(IMG "/probe");

    run("A. дескриптор без O_CLOEXEC", 0, uid, gid);
    run("Б. той самий дескриптор із O_CLOEXEC", 1, uid, gid);

    puts("== В. три способи не дійти до підміни ==");
    attempt("образ не прив'язали сам до себе:",            1, 1, 0, 0, uid, gid);
    attempt("простір монтувань належить чужому userns:",   1, 1, 1, 1, uid, gid);
    if (geteuid() == 0)
        attempt("корінь лишився спільним (лише під sudo):", 0, 0, 1, 0, uid, gid);
    else
        puts("  корінь лишився спільним: у безкореневому запуску не відтворюється (див. нижче)");
    return 0;
}
```

## Як зібрати й запустити

```
cc -static -Wall -O2 -o probe probe.c
./probe
```

`-static` тут обов'язковий. Програма копіює саму себе в образ і робить там `execve`, а в образі немає ні динамічного завантажувача, ні libc — [динамічно злінкований](topic:unix-linux/static-and-dynamic-linking) файл дав би `ENOENT` від `execve`, і виглядало б це так, ніби бінарника немає, хоча він на місці. Це, до речі, найчастіша причина плутанини при першому знайомстві з контейнерами.

Справжній root не потрібен: `unshare(CLONE_NEWUSER)` дає повний набір можливостей у власному просторі. Якщо цей виклик віддає `EPERM`, безкореневі простори користувачів вимкнено адміністративно — Ubuntu з 24.04 обмежує їх через AppArmor (`sysctl kernel.apparmor_restrict_unprivileged_userns`), деякі складання Debian мають `kernel.unprivileged_userns_clone`. Тоді лишається `sudo ./probe`.

## Що друкує перший запуск

```
== A. дескриптор без O_CLOEXEC ==
  ДО (/proc/self/mountinfo):
    id=201  259:2   root=/                    point=/                                ext4
    id=232  0:24    root=/pivot-probe/img     point=/tmp/pivot-probe/img             tmpfs
    id=233  0:31    root=/                    point=/tmp/pivot-probe/img/proc        proc
    (усього рядків: 31, показано: 3)
    корінь контейнера (/): only-in-image proc probe
  ПІСЛЯ (/proc/self/mountinfo):
    id=232  0:24    root=/pivot-probe/img     point=/                                tmpfs
    id=233  0:31    root=/                    point=/proc                            proc
    (усього рядків: 2, показано: 2)
    fchdir(3) -> успіх: поточний каталог у від'єднаному дереві
    під дескриптором (.): host-secret.txt
    крок 1 вгору: 0:24 ino=5338
    крок 2 вгору: 0:24 ino=1
    крок 3 вгору: 259:2 ino=2
    крок 4 вгору: 259:2 ino=2 — не змінилось, стеля
    стеля (.): bin boot dev etc home lib
```

Номери й вузли на вашій машині будуть інші; важать не вони, а те, які з них збігаються між рядками.

## Як читати цей вивід

**Тридцять один рядок став двома.** Це не приховування: `mountinfo` показує лише монтування, досяжні від кореня процесу, а після `umount2(".", MNT_DETACH)` старе піддерево з таблиці простору просто зникло. Перевірити, що воно «десь є, тільки не видно», через імена неможливо — імен не лишилося.

**Номер 232 той самий до й після.** Монтування, яке ми зробили прив'язкою образу самого до себе, не пересотворювалося: той самий об'єкт до виклику стояв у точці `/tmp/pivot-probe/img`, після виклику стоїть у точці `/`. Це і є вся суть операції — переставляння точок у наявних об'єктах. Так само вцілів `id=233`: змонтований усередині образу procfs поїхав разом із батьком і став `/proc` контейнера.

**Поле `root` нового кореня лишилося чесним.** У `mountinfo` це шлях кореня монтування **всередині його файлової системи**, і він каже `/pivot-probe/img` — бо `/tmp` тут окремий tmpfs, і в його суперблоці образ лежить саме там. Корінь контейнера не став новою файловою системою; він і далі є підкаталогом чужого суперблока, просто [розбір шляхів](topic:unix-linux/path-resolution) для цього процесу тепер починається з нього. Хто хоче побачити, звідки взявся корінь контейнера, дивиться саме на це поле — воно перше видає бідність ізоляції, побудованої на самій лише підміні кореня.

## Другий запуск

Той самий код, та сама послідовність, різниця в одному прапорці при `open`:

```
== Б. той самий дескриптор із O_CLOEXEC ==
  ...
    корінь контейнера (/): only-in-image proc probe
    fchdir(3) -> Bad file descriptor — дороги у від'єднане дерево немає
```

`EBADF` означає, що номера 3 в процесі більше немає: `execve` закрив його, бо на дескрипторі стояв прапорець `FD_CLOEXEC`. Дерево монтувань в обох запусках однакове до останнього номера — його вигляд не пояснює жодної з двох поведінок. Тобто підміна кореня зробила рівно те, що обіцяла, і рівно стільки: прибрала **імена**. Чи лишиться дорога через дескриптори — вирішує не ядро, а програма, яка їх відкривала.

Саме на цій межі стояла вразливість `CVE-2024-21626` у `runc`: рушій усе робив правильно з монтуваннями й лишав відкритим один свій внутрішній дескриптор у дерево господаря.

## Де в цьому дереві стеля

Найцікавіше — підйом. Дескриптор дає одну точку входу, `data`; далі йдемо звичайним `..`, і кожен крок друкує пристрій і вузол:

- крок 1 і 2 підіймають нас у межах tmpfs (`0:24`) до кореня `/tmp`;
- крок 3 **міняє пристрій** на `259:2` — ми перетнули межу монтування й опинилися в кореневій файловій системі господаря. Це видимий доказ того, що `MNT_DETACH` зняв із дерева ціле піддерево, лишивши монтування всередині нього з'єднаними між собою як були: `..` на корені tmpfs штатно стрибнув на точку монтування `/tmp` у батьківському монтуванні;
- крок 4 не змінює нічого. Ми на корені від'єднаного піддерева, і в нього більше немає батька, куди стрибати. Ядро тут не віддає помилки — воно робить те саме, що на `/..` звичайного кореня: лишає вас на місці. `chdir("..")` повертає нуль, і лише незмінні `dev`/`ino` показують, що рух припинився.

Що ж до `ENOENT`, який часто згадують поруч, — це інша, вужча перевірка. Функція `path_connected` з'явилася в серпні 2015 року (автор Ерік Бідерман; мейнлайн 4.3, звідти бекпорт у стабільні гілки) і повертає `-ENOENT`, коли при обробці `..` батьківський каталог виявляється **недосяжним від кореня свого монтування**. Пізніше перевірку звузили до монтувань, чий корінь — підкаталог файлової системи; для монтування цілої файлової системи вона завжди проходить. Тому в нашому досліді її не видно: старе кореневе монтування охоплює свій суперблок цілком. Але зникає вона з поля зору не тому, що дірка закрита, а тому, що впертися в цю стелю й не треба — під нею вже вся машина.

## Три способи не дійти до підміни

```
== В. три способи не дійти до підміни ==
  образ не прив'язали сам до себе:
    pivot_root -> Invalid argument
  простір монтувань належить чужому userns:
    pivot_root -> Operation not permitted
  корінь лишився спільним: у безкореневому запуску не відтворюється (див. нижче)
```

**`EINVAL` без прив'язки.** Виклик переставляє об'єкт монтування; якщо на майбутньому корені його немає, переставляти нічого. Тека з розпакованим образом сама по собі — не точка монтування, і `mount(IMG, IMG, NULL, MS_BIND, NULL)` не переносить жодного байта, а створює саме той об'єкт, якого бракує.

**`EPERM` через чужий власника.** Другий `unshare(CLONE_NEWUSER)` виглядає безневинно: ми ж лише додали собі ще один простір користувачів, у якому теж повновладні. Але простір монтувань лишився за **першим**, а можливостей у ньому в нас уже немає — процес володіє можливостями у своєму просторі й у його нащадках, не в предках. Ядро перевіряє `CAP_SYS_ADMIN` саме у власника простору монтувань, тому відповідь — `EPERM`. Це та сама помилка, у яку впираються, коли ставлять `setns` не в тому порядку.

**`EINVAL` через спільне поширення** відтворюється лише в привілейованому запуску — і це не дрібниця, а корисний факт про безкореневі контейнери. Коли простір монтувань створює процес із **іншого** простору користувачів, ядро понижує спільні монтування до підлеглих: «shared mounts are reduced to slave mounts», як прямо каже `mount_namespaces(7)`. Тож у безкореневому запуску батько нового кореня вже не `MS_SHARED`, і `pivot_root` проходить навіть без `--make-rprivate`. Під `sudo ./probe` (простір монтувань відгалужується в тому самому просторі користувачів) копії лишаються спільними, і той самий код одразу дає `EINVAL`.

## Пастки, на яких легко спіткнутися

**`getuid()` треба взяти до `unshare`.** Після створення простору користувачів і до запису відображення ваш uid у ньому не відображений, і `getuid()` віддає `65534`. Записати `0 65534 1` — значить відобразити не себе, і ядро відмовить.

**`MNT_DETACH` не замінюється звичайним `umount`.** У старому дереві повно відкритих файлів — це вся машина, — тож негайне зняття дало б `EBUSY`. І окремо: у безкореневому запуску монтування, успадковані з привілейованішого простору, замкнені разом і поодинці не знімаються (`EINVAL`). Знімати ціле піддерево старого кореня після `pivot_root` — дозволено, і саме тому ця ідіома підходить безкореневим рушіям, а спроба «просто відмонтувати зайве» — ні.

**`chdir("/")` наприкінці — не гігієна.** Ядро переставляє поточний каталог лише тим, у кого він указував точно на старий кореневий каталог; наш стояв на образі — тобто на монтуванні, яке саме й стало кореневим, — і виклик його не чіпав. Тонкість в іншому: розбір імені `"."` перед зняттям давав верхній шар стосу, старий корінь (на цьому й тримається `umount2(".", MNT_DETACH)`), а на що показуватиме `/proc/self/cwd` після підміни, ядро не обіцяє — тому поточний каталог задають явно. У загальній ідіомі, де перед викликом стоять деінде в старому дереві, без цього рядка перший же відносний шлях відкрився б у щойно від'єднаному піддереві.

**Власний procfs може не змонтуватися.** Ядро дозволяє новий екземпляр `proc` у просторі користувачів лише тоді, коли наявний [/proc](topic:unix-linux/proc-filesystem) видно повністю. Якщо ви запускаєте дослід усередині іншого контейнера, де `/proc` частково прикритий, буде `EPERM` — і подивитися на [дерево монтувань](topic:unix-linux/mount-model) після підміни стане нізвідки. Запускайте на самій машині.

**Прибирати за собою доведеться руками.** Простір монтувань зникає разом з останнім процесом у ньому, а `/tmp/pivot-probe` лишається — разом із копією програми на кілька мегабайтів, бо `-static`.
