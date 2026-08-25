# 📋 Контракт cgroup-writeback: що оголошує файлова система і де це видно

Облік фонового запису по групах не вмикається сам собою: файлова система мусить проставити один прапорець на суперблоці й зробити два виклики у своєму `->writepages()`. Тут зібрано точні імена, сигнатури, поля структур і числа арбітражу, а далі — файли, за якими на живій машині видно, чи механізм справді працює. Стан коду — ядро 6.16; де сигнатура мінялася, це позначено.

## Чотири умови, за яких механізм узагалі живий

Ядро перевіряє їх усі разом у функції `inode_cgwb_enabled()` (`include/linux/backing-dev.h`). Хоч одна не виконана — inode обслуговує кореневий wb, мовчки й без жодного повідомлення.

| Умова в коді | Що означає | Як перевірити ззовні |
|---|---|---|
| `cgroup_subsys_on_dfl(memory_cgrp_subsys)` | контролер `memory` — на єдиній ієрархії v2 | `grep cgroup2 /proc/mounts` |
| `cgroup_subsys_on_dfl(io_cgrp_subsys)` | контролер `io` — теж на v2 | `io` у `cgroup.subtree_control` батьківської теки |
| `bdi->capabilities & BDI_CAP_WRITEBACK` | пристрій-підкладка взагалі робить зворотний запис | у `tmpfs`, наприклад, цієї здатності немає |
| `inode->i_sb->s_iflags & SB_I_CGROUPWB` | файлова система оголосила підтримку | непрямо — по `wb_stats` (нижче) |

Перевірка динамічна: та сама умова на тому самому inode-і дасть іншу відповідь, якщо контролери в системі переставити на ходу.

Нульова умова — збірка ядра. Опція `CONFIG_CGROUP_WRITEBACK` не має власного пункту меню: вона `depends on MEMCG && BLK_CGROUP` і `default y`, тобто вмикається сама, щойно ввімкнено обидва контролери. Шукати її в `menuconfig` марно; дивитися треба в `/boot/config-$(uname -r)`.

## Три обов'язки файлової системи

**1. Прапорець на суперблоці** — у функції заповнення суперблока:

```c
sb->s_iflags |= SB_I_CGROUPWB;   /* include/linux/fs.h, 0x00000001 */
```

Прапорець живе на **суперблоці**, а не на типі файлової системи, і це не дрібниця. У першій редакції серії (2015) було поле `FS_CGROUP_WRITEBACK` в `fs_type->fs_flags`, але його прибрали ще до випуску 4.2 — у жодному випущеному ядрі такої константи немає. Причина: одна й та сама ФС буває змонтована так, що облік працює, і так, що ні. Живий приклад — ext4, де прапорець ставлять лише в гілці `else`: монтування з [журналюванням самих даних](topic:sys-unix/journaling-consistency) (`data=journal`) залишає весь фоновий запис кореневій групі, і попередження про це не друкують.

Сьогодні прапорець ставлять ext2, btrfs, f2fs, XFS та ext4 (крім `data=journal`).

**2. Штамп на кожному bio:**

```c
static inline void wbc_init_bio(struct writeback_control *wbc, struct bio *bio);
```

Викликати **після** того, як [bio](topic:sys-unix/block-device-model) прив'язали до пристрою, і **до** подання. Усередині — `bio_associate_blkg_from_css(bio, wbc->wb->blkcg_css)`: саме тут запит дістає групу вводу-виводу, якій виписувати рахунок. Коли `wbc->wb` порожній (шлях `pageout()`), виклик не робить нічого — навмисно, щоб витіснення не блокувалося за повільною групою.

**3. Голос за кожен діапазон даних:**

```c
void wbc_account_cgroup_owner(struct writeback_control *wbc,
                              struct folio *folio, size_t bytes);
```

Викликати на кожен сегмент даних, що йде на запис; найприродніше — там, де сегменти додають у bio. До ядра 6.13 другим аргументом була `struct page *`. Функція бере групу зі сторінки (`mem_cgroup_css_from_folio()`), відкидає групи, що вже вмирають, і додає байти до одного з трьох лічильників у `wbc`.

Опція відмови — `wbc->no_cgroup_owner = 1`: вимикає голосування на всю сесію. Так робить btrfs для стиснених екстентів, бо записувані там сторінки не ті, що їх облікував контролер пам'яті, і голос за них був би брехнею.

**Чого робити не треба.** Прив'язку `wbc` до inode-а й підбиття підсумків веде сам VFS: `wbc_attach_fdatawrite_inode()` перед `do_writepages()` і `wbc_detach_inode()` після нього. Файлова система в це не втручається.

## Кістяк подання, як його пише ext4

