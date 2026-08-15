# 📋 Реєстр причин та хуків перевірки: lockdown_reasons

Усі перевірки режиму блокування ядра (Kernel Lockdown) у Linux виконуються через єдину точку входу — системний хук `security_locked_down(enum lockdown_reason reason)`. Призначення цього механізму полягає у наданні кожній підсистемі ядра специфічної мови для опису потенційно небезпечних операцій за допомогою стандартизованих констант причин блокування. Повний перелік причин, їхні межі та службові константи визначено у заголовному файлі ядра `include/linux/security.h`.

## 1. Архітектура та структура перерахування enum lockdown_reason

Перерахування `enum lockdown_reason` побудовано за принципом суворої монотонності та ієрархічного розширення привілеїв. Кожна наступна константа в списку вимагає більшого або рівного рівня захисту порівняно з попередніми значеннями. Причини розділені на дві фундаментальні групи спеціальними межовими константами `LOCKDOWN_INTEGRITY_MAX` та `LOCKDOWN_CONFIDENTIALITY_MAX`.

```c
enum lockdown_reason {
	LOCKDOWN_NONE,
	/* ── Причини, що блокуються у режимі Integrity ── */
	LOCKDOWN_MODULE_SIGNATURE,
	LOCKDOWN_DEV_MEM,
	LOCKDOWN_EFI_TEST,
	LOCKDOWN_KEXEC,
	LOCKDOWN_HIBERNATION,
	LOCKDOWN_PCI_ACCESS,
	LOCKDOWN_IOPORT,
	LOCKDOWN_MSR,
	LOCKDOWN_ACPI_TABLES,
	LOCKDOWN_DEVICE_TREE,
	LOCKDOWN_PCMCIA_CIS,
	LOCKDOWN_TIOCSSERIAL,
	LOCKDOWN_MODULE_PARAMETERS,
	LOCKDOWN_MMIOTRACE,
	LOCKDOWN_DEBUGFS,
	LOCKDOWN_XMON_WR,
	LOCKDOWN_BPF_WRITE_USER,
	LOCKDOWN_DBG_WRITE_KERNEL,
	LOCKDOWN_RTAS_ERROR_INJECTION,
	LOCKDOWN_INTEGRITY_MAX,
	/* ── Причини, що блокуються у режимі Confidentiality ── */
	LOCKDOWN_KCORE,
	LOCKDOWN_KPROBES,
	LOCKDOWN_BPF_READ_KERNEL,
	LOCKDOWN_DBG_READ_KERNEL,
	LOCKDOWN_PERF,
	LOCKDOWN_TRACEFS,
	LOCKDOWN_XMON_RW,
	LOCKDOWN_XSK_WAKEUP,
	LOCKDOWN_CONFIDENTIALITY_MAX,
};
```

Значення, що розміщені від `LOCKDOWN_NONE` до `LOCKDOWN_INTEGRITY_MAX`, активуються при переході ядра у режим **Integrity**. Вони спрямовані на запобігання несанкціонованій модифікації бінарного коду ядра, системних таблиць викликів та конфігурації шин. Значення від `LOCKDOWN_INTEGRITY_MAX` до `LOCKDOWN_CONFIDENTIALITY_MAX` додатково активуються у режимі **Confidentiality**, розширюючи захист на операції зчитування внутрішніх даних ядра та дампів пам'яті. Склад переліку залежить від версії ядра: з новими підсистемами додають і нові причини, тож наведене вище відповідає ядрам 6.x.

## 2. Класифікація причин за підсистемами ядра

Для зручності аналізу та розробки системних драйверів причини блокування розділяють на чотири основні категорії залежно від цільової підсистеми ядра.

### 2.1. Захист оперативної пам'яті та завантаження коду

Ця категорія охоплює причини, які запобігають впровадженню сторонніх інструкцій або перезапису пам'яті ядра під час виконання.

