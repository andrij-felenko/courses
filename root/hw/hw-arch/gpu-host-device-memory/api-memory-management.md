# 📋 Специфікація інтерфейсів керування пам'яттю: CUDA та ROCm/HIP

Розробка високопродуктивних гетерогенних застосунків вимагає точного контролю над розміщенням даних у фізичних адресних просторах, типом сторінкового блокування та протоколами синхронізації між Host і Device. Невірно обраний тип виділення пам'яті або відсутність вирівнювання здатні знизити пропускну здатність шини в десятки разів і заблокувати роботу потокових мультипроцесорів. Ця довідкова специфікація визначає сигнатури, конфігураційні прапорці, семантику пам'яті, інваріанти, правила синхронізації та коди помилок фундаментальних інтерфейсів керування пам'яттю в середовищах NVIDIA CUDA Runtime API та AMD ROCm / HIP API.

## 1. Архітектурна класифікація типів виділення пам'яті

Сучасні гетерогенні середовища надають кілька взаємодоповнюючих механізмів виділення пам'яті. Кожен тип розрахований на специфічний сценарій доступу та забезпечує певний компроміс між доступністю для процесорів, затримкою звернення та піковою пропускною здатністю.

Стандартна сторінкова пам'ять хоста виділяється через звичайні системні виклики операційної системи. Вона є найпростішою у використанні, проте контролер прямого доступу до пам'яті (DMA) графічного прискорювача не може звертатися до неї безпосередньо через ризик витискання сторінок у файл підкачки. Для виконання пересилки драйвер вимушений використовувати прихований проміжний буфер ядра, що призводить до подвійного копіювання даних та завантаження ядер центрального процесора.

Фіксована пам'ять хоста позбавлена цього недоліку: її фізичні сторінки апаратно блокуються операційною системою від переміщення. Це дозволяє контролеру DMA на платі прискорювача напряму зчитувати й записувати байти по шині PCIe на максимальній фізичній швидкості інтерфейсу. Відображена пам'ять є розширенням фіксованої пам'яті, де сторінки хоста отримують додаткове відображення безпосередньо у віртуальний адресний простір графічного процесора, дозволяючи обчислювальним ядрам читати дані з оперативної пам'яті процесора без попереднього копіювання.

Пам'ять пристрою виділяється безпосередньо у фізичних мікросхемах VRAM графічного процесора. Вона забезпечує найвищу швидкість читання й запису завдяки широкій локальній шині, але не може бути безпосередньо розіменована кодом центрального процесора. Нарешті, керована пам'ять об'єднує адресні простори в єдиний спільний масив, де фізичне переміщення сторінок між Host RAM та Device VRAM автоматично виконується драйвером та апаратним блоком обробки сторінкових промахів.

| Тип пам'яті | Функція виділення (CUDA) | Функція виділення (HIP) | Фізичне розміщення | Доступність CPU | Доступність GPU | Механізм доступу GPU |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Сторінкова (Pageable Host)** | `malloc()` / `new` | `malloc()` / `new` | Системна RAM | Прямий (кеш L1–L3) | Немає прямого | Синхронний staging буфер ядра |
| **Фіксована (Pinned / Locked)** | `cudaHostAlloc()` | `hipHostMalloc()` | Системна RAM (Lock) | Прямий (кеш L1–L3) | Немає (або Mapped) | Прямий PCIe DMA трансфер |
| **Відображена (Zero-Copy)** | `cudaHostAlloc(..., Mapped)` | `hipHostMalloc(..., Mapped)` | Системна RAM (Lock) | Прямий (кеш L1–L3) | Прямий через PCIe | Прямі транзакції по PCIe (TLP) |
| **Пам'ять пристрою (Device VRAM)** | `cudaMalloc()` | `hipMalloc()` | Локальна VRAM | Немає прямого | Прямий (надширока шина) | Локальний контролер VRAM |
| **Потокова асинхронна (Stream-Ordered)** | `cudaMallocAsync()` | `hipMallocAsync()` | Локальна VRAM (Pool) | Немає прямого | Прямий (надширока шина) | Пул без системних блокувань |
| **Керована (Unified / Managed)** | `cudaMallocManaged()` | `hipMallocManaged()` | Динамічна міграція | Прямий (єдиний вказівник) | Прямий (єдиний вказівник) | Апаратні Page Faults / HMM |

## 2. Керування пам'яттю пристрою (Device Memory)

