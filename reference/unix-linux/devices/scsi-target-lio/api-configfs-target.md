# 📋 Довідка: дерево /sys/kernel/config/target — гілка сховища й гілка фабрики

Уся конфігурація цілі LIO — це каталоги, текстові файли й символьні посилання під `/sys/kernel/config/target`; іншого сховища налаштувань у ядра немає. Нижче — точна розкладка обох гілок дерева: імена атрибутів і одиниці їхніх значень, параметри кожного backstore, відповідність команд `targetcli` каталогам і — найважливіше для практики — де проходить межа між тим, що фіксується назавжди, і тим, що крутять під працюючим ініціатором.

Імена й поведінку звірено з деревом ядра v6.12 (`drivers/target/`); там, де файл раніше був, а тепер його немає, це сказано окремо.

## Верхівка: дві гілки, які зустрічаються посиланням

```
/sys/kernel/config/target/
├─ version                    ro — версія ядра цілі й ядра системи
├─ dbroot                     rw — де лежать метадані APTPL і ALUA, типово /var/target
├─ core/                      ЩО віддаємо: пристрої
│  ├─ alua/lu_gps/default_lu_gp/
│  └─ <плагін>_<число>/       ← mkdir
└─ iscsi/ loopback/ vhost/ qla2xxx/ srpt/ sbp/ xen-pvscsi/      ЯК віддаємо
```

Тека фабрики з'являється сама, щойно завантажено її модуль, і зникає з його вивантаженням; створити її `mkdir` не можна. Гілки `core/` і фабрики не знають одна про одну — єдиний місток між ними, символьне посилання з `lun/`, з'являється аж наприкінці налаштування. Загальну механіку — чому тут `mkdir` не заводить каталог, а породжує в ядрі об'єкт, — описує [configfs](book:unix-linux/configfs).

## Гілка core: пристрій, якого ще немає

`mkdir core/iblock_0` не створює пристрій. Він створює **HBA** — контейнер, і його ім'я ядро розбирає буквально: рядок до останнього підкреслення береться як ім'я плагіна, залишок — як число (окремими випадками прописано `rd_mcp` і `rd_direct`, де підкреслення входить у саму назву). Число довільне, воно лише мусить різнити контейнери; жодного змісту, крім унікальності, у ньому немає. Пристрій — це вже `mkdir` усередині.

```
core/iblock_0/                ← mkdir: контейнер HBA
└─ disk1/                     ← mkdir: сам пристрій
   ├─ control      w   параметри плагіна: "ключ=значення,ключ=значення"
   ├─ enable       rw  1 — зібрати пристрій; читання показує 0/1
   ├─ info         ro  рядок стану від плагіна
   ├─ udev_path    rw  довідковий шлях до носія
   ├─ alias        rw  довільний рядок, звідки береться модель у INQUIRY
   ├─ alua_lu_gp   rw  ім'я групи LU з core/alua/lu_gps/
   ├─ lba_map      rw  карта діапазонів для ALUA-стану lba_dependent
   ├─ attrib/      геометрія й поведінка емуляції
   ├─ wwn/         ким пристрій себе називає
   ├─ pr/          ro  знімок постійних резервацій
   ├─ alua/default_tg_pt_gp/
   └─ statistics/  ro  лічильники
```

### Що приймає `control` у кожного плагіна

| Плагін | Токени | Нотатки |
|---|---|---|
| `iblock` | `udev_path=`, `readonly=`, `force=` | `force=` розбирається, але нічого не робить — код обробника порожній |
| `fileio` | `fd_dev_name=`, `fd_dev_size=`, `fd_buffered_io=`, `fd_async_io=` | `fd_dev_size` у байтах і потрібен лише для звичайного файлу; обидва прапорці приймають одиницю |
| `rd_mcp` | `rd_pages=`, `rd_nullio=`, `rd_dummy=` | `rd_pages` — кількість сторінок; `rd_nullio=1` завершує команди, не торкаючись пам'яті |
| `pscsi` | `scsi_host_id=`, `scsi_channel_id=`, `scsi_target_id=`, `scsi_lun_id=` | адреса H:C:T:L справжнього пристрою в цій машині |
| `user` | `dev_config=`, `dev_size=`, `hw_block_size=`, `hw_max_sectors=`, `nl_reply_supported=`, `max_data_area_mb=`, `data_pages_per_blk=`, `cmd_ring_size_mb=` | `dev_config` — рядок, який ядро не тлумачить, а передає демонові |

