# 📋 Керування блокуванням: опції, параметри, файл, причини

Блокування вмикають у трьох різних місцях — у конфігурації збірки, у командному рядку завантаження і в одному файлі securityfs, — а бачать його роботу в єдиному рядку журналу ядра. Тут ця поверхня зібрана повністю: кожен перемикач, формат читання й запису файла, повний перелік причин відмови з тими самими рядками, які ядро друкує, і підпис, яким код ядра ставить питання. Усе за основним деревом ядра; імена й числа з випусками змінюються, тож зверятися варто з деревом своєї версії.

## Опції збирання

Усі вони живуть у `security/lockdown/Kconfig` — тобто задаються там само, де й решта [конфігурації ядра](book:unix-linux/kernel-config-and-build) (система Kconfig, файл `.config`, символи `CONFIG_*`).

| Символ | Що робить |
|---|---|
| `CONFIG_SECURITY_LOCKDOWN_LSM` | збирає сам модуль. `depends on SECURITY`, `select MODULE_SIG if MODULES` — тобто вмикає підпис модулів за собою |
| `CONFIG_LOCK_DOWN_KERNEL_FORCE_NONE` | типово: ядро стартує на рівні `none` |
| `CONFIG_LOCK_DOWN_KERNEL_FORCE_INTEGRITY` | ядро стартує вже на `integrity` |
| `CONFIG_LOCK_DOWN_KERNEL_FORCE_CONFIDENTIALITY` | ядро стартує вже на `confidentiality` |
| `CONFIG_SECURITY_LOCKDOWN_LSM_EARLY` | піднімає модуль до розбору параметрів завантаження |

Три `FORCE_*` зібрані в `choice`, отже, чинний рівно один. «Зашитий» рівень не є чимось окремим від решти: під час ініціалізації модуль просто сам себе замикає звичайним викликом — `lock_kernel_down("Kernel configuration", LOCKDOWN_INTEGRITY_MAX)`. Тому джерело рівня видно в журналі так само, як і для двох інших способів.

Окремої уваги вартий `_EARLY`. Модуль безпеки зазвичай стає до роботи разом з рештою [каркаса LSM](book:unix-linux/lsm-framework) (гачки, які ядро питає перед операцією), а це вже після того, як розібрано командний рядок. Але частину параметрів завантаження обробники самі перевіряють через блокування — і якщо модуля ще немає, перевірка мовчки проходить. `_EARLY` кладе структуру модуля в окрему секцію `.early_lsm_info.init` (макрос `DEFINE_EARLY_LSM` замість `DEFINE_LSM`), а її ядро обробляє в `early_security_init()` — виклику, що стоїть у `start_kernel()` **до** `parse_early_param()`. Наслідок подвійний: гачки живі вже під час розбору параметрів, і блокування ініціалізується беззастережно, раніше за всі інші модулі безпеки й незалежно від упорядкованого списку.

## Параметри завантаження

Рівень задають у [командному рядку ядра](book:unix-linux/bootloader-and-cmdline) — рядку, що його завантажувач передає ядру при старті.

```
lockdown=integrity
lockdown=confidentiality
```

Це `early_param`, і розпізнає він рівно ці два слова, порівнюючи їх через `strcmp()`. Будь-що інше — `lockdown=on`, `lockdown=1`, `lockdown=integrity ` з пробілом — дає `-EINVAL`: ядро пише в журнал скаргу на неправильний ранній параметр і завантажується **без блокування**. Мовчазного схилення в безпечніший бік тут немає, тому рядок варто перевіряти в `/proc/cmdline`, а не покладатися на намір.

Другий параметр — `lsm=`. Він перелічує через кому модулі безпеки в порядку ініціалізації й повністю заміщає список із `CONFIG_LSM` (де `lockdown` типово стоїть другим, одразу після `landlock`). Отже, власний `lsm=`, у якому `lockdown` забули, вимикає блокування цілком — крім випадку `_EARLY`, коли модуль піднімають окремим шляхом, і список на нього не впливає.

