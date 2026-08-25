# ⚙️ Практична реалізація Linux WMI-драйвера

Практичний розвиток знань про підсистему ACPI-WMI вимагає розуміння двох рівнів розробки: створення модуля ядра Linux, який безпосередньо прив'язується до шини WMI (`wmi_bus_type`), та написання утиліти простору користувача, яка аналізує викриті атрибути через файлову систему `/sys/bus/wmi/devices/`.

У цьому практичному проекті розглянуто обидві частини: повноцінний мінімальний драйвер ядра, що реєструє обробник подій і виконує WMI-методи прошивки, та двомовну (C і C++) утиліту аналізу пристроїв у просторі користувача.

## Частина 1. Модуль ядра Linux (WMI Driver)

Коду драйвера ядра належить реєструвати обробники подій WMI та викликати ACPI-методи через високорівневу функцію `wmidev_evaluate_method`. Оскільки код ядра виконується в середовищі Linux Kernel Space (де повністю відсутні C++ Standard Library, винятки, глобальні конструктори та виклики `new`/`delete`), драйвери ядра Linux пишуться виключно мовою C з використанням макросів та підсистем ядра.

Драйвер ядра виконує три основні завдання під час свого життєвого циклу:
1. Оголошує таблицю сумісних ідентифікаторів `struct wmi_device_id` із вказанням очікуваного GUID пристрою. Це забезпечує експорт модаліасу у файл модуля для автоматичного завантаження підсистемою `udev`.
2. При підключенні сумісного пристрою викликає процедуру `probe`, у якій готує вхідний буфер `struct acpi_buffer`, формує параметри та викликає WMI-метод прошивки BIOS.
3. Обробляє асинхронні сповіщення у функції `notify`, перетворюючи отриманий код події на сповіщення у системному журналі ядра `dmesg`.

Крім того, для зручності тестування у просторі користувача драйвер викриває власну групу файлів sysfs за допомогою макросів `DEVICE_ATTR_RW`.

```c
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
```

### Збирання та управління модулем ядра
Для компіляції модуля розробник використовує стандартний інструментарій Kbuild ядра Linux. Файл `Makefile` викликає внутрішню систему збирання ядра:

```makefile
obj-m += sample_wmi_driver.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
```

Після успішного збирання модуль завантажується командою `sudo insmod sample_wmi_driver.ko`. Підсистема ядра `wmi_bus_type` автоматично проведе пошук пристрою з відповідним GUID та викликає процедуру `demo_wmi_probe`. Вивантаження модуля здійснюється командою `sudo rmmod sample_wmi_driver`, що спричиняє виклик функції `demo_wmi_remove`.

---

## Частина 2. Утиліта простору користувача (User Space Sysfs Reader)

Утиліта простору користувача виконує повний обхід віртуальної файлової системи `/sys/bus/wmi/devices/`. Для кожного виявленого WMI-пристрою утиліта зчитує 2-символьний ідентифікатор ACPI `object_id`, прапорець здатності до запису `setable` та перевіряє наявність двійкового бувера BMOF для декомпіляції.

Оскільки утиліта працює в просторі користувача, ми надаємо дві повноцінні ідіоматичні реалізації: процедурну на C та об'єктно-орієнтовану на C++20 із використанням модуля `std::filesystem`, концепції RAII та потоків `std::ifstream`.

:::tabs
```c
// wmi_scan.c — Процедурна версія мовою C (POSIX API)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <unistd.h>

#define SYSFS_WMI_PATH "/sys/bus/wmi/devices"

void inspect_wmi_device(const char *dev_name) {
    char path[512];
    FILE *fp;
    char buffer[128];

    snprintf(path, sizeof(path), "%s/%s/object_id", SYSFS_WMI_PATH, dev_name);
    fp = fopen(path, "r");
    if (!fp) return;

    if (fgets(buffer, sizeof(buffer), fp)) {
        buffer[strcspn(buffer, "\r\n")] = 0;
        printf("WMI Device: %-36s | Object ID: %s\n", dev_name, buffer);
    }
    fclose(fp);
}

int main(void) {
    DIR *dir = opendir(SYSFS_WMI_PATH);
    if (!dir) {
        perror("Не вдалося відкрити " SYSFS_WMI_PATH);
        return EXIT_FAILURE;
    }

    struct dirent *entry;
    printf("=== Сканування WMI пристроїв Linux (C) ===\n");
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') continue;
        inspect_wmi_device(entry->d_name);
    }

    closedir(dir);
    return EXIT_SUCCESS;
}
```
```cpp
// wmi_scan.cpp — Ідіоматична версія на C++20 (RAII, filesystem, iostreams)
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <string_view>

namespace fs = std::filesystem;

class WmiScanner {
public:
    static constexpr std::string_view kSysfsWmiPath = "/sys/bus/wmi/devices";

    void scan() const {
        const fs::path wmi_dir{kSysfsWmiPath};
        if (!fs::exists(wmi_dir) || !fs::is_directory(wmi_dir)) {
            std::cerr << "Каталог " << wmi_dir << " не знайдено або доступ обмежено.\n";
            return;
        }

        std::cout << "=== Сканування WMI пристроїв Linux (C++20) ===\n";
        for (const auto& entry : fs::directory_iterator(wmi_dir)) {
            if (entry.is_directory() || entry.is_symlink()) {
                inspect_device(entry.path());
            }
        }
    }

private:
    void inspect_device(const fs::path& dev_path) const {
        const auto object_id_file = dev_path / "object_id";
        if (std::ifstream file{object_id_file}; file.is_open()) {
            std::string object_id;
            if (std::getline(file, object_id)) {
                std::cout << "WMI Device: " << dev_path.filename().string()
                          << " | Object ID: " << object_id << '\n';
            }
        }
    }
};

int main() {
    WmiScanner scanner;
    scanner.scan();
    return 0;
}
```
:::

