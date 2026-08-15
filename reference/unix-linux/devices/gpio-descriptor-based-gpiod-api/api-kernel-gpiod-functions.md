# 📋 API-довідник сигнатур та прапорів підсистеми gpiod

Ця довідкова вставка містить вичерпну специфікацію функцій, прапорів ініціалізації, кодів повернення та правил обробки помилок ядерного дескрипторного API `gpiod` (`<linux/gpio/consumer.h>`), який використовується розробниками драйверів пристроїв ядра Linux для керування лініями GPIO.

---

## 1. Прапори ініціалізації (`enum gpiod_flags`)

При отриманні дескриптора лінії через `gpiod_get()` або `devm_gpiod_get()` драйвер обов'язково передає один із прапорів `enum gpiod_flags`. Цей прапор визначає напрямок (вхід або вихід), початкове логічне значення та електричний режим лінії під час її первинного налаштування.

```c
enum gpiod_flags {
    GPIOD_ASIS                = 0,
    GPIOD_IN                  = GPIOD_FLAGS_BIT_DIR_SET,
    GPIOD_OUT_LOW             = GPIOD_FLAGS_BIT_DIR_SET | GPIOD_FLAGS_BIT_DIR_OUT,
    GPIOD_OUT_HIGH            = GPIOD_FLAGS_BIT_DIR_SET | GPIOD_FLAGS_BIT_DIR_OUT |
                                GPIOD_FLAGS_BIT_DIR_VAL,
    GPIOD_OUT_LOW_OPEN_DRAIN  = GPIOD_OUT_LOW  | GPIOD_FLAGS_BIT_OPEN_DRAIN,
    GPIOD_OUT_HIGH_OPEN_DRAIN = GPIOD_OUT_HIGH | GPIOD_FLAGS_BIT_OPEN_DRAIN,
};
```

### Деталізація призначення прапорів

* `GPIOD_ASIS`: Не змінювати поточний стан та напрямок лінії. Використовується, якщо лінія вже була налаштована первинним завантажувачем (U-Boot/EDK2) або іншою підсистемою ядра, і драйвер бажає зчитати поточний апаратний стан без генерації небажаних імпульсів.
* `GPIOD_IN`: Налаштувати лінію у режим входу (Input) та вимкнути вихідні буфери.
* `GPIOD_OUT_LOW`: Налаштувати лінію у режим виходу (Output) та виставити **початкове логічне значення 0** (неактивний стан).
* `GPIOD_OUT_HIGH`: Налаштувати лінію у режим виходу (Output) та виставити **початкове логічне значення 1** (активний стан).
* `GPIOD_OUT_LOW_OPEN_DRAIN`: Налаштувати режим виходу з відкритим стоком (Open Drain) та початковим логічним значенням `0`. У цьому режимі вивід активується лише до землі (LOW), а при високому рівні переходить у високоімпедансний стан (Hi-Z).
* `GPIOD_OUT_HIGH_OPEN_DRAIN`: Налаштувати режим виходу з відкритим стоком (Open Drain) та початковим логічним значенням `1`.

> ⚠️ **Важливо:** Прапори `GPIOD_OUT_LOW` та `GPIOD_OUT_HIGH` оперують **логічними значеннями**, а не електричною напругою. Якщо в Device Tree вказано прапор `GPIO_ACTIVE_LOW`, передача `GPIOD_OUT_HIGH` призведе до встановлення на виводі фізичного рівня **LOW (0V)**.

---

## 2. Функції отримання та вивільнення дескрипторів

Усі функції заголовкового файла `<linux/gpio/consumer.h>` поділяються на дві категорії: базові (вимагають ручного виклику `gpiod_put()`) та Devres-керовані (з автоматичним очищенням ресурсів при вилученні пристрою).

### 2.1. Базовий API (Manual Resource Management)

Базові функції використовуються у низькорівневому коді ядра або підсистемах, де життєвий цикл ресурсу не прив'язаний до структури `struct device`.

