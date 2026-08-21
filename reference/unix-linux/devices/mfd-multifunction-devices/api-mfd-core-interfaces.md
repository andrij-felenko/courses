# 📋 Довідник ядерних інтерфейсів та структур підсистеми MFD

Цей довідник містить детальний опис структур даних, публічних функцій ядра, прапорців та контрактів виконання підсистеми MFD (Multi-Function Devices) та супутнього механізму демультиплексування переривань `regmap-irq` у ядрі Linux.

## 1. Головні структури даних

### 1.1. Структура `struct mfd_cell`

Визначена у заголовковому файлі `include/linux/mfd/core.h`. Вона описує логічну функціональну одиницю (комірку) мікросхеми, для якої ядро створює платформений пристрій (`struct platform_device`).

```c
struct mfd_cell {
	const char *name;
	int id;
	int (*enable)(struct platform_device *dev);
	int (*disable)(struct platform_device *dev);
	int (*suspend)(struct platform_device *dev);
	int (*resume)(struct platform_device *dev);
	void *platform_data;
	size_t pdata_size;
	const char * const *parent_supplies;
	int num_parent_supplies;
	int num_resources;
	const struct resource *resources;
	bool ignore_resource_conflicts;
	bool pm_runtime_no_callbacks;
	bool allow_claim_mfd_has_no_parent;
	bool use_parent;
	const char *of_compatible;
	const struct mfd_cell_acpi_match *acpi_match;
	const struct mfd_cell_match *matches;
	int num_matches;
};
```

#### Детальний опис полів:

- `name`: Рядок імені пристрою. Використовується для зіставлення з `platform_driver.driver.name`, якщо не знайдено збігу за Device Tree або ACPI.
- `id`: Ідентифікатор екземпляра пристрою. Використовує значення `PLATFORM_DEVID_NONE` (-1), якщо пристрій єдиний, або `PLATFORM_DEVID_AUTO` (-2), якщо ядро має призначити порядковий індекс автоматично.
- `enable` / `disable`: Необов'язкові вказівники на функції зворотного виклику, які викликаються до або після того, як дочірній драйвер захоплює/звільняє ресурси.
- `suspend` / `resume`: Застарілі функції переходу в режим сну для комірки (наразі рекомендовано використовувати стандартні механізми `dev_pm_ops` у дочірньому драйвері).
- `platform_data`: Вказівник на специфічні дані конфігурації платформи, які копіюються у дочірній `pdev->dev.platform_data`.
- `pdata_size`: Розмір блоку пам'яті `platform_data` у байтах.
- `parent_supplies`: Масив імен регуляторів живлення, від яких залежить ця комірка. MFD автоматично реєструє зв'язки живлення перед реєстрацією дочірнього пристрою.
- `num_parent_supplies`: Кількість елементів у масиві `parent_supplies`.
- `resources`: Масив структур `struct resource` (типово `IORESOURCE_IRQ` або `IORESOURCE_MEM`).
- `num_resources`: Кількість ресурсів у масиві.
- `ignore_resource_conflicts`: Логічний прапорець. Якщо виставлено у `true`, ядро ігнорує конфлікти пам'яті `IORESOURCE_MEM`, дозволяючи кільком дочірнім пристроям перекривати той самий діапазон фізичних адрес.
- `pm_runtime_no_callbacks`: Якщо виставлено у `true`, ядро позначає дочірній пристрій прапорцем `pm_runtime_no_callbacks(&pdev->dev)`.
- `use_parent`: Якщо виставлено у `true`, дочірній пристрій напряму використовує `dev.of_node` батьківського вузла, коли власний підвузол у Device Tree відсутній.
- `of_compatible`: Рядок сумісності для пошуку дочірнього підвузла у дереві Device Tree (`of_find_matching_node`).
- `matches`: Таблиця зіставлення за індексом для складних багатоекземплярних вузлів.
- `num_matches`: Кількість елементів у таблиці `matches`.

---

### 1.2. Структура `struct regmap_irq`

Описує одиничне переривання всередині мікросхеми PMIC або мультичипа.

```c
struct regmap_irq {
	unsigned int reg_offset;
	unsigned int mask;
	unsigned int type_reg_offset;
	unsigned int type_rising_mask;
	unsigned int type_falling_mask;
	unsigned int type_level_high_mask;
	unsigned int type_level_low_mask;
};
```

#### Детальний опис полів:
- `reg_offset`: Зміщення регістру статусу/маски відносно базової адреси (`status_base`/`mask_base`) у кроках регістрів.
- `mask`: Бітова маска переривання всередині вибраного регістру.
- `type_reg_offset`: Зміщення регістру конфігурації типу спрацьовування.
- `type_rising_mask` / `type_falling_mask`: Бітові маски налаштування спрацьовування за наростаючим чи спадаючим фронтом.
- `type_level_high_mask` / `type_level_low_mask`: Бітові маски налаштування спрацьовування за високим чи низьким рівнем напруги.

