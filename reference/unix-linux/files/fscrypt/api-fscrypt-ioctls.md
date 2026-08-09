# 📋 Інтерфейс fscrypt: сім ioctl, п'ять структур і карта відмов

Довідка подає контракт fscrypt дослівно: якими сімома викликами `ioctl` живуть чинні політики другої версії, як улаштовані `struct fscrypt_policy_v2`, `fscrypt_key_specifier`, `fscrypt_add_key_arg`, `fscrypt_remove_key_arg` і `fscrypt_get_key_status_arg`, які номери мають режими шифрування, що обмежує кожен прапорець політики і який `errno` за якою причиною повертає кожен виклик.

## Сім викликів

```c
#include <linux/fscrypt.h>   /* окремий uapi-заголовок — з ядра 5.4 */

#define FS_IOC_SET_ENCRYPTION_POLICY     _IOR('f', 19, struct fscrypt_policy_v1)
#define FS_IOC_GET_ENCRYPTION_PWSALT     _IOW('f', 20, __u8[16])
#define FS_IOC_GET_ENCRYPTION_POLICY     _IOW('f', 21, struct fscrypt_policy_v1)
#define FS_IOC_GET_ENCRYPTION_POLICY_EX  _IOWR('f', 22, __u8[9])
#define FS_IOC_ADD_ENCRYPTION_KEY        _IOWR('f', 23, struct fscrypt_add_key_arg)
#define FS_IOC_REMOVE_ENCRYPTION_KEY     _IOWR('f', 24, struct fscrypt_remove_key_arg)
#define FS_IOC_REMOVE_ENCRYPTION_KEY_ALL_USERS \
                                         _IOWR('f', 25, struct fscrypt_remove_key_arg)
#define FS_IOC_GET_ENCRYPTION_KEY_STATUS _IOWR('f', 26, struct fscrypt_get_key_status_arg)
#define FS_IOC_GET_ENCRYPTION_NONCE      _IOR('f', 27, __u8[16])
```

| Виклик | На чому викликають | Аргумент | З ядра |
| --- | --- | --- | --- |
| `FS_IOC_SET_ENCRYPTION_POLICY` | **порожній** каталог | `struct fscrypt_policy_v2 *` | 4.1; версія v2 — 5.4 |
| `FS_IOC_GET_ENCRYPTION_POLICY_EX` | будь-який файл | `struct fscrypt_get_policy_ex_arg *` | 5.4 |
| `FS_IOC_ADD_ENCRYPTION_KEY` | будь-який файл цієї ФС | `struct fscrypt_add_key_arg *` | 5.4 |
| `FS_IOC_REMOVE_ENCRYPTION_KEY` | те саме | `struct fscrypt_remove_key_arg *` | 5.4 |
| `FS_IOC_REMOVE_ENCRYPTION_KEY_ALL_USERS` | те саме, потрібен `CAP_SYS_ADMIN` | `struct fscrypt_remove_key_arg *` | 5.4 |
| `FS_IOC_GET_ENCRYPTION_KEY_STATUS` | те саме | `struct fscrypt_get_key_status_arg *` | 5.4 |
| `FS_IOC_GET_ENCRYPTION_NONCE` | зашифрований файл | `__u8[16]` | 5.7 |

Чотири виклики керування ключами приймають дескриптор **будь-якого** файлу чи каталогу на потрібній файловій системі — звично беруть корінь монтування, бо ключ належить саме змонтованій ФС, а не процесові й не каталогові. Підсистему мають ext4, F2FS, UBIFS і CephFS; решта відповість `ENOTTY`.

Одну пастку в цьому переліку варто прочитати уважно: напрямок у макросах 19 і 21 переставлений. `SET` оголошено через `_IOR`, `GET` — через `_IOW`. Це давня помилка, і виправити її вже не можна, бо біти напрямку входять у [числовий код ioctl](book:unix-linux/ioctl-interface/api-ioctl-encoding.md), а отже й в ABI. Напрямок тут читають із назви, не з макроса.

## Політика