```c
/* Отримання однієї обов'язкової лінії */
struct gpio_desc *gpiod_get(struct device *dev, const char *con_id, 
                           enum gpiod_flags flags);

/* Отримання опціональної лінії (повертає NULL замість -ENOENT) */
struct gpio_desc *gpiod_get_optional(struct device *dev, const char *con_id, 
                                     enum gpiod_flags flags);

/* Отримання лінії з масиву за індексом */
struct gpio_desc *gpiod_get_index(struct device *dev, const char *con_id, 
                                  unsigned int idx, enum gpiod_flags flags);

/* Отримання опціональної лінії за індексом */
struct gpio_desc *gpiod_get_index_optional(struct device *dev, const char *con_id, 
                                           unsigned int idx, enum gpiod_flags flags);

/* Ручне вивільнення дескриптора лінії */
void gpiod_put(struct gpio_desc *desc);
```

### 2.2. Автоматизований Devres API (Рекомендований)

Префікс `devm_` означає, що виділений ресурс прив'язується до життєвого циклу пристрою `struct device`. Виклик `gpiod_put()` відбувається автоматично під час звільнення драйвера.

```c
struct gpio_desc *devm_gpiod_get(struct device *dev, const char *con_id, 
                                 enum gpiod_flags flags);

struct gpio_desc *devm_gpiod_get_optional(struct device *dev, const char *con_id, 
                                          enum gpiod_flags flags);

struct gpio_desc *devm_gpiod_get_index(struct device *dev, const char *con_id, 
                                       unsigned int idx, enum gpiod_flags flags);

struct gpio_desc *devm_gpiod_get_index_optional(struct device *dev, const char *con_id, 
                                                unsigned int idx, enum gpiod_flags flags);

void devm_gpiod_put(struct device *dev, struct gpio_desc *desc);
```

---

## 3. Механізми обробки помилок та кодування вказівників

### 3.1. Кодування коду помилки у вказівник (`ERR_PTR`)

Функції `gpiod_get*` не повертають `NULL` у разі виникнення збою. Натомість вони використовують ядерну концепцію кодування негативного цілочисельного коду помилки у значення вказівника: помилці відповідають останні `MAX_ERRNO` (4095) значень адресного простору — від `-MAX_ERRNO` до `-1`, які ніколи не бувають дійсними адресами.

Для перевірки результату виклику використовуються спеціальні макроси:

```c
struct gpio_desc *reset_gpio;

reset_gpio = devm_gpiod_get(dev, "reset", GPIOD_OUT_LOW);
if (IS_ERR(reset_gpio)) {
    int err = PTR_ERR(reset_gpio);
    
    if (err == -EPROBE_DEFER) {
        /* Контролер GPIO ще не ініціалізовано, чекаємо повторної спроби */
        return -EPROBE_DEFER;
    }
    
    dev_err(dev, "Failed to get reset GPIO: %d\n", err);
    return err;
}
```

### 3.2. Детальна класифікація кодів помилок

- **`-ENOENT` (No Such File or Directory):** Властивість з вказаним `con_id` відсутня у специфікації Device Tree чи ACPI. Для функцій `*_optional()` ця помилка перехоплюється ядром, і функція повертає `NULL`, що сигналізує про відсутність опціональної лінії.
- **`-EBUSY` (Device or Resource Busy):** Запитана лінія вже була захоплена іншим споживачем або підсистемою ядра (наприклад, драйвером TTY або I2C).
- **`-EPROBE_DEFER` (Driver Probe Deferral):** Властивість існує, але драйвер відповідного GPIO-контролера ще не пройшов ініціалізацію. Драйвер пристрою повинен негайно припинити виконання `probe()` і повернути цей код ядру.
- **`-EINVAL` (Invalid Argument):** Передано некоректні комбінації прапорів або відсутній вказівник `struct device`.

---

## 4. Читання та запис стану ліній

### 4.1. Атомарний доступ (Atomic Context Safe)

Ці функції призначені для роботи з контролерами GPIO, регістри яких відображені безпосередньо у фізичний адресний простір пам'яті процесора (MMIO). Вони гарантують миттєвий доступ і **не можуть викликати блокування чи вихід у сон**.

