# Том 3. Файли й носій

Курс «Unix крок за кроком», том 3 із шести.

**Читач на вході тому.** Знає устрій системи (том 1: ядро й простір користувача,
системний виклик, «усе є файлом») і світ одного процесу (том 2: адресний простір,
`mmap`, таблиця дескрипторів, простори імен). Дескриптор він уже тримав у руках — але
що **за** дескриптором, не бачив жодного разу.

**Читач на виході тому.** Розуміє, що ім'я і вміст — різні речі; уміє прочитати дерево
як зібране з кількох файлових систем, зокрема таких, під якими взагалі немає диска;
знає, коли запис справді на носії, а коли лише обіцяний; спускається під файлову
систему — до блокового пристрою, розділів, шарів device mapper, LVM, RAID і шифрування;
розуміє, чому носій зношується й бреше про власне здоров'я; і **розбирає аварію
сховища за моделлю, а не за рецептом зі StackOverflow**.

**10 розділів · 108 кроків.**
14 наявних кроків курсу (12 із модуля «Файли» + 2 спірні, забрані з інших томів;
серед цих 14 — обидві наявні власні статті) ·
**90 `+ref` у резерв корпусу** (83 написані, 7 `+ref*` — заведені, ще не написані) ·
**1 нова тема в корпус** (`НОВА`) · **3 нові власні статті курсу**.

## Позначки

| позначка | значення |
|---|---|
| `наявна` | крок уже є в курсі (`flat-unix.md`) |
| `+ref <шлях>` | стаття **написана** й лежить у резерві (`pool-unix.md`), курс туди не веде |
| `+ref* <шлях>` | тема **заведена в маніфесті корпусу**, стаття `pending` — адреса є, писати ще треба |
| `кандидат (N)` | тему назвав скаут у `newtopics-unix.md`; N — скільки джерел |
| `НОВА <слуг>` | теми немає ніде; заводимо в названу книгу корпусу |
| `ВЛАСНА` | власна стаття курсу: самодостатній атом такого дати не може |
| `СПІРНА` | межу з іншим томом треба узгодити; суперник і аргумент названі |

Шляхи `ref` подано рівно так, як у `pool-unix.md` і в `guide/unix/manifest.js`:
`unix-linux/...` — це `reference/unix-linux`, а `programming/...`, `algorithms/...`,
`communications/...` — це книги `book/`.

---

# Головне, що знайшов цей прохід

## 1. «Носія під деревом» у корпусі не бракує — бракує доріжки до нього

Попередній прохід записав розділ «Носій» у діри. Це неправда. У резерві лежить
**близько сотні написаних статей** про сховище, у які курс не веде **жодного** кроку:
уся секція `unix-linux/files` (45), уся `unix-linux/proc` (12), сховищна половина
`unix-linux/devices` (`block-device-model`, `disk-partitions`, `loop-device`,
`device-mapper`, `lvm-and-snapshots`, `md-raid`, `dm-crypt`, `luks-format`,
`dm-thin-provisioning`, `dm-integrity`, `dm-verity`, `discard-and-trim`,
`smart-self-monitoring`, `secure-erase-and-sanitize`, `nvme-in-linux`, `libata`,
`scsi-subsystem`, `usb-mass-storage`, `persistent-memory-devices`,
`userspace-block-devices`, `io-schedulers`), блокова частина `unix-linux/io` — і, після
розширення резерву, ще й **`algorithms/data-structures`** (FTL, підсилення запису,
over-provisioning, збирання сміття у флеші, рівні RAID, B-дерево, LSM, дерево Меркла,
COW-структури) та **`communications/coding-theory`** (парність, CRC, Ріда — Соломона,
ECC у флеші й бюджет помилок).

Із 108 кроків тому **90 — це `ref` у резерв**, і 83 з них читач відкриє одразу.

## 2. Перевірка по тілах статей убила вісім із дев'яти моїх «дір»

Перший варіант цього тому називав дев'ять тем, яких «у корпусі немає». Після читання
**тіл** сусідніх статей (а не назв) вижила одна. Це не дрібниця, а метод — тому нижче
поіменно, з доказом:

| що я хотів завести | де воно насправді вже написано |
|---|---|
| Bind-монтування, простір монтування, поширення (shared/slave/private) | **тіло наявного кроку** `files/mount-model`: `--bind`/`--rbind`, прапорці на монтуванні, `CLONE_NEWNS`, чотири типи поширення, `--make-rslave`, поля `shared:`/`master:` у `mountinfo` |
| Опції монтування, `fstab`, монтування за UUID | вставка `files/mount-model/api-mount-syscalls.md` (усі `MS_*`, правила `MS_REMOUNT`, `relatime` як перелічуваний тип) + `boot-init/systemd-generator-architecture` (`fstab` → `.mount`, `nofail`, `x-systemd.automount`, `_netdev`) |
| Стабільні імена носіїв, `blkid`, `wipefs` | `devices/udev-rules` (звідки беруться `/dev/disk/by-uuid/`, `by-label/`, і чому рядок `UUID=` у `fstab` узагалі працює) + `devices/disk-partitions` (`by-partuuid`, чому `sda` роз'їжджається) |
| Кеш диска, FLUSH/FUA, бар'єри | розділ «Другий кеш, про який ядро не знає» в наявному кроці `files/page-cache-durability` + вставка `devices/block-device-model/api-queue-attributes.md` (`write_cache`, `fua`, `hdparm -W`, чому `write through` робить `fsync` брехнею) + `devices/dm-persistent-data` (`REQ_PREFLUSH`, `REQ_FUA`) |
| FTL, підсилення запису, over-provisioning | `algorithms/data-structures/ftl-flash-translation`, `write-amplification`, `over-provisioning`, `flash-garbage-collection` — усі написані |
| `mkfs`, суперблок, групи блоків, таблиця inode | вставка `files/filesystem-families/api-mkfs-and-mount.md` (що фіксується назавжди, що правиться `tune2fs`, що — при монтуванні; чотири родини) + фігура розкладки на носії в тілі самої `filesystem-families-d.md` |
| Атомарна заміна файлу (я вів `+ref*` у `programming/systems/atomic-file-replace`) | вставка `files/page-cache-durability/proj-durable-write.md`: готова функція C/C++ із `openat`/`renameat`, `fsync` каталогу, перевіркою лічильників скидань |
| «Своя ФС на FUSE» (я хотів власну статтю курсу) | вставка `files/fuse-userspace-filesystems/proj-hello-fuse.md` — саме така збірка на `libfuse 3`, з лічильником викликів |
| «Стек шарів: диск → LUKS → LVM → ФС» (власна стаття) | розділ «Чому шари складаються» в `devices/device-mapper` (`slaves`/`holders`, порядок призупинення) + `devices/loop-device` (складання шарів) + `devices/discard-and-trim` (проходження discard крізь dm-crypt, LVM, тонкий пул — з готовою методикою пошуку обриву) |
| «Розмонтувати не виходить» (власна стаття) | тіло `files/mount-model`: `EBUSY` і всі його причини, `lsof +f`, `fuser -m`, `umount -l` та його пастка, `umount -f` і мережеві ФС |

**Вижила одна тема** (копіювання дерева без втрат) — і дві перетворилися на власні
статті курсу, бо матеріал у корпусі є, але **розкиданий по десятку статей** і
збирається лише кумулятивно.

## 3. Порожня секція `storage` більше не потрібна

У `reference/unix-linux` є заведена секція **`storage` «Сховище»** зі `scope`
«блокові пристрої, розділи, RAID, файлові системи на диску» й **нулем тем**. Перший
варіант тому селив туди п'ять нових статей. Після перевірки — **жодної**: усе, під що
її заводили, уже написане в `devices`, `files` і `algorithms/data-structures`.
Секцію варто або закрити, або визнати, що вона дублює `devices` + `files`.

## 4. Каталог цьому томові не дав нічого

Із 384 доданих каталожних тем сховища не стосується жодна: `boards/expansion/microsd-card`
— це SPI-модуль для мікроконтролера, а не носій під Linux. Це нормально: каталог зібрано
під `embedded`.

---

# Частина 1. Розділи

### 1. Ім'я та вміст — 11 кроків

Ім'я не є файлом: каталог — це відображення імен у номери, файл живе, доки на нього
хтось посилається, а шлях — не адреса, а процедура. Наслідки: чому видалений відкритий
файл ще існує, чому `rename` не копіює, чому між перевіркою шляху й дією є щілина.

**Спирається:** том 2 дав дескриптор і `fork`; тут уперше показано, що по той бік
дескриптора — inode, а не ім'я.
**Чому перший:** усі дев'ять наступних розділів — це або те, що лежить в inode, або
те, з чого inode зроблено.

### 2. Атрибути й позначки часу — 8

Решта вмісту inode: що показує `statx`, чому розмір і зайняті блоки — різні числа, які
насправді є часові позначки, які прапорці забороняють запис навіть власникові, хто
дізнається про зміну файлу — і що з усього цього губить звичайне копіювання.

**Спирається:** §1 (inode як об'єкт).
**Межа:** тут — **бік файла**. Хто саме що може зробити — том 5 (див. «Заперечення», п. 1).

### 3. Монтування — 7

Дерево — не одна файлова система, а кілька, зшитих у точках монтування; склад дерева
не лежить на носії, а відтворюється при кожному запуску. Підміна кореня, прийнята
розкладка дерева й місце, де застосунок тримає свої файли.

**Спирається:** §1 (розбір шляху впирається в точку монтування).
**Потребує з тому 2:** крок «Простори імен».
**Найлегший розділ тому — і це правильно:** наявний крок `files/mount-model` разом зі
своїми вставками покриває bind, поширення, простір монтування й `umount`; дописувати
до нього нема чого, треба лише вести.

### 4. Файлові системи без носія — 11

Файлова система — це інтерфейс, а не диск. Файли, породжені ядром (`procfs`, `sysfs`,
`devtmpfs`, `configfs`), що живуть у пам'яті (`tmpfs`), складені з інших ФС
(`overlayfs`), розпаковані з образу, принесені з іншої машини (NFS, SMB) і породжені
звичайною програмою (FUSE — разом із готовою збіркою власної ФС у вставці кроку).

**Спирається:** §3 (усе це треба спершу змонтувати).
**Чому саме тут:** обіцянку «усе є файлом» дано в томі 1 першим кроком. Це розділ,
який її гасить.

### 5. Довговічність запису — 12

Між `write()` і носієм лежить кеш, і в цьому проміжку живе більшість утрачених даних.
Сторінковий кеш, зворотний запис і його гальмування, прямий ввід-вивід, сімейство
`fsync`, розривний запис, журнал, замки й оренда — і те, як ту саму задачу вирішують
застосунок із автозбереженням і база даних.

**Спирається:** §1 (`rename` над іменем), §2, том 2 (сторінки).
**Чому тут, а не в кінці:** це найдорожча помилка читача-практика, і вона не потребує
знання про пристрій. Далі том спускається під ФС уже з готовим питанням «а хто мені
це обіцяв».

### 6. Блочний пристрій — 12

Що під файловою системою: чим блоковий пристрій відрізняється від символьного, сектор
проти блока, черга запитів і планувальники, розділи й вирівнювання, файл у ролі
пристрою (loop), флешка як SCSI-диск, програма в ролі диска (NBD/ublk), NVMe — і носій,
який узагалі не блоковий (постійна пам'ять і DAX).

**Спирається:** §5, том 1 (файл пристрою, старший і молодший номери).
**Самодостатність:** перший крок сам уводить різницю символьний/блоковий, тож розділ
читається навіть якщо томові 1 дісталися не всі кроки про пристрої.

### 7. Здоров'я носія — 13

Носій зношується й бреше. Флеш зсередини, типи комірок, вирівнювання зносу, шар
трансляції, підсилення запису, надлишкова ємність, збирання сміття, бюджет помилок ECC,
`TRIM`, SMART — і звідки в `dmesg` беруться сенс-коди SCSI.

**Спирається:** §6 (є пристрій, у якого можна щось спитати).
**Чому перед розділом про RAID і LVM:** до вміння потрібна причина. Читач, який уже
бачив, як диск помирає, розуміє дзеркало й контрольні суми як **відповідь**. Читач,
якому RAID дали першим, вважає його способом додати місця — і тримає RAID 0 на єдиному
примірнику даних.

### 8. Складені носії — 14

Пристрій, зібраний із пристроїв: device mapper, рівні RAID і математика парності,
програмний масив і його перебудова наживо, логічні томи, знімки й тонкий пул, прозоре
шифрування (dm-crypt, LUKS2, AES-XTS), шифрування на рівні файлів, контрольні суми
й дерево Меркла на блоках.

**Спирається:** §6 (блоковий пристрій), §7 (навіщо це все), §5 (знімок без
заморожування ФС — це знімок після збою).

### 9. Устрій файлової системи — 13

Як ФС лежить на тому, що дав §8, і на яких структурах даних вона стоїть: розкладка
чотирьох родин на носії, розміщення блоків, B-дерева, копіювання при записі,
лог-структурований запис і LSM, контрольні суми, пули ZFS — і найпростіша ФС світу,
FAT на флешці. Завершує том наскрізний розбір одного запису.

**Спирається:** §5 (журнал), §6 (блоки й сектори), §8 (шари під ФС).
**Чому наприкінці:** внутрішня будова має сенс лише тоді, коли вже видно і кеш, і носій.

### 10. Аварії файлової системи — 7

Місце скінчилося (і `df` із `du` не сходяться), квоти, `fsck` і межа його можливостей,
метадані тонкого пулу, диск, що перестав відповідати, бекап як єдина чесна відповідь —
і розбір «ФС не монтується» за моделлю всього тому.

**Спирається:** на весь том. Це його іспит.

---

# Частина 2. Розкладка

## Розділ 1. Ім'я та вміст (11)

| # | крок | звідки |
|---:|---|---|
| 1 | Inode | `наявна` — `unix-linux/files/inode-model` |
| 2 | Каталог як відображення | `наявна` — `unix-linux/files/directory-as-mapping` |
| 3 | Жорсткі й символьні посилання | `наявна` — `unix-linux/files/hard-and-symbolic-links` |
| 4 | Кеш каталогових записів: dentry й негативні записи | `+ref unix-linux/files/dentry-cache` |
| 5 | Розбір шляху | `наявна` — `unix-linux/files/path-resolution` |
| 6 | Обхід каталогу з програми: `readdir`, `getdents64` | `+ref unix-linux/io/readdir-getdents64-directory-traversal` · `кандидат (6)` |
| 7 | Гонка між перевіркою й використанням (TOCTOU) | `+ref* programming/security/toctou-race` |
| 8 | Сімейство `*at`: шлях від дескриптора каталогу | `+ref unix-linux/files/at-family-syscalls` · `кандидат (3)` |
| 9 | `O_TMPFILE`: вміст без жодного імені | `+ref unix-linux/files/o-tmpfile` · `кандидат (3)` |
| 10 | Стійке посилання на файл: `name_to_handle_at` | `+ref unix-linux/files/file-handles` |
| 11 | Ім'я — не файл: наслідки для щоденної роботи | `наявна ВЛАСНА` — `name-is-not-the-file` |

`dentry-cache` стоїть **перед** розбором шляху як «звідки ядро взагалі знає імена»;
розбір шляху відкриває щілину TOCTOU, і `*at` — відповідь на неї. `O_TMPFILE` і
`file-handles` замикають розділ із двох кінців: вміст без імені й посилання, стійкіше
за ім'я.

## Розділ 2. Атрибути й позначки часу (8)

| # | крок | звідки |
|---:|---|---|
| 1 | `statx`: розширений запит атрибутів | `+ref unix-linux/files/statx-extended-stat` |
| 2 | Часові позначки файлів: mtime, ctime, роздільність | `+ref* programming/systems/file-timestamps` |
| 3 | Розріджені файли: діри замість нулів | `+ref unix-linux/files/sparse-files` · `кандидат (1)` |
| 4 | Великі файли: `off_t`, LFS і `_FILE_OFFSET_BITS` | `+ref unix-linux/files/large-file-support` |
| 5 | Прапорці inode: immutable, append-only, `chattr` | `+ref unix-linux/files/inode-flags-chattr` · `кандидат (3)` |
| 6 | Стеження за змінами: inotify і fanotify | `+ref unix-linux/files/inotify-and-fanotify` · `кандидат (1)` |
| 7 | Копії з поділом блоків: reflink і `copy_file_range` | `+ref unix-linux/files/reflink-copies` |
| 8 | Копіювання дерева без втрат: `cp`, `tar`, `rsync` | **`НОВА reference/unix-linux/files/copying-trees-preserving-metadata`** · `кандидат (1)` |

Крок 1 подає `statx` як **вікно в inode**, і саме там читач уперше бачить поля `mode`,
`uid`, `gid` — названі, не розкриті: їх бере том 5.

Крок 8 — єдина тема тому, якої в корпусі немає **ніде** (перевірено грепом по тілах:
`rsync` трапляється один раз у вставці про сон системи, `cp -a` — жодного разу,
`cp --reflink` — лише як приклад у статті про знімки віртуальних машин). Він же —
природний іспит розділу: усе, про що щойно йшлося (жорсткі посилання, розрідженість,
часи, прапорці, xattr, reflink), — це рівно те, що `cp` за замовчуванням губить.

## Розділ 3. Монтування (7)

| # | крок | звідки |
|---:|---|---|
| 1 | VFS | `наявна` — `unix-linux/files/vfs-layer` |
| 2 | Монтування | `наявна` — `unix-linux/files/mount-model` |
| 3 | Генератори systemd: як `fstab` стає юнітами | `+ref unix-linux/boot-init/systemd-generator-architecture` · `СПІРНА` |
| 4 | `chroot` і його межі | `+ref unix-linux/files/chroot` · `кандидат (5)` |
| 5 | `pivot_root`: підміна кореневого монтування | `+ref unix-linux/files/pivot-root` · `кандидат (1)` |
| 6 | Ієрархія файлової системи | `наявна` `СПІРНА` — `unix-linux/packaging/fhs-layout` |
| 7 | Теки застосунку: конфіг, дані, кеш | `+ref* programming/systems/app-data-directories` |

Крок 2 несе більше, ніж каже назва: у його тілі — bind-монтування, чотири типи
поширення, простір монтування, `EBUSY` із `lsof`/`fuser` і пастка `umount -l`, а у
вставці `api-mount-syscalls.md` — усі прапорці (`nosuid`, `noexec`, `relatime`,
правила `MS_REMOUNT`). Тому розділ короткий: додавати нема чого.

**`СПІРНА` (крок 3).** Суперник — том 5 (завантаження й служби). Аргумент за том 3:
читачеві тут потрібна відповідь на питання «якщо монтування не лежить на носії, хто
його відтворює при кожному старті», і `fstab`-генератор — це саме вона; томові 5
лишається решта генераторів і решта systemd. Якщо том 5 наполягає — крок віддається,
і §3 стає шестикроковим.

**`СПІРНА` (крок 6).** Суперник — том 6 (там FHS пояснює, куди пакунок кладе файли).
Аргумент за том 3: розкладка дерева — властивість **дерева**, а половина FHS
(`/proc`, `/sys`, `/dev`, `/run`) — буквально точки монтування з §3–§4; до того ж ці
шляхи вживає кожен том, починаючи з першого.

## Розділ 4. Файлові системи без носія (11)

| # | крок | звідки |
|---:|---|---|
| 1 | Псевдо-ФС | `наявна` — `unix-linux/files/pseudo-filesystems` |
| 2 | Архітектура procfs і `/proc/[pid]` | `+ref unix-linux/proc/procfs-architecture-and-proc-pid` |
| 3 | sysfs, kobject і `sysfs_dirent` | `+ref unix-linux/proc/sysfs-kobject-sysfs-dirent` |
| 4 | kernfs: спільний каркас під procfs, sysfs і cgroupfs | `+ref unix-linux/proc/kernfs-vfs-abstraction-layer` |
| 5 | devtmpfs: вузли пристроїв з'являються самі | `+ref unix-linux/proc/devtmpfs-kernel-device-node-management` |
| 6 | tmpfs і shmem: файли, яких немає на диску | `+ref unix-linux/proc/tmpfs-shmem-ram-filesystem` |
| 7 | configfs: файли, які створюють об'єкти ядра | `+ref unix-linux/proc/configfs-user-space-kernel-object-creation` |
| 8 | Накладені файлові системи: overlayfs і «білило» | `+ref unix-linux/files/overlay-filesystems` · `кандидат (2)` |
| 9 | Стиснені образи лише для читання: SquashFS і EROFS | `+ref unix-linux/files/read-only-image-filesystems` · `кандидат (1)` |
| 10 | Мережеві файлові системи: NFS, SMB і чого від них чекати | `+ref unix-linux/files/network-filesystems` |
| 11 | FUSE: файлова система в просторі користувача | `+ref unix-linux/files/fuse-userspace-filesystems` · `кандидат (7)` |

Розділ ріже впоперек «кафедр»: ядрові псевдо-ФС, накладення, образ, мережа й FUSE —
з погляду підручника п'ять різних тем, а з погляду читача одна: **файли, під якими
немає диска**. Саме ця збірка робить «усе є файлом» механізмом, а не гаслом.

Власної статті тут не буде: крок 11 приносить із собою вставку `proj-hello-fuse.md` —
готову збірку власної файлової системи на `libfuse 3`, з лічильником звернень ядра.
Курсові лишається тільки привести читача до неї.

**Шов із томом 6.** Крок «/proc» у сенсі «вікно в процес» (`ps`, `top`, `/proc/PID/…`)
лишається томові, що вчить дивитися на живу систему. Тут — `procfs` як **файлова
система**: звідки береться текст і чому файл нульового розміру.

## Розділ 5. Довговічність запису (12)

| # | крок | звідки |
|---:|---|---|
| 1 | Кеш сторінок і `fsync` | `наявна` — `unix-linux/files/page-cache-durability` |
| 2 | Випереджувальне читання | `+ref unix-linux/files/readahead` |
| 3 | Гальмування фонового запису | `+ref unix-linux/devices/writeback-throttling` |
| 4 | Буферизований і прямий ввід-вивід | `наявна` `СПІРНА` — `unix-linux/io/buffered-and-direct-io` |
| 5 | Гарантії скидання: `fsync`, `fdatasync`, `sync_file_range` | `+ref unix-linux/io/fsync-fdatasync-sync-file-range` |
| 6 | Розривне читання: чому запис буває наполовину | `+ref* programming/systems/torn-reads` |
| 7 | Журналювання | `наявна` — `unix-linux/files/journaling-consistency` |
| 8 | Документ переживає крах: автозбереження і журнал | `+ref programming/client-architecture/client-crash-recovery` |
| 9 | Блокування файлів: flock, POSIX- і OFD-замки | `+ref unix-linux/files/file-locking` · `кандидат (4)` |
| 10 | Оренда файлу: `F_SETLEASE` | `+ref unix-linux/files/file-leases` |
| 11 | Журнал попереднього запису (WAL) | `+ref programming/databases/write-ahead-log` |
| 12 | Коли запис справді записаний | `наявна ВЛАСНА` — `when-write-is-really-written` |

**Крок 1 несе більше, ніж назва:** у його тілі є розділ «Другий кеш, про який ядро не
знає» (кеш накопичувача, FTL, чому підтвердження запису — не гарантія) і «Помилку чують
один раз» (fsyncgate), а у вставці `proj-durable-write.md` — **готова атомарна заміна
файлу** з `openat`/`renameat`, `fsync` каталогу й перевіркою лічильників скидань. Тому
ні «бар'єрів», ні «атомарної заміни» окремими кроками тут немає: це вже прочитано.

**`СПІРНА` (крок 4).** Суперник — том, що бере розділ «Як чекати на дані» (найімовірніше
том 6). Аргумент за том 3: «буферизований проти прямого» — питання **про сторінковий
кеш і носій**, а не про очікування; без нього §5 має дірку посередині, а розділ про
очікування не втрачає нічого.

**Поправка до скаутів.** «Атомарну заміну файлу» тричі пропонували як `НОВА (писати)`.
Тема не лише заведена (`programming/systems/atomic-file-replace`, `pending`) — вона ще
й **уже написана як вставка** до наявного кроку курсу. Це кандидат на дубль: перш ніж
писати `atomic-file-replace`, варто вирішити, чи він узагалі потрібен.

## Розділ 6. Блочний пристрій (12)

| # | крок | звідки |
|---:|---|---|
| 1 | Символьні та блочні пристрої | `+ref unix-linux/devices/character-and-block-devices` |
| 2 | Блоковий пристрій: сектори, блоки й черга запитів | `+ref unix-linux/devices/block-device-model` · `кандидат (12+3)` |
| 3 | Розділи диска: таблиця, вирівнювання, що бачить ядро | `+ref unix-linux/devices/disk-partitions` · `кандидат (2)` |
| 4 | Loop-пристрій: файл у вигляді блокового пристрою | `+ref unix-linux/devices/loop-device` · `кандидат (2)` |
| 5 | Накопичувачі по USB: mass storage, `usb-storage`, UAS | `+ref unix-linux/devices/usb-mass-storage` |
| 6 | Блоковий пристрій із простору користувача: NBD і ublk | `+ref unix-linux/devices/userspace-block-devices` |
| 7 | Багаточергова підсистема blk-mq | `+ref unix-linux/io/block-layer-mq` |
| 8 | Планувальники блокового вводу-виводу | `+ref unix-linux/devices/io-schedulers` · `кандидат (10)` |
| 9 | Пріоритет вводу-виводу: `ionice`, `ioprio_set` | `+ref unix-linux/io/io-priorities` · `кандидат (2)` |
| 10 | NVMe в Linux: черги й простори імен | `+ref unix-linux/devices/nvme-in-linux` · `кандидат (1)` |
| 11 | Постійна пам'ять як пристрій: NVDIMM і `/dev/pmem` | `+ref unix-linux/devices/persistent-memory-devices` |
| 12 | DAX: файли без сторінкового кешу | `+ref unix-linux/files/dax-direct-access` |

Кроки 4–6 стоять поруч навмисно: файл, що прикидається диском; флешка, що прикидається
SCSI-диском; програма, що прикидається диском. Та сама думка, що в §4 про FUSE, лише
поверхом нижче — читач має побачити симетрію.

Стабільних імен (`/dev/disk/by-uuid`, `by-id`, `blkid`) окремим кроком немає: їх пояснює
крок 3 (`by-partuuid`, чому `sda` роз'їжджається) і наявний крок курсу `devices/udev-rules`
з іншого тому, у тілі якого сказано прямо, що ці теки створюють правила udev, а не ядро.

Кроки 11–12 закривають розділ зустрічним питанням: а якщо носій — це пам'ять? Тоді
зникає і черга, і сторінковий кеш (§5), і сама потреба в блоках.

## Розділ 7. Здоров'я носія (13)

| # | крок | звідки |
|---:|---|---|
| 1 | Flash зсередини: сторінка, блок стирання, читання | `+ref programming/embedded-systems/flash-internals` |
| 2 | SLC, MLC, TLC, QLC: типи комірок і ресурс | `+ref* programming/embedded-systems/flash-cell-types` |
| 3 | Вирівнювання зносу | `+ref programming/embedded-systems/wear-leveling` |
| 4 | Шар трансляції флешу (FTL) | `+ref algorithms/data-structures/ftl-flash-translation` |
| 5 | Підсилення запису (Write Amplification Factor) | `+ref algorithms/data-structures/write-amplification` |
| 6 | Надлишкова ємність (over-provisioning) | `+ref algorithms/data-structures/over-provisioning` |
| 7 | Збирання сміття у флеш-сховищах | `+ref algorithms/data-structures/flash-garbage-collection` |
| 8 | Flash: бюджет помилок ECC і знос | `+ref communications/coding-theory/flash-ecc-budget` |
| 9 | Discard і TRIM | `+ref unix-linux/devices/discard-and-trim` · `кандидат (1)` |
| 10 | SMART: що носій знає про власне здоров'я | `+ref unix-linux/devices/smart-self-monitoring` · `кандидат (1)` |
| 11 | libata: як ATA-диск потрапляє під SCSI-шар | `+ref unix-linux/devices/libata` |
| 12 | Підсистема SCSI: команди, сенс-коди, обробка помилок | `+ref unix-linux/devices/scsi-subsystem` |
| 13 | Надійне стирання: ATA Secure Erase, Sanitize | `+ref unix-linux/devices/secure-erase-and-sanitize` |

Кроки 1–8 — крос-книжні, і це не натяжка: `flash-internals` і `wear-leveling` описують
саму пам'ять, а не мікроконтролер; FTL, підсилення запису, over-provisioning і збирання
сміття лежать у `algorithms/data-structures` як **структури даних усередині
накопичувача**; бюджет ECC — у теорії кодування. Разом вони дають те, чого не дає жоден
Linux-атом: чому SSD сповільнюється, зношується й бреше про власний стан.

Кроки 11–12 стоять тут, а не в §6, свідомо: `libata` і сенс-коди SCSI читач шукає рівно
тоді, коли в `dmesg` з'явився рядок про помилку читання.

## Розділ 8. Складені носії (14)

| # | крок | звідки |
|---:|---|---|
| 1 | Device mapper: пристрій, зібраний із шарів | `+ref unix-linux/devices/device-mapper` · `кандидат (5)` |
| 2 | RAID: смуги, дзеркала й парність | `+ref algorithms/data-structures/raid-levels` |
| 3 | Програмний RAID: md, рівні масиву, відновлення | `+ref unix-linux/devices/md-raid` · `кандидат (2)` |
| 4 | Перебудова масиву наживо: `--grow` і reshape | `+ref unix-linux/devices/md-reshape` |
| 5 | Ріда — Соломона: чому RAID 6 витримує два диски | `+ref communications/coding-theory/reed-solomon` |
| 6 | LVM: логічні томи й миттєві знімки | `+ref unix-linux/devices/lvm-and-snapshots` · `кандидат (2)` |
| 7 | Заморожування ФС: узгоджений момент для знімка | `+ref unix-linux/files/filesystem-freeze` |
| 8 | Тонке виділення: dm-thin, спільний пул, повернення місця | `+ref unix-linux/devices/dm-thin-provisioning` |
| 9 | dm-crypt: прозоре шифрування блокового пристрою | `+ref unix-linux/devices/dm-crypt` · `кандидат (2)` |
| 10 | LUKS2: формат заголовка шифрованого тому | `+ref unix-linux/devices/luks-format` |
| 11 | AES-XTS: чому для дисків саме цей режим | `+ref* programming/security/aes-xts` |
| 12 | fscrypt: шифрування на рівні файлової системи | `+ref unix-linux/files/fscrypt` · `кандидат (1)` |
| 13 | dm-integrity: контрольні суми на записуваному пристрої | `+ref unix-linux/devices/dm-integrity` |
| 14 | dm-verity: пристрій під деревом Меркла | `+ref unix-linux/devices/dm-verity` |

Крок 2 — теорія перед механізмом: смуга, дзеркало й парність як **структура даних**,
перш ніж читач побачить `mdadm`. Крок 7 стоїть одразу після знімків не випадково:
знімок без заморожування ФС — це знімок стану «після збою», який рятує лише тому, що
ФС має журнал (§5).

Власної статті про порядок шарів тут не буде: `device-mapper` пояснює складання шарів
(`slaves`/`holders`, порядок призупинення, чому шарів у житті один-два), `loop-device`
показує типові стеки, а `discard-and-trim` дає готову методику пошуку обриву в стеку —
разом із таблицею, який шар пропускає discard, а який ні.

## Розділ 9. Устрій файлової системи (13)

| # | крок | звідки |
|---:|---|---|
| 1 | Родини файлових систем | `наявна` — `unix-linux/files/filesystem-families` |
| 2 | Розміщення блоків файлу: екстенти, відкладене виділення | `+ref unix-linux/files/file-block-allocation` |
| 3 | B-дерево | `+ref algorithms/data-structures/b-tree` |
| 4 | Btrfs: архітектура B-дерев | `+ref unix-linux/files/btrfs-b-tree-architecture` |
| 5 | Copy-on-write у структурах даних | `+ref algorithms/data-structures/copy-on-write-structures` |
| 6 | Btrfs: копіювання при записі, субтоми, знімки | `+ref unix-linux/files/btrfs-copy-on-write-and-subvolumes` |
| 7 | Btrfs: контрольні суми, scrub і RAID | `+ref unix-linux/files/btrfs-checksums-scrubbing-raid` |
| 8 | B-tree проти LSM-дерева | `+ref algorithms/data-structures/lsm-tree` |
| 9 | Лог-структуровані файлові системи | `+ref unix-linux/files/log-structured-filesystems` |
| 10 | Архітектура пулів ZFS | `+ref unix-linux/files/zfs-pool-architecture` |
| 11 | ZFS у Linux: ARC і ZIL | `+ref unix-linux/files/zfs-on-linux-arc` |
| 12 | Файлова система FAT | `+ref* programming/databases/fat-filesystem` |
| 13 | Один запис наскрізь: від `write()` до сектора | **`ВЛАСНА one-write-end-to-end`** |

Крок 1 несе розкладку всіх чотирьох родин на носії (суперблок, групи блоків, бітові
карти, таблиця inode; групи розподілу XFS; дерева btrfs; сегменти F2FS) — це є в тілі
статті, фігурою й текстом, — а його вставка `api-mkfs-and-mount.md` дає те, що
вирішується один раз назавжди в `mkfs`, і те, що правиться потім. Тому окремого кроку
про суперблок і `mkfs` немає: він був би переказом.

Пари «структура — її втілення» (3–4, 5–6, 8–9) навмисні: спершу структура даних із
книги алгоритмів, одразу за нею — файлова система, що на ній стоїть. Це те, заради
чого варто було підключати `algorithms` до цього курсу.

Крок 12 (FAT) — після btrfs і ZFS: найпростіша ФС світу читається за півгодини, коли
вже видно, чого в ній немає — ні журналу, ні контрольних сум, ні прав.

Крок 13 — **капстоун тому**, і це має бути **вимір, а не переказ**: записати 4 КіБ і
простежити їх лічильниками — брудні сторінки в `/proc/meminfo`, `blktrace` на черзі,
`dmsetup status` на шарах, лічильник записаних гігабайтів у SMART, — з відповіддю, у
якій точці кожен шар міг збрехати про «записано». Жоден атом такого не робить: кожен
чесно описує свій поверх.

## Розділ 10. Аварії файлової системи (7)

| # | крок | звідки |
|---:|---|---|
| 1 | Місце скінчилося: `df` проти `du`, inode і видалений відкритий файл | **`ВЛАСНА disk-space-illusion`** · `кандидат (3)` |
| 2 | Дискові квоти: облік місця за власником | `+ref unix-linux/files/disk-quotas` |
| 3 | `fsck`: перевірка й ремонт файлової системи | `+ref unix-linux/files/fsck-and-repair` · `кандидат (7)` |
| 4 | persistent-data: транзакційні метадані device mapper | `+ref unix-linux/devices/dm-persistent-data` |
| 5 | Таймери транспорту SCSI: коли диск перестав відповідати | `+ref unix-linux/devices/scsi-transport-timeouts` |
| 6 | Бекапи і DR | `+ref programming/operations/disaster-recovery` |
| 7 | ФС не монтується: розбір за моделлю | **`ВЛАСНА filesystem-will-not-mount`** |

**Крок 1 — власна стаття, а не нова тема довідника**, і це зміна проти першого варіанта.
Причина в перевірці по тілах: усі складники вже написані, але **в п'ятьох різних
статтях** — прихований вміст під точкою монтування (🔧-врізка в `mount-model`),
`du` проти видимого розміру (`loop-device`), `st_blocks` і жорсткі посилання (вставка
`proj-walk-directory.md`), вичерпані inode при вільному місці (вставка
`api-mkfs-and-mount.md`), тонкий том, що «займає 900 ГіБ, а `df` показує 80»
(`dm-thin-provisioning`). Зібрати це в одну процедуру може лише курс — і лише після
того, як читач пройшов §3, §6 і §9. Це і є визначення власної статті.

**Крок 7** — метод, а не рецепт: від рядка `EXT4-fs error` у `dmesg` через `blkid`,
SMART (§7) і **рятувальне копіювання `ddrescue`** до `fsck -n` на копії й рішення
«ремонтувати чи відновлювати з бекапу». Правило «спершу образ, потім ремонт» уже стоїть
у тілі `fsck-and-repair` (там же `e2image -r` і резервні суперблоки), а от `ddrescue`
з його картою збійних секторів не описаний ніде — і в окрему тему довідника він не
тягне, тож живе тут.

---

# Частина 3. Не лягло нікуди — з адресами

## Віддаю іншим томам

| тема | адреса |
|---|---|
| `unix-linux/files/file-descriptors-and-open-file-table` `[pending]`, `files/file-descriptor`, `open-file-description` | **том 2** — дескриптор і таблиця відкритих файлів; мій §1 на них спирається |
| `unix-linux/processes/namespace-deep-dive` | **том 5** — простори імен цілком |
| `permissions/*` — `permission-bits`, `umask-and-defaults`, `setuid-and-privilege`, `acl-and-xattr`, `capabilities`, `landlock`, `lsm-framework`, `ima-appraisal` | **том 5** — див. «Заперечення», п. 1 |
| `unix-linux/files/fs-verity`, `devices/sed-opal-drives`, `programming/security/encryption-at-rest`, `programming/security/tpm-root-of-trust` | **том 5** — цілісність системного образу й довіра; §8 дає блочний бік |
| `unix-linux/devices/io-cgroup-control`, `memory/cgroup-writeback` | **том 5** — обмеження ресурсів по cgroup |
| `unix-linux/devices/ioctl-interface`, `random-devices`, `device-file-model`, `major-minor-numbers`, `sysfs-device-model`, `udev-rules` | **том 1 або 5** — модель пристроїв; §6.1 самодостатній і на них не чекає |
| `unix-linux/proc/debugfs-tracefs-*`, `psi-pressure-stall-information`, `sysctl-kernel-tuning-interface`, `bpffs-*`, `devices/procfs-process-reflection` | **том 6** — дивитися на живу систему |
| `unix-linux/proc/cgroupfs-v1-v2-*`, `hugetlbfs-and-transparent-hugepages` | **том 2 / том 5** |
| `unix-linux/io/zero-copy`, `posix-aio`, `linux-aio-io-submit`, `io-uring-architecture`, `io-uring-cmd-passthrough`, `blk-iopoll-and-io-polling`, `blk-mq-tag-sets-and-hardware-queues` | **том 6** — асинхронний ввід-вивід |
| `unix-linux/io/stdio-buffering` | **том 4** — оболонка й конвеєр |
| `unix-linux/boot-init/initramfs-and-initrd-architecture`, `dracut-and-mkinitcpio-toolchains`, `tmpfiles-d-runtime-volatile-files`, `service-directories`, решта генераторів systemd | **том 5** — завантаження й служби; §3.5 дає механізм (`pivot_root`), яким initramfs користується |
| `unix-linux/files/virtiofs`, `devices/virtio-*`, `virtualization-and-containers/kvm-and-qemu-architecture`, `programming/operations/vm-snapshot-and-clone`, `live-migration` | **том 5** — віртуалізація |
| `unix-linux/devices/magic-sysrq` | **том 6** — аварійні команди |
| `programming/embedded-systems/bad-block-management`, `flash-filesystem`, `nor-flash-spi-protocol`, `peripherals/microsd`, `spi-flash`, `boards/expansion/microsd-card` | **не цей курс** — матеріал курсу `embedded` |
| `algorithms/data-structures/ecc-memory`, `single-event-upset`, `bit-flips`, `communications/coding-theory/ecc-ram-flash`, `memory-scrubbing`, `secded`, `ldpc` | **том 2** (пам'ять) або поза курсом; §7.8 бере з цієї лінії рівно один крок — бюджет ECC у флеші |

## Лишаю в довіднику — курс туди не веде

- **мережеве й кластерне сховище:** `devices/iscsi-in-linux`, `nvme-over-fabrics*`,
  `nvme-target-kernel-subsystem`, `scsi-target-lio`, `dm-multipath`,
  `nvme-native-multipath-ana`, `scsi-alua`, `scsi-persistent-reservations`,
  `files/cluster-filesystems-gfs2-ocfs2`;
- **зоноване сховище:** `devices/zoned-block-devices`, `dm-zoned`,
  `nvme-zoned-namespaces-zns`, `io/zoned-block-devices-zns`,
  `io/zoned-storage-f2fs-integration`, `files/zonefs`;
- **тонкі налаштування блокового шару:** `io/dm-writecache-and-dm-cache`,
  `devices/scsi-generic-passthrough`, `devices/block-integrity-profile` (T10 DIF/DIX),
  `devices/kernel-crypto-api`, `devices/hwmon`;
- **вузькі ФС:** `files/incfs-incremental-filesystem`, `files/pidfs-filesystem-architecture`,
  `files/erofs-read-only-filesystem`, `files/zfs-native-encryption`,
  `programming/systems/log-structured-storage`, `programming/systems/persistent-storage`;
- **`devices/seq-file-iterator`** — механіка виводу procfs; законний кандидат у §4,
  прибраний як зайва глибина;
- **`algorithms/data-structures/merkle-tree`** — законний кандидат перед §8.14, але
  `dm-verity` пояснює дерево Меркла сам;
- **`algorithms/data-structures/key-value-store`, `bloom-filter`, `cache-oblivious`,
  `rolling-hash`, `non-cryptographic-hash`, `z-order-curve`** — сусіди §9 з книги
  алгоритмів; беру три (B-дерево, COW, LSM), решту лишаю: том про файли, а не про
  структури даних.

## Знищена тема

`reference/unix-linux/permissions/seccomp-syscall-filtering` — назва й вміст побиті
кодуванням. Курс туди не веде й не має вести: тема належить томові 5, і в корпусі є дві
живі статті на те саме — `permissions/seccomp-filtering` і `permissions/seccomp-bpf-filtering`.

## Дублі в корпусі, які я обходив

| дубль | що робив |
|---|---|
| `files/statx-extended-stat` ↔ `files/statx-extended-stat-api` | веду перший |
| `files/device-mapper-dm-crypt` ↔ `devices/device-mapper` + `devices/dm-crypt` + `devices/luks-format` | веду три окремі з `devices` |
| `files/configfs` ↔ `proc/configfs-user-space-kernel-object-creation` | веду другий |
| `files/reflink-copies` ↔ `io/copy-file-range-cross-fs-reflink` ↔ `files/copy-file-range-syscall` | веду `files/reflink-copies` |
| `files/read-only-image-filesystems` ↔ `files/erofs-read-only-filesystem` | веду перший |
| `files/inotify-and-fanotify` ↔ `files/fanotify-fsnotify-permission-events` | веду перший |
| `devices/zoned-block-devices` ↔ `io/zoned-block-devices-zns` | обидва поза курсом |
| `programming/systems/atomic-file-replace` `[pending]` ↔ вставка `files/page-cache-durability/proj-durable-write.md` | не веду в жодну: вставка вже все дає, а `pending`-тему варто перевірити на потребу |
| `algorithms/data-structures/ftl-flash-translation` ↔ `programming/embedded-systems/flash-internals` ↔ `book/electronics/…/nand-flash-controller` | веду перші дві (третьої в резерві цього курсу немає) |
| `permissions/seccomp-filtering` ↔ `seccomp-bpf-filtering` ↔ `seccomp-syscall-filtering` (побита) | не мій том, але в реєстр дублів варто |

---

# Частина 4. Діри — і вирок кожній

Після перевірки по тілах статей у томі лишилося **чотири** місця, де писати доведеться:
одна нова тема довідника й три власні статті курсу. Решту закриває резерв.

## `НОВА` — заводимо в корпус (1)

| тема | адреса | доказ, що діра справжня |
|---|---|---|
| Копіювання дерева без втрат: `cp`, `tar`, `rsync` і що вони гублять | `reference/unix-linux/files/copying-trees-preserving-metadata` | греп по всьому корпусу: `rsync` — одна згадка (у вставці про сон системи), `cp -a` — жодної, `cp --reflink` — один приклад у статті про клони ВМ. Атоми про жорсткі посилання, розрідженість, xattr, часи й reflink є всі; статті про те, що з цього переживає копіювання, немає |

## `ВЛАСНА` — може дати лише курс (3 нові + 2 наявні)

| стаття | розділ | чому атом цього не може |
|---|---|---|
| Ім'я — не файл: наслідки для щоденної роботи | §1 | `наявна`, лишається |
| Коли запис справді записаний | §5 | `наявна`, лишається |
| Один запис наскрізь: від `write()` до сектора | §9.13 | капстоун: сім поверхів в одному вимірі (`/proc/meminfo` → `blktrace` → `dmsetup status` → SMART). Кожен атом чесно описує свій поверх і мовчить про сусідів |
| Місце скінчилося: `df`, `du` і видалений файл, що тримає гігабайти | §10.1 | складники розкидані по п'яти статтях (`mount-model`, `loop-device`, `proj-walk-directory`, `api-mkfs-and-mount`, `dm-thin-provisioning`); процедура збирається лише після §3, §6 і §9 |
| ФС не монтується: розбір за моделлю | §10.7 | метод від `dmesg` через SMART і `ddrescue` до рішення; `fsck-and-repair` дає ремонт, але не шлях до нього, а `ddrescue` не описаний ніде |

## Чого в томі свідомо немає

- **Прав доступу** — том 5 (див. нижче).
- **Мережевого стека** — NFS і SMB узято як джерела дерева (§4.10), не більше.
- **Контейнерів** — §3 дає монтування, простір монтування й `pivot_root`; складання
  з них контейнера — том 5.
- **Інструментів спостереження** — `dmesg`, `lsof`, `blktrace` уживаються в кроках,
  але окремих кроків про них немає: це том 6.

---

# Частина 5. Заперечення й межі

## 1. Права доступу — віддаю тому 5. `СПІРНА`, вирок мій

**Біти прав, `umask`, `setuid`, ACL і користувачі — том 5 «Машина, яку ділять».**

Право доступу — не властивість файла, а **відношення** між файлом і тим, хто до нього
тягнеться. Половина цього відношення (реальний, ефективний і збережений UID, додаткові
групи, capabilities) живе в процесі, і саме вона робить перевірку осмисленою. Поле
`mode` без користувачів — три вісімкові цифри без значення. До того ж наявні кроки
курсу («Користувачі й групи», «Біти прав», «umask», «setuid», власна «Permission denied»)
складаються в **один розділ, який читач проходить одним заходом**; різати його по томах —
рівно та помилка, яку автор виправляв на прикладі мультиметра.

Що том 3 усе-таки бере:

- `statx` (§2.1) показує `mode`, `uid`, `gid` **як поля inode** — названі, не розкриті;
- прапорці `chattr` (§2.5): `immutable` і `append-only` забороняють запис **навіть
  власникові й root** — це властивість об'єкта, а не контроль за особою;
- опції монтування `noexec`, `nosuid`, `nodev`, `ro` (у тілі §3.2) — обмеження **гілки
  дерева**, а не особи;
- `fscrypt` і `dm-crypt` (§8) — криптографія: ключ або є, або ні.

Том 5 отримує від мене готовими inode, точку монтування, xattr як механізм зберігання
(на ньому стоять і ACL, і мітки SELinux), прапорці inode й розуміння, що ім'я — не файл
(інакше `chmod` по симпосиланню й гонки TOCTOU не пояснити).

## 2. Назва тому — згоден

«Файли й носій» — точна. Дві частини, обидві справді в томі, жодної обіцянки понад
вміст. Слово «носій» несе вагу: воно **дозволяє** другу половину тому, якої курс досі
не мав, і водночас чесно каже, що це не «сховище взагалі» (без SAN, кластерів і хмар).
Варіант «Файли: ім'я, вміст і носій» був би гірший удвічі — двокрапка з поясненням
і перелік.

Ділити том на «Файли» й «Носій» я **не** пропоную: половини безглузді нарізно (журнал
без кешу диска, TRIM без ФС, знімок без заморожування), а спуск під дерево — це і є
одна думка тому.

## 3. Порядок: здоров'я носія — перед RAID і LVM

Найнеочевидніше рішення тому. Інстинкт каже «шари, потім залізо»; я ставлю навпаки.
Причина — «до вміння потрібна причина». Читач, який спершу побачив підсилення запису,
вичерпаний ресурс і сенс-код у `dmesg`, розуміє дзеркало, контрольні суми й знімки як
**відповідь**. Читач, якому RAID дали першим, вважає його способом додати місця.

## 4. Простори монтування — механізм мій, застосування чуже

Механізм (bind, `MS_MOVE`, shared/slave/private, `unshare -m`, `mountinfo`) уже лежить
у тілі наявного кроку `files/mount-model` — тобто дістається томові 3 задарма.
Контейнер як **композиція** просторів імен, cgroups і відображення UID — том 5.
Залежність: крок §3.2 вимагає кроку «Простори імен» із тому 2; якщо той переїде в том 5,
ланцюг рветься.

## 5. Скаути помилилися тричі — виправляю

- «Атомарна заміна файлу» як `НОВА (писати)` (3 джерела) — тема і заведена
  (`programming/systems/atomic-file-replace`, `pending`), і **вже написана** як вставка
  `proj-durable-write.md` до наявного кроку курсу. Не веду нікуди; кандидат на дубль.
- «Місце скінчилося» пропонувалося трьома різними слугами
  (`disk-space-triage`, `disk-full-diagnosis`, `disk-space-illusion`) — це одна тема,
  і вона власна стаття курсу, а не тема довідника.
- «Носій під файловою системою» як діра (12 джерел!) — не діра. Усе написано; курс
  просто не веде. Одинадцять кроків §6 і чотирнадцять §8 — це `ref` у резерв.

## 6. Що я вимагаю від сусідніх томів

| потрібно з | що саме | якщо цього не буде |
|---|---|---|
| том 1 | «Усе є файлом», системний виклик, `errno` | §1 доведеться починати з пояснення `−1` і `ENOENT` |
| том 2 | Дескриптор, опис відкритого файлу, `fork` і успадкування | падає §1 (видалений відкритий файл) і §10.1 |
| том 2 | «Простори імен» | падає половина §3.2 |
| том 1 або 5 | Файл пристрою, старший і молодший номери, udev | §6 виживе (крок 6.1 самодостатній), але стабільні імена доведеться пояснювати самому |

## 7. Одна межа, яку лишаю відкритою

`unix-linux/io/buffered-and-direct-io` (§5.4) — наявний крок курсу з розділу про
ввід-вивід. Забираю його, але не наполягаю: якщо том, що бере «Як чекати на дані»,
покаже, що без нього рветься його ланцюг, крок лишається там, а §5 закриває дірку
абзацом усередині власної статті «Коли запис справді записаний». Це єдина справді
двозначна межа тому; межа з правами (п. 1) двозначною не є.