Пам'ять пристрою виділяється виключно у фізичному пулі VRAM графічного прискорювача. Обчислювальні ядра мають до неї максимальну пропускну здатність (1 000–3 300 ГБ/с), але центральний процесор не може безпосередньо розіменувати такий покажчик.

### 2.1. Сигнатури функцій

:::tabs
```c
/* CUDA Runtime API */
cudaError_t cudaMalloc(void **devPtr, size_t size);
cudaError_t cudaMallocPitch(void **devPtr, size_t *pitch, size_t width, size_t height);
cudaError_t cudaFree(void *devPtr);

/* ROCm HIP API */
hipError_t hipMalloc(void **ptr, size_t size);
hipError_t hipMallocPitch(void **ptr, size_t *pitch, size_t width, size_t height);
hipError_t hipFree(void *ptr);
```
```cpp
/* C++ RAII-обгортка з контролем винятків */
#include <cuda_runtime.h>
#include <stdexcept>
#include <string>

template <typename T>
class DeviceMemory {
public:
    explicit DeviceMemory(size_t count) : count_(count) {
        cudaError_t err = cudaMalloc(reinterpret_cast<void**>(&ptr_), count_ * sizeof(T));
        if (err != cudaSuccess) {
            throw std::runtime_error(std::string("cudaMalloc error: ") + cudaGetErrorString(err));
        }
    }
    ~DeviceMemory() noexcept {
        if (ptr_) {
            cudaFree(ptr_);
        }
    }
    DeviceMemory(const DeviceMemory&) = delete;
    DeviceMemory& operator=(const DeviceMemory&) = delete;
    DeviceMemory(DeviceMemory&& other) noexcept : ptr_(other.ptr_), count_(other.count_) {
        other.ptr_ = nullptr;
        other.count_ = 0;
    }
    DeviceMemory& operator=(DeviceMemory&& other) noexcept {
        if (this != &other) {
            if (ptr_) cudaFree(ptr_);
            ptr_ = other.ptr_;
            count_ = other.count_;
            other.ptr_ = nullptr;
            other.count_ = 0;
        }
        return *this;
    }

    [[nodiscard]] T* get() noexcept { return ptr_; }
    [[nodiscard]] const T* get() const noexcept { return ptr_; }
    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] size_t bytes() const noexcept { return count_ * sizeof(T); }

private:
    T *ptr_{nullptr};
    size_t count_{0};
};
```
:::

### 2.2. Параметри та семантика виклику

Параметр `devPtr` представляє адресу змінної типу `void*`, куди записується початкова лінійна адреса виділеного блока в адресному просторі GPU. Адреса завжди вирівнюється на межу 256 або 512 байтів для забезпечення ефективного вирівнювання транзакцій.

Параметр `size` вказує розмір виділеного блока в байтах. Якщо значення дорівнює `0`, функція повертає `cudaSuccess`, а `*devPtr` встановлюється в `nullptr`. Розподільник пам'яті драйвера виділяє пам'ять великими сторінками або чанками для зменшення фрагментації пулу VRAM.

Функція `cudaMallocPitch` призначена для виділення пам'яті під двовимірні матриці та зображення. Параметр `pitch` повертає вирівняну апаратну ширину рядка двовимірного масиву в байтах. Додавання вирівнювальних байтів гарантує, що кожен рядок матриці починається з адреси, кратної розміру сегмента пам'яті (128 байтів), що запобігає деградації транзакцій об'єднання пам'яті (*memory coalescing*) при читанні стовпчиків або сусідніх елементів варпом.

### 2.3. Коди помилок та інваріанти

- `cudaSuccess (0)`: пам'ять успішно зарезервована та виділена.
- `cudaErrorMemoryAllocation (2)`: у пристрої недостатньо вільної фізичної пам'яті VRAM для задоволення запиту.
- `cudaErrorInvalidValue (1)`: передано недійсний вказівник або непідтримувані параметри розміру.
- `cudaErrorInitializationError (3)`: збій підсистеми драйвера або відсутність сумісного обладнання.

## 3. Асинхронне потокове виділення пам'яті (Stream-Ordered Memory Allocation)

Починаючи з версії CUDA 11.2 (та ROCm 5.2), з'явився механізм потокового виділення пам'яті через виклики `cudaMallocAsync()` та `cudaFreeAsync()`. Традиційний `cudaMalloc()` є важким синхронним системним викликом, що блокує всі потоки хоста, оскільки вимагає глобального м'ютекса в драйвері. Потокове виділення використовує вбудований пул пам'яті (*Memory Pool*), прив'язаний до конкретного потоку CUDA, усуваючи синхронізацію процесора.

