# ⚙️ Покажчик файлів, що переживає перейменування

Ця вставка пояснює ⚙️ покажчик файлів, що переживає перейменування та дозволяє зрозуміти її детальніше. Ця робоча програма мовою C обходить дерево каталогів і записує кожен файл у покажчик не за іменем, а за рукояткою, щоб наступного разу розрізнити три різні речі: файл лежить, де лежав; файл перейменували; файла вже немає. Найдорожча тут друга відповідь: без неї перейменована тека виглядає як тисячі нових файлів, і нічне резервування читає терабайт наново.

## Що мусить нести рядок покажчика

Рядок має містити все, чого забракне завтра, — і жодне поле тут не випадкове.

Рукоятка називає файл лише всередині своєї файлової системи, тож поруч потрібна назва самої ФС. Номер монтування, який `name_to_handle_at` віддає задарма, на цю роль не годиться: номери перевикористовуються, і після перезавантаження той самий номер може означати геть інший диск. Довговічним є **UUID файлової системи** — його носить у своєму суперблоці сама ФС, і він переживає і перезавантаження, і перестановку диска в інше гніздо.

Далі — самі байти рукоятки, і обов'язково разом із `handle_type`: одна ФС кодує кількома різними правилами, тож байти без типу не значать нічого.

Потім — контрольна сума вмісту, бо покажчик відповідає не лише на «чи це той самий файл», а й на «чи він змінився».

І нарешті шлях. Він більше не ключ, але лишається з двох причин: це найдешевша перевірка (якщо під старим іменем лежить той самий файл, більше робити нічого не треба) і це єдине, що в звіті зрозуміле людині.

Формат на диску — текстовий і самоописний: перший рядок каже, що це за файл і якої він версії, другий перелічує поля.

```
#handleidx 1
#fields fs_uuid handle_type handle_hex fnv1a64 size path_len path
b6f1-…-9c02 1 6712000048b3a204 8f2c91d2c40e5518 4096 19 /srv/data/index.log
```

Записати `struct file_handle` сирим `fwrite` не можна: перед байтами в ній лежать `unsigned int` і `int`, тож дамп залежить від розрядності машини й порядку байтів у ній. Тип і довжину пишемо числами, самі байти — шістнадцятковим рядком.

Довжина шляху **перед** шляхом — теж не примха. В іменах Unix дозволено все, крім `/` і нульового байта, зокрема й переведення рядка. Читати «до кінця рядка» означає одного дня зіпсувати покажчик через один-єдиний файл із дивною назвою.

## Перший прохід: обхід і рукоятки

Обхід тут навмисно найпростіший — `nftw` з `FTW_PHYS`, щоб не ходити за символьними посиланнями. Справжнє резервування натомість спускається деревом на дескрипторах каталогів, щоб між перевіркою й відкриттям ніхто не підмінив ланку шляху (це окрема робота, розібрана у [власному обході каталогу](book:unix-linux/directory-as-mapping/proj-walk-directory.md)).

