# ⚙️ Практична реалізація ітератора procfs для динамічного списку пристроїв

Нижче наведено практичну реалізацію повноцінного навчального модуля ядра Linux `device_inventory.ko`, що реєструє псевдофайл `/proc/device_inventory`. Модуль керує динамічним зв'язним списком віртуальних сенсорів, захищеним механізмом RCU (*Read-Copy-Update*), і реалізує повний цикл ітератора `struct seq_operations` із коректною обробкою табличних заголовків через `SEQ_START_TOKEN`, позиціонуванням `*pos` та безпечним розблокуванням.

У цій вставці розібрано повний життєвий цикл коду: структуру вузлів у пам'яті ядра, механіку блокування при паралельних модифікаціях, компіляцію модуля, користувацькі утиліти для перевірки читання й позиціонування та методи динамічного трасування викликів.

---

## 1. Архітектура та код модуля ядра

У просторі ядра драйвер описує структуру елемента `struct dev_node`, що містить стандартний вузол списку `struct list_head`, корисне навантаження (ідентифікатор, назву пристрою, стан, робочу температуру та лічильник збоїв), а також структуру `struct rcu_head` для безпечного асинхронного звільнення пам'яті після закінчення періоду очікування (*grace period*).

Для захисту списку під час запису (додавання чи видалення пристроїв) використовується спінлок `dev_list_lock`. Проте всі операції читання через `seq_file` виконуються виключно під захистом `rcu_read_lock()`. Це дозволяє процесам у просторі користувача безперешкодно вичитувати файл інвентаризації, не блокуючи паралельні оновлення стану сенсорів іншими підсистемами ядра.