* **`LOCKDOWN_MODULE_SIGNATURE`:** Викликається підсистемою завантаження модулів `kernel/module/main.c` під час обробки системних викликів `init_module()` та `finit_module()`. Якщо бінарний файл модуля (`.ko`) не містить криптографічного підпису або підпис засновано на сертифікаті, якого немає в довірених зв'язках ключів ядра (`builtin_trusted_keys`, `secondary_trusted_keys`, `.machine`), ядро відхиляє завантаження.
* **`LOCKDOWN_DEV_MEM`:** Викликається драйверами символьних пристроїв `drivers/char/mem.c`. Перевіряє спроби відкриття файлів `/dev/mem` та `/dev/kmem` у режимі запису (`O_WRONLY` або `O_RDWR`). Запобігає прямому перезапису фізичної пам'яті, у якій лежать код і структури ядра.
* **`LOCKDOWN_KEXEC`:** Викликається підсистемою гарячої заміни ядра `kernel/kexec.c`. Блокує системний виклик `kexec_load()` цілком: він приймає готові сегменти пам'яті, і перевіряти в них підпис ніде. Підписаний образ лишається завантажити через `kexec_file_load()`, який сам читає файл і звіряє підпис PKCS#7.
* **`LOCKDOWN_HIBERNATION`:** Викликається підсистемою управління живленням `kernel/power/hibernate.c`. Забороняє хібернацію як таку: ядро не має чим перевірити цілісність образу, збереженого на диску, тож підміна swap-файлу означала б запис довільних даних просто в RAM під час пробудження.

### 2.2. Прямий доступ до апаратного забезпечення та шин

Ця категорія блокує неконтрольований доступ процесів простору користувача до фізичних регістрів процесора та периферійних шин.

* **`LOCKDOWN_IOPORT`:** Викликається архітектурно-залежним кодом `arch/x86/kernel/ioport.c` при виконанні системних викликів `iopl()` та `ioperm()`. Забороняє підвищення привілеїв вводу/виводу процесора (IOPL > 0) та вибіркове відкриття побітових масок портів.
* **`LOCKDOWN_MSR`:** Викликається драйвером `/dev/cpu/*/msr` (`arch/x86/kernel/msr.c`). Забороняє запис у специфічні регістри процесора, які контролюють термальні межі, конфігурацію блокування CR0.WP, вектори системних викликів MSR_LSTAR та мікрокод CPU.
* **`LOCKDOWN_PCI_ACCESS`:** Викликається драйвером bus-sysfs `drivers/pci/pci-sysfs.c`. Забороняє прямий запис у конфігураційний простір PCI-пристроїв та переналаштування адресних регістрів BAR з простору користувача, унеможливлюючи ініціацію DMA-атак.
* **`LOCKDOWN_TIOCSSERIAL`:** Викликається драйверами послідовних портів TTY. Забороняє використання виклику ioctl `TIOCSSERIAL` для зміни фізичних базових портів I/O та ліній апаратних переривань IRQ.

### 2.3. Конфігурація прошивки та дерева пристроїв

Ця група захищає інтерфейси взаємодії з апаратною прошивкою плати.

* **`LOCKDOWN_ACPI_TABLES`:** Викликається підсистемою ACPI (`drivers/acpi/tables.c`). Блокує завантаження користувацьких оверлеїв та підмінювання таблиць DSDT/SSDT через initrd або sysfs, запобігаючи виконанню довільного коду AML (ACPI Machine Language).
* **`LOCKDOWN_DEVICE_TREE`:** Викликається підсистемою Open Firmware (`drivers/of/resolver.c`). Забороняє динамічне накладання оверлеїв Device Tree у системне дерево пристроїв на архітектурах ARM, AArch64 та RISC-V.
* **`LOCKDOWN_EFI_TEST`:** Викликається тестовим драйвером EFI (`drivers/firmware/efi/test.c`). Забороняє модифікацію енергонезалежних змінних NVRAM прошивки через відлагоджувальні інтерфейси.

### 2.4. Захист конфіденційності даних та інструменти трасування

Операції цієї категорії блокуються виключно у режимі **Confidentiality** для запобігання витоку секретів ядра.

