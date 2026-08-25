# ⚙️ Практика: написання драйвера з інтерфейсом configfs та інструмента керування

Нижче — робочий модуль ядра, який заводить власну підсистему `configfs` у `/sys/kernel/config/demo_target/`, розбір його небезпечних місць (виділення пам'яті, підрахунок посилань, крайні випадки, трасування через `ftrace`) і дві утиліти простору користувача — мовами C та C++, — які цим модулем керують.

## Архітектура драйвера модуля ядра `demo_configfs`

Драйвер ядра створює конфігураційну підсистему `/sys/kernel/config/demo_target/`. Головна мета коду — показати правильне розділення між фабричними методами створення груп, обробниками атрибутів та зворотновикликальним деструктором `release()`.

Оскільки простір ядра Linux не підтримує стандартну бібліотеку C++ та механізми винятків, код модуля реалізовано мовою C з дотриманням усіх вимог безпеки підрахунку посилань `ci_kref` та розподілу пам'яті SLUB.

```c
#include <linux/module.h>
#include <linux/init.h>
#include <linux/slab.h>
#include <linux/configfs.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Unix-Linux Reference Author");
MODULE_DESCRIPTION("ConfigFS Demo Subsystem Driver");

/* Власна структура об'єкта драйвера */
struct demo_item {
    int                     value;
    bool                    enabled;
    struct config_item      item;
};

/* Макрос безпечного отримання вказівника на структуру драйвера */
static inline struct demo_item *to_demo_item(struct config_item *item)
{
    return item ? container_of(item, struct demo_item, item) : NULL;
}

/* 1. Читання атрибута "value" */
static ssize_t demo_item_value_show(struct config_item *item, char *page)
{
    struct demo_item *demo = to_demo_item(item);
    return sprintf(page, "%d\n", demo->value);
}

/* 2. Запис атрибута "value" */
static ssize_t demo_item_value_store(struct config_item *item, const char *page, size_t count)
{
    struct demo_item *demo = to_demo_item(item);
    int val, ret;

    ret = kstrtoint(page, 10, &val);
    if (ret < 0)
        return ret;

    demo->value = val;
    pr_info("demo_configfs: item '%s' value set to %d\n", config_item_name(item), val);
    return count;
}

/* 3. Читання атрибута "status" */
static ssize_t demo_item_status_show(struct config_item *item, char *page)
{
    struct demo_item *demo = to_demo_item(item);
    return sprintf(page, "enabled=%s, value=%d\n", demo->enabled ? "yes" : "no", demo->value);
}

/* Оголошення атрибутів configfs */
CONFIGFS_ATTR(demo_item_, value);
CONFIGFS_ATTR_RO(demo_item_, status);

static struct configfs_attribute *demo_item_attrs[] = {
    &demo_item_attr_value,
    &demo_item_attr_status,
    NULL,
};

/* 4. Деструктор об'єкта (викликається при ci_kref == 0) */
static void demo_item_release(struct config_item *item)
{
    struct demo_item *demo = to_demo_item(item);
    pr_info("demo_configfs: releasing memory for item '%s'\n", config_item_name(item));
    kfree(demo);
}

static struct configfs_item_operations demo_item_ops = {
    .release = demo_item_release,
};

static const struct config_item_type demo_item_type = {
    .ct_owner    = THIS_MODULE,
    .ct_item_ops = &demo_item_ops,
    .ct_attrs    = demo_item_attrs,
};

/* 5. Метод створення об'єкта при mkdir */
static struct config_item *demo_group_make_item(struct config_group *group, const char *name)
{
    struct demo_item *demo;

    demo = kzalloc(sizeof(*demo), GFP_KERNEL);
    if (!demo)
        return ERR_PTR(-ENOMEM);

    demo->value = 0;
    demo->enabled = true;

    config_item_init_type_name(&demo->item, name, &demo_item_type);
    pr_info("demo_configfs: created item '%s'\n", name);
    return &demo->item;
}

/* 6. Метод вилучення об'єкта при rmdir */
static void demo_group_drop_item(struct config_group *group, struct config_item *item)
{
    struct demo_item *demo = to_demo_item(item);
    pr_info("demo_configfs: dropping item '%s' from group\n", config_item_name(item));
    demo->enabled = false;
    config_item_put(item);
}

static struct configfs_group_operations demo_group_ops = {
    .make_item = demo_group_make_item,
    .drop_item = demo_group_drop_item,
};

static const struct config_item_type demo_group_type = {
    .ct_owner     = THIS_MODULE,
    .ct_group_ops = &demo_group_ops,
};

/* 7. Реєстрація підсистеми верхнього рівня */
static struct configfs_subsystem demo_subsys = {
    .su_group = {
        .cg_item = {
            .ci_namebuf = "demo_target",
            .ci_type    = &demo_group_type,
        },
    },
};

static int __init demo_init(void)
{
    config_group_init(&demo_subsys.su_group);
    mutex_init(&demo_subsys.su_mutex);
    pr_info("demo_configfs: registering subsystem /sys/kernel/config/demo_target/\n");
    return configfs_register_subsystem(&demo_subsys);
}

static void __exit demo_exit(void)
{
    pr_info("demo_configfs: unregistering subsystem\n");
    configfs_unregister_subsystem(&demo_subsys);
}

module_init(demo_init);
module_exit(demo_exit);
```

## Покроковий розбір коду ядра та механізми безпеки

1. **Допоміжний макрос `container_of` у коді `to_demo_item`**:
   Оскільки ядро оперує уніфікованим вказівником `struct config_item *item`, обробник атрибутів повинен отримати доступ до зовнішньої структури `struct demo_item`. Функція `to_demo_item` обчислює відносний зсув поля `item` у структурі `demo_item` за допомогою макросу `offsetof` і віднімає цей зсув від отриманого вказівника. Це забезпечує строгу типізацію та нульові накладні витрати під час виконання. Ядро використовує цю техніку для всіх об'єктно-орієнтованих абстракцій C.

2. **Контекст виділення пам'яті у `demo_group_make_item`**:
   Виклик `make_item` відбувається у процесному контексті системного виклику `mkdir`, причому ядро вже утримує м'ютекс підсистеми `su_mutex`. Оскільки процес перебуває у контексті, що дозволяє засинати, виділення пам'яті виконується через `kzalloc()` з прапором `GFP_KERNEL`. Прапор `GFP_KERNEL` дозволяє розподільнику SLUB переводити потік у стан очікування (Sleep), якщо система відчуває дефіцит вільних сторінок пам'яті, або витісняти сторінки на диск. Якщо пам'яті недостатньо, макрос `ERR_PTR(-ENOMEM)` упаковує код помилки у вказівник, що повідомляє VFS про скасування системного виклику з поверненням помилки у простір користувача.

3. **Ініціалізація та прив'язка типів**:
   Функція `config_item_init_type_name()` виконує три критичні дії:
   - Призначує текстове ім'я каталогу у полі `ci_name`. Коротше за `CONFIGFS_ITEM_NAME_LEN` (20) ім'я лягає у вбудований масив `ci_namebuf`; від двадцяти символів ядро виділяє окремий буфер у купі.
   - Встановлює початкове значення лічильника посилань `ci_kref = 1`.
   - Прив'язує таблицю `demo_item_type`, яка описує методи обробки атрибутів та зворотний деструктор.

4. **Розділення обов'язків між `drop_item` та `release`**:
   Найчастішою помилкою розробників-початківців є прямий виклик `kfree()` у коді `drop_item`. У розробленому драйвері метод `drop_item` виконує лише логічне виключення об'єкта: змінює прапор `enabled = false` та зменшує лічильник посилань через `config_item_put(item)`. Фізичне звільнення пам'яті викликом `kfree(demo)` відбувається виключно всередині `demo_item_release()`, коли лічильник посилань `ci_kref` гарантовано досягає нуля. Це виключає помилки типу *use-after-free*: у мить `rmdir` на елемент іще можуть указувати службовий вузол дерева `configfs` або чуже символічне посилання, і `kfree()` просто з `drop_item()` вирвав би пам'ять із-під них. Відкритий дескриптор атрибута до цієї картини не належить — від ядра 5.3 його стереже окремий механізм мертвої гілки (`frag_dead`), а не `ci_kref`.

## Аналіз крайніх випадків та станів гонитви (Race Conditions)

Під час розробки реальних драйверів на базі `configfs` виникають декілька складних ситуацій, які вимагають обережності:

### 1. Вивантаження модуля ядра при відкритих файлах атрибутів
Якщо користувач виконав `cat /sys/kernel/config/demo_target/node_1/status` і заблокував процес, а адміністратор намагається вивантажити модуль через `rmmod demo_configfs`, ядро захищає систему лічильником посилань на модуль. Відкриття файла атрибута робить `try_module_get(attr->ca_owner)` — а `ca_owner` макрос `CONFIGFS_ATTR` виставляє у `THIS_MODULE`, — тож поки дескриптор відкритий, модуль має ненульовий лічильник, і `rmmod` відмовляє з `rmmod: ERROR: Module demo_configfs is in use`. Той самий захист працює й на рівні дерева: доки в підсистемі лишається хоч один створений `mkdir`-ом каталог, `configfs_mkdir()` тримає посилання і на власника підсистеми, і на власника типу нового елемента, тож `demo_exit()` просто не буде викликано.

### 2. Захист від повторного або некоректного rmdir
Спроба виконати `rmdir` для каталогу, задіяного у графі зв'язків, автоматично відхиляється файловою системою `configfs`. Вирішує це внутрішня функція `configfs_detach_prep()`, і дивиться вона не на `ci_kref`, а на службове дерево `configfs_dirent`: ненульовий `parent_sd->s_links` (тобто на вузол указує чуже символічне посилання) дає `-EBUSY`, а дочірній вузол, який не є типовою групою — вкладений елемент чи симлінк, створений усередині каталогу, — дає `-ENOTEMPTY`. Документація формулює те саме правило з двох боків: елемент не можна вилучити ні поки він сам на когось посилається, ні поки посилаються на нього. Відкриті файлові дескриптори атрибутів у цю перевірку не входять і `rmdir` не блокують — від ядра 5.3 вони після видалення просто дістають `-ENOENT` на кожному `read()`/`write()`.

### 3. Запобігання взаємним блокуванням (Deadlocks)
Усі обробники `make_item`, `make_group` та `drop_item` викликаються шаром `configfs` із вже захопленим м'ютексом підсистеми `su_mutex`. З цієї причини драйверу **суворо заборонено** повторно захоплювати `su_mutex` або викликати функції реєстрації інших підсистем всередині цих методів, оскільки це спричинить самоблокування потоку (Self-Deadlock).

## Компіляція та збирання модуля ядра

Для збирання модуля ядра використовується стандартний `Makefile`:

```makefile
obj-m += demo_configfs.o

KDIR ?= /lib/modules/$(shell uname -r)/build
PWD  := $(shell pwd)

default:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
```

Послідовність команд для завантаження модуля та перевірки точки монтування:

```bash
# 1. Збирання модуля
make

# 2. Монтування configfs, якщо вона не була змонтована автоматично
sudo mount -t configfs none /sys/kernel/config

# 3. Завантаження модуля ядра
sudo insmod demo_configfs.ko

# 4. Перевірка наявності кореневого каталогу підсистеми
ls -la /sys/kernel/config/demo_target/
```

## Утиліти простору користувача: Керування через VFS

Для керування цим драйвером із простору користувача можна використовувати як стандартні інструменти Shell (`mkdir`, `echo`, `cat`, `rmdir`), так і прикладні програми. Нижче наведено ідіоматичні реалізації утиліти створення та налаштування вузлів мовами C та C++.

:::tabs
```c
/* Утиліта керування configfs мовою C (POSIX API) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <errno.h>

#define CONFIGFS_PATH "/sys/kernel/config/demo_target/node_c"

int main(void)
{
    int fd;
    char buffer[128];
    ssize_t bytes;

    /* 1. Створення ядерного об'єкта через mkdir */
    printf("[C] Створення об'єкта %s...\n", CONFIGFS_PATH);
    if (mkdir(CONFIGFS_PATH, 0755) < 0 && errno != EEXIST) {
        perror("Помилка mkdir");
        return EXIT_FAILURE;
    }

    /* 2. Запис значення атрибута value */
    char attr_val_path[256];
    snprintf(attr_val_path, sizeof(attr_val_path), "%s/value", CONFIGFS_PATH);

    fd = open(attr_val_path, O_WRONLY);
    if (fd < 0) {
        perror("Помилка відкриття value для запису");
        return EXIT_FAILURE;
    }

    const char *val_str = "42";
    if (write(fd, val_str, strlen(val_str)) < 0) {
        perror("Помилка запису в value");
        close(fd);
        return EXIT_FAILURE;
    }
    close(fd);
    printf("[C] Успішно записано value = 42\n");

    /* 3. Зчитання стану об'єкта з атрибута status */
    char attr_status_path[256];
    snprintf(attr_status_path, sizeof(attr_status_path), "%s/status", CONFIGFS_PATH);

    fd = open(attr_status_path, O_RDONLY);
    if (fd >= 0) {
        bytes = read(fd, buffer, sizeof(buffer) - 1);
        if (bytes > 0) {
            buffer[bytes] = '\0';
            printf("[C] Прочитано status:\n%s", buffer);
        }
        close(fd);
    }

    /* 4. Видалення ядерного об'єкта через rmdir */
    printf("[C] Видалення об'єкта через rmdir...\n");
    if (rmdir(CONFIGFS_PATH) < 0) {
        perror("Помилка rmdir");
        return EXIT_FAILURE;
    }

    printf("[C] Об'єкт успішно знищено у ядрі.\n");
    return EXIT_SUCCESS;
}
```
```cpp
// Утиліта керування configfs мовою C++ (C++20 std::filesystem & RAII)
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <string_view>
#include <system_error>

namespace fs = std::filesystem;

class ConfigFsManager {
public:
    explicit ConfigFsManager(fs::path target_path) : path_(std::move(target_path)) {}

    bool create_object() {
        std::error_code ec;
        std::cout << "[C++] Створення об'єкта " << path_ << "...\n";
        if (fs::create_directory(path_, ec)) {
            std::cout << "[C++] Об'єкт успішно створено у ядрі.\n";
            return true;
        }
        if (ec) {
            std::cerr << "[C++] Помилка створення каталогу: " << ec.message() << "\n";
            return false;
        }
        return true;
    }

    bool write_attribute(std::string_view attr_name, std::string_view value) {
        fs::path attr_path = path_ / attr_name;
        std::ofstream ofs(attr_path);
        if (!ofs.is_open()) {
            std::cerr << "[C++] Не вдалося відкрити атрибут: " << attr_path << "\n";
            return false;
        }
        ofs << value;
        std::cout << "[C++] Записано значення '" << value << "' у " << attr_name << "\n";
        return ofs.good();
    }

    void print_attribute(std::string_view attr_name) const {
        fs::path attr_path = path_ / attr_name;
        std::ifstream ifs(attr_path);
        if (!ifs.is_open()) {
            std::cerr << "[C++] Не вдалося прочитати атрибут: " << attr_path << "\n";
            return;
        }
        std::string line;
        std::cout << "[C++] Зміст атрибута " << attr_name << ":\n";
        while (std::getline(ifs, line)) {
            std::cout << "  " << line << "\n";
        }
    }

    bool destroy_object() {
        std::error_code ec;
        std::cout << "[C++] Видалення об'єкта через rmdir " << path_ << "...\n";
        if (fs::remove(path_, ec)) {
            std::cout << "[C++] Об'єкт успішно знищено з ядра.\n";
            return true;
        }
        std::cerr << "[C++] Помилка видалення: " << ec.message() << "\n";
        return false;
    }

private:
    fs::path path_;
};

int main() {
    fs::path config_path = "/sys/kernel/config/demo_target/node_cpp";
    ConfigFsManager manager(config_path);

    if (!manager.create_object()) {
        return 1;
    }

    if (manager.write_attribute("value", "100")) {
        manager.print_attribute("status");
    }

    if (!manager.destroy_object()) {
        return 1;
    }

    return 0;
}
```
:::

## Зіставлення підходів у просторі користувача (C POSIX vs C++20)

Обидва прикладні варіанти утиліти демонструють принципово різні філософії взаємодії з віртуальною файловою системою `configfs`:

- **Варіант C (POSIX System Calls)**: спирається на низькорівневі системні виклики `mkdir()`, `open()`, `write()`, `read()`, `rmdir()`. Він є максимально детермінованим і використовується в системних демонах або мінімалістичних утилітах на кшталт `busybox`. Програміст повинен вручну перевіряти коди помилок `errno`, самостійно керувати файловими дескрипторами та форматувати файлові шляхи через `snprintf()`.
- **Варіант C++ (C++20 `std::filesystem` & RAII)**: абстрагує файлові операції через стандартні класи `std::filesystem::path`, `std::ofstream` та `std::ifstream`. Автоматичне закриття файлових дескрипторів у деструкторах потоків унеможливлює витоки файлових дескрипторів, а обробка помилок через `std::error_code` дозволяє уникнути важких винятків та писати безпечний код для системного програмування.

## Простеження викликів у реальному часі через ftrace

Для діагностики виконання методів `make_item` та `drop_item` у ядрі під час роботи утиліти можна застосувати інструмент трасування `ftrace`:

```bash
# 1. Увімкнення графіку викликів функцій для підсистеми configfs.
#    Шаблон беремо в лапки, інакше оболонка спробує розкрити його
#    як маску імен файлів у поточному каталозі.
echo function_graph > /sys/kernel/tracing/current_tracer
echo 'configfs_*' > /sys/kernel/tracing/set_ftrace_filter
echo 'vfs_mkdir'  >> /sys/kernel/tracing/set_ftrace_filter
echo 'vfs_rmdir'  >> /sys/kernel/tracing/set_ftrace_filter
echo 'demo_group_*' >> /sys/kernel/tracing/set_ftrace_filter

# 2. Очищення буфера трасування та запуск спостереження
echo > /sys/kernel/tracing/trace
echo 1 > /sys/kernel/tracing/tracing_on
mkdir /sys/kernel/config/demo_target/test_node
rmdir /sys/kernel/config/demo_target/test_node
echo 0 > /sys/kernel/tracing/tracing_on

# 3. Перегляд траси викликів у ядрі
cat /sys/kernel/tracing/trace | head -n 30
```

У трасі чітко видно послідовний перехід від системного виклику VFS `vfs_mkdir()` через метод `configfs_mkdir()` до зворотного виклику драйвера `demo_group_make_item()`, що підтверджує пряму прив'язку файлових інструкцій POSIX до життєвого циклу об'єктів у ядрі.

## Очікуваний вивід ядра у dmesg

Під час виконання розробленої утиліти у системному журналі ядра `dmesg` відображається повна послідовність викликів створення та знищення об'єкта:

```text
[ 142.105120] demo_configfs: registering subsystem /sys/kernel/config/demo_target/
[ 145.310245] demo_configfs: created item 'node_cpp'
[ 145.311012] demo_configfs: item 'node_cpp' value set to 100
[ 145.312150] demo_configfs: dropping item 'node_cpp' from group
[ 145.312210] demo_configfs: releasing memory for item 'node_cpp'
```

Цей приклад демонструє строгу послідовність життя: створення через `mkdir` викликає `make_item()`, вилучення через `rmdir` викликає `drop_item()`, а фізичне звільнення пам'яті виконується у деструкторі `release()` після обнулення лічильника посилань `ci_kref`.