---

### 1.3. Структура `struct regmap_irq_chip`

Описує загальну конфігурацію вбудованого контролера переривань мікросхеми.

```c
struct regmap_irq_chip {
	const char *name;
	unsigned int status_base;
	unsigned int mask_base;
	unsigned int unmask_base;
	unsigned int ack_base;
	unsigned int wake_base;
	unsigned int type_base;
	bool mask_writeonly;
	bool mask_invert;
	bool clear_on_unmask;
	bool ack_invert;
	bool runtime_pm;
	int num_regs;
	const struct regmap_irq *irqs;
	int num_irqs;
	int num_type_reg;
	int (*handle_pre_irq)(void *irq_drv_data);
	int (*handle_post_irq)(void *irq_drv_data);
	int (*set_type_config)(unsigned int **buf, unsigned int type,
			       const struct regmap_irq *irq_data, int idx,
			       void *irq_drv_data);
};
```

#### Детальний опис полів:
- `name`: Рядкове ім'я контролера переривань для відображення у `/proc/interrupts`.
- `status_base`: Базова адреса регістрів статусу переривань.
- `mask_base`: Базова адреса регістрів маскування переривань.
- `unmask_base`: Базова адреса регістрів розмаскування (якщо контролер має окремі регістри Set/Clear).
- `ack_base`: Базова адреса регістрів квитування переривань (Acknowledge / W1C).
- `wake_base`: Базова адреса регістрів пробудження системи (Wake-up).
- `mask_invert`: Якщо `true`, запис `1` дозволяє переривання, а `0` — маскує (за замовчуванням навпаки).
- `num_regs`: Кількість послідовних регістрів статусу/маски в контролері.
- `irqs`: Масив дескрипторів `struct regmap_irq`.
- `num_irqs`: Розмір масиву переривань.
- `handle_pre_irq` / `handle_post_irq`: Зворотні виклики перед і після зчитування статусних регістрів у потоці `regmap_irq_thread`.

---

## 2. Інтерфейси керування пристроями (MFD Core API)

### 2.1. `mfd_add_devices` та `devm_mfd_add_devices`

Реєструють масив дочірніх комірок як платформені пристрої ядра.

```c
int mfd_add_devices(struct device *parent, int id,
		    const struct mfd_cell *cells, int n_devs,
		    const struct resource *mem_base,
		    int irq_base, struct irq_domain *domain);

int devm_mfd_add_devices(struct device *dev, int id,
			 const struct mfd_cell *cells, int n_devs,
			 const struct resource *mem_base,
			 int irq_base, struct irq_domain *domain);
```

#### Параметри:
- `parent` / `dev`: Батьківський пристрій фізичної шини (I2C, SPI, PCI тощо).
- `id`: Базовий ідентифікатор екземплярів (`PLATFORM_DEVID_AUTO` або `PLATFORM_DEVID_NONE`).
- `cells`: Масив структур `struct mfd_cell`.
- `n_devs`: Кількість елементів у масиві `cells`.
- `mem_base`: Необов'язковий базовий ресурс пам'яті для трансляції відносних адрес `IORESOURCE_MEM`.
- `irq_base`: Базовий номер віртуального переривання (для застарілих систем без `irq_domain`, зазвичай передається `0`).
- `domain`: Вказівник на домен переривань `struct irq_domain` (створений через `regmap_irq_chip`).

#### Внутрішній алгоритм роботи `mfd_add_device`:
1. **Виділення пристрою:** Ядро викликає `platform_device_alloc(cell->name, cell->id + id)`.
2. **Встановлення батьківства:** Поле `pdev->dev.parent` встановлюється на `parent`. Це критично для успадкування контексту керування живленням (Runtime PM) та доступу до `dev_get_regmap()`.
3. **Пошук Device Tree вузла:** Функція `mfd_match_of_node()` обходить дочірні вузли `parent->of_node`. Вона порівнює властивість `compatible` вузла з полем `cell->of_compatible`. Якщо знайдено збіг, вказівник на вузол зберігається у `pdev->dev.of_node`.
4. **Трансляція ресурсів:** Для кожного ресурсу `IORESOURCE_IRQ` у масиві комірки ядро перетворює відносний індекс у системний номер віртуального переривання через виклик `irq_create_mapping(domain, res->start)`.
5. **Реєстрація:** Пристрій публікується на платформеній шині через `platform_device_add()`, що запускає процес зіставлення (`probe`) із відповідним драйвером підсистеми.

#### Повертане значення:
- `0` у разі успішної реєстрації всіх комірок.
- Від'ємний код помилки (`-ENOMEM`, `-EINVAL`, `-EBUSY`), якщо створення хоча б одного пристрою зазнало невдачі. Усі раніше створені в цьому виклику пристрої автоматично видаляються.

