# 📋 Поверхня UAPI та sysfs підсистеми DRM Accel

Підсистема DRM Accel стандартизує взаємодію простору користувача з NPU та AI-прискорювачами через набір викликів користувацького інтерфейсу ядра (UAPI, англ. *User Application Binary Interface*), системні заголовочні файли, реєстр системних викликів `ioctl` та структури віртуальної файлової системи `sysfs`. Головна мета UAPI-поверхні підсистеми — надати уніфіковану інфраструктуру для відкриття пристроїв, виділення пам'яті GEM, асинхронної синхронізації та моніторингу обладнання, одночасно унеможлививши випадкове включення таких пристроїв у конвеєр 2D/3D-рендерингу або графічного виводу KMS.

## 1. Заголовочні файли, базові константи та інваріанти ядра

Простір користувача спілкується з підсистемою Accel через стандартний заголовочний файл ядра `<drm/drm.h>` та драйверно-специфічні розширення (наприклад, `<drm/ivpu_drm.h>` для Intel VPU або `<drm/habanalabs_accel.h>` для Intel Gaudi).

Ключовими системними константами для підсистеми є:
- `ACCEL_MAJOR` = `261` — офіційно виділений мажорний номер символьного пристрою (зареєстрований у системному заголовочному файлі ядра `include/uapi/linux/major.h`).
- `DRM_COMMAND_BASE` = `0x40` — базова зміщення (offset) для приватних викликів IOCTL конкретного вендора.
- `DRIVER_COMPUTE_ACCEL` = `0x10000` — прапорець ініціалізації у структурі `drm_driver.driver_features`, який ідентифікує драйвер як обчислювальний прискорювач.

### Ключові інваріанти UAPI-поверхні DRM Accel

Побудова UAPI підсистеми DRM Accel спирається на чотири фундаментальні архітектурні інваріанти:

1. **Ізоляція від графічного стека KMS (Kernel Mode Setting):** Прискорювачі не володіють кадровими буферами (framebuffers), плоскостями (planes) або CRTC-контролерами. Будь-який спроба викликати KMS-специфічний IOCTL блокується на рівні ядра без звернення до драйвера обладнання.
2. **Обов'язковість менеджера пам'яті GEM та механізму DMA-BUF:** Драйвери підсистеми Accel зобов'язані використовувати GEM (Graphics Execution Manager) для виділення й картографування пам'яті та експортувати буфери у загальносистемний механізм DMA-BUF для безкопійного обміну з іншими пристроями.
3. **Строга ізоляція віртуальних просторів адрес (Per-File Context Isolation):** Кожне відкриття файлу `/dev/accel/accelX` через системний виклик `open()` створює ізольовану структуру `struct drm_file`. Хендли пам'яті GEM та об'єкти синхронізації є приватними для даного контексту користувача й не можуть бути використані іншим процесом без явного експорту через дескриптор `dma_buf_fd` або `syncobj_fd`.
4. **Неблокуючий моніторінг через sysfs:** Будь-яке зчитування метрик стану (температура, завантаження обчислювальних ядер, версія прошивки) через віртуальну файлову систему `sysfs` мусить виконуватися за амортизований час `O(1)` і не має блокувати обчислювальний конвеєр прискорювача.

## 2. Ініціалізація та структура пристроїв у /dev/accel/accelX

Під час завантаження модуля ядра прискорювача та ініціалізації драйвера виконаються послідовні системні процедури:

1. **Реєстрація мажорного номера:** Функція `accel_core_init()` під час старта підсистеми реєструє діапазон мажорних номерів `261` за допомогою системного виклику `register_chrdev_region()`.
2. **Створення класа sysfs:** Ядро створює окремий клас `accel_class` у дереві `/sys/class/accel/`.
3. **Виділення мінорного номера:** Для кожного підключеного NPU функція `accel_minor_alloc()` виділяє структуру `drm_minor` і присвоює йому послідовний мінорний номер (`0`, `1`, `2` і так далі).
4. **Створення символьного файла пристрою:** У системному каталозі `/dev/accel/` створюються вузли пристроїв `/dev/accel/accel0`, `/dev/accel/accel1`.