* **`LOCKDOWN_KCORE`:** Викликається драйвером `/proc/kcore` (`fs/proc/kcore.c`). Блокує зчитання повного віртуального адресного простору ядра у форматі ELF, а також читання `/dev/mem` і `/dev/kmem`.
* **`LOCKDOWN_KPROBES`:** Викликається підсистемою трасування `kernel/kprobes.c`. Забороняє встановлення точок динамічного інспектування `kprobes` над адресами інструкцій ядра.
* **`LOCKDOWN_BPF_READ_KERNEL`:** Перевіряється під час завантаження програми верифікатором eBPF (`kernel/bpf/`); до ядра 5.13 причина звалася `LOCKDOWN_BPF_READ`. Забороняє виконання eBPF-програм, які викликають helper-функцію `bpf_probe_read_kernel()` для читання довільних вказівників пам'яті ядра.
* **`LOCKDOWN_PERF`:** Викликається підсистемою `perf` (`kernel/events/core.c`). Забороняє події, що читають пам'ять ядра, і зчитування апаратних буферів Intel PT та ARM CoreSight, які містять покрокову історію виконаних інструкцій.

## 3. Зведена специфікація причин перевірки

Нижче наведено таблицю основних причин блокування з відображенням на підсистеми ядра та наслідки для користувацьких процесів.

| Код причини (`enum lockdown_reason`) | Поріг блокування | Підсистема ядра та системний виклик | Опис операції та безпековий ризик | Наслідок блокування для користувача |
| :--- | :--- | :--- | :--- | :--- |
| `LOCKDOWN_MODULE_SIGNATURE` | **Integrity** | `kernel/module/`, `init_module()`, `finit_module()` | Спроба завантаження бінарного модуля ядра (`.ko`), який не має перевіреного цифрового підпису. | Завантаження модуля відхиляється з помилкою `-EPERM`. |
| `LOCKDOWN_DEV_MEM` | **Integrity** | `drivers/char/mem.c`, `open("/dev/mem")` | Спроба відкриття пристроїв прямого доступу до фізичної чи віртуальної пам'яті на запис. | Модифікація коду та даних ядра через файли пристроїв заборонена. |
| `LOCKDOWN_EFI_TEST` | **Integrity** | `drivers/firmware/efi/test.c` | Використання тестового інтерфейсу EFI для маніпуляції змінними NVRAM прошивки. | Захищає змінні завантаження Secure Boot від підробки з ОС. |
| `LOCKDOWN_KEXEC` | **Integrity** | `kernel/kexec.c`, `kexec_load()` | Виклик `kexec_load()`, який приймає готові сегменти пам'яті й не має де взяти підпис. | Блокується цілком; лишається `kexec_file_load()` з перевіркою підпису. |
| `LOCKDOWN_HIBERNATION` | **Integrity** | `kernel/power/hibernate.c` | Хібернація: образ пам'яті на диску нічим не перевіряється під час пробудження. | Перехід у сплячий режим із записом на диск заборонено. |
| `LOCKDOWN_PCI_ACCESS` | **Integrity** | `drivers/pci/pci-sysfs.c` | Прямий запис у простори конфігурації PCI-пристроїв та BAR-регістри з простору користувача. | Блокує переналаштування пристроїв для ініціації DMA-атак. |
| `LOCKDOWN_IOPORT` | **Integrity** | `arch/x86/kernel/ioport.c`, `iopl()` | Надання процесу простору користувача прямого доступу до портів вводу/виводу. | Забороняє користувацьким процесам керувати шиною I/O. |
| `LOCKDOWN_MSR` | **Integrity** | `arch/x86/kernel/msr.c`, `open("/dev/cpu/*/msr")` | Запис у MSR-регістри процесора. Запобігає зміні термальних меж та вимкненню захисту. | Запис у MSR відхиляється, читання лишається дозволеним. |
| `LOCKDOWN_ACPI_TABLES` | **Integrity** | `drivers/acpi/tables.c` | Динамічне підмінювання таблиць ACPI (DSDT/SSDT) таблицями з користувацького простору. | Забороняє виконання неперевіреного AML-коду. |
| `LOCKDOWN_DEVICE_TREE` | **Integrity** | `drivers/of/resolver.c` | Завантаження непідписаних оверлеїв Device Tree у системне дерево пристроїв. | Блокує підробку конфігурації периферії на ARM/RISC-V. |
| `LOCKDOWN_PCMCIA_CIS` | **Integrity** | `drivers/pcmcia/` | Перевизначення плат Card Information Structure (CIS) для застарілих пристроїв. | Захищає структури даних драйверів PCMCIA. |
| `LOCKDOWN_TIOCSSERIAL` | **Integrity** | `drivers/tty/serial/` | Використання ioctl `TIOCSSERIAL` для зміни портів I/O та ліній IRQ. | Забороняє зміну апаратних ресурсів COM-портів. |
| `LOCKDOWN_KCORE` | **Confidentiality** | `fs/proc/kcore.c`, `/proc/kcore` | Читання повного образу оперативної пам'яті ядра через elf-інтерфейс procfs або `/dev/mem`. | Блокує дамп пам'яті ядра для викрадення ключів LUKS. |
| `LOCKDOWN_KPROBES` | **Confidentiality** | `kernel/kprobes.c` | Динамічне встановлення точок інспекції `kprobes` чи `ftrace` над функціями ядра. | Забороняє трасування пам'яті та зчитування аргументів викликів. |
| `LOCKDOWN_BPF_READ_KERNEL` | **Confidentiality** | `kernel/bpf/` | Завантаження eBPF-програм, що викликають helper `bpf_probe_read_kernel()`. | Унеможливлює викрадення секретів ядра через BPF. |
| `LOCKDOWN_PERF` | **Confidentiality** | `kernel/events/core.c` | Читання пам'яті ядра через `perf` та апаратних буферів трасування (Intel PT, ARM CoreSight). | Забороняє інспекцію покрокового потоку інструкцій ядра. |