Один токен варто виділити. `fd_buffered_io=1` — це не оптимізація, а зміна гарантії: без нього fileio відкриває файл із `O_DSYNC`, з ним записи осідають у сторінковому кеші цілі. Саме тому цей прапорець нерозривно пов'язаний з `attrib/emulate_write_cache`: оголосити «кешу немає», склавши записи в кеш, означає збрехати ініціаторові про довговічність. Різницю між двома режимами розбирає [буферизований і прямий ввід-вивід](book:unix-linux/buffered-and-direct-io) — байти або лежать у чужій оперативці до скидання, або вже на носії, коли повернувся системний виклик.

Плагін `user` (TCMU) додає до `attrib/` власні файли: `cmd_time_out`, `qfull_time_out`, `dev_config`, `dev_size`, `emulate_write_cache`, `tmr_notification`, `nl_reply_supported`, а на читання — `max_data_area_mb`, `data_pages_per_blk`, `cmd_ring_size_mb`; окремо стоять дії `block_dev`, `reset_ring` і `free_kept_buf` — запис у них не запам'ятовується, а негайно щось робить із кільцем команд.

### attrib/ — файл, зміст, коли можна міняти

| Файл | Що означає | Коли приймає запис |
|---|---|---|
| `hw_block_size` | розмір блоку, який дав носій | ro |
| `block_size` | розмір блоку, оголошений у `READ CAPACITY`: 512, 1024, 2048, 4096 | доки `export_count` = 0 |
| `hw_max_sectors` | стеля передачі від носія | ro |
| `optimal_sectors` | «зручна» довжина передачі у Block Limits | доки `export_count` = 0, не більше за `hw_max_sectors` |
| `hw_queue_depth` | глибина черги носія | ro |
| `queue_depth` | скільки команд ціль тримає в польоті | доки `export_count` = 0 |
| `emulate_write_cache` | біт WCE у `MODE SENSE` | на ходу; хост побачить після `rescan` — **на iblock запис `1` відмовляється завжди** |
| `emulate_fua_write`, `emulate_dpo` | чи приймаються біти FUA і DPO в CDB | на ходу |
| `emulate_tpu`, `emulate_tpws` | підтримка `UNMAP` і `WRITE SAME` зі звільненням | доки `export_count` = 0 |
| `max_unmap_lba_count`, `max_unmap_block_desc_count` | стелі однієї команди `UNMAP` | на ходу |
| `unmap_granularity`, `unmap_granularity_alignment` | крок і зсув, якими носій звільняє місце | на ходу |
| `unmap_zeroes_data` | чи читається звільнене як нулі | доки `export_count` = 0 |
| `max_write_same_len` | стеля `WRITE SAME` у блоках | на ходу |
| `emulate_model_alias` | брати модель у INQUIRY з файла `alias` | доки `export_count` = 0 |
| `pi_prot_type`, `pi_prot_format`, `pi_prot_verify` | тип захисту T10 і форматування захисних байтів | доки `export_count` = 0 і пристрій уже зібрано |
| `hw_pi_prot_type` | що вміє носій | ro |
| `emulate_caw`, `emulate_3pc`, `emulate_rsoc` | `COMPARE AND WRITE`, копіювання третьою стороною, `REPORT SUPPORTED OPERATION CODES` | на ходу |
| `emulate_pr`, `force_pr_aptpl`, `enforce_pr_isids` | постійні резервації: чи вмикати, чи зберігати на диск, чи звіряти ISID | на ходу |
| `emulate_tas`, `emulate_ua_intlck_ctrl`, `emulate_rest_reord` | поведінка при перериванні задач, unit attention і переупорядкуванні | на ходу |
| `is_nonrot` | «я не крутиться» — хост вимикає планувальник обертання | на ходу |
| `alua_support`, `pgr_support` | чи бере фабрика на себе ALUA й резервації | залежить від фабрики |
| `submit_type` | як команда потрапляє в backstore | на ходу |

Файла `max_sectors` у сучасних ядрах немає — його прибрали ще до 4.9, і настанови, які радять у нього писати, застаріли на десятиліття. Стеля читається з `hw_max_sectors`, а підказка ініціаторові дається через `optimal_sectors`.

