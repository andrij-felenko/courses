# 📋 Інтерфейс контролера та домену переривань: структури, методи й операції ядра

Підсистема керування перериваннями ядра Linux надає строго типізований програмний інтерфейс для розробників драйверів контролерів переривань, мостів шин та системних контролерів вводу-виводу. Цей інтерфейс інкапсулює апаратні операції в структурі struct irq_chip, логіку просторів імен у структурі struct irq_domain_ops та сервісні функції створення й трансляції дескрипторів. Нижче наведено детальний опис контрактів функцій, вимог до контексту виконання, правил синхронізації та життєвого циклу дескрипторів.

## Структура операцій контролера: struct irq_chip

Об'єкт struct irq_chip визначає набір функціональних покажчиків, які ядро викликає для безпосередньої маніпуляції лініями та регістрами фізичного контролера переривань. Усі методи приймають покажчик на структуру struct irq_data, через яку драйвер отримує локальний апаратний номер data->hwirq, приватні дані data->chip_data та маску процесорів.

`c
#include <linux/irq.h>

struct irq_chip {
    const char   *name;
    void        (*irq_enable)(struct irq_data *data);
    void        (*irq_disable)(struct irq_data *data);
    void        (*irq_ack)(struct irq_data *data);
    void        (*irq_mask)(struct irq_data *data);
    void        (*irq_unmask)(struct irq_data *data);
    void        (*irq_eoi)(struct irq_data *data);
    int         (*irq_set_affinity)(struct irq_data *data,
                                    const struct cpumask *dest, bool force);
    int         (*irq_retrigger)(struct irq_data *data);
    int         (*irq_set_type)(struct irq_data *data, unsigned int flow_type);
    int         (*irq_set_wake)(struct irq_data *data, unsigned int on);
    void        (*irq_bus_lock)(struct irq_data *data);
    void        (*irq_bus_sync_unlock)(struct irq_data *data);
    unsigned long flags;
};
`

### Семантика методів та правила синхронізації

Кожен функціональний покажчик викликається підсистемою ядра за чітко визначених умов синхронізації та в різному контексті процесора:

- **irq_enable(data) та irq_disable(data):** Повністю дозволяють або відключають прийом сигналу на фізичній лінії. Якщо драйвер не реалізує ці методи, ядро за замовчуванням викликає пару irq_unmask та irq_mask. Викликаються з утриманням спінлока дескриптора desc->lock.
- **irq_mask(data):** Записує бітову маску блокування в регістр контролера. Викликається в атомарному контексті переривання або під час виклику disable_irq_nosync(). У цьому методі суворо заборонено засинати, виділяти динамічну пам'ять або захоплювати сплячі м'ютекси.
- **irq_unmask(data):** Знімає бітову маску блокування, дозволяючи фізичній лінії знову сигналізувати центральному процесору про нові події. Викликається після завершення роботи драйвера або при виклику enable_irq().
- **irq_ack(data):** Квитує прийом імпульсу переривання. Метод є обов'язковим для ліній, чутливих до фронту (*edge-triggered*). Як правило, драйвер виконує запис логічної одиниці в регістр статусу (*write-1-to-clear*). Викликається в жорсткому hardirq-контексті.
- **irq_eoi(data):** Надсилає сигнал завершення обробки (*End of Interrupt*) у контролер з апаратною чергою пріоритетів (Intel APIC, ARM GIC). Метод викликається наприкінці роботи диспетчера handle_fasteoi_irq.
- **irq_set_affinity(data, dest, force):** Перенаправляє лінію переривання на вказану бітову маску процесорів dest. Повертає 0 у разі успішної зміни конфігурації, константу IRQ_SET_MASK_OK, якщо ядро має самостійно оновити внутрішні маски, або від'ємний код помилки (-EINVAL), якщо контролер не підтримує таку комбінацію ядер.
- **irq_set_type(data, flow_type):** Програмує електричну чутливість входу контролера. Параметр flow_type містить бітові прапорці IRQ_TYPE_EDGE_RISING, IRQ_TYPE_EDGE_FALLING, IRQ_TYPE_LEVEL_HIGH або IRQ_TYPE_LEVEL_LOW. Повертає 0 або від'ємний код помилки при некоректних параметрах.
- **irq_set_wake(data, on):** Вмикає або вимикає здатність цього переривання пробуджувати систему зі стану глибокого сну (*System Suspend*).
- **irq_bus_lock(data) та irq_bus_sync_unlock(data):** Застосовуються для повільних контролерів на шинах I2C або SPI. Метод irq_bus_lock захоплює м'ютекс драйвера, а irq_bus_sync_unlock надсилає накопичені зміни регістрів по шині у контексті потоку та відпускає м'ютекс.

## Операції домену переривань: struct irq_domain_ops

Структура struct irq_domain_ops визначає логіку зіставлення вузлів дерева пристроїв, створення дескрипторів та трансляції параметрів:

`c
#include <linux/irqdomain.h>

struct irq_domain_ops {
    int (*match)(struct irq_domain *d, struct device_node *node,
                 enum irq_domain_bus_token bus_token);
    int (*map)(struct irq_domain *d, unsigned int virq, irq_hw_number_t hw);
    void (*unmap)(struct irq_domain *d, unsigned int virq);
    int (*xlate)(struct irq_domain *d, struct device_node *node,
                 const u32 *intspec, unsigned int intsize,
                 unsigned long *out_hwirq, unsigned int *out_type);
    int (*alloc)(struct irq_domain *d, unsigned int virq,
                 unsigned int nr_irqs, void *arg);
    void (*free)(struct irq_domain *d, unsigned int virq,
                 unsigned int nr_irqs);
    int (*activate)(struct irq_domain *d, struct irq_data *irqd, bool reserve);
    void (*deactivate)(struct irq_domain *d, struct irq_data *irqd);
};
`

