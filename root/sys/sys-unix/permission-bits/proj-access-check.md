# ⚙️ Програма, що вирішує так само, як ядро

Найдешевший спосіб перестати вгадувати, звідки взявся `Permission denied`, — написати сотню рядків мовою C, які за шляхом і власними обліковими даними скажуть те саме, що скаже `open()`, і додатково покажуть те, чого не показує жодна утиліта: **який клас прав ядро обрало**. У виводі `ls -l` видно всі дев'ять бітів одночасно, і око саме собі домальовує, ніби система бере з них найкраще. Програма, що проходить драбину явно й друкує вибраний клас, вбиває цю ілюзію за один прогін.

## Що має бути на виході

Приймаємо дві речі: літери потрібних дій (`r`, `w`, `x` у будь-якому сполученні) і шлях. Видаємо чотири.

Перше — покроковий звіт про кожен каталог у префіксі шляху: який клас обрано, яка трійка, чи є в ній `x`. Друге — те саме про саму ціль, але вже з потрібними літерами. Третє — власний вердикт. Четверте — три чужі вердикти для звірки: `access()`, `faccessat()` із прапорцем `AT_EACCESS` і — коли питали саме про читання — справжня спроба `open()`. Розбіжність між цими трьома — не збій програми, а найцінніше, що вона вміє показати.

## Хто питає — не той, кого показує `id`

Ядро звіряє власника файлу не з тим UID, що видно в `id`, а з **fsuid** — окремим ідентифікатором «для файлової системи». У переважній більшості процесів він дорівнює дійсному, бо змінюється разом із ним; розійтися вони можуть лише там, де хтось свідомо викликав `setfsuid()`. Оскільки ми будуємо дзеркало ядра, беремо саме fsuid — це четверте число в рядках `Uid:` і `Gid:` файлу `/proc/self/status`.

Звідти ж дістаємо дійсний набір [можливостей](topic:sys-unix/capabilities) — іменованих часток колишньої всесильності root, які роздаються процесові поодинці. Рядок `CapEff:` — шістнадцяткова маска, у якій біт номер 1 означає `CAP_DAC_OVERRIDE`, а біт номер 2 — `CAP_DAC_READ_SEARCH`. Читання одного рядка звільняє нас від залежності від `libcap`.

Лишаються додаткові групи. `getgroups()` віддає їх список, але стандарт не зобов'язує включати в нього дійсний GID — тому перевіряти доведеться і список, і `fsgid` окремо.

```c
/* whocan.c — вердикт про доступ, зроблений так само, як його робить ядро.
   Збірка: cc -Wall -O2 -o whocan whocan.c        Виклик: ./whocan r ШЛЯХ */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <linux/capability.h>      /* CAP_DAC_OVERRIDE == 1, CAP_DAC_READ_SEARCH == 2 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#define WANT_R 4u
#define WANT_W 2u
#define WANT_X 1u

struct ident {
    uid_t fsuid;
    gid_t fsgid;
    gid_t *groups;
    int ngroups;
    unsigned long long capeff;
};

static void who_am_i(struct ident *me)
{
    unsigned long r, e, s, fs;
    char line[256];
    FILE *f = fopen("/proc/self/status", "r");

    me->fsuid = geteuid();          /* запасний варіант, якщо /proc не змонтовано */
    me->fsgid = getegid();
    me->capeff = 0;
    while (f && fgets(line, sizeof line, f)) {
        if (sscanf(line, "Uid: %lu %lu %lu %lu", &r, &e, &s, &fs) == 4)
            me->fsuid = (uid_t)fs;
        else if (sscanf(line, "Gid: %lu %lu %lu %lu", &r, &e, &s, &fs) == 4)
            me->fsgid = (gid_t)fs;
        else
            sscanf(line, "CapEff: %llx", &me->capeff);
    }
    if (f)
        fclose(f);

    me->ngroups = getgroups(0, NULL);
    if (me->ngroups < 0)
        me->ngroups = 0;
    me->groups = calloc((size_t)me->ngroups + 1, sizeof *me->groups);
    if (!me->groups) {
        perror("calloc");
        exit(1);
    }
    if (me->ngroups)
        getgroups(me->ngroups, me->groups);
}
```

