# ⚙️ Реєстрація модуля LSM та робота зі зміщеннями контексту

Цей практичний посібник описує повний цикл розробки та взаємодії з каркасом модулів безпеки Linux (LSM Stacking) на двох рівнях системного програмування:
1. **Рівень ядра (Kernel Space C):** Створення та реєстрація статично скомпільованого модуля LSM, який запитує власний блок пам'яті (security blob) для об'єктів `struct task_struct`, розраховує зміщення (offsets), налаштовує збірку в Kconfig та перехоплює файлові операції VFS.
2. **Рівень користувача (User Space UAPI):** Написання утиліти мовами **C** та ідіоматичною **C++23** для інспектування активного стеку LSM через віртуальні файлові системи та системні виклики ядра Linux 6.8+.

## Архітектурний план розробки

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Kernel Space (C Модуль)                         │
│                                                                        │
│ 1. DEFINE_LSM(demo_lsm) ──► 2. lsm_blob_sizes (.lbs_task = sizeof)    │
│                                     │                                  │
│ 3. security_add_hooks() ◄───────────┴──► 4. Обчислення demo_blob_offset│
│                                                                        │
│ 5. Hook: demo_file_open() ──► current->security + demo_blob_offset     │
└────────────────────────────────────────────────────────────────────────┘
                                   ▲
                                   │ /sys/kernel/security/lsm
                                   │ sys_lsm_list_modules()
┌──────────────────────────────────┴─────────────────────────────────────┐
│                      User Space (Утиліта C / C++)                      │
│                                                                        │
│ inspect_sysfs_lsm() ──► Зчитування /sys/kernel/security/lsm            │
│ inspect_syscall_lsm() ──► Виклик lsm_list_modules(ids, &size, 0)       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Частина 1: Реалізація та інтеграція модуля ядра (Kernel Space C)

Розробка нового модуля безпеки в ядрі Linux вимагає глибокого розуміння того, як ядро обробляє пам'ять об'єктів під час їхнього створення й знищення. Усі сучасні модулі LSM є статично скомпільованими компонентами ядра (in-tree modules). Можливість завантажувати LSM як динамічні модулі ядра (LKM через `insmod`) була свідомо вилучена з ядра Linux 2.6.24 з міркувань безпеки: руткіти могли б використовувати реєстрацію гачків для підміни системних викликів або приховування процесів.

### Механізм розподілу пам'яті та ініціалізації

Коли ядро Linux створює новий процес (системні виклики `clone` або `fork`), підсистема управління завданнями виділяє структуру `struct task_struct` із використанням спеціалізованого кешу розподільника пам'яті SLUB (`task_struct_cachep`). Під час цього виділення ядро автоматично виділяє єдиний неперервний блок пам'яті розміром, який дорівнює сумі розмірів блоків усіх зареєстрованих модулів LSM.

Вказівник `task_struct->security` ініціалізується адресою цього спільного блоку. Кожен модуль отримує своє власне цілочисельне зміщення (`offset`), обчислене під час виконання функції `security_init()`.

Нижче наведено повну реалізацію навчального модуля ядра `demo_lsm.c`.

