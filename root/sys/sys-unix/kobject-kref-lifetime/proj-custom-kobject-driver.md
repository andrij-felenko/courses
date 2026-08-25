# ⚙️ Практична реалізація підсистеми з kobject, kref та безпечним деструктором

Цей практичний проєкт демонструє створення повноцінного завантажуваного модуля ядра Linux (LKM), який інтегрує структуру `struct kobject` у користувацький тип даних `struct sample_device`, створює власну таблицю методів `kobj_type`, експортує керовані файли-атрибути у віртуальну файлову систему `sysfs` та забезпечує повний захист від стану гонитви під час вивантаження завдяки асинхронному зворотному виклику `release`.

## 1. Архітектура та вихідний код модуля ядра

Модуль реалізує віртуальний пристрій, який експортує каталог `/sys/kernel/sample_device/` з двома атрибутами:
- **`baud_rate`**: числовий параметр швидкості передачі даних, доступний для читання та запису процесами з правами `0644`.
- **`status`**: текстовий діагностичний рядок стану, доступний виключно для читання (`0444`).

Внутрішня структура `struct sample_device` динамічно виділяється в оперативній пам'яті ядра під час завантаження модуля. Вона містить у собі вбудований екземпляр `struct kobject`, завдяки чому весь життєвий цикл структури керується виключно через атомарний лічильник посилань `kref`.

```c
// sample_kobject_module.c
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/kobject.h>
#include <linux/slab.h>
#include <linux/sysfs.h>
#include <linux/string.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Kernel Architecture Guide");
MODULE_DESCRIPTION("Dynamic kobject embedding and lifetime management example");

/* Власна структура драйвера, що інкапсулює апаратний або логічний контекст */
struct sample_device {
    int dev_id;
    int baud_rate;
    char status_str[32];
    struct kobject kobj; /* Вбудований atomic kobject */
};

/* Специфічний атрибут для нашого типу пристрою */
struct sample_attribute {
    struct attribute attr;
    ssize_t (*show)(struct sample_device *dev, struct sample_attribute *attr, char *buf);
    ssize_t (*store)(struct sample_device *dev, struct sample_attribute *attr, const char *buf, size_t count);
};

#define to_sample_attr(a) container_of(a, struct sample_attribute, attr)

/* ── Зворотний виклик звільнення пам'яті (Деструктор) ────────────────────── */
static void sample_device_release(struct kobject *kobj)
{
    struct sample_device *dev = container_of(kobj, struct sample_device, kobj);
    pr_info("sample_device: release callback executed for dev_id=%d. Freeing memory at %p\n",
            dev->dev_id, dev);
    kfree(dev);
}

/* ── Диспетчеризація операцій sysfs ─────────────────────────────────────── */
static ssize_t sample_attr_show(struct kobject *kobj, struct attribute *attr, char *buf)
{
    struct sample_device *dev = container_of(kobj, struct sample_device, kobj);
    struct sample_attribute *sattr = to_sample_attr(attr);

    if (!sattr->show)
        return -EIO;
    return sattr->show(dev, sattr, buf);
}

static ssize_t sample_attr_store(struct kobject *kobj, struct attribute *attr, const char *buf, size_t count)
{
    struct sample_device *dev = container_of(kobj, struct sample_device, kobj);
    struct sample_attribute *sattr = to_sample_attr(attr);

    if (!sattr->store)
        return -EIO;
    return sattr->store(dev, sattr, buf, count);
}

static const struct sysfs_ops sample_sysfs_ops = {
    .show  = sample_attr_show,
    .store = sample_attr_store,
};

/* ── Обробники окремих атрибутів ────────────────────────────────────────── */
static ssize_t baud_rate_show(struct sample_device *dev, struct sample_attribute *attr, char *buf)
{
    return sysfs_emit(buf, "%d\n", dev->baud_rate);
}

static ssize_t baud_rate_store(struct sample_device *dev, struct sample_attribute *attr, const char *buf, size_t count)
{
    int val, ret;
    ret = kstrtoint(buf, 10, &val);
    if (ret < 0)
        return ret;
    if (val <= 0 || val > 3000000)
        return -EINVAL;
    dev->baud_rate = val;
    return count;
}

static ssize_t status_show(struct sample_device *dev, struct sample_attribute *attr, char *buf)
{
    return sysfs_emit(buf, "%s\n", dev->status_str);
}

static struct sample_attribute attr_baud = {
    .attr = { .name = "baud_rate", .mode = 0644 },
    .show = baud_rate_show,
    .store = baud_rate_store,
};

static struct sample_attribute attr_status = {
    .attr = { .name = "status", .mode = 0444 },
    .show = status_show,
    .store = NULL,
};

static struct attribute *sample_default_attrs[] = {
    &attr_baud.attr,
    &attr_status.attr,
    NULL,
};
ATTRIBUTE_GROUPS(sample_default);

/* ── Тип об'єкта kobj_type ──────────────────────────────────────────────── */
static const struct kobj_type sample_ktype = {
    .release        = sample_device_release,
    .sysfs_ops      = &sample_sysfs_ops,
    .default_groups = sample_default_groups,
};

static struct sample_device *g_device = NULL;

/* ── Ініціалізація та вивантаження модуля ───────────────────────────────── */
static int __init sample_module_init(void)
{
    int ret;
    pr_info("sample_device: initializing module\n");

    /* 1. Виділення пам'яті під зовнішній контейнер */
    g_device = kzalloc(sizeof(*g_device), GFP_KERNEL);
    if (!g_device)
        return -ENOMEM;

    g_device->dev_id = 42;
    g_device->baud_rate = 115200;
    strscpy(g_device->status_str, "OPERATIONAL_OK", sizeof(g_device->status_str));

    /* 2. Ініціалізація kobject та створення каталогу в /sys/kernel/ */
    ret = kobject_init_and_add(&g_device->kobj, &sample_ktype, kernel_kobj, "sample_device");
    if (ret) {
        pr_err("sample_device: failed to create kobject (err=%d)\n", ret);
        /* kobject_put обов'язковий навіть при збої додавання для очищення імені */
        kobject_put(&g_device->kobj);
        g_device = NULL;
        return ret;
    }

    pr_info("sample_device: registered successfully at /sys/kernel/sample_device/\n");
    return 0;
}

static void __exit sample_module_exit(void)
{
    pr_info("sample_device: exiting module, tearing down kobject\n");
    if (g_device) {
        /* 1. Видалення каталогу з sysfs (блокує нові open/read/write) */
        kobject_del(&g_device->kobj);

        /* 2. Скидання власного посилання модуля.
         * Коли всі відкриті дескриптори закриються, ядро викличе sample_device_release() */
        kobject_put(&g_device->kobj);
        g_device = NULL;
    }
}

module_init(sample_module_init);
module_exit(sample_module_exit);
```

