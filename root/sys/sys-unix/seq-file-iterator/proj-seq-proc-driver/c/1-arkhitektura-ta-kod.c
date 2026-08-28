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
