# 📋 Контракт ublk: вузли, команди, структури

Тут зібрано все, чим сервер ublk говорить із ядром: три вузли в `/dev`, керуючі команди, структури й прапорці можливостей — щоб сервер можна було написати без бібліотеки, самим заголовком. Заголовок один, `include/uapi/linux/ublk_cmd.h`, і жодного власного системного виклику ublk не має: і керування, і ввід-вивід ідуть наскрізними командами [io_uring](topic:sys-unix/io-uring-rings-model) — `IORING_OP_URING_CMD` на дескрипторі відповідного вузла.

## Три вузли

| вузол | хто відкриває | що ним ходить |
|---|---|---|
| `/dev/ublk-control` | керуюча програма | усі команди `UBLK_U_CMD_*`: створити, налаштувати, запустити, зупинити, видалити |
| `/dev/ublkc<N>` | сервер | канал даних: `mmap` масиву описів запитів і команди `UBLK_U_IO_*` |
| `/dev/ublkb<N>` | усі решта | власне блоковий пристрій — той, що йде в `mount`, `mkfs`, `dd` |

`ublkc` з'являється після `ADD_DEV`, `ublkb` — після `START_DEV` і зникає після `STOP_DEV`, тоді як `ublkc` живе аж до `DEL_DEV`. Саме через цей проміжок і працює відновлення після смерті демона: пристрій уже є, сервера ще немає.

## Керуюча команда

```c
struct ublksrv_ctrl_cmd {
        __u32   dev_id;         /* номер пристрою; -1 в ADD_DEV — «вибери сам» */
        __u16   queue_id;       /* -1, якщо команда не про чергу */
        __u16   len;            /* довжина буфера за addr */
        __u64   addr;           /* буфер команди: IN або OUT */
        __u64   data[1];        /* вбудоване число: pid, номер черги */
        __u16   dev_path_len;   /* лише для UBLK_F_UNPRIVILEGED_DEV, із нульовим байтом */
        __u16   pad;
        __u32   reserved;
};
```

Тридцять два байти цієї структури кладуть у поле `cmd` подання io_uring, а туди без `IORING_SETUP_SQE128` уміщається лише шістнадцять — тому керуюче кільце створюють саме з цим прапорцем.

Номери команд від ядра 6.4 закодовані [як номери ioctl](topic:sys-unix/ioctl-interface): `UBLK_U_CMD_ADD_DEV` — це `_IOWR('u', 0x04, struct ublksrv_ctrl_cmd)`. Голі числа ядро приймає й досі, а чи розуміє воно закодовану форму, видно з прапорця `UBLK_F_CMD_IOCTL_ENCODE`.

| команда | № | що заповнити | що станеться |
|---|---|---|---|
| `ADD_DEV` | 0x04 | `dev_id` (можна −1), `addr`→`ublksrv_ctrl_dev_info`, `len` | створює `/dev/ublkc<N>`; ядро вписує в структуру виданий номер |
| `SET_PARAMS` | 0x08 | `addr`→`ublk_params`, `len` | задає геометрію й можливості; після запуску — `-EACCES` |
| `GET_PARAMS` | 0x09 | `addr`, `len` | вичитує чинні параметри |
| `GET_QUEUE_AFFINITY` | 0x01 | `data[0]` = номер черги, `addr`→`cpu_set_t`, `len` | віддає маску ядер, що живлять цю чергу |
| `GET_DEV_INFO` | 0x02 | `dev_id`, `addr`, `len` | віддає `ublksrv_ctrl_dev_info` |
| `GET_DEV_INFO2` | 0x12 | те саме плюс шлях і `dev_path_len` | те саме для непривілейованого пристрою (з 6.3) |
| `START_DEV` | 0x06 | `data[0]` = pid демона | створює `/dev/ublkb<N>`; чекає, доки всі черги подадуть свої `FETCH_REQ` |
| `STOP_DEV` | 0x07 | `dev_id` | прибирає `ublkb`, обриває ввід-вивід |
| `DEL_DEV` | 0x05 | `dev_id` | прибирає `ublkc` |
| `START_USER_RECOVERY` | 0x10 | `dev_id` | готує пристрій до нового демона (з 6.2) |
| `END_USER_RECOVERY` | 0x11 | `data[0]` = pid нового демона | вмикає ввід-вивід назад |
| `GET_FEATURES` | 0x13 | `addr`→8 байтів, `len` = 8 | бітова карта підтримуваних `UBLK_F_*` (з 6.5) |

