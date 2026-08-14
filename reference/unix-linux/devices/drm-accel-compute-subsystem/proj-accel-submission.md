# ⚙️ Взаємодія з /dev/accel: створення GEM-буфера, подання команд та синхронізація через dma-fence

Користувацький драйвер (User Mode Driver, UMD) взаємодіє з обчислювальним прискорювачем NPU через вузол пристрою `/dev/accel/accel0` за допомогою системних викликів `open()`, `mmap()`, реєстру викликів `ioctl` підсистеми DRM та асинхронних примітивів синхронізації `dma_fence` і `drm_syncobj`.

## 1. Архітектурний конвеєр взаємодії простору користувача з NPU

Процес виконання нейромережевого інференсу або матричних обчислень на прискорювачі під управлінням підсистеми DRM Accel поділяється на кілька чітко розмежованих послідовних етапів:

1. **Ініціалізація та відкриття сесії:** Застосунок або високорівневий фреймворк (TensorFlow, PyTorch, OpenVINO) ініціалізує UMD-бібліотеку виробника. Бібліотека виконує системний виклик `open("/dev/accel/accel0", O_RDWR | O_CLOEXEC)`. Драйвер ядра (KMD) створює ізольований системний контекст клієнта `struct drm_file`.
2. **Виділення пам'яті під тензори та командний буфер (GEM Allocation):** UMD надсилає драйверу прискорювача IOCTL виділення GEM-буферів. Драйвер ядра виділяє потрібний обсяг фізичних сторінок пам'яті у системній RAM або VRAM/SRAM прискорювача та повертає числові хендли (GEM handles) для буферів даних (вхідні тензори, ваги, вихідні активи) та командного буфера (Command Buffer).
3. **Відображення пам'яті у простір процесу (mmap):** Для заповнення буферів вхідними даними UMD запитує зміщення (mmap offset) через IOCTL та виконує системний виклик `mmap()`. Це дозволяє UMD записувати вхідні тензори та формувати бінарний пакет команд для NPU напряму в оперативну пам'яті, минаючи копіювання через ядро.
4. **Формування та подання командного буфера (Command Submission / CS):** UMD будує у пам'яті командний буфер зі специфічними інструкціями для NPU (структури тензорів, адреси вагових коефіцієнтів, шейдерні програми/активації) та передає його в ядро через IOCTL `DRM_IOCTL_ACCEL_SUBMIT` (або вендорні аналоги `DRM_IVPU_SUBMIT`, `HL_IOCTL_CS`).
5. **Планування та передача в кільцевий буфер апаратури (drm_sched):** Драйвер ядра перевіряє права доступу, валідує адреси буферів, фіксує сторінки пам'яті (memory pinning), загортає завдання у структуру `drm_sched_job` та передає його в обчислювальний планувальник `drm_sched`. Планувальник записує командний пакет у кільцевий буфер (Hardware Ring Buffer / Command Queue) прискорювача й «смикає» MMIO-регістр Дзвінка (Doorbell Register).
6. **Асинхронна синхронізація завершення (dma_fence, syncobj & poll):** Під час подання ядро створює асинхронний бар'єр `dma_fence` і повертає простір користувача дескриптор `syncobj` або `sync_file_fd`. UMD виконує асинхронне очікування завершення обчислень через виклики `DRM_IOCTL_SYNCOBJ_WAIT`, `poll()` або `epoll()`, не блокуючи головний потік CPU.

```
+-----------------------------------------------------------------------------+
|                            USER SPACE (UMD)                                 |
|  1. open("/dev/accel/accel0") -> 2. GEM Alloc (tensors + cmds) ->           |
|  3. mmap() & fill data -> 4. DRM_IOCTL_ACCEL_SUBMIT -> 6. SYNCOBJ_WAIT      |
+--------------------------------─────┬────────────────-----------------------+
                                      | ioctl / mmap
+-------------------------------------v────────────────-----------------------+
|                            KERNEL SPACE (KMD)                               |
|  Validate Handles -> Pin Memory Pages -> Create dma_fence -> Push drm_sched |
+--------------------------------─────┬────────────────-----------------------+
                                      | MMIO Doorbell
+-------------------------------------v────────────────-----------------------+
|                            HARDWARE (NPU)                                   |
|  Fetch Commands -> Compute Tensor Matrix (Systolic Array) -> Signal IRQ     |
+-----------------------------------------------------------------------------+
```

## 2. Глибокий аналіз механізму подання команд (Command Submission)

Подання команд (Command Submission, CS) — це ключова операція в UAPI прискорювача. На відміну від класичного процесора (CPU), де інструкції виконуються послідовно з пам'яті команд, NPU є автономним DMA-пристроєм. Він зчитує команди у вигляді бінарних пакетів дескрипторів із системної або локальної пам'яті.

