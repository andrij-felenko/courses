# 📋 Довідник PCI API ядра Linux

Цей документ містить фундаментальний опис типів даних, структур, макросів та системних функцій підсистеми PCI ядра Linux (`<linux/pci.h>`), які застосовуються під час розробки та налагодження драйверів пристроїв PCI Express.

> ℹ️ **Контекст ядра (Kernel Space):** Наведені нижче структури та функції виконуються виключно в режимі ядра Linux. У просторі ядра мова C є єдиним стандартом реалізації драйверів; C++ тут не застосовується через відсутність runtime-бібліотеки, винятків та відстеження стеку.

---

## 1. Головні структури даних підсистеми PCI

### 1.1 `struct pci_dev`
Об'єкт `struct pci_dev` описує екземпляр конкретного пристрою PCI або PCIe в системі. Створюється та ініціалізується підсистемою PCI Core під час перерахування шини (enumeration) на етапі завантаження або при підключенні гарячого пристрою (Hotplug).

:::code api-pci-kernel-interface/c/1-1-struct-pci-dev.c

Драйвер отримує вказівник на `struct pci_dev` як перший аргумент у функції `probe()`. Об'єкт `dev` керується лічильником посилань (refcount) через системні функції `pci_dev_get(pdev)` та `pci_dev_put(pdev)`. Якщо пристрій фізично видаляється із системи (Surprise Removal), підсистема маркує структуру як відключену, але об'єкт пам'яті звільняється лише після останнього `pci_dev_put()`.

Поле `dev` служить для виводу діагностичних повідомлень через `dev_info()`, `dev_err()`, `dev_dbg()`, а також для прив'язки приватного контексту драйвера за допомогою `pci_set_drvdata(pdev, data)` та `pci_get_drvdata(pdev)`.

### 1.2 `struct pci_driver`
Структура описує драйвер пристрою та реєструється в підсистемі PCI для автоматичного зв'язування з апаратурою (Driver Binding).

:::code api-pci-kernel-interface/c/1-2-struct-pci-driver.h

* **`probe()`:** Викликається ядрами PCI, коли підсистема знаходить фізичний пристрій, чий Vendor ID, Device ID або Class Code збігаються із записом у `id_table`. Якщо `probe()` повертає `0`, прив'язка вважається успішною. У разі помилки повертає від'ємний код (`-ENODEV`, `-ENOMEM`, `-EIO`).
* **`remove()`:** Викликається під час вивантаження модуля драйвера або гарячого відключення пристрою. Драйвер зобов'язаний звільнити всі відображення MMIO, скасувати зареєстровані вектори переривань, зупинити DMA-транзакції та вимкнути апаратуру.
* **`shutdown()`:** Викликається під час перезавантаження або вимкнення всієї системи (System Reboot/Poweroff). Застосовується для переведення контролера у безпечний стан без повного вивантаження драйвера.

### 1.3 `struct pci_device_id`
Структура запису в таблиці ідентифікаторів пристроїв. Масив підтримуваних пристроїв обов'язково повинен закінчуватися термінуючим порожнім записом `{ 0, }`.

:::code api-pci-kernel-interface/c/1-3-struct-pci-device-id.c

Для експорту таблиці ідентифікаторів у простір користувача (що дозволяє утилітам `udev` та `depmod` автоматично завантажувати потрібний модуль ядра при появі пристрою) використовується макрос `MODULE_DEVICE_TABLE(pci, my_id_table)`.

### 1.4 `struct pci_error_handlers`
Структура зворотного виклику для підтримки розширеної обробки апаратних помилок AER (Advanced Error Reporting).

```c
struct pci_error_handlers {
    pci_ers_result_t (*error_detected)(struct pci_dev *dev, pci_channel_state_t error);
    pci_ers_result_t (*mmio_enabled)(struct pci_dev *dev);
    pci_ers_result_t (*slot_reset)(struct pci_dev *dev);
    void (*reset_prepare)(struct pci_dev *dev);
    void (*reset_done)(struct pci_dev *dev);
    void (*resume)(struct pci_dev *dev);
};
```

---

## 2. Управління життєвим циклом пристрою та ресурсами BAR

### 2.1 Ввімкнення та вимкнення пристрою

```c
int pci_enable_device(struct pci_dev *dev);
int pcim_enable_device(struct pci_dev *dev);
void pci_disable_device(struct pci_dev *dev);
```

