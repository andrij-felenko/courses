# ⚙️ Практична реалізація DMA-відображень у драйвері ядра Linux

Цей навчальний проект демонструє розробку тестового драйвера периферійного пристрою шини PCI Express для ядра Linux. Практичний модуль ілюструє повний життєвий цикл управління пам'яттю прямого доступу (Direct Memory Access, DMA): налаштування розрядності системної шини (DMA masks), виділення зв'язаної (coherent) пам'яті під апаратні кільцеві буфери дескрипторів за допомогою функції `dma_alloc_coherent()`, та обробку мережевих чи дискових пакетів через потокове (streaming) відображення `dma_map_single()` з керуванням когерентністю кеш-пам'яті центрального процесора.

## Архітектура драйвера та поділ типів пам'яті

Сучасні високошвидкісні периферійні контролери (наприклад, мережеві адаптери Ethernet або NVMe-накопичувачі) працюють за принципом апаратних кільцевих буферів (Ring Buffers). Апаратура та центральний процесор розділяють між собою два типи даних:

1. **Кільце апаратних дескрипторів (Descriptor Ring):** Масив фіксованого розміру, який містить інформацію про транзакції (покажчики на буфери даних, довжину пакета, прапорці готовності). Оскільки і CPU, і контролер PCI Express постійно читають та оновлюють дескриптори у довільні моменти часу, цей масив виділяється у зв'язаній (coherent) безкешованій пам'яті.
2. **Буфери корисного навантаження (Data Buffers):** Масиви пам'яті, які містять безпосередній вміст мережевих пакетів чи блоків диска. Вони виділяються через стандартний сторінковий розподільник ядра (`kmalloc`) і відображаються тимчасово через потоковий інтерфейс (streaming mapping) лише на час виконання конкретної операції вводу-виводу.

---

## Вихідний код модуля ядра на мові C

Нижче наведено самодостатній модуль ядра Linux, який реалізує повний життєвий цикл управління DMA-ресурсами.