```c
// SPDX-License-Identifier: GPL-2.0
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/slab.h>
#include <linux/list.h>
#include <linux/rculist.h>
#include <linux/rcupdate.h>
#include <linux/spinlock.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Unix & Linux Reference");
MODULE_DESCRIPTION("Демонстраційний ітератор seq_file для списку пристроїв");

#define PROC_FILENAME "device_inventory"
#define DEV_COUNT 64

struct dev_node {
	int id;
	char name[20];
	int status;         /* 1 - ONLINE, 0 - FAULT */
	int temperature;    /* Градуси Цельсія */
	unsigned long errs; /* Кількість помилок шини */
	struct list_head list;
	struct rcu_head rcu;
};

static LIST_HEAD(dev_list);
static DEFINE_SPINLOCK(dev_list_lock);
static struct proc_dir_entry *proc_entry;

/*
 * Метод start: підготовка до читання та пошук початкового елемента.
 * Якщо *pos == 0, повертаємо SEQ_START_TOKEN для друку шапки таблиці.
 */
static void *dev_seq_start(struct seq_file *m, loff_t *pos)
{
	struct dev_node *node;
	loff_t n = *pos;

	/* Захоплюємо блокування читача RCU на весь цикл ітерації */
	rcu_read_lock();

	if (n == 0)
		return SEQ_START_TOKEN;

	/* Шукаємо елемент із порядковим номером (n - 1) */
	n--;
	list_for_each_entry_rcu(node, &dev_list, list) {
		if (n == 0)
			return node;
		n--;
	}

	return NULL; /* За межами списку */
}

/*
 * Метод next: перехід до наступного запису списку.
 */
static void *dev_seq_next(struct seq_file *m, void *v, loff_t *pos)
{
	struct dev_node *node;
	struct list_head *next_head;

	(*pos)++;

	if (v == SEQ_START_TOKEN) {
		/* Перехід від заголовка до першого реального елемента */
		node = list_first_or_null_rcu(&dev_list, struct dev_node, list);
		return node;
	}

	node = (struct dev_node *)v;
	next_head = rcu_dereference_raw(node->list.next);

	if (next_head == &dev_list)
		return NULL; /* Дійшли кінця кільцевого списку */

	return list_entry_rcu(next_head, struct dev_node, list);
}

/*
 * Метод stop: обов'язкове зняття блокування RCU.
 */
static void dev_seq_stop(struct seq_file *m, void *v)
{
	rcu_read_unlock();
}

/*
 * Метод show: генерація текстового рядка для об'єкта.
 */
static int dev_seq_show(struct seq_file *m, void *v)
{
	struct dev_node *node;

	if (v == SEQ_START_TOKEN) {
		/* Друк шапки з фіксованим вирівнюванням колонок */
		seq_puts(m, "ID     Name             Status     Temp(C)  BusErrors\n");
		seq_puts(m, "-----------------------------------------------------\n");
		return 0;
	}

	node = (struct dev_node *)v;
	seq_printf(m, "%-6d %-16s %-10s %-8d %lu\n",
		   node->id,
		   node->name,
		   (node->status ? "ONLINE" : "FAULT"),
		   node->temperature,
		   node->errs);

	return 0;
}

/* Таблиця операцій ітератора */
static const struct seq_operations dev_seq_ops = {
	.start = dev_seq_start,
	.next  = dev_seq_next,
	.stop  = dev_seq_stop,
	.show  = dev_seq_show,
};

static int __init dev_inv_init(void)
{
	int i;
	struct dev_node *node;

	/* Наповнюємо список початковими тестовими пристроями */
	for (i = 0; i < DEV_COUNT; i++) {
		node = kzalloc(sizeof(*node), GFP_KERNEL);
		if (!node)
			goto err_cleanup;

		node->id = 1000 + i;
		snprintf(node->name, sizeof(node->name), "sensor_temp_%02d", i);
		node->status = (i % 7 != 0); /* Деякі сенсори у стані FAULT */
		node->temperature = 22 + (i % 15);
		node->errs = i * 3;

		spin_lock(&dev_list_lock);
		list_add_tail_rcu(&node->list, &dev_list);
		spin_unlock(&dev_list_lock);
	}

	/* Створюємо запис у procfs через зручний високорівневий помічник */
	proc_entry = proc_create_seq(PROC_FILENAME, 0444, NULL, &dev_seq_ops);
	if (!proc_entry) {
		pr_err("Не вдалося створити /proc/%s\n", PROC_FILENAME);
		goto err_cleanup;
	}

	pr_info("Модуль device_inventory завантажено, зареєстровано /proc/%s\n", PROC_FILENAME);
	return 0;

err_cleanup:
	spin_lock(&dev_list_lock);
	while (!list_empty(&dev_list)) {
		node = list_first_entry(&dev_list, struct dev_node, list);
		list_del(&node->list);
		kfree(node);
	}
	spin_unlock(&dev_list_lock);
	return -ENOMEM;
}

static void __exit dev_inv_exit(void)
{
	struct dev_node *node, *tmp;

	if (proc_entry)
		remove_proc_entry(PROC_FILENAME, NULL);

	spin_lock(&dev_list_lock);
	list_for_each_entry_safe(node, tmp, &dev_list, list) {
		list_del_rcu(&node->list);
		kfree_rcu(node, rcu);
	}
	spin_unlock(&dev_list_lock);

	/* Очікуємо завершення всіх паралельних читачів RCU */
	rcu_barrier();
	pr_info("Модуль device_inventory вивантажено\n");
}

module_init(dev_inv_init);
module_exit(dev_inv_exit);
```

---

## 2. Аналіз реалізації методів ітератора

Розглянемо ключові нюанси, закладені в чотири функції ітератора:

1. **Робота з маркером `SEQ_START_TOKEN`:** Замість того щоб друкувати заголовок окремо або перевіряти стан у кожній функції, метод `dev_seq_start()` повертає значення `((void *)1)` при `*pos == 0`. Функція `dev_seq_show()` розпізнає цей маркер і форматує рядок заголовків із розділювальною лінією. Наступний виклик `dev_seq_next()` бачить, що попереднім елементом був заголовок, і повертає перший дійсний вузол списку, збільшуючи `*pos` до `1`.
2. **Безпека RCU:** Виклик `rcu_read_lock()` розміщено у `dev_seq_start()`, а симетричний `rcu_read_unlock()` — у `dev_seq_stop()`. Оскільки ядро гарантує, що між `start()` і `stop()` не відбудеться перемикання контексту, який міг би порушити цілісність пам'яті RCU, обхід списку через `list_for_each_entry_rcu` є абсолютно безпечним. Навіть якщо інший потік ядра одночасно видалить вузол через `list_del_rcu()`, сам об'єкт пам'яті залишиться валідним до завершення `dev_seq_stop()`.
3. **Позиціонування за індексом:** У методі `dev_seq_start()` логічний зсув `*pos` інтерпретується як порядковий номер рядка. Якщо користувач викликає `lseek(fd, 20, SEEK_SET)`, метод `start` пропускає перші 19 елементів і повертає покажчик на 20-й вузол. Це усуває потребу зберігати байтові зсуви.
4. **Вивантаження модуля та бар'єри:** Під час виклику `dev_inv_exit()` вузли видаляються через `list_del_rcu()`, а пам'ять звільняється асинхронно макросом `kfree_rcu(node, rcu)`. Виклик `rcu_barrier()` перед виходом гарантує, що всі заплановані колбеки звільнення пам'яті завершилися до того, як код модуля буде остаточно вивантажено з адресного простору ядра.