* **Механізм:** `pci_enable_device()` переводить пристрій зі стану зниженого енергоспоживання (D3hot/D3cold) у робочий стан D0, встановлює біт `Memory Space Enable` (Bit 1) та `I/O Space Enable` (Bit 0) у Command Register конфігураційного простору (offset `0x04`), а також запитує виділення IRQ у системного контролера переривань.
* **Керована версія (devres):** `pcim_enable_device()` виконує ті ж дії, але реєструє авто-виклики очищення: при збої або вивантаженні драйвера пристрій буде вимкнено автоматично.
* **Крайові випадки та інваріанти:**
  - Функція підтримує внутрішній лічильник `dev->enable_cnt`. Повторний виклик `pci_enable_device()` не викликає помилки, але вимагає відповідної кількості викликів `pci_disable_device()`.
  - Якщо пристрій перебуває в стані D3cold і системне джерело живлення слота вимкнено, функція ініціює виклик шинного регулятора ACPI/PM. При відсутності живлення повертається код `-EIO` або `-ENODEV`.
* **Повертає:** `0` при успіху або від'ємний код помилки (`-EIO`, `-ENODEV`, `-EBUSY`).

### 2.2 Резервування та перевірка регіонів BAR

```c
int pci_request_regions(struct pci_dev *dev, const char *res_name);
int pci_request_selected_regions(struct pci_dev *dev, int bars, const char *res_name);
void pci_release_regions(struct pci_dev *dev);
void pci_release_selected_regions(struct pci_dev *dev, int bars);
```

* **Механізм:** Запитує у підсистеми виділення ресурсів ядра зарезервоване монопольне право володіння регіонами BAR0..BAR5, які використовуються пристроєм. Реєстрація відображається у системних файлах `/proc/iomem` та `/proc/ioport` під іменем `res_name`.
* **Інваріант цілісності:** Упереджує конфлікти, коли два різні драйвери намагаються одночасно відобразити один і той самий фізичний BAR. Якщо інший драйвер вже зарезервував цей діапазон, виклик повертає `-EBUSY`.

### 2.3 Відображення MMIO пам'яті (`pci_iomap` / `pci_iounmap`)

```c
void __iomem *pci_iomap(struct pci_dev *dev, int bar, unsigned long maxlen);
void __iomem *pci_iomap_wc(struct pci_dev *dev, int bar, unsigned long maxlen);
void pci_iounmap(struct pci_dev *dev, void __iomem *addr);
void __iomem * const *pcim_iomap_table(struct pci_dev *dev);
```

* **Механізм:** Створює віртуальне відображення фізичного BAR з індексом `bar` (0..5) у віртуальний адресний простір ядра.
  - Для Memory BAR викликом `ioremap()` будуються сторінкові таблиці ядра з прапорцями No-Cache (Uncacheable, `_PAGE_PCD`).
  - `pci_iomap_wc()` використовує режим Write-Combining (`ioremap_wc()`), що є критичним для відеобуферів графічних прискорювачів, оскільки дозволяє процесору об'єднувати послідовні записи у кеш-лінії перед відправкою на шину PCIe.
  - Для I/O BAR повертає портову адресу для використання з `inb()`/`outb()`.
  - Масив `pcim_iomap_table()` повертає таблицю автоматично керованих відображень devres.
* **Крайові випадки:** Параметр `maxlen = 0` означає відображення всієї довжини BAR. Якщо BAR не існує, має нульову довжину або ядру не вдалося побудувати відображення, функція повертає `NULL`.
* **Правила доступу:** Доступ до віртуальних адрес `void __iomem *` суворо заборонено здійснювати через розіменування звичайних вказівників C (`*ptr`). Необхідно використовувати спеціальні аксесори ядра: `ioread8()`, `ioread16()`, `ioread32()`, `iowrite8()`, `iowrite16()`, `iowrite32()`. Окремий бар'єр `mmiowb()` більше не потрібен: до ядра 5.2 його ставили після серії записів під спінлоком, у 5.2 його прибрали з API — упорядкування тепер забезпечує саме звільнення спінлока.

---

## 3. Читання та запис атрибутів BAR

Для отримання характеристик фізичного BAR (початкової адреси, довжини та прапорців) використовуються уніфіковані макроси ядра:

* `pci_resource_start(dev, bar)` — повертає початкову фізичну адресу (тип `resource_size_t`, 32 або 64-бітну) для ресурсу `bar`.
* `pci_resource_end(dev, bar)` — повертає кінцеву фізичну адресу для ресурсу `bar`.
* `pci_resource_len(dev, bar)` — повертає повну довжину BAR у байтах (`end - start + 1`).
* `pci_resource_flags(dev, bar)` — повертає бітову маску властивостей ресурсу.

