# 📋 Контракт sed-opal: виклики IOC_OPAL_*, структури, коди помилок

Усе, що ядро приймає від програми, яка керує самошифрувальним носієм: двадцять сім викликів `IOC_OPAL_*`, структури-аргументи до кожного, прапорці стану й коди помилок на кожній перевірці. Довідка потрібна тоді, коли треба не «запустити sedutil», а зрозуміти чужий виклик, написати свій або пояснити, чому в журналі `EOPNOTSUPP` замість роботи. Звірено з `include/uapi/linux/sed-opal.h`, `include/linux/sed-opal.h`, `block/sed-opal.c` і `block/Kconfig`.

## Де це живе

| що | де |
| --- | --- |
| параметр збірки | `CONFIG_BLK_SED_OPAL` — `bool`, `depends on KEYS` |
| публічні визначення | `include/uapi/linux/sed-opal.h` |
| реалізація протоколу | `block/sed-opal.c` |
| точка входу | `sed_ioctl()`, `EXPORT_SYMBOL_GPL` |
| магічне число ioctl | `'p'`, номери 220–246 |

`depends on KEYS` тут не формальність: без [кілець ключів ядра](book:unix-linux/kernel-keyrings) не буде кільця `.sed_opal`, а з ним і другого способу подати пароль.

## Точка входу

```c
int sed_ioctl(struct opal_dev *dev, unsigned int cmd, void __user *ioctl_ptr);
```

Програма цієї сигнатури не бачить. Вона робить звичайний [ioctl](book:unix-linux/ioctl-interface) на дескрипторі **цілого носія** — `/dev/nvme0n1`, `/dev/sda`, — а блоковий шар упізнає код за списком `is_sed_ioctl()` і передає його сюди. Перед будь-якою роботою стоять три ворота й одні на виході:

| перевірка | не пройшла — повертається |
| --- | --- |
| `capable(CAP_SYS_ADMIN)` | `-EACCES` |
| драйвер підставив `struct opal_dev` (тобто вміє носити службові буфери) | `-EOPNOTSUPP` |
| `dev->flags & OPAL_FL_SUPPORTED` — Level 0 Discovery підтвердив Opal | `-EOPNOTSUPP` |
| код команди знайшовся в `switch` | `-ENOTTY` |

Перша перевірка — саме [капабілність](book:unix-linux/capabilities), а не «нульовий uid»: команда, здатна стерти носій цілком, не роздається за одним фактом володіння файлом.

Аргумент ядро копіює одним шматком — `memdup_user(arg, _IOC_SIZE(cmd))`. Розмір воно бере з самого номера команди, а не з того, що сказала програма, тож неузгодженого розміру структури не буває за побудовою. Виняток один: `IOC_OPAL_STACK_RESET` оголошено як `_IO`, аргументу не має зовсім.

## Ключ — атом усього інтерфейсу

```c
#define OPAL_KEY_MAX    256
#define OPAL_MAX_LRS    9
#define OPAL_UID_LENGTH 8

struct opal_key {
        __u8 lr;                  /* номер діапазону; 0 — глобальний */
        __u8 key_len;             /* довжина пароля в байтах */
        __u8 key_type;            /* OPAL_INCLUDED | OPAL_KEYRING */
        __u8 __align[5];
        __u8 key[OPAL_KEY_MAX];
};
```

`key_type` вирішує, звідки ядро візьме пароль. `OPAL_INCLUDED` (нуль) — пароль лежить тут же, у `key[]`. `OPAL_KEYRING` — у структурі його немає, ядро прочитає його з кільця `.sed_opal` за описом `opal-boot-pin`, підставить довжину в `key_len` і перепише `key_type` на `OPAL_INCLUDED`. Порожній ключ після цього (`key_len == 0`) або невідомий `key_type` — `-EINVAL`; ключ, довший за 255 байтів, — `-ENOSPC`.

`OPAL_MAX_LRS` дорівнює дев'яти: вісім окремих діапазонів, яких вимагає Opal SSC, і глобальний під номером нуль.