```c
/* fs/ext4/page-io.c, спрощено */
static void io_submit_init_bio(struct ext4_io_submit *io, struct buffer_head *bh)
{
    struct bio *bio = bio_alloc(bh->b_bdev, BIO_MAX_VECS, REQ_OP_WRITE, GFP_NOIO);

    bio->bi_iter.bi_sector = bh->b_blocknr * (bh->b_size >> 9);
    bio->bi_end_io = ext4_end_bio;
    io->io_bio = bio;
    wbc_init_bio(io->io_wbc, bio);          /* пристрій уже відомий */
}

static void io_submit_add_bh(struct ext4_io_submit *io, struct inode *inode,
                             struct folio *folio, struct folio *io_folio,
                             struct buffer_head *bh)
{
    if (io->io_bio == NULL)
        io_submit_init_bio(io, bh);

    if (!bio_add_folio(io->io_bio, io_folio, bh->b_size, bh_offset(bh)))
        goto submit_and_retry;              /* bio повний — подати й почати новий */

    wbc_account_cgroup_owner(io->io_wbc, folio, bh->b_size);
}
```

Тут видно розрізнення, яке легко проґавити: у bio додають `io_folio` (можливо, підмінну сторінку — зашифровану чи стиснену), а в облік подають `folio` — ту, яку облікував контролер пам'яті. Голосувати треба за сторінку кешу, а не за те, що фізично поїхало на диск.

## Поля, у яких живе стан

`struct writeback_control` (`include/linux/writeback.h`, під `CONFIG_CGROUP_WRITEBACK`) — стан однієї сесії:

| Поле | Тип | Роль |
|---|---|---|
| `wb` | `struct bdi_writeback *` | wb, під яким іде сесія; `NULL` — облік вимкнено |
| `inode` | `struct inode *` | inode, що записується |
| `wb_id` | `int` | id групи пам'яті нинішнього власника |
| `wb_bytes` | `size_t` | байти, зараховані власникові |
| `wb_lcand_id`, `wb_lcand_bytes` | `int`, `size_t` | переможець минулого обходу і його байти |
| `wb_tcand_id`, `wb_tcand_bytes` | `int`, `size_t` | кандидат цього обходу за [голосуванням більшості](topic:sf-algorithms/majority-vote-boyer-moore) — один id і один лічильник замість таблиці на групу |

`struct inode` (`include/linux/fs.h`) — те, що переживає сесію:

| Поле | Тип | Роль |
|---|---|---|
| `i_wb` | `struct bdi_writeback *` | нинішній власник inode-а |
| `i_wb_frn_winner` | `int` | id переможця минулого обходу |
| `i_wb_frn_avg_time` | `u16` | ковзне середнє тривалості обходу |
| `i_wb_frn_history` | `u16` | шістнадцятибітова історія «чужих» комірок |

Дістати wb inode-а — `inode_to_wb(inode)` (під `i_lock`), поза замком — парою `unlocked_inode_to_wb_begin()` / `unlocked_inode_to_wb_end()` із курсором `struct wb_lock_cookie`. Знайти чи створити wb для пари «пристрій + група пам'яті» — `wb_get_lookup(bdi, memcg_css)` і `wb_get_create(bdi, memcg_css, gfp)`; запустити запис саме такої пари ззовні — `cgroup_writeback_by_id(bdi_id, memcg_id, reason, done)`.

## Константи арбітражу власності (`fs/fs-writeback.c`)

| Константа | Значення | Що з нього виходить |
|---|---|---|
| `WB_FRN_TIME_SHIFT` | 13 | одиниця часу: 1 с = 2¹³ = 8192 |
| `WB_FRN_TIME_PERIOD` | 2·2¹³ = 16384 | вікно історії — 2 с |
| `WB_FRN_HIST_SLOTS` | 16 | стільки комірок у полі `i_wb_frn_history` |
| `WB_FRN_HIST_UNIT` | 16384 / 16 = 1024 | одна комірка — 125 мс |
| `WB_FRN_HIST_THR_SLOTS` | 16 / 2 = 8 | поріг переходу власності |
| `WB_FRN_HIST_MAX_SLOTS` | 8 / 2 + 1 = 5 | один обхід зсуває не більш ніж 5 комірок |
| `WB_FRN_TIME_AVG_SHIFT` | 3 | avg = avg·7/8 + new·1/8 |
| `WB_FRN_TIME_CUT_DIV` | 8 | обхід коротший за avg/8 в історію не потрапляє |
| `WB_FRN_MAX_IN_FLIGHT` | 1024 | стільки перемикань inode-ів одночасно щонайбільше |

Тривалість обходу міряють не годинником, а вартістю для пристрою:

```
max_time = ⌈(max_bytes / розмір_сторінки) · 8192 / wb->avg_write_bandwidth⌉
slots    = min(⌈max_time / 1024⌉, 5)
```

Одна тонкість, на якій легко спіткнутися, читаючи джерело: коментар біля константи каже «if foreign slots >= 8, switch», а сама умова записана як `hweight16(history) > WB_FRN_HIST_THR_SLOTS`, тобто **строго більш ніж 8** установлених бітів. Щоб власність перейшла, чужій групі потрібні дев'ять комірок із шістнадцяти, а не вісім.