```c
/* security/demo_lsm/demo_lsm.c */
#include <linux/init.h>
#include <linux/lsm_hooks.h>
#include <linux/sysfs.h>
#include <linux/cred.h>
#include <linux/fs.h>
#include <linux/err.h>
#include <linux/printk.h>

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Minimal Stacked LSM Demonstration Module");
MODULE_AUTHOR("Antigravity Kernel Team");

/* 
 * Внутрішній контекст безпеки нашого модуля.
 * Ця структура зберігатиметься у спільному блоці пам'яті task_struct->security
 * для кожного процесу в системі.
 */
struct demo_task_blob {
	u32 magic_tag;        /* Маркер стану перевірки (0xDEADBEEF для відмови) */
	u32 audit_counter;    /* Лічильник відкритих файлів даним процесом */
};

/* 
 * Змінна для збереження зміщення (offset) нашого блоку у байтах.
 * Позначена як __lsm_ro_after_init, що робить її захищеною від запису
 * після завершення етапу ініціалізації ядра підсистемою MMU.
 */
static int demo_blob_offset __lsm_ro_after_init;

/* 
 * Функція-гачок перехоплення файлових операцій VFS.
 * Викликається з do_dentry_open() під час спроби процесу відкрити файл.
 */
static int demo_file_open(struct file *file)
{
	struct demo_task_blob *blob;
	
	/* 
	 * Отримуємо вказівник на наш конкретний слот у спільному блоці пам'яті.
	 * current->security вказує на початок загального блоку.
	 */
	blob = current->security + demo_blob_offset;
	blob->audit_counter++;

	/* 
	 * Демонстрація перевірки політики: якщо у контексті процесу встановлено
	 * спеціальний маркер 0xDEADBEEF, модуль відхиляє відкриття файлу,
	 * повертаючи системну помилку -EACCES (Permission denied).
	 */
	if (unlikely(blob->magic_tag == 0xDEADBEEF)) {
		pr_warn_ratelimited("Demo_LSM: Відхилено відкриття файлу для PID %d (всього спроб: %u)\n",
				    current->pid, blob->audit_counter);
		return -EACCES;
	}

	return 0; /* Операцію дозволено всіма правилами модуля */
}

/* 
 * Таблиця гачків, які реєструє наш модуль у списку security_hook_heads.
 */
static struct security_hook_list demo_hooks[] __lsm_ro_after_init = {
	LSM_HOOK_INIT(file_open, demo_file_open),
};

/* 
 * Оголошення запитуваних розмірів блоків пам'яті.
 * Запитуємо у ядра розмір sizeof(struct demo_task_blob) під об'єкти task_struct.
 */
static struct lsm_blob_sizes demo_blob_sizes __lsm_ro_after_init = {
	.lbs_task = sizeof(struct demo_task_blob),
};

/* Ідентифікатор модуля у системі LSM UAPI */
static const struct lsm_id demo_lsmid = {
	.name = "demo_lsm",
	.id = 99,
};

/* 
 * Функція ініціалізації модуля під час стартів ядра.
 */
static int __init demo_lsm_init(void)
{
	/* 
	 * До цього моменту ядро вже переписало demo_blob_sizes.lbs_task:
	 * замість запитаного розміру там лежить наше зміщення у спільному
	 * блоці пам'яті. Запам'ятовуємо його й реєструємо гачки.
	 */
	demo_blob_offset = demo_blob_sizes.lbs_task;
	security_add_hooks(demo_hooks, ARRAY_SIZE(demo_hooks), &demo_lsmid);
	pr_info("Demo_LSM: Зареєстровано успішно! Зміщення task_blob = %d байт\n",
		demo_blob_offset);
	return 0;
}

/* 
 * Реєстрація модуля у спеціальній секції ELF .lsm_info.init
 */
DEFINE_LSM(demo_lsm) = {
	.name = "demo_lsm",
	.lsmid = &demo_lsmid,
	.init = demo_lsm_init,
	.blobs = &demo_blob_sizes,
};
```

### Інтеграція модуля в систему збірки Kconfig та Makefile

Щоб модуль скомпілювався у складі ядра Linux, у директорії `security/` створюється піддерево `security/demo_lsm/` та додаються файли конфігурації.

У файл `security/Kconfig` додається перемикач конфігурації:

```text
config SECURITY_DEMO_LSM
	bool "Demo Security Module support"
	depends on SECURITY
	default y
	help
	  Цей параметр включає демонстраційний модуль безпеки Demo_LSM,
	  який використовує механізм LSM Stacking для виділення контексту task_blob.
```

У файл `security/Makefile` додається рядок збірки:

```makefile
obj-$(CONFIG_SECURITY_DEMO_LSM) += demo_lsm/
```

Файл `security/demo_lsm/Makefile`:

```makefile
obj-$(CONFIG_SECURITY_DEMO_LSM) += demo_lsm.o
```

Після перекомпіляції ядра модуль автоматично реєструється в загальному ланцюгу гачків під час старту ядра.

---

## Частина 2: Інспектування активного стеку в користувацькому просторі

Програма користувача може перевірити список активних модулів LSM у системі двома шляхами:
1. Зчитати текстовий список через віртуальну файлову систему sysfs за шляхом `/sys/kernel/security/lsm`.
2. Виконати системний виклик `lsm_list_modules()` (доступний у ядрі Linux 6.8+).

Розглянемо практичну реалізацію утиліти інспектування користувацького простору, імплементовану у вигляді двох паралельних вкладок: **C** та ідіоматичний **C++23**.