```c
#include <linux/module.h>
#include <linux/init.h>
#include <linux/pci.h>
#include <linux/dma-mapping.h>
#include <linux/slab.h>

#define DRV_NAME "demo_dma_driver"
#define RING_SIZE 16
#define PKT_BUF_SIZE 2048

/* Апаратний дескриптор кільцевого буфера, що передається у DMA-реєстри пристрою */
struct demo_dma_desc {
    __le64 buf_addr;  /* Шинна адреса (IOVA) буфера корисного навантаження */
    __le32 len;       /* Довжина пакета в байтах */
    __le32 flags;     /* Прапорці стану: bit 0 — READY, bit 1 — COMPLETED */
};

/* Приватний контекст драйвера пристрою */
struct demo_device {
    struct pci_dev *pdev;
    
    /* Coherent DMA: кільцевий буфер дескрипторів */
    struct demo_dma_desc *ring_cpu;
    dma_addr_t ring_dma;
    size_t ring_size_bytes;

    /* Streaming DMA: відображення окремого пакета даних */
    void *tx_buf_cpu;
    dma_addr_t tx_buf_dma;
};

/* Крок 1. Узгодження та налаштування розрядності DMA-маски */
static int demo_setup_dma_masks(struct pci_dev *pdev)
{
    int err;

    /* Намагаємося встановити повноцінне 64-бітне адресування */
    err = dma_set_mask_and_coherent(&pdev->dev, DMA_BIT_MASK(64));
    if (err) {
        dev_warn(&pdev->dev, "64-бітна DMA маска недоступна, спроба встановити 32-бітну\n");
        /* Якщо 64 біти не підтримуються материнською платою чи контролером, падаємо до 32 біт */
        err = dma_set_mask_and_coherent(&pdev->dev, DMA_BIT_MASK(32));
        if (err) {
            dev_err(&pdev->dev, "Не вдалося встановити жодну з сумісних DMA маск!\n");
            return err;
        }
    }

    dev_info(&pdev->dev, "DMA маску пристрою успішно узгоджено з ядром\n");
    return 0;
}

/* Крок 2. Виділення Coherent пам'яті для кільця дескрипторів */
static int demo_alloc_ring(struct demo_device *demo)
{
    struct device *dev = &demo->pdev->dev;

    demo->ring_size_bytes = RING_SIZE * sizeof(struct demo_dma_desc);

    /* dma_alloc_coherent гарантує фізичну підготовку безкешової пам'яті */
    demo->ring_cpu = dma_alloc_coherent(dev, demo->ring_size_bytes,
                                       &demo->ring_dma, GFP_KERNEL);
    if (!demo->ring_cpu) {
        dev_err(dev, "Збій виділення coherent пам'яті для кільцевого буфера\n");
        return -ENOMEM;
    }

    /* Явне обнулення пам'яті кільця */
    memset(demo->ring_cpu, 0, demo->ring_size_bytes);

    dev_info(dev, "Виділено кільце дескрипторів: CPU addr=%p, DMA IOVA=%pad\n",
             demo->ring_cpu, &demo->ring_dma);
    return 0;
}

/* Крок 3. Потокове відображення буфера даних (Streaming DMA) */
static int demo_map_tx_packet(struct demo_device *demo)
{
    struct device *dev = &demo->pdev->dev;

    /* Виділяємо звичайний кешований буфер з загального сторінкового пулу */
    demo->tx_buf_cpu = kmalloc(PKT_BUF_SIZE, GFP_KERNEL);
    if (!demo->tx_buf_cpu)
        return -ENOMEM;

    /* Заповнюємо тестовими даними */
    memset(demo->tx_buf_cpu, 0xAB, PKT_BUF_SIZE);

    /* Здійснюємо потокове відображення у напрямку від CPU до пристрою */
    demo->tx_buf_dma = dma_map_single(dev, demo->tx_buf_cpu,
                                      PKT_BUF_SIZE, DMA_TO_DEVICE);

    /* Обов'язкова перевірка помилки через dma_mapping_error */
    if (dma_mapping_error(dev, demo->tx_buf_dma)) {
        dev_err(dev, "Збій виконання dma_map_single()\n");
        kfree(demo->tx_buf_cpu);
        demo->tx_buf_cpu = NULL;
        return -EIO;
    }

    /* Записуємо конвертовані у Little-Endian дані в дескриптор */
    demo->ring_cpu[0].buf_addr = cpu_to_le64(demo->tx_buf_dma);
    demo->ring_cpu[0].len      = cpu_to_le32(PKT_BUF_SIZE);
    demo->ring_cpu[0].flags    = cpu_to_le32(0x1); /* READY flag */

    dev_info(dev, "Пакет успішно відображено для DMA: IOVA=%pad\n", &demo->tx_buf_dma);
    return 0;
}

/* Крок 4. Приклад ручної синхронізації кешу CPU (DMA Sync) */
static void demo_update_packet_payload(struct demo_device *demo)
{
    struct device *dev = &demo->pdev->dev;

    /* Тимчасово забираємо володіння буфером назад у CPU */
    dma_sync_single_for_cpu(dev, demo->tx_buf_dma, PKT_BUF_SIZE, DMA_TO_DEVICE);

    /* Тепер CPU має право читати та змінювати вміст буфера */
    ((char *)demo->tx_buf_cpu)[0] = 0xFF;

    /* Повертаємо володіння буфером пристрою перед передачею контролю DMA */
    dma_sync_single_for_device(dev, demo->tx_buf_dma, PKT_BUF_SIZE, DMA_TO_DEVICE);
}

/* Крок 5. Скасування відображень та очищення ресурсів */
static void demo_cleanup_dma(struct demo_device *demo)
{
    struct device *dev = &demo->pdev->dev;

    /* 1. Скасовуємо потокове відображення пакета */
    if (demo->tx_buf_dma && !dma_mapping_error(dev, demo->tx_buf_dma)) {
        dma_unmap_single(dev, demo->tx_buf_dma, PKT_BUF_SIZE, DMA_TO_DEVICE);
        demo->tx_buf_dma = 0;
    }

    if (demo->tx_buf_cpu) {
        kfree(demo->tx_buf_cpu);
        demo->tx_buf_cpu = NULL;
    }

    /* 2. Звільняємо coherent пам'ять кільця дескрипторів */
    if (demo->ring_cpu) {
        dma_free_coherent(dev, demo->ring_size_bytes,
                          demo->ring_cpu, demo->ring_dma);
        demo->ring_cpu = NULL;
        demo->ring_dma = 0;
    }

    dev_info(dev, "Усі DMA ресурси пристрою успішно вилучено\n");
}

/* Демонстраційна точка входу модуля ядра */
static int __init demo_dma_init(void)
{
    pr_info("Завантаження демонстраційного модуля підсистеми DMA mapping\n");
    return 0;
}

static void __exit demo_dma_exit(void)
{
    pr_info("Вивантаження демонстраційного модуля підсистеми DMA mapping\n");
}

module_init(demo_dma_init);
module_exit(demo_dma_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Antigravity Team");
MODULE_DESCRIPTION("Демонстраційний модуль DMA Mapping та IOMMU в ядрі Linux");
```