### 3.1. Сигнатури потокового виділення

:::tabs
```c
/* CUDA Runtime API */
cudaError_t cudaMallocAsync(void **devPtr, size_t size, cudaStream_t stream);
cudaError_t cudaFreeAsync(void *devPtr, cudaStream_t stream);

cudaError_t cudaMemPoolCreate(cudaMemPool_t *memPool, const cudaMemPoolProps *poolProps);
cudaError_t cudaMemPoolDestroy(cudaMemPool_t memPool);
cudaError_t cudaMemPoolTrimTo(cudaMemPool_t memPool, size_t minBytesToKeep);

/* ROCm HIP API */
hipError_t hipMallocAsync(void **devPtr, size_t size, hipStream_t stream);
hipError_t hipFreeAsync(void *devPtr, hipStream_t stream);
```
```cpp
/* C++ інтерфейс асинхронного буфера, прив'язаного до життєвого циклу потоку */
#include <cuda_runtime.h>
#include <stdexcept>
#include <string>

template <typename T>
class AsyncDeviceMemory {
public:
    AsyncDeviceMemory(size_t count, cudaStream_t stream) 
        : count_(count), stream_(stream) {
        cudaError_t err = cudaMallocAsync(reinterpret_cast<void**>(&ptr_),
                                          count_ * sizeof(T),
                                          stream_);
        if (err != cudaSuccess) {
            throw std::runtime_error(std::string("cudaMallocAsync error: ") + 
                                     cudaGetErrorString(err));
        }
    }
    ~AsyncDeviceMemory() noexcept {
        if (ptr_) {
            cudaFreeAsync(ptr_, stream_);
        }
    }
    AsyncDeviceMemory(const AsyncDeviceMemory&) = delete;
    AsyncDeviceMemory& operator=(const AsyncDeviceMemory&) = delete;
    AsyncDeviceMemory(AsyncDeviceMemory&& other) noexcept 
        : ptr_(other.ptr_), count_(other.count_), stream_(other.stream_) {
        other.ptr_ = nullptr;
        other.count_ = 0;
    }
    AsyncDeviceMemory& operator=(AsyncDeviceMemory&& other) noexcept {
        if (this != &other) {
            if (ptr_) cudaFreeAsync(ptr_, stream_);
            ptr_ = other.ptr_;
            count_ = other.count_;
            stream_ = other.stream_;
            other.ptr_ = nullptr;
            other.count_ = 0;
        }
        return *this;
    }

    [[nodiscard]] T* get() noexcept { return ptr_; }
    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] size_t bytes() const noexcept { return count_ * sizeof(T); }

private:
    T *ptr_{nullptr};
    size_t count_{0};
    cudaStream_t stream_{nullptr};
};
```
:::

### 3.2. Налаштування атрибутів пулу пам'яті

Диспетчер пулу пам'яті підтримує конфігурацію політики утилізації через функцію `cudaMemPoolSetAttribute()`. Атрибут `cudaMemPoolAttrReleaseThreshold` визначає обсяг пам'яті в байтах, який пул утримує перед тим, як повернути надлишкові сторінки операційній системі. Встановлення високого порогу дозволяє повторно використовувати виділені ділянки в циклі обчислень без жодних системних викликів.

Атрибут `cudaMemPoolReuseFollowEventDependencies` дозволяє розподільнику пам'яті автоматично перевикористовувати блоки пам'яті між різними потоками, якщо між ними встановлено відношення порядку через події CUDA (`cudaEvent_t`).

:::tabs
```c
/* Конфігурація порогу утримання фізичної пам'яті в пулі */
uint64_t threshold = 1024 * 1024 * 512; /* 512 МБ */
cudaMemPoolSetAttribute(pool, cudaMemPoolAttrReleaseThreshold, &threshold);

/* Дозвіл повторного використання пам'яті між різними потоками при наявності подій */
int enable_reuse = 1;
cudaMemPoolSetAttribute(pool, cudaMemPoolReuseFollowEventDependencies, &enable_reuse);
```
```cpp
/* C++ обгортка конфігурації пулу пам'яті */
#include <cuda_runtime.h>
#include <stdexcept>

inline void configure_pool(cudaMemPool_t pool, uint64_t release_threshold_bytes) {
    cudaError_t err = cudaMemPoolSetAttribute(pool, 
                                              cudaMemPoolAttrReleaseThreshold, 
                                              &release_threshold_bytes);
    if (err != cudaSuccess) {
        throw std::runtime_error("cudaMemPoolSetAttribute failed");
    }
}
```
:::