:::tabs
```c
/* lsm_inspector.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <errno.h>
#include <stdint.h>

#ifndef __NR_lsm_list_modules
#define __NR_lsm_list_modules 461
#endif

#ifndef __NR_lsm_get_self_attr
#define __NR_lsm_get_self_attr 459
#endif

static void inspect_sysfs_lsm(void)
{
	int fd = open("/sys/kernel/security/lsm", O_RDONLY);
	if (fd < 0) {
		perror("open /sys/kernel/security/lsm failed");
		return;
	}

	char buffer[512];
	ssize_t bytes_read = read(fd, buffer, sizeof(buffer) - 1);
	close(fd);

	if (bytes_read > 0) {
		buffer[bytes_read] = '\0';
		/* Видаляємо символ переходу рядка наприкінці */
		char *newline = strchr(buffer, '\n');
		if (newline) *newline = '\0';
		printf("[sysfs] Активні модулі LSM (порядок виконання): %s\n", buffer);
	}
}

static void inspect_syscall_lsm(void)
{
	uint64_t ids[16];
	uint32_t size = sizeof(ids);

	long ret = syscall(__NR_lsm_list_modules, ids, &size, 0);
	if (ret < 0) {
		if (errno == ENOSYS) {
			printf("[syscall] lsm_list_modules не підтримується цим ядром (< 6.8).\n");
		} else {
			perror("[syscall] lsm_list_modules failed");
		}
		return;
	}

	printf("[syscall] Виявлено %ld активних модулів (IDs):\n", ret);
	for (long i = 0; i < ret; i++) {
		printf("  - Module [%ld]: ID 0x%lx\n", i, (unsigned long)ids[i]);
	}
}

int main(void)
{
	printf("=== Інспектор стеку Linux Security Modules (C Interface) ===\n");
	inspect_sysfs_lsm();
	inspect_syscall_lsm();
	return 0;
}
```
```cpp
// lsm_inspector.cpp
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <string_view>
#include <cstdint>
#include <cerrno>
#include <cstring>
#include <unistd.h>
#include <sys/syscall.h>
#include <expected>

#ifndef __NR_lsm_list_modules
#define __NR_lsm_list_modules 461
#endif

namespace lsm {

// Безпечне зчитування конфігурації sysfs за допомогою C++ iostreams та RAII
std::expected<std::string, std::string> read_sysfs_active_lsms() {
    std::ifstream file("/sys/kernel/security/lsm");
    if (!file.is_open()) {
        return std::unexpected("Не вдалося відкрити /sys/kernel/security/lsm (перевірте наявність securityfs)");
    }
    std::string line;
    if (std::getline(file, line)) {
        return line;
    }
    return std::unexpected("Файл /sys/kernel/security/lsm порожній");
}

// Прямий виклик lsm_list_modules із поверненням типу std::expected (C++23)
std::expected<std::vector<std::uint64_t>, std::string> query_lsm_ids_syscall() {
    std::vector<std::uint64_t> ids(16);
    std::uint32_t size = static_cast<std::uint32_t>(ids.size() * sizeof(std::uint64_t));

    const long ret = ::syscall(__NR_lsm_list_modules, ids.data(), &size, 0);
    if (ret < 0) {
        if (errno == ENOSYS) {
            return std::unexpected("Системний виклик lsm_list_modules відсутній (потрібне ядро Linux >= 6.8)");
        }
        return std::unexpected(std::string("Помилка виконання lsm_list_modules: ") + std::strerror(errno));
    }

    ids.resize(static_cast<std::size_t>(ret));
    return ids;
}

} // namespace lsm

int main() {
    std::cout << "=== Інспектор стеку Linux Security Modules (C++23 UAPI) ===\n";

    // 1. Перевірка sysfs
    if (auto sysfs_res = lsm::read_sysfs_active_lsms(); sysfs_res.has_value()) {
        std::cout << "[sysfs] Активні модулі LSM (порядок виконання): " << *sysfs_res << "\n";
    } else {
        std::cerr << "[sysfs помилка] " << sysfs_res.error() << "\n";
    }

    // 2. Перевірка системного виклику
    if (auto ids_res = lsm::query_lsm_ids_syscall(); ids_res.has_value()) {
        std::cout << "[syscall] Виявлено " << ids_res->size() << " активних модулів у стеку (ID):\n";
        std::size_t idx = 0;
        for (const auto id : *ids_res) {
            std::cout << "  - Module [" << idx++ << "]: ID 0x" << std::hex << id << std::dec << "\n";
        }
    } else {
        std::cerr << "[syscall помилка] " << ids_res.error() << "\n";
    }

    return 0;
}
```
:::