---

## 3. Складання та тестування модуля

Для складання модуля використовується стандартний `Makefile` ядра Linux:

```makefile
obj-m += device_inventory.o

KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	make -C $(KDIR) M=$(PWD) modules

clean:
	make -C $(KDIR) M=$(PWD) clean
```

Після компіляції та завантаження модуля в систему перевіримо коректність генерації псевдофайлу за допомогою стандартних утиліт:

```bash
# Завантаження зібраного модуля
sudo insmod device_inventory.ko

# Перевірка виводу утилітою cat
cat /proc/device_inventory

# Перевірка читання невеликими фіксованими блоками (по 64 байти)
dd if=/proc/device_inventory bs=64 2>/dev/null
```

Команда `dd` із малим розміром блоку змушує VFS багаторазово викликати `seq_read()`, перевіряючи, чи зберігаються межі рядків і чи не виникає дублювання даних між окремими викликами.

---

## 4. Програма перевірки позиціонування lseek та читання

Для детального аналізу взаємодії з системними викликами `read()` та `lseek()` створимо тестову утиліту `inspect_devices`. Вона відкриває файл `/proc/device_inventory`, зчитує початковий блок, а потім виконує зміщення покажчика файлу за допомогою `lseek()`, перевіряючи коректність перезапуску ітератора.

У реалізації мовою C використовується низькорівневий файловий дескриптор `open()`, ручний контроль буфера та системний виклик `read()`. У реалізації мовою C++ управління життєвим циклом дескриптора інкапсульовано в ідіоматичний клас RAII `FileDescriptor`, обробка помилок спирається на `std::error_code`, а робота з пам'яттю організована через безпечний контейнер `std::array`.