### 2.1 Етапи обробки подання команд у ядрі (KMD)

Коли UMD викликає `DRM_IOCTL_ACCEL_SUBMIT`, ядро Linux реалізує наступний алгоритм:

1. **Копіювання масиву параметрів (`copy_from_user`):** Ядро копіює з простору користувача структуру подання, що містить списки GEM-хендлів, масиви вхідних/вихідних об'єктів синхронізації `syncobj` та адресу командного буфера.
2. **Перевірка та локалізація GEM-хендлів:** Драйвер ядра шукає кожен GEM-хендл у приватній таблиці `file_priv->object_idr` поточного відкриття `struct drm_file`. Якщо хоча б один хендл не належить даному процесу, подання негайно відхиляється з кодом `-BOINVAL` або `-EINVAL`.
3. **Блокування резервування пам'яті (`dma_resv_lock`):** Драйвер запирає огородження пам'яті `dma_resv` для всіх задіяних GEM-буферів. Це гарантує, що під час формування завдання підсистема підкачки сторінок (swapping) або менеджер пам'яті ядра не перемістить фізичні сторінки пам'яті у системній RAM.
4. **Створення асинхронного бар'єра `dma_fence`:** Ядро створює новий екземпляр `struct dma_fence`, який прив'язується до поточного завдання і додається у контейнер `dma_resv` кожного задіяного GEM-буфера як огорожа читання/запису.
5. **Загортання в `drm_sched_job` та передача у чергу:** Завдання додається у чергу контексту через `drm_sched_entity_push_job()`. Робочий потік планувальника ядра переміщує завдання до апаратного кільцевого буфера (Hardware Queue) і подає сигнал NPU про наявність нових команд через MMIO-регістр `doorbell`.

### 2.2 Простеження роботи планувальника drm_sched

Фреймворк `drm_sched` реалізує багатониткову чергу завдань ядра:

- `drm_sched_job_init()`: Виділяє структуру завдання `struct drm_sched_job`, зв'язує її з файловим контекстом користувача та ініціалізує внутрішній таймер TDR.
- `drm_sched_job_arm()`: Прив'язує апаратну огорожу `dma_fence` до завдання і готує його до передачі у роботу.
- `drm_sched_entity_push_job()`: Поміщає завдання у чергу `drm_sched_entity`. Робочий потік ядра `drm_sched_main` прокидається, викликає колбек KMD `drm_sched_backend_ops.run_job()`, записує команди в ring buffer та підтверджує подання через MMIO doorbell register.

### 2.3 Управління пріоритетами черг та розкладом виконання

Підсистема `drm_sched` підтримує кілька рівнів пріоритету виконання для обчислювальних контекстів:

1. **Пріоритет реального часу (`DRM_SCHED_PRIORITY_HIGH` / `KERNEL`):** Використовується для інференсу з низькою затримкою (наприклад, обробка відеопотоку в реальному часі). Завдання з високим пріоритетом виконуються позачергово, витісняючи фонові обчислення.
2. **Ззвичайний пріоритет (`DRM_SCHED_PRIORITY_NORMAL`):** Стандартний рівень для більшості пакетних обчислень та навчання моделей.
3. **Фоновий пріоритет (`DRM_SCHED_PRIORITY_MIN`):** Застосовується для фонових задач аналітики з низькими вимогами до затримки.

Планувальник ядра розподіляє кванти часу апаратури між сутностями (`drm_sched_entity`) за допомогою алгоритму Round-Robin з урахуванням пріоритетів, запобігаючи «голодуванню» (starvation) низькопріоритетних задач.

## 3. Фіксація пам'яті (Memory Pinning) та Scatter-Gather мапування

Оскільки NPU здійснює прямому доступ до пам'яті (DMA), адреси буферів, що передаються з простору користувача, повинні бути зафіксовані у фізичних сторінках RAM, щоб запобігти їх переміщенню під час виконання обчислень.

1. **Фіксація сторінок користувача (`pin_user_pages_fast`):** Якщо UMD передає буфер `userptr` (виділений через `posix_memalign`), KMD викликає `pin_user_pages_fast()`. Перевіряються права доступу сторінок, а лічильники посилань `struct page` інкрементуються.
2. **Побудова Scatter-Gather таблиці (`sg_table`):** Фізичні сторінки пам'яті можуть не бути неперервними. KMD будує структуру `struct sg_table`, яка описує фрагментовані фізичні блоки.
3. **DMA-картографування (`dma_map_sgtable`):** Драйвер викликає `dma_map_sgtable()`, яка налаштовує IOMMU (Input-Output Memory Management Unit). IOMMU мапить неперервні віртуальні адреси прискорювача (NPU VA) на розсічені фізичні сторінки RAM.
4. **Розфіксування після сигналювання `dma_fence`:** Після завершення завдання та спрацювання IRQ колбек `drm_sched_backend_ops.free_job()` викликає `dma_unmap_sgtable()` та `unpin_user_pages()`, вивільняючи сторінки.