```c
/* Зчитування логічного стану лінії (1 = активний, 0 = неактивний) */
int gpiod_get_value(const struct gpio_desc *desc);

/* Встановлення логічного стану лінії */
void gpiod_set_value(struct gpio_desc *desc, int value);

/* Зчитування фізичного електричного рівня (ігнорує прапор ACTIVE_LOW) */
int gpiod_get_raw_value(const struct gpio_desc *desc);

/* Встановлення фізичного електричного рівня (ігнорує прапор ACTIVE_LOW) */
void gpiod_set_raw_value(struct gpio_desc *desc, int value);
```

### 4.2. Контекст із можливим сном (`_cansleep`)

Ці функції призначені для керування лініями на зовнішніх розширювачах портів (наприклад, PCF8574, MCP23017), підключених через шини I2C або SPI. Обмін даними вимагає надсилання послідовних пакетів та очікування завершення шинних транзакцій.

```c
/* Зчитування логічного стану лінії з можливістю сну */
int gpiod_get_value_cansleep(const struct gpio_desc *desc);

/* Встановлення логічного стану лінії з можливістю сну */
void gpiod_set_value_cansleep(struct gpio_desc *desc, int value);

/* Зчитування фізичного рівня з можливістю сну */
int gpiod_get_raw_value_cansleep(const struct gpio_desc *desc);

/* Встановлення фізичного рівня з можливістю сну */
void gpiod_set_raw_value_cansleep(struct gpio_desc *desc, int value);
```

> 🛑 **Попередження:** Виклик `gpiod_set_value()` замість `gpiod_set_value_cansleep()` для зовнішнього розширювача I2C спричиняє спрацювання перевірки `WARN_ON(desc->gdev->can_sleep)` і вивід стек-трейсу у `dmesg` — незалежно від того, з якого контексту зроблено виклик.

---

## 5. Пакетні операції з масивами ліній

Для одночасного керування декількома лініями (наприклад, паралельною шиною даних або бітбенгінгом) підсистема `gpiolib` виділяє спеціальну структуру `struct gpio_descs` та надає групові операції.

```c
struct gpio_descs {
    unsigned int ndescs;
    struct gpio_desc *desc[];
};

/* Отримання групи ліній з Device Tree */
struct gpio_descs *gpiod_get_array(struct device *dev, const char *con_id, 
                                   enum gpiod_flags flags);

struct gpio_descs *devm_gpiod_get_array(struct device *dev, const char *con_id, 
                                        enum gpiod_flags flags);

/* Одночасне встановлення значень для масиву ліній */
void gpiod_set_array_value(unsigned int array_size, 
                           struct gpio_desc **desc_array,
                           struct gpio_array *array_info, 
                           unsigned long *value_bitmap);

/* Пакетне встановлення значень для розширювачів I2C/SPI з сном */
void gpiod_set_array_value_cansleep(unsigned int array_size, 
                                    struct gpio_desc **desc_array,
                                    struct gpio_array *array_info, 
                                    unsigned long *value_bitmap);
```

Якщо усі лінії масиву належать одному апаратному контролеру GPIO, `gpiolib` автоматично оптимізує операцію та здійснює один єдиний запис у масовий регістр контролера (`chip->set_multiple`), що суттєво прискорює виведення даних.

---

## 6. Інтеграція з підсистемою переривань (IRQ)

Для перетворення лінії GPIO у номер системного переривання Linux використовується функція:

```c
int gpiod_to_irq(const struct gpio_desc *desc);
```

* **Призначення:** Повертає віртуальний номер системного переривання (Linux IRQ number), який можна передати у `request_threaded_irq()` або `devm_request_threaded_irq()`.
* **Помилка:** Повертає `-ENXIO`, якщо контролер лінії не реалізує метод `to_irq()` — тобто вказана лінія не має апаратної підтримки генерації переривань або не прив'язана до контролера переривань (`irq_domain`).