Управління правами доступу до файлів пристроїв регулюється правилами підсистеми `udev` (наприклад, файлом `/lib/udev/rules.d/50-udev-default.rules`). За замовчуванням файли `/dev/accel/accelX` отримують права доступу `0666` або належать системній групі `render`. Це дозволяє запускати високопродуктивні обчислення та інференс нейронних мереж від імені звичайного користувача без привілеїв суперкористувача `root`.

### Системна структура файлових операцій `accel_driver_fops`

При відкритті файла `/dev/accel/accel0` ядро прив'язує файловий дескриптор до таблиці операцій `accel_driver_fops`:

```c
static const struct file_operations accel_driver_fops = {
    .owner          = THIS_MODULE,
    .open           = accel_open,
    .release        = drm_release,
    .unlocked_ioctl = drm_ioctl,
    .compat_ioctl   = drm_compat_ioctl,
    .mmap           = drm_gem_mmap,
    .poll           = drm_poll,
    .read           = drm_read,
    .llseek         = noop_llseek,
};
```

### Покрокове простеження виконання open("/dev/accel/accel0") у ядрі

Коли користувацький застосунок або UMD виконує системний виклик `open("/dev/accel/accel0", O_RDWR)`, в ядрі Linux відбувається наступний ланцюжок викликів:

1. `sys_open()` -> `chrdev_open()`: Ядро знаходить символьний пристрій за мажорним номером `261` та мінорним номером `0`, звертаючись до таблиці cdev.
2. `accel_open()`: Функція підсистеми Accel викликом `drm_minor_acquire()` отримує посилання на `struct drm_minor` і перевіряє стан пристрою.
3. `drm_open_helper()`: Ядро виділяє нову структуру `struct drm_file`, яка репрезентує відкритий файловий контекст клієнта.
4. **Ініціалізація IDR-дерева:** Усередині `struct drm_file` функція `idr_init_base()` ініціалізує IDR-структуру `object_idr` із захисним спінлоком `table_lock`. Ця таблиця призначена для збереження приватних GEM-хендлів даного відкриття.
5. **Колбек драйвера `driver->open()`:** Якщо драйвер прискорювача реалізує власну функцію ініціалізації (наприклад, `ivpu_open()`), ядро викликає її для виділення приватної таблиці сторінок віртуальної пам'яті NPU (NPU MMU context) для даного процесу.
6. **Прив'язка приватних даних:** Вказівник `file->private_data` встановлюється на створену структуру `struct drm_file`, і системний виклик `open()` повертає у простір користувача новий цілочисельний файловий дескриптор `fd`.

## 3. Дерево системної файлової системи sysfs (/sys/class/accel/)

Кожен прискорювач експортує свої системні атрибути та стан у віртуальну файлову систему `sysfs`. Ієрархія каталогу пристрою `/sys/class/accel/accelX/` має наступний вигляд:

```
/sys/class/accel/accel0/
├── dev                 # Мажорний і мінорний номери символьного пристрою (261:0)
├── device -> ../../../devices/pci0000:00/0000:00:0b.0  # Символьне посилання на PCI/Platform пристрій
├── subsystem -> ../../../class/accel                   # Посилання на клас підсистеми accel
├── uevent              # Інтерфейс генерації подій та гарячого підключення udev
├── power/              # Підсистема управління живленням ядра (Runtime PM)
│   ├── control         # Режим управління живленням (auto / on)
│   ├── runtime_status  # Поточний стан пристрою (active / suspended / suspending)
│   ├── runtime_usage   # Лічильник активних посилань використання (reference count)
│   └── autosuspend_delay_ms # Затримка перед переходом у режим енергозбереження (мс)
└── device/             # Атрибути, експортовані безпосередньо KMD-драйвером прискорювача
    ├── engine_usage    # Відсоток завантаження матричних обчислювачів NPU
    ├── temperature     # Поточна температура кристала (у міліградусах Цельсія)
    ├── fw_version      # Версія завантаженого мікрокоду прошивки NPU
    ├── mem_info        # Статистика використання локальної пам'яті SRAM/HBM
    ├── ras_error_count # Лічильник виправлених та невиправлених помилок пам'яті ECC
    └── reset_count     # Лічильник апаратних скидань (hardware resets) пристрою
```