## 4. Механізм асинхронної синхронізації: dma_fence, drm_syncobj та Timeline Syncobj

Прискорювачі NPU працюють асинхронно відносно CPU. Системний виклик `DRM_IOCTL_ACCEL_SUBMIT` не чекає завершення обчислень на апаратурі; він лише додає завдання у чергу та миттєво повертає управління в UMD.

```
+---------------+      drm_sched      +-------------------+      Hardware IRQ      +------------------+
|  INIT / ARM   | ------------------> | HW EXECUTION (NPU)| ---------------------> | SIGNALED (READY) |
+---------------+                     +-------------------+                        +------------------+
        |                                       |                                           |
        | Exception                             | Hang Timeout                              | Read Results
        v                                       v                                           v
+---------------+                     +-------------------+                        +------------------+
| ERROR -EINVAL |                     |  ERROR -ETIMEDOUT |                        | UMD Unblocked    |
+---------------+                     +-------------------+                        +------------------+
```

### 4.1 Примітив ядра dma_fence

Усередині ядра асинхронне виконання контролюється об'єктом `struct dma_fence`. Основні властивості `dma_fence`:
- **Неповторність сигналу:** `dma_fence` перебуває у несигнальному стані під час виконання обчислень NPU і переходить у сигнальний стан один раз, коли прискорювач генерує апаратне переривання (IRQ).
- **Зворотне відстеження помилок:** Якщо прискорювач зазнав апаратного збою під час обчислень, функція `dma_fence_set_error()` записує код помилки (наприклад, `-EIO` або `-ECANCELED`) у структуру огорожі, що дозволяє UMD дізнатися про збій.
- **Підтримка межпристройної синхронізації:** `dma_fence` може використовуватися як бар'єр між різними пристроями. Наприклад, GPU чекає завершення `dma_fence` від NPU перед тим, як зчитати обчислені тензори для відображення на моніторі.

### 4.2 Користувацький обгортковий об'єкт drm_syncobj та Timeline Syncobjs

Оскільки `dma_fence` є внутрішньою структурою ядра й не може бути безпосередньо передана у простір користувача, DRM надає об'єкт `drm_syncobj`. 

`drm_syncobj` діє як контейнер (покажчик) для поточного `dma_fence`:
- UMD створює `syncobj` через `DRM_IOCTL_SYNCOBJ_CREATE`.
- При поданні завдань UMD передає хендл `syncobj` як `out_syncobj`. Ядро замінює внутрішній вказівник у `syncobj` на нову `dma_fence` цього подання.
- UMD може викликати `DRM_IOCTL_SYNCOBJ_WAIT` або експортувати `syncobj` у дескриптор `sync_file_fd` за допомогою `DRM_IOCTL_SYNCOBJ_HANDLE_TO_FD` для синхронізації з іншими процесами через системний виклик `poll()`.

**Timeline Syncobjs (Часові точки синхронізації):**
Сучасний розширений варіант `drm_syncobj` підтримує часові точки (timeline points). Замість бінарного прапорця (signaled / unsignaled), timeline syncobj містить 64-бітне монотоно зростаюче число `point`. Кожне нове подання додає завдання на точку `point = N`. UMD може чекати досягнення конкретного значення точки (наприклад, `point == 42`), що спрощує конвеєризацію багатокрокових нейромереж без створення окремого `syncobj` для кожного шару.

## 5. Формат та поля IOCTL подання команд DRM_IOCTL_ACCEL_SUBMIT

Хоча кожен вендор може додавати розширені прапорці, стандартизований IOCTL подання команд має наступну концептуальну структуру:

```c
struct drm_accel_submit_op {
    __u64 flags;             /* Прапорці подання (наприклад, ACCEL_SUBMIT_FENCE_WAIT) */
    __u64 engine_idx;        /* Індекс обчислювального ядра NPU */
    __u64 cmds_ptr;          /* Вказівник у просторі користувача на масив командних буферів */
    __u32 cmd_count;         /* Кількість командних буферів у масиві */
    __u32 pad;               /* Заповнювальне поле для 64-бітного вирівнювання */
    __u64 in_syncobjs_ptr;   /* Вказівник на масив вхідних syncobj (In-fences) */
    __u32 in_syncobj_count;  /* Кількість вхідних syncobj */
    __u32 out_syncobj_count; /* Кількість вихідних syncobj */
    __u64 out_syncobjs_ptr;  /* Вказівник на масив вихідних syncobj (Out-fences) */
};
```