Номер черги в `GET_QUEUE_AFFINITY` береться з `data[0]`, а не з поля `queue_id` — пастка, на якій спотикаються всі. Маску згодовують [прив'язці потоку до ядер](topic:sys-unix/cpu-affinity), щоб потік черги не мандрував машиною.

## Опис пристрою

```c
struct ublksrv_ctrl_dev_info {
        __u16   nr_hw_queues;      /* ≤ UBLK_MAX_NR_QUEUES        */
        __u16   queue_depth;       /* ≤ UBLK_MAX_QUEUE_DEPTH = 4096 */
        __u16   state;             /* ← ядро: DEAD 0, LIVE 1, QUIESCED 2, FAIL_IO 3 */
        __u16   pad0;
        __u32   max_io_buf_bytes;  /* стеля одного запиту в байтах */
        __u32   dev_id;            /* ↔ на вході -1, на виході — виданий номер */
        __s32   ublksrv_pid;       /* ← ядро: pid демона з START_DEV */
        __u32   pad1;
        __u64   flags;             /* UBLK_F_*                     */
        __u64   ublksrv_flags;     /* ядро не читає: приватне поле сервера */
        __u32   owner_uid;         /* ← ядро, для UBLK_F_UNPRIVILEGED_DEV */
        __u32   owner_gid;
        __u64   reserved1, reserved2;
};
```

## Параметри пристрою

`SET_PARAMS` бере одну структуру, у якій `types` — бітова маска того, які з укладених усередину частин заповнено, а `len` — розмір самої структури (так ядро розуміє, з якого заголовка зібрано програму).

```c
struct ublk_params {
        __u32   len, types;              /* UBLK_PARAM_TYPE_* */
        struct ublk_param_basic    basic;
        struct ublk_param_discard  discard;
        struct ublk_param_devt     devt;     /* ← ядро віддає major/minor обох вузлів */
        struct ublk_param_zoned    zoned;    /* з 6.6 */
        /* далі — dma_align, segment, integrity */
};

struct ublk_param_basic {
        __u32   attrs;                   /* UBLK_ATTR_*            */
        __u8    logical_bs_shift;        /* 9 → 512 Б, 12 → 4 КіБ  */
        __u8    physical_bs_shift;
        __u8    io_opt_shift, io_min_shift;
        __u32   max_sectors;             /* стеля запиту в секторах по 512 Б */
        __u32   chunk_sectors;
        __u64   dev_sectors;             /* розмір пристрою, сектори по 512 Б */
        __u64   virt_boundary_mask;
};
```

Розміри блоків задаються **показником степеня двійки**, а не числом байтів, і саме звідси беруться `logical_block_size` та `physical_block_size` у sysfs. Довжини всюди — у секторах по 512 байтів, незалежно від того, який логічний блок оголошено.

| `attrs` | що каже блоковому шарові |
|---|---|
| `UBLK_ATTR_READ_ONLY` | пристрій лише для читання |
| `UBLK_ATTR_ROTATIONAL` | «обертається» — планувальник рахує це за диск, а не за SSD |
| `UBLK_ATTR_VOLATILE_CACHE` | є летючий кеш запису, тож ядро слатиме `FLUSH` |
| `UBLK_ATTR_FUA` | сервер уміє позначку «цей запис — одразу на носій» |

> 🔧 **Навіщо це.** Ці два останні біти — уся правда про [довговічність запису](topic:sys-unix/page-cache-durability) на вашому пристрої. Не оголосили летючого кеша — ядро вважає, що записане вже довговічне, і `FLUSH` не надішле взагалі; оголосили, але виконуєте його не по-справжньому — `fsync` перетворюється на брехню. Третього не дано.

`ublk_param_discard` описує [викидання блоків](topic:sf-data/discard-and-trim): `discard_granularity` і `discard_alignment` у байтах, `max_discard_sectors` та `max_write_zeroes_sectors` у секторах, `max_discard_segments` — скільки проміжків уміщає один запит.

## Канал даних: розкладка `/dev/ublkc<N>`

Описи запитів сервер бачить як пам'ять — [відображенням](topic:sys-unix/mmap-model) символьного вузла. Зсув відображення обирає чергу, і крок між чергами сталий, від глибини не залежить:

```
крок  = round_up(UBLK_MAX_QUEUE_DEPTH · sizeof(ublksrv_io_desc), сторінка)
      = round_up(4096 · 24, 4096) = 98304             /* 96 КіБ на чергу */
зсув  = UBLKSRV_CMD_BUF_OFFSET + q_id · крок          /* UBLKSRV_CMD_BUF_OFFSET = 0 */
довжина = round_up(queue_depth · 24, сторінка)
```

```c
q->desc = mmap(NULL, len, PROT_READ, MAP_SHARED | MAP_POPULATE, ublkc_fd, off);
```

`PROT_READ` тут не осторога, а вимога: відображення з `VM_WRITE` ядро відхиляє кодом `-EPERM`.

```c
struct ublksrv_io_desc {
        __u32   op_flags;       /* операція: біти 0–7; прапорці: біти 8–31 */
        __u32   nr_sectors;
        __u64   start_sector;
        __u64   addr;           /* буфер сервера під дані цього запиту */
};

__u8  op  = iod->op_flags & 0xff;
bool  fua = iod->op_flags & UBLK_IO_F_FUA;   /* прапорці стоять на своїх бітах */
```

| операція | № | | прапорець | біт |
|---|---|---|---|---|
| `UBLK_IO_OP_READ` | 0 | | `UBLK_IO_F_FAILFAST_DEV` | 8 |
| `UBLK_IO_OP_WRITE` | 1 | | `UBLK_IO_F_FAILFAST_TRANSPORT` | 9 |
| `UBLK_IO_OP_FLUSH` | 2 | | `UBLK_IO_F_FAILFAST_DRIVER` | 10 |
| `UBLK_IO_OP_DISCARD` | 3 | | `UBLK_IO_F_META` | 11 |
| `UBLK_IO_OP_WRITE_SAME` | 4 | | `UBLK_IO_F_FUA` | 13 |
| `UBLK_IO_OP_WRITE_ZEROES` | 5 | | `UBLK_IO_F_NOUNMAP` | 15 |
| зонні, 10–18 (з 6.6) | | | `UBLK_IO_F_SWAP` | 16 |

`UBLK_IO_F_SWAP` варто читати окремо: цей запит прийшов від вивільнення пам'яті, і сервер, який заради нього піде по пам'ять сам, ризикує замкнути коло.

## Команди вводу-виводу

```c
struct ublksrv_io_cmd {
        __u16   q_id;
        __u16   tag;
        __s32   result;   /* оброблені байти, або -errno */
        __u64   addr;     /* буфер сервера */
};
```

Шістнадцять байтів — уміщається у звичайне подання, `SQE128` для кільця черги не потрібен.

| команда | № | коли подають |
|---|---|---|
| `UBLK_U_IO_FETCH_REQ` | 0x20 | по одній на кожен тег до `START_DEV`: озброює комірку й заявляє потік демоном цієї пари (черга, тег) |
| `UBLK_U_IO_COMMIT_AND_FETCH_REQ` | 0x21 | після обробки: віддає `result` і одразу стає в чергу знову |
| `UBLK_U_IO_NEED_GET_DATA` | 0x22 | лише з `UBLK_F_NEED_GET_DATA`: другий крок запису — сервер називає буфер, ядро копіює в нього дані |
| `UBLK_U_IO_REGISTER_IO_BUF` | 0x23 | з 6.15: реєструє сторінки запиту як буфер io_uring під номером `addr` |
| `UBLK_U_IO_UNREGISTER_IO_BUF` | 0x24 | з 6.15: звільняє цей номер |

Результат завершення читається так: `UBLK_IO_RES_OK` (0) — прийшов новий запит, іди читати комірку; `UBLK_IO_RES_NEED_GET_DATA` (1) — запит на запис чекає буфера; `UBLK_IO_RES_ABORT` (`-ENODEV`) — пристрій зупиняють, більше нічого не подавай. Тег зручно класти в `user_data` подання: у завершенні воно повертається незмінним.

## Прапорці можливостей

| біт | прапорець | що змінює | з ядра |
|---|---|---|---|
| 0 | `UBLK_F_SUPPORT_ZERO_COPY` | передавання даних без копії; оголошений із самого початку, а робочим став із парою `REGISTER_IO_BUF`/`UNREGISTER_IO_BUF` | 6.0 / 6.15 |
| 1 | `UBLK_F_URING_CMD_COMP_IN_TASK` | завершення команди виконується в контексті потоку сервера | 6.0 |
| 2 | `UBLK_F_NEED_GET_DATA` | запис у два кроки: буфер називають уже після появи запиту | 6.0 |
| 3 | `UBLK_F_USER_RECOVERY` | пристрій переживає смерть демона: неподані запити чекають нового | 6.2 |
| 4 | `UBLK_F_USER_RECOVERY_REISSUE` | до нового демона віддають і ті запити, що вже були в роботі — для сховищ, яким подвійний запис не шкодить | 6.2 |
| 5 | `UBLK_F_UNPRIVILEGED_DEV` | права перевіряються за вузлом `ublkc`, тож пристроєм керує його власник; шлях передають у `dev_path_len` | 6.3 |
| 6 | `UBLK_F_CMD_IOCTL_ENCODE` | ядро розуміє закодовані номери `UBLK_U_*` | 6.4 |
| 7 | `UBLK_F_USER_COPY` | дані переносять `pread`/`pwrite` по `ublkc` замість поля `addr` | 6.5 |
| 8 | `UBLK_F_ZONED` | зонний пристрій, з'являються операції 10–18 | 6.6 |
| 9 | `UBLK_F_USER_RECOVERY_FAIL_IO` | замість чекання — помилки вводу-виводу, доки відновлення не завершилося | 6.13 |
| 11 | `UBLK_F_AUTO_BUF_REG` | сторінки запиту реєструються під номером `ublk_auto_buf_reg.index` самі, без двох окремих команд | 6.16 |

Прапорець 5 — єдиний, що змінює модель прав: без нього кожна керуюча команда вимагає [загальносистемної можливості](topic:sys-unix/capabilities), з ним — лише права на вузол, які роздають [правила udev](topic:sys-unix/udev-rules).

Із `UBLK_F_USER_COPY` зсув для `pread`/`pwrite` складають із трьох полів:

| поле | біти | ширина |
|---|---|---|
| зсув усередині буфера | 0–24 | 25 |
| тег | 25–40 | 16 |
| номер черги | 41–52 | 12 |

до чого додають базу `UBLKSRV_IO_BUF_OFFSET` = `0x80000000`.

## Найменший робочий виклик

```c
struct io_uring ctrl;
io_uring_queue_init(2, &ctrl, IORING_SETUP_SQE128);   /* 32 байти не влізуть у звичайний SQE */
int cfd = open("/dev/ublk-control", O_RDWR);

struct ublksrv_ctrl_dev_info info = {
        .nr_hw_queues     = 1,
        .queue_depth      = 128,
        .max_io_buf_bytes = 512 * 1024,
        .dev_id           = (__u32)-1,        /* хай ядро вибере номер */
        .flags            = UBLK_F_CMD_IOCTL_ENCODE,
};

struct io_uring_sqe *sqe = io_uring_get_sqe(&ctrl);
io_uring_prep_read(sqe, cfd, NULL, 0, 0);             /* обнуляємо поля, далі перекриваємо */
sqe->opcode = IORING_OP_URING_CMD;
sqe->cmd_op = UBLK_U_CMD_ADD_DEV;

struct ublksrv_ctrl_cmd *c = (struct ublksrv_ctrl_cmd *)sqe->cmd;
c->dev_id   = (__u32)-1;
c->queue_id = (__u16)-1;                              /* команда не про чергу */
c->addr     = (__u64)(uintptr_t)&info;
c->len      = sizeof(info);

io_uring_submit(&ctrl);

struct io_uring_cqe *cqe;
io_uring_wait_cqe(&ctrl, &cqe);
if (cqe->res == 0)
        printf("з'явився /dev/ublkc%u\n", info.dev_id);   /* номер уписало ядро */
```

Далі порядок незмінний: `SET_PARAMS` із розміром і геометрією, відображення описів і по `FETCH_REQ` на кожен тег — і аж тоді `START_DEV` із `data[0] = getpid()`, після якого в системі з'явиться `/dev/ublkb<N>`.
