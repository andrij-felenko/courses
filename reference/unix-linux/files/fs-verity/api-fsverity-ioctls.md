# 📋 Інтерфейс fs-verity: три ioctl, чотири структури й таблиця відмов

Довідка подає контракт fs-verity дослівно: які три виклики `ioctl` існують і що передають у кожен, як улаштовано `struct fsverity_enable_arg`, `struct fsverity_digest`, `struct fsverity_read_metadata_arg` і сам дескриптор на 256 байтів, який `errno` за якою причиною стоїть, звідки береться довіра до вбудованого підпису й чим те саме роблять із командного рядка.

## Три виклики

```c
#include <linux/fsverity.h>     /* uapi-заголовок; є з ядра 5.4 */

#define FS_IOC_ENABLE_VERITY   _IOW('f', 133, struct fsverity_enable_arg)
#define FS_IOC_MEASURE_VERITY  _IOWR('f', 134, struct fsverity_digest)
#define FS_IOC_READ_VERITY_METADATA \
                               _IOWR('f', 135, struct fsverity_read_metadata_arg)
```

| Виклик | Аргумент | З ядра | Повертає за успіху |
| --- | --- | --- | --- |
| `FS_IOC_ENABLE_VERITY` | `struct fsverity_enable_arg *` | 5.4 | `0` |
| `FS_IOC_MEASURE_VERITY` | `struct fsverity_digest *` | 5.4 | `0` |
| `FS_IOC_READ_VERITY_METADATA` | `struct fsverity_read_metadata_arg *` | 5.12 | кількість прочитаних байтів |

Усі три — звичайні [ioctl](book:unix-linux/ioctl-interface) на дескрипторі відкритого файлу, і всі три за відмови повертають `-1` та ставлять `errno`. Підтримка з боку файлових систем: ext4 і f2fs — з ядра 5.4, btrfs — з 5.15.

## Увімкнення

```c
struct fsverity_enable_arg {
        __u32 version;          /* має бути 1 */
        __u32 hash_algorithm;   /* 1 = SHA-256, 2 = SHA-512 */
        __u32 block_size;       /* у байтах, степінь двійки */
        __u32 salt_size;        /* 0..32 */
        __u64 salt_ptr;         /* адреса солі в просторі користувача */
        __u32 sig_size;         /* 0, якщо вбудованого підпису немає */
        __u32 __reserved1;      /* нуль */
        __u64 sig_ptr;          /* адреса підпису PKCS#7 */
        __u64 __reserved2[11];  /* нулі */
};                              /* 128 байтів */
```

| Поле | Межі | Примітка |
| --- | --- | --- |
| `version` | рівно `1` | інше значення — `EINVAL` |
| `hash_algorithm` | `FS_VERITY_HASH_ALG_SHA256` (1), `FS_VERITY_HASH_ALG_SHA512` (2) | алгоритм має бути зібраний у ядрі, інакше `ENOPKG` |
| `block_size` | степінь двійки від 1024 до меншого з двох: розмір сторінки й розмір блока ФС | до ядра 6.3 дозволено було лише розмір сторінки |
| `salt_size` | 0..32 | більше — `EMSGSIZE` |
| `sig_size` | 0..16128 | більше — `EMSGSIZE` |

Дескриптор файлу мусить бути відкритий **тільки на читання** — і водночас процес мусить мати право запису на сам файл. Кожен зайвий дескриптор на запис, чий завгодно і навіть відображення в пам'ять, дає `ETXTBSY`.

```c
int fd = open("app.apk", O_RDONLY);          /* саме O_RDONLY */

struct fsverity_enable_arg arg = {
        .version        = 1,
        .hash_algorithm = FS_VERITY_HASH_ALG_SHA256,
        .block_size     = 4096,
};                                            /* решта полів — нулі */

if (ioctl(fd, FS_IOC_ENABLE_VERITY, &arg) != 0)
        perror("FS_IOC_ENABLE_VERITY");
```

Ініціалізація структури нулями обов'язкова: ядро перевіряє резервні поля й на ненульовому смітті з купи відповість `EINVAL`.

## Чому відмовляє ввімкнення

| `errno` | Причина |
| --- | --- |
| `EACCES` | процесові бракує права **запису** на файл |
| `EISDIR` | дескриптор указує на каталог |
| `EINVAL` | не та версія, алгоритм чи розмір блока; ненульове резервне поле; файл не звичайний |
| `EMSGSIZE` | сіль довша за 32 байти або підпис довший за 16128 |
| `EEXIST` | на файлі вже ввімкнено перевірку |
| `ETXTBSY` | файл хтось тримає відкритим на запис |
| `EBUSY` | цей самий `ioctl` уже виконують над цим файлом |
| `EPERM` | файл позначено як лише-дозапис (`chattr +a`); або підпис вимагають, а його не передали |
| `EROFS` | файлова система змонтована лише для читання |
| `EFBIG` | файл завеликий для дерева |
| `EINTR` | побудову дерева перервав фатальний сигнал |
| `EFAULT` | `salt_ptr` або `sig_ptr` указують у недоступну пам'ять |
| `ENOPKG` | алгоритм відомий, але не зібраний у цьому ядрі |
| `EBADMSG` | підпис несформований — його не вдалося розібрати |
| `EKEYREJECTED` | підпис розібрано, але він не відповідає цифрі файлу |
| `ENOKEY` | у кільці `.fs-verity` немає сертифіката, яким його перевірити |
| `ENOTTY` | ця файлова система fs-verity не має взагалі |
| `EOPNOTSUPP` | ядро зібране без fs-verity або на суперблоці не ввімкнено можливість `verity` |