### Крок за кроком: перевірка вхідних параметрів у KMD

1. **Вирівнювання полів:** Ядро перевіряє, щоб `cmds_ptr`, `in_syncobjs_ptr` та `out_syncobjs_ptr` були вирівняні по межі 8 байтів, а `pad == 0`. Якщо ні — повертає `-EINVAL`.
2. **Перевірка вхідних огорож (In-fences):** Ядро перевіряє стан усіх `syncobj` з масиву `in_syncobjs_ptr`. Якщо попередні завдання в ланцюжку ще виконуються, нове завдання блокується у планувальнику `drm_sched` доти, доки вхідні `dma_fence` не перейдуть у сигнальний стан.
3. **Прив'язка вихідних огорож (Out-fences):** Ядро створює нову `dma_fence` і встановлює її в усі `syncobj` з масиву `out_syncobjs_ptr`.

## 6. Повноцінний практичний приклад C та C++: створення GEM, подання команд та очікування результату

Нижче наведено завершений практичний приклад створення GEM-буферів, формування командного буфера, його подання на виконання та асинхронної синхронізації завершення мовами C та C++20.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <string.h>
#include <errno.h>
#include <stdint.h>
#include <drm/drm.h>

/* Спрощені структури UAPI для створення, картографування та подання GEM */
struct accel_gem_create {
    uint64_t size;
    uint32_t handle;
    uint32_t pad;
};

struct accel_gem_mmap {
    uint32_t handle;
    uint32_t pad;
    uint64_t offset;
};

struct accel_command_desc {
    uint32_t handle;
    uint32_t size;
    uint64_t offset;
};

struct accel_submit {
    uint64_t cmds_ptr;
    uint32_t cmd_count;
    uint32_t out_syncobj;
    uint64_t flags;
};

#define DRM_IOCTL_ACCEL_GEM_CREATE  DRM_IOWR(DRM_COMMAND_BASE + 0x01, struct accel_gem_create)
#define DRM_IOCTL_ACCEL_GEM_MMAP    DRM_IOWR(DRM_COMMAND_BASE + 0x02, struct accel_gem_mmap)
#define DRM_IOCTL_ACCEL_SUBMIT      DRM_IOWR(DRM_COMMAND_BASE + 0x03, struct accel_submit)