:::tabs
```c
/* inspect_devices.c */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

#define PROC_PATH "/proc/device_inventory"
#define CHUNK_SIZE 128

int main(void)
{
	int fd = open(PROC_PATH, O_RDONLY);
	if (fd < 0) {
		perror("open " PROC_PATH);
		return EXIT_FAILURE;
	}

	printf("=== 1. Читання перших 256 байтів ===\n");
	char buf[CHUNK_SIZE];
	ssize_t n;
	int total_bytes = 0;

	while (total_bytes < 256 && (n = read(fd, buf, sizeof(buf) - 1)) > 0) {
		buf[n] = '\0';
		printf("%s", buf);
		total_bytes += n;
	}

	printf("\n=== 2. Перевірка lseek: повернення на початок ===\n");
	off_t new_off = lseek(fd, 0, SEEK_SET);
	if (new_off == (off_t)-1) {
		perror("lseek SEEK_SET");
		close(fd);
		return EXIT_FAILURE;
	}

	n = read(fd, buf, sizeof(buf) - 1);
	if (n > 0) {
		buf[n] = '\0';
		printf("Перший рядок після lseek(0):\n%s\n", buf);
	}

	close(fd);
	return EXIT_SUCCESS;
}
```
```cpp
// inspect_devices.cpp
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <array>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>

namespace {
constexpr const char* ProcPath = "/proc/device_inventory";
constexpr std::size_t ChunkSize = 128;

class FileDescriptor {
public:
	explicit FileDescriptor(int fd) noexcept : fd_(fd) {}
	~FileDescriptor() {
		if (fd_ >= 0) {
			::close(fd_);
		}
	}

	FileDescriptor(const FileDescriptor&) = delete;
	FileDescriptor& operator=(const FileDescriptor&) = delete;

	[[nodiscard]] int get() const noexcept { return fd_; }
	[[nodiscard]] bool isValid() const noexcept { return fd_ >= 0; }

private:
	int fd_{-1};
};
}

int main()
{
	FileDescriptor fd(::open(ProcPath, O_RDONLY));
	if (!fd.isValid()) {
		std::cerr << "Помилка відкриття " << ProcPath << ": "
		          << std::error_code(errno, std::generic_category()).message() << '\n';
		return EXIT_FAILURE;
	}

	std::cout << "=== 1. Читання перших 256 байтів ===\n";
	std::array<char, ChunkSize> buffer{};
	std::size_t totalBytesRead = 0;

	while (totalBytesRead < 256) {
		ssize_t bytes = ::read(fd.get(), buffer.data(), buffer.size() - 1);
		if (bytes <= 0) {
			break;
		}
		buffer[bytes] = '\0';
		std::cout.write(buffer.data(), bytes);
		totalBytesRead += bytes;
	}

	std::cout << "\n=== 2. Перевірка lseek: повернення на початок ===\n";
	if (::lseek(fd.get(), 0, SEEK_SET) == -1) {
		std::cerr << "Помилка lseek: "
		          << std::error_code(errno, std::generic_category()).message() << '\n';
		return EXIT_FAILURE;
	}

	ssize_t bytes = ::read(fd.get(), buffer.data(), buffer.size() - 1);
	if (bytes > 0) {
		buffer[bytes] = '\0';
		std::cout << "Перший рядок після lseek(0):\n" << buffer.data() << '\n';
	}

	return EXIT_SUCCESS;
}
```
:::

---

## 5. Трасування ітератора за допомогою bpftrace

Для того щоб наочно переконатися у послідовності викликів функцій ітератора ядром під час читання, скористаємося динамічним трасувальником `bpftrace`. Однорядковий скрипт дозволяє зафіксувати кожен крок обходу списку:

```bash
sudo bpftrace -e '
kprobe:dev_seq_start { printf("start: pos=%d\n", *arg1); }
kprobe:dev_seq_show  { printf("  show: ptr=%p\n", arg1); }
kprobe:dev_seq_next  { printf("  next: pos=%d\n", *arg2); }
kprobe:dev_seq_stop  { printf("stop\n"); }
'
```

Якщо під час роботи трасувальника виконати `head -n 3 /proc/device_inventory`, у терміналі відобразиться чітка послідовність:
1. `start: pos=0` (повертає покажчик `SEQ_START_TOKEN`).
2. `show` (друкує заголовок таблиці).
3. `next: pos=0` (інкрементує `pos` до 1 і повертає перший елемент).
4. `show` (друкує рядок пристрою 1000).
5. `next: pos=1` (інкрементує `pos` до 2 і повертає другий елемент).
6. `show` (друкує рядок пристрою 1001).
7. `stop` (знімає блокування RCU).

---

## 6. Спостереження за динамічним розширенням буфера

Якщо збільшити кількість вузлів у списку `DEV_COUNT` до 10000, загальний обсяг текстового виводу перевищить 500 КБ. Це дозволяє спостерігати автоматичне розширення буфера ядра:

1. Під час першого виклику `read()` підсистема виділяє початковий буфер розміром 4096 байтів (`PAGE_SIZE`).
2. Коли `seq_printf()` заповнює цей обсяг, `seq_has_overflowed(m)` фіксує переповнення.
3. VFS скидає вміст буфера, викликає `dev_seq_stop()`, подвоює розмір пам'яті до 8192 байтів через `kvmalloc()`, і повторно викликає `dev_seq_start()` з початкової позиції.
4. Процедура повторюється геометрично (16 КБ, 32 КБ...), доки буфер не вмістить усю порцію виводу.

Такий підхід повністю захищає модуль від помилок переповнення буфера: драйвер зосереджується виключно на логіці форматування окремого вузла, а ядро самостійно підбирає необхідний обсяг пам'яті під будь-який масив даних.
