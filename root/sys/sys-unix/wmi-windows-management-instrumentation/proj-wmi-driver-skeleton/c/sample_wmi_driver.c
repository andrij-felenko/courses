// sample_wmi_driver.c — Драйвер ядра Linux для обслуговування WMI-пристрою
#include <linux/module.h>
#include <linux/init.h>
#include <linux/acpi.h>
#include <linux/wmi.h>
#include <linux/device.h>

#define DEMO_WMI_GUID "12345678-ABCD-1234-5678-1234567890AB"
#define DEMO_METHOD_ID 0x01

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Linux Kernel Developer");
MODULE_DESCRIPTION("Sample ACPI-WMI Driver for Linux");

// Системні атрибути sysfs для тестування з простору користувача
static ssize_t demo_control_show(struct device *dev, struct device_attribute *attr, char *buf)
{
    return sysfs_emit(buf, "WMI driver active\n");
}

static ssize_t demo_control_store(struct device *dev, struct device_attribute *attr, const char *buf, size_t count)
{
    struct wmi_device *wdev = to_wmi_device(dev);
    u32 val;

    if (kstrtou32(buf, 10, &val))
        return -EINVAL;

    dev_info(dev, "Запис у sysfs: нове значення %u\n", val);
    return count;
}
static DEVICE_ATTR_RW(demo_control);

static struct attribute *demo_attrs[] = {
    &dev_attr_demo_control.attr,
    NULL,
};
ATTRIBUTE_GROUPS(demo);

static int demo_wmi_probe(struct wmi_device *wdev, const void *context)
{
    struct acpi_buffer input;
    struct acpi_buffer output = { ACPI_ALLOCATE_BUFFER, NULL };
    union acpi_object *obj;
    u32 in_value = 100;
    acpi_status status;

    dev_info(&wdev->dev, "WMI пристрій підключено (GUID: %s)\n", DEMO_WMI_GUID);

    // Підготовка вхідних даних для WMI-методу
    input.length = sizeof(u32);
    input.pointer = &in_value;

    // Виклик WMI-методу через сучасне API ядра
    status = wmidev_evaluate_method(wdev, 0, DEMO_METHOD_ID, &input, &output);
    if (ACPI_FAILURE(status)) {
        dev_err(&wdev->dev, "Помилка виконання WMI-методу: 0x%x\n", status);
        return -EIO;
    }

    obj = (union acpi_object *)output.pointer;
    if (obj && obj->type == ACPI_TYPE_INTEGER) {
        dev_info(&wdev->dev, "Отримано результат від WMI: %llu\n", obj->integer.value);
    }

    kfree(output.pointer);
    return 0;
}

static void demo_wmi_remove(struct wmi_device *wdev)
{
    dev_info(&wdev->dev, "WMI пристрій відключено\n");
}

static void demo_wmi_notify(struct wmi_device *wdev, union acpi_object *data)
{
    if (data && data->type == ACPI_TYPE_INTEGER) {
        dev_info(&wdev->dev, "Отримано WMI сповіщення: код 0x%llx\n", data->integer.value);
    }
}

static const struct wmi_device_id demo_wmi_id_table[] = {
    { DEMO_WMI_GUID, NULL },
    { }
};
MODULE_DEVICE_TABLE(wmi, demo_wmi_id_table);

static struct wmi_driver demo_wmi_driver = {
    .driver = {
        .name = "demo_wmi_driver",
        .dev_groups = demo_groups,
    },
    .id_table = demo_wmi_id_table,
    .probe = demo_wmi_probe,
    .remove = demo_wmi_remove,
    .notify = demo_wmi_notify,
};

module_wmi_driver(demo_wmi_driver);
