# ⚙️ Практичний розбір помилок пам'яті через KASAN

У цій практичній вставці розглядається створення повноцінного тестового модуля ядра Linux (`kasan_demo.c`), який свідомо відтворює три основні категорії помилок роботи з пам'яттю: Use-After-Free (UAF), Out-of-Bounds Write (OOB Write) та Out-of-Bounds Read (OOB Read). Також наведено детальний покроковий аналіз реального звіту KASAN із системного журналу `dmesg`, методологію розшифровки зсувів адреси інструкцій та практичні інструменти для прив'язки до рядків сирцевого коду.

> [!NOTE]
> Код прикладу виконується у просторі ядра Linux (`kernel space`). Згідно з каноном §5, для модулів ядра використовується мова C без вкладки C++, оскільки ядро Linux не підтримує стандартну бібліотеку C++, винятки та розгортання стека.

## 1. Архітектурні засади створення тестового модуля

Для безпечної демонстрації спрацьовувань KASAN без випадкового пошкодження критичних структур даних ядра використовується підсистема `debugfs`. Модуль створює віртуальну директорію `/sys/kernel/debug/kasan_demo/` із трьома керуючими файлами (`trigger_uaf`, `trigger_oob_write`, `trigger_oob_read`).

При записі будь-яких даних у відповідний файл викликається обробник `write` файлової операції (`file_operations`), який виконує конкретну маніпуляцію з пам'яттю через підсистему алокатора `SLUB` (`kmalloc`/`kfree`).

### 1.1 Механіка виділення та отруєння в прикладі