Тонкі теми `emulate_tpu`/`emulate_tpws` мають ціну далі по ланцюжку: ввімкнений `UNMAP` означає, що файлова система гостя зможе повернути місце вниз, аж до справжнього `discard` на носії — про механіку цього повернення й про те, чому воно не безкоштовне, є [discard і TRIM](book:unix-linux/discard-and-trim). Так само `pi_prot_type` вмикає додаткові байти на сектор і наскрізну перевірку контрольної суми — [профіль цілісності блокового шару](book:unix-linux/block-integrity-profile) пояснює, звідки ці байти беруться й хто їх рахує.

### wwn/ — ким пристрій себе називає

| Файл | Куди їде | Нотатка |
|---|---|---|
| `vendor_id`, `product_id`, `revision` | поля стандартної відповіді `INQUIRY` | усталено `LIO-ORG` і назва плагіна |
| `company_id` | префікс OUI для NAA-ідентифікатора | шість шістнадцяткових цифр |
| `vpd_unit_serial` | серійний номер на сторінці 0x80 і в дескрипторах 0x83 | генерується з випадкового UUID при створенні |
| `vpd_protocol_identifier` | ідентифікатор транспорту | |
| `vpd_assoc_logical_unit` | ro — дескриптори, прив'язані до логічного пристрою | сюди дивиться multipath |
| `vpd_assoc_target_port` | ro — дескриптори порту цілі | |
| `vpd_assoc_scsi_target_device` | ro — дескриптори самої цілі | |

Запис у `vpd_unit_serial` відкидається у двох випадках: коли серійний номер прийшов від прошивки справжнього пристрою (`pscsi`), і коли `export_count` уже не нуль. Друга умова точніша, ніж звичне «поки не ввімкнено»: пристрій може бути зібраний і ввімкнений, і серійний номер усе ще міняється — доти, доки на нього не послався жоден LUN.

### pr/ і alua/

Тека `pr/` — суто на читання, це знімок стану: `res_holder`, `res_type`, `res_pr_type`, `res_pr_generation`, `res_pr_holder_tg_port`, `res_pr_registered_i_pts`, `res_pr_all_tgt_pts`, `res_aptpl_active`, `res_aptpl_metadata`. Керують резерваціями не звідси, а командами `PERSISTENT RESERVE IN`/`OUT` від самих ініціаторів; конфігурація лише вмикає механізм (`attrib/emulate_pr`) і вирішує, чи переживає він перезавантаження (`force_pr_aptpl` плюс `dbroot`). Що це за механізм і чому кластерові без нього не обійтися — у [постійних резерваціях SCSI](book:unix-linux/scsi-persistent-reservations): вузол реєструє на LUN ключ, а той, хто вижив, витісняє ключ мовчазного сусіда.

Тека `alua/default_tg_pt_gp/` описує групу портів: `alua_access_state` і `alua_access_status`, `alua_access_type` (неявний, явний чи обидва), сім прапорців `alua_support_*` на кожен оголошуваний стан, `preferred`, `tg_pt_gp_id`, `members`, `alua_write_metadata`, а також затримки `nonop_delay_msecs`, `trans_delay_msecs`, `implicit_trans_secs`. Група LU — простіша: `lu_gp_id` і `members`. Саме ці стани читає з іншого боку [multipath](book:unix-linux/dm-multipath), вирішуючи, який шлях зараз оптимальний.

## Гілка фабрики: iscsi/

```
iscsi/                                        ← після modprobe iscsi_target_mod
├─ discovery_auth/    userid  password  authenticate_target
│                     userid_mutual  password_mutual  enforce_discovery_auth
└─ iqn.2026-08.org.example:store/             ← mkdir: WWN цілі
   └─ tpgt_1/                                 ← mkdir: група портів цілі
      ├─ enable             w 1 — почати відповідати на логіни
      ├─ rtpi               відносний номер порту цілі
      ├─ dynamic_sessions   ro
      ├─ np/0.0.0.0:3260/   ← mkdir: сокет починає слухати негайно
      │     iser  cxgbit    ← перемкнути портал на RDMA чи розвантаження
      ├─ lun/lun_0/         ← mkdir, далі ln -s на core/<плагін>_<N>/<пристрій>
      │     alua_tg_pt_gp  alua_tg_pt_offline
      │     alua_tg_pt_status  alua_tg_pt_write_md
      ├─ acls/iqn.2026-08.org.example:client/  ← mkdir: кому дозволено
      │  ├─ cmdsn_depth  info  tag
      │  └─ lun_0/        ← mkdir, далі ln -s на ../../../lun/lun_0
      │        write_protect
      ├─ attrib/            політика цієї групи портів
      ├─ param/             стартові значення ключів логіну iSCSI
      └─ auth/              CHAP для цієї групи
```