### Ключові бітові маски прапорців (`flags`):
* `IORESOURCE_MEM`: Регіон є адресною пам'яттю (Memory-Mapped I/O).
* `IORESOURCE_IO`: Регіон є адресою порту введення-виведення (Port I/O).
* `IORESOURCE_PREFETCH`: Пам'ять підтримує кешоване випереджальне читання (Prefetchable).
* `IORESOURCE_MEM_64`: BAR використовує 64-бітну адресацію (займає два послідовні 32-бітні регістри BARn та BARn+1).

---

## 4. Навігація та доступ до PCI Configuration Space

### 4.1 Функції прямого читання та запису

```c
int pci_read_config_byte(const struct pci_dev *dev, int where, u8 *val);
int pci_read_config_word(const struct pci_dev *dev, int where, u16 *val);
int pci_read_config_dword(const struct pci_dev *dev, int where, u32 *val);

int pci_write_config_byte(const struct pci_dev *dev, int where, u8 val);
int pci_write_config_word(const struct pci_dev *dev, int where, u16 val);
int pci_write_config_dword(const struct pci_dev *dev, int where, u32 val);
```

* **Механізм:** Виконують читання та запис у 256-байтний (PCI) або 4096-байтний (PCIe ECAM) конфігураційний простір пристрою. Параметр `where` задає байтовий зсув від початку конфігураційного масиву (`0x00`..`0x0FFF`).
* **Константи зсувів:** Застосовуються стандартні константи з `<linux/pci_regs.h>`:
  - `PCI_COMMAND` (`0x04`) — регістр команд (вмикання MMIO, IO, Bus Master).
  - `PCI_STATUS` (`0x06`) — регістр стану (прапорці помилок, підтримка capabilities).
  - `PCI_CAPABILITY_LIST` (`0x34`) — вказівник на перший елемент списку розширень.
* **Повертають:** `PCIBIOS_SUCCESSFUL` (`0`) у разі успіху або від'ємний код помилки шини (`PCIBIOS_DEVICE_NOT_FOUND`, `PCIBIOS_BAD_REGISTER_NUMBER`).
* **Крайові випадки:** Спроба читання зсуву з невирівняною адресою (наприклад, `pci_read_config_dword` зі зсувом `0x01`) призводить до апаратної помилки або повернення некоректного значення. Якщо пристрій відключився від шини під час виконання операції, хост-контролер повертає `0xFFFFFFFF` (Master Abort).

### 4.2 Пошук розширених можливостей (Capabilities)

```c
int pci_find_capability(struct pci_dev *dev, int cap);
int pci_find_ext_capability(struct pci_dev *dev, int cap);
int pci_find_next_capability(struct pci_dev *dev, u8 pos, int cap);
```

* **Механізм:** `pci_find_capability()` сканує зв'язаний список стандартних структур Capability у базовому конфігураційному просторі (`0x40`..`0xFF`). `pci_find_ext_capability()` шукає розширені структури PCIe Extended Capabilities у діапазоні `0x100`..`0x0FFF` (наприклад, `PCI_EXT_CAP_ID_ERR` для AER або `PCI_EXT_CAP_ID_SRIOV`).
* **Повертають:** Байтовий зсув знайденої структури в конфігураційному просторі або `0`, якщо можливість не підтримується апаратурою.

---

## 5. Виділення векторів переривань (MSI / MSI-X)

### 5.1 Алокація векторів

```c
int pci_alloc_irq_vectors(struct pci_dev *dev, unsigned int min_vecs,
                          unsigned int max_vecs, unsigned int flags);
void pci_free_irq_vectors(struct pci_dev *dev);
int pci_irq_vector(struct pci_dev *dev, unsigned int nr);
```

* **Механізм:** Запитує у підсистеми переривань виділення від `min_vecs` до `max_vecs` векторів.
* **Порядок пріоритету:** Спроба виділення виконується послідовно залежно від встановлених прапорів у `flags`:
  1. **MSI-X (`PCI_IRQ_MSIX`):** До 2048 векторів з окремими адресами й даними, записаними в таблицю в Memory BAR.
  2. **MSI (`PCI_IRQ_MSI`):** До 32 векторів із суміжними номерами.
  3. **Legacy INTx (`PCI_IRQ_LEGACY`; з ядра 6.8 прапорець зветься `PCI_IRQ_INTX`):** Спільна лінія переривання.
  4. `PCI_IRQ_ALL_TYPES`: Автоматична спроба в порядку MSI-X -> MSI -> Legacy.