---

## Детальний розбір механізмів, крайових випадків та системних вимог

### 1. Порядок узгодження масок адресування

У функції `demo_setup_dma_masks()` драйвер обов'язково викликає `dma_set_mask_and_coherent()`. Найпоширенішою помилкою розробників початківців є нехтування перевіркою статусу повернення цієї функції. Якщо драйвер за замовчуванням розраховує на 64-бітне адресування, але пристрій встановлено у застарілу материнську плату чи системний шинний міст, який підтримує лише 32 біти, виклик поверне помилку `-EIO`. Якщо драйвер не виконає спробу відкату до `DMA_BIT_MASK(32)`, ядро дозволить виділення сторінок з адресами >4 ГБ, що призведе до зрізання старших бітів адреси периферійним контролером та мовчки виникаючого пошкодження оперативної пам'яті.

### 2. Вибір прапорців пам'яті (`GFP_KERNEL` проти `GFP_ATOMIC`)

Під час виділення зв'язаної пам'яті функцією `dma_alloc_coherent()` або під час відображення буферів через `kmalloc()` розробник повинен суворо враховувати контекст виконання коду.
- **Контекст процесу (Process Context):** Використовується прапорець `GFP_KERNEL`. Ядро має право переводити поточний потік у стан сну (sleep/schedule), якщо для виділення неперервної пам'яті потрібно очистити сторінковий кеш або виконати дефрагментацію пам'яті (CMA).
- **Контекст обробника переривань (Atomic Interrupt Context / ISR):** Перебування у стані сну заборонено. Драйвер зобов'язаний передавати прапорець `GFP_ATOMIC`. У цьому випадку підсистема пам'яті виділяє сторінки з аварійного зарезервованого пулу без переведення процесу в сон.

### 3. Захист від помилок утворення завад кешу (False Sharing)

Під час потокового відображення через `dma_map_single()` з напрямком `DMA_FROM_DEVICE` ядро виконує інвалідацію кеш-рядків CPU. Кеш-рядок процесора на сучасних архітектурах x86-64 та ARM64 має фіксований розмір 64 або 128 байтів.

Якщо буфер пакета даних не вирівняний по межі лінії кешу, або якщо його розмір не кратний розміру кеш-рядка, у той самий кеш-рядок потраплять суміжні змінні ядра. Коли підсистема DMA виконає інвалідацію кеш-рядка для прийому мережевого пакета, суміжні змінні ядра, модифіковані сусіднім ядром CPU, будуть моментально вилучені з кешу без збереження у RAM. Це створює так звані "фантомні дефекти" (silent memory corruption). Щоб запобігти цьому, підсистема `dma-mapping` вимагає, щоб усі буфери для `DMA_FROM_DEVICE` вирівнювалися за допомогою макросу `ARCH_DMA_MINALIGN`.

### 4. Конвертація порядку байтів (Endianness)

Зверніть увагу на використання макросів `cpu_to_le64()` та `cpu_to_le32()` під час заповнення структури `demo_dma_desc`. Більшість системних шин (зокрема PCI Express) та периферійних контролерів вимагають порядок байтів Little-Endian. Якщо драйвер виконується на Big-Endian процесорі (наприклад, IBM POWER або s390x), прямий запис шинної адреси `dma_addr_t` у дескриптор без конвертації призведе до того, що апаратура прочитає байтові регістри у зворотному порядку та виконає DMA за сміттєвою адресою.

### 5. Контракт передачі володіння та синхронізація кешу

У функції `demo_update_packet_payload()` продемонстровано роботу викликів `dma_sync_single_for_cpu()` та `dma_sync_single_for_device()`. Це єдиний безпечний спосіб модифікувати буфер CPU під час активного відображення. Звернення до пам'яті без виклику `dma_sync_single_for_cpu()` призведе до прочитання застарілих даних з кешу CPU, а спроба віддати буфер пристрою назад без виклику `dma_sync_single_for_device()` призведе до того, що пристрій прочитає застарілі дані з RAM, оскільки оновлення CPU залишилося в його кеші.

### 6. Порядок скасування відображень під час вивантаження

Функція `demo_cleanup_dma()` строго дотримується зворотного порядку звільнення ресурсів. Спочатку скасовується потокове відображення `dma_unmap_single()`, звільняється пам'ять пакета `kfree()`, і лише після цього скасовується зв'язане відображення кільця дескрипторів `dma_free_coherent()`. Спроба звільнити пам'ять кільця до скасування відображення пакетів призведе до звернення периферійного пристрою до вивільнених адрес IOVA (Use-After-Free / Invalid DMA Access).