---

## Інженерні пастки, відлагодження та крайові випадки

Під час розробки та експлуатації стекованих модулів LSM виникають специфічні проблеми, пов'язані з порядком ініціалізації, зсувами пам'яті та налагодженням.

### 1. Рання вибірка пам'яті (Early Initialization Races)

Якщо модуль прочитає `demo_blob_sizes.lbs_task` до того, як ядро завершить обчислення розмірів блоків у `security_init()`, він дістане не зміщення, а власний запитаний розмір — і писатиме поверх чужого слота, найімовірніше поверх контексту першого модуля в блоці. Саме тому зміщення запам'ятовують не раніше за функцію ініціалізації модуля, яку ядро викликає вже після розрахунку.

Від іншої біди — пошкодження вже обчисленого зміщення під час роботи системи — захищає окремий засіб: зміщення оголошують з макросом `__lsm_ro_after_init`:

```c
static int demo_blob_offset __lsm_ro_after_init;
```

Цей макрос розміщує змінну в секції `.data..ro_after_init`. Після завершення ініціалізації ядра сторінки цієї секції позначаються у таблицях сторінок пам'яті (MMU) як «лише для читання» (`read-only`), унеможливлюючи її випадкове пошкодження чи зловмисну модифікацію.

### 2. Вирівнювання структур у пам'яті (Cache Line Alignment)

При оголошенні полів у `struct lsm_blob_sizes` важливо враховувати вирівнювання типів на архітектурах x86_64 та ARM64. Якщо модуль оголошує структуру з непарним розміром (наприклад, 5 байт), ядро автоматично вирівнює наступний слот до межі 4 або 8 байт. Ігнорування цього правила при ручному обчисленні адреси призведе до некоректного зсуву покажчиків і читання пошкоджених даних.

### 3. Відлагодження виконання за допомогою ftrace та bpftrace

Для перевірки порядку виконання стекованих гачків у реальному ядрі можна використовувати інструмент динамічного трасування `bpftrace`. Оскільки гачки LSM є звичайними функціями ядра, до них можна підключити kprobe:

```bash
# Трасування викликів security_file_open з виведенням імені процесу та PID
$ sudo bpftrace -e 'kprobe:security_file_open { printf("%s (PID %d) opens file\n", comm, pid); }'
```

Цей спосіб дозволяє переконатися, що гачок відпрацьовує на кожній операції `openat`, а стекування модулів не викликає взаємного блокування процесів (deadlocks).

### 4. Обробка помилки `-E2BIG` у системних викликах

При роботі із системним викликом `lsm_get_self_attr()` розмір відгуку залежить від кількості активованих модулів та довжини їхніх рядків контексту. Якщо під час виконання системного виклику додається новий динамічний профіль AppArmor або Landlock, переданий буфер може стати занадто малим. 

Користувацька програма повинна завжди обробляти код помилки `-E2BIG`:

```c
uint32_t size = 0;
long ret = syscall(__NR_lsm_get_self_attr, LSM_ATTR_CURRENT, NULL, &size, 0);
if (ret < 0 && errno == E2BIG) {
    /* Ядро поклало в size потрібну кількість байт: виділяємо й повторюємо */
    struct lsm_ctx *ctx = malloc(size);
    if (ctx) {
        ret = syscall(__NR_lsm_get_self_attr, LSM_ATTR_CURRENT, ctx, &size, 0);
        free(ctx);
    }
}
```

### 5. Несумісність викликів `setuid` та зміна контексту

При зміні UID процесу системним викликом `setuid()` ядро викликає гачок `security_task_fix_setuid()`. Тут стекування рятує сама механіка облікових даних: модулі правлять не чинні `cred`, а їхню свіжу копію, підготовану `prepare_creds()` (саме на ній працює гачок `security_cred_prepare()`). Якщо будь-який модуль у стеку відхиляє зміну, копію просто викидають через `abort_creds()`, а процес лишається зі старими обліковими даними — відкочувати чужі часткові правки нікому не доводиться.