Драйвер ядра створює ці атрибути під час процедури `device_add()`, зв'язуючи їх з колбеками `show()` (зчитання) та `store()` (запис). Зчитування цих файлів у простір користувача здійснюється без блокування системного конвеєра обчислень.

### Інваріанти та розмежування прав у sysfs

1. **Безпека зчитування:** Будь-який процес з правами читання файлів sysfs може отримувати метрики `engine_usage` або `temperature`.
2. **Адміністративний контроль:** Запис у модифікуючі атрибути (наприклад, ручний виклик скидання пристрою через `device/reset` або зміна режиму живлення `power/control`) вимагає наявності системного мандата `CAP_SYS_ADMIN`.
3. **Гарячі події uevent:** При виникненні критичних подій (наприклад, перегрів кристала або виявлення невиправної помилки пам'яті RAS ECC) KMD-драйвер викликає `kobject_uevent_env()`, надсилаючи uevent-сигнал у daemon `udevd` для сповіщення системного моніторингу.

## 4. Реєстр системних викликів IOCTL: Розділення повноважень

Підсистема DRM Accel реалізує суворе фільтрування системних викликів IOCTL. Таблиця викликів розділяється на дві принципові категорії.

### 4.1 Дозволені та стандартизовані системні IOCTL

Стандартні виклики DRM Accel дозволяють керувати ідентифікацією пристрою, об'єктами пам'яті GEM та примітивами синхронізації:

- `DRM_IOCTL_VERSION` (`struct drm_version`) — повертає назву драйвера ядра (наприклад, `"intel_vpu"` або `"habanalabs"`), версію релізу та текстовий опис пристрою.
- `DRM_IOCTL_GET_UNIQUE` (`struct drm_unique`) — повертає унікальний шинний ідентифікатор пристрою на шині PCIe (наприклад, `"pci:0000:00:0b.0"`).
- `DRM_IOCTL_GEM_CLOSE` (`struct drm_gem_close`) — вивільняє користувацький хендл об'єкта GEM та зменшує лічильник посилань пам'яті `drm_gem_object_put()`.
- `DRM_IOCTL_PRIME_HANDLE_TO_FD` (`struct drm_prime_handle`) — конвертує локальний хендл GEM у загальносистемний файловий дескриптор `dma_buf_fd` для безкопійної передачі пам'яті іншим драйверам.
- `DRM_IOCTL_PRIME_FD_TO_HANDLE` (`struct drm_prime_handle`) — імпортує дескриптор `dma_buf_fd` від іншого пристрою (наприклад, V4L2 або GPU) і створює локальний GEM-хендл у контексті даного `struct drm_file`.
- `DRM_IOCTL_SYNCOBJ_CREATE` (`struct drm_syncobj_create`) — створює об'єкт синхронізації `syncobj` для відстеження стану виконання завдань.
- `DRM_IOCTL_SYNCOBJ_DESTROY` (`struct drm_syncobj_destroy`) — знищує об'єкт синхронізації `syncobj` та вивільняє пов'язані з ним ресурси ядра.
- `DRM_IOCTL_SYNCOBJ_HANDLE_TO_FD` / `DRM_IOCTL_SYNCOBJ_FD_TO_HANDLE` (`struct drm_syncobj_handle`) — експортує та імпортує об'єкт `syncobj` у вигляді дескриптора `sync_file_fd` для міжпроцесного обміну станами синхронізації.
- `DRM_IOCTL_SYNCOBJ_WAIT` (`struct drm_syncobj_wait`) — виконує асинхронне очікування сигналу завершення виконання на NPU з можливістю вказати таймаут у наносекундах та прапорці очікування.

### Покрокове простеження ключових системних IOCTL в ядрі

1. **Обробка DRM_IOCTL_VERSION:**
   При виконанні виклику ядро звертається до структури `drm_driver`. Функція `drm_version()` копіює рядки `driver->name`, `driver->date` та `driver->desc` у буфери користувача за допомогою `copy_to_user()`. Якщо переданий буфер занадто малий, ядро обрізає рядок і записує фактичну довжину у поля `name_len`, `date_len`, `desc_len`.

2. **Обробка DRM_IOCTL_GEM_CLOSE:**
   Ядро отримує структуру `struct drm_gem_close` з полем `handle`. Функція `drm_gem_handle_delete(file_priv, handle)` вилучає числовий хендл з IDR-дерева даного `struct drm_file` і зменшує лічильник посилань об'єкта `drm_gem_object_put()`. Якщо лічильник досягає нуля, викликається деструктор драйвера `driver->gem_free_object_unlocked()`, який вивільняє фізичні сторінки пам'яті.

3. **Обробка DRM_IOCTL_PRIME_HANDLE_TO_FD:**
   UMD передає GEM-хендл та прапорці доступу (`DRM_CLOEXEC | DRM_RDWR`). Ядро звертається до функції `drm_gem_prime_handle_to_fd()`, яка загортає об'єкт `drm_gem_object` у системну структуру `struct dma_buf`, реєструє новий анонімний файловий дескриптор у таблиці файлів процесу та повертає його номер `fd`.

4. **Обробка DRM_IOCTL_SYNCOBJ_WAIT:**
   Ядро приймає масив хендлів `syncobj`, таймаут у наносекундах (`timeout_nsec`) та прапорці. Функція `drm_syncobj_array_wait()` витягує підпорядковані об'єкти `dma_fence` з кожного `syncobj` і викликає `dma_fence_wait_timeout()`. Потік UMD переводиться у стан сну `TASK_INTERRUPTIBLE`. При спрацюванні апаратного переривання NPU потік пробуджується й повертає `0` або `-ETIMEDOUT`.

### 4.2 Заблоковані KMS IOCTL (повертають коди помилок -EINVAL або -ENOTTY)

Під час обробки системного виклику `drm_ioctl()` ядро перевіряє маску прапорців дозволу `drm_ioctl_permit()`. Якщо драйвер зареєстровано з прапорцем `DRIVER_COMPUTE_ACCEL` без `DRIVER_MODESET`, усі виклики підсистеми KMS блокуються на найпершому етапі:

- `DRM_IOCTL_MODE_GETCRTC` — перевірка стану CRT-контролерів дисплея.
- `DRM_IOCTL_MODE_SETCRTC` — встановлення роздільної здатності та частоти розгортки.
- `DRM_IOCTL_MODE_GETCONNECTOR` — опитування підключених моніторів та ТВ-виходів.
- `DRM_IOCTL_MODE_PAGE_FLIP` — команда перемикання кадрів графічного буфера.
- `DRM_IOCTL_MODE_CURSOR` — апаратне керування курсором миші.

Блокування цих викликів гарантує, що жоден користувацький процес або графічний стек (Mesa, Vulkan loader, X11, Wayland) не зможе помилково сприйняти прискорювач NPU як відеокарту.

## 5. Драйверно-специфічні розширення UAPI (Private IOCTLs)

Оскільки кожен AI-прискорювач має унікальну систему інструкцій (ISA NPU), архітектуру конвеєрів та локальну пам'ять, вендори додають власні виклики у піддіапазоні `DRM_COMMAND_BASE` (0x40):

1. **Intel VPU (`ivpu` — заголовочний файл `<drm/ivpu_drm.h>`):**
   - `DRM_IVPU_BO_CREATE` — створення об'єкта буфера з урахуванням кєш-політики VPU (uncached, write-combining, cached).
   - `DRM_IVPU_SUBMIT` — подання командного буфера на виконання в NPU.
   - `DRM_IVPU_BO_INFO` — отримання системної адреси та фізичного мапування буфера.
2. **Habana Labs (`habanalabs` — заголовочний файл `<drm/habanalabs_accel.h>`):**
   - `HL_IOCTL_CB_CREATION` — виділення командного буфера (Command Buffer).
   - `HL_IOCTL_CS` — подання командної черги (Command Submission) з вказанням масиву хендлів пам'яті.
   - `HL_IOCTL_MEMORY` — розширене управління логічними блоками HBM/SRAM.
3. **Qualcomm Cloud AI (`qaic` — заголовочний файл `<drm/qaic_accel.h>`):**
   - `DRM_QAIC_MANAGE_EXEC_OBJ` — керування контекстами виконання та нарізанням обчислювальних ядер прискорювача.
   - `DRM_QAIC_ATTACH_BO` — приєднування буфера пам'яті до конкретного обчислювального контексту.

## 6. Безпека, ізоляція та контейнеризація AI-навантажень (Cgroups & Namespaces)

У сучасних хмарних середовищах (Kubernetes, Docker, Podman) інференс нейромереж виконується усередині ізольованих контейнерів. Підсистема DRM Accel підтримує суворе розмежування ресурсів між контейнерами:

1. **Контрольні групи пристроїв (cgroups v2 devices controller):** Доступ до файлів `/dev/accel/accelX` обмежується правилами cgroup. Контейнеру виділяється лише конкретний прискорювач (наприклад, `/dev/accel/accel0`), тоді як інші NPU системи залишаються недоступними.
2. **Ізоляція пам'яті та GEM-хендлів:** Контейнер A не має змоги відгадати або підставити GEM-хендл контейнера B, оскільки хендли є локальними для кожної структури `struct drm_file`. Без явного прокидання `dma_buf_fd` через IPC міжпроцесний доступ унеможливлено.
3. **Обмеження ресурсів VRAM/SRAM:** Драйвери підсистеми Accel інтегруються з підсистемою cgroup memory/drm для лімітування максимального обсягу пам'яті, який один контейнер може виділити під GEM-буфери.

## 7. Крайові випадки та інваріанти обробки помилок у UAPI

При розробці та експлуатації UAPI підсистеми Accel виникають критичні крайові випадки, які обробляються на рівні DRM core та KMD:

1. **Аварійне завершення процесу UMD (Crash або SIGKILL):**
   Якщо користувацький процес аварійно завершується під час виконання обчислень на NPU, ядро автоматично викликає функцію `drm_release()`. Ядро закриває `struct drm_file`, вилучає усі незакриті GEM-хендли користувача через `drm_gem_object_put()`, але зберігає самі фізичні буфери до завершення активних `dma_fence` у планувальнику. Завдання, що зависли на апаратурі, скасовуються таймером TDR.
2. **Переповнення IDR-таблиці GEM-хендлів (Handle Exhaustion):**
   Кожен виділений буфер отримує числовий хендл у контексті `struct drm_file`. Якщо UMD зациклюється й відкриває тисячі буферів без виклику `DRM_IOCTL_GEM_CLOSE`, ядро вичерпує ліміт IDR-дерева й повертає коди помилок `-EMFILE` або `-ENOMEM`, запобігаючи вичерпанню оперативної пам'яті ядра.
3. **Валідація структур та перевірка вирівнювання (Alignment & Padding Validation):**
   Для запобігання витоку некоректно ініціалізованої пам'яті ядра через `copy_to_user()`, усі UAPI-структури IOCTL підсистеми Accel повинні мати суворе вирівнювання за межами 64 біт та містити явні заповнювальні поля (`__u32 pad`). Драйвер ядра обов'язково перевіряє, щоб `pad == 0`, інакше повертає `-EINVAL`.
4. **Апаратний збій або зависання (Hardware Timeout & Recovery):**
   Якщо прискорювач не відповідає протягом заданого інтервалу (зазвичай 5000 мс), планувальник `drm_sched` ініціює процедуру скидання (TDR). Усі активні `syncobj` та `dma_fence` даного контексту переводяться у сигнальний стан з помилкою `-ECANCELED`, а системний лічильник `/sys/class/accel/accelX/device/reset_count` інкрементується.

## 8. Практичний C та C++ приклад використання UAPI та sysfs

Нижче наведено повноцінний приклад взаємодії з UAPI та sysfs підсистеми DRM Accel мовами C та C++20. Приклад демонструє запит версії драйвера через `DRM_IOCTL_VERSION`, зчитування завантаження та температури з `sysfs`, створення об'єкта `syncobj` через `DRM_IOCTL_SYNCOBJ_CREATE` та асинхронну перевірку його стану.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <errno.h>
#include <stdint.h>
#include <drm/drm.h>

/* Допоміжна функція зчитання sysfs-атрибута */
static int read_sysfs_attr(const char *path, char *buf, size_t size) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) return -1;
    ssize_t bytes = read(fd, buf, size - 1);
    close(fd);
    if (bytes < 0) return -1;
    buf[bytes] = '\0';
    /* Видаляємо символ нового рядка */
    char *newline = strchr(buf, '\n');
    if (newline) *newline = '\0';
    return 0;
}