> 🔧 **Навіщо це.** Два останніх рядки легко переплутати, а лікуються вони по-різному. `ENOTTY` означає «тут ніколи»: файлова система такого не вміє, і зробити нічого не можна, крім як покласти файл в іншу. `EOPNOTSUPP` означає «тут поки що»: ext4 створюють із `mkfs.ext4 -O verity`, і на розділі без цієї позначки жоден файл перевірки не дістане, хоч би яким правильним був виклик.

## Цифра

```c
struct fsverity_digest {
        __u16 digest_algorithm;   /* вихід: 1 або 2 */
        __u16 digest_size;        /* вхід: розмір буфера; вихід: скільки записано */
        __u8  digest[];           /* вихід */
};
```

`digest_size` — єдине поле, що працює в обидва боки: на вході в ньому лежить довжина місця, яке ви виділили, на виході — довжина справжньої цифри. Алгоритм наперед невідомий, тож буфер беруть із запасом на найдовший, тобто 64 байти для SHA-512; замалий буфер дає `EOVERFLOW`.

```c
union {
        struct fsverity_digest d;
        char pad[sizeof(struct fsverity_digest) + 64];
} u = { .d.digest_size = 64 };

if (ioctl(fd, FS_IOC_MEASURE_VERITY, &u.d) == 0)
        /* u.d.digest_size байтів цифри лежать в u.d.digest */;
```

Відмови тут короткі: `ENODATA` — на файлі перевірки немає; `EOVERFLOW` — буфер замалий; `EFAULT`, `ENOTTY`, `EOPNOTSUPP` — те саме, що й вище.

## Метадані

```c
struct fsverity_read_metadata_arg {
        __u64 metadata_type;   /* 1 дерево, 2 дескриптор, 3 підпис */
        __u64 offset;
        __u64 length;
        __u64 buf_ptr;
        __u64 __reserved;      /* нуль */
};
```

| `metadata_type` | Стала | Що читається |
| --- | --- | --- |
| 1 | `FS_VERITY_METADATA_TYPE_MERKLE_TREE` | блоки дерева суцільним потоком: від кореневого рівня вниз до листя, а всередині рівня — у тому порядку, у якому їх гешують |
| 2 | `FS_VERITY_METADATA_TYPE_DESCRIPTOR` | дескриптор без вбудованого підпису |
| 3 | `FS_VERITY_METADATA_TYPE_SIGNATURE` | сам підпис PKCS#7, якщо він є |

Поводиться виклик як `pread`: повертає число прочитаних байтів, менше за `length` наприкінці й `0` за кінцем. Одне застереження вагоміше за решту опису: **прочитані метадані ніхто не засвідчує**. Ядро віддає їх як є, не звіряючи з цифрою; той, хто збирається на них покладатися, звіряє сам.

Відмови: `ENODATA` — на файлі немає перевірки або немає саме підпису; `EINVAL` — ненульове резервне поле чи переповнення від `offset + length`; `EINTR` — сигнал прийшов, поки не прочитано ще нічого; далі `EFAULT`, `ENOTTY`, `EOPNOTSUPP`. Окремо варто пам'ятати, що `ENOTTY` тут означає ще й «файлова система fs-verity має, але цього виклику не реалізує», — він молодший за два інших на вісім випусків ядра.

## Дескриптор — 256 байтів, які й гешують

| Зсув | Розмір | Поле | Що в ньому |
| --- | --- | --- | --- |
| 0 | 1 | `version` | `1` |
| 1 | 1 | `hash_algorithm` | 1 або 2 |
| 2 | 1 | `log_blocksize` | log₂ розміру блока: `12` для 4096 |
| 3 | 1 | `salt_size` | 0..32 |
| 4 | 4 | `__reserved_0x04` | нулі — у першому варіанті інтерфейсу тут стояв `sig_size` |
| 8 | 8 | `data_size` | розмір даних файлу, порядок байтів молодшим уперед |
| 16 | 64 | `root_hash[64]` | кореневий геш; для SHA-256 задіяно 32 байти, решта нулі |
| 80 | 32 | `salt[32]` | сіль, доповнена нулями до 32 |
| 112 | 144 | `__reserved[144]` | нулі |
| | **256** | | |

Поле фіксованої довжини там, де значення коротше, доповнюють нулями — саме тому структура завжди рівно 256 байтів і саме тому її геш однозначний. Це й дозволяє порахувати цифру збоку, не питаючи ядро.

## Що саме підписують