* **Прив'язка до ядер CPU:** Якщо передано прапор `PCI_IRQ_AFFINITY`, ядро автоматично розподіляє виділені вектори між доступними процесорними ядрами системи для забезпечення балансування навантаження.
* **Крайові випадки:**
  - Якщо система не може виділити навіть `min_vecs` векторів, функція повертає від'ємний код помилки `-ENOSPC`.
  - Якщо виділено менше ніж `max_vecs`, повертається фактична кількість виділених векторів (позитивне число). Драйвер повинен уміти працювати з цією меншою кількістю.

### 5.2 Отримання системного IRQ

`pci_irq_vector(dev, nr)` перетворює локальний індекс вектора пристрою `nr` (`0`..`n-1`) у глобальний номер лінії IRQ ядра Linux. Отримане значення передається у системні функції `request_threaded_irq()` або `devm_request_threaded_irq()`.

---

## 6. Налаштування DMA, Bus Master та IOMMU

### 6.1 Активація режиму Bus Master

```c
void pci_set_master(struct pci_dev *dev);
void pci_clear_master(struct pci_dev *dev);
```

* **Механізм:** `pci_set_master()` встановлює біт `Bus Master Enable` (Bit 2) у Command Register конфігураційного простору.
* **Інваріант:** Поки біт Bus Master скинутий, пристрій не має права ініціювати транзакції на шині: його DMA-запити до оперативної пам'яті просто не виходять за межі контролера, а якщо апаратура все ж виставить такий пакет, Root Complex відкине його й зафіксує помилку.

### 6.2 Маскування адресації DMA

```c
int dma_set_mask_and_coherent(struct device *dev, u64 mask);
```

* **Механізм:** Інформує підсистему DMA та IOMMU ядра про максимальну фізичну розрядність адресації, яку підтримує апаратний контролер. Першим аргументом передається вказівник `&pdev->dev`.
* **Маски:**
  - `DMA_BIT_MASK(64)` — 64-бітна адресація системної RAM (Dual Address Cycle, DAC).
  - `DMA_BIT_MASK(32)` — 32-бітна адресація (Single Address Cycle, SAC, обмежена 4 ГБ).
* **Інваріант та транзитні буфери:** Якщо пристрій підтримує лише 32-бітний DMA, а системна пам'ять розташована вище 4 ГБ, ядро Linux автоматично задіяє транзитні буфери SWIOTLB (Bounce Buffers). Повертає `0` при успішному узгодженні маски.

### 6.3 Потокове та когерентне виділення DMA-буферів

```c
void *dma_alloc_coherent(struct device *dev, size_t size, dma_addr_t *dma_handle, gfp_t flag);
void dma_free_coherent(struct device *dev, size_t size, void *cpu_addr, dma_addr_t dma_handle);

dma_addr_t dma_map_single(struct device *dev, void *ptr, size_t size, enum dma_data_direction dir);
void dma_unmap_single(struct device *dev, dma_addr_t dma_handle, size_t size, enum dma_data_direction dir);
```

* **Когерентне виділення (`dma_alloc_coherent`):** Виділяє область оперативної пам'яті, яка одночасно доступна CPU та пристрою без необхідності явного скидання кешу. Повертає віртуальну адресу для CPU та фізичну адресу DMA у `dma_handle`.
* **Потокове відображення (`dma_map_single`):** Відображає вже існуючий буфер пам'яті ядра (`kmalloc` або `alloc_pages`) для одноразової DMA-транзакції. На архітектурах без апаратної когерентності кешу (ARM, MIPS) викликає скидання кеш-ліній CPU.
* **Напрямок транзакції (`dir`):** `DMA_TO_DEVICE` (запис у пристрій), `DMA_FROM_DEVICE` (читання з пристрою), `DMA_BIDIRECTIONAL`.

---

## 7. Керування живленням (PCI Power Management)

```c
int pci_set_power_state(struct pci_dev *dev, pci_power_t state);
pci_power_t pci_choose_state(struct pci_dev *dev, pm_message_t state);
int pci_enable_wake(struct pci_dev *dev, pci_power_t state, bool enable);
```

* **Механізм:** `pci_set_power_state()` переводить пристрій між станами PM: `PCI_D0` (робочий), `PCI_D1`, `PCI_D2` (проміжні енергозберігаючі стани) та `PCI_D3hot` / `PCI_D3cold` (стан глибокого сну).
* **Інваріант:** Перехід зі стану D3hot у D0 вимагає від ядра повного відновлення конфігураційного простору через `pci_restore_state(dev)`, оскільки внутрішній стан регістрів контролера міг бути скинутий.

---

## 8. Повний приклад реалізації драйвера PCIe

Нижче наведено самодостатній приклад реалізації драйвера PCIe пристрою з використанням сучасного API ядра Linux (`pcim_` managed interface, MSI-X, BAR0 MMIO та DMA).