Атрибути самого об'єкта беремо звичайним `fstat()`. Там, де потрібні речі, яких у старій структурі немає — точний час створення, ознаки, чи файл змонтований, — його заступає [`statx`](topic:sys-unix/statx-mask-and-unknown-values), що дозволяє попросити лише потрібні поля; для нашої задачі вистачає власника, групи й режиму, тобто найдешевшого запиту.

## Драбина: клас, потім одна трійка, потім привілей

Далі йде серце програми — і воно дослівно повторює те, що робить ядрова функція `generic_permission()`. Спершу клас: збіг за fsuid, інакше збіг за групою (fsgid або будь-яка додаткова), інакше «решта». Вибраний клас дає **одну** трійку, і питання «чи вистачає прав» зводиться до `(want & ~have) == 0` — чи не залишилося серед потрібних букв жодної, якої немає в трійці.

Якщо біти відмовили, лишається привілей, і тут ядро розрізняє каталоги й решту. Для каталогу `CAP_DAC_READ_SEARCH` рятує все, крім запису, а `CAP_DAC_OVERRIDE` — узагалі все. Для звичайного файлу `CAP_DAC_READ_SEARCH` діє тільки на чисте читання, а `CAP_DAC_OVERRIDE` має єдиний, але промовистий виняток: виконати файл він дозволить лише тоді, коли в режимі стоїть **хоч один** біт `x`, байдуже чий. Привілей дозволяє знехтувати тим, кому дозволено, але не дозволяє видати за програму те, що програмою ніхто не оголошував.

```c
enum cls { OWNER, GROUP, OTHER };
static const char *cls_name[] = { "власник", "група", "решта" };

static enum cls classify(const struct stat *st, const struct ident *me)
{
    if (st->st_uid == me->fsuid)
        return OWNER;
    if (st->st_gid == me->fsgid)
        return GROUP;
    for (int i = 0; i < me->ngroups; i++)
        if (st->st_gid == me->groups[i])
            return GROUP;
    return OTHER;                      /* перше «так» уже обрало — назад не вертаємось */
}

static unsigned triple(const struct stat *st, enum cls c)
{
    unsigned m = (unsigned)st->st_mode;
    return c == OWNER ? (m >> 6) & 7u
         : c == GROUP ? (m >> 3) & 7u
                      :  m       & 7u;
}

static int decide(const struct stat *st, const struct ident *me, unsigned want,
                  enum cls *chosen, const char **rule)
{
    int over = (int)((me->capeff >> CAP_DAC_OVERRIDE)    & 1);
    int look = (int)((me->capeff >> CAP_DAC_READ_SEARCH) & 1);
    unsigned have;

    *chosen = classify(st, me);
    have = triple(st, *chosen);
    if ((want & ~have) == 0) {
        *rule = "біти класу";
        return 1;
    }

    if (S_ISDIR(st->st_mode)) {
        if (!(want & WANT_W) && look) { *rule = "CAP_DAC_READ_SEARCH"; return 1; }
        if (over)                     { *rule = "CAP_DAC_OVERRIDE";    return 1; }
        *rule = "ні бітів, ні можливості";
        return 0;
    }
    if (want == WANT_R && look) { *rule = "CAP_DAC_READ_SEARCH"; return 1; }
    if ((!(want & WANT_X) || (st->st_mode & 0111)) && over) {
        *rule = "CAP_DAC_OVERRIDE";
        return 1;
    }
    *rule = (want & WANT_X) && !(st->st_mode & 0111)
          ? "жодного біта x — тут не рятує й CAP_DAC_OVERRIDE"
          : "ні бітів, ні можливості";
    return 0;
}
```

> 🔧 **Навіщо це.** Програма друкує не саме «так» чи «ні» — це й `open()` скаже, — а **обраний клас**. Саме він і є діагнозом: якщо у звіті стоїть «клас власник», то трійки групи в цьому рішенні не було зовсім, скільки б букв там не світилося в `ls -l`. Далі лікування очевидне: або міняти власника файлу, або переносити права у трійку власника — але вже без здогадів.