## 2. Покроковий розбір життєвого циклу драйвера

### Виділення пам'яті та ініціалізація структури

Під час виконання функції `sample_module_init()` драйвер звертається до ядра за пам'яттю за допомогою виклику `kzalloc(sizeof(*g_device), GFP_KERNEL)`. Алокатор SLUB повертає безперервну ділянку оперативної пам'яті ядра, заповнену нулями.

Функція `kobject_init_and_add()` виконує два послідовні архітектурні кроки:
1. `kobject_init()` призначає вказівник на статичну таблицю методів `sample_ktype`, встановлює внутрішній прапорець стану `state_initialized = 1` та викликає `kref_init(&kobj->kref)`, встановлюючи початкове значення лічильника посилань рівним `1`.
2. `kobject_add()` форматує рядок імені `"sample_device"`, встановлює батьківським об'єктом глобальний `kernel_kobj` (що відповідає системному каталогу `/sys/kernel/`) і створює новий каталог у sysfs. Після цього ядро автоматично створює всі файли атрибутів, перелічені в масиві груп `sample_default_groups`.

### Обробка запитів sysfs через `container_of`

Коли процес у просторі користувача виконує читання файла `/sys/kernel/sample_device/baud_rate`, шар VFS перенаправляє запит до функції `sample_attr_show()`. Сигнатура уніфікованого інтерфейсу ядра містить лише базовий вказівник `struct kobject *kobj` та дескриптор атрибута `struct attribute *attr`.

Для безпечного доступу до конкретних полів структури драйвера застосовуються два макроси зміщення адреси:
- `container_of(kobj, struct sample_device, kobj)` обчислює базову адресу екземпляра `sample_device`, віднімаючи зміщення поля `kobj` від переданого вказівника.
- `to_sample_attr(attr)` знаходить адресу обгортки `sample_attribute`, у якій збережено вказівник на спеціалізований метод `baud_rate_show()`.

Функція `sysfs_emit(buf, "%d\n", dev->baud_rate)` записує відформатоване значення у наданий ядром сторінковий буфер, автоматично гарантуючи захист від виходу за межі розміру сторінки `PAGE_SIZE` (4096 байтів).

### Двофазне вивантаження модуля