Над ключем надбудовано рівно один проміжний рівень, і саме він пояснює форму більшості аргументів:

```c
struct opal_session_info {
        __u32 sum;                /* сеанс у режимі Single User Mode */
        __u32 who;                /* OPAL_ADMIN1 = 0, OPAL_USER1…OPAL_USER9 = 1…9 */
        struct opal_key opal_key;
};
```

![Два рівні вкладення структур sed-opal над opal_key](/reference/unix-linux/devices/sed-opal-drives/img/opal-structs.svg)

*Хто виконує дію й чим доводить право — це `opal_session_info`; аргументи, яким користувач не потрібен, беруть голий `opal_key`, а три виклики читання не беруть ключа взагалі.*

## Власність і життєвий цикл

| виклик | напрям | аргумент | що робить |
| --- | --- | --- | --- |
| `IOC_OPAL_TAKE_OWNERSHIP` | `_IOW` 222 | `opal_key` | увійти рядком MSID і замінити SID на свій |
| `IOC_OPAL_ACTIVATE_LSP` | `_IOW` 223 | `opal_lr_act` | активувати Locking SP; у режимі SUM ще й завести діапазони зі списку `lr[num_lrs]` |
| `IOC_OPAL_REACTIVATE_LSP` | `_IOW` 242 | `opal_lr_react` | переактивувати Locking SP з новим ключем адміністратора (`new_admin_key`) і новою політикою діапазонів |
| `IOC_OPAL_SET_SID_PW` | `_IOW` 241 | `opal_new_pw` | змінити пароль SID в Admin SP |
| `IOC_OPAL_REVERT_TPR` | `_IOW` 226 | `opal_key` | повернути носій до заводського стану ключем SID — з породженням нового MEK, тобто [зі знищенням даних](book:unix-linux/secure-erase-and-sanitize) |
| `IOC_OPAL_PSID_REVERT_TPR` | `_IOW` 232 | `opal_key` | те саме, але ключ — PSID з наліпки; єдиний шлях, коли пароль загублено |
| `IOC_OPAL_REVERT_LSP` | `_IOW` 240 | `opal_revert_lsp` | відкотити лише Locking SP; `options = OPAL_PRESERVE` просить зберегти дані |
| `IOC_OPAL_STACK_RESET` | `_IO` 246 | — | скинути стек протоколу на носії (виходить із завислих сеансів) |

`opal_lr_act` і `opal_lr_react` носять список діапазонів масивом на дев'ять байтів; `num_lrs > OPAL_MAX_LRS` — `-EINVAL`. У `opal_lr_react` ще й `entire_table` разом із непорожнім `num_lrs` — теж `-EINVAL`: або вся таблиця, або перелік.

## Діапазони й замок

```c
struct opal_user_lr_setup {
        __u64 range_start;
        __u64 range_length;
        __u32 RLE;                /* Read Lock Enabled  */
        __u32 WLE;                /* Write Lock Enabled */
        struct opal_session_info session;
};

struct opal_lock_unlock {
        struct opal_session_info session;
        __u32 l_state;            /* OPAL_RO = 1 | OPAL_RW = 2 | OPAL_LK = 4 */
        __u16 flags;              /* OPAL_SAVE_FOR_LOCK = 1 */
        __u8  __align[2];
};
```

