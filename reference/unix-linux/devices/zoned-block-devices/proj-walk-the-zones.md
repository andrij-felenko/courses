# ⚙️ Пройтися зонами руками: звіт, запис у вказівник, скидання

Триста рядків на C, які розмовляють із зонованим пристроєм без посередників: питають розмір зони й кількість зон, обходять усі зони звітом і друкують таблицю, а потім ставлять три досліди — запис рівно у вказівник, запис на один блок далі й скидання зони. Заліза для цього не треба: стенд піднімається одним `modprobe`.

Різниця між «прочитав про вказівник запису» і «побачив, як він зсунувся рівно на вісім секторів після одного `pwrite`», більша, ніж здається. Відмова від запису повз вказівник теж не абстракція: у неї є номер помилки, і по ньому видно, хто саме її повернув — пристрій чи ядро, яке не пустило запит далі.

## Стенд без заліза

Драйвер `null_blk` уміє вдавати зонований пристрій чесно: зі станами зон, вказівниками й лімітами відкритих та активних зон. [Модуль ядра](book:unix-linux/kernel-modules) — це шматок коду, який вантажать у вже працююче ядро командою `modprobe`, а налаштування передають йому просто в тому ж рядку; для `null_blk` ці параметри й задають форму майбутнього пристрою.

```sh
sudo modprobe null_blk \
     nr_devices=1 gb=1 bs=4096 memory_backed=1 \
     zoned=1 zone_size=4 zone_capacity=3 zone_nr_conv=2 \
     zone_max_open=4 zone_max_active=6
```

`gb=1` — місткість у гігабайтах, `bs=4096` — логічний блок, який пристрій оголосить системі. `zone_size` і `zone_capacity` задають у мегабайтах: розмір зони мусить бути степенем двійки, ємність — не більша за нього. Узявши 4 і 3, ми навмисно лишаємо в кожній зоні мегабайт, недосяжний для запису, — саме ту дірку, на якій і ламаються наївні розрахунки адрес. `zone_nr_conv=2` віддає дві перші зони під звичайні. `memory_backed=1` змушує драйвер справді тримати записане в пам'яті: без нього зони живуть повноцінно, а вміст губиться, і перевірити записане нічим.

Пристрій з'явиться як `/dev/nullb0`, а найкоротша перевірка, що він вийшов саме зонованим, — три файли:

```sh
$ cat /sys/block/nullb0/queue/zoned          # host-managed
$ cat /sys/block/nullb0/queue/nr_zones       # 256
$ cat /sys/block/nullb0/queue/chunk_sectors  # 8192  (розмір зони в секторах)
```

Прибирає стенд `sudo rmmod null_blk` — разом із усім, що на нього написали. Готову звірку дає `blkzone report /dev/nullb0` з util-linux; ми пишемо своє рівно для того, щоб побачити, звідки ті числа беруться.

## Що саме питаємо в пристрою

Розмову ведуть через [ioctl](book:unix-linux/ioctl-interface) — керуючий канал до драйвера, де кожна команда має свій номер, а дані ходять через структуру, адресу якої передають третім аргументом. Дві команди віддають прості числа: `BLKGETZONESZ` — розмір зони, `BLKGETNRZONES` — скільки їх усього. Третя, `BLKREPORTZONE`, найцікавіша: їй дають буфер із шапкою й місцем під N описів, а вона заповнює стільки, скільки змогла.

Одиниця скрізь одна — сектор у 512 байтів, і вона не залежить від того, який логічний блок оголосив пристрій. На нашому стенді блок 4096 байтів, тож кожен запис зсуває вказівник на вісім, а байтовий зсув для `pwrite` доводиться рахувати множенням на 512. Це перше місце, де програми мовчки помиляються.