```c
/* handleidx.c — покажчик файлів, ключем якого є рукоятка, а не ім'я.
 *   збирання: ./handleidx scan /srv/data index.txt
 *   звірка:   ./handleidx check index.txt
 * збірка:     cc -O2 -o handleidx handleidx.c
 */
#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <ftw.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <unistd.h>

static struct file_handle *fh;          /* один буфер на всю програму */
static FILE *idx;
static const char *uuid_of_mount(int id);

/* FNV-1a, 64 біти: дешева сума «чи змінився вміст», не криптографія. */
static unsigned long long content_sum(const char *path)
{
    unsigned long long h = 1469598103934665603ULL;
    unsigned char buf[1 << 16];
    ssize_t n;
    int fd = open(path, O_RDONLY);

    if (fd < 0)
        return 0;
    while ((n = read(fd, buf, sizeof buf)) > 0)
        for (ssize_t i = 0; i < n; i++)
            h = (h ^ buf[i]) * 1099511628211ULL;
    close(fd);
    return h;
}

static int visit(const char *path, const struct stat *st, int kind, struct FTW *w)
{
    int mount_id = -1;

    (void)w;
    if (kind != FTW_F || !S_ISREG(st->st_mode))
        return 0;

    /* handle_bytes виставляємо наново ПЕРЕД КОЖНИМ викликом: після вдалого
       виклику ядро лишає в ньому справжню довжину рукоятки (для ext4 — 8),
       і наступний файл на іншій ФС у цей огризок не влізе — прийде EOVERFLOW. */
    fh->handle_bytes = MAX_HANDLE_SZ;
    if (name_to_handle_at(AT_FDCWD, path, fh, &mount_id, 0) < 0) {
        if (errno != EOPNOTSUPP) {
            perror(path);
            return 0;
        }
        fh->handle_bytes = 0;       /* ФС кодувати не вміє — ключем лишиться шлях */
        fh->handle_type = -1;
        mount_id = -1;
    }

    fprintf(idx, "%s %d ", uuid_of_mount(mount_id), fh->handle_type);
    if (fh->handle_bytes)
        for (unsigned i = 0; i < fh->handle_bytes; i++)
            fprintf(idx, "%02x", fh->f_handle[i]);
    else
        fputc('-', idx);
    fprintf(idx, " %016llx %llu %zu %s\n", content_sum(path),
            (unsigned long long)st->st_size, strlen(path), path);
    return 0;
}

static int scan(const char *root, const char *out)
{
    if (!(idx = fopen(out, "w"))) {
        perror(out);
        return 1;
    }
    fputs("#handleidx 1\n"
          "#fields fs_uuid handle_type handle_hex fnv1a64 size path_len path\n", idx);
    if (nftw(root, visit, 32, FTW_PHYS) < 0) {
        perror(root);
        return 1;
    }
    return fclose(idx) != 0;
}
```

`EOPNOTSUPP` тут не помилка, а звичайна гілка. Спитати наперед, чи вміє ФС кодувати, ніде: з'ясовують це спробою. Такий файл потрапляє в покажчик із порожньою рукояткою й перевіряється по-старому, за шляхом і сумою, — і це головна причина, чому формат мусить дозволяти рядок без ключа.

## Від UUID до чинного монтування

UUID у самому ядрі ніде поруч не лежить: `name_to_handle_at` віддає номер монтування, `/proc/self/mountinfo` — номер пристрою й шлях до нього, а зв'язок «пристрій → UUID» тримає [udev](book:unix-linux/udev-rules) у вигляді символьних посилань `/dev/disk/by-uuid`, де ім'я посилання і є UUID. Отже, дорога складається з двох ланок, і кожну треба пройти.

```c
struct mnt { int id; char uuid[64]; char point[PATH_MAX]; };
static struct mnt mtab[256];
static int mtab_n;

static void uuid_lookup(dev_t sb_dev, const char *source, char *out, size_t n)
{
    char link[PATH_MAX], real_src[PATH_MAX], real_lnk[PATH_MAX];
    struct dirent *e;
    struct stat st;
    DIR *d;

    snprintf(out, n, "-");                       /* «UUID невідомий» */
    if (!(d = opendir("/dev/disk/by-uuid")))
        return;
    if (!realpath(source, real_src))
        real_src[0] = '\0';
    while ((e = readdir(d))) {
        if (e->d_name[0] == '.')
            continue;
        snprintf(link, sizeof link, "/dev/disk/by-uuid/%s", e->d_name);
        if (stat(link, &st) < 0)
            continue;
        /* ext4, XFS та інші однодискові: номер пристрою в mountinfo справжній */
        if (major(sb_dev) && st.st_rdev == sb_dev) {
            snprintf(out, n, "%s", e->d_name);
            break;
        }
        /* Btrfs і подібні беруть анонімний номер (major 0) —
           там лишається звіряти самі шляхи до пристрою */
        if (real_src[0] && realpath(link, real_lnk) && !strcmp(real_lnk, real_src)) {
            snprintf(out, n, "%s", e->d_name);
            break;
        }
    }
    closedir(d);
}

static void load_mounts(void)
{
    char line[8192], point[PATH_MAX], source[PATH_MAX], *sep;
    FILE *f = fopen("/proc/self/mountinfo", "r");
    int id, maj, min;

    if (!f) {
        perror("mountinfo");
        exit(1);
    }
    /* поля: 1 id · 2 батько · 3 major:minor · 4 корінь ФС · 5 точка монтування,
       далі змінне число полів, роздільник " - ", по ньому тип і джерело */
    while (mtab_n < 256 && fgets(line, sizeof line, f)) {
        if (sscanf(line, "%d %*d %d:%d %*s %4095s", &id, &maj, &min, point) != 4)
            continue;
        if (!(sep = strstr(line, " - ")))
            continue;
        if (sscanf(sep + 3, "%*s %4095s", source) != 1)
            continue;
        mtab[mtab_n].id = id;
        snprintf(mtab[mtab_n].point, PATH_MAX, "%s", point);
        uuid_lookup(makedev(maj, min), source, mtab[mtab_n].uuid, 64);
        mtab_n++;
    }
    fclose(f);
}

static const char *uuid_of_mount(int id)
{
    for (int i = 0; i < mtab_n; i++)
        if (mtab[i].id == id)
            return mtab[i].uuid;
    return "-";
}

static int open_mount_by_uuid(const char *uuid)
{
    for (int i = 0; i < mtab_n; i++)
        if (!strcmp(mtab[i].uuid, uuid))
            return open(mtab[i].point, O_RDONLY | O_DIRECTORY);
    return -1;
}
```