Дві речі тут ламають очікування. Перша: **ім'я символьного посилання не має значення** — ядро дивиться лише на те, куди воно вказує. `rtslib` кладе туди випадковий десятизначний огризок UUID; у прикладах пишуть `store` або `virtual_scsi_port` — усі три однаково правильні.

Друга: номерів LUN тут два, і бачить ініціатор не той, що в `tpgt_1/lun/`. Тека `lun/lun_N` — це LUN самої групи портів, а `acls/<IQN>/lun_M` — **зіставлений** LUN, і саме `M` приїде в `REPORT LUNS` цьому ініціаторові. Один і той самий пристрій можна віддати одній машині як LUN 0, а другій — як LUN 3, і кожна вважатиме свій номер єдиним. Тому кроків на LUN завжди три: `mkdir` у `lun/`, посилання на пристрій, а потім ще один `mkdir` із посиланням усередині `acls/`.

### attrib/ групи портів

| Файл | Що вирішує |
|---|---|
| `authentication` | чи вимагати CHAP на звичайному логіні |
| `generate_node_acls` | 1 — пускати будь-якого ініціатора, створюючи ACL на льоту (демо-режим) |
| `cache_dynamic_acls` | чи лишати такий ACL після виходу сеансу |
| `demo_mode_write_protect` | у демо-режимі усталено 1: пускає, але лише на читання |
| `prod_mode_write_protect` | те саме для явно заведених ACL |
| `demo_mode_discovery` | чи віддавати `SendTargets` тому, хто не має ACL |
| `default_cmdsn_depth` | глибина черги нового сеансу |
| `login_timeout` | секунди на завершення логіну |
| `default_erl` | рівень відновлення після помилок, 0–2 |
| `t10_pi` | чи пропонувати захист T10 у цій групі |
| `fabric_prot_type` | захист, який фабрика робить сама, без носія |
| `tpg_enabled_sendtargets` | чи показувати вимкнені групи в `SendTargets` |
| `login_keys_workaround` | поблажливість до ініціаторів, що порушують RFC |

Пара `generate_node_acls` і `demo_mode_write_protect` — найчастіше джерело здивування: ціль, зібрана «щоб просто спробувати», пускає всіх, але віддає диск на читання, і запис падає з відмовою, хоча дозвіл ніби є.

### param/ і auth/

У `param/` лежать стартові значення ключів, які ціль пропонує на логіні: `AuthMethod`, `HeaderDigest`, `DataDigest`, `MaxConnections`, `TargetAlias`, `InitialR2T`, `ImmediateData`, `MaxRecvDataSegmentLength`, `MaxXmitDataSegmentLength`, `MaxBurstLength`, `FirstBurstLength`, `DefaultTime2Wait`, `DefaultTime2Retain`, `MaxOutstandingR2T`, `DataPDUInOrder`, `DataSequenceInOrder`, `ErrorRecoveryLevel`, `IFMarker`, `OFMarker`, `IFMarkInt`, `OFMarkInt`. Це не налаштування з'єднання, а **позиція в перемовинах**: остаточне значення виходить із зустрічної пропозиції ініціатора, і змінене число діє лише на сеанси, що заходять після правки. Як саме домовляються два боки, розбирає [iSCSI у Linux](book:unix-linux/iscsi-in-linux).

`auth/` містить `userid`, `password`, `userid_mutual`, `password_mutual` і `authenticate_target` — CHAP для звичайного логіну; така сама п'ятірка з додатковим `enforce_discovery_auth` лежить у `discovery_auth/` і стосується етапу пошуку цілей. Ті самі файли є і всередині кожного ACL — тоді пароль свій на кожного ініціатора.

## Мінімальна послідовність і зворотний порядок

Найкоротший повний шлях від порожнього дерева до диска, який видно ініціаторові, — вісім команд; зверніть увагу на потрійний крок для LUN.

```sh
T=/sys/kernel/config/target
IQN=iqn.2026-08.org.example:store
CLI=iqn.2026-08.org.example:client

mkdir -p $T/core/fileio_0/disk1
echo "fd_dev_name=/srv/disk1.img,fd_dev_size=1073741824" > $T/core/fileio_0/disk1/control
echo 1 > $T/core/fileio_0/disk1/enable

mkdir -p $T/iscsi/$IQN/tpgt_1/np/0.0.0.0:3260
cd $T/iscsi/$IQN/tpgt_1

mkdir lun/lun_0 &&        ln -s $T/core/fileio_0/disk1 lun/lun_0/backing
mkdir -p acls/$CLI/lun_0 && ln -s $PWD/lun/lun_0      acls/$CLI/lun_0/mapped
echo 1 > enable
```