```c
/* zonewalk.c — обхід зон зонованого пристрою і три досліди над вказівником.
   збірка:  cc -O2 -Wall -Wextra -D_FILE_OFFSET_BITS=64 -o zonewalk zonewalk.c
   запуск:  sudo ./zonewalk /dev/nullb0            — лише таблиця
            sudo ./zonewalk /dev/nullb0 --write    — таблиця й досліди (ПИШЕ!) */

#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/blkzoned.h>
#include <linux/fs.h>

#define SECT  512u   /* про зони ядро звітує в 512-байтових секторах — завжди */
#define BATCH 64u    /* скільки зон просити одним звітом: рівно 4 КіБ описів */

static const char *type_name(unsigned t)
{
    switch (t) {
    case BLK_ZONE_TYPE_CONVENTIONAL:  return "звичайна";
    case BLK_ZONE_TYPE_SEQWRITE_REQ:  return "послідовна";
    case BLK_ZONE_TYPE_SEQWRITE_PREF: return "послідовна (м'яка)";
    default:                          return "?";
    }
}

static const char *cond_name(unsigned c)
{
    switch (c) {
    case BLK_ZONE_COND_NOT_WP:   return "без вказівника";
    case BLK_ZONE_COND_EMPTY:    return "порожня";
    case BLK_ZONE_COND_IMP_OPEN: return "відкрита неявно";
    case BLK_ZONE_COND_EXP_OPEN: return "відкрита явно";
    case BLK_ZONE_COND_CLOSED:   return "закрита";
    case BLK_ZONE_COND_READONLY: return "лише читання";
    case BLK_ZONE_COND_FULL:     return "повна";
    case BLK_ZONE_COND_OFFLINE:  return "відключена";
    default:                     return "?";
    }
}

/* Буфер під звіт: шапка плюс місце під n описів зон. */
static struct blk_zone_report *rep_alloc(unsigned n)
{
    struct blk_zone_report *r =
        calloc(1, sizeof(*r) + (size_t)n * sizeof(struct blk_zone));

    if (!r) { perror("calloc"); exit(1); }
    return r;
}

/* Звіт починаючи з сектора from. Драйвер має право віддати МЕНШЕ зон, ніж
   просили, і переписує nr_zones фактичною кількістю — саме її й повертаємо. */
static unsigned zones_report(int fd, uint64_t from, unsigned want,
                             struct blk_zone_report *r)
{
    r->sector = from;
    r->nr_zones = want;
    r->flags = 0;
    if (ioctl(fd, BLKREPORTZONE, r) < 0) { perror("BLKREPORTZONE"); exit(1); }
    return r->nr_zones;
}

/* Свіжий опис однієї зони — тієї, якій належить сектор sector. */
static struct blk_zone zone_at(int fd, uint64_t sector)
{
    struct blk_zone_report *r = rep_alloc(1);
    struct blk_zone z;

    if (zones_report(fd, sector, 1, r) != 1) {
        fprintf(stderr, "звіту про зону при секторі %llu немає\n",
                (unsigned long long)sector);
        exit(1);
    }
    z = r->zones[0];
    free(r);
    return z;
}
```

## Таблиця зон

Обхід виглядає простим циклом, але в ньому є одна дисципліна, без якої він рано чи пізно збреше. Наступний сектор беремо не з арифметики «номер × розмір», а з останньої відданої зони: `start + len`. Так цикл переживе і вкорочену останню зону наприкінці носія, і звіт, урізаний драйвером до кількох записів.

```c
/* Таблиця всіх зон пристрою. */
static void print_table(int fd, uint32_t nr)
{
    struct blk_zone_report *r = rep_alloc(BATCH);
    uint64_t sector = 0;
    unsigned seen = 0, idx = 0;

    puts(" зона    початок  довжина  ємність  вказівник  тип і стан");

    while (seen < nr) {
        unsigned got = zones_report(fd, sector, BATCH, r);

        if (!got) break;
        for (unsigned i = 0; i < got; i++) {
            const struct blk_zone *z = &r->zones[i];
            /* до ядра 5.9 поле ємності не заповнювали: нуль там значить
               «уся зона придатна», а не «нуль секторів» */
            uint64_t cap = z->capacity ? z->capacity : z->len;
            char wp[16];

            if (z->cond == BLK_ZONE_COND_EMPTY ||
                z->cond == BLK_ZONE_COND_IMP_OPEN ||
                z->cond == BLK_ZONE_COND_EXP_OPEN ||
                z->cond == BLK_ZONE_COND_CLOSED)
                snprintf(wp, sizeof wp, "+%llu",
                         (unsigned long long)(z->wp - z->start));
            else
                snprintf(wp, sizeof wp, "-");   /* вказівник недійсний */

            printf("%5u %10llu %8llu %8llu %10s  %s, %s\n", idx++,
                   (unsigned long long)z->start,
                   (unsigned long long)z->len,
                   (unsigned long long)cap, wp,
                   type_name(z->type), cond_name(z->cond));
        }
        sector = r->zones[got - 1].start + r->zones[got - 1].len;
        seen += got;
    }
    free(r);
}

/* Перша порожня послідовна зона — вона й буде піддослідною. */
static int find_target(int fd, uint32_t nr, struct blk_zone *out)
{
    struct blk_zone_report *r = rep_alloc(BATCH);
    uint64_t sector = 0;
    unsigned seen = 0;

    while (seen < nr) {
        unsigned got = zones_report(fd, sector, BATCH, r);

        if (!got) break;
        for (unsigned i = 0; i < got; i++)
            if (r->zones[i].type != BLK_ZONE_TYPE_CONVENTIONAL &&
                r->zones[i].cond == BLK_ZONE_COND_EMPTY) {
                *out = r->zones[i];
                free(r);
                return 1;
            }
        sector = r->zones[got - 1].start + r->zones[got - 1].len;
        seen += got;
    }
    free(r);
    return 0;
}
```

