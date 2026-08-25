# ⚙️ Програма, що читає список доступу як звичайні байти

Дві сотні рядків мовою C, які дістають атрибут `system.posix_acl_access` тим самим `getxattr`, що й будь-який інший атрибут, розкладають його значення на записи й друкують те саме, що друкує `getfacl` — разом із позначками `#effective`, порахованими самотужки. Сенс не в тому, щоб замінити `getfacl`: сенс у тому, що після такої програми список доступу перестає бути окремою підсистемою зі власною магією. Це рядкове ім'я, сорок чотири байти і арифметика над трьома бітами.

## Що саме лежить у значенні атрибута

Формат оголошений в одному короткому заголовку ядра — `include/uapi/linux/posix_acl_xattr.h` — і незмінний десятиліттями. Спершу чотири байти: беззнакове число версії, `0x0002`. Далі щільно, без вирівнювання й без лічильника, ідуть записи рівно по вісім байтів: двобайтовий тег (хто це), двобайтові права (що можна) і чотирибайтовий ідентифікатор (uid або gid). Скільки записів — ніде не написано; це дає сама довжина значення: `(розмір − 4) / 8`.

Теги — окремі біти, щоб їх можна було збирати в маску одним словом: `1` власник, `2` іменований користувач, `4` група файлу, `8` іменована група, `16` маска, `32` решта. Права — ті самі три біти, що й у режимі: `4` читання, `2` запис, `1` виконання. Там, де ідентифікатор ні до чого (власник, група файлу, маска, решта), лежить `0xffffffff` — «не визначено».