Найдешевша перевірка «а чи воно взагалі є» — наявність файла: без зібраного або не включеного в список модуля `/sys/kernel/security/lockdown` не з'являється зовсім.

| Хто підняв рівень | Рядок у журналі |
|---|---|
| опція збирання `FORCE_*` | `Kernel is locked down from Kernel configuration; …` |
| параметр `lockdown=` | `Kernel is locked down from command line; …` |
| запис у securityfs | `Kernel is locked down from securityfs; …` |

Якщо задано кілька, виграє найвищий, у якому б порядку їх не застосували: кожна спроба проходить через ту саму перевірку «тільки вгору», і нижча просто не спрацьовує.

## Файл /sys/kernel/security/lockdown

Файл створюють у securityfs — [псевдофайловій системі](book:unix-linux/pseudo-filesystems), яка не має даних на диску, а показує стан ядра як файли; змонтована вона в `/sys/kernel/security` (це робить systemd, вручну — `mount -t securityfs none /sys/kernel/security`). Режим файла `0644`: читає будь-хто, пише лише root.

Читання показує всі три рівні одним рядком, а чинний бере в квадратні дужки:

```
# cat /sys/kernel/security/lockdown
[none] integrity confidentiality

# echo integrity > /sys/kernel/security/lockdown
# cat /sys/kernel/security/lockdown
none [integrity] confidentiality
```

Записувати треба точну назву рівня — ту саму, що видно при читанні; кінцевий перевід рядка ядро зрізає саме́, тож звичайний `echo` годиться.

| Що записали | Що повернеться |
|---|---|
| `integrity` чи `confidentiality`, вище за чинний | успіх, `write()` повертає кількість записаних байтів |
| той самий рівень, що вже стоїть | `-EPERM` — перевірка «тільки вгору» строга, повторний запис теж не проходить |
| `none` або нижчий рівень | `-EPERM` |
| будь-що інше | `-EINVAL` |

```
# echo none > /sys/kernel/security/lockdown
-bash: echo: write error: Operation not permitted

# echo full > /sys/kernel/security/lockdown
-bash: echo: write error: Invalid argument
```

## Повний перелік причин

Причини відмови складено в один упорядкований перелік `enum lockdown_reason`, і межу між рівнями позначають два його значення: усе до `LOCKDOWN_INTEGRITY_MAX` закривається на рівні `integrity`, усе після — лише на `confidentiality`. Другий стовпчик — рядок з масиву `lockdown_reasons[]`; саме він потрапляє в журнал, тому шукати причину зручно за ним.

**Рівень `integrity` — усе, чим можна змінити працююче ядро:**

| Значення переліку | Рядок у журналі |
|---|---|
| `LOCKDOWN_NONE` | `none` |
| `LOCKDOWN_MODULE_SIGNATURE` | `unsigned module loading` |
| `LOCKDOWN_DEV_MEM` | `/dev/mem,kmem,port` |
| `LOCKDOWN_EFI_TEST` | `/dev/efi_test access` |
| `LOCKDOWN_KEXEC` | `kexec of unsigned images` |
| `LOCKDOWN_HIBERNATION` | `hibernation` |
| `LOCKDOWN_PCI_ACCESS` | `direct PCI access` |
| `LOCKDOWN_IOPORT` | `raw io port access` |
| `LOCKDOWN_MSR` | `raw MSR access` |
| `LOCKDOWN_ACPI_TABLES` | `modifying ACPI tables` |
| `LOCKDOWN_DEVICE_TREE` | `modifying device tree contents` |
| `LOCKDOWN_PCMCIA_CIS` | `direct PCMCIA CIS storage` |
| `LOCKDOWN_TIOCSSERIAL` | `reconfiguration of serial port IO` |
| `LOCKDOWN_MODULE_PARAMETERS` | `unsafe module parameters` |
| `LOCKDOWN_MMIOTRACE` | `unsafe mmio` |
| `LOCKDOWN_DEBUGFS` | `debugfs access` |
| `LOCKDOWN_XMON_WR` | `xmon write access` |
| `LOCKDOWN_BPF_WRITE_USER` | `use of bpf to write user RAM` |
| `LOCKDOWN_DBG_WRITE_KERNEL` | `use of kgdb/kdb to write kernel RAM` |
| `LOCKDOWN_RTAS_ERROR_INJECTION` | `RTAS error injection` |
| `LOCKDOWN_XEN_USER_ACTIONS` | `Xen guest user action` |
| **`LOCKDOWN_INTEGRITY_MAX`** | `integrity` — межа, не причина |