Прочерк замість числа стоїть не для краси. Вказівник має сенс лише в зоні порожній, відкритій або закритій; у звичайній зоні його немає взагалі, а в повній, «лише для читання» та відключеній він недійсний, і пристрої заповнюють це поле хто чим. Дивитися треба на стан, число брати — тільки коли стан дозволяє.

## Три досліди

Тепер власне сама механіка. Програма бере першу порожню послідовну зону й тричі торкається її: пише рівно туди, куди дозволено; пише на один логічний блок далі; повертає зону на початок. Після кожного кроку вона перепитує звіт — бо єдина правда про вказівник живе в пристрої, а не в змінній програми.

```c
static void try_write(int fd, const void *buf, size_t len, off_t off,
                      const char *what)
{
    ssize_t n = pwrite(fd, buf, len, off);

    if (n < 0)
        printf("  %s: помилка, errno %d (%s)\n", what, errno, strerror(errno));
    else if ((size_t)n != len)
        printf("  %s: коротко — %zd із %zu Б\n", what, n, len);
    else
        printf("  %s: записано %zu Б\n", what, len);
}

static void experiments(int fd, uint32_t zsect, unsigned lbs, uint32_t nr)
{
    struct blk_zone z;
    struct blk_zone_range rg;
    void *buf;

    if (!find_target(fd, nr, &z)) {
        fprintf(stderr, "порожньої послідовної зони немає\n");
        return;
    }
    /* прямий ввід-вивід вимагає вирівняної АДРЕСИ буфера, не лише довжини */
    if (posix_memalign(&buf, lbs, lbs) != 0) {
        fprintf(stderr, "вирівняного буфера не вийшло\n");
        return;
    }
    memset(buf, 0xA5, lbs);

    printf("\nпіддослідна зона: сектор %llu, ємність %llu секторів\n",
           (unsigned long long)z.start,
           (unsigned long long)(z.capacity ? z.capacity : z.len));

    try_write(fd, buf, lbs, (off_t)z.wp * SECT, "запис у вказівник");
    z = zone_at(fd, z.start);
    printf("     вказівник +%llu, стан «%s»\n",
           (unsigned long long)(z.wp - z.start), cond_name(z.cond));

    try_write(fd, buf, lbs, (off_t)z.wp * SECT + lbs, "запис повз вказівник");
    z = zone_at(fd, z.start);
    printf("     вказівник +%llu, стан «%s»\n",
           (unsigned long long)(z.wp - z.start), cond_name(z.cond));

    rg.sector = z.start + 8;          /* навмисно не з межі зони */
    rg.nr_sectors = zsect;
    if (ioctl(fd, BLKRESETZONE, &rg) < 0)
        printf("  скидання з середини зони: errno %d (%s)\n",
               errno, strerror(errno));

    rg.sector = z.start;              /* а тепер рівно на зону */
    rg.nr_sectors = zsect;
    if (ioctl(fd, BLKRESETZONE, &rg) < 0) {
        perror("BLKRESETZONE");
    } else {
        z = zone_at(fd, z.start);
        printf("  скидання зони: вказівник +%llu, стан «%s»\n",
               (unsigned long long)(z.wp - z.start), cond_name(z.cond));
    }
    free(buf);
}

int main(int argc, char **argv)
{
    uint32_t zsect = 0, nr = 0;
    int lbs = 0, fd, do_write;
    const char *path;

    if (argc < 2) {
        fprintf(stderr, "вжиток: %s <вузол> [--write]\n", argv[0]);
        return 2;
    }
    path = argv[1];
    do_write = (argc > 2 && strcmp(argv[2], "--write") == 0);

    /* O_DIRECT тут не оптимізація, а умова задачі: кеш сторінок віддає
       брудні сторінки носієві в зручному собі порядку, а послідовна
       зона такого не пробачає */
    fd = open(path, O_RDWR | O_DIRECT);
    if (fd < 0) { perror(path); return 1; }

    if (ioctl(fd, BLKGETZONESZ, &zsect) < 0) { perror("BLKGETZONESZ"); return 1; }
    if (ioctl(fd, BLKGETNRZONES, &nr) < 0)   { perror("BLKGETNRZONES"); return 1; }
    if (ioctl(fd, BLKSSZGET, &lbs) < 0)      { perror("BLKSSZGET"); return 1; }

    /* нуль у будь-якому з двох означає «пристрій не зонований»: BLKGETZONESZ
       віддає chunk_sectors, а це поле буває ненульовим і в масивів */
    if (zsect == 0 || nr == 0) {
        fprintf(stderr, "%s: пристрій не зонований\n", path);
        return 1;
    }
    printf("зона %u секторів (%.1f МіБ), зон %u, логічний блок %d Б\n\n",
           zsect, zsect * (double)SECT / (1024 * 1024), nr, lbs);

    print_table(fd, nr);
    if (do_write)
        experiments(fd, zsect, (unsigned)lbs, nr);

    close(fd);
    return 0;
}
```