![Ліворуч колонки байтів у шістнадцятковому вигляді, праворуч розшифровка й відповідний рядок виводу. Угорі заголовок із чотирьох байтів 02 00 00 00 — u32 версія 0x0002; інше число дало б EOPNOTSUPP. Далі підписи полів запису: перші два байти — тег u16, наступні два — права u16, останні чотири — ідентифікатор u32. П'ять записів: 01 00 06 00 ff ff ff ff — тег 1, власник файлу, права 6 = rw-, ідентифікатор не вжито, рядок user::rw-; 02 00 06 00 e9 03 00 00 — тег 2, іменований користувач, права 6 = rw-, uid 1001, рядок user:hanna:rw- з позначкою #effective:r--; 04 00 04 00 ff ff ff ff — тег 4, група файлу, права 4 = r--, рядок group::r--; 10 00 04 00 ff ff ff ff — тег 16, маска, права 4 = r--, стеля класу групи, рядок mask::r--; 20 00 00 00 ff ff ff ff — тег 32, решта, права 0, рядок other::---. Унизу: разом 4 + 5 × 8 = 44 байти, числа на носії завжди little-endian, а імені hanna в байтах немає — є число 1001](img/acl-blob-bytes.svg)

*Уся «складність» ACL на носії — це заголовок і однорідний масив вісімок. Імен там немає, є числа.*

## Дістати байти: чому викликів два

`getxattr` не вміє «дати скільки є»: буфер із розміром надає той, хто питає. Тому шаблон завжди двокроковий — перший виклик із нульовим буфером повертає потрібну довжину, другий читає в щойно виділену пам'ять. Між цими двома викликами хтось міг додати запис, і тоді другий відповість `ERANGE`. Чесна реакція на це — не «збільшу буфер удвічі», а «почну спочатку», бо новий розмір знову треба питати в ядра.

Спокуса обійти все це статичним буфером на 64 КіБ (стеля значення атрибута в Linux) справді працює. Але двокроковий шаблон однаковий для будь-якого атрибута — і для `security.capability`, і для власного `user.mime_type`, — тож вивчити його дешевше на найпростішому випадку.

## Код

```c
/* aclcat.c — друкує список доступу, прочитавши атрибут як звичайні байти.
   Збірка: cc -Wall -Wextra -O2 -o aclcat aclcat.c
   Виклик: ./aclcat [-x] ШЛЯХ...       (-x додає шістнадцятковий вигляд запису) */
#define _GNU_SOURCE
#include <errno.h>
#include <grp.h>
#include <pwd.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/xattr.h>

#define ACL_XATTR_VERSION 0x0002u
#define TAG_USER_OBJ  0x01u
#define TAG_USER      0x02u
#define TAG_GROUP_OBJ 0x04u
#define TAG_GROUP     0x08u
#define TAG_MASK      0x10u
#define TAG_OTHER     0x20u

#define HDR 4   /* заголовок: u32 версія                        */
#define REC 8   /* запис: u16 тег + u16 права + u32 ідентифікатор */

/* Числа на носії little-endian незалежно від машини — тому збираємо
   їх із байтів руками, а не накладаємо struct на буфер.          */
static uint16_t le16(const unsigned char *p)
{
    return (uint16_t)(p[0] | (p[1] << 8));
}

static uint32_t le32(const unsigned char *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8)
         | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static char *rwx(unsigned perm, char out[4])
{
    out[0] = (perm & 4) ? 'r' : '-';
    out[1] = (perm & 2) ? 'w' : '-';
    out[2] = (perm & 1) ? 'x' : '-';
    out[3] = '\0';
    return out;
}

static void who_name(uint32_t id, int group, char *out, size_t n)
{
    if (group) {
        struct group *g = getgrgid((gid_t)id);
        if (g) { snprintf(out, n, "%s", g->gr_name); return; }
    } else {
        struct passwd *u = getpwuid((uid_t)id);
        if (u) { snprintf(out, n, "%s", u->pw_name); return; }
    }
    snprintf(out, n, "%u", id);                 /* немає в базі — лишаємо число */
}

/* Двокроковий шаблон: спитати розмір, виділити, прочитати.
   Список міг вирости між викликами — тоді ERANGE, і все спочатку. */
static ssize_t slurp(const char *path, const char *name, unsigned char **out)
{
    for (int attempt = 0; attempt < 8; attempt++) {
        ssize_t need = getxattr(path, name, NULL, 0);
        if (need < 0) return -1;                /* ENODATA, EOPNOTSUPP, EACCES… */
        unsigned char *buf = malloc(need ? (size_t)need : 1);
        if (!buf) { errno = ENOMEM; return -1; }
        ssize_t got = getxattr(path, name, buf, (size_t)need);
        if (got >= 0) { *out = buf; return got; }
        free(buf);
        if (errno != ERANGE) return -1;
    }
    errno = ERANGE;
    return -1;
}

static void print_rec(const unsigned char *r, unsigned mask, int have_mask,
                      const char *prefix, int hex)
{
    unsigned tag = le16(r), perm = le16(r + 2);
    uint32_t id = le32(r + 4);
    char who[128], name[64], a[4], b[4];

    switch (tag) {
    case TAG_USER_OBJ:  snprintf(who, sizeof who, "%suser::",  prefix); break;
    case TAG_GROUP_OBJ: snprintf(who, sizeof who, "%sgroup::", prefix); break;
    case TAG_MASK:      snprintf(who, sizeof who, "%smask::",  prefix); break;
    case TAG_OTHER:     snprintf(who, sizeof who, "%sother::", prefix); break;
    case TAG_USER:
    case TAG_GROUP:
        who_name(id, tag == TAG_GROUP, name, sizeof name);
        snprintf(who, sizeof who, "%s%s:%s:", prefix,
                 tag == TAG_GROUP ? "group" : "user", name);
        break;
    default:
        printf("# запис із невідомим тегом 0x%02x\n", tag);
        return;
    }

    /* маска стелить лише середній клас: іменовані записи і group:: */
    int capped = have_mask &&
                 (tag == TAG_USER || tag == TAG_GROUP || tag == TAG_GROUP_OBJ);
    unsigned eff = capped ? (perm & mask) : perm;

    if (hex)
        printf("%02x %02x %02x %02x %02x %02x %02x %02x  ",
               r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]);
    printf("%s%s", who, rwx(perm, a));
    if (eff != perm) printf("\t#effective:%s", rwx(eff, b));
    putchar('\n');
}

static int print_list(const unsigned char *raw, size_t size,
                      const char *prefix, int hex)
{
    if (size < HDR || (size - HDR) % REC) {
        fprintf(stderr, "довжина %zu не складається із заголовка й цілих записів\n",
                size);
        return -1;
    }
    if (le32(raw) != ACL_XATTR_VERSION) {
        fprintf(stderr, "версія формату 0x%04x, а розбирати вміємо лише 0x%04x\n",
                (unsigned)le32(raw), ACL_XATTR_VERSION);
        return -1;
    }

    size_t n = (size - HDR) / REC;
    unsigned mask = 0;
    int have_mask = 0;
    for (size_t i = 0; i < n; i++) {            /* маску шукаємо першим проходом */
        const unsigned char *r = raw + HDR + i * REC;
        if (le16(r) == TAG_MASK) { mask = le16(r + 2); have_mask = 1; }
    }
    for (size_t i = 0; i < n; i++)
        print_rec(raw + HDR + i * REC, mask, have_mask, prefix, hex);
    return 0;
}

static int dump(const char *path, int hex)
{
    struct stat st;
    char nm[64], a[4];

    if (stat(path, &st)) { perror(path); return 1; }   /* stat, як і getxattr,
                                                          іде за символьним
                                                          посиланням          */
    who_name(st.st_uid, 0, nm, sizeof nm);
    printf("# file: %s\n# owner: %s\n", path, nm);
    who_name(st.st_gid, 1, nm, sizeof nm);
    printf("# group: %s\n", nm);

    unsigned char *raw = NULL;
    ssize_t size = slurp(path, "system.posix_acl_access", &raw);
    if (size < 0) {
        if (errno != ENODATA) {                 /* ENODATA — не помилка */
            fprintf(stderr, "%s: %s\n", path, strerror(errno));
            return 1;
        }
        printf("user::%s\n",  rwx((st.st_mode >> 6) & 7, a));
        printf("group::%s\n", rwx((st.st_mode >> 3) & 7, a));
        printf("other::%s\n", rwx(st.st_mode & 7, a));
        printf("# атрибута немає: список мінімальний, це самі біти режиму\n");
    } else {
        int bad = print_list(raw, (size_t)size, "", hex);
        free(raw);
        if (bad) return 1;
    }

    if (S_ISDIR(st.st_mode)) {                  /* шаблон буває лише в каталогу */
        raw = NULL;
        size = slurp(path, "system.posix_acl_default", &raw);
        if (size >= 0) {
            print_list(raw, (size_t)size, "default:", hex);
            free(raw);
        } else if (errno != ENODATA) {
            fprintf(stderr, "%s (default): %s\n", path, strerror(errno));
        }
    }
    return 0;
}

int main(int argc, char **argv)
{
    int hex = 0, i = 1;
    if (i < argc && !strcmp(argv[i], "-x")) { hex = 1; i++; }
    if (i >= argc) {
        fprintf(stderr, "вжиток: %s [-x] ШЛЯХ...\n", argv[0]);
        return 2;
    }
    int first = i, rc = 0;
    for (; i < argc; i++) {
        if (i > first) putchar('\n');
        if (dump(argv[i], hex)) rc = 1;
    }
    return rc;
}
```

## Діючі права рахуємо самі — і в два проходи

На носії немає жодного поля «діючі права»: позначка `#effective:` — це арифметика, яку робить той, хто друкує. Правило коротке: маска стелить середній клас — іменованих користувачів, іменовані групи **і** запис `group::`. Власника й `other::` вона не бачить зовсім. Останнє забувають найчастіше: `group::` здається «своїм» записом, а насправді підлягає масці нарівні з іменованими.

**Умова.** Запис про Ганну має байти `02 00 06 00 e9 03 00 00`, запис маски — `10 00 04 00 ff ff ff ff`.

```
права запису   0x0006 = rw-
маска          0x0004 = r--
діюче          0x0006 & 0x0004 = 0x0004 = r--

0x0004 ≠ 0x0006  →  user:hanna:rw-   #effective:r--
```

Право `w` лишилося в байтах на диску — воно просто не діє, поки маска опущена; підніміть маску назад, і байти запрацюють без жодного `setfacl`.

Звідси й друга особливість коду — окремий перший прохід по масиву заради маски. Порядок записів жорсткий: маска стоїть після всіх іменованих записів і перед `other::`. Отже, коли розбирач доходить до `user:hanna:`, стелі він ще не знає, і порахувати діюче за один прохід можна хіба відклавши весь вивід у пам'ять до кінця. Два проходи по масиву з кількох десятків елементів дешевші за будь-яку таку хитрість.

## Звірка з тим, що каже libacl

Готуємо той самий випадок, що й у поясненні маски: файл належить `bohdan` і групі `staff`, Ганні (uid 1001) окремо видали запис, а потім хтось звично прибрав право групи.

```sh
$ setfacl -m u:hanna:rw report.csv
$ chmod g-w report.csv
$ getfattr -n system.posix_acl_access --only-values report.csv | xxd
00000000: 0200 0000 0100 0600 ffff ffff 0200 0600  ................
00000010: e903 0000 0400 0400 ffff ffff 1000 0400  ................
00000020: ffff ffff 2000 0000 ffff ffff            .... .......

$ ./aclcat -x report.csv
# file: report.csv
# owner: bohdan
# group: staff
01 00 06 00 ff ff ff ff  user::rw-
02 00 06 00 e9 03 00 00  user:hanna:rw-	#effective:r--
04 00 04 00 ff ff ff ff  group::r--
10 00 04 00 ff ff ff ff  mask::r--
20 00 00 00 ff ff ff ff  other::---
```

Тепер найцікавіше — порівняти без `-x` із бібліотечним інструментом:

```sh
$ ./aclcat report.csv > mine.txt
$ getfacl report.csv | grep -v '^$' > theirs.txt
$ diff -b mine.txt theirs.txt && echo "рядок у рядок"
рядок у рядок
```

Збіг не випадковий і не є доказом нашої вправності: `getfacl` спирається на `libacl`, а `acl_get_file()` там робить рівно те саме — той самий `getxattr` за тим самим іменем, той самий двокроковий шаблон із `ERANGE`. Ми не обійшли бібліотеку, ми повторили її нутрощі. Відомі відмінності лишаються чотири, і всі поза форматом: `getfacl` вирівнює позначку `#effective:` до сталої колонки, а ми ставимо один табулятор (саме тому в `diff` і стоїть `-b`), відділяє файли порожнім рядком (його ми відрізали `grep`), додає рядок `# flags:`, коли на файлі стоїть setuid, setgid або біт залипання, і зрізає початкові скісні риски в імені, якщо не сказати `--absolute-names`.

Одна відмінність глибша й варта окремої уваги. Для файлу без розширеного списку `getxattr` повертає `ENODATA`, і `libacl` у цьому разі не здається, а сам добудовує список із дев'яти бітів режиму. Наша гілка `ENODATA` робить те саме навмисно — інакше `./aclcat` мовчав би там, де `getfacl` показує три рядки, і читач вирішив би, що зламалася програма.

## Пастки

**Порядок байтів — не вашої машини, а носія.** Поля оголошені як `__le16` і `__le32`, тобто завжди little-endian. Тому спокусливий `memcpy` у структуру дасть правильні числа на x86 і безглузді на s390x, а помилка виявиться лише тоді, коли хтось прочитає той самий диск іншою архітектурою. Складання числа зі зсувів працює однаково всюди й нічого не коштує. [Біти й порядок байтів](topic:sf-algorithms/bits-bytes-endianness) — про те, чому «як у пам'яті» і «як на носії» взагалі різні питання.

**`ENODATA` — це відповідь, а не збій.** Мінімальний список (лише власник, група, решта) на носії не тримають узагалі: він дослівно дорівнює [дев'ятьом бітам режиму](topic:sys-unix/permission-bits). Тому «атрибута немає» означає «прав рівно стільки, скільки в режимі», а не «щось пішло не так». Тут же поруч живе `EOPNOTSUPP` — і от він таки означає інше: файлова система списків не тримає або змонтована без них.

**Два списки, і другий не про доступ.** `system.posix_acl_default` не вирішує нічого про сам об'єкт — це шаблон для того, що в ньому створять, і сенс він має лише в каталогу. Тому програма й питає його лише для каталогів. У звичайного файлу його не буде (`ENODATA`), а спроба його файлу *призначити* дасть `EACCES` — не тому, що бракує прав, а тому, що прохання безглузде.

**Довжина — єдина перевірка цілості.** У форматі немає ні лічильника записів, ні контрольної суми. Тому обрізане значення видає себе лише остачею: `(розмір − 4)` не ділиться на вісім. А якщо обріз випадково влучив у межу запису, розбирач не помітить нічого й покаже коротший список як цілком справний. Це не привід вигадувати свою контрольну суму — це привід не тягати ці байти руками там, де є пара `getfacl -R` / `setfacl --restore` і `cp --preserve=all`.

**Числа, а не люди.** У байтах немає жодного імені: `getpwuid` — це наша прикраса, і саме вона найдорожча в усій програмі, бо може піти в LDAP по мережі (`getfacl -n` для цього й має ключ «без імен»). Наслідок серйозніший за швидкість: список зберігає [uid і gid](topic:sys-unix/uid-gid-identity-model), а не людей. Перенесіть файл туди, де `1001` — інший працівник, і права дістануться йому; у контейнері з [власним простором імен користувачів](topic:sys-unix/namespaces) те саме число теж означає когось іншого.

**Читати можна прямо, а от писати «прямо» не вийде.** Формально `setxattr` на `system.posix_acl_access` працює — так і робить `libacl`. Хибним є інше припущення: що це сховище байтів, як `user.*`. Ядро перехоплює це ім'я й проганяє значення через розбір і перевірку: версія мусить бути `0x0002` (інакше `EOPNOTSUPP`), записи — іти строгим порядком видів (власник, іменовані користувачі, група файлу, іменовані групи, маска, решта), кожного з трьох обов'язкових — рівно по одному, маска — обов'язкова за наявності іменованих записів, а в полі прав не сміє стояти нічого поза трьома бітами. Будь-яке порушення — `EINVAL` цілком, без «часткового» запису. І успішний запис має побічну дію: ядро переписує `st_mode` файлу під новий список. Тому копіювати байти між машинами наосліп — поганий задум: `setfacl --restore` для того й існує, що він працює з іменами.

**Ціна.** Два системні виклики на атрибут (три, якщо список устиг вирости), одне виділення пам'яті й два проходи по записах — маску знаходимо першим, друкуємо другим, разом лінійно від кількості записів. Записів мало за побудовою: в ext4 усі атрибути об'єкта мусять уміститися в один блок, тож при блоці 4 КіБ їх туди входить кількасот, а не тисячі. Уся програма робить менше роботи, ніж один `stat` по холодному кешу.