```c
#define FSCRYPT_POLICY_V1  0            /* так, нуль */
#define FSCRYPT_POLICY_V2  2

struct fscrypt_policy_v2 {
        __u8 version;                   /* 2 */
        __u8 contents_encryption_mode;
        __u8 filenames_encryption_mode;
        __u8 flags;
        __u8 log2_data_unit_size;       /* 0 — блок файлової системи */
        __u8 __reserved[3];             /* нулі */
        __u8 master_key_identifier[16]; /* FSCRYPT_KEY_IDENTIFIER_SIZE */
};
```

| Поле | Межі | Примітка |
| --- | --- | --- |
| `version` | `FSCRYPT_POLICY_V2` (2) | нумерація без одиниці: v1-політика має тут **0** |
| `contents_encryption_mode` | 1, 5, 7, 9 | таблиця нижче |
| `filenames_encryption_mode` | 4, 6, 8, 9, 10 | таблиця нижче |
| `flags` | доповнення + не більш як один із трьох прапорців ключа | інші біти — `EINVAL` |
| `log2_data_unit_size` | 0 або log₂ власної одиниці шифрування | ненульове значення підтримує не кожна ФС |
| `__reserved[3]` | нулі | сміття з купи дає `EINVAL` |
| `master_key_identifier` | 16 байтів | те, що `FS_IOC_ADD_ENCRYPTION_KEY` повернув у `key_spec.u.identifier` |

Політику ставлять один раз і назавжди: повторний виклик із **точно такою самою** політикою минає без наслідків, а з будь-якою іншою — `EEXIST`. Успадковують її всі нащадки каталогу.

## Режими

Для **вмісту**:

| № | Стала | Режим | Ключ | IV |
| --- | --- | --- | --- | --- |
| 1 | `FSCRYPT_MODE_AES_256_XTS` | [AES-256-XTS](book:programming/aes-xts) | 64 Б | 16 Б |
| 5 | `FSCRYPT_MODE_AES_128_CBC` | AES-128-CBC-ESSIV | 16 Б | 16 Б |
| 7 | `FSCRYPT_MODE_SM4_XTS` | SM4-XTS | 32 Б | 16 Б |
| 9 | `FSCRYPT_MODE_ADIANTUM` | Adiantum | 32 Б | 32 Б |

Для **імен**:

| № | Стала | Режим | Ключ | IV |
| --- | --- | --- | --- | --- |
| 4 | `FSCRYPT_MODE_AES_256_CTS` | AES-256-CBC-CTS | 32 Б | 16 Б |
| 6 | `FSCRYPT_MODE_AES_128_CTS` | AES-128-CBC-CTS | 16 Б | 16 Б |
| 8 | `FSCRYPT_MODE_SM4_CTS` | SM4-CBC-CTS | 16 Б | 16 Б |
| 9 | `FSCRYPT_MODE_ADIANTUM` | Adiantum | 32 Б | 32 Б |
| 10 | `FSCRYPT_MODE_AES_256_HCTR2` | AES-256-HCTR2 | 32 Б | 32 Б |

Номери 2 і 3 у переліку відсутні: їх колись зайняли й ніколи не вживали. Довжина ключа в таблиці — це довжина **виведеного** ключа, а не того, що подають у ядро.

Пари складають не довільно. Рекомендована — `(1, 4)`; `(1, 10)` дає для імен ширший і стійкіший режим там, де процесор має інструкції AES; `(9, 9)` беруть там, де їх немає; `(5, 6)` і `(7, 8)` тримають однакову стійкість з обох боків.

## Прапорці політики

| Значення | Стала | Що робить |
| --- | --- | --- |
| 0x00–0x03 | `FSCRYPT_POLICY_FLAGS_PAD_4/8/16/32` | межа доповнення імен нулями; маска `0x03` |
| 0x04 | `FSCRYPT_POLICY_FLAG_DIRECT_KEY` | не виводити ключ на кожен inode; nonce файлу йде у вектор ініціалізації |
| 0x08 | `FSCRYPT_POLICY_FLAG_IV_INO_LBLK_64` | один ключ на політику; IV = номер inode у старших 32 бітах, номер одиниці даних у молодших |
| 0x10 | `FSCRYPT_POLICY_FLAG_IV_INO_LBLK_32` | те саме, але номер inode згортають SipHash-2-4 і додають до номера одиниці за модулем 2³² |

Обмеження на них жорсткіші, ніж здається з опису.

