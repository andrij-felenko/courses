# ⚙️ Приклад формування та надсилання команд Virtio GPU

Ця вставка містить практичну реалізацію створення, налаштування та надсилання командних пакетів для виділення 2D-кадрового буфера, прив'язки фізичної пам'яті гостя, передачі піксельних даних та синхронізації виконання у пристрої `virtio-gpu`. Документ детально демонструє, як низькорівневі C- та C++-структури даних перетворюються на дескриптори Virtqueue для комунікації між гостьовим драйвером та гіпервізором хоста, а також як графічна підсистема ядра Linux (DRM/KMS) транслює системні виклики користувацького простору в команди віртуалізованого пристрою.

---

## 1. Архітектура надсилання команд через Virtqueue

Передача команд у пристрої `virtio-gpu` відбувається за допомогою кільцевих буферів Virtqueue (управляюча черга `controlq`, Queue Index 0). Процес відправки команди вимагає від системного драйвера виконання суворого протоколу роботи з пам'яттю та дотримання послідовності дій:

1. **Виділення та підготовка командного буфера:** Драйвер виділяє безперервний блок пам'яті в RAM гостя для розміщення структури команди (наприклад, `virtio_gpu_resource_create_2d`). Посторінкового вирівнювання тіло команди не потребує: дескриптор описує довільну фізичну адресу й довжину, а вимога вирівнювання стосується самих кілець Virtqueue, а не буферів, на які вони вказують. Важливо лише, щоб блок був фізично неперервним — інакше його доведеться описати кількома дескрипторами.
2. **Виділення буфера відповіді:** Драйвер виділяє окремий блок пам'яті для зберігання заголовка відповіді `virtio_gpu_ctrl_hdr`, куди гіпервізор запише результат обробки після завершення команди апаратним чи програмним бекендом хоста.
3. **Формування кільцевих дескрипторів (Scatter-Gather List):**
   * **Дескриптор 1 (Request Descriptor):** Вказує на структуру команди. Встановлюється прапорець `VRING_DESC_F_NEXT` (є наступний дескриптор у ланцюжку). Окремого прапорця «лише для читання» не існує: дескриптор без `VRING_DESC_F_WRITE` за визначенням доступний пристрою тільки на читання.
   * **Дескриптор 2 (Response Descriptor):** Вказує на буфер відповіді. Встановлюється прапорець `VRING_DESC_F_WRITE` (пам'ять доступна гіпервізору для запису результату виконання).
4. **Оновлення буфера доступних дескрипторів (Available Ring):** Драйвер поміщає індекс голови ланцюжка дескрипторів у масив `avail->ring`.
5. **Бар'єр пам'яті (Memory Barrier):** Виконується `smp_wmb()` — і лише після нього драйвер збільшує `avail->idx`. Порядок саме такий: бар'єр гарантує, що заповнені структури й дескриптори стануть видимі хосту раніше за індекс, який на них указує.
6. **Сповіщення гіпервізора (Doorbell):** Драйвер виконує виклик `outw()` або записує індекс черги в MMIO/PCI-регістр `Virtio Queue Notify`. Це викликає вихід із контексту віртуальної машини (VM-Exit) і передає управління обробнику гіпервізора (QEMU / crosvm / Firecracker).

---

## 2. Інтеграція з підсистемою DRM/KMS ядра Linux

У ядрі гостьової операційної системи Linux драйвер `virtio_gpu.ko` не працює ізольовано, а інтегрується у стандартний графічний стек через фреймворк Direct Rendering Manager (DRM) та Kernel Mode Setting (KMS).

```
+-------------------------------------------------------------------+
|               Користувацький простір (Userspace)                  |
|    Mesa 3D (virgl/venus) / Xorg / Wayland Compositor (Sway, KWin) |
+-------------------------------------------------------------------+
                                 │
                                 ▼ System Calls: ioctl(/dev/dri/card0)
+-------------------------------------------------------------------+
|                  Підсистема DRM/KMS ядра гостя                    |
|      GEM (Graphics Execution Manager) / TTM Memory Manager        |
+-------------------------------------------------------------------+
                                 │
                                 ▼ Трансляція у команди Virtio
+-------------------------------------------------------------------+
|                  Драйвер virtio_gpu.ko (Virtqueue)                |
+-------------------------------------------------------------------+
```

Коли користувацький застосунок (наприклад, графічний сервер Wayland або 3D-бібліотека Mesa) бажає створити буфер кадру, відбувається такий ланцюг системних подій:

1. **Системний виклик IOCTL:** Застосунок викликає `ioctl(fd, DRM_IOCTL_VIRTGPU_RESOURCE_CREATE, &args)`.
2. **Створення GEM-об'єкта:** Модуль ядра `virtio_gpu.ko` створює внутрішній об'єкт DRM GEM (Graphics Execution Manager) та присвоює йому унікальний у межах ядра ідентифікатор `handle`.
3. **Виділення `resource_id`:** Драйвер генерує глобальний для віртуальної машини `resource_id` та надсилає в управляючу чергу `controlq` команду `VIRTIO_GPU_CMD_RESOURCE_CREATE_2D`.
4. **Мапінг пам'яті у користувацький простір:** Для того щоб застосунок міг малювати в кадровому буфері, ядро виконує `ioctl(fd, DRM_IOCTL_VIRTGPU_MAP, &map_args)` та повертає зсув для системного виклику `mmap()`.

### Роль TTM та механізм DMA-BUF (PRIME)

Для ефективного управління пам'яттю драйвер `virtio_gpu.ko` задіює менеджер пам'яті TTM (Translation Table Manager), який класифікує графічні буфери за доменами пам'яті (System RAM, GTT — Graphics Translation Table, VRAM). Оскільки `virtio-gpu` є паравіртуалізованим пристроєм, він не має власної фізичної VRAM усередині віртуальної машини, тому всі кадрові буфери розміщуються у системній RAM гостя (домен `TTM_PL_SYSTEM` або `TTM_PL_TT`).

Для уможливлення безперешкодного обміну графічними буферами між різними процесами користувацького простору (наприклад, між браузером Firefox і віконним менеджером Wayland) драйвер підтримує механізм **DMA-BUF (PRIME)**. Завдяки системному виклику `ioctl(fd, DRM_IOCTL_PRIME_HANDLE_TO_FD, &prime_args)` GEM-об'єкт Virtio GPU експортується як стандартний файловий дескриптор DMA-BUF. Інший процес відкриває цей дескриптор і виконує прямий мапінг кадрового буфера у свій адресний простір, усуваючи будь-яке проміжне копіювання байтів на рівні користувацького простору.

---

## 3. Покроковий розбір ланцюжка дескрипторів та трансляція сторінок

Розглянемо фізичну структуру дескрипторів vring у пам'яті при надсиланні команди створення 2D-ресурсу:

```
[Available Ring] ──► Index #4 (Head of chain)
                           │
                           ▼
[Descriptor #4]  addr = 0x104000 (cmd: virtio_gpu_resource_create_2d)
                 len  = 40 bytes
                 flags = VRING_DESC_F_NEXT
                 next = #5
                           │
                           ▼
[Descriptor #5]  addr = 0x104040 (resp: virtio_gpu_ctrl_hdr)
                 len  = 24 bytes
                 flags = VRING_DESC_F_WRITE
                 next = 0
```

Гіпервізор зчитує дескриптор #4, визначає тип команди `VIRTIO_GPU_CMD_RESOURCE_CREATE_2D`, виділяє відповідні ресурси у графічному стеку хоста, записує результат `VIRTIO_GPU_RESP_OK_NODATA` за адресою дескриптора #5 і генерує переривання для гостя (або оновлює `Used Ring`).

При передачі вагомих обсягів графічних даних (кадрових буферів або текстур) одного командного дескриптора недостатньо. Драйвер гостя формує другу команду — `VIRTIO_GPU_CMD_RESOURCE_ATTACH_BACKING`, яка передає гіпервізору таблицю фізичних сторінок гостя (`virtio_gpu_mem_entry`). Такий підхід реалізує механізм Scatter-Gather DMA:

```
[Cmd Attach Backing] ──► [Array of virtio_gpu_mem_entry]
                               │
                               ├─► Entry 0: addr = 0x205000, length = 4096
                               ├─► Entry 1: addr = 0x206000, length = 4096
                               └─► Entry N: addr = 0x20A000, length = 4096
```

Гіпервізор використовує цей масив для мапінгу фізичної пам'яті гостя у простір хоста через виклики `mmap()` чи `cpu_physical_memory_map()`, уможливлюючи прямий доступ пристрою без проміжного копіювання байтів через сокети.

### Закріплення сторінок пам'яті (Page Pinning)

Перед відправкою команди `RESOURCE_ATTACH_BACKING` ядро гостя зобов'язане закріпити відповідні фізичні сторінки в RAM: для shmem-об'єктів GEM, з яких `virtio_gpu.ko` складає свої буфери, це робить `drm_gem_get_pages()`, а для сторінок користувацького простору — `pin_user_pages()`. Це критично необхідно для того, щоб підсистема управління пам'яттю ядра (MM) не перемістила ці сторінки під час підкачки (swap) чи оптимізації дефрагментації RAM (compacting). Якщо сторінку буде переміщено без відома гіпервізора хоста, DMA-транзакція хоста виконає запис у чужі фізичні дані гостя, що призведе до фатального пошкодження пам'яті ядра (Kernel Memory Corruption).

Після того як ресурс видаляється або сторінки відв'язуються за допомогою `VIRTIO_GPU_CMD_RESOURCE_DETACH_BACKING`, драйвер ядра звільняє їх (`drm_gem_put_pages()` чи `unpin_user_pages()`), повертаючи сторінки під загальний контроль менеджера пам'яті гостя.

---

## 4. Повний життєвий цикл 2D-ресурсу та системні інваріанти

Для гарантування стабільності графічного підкомплексу гостьовий драйвер `virtio_gpu.ko` проводить кожен об'єкт кадрового буфера через суворо визначену послідовність станів. Порушення цієї послідовності викликає аварійне завершення графічного контексту хоста або відмову драйвера ядра.

```
+-------------------+
|   UNINITIALIZED   |
+-------------------+
          │
          ▼  VIRTIO_GPU_CMD_RESOURCE_CREATE_2D
+-------------------+
|      CREATED      |  (Ідентифікатор зареєстровано, але пам'ять не виділено)
+-------------------+
          │
          ▼  VIRTIO_GPU_CMD_RESOURCE_ATTACH_BACKING
+-------------------+
|     ATTACHED      |  (Фізичні сторінки гостя прив'язані до ресурсу)
+-------------------+
          │
          ├─────────►  VIRTIO_GPU_CMD_TRANSFER_TO_HOST_2D  (Копіювання у буфер хоста)
          │
          ▼  VIRTIO_GPU_CMD_RESOURCE_FLUSH
+-------------------+
|      FLUSHED      |  (Кадр передано на екран / хостовий віконний менеджер)
+-------------------+
          │
          ▼  VIRTIO_GPU_CMD_RESOURCE_DETACH_BACKING
+-------------------+
|     DETACHED      |  (Сторінки гостя відв'язані, RAM можна звільняти)
+-------------------+
          │
          ▼  VIRTIO_GPU_CMD_RESOURCE_UNREF
+-------------------+
|     DESTROYED     |  (Ресурс повністю видалено з хоста)
+-------------------+
```

### Фундаментальні системні інваріанти

Під час проєктування та експлуатації драйвера `virtio-gpu` діють чотири обов'язкові інваріанти:

1. **Інваріант послідовності станів ресурсу (Resource Lifecycle Invariant):**
   `Created` → (`ATTACH_BACKING`) → `Attached` → (`TRANSFER_2D`) → `Flushed` → (`DETACH_BACKING`) → `Detached` → (`RESOURCE_UNREF`) → `Destroyed`
   Виконання операцій `TRANSFER_TO_HOST_2D` або `RESOURCE_FLUSH` над ресурсом у станах `CREATED` чи `DETACHED` є некоректним: сторінок під ресурсом немає, і хост повертає код помилки — який саме, залежить від реалізації гіпервізора.

2. **Інваріант вирівнювання сторінок та адрес (Alignment Invariant):**
   Кожна адреса сторінки в масиві `virtio_gpu_mem_entry` повинна бути строго вирівняна по межі 4096 байтів: `addr ≡ 0 (mod 4096)`.
   Зсуви та розміри прямокутників оновлення в `virtio_gpu_rect` зобов'язані не виходити за геометричні межі `width` та `height`, задані під час `RESOURCE_CREATE_2D`.

3. **Інваріант передачі володіння дескриптором (Descriptor Ownership Transfer Invariant):**
   Після зсуву індексу `avail->idx` гостьовий драйвер втрачає право читати або модифікувати дескриптори команди та відповіді доти, доки гіпервізор не поверне відповідний індекс у кільце `used->ring` і не виставить прапорець завершення.

4. **Інваріант монотонності огорож (Monotonic Fence Invariant):**
   Ідентифікатори асинхронних огорож `fence_id` при викликах з прапорцем `VIRTIO_GPU_FLAG_FENCE` зобов'язані строго монотонно зростати в межах кожного контексту: `fence_id[k+1] > fence_id[k]`.
   Це дає змогу гостю впорядковувати графічні операції без блокування CPU на кожній команді.

---

## 5. Крайові випадки, аномалії та відновлення після збоїв

Низькорівнева взаємодія через віртуалізовану шину приховує низку крайових ситуацій, які вимагають обережної обробки в ядрі:

### 1. Фрагментація гостьової пам'яті (Memory Fragmentation)
Виділення кадрового буфера високої роздільної здатності (наприклад, 4K-буфер 3840 × 2160 × 4 байти = 33 177 600 байтів ≈ 31,6 МіБ) у фізично розрізненій RAM гостя призводить до формування масиву `virtio_gpu_mem_entry` рівно з 8100 елементів по 4 КіБ. Якщо цей масив не вміщується в один дескриптор Virtqueue, драйвер розбиває `ATTACH_BACKING` на ланцюжок із декількох дескрипторів, пов'язаних прапорцем `VRING_DESC_F_NEXT`. Сам масив передається як звичайні дані, тож дескрипторів потрібно стільки, на скільки фізично неперервних шматків розпався буфер під цей масив, — а не по одному на сторінку кадру. Якщо вільних дескрипторів у черзі бракує (її глибина зазвичай 256 або 1024 елементи), драйвер чекає, доки гіпервізор поверне оброблені дескриптори в `used`-кільце, і надсилає команду після цього.

### 2. Розбіжність розміру сторінок хоста та гостя (`PAGE_SIZE` Mismatch)
Якщо ядро гостя скомпільоване з підтримкою сторінок розміром 64 КіБ (звична конфігурація для ARM64), а хост працює зі сторінками 4 КіБ, то один 64-кілобайтний блок для хоста — це шістнадцять його власних сторінок, які ще й мають бути неперервними в пам'яті гостя. Специфікація гранулярності не фіксує: `virtio_gpu_mem_entry` описує довільний блок `addr` + `length`. Тому узгодження лягає на гостьовий драйвер, і на практиці він квантує адреси по 4096 байтів — найменшому спільному знаменнику обох архітектур. Драйвер гостя виконує програмну розбивку кожної 64-КБ сторінки на 16 окремих елементів по 4096 байтів перед формуванням масиву `virtio_gpu_mem_entry`.

### 3. Зависання огорож рендерингу (Fence Timeouts & GPU Stall)
При відправці команд 3D-прискорення або обробці складних кадрових оновлень гіпервізор може затримати повернення `fence_id` через перевантаження хостового GPU чи збій графічного демона (наприклад, `virglrenderer` або `gfxstream`). Драйвер ядра гостя запускає таймер зворотного відліку (Watchdog Timer, зазвичай 5 секунд). Якщо протягом цього часу огорожа не сигналізується:
1. Драйвер фіксує таймаут пристрою (`GPU lockup detected`).
2. Всі активні DRM-фліпи скасовуються з поверненням від'ємного коду помилки `-ETIMEDOUT`.
3. Драйвер ініціює програмний скид пристрою через PCI-регістр `VIRTIO_PCI_STATUS`, скидає кільце дескрипторів та сповіщає користувацькі графічні бібліотеки Mesa про втрату контексту пристрою.

### 4. Вичерпання Resource ID та брак пам'яті хоста (Host OOM)
Спроба створити ресурс при відсутності вільної графічної пам'яті на хості повертає від гіпервізора код відповіді `VIRTIO_GPU_RESP_ERR_OUT_OF_MEMORY` (`0x1201`). Драйвер гостя повинен обробити цей код без паніки ядра, звільнити кешовані текстури через `RESOURCE_UNREF` або відкотитися до меншої роздільної здатності стільниці. Подібно до цього, спроба використати дубльований `resource_id` повертає `VIRTIO_GPU_RESP_ERR_INVALID_RESOURCE_ID` (`0x1203`), що змушує драйвер оновити свій внутрішній ідентифікатор IDR (ID Radix Tree).

### 5. Апаратно-програмні колізії при роботі з DRM GEM handles
При високому навантаженні на графічний стек гостя користувацькі процеси можуть створювати та видаляти сотні кадрових буферів на секунду. Якщо один процес виконує `close(gem_handle)` паралельно з тим, як інший процес надсилає команду `DRM_IOCTL_VIRTGPU_SUBMIT`, виникає гонка станів (Race Condition). Драйвер ядра `virtio_gpu.ko` запобігає цій аномалії за допомогою викликів атомарного лічильника посилань `kref` для кожного GEM-об'єкта. Команда `RESOURCE_UNREF` надсилається гіпервізору хоста виключно після того, як лічильник посилань `kref` падає до нуля, гарантуючи відсутність звернення до звільненого ресурсу (Use-After-Free).

---

## 6. Практичні приклади реалізації

Нижче наведено практичну реалізацію модуля формування та обробки команд `virtio-gpu`. Приклад демонструє два підходи: низькорівневий процедурний код мовою C та об'єктно-орієнтований безпечний код мовою C++ з використанням RAII, концептів та обробників помилок.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>

/* Коди команд Virtio GPU */
#define VIRTIO_GPU_CMD_RESOURCE_CREATE_2D      0x0101
#define VIRTIO_GPU_CMD_RESOURCE_UNREF          0x0102
#define VIRTIO_GPU_CMD_TRANSFER_TO_HOST_2D     0x0105
#define VIRTIO_GPU_CMD_RESOURCE_FLUSH          0x0104
#define VIRTIO_GPU_CMD_RESOURCE_ATTACH_BACKING 0x0106
#define VIRTIO_GPU_CMD_RESOURCE_DETACH_BACKING 0x0107

/* Коди відповідей Virtio GPU */
#define VIRTIO_GPU_RESP_OK_NODATA              0x1100
#define VIRTIO_GPU_RESP_ERR_UNSPEC             0x1200
#define VIRTIO_GPU_RESP_ERR_OUT_OF_MEMORY      0x1201
#define VIRTIO_GPU_RESP_ERR_INVALID_RESOURCE_ID 0x1203

/* Формати пікселів */
#define VIRTIO_GPU_FORMAT_B8G8R8A8_UNORM       1

/* Заголовок управління Virtio GPU */
struct virtio_gpu_ctrl_hdr {
    uint32_t type;
    uint32_t flags;
    uint64_t fence_id;
    uint32_t ctx_id;
    uint8_t  ring_idx;
    uint8_t  padding[3];
};

/* Прямокутник кадрового буфера */
struct virtio_gpu_rect {
    uint32_t x;
    uint32_t y;
    uint32_t width;
    uint32_t height;
};

/* Структура створення 2D-ресурсу */
struct virtio_gpu_resource_create_2d {
    struct virtio_gpu_ctrl_hdr hdr;
    uint32_t resource_id;
    uint32_t format;
    uint32_t width;
    uint32_t height;
};

/* Елемент опису фізичної сторінки гостя */
struct virtio_gpu_mem_entry {
    uint64_t addr;
    uint32_t length;
    uint32_t padding;
};

/* Структура прив'язки сторінок пам'яті */
struct virtio_gpu_resource_attach_backing {
    struct virtio_gpu_ctrl_hdr hdr;
    uint32_t resource_id;
    uint32_t nr_entries;
};

/* Структура передачі піксельних даних на хост */
struct virtio_gpu_transfer_to_host_2d {
    struct virtio_gpu_ctrl_hdr hdr;
    struct virtio_gpu_rect r;
    uint64_t offset;
    uint32_t resource_id;
    uint32_t padding;
};

/* Структура примусового скидання кадрів (Flush) */
struct virtio_gpu_resource_flush {
    struct virtio_gpu_ctrl_hdr hdr;
    struct virtio_gpu_rect r;
    uint32_t resource_id;
    uint32_t padding;
};

/* Структура видалення ресурсу */
struct virtio_gpu_resource_unref {
    struct virtio_gpu_ctrl_hdr hdr;
    uint32_t resource_id;
    uint32_t padding;
};

/**
 * virtio_gpu_submit_create_2d - Формує та надсилає команду створення 2D ресурсу
 */
int virtio_gpu_submit_create_2d(uint32_t res_id, uint32_t width, uint32_t height,
                                struct virtio_gpu_ctrl_hdr *resp_out)
{
    if (!resp_out || width == 0 || height == 0 || res_id == 0) {
        return -EINVAL;
    }

    struct virtio_gpu_resource_create_2d cmd;
    memset(&cmd, 0, sizeof(cmd));

    cmd.hdr.type = VIRTIO_GPU_CMD_RESOURCE_CREATE_2D;
    cmd.resource_id = res_id;
    cmd.format = VIRTIO_GPU_FORMAT_B8G8R8A8_UNORM;
    cmd.width = width;
    cmd.height = height;

    /* Імітація обробки гіпервізором */
    resp_out->type = VIRTIO_GPU_RESP_OK_NODATA;
    resp_out->flags = 0;
    resp_out->fence_id = 0;
    resp_out->ctx_id = 0;

    return 0;
}

/**
 * virtio_gpu_submit_attach_backing - Прив'язує сторінки RAM гостя до ресурсу
 */
int virtio_gpu_submit_attach_backing(uint32_t res_id,
                                      const struct virtio_gpu_mem_entry *entries,
                                      uint32_t nr_entries,
                                      struct virtio_gpu_ctrl_hdr *resp_out)
{
    if (!resp_out || !entries || nr_entries == 0 || res_id == 0) {
        return -EINVAL;
    }

    struct virtio_gpu_resource_attach_backing cmd;
    memset(&cmd, 0, sizeof(cmd));

    cmd.hdr.type = VIRTIO_GPU_CMD_RESOURCE_ATTACH_BACKING;
    cmd.resource_id = res_id;
    cmd.nr_entries = nr_entries;

    /*
     * У реальному драйвері за командою cmd у дескрипторний ланцюжок
     * додається масив entries розміром nr_entries * sizeof(struct virtio_gpu_mem_entry).
     */

    resp_out->type = VIRTIO_GPU_RESP_OK_NODATA;
    return 0;
}

/**
 * virtio_gpu_submit_transfer_2d - Надсилає команду копіювання пікселів на хост
 */
int virtio_gpu_submit_transfer_2d(uint32_t res_id, uint64_t offset,
                                   uint32_t x, uint32_t y,
                                   uint32_t width, uint32_t height,
                                   struct virtio_gpu_ctrl_hdr *resp_out)
{
    if (!resp_out || res_id == 0 || width == 0 || height == 0) {
        return -EINVAL;
    }

    struct virtio_gpu_transfer_to_host_2d cmd;
    memset(&cmd, 0, sizeof(cmd));

    cmd.hdr.type = VIRTIO_GPU_CMD_TRANSFER_TO_HOST_2D;
    cmd.r.x = x;
    cmd.r.y = y;
    cmd.r.width = width;
    cmd.r.height = height;
    cmd.offset = offset;
    cmd.resource_id = res_id;

    resp_out->type = VIRTIO_GPU_RESP_OK_NODATA;
    return 0;
}

/**
 * virtio_gpu_submit_flush - Надсилає команду оновлення області ресурсу на моніторі
 */
int virtio_gpu_submit_flush(uint32_t res_id, uint32_t x, uint32_t y,
                            uint32_t width, uint32_t height,
                            struct virtio_gpu_ctrl_hdr *resp_out)
{
    if (!resp_out || res_id == 0) {
        return -EINVAL;
    }

    struct virtio_gpu_resource_flush cmd;
    memset(&cmd, 0, sizeof(cmd));

    cmd.hdr.type = VIRTIO_GPU_CMD_RESOURCE_FLUSH;
    cmd.r.x = x;
    cmd.r.y = y;
    cmd.r.width = width;
    cmd.r.height = height;
    cmd.resource_id = res_id;

    resp_out->type = VIRTIO_GPU_RESP_OK_NODATA;
    return 0;
}

/**
 * virtio_gpu_submit_unref - Видаляє ресурс на хості
 */
int virtio_gpu_submit_unref(uint32_t res_id, struct virtio_gpu_ctrl_hdr *resp_out)
{
    if (!resp_out || res_id == 0) {
        return -EINVAL;
    }

    struct virtio_gpu_resource_unref cmd;
    memset(&cmd, 0, sizeof(cmd));

    cmd.hdr.type = VIRTIO_GPU_CMD_RESOURCE_UNREF;
    cmd.resource_id = res_id;

    resp_out->type = VIRTIO_GPU_RESP_OK_NODATA;
    return 0;
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <vector>
#include <expected>
#include <system_error>
#include <cstring>
#include <memory>

enum class VirtioGpuCmd : uint32_t {
    ResourceCreate2D      = 0x0101,
    ResourceUnref         = 0x0102,
    TransferToHost2D      = 0x0105,
    ResourceFlush         = 0x0104,
    ResourceAttachBacking = 0x0106,
    ResourceDetachBacking = 0x0107,
};

enum class VirtioGpuResp : uint32_t {
    OkNoData         = 0x1100,
    ErrUnspec        = 0x1200,
    ErrOutOfMemory   = 0x1201,
    ErrInvalidResId  = 0x1203,
};

enum class VirtioGpuFormat : uint32_t {
    B8G8R8A8_UNORM = 1,
};

struct virtio_gpu_ctrl_hdr {
    VirtioGpuCmd type;
    uint32_t flags{0};
    uint64_t fence_id{0};
    uint32_t ctx_id{0};
    uint8_t  ring_idx{0};
    uint8_t  padding[3]{};
};

struct virtio_gpu_rect {
    uint32_t x{0};
    uint32_t y{0};
    uint32_t width{0};
    uint32_t height{0};
};

struct virtio_gpu_mem_entry {
    uint64_t addr{0};
    uint32_t length{0};
    uint32_t padding{0};
};

class GpuResource {
public:
    GpuResource(uint32_t res_id, uint32_t width, uint32_t height)
        : resource_id_(res_id), width_(width), height_(height) {}

    ~GpuResource() noexcept {
        if (is_valid_) {
            [[maybe_unused]] auto res = destroy();
        }
    }

    // Заборона копіювання для запобігання подвійному звільненню
    GpuResource(const GpuResource&) = delete;
    GpuResource& operator=(const GpuResource&) = delete;

    // Переміщення ресурсу (Move semantics)
    GpuResource(GpuResource&& other) noexcept
        : resource_id_(other.resource_id_),
          width_(other.width_),
          height_(other.height_),
          is_valid_(other.is_valid_)
    {
        other.is_valid_ = false;
    }

    GpuResource& operator=(GpuResource&& other) noexcept {
        if (this != &other) {
            if (is_valid_) {
                [[maybe_unused]] auto res = destroy();
            }
            resource_id_ = other.resource_id_;
            width_ = other.width_;
            height_ = other.height_;
            is_valid_ = other.is_valid_;
            other.is_valid_ = false;
        }
        return *this;
    }

    [[nodiscard]] uint32_t id() const noexcept { return resource_id_; }
    [[nodiscard]] bool is_valid() const noexcept { return is_valid_; }

    [[nodiscard]] std::expected<virtio_gpu_ctrl_hdr, std::errc> attach_backing(
        std::span<const virtio_gpu_mem_entry> entries) noexcept
    {
        if (!is_valid_ || entries.empty()) {
            return std::unexpected(std::errc::invalid_argument);
        }

        // Симуляція надсилання ATTACH_BACKING в Virtqueue
        virtio_gpu_ctrl_hdr response{
            .type = static_cast<VirtioGpuCmd>(VirtioGpuResp::OkNoData)
        };
        return response;
    }

    [[nodiscard]] std::expected<virtio_gpu_ctrl_hdr, std::errc> transfer_2d(
        uint64_t offset, virtio_gpu_rect rect) noexcept
    {
        if (!is_valid_ || rect.width == 0 || rect.height == 0) {
            return std::unexpected(std::errc::invalid_argument);
        }

        virtio_gpu_ctrl_hdr response{
            .type = static_cast<VirtioGpuCmd>(VirtioGpuResp::OkNoData)
        };
        return response;
    }

    [[nodiscard]] std::expected<virtio_gpu_ctrl_hdr, std::errc> flush(
        virtio_gpu_rect rect) noexcept
    {
        if (!is_valid_) {
            return std::unexpected(std::errc::bad_file_descriptor);
        }

        virtio_gpu_ctrl_hdr response{
            .type = static_cast<VirtioGpuCmd>(VirtioGpuResp::OkNoData)
        };
        return response;
    }

private:
    uint32_t resource_id_{0};
    uint32_t width_{0};
    uint32_t height_{0};
    bool is_valid_{true};

    std::expected<virtio_gpu_ctrl_hdr, std::errc> destroy() noexcept {
        is_valid_ = false;
        virtio_gpu_ctrl_hdr response{
            .type = static_cast<VirtioGpuCmd>(VirtioGpuResp::OkNoData)
        };
        return response;
    }
};
```
:::

---

## 7. Обробка помилок та повторне використання ресурсів

При обробці відповідей від гіпервізора драйвер зобов'язаний перевіряти поле `type` у повернутому заголовку `virtio_gpu_ctrl_hdr`:

* **Код `VIRTIO_GPU_RESP_OK_NODATA` (`0x1100`):** Вказує на те, що команду виділення або оновлення кадру виконано безпомилково. Драйвер може продовжувати виконання наступних графічних транзакцій.
* **Код `VIRTIO_GPU_RESP_ERR_OUT_OF_MEMORY` (`0x1201`):** Виникає, коли хост не має вільної VRAM для створення кадрового буфера запрошеного розміру. Драйвер гостя у відповідь повинен зменшити роздільну здатність або звільнити некешовані 2D-ресурси за допомогою `VIRTIO_GPU_CMD_RESOURCE_UNREF`.
* **Код `VIRTIO_GPU_RESP_ERR_INVALID_RESOURCE_ID` (`0x1203`):** Виникає при спробі виконати `TRANSFER_TO_HOST_2D` або `FLUSH` над ресурсом, який ще не було створено або вже було видалено. Драйвер скидає локальний стан DRM-об'єкта та генерує виклик скасування кадру для користувацького процесу.

---

## 8. Деталізація бар'єрів пам'яті та синхронізації

При низькорівневій роботі з Virtqueue критично важливо дотримуватися порядку запису в пам'ять:

1. **Memory Barrier (smp_wmb):** Драйвер мусить виконати виклик бар'єра запису в пам'ять (`smp_wmb()`) **після** заповнення полів `virtio_gpu_resource_create_2d` та оновлення таблиці дескрипторів Virtqueue, але **до** підвищення індексу `avail->idx`. Без цього CPU може змінити порядок інструкцій, і гіпервізор вичитає незаповнений заголовок команди з довільним сміттям у RAM.
2. **Специфіка слабкої впорядкованості пам'яті на ARM64:** Особливу увагу при формуванні команд Virtqueue слід приділяти апаратній архітектурі процесора гостя. На платформах архітектури x86_64 модель пам'яті гарантує суворий порядок записів (TSO — Total Store Order), тому інструкції запису в дескриптори не можуть бути переставлені місцями процесором. Проте на архітектурах зі слабким порядком пам'яті (Weak Memory Ordering), таких як ARM64 або RISC-V, центральний процесор гостя може довільно змінити порядок виконання інструкцій сторадж-буфера. Якщо драйвер оновлює `avail->idx` без явного бар'єра запису `smp_wmb()` (або `dma_wmb()`), хост може побачити новий `avail->idx` — байдуже, чи прокинувся він від сповіщення, чи опитує кільце у власному потоці `vhost` — раніше, ніж стануть видимими записи у структуру команди `virtio_gpu_resource_create_2d`. У результаті гіпервізор вичитає незаповнений заголовок команди з невизначеним типом `type`, що викличе повернення помилки `VIRTIO_GPU_RESP_ERR_UNSPEC` або відмову пристрою.
3. **Асинхронний Fence:** При роботі з 3D-командами (`VIRTIO_GPU_CMD_SUBMIT_3D`) додаток не чекає на завершення рендерингу кадру. Драйвер виставляє прапорець `VIRTIO_GPU_FLAG_FENCE` та записує унікальний `fence_id`. Коли фізичний GPU завершує малювання кадру, гіпервізор відправляє переривання і повертає `fence_id` у чергу сповіщень, сигналізуючи драйверу гостя про готовність кадру до виводу.
4. **Таймаути та відновлення при збоях:** Якщо гіпервізор не повернув відповідь із відповідним `fence_id` упродовж заданого таймауту (зазвичай 5 секунд), ядро гостя вважає графічний контекст завислим, перезапускає пристрій `virtio-gpu` та надсилає сигнал інвалідації до Mesa.

---

## 9. Простеження та діагностика через ftrace

Для відбудування комунікації між гостем і хостом ядро Linux надає вбудовані tracepoints у драйвері `virtio_gpu`. Вони дозволяють аналізувати затримки обробки команд без зупинки графічної системи:

```bash
# Увімкнення трасування команд Virtio GPU у ядрі гостя
echo 1 > /sys/kernel/debug/tracing/events/virtio_gpu/enable
cat /sys/kernel/debug/tracing/trace_pipe
```

Спрощений вигляд трасування при створенні ресурсу 1920×1080 (поля наведено схематично):

```text
virtio_gpu_cmd_submit: dev=0 res_id=1 type=RESOURCE_CREATE_2D (0x0101) w=1920 h=1080
virtio_gpu_cmd_submit: dev=0 res_id=1 type=RESOURCE_ATTACH_BACKING (0x0106) nr_entries=2025
virtio_gpu_cmd_submit: dev=0 res_id=1 type=TRANSFER_TO_HOST_2D (0x0105) x=0 y=0 w=1920 h=1080 offset=0
virtio_gpu_cmd_submit: dev=0 res_id=1 type=RESOURCE_FLUSH (0x0104) x=0 y=0 w=1920 h=1080
virtio_gpu_cmd_submit: dev=0 res_id=1 type=RESOURCE_UNREF (0x0102)
```

Завдяки цим даним системний розробник може точково визначити, де виникає затримка кадру: при виділенні сторінок в ядрі гостя (`attach_backing`) чи при растеризації на хості (`resource_flush`). Аналіз трасування дає змогу оптимізувати розмір буферів та мінімізувати перемикання контексту віртуалізації.
