# 📋 Поверхня API: devres та керовані функції devm_*

Керовані ресурси ядра Linux розділені на дві функціональні частини: низькорівневе ядро підсистеми `devres`, що оперує універсальними вузлами списку прив'язки до `struct device`, та високорівневе сімейство допоміжних функцій `devm_*`, розкиданих по спеціалізованих підсистемах ядра (пам'ять, MMIO, переривання, тактування, живлення, GPIO, шини PCI та платформені пристрої).

## 1. Базовий інтерфейс ядра devres

Функції ядра `devres` визначені в заголовку `<linux/device.h>` та реалізовані в `drivers/base/devres.c`. Вони забезпечують безпосереднє виділення службового вузла, його реєстрацію у списку пристрою та ручне керування життєвим циклом об'єкта.

### Типи даних і зворотні виклики

```c
typedef void (*dr_release_t)(struct device *dev, void *res);
typedef int (*dr_match_t)(struct device *dev, void *res, void *match_data);
```

- `dr_release_t`: вказівник на функцію звільнення конкретного ресурсу. Викликається автоматично підсистемою `devres` під час вивантаження драйвера, аварійного виходу з `probe()` або явного виклику `devres_release()`. Приймає вказівник на пристрій `dev` та вказівник на корисні дані ресурсу `res`. Контекст виклику завжди є сплячим (sleepable), за винятком випадків явного ручного звільнення в атомарному коді.
- `dr_match_t`: предикат пошуку ресурсу в списку `devres_head`. Повертає ненульове значення, якщо ресурс `res` відповідає критеріям `match_data`.

### Керування окремими ресурсами

```c
void *devres_alloc(dr_release_t release, size_t size, gfp_t gfp);
void devres_add(struct device *dev, void *res);
void devres_free(void *res);
int devres_destroy(struct device *dev, dr_release_t release,
                   dr_match_t match, void *match_data);
int devres_release(struct device *dev, dr_release_t release,
                   dr_match_t match, void *match_data);
void *devres_find(struct device *dev, dr_release_t release,
                  dr_match_t match, void *match_data);
void *devres_get(struct device *dev, void *new_res,
                 dr_match_t match, void *match_data);
void *devres_remove(struct device *dev, dr_release_t release,
                    dr_match_t match, void *match_data);
```

- `devres_alloc(release, size, gfp)`: виділяє пам'ять у SLAB під заголовок `struct devres_node` разом із корисним навантаженням розміром `size`. Ініціалізує поле `release`. Повертає вказівник на корисне навантаження `data[]` або `NULL` при вичерпанні пам'яті. Ресурс ще не прив'язаний до жодного пристрою.
- `devres_add(dev, res)`: додає попередньо виділений ресурс `res` до голови списку `dev->devres_head` під захистом спін-блокування `dev->devres_lock`. Передає володіння ресурсом пристрою. Виклик цієї функції після `devres_alloc()` є обов'язковим для взяття об'єкта під контроль ядра.
- `devres_free(res)`: звільняє пам'ять не доданого до списку ресурсу (наприклад, якщо після `devres_alloc()` сталася помилка до виклику `devres_add()`). Заборонено викликати після того, як ресурс передано у `devres_add()`.
- `devres_destroy(dev, release, match, match_data)`: знаходить ресурс за предикатом, вилучає його зі списку пристрою та негайно звільняє пам'ять вузла, **не викликаючи** деструктор `release`. Повертає `0` у разі успіху або `-ENOENT`. Використовується, коли ресурс уже очищено іншим шляхом або деструктор виконувати непотрібно.
- `devres_release(dev, release, match, match_data)`: знаходить ресурс за предикатом, вилучає зі списку, викликає відповідний зворотний виклик `release(dev, res)` і звільняє пам'ять вузла. Повертає `0` або `-ENOENT`.
- `devres_find(dev, release, match, match_data)`: знаходить ресурс у списку без вилучення. Повертає вказівник на дані або `NULL`.
- `devres_get(dev, new_res, match, match_data)`: атомарна операція: шукає наявний ресурс; якщо знайдено — звільняє `new_res` через `devres_free()` і повертає знайдений. Якщо не знайдено — реєструє `new_res` через `devres_add()` і повертає його.
- `devres_remove(dev, release, match, match_data)`: вилучає ресурс зі списку пристрою без виклику деструктора і повертає вказівник на нього. Відповідальність за подальший виклик `devres_free()` або деініціалізацію лягає на викликача.

## 2. Користувацькі дії: сімейство devm_add_action

Дозволяє прив'язати довільну C-функцію очищення до пристрою без ручного виділення структур `devres`.

```c
typedef void (*devm_action_t)(void *data);

int devm_add_action(struct device *dev, devm_action_t action, void *data);
int devm_add_action_or_reset(struct device *dev, devm_action_t action, void *data);
void devm_remove_action(struct device *dev, devm_action_t action, void *data);
void devm_release_action(struct device *dev, devm_action_t action, void *data);
```