- **Доповнення.** Імена, коротші за 16 байтів, ядро добиває нулями до 16 незалежно від прапорця — менше режим CBC-CTS просто не вміє. Далі довжину округляють угору до заданої межі. `PAD_32` рекомендоване: чим грубша сітка, тим менше з довжини видно.
- **`DIRECT_KEY`** вимагає, щоб режим вмісту й режим імен збігалися, а вектор ініціалізації був не менший за 24 байти — 8 на номер одиниці даних плюс 16 на nonce. На практиці це означає Adiantum з обох боків.
- **`IV_INO_LBLK_64` і `IV_INO_LBLK_32`** нині дозволені лише з AES-256-XTS для вмісту, лише в політиці v2 і лише на файловій системі зі **сталими номерами inode** (для ext4 це позначка `stable_inodes`, після якої розділ уже не стиснути). Номери inode мусять уміщатися в 32 біти; для `_64` у 32 біти мусить уміщатися ще й номер одиниці даних, що дає стелю розміру файлу. `_32` цю стелю знімає ціною повторення векторів і призначений лише для заліза, яке інакше не вміє.
- Три прапорці ключа **взаємно виключні**: два одночасно — `EINVAL`.

## Ключ

```c
struct fscrypt_key_specifier {
        __u32 type;             /* 1 = DESCRIPTOR (v1), 2 = IDENTIFIER (v2) */
        __u32 __reserved;
        union {
                __u8 __reserved[32];
                __u8 descriptor[8];     /* FSCRYPT_KEY_DESCRIPTOR_SIZE */
                __u8 identifier[16];    /* FSCRYPT_KEY_IDENTIFIER_SIZE */
        } u;
};

struct fscrypt_add_key_arg {
        struct fscrypt_key_specifier key_spec;  /* вхід; для v2 identifier — ВИХІД */
        __u32 raw_size;                         /* 16..64, або 0 при key_id != 0 */
        __u32 key_id;                           /* 0 або ключ зі зв'язки ядра */
        __u32 flags;                            /* 0x1 = FSCRYPT_ADD_KEY_FLAG_HW_WRAPPED */
        __u32 __reserved[7];                    /* нулі */
        __u8  raw[];                            /* сам секрет */
};
```

`key_spec.u.identifier` для політик v2 — поле **вихідне**: його лишають нулями, а ядро вписує туди криптографічний геш поданого ключа. Саме ці шістнадцять байтів потім кладуть у політику.

Про сам секрет:

- довжина 16–64 байти (`FSCRYPT_MAX_KEY_SIZE` = 64) і не менша за стійкість найсильнішого з двох режимів — для AES-256 це 32 байти;
- політика v1 вимагає рівно стільки, скільки має виведений ключ режиму, тобто 64 байти для AES-256-XTS;
- `key_id ≠ 0` означає, що секрет уже лежить у [зв'язці ключів ядра](book:unix-linux/kernel-keyrings) як ключ типу `fscrypt-provisioning`; тоді `raw_size` мусить бути 0, а `raw` — порожній;
- специфікатор типу `DESCRIPTOR` (тобто політики v1) потребує [`CAP_SYS_ADMIN`](book:unix-linux/capabilities); для `IDENTIFIER` жодних прав не треба — звичайний користувач додає й прибирає свої ключі сам.

## Вилучення й статус

```c
struct fscrypt_remove_key_arg {
        struct fscrypt_key_specifier key_spec;
        __u32 removal_status_flags;   /* вихід */
        __u32 __reserved[5];
};

struct fscrypt_get_key_status_arg {
        struct fscrypt_key_specifier key_spec;   /* вхід */
        __u32 __reserved[6];
        __u32 status;                            /* вихід: 1 / 2 / 3 */
        __u32 status_flags;                      /* 0x1 = ADDED_BY_SELF */
        __u32 user_count;                        /* скільки заявок на ключ */
        __u32 __out_reserved[13];
};
```

| Прапорець `removal_status_flags` | Значення | Коли ставиться |
| --- | --- | --- |
| `FSCRYPT_KEY_REMOVAL_STATUS_FLAG_FILES_BUSY` | 0x1 | секрет затерто, але якісь файли лишилися відкриті |
| `FSCRYPT_KEY_REMOVAL_STATUS_FLAG_OTHER_USERS` | 0x2 | знято лише вашу заявку, ключ лишився для інших |

![Три рамки в ряд показують стани ключа. Ліворуч ABSENT з номером один: ключа у файловій системі немає, відкрити чи створити файл під ним дає ENOKEY, а ls, stat і rm працюють. Посередині PRESENT з номером два: ключ у пам'яті файлової системи, поле user_count каже, скільки користувачів його заявили, а виклик REMOVE_KEY від одного з кількох знімає лише його заявку й повертає нуль із прапорцем OTHER_USERS, не міняючи стану. Праворуч INCOMPLETELY_REMOVED з номером три: секрет затерто, але частина файлів ще відкрита, нові відкриття вже дають ENOKEY, а ключі вже відкритих файлів ядро не забирає. Зелена стрілка зліва направо підписана FS_IOC_ADD_ENCRYPTION_KEY і переходом user_count з нуля в одиницю. Жовта стрілка від PRESENT до INCOMPLETELY_REMOVED підписана: REMOVE_KEY від останнього користувача, коли якісь файли ще відкриті, дає FILES_BUSY. Синій шлях знизу веде від PRESENT назад до ABSENT: REMOVE_KEY від останнього користувача, коли жоден файл не відкрито, затирає секрет, скидає кеші імен і сторінок і повертає нуль без прапорців. Найнижчий жовтий шлях веде від INCOMPLETELY_REMOVED до ABSENT із підписом: закрити ті файли й повторити REMOVE_KEY, саме воно не довершиться. Унизу зауваження, що FS_IOC_GET_ENCRYPTION_KEY_STATUS читає цей стан без жодних прав і показує відсутній ключ станом ABSENT, а не помилкою ENOKEY](/reference/unix-linux/files/fscrypt/img/key-lifecycle.svg)

*Статус `INCOMPLETELY_REMOVED` — не помилка й не проміжна фаза, яка мине сама: доки відкриті файли не закриють і виклик не повторять, ключ так і лишиться напівприбраним.*

> 🔧 **Навіщо це.** `FS_IOC_REMOVE_ENCRYPTION_KEY` повертає нуль у трьох геть різних випадках: ключ справді затерто; затерто, але частина файлів працює далі; не затерто взагалі, бо його заявили ще інші користувачі. Розрізняє їх лише `removal_status_flags`, і код, який перевіряє тільки повернене значення, спокійно доповість про замкнені дані там, де вони лишилися відкритими. Той, кому потрібне саме замикання, читає прапорці, а потім ще й звіряється зі статусом.

## Мінімальний робочий виклик

```c
struct {
        struct fscrypt_add_key_arg arg;
        __u8 raw[32];
} k = { 0 };                       /* обнулення обов'язкове: є резервні поля */

k.arg.key_spec.type = FSCRYPT_KEY_SPEC_TYPE_IDENTIFIER;
k.arg.raw_size      = 32;
memcpy(k.raw, master_key, 32);     /* 32 байти з /dev/urandom */

int mnt = open("/data", O_RDONLY | O_DIRECTORY);
if (ioctl(mnt, FS_IOC_ADD_ENCRYPTION_KEY, &k.arg) != 0)
        perror("FS_IOC_ADD_ENCRYPTION_KEY");
/* ядро вписало 16 байтів у k.arg.key_spec.u.identifier */

struct fscrypt_policy_v2 pol = {
        .version                   = FSCRYPT_POLICY_V2,
        .contents_encryption_mode  = FSCRYPT_MODE_AES_256_XTS,
        .filenames_encryption_mode = FSCRYPT_MODE_AES_256_CTS,
        .flags                     = FSCRYPT_POLICY_FLAGS_PAD_32,
};
memcpy(pol.master_key_identifier, k.arg.key_spec.u.identifier, 16);

int dir = open("/data/oksana", O_RDONLY | O_DIRECTORY);   /* каталог порожній */
if (ioctl(dir, FS_IOC_SET_ENCRYPTION_POLICY, &pol) != 0)
        perror("FS_IOC_SET_ENCRYPTION_POLICY");
```

Порядок нежорсткий лише на позір: політику v2 з незнайомим ідентифікатором ядро прийме тільки від процесу з `CAP_FOWNER`, а звичайному користувачеві відповість `ENOKEY`. Тому ключ додають першим.

## Карта відмов

| `errno` | Де | Причина |
| --- | --- | --- |
| `ENOTTY` | усі | ця файлова система fscrypt не має взагалі |
| `EOPNOTSUPP` | усі | ядро зібране без `CONFIG_FS_ENCRYPTION` або на суперблоці не ввімкнено шифрування |
| `EINVAL` | усі | невідома версія, режим чи прапорець; несумісні прапорці; ненульове резервне поле; неприйнятна довжина ключа |
| `ENOTEMPTY` | `SET_POLICY` | каталог не порожній |
| `ENOTDIR` | `SET_POLICY` | ціль — не каталог, а звичайний незашифрований файл |
| `EEXIST` | `SET_POLICY` | на файлі вже стоїть **інша** політика |
| `EACCES` | `SET_POLICY` | процес не власник файлу й не має `CAP_FOWNER` |
| `EACCES` | `ADD_KEY`, `REMOVE_KEY` | специфікатор `DESCRIPTOR` без `CAP_SYS_ADMIN`; або немає права `search` на ключ зі зв'язки |
| `ENOKEY` | `SET_POLICY` | ключ із цим ідентифікатором не доданий, а `CAP_FOWNER` немає |
| `ENOKEY` | `ADD_KEY` | `key_id` указує на ключ, якого у зв'язці немає |
| `ENOKEY` | `REMOVE_KEY` | ключ ніколи не додавали, вже прибрали, або саме ваша заявка не знайдена |
| `ENOKEY` | `open`, `creat`, `truncate`, `rename` | у зашифрованому каталозі немає ключа — це не помилка ioctl, а звичайна відмова файлової операції |
| `EDQUOT` | `ADD_KEY` | вичерпано квоту ключів користувача |
| `EKEYREJECTED` | `ADD_KEY` | ключ зі зв'язки має не той тип |
| `EBADMSG` | `ADD_KEY` | апаратно загорнутий ключ несформований |
| `ENODATA` | `GET_POLICY_EX`, `GET_NONCE` | файл не зашифровано |
| `EOVERFLOW` | `GET_POLICY_EX` | політика не влазить у буфер, заявлений у `policy_size` |
| `EPERM` | `SET_POLICY` | цей каталог шифрувати не можна — наприклад, корінь файлової системи |
| `EROFS` | `SET_POLICY` | ФС змонтовано лише для читання |

`FS_IOC_GET_ENCRYPTION_KEY_STATUS` у цій таблиці має рівно три рядки — `EINVAL`, `ENOTTY`, `EOPNOTSUPP`. Відсутність ключа помилкою для нього не є: він повертає нуль і статус `ABSENT`.

## Те саме з командного рядка

`fscryptctl` — тонка обгортка, у якій кожна підкоманда відповідає одному ioctl.

| Команда | Виклик |
| --- | --- |
| `fscryptctl add_key ТОЧКА` (ключ зі stdin, друкує ідентифікатор) | `FS_IOC_ADD_ENCRYPTION_KEY` |
| `fscryptctl set_policy ІДЕНТИФІКАТОР КАТАЛОГ` | `FS_IOC_SET_ENCRYPTION_POLICY` |
| `fscryptctl get_policy ШЛЯХ` | `FS_IOC_GET_ENCRYPTION_POLICY_EX` |
| `fscryptctl remove_key ІДЕНТИФІКАТОР ТОЧКА` | `FS_IOC_REMOVE_ENCRYPTION_KEY` |
| `fscryptctl key_status ІДЕНТИФІКАТОР ТОЧКА` | `FS_IOC_GET_ENCRYPTION_KEY_STATUS` |

```
$ head -c 32 /dev/urandom > key.bin
$ fscryptctl add_key /data < key.bin
f2b5a8c1d4e7093a6b0c5f8e2d1a4703
$ mkdir /data/oksana && fscryptctl set_policy f2b5a8c1d4e7093a6b0c5f8e2d1a4703 /data/oksana
$ fscryptctl remove_key f2b5a8c1d4e7093a6b0c5f8e2d1a4703 /data
$ ls /data/oksana
nyLEwEhVe0RY9c4tKq3B1AoZ7xPmT2fUdG5rIsJv0Cw
```

Останній рядок і є перевіркою, що ключ пішов: імена лишилися на місці, але вже безключові — сорок три символи base64url на кожні тридцять два байти шифротексту.