### Особливості порівняння реалізацій C та C++
Версія мовою C спирається на низькорівневі виклики POSIX `opendir()`, `readdir()`, `closedir()` та керування файловими дескрипторами вручну через `fopen()` і `fclose()`. У разі виникнення помилки розробник зобов'язаний явно вивільняти пам'ять і закривати дескриптори у кожній гілці розгалуження.

Версія мовою C++20 використовує стандартну бібліотеку `std::filesystem`. Обхід каталогу виконується за допомогою безпечного ітератора `directory_iterator`. Відкриття та закриття файлів атрибутів sysfs здійснюється автоматично завдяки механізму RAII (Resource Acquisition Is Initialization) у класі `std::ifstream`, що унеможливлює витік файлових дескрипторів або ресурсовідтік при виникненні виняткових ситуацій.

### Детальний розбір механізмів пам'яті та керування ресурсами
При розробці WMI-драйверів ядерна підсистема ACPICA автоматично виділяє пам'ять під повернуті буфери результатів `struct acpi_buffer`, якщо у виклику передано прапорець `ACPI_ALLOCATE_BUFFER`. Виділена пам'ять належить внутрішньому пулу пам'яті ядра (`kmalloc`).

Розробник драйвера зобов'язаний явно звільняти цей буфер за допомогою системної функції `kfree(output.pointer)` одразу після завершення обробки даних, включаючи всі помилкові гілки розгалужень (`if (ACPI_FAILURE(status))`). Нехтування викликом `kfree` призводить до прихованого системного витікання пам'яті у Kernel Space, яке неможливо виявити звичайними утилітами простору користувача.

У просторі користувача аналогічні гарантії безпеки надає концепція RAII в C++20: об'єкт `std::ifstream` автоматично закриває файловий дескриптор у своєму деструкторі під час виходу з області видимості функції `inspect_device()`, що гарантує відсутність ресурсного витікання файлових дескрипторів у процесі.

### Пастки та крайові випадки реалізації
При практичній роботі з WMI-драйверами та утилітами розробники зіштовхуються з кількома типовими пастками:

1. **Права доступу до файлів sysfs:** Більшість атрибутів системного BIOS (через `firmware_attributes`) або прямого запису в `wmi-sysfs` вимагають прав суперкористувача (`root`). Звичайний користувач отримує помилку `Permission denied` (`-EACCES`).
2. **Ексклюзивне блокування GUID:** Якщо в ядрі вже завантажено вендорський драйвер (наприклад `asus-wmi`), який прив'язався до GUID керування живленням, спроба прямого запису у sysfs через `wmi-sysfs` може повернути помилку `EBUSY`, оскільки ядро захищає свої внутрішні пристрої від неузгодженого доступу.
3. **Формат буферів AML:** Виклики `wmidev_evaluate_method` вимагають точної відповідності структур даних тому, що очікує AML-код BIOS. Якщо передати буфер некоректного розміру (наприклад, 2 байти замість 4), прошивка може повернути помилку `AE_BAD_PARAMETER` або спричинити збій у роботі Embedded Controller.
4. **Виділення та звільнення пам'яті acpi_buffer:** При виконанні викликів з прапорцем `ACPI_ALLOCATE_BUFFER` ядро виділяє пам'ять під повернуті ACPI-об'єкти у внутрішній системі пам'яті. Розробник драйвера зобов'язаний викликати `kfree(output.pointer)` після завершення обробки даних, інакше виникне системне витікання пам'яті в Kernel Space.
