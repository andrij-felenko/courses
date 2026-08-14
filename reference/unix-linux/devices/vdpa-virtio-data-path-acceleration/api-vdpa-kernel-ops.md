# 📋 Інтерфейс vDPA у ядрі Linux та ioctl-команди vhost-vdpa

Фреймворк vDPA пропонує дворазово розмежовану систему програмних інтерфейсів. На низькому рівні ядра Linux реалізовано C-API для розробників драйверів мережевих карт SmartNIC (`struct vdpa_config_ops`), які транслюють стандартні команди у пропрієтарні команди кремнію. На високому рівні функціонує користувацький `ioctl`-інтерфейс через файлові вузли `/dev/vhost-vdpa-N`, призначений для взаємодії з гіпервізорами (QEMU, KVM, Cloud-Hypervisor, Firecracker).

## 1. Внутрішньоядерний інтерфейс ядра: struct vdpa_config_ops

Кожен драйвер апаратного забезпечення (наприклад, `mlx5_vdpa` для апаратури NVIDIA/Mellanox або `ifcvf` для платформ Intel) описує специфіку свого кремнію за допомогою таблиці колбеків `struct vdpa_config_ops` (визначена в системному заголовку `<linux/vdpa.h>`).

Низькорівнева таблиця колбеків ядра оперує наступними основними блоками функцій:

```c
struct vdpa_config_ops {
    /* Налаштування зв'язку з IOMMU та апаратними ASID */
    int (*set_map)(struct vdpa_device *vdev, u32 asid, struct vhost_iotlb *iotlb);
    int (*dma_map)(struct vdpa_device *vdev, u32 asid, u64 iova, u64 size, u64 pa, u32 perm);
    int (*dma_unmap)(struct vdpa_device *vdev, u32 asid, u64 iova, u64 size);

    /* Опитування та зміна стану virtqueue (потрібно для Live Migration) */
    int (*get_vq_state)(struct vdpa_device *vdev, u16 idx, struct vdpa_vq_state *state);
    int (*set_vq_state)(struct vdpa_device *vdev, u16 idx, const struct vdpa_vq_state *state);

    /* Ініціалізація структур ring адресації */
    void (*set_vq_address)(struct vdpa_device *vdev, u16 idx,
                           u64 desc_area, u64 driver_area, u64 device_area);
    void (*set_vq_num)(struct vdpa_device *vdev, u16 idx, u32 num);
    void (*kick_vq)(struct vdpa_device *vdev, u16 idx);
    void (*set_vq_cb)(struct vdpa_device *vdev, u16 idx, struct vdpa_callback *cb);
    void (*set_vq_ready)(struct vdpa_device *vdev, u16 idx, bool ready);
    bool (*get_vq_ready)(struct vdpa_device *vdev, u16 idx);

    /* Узгодження прапорів virtio та байтів статусу */
    u64 (*get_device_features)(struct vdpa_device *vdev);
    int (*set_driver_features)(struct vdpa_device *vdev, u64 features);
    u8 (*get_status)(struct vdpa_device *vdev);
    void (*set_status)(struct vdpa_device *vdev, u8 status);
    void (*reset)(struct vdpa_device *vdev);

    /* Робота з простором конфігурації пристрою (MAC, MTU, Links) */
    size_t (*get_config_size)(struct vdpa_device *vdev);
    void (*get_config)(struct vdpa_device *vdev, unsigned int offset,
                       void *buf, unsigned int len);
    void (*set_config)(struct vdpa_device *vdev, unsigned int offset,
                       const void *buf, unsigned int len);

    /* Прив'язка групи черг до індексу ASID */
    u32 (*get_vq_group)(struct vdpa_device *vdev, u16 idx);
    int (*set_group_asid)(struct vdpa_device *vdev, u32 group, u32 asid);
};
```

### Подетальний розбір груп методів ядра:

1. **Керування таблицями відображення IOMMU (`set_map`, `dma_map`, `dma_unmap`):** Ці операції виконуються для трансляції віртуальних адрес введення-виведення (IOVA) у фізичні адреси хоста (HPA). Якщо SmartNIC має власну таблицю IOMMU, ядро передає всю таблицю IOTLB через `set_map`. Якщо пристрій спирається на загальносистемний IOMMU (наприклад, Intel VT-d або AMD-Vi), ядро викликає точкові мапінги `dma_map` та `dma_unmap`.
2. **Збереження та відновлення стану кілець (`get_vq_state`, `set_vq_state`):** Повертають або відновлюють поточний лічильник дескрипторів (`last_avail_idx` та `last_used_idx`) для вказаної черги. Під час живої міграції гіпервізори заморожують пристрій через `set_status(RESET)` та вичитують цей стан, щоб передати його новому хосту без втрати чи дублювання пакетів.
3. **Конфігурація кілець та сигналізація дверних дзвінків (`set_vq_address`, `kick_vq`, `set_vq_cb`):** Пов'язують кільцеві буфери з апаратними регістрами ASIC. Метод `kick_vq` дозволяє ядру вручну відправити дверний дзвінок (doorbell) в апаратуру, а `set_vq_cb` реєструє функцію зворотного виклику ядра при надходженні апаратного переривання від SmartNIC.
4. **Конфігураційний простір пристрою (`get_config`, `set_config`):** Забезпечує допуск до регістрів конфігурації конкретного типу virtio (для `virtio-net` — це MAC-адреса, статус лінка, MTU, кількість черг RSS; для `virtio-blk` — це обсяг диска, розмір сектора, геометрія).

### 1.1. Детальна специфікація об'єкта стану черги `struct vdpa_vq_state`

Для підтримки як розділених (split), так і упакованих (packed) віртчерг ядро визначає об'єднану структуру стану:

```c
struct vdpa_vq_state_split {
    u16 avail_index; /* Поточний індекс доступних дескрипторів */
};

struct vdpa_vq_state_packed {
    u16 last_avail_idx; /* Індекс доступного дескриптора у кільці */
    u16 last_used_idx;  /* Індекс використаного дескриптора */
    u8  avail_counter;  /* Однобітовий прапор фази доступності */
    u8  used_counter;   /* Однобітовий прапор фази використання */
};

struct vdpa_vq_state {
    union {
        struct vdpa_vq_state_split split;
        struct vdpa_vq_state_packed packed;
    };
};
```

Цей об'єкт дозволяє драйверу `vhost-vdpa` прозоро заморожувати та відновлювати стан черги будь-якого типу під час живої міграції віртуальної машини.

---

## 2. Користувацький ioctl-інтерфейс /dev/vhost-vdpa-N

Користувацькі процеси (QEMU, Rust VMM) взаємодіють із підсистемою vDPA через символьний пристрій `/dev/vhost-vdpa-N`. Інтерфейс розширює стандартний заголовок `<linux/vhost.h>` специфічними викликами `VHOST_VDPA_*`.

### 2.1. Докладна таблиця ioctl-команд vhost-vdpa

| Ioctl команда | Аргумент / Тип | Напрямок | Докладний опис та призначення |
| :--- | :--- | :--- | :--- |
| `VHOST_VDPA_GET_DEVICE_ID` | `__u32 *` | Read (`_IOR`) | Повертає ID пристрою virtio (1 = Network, 2 = Block, 3 = Console, 9 = 9P FS). |
| `VHOST_VDPA_GET_STATUS` | `__u8 *` | Read (`_IOR`) | Зчитує поточний байт статусу virtio (наприклад, `VIRTIO_CONFIG_S_DRIVER_OK`). |
| `VHOST_VDPA_SET_STATUS` | `const __u8 *` | Write (`_IOW`) | Записує байт статусу, активуючи або скидаючи пристрій в апаратурі. |
| `VHOST_VDPA_GET_CONFIG` | `struct vhost_vdpa_config *` | Read/Write (`_IOWR`) | Зчитує фрагмент конфігураційного простору (MAC-адреса, MTU, дуплекс). |
| `VHOST_VDPA_SET_CONFIG` | `struct vhost_vdpa_config *` | Write (`_IOW`) | Записує нові параметри в конфігураційний простір пристрою. |
| `VHOST_VDPA_GET_IOVA_RANGE` | `struct vhost_vdpa_iova_range *` | Read (`_IOR`) | Отримує підтримуваний апаратурою діапазон віртуальних адрес I/O. |
| `VHOST_VDPA_GET_VRING_GROUP` | `struct vhost_vdpa_mgmtdev_group *` | Read/Write (`_IOWR`) | Запитує номер групи IOMMU для вказаної черги `index`. |
| `VHOST_VDPA_SET_GROUP_ASID` | `struct vhost_vdpa_vring_asid *` | Write (`_IOW`) | Зв'язує групу черг із конкретним табличним простіром ASID у IOMMU. |
| `VHOST_SET_VRING_ADDR` | `struct vhost_vring_addr *` | Write (`_IOW`) | Передає фізичні (GPA) адреси Descriptor, Available та Used кілець. |
| `VHOST_SET_VRING_KICK` | `struct vhost_vring_file *` | Write (`_IOW`) | Реєструє `eventfd`, через який гість сповіщає апаратуру про нові буфери. |
| `VHOST_SET_VRING_CALL` | `struct vhost_vring_file *` | Write (`_IOW`) | Реєструє `eventfd` для генерації MSI-X переривань від SmartNIC у гість. |
| `VHOST_SET_VRING_ENABLE` | `struct vhost_vring_state *` | Write (`_IOW`) | Вмикає або вимикає обробку конкретної віртчерги в апаратурі. |