Кожен виклик `kmalloc(size, GFP_KERNEL)` у модулі ядра проходить через такі етапи у KASAN:
1. **Виділення слота у SLUB:** Алокатор обирає підходящий кеш (наприклад, `kmalloc-32` для 32-байтних об'єктів).
2. **Розмітка червоних зон:** KASAN позначає пам'ять ліворуч та праворуч від корисного навантаження маркером `0xF1` (`KASAN_KMALLOC_REDZONE`).
3. **Зняття отрути з навантаження:** Тіньова пам'ять для власне об'єкта переводиться у стан `0x00` (Valid).
4. **Звільнення (`kfree`):** Пам'ять об'єкта отруюється маркером `0xFC` (`KASAN_SLAB_FREE`), а сам об'єкт вміщується у FIFO-чергу карантину KASAN (`kasan_quarantine`), затримуючи його повторне використання іншими підсистемами.

---

## 2. Повний сирцевий код модуля ядра (`kasan_demo.c`)

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/slab.h>
#include <linux/debugfs.h>
#include <linux/uaccess.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("KASAN Lab Demo");
MODULE_DESCRIPTION("Модуль для демонстрації спрацювання KASAN при багах UAF та OOB");

static struct dentry *demo_dir;

struct demo_struct {
	char name[16];
	int id;
	int flags;
};

/* 
 * 1. Тригер Use-After-Free (UAF):
 * Виділяємо структуру, звільняємо її через kfree(),
 * але зберігаємо висячий вказівник і здійснюємо читання та запис.
 */
static ssize_t uaf_write(struct file *file, const char __user *user_buf,
			 size_t count, loff_t *ppos)
{
	struct demo_struct *ptr;

	pr_info("KASAN_DEMO: Запуск сценарію Use-After-Free (UAF)...\n");

	/* Крок 1: Виділення пам'яті у SLUB-кеші kmalloc-32 */
	ptr = kmalloc(sizeof(struct demo_struct), GFP_KERNEL);
	if (!ptr)
		return -ENOMEM;

	ptr->id = 101;
	ptr->flags = 0xABCD;
	snprintf(ptr->name, sizeof(ptr->name), "UAF_Target");

	pr_info("KASAN_DEMO: Створено об'єкт за віртуальною адресою %px\n", ptr);

	/* Крок 2: Звільнення пам'яті. KASAN отруює тіньові байти кодом 0xFC */
	kfree(ptr);
	pr_info("KASAN_DEMO: Пам'ять звільнено через kfree(). Вказівник збережено у стек-фреймі.\n");

	/* Крок 3: Спроба читання за висячим вказівником */
	pr_info("KASAN_DEMO: Зчитано ptr->id = %d (Очікується негайний звіт KASAN)\n", ptr->id);

	return count;
}

/* 
 * 2. Тригер Out-of-Bounds Write (OOB Write):
 * Виділяємо буфер на 32 байти, але записуємо 48 байтів,
 * виходячи за праву межу у червону зону SLUB (0xF1).
 */
static ssize_t oob_write(struct file *file, const char __user *user_buf,
			 size_t count, loff_t *ppos)
{
	char *buffer;
	int i;

	pr_info("KASAN_DEMO: Запуск сценарію Out-of-Bounds Write (OOB Write)...\n");

	buffer = kmalloc(32, GFP_KERNEL);
	if (!buffer)
		return -ENOMEM;

	pr_info("KASAN_DEMO: Виділено буфер 32 байти за адресою %px\n", buffer);

	/* Записуємо 48 байтів: перші 32 коректні, наступні 16 псують червону зону */
	for (i = 0; i < 48; i++) {
		buffer[i] = 'X';
	}

	pr_info("KASAN_DEMO: Запис 48 байтів завершено.\n");

	kfree(buffer);
	return count;
}

/* 
 * 3. Тригер Out-of-Bounds Read (OOB Read):
 * Зчитуємо байти за межами виділеного масиву.
 */
static ssize_t oob_read(struct file *file, const char __user *user_buf,
			size_t count, loff_t *ppos)
{
	char *buffer;
	char val;
	int i;

	pr_info("KASAN_DEMO: Запуск сценарію Out-of-Bounds Read (OOB Read)...\n");

	buffer = kmalloc(16, GFP_KERNEL);
	if (!buffer)
		return -ENOMEM;

	pr_info("KASAN_DEMO: Виділено буфер 16 байтів за адресою %px\n", buffer);

	/* Читаємо на 10 байтів далі виділеного розміру */
	for (i = 0; i < 26; i++) {
		val = buffer[i];
	}

	pr_info("KASAN_DEMO: Зчитано байт за межею: 0x%x\n", val);

	kfree(buffer);
	return count;
}

static const struct file_operations uaf_fops = {
	.owner = THIS_MODULE,
	.write = uaf_write,
};

static const struct file_operations oob_write_fops = {
	.owner = THIS_MODULE,
	.write = oob_write,
};

static const struct file_operations oob_read_fops = {
	.owner = THIS_MODULE,
	.write = oob_read,
};

static int __init kasan_demo_init(void)
{
	demo_dir = debugfs_create_dir("kasan_demo", NULL);
	if (!demo_dir) {
		pr_err("KASAN_DEMO: Не вдалося створити директорію debugfs\n");
		return -ENOMEM;
	}

	debugfs_create_file("trigger_uaf", 0200, demo_dir, NULL, &uaf_fops);
	debugfs_create_file("trigger_oob_write", 0200, demo_dir, NULL, &oob_write_fops);
	debugfs_create_file("trigger_oob_read", 0200, demo_dir, NULL, &oob_read_fops);

	pr_info("KASAN_DEMO: Модуль успішно завантажено. Вузли у /sys/kernel/debug/kasan_demo/ готово.\n");
	return 0;
}

static void __exit kasan_demo_exit(void)
{
	debugfs_remove_recursive(demo_dir);
	pr_info("KASAN_DEMO: Модуль вивантажено.\n");
}

module_init(kasan_demo_init);
module_exit(kasan_demo_exit);
```

---

## 3. Процедура збірки, завантаження та виконання (`Makefile`)

Для проведення лабораторного випробування необхідне ядро Linux, зібране з опціями `CONFIG_KASAN=y` та `CONFIG_KASAN_GENERIC=y`.

**Файл `Makefile`:**
```makefile
obj-m += kasan_demo.o

KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	make -C $(KDIR) M=$(PWD) modules

clean:
	make -C $(KDIR) M=$(PWD) clean
```

**Інструкції виконання в терміналі:**
```bash
# 1. Компіляція модуля ядра
make

# 2. Перевірка наявності debugfs та монтування за потреби
sudo mount -t debugfs none /sys/kernel/debug

# 3. Завантаження модуля в ядро
sudo insmod kasan_demo.ko

# 4. Виклик сценарію Use-After-Free
echo 1 | sudo tee /sys/kernel/debug/kasan_demo/trigger_uaf

# 5. Виклик сценарію Out-of-Bounds Write
echo 1 | sudo tee /sys/kernel/debug/kasan_demo/trigger_oob_write

# 6. Виклик сценарію Out-of-Bounds Read
echo 1 | sudo tee /sys/kernel/debug/kasan_demo/trigger_oob_read
```

---

## 4. Глибокий аналіз системного звіту KASAN (Bug Report Analysis)

Нижче наведено повний звіт, записаний ядром у `dmesg` під час спроби виконання `echo 1 > /sys/kernel/debug/kasan_demo/trigger_uaf`:

```text
==================================================================
[   84.312104] BUG: KASAN: use-after-free in uaf_write+0x8a/0xd0 [kasan_demo]
[   84.312112] Read of size 4 at addr ffff88810345a010 by task tee/2145
[   84.312117] CPU: 2 PID: 2145 Comm: tee Tainted: G        W          6.6.0-kasan #1
[   84.312121] Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 1.16.2
[   84.312125] Call Trace:
[   84.312128]  <TASK>
[   84.312131]  dump_stack_lvl+0x48/0x70
[   84.312139]  print_report+0xcf/0x610
[   84.312146]  kasan_report+0xaa/0xd0
[   84.312153]  uaf_write+0x8a/0xd0 [kasan_demo]
[   84.312160]  vfs_write+0x134/0x420
[   84.312167]  ksys_write+0x72/0x100
[   84.312173]  do_syscall_64+0x3f/0x90
[   84.312179]  entry_SYSCALL_64_after_hwframe+0x6e/0xd8
[   84.312186]  </TASK>
[   84.312189] 
[   84.312191] Allocated by task 2145:
[   84.312194]  kasan_save_stack+0x22/0x50
[   84.312199]  kasan_set_track+0x25/0x30
[   84.312208]  uaf_write+0x3d/0xd0 [kasan_demo]
[   84.312213]  vfs_write+0x134/0x420
[   84.312218] 
[   84.312220] Freed by task 2145:
[   84.312223]  kasan_save_stack+0x22/0x50
[   84.312227]  kasan_set_track+0x25/0x30
[   84.312231]  kasan_save_free_info+0x2b/0x50
[   84.312246]  uaf_write+0x68/0xd0 [kasan_demo]
[   84.312251]  vfs_write+0x134/0x420
[   84.312255] 
[   84.312257] Memory state around the buggy address:
[   84.312261]  ffff88810345bf00: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
[   84.312266]  ffff88810345bf80: fc fc fc fc fc fc fc fc fc fc fc fc fc fc fc fc
[   84.312271] >ffff88810345a000: fc fc [fc] fc fc fc fc fc fc fc fc fc fc fc fc fc
[   84.312275]                               ^
==================================================================
```

### Покроковий технічний аналіз засадничих структур звіту

1. **Ідентифікація категорії вразливості та адреси:**
   - Рядок `BUG: KASAN: use-after-free` сигналізує про виявлення спроби доступу до пам'яті, яку вже було повернено алокатору через виклик `kfree()`.
   - Рядок `Read of size 4 at addr ffff88810345a010` повідомляє, що інструкція процесора намагалася виконувати 4-байтну операцію зчитання цілого числа `int` за віртуальною адресою `0xffff88810345a010`.
   - Поле `Tainted: G W 6.6.0-kasan` інформує про стан заплямованості ядра (`taint flags`). Символ `W` вказує на наявність попереджень (warning) під час поточного сеансу роботи ядра.

2. **Аналіз стека викликів місця порушення (Offending Access Call Trace):**
   - Стек викликів показує повний ланцюжок виконання процесу `tee` (PID 2145) у момент спрацювання перевірки KASAN.
   - Смуга виклику бере початок у точки входу системного виклику `entry_SYSCALL_64_after_hwframe`, проходить через загальну шар-абстракцію VFS `vfs_write` і переходить у функцію обробника файлової операції `uaf_write` зі зсувом `+0x8a/0xd0`.
   - Утиліта KASAN негайно перехоплює нелегітимний виклик усередині `kasan_report+0xaa/0xd0`, не дозволяючи пошкодженим даним поширитися далі по системі.

3. **Стек історії виділення пам'яті (Allocated by task 2145):**
   - Завдяки збереженню відпечатка стека під час виконання `kmalloc()` KASAN дає відповідь на питання «хто створив проблемний об'єкт?».
   - Рядок `uaf_write+0x3d/0xd0` вказує на точний зсув інструкції, у якій було виконано виклик `kmalloc(sizeof(struct demo_struct), GFP_KERNEL)`.

4. **Стек історії звільнення пам'яті (Freed by task 2145):**
   - Ця секція є найціннішою частиною аналізу для усунення помилок у розробці складнопаралельних драйверів. При багах UAF звільнення пам'яті та повторне некоректне звернення часто виконуються у різних потоках, асинхронних обробниках переривань (`bottom halves`) або таймерах.
   - Стек чітко розкриває, що функція `uaf_write` на зсуві `+0x68` викликала `kfree(ptr)`, зв'язуючи момент вивільнення об'єкта з його подальшим неправильним розіменуванням.

5. **Дамп тіньової пам'яті (Shadow Memory Dump):**
   - Секція показує зліпок байтів тіньової пам meті навколо адреси `0xffff88810345a010`.
   - Рядок зі знаком `>` позначає 16-байтну тіньову смугу, яка покриває цільову адресу.
   - Маркер `[fc]` у квадратних дужках фіксує, що тіньовий байт адреси `0xffff88810345a010` дорівнює `0xFC` (`KASAN_SLAB_FREE`). Це беззаперечно доводить, що об'єкт перебуває у черзі карантину KASAN і будь-яка спроба його зчитання чи запису є грубим порушенням безпеки пам'яті.

---

## 5. Розбір Out-of-Bounds Write (OOB Write) у dmesg

При виконанні команди `echo 1 > /sys/kernel/debug/kasan_demo/trigger_oob_write` KASAN генерує звіт іншої категорії:

```text
==================================================================
[  112.451020] BUG: KASAN: slab-out-of-bounds in oob_write+0x62/0x90 [kasan_demo]
[  112.451028] Write of size 1 at addr ffff888102b40020 by task tee/2180
[  112.451033] CPU: 0 PID: 2180 Comm: tee Tainted: G        W          6.6.0-kasan #1
[  112.451037] Call Trace:
[  112.451040]  <TASK>
[  112.451043]  dump_stack_lvl+0x48/0x70
[  112.451050]  kasan_report+0xaa/0xd0
[  112.451058]  oob_write+0x62/0x90 [kasan_demo]
[  112.451064]  vfs_write+0x134/0x420
[  112.451070]  </TASK>
[  112.451073] 
[  112.451075] Allocated by task 2180:
[  112.451078]  kasan_save_stack+0x22/0x50
[  112.451083]  __kasan_kmalloc+0x82/0x90
[  112.451088]  oob_write+0x2b/0x90 [kasan_demo]
[  112.451093] 
[  112.451095] Memory state around the buggy address:
[  112.451098]  ffff888102b40000: 00 00 00 00 [f1] f1 f1 f1 00 00 00 00 00 00 00 00
[  112.451103]                               ^
==================================================================
```

### Особливості аналізу OOB звіту:

- **Категорія `slab-out-of-bounds`:** Показує, що операція запису вийшла за межі розміру виділеного буфера у SLUB-кеші.
- **Маркер `[f1]` у дампі тіньової пам'яті:** У квадратних дужках виділено байт `0xF1` (`KASAN_KMALLOC_REDZONE`). Це доводить, що 32 байти об'єкта (позначені як `00 00 00 00`) закінчилися, і запис на зсуві 32 влучив прямо у праву червону зону, додану алокатором для захисту сусідніх об'єктів.

---

## 6. Методологія локалізації помилки у сирцевому коді

Для перетворення шестнадцятирічного зсуву інструкції (наприклад `uaf_write+0x8a/0xd0` або `oob_write+0x62/0x90`) у конкретний номер рядка у файлі `kasan_demo.c` використовуються два стандартні інструменти аналізу ядра Linux.

### 6.1 Використання утилітарного скрипту `decode_stacktrace.sh`

У джерельному дереві ядра Linux наявний утилітарний скрипт `scripts/decode_stacktrace.sh`, який автоматично розшифровує адреси за допомогою відлагоджувальної інформації DWARF:

```bash
# Синтаксис декодування дампа з використанням зібраного образу vmlinux:
./scripts/decode_stacktrace.sh vmlinux . < dmesg_kasan.log
```

**Результат роботи декодера:**
```text
uaf_write (e:/develop/courses/reference/unix-linux/observability/kasan-kernel-address-sanitizer/kasan_demo.c:54)
Allocated by task 2145:
uaf_write (e:/develop/courses/reference/unix-linux/observability/kasan-kernel-address-sanitizer/kasan_demo.c:38)
Freed by task 2145:
uaf_write (e:/develop/courses/reference/unix-linux/observability/kasan-kernel-address-sanitizer/kasan_demo.c:48)
```

### 6.2 Ручне декодування через `addr2line` або `gdb`

Якщо доступний скомпільований об'єктний файл модуля `kasan_demo.o` (із прапорцем відлагоджувальних символів `-g`), можна використати утиліту `addr2line`:

```bash
# Знаходження точної лінії коду за зсувом 0x8a
addr2line -e kasan_demo.o -f -i 0x8a
```

Або через інтерактивний налагоджувач GDB:
```bash
gdb kasan_demo.o
(gdb) list *uaf_write+0x8a
```

Використання KASAN у поєднанні з автоматичними скриптами розшифровки дозволяє розробникам ядра у найкоротші терміни виявляти критичні порушення пам'яті, усувати баги UAF та OOB і гарантувати високу надійність системних компонентів.