int main(void) {
    int fd = open("/dev/accel/accel0", O_RDWR | O_CLOEXEC);
    if (fd < 0) {
        perror("Не вдалося відкрити /dev/accel/accel0");
        return EXIT_FAILURE;
    }

    /* 1. Створення GEM-буфера для даних (тензорів) */
    struct accel_gem_create data_req = { .size = 4096 };
    if (ioctl(fd, DRM_IOCTL_ACCEL_GEM_CREATE, &data_req) < 0) {
        perror("Помилка створення GEM-буфера даних");
        close(fd);
        return EXIT_FAILURE;
    }

    /* 2. Створення GEM-буфера для команд NPU */
    struct accel_gem_create cmd_req = { .size = 4096 };
    if (ioctl(fd, DRM_IOCTL_ACCEL_GEM_CREATE, &cmd_req) < 0) {
        perror("Помилка створення GEM-буфера команд");
        close(fd);
        return EXIT_FAILURE;
    }

    /* 3. Картографування буферів у простір адреси процесу */
    struct accel_gem_mmap mmap_data = { .handle = data_req.handle };
    ioctl(fd, DRM_IOCTL_ACCEL_GEM_MMAP, &mmap_data);
    void *data_ptr = mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fd, (off_t)mmap_data.offset);

    struct accel_gem_mmap mmap_cmd = { .handle = cmd_req.handle };
    ioctl(fd, DRM_IOCTL_ACCEL_GEM_MMAP, &mmap_cmd);
    void *cmd_ptr = mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fd, (off_t)mmap_cmd.offset);

    if (data_ptr == MAP_FAILED || cmd_ptr == MAP_FAILED) {
        perror("Помилка mmap буферів");
        close(fd);
        return EXIT_FAILURE;
    }

    /* Заповнюємо буфер даних тестовим тензором */
    memset(data_ptr, 0x7E, 4096);
    /* Заповнюємо командний буфер умовним нопом / інструкцією NPU */
    memset(cmd_ptr, 0x00, 4096);

    /* 4. Створення об'єкта синхронізації syncobj */
    struct drm_syncobj_create sync_create = { .flags = 0 };
    if (ioctl(fd, DRM_IOCTL_SYNCOBJ_CREATE, &sync_create) < 0) {
        perror("Помилка DRM_IOCTL_SYNCOBJ_CREATE");
        close(fd);
        return EXIT_FAILURE;
    }

    /* 5. Формування та подання завдання CS */
    struct accel_command_desc cmd_desc = {
        .handle = cmd_req.handle,
        .size = 4096,
        .offset = 0,
    };

    struct accel_submit submit_req = {
        .cmds_ptr = (uint64_t)(uintptr_t)&cmd_desc,
        .cmd_count = 1,
        .out_syncobj = sync_create.handle,
        .flags = 0,
    };

    if (ioctl(fd, DRM_IOCTL_ACCEL_SUBMIT, &submit_req) < 0) {
        perror("Помилка подання обчислювального завдання DRM_IOCTL_ACCEL_SUBMIT");
        close(fd);
        return EXIT_FAILURE;
    }

    printf("Подання команд успішно відправлено на NPU. Очікування syncobj...\n");

    /* 6. Очікування завершення виконання на NPU */
    struct drm_syncobj_wait wait_req = {
        .handles = (uint64_t)(uintptr_t)&sync_create.handle,
        .timeout_nsec = 5000000000ULL, /* 5 секунд */
        .count_handles = 1,
        .flags = DRM_SYNCOBJ_WAIT_FLAGS_WAIT_ALL,
        .first_signaled = 0,
        .pad = 0,
    };

    if (ioctl(fd, DRM_IOCTL_SYNCOBJ_WAIT, &wait_req) < 0) {
        perror("Помилка або таймаут DRM_IOCTL_SYNCOBJ_WAIT");
    } else {
        printf("Обчислення на NPU успішно завершено! Перевірка даних тензора...\n");
    }

    /* 7. Очищення ресурсів */
    struct drm_syncobj_destroy sync_destroy = { .handle = sync_create.handle };
    ioctl(fd, DRM_IOCTL_SYNCOBJ_DESTROY, &sync_destroy);

    struct drm_gem_close close_data = { .handle = data_req.handle };
    struct drm_gem_close close_cmd = { .handle = cmd_req.handle };
    ioctl(fd, DRM_IOCTL_GEM_CLOSE, &close_data);
    ioctl(fd, DRM_IOCTL_GEM_CLOSE, &close_cmd);

    munmap(data_ptr, 4096);
    munmap(cmd_ptr, 4096);
    close(fd);

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <memory>
#include <string_view>
#include <system_error>
#include <vector>
#include <cstdint>
#include <cstddef>
#include <span>
#include <algorithm>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <drm/drm.h>

struct AccelGemCreate {
    std::uint64_t size;
    std::uint32_t handle;
    std::uint32_t pad;
};

struct AccelGemMmap {
    std::uint32_t handle;
    std::uint32_t pad;
    std::uint64_t offset;
};

struct AccelCommandDesc {
    std::uint32_t handle;
    std::uint32_t size;
    std::uint64_t offset;
};

struct AccelSubmit {
    std::uint64_t cmds_ptr;
    std::uint32_t cmd_count;
    std::uint32_t out_syncobj;
    std::uint64_t flags;
};

#define DRM_IOCTL_ACCEL_GEM_CREATE  DRM_IOWR(DRM_COMMAND_BASE + 0x01, AccelGemCreate)
#define DRM_IOCTL_ACCEL_GEM_MMAP    DRM_IOWR(DRM_COMMAND_BASE + 0x02, AccelGemMmap)
#define DRM_IOCTL_ACCEL_SUBMIT      DRM_IOWR(DRM_COMMAND_BASE + 0x03, AccelSubmit)