Розбирають це рівно у зворотному порядку, і порядок тут не ввічливість, а вимога ядра: `rmdir` пристрою відмовить, доки `export_count` більший за нуль, тобто доки на нього дивиться бодай одне посилання. Спершу `echo 0 > enable` на групі портів — сеанси розриваються, нові логіни не приймаються. Далі знімаються посилання й теки в порядку, зворотному до створення: спочатку зіставлений LUN усередині ACL, потім сам ACL, потім LUN групи портів, портал, група, ціль. І аж наостанок `rmdir` пристрою й контейнера HBA — тепер, коли на пристрій ніхто не посилається, він звільняється.

Порушений порядок дає не аварію, а `EBUSY` чи `EINVAL` на `rmdir`, і зазвичай означає забуте посилання в чиємусь ACL. Точну причину відмови ядро пише в журнал — саме там, а не у відповіді оболонки, лежить пояснення.

## targetcli й що воно робить у дереві

| Команда `targetcli` | Дії в configfs |
|---|---|
| `/backstores/fileio create disk1 /srv/disk1.img 1G` | `mkdir core/fileio_0/disk1`, запис `fd_dev_name=…,fd_dev_size=…` у `control`, `1` у `enable` |
| `/backstores/block create disk2 /dev/sdb` | те саме в `core/iblock_0/disk2` з `udev_path=/dev/sdb` |
| `… set attribute emulate_write_cache=1` | `echo 1 > attrib/emulate_write_cache` |
| `… set wwn vpd_unit_serial=…` | запис у `wwn/vpd_unit_serial` |
| `/iscsi create iqn.2026-08.org.example:store` | `mkdir iscsi/<IQN>/tpgt_1` і портал `np/0.0.0.0:3260` заразом |
| `…/tpg1/luns create /backstores/fileio/disk1` | `mkdir lun/lun_0` плюс посилання на пристрій, і дзеркалення в усі наявні ACL |
| `…/tpg1/acls create iqn…:client` | `mkdir acls/<IQN>` і по `lun_N` із посиланням на кожен LUN групи |
| `…/tpg1 set attribute authentication=1` | `echo 1 > attrib/authentication` |
| `…/tpg1 set auth userid=u password=p` | запис у `auth/userid` і `auth/password` |
| `…/tpg1 enable` | `echo 1 > enable` |
| `saveconfig` | обхід усього дерева й запис `/etc/target/saveconfig.json` |

Останній рядок пояснює всю конструкцію керування. `targetcli` — не демон і не служба: він щоразу читає стан із ядра, робить свої `mkdir` і виходить. Конфігурація живе в ядрі, а `saveconfig.json` — лише її злі́пок, який `target.service` програє наново після перезавантаження. Тому редагувати цей JSON під працюючою ціллю марно, а різниця між «зберіг» і «не зберіг» видно лише після перезавантаження.

## Три яруси незмінності

Усе, що вище, укладається в одне правило з трьома ярусами.

До запису `1` в `enable` фіксуються параметри плагіна в `control`: шлях до носія, розмір, режим вводу-виводу. Далі — доки `export_count` дорівнює нулю, тобто доки на пристрій не послався жоден LUN, — міняється все, що потрапляє у відповіді на `INQUIRY` і `READ CAPACITY`: `block_size`, вміст `wwn/`, `alias` з `emulate_model_alias`, `optimal_sectors`, `queue_depth`, тонке виділення й тип захисту T10. На ходу лишається решта: біт кешу `emulate_write_cache` (хост перечитає його при `rescan`), поведінкові прапорці, стелі `UNMAP`, стан ALUA, а в гілці фабрики — `attrib/`, `param/` і `acls/`, де правка діє на нові сеанси.

Межа проходить саме по `export_count`, а не по `enable`, і причина не в реалізації, а в протоколі. Щойно LUN виставлено, ініціатор міг прочитати геометрію й побудувати на ній файлову систему. Забрати сказане ціль не може: у SCSI є unit attention, яким повідомляють про змінену ємність чи витіснену резервацію, але немає способу сказати «я передумала щодо розміру блоку». Тому ядро не покладається на дисципліну адміністратора, а просто відмовляє в записі.