Ось що це друкує на описаному стенді (виведення під `LC_ALL=C`, таблицю вкорочено):

```
зона 8192 секторів (4.0 МіБ), зон 256, логічний блок 4096 Б

 зона    початок  довжина  ємність  вказівник  тип і стан
    0          0     8192     8192          -  звичайна, без вказівника
    1       8192     8192     8192          -  звичайна, без вказівника
    2      16384     8192     6144         +0  послідовна, порожня
    3      24576     8192     6144         +0  послідовна, порожня
  ...
  255    2088960     8192     6144         +0  послідовна, порожня

піддослідна зона: сектор 16384, ємність 6144 секторів
  запис у вказівник: записано 4096 Б
     вказівник +8, стан «відкрита неявно»
  запис повз вказівник: помилка, errno 5 (Input/output error)
     вказівник +8, стан «відкрита неявно»
  скидання з середини зони: errno 22 (Invalid argument)
  скидання зони: вказівник +0, стан «порожня»
```

Три рядки тут варті окремої уваги. Перший запис зробив зону відкритою, хоча ми не просили її відкривати: пристрій виділив під неї буфер сам, бо в неї почали писати. Другий запис повернув `EIO` — не `EINVAL`, не «поза межами», а саме помилку введення-виведення, ту саму, що приходить від зіпсованого носія. Вона й має так виглядати: з погляду інтерфейсу команда була законною, її відхилив стан пристрою. На ядрах від 6.10 цю відмову часто видає ще блоковий шар, не доводячи запиту до носія: механізм затичок запису звіряє зсув із власним обліком вказівника й гасить біо на місці. Ззовні різниці немає — той самий `EIO`.

Третій рядок показує, що межа зони — не порада. Скидання з сектора, який не є початком зони, ядро відкидає одразу, ще не питаючи пристрій.

## Четвертий дослід: упертися в ліміт

Два параметри стенда ми поки не чіпали — `zone_max_open=4` і `zone_max_active=6`. Побачити їх дією простіше, ніж прочитати: відкриваймо порожні зони явною командою одну за одною, доки пристрій не відмовить.

```c
/* Скільки зон пристрій дасть відкрити явно, поки не скаже «досить». */
static void probe_open_limit(int fd, uint32_t zsect, uint32_t nr)
{
    struct blk_zone_report *r = rep_alloc(BATCH);
    struct blk_zone_range rg;
    unsigned opened = 0, seen = 0;
    uint64_t sector = 0;

    while (seen < nr) {
        unsigned got = zones_report(fd, sector, BATCH, r);

        if (!got) break;
        for (unsigned i = 0; i < got; i++) {
            const struct blk_zone *z = &r->zones[i];

            if (z->type == BLK_ZONE_TYPE_CONVENTIONAL ||
                z->cond != BLK_ZONE_COND_EMPTY)
                continue;
            rg.sector = z->start;
            rg.nr_sectors = zsect;
            if (ioctl(fd, BLKOPENZONE, &rg) < 0) {
                printf("відкрито зон: %u; наступна — errno %d (%s)\n",
                       opened, errno, strerror(errno));
                free(r);
                return;
            }
            opened++;
        }
        sector = r->zones[got - 1].start + r->zones[got - 1].len;
        seen += got;
    }
    printf("відкрито зон: %u, ліміт не досягнуто\n", opened);
    free(r);
}
```