## 4. Фіксована пам'ять хоста (Pinned / Page-Locked Host Memory)

Фіксована пам'ять виділяється в оперативній пам'яті процесора, але її фізичні сторінки апаратно блокуються операційною системою від витискання у файл підкачки (*paging/swapping*). Це дозволяє контролеру DMA прискорювача транслювати віртуальні адреси безпосередньо у фізичні адреси шини PCIe.

### 4.1. Сигнатури функцій

:::tabs
```c
/* CUDA Runtime API */
cudaError_t cudaHostAlloc(void **pHost, size_t size, unsigned int flags);
cudaError_t cudaMallocHost(void **ptr, size_t size); /* Еквівалент flags = 0 */
cudaError_t cudaFreeHost(void *pHost);

/* ROCm HIP API */
hipError_t hipHostMalloc(void **ptr, size_t size, unsigned int flags);
hipError_t hipHostFree(void *ptr);
```
```cpp
/* C++ інтерфейс типізованого виділення фіксованого буфера */
#include <cuda_runtime.h>
#include <span>
#include <memory>
#include <new>

template <typename T>
struct PinnedDeleter {
    void operator()(T *ptr) const noexcept {
        if (ptr) cudaFreeHost(ptr);
    }
};

template <typename T>
using UniquePinned = std::unique_ptr<T[], PinnedDeleter<T>>;

template <typename T>
UniquePinned<T> make_pinned(size_t count, unsigned int flags = cudaHostAllocDefault) {
    void *raw = nullptr;
    cudaError_t err = cudaHostAlloc(&raw, count * sizeof(T), flags);
    if (err != cudaSuccess) {
        throw std::bad_alloc();
    }
    return UniquePinned<T>(static_cast<T*>(raw));
}
```
:::

### 4.2. Таблиця конфігураційних прапорців (`flags`)

Прапорці конфігурації дозволяють точно налаштувати поведінку кешування та доступності сторінок хоста з боку різних пристроїв системи:

| Прапорець CUDA | Прапорець HIP | Опис функціональності та апаратна поведінка |
| :--- | :--- | :--- |
| `cudaHostAllocDefault` | `hipHostMallocDefault` | Стандартне виділення заблокованих сторінок. Прямий DMA доступний для асинхронних копіювань `cudaMemcpyAsync`. |
| `cudaHostAllocPortable` | `hipHostMallocPortable` | Робить пам'ять заблокованою для *всіх* контекстів CUDA в системі (критично для систем із кількома GPU). |
| `cudaHostAllocMapped` | `hipHostMallocMapped` | Відображає виділену системну пам'ять безпосередньо у віртуальний адресний простір GPU (Zero-Copy режим). |
| `cudaHostAllocWriteCombined` | `hipHostMallocWriteCombined` | Вимикає кешування L1/L2 процесора (WC-буферизація). Прискорює запис із CPU та DMA-читання з GPU, але критично уповільнює читання з боку CPU. |

### 4.3. Блокування наявної пам'яті (Host Register API)

Якщо буфер уже виділений стандартним розподільником ОС (`malloc`, `posix_memalign`, `mmap`), його можна заблокувати для прямого DMA без виділення нового масиву. Це критично для інтеграції з існуючими сторонніми бібліотеками, мережевими буферами та драйверами захоплення відео.

:::tabs
```c
/* CUDA Runtime API: блокування наявного віртуального діапазону ОС */
cudaError_t cudaHostRegister(void *ptr, size_t size, unsigned int flags);
cudaError_t cudaHostUnregister(void *ptr);

/* Прапорці:
 * cudaHostRegisterDefault    - фіксація сторінок
 * cudaHostRegisterPortable   - доступність усім контекстам
 * cudaHostRegisterMapped     - відображення адрес у простір GPU
 * cudaHostRegisterIoMemory   - для пам'яті сторонніх PCIe пристроїв
 */
```
```cpp
/* C++ RAII-обгортка для реєстрації існуючих контейнерів (std::vector) */
#include <cuda_runtime.h>
#include <span>
#include <stdexcept>

template <typename T>
class RegisteredHostSpan {
public:
    explicit RegisteredHostSpan(std::span<T> data_span, unsigned int flags = cudaHostRegisterDefault)
        : span_(data_span) {
        cudaError_t err = cudaHostRegister(span_.data(), span_.size_bytes(), flags);
        if (err != cudaSuccess) {
            throw std::runtime_error("cudaHostRegister failed");
        }
    }
    ~RegisteredHostSpan() noexcept {
        cudaHostUnregister(span_.data());
    }
    RegisteredHostSpan(const RegisteredHostSpan&) = delete;
    RegisteredHostSpan& operator=(const RegisteredHostSpan&) = delete;

    [[nodiscard]] std::span<T> span() const noexcept { return span_; }

private:
    std::span<T> span_;
};
```
:::