Коли адміністратор викликає `rmmod sample_kobject_module`, функція `sample_module_exit()` виконує дві строго розмежовані операції:
1. `kobject_del(&g_device->kobj)`: видаляє каталог `sample_device` та його атрибути з дерева `sysfs`. Підсистема `kernfs` чекає завершення поточних операцій `show()` або `store()` і переводить вузли у недійсний стан. Будь-який наступний системний виклик `read()` чи `write()` на відкритому файлі негайно поверне помилку `-ENODEV`.
2. `kobject_put(&g_device->kobj)`: зменшує лічильник `kref` на одиницю. Якщо жоден процес у просторі користувача не тримає відкритих файлів, лічильник миттєво досягає нуля, і ядро синхронно викликає `sample_device_release()`, яка виконує `kfree(dev)`. Якщо ж відкриті дескриптори існують, лічильник залишається рівним кількості відкритих файлів, і фізичне звільнення пам'яті відкладається до виклику `close()` останнім процесом.

---

## 3. Утиліта стрес-тестування простору користувача

Для перевірки стійкості ядра до гонитви за часом життя утиліта запускає пул паралельних потоків, які безперервно відкривають, зчитують та модифікують атрибути `/sys/kernel/sample_device/baud_rate` під час виконання команди вивантаження модуля `rmmod`.

:::tabs
```c
// test_kobject_stress.c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <pthread.h>
#include <string.h>
#include <stdbool.h>

#define SYSFS_PATH "/sys/kernel/sample_device/baud_rate"
#define THREAD_COUNT 8

static volatile bool running = true;

static void *reader_thread(void *arg)
{
    long id = (long)arg;
    char buffer[64];

    while (running) {
        int fd = open(SYSFS_PATH, O_RDONLY);
        if (fd < 0) {
            // Файл видалено ядром під час вивантаження модуля
            usleep(1000);
            continue;
        }

        ssize_t bytes = read(fd, buffer, sizeof(buffer) - 1);
        if (bytes > 0) {
            buffer[bytes] = '\0';
        }
        close(fd);
        usleep(500);
    }
    return NULL;
}

static void *writer_thread(void *arg)
{
    const char *values[] = {"9600", "19200", "38400", "57600", "115200", "230400"};
    int idx = 0;

    while (running) {
        int fd = open(SYSFS_PATH, O_WRONLY);
        if (fd >= 0) {
            const char *val = values[idx % 6];
            write(fd, val, strlen(val));
            close(fd);
            idx++;
        }
        usleep(1000);
    }
    return NULL;
}

int main(void)
{
    pthread_t threads[THREAD_COUNT];
    printf("[STRESS] Запуск %d потоків читання/запису до %s\n", THREAD_COUNT, SYSFS_PATH);

    for (long i = 0; i < THREAD_COUNT - 1; i++) {
        pthread_create(&threads[i], NULL, reader_thread, (void *)i);
    }
    pthread_create(&threads[THREAD_COUNT - 1], NULL, writer_thread, NULL);

    printf("[STRESS] Тест активний. Виконайте 'rmmod sample_kobject_module' в іншому терміналі.\n");
    printf("[STRESS] Очікування 10 секунд...\n");
    sleep(10);

    running = false;
    for (int i = 0; i < THREAD_COUNT; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("[STRESS] Тест завершено без збоїв системи.\n");
    return 0;
}
```
```cpp
// test_kobject_stress.cpp
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <thread>
#include <atomic>
#include <chrono>
#include <array>

namespace {
    constexpr const char* SYSFS_PATH = "/sys/kernel/sample_device/baud_rate";
    constexpr int READER_THREADS = 7;
    std::atomic<bool> g_running{true};

    void reader_worker(int id) {
        std::string line;
        while (g_running.load(std::memory_order_relaxed)) {
            std::ifstream file(SYSFS_PATH);
            if (file.is_open()) {
                if (std::getline(file, line)) {
                    // Успішне зчитування атрибута kernfs
                }
            } else {
                // Модуль вивантажується або файл видалено
                std::this_thread::sleep_for(std::chrono::milliseconds(1));
            }
            std::this_thread::sleep_for(std::chrono::microseconds(500));
        }
    }

    void writer_worker() {
        const std::array<std::string, 6> values = {"9600", "19200", "38400", "57600", "115200", "230400"};
        size_t idx = 0;

        while (g_running.load(std::memory_order_relaxed)) {
            std::ofstream file(SYSFS_PATH);
            if (file.is_open()) {
                file << values[idx % values.size()] << std::endl;
                idx++;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }
    }
}

int main() {
    std::cout << "[STRESS-CPP] Запуск потоків тестування sysfs: " << SYSFS_PATH << std::endl;

    std::vector<std::thread> workers;
    workers.reserve(READER_THREADS + 1);

    for (int i = 0; i < READER_THREADS; ++i) {
        workers.emplace_back(reader_worker, i);
    }
    workers.emplace_back(writer_worker);

    std::cout << "[STRESS-CPP] Потоки активні. Спробуйте вивантажити модуль ядра (rmmod).\n";
    std::this_thread::sleep_for(std::chrono::seconds(10));

    g_running.store(false, std::memory_order_relaxed);
    for (auto& t : workers) {
        if (t.joinable()) {
            t.join();
        }
    }

    std::cout << "[STRESS-CPP] Тестування завершено коректно.\n";
    return 0;
}
```
:::