int main(void) {
    int fd = open("/dev/accel/accel0", O_RDWR | O_CLOEXEC);
    if (fd < 0) {
        perror("Не вдалося відкрити /dev/accel/accel0");
        return EXIT_FAILURE;
    }

    /* 1. Запит версії драйвера через DRM_IOCTL_VERSION */
    char name[32] = {0};
    char date[32] = {0};
    char desc[64] = {0};

    struct drm_version ver = {
        .name_len = sizeof(name) - 1,
        .name = name,
        .date_len = sizeof(date) - 1,
        .date = date,
        .desc_len = sizeof(desc) - 1,
        .desc = desc,
    };

    if (ioctl(fd, DRM_IOCTL_VERSION, &ver) < 0) {
        perror("Помилка DRM_IOCTL_VERSION");
        close(fd);
        return EXIT_FAILURE;
    }

    printf("Драйвер Accel: %s (%s), опис: %s\n", ver.name, ver.date, ver.desc);

    /* 2. Зчитання атрибутів з sysfs */
    char temp_buf[32] = {0};
    char usage_buf[32] = {0};
    if (read_sysfs_attr("/sys/class/accel/accel0/device/temperature", temp_buf, sizeof(temp_buf)) == 0) {
        printf("Температура NPU: %s mC\n", temp_buf);
    }
    if (read_sysfs_attr("/sys/class/accel/accel0/device/engine_usage", usage_buf, sizeof(usage_buf)) == 0) {
        printf("Завантаження NPU: %s%%\n", usage_buf);
    }

    /* 3. Створення об'єкта синхронізації syncobj */
    struct drm_syncobj_create create_sync = {
        .flags = DRM_SYNCOBJ_CREATE_SIGNALED,
    };

    if (ioctl(fd, DRM_IOCTL_SYNCOBJ_CREATE, &create_sync) < 0) {
        perror("Помилка DRM_IOCTL_SYNCOBJ_CREATE");
        close(fd);
        return EXIT_FAILURE;
    }

    printf("Успішно створено syncobj, handle: %u\n", create_sync.handle);

    /* 4. Очищення об'єкта syncobj */
    struct drm_syncobj_destroy destroy_sync = {
        .handle = create_sync.handle,
    };
    ioctl(fd, DRM_IOCTL_SYNCOBJ_DESTROY, &destroy_sync);

    close(fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <system_error>
#include <vector>
#include <memory>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <drm/drm.h>

namespace accel {

class AccelDevice {
public:
    explicit AccelDevice(std::string_view path) {
        fd_ = ::open(path.data(), O_RDWR | O_CLOEXEC);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити прискорювач Accel");
        }
    }

    ~AccelDevice() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    AccelDevice(const AccelDevice&) = delete;
    AccelDevice& operator=(const AccelDevice&) = delete;

    AccelDevice(AccelDevice&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    AccelDevice& operator=(AccelDevice&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int fd() const noexcept { return fd_; }

    struct DriverInfo {
        std::string name;
        std::string date;
        std::string desc;
    };

    [[nodiscard]] DriverInfo query_version() const {
        std::vector<char> name(32, 0);
        std::vector<char> date(32, 0);
        std::vector<char> desc(64, 0);

        drm_version ver{};
        ver.name_len = name.size() - 1;
        ver.name = name.data();
        ver.date_len = date.size() - 1;
        ver.date = date.data();
        ver.desc_len = desc.size() - 1;
        ver.desc = desc.data();

        if (::ioctl(fd_, DRM_IOCTL_VERSION, &ver) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка DRM_IOCTL_VERSION");
        }

        return DriverInfo{
            .name = std::string(name.data()),
            .date = std::string(date.data()),
            .desc = std::string(desc.data())
        };
    }

    [[nodiscard]] std::uint32_t create_syncobj(bool signaled = true) const {
        drm_syncobj_create req{};
        if (signaled) {
            req.flags = DRM_SYNCOBJ_CREATE_SIGNALED;
        }

        if (::ioctl(fd_, DRM_IOCTL_SYNCOBJ_CREATE, &req) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка DRM_IOCTL_SYNCOBJ_CREATE");
        }
        return req.handle;
    }

    void destroy_syncobj(std::uint32_t handle) const noexcept {
        drm_syncobj_destroy req{.handle = handle};
        ::ioctl(fd_, DRM_IOCTL_SYNCOBJ_DESTROY, &req);
    }

private:
    int fd_{-1};
};

[[nodiscard]] inline std::string read_sysfs_value(std::string_view sysfs_path) {
    std::ifstream file(sysfs_path.data());
    if (!file.is_open()) {
        return "N/A";
    }
    std::string val;
    std::getline(file, val);
    return val;
}

} // namespace accel

int main() {
    try {
        accel::AccelDevice dev("/dev/accel/accel0");

        auto info = dev.query_version();
        std::cout << "[C++ RAII] Драйвер Accel: " << info.name 
                  << " (" << info.date << "), опис: " << info.desc << '\n';

        auto temp = accel::read_sysfs_value("/sys/class/accel/accel0/device/temperature");
        auto usage = accel::read_sysfs_value("/sys/class/accel/accel0/device/engine_usage");
        std::cout << "[sysfs] Температура NPU: " << temp << " mC, завантаження: " << usage << "%\n";

        std::uint32_t sync_handle = dev.create_syncobj(true);
        std::cout << "[C++ RAII] Створено syncobj handle: " << sync_handle << '\n';

        dev.destroy_syncobj(sync_handle);
    } catch (const std::exception& e) {
        std::cerr << "Помилка в програмі: " << e.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

## 9. Порівняльний аналіз C та C++20 підходів у роботі з UAPI

Розгляд двох практичних реалізацій демонструє фундаментальні проектувальні розбіжності між системним C-підходом та сучасним C++20 підходом:

1. **Управління дескрипторами (RAII проти ручного закриття):** У C-коді закриття `fd` виконується вручну перед кожним `return EXIT_FAILURE`. Забутий виклик `close(fd)` призводить до витоку системних ресурсів. У C++ клас `AccelDevice` реалізує семантику переміщення (Move semantics) і видаляє конструктори копіювання, що гарантує закриття `fd` у деструкторі при будь-якому варіанті виходу з програми, включаючи генерацію винятків.
2. **Зчитання sysfs (Системні виклики проти std::ifstream):** У C використовуються нізькорівневі системні виклики `open()`, `read()`, `close()` та маніпуляції з C-рядками. У C++ застосовуються стандартні потоки введення-виведення `std::ifstream`, які забезпечують безпечний буферизований розбір текстових атрибутів sysfs.
3. **Обробка помилок (Системний errno проти std::system_error):** Код мовою C перевіряє повернуте від'ємне значення `ioctl` й викликає `perror()`. Код мовою C++ викидає об'єкт винятку `std::system_error`, який інтегрує код `errno` у канонічну категорію `std::generic_category()`.

## 10. Підсистема трасування ftrace та точки спостереження

Для розробників UMD та системних інженерів підсистема DRM Accel надає набір трасувальних точок (tracepoints), які інтегровані у стандартний інструментарій ядра Linux `ftrace`:

1. `drm:drm_sched_job` — викликається у момент, коли користувацьке завдання загортається у структуру `drm_sched_job` і додається до черги контексту.
2. `drm:drm_sched_process_job` — викликається під час передачі командного буфера на апаратні кільця NPU.
3. `dma_fence:dma_fence_init` — реєструє створення асинхронного бар'єра виконання `dma_fence`.
4. `dma_fence:dma_fence_signaled` — фіксує момент генерації апаратного переривання (IRQ) прискорювачем по завершенню інференсу.

Використання цих точок дозволяє проводити профільовання затримок у реальному часі за допомогою інструментів `trace-cmd record` або `perf trace`.