Дві гілки в `uuid_lookup` — не перестраховка. Номер пристрою в третьому полі `mountinfo` належить суперблокові, а суперблок не завжди сидить на одному блоковому пристрої: Btrfs, tmpfs, overlayfs і мережеві ФС дістають **анонімний** номер зі старшою частиною 0, якого в `/dev` немає взагалі. Для них лишається порівнювати шлях до джерела монтування — а для tmpfs і мережевих не лишається й цього, і UUID чесно вийде «`-`». Розкладка полів `mountinfo` і те, чому їх доводиться читати саме так, розібрані в [дереві монтувань](book:unix-linux/mount-model).

Хто не хоче ходити в `/dev` руками, бере `blkid_get_tag_value` з `libblkid` — та сама відповідь, але з читанням суперблока напряму, а отже, з правом на блоковий пристрій.

## Другий прохід: три різні відповіді

![Ліворуч ланцюг перевірки: рядок покажчика, пошук монтування за UUID, name_to_handle_at на збереженому шляху, звірка типу й байтів, і лише в разі розбіжності open_by_handle_at. Праворуч чотири результати: файл на місці, файл перейменовано, ESTALE — файла немає, і помилки EPERM та EOPNOTSUPP із відкотом на звичайний обхід](/reference/unix-linux/files/file-handles/img/check-flow.svg)

*Порядок перевірок побудовано так, щоб дорогий шлях узагалі не вмикався для більшості файлів: у незмінному дереві все закінчується на другому кроці, і рукоятка потрібна лише там, де ім'я підвело.*