## 5. Відображена пам'ять (Zero-Copy / Mapped Memory API)

У режимі Zero-Copy графічний процесор не копіює масив у VRAM, а надсилає атомарні транзакції читання й запису безпосередньо через шину PCIe на кожній інструкції ядра.

### 5.1. Отримання покажчика пристрою

Для отримання віртуальної адреси пристрою для відображеного буфера застосовують функцію `cudaHostGetDevicePointer()`. Отриманий покажчик передається в ядро так само, як і покажчик на звичайну VRAM.

:::tabs
```c
/* Отримання покажчика пристрою для Mapped буфера */
cudaError_t cudaHostGetDevicePointer(void **pDevice, void *pHost, unsigned int flags);
```
```cpp
/* C++ допоміжна функція отримання device покажчика */
#include <cuda_runtime.h>
#include <stdexcept>

template <typename T>
T* get_mapped_device_pointer(T* host_mapped_ptr) {
    void* dev_ptr = nullptr;
    cudaError_t err = cudaHostGetDevicePointer(&dev_ptr, host_mapped_ptr, 0);
    if (err != cudaSuccess) {
        throw std::runtime_error("cudaHostGetDevicePointer failed");
    }
    return static_cast<T*>(dev_ptr);
}
```
:::

- `pDevice`: повертає адресу у віртуальному просторі пристрою, яку можна передавати аргументом у ядро `kernel<<<grid, block>>>(pDevice)`.
- `pHost`: адреса вихідного буфера, створеного з прапорцем `cudaHostAllocMapped` або зареєстрованого з `cudaHostRegisterMapped`.
- `flags`: зарезервовано для майбутніх розширень (мусить дорівнювати `0`).

## 6. Керована пам'ять (Unified / Managed Memory API)

Керована пам'ять створює єдиний спільний адресний простір, де один і той самий покажчик є валідним для коду як центрального, так і графічного процесорів.

### 6.1. Сигнатура виділення

:::tabs
```c
/* CUDA Runtime API */
cudaError_t cudaMallocManaged(void **devPtr, size_t size, unsigned int flags);

/* ROCm HIP API */
hipError_t hipMallocManaged(void **ptr, size_t size, unsigned int flags);
```
```cpp
/* C++ обгортка автоматичної пам'яті з префетчингом */
#include <cuda_runtime.h>
#include <stdexcept>

template <typename T>
class ManagedBuffer {
public:
    explicit ManagedBuffer(size_t count, unsigned int flags = cudaMemAttachGlobal) 
        : count_(count) {
        cudaError_t err = cudaMallocManaged(reinterpret_cast<void**>(&ptr_),
                                            count_ * sizeof(T),
                                            flags);
        if (err != cudaSuccess) {
            throw std::runtime_error("cudaMallocManaged failed");
        }
    }
    ~ManagedBuffer() noexcept {
        if (ptr_) cudaFree(ptr_);
    }

    void prefetch_to_device(int device_id, cudaStream_t stream = 0) {
        cudaMemPrefetchAsync(ptr_, count_ * sizeof(T), device_id, stream);
    }
    void prefetch_to_host(cudaStream_t stream = 0) {
        cudaMemPrefetchAsync(ptr_, count_ * sizeof(T), cudaCpuDeviceId, stream);
    }

    [[nodiscard]] T* data() noexcept { return ptr_; }
    [[nodiscard]] size_t size() const noexcept { return count_; }

private:
    T *ptr_{nullptr};
    size_t count_{0};
};
```
:::

Прапорець `cudaMemAttachGlobal` робить виділену пам'ять доступною для будь-якого потоку будь-якого пристрою системи. Прапорець `cudaMemAttachHost` створює пам'ять, яка спочатку відображається лише в контексті процесора хоста, що дозволяє оптимізувати використання віртуальних адрес на системах із багатьма відеокартами.

### 6.2. Асинхронне підтягування сторінок (Prefetching API)

Щоб уникнути катастрофічної затримки обробки тисяч сторінкових переривань (*Page Faults*), пам'ять підтягують у VRAM завчасно апаратним DMA. Це виконується викликом `cudaMemPrefetchAsync()`, який ставить у чергу потоку команду пакетного перенесення сторінок.