![Ланцюг із чотирьох рамок згори вниз. Перша — struct fsverity_descriptor на 256 байтів із переліком полів: version, hash_algorithm, log_blocksize, salt_size, data_size, root_hash[64], salt[32], reserved[144]. Стрілка вниз, підписана «SHA-256 над цими 256 байтами», веде до другої рамки: цифра файлу — 32 байти для SHA-256, саме її віддає FS_IOC_MEASURE_VERITY. Стрілка «обгортка з магією FSVerity» веде до третьої: struct fsverity_formatted_digest на 44 байти, складена з магії FSVerity у вісім байтів, алгоритму у два, довжини у два й самої цифри у тридцять два. Остання стрілка, підписана «підписують саме ці 44 байти», веде до четвертої рамки: підпис PKCS#7 у sig_ptr, не більший за 16128 байтів, який ядро звіряє з кільцем ключів .fs-verity. Унизу зауваження, що з fs.verity.require_signatures рівним одиниці файл без дійсного підпису не відкриється](/reference/unix-linux/files/fs-verity/img/signed-bytes.svg)

*Підпис накриває не файл і не дескриптор, а коротку обгортку навколо цифри — тому підписати можна, ще не маючи файлу під рукою.*

```c
struct fsverity_formatted_digest {
        char   magic[8];          /* "FSVerity", без кінцевого нуля */
        __le16 digest_algorithm;
        __le16 digest_size;
        __u8   digest[];
};
```

Магічний рядок тут не прикраса: він прив'язує підпис до fs-verity, щоб той самий ключ, підписавши щось в іншому контексті, не дав випадково придатного для fs-verity підпису.

Довіру до підпису задають ззовні, двома діями. Сертифікат кладуть у [кільце ключів](book:unix-linux/kernel-keyrings) на ім'я `.fs-verity`, яке ядро заводить при завантаженні, а обов'язковість підпису вмикають [параметром ядра](book:unix-linux/sysctl-tunables):

```
# keyctl padd asymmetric '' %keyring:.fs-verity < cert.der
# sysctl fs.verity.require_signatures=1
```

Обидва працюють лише з `CONFIG_FS_VERITY_BUILTIN_SIGNATURES=y`. Самі ж розробники fs-verity радять цю можливість стримано: ключ один на всю систему, підпис після ввімкнення вже не змінити, а розбір X.509 і PKCS#7 усередині ядра — зайва поверхня для нападу. Політика в просторі користувача, що звіряє цифру з підписаного переліку, робить те саме без цих трьох вад.

## Побачити ззовні, не відкриваючи файл

`statx` виставляє прапорець `STATX_ATTR_VERITY` (0x00100000) у `stx_attributes` — з ядра 5.5. Прапорці атрибутів у [statx](book:unix-linux/statx-extended-stat) читають тільки разом із маскою: біт поза `stx_attributes_mask` означає не «вимкнено», а «ядро про такий не знає».

```c
struct statx st;
statx(AT_FDCWD, "app.apk", AT_STATX_SYNC_AS_STAT, STATX_BASIC_STATS, &st);

int verity_on = (st.stx_attributes_mask & STATX_ATTR_VERITY)
             && (st.stx_attributes      & STATX_ATTR_VERITY);
```

Той самий факт віддає `FS_IOC_GETFLAGS` бітом `FS_VERITY_FL` (0x00100000), а з ядра 7.0 — `FS_IOC_FSGETXATTR` бітом `FS_XFLAG_VERITY` (0x00020000).

## Те саме з командного рядка

| Команда | Що робить |
| --- | --- |
| `fsverity enable ФАЙЛ` | `FS_IOC_ENABLE_VERITY`; ключі `--hash-alg`, `--block-size`, `--salt`, `--signature` |
| `fsverity measure ФАЙЛ…` | `FS_IOC_MEASURE_VERITY`; ключів не приймає |
| `fsverity digest ФАЙЛ…` | рахує цифру **сам**, без ядра, з тих самих параметрів; `--compact`, `--for-builtin-sig` |
| `fsverity sign ФАЙЛ ПІДПИС` | рахує цифру й підписує її ключем `--key` із сертифікатом `--cert`, кладе PKCS#7 у DER |
| `fsverity dump_metadata ТИП ФАЙЛ` | `FS_IOC_READ_VERITY_METADATA`; ТИП — `merkle_tree`, `descriptor` або `signature` |

Повний шлях від ключа до незмінного файлу:

```
$ openssl req -newkey rsa:4096 -nodes -keyout key.pem -x509 -out cert.pem
$ openssl x509 -in cert.pem -out cert.der -outform der
# keyctl padd asymmetric '' %keyring:.fs-verity < cert.der

$ fsverity sign app.apk app.sig --key=key.pem --cert=cert.pem
$ fsverity enable app.apk --signature=app.sig
$ fsverity measure app.apk
```

`digest` і `measure` мусять давати той самий рядок: перший рахує цифру з файлу, другий питає її в ядра. Розбіжність означає, що параметри при ввімкненні були інші, ніж ті, які ви передали в `digest`, — найчастіше розмір блока або сіль.
