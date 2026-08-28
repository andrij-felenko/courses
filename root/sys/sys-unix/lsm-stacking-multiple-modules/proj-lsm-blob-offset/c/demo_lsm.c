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