### Контракти методів домену

- **match(d, node, bus_token):** Перевіряє, чи належить вузол Device Tree або тип шини цьому екземпляру домену. Якщо метод відсутній, ядро порівнює покажчики d->of_node == node. Повертає 1 при збігу або 0 при невідповідності.
- **map(d, virq, hw):** Головна функція ініціалізації дескриптора. Викликається автоматично ядром під час першого створення зв'язку між hw та virq. Усередині методу драйвер зобов'язаний прив'язати таблицю операцій чіпа та призначити flow-handler через виклик irq_set_chip_and_handler(). Повертає 0 у разі успіху або від'ємний код помилки при невдачі.
- **unmap(d, virq):** Викликається під час видалення зв'язку та звільнення номера virq. Дозволяє драйверу контролера звільнити виділені динамічні ресурси.
- **xlate(d, node, intspec, intsize, out_hwirq, out_type):** Розбирає масив сирих 32-бітних чисел intspec з властивості interrupts дерева пристроїв і записує отриманий апаратний номер у *out_hwirq, а тип чутливості — у *out_type. Повертає 0 або -EINVAL, якщо розмір кортежу не відповідає очікуваному значенню.
- **alloc(d, virq, nr_irqs, arg):** Використовується в ієрархічних доменах для виділення ланцюжка дескрипторів на всіх рівнях каскаду. Метод викликає функцію irq_domain_alloc_irqs_parent() для передачі трансляції батьківському домену. Повертає 0 при успішному виділенні.
- **free(d, virq, nr_irqs):** Звільняє виділені ресурси ієрархічного домену та каскадно викликає звільнення на батьківському рівні.

## Сервісні функції реєстрації та управління доменами

Ядро Linux надає набір функцій для створення різних типів доменів та керування їхнім життєвим циклом:

`c
/* Створення лінійного домену переривань з таблицею O(1) */
struct irq_domain *irq_domain_add_linear(struct device_node *of_node,
                                         unsigned int size,
                                         const struct irq_domain_ops *ops,
                                         void *host_data);

/* Створення деревовидного домену для розріджених просторів номерів */
struct irq_domain *irq_domain_add_tree(struct device_node *of_node,
                                       const struct irq_domain_ops *ops,
                                       void *host_data);

/* Створення ієрархічного домену з прив'язкою до батьківського */
struct irq_domain *irq_domain_create_hierarchy(struct irq_domain *parent,
                                               unsigned int flags,
                                               unsigned int size,
                                               struct fwnode_handle *fwnode,
                                               const struct irq_domain_ops *ops,
                                               void *host_data);

/* Видалення домену з глобального списку ядра */
void irq_domain_remove(struct irq_domain *d);
`

### Параметри та повертані значення

- **irq_domain_add_linear:** Виділяє пам'ять під лінійний масив швидкого пошуку розміром size. Параметр host_data зберігає покажчик на приватну структуру драйвера. Повертає покажчик на новий struct irq_domain або NULL при нестачі оперативної пам'яті.
- **irq_domain_add_tree:** Створює домен на базі Radix Tree для обслуговування великих або розріджених діапазонів апаратних номерів (наприклад, векторів MSI).
- **irq_domain_create_hierarchy:** Створює дочірній домен і зв'язує його з батьківським доменом parent. Це дозволяє будувати багаторівневі стеки обробки (PCIe MSI -> GIC ITS -> GIC Core).
- **irq_domain_remove:** Видаляє домен із підсистеми ядра. Перед викликом усі створені мапінги повинні бути попередньо видалені, інакше виникне витік дескрипторів.

## Функції трансляції та виділення віртуальних номерів

`c
/* Створення нового або повернення існуючого віртуального номера */
unsigned int irq_create_mapping(struct irq_domain *host,
                                irq_hw_number_t hwirq);

/* Швидкий пошук існуючого номера без виділення нових дескрипторів */
unsigned int irq_find_mapping(struct irq_domain *host,
                              irq_hw_number_t hwirq);

/* Звільнення віртуального номера та дескриптора */
void irq_dispose_mapping(unsigned int virq);
`

- **irq_create_mapping:** Перевіряє, чи зареєстровано вже дескриптор для заданого hwirq. Якщо ні, виділяє новий системний номер virq, викликає метод ops->map і зберігає відображення в таблиці домену. Повертає номер virq або 0 при помилці виділення.
- **irq_find_mapping:** Виконує швидке безблокувальне читання з таблиці відображення. Призначена для використання в гарячому контексті обробника переривань. Повертає номер virq або 0, якщо переривання не зареєстроване.
- **irq_dispose_mapping:** Розриває зв'язок між hwirq та virq, викликає метод ops->unmap і повертає системний номер у пул вільних дескрипторів.

## Допоміжні функції налаштування дескрипторів

`c
/* Призначення чіпа та обробника потоку */
void irq_set_chip_and_handler(unsigned int irq, const struct irq_chip *chip,
                              irq_flow_handler_t handle);

/* Встановлення приватних даних контролера */
int irq_set_chip_data(unsigned int irq, void *data);

/* Налаштування каскадного ланцюгового обробника */
void irq_set_chained_handler_and_data(unsigned int irq,
                                      irq_flow_handler_t handle,
                                      void *data);
`

Ці функції викликаються всередині методу ops->map або під час ініціалізації каскадних контролерів для остаточного налаштування зв'язку між апаратним драйвером та підсистемою ядра.