## 4. Внутрішньоядерний механізм виконання та стекування LSM

Підсистеми ядра перевіряють можливість виконання чутливої операції за допомогою функції `security_locked_down()`. Ця функція є стандартизованою обгорткою над інфраструктурою викликів Linux Security Modules:

```c
int security_locked_down(enum lockdown_reason reason)
{
	return call_int_hook(locked_down, 0, reason);
}
```

Модуль безпеки Lockdown під час ініціалізації ядра ставить свій обробник у глобальний список LSM-хуків. Внутрішня реалізація перевірки в ядрі порівнює поточний глобальний рівень `kernel_locked_down` з переданим значенням причини:

```c
static enum lockdown_reason kernel_locked_down;

static int lockdown_is_locked_down(enum lockdown_reason reason)
{
	if (kernel_locked_down != LOCKDOWN_NONE && kernel_locked_down >= reason) {
		if (lockdown_reasons[reason])
			pr_notice("Lockdown: %s: %s is restricted; see man kernel_lockdown.7\n",
				  current->comm, lockdown_reasons[reason]);
		return -EPERM;
	}
	return 0;
}
```

Завдяки механізму стекування LSM (LSM Stacking) модуль Lockdown функціонує паралельно з SELinux, AppArmor або SMACK. Якщо SELinux дозволяє операцію, але Lockdown повертає `-EPERM`, підсистема ядра відмовляє у виконанні системного виклику.

## 5. Формування журналів аудіту dmesg

При виконанні умови блокування `lockdown_is_locked_down()` ядро фіксує подібну спробу у системному журналі dmesg з індикатором `LOGLEVEL_NOTICE`. Запис містить назву виконуваного файла процесу (`current->comm`) та відповідне текстове пояснення з масиву `lockdown_reasons`:

```text
[   42.108234] Lockdown: insmod: unsigned module loading is restricted; see man kernel_lockdown.7
[  108.451902] Lockdown: devmem_tool: /dev/mem,kmem,port is restricted; see man kernel_lockdown.7
[  312.891004] Lockdown: bpftrace: use of bpf to read kernel RAM is restricted; see man kernel_lockdown.7
```

Ці журнальні повідомлення дозволяють засобам системного моніторингу та аналізаторам безпеки (SIEM) фіксувати спроби ескалації привілеїв чи несанкціонованої ін'єкції коду на найраніших етапах атаки.
