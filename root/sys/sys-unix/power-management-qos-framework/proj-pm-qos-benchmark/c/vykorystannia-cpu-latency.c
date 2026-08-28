#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/pm_qos.h>
#include <linux/slab.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("PM QoS Example Author");
MODULE_DESCRIPTION("Приклад драйвера з підключенням CPU Latency QoS");

static struct pm_qos_request my_driver_qos_req;

static int __init my_driver_init(void) {
    pr_info("my_driver: Реєстрація вимоги CPU Latency QoS (20 мкс)\n");

    // Додаємо запит на максимальну затримку пробудження CPU у 20 мкс
    cpu_latency_qos_add_request(&my_driver_qos_req, 20);

    return 0;
}

// Викликається при старті інтенсивного DMA-обміну даними
void my_driver_start_heavy_io(void) {
    pr_info("my_driver: Знижуємо межу затримки до 0 мкс (заборона сну)\n");
    // Робимо вимогу найжорсткішою: допустима затримка пробудження — нуль
    cpu_latency_qos_update_request(&my_driver_qos_req, 0);
}

// Викликається після завершення інтенсивного DMA-обміну даними
void my_driver_stop_heavy_io(void) {
    pr_info("my_driver: Повернення затримки до 20 мкс\n");
    // Повертаємо початкову вимогу
    cpu_latency_qos_update_request(&my_driver_qos_req, 20);
}

static void __exit my_driver_exit(void) {
    pr_info("my_driver: Видалення вимоги CPU Latency QoS\n");

    // Видаляємо запит з глобального списку агрегації
    cpu_latency_qos_remove_request(&my_driver_qos_req);
}

module_init(my_driver_init);
module_exit(my_driver_exit);