| виклик | напрям | аргумент | що робить |
| --- | --- | --- | --- |
| `IOC_OPAL_LR_SETUP` | `_IOW` 227 | `opal_user_lr_setup` | задати межі діапазону **і** прапорці `RLE`/`WLE` одним заходом |
| `IOC_OPAL_LR_SET_START_LEN` | `_IOW` 243 | `opal_user_lr_setup` | лише зсунути межі; на глобальному діапазоні (`lr == 0`) — `-EINVAL` |
| `IOC_OPAL_ENABLE_DISABLE_LR` | `_IOW` 244 | `opal_user_lr_setup` | лише перемкнути `RLE`/`WLE`, не чіпаючи меж |
| `IOC_OPAL_LOCK_UNLOCK` | `_IOW` 221 | `opal_lock_unlock` | перевести діапазон у `OPAL_RO`, `OPAL_RW` або `OPAL_LK` |
| `IOC_OPAL_SAVE` | `_IOW` 220 | `opal_lock_unlock` | **нічого не робить зараз**: запам'ятовує запит, щоб відтворити його після пробудження |
| `IOC_OPAL_ADD_USR_TO_LR` | `_IOW` 228 | `opal_lock_unlock` | дати користувачеві право на діапазон; `l_state` тут означає **дозволений** режим і мусить бути `OPAL_RO` або `OPAL_RW` |
| `IOC_OPAL_ERASE_LR` | `_IOW` 230 | `opal_session_info` | стерти діапазон засобами режиму SUM |
| `IOC_OPAL_SECURE_ERASE_LR` | `_IOW` 231 | `opal_session_info` | `GenKey` над діапазоном: новий ключ, старий шифротекст стає шумом |

Три деталі, на яких найлегше спіткнутися.

`IOC_OPAL_SAVE` не відмикає нічого. Він додає запис у список `dev->unlk_lst`, звідки `opal_unlock_from_suspend()` відтворює всі збережені відмикання при [поверненні зі сну](book:unix-linux/suspend-and-resume) — раніше, ніж черга запитів почне приймати роботу. Повторний `SAVE` на той самий `lr` витісняє попередній запис.

`OPAL_SAVE_FOR_LOCK` у полі `flags` розв'язує окрему незручність. Opal вимагає пароль навіть на **замикання**, хоча решта світу закриває шифрований пристрій без ключа. Тому якщо в `IOC_OPAL_SAVE` був піднятий цей прапорець, то пізніший `IOC_OPAL_LOCK_UNLOCK` зі станом `OPAL_LK`, порожнім `key_len` і тим самим `lr` ядро дозволить: воно підставить збережений ключ саме́. Це і є те, завдяки чому Opal вкладається у звичні звички [dm-crypt](book:unix-linux/dm-crypt) і LUKS.

`who > OPAL_USER9` — `-EINVAL` у `LOCK_UNLOCK`, `ADD_USR_TO_LR` і `SET_PW`. Дев'ять користувачів — це не обмеження ядра, а межа переліку `opal_user`.

## Користувачі й паролі

| виклик | напрям | аргумент | що робить |
| --- | --- | --- | --- |
| `IOC_OPAL_ACTIVATE_USR` | `_IOW` 225 | `opal_session_info` | увімкнути запис користувача (свіжі `USER1…USER9` вимкнені) |
| `IOC_OPAL_SET_PW` | `_IOW` 224 | `opal_new_pw` | змінити пароль |

`struct opal_new_pw` — це дві `opal_session_info` підряд: `session` каже, **чим авторизуємось**, `new_user_pw` — **кому** ставимо новий пароль і **який**. Плутанина цих двох полів — найчастіша причина `-ERANGE` у відповідь на, здавалося б, правильний виклик.

## Тіньовий MBR

| виклик | напрям | аргумент | що робить |
| --- | --- | --- | --- |
| `IOC_OPAL_ENABLE_DISABLE_MBR` | `_IOW` 229 | `opal_mbr_data` | `enable_disable` ∈ {`OPAL_MBR_ENABLE` = 0, `OPAL_MBR_DISABLE` = 1}; інше — `-EINVAL` |
| `IOC_OPAL_MBR_DONE` | `_IOW` 233 | `opal_mbr_done` | `done_flag` ∈ {`OPAL_MBR_NOT_DONE` = 0, `OPAL_MBR_DONE` = 1} |
| `IOC_OPAL_WRITE_SHADOW_MBR` | `_IOW` 234 | `opal_shadow_mbr` | залити образ у тіньову область шматками |

```c
struct opal_shadow_mbr {
        struct opal_key key;
        const __u64 data;         /* вказівник простору користувача, покладений у u64 */
        __u64 offset;
        __u64 size;
};
```

Поле `data` — саме число, а не вказівник: так структура має однаковий вигляд для 32- і 64-бітних програм, і [шар сумісности](book:unix-linux/compat-32-on-64) не мусить її перекладати. Той самий прийом ужито в `opal_discovery` та `opal_read_write_table`.