- `devm_add_action(dev, action, data)`: створює внутрішній вузол `devres`, де функцією звільнення є спеціальна обгортка, що викличе `action(data)`. При невдачі виділення пам'яті повертає `-ENOMEM`, але **не викликає** `action(data)`.
- `devm_add_action_or_reset(dev, action, data)`: рекомендований аналог. Якщо додавання дії зазнало невдачі (наприклад, через брак пам'яті під вузол), негайно викликає `action(data)` і повертає `-ENOMEM`. Запобігає витоку ресурсів на аварійній гілці `probe()`.
- `devm_remove_action(dev, action, data)`: видаляє зареєстровану дію зі списку без її виконання.
- `devm_release_action(dev, action, data)`: вилучає дію зі списку і негайно виконує `action(data)`.

## 3. Групи ресурсів: devres groups

Групи дозволяють організувати вузли у вкладені логічні блоки з можливістю селективного відкочування окремих етапів конфігурації.

```c
void *devres_open_group(struct device *dev, void *id, gfp_t gfp);
void devres_close_group(struct device *dev, void *id);
void devres_remove_group(struct device *dev, void *id);
int devres_release_group(struct device *dev, void *id);
```

- `devres_open_group(dev, id, gfp)`: створює вузол-маркер початку групи в списку `devres_head`. Якщо `id == NULL`, повертає згенерований непрозорий вказівник групи. Усі подальші виклики `devm_*` додаватимуться всередину цієї групи до моменту закриття або відкриття нової.
- `devres_close_group(dev, id)`: знаходить найновішу відкриту групу (або групу за конкретним `id`) і позначає її закритою. Ресурси всередині групи лишаються прив'язаними до пристрою.
- `devres_remove_group(dev, id)`: видаляє маркер групи зі списку, залишаючи всі виділені всередині неї ресурси у загальному списку пристрою.
- `devres_release_group(dev, id)`: знаходить групу за `id`, послідовно викликає деструктори `release` для **всіх** ресурсів, зареєстрованих від моменту відкриття цієї групи до її кінця (у зворотному порядку LIFO), видаляє їх зі списку і звільняє пам'ять. Повертає кількість звільнених байтів або `-ENOENT`.

## 4. Спеціалізовані помічники підсистем ядра

### Виділення пам'яті ядра (`<linux/device.h>`)

| Функція | Призначення | Поведінка при помилці |
| :--- | :--- | :--- |
| `devm_kmalloc(dev, size, gfp)` | Виділення блоку пам'яті у просторі ядра | Повертає `NULL` |
| `devm_kzalloc(dev, size, gfp)` | Виділення блоку пам'яті з обнуленням байтів | Повертає `NULL` |
| `devm_kcalloc(dev, n, size, gfp)` | Безпечне множення кількості елементів на розмір та обнулення | Повертає `NULL` |
| `devm_kstrdup(dev, s, gfp)` | Дублювання C-рядка у керовану пам'ять | Повертає `NULL` |
| `devm_kmemdup(dev, src, len, gfp)` | Дублювання довільного буфера пам'яті | Повертає `NULL` |
| `devm_kfree(dev, p)` | Дострокове ручне звільнення керованої пам'яті | Нічого не повертає |

### Регістри MMIO та простори введення-виведення (`<linux/io.h>`, `<linux/platform_device.h>`)

```c
void __iomem *devm_ioremap(struct device *dev, resource_size_t offset,
                           resource_size_t size);
void __iomem *devm_ioremap_resource(struct device *dev,
                                    const struct resource *res);
void __iomem *devm_platform_ioremap_resource(struct platform_device *pdev,
                                             unsigned int index);
void __iomem *devm_platform_ioremap_resource_byname(struct platform_device *pdev,
                                                    const char *name);
```

- `devm_ioremap(dev, offset, size)`: відображає фізичний діапазон MMIO у віртуальний адресний простір ядра. Звільняється автоматично через `iounmap`. Повертає `NULL` при помилці.
- `devm_ioremap_resource(dev, res)`: комплексний захищений виклик. Перевіряє коректність структури `res`, викликає `devm_request_mem_region()` для ексклюзивного блокування шинного діапазону та `devm_ioremap()`. При збої повертає закодований вказівник помилки (`ERR_PTR(-EBUSY)`, `ERR_PTR(-ENOMEM)`, `ERR_PTR(-EINVAL)`), а не `NULL`. Перевіряється виключно макросом `IS_ERR()`.
- `devm_platform_ioremap_resource(pdev, index)`: зручна обгортка для платформених драйверів, яка поєднує `platform_get_resource(pdev, IORESOURCE_MEM, index)` та `devm_ioremap_resource(&pdev->dev, res)`.

### Лінії переривань (`<linux/interrupt.h>`)

```c
int devm_request_irq(struct device *dev, unsigned int irq,
                     irq_handler_t handler, unsigned long irqflags,
                     const char *devname, void *dev_id);

int devm_request_threaded_irq(struct device *dev, unsigned int irq,
                              irq_handler_t handler, irq_handler_t thread_fn,
                              unsigned long irqflags, const char *devname,
                              void *dev_id);

void devm_free_irq(struct device *dev, unsigned int irq, void *dev_id);
```

- `devm_request_threaded_irq()`: реєструє первинний обробник (top-half) та потоковий обробник (bottom-half). Під час вивантаження викликає `free_irq(irq, dev_id)`, гарантуючи синхронізацію та завершення всіх активних обробників до звільнення структур драйвера. Повертає `0` при успіху або від'ємний код помилки (`-EBUSY`, `-EINVAL`).
- `devm_free_irq()`: дострокове звільнення лінії переривання, якщо драйверу необхідно відключити лінію до завершення роботи пристрою.

### Тактові сигнали (`<linux/clk.h>`)

```c
struct clk *devm_clk_get(struct device *dev, const char *id);
struct clk *devm_clk_get_optional(struct device *dev, const char *id);
struct clk *devm_clk_get_enabled(struct device *dev, const char *id);
int devm_clk_bulk_get_all_enable(struct device *dev, struct clk_bulk_data **clks);
```

- `devm_clk_get(dev, id)`: отримує дескриптор тактового генератора. Повертає `ERR_PTR` у разі збою. Автоматично викликає `clk_put()`.
- `devm_clk_get_optional(dev, id)`: повертає `NULL`, якщо лінія тактування відсутня в дереві пристроїв, і дескриптор, якщо лінія є.
- `devm_clk_get_enabled(dev, id)`: отримує тактовий сигнал, готує його та вмикає (`clk_prepare_enable`). Під час очищення автоматично викликає `clk_disable_unprepare()` та `clk_put()`.

### Лінії GPIO (`<linux/gpio/consumer.h>`)

```c
struct gpio_desc *devm_gpiod_get(struct device *dev, const char *con_id,
                                 enum gpiod_flags flags);
struct gpio_desc *devm_gpiod_get_optional(struct device *dev, const char *con_id,
                                          enum gpiod_flags flags);
struct gpio_desc *devm_gpiod_get_index(struct device *dev, const char *con_id,
                                       unsigned int idx, enum gpiod_flags flags);
```

- `devm_gpiod_get(dev, con_id, flags)`: знаходить лінію GPIO у Device Tree / ACPI, налаштовує початковий напрямок (вхід або вихід) та підтяжки відповідно до `flags`. Повертає `ERR_PTR` при помилці. Звільняється через `gpiod_put()`.

### Регулятори напруги та скидання (`<linux/regulator/consumer.h>`, `<linux/reset.h>`)

```c
struct regulator *devm_regulator_get(struct device *dev, const char *id);
struct regulator *devm_regulator_get_optional(struct device *dev, const char *id);
int devm_regulator_get_enable(struct device *dev, const char *id);
struct reset_control *devm_reset_control_get_exclusive(struct device *dev, const char *id);
```

- `devm_regulator_get_enable(dev, id)`: отримує дескриптор регулятора живлення та вмикає його. Автоматично вимикає живлення під час вивантаження пристрою.
- `devm_reset_control_get_exclusive(dev, id)`: захоплює монопольний контроль над апаратною лінією апаратного скидання контролера.

### Підсистема шини PCI (`<linux/pci.h>`)

```c
int pcim_enable_device(struct pci_dev *pdev);
int pcim_iomap_regions(struct pci_dev *pdev, int mask, const char *name);
void __iomem * const *pcim_iomap_table(struct pci_dev *pdev);
void pcim_pin_device(struct pci_dev *pdev);
```

- `pcim_enable_device(pdev)`: вмикає PCI-пристрій під керуванням devres. При вивантаженні автоматично викликає `pci_disable_device()`.
- `pcim_iomap_regions(pdev, mask, name)`: резервує та відображає MMIO/IO BAR-регістри пристрою згідно з бітовою маскою `mask`. Звільняється автоматично через `pci_release_regions()`.
- `pcim_pin_device(pdev)`: наказує ядру не вимикати PCI-пристрій автоматично під час вилучення модуля (наприклад, для пристроїв, що обслуговують системну консоль або пам'ять).

### Реєстрація пристроїв у класах та підсистемах

| Підсистема | Функція реєстрації | Автоматичне скасування |
| :--- | :--- | :--- |
| **IIO** | `devm_iio_device_alloc(dev, sizeof_priv)` | Звільнення структури `iio_dev` |
| **IIO** | `devm_iio_device_register(dev, indio_dev)` | `iio_device_unregister()` |
| **HWMON** | `devm_hwmon_device_register_with_info(...)` | `hwmon_device_unregister()` |
| **RTC** | `devm_rtc_device_register(...)` | `rtc_device_unregister()` |
| **PWM** | `devm_pwmchip_add(dev, &chip)` | `pwmchip_remove()` |
| **Sysfs** | `devm_device_add_group(dev, &grp)` | `sysfs_remove_group()` |
| **LEDs** | `devm_led_classdev_register(dev, &led_cdev)` | `led_classdev_unregister()` |