```c
struct rec {
    char uuid[64];
    int type;
    unsigned char h[MAX_HANDLE_SZ];
    unsigned hn;
    unsigned long long sum, size;
    char path[PATH_MAX];
};

static int read_rec(FILE *f, struct rec *r)
{
    char hex[2 * MAX_HANDLE_SZ + 1];
    size_t len;

    if (fscanf(f, "%63s %d %256s %16llx %llu %zu",
               r->uuid, &r->type, hex, &r->sum, &r->size, &len) != 6)
        return 0;
    if (fgetc(f) != ' ')                 /* рівно один пробіл, не «пропустити пробіли»: */
        return 0;                        /* ім'я файлу може починатися з пробілу */
    r->hn = 0;
    if (strcmp(hex, "-"))
        for (const char *p = hex; p[0] && p[1]; p += 2)
            sscanf(p, "%2hhx", &r->h[r->hn++]);
    if (len >= PATH_MAX || fread(r->path, 1, len, f) != len)
        return 0;
    r->path[len] = '\0';
    return fgetc(f) == '\n';
}

static int check(const char *idxpath)
{
    char line[256];
    struct rec r;
    FILE *f = fopen(idxpath, "r");

    if (!f) {
        perror(idxpath);
        return 1;
    }
    if (!fgets(line, sizeof line, f) || strncmp(line, "#handleidx 1", 12)) {
        fprintf(stderr, "%s: не той формат\n", idxpath);
        return 1;
    }
    if (!fgets(line, sizeof line, f))    /* рядок #fields */
        return 1;

    while (read_rec(f, &r)) {
        int mid, mfd, fd;

        if (!r.hn) {                     /* рукоятки немає — ФС її не вміє */
            printf("без ключа  %s\n", r.path);
            continue;
        }

        /* 1. Найдешевше: хто зараз лежить під збереженим іменем? */
        fh->handle_bytes = MAX_HANDLE_SZ;
        if (name_to_handle_at(AT_FDCWD, r.path, fh, &mid, 0) == 0 &&
            fh->handle_type == r.type && fh->handle_bytes == r.hn &&
            memcmp(fh->f_handle, r.h, r.hn) == 0) {
            printf("на місці   %s%s\n", r.path,
                   content_sum(r.path) == r.sum ? "" : "   (вміст змінився)");
            continue;
        }

        /* 2. Ім'я більше не веде до нашого файлу. Чи він узагалі живий? */
        if ((mfd = open_mount_by_uuid(r.uuid)) < 0) {
            printf("не видно   %s   (ФС %s не змонтована)\n", r.path, r.uuid);
            continue;
        }
        fh->handle_bytes = r.hn;
        fh->handle_type = r.type;
        memcpy(fh->f_handle, r.h, r.hn);

        fd = open_by_handle_at(mfd, fh, O_RDONLY);
        if (fd >= 0) {
            char link[64], now[PATH_MAX];
            ssize_t k;

            snprintf(link, sizeof link, "/proc/self/fd/%d", fd);
            k = readlink(link, now, sizeof now - 1);
            now[k > 0 ? k : 0] = '\0';
            printf("перейм.    %s → %s\n", r.path,
                   k > 0 ? now : "(шлях невідомий)");
            close(fd);
        } else if (errno == ESTALE) {
            printf("немає      %s\n", r.path);
        } else {
            perror("open_by_handle_at");  /* EPERM — бракує CAP_DAC_READ_SEARCH */
        }
        close(mfd);
    }
    fclose(f);
    return 0;
}

int main(int argc, char **argv)
{
    if (!(fh = malloc(sizeof *fh + MAX_HANDLE_SZ)))
        return 1;
    load_mounts();
    if (argc == 4 && !strcmp(argv[1], "scan"))
        return scan(argv[2], argv[3]);
    if (argc == 3 && !strcmp(argv[1], "check"))
        return check(argv[2]);
    fprintf(stderr, "вжиток: %s scan <корінь> <покажчик> | %s check <покажчик>\n",
            argv[0], argv[0]);
    return 2;
}
```

**Прогін на ext4: між двома проходами один файл перейменували, другий дописали, третій вилучили.**

```
$ ./handleidx scan /srv/data index.txt
$ mv /srv/data/index.log /srv/data/arch/index.log
$ echo ще-рядок >> /srv/data/notes.txt
$ rm /srv/data/tmp/build.lock
$ ./handleidx check index.txt
на місці   /srv/data/notes.txt   (вміст змінився)
перейм.    /srv/data/index.log → /srv/data/arch/index.log
немає      /srv/data/tmp/build.lock
```

Три рядки — три різні дії резервування: перечитати вміст, лише переписати шлях у покажчику, викреслити запис. Покажчик на іменах побачив би тут інше: `/srv/data/index.log` зник, `/srv/data/arch/index.log` з'явився, — і слухняно скопіював би файл, у якому не змінилося жодного байта.

Перевірка «на місці» зроблена не порівнянням номера inode, а порівнянням рукояток — і це важливо. Номер збігся б і тоді, коли комірку встигли заселити наново; рукоятка несе ще й покоління, тож збіг рукояток означає саме той файл, а не ту саму комірку.

Шлях, який `readlink` дістає з `/proc/self/fd`, — підказка, а не обіцянка. Файл, відкритий за рукояткою, часто має **відв'язаний** запис у кеші каталогів: ядро знайшло inode, але не знає ланцюга батьків до нього, і тоді рядок у `/proc` буде безглуздий або неповний. Хто хоче чесний шлях, кодує рукоятку з прапорцем `AT_HANDLE_CONNECTABLE` (ядро 6.13) — ціною того, що така рукоятка вміщує ще й батьківський каталог і переїзду файлу в іншу теку вже не переживе.

## Чому байти порівнювати можна, а розбирати — ні