:::tabs
```c
/* CUDA Runtime API: примусова міграція сторінок у потік */
cudaError_t cudaMemPrefetchAsync(const void *devPtr,
                                size_t count,
                                int dstDevice,
                                cudaStream_t stream);
```
```cpp
/* C++ виклик префетчингу для діапазону пам'яті */
#include <cuda_runtime.h>

inline void prefetch_range(const void* ptr, size_t bytes, int device_id, cudaStream_t stream = 0) {
    cudaMemPrefetchAsync(ptr, bytes, device_id, stream);
}
```
:::

- `dstDevice`: числовий ідентифікатор цільового пристрою (наприклад, `0` для першої відеокарти) або спеціальна константа `cudaCpuDeviceId` для повернення сторінок у системне ОЗП хоста.
- `stream`: потік CUDA, у чергу якого ставиться асинхронна операція міграції.

### 6.3. Підказки розміщення сторінок (Memory Advice API)

Драйвер та апаратний блок MMU можуть оптимізувати політику когерентності за допомогою виклику `cudaMemAdvise()`. Підказки дозволяють контролювати дублювання сторінок тільки для читання та встановлювати базову локацію проживання пам'яті:

:::tabs
```c
/* Встановлення підказок диспетчеру сторінок */
cudaError_t cudaMemAdvise(const void *devPtr,
                          size_t count,
                          enum cudaMemoryAdvise advice,
                          int device);
```
```cpp
/* C++ обгортка конфігурації підказок розміщення пам'яті */
#include <cuda_runtime.h>
#include <stdexcept>

inline void advise_memory(const void* ptr, size_t bytes, cudaMemoryAdvise advice, int device) {
    cudaError_t err = cudaMemAdvise(ptr, bytes, advice, device);
    if (err != cudaSuccess) {
        throw std::runtime_error("cudaMemAdvise failed");
    }
}
```
:::

| Значення `cudaMemoryAdvise` | Призначення та оптимізація драйвера |
| :--- | :--- |
| `cudaMemAdviseSetReadMostly` | Створює локальні копії сторінок у пам'яті кожного пристрою, що їх читає (дублювання без міграції). Запис інвалідує копії. |
| `cudaMemAdviseSetPreferredLocation` | Встановлює базове фізичне місце проживання сторінок (наприклад, VRAM пристрою). Дані повертаються туди після завершення обробки CPU. |
| `cudaMemAdviseSetAccessedBy` | Створює прямі таблиці відображення сторінок для вказаного пристрою, дозволяючи доступ без генерації Page Fault. |

### 6.4. Опитування атрибутів діапазонів керованої пам'яті

Для діагностики фізичного розташування сторінок у рантаймі застосовують виклик `cudaMemRangeGetAttribute()`:

:::tabs
```c
/* Запит атрибута поточного фізичного розміщення сторінок */
int location = 0;
cudaMemRangeGetAttribute(&location, sizeof(int), 
                         cudaMemRangeAttributeLastPrefetchLocation, 
                         devPtr, count);
```
```cpp
/* C++ функція отримання пристрою поточної локації пам'яті */
#include <cuda_runtime.h>
#include <stdexcept>

inline int query_last_prefetch_device(const void* ptr, size_t bytes) {
    int dev_id = -1;
    cudaError_t err = cudaMemRangeGetAttribute(&dev_id, sizeof(int),
                                               cudaMemRangeAttributeLastPrefetchLocation,
                                               ptr, bytes);
    if (err != cudaSuccess) {
        throw std::runtime_error("cudaMemRangeGetAttribute failed");
    }
    return dev_id;
}
```
:::

## 7. Внутрішня ієрархія пам'яті пристрою (On-Device Memory Hierarchy)

Окрім глобальної пам'яті VRAM, кристал графічного процесора містить кілька спеціалізованих апаратних просторів пам'яті, оптимізованих під конкретні патерни доступу всередині потокових мультипроцесорів (SM):