#### Контекст виклику:
- Функція може засинати (`might_sleep()`), оскільки виконує динамічне виділення пам'яті (`kmalloc`) та реєстрацію у моделі драйверів (`device_add`). Не викликається з переривань або спинлоків.

---

### 2.2. `mfd_remove_devices` та `devm_mfd_remove_devices`

Видаляють усі дочірні пристрої, зареєстровані для вказаного батьківського пристрою.

```c
void mfd_remove_devices(struct device *parent);
void devm_mfd_remove_devices(struct device *dev);
```

#### Механізм видалення:
Функція викликає `device_for_each_child(parent, NULL, mfd_remove_devices_fn)`. Для кожного дочірнього пристрою, у якого прапорець `mfd_cell` дійсний, ядро викликає `platform_device_unregister()`. Це призводить до виклику `remove()` відповідного дочірнього драйвера, вивільнення пов'язаних переривань і видалення записів із sysfs.

---

### 2.3. `mfd_clone_cell`

Клонує наявну комірку MFD для динамічного створення додаткових екземплярів пристроїв (наприклад, коли кількість каналів визначається версією апаратної ревізії).

```c
int mfd_clone_cell(const char *cell, const char **clones, size_t n_clones);
```

---

## 3. Інтерфейси демультиплексування переривань (Regmap-IRQ API)

### 3.1. `devm_regmap_add_irq_chip` та `regmap_add_irq_chip`

Ініціалізують потоковий обробник переривань та створюють домен `struct irq_domain`.

```c
int devm_regmap_add_irq_chip(struct device *dev, struct regmap *map,
			     int irq, int irq_flags, int irq_base,
			     const struct regmap_irq_chip *chip,
			     struct regmap_irq_chip_data **data);

int regmap_add_irq_chip(struct regmap *map, int irq, int irq_flags,
			int irq_base, const struct regmap_irq_chip *chip,
			struct regmap_irq_chip_data **data);
```

#### Параметри:
- `dev`: Дескриптор пристрою для прив'язки керованого ресурсу (`devres`).
- `map`: Ініціалізована мапа регістрів `struct regmap`.
- `irq`: Номер фізичного головного переривання SoC (наприклад, пін GPIO чи лінія GIC).
- `irq_flags`: Прапорці переривання ядра (типово `IRQF_ONESHOT | IRQF_SHARED`).
- `irq_base`: Базовий номер віртуального переривання (`0` для динамічного виділення).
- `chip`: Таблиця конфігурації `struct regmap_irq_chip`.
- `data`: Вихідний вказівник, куди записується створена контекстна структура `struct regmap_irq_chip_data`.

---

### 3.2. `regmap_irq_get_virq` та `regmap_irq_get_domain`

Отримують віртуальний номер переривання Linux або домен переривань для зв'язування з MFD.

```c
int regmap_irq_get_virq(struct regmap_irq_chip_data *data, int irq);
struct irq_domain *regmap_irq_get_domain(struct regmap_irq_chip_data *data);
```

#### Параметри та повертані значення:
- `regmap_irq_get_virq`: Приймає дескриптор `data` та апаратний індекс переривання `irq` (від `0` до `num_irqs - 1`). Повертає віртуальний системний номер переривання Linux (позитивне число) або `-EINVAL`.
- `regmap_irq_get_domain`: Повертає вказівник на `struct irq_domain` для передачі у функцію `devm_mfd_add_devices()`.

---

## 4. Допоміжні функції доступу (Helper Functions)

### 4.1. `dev_get_regmap`

Дозволяє дочірньому драйверу отримати вказівник на мапу регістрів від батька або дідуся.

```c
struct regmap *dev_get_regmap(struct device *dev, const char *name);
```

#### Контракт використання:
- Якщо `name == NULL`, функція повертає головний (або єдиний) `regmap`, асоційований із пристроєм `dev`.
- Якщо пристрій `dev` не має власного `regmap`, дочірні драйвери передають `dev->parent`:
```c
struct regmap *map = dev_get_regmap(pdev->dev.parent, NULL);
```

---

## 5. Таблиця кодів помилок та контекстів виконання

| Функція | Контекст | Сплячий (Sleep) | Блокування | Типові коди помилок |
| :--- | :--- | :--- | :--- | :--- |
| `devm_mfd_add_devices` | Process | Так | `device_lock`, `sysfs_lock` | `-ENOMEM`, `-EINVAL`, `-EBUSY` |
| `mfd_remove_devices` | Process | Так | `device_lock` | void |
| `devm_regmap_add_irq_chip` | Process | Так | `mutex`, `rt_mutex` | `-ENOMEM`, `-EINVAL`, `-EBUSY` |
| `regmap_irq_get_virq` | Any | Ні | RCU / Lockless | `-EINVAL` |
| `dev_get_regmap` | Any | Ні | Lockless | `NULL` |
| `regmap_update_bits` | Process / Any | Залежить від шини | `regmap->lock` | `-EIO`, `-ETIMEDOUT`, `-EAGAIN` |