:::code api-pci-kernel-interface/c/8-povnyi-pryklad.c

### 8.1 Розбір послідовності probe та крайових випадків

1. **Кероване виділення ресурсів (devres):** Використання `pcim_enable_device()` та `pcim_iomap_regions()` спрощує очищення ресурсів. При виклику `my_pci_remove()` або у разі виникнення помилки всередині `probe()` задекодовані MMIO-адреси скасовуються підсистемою ядра без ризику витоку ресурсів.
2. **Виділення векторів:** Алгоритм `pci_alloc_irq_vectors(pdev, 1, 4, PCI_IRQ_ALL_TYPES)` гарантує, що драйвер задіяє MSI-X якщо платформа підтримує вектори, інакше перейде на MSI або Legacy.
3. **Обробка вивантаження (remove):** При вивантаженні обов'язково виконується `pci_clear_master()`. Це гарантує, що якщо апаратний пристрій збійний і продовжить генерувати DMA-транзакції після вивантаження драйвера, ці транзакції будуть негайно заблоковані на рівні Root Complex.

---

## 9. Віртуалізація SR-IOV та обробка апаратних помилок AER

### 9.1 API підтримки SR-IOV (Single Root I/O Virtualization)

Розширення SR-IOV дозволяє одному фізичному контролеру (Physical Function, PF) створювати декілька віртуальних пристроїв (Virtual Functions, VF), кожен з яких має власний BDF та власні BAR для прямого прокидання у віртуальні машини KVM/QEMU.

```c
int pci_enable_sriov(struct pci_dev *dev, int nr_virtfn);
void pci_disable_sriov(struct pci_dev *dev);
int pci_num_vf(struct pci_dev *dev);
int pci_vfs_assigned(struct pci_dev *dev);
```

* **`pci_enable_sriov()`:** Викликається з колбеку `sriov_configure` драйвера PF. Активує `nr_virtfn` віртуальних функцій. Ядро зчитує конфігурацію з розширеного регістру `PCI_EXT_CAP_ID_SRIOV`, виділяє суміжні індекси BDF для кожної VF та динамічно розраховує регіони BAR для VF.
* **`pci_disable_sriov()`:** Вимикає всі віртуальні функції, звільняючи їхні ресурси в системі.
* **Крайові випадки та інваріанти:**
  - Кількість `nr_virtfn` не повинна перевищувати `InitialVFs` / `TotalVFs`, прочитане з розширеної капабіліті SR-IOV (`PCI_SRIOV_TOTAL_VF`). Перевищення цього числа призводить до повернення помилки `-EINVAL`.
  - Спроба виклику `pci_disable_sriov()`, коли хоча б одна VF прокинута у запущену віртуальну машину (перевіряється через `pci_vfs_assigned()`), призводить до помилки `-EBUSY` для збереження цілісності системи.

### 9.2 Відновлення пристрою після апаратних помилок AER

При виникненні апаратної помилки на шині PCIe (наприклад, скидання лінку через заваду або неотримання відповіді TLP) підсистема AER ядра Linux звертається до колбеків `struct pci_error_handlers`:

1. **`error_detected(dev, state)`:** Пристрій переводиться в стан розірваного каналу (`pci_channel_io_frozen` при невідновлюваній помилці або `pci_channel_io_normal` при усуненій). Драйвер повинен негайно зупинити всі активні DMA-черги, скасувати нові операції I/O та вимкнути апаратні переривання. Залежно від стану повертає:
   - `PCI_ERS_RESULT_CAN_RECOVER`: Пристрій спроможний відновити роботу без апаратного скидання слота.
   - `PCI_ERS_RESULT_NEED_RESET`: Пристрій потребує повного перезавантаження через подачу сигналу Reset на слоті PCIe.
   - `PCI_ERS_RESULT_DISCONNECT`: Пристрій перейшов у незворотний апаратний збій (Surprise Down) і повинен бути виключений із системи.
2. **`slot_reset(dev)`:** Викликається підсистемою ядра після подачі сигналу апаратного скидання Secondary Bus Reset на слоті PCIe. Драйвер зобов'язаний заново викликати `pci_restore_state(dev)` для відновлення конфігураційних регістрів, переініціалізувати вказівники BAR, активувати біт Bus Master та виділити векторні переривання.
3. **`resume(dev)`:** Завершальний крок ланцюжка відновлення. Викликається після того, як пристрій повернуто в робочий стан D0. Драйвер відновлює нормальну обробку переривань, розблоковує черги DMA та відновлює виконання системних запитів. Значення `resume()` не повертає — воно оголошене як `void`, а успішність відновлення підсистема AER визначає за результатами попередніх колбеків.