**Рівень `confidentiality` — усе, чим можна прочитати пам'ять ядра:**

| Значення переліку | Рядок у журналі |
|---|---|
| `LOCKDOWN_KCORE` | `/proc/kcore access` |
| `LOCKDOWN_KPROBES` | `use of kprobes` |
| `LOCKDOWN_BPF_READ_KERNEL` | `use of bpf to read kernel RAM` |
| `LOCKDOWN_DBG_READ_KERNEL` | `use of kgdb/kdb to read kernel RAM` |
| `LOCKDOWN_PERF` | `unsafe use of perf` |
| `LOCKDOWN_TRACEFS` | `use of tracefs` |
| `LOCKDOWN_XMON_RW` | `xmon read and write access` |
| `LOCKDOWN_XFRM_SECRET` | `xfrm SA secret` |
| **`LOCKDOWN_CONFIDENTIALITY_MAX`** | `confidentiality` — межа, не причина |

Числові значення тут не є частиною жодного зовнішнього домовлення: назовні їх не видно ніде, і з випусками вони пливуть. Наочно: у першій версії механізму (5.4) `LOCKDOWN_INTEGRITY_MAX` дорівнював 15, а тепер 21 — бо між ними доклали `DEVICE_TREE`, `BPF_WRITE_USER`, `DBG_WRITE_KERNEL`, `RTAS_ERROR_INJECTION`, `XEN_USER_ACTIONS`; заразом `LOCKDOWN_BPF_READ` перейменували на `LOCKDOWN_BPF_READ_KERNEL`. Тому в коді й у розборі журналу спираються на імена та рядки, а не на числа.

## Виклик з коду ядра

```c
int security_locked_down(enum lockdown_reason what);
```

Повертає `0` (дозволено) або `-EPERM` (відмова) — цей самий код зазвичай і віддають угору як результат системного виклику. Без `CONFIG_SECURITY` це вбудована заглушка, що завжди повертає `0`.

Аргументом дають причину — і саме причину, не рівень. Два значення `*_MAX` тут заборонені: на `what >= LOCKDOWN_CONFIDENTIALITY_MAX` модуль спрацьовує `WARN()` і на всяк випадок відмовляє.

Кожна відмова лишає слід у [журналі ядра](book:unix-linux/kernel-log-printk) — кільцевому буфері, який читають через `dmesg` чи `journalctl -k`:

```
Lockdown: <ім'я програми>: <рядок причини> is restricted; see man kernel_lockdown.7
```

Наприклад, спроба відкрити `/dev/mem` на замкненій системі дає рядок такого вигляду:

```
Lockdown: dd: /dev/mem,kmem,port is restricted; see man kernel_lockdown.7
```

Ім'я береться з `current->comm`, тобто це коротке ім'я самого потоку, а не повний шлях до програми й не її аргументи. Для пошуку винуватця цього часто замало — тоді ім'я з рядка дає лише перший натяк, а решту доводиться зіставляти за часом.

> 🔧 **Навіщо це.** Друк іде через `pr_notice_ratelimited()`, тобто ядро свідомо глушить потік однакових повідомлень. Програма, що стукає в закриті двері в циклі, дасть кілька рядків, а не тисячі, — і в журналі це виглядатиме як поодинокі відмови посеред роботи. Тому відсутність рядка `Lockdown:` не доводить, що відмов не було: рахувати спроби за рядками журналу не можна, а от знайти саму причину — цілком.