### 2.2. Формат та обробка структури `vhost_vdpa_config`

Для зчитування конфігурації (наприклад, MAC-адреси мережевої карти) використовується структура з гнучким масивом:

```c
struct vhost_vdpa_config {
    __u32 off;    /* Зсув у конфігураційному просторі (байтів) */
    __u32 len;    /* Довжина буфера для зчитування/запису */
    __u8 buf[];   /* Гнучкий масив байтів конфігурації */
};
```

При виконанні ioctl `VHOST_VDPA_GET_CONFIG` ядро перевіряє, щоб сума `off + len` не перевищувала загальний розмір конфігураційного простору, повернутий драйвером через `get_config_size()`. Якщо для virtio-net потрібно зчитати MAC-адресу, `off` встановлюється в `0`, a `len` — у `6`. Зчитуваний буфер містить шість байтів фізичної MAC-адреси, зпрограмованої у SmartNIC. При виклику `VHOST_VDPA_SET_CONFIG` ядро транслює записаний буфер через колбек `.set_config()` у фізичний контролер.

---

## 3. Реєстрація символьних пристроїв та обробка помилок у ядрі

Модуль `vhost_vdpa` реєструє старший номер символьного пристрою (chrdev major number) і динамічно виділяє молодші номери (minor numbers) для кожного екземпляра пристрою. При виконанні виклику `open("/dev/vhost-vdpa-N")` ядро ініціалізує внутрішній контекст `struct vhost_vdpa`, що містить таблицю IOTLB та посилання на відповідний `struct vdpa_device`.

Під час виконання ioctl-операцій ядро повертає стандартизовані коди помилок у разі порушення контракту:

- **`EFAULT`:** Виникає, коли вказувач на структуру простору користувача є невалідним або спостерігається збій при виклику `copy_from_user()` / `copy_to_user()`.
- **`EINVAL`:** Передано неприпустимий розмір черги, неузгоджений напрямок зсуву конфігурації або некоректний ідентифікатор групи ASID.
- **`EBUSY`:** Спроба змінити конфігурацію чи адреси віртчерги під час активного стану пристрою (`DRIVER_OK`), коли пристрій не було попередньо скинуто у стан `RESET`.
- **`EOPNOTSUPP`:** Запитана команда ioctl або прапорець virtio не підтримується конкретним апаратним драйвером SmartNIC.

Сигналізація дверних дзвінків `VHOST_SET_VRING_KICK` та сповіщень `VHOST_SET_VRING_CALL` спирається на внутрішньоядерний об'єкт `struct eventfd_ctx`. При передачі файлового дескриптора `eventfd` через ioctl ядро виконує `eventfd_ctx_fdget()`, створюючи прямий вказувач зв'язку між апаратним перериванням SmartNIC та віртуальним перериванням KVM.

---

## 4. Організація груп IOMMU та Address Space Identifier (ASID)

Для забезпечення апаратної ізоляції vDPA підтримує концепцію груп черг та просторів адрес ASID.

```c
struct vhost_vdpa_vring_asid {
    __u32 index; /* Індекс віртчерги */
    __u32 asid;  /* Призначений ідентифікатор простору адрес */
};

struct vhost_vdpa_iova_range {
    __u64 first; /* Перша допустима віртуальна адреса I/O */
    __u64 last;  /* Остання допустима віртуальна адреса I/O */
};
```

За допомогою `VHOST_VDPA_GET_VRING_GROUP` QEMU запитує, до якої апаратної групи належить черга `index`. Після цього команда `VHOST_VDPA_SET_GROUP_ASID` зв'язує цю групу з окремою таблицею мапінгу IOMMU. Це дозволяє ізолювати керуючу чергу Control Virtqueue (CVQ) від основних черг передачі даних (Rx/Tx queues), забезпечуючи найвищий рівень захисту від некоректних DMA-транзакцій.