Дві дії тут навмисно розділені. `ENABLE_DISABLE_MBR` вмикає підміну назавжди (переживає перезавантаження), `MBR_DONE` знімає її **до найближчої втрати живлення**. Перше — налаштування, друге — крок кожного завантаження.

## Читання стану

| виклик | напрям | аргумент | що повертає |
| --- | --- | --- | --- |
| `IOC_OPAL_GET_STATUS` | `_IOR` 236 | `opal_status` | `flags` — прапорці `OPAL_FL_*` |
| `IOC_OPAL_GET_LR_STATUS` | `_IOW` 237 | `opal_lr_status` | межі діапазону, `RLE`/`WLE` і `l_state` |
| `IOC_OPAL_GET_SUM_STATUS` | `_IOW` 245 | `opal_sum_ranges` | які діапазони заведено в режимі SUM |
| `IOC_OPAL_GET_GEOMETRY` | `_IOR` 238 | `opal_geometry` | `logical_block_size`, `alignment_granularity`, `lowest_aligned_lba`, `align` |
| `IOC_OPAL_DISCOVERY` | `_IOW` 239 | `opal_discovery` | сирі байти Level 0 Discovery у буфер `data` розміром `size` |
| `IOC_OPAL_GENERIC_TABLE_RW` | `_IOW` 235 | `opal_read_write_table` | читання або запис довільної таблиці за `table_uid[8]`; напрям — `flags` = `OPAL_TABLE_READ` або `OPAL_TABLE_WRITE` |

Напрям у номері команди відповідає не «читаємо чи пишемо», а «чи є вхідні дані». `GET_LR_STATUS` оголошено як `_IOW`, бо мусить **прийняти** сеанс і номер діапазону; результат він потім кладе назад у той самий буфер через `copy_to_user`. Лише `GET_STATUS` і `GET_GEOMETRY` — чисте `_IOR`: їм на вхід не треба нічого.

`IOC_OPAL_DISCOVERY` вибивається з ряду ще й поверненим значенням: при успіху він повертає **число прочитаних байтів**, а не нуль. Хто перевіряє `ret != 0` замість `ret < 0`, побачить помилку там, де все спрацювало.

| прапорець `opal_status.flags` | значення |
| --- | --- |
| `OPAL_FL_SUPPORTED` (0x01) | носій узагалі відповів дескриптором Opal |
| `OPAL_FL_LOCKING_SUPPORTED` (0x02) | є можливість замикання |
| `OPAL_FL_LOCKING_ENABLED` (0x04) | замикання ввімкнено (носій уже налаштовано) |
| `OPAL_FL_LOCKED` (0x08) | зараз замкнено |
| `OPAL_FL_MBR_ENABLED` (0x10) | тіньовий MBR увімкнено |
| `OPAL_FL_MBR_DONE` (0x20) | підміну вже знято в цьому вмиканні |
| `OPAL_FL_SUM_SUPPORTED` (0x40) | підтримано режим Single User Mode |

## Коди помилок

| код | коли |
| --- | --- |
| `EACCES` | немає `CAP_SYS_ADMIN` — єдина перевірка прав у всьому інтерфейсі |
| `EOPNOTSUPP` | носій не має `opal_dev` або Discovery не побачив Opal; те саме отримає диск без підтримки |
| `ENOTTY` | код команди не з набору `IOC_OPAL_*` |
| `EINVAL` | аргумент суперечливий: порожній чи невідомий ключ, `who > USER9`, `num_lrs > 9`, `lr == 0` у `LR_SET_START_LEN`, стан поза `OPAL_RO`/`OPAL_RW`, прапорець MBR поза переліком |
| `ERANGE` | не вдалося скласти UID об'єкта з номера діапазону чи користувача, або носій відмовив на зміні пароля |
| `EBUSY` | `STACK_RESET`: носій не підтвердив скидання (відповідь неочікуваної довжини) |
| `EIO` | `STACK_RESET`: носій відповів ненульовим кодом |
| `EFAULT` | не вдалося скопіювати буфер до або з простору користувача |
| `ENODEV` | Locking SP не в стані «виготовлено, не активовано» — активувати нічого |
| `ENOSPC` | ключ із кільця довший за 255 байтів |