## Ціль — не файл, а весь шлях до нього

Права файлу нічого не вирішують, якщо якийсь каталог по дорозі не пустив усередину. [Розбір шляху](topic:sys-unix/path-resolution) — покомпонентний: ядро йде від кореня чи від поточного каталогу й у кожному каталозі шукає одне ім'я, а на це потрібен `x`. Тобто одне `open()` — це не одне рішення, а стільки рішень, скільки складників у шляху, плюс одне на цілі.

![Чотири колонки в ряд для шляху /home/alice/secret.txt. Перші три — каталоги: кореневий і home мають режим drwxr-xr-x і власника root, клас обрано «решта», трійка r-x містить x, обхід іде далі; каталог alice має режим drwx------ і власника alice, клас «власник», трійка rwx містить x, обхід іде далі. Четверта колонка — ціль secret.txt із режимом ----rw---- , власником alice і групою devs: потрібне читання, клас обрано «власник», трійка власника порожня, результат EACCES. Внизу пояснення: у каталозі з префікса нічого не читають, у ньому лише шукають одне ім'я, тому потрібен саме x, а не r](img/prefix-walk.svg)

*Одне звернення до файлу — ланцюг незалежних рішень, і кожне має свій клас.*

Спокуслива реалізація — різати рядок і робити `stat()` для кожного префікса окремо. Так робити не варто, і не лише через зайві розбори шляху: між двома `stat()` дерево під ногами може перекласти хто завгодно, і ви виміряєте один каталог, а зайдете в інший. Правильний хід — тримати вже знайдений об'єкт [дескриптором](topic:sys-unix/file-descriptor) і спускатися сімейством `*at`: `openat(dirfd, "ім'я", …)` шукає одне ім'я в тому самому каталозі, який ви щойно перевірили.

Прапорець `O_PATH` тут ключовий: він дає дескриптор-указівку без права читати чи писати вміст. Щоб його отримати, потрібен рівно той самий `x` на батьківському каталозі, який ядро й вимагає для пошуку, — тож ним можна пройти навіть крізь каталог, який нам заборонено читати. `fstat()` на такому дескрипторі працює, і цього досить.

І остання деталь ходу: спершу передбачаємо, потім спускаємося. Якщо наш вердикт — «`x` є», а `openat()` після цього повертає `EACCES`, значить, дзеркало розійшлося з оригіналом, і програма скаже про це вголос замість того, щоб мовчки збрехати.

```c
/* одне рішення: надрукувати клас, потрібні букви й вердикт для об'єкта за fd */
static int step(const char *mark, const char *name, int fd,
                const struct ident *me, unsigned want)
{
    struct stat st;
    enum cls c;
    const char *rule;
    int ok;

    if (fstat(fd, &st) < 0) { perror("fstat"); return -1; }
    ok = decide(&st, me, want, &c, &rule);
    printf("  %s %-14s %04o  потрібно %c%c%c → %s  [клас %s; %s]\n",
           mark, name, (unsigned)(st.st_mode & 07777),
           want & WANT_R ? 'r' : '-', want & WANT_W ? 'w' : '-',
           want & WANT_X ? 'x' : '-', ok ? "так" : "НІ", cls_name[c], rule);
    return ok;
}

static int walk(const char *path, const struct ident *me, unsigned want)
{
    char buf[PATH_MAX], *comp, *next, *save = NULL;
    const char *here = path[0] == '/' ? "/" : ".";
    int dirfd, ok, verdict = 1;

    if (strlen(path) >= sizeof buf) { fprintf(stderr, "задовгий шлях\n"); return -1; }
    strcpy(buf, path);

    dirfd = open(here, O_PATH | O_DIRECTORY);
    if (dirfd < 0) { perror(here); return -1; }

    comp = strtok_r(buf, "/", &save);
    if (!comp) {                        /* «/» або «.» — ціль і є цей каталог */
        ok = step("└", here, dirfd, me, want);
        close(dirfd);
        return ok;
    }

    for (; comp; comp = next) {
        int fd;
        next = strtok_r(NULL, "/", &save);

        ok = step("├", here, dirfd, me, WANT_X);   /* пошук імені в цьому каталозі */
        if (ok < 0) { close(dirfd); return -1; }
        verdict &= ok;

        fd = openat(dirfd, comp, O_PATH);   /* без O_NOFOLLOW: посилання йдуть як у ядрі */
        close(dirfd);
        if (fd < 0) {
            printf("  openat(\"%s\") → %s%s\n", comp, strerror(errno),
                   errno == EACCES && ok ? "   ← наш вердикт розійшовся з ядровим" : "");
            return -1;
        }
        dirfd = fd;
        here = comp;
    }

    ok = step("└", here, dirfd, me, want);          /* дійшли: dirfd — це вже ціль */
    close(dirfd);
    return ok < 0 ? -1 : (verdict & ok);
}

int main(int argc, char **argv)
{
    struct ident me;
    unsigned want = 0;
    int amode = 0, mine, fd;

    if (argc != 3) {
        fprintf(stderr, "вжиток: %s rwx ШЛЯХ\n", argv[0]);
        return 2;
    }
    for (const char *p = argv[1]; *p; p++)
        switch (*p) {
        case 'r': want |= WANT_R; amode |= R_OK; break;
        case 'w': want |= WANT_W; amode |= W_OK; break;
        case 'x': want |= WANT_X; amode |= X_OK; break;
        default: fprintf(stderr, "невідома буква: %c\n", *p); return 2;
        }

    who_am_i(&me);
    printf("я: fsuid=%u fsgid=%u груп=%d CapEff=%016llx\n",
           (unsigned)me.fsuid, (unsigned)me.fsgid, me.ngroups, me.capeff);

    mine = walk(argv[2], &me, want);
    printf("\nмій вердикт          : %s\n",
           mine < 0 ? "обхід урвався" : mine ? "дозволено" : "заборонено");

    errno = 0;
    printf("access()             : %s   (реальні UID/GID)\n",
           access(argv[2], amode) == 0 ? "дозволено" : strerror(errno));
    errno = 0;
    printf("faccessat AT_EACCESS : %s   (дійсні)\n",
           faccessat(AT_FDCWD, argv[2], amode, AT_EACCESS) == 0
               ? "дозволено" : strerror(errno));

    if (want == WANT_R) {
        errno = 0;
        fd = open(argv[2], O_RDONLY);
        printf("справжній open()     : %s\n", fd >= 0 ? "дозволено" : strerror(errno));
        if (fd >= 0)
            close(fd);
    }
    free(me.groups);
    return 0;
}
```

## Прогін на файлі, що відрізає власника

Сцену збирають трьома командами від root. Членство alice у групі `devs` тут принципове: без нього приклад був би нецікавий — клас усе одно вийшов би «власник», але й підстав чекати іншого не було б.

```sh
head -c 512 /dev/urandom > /home/alice/secret.txt
chown alice:devs /home/alice/secret.txt
chmod 060 /home/alice/secret.txt      # ----rw----
```

```
$ ls -l /home/alice/secret.txt
----rw---- 1 alice devs 512 /home/alice/secret.txt
$ id
uid=1000(alice) gid=1000(alice) groups=1000(alice),1002(devs)

$ ./whocan r /home/alice/secret.txt
я: fsuid=1000 fsgid=1000 груп=2 CapEff=0000000000000000
  ├ /              0755  потрібно --x → так  [клас решта; біти класу]
  ├ home           0755  потрібно --x → так  [клас решта; біти класу]
  ├ alice          0700  потрібно --x → так  [клас власник; біти класу]
  └ secret.txt     0060  потрібно r-- → НІ  [клас власник; ні бітів, ні можливості]

мій вердикт          : заборонено
access()             : Permission denied   (реальні UID/GID)
faccessat AT_EACCESS : Permission denied   (дійсні)
справжній open()     : Permission denied
```

Останній рядок звіту й є все пояснення. Alice входить у групу `devs`, і група має `rw`, — але fsuid збігся з власником на першому ж щаблі, а перше «так» обирає клас остаточно. Трійка власника порожня, і трійки групи в цьому рішенні просто не існувало.

Тепер видамо програмі можливість і подивимося, як розсипається згода трьох вердиктів:

```
$ sudo setcap cap_dac_override=ep ./whocan
$ ./whocan r /home/alice/secret.txt
я: fsuid=1000 fsgid=1000 груп=2 CapEff=0000000000000002
  ├ /              0755  потрібно --x → так  [клас решта; біти класу]
  ├ home           0755  потрібно --x → так  [клас решта; біти класу]
  ├ alice          0700  потрібно --x → так  [клас власник; біти класу]
  └ secret.txt     0060  потрібно r-- → так  [клас власник; CAP_DAC_OVERRIDE]

мій вердикт          : дозволено
access()             : Permission denied   (реальні UID/GID)
faccessat AT_EACCESS : дозволено
справжній open()     : дозволено
```

## Чому `access()` збрехав

Він не збрехав — він відповів на інше питання, і аж двома способами. По-перше, `access()` навмисне рахує **реальні** UID і GID замість дійсних: це зроблено для [setuid-програм](topic:sys-unix/setuid-and-privilege), які працюють від чужого імені й хочуть знати, чи мав би доступ той, хто їх запустив. По-друге — і про це згадують значно рідше — на час перевірки ядро підмінює облікові дані процесу, а разом із ними, коли реальний UID не нульовий, **очищає весь дійсний набір можливостей**. Тому наш `CAP_DAC_OVERRIDE` у відповіді `access()` не бере участі зовсім.

`faccessat()` із `AT_EACCESS` не робить жодної підміни, тому й збігається з реальністю. Але й тут є історична яма: власного прапорця в ядровому виклику `faccessat()` не було, і бібліотека роками вдавала `AT_EACCESS` через `fstatat()` — з відомо кривим результатом. Справжня підтримка з'явилася в системному виклику `faccessat2()` в ядрі 5.8 (2020); glibc версії 2.32 і старіші все ще емулюють.

## Ціна й пастки

Обхід коштує один `openat` і один `fstat` на складник — стільки ж звернень, скільки робить саме ядро, тільки в просторі користувача. Класифікація лінійна за числом додаткових груп; ядро в цьому місці хитріше й питає про членство лише тоді, коли трійки групи й решти різняться саме в потрібних бітах — відповідь від цього не міняється, а пошуку в списку часто вдається уникнути.

Головна пастка — не в коді, а в самому намірі щось питати наперед. Між нашим вердиктом і дією минає час, і за цей час ім'я можна підмінити [символьним посиланням](topic:sys-unix/hard-and-symbolic-links) на зовсім інший об'єкт. Це класична [гонка перевірки й використання](topic:sf-security/toctou-race), і найгучніші дірки в привілейованих програмах виросли рівно з неї: перевіряли ім'я, а відкривали вже інший файл. Наш обхід через `*at` звужує вікно, бо кожен крок тримає знайдений об'єкт дескриптором, — але вікно між останнім кроком і подальшим `open()` лишається.

Є й межа самого дзеркала. Дев'ять бітів — не єдине слово в цій розмові: [ACL](topic:sys-unix/acl-and-xattr) додає іменовані записи й маску, які втручаються рівно на щаблі групи; після успішної перевірки прав своє слово каже примусовий контроль на кшталт SELinux; на змонтованій «тільки для читання» файловій системі запис відмовить, коли всі біти дозволяють; те саме зробить прапорець незмінності. Не відтворює наш обхід і того, що робиться з посиланням посеред шляху: ядро розгортає його в новий шлях і перевіряє вже той префікс, а ми бачимо лише кінцевий об'єкт, бо `openat` пройшов посилання за нас. Відтворити все це в сотні рядків не вийде — та й не треба.

Звідси й практичний висновок, який стосується будь-якого коду, а не лише цього: **пробуйте, а не питайте**. Викликайте `open()` і розбирайте `EACCES`, а не збирайте вердикт наперед. Ця програма потрібна не для того, щоб вирішувати замість ядра, а для того, щоб один раз побачити, як воно вирішує, — і надалі читати `ls -l` очима, які починають із питання «а яким класом я доводжуся цьому файлові».