1. **Регістровий файл (Register File)**: Найшвидша пам'ять на чипі. Кожен мультипроцесор містить від 64 КБ до 256 КБ 32-бітних регістрів. Звернення до регістрів відбувається за 0–1 такт без використання кешів. Регістри розподіляються між нитками варпу під час запуску ядра; якщо кількість змінних перевищує доступний ліміт, надлишкові змінні витісняються у локальну пам'ять (*Register Spilling*).
2. **Розділювана пам'ять (Shared Memory / LDS)**: Програмований L1-кеш на рівні блоку ниток (*Thread Block*), розташований на кристалі поруч із ядрами ALU. Має пропускну здатність понад 10–20 ТБ/с на чип та затримку близько 20–30 тактів. Фізично розділена на 32 банки пам'яті по 4 байти. Якщо кілька потоків варпу одночасно звертаються до різних адрес в одному банку, виникає **конфлікт банків** (*Bank Conflict*), що серіалізує запити.
3. **Константна пам'ять (Constant Memory, `__constant__`)**: Простір обсягом 64 КБ, зарезервований у VRAM і кешований спеціальним апаратним кешем констант. Якщо всі 32 потоки варпу читають одну й ту саму адресу (наприклад, ваговий коефіцієнт або параметр маски), кеш констант виконує апаратне радіомовлення (*Broadcast*) за один такт.
4. **Текстурна пам'ять та Read-Only Cache (`__ldg()`)**: Апаратний кеш, оптимізований під 2D/3D просторову локальність. Підтримує апаратну нормалізацію координат, адресацію з відсіканням країв та лінійну фільтрацію.

## 8. Асинхронне копіювання пам'яті (Memory Transfer API)

### 8.1. Сигнатура та напрямки пересилки

Функція `cudaMemcpyAsync()` здійснює неблокуюче копіювання пам'яті між будь-якими адресними просторами системи. Виклик негайно повертає керування центральному процесору, поміщаючи задачу копіювання у чергу вказаного потоку `stream`.

:::tabs
```c
/* CUDA Runtime API */
cudaError_t cudaMemcpyAsync(void *dst,
                            const void *src,
                            size_t count,
                            enum cudaMemcpyKind kind,
                            cudaStream_t stream);

/* ROCm HIP API */
hipError_t hipMemcpyAsync(void *dst,
                          const void *src,
                          size_t count,
                          hipMemcpyKind kind,
                          hipStream_t stream);
```
```cpp
/* C++ безпечна обгортка неблокуючого копіювання */
#include <cuda_runtime.h>
#include <stdexcept>

inline void async_copy(void* dst, const void* src, size_t bytes, cudaMemcpyKind kind, cudaStream_t stream) {
    cudaError_t err = cudaMemcpyAsync(dst, src, bytes, kind, stream);
    if (err != cudaSuccess) {
        throw std::runtime_error("cudaMemcpyAsync failed");
    }
}
```
:::

- `kind` визначає топологічний напрямок копіювання:
  - `cudaMemcpyHostToHost (0)`: внутрішнє копіювання в RAM (використовує CPU memcpy);
  - `cudaMemcpyHostToDevice (1)`: завантаження з системної RAM у відеопам'ять VRAM через PCIe;
  - `cudaMemcpyDeviceToHost (2)`: вивантаження з VRAM у системну RAM через PCIe;
  - `cudaMemcpyDeviceToDevice (3)`: локальне копіювання всередині VRAM або P2P між відеокартами;
  - `cudaMemcpyDefault (4)`: автоматичне визначення напрямку на основі адресних просторів покажчиків (потребує Unified Virtual Addressing, UVA).

## 9. Прямий доступ між пристроями (Peer-to-Peer Multi-GPU Access)

У багатопроцесорних серверах прискорювачі можуть обмінюватися даними безпосередньо по шині PCIe або через високошвидкісний міст NVLink, минаючи оперативну пам'ять хоста. Функція `cudaDeviceEnablePeerAccess()` налаштовує адресні регістри пристрою для прямого читання пам'яті сусідньої карти.

:::tabs
```c
/* CUDA Runtime API */
cudaError_t cudaDeviceCanAccessPeer(int *canAccessPeer, int device, int peerDevice);
cudaError_t cudaDeviceEnablePeerAccess(int peerDevice, unsigned int flags);
cudaError_t cudaDeviceDisablePeerAccess(int peerDevice);

cudaError_t cudaMemcpyPeerAsync(void *dst, int dstDevice,
                                const void *src, int srcDevice,
                                size_t count, cudaStream_t stream);
```
```cpp
/* C++ утиліта підключення прямого P2P доступу між двома картами */
#include <cuda_runtime.h>
#include <iostream>

inline bool enable_p2p_if_supported(int dev_a, int dev_b) {
    int can_access = 0;
    cudaDeviceCanAccessPeer(&can_access, dev_a, dev_b);
    if (can_access) {
        cudaSetDevice(dev_a);
        cudaError_t err = cudaDeviceEnablePeerAccess(dev_b, 0);
        return (err == cudaSuccess || err == cudaErrorPeerAccessAlreadyEnabled);
    }
    return false;
}
```
:::