Коди, з якими носій відмовляє **по суті** — не той пароль, замкнений діапазон, — сюди не потрапляють окремими значеннями: помилка протоколу приїжджає з відповіді TCG і перекладається на загальне ненульове повернення, а подробиця лишається в `pr_debug`. Тому налагоджувати такі виклики без `dyndbg` на `block/sed-opal.c` майже неможливо.

## Мінімальний робочий виклик

Відімкнути діапазон 1 і одразу озброїти відновлення після сну — це два `ioctl` на одній структурі:

```c
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <linux/sed-opal.h>

int main(void)
{
        int fd = open("/dev/nvme0n1", O_RDONLY);   /* цілий носій, не розділ */
        struct opal_status st = {0};
        const char *pin = "correct horse battery";

        if (ioctl(fd, IOC_OPAL_GET_STATUS, &st) < 0) { perror("GET_STATUS"); return 1; }
        printf("flags=0x%08x locked=%d mbr=%d\n", st.flags,
               !!(st.flags & OPAL_FL_LOCKED), !!(st.flags & OPAL_FL_MBR_ENABLED));

        struct opal_lock_unlock lu = {
                .session = {
                        .who = OPAL_ADMIN1,
                        .sum = 0,
                        .opal_key = { .lr = 1, .key_type = OPAL_INCLUDED },
                },
                .l_state = OPAL_RW,
        };
        lu.session.opal_key.key_len = strlen(pin);
        memcpy(lu.session.opal_key.key, pin, lu.session.opal_key.key_len);

        if (ioctl(fd, IOC_OPAL_LOCK_UNLOCK, &lu) < 0) { perror("UNLOCK"); return 1; }

        lu.flags = OPAL_SAVE_FOR_LOCK;             /* дозволити замикання без пароля */
        if (ioctl(fd, IOC_OPAL_SAVE, &lu) < 0) { perror("SAVE"); return 1; }

        return 0;
}
```

Щоб той самий код не тримав пароль у своїй пам'яті, досить поміняти два поля: `.key_type = OPAL_KEYRING` і не заповнювати `key[]` — ядро візьме `opal-boot-pin` із кільця `.sed_opal`, куди його заклав [initramfs](book:unix-linux/initramfs).

## Інструменти простору користувача

| інструмент | охоплення | тракт до носія |
| --- | --- | --- |
| `cryptsetup` ≥ 2.7 — `--hw-opal`, `--hw-opal-only`, `cryptsetup erase --hw-opal-factory-reset` | лише ключ відмикання діапазону, зате в межах тому LUKS2: `--hw-opal-only` — самий апаратний замок, `--hw-opal` — він же плюс dm-crypt поверх | `IOC_OPAL_*` |
| `sedutil-cli` (Drive Trust Alliance / Bright Plaza) | найширше покриття Opal 2.0: власність, діапазони, користувачі, збірка й заливка образу PBA | старший за sed-opal, ходить власним трактом наскрізних команд |
| `sedcli` і бібліотека `libsed` (початково Intel, далі Solidigm) | керування NVMe-носіями Opal програмно, з прицілом на зовнішнє зберігання ключів | орієнтований на NVMe |

Різниця між ними не в зручності, а в тому, скільки специфікації вони бачать. Ядро реалізує **підмножину** Opal 2.0 — рівно стільки, щоб володіти носієм і керувати замками; тому інструмент, який хоче більшого (складна робота з таблицями, підготовка образу PBA), або тягне все через `IOC_OPAL_GENERIC_TABLE_RW`, або взагалі обходить `sed-opal` [наскрізними командами](book:unix-linux/scsi-generic-passthrough). Cryptsetup же навмисно не намагається бути інструментом керування Opal: він бере з нього рівно одну властивість — ключ, який відмикає діапазон, — і вбудовує її в те, що вже вміє.