```
відкрито зон: 4; наступна — errno 109 (Too many references: cannot splice)
```

Номер виглядає безглуздо, і причина в тому, що вільних місць у таблиці помилок POSIX не лишилося: ядро віддає «перевищено ліміт відкритих зон» через `ETOOMANYREFS`, а «перевищено ліміт активних зон» — через `EOVERFLOW`. Текст від `strerror` тут не пояснює нічого; значення має саме число.

Другий ліміт цим циклом не дістати, і це не хиба досліду, а суть різниці між двома числами. Закрити зону означає віддати пристроєві буфер, лишивши вказівник на місці, — відкритою вона бути перестає, а активною лишається. Тож щоб упертися в шосту активну зону, треба відкривати й закривати: чотири відкрити, чотири закрити (`BLKCLOSEZONE` тим самим діапазоном), потім ще дві — і сьома вже не пройде, тепер із `EOVERFLOW`. Повертає зону з активних лише скидання або заповнення до кінця.

## Пастки

**Діапазон для керування зонами вирівнюють на зони.** `BLKRESETZONE` (як і `BLKOPENZONE`, `BLKCLOSEZONE`, `BLKFINISHZONE`) бере пару «сектор, кількість секторів». Ядро вимагає, щоб сектор був початком зони, а кількість — цілим числом зон; єдина поблажка — діапазон, що впирається в кінець пристрою, бо остання зона буває коротшою. Усе інше — `EINVAL`, і ця перевірка стоїть до драйвера, тому помилку видно миттєво.

**Розмір і ємність — два різні числа для двох різних дій.** Розмір (`len`) відповідає на питання «де починається наступна зона», ємність (`capacity`) — «скільки сюди ще влізе». Плутанина тут дає стабільну помилку на хвості кожної зони.

**Зона розміром 8192 і ємністю 6144 сектори, вказівник на +5000, логічний блок 4096 Б:**

```
байтовий зсув запису  = (start + 5000) · 512        ← сектор завжди 512 Б
місця до кінця        = 6144 − 5000 = 1144 сектори
                      = 1144 · 512  = 585728 Б
цілих блоків влізе    = 585728 / 4096 = 143
хвіст зони            = 8192 − 6144 = 2048 секторів → недосяжні назавжди
```

До того ж на ядрах, старших за 5.9, поле ємності просто нульове — там його треба читати як «уся зона», а не як «нуль». Перевірка `z->capacity ? z->capacity : z->len` у коді стоїть саме тому.

**`O_DIRECT` тут обов'язковий, і не заради швидкості.** [Буферизований запис](book:unix-linux/buffered-and-direct-io) лише кладе дані в кеш сторінок, а на носій вони їдуть потім і в тому порядку, який кеш вважає зручним. Для звичайного диска це байдуже, для послідовної зони — гарантований `EIO` в невгаданий момент, причому в тієї програми, яка «просто писала підряд». Прямий шлях натомість платить вирівнюванням: кратними логічному блоку мають бути і довжина, і зсув, і **адреса буфера**. Останнє — найчастіший недогляд: `malloc` вирівнювання не обіцяє, тому в коді стоїть `posix_memalign`. І перевіряти треба саме те, що `pwrite` повернув усю замовлену довжину, а не просто невід'ємне число.

**Обхід усіх зон коштує запитів.** На нашій іграшці зон 256, на справжньому черепичному диску на 20 ТБ із зонами по 256 МіБ їх близько 75 тисяч — це майже 1200 звітів пачками по 64, і кожен звіт іде до пристрою окремою командою. Тому робочий код майже ніколи не обходить усе: він просить звіт про той діапазон секторів, який зараз потрібен, а решту тримає у власній таблиці й освіжає точково.

Ще один параметр стенда варто спробувати окремо: `zone_append_max_sectors=0` вимикає в `null_blk` власний дозапис у зону, і блоковий шар починає вдавати його звичайними записами. Пристрій ззовні лишається таким самим, а от `/sys/block/nullb0/queue/zone_append_max_bytes` показує вже інше число — це найдешевший спосіб побачити, де закінчується залізо й починається ядро.