## 10. Особливості моделі пам'яті в AMD ROCm / HIP

Середовище AMD ROCm має глибоку архітектурну еквівалентність з CUDA через інтерфейс сумісності HIP, проте має специфічні особливості в апаратній підтримці когерентності пам'яті:

1. **Грубозерниста пам'ять (Coarse-Grained Memory)**: Стандартна пам'ять пристрою в ROCm. Кеші L1/L2 прискорювача не узгоджуються з кешами центрального процесора під час виконання ядра. Інвалідація кешів відбувається лише на межах запуску ядер (*Kernel Dispatch Boundaries*).
2. **Дрібнозерниста пам'ять (Fine-Grained Memory)**: Спеціальний режим виділення (`hipExtMallocWithFlags` із прапорцем `hipDeviceMallocFinegrained`), за якого кожен атомарний запис ядра GPU миттєво стає видимим для кешів CPU через шину PCIe або Infinity Fabric. Забезпечує пряму побудову неблокуючих черг (Lock-free queues) між процесором та відеокартою ціною відключення частини локальних кешів прискорювача.
3. **Підтримка Heterogeneous Memory Management (HMM)**: Починаючи з ROCm 5.0 та архітектур CDNA/RDNA3, середовище підтримує апаратну міграцію звичайних покажчиків системи Linux (`malloc`), виділених у системній пам'яті, без необхідності явної адаптації коду.

## 11. Діагностика помилок пам'яті та налагодження

Оскільки команди в GPU виконуються асинхронно, звичайні перевірки кодів помилок можуть повертати статус успіху, навіть якщо ядро впало через недійсний доступ до пам'яті (*Illegal Memory Access*). 

Драйвер CUDA використовує концепцію **липких асинхронних помилок** (*Sticky Errors*): якщо в ядрі трапляється вихід за межі масиву у VRAM, пристрій встановлює статус фатальної помилки. Усі наступні виклики `cudaMemcpy` або `cudaMalloc` повертатимуть код помилки `cudaErrorIllegalAddress (700)` аж до повного перезавантаження контексту пристрою.

:::tabs
```c
/* C: перевірка наявності асинхронних помилок ядра */
cudaError_t err = cudaGetLastError();
if (err != cudaSuccess) {
    printf("Асинхронний збій ядра: %s (%s)\n", cudaGetErrorName(err), cudaGetErrorString(err));
}
```
```cpp
/* C++: функція верифікації стану пристрою */
#include <cuda_runtime.h>
#include <stdexcept>
#include <string>

inline void verify_device_health() {
    cudaError_t err = cudaGetLastError();
    if (err != cudaSuccess) {
        throw std::runtime_error(std::string("GPU Health Failure: ") + 
                                 cudaGetErrorName(err) + " - " + 
                                 cudaGetErrorString(err));
    }
}
```
:::

Для точного знаходження рядка коду, де відбувся недійсний доступ, застосовують запуск програми зі змінною середовища `CUDA_LAUNCH_BLOCKING=1`, що змушує драйвер автоматично синхронізувати процесор після кожного виклику ядра, або використовують санітайзер пам'яті **compute-sanitizer** (`compute-sanitizer --tool memcheck ./app`).

## 12. Інженерний чекліст продуктивності та безпеки

1. **Неблокуючий контракт `cudaMemcpyAsync`**: Асинхронна передача є справді неблокуючою для CPU лише за умови, що буфер на хості виділено через `cudaHostAlloc()` або заблоковано через `cudaHostRegister()`. Для звичайної пам'яті виклик блокує викликаючий потік CPU до моменту завершення копіювання в транзитний буфер.
2. **Вимога до вирівнювання Zero-Copy**: Розмір структур даних при прямому доступі через шину PCIe мусить бути кратним 32, 64 або 128 байтам для повної утилізації розміру пакету PCIe TLP (Transaction Layer Packet).
3. **Запобігання Page Thrashing**: Ніколи не чергуйте паралельні побайтові операції запису з боку CPU та GPU у керовану пам'ять (`cudaMallocManaged`) без попередньої явної синхронізації `cudaStreamSynchronize()` та виклику `cudaMemPrefetchAsync()`.
4. **Утилізація пулу `cudaMallocAsync`**: Для короткоживучих проміжних буферів усередині циклу ітерацій завжди віддавайте перевагу `cudaMallocAsync` перед `cudaMalloc`, оскільки це усуває глобальні блокування драйвера та скорочує час виділення з мікросекунд до десятків наносекунд.