## Поверхня спостереження

**Група пам'яті — `memory.stat`**, значення в байтах:

| Поле | Що показує |
|---|---|
| `file_dirty` | брудні сторінки кешу, ще не записані |
| `file_writeback` | сторінки, що просто зараз ідуть на пристрій |

**Група вводу-виводу — `io.stat`**, рядок на пристрій `<maj>:<min>` із полями `rbytes`, `wbytes`, `rios`, `wios`, `dbytes`, `dios`. Головна перевірка контракту саме тут: `wbytes` мусить рости в **тій** групі, що бруднила сторінки. Росте лише в кореневій — котрийсь із трьох обов'язків не виконано.

Побачити це можна кількома командами від кореня ієрархії:

```sh
echo "+memory +io" > /sys/fs/cgroup/cgroup.subtree_control
mkdir /sys/fs/cgroup/probe && echo $$ > /sys/fs/cgroup/probe/cgroup.procs
dd if=/dev/zero of=/mnt/data/probe bs=1M count=512   # ФС мусить бути з підтримкою
sync
cat /sys/fs/cgroup/probe/io.stat                     # wbytes тут ≈ 512 МіБ
```

**Ручки в `/proc/sys/vm/`** ([sysctl](topic:sys-unix/sysctl-tunables)):

| Ручка | Типове | Дія на групу |
|---|---|---|
| `vm.dirty_ratio` | 20 | той самий відсоток, але від пам'яті, доступної групі |
| `vm.dirty_background_ratio` | 10 | те саме для порогу фонового запису |
| `vm.dirty_bytes`, `vm.dirty_background_bytes` | 0 | абсолютні; для групи перераховуються назад у частку |
| `vm.dirty_expire_centisecs` | 3000 | вік брудної сторінки, після якого її беруть — 30 с |
| `vm.dirty_writeback_centisecs` | 500 | період пробудження потоків — 5 с |

**Пристрій — [debugfs](topic:sys-unix/debugfs-kernel-debug-vfs).** Файл `/sys/kernel/debug/bdi/<maj:min>/stats` дає підсумок по всьому пристрою: `BdiWriteback`, `BdiReclaimable`, `BdiDirtyThresh`, `DirtyThresh`, `BackgroundThresh`, `BdiDirtied`, `BdiWritten` (усе в кБ), `BdiWriteBandwidth` (кБ/с) і довжини черг `b_dirty`, `b_io`, `b_more_io`, `b_dirty_time`.

Значно цікавіший сусідній файл `wb_stats` (з ядра 6.10): він друкує окремий блок **на кожен wb** пристрою, і перший рядок блоку — `WbCgIno`, номер inode-а тієї cgroup-теки:

```
WbCgIno:                 1
WbWriteback:             0 kB
WbReclaimable:           0 kB
WbDirtyThresh:      102400 kB
WbDirtied:          524288 kB
WbWritten:          524288 kB
WbWriteBandwidth:    98304 kBps
```

Це найпряміша відповідь на питання «чи механізм узагалі ввімкнувся»: один-єдиний блок із `WbCgIno: 1` означає, що всі брудні сторінки пристрою обслуговує коренева група. Зіставити номер із текою — `find /sys/fs/cgroup -inum <WbCgIno>`.

**Налаштування пристрою — `/sys/class/bdi/<maj:min>/`**: `read_ahead_kb`, `min_ratio` й `max_ratio` (та їхні точніші відповідники `min_ratio_fine` і `max_ratio_fine`), `min_bytes`, `max_bytes`, `stable_pages_required`, `strict_limit`.

## Від симптому до порушеної умови

Механізм ніколи не повідомляє про свою відмову — він просто вироджується. Тому діагностика йде від показань лічильників назад до умови:

| Що видно | Яка умова не виконана | Куди дивитися |
|---|---|---|
| `wb_stats` показує єдиний блок `WbCgIno: 1` | будь-яка з чотирьох | пройти таблицю умов згори вниз |
| `memory.stat` рахує `file_dirty`, а `io.stat` групи порожній | ФС не оголосила `SB_I_CGROUPWB` | тип ФС і опції монтування (`data=journal` в ext4) |
| `io.stat` групи росте на читаннях, але не на записах | ФС не робить `wbc_init_bio()` | код `->writepages()` цієї ФС |
| облік «липне» до групи, яка вже не пише | у файл пише кілька груп водночас | одна група — один дописувач на файл |
| `wbytes` менший за обсяг запису на порядок | метадані й журнал не підлягають обліку по групах | навантаження з безлічі дрібних файлів |
| файлів `memory.stat` і `io.stat` немає | ієрархія перша, а не друга | `/proc/mounts`, `systemd.unified_cgroup_hierarchy` |