Порівняння байт у байт — законна дія, і саме на ній тримається вся звірка. Трійка «UUID · `handle_type` · байти» є рівно тим, чим файлова система сама себе питає «який це файл»; на цій самій рівності стоїть режим `FAN_REPORT_FID` у `fanotify`, який віддає програмі рукоятку замість дескриптора саме для впізнавання.

Рівність працює в один бік. Однакові трійки означають той самий файл; **різні трійки не означають різних файлів**. Той самий файл дає інші байти, якщо попросити рукоятку з іншими прапорцями — з `AT_HANDLE_CONNECTABLE` вона довша й інакшого типу. Отже, порівнювати вільно лише рукоятки, зняті однаково; покажчик, що змішав два способи, почне «губити» файли на рівному місці.

А розбирати вміст не можна тому, що правила розбору просто не існує: розкладка байтів належить драйверові ФС, номери в `handle_type` живуть у власному просторі кожної ФС (одне й те саме число в ext4 та XFS означає різні речі), одна ФС видає кілька форматів, і наступний випуск ядра вільний додати ще один. Програма, що прочитала «перші чотири байти — номер inode», сьогодні працює на ext4 і завтра мовчки бреше на іншій ФС. Обіцянка в цьому інтерфейсі одна: **віддай ті самі байти назад**.

> 🔧 **Навіщо це.** Звідси випливає, навіщо в першому рядку покажчика стоїть номер версії. Спосіб зняття рукоятки — частина ключа, не деталь реалізації: варто наступному випускові програми почати просити рукоятки з іншим прапорцем, і всі старі записи мовчки перестануть збігатися з новими, а звірка оголосить перейменованим геть усе дерево. Номер версії робить цю зміну гучною: покажчик старої версії видно з першого рядка, і його або перечитують наново, або читають старим правилом.

## Ціна й граблі

Обхід коштує стільки ж, скільки звичайний `stat` на файл: `name_to_handle_at` — це той самий розбір шляху плюс дешеве кодування. Дорога тут контрольна сума, бо вона читає вміст.

```
запис ≈ 36 (UUID) + 16 (рукоятка) + 16 (сума) + ~60 (шлях) ≈ 140 байтів
10⁶ файлів · 140 Б ≈ 140 МБ покажчика
```

Викинути поле шляху означає вдвічі менший покажчик — і втрату відповіді «перейменовано на що».

Друга дешева правка стосується порядку записів. Тут `open_mount_by_uuid` відкриває точку монтування наново для кожного розбіжного рядка; варто відсортувати покажчик за UUID під час збирання — і дескриптор монтування відкривається один раз на файлову систему, а не один раз на файл.

Найгостріша грабля — **повноваження**. Збирання покажчика не потребує нічого: `name_to_handle_at` доступний усім. Звірка потребує `CAP_DAC_READ_SEARCH`, і видавати його треба самій програмі (`setcap cap_dac_read_search+ep ./handleidx`), а не запускати все від `root`. Ядро 6.12 послабило вимогу для контейнерів, але лише для рукояток **каталогів**, відкриваних з `O_DIRECTORY`, і лише коли той, хто відкриває, і так міг би дійти до цього каталогу від переданого дескриптора монтування; для звичайних файлів усе лишилося як було. Чому саме це повноваження й чому воно рівносильне праву читати всю ФС — у [можливостях](book:unix-linux/capabilities).

Друга грабля — `handle_bytes`, який після вдалого виклику містить не ємність буфера, а справжню довжину. Забути виставити його наново — це помилка, яка не проявиться на одній файловій системі й вилізе `EOVERFLOW` на іншій, з довшими рукоятками.

Третя — думка, що `ESTALE` є дивиною з мережевих ФС. Тут це штатна відповідь «файла немає», і саме заради неї все й будувалося; програма, що трактує його як збій, перетворює корисний сигнал на аварію.

Але й довіряти цій відповіді сліпо не варто, коли покажчик збирає ще й каталоги. Відкриваючи каталог за рукояткою, ядро мусить прив'язати його до кореня ФС — піднятися батьками вгору, — і невдала прив'язка теж закінчується `ESTALE`, хоча каталог цілий. Відрізнити два випадки за кодом помилки неможливо, тож перед тим, як викреслити каталог із покажчика, його варто перепитати звичайним обходом. Наведена програма цього клопоту не має свідомо: `visit` бере лише звичайні файли.
