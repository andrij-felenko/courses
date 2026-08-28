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