---

## 4. Збирання, виконання та аналіз журналу ядра

Для компіляції модуля використовується стандартний файл збирання `Makefile` системи Kbuild:

```makefile
obj-m += sample_kobject_module.o

KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	make -C $(KDIR) M=$(PWD) modules
	$(CC) -O2 -pthread test_kobject_stress.c -o test_stress_c
	g++ -O2 -std=c++20 test_kobject_stress.cpp -o test_stress_cpp

clean:
	make -C $(KDIR) M=$(PWD) clean
	rm -f test_stress_c test_stress_cpp
```

### Послідовність перевірки стійкості до вивантаження

1. Завантаження модуля в систему:
   ```bash
   sudo insmod sample_kobject_module.ko
   ```
2. Перевірка створення файлів у sysfs:
   ```bash
   ls -la /sys/kernel/sample_device/
   cat /sys/kernel/sample_device/baud_rate
   cat /sys/kernel/sample_device/status
   ```
3. Запуск утиліти стрес-тестування в одному терміналі:
   ```bash
   ./test_stress_cpp
   ```
4. Одночасне вивантаження модуля в іншому терміналі під піковим навантаженням:
   ```bash
   sudo rmmod sample_kobject_module
   ```
5. Перегляд діагностичного журналу `dmesg`:
   ```bash
   dmesg | tail -n 10
   ```

У системному журналі відобразиться коректна послідовність викликів без жодних повідомлень про стан гонитви чи помилок KASAN:

```
[ 1420.102340] sample_device: initializing module
[ 1420.102512] sample_device: registered successfully at /sys/kernel/sample_device/
[ 1428.450110] sample_device: exiting module, tearing down kobject
[ 1428.451204] sample_device: release callback executed for dev_id=42. Freeing memory at ffff888104b2c180
```

Зверніть увагу: повідомлення про виконання деструктора `sample_device_release` з'являється після того, як вивантаження модуля ініціювало скидання посилання, а всі паралельні системні виклики успішно закрили дескриптори, гарантуючи нульовий рівень помилок `Use-After-Free`.

### Типові діагностичні пастки та їх усунення

1. **Помилка `EEXIST` під час `kobject_add`**: виникає, якщо драйвер намагається зареєструвати два об'єкти з однаковим ім'ям у межах одного батьківського каталогу. Ядро перевіряє унікальність імен за допомогою дерева червоно-чорних вузлів `kernfs_node`. При отриманні такої помилки драйвер повинен змінити шаблон іменування (наприклад, додавати числовий індекс `dev%d`) та викликати `kobject_put()`.
2. **Зависання `rmmod` у стані `D` (Uninterruptible Sleep)**: якщо деструктор `release` або обробник `kobject_del` намагається захопити м'ютекс, який вже утримується потоком, що виконує заблоковану операцію I/O, виникає класичний дедлок. Щоб уникнути цього, синхронізація між шаром VFS та внутрішніми даними драйвера має виконуватися через роздільні спінлоки або механізм RCU.
3. **Витік пам'яті імені при помилках ініціалізації**: функція `kobject_set_name()` копіює переданий рядок у динамічну пам'ять ядра за допомогою `kstrdup_const()`. Якщо після цього виклик `kobject_add()` завершився аварійно, але драйвер замість `kobject_put()` виконав прямий `kfree()`, виділений буфер імені назавжди залишається висіти в купі ядра (англ. *memory leak*). Виклик `kobject_put()` автоматично запускає очищення імені навіть для частково ініціалізованих об'єктів.
4. **Використання `kfree()` замість `devm_kfree()` у фреймворку керованих ресурсів**: якщо драйвер переходить на сучасний фреймворк керованих ресурсів `devres` (`devm_kzalloc`), життєвий цикл пам'яті прив'язується до структури `struct device`. Проте якщо всередині використовується власний незалежний `kobject`, його деструктор `release` не повинен конфліктувати з автоматичним очищенням `devres`.