class AccelDevice {
public:
    explicit AccelDevice(std::string_view path) {
        fd_ = ::open(path.data(), O_RDWR | O_CLOEXEC);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити NPU прискорювач");
        }
    }

    ~AccelDevice() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    AccelDevice(const AccelDevice&) = delete;
    AccelDevice& operator=(const AccelDevice&) = delete;

    AccelDevice(AccelDevice&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    AccelDevice& operator=(AccelDevice&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int fd() const noexcept { return fd_; }

    [[nodiscard]] std::uint32_t create_gem(std::size_t size) const {
        AccelGemCreate req{.size = static_cast<std::uint64_t>(size)};
        if (::ioctl(fd_, DRM_IOCTL_ACCEL_GEM_CREATE, &req) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка виділення GEM-буфера");
        }
        return req.handle;
    }

    void close_gem(std::uint32_t handle) const noexcept {
        drm_gem_close req{.handle = handle};
        ::ioctl(fd_, DRM_IOCTL_GEM_CLOSE, &req);
    }

    [[nodiscard]] std::uint64_t get_mmap_offset(std::uint32_t handle) const {
        AccelGemMmap req{.handle = handle};
        if (::ioctl(fd_, DRM_IOCTL_ACCEL_GEM_MMAP, &req) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка картографування GEM");
        }
        return req.offset;
    }

    [[nodiscard]] std::uint32_t create_syncobj() const {
        drm_syncobj_create req{.flags = 0};
        if (::ioctl(fd_, DRM_IOCTL_SYNCOBJ_CREATE, &req) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка створення syncobj");
        }
        return req.handle;
    }

    void destroy_syncobj(std::uint32_t handle) const noexcept {
        drm_syncobj_destroy req{.handle = handle};
        ::ioctl(fd_, DRM_IOCTL_SYNCOBJ_DESTROY, &req);
    }

    void submit_job(std::uint32_t cmd_handle, std::size_t cmd_size, std::uint32_t out_syncobj) const {
        AccelCommandDesc desc{
            .handle = cmd_handle,
            .size = static_cast<std::uint32_t>(cmd_size),
            .offset = 0,
        };

        AccelSubmit req{
            .cmds_ptr = reinterpret_cast<std::uint64_t>(&desc),
            .cmd_count = 1,
            .out_syncobj = out_syncobj,
            .flags = 0,
        };

        if (::ioctl(fd_, DRM_IOCTL_ACCEL_SUBMIT, &req) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка подання обчислювального завдання");
        }
    }

    bool wait_syncobj(std::uint32_t handle, std::uint64_t timeout_ns = 5'000'000'000ULL) const {
        std::uint64_t h_val = handle;
        drm_syncobj_wait req{
            .handles = reinterpret_cast<std::uint64_t>(&h_val),
            .timeout_nsec = static_cast<std::int64_t>(timeout_ns),
            .count_handles = 1,
            .flags = DRM_SYNCOBJ_WAIT_FLAGS_WAIT_ALL,
            .first_signaled = 0,
            .pad = 0,
        };

        return (::ioctl(fd_, DRM_IOCTL_SYNCOBJ_WAIT, &req) == 0);
    }

private:
    int fd_{-1};
};

/* RAII Обгортка для GEM буфера */
class GemBuffer {
public:
    GemBuffer(const AccelDevice& dev, std::size_t size) : dev_(dev), size_(size) {
        handle_ = dev_.create_gem(size_);
        std::uint64_t offset = dev_.get_mmap_offset(handle_);
        void* ptr = ::mmap(nullptr, size_, PROT_READ | PROT_WRITE, MAP_SHARED, dev_.fd(), static_cast<off_t>(offset));
        if (ptr == MAP_FAILED) {
            dev_.close_gem(handle_);
            throw std::system_error(errno, std::generic_category(), "Помилка mmap для GEM-буфера");
        }
        mapped_ptr_ = static_cast<std::uint8_t*>(ptr);
    }

    ~GemBuffer() {
        if (mapped_ptr_ != nullptr) {
            ::munmap(mapped_ptr_, size_);
        }
        if (handle_ != 0) {
            dev_.close_gem(handle_);
        }
    }

    GemBuffer(const GemBuffer&) = delete;
    GemBuffer& operator=(const GemBuffer&) = delete;

    [[nodiscard]] std::uint32_t handle() const noexcept { return handle_; }
    [[nodiscard]] std::size_t size() const noexcept { return size_; }

    [[nodiscard]] std::span<std::uint8_t> bytes() noexcept {
        return std::span<std::uint8_t>(mapped_ptr_, size_);
    }

private:
    const AccelDevice& dev_;
    std::size_t size_{0};
    std::uint32_t handle_{0};
    std::uint8_t* mapped_ptr_{nullptr};
};

/* RAII Обгортка для Syncobj */
class ScopedSyncobj {
public:
    explicit ScopedSyncobj(const AccelDevice& dev) : dev_(dev) {
        handle_ = dev_.create_syncobj();
    }

    ~ScopedSyncobj() {
        if (handle_ != 0) {
            dev_.destroy_syncobj(handle_);
        }
    }

    ScopedSyncobj(const ScopedSyncobj&) = delete;
    ScopedSyncobj& operator=(const ScopedSyncobj&) = delete;

    [[nodiscard]] std::uint32_t handle() const noexcept { return handle_; }

private:
    const AccelDevice& dev_;
    std::uint32_t handle_{0};
};

int main() {
    try {
        AccelDevice accel("/dev/accel/accel0");
        constexpr std::size_t buffer_size = 4096;

        /* Створення буферів з автоочищенням RAII */
        GemBuffer data_buf(accel, buffer_size);
        GemBuffer cmd_buf(accel, buffer_size);
        ScopedSyncobj syncobj(accel);

        /* Заповнюємо тензори через std::span */
        std::fill(data_buf.bytes().begin(), data_buf.bytes().end(), static_cast<std::uint8_t>(0x7E));
        std::fill(cmd_buf.bytes().begin(), cmd_buf.bytes().end(), static_cast<std::uint8_t>(0x00));

        std::cout << "[C++ RAII] GEM буфери та syncobj успішно створені\n";

        /* Подання обчислювального завдання */
        accel.submit_job(cmd_buf.handle(), cmd_buf.size(), syncobj.handle());
        std::cout << "[C++ RAII] Завдання відправлено в NPU. Чекаємо syncobj...\n";

        if (accel.wait_syncobj(syncobj.handle())) {
            std::cout << "[C++ RAII] Успішно! Обчислення на NPU завершено.\n";
        } else {
            std::cerr << "[C++ RAII] Таймаут або помилка виконання обчислень\n";
        }

    } catch (const std::exception& e) {
        std::cerr << "Критична помилка: " << e.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

## 7. Аналіз розбіжностей у проектуванні системного коду C та C++

Наведений розширений приклад ілюструє концептуальні відмінності підходів до проектування UMD простору користувача.

### 7.1 Порівняльна таблиця архітектурних підходів C проти C++20

| Критерій проектування | Системна реалізація C (C99 / C11) | Сучасна реалізація C++ (C++20) |
|---|---|---|
| **Управління ресурсами** | Ручний виклик `close()`, `munmap()`, `gem_close` | Принцип **RAII**: автоматичні деструктори |
| **Безпека від витоків** | Вимагає складних гілок `goto out_clean` | Гарантована виняткобезпека (Exception Safety) |
| **Буфери пам'яті** | Нетипізовані вказівники `void*` + `memset` | Шаблонний `std::span<T>` + `std::fill` / ітератори |
| **Обробка помилок** | Повернення від'ємного коду `-1` та `errno` | Об'єкти винятків `std::system_error` з категоріями |
| **Копіювання об'єктів** | Ручний контроль дублювання хендлів | Видалені оператори копіювання (`= delete`), Move semantics |

### 7.2 Автоматичне управління життєвим циклом ресурсів (RAII)

У C-реалізації розробник змушений вручну відстежувати п'ять системних ресурсів: файловий дескриптор пристрою (`fd`), два GEM-хендли (`data_req.handle`, `cmd_req.handle`), два відображення `mmap` (`data_ptr`, `cmd_ptr`) та об'єкт синхронізації (`sync_create.handle`). У разі виникнення помилки на будь-якому з кроків необхідні заплутані виклики очищення (`goto clean_sync; goto clean_mmap;`).

У C++20 застосовуються RAII-обгортки:
- Об'єкти `GemBuffer` та `ScopedSyncobj` зв'язують виділення ресурсу з конструктором, а його знищення (`munmap`, `DRM_IOCTL_GEM_CLOSE`, `DRM_IOCTL_SYNCOBJ_DESTROY`) — із деструктором.
- При виникненні винятку на етапі `submit_job()` деструктори викликаються у зворотному порядку для всіх вже створених об'єктів, виключаючи витоки пам'яті ядра або хендлів IDR.

### 7.3 Безпека типів та абстракція пам'яті через std::span

У C-коді відображена пам'ять обробляється як сирі вказівники `void*`, а заповнення здійснюється низькорівневою функцією `memset()`. Це підвищує ризик помилок виходу за межі буфера (buffer overflow) при неправильному підрахунку байтів.

У C++20 метод `data_buf.bytes()` повертає шаблонний тип `std::span<std::uint8_t>`. Це безпечне посилання на неперервний масив пам'яті з фіксованим розміром. Для заповнення даними використовується стандартний алгоритм `std::fill()`, який працює з ітераторами й виключає вихід за межі відображеної сторінки.

### 7.4 Модель обробки системних помилок

Класичний C-підхід спирається на перевірку поверненого від'ємного значення `ioctl` й перевірку глобальної змінної `errno`. У C++ реалізації використовується стандартний клас винятків `std::system_error`, який обгортає код `errno` у канонічну категорію `std::generic_category()`. Це дозволяє перехоплювати помилки драйвера ядра вище по стеку викликів за допомогою єдиного блоку `try/catch`.

## 8. Практичні підводні камені та крайові випадки (Edge Cases)

Під час розробки UMD-бібліотек та взаємодії з прискорювачами NPU системні розробники стикаються з критичними крайовими випадками:

1. **Апаратне зависання NPU (Hardware Timeout & Recovery / TDR):**
   Якщо нейронна мережа потрапляє у нескінченний цикл або апаратний обчислювач застрягає, планувальник ядра `drm_sched` фіксує таймаут виконання (за замовчуванням 5 секунд). Спрацьовує процедура TDR: драйвер виконує апаратне скидання (reset) NPU, скасовує подальші завдання в черзі, а `dma_fence` переводиться у сигнальний стан із помилкою `-ETIMEDOUT` або `-ECANCELED`.
2. **Alignment (Вирівнювання пам'яті та структур):**
   Фізичні DMA-контролери NPU вимагають суворого вирівнювання адрес буферів (наприклад, по межі 64 байтів або 4 КБ). Спроба передати невирівняне зміщення у CS IOCTL призведе до відхилення завдання KMD-драйвером з кодом `-EINVAL`.
3. **Page Cache Coherency (Узгодженість кешів CPU та NPU):**
   Оскільки CPU виконує запис у GEM-буфер через `mmap()`, дані можуть застрягти у L1/L2/L3 кешах процесора. Якщо NPU не підтримує апаратну когерентність кешів (Cache Coherency / CCI), UMD змушений надсилати IOCTL очищення кешу (`DRM_IOCTL_ACCEL_GEM_CPU_FINI`) перед подачею команди на NPU.
4. **Переривання системних викликів сигналами (EINTR Signal Interruption):**
   Під час тривалого очікування у `DRM_IOCTL_SYNCOBJ_WAIT` процес користувача може отримати сигнал Linux (наприклад, `SIGINT` або `SIGALRM`). Виклик `ioctl` повертає `-1`, а `errno` встановлюється в `EINTR`. UMD повинен обгортати очікування у цикл `do { ... } while (errno == EINTR)`.
5. **Гонка ресурсів та відкладене вивільнення GEM (Deferred GEM Destruction):**
   Якщо UMD викликає `DRM_IOCTL_GEM_CLOSE` для буфера, який у даний момент ще використовується NPU під час обчислень, ядро негайно видаляє хендл із таблиці простору користувача, але зберігає сам об'єкт пам'яті `struct drm_gem_object` в ядрі доти, доки прив'язана `dma_fence` не перейде у сигнальний стан.
6. **Витоки файлових дескрипторів sync_file_fd:**
   При експорті `syncobj` у дескриптор `sync_file_fd` для міжпроцесної синхронізації, якщо процес споживач не викликає `close(sync_file_fd)`, в ядрі залишається відкритим об'єкт `struct sync_file` разом із прив'язаною `dma_fence`, що блокує очищення пов'язаних GEM-буферів.
7. **Конкурентна багатопотокова подача (Multi-Threaded Submission Handling):**
   Коли кілька робочих потоків UMD одночасно викликають `DRM_IOCTL_ACCEL_SUBMIT` на один і той самий пристрій, `drm_sched_entity` гарантує порядкове впорядкування подань без взаємного заклинювання (deadlock), використовуючи внутрішнє замкнення огорож резервування `dma_resv_lock`.
8. **Профілювання та діагностика через debugfs та ftrace (`/sys/kernel/debug/accel/`):**
   Під час виявлення проблем з поданням команд системні інженери використовують атрибути debugfs. Читання `/sys/kernel/debug/accel/accel0/sched_job_list` показує список активних завдань у черзі `drm_sched`, а `/sys/kernel/debug/accel/accel0/error_state` містить дампи регістрів NPU у момент апаратного збою TDR. Команда `trace-cmd record -e drm:drm_sched_job -e dma_fence:dma_fence_signaled` дозволяє точно виміряти затримку апаратного виконання кожного подання без внесення змін у код UMD. Для аналізу затримок у просторі користувача застосовується `perf trace -e ioctl --call-graph fp`, який фіксує точний час передачі системного виклику `DRM_IOCTL_ACCEL_SUBMIT` та його параметри.
9. **Обробка сигналів завершення та коректне закриття конвеєра:**
   При отриманні сигналу завершення (`SIGTERM` або `SIGINT`) бібліотека UMD мусить завершити поточні виклики `SYNCOBJ_WAIT`, переконатися у сигналюванні `dma_fence` усіх активних обчислень, після чого послідовно викликати `munmap()`, `DRM_IOCTL_GEM_CLOSE` та `close(fd)`. Якщо процес вбивається примусово через `SIGKILL`, KMD-драйвер бере на себе очищення некоректно завершених контекстів у функції `drm_release()`.
