# ⚙️ Асинхронний конвеєр пересилок і подвійна буферизація в CUDA

Коли обчислювальна задача опрацьовує масив даних, що надходить неперервним потоком або перевищує розмір кешів відеокарти, наївний синхронний підхід призводить до катастрофічного падіння утилізації заліза. Якщо програма послідовно виконує виділення, копіювання `Host-to-Device`, запуск ядра та копіювання `Device-to-Host`, шина PCIe та обчислювальні ядра графічного процесора почергово простоюють більшу частину часу.

## Задача: усунення простою через конвеєризацію

Нехай потрібно опрацювати `N` порцій даних (тайлів або кадрів). Для кожної порції необхідно виконати три послідовні стадії:
1. `H2D`: передати вхідний буфер із оперативної пам'яті хоста у відеопам'ять GPU через системну шину PCIe;
2. `Kernel`: виконати масивно-паралельні обчислення на потокових мультипроцесорах (SM);
3. `D2H`: скопіювати отриманий результат назад у системну пам'ять хоста.

За послідовного синхронного виконання загальний час обробки `N` порцій складається з простої суми часів кожного етапу для кожного блока:

```
T_sync = N · (T_h2d + T_kernel + T_d2h)
```

Сучасний графічний процесор містить у кремнії **три незалежні апаратні рушії**, здатні працювати абсолютно одночасно:
- апаратний рушій DMA для копіювання з Host у Device (`H2D DMA Engine`);
- апаратний рушій DMA для копіювання з Device у Host (`D2H DMA Engine`);
- обчислювальний масив ядер (мультипроцесори SM та планувальники варпів).

Якщо розбити загальний масив на `K` незалежних блоків і використати окремі черги команд — [потоки CUDA](root:hw-arch/gpu-host-device-memory/api-memory-management.md) (*CUDA Streams*), — ми можемо організувати класичний тристадійний конвеєр. Поки рушій `D2H` повертає результати порції `i-1`, обчислювальні ядра рахують порцію `i`, а рушій `H2D` завантажує порцію `i+1`.

```
T_pipeline = T_h2d + T_kernel + (N - 1) · max(T_h2d, T_kernel, T_d2h) + T_d2h
```

Якщо час обчислення переважає час пересилки (`T_kernel ≥ T_h2d`), передача даних через PCIe стає повністю «безкоштовною» за часом, оскільки вона цілком ховається за роботою мультипроцесорів.

## Апаратна анатомія трьох стадій конвеєра

Щоб зрозуміти, чому конвеєризація вимагає спеціальної організації пам'яті, розглянемо поведінку контролерів на кристалі прискорювача під час проходження трьох фаз:

1. **Фаза прологу (Prologue)**: Перша порція даних `Chunk 0` завантажується через `H2D DMA Engine`. Обчислювальні ядра та рушій `D2H` у цей момент ще не мають даних і очікують.
2. **Стаціонарна фаза (Steady State)**: Конвеєр повністю заповнений. Усі три кремнієві блоки працюють паралельно:
   - `H2D DMA Engine` прокачує байти порції `k + 1` через лінії PCIe;
   - `Streaming Multiprocessors (SM)` виконують математичні інструкції над порцією `k` у локальній пам'яті VRAM;
   - `D2H DMA Engine` відправляє обчислені результати порції `k - 1` назад у системне ОЗП.
3. **Фаза епілогу (Epilogue)**: Усі вхідні дані завантажені. Рушій `H2D` завершує роботу, обчислювальні ядра дораховують останній блок, а рушій `D2H` вивантажує фінальні результати.

```
Час --->
H2D Engine:   [ H2D 0 ][ H2D 1 ][ H2D 2 ][ H2D 3 ] ...
Compute SMs:           [ Knl 0 ][ Knl 1 ][ Knl 2 ][ Knl 3 ] ...
D2H Engine:                     [ D2H 0 ][ D2H 1 ][ D2H 2 ][ D2H 3 ]
              |<-Пролог| <----- Стаціонарний режим -----> | Епілог ->|
```

## Подвійна буферизація проти потрійної буферизації

Для організації конвеєра на боці пристрою виділяють кілька наборів буферів:

**Подвійна буферизація (Double Buffering — 2 набори буферів)**:
Використовує два чергові буфери у VRAM: `Buffer A` та `Buffer B`. Поки потік 0 обчислює дані в `Buffer A`, потік 1 завантажує наступну порцію в `Buffer B`. Ця схема чудово перекриває завантаження з обчисленням (`H2D || Compute`), однак рушій зворотного вивантаження `D2H` змушений ділити час із завантаженням `H2D`, якщо шина PCIe перевантажена або якщо час обчислення набагато коротший за час пересилки.

**Потрійна буферизація (Triple Buffering — 3 набори буферів / Ring Buffer)**:
Використовує кільцевий масив із трьох буферів у VRAM (`Buffer 0`, `Buffer 1`, `Buffer 2`) та три незалежні потоки CUDA. Це дозволяє досягти теоретичного максимуму апаратного перекриття:
- Буфер 0: обробляється рушієм `D2H DMA` (вивантаження попереднього результату);
- Буфер 1: обробляється мультипроцесорами `SM` (поточні обчислення);
- Буфер 2: обробляється рушієм `H2D DMA` (завантаження наступного вхідного блоку).

Ця організація гарантує, що жоден з апаратних блоків не блокує інші через брак тимчасового простору у відеопам'яті.

## Апаратна еволюція черг: від єдиної черги Fermi до Hyper-Q

У ранніх поколіннях графічних процесорів (архітектура NVIDIA Fermi) усі потоки користувача на апаратному рівні мультиплексувалися в одну-єдину фізичну чергу команд. Це створювало так звану **фальшиву залежність** (*false dependency*): якщо в потік 0 ставилося обчислювальне ядро, а в потік 1 — копіювання пам'яті, драйвер не міг запустити копіювання раніше, ніж ядро звільнить чергу.

Починаючи з архітектури Kepler та Pascal, у кремній було впроваджено технологію **Hyper-Q**. Вона реалізує до 32 або 64 повністю незалежних апаратних черг на рівні чипа. Завдяки Hyper-Q кожна команда з окремого об'єкта `cudaStream_t` потрапляє у власну фізичну чергу диспетчера хоста (*Host Interface Queue*). Диспетчер відеокарти аналізує готовність рушіїв у реальному часі й запускає операції різних потоків безпосередньо у відповідні вільні функціональні блоки без жодних програмних затримок.

## Математичний баланс обчислень та передачі (Roofline Analysis)

Для визначення того, скільки потоків і буферів потрібно створити, слід обчислити співвідношення між часом передачі `T_transfer = T_h2d + T_d2h` та часом роботи обчислювального ядра `T_kernel`:

1. **Якщо `T_kernel > T_transfer` (Compute-bound режим)**:
   Обчислення тривають довше за пересилку. Тут достатньо класичної подвійної буферизації (`NUM_STREAMS = 2`). Передача даних через шину PCIe повністю сховається за обчисленнями.
2. **Якщо `T_transfer > T_kernel` (Memory-bound / PCIe-bound режим)**:
   Шина PCIe є найповільнішою ланкою. Навіть ідеальний конвеєр не зможе завантажити мультипроцесори на 100%, оскільки ядра закінчуватимуть роботу раніше, ніж рушій DMA доставить наступну порцію даних. У цьому разі слід збільшувати розмір порції або застосовувати стиснення даних перед передачею.

## Апаратні вимоги до коду

Щоб перекриття спрацювало на рівні заліза, мають одночасно виконуватися три обов'язкові умови:
1. **Фіксована пам'ять хоста (Pinned Host Memory)**: виділена функцією `cudaHostAlloc()` або `cudaMallocHost()`. Звичайна пам'ять (`malloc`) змушує драйвер виконувати синхронне копіювання через проміжний буфер ядра, що руйнує асинхронність.
2. **Асинхронні виклики `cudaMemcpyAsync()`**: прив'язані до явних користувацьких потоків `cudaStream_t`.
3. **Нетипові потоки без прапорця синхронізації**: створені через `cudaStreamCreateWithFlags(&stream, cudaStreamNonBlocking)`, що запобігає неявній синхронізації з головним потоком (Stream 0).

Нижче наведено повну реалізацію подвійної буферизації мовами C та C++.

## Реалізація конвеєра з подвійною буферизацією

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <cuda_runtime.h>

#define CHUNK_SIZE (1024 * 1024)   /* 1M елементів на порцію (4 МБ) */
#define NUM_CHUNKS 8               /* Кількість порцій */
#define NUM_STREAMS 2              /* Подвійна буферизація: 2 потоки */

/* Макрос для обробки помилок CUDA API */
#define CUDA_CHECK(call) do { \
    cudaError_t err = (call); \
    if (err != cudaSuccess) { \
        fprintf(stderr, "CUDA помилка %s:%d: %s\n", \
                __FILE__, __LINE__, cudaGetErrorString(err)); \
        exit(EXIT_FAILURE); \
    } \
} while (0)

/* Обчислювальне ядро: зважене масштабування масиву */
__global__ void process_kernel(const float *in, float *out, float scale, int n) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idx < n) {
        float val = in[idx];
        /* Інтенсивне обчислювальне навантаження для демонстрації перекриття */
        #pragma unroll
        for (int i = 0; i < 64; ++i) {
            val = val * scale + 0.001f;
        }
        out[idx] = val;
    }
}

int main(void) {
    size_t total_elements = (size_t)CHUNK_SIZE * NUM_CHUNKS;
    size_t chunk_bytes = (size_t)CHUNK_SIZE * sizeof(float);
    size_t total_bytes = total_elements * sizeof(float);

    /* 1. Виділення фіксованої (Pinned) пам'яті на хості */
    float *h_in = NULL;
    float *h_out = NULL;
    CUDA_CHECK(cudaHostAlloc((void **)&h_in, total_bytes, cudaHostAllocDefault));
    CUDA_CHECK(cudaHostAlloc((void **)&h_out, total_bytes, cudaHostAllocDefault));

    /* Ініціалізація вхідних даних */
    for (size_t i = 0; i < total_elements; ++i) {
        h_in[i] = (float)(i % 100) * 0.01f;
    }

    /* 2. Виділення подвійних буферів на пристрої (по одному на потік) */
    float *d_in[NUM_STREAMS];
    float *d_out[NUM_STREAMS];
    for (int s = 0; s < NUM_STREAMS; ++s) {
        CUDA_CHECK(cudaMalloc((void **)&d_in[s], chunk_bytes));
        CUDA_CHECK(cudaMalloc((void **)&d_out[s], chunk_bytes));
    }

    /* 3. Створення неблокуючих потоків CUDA */
    cudaStream_t streams[NUM_STREAMS];
    for (int s = 0; s < NUM_STREAMS; ++s) {
        CUDA_CHECK(cudaStreamCreateWithFlags(&streams[s], cudaStreamNonBlocking));
    }

    /* Створення подій для точного апаратного профілювання */
    cudaEvent_t start_evt, stop_evt;
    CUDA_CHECK(cudaEventCreate(&start_evt));
    CUDA_CHECK(cudaEventCreate(&stop_evt));

    dim3 block(256);
    dim3 grid((CHUNK_SIZE + block.x - 1) / block.x);

    CUDA_CHECK(cudaEventRecord(start_evt, 0));

    /* 4. Головний конвеєрний цикл */
    for (int i = 0; i < NUM_CHUNKS; ++i) {
        int stream_idx = i % NUM_STREAMS;
        size_t offset = (size_t)i * CHUNK_SIZE;

        /* Асинхронне копіювання вхідної порції: Host -> Device */
        CUDA_CHECK(cudaMemcpyAsync(d_in[stream_idx],
                                   h_in + offset,
                                   chunk_bytes,
                                   cudaMemcpyHostToDevice,
                                   streams[stream_idx]));

        /* Запуск обчислювального ядра в тому самому потоці */
        process_kernel<<<grid, block, 0, streams[stream_idx]>>>(
            d_in[stream_idx], d_out[stream_idx], 1.002f, CHUNK_SIZE
        );

        /* Асинхронне копіювання результатів: Device -> Host */
        CUDA_CHECK(cudaMemcpyAsync(h_out + offset,
                                   d_out[stream_idx],
                                   chunk_bytes,
                                   cudaMemcpyDeviceToHost,
                                   streams[stream_idx]));
    }

    /* 5. Очікування завершення всіх операцій в усіх потоках */
    for (int s = 0; s < NUM_STREAMS; ++s) {
        CUDA_CHECK(cudaStreamSynchronize(streams[s]));
    }

    CUDA_CHECK(cudaEventRecord(stop_evt, 0));
    CUDA_CHECK(cudaEventSynchronize(stop_evt));

    float elapsed_ms = 0.0f;
    CUDA_CHECK(cudaEventElapsedTime(&elapsed_ms, start_evt, stop_evt));
    printf("Конвеєрна обробка %d МБ завершена за %.2f мс\n",
           (int)(total_bytes / (1024 * 1024)), elapsed_ms);

    /* 6. Звільнення ресурсів */
    for (int s = 0; s < NUM_STREAMS; ++s) {
        CUDA_CHECK(cudaStreamDestroy(streams[s]));
        CUDA_CHECK(cudaFree(d_in[s]));
        CUDA_CHECK(cudaFree(d_out[s]));
    }
    CUDA_CHECK(cudaEventDestroy(start_evt));
    CUDA_CHECK(cudaEventDestroy(stop_evt));
    CUDA_CHECK(cudaFreeHost(h_in));
    CUDA_CHECK(cudaFreeHost(h_out));

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <span>
#include <stdexcept>
#include <string>
#include <format>
#include <cuda_runtime.h>

/* Безпечна обгортка перевірки помилок CUDA через винятки */
inline void check_cuda(cudaError_t result, const char *msg) {
    if (result != cudaSuccess) {
        throw std::runtime_error(std::string(msg) + ": " + cudaGetErrorString(result));
    }
}

/* RAII-керування потоком CUDA */
class CudaStream {
public:
    CudaStream() {
        check_cuda(cudaStreamCreateWithFlags(&stream_, cudaStreamNonBlocking),
                   "Не вдалося створити cudaStream");
    }
    ~CudaStream() noexcept {
        if (stream_) {
            cudaStreamDestroy(stream_);
        }
    }
    CudaStream(const CudaStream&) = delete;
    CudaStream& operator=(const CudaStream&) = delete;
    CudaStream(CudaStream&& other) noexcept : stream_(other.stream_) {
        other.stream_ = nullptr;
    }
    CudaStream& operator=(CudaStream&& other) noexcept {
        if (this != &other) {
            if (stream_) cudaStreamDestroy(stream_);
            stream_ = other.stream_;
            other.stream_ = nullptr;
        }
        return *this;
    }

    [[nodiscard]] cudaStream_t get() const noexcept { return stream_; }
    void synchronize() const {
        check_cuda(cudaStreamSynchronize(stream_), "Помилка синхронізації потоку");
    }

private:
    cudaStream_t stream_{nullptr};
};

/* RAII-буфер зафіксованої пам'яті хоста (Pinned Host Memory) */
template <typename T>
class PinnedBuffer {
public:
    explicit PinnedBuffer(size_t count) : count_(count) {
        check_cuda(cudaHostAlloc(reinterpret_cast<void**>(&ptr_),
                                 count_ * sizeof(T),
                                 cudaHostAllocDefault),
                   "Помилка виділення Pinned пам'яті");
    }
    ~PinnedBuffer() noexcept {
        if (ptr_) {
            cudaFreeHost(ptr_);
        }
    }
    PinnedBuffer(const PinnedBuffer&) = delete;
    PinnedBuffer& operator=(const PinnedBuffer&) = delete;
    PinnedBuffer(PinnedBuffer&& other) noexcept : ptr_(other.ptr_), count_(other.count_) {
        other.ptr_ = nullptr;
        other.count_ = 0;
    }
    PinnedBuffer& operator=(PinnedBuffer&& other) noexcept {
        if (this != &other) {
            if (ptr_) cudaFreeHost(ptr_);
            ptr_ = other.ptr_;
            count_ = other.count_;
            other.ptr_ = nullptr;
            other.count_ = 0;
        }
        return *this;
    }

    [[nodiscard]] T* data() noexcept { return ptr_; }
    [[nodiscard]] const T* data() const noexcept { return ptr_; }
    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] size_t bytes() const noexcept { return count_ * sizeof(T); }
    [[nodiscard]] std::span<T> span() noexcept { return std::span<T>(ptr_, count_); }

private:
    T* ptr_{nullptr};
    size_t count_{0};
};

/* RAII-буфер пам'яті пристрою (Device VRAM) */
template <typename T>
class DeviceBuffer {
public:
    explicit DeviceBuffer(size_t count) : count_(count) {
        check_cuda(cudaMalloc(reinterpret_cast<void**>(&ptr_), count_ * sizeof(T)),
                   "Помилка виділення VRAM пам'яті");
    }
    ~DeviceBuffer() noexcept {
        if (ptr_) {
            cudaFree(ptr_);
        }
    }
    DeviceBuffer(const DeviceBuffer&) = delete;
    DeviceBuffer& operator=(const DeviceBuffer&) = delete;
    DeviceBuffer(DeviceBuffer&& other) noexcept : ptr_(other.ptr_), count_(other.count_) {
        other.ptr_ = nullptr;
        other.count_ = 0;
    }
    DeviceBuffer& operator=(DeviceBuffer&& other) noexcept {
        if (this != &other) {
            if (ptr_) cudaFree(ptr_);
            ptr_ = other.ptr_;
            count_ = other.count_;
            other.ptr_ = nullptr;
            other.count_ = 0;
        }
        return *this;
    }

    [[nodiscard]] T* data() noexcept { return ptr_; }
    [[nodiscard]] const T* data() const noexcept { return ptr_; }
    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] size_t bytes() const noexcept { return count_ * sizeof(T); }

private:
    T* ptr_{nullptr};
    size_t count_{0};
};

/* Ядро CUDA */
__global__ void process_kernel_cpp(const float *in, float *out, float scale, int n) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idx < n) {
        float val = in[idx];
        #pragma unroll
        for (int i = 0; i < 64; ++i) {
            val = val * scale + 0.001f;
        }
        out[idx] = val;
    }
}

int main() {
    try {
        constexpr size_t chunk_size = 1024 * 1024;
        constexpr size_t num_chunks = 8;
        constexpr size_t num_streams = 2;
        constexpr size_t total_elements = chunk_size * num_chunks;

        /* Виділення фіксованих буферів хоста з автоматичним вивільненням */
        PinnedBuffer<float> host_in(total_elements);
        PinnedBuffer<float> host_out(total_elements);

        auto in_span = host_in.span();
        for (size_t i = 0; i < in_span.size(); ++i) {
            in_span[i] = static_cast<float>(i % 100) * 0.01f;
        }

        /* Створення масиву подвійних буферів та потоків */
        std::vector<DeviceBuffer<float>> dev_in;
        std::vector<DeviceBuffer<float>> dev_out;
        std::vector<CudaStream> streams;

        dev_in.reserve(num_streams);
        dev_out.reserve(num_streams);
        streams.reserve(num_streams);

        for (size_t s = 0; s < num_streams; ++s) {
            dev_in.emplace_back(chunk_size);
            dev_out.emplace_back(chunk_size);
            streams.emplace_back();
        }

        dim3 block(256);
        dim3 grid((chunk_size + block.x - 1) / block.x);

        /* Конвеєрний запуск */
        for (size_t i = 0; i < num_chunks; ++i) {
            size_t s = i % num_streams;
            size_t offset = i * chunk_size;

            check_cuda(cudaMemcpyAsync(dev_in[s].data(),
                                       host_in.data() + offset,
                                       chunk_size * sizeof(float),
                                       cudaMemcpyHostToDevice,
                                       streams[s].get()),
                       "H2D копіювання зазнало невдачі");

            process_kernel_cpp<<<grid, block, 0, streams[s].get()>>>(
                dev_in[s].data(), dev_out[s].data(), 1.002f, static_cast<int>(chunk_size)
            );

            check_cuda(cudaMemcpyAsync(host_out.data() + offset,
                                       dev_out[s].data(),
                                       chunk_size * sizeof(float),
                                       cudaMemcpyDeviceToHost,
                                       streams[s].get()),
                       "D2H копіювання зазнало невдачі");
        }

        /* Синхронізація потоків */
        for (auto &stream : streams) {
            stream.synchronize();
        }

        std::cout << "C++ RAII конвеєрна обробка успішно завершена.\n";

    } catch (const std::exception &ex) {
        std::cerr << "Критична помилка: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
```
:::

## Синхронізація між потоками без участі CPU (CUDA Events)

У складних графах обчислень одна частина конвеєра може залежати від результатів іншого потоку. Якщо для координації викликати `cudaStreamSynchronize()` або `cudaDeviceSynchronize()`, центральний процесор заблокується, що зруйнує конвеєр.

Для неблокуючої координації на апаратному рівні застосовують **події CUDA (CUDA Events)**:

:::tabs
```c
/* Координація потоків на GPU без блокування центрального процесора */
cudaEvent_t compute_ready;
cudaEventCreateWithFlags(&compute_ready, cudaEventDisableTiming);

/* Потік 0 завершує обчислення і записує подію в апаратний таймлайн */
kernel_stage1<<<grid, block, 0, stream0>>>(d_buf0);
cudaEventRecord(compute_ready, stream0);

/* Потік 1 починає залежну операцію ТІЛЬКИ після спрацювання події */
cudaStreamWaitEvent(stream1, compute_ready, 0);
kernel_stage2<<<grid, block, 0, stream1>>>(d_buf0, d_buf1);

/* CPU вільний і продовжує виконувати фонову логіку */
```
```cpp
/* C++ RAII-обгортка для подій CUDA */
#include <cuda_runtime.h>
#include <stdexcept>

class CudaEvent {
public:
    explicit CudaEvent(unsigned int flags = cudaEventDisableTiming) {
        if (cudaEventCreateWithFlags(&event_, flags) != cudaSuccess) {
            throw std::runtime_error("cudaEventCreate failed");
        }
    }
    ~CudaEvent() noexcept {
        if (event_) cudaEventDestroy(event_);
    }
    void record(cudaStream_t stream) {
        cudaEventRecord(event_, stream);
    }
    void wait_in_stream(cudaStream_t stream) {
        cudaStreamWaitEvent(stream, event_, 0);
    }
    [[nodiscard]] cudaEvent_t get() const noexcept { return event_; }

private:
    cudaEvent_t event_{nullptr};
};
```
:::

Виклик `cudaStreamWaitEvent()` змушує апаратний планувальник прискорювача затримати виконання команд у черзі `stream1` до моменту, поки черга `stream0` не дійде до точки запису події `compute_ready`. При цьому центральний процесор взагалі не бере участі в очікуванні й продовжує планування наступних кадрів.

## Керування пріоритетами потоків (Stream Priorities)

Сучасні графічні процесори NVIDIA підтримують багаторівневе пріоритетне планування черг команд. За замовчуванням усі потоки мають однаковий пріоритет (числове значення `0`). Однак у чутливих до затримок застосунках (наприклад, інтерактивний рендеринг або алгоритми високочастотної торгівлі HFT) вивантаження критичних результатів має відбуватися негайно, не чекаючи завершення фонових обчислень.

Функція `cudaStreamCreateWithPriority()` дозволяє створити потік із підвищеним пріоритетом. Діапазон підтримуваних значень опитується викликом `cudaDeviceGetStreamPriorityRange()`. Робота, поставлена у високопріоритетний потік, витісняє варпи низькопріоритетних потоків у планувальниках мультипроцесорів SM, гарантуючи мінімальний час відгуку системи.

## Керування утриманням даних у кеші L2 (L2 Cache Persistence)

Починаючи з архітектури NVIDIA Ampere, у кремній впроваджено апаратний механізм прямого керування резидентністю кешу L2 (*L2 Cache Residency Control*). Якщо вихідний буфер порції `k` після обчислення ядра має бути негайно прочитаний ядром наступної стадії конвеєра, його скидання у відносно повільну VRAM створює зайвий енергетичний та часовий оверхед.

Викликом `cudaStreamSetL2PersistenceWindow()` програма може виділити вікно кешу L2 (наприклад, 8 МБ або 16 МБ) і закріпити в ньому покажчики активних буферів конвеєра. Планувальник кешу GPU гарантує, що рядки цих адрес не витіснятимуться сторонніми транзакціями до завершення роботи конвеєра, дозволяючи проміжним стадіям обмінюватися даними на швидкості понад 5 ТБ/с безпосередньо через кристал.

## Оптимізація запуску конвеєра через графи CUDA (CUDA Graphs Capture)

Якщо конвеєр виконується в неперервному циклі з мільйонами ітерацій (наприклад, обробка потоку кадрів із камери), затримки драйвера CPU на виклик кожної окремої функції `cudaMemcpyAsync` та конфігурації ядра можуть складати значну частку загального часу кадру.

Для повної ліквідації накладних витрат процесора застосовують **захоплення потоку в граф обчислень (Stream Capture)**:

:::tabs
```c
/* C: захоплення та створення виконуваного графа */
cudaGraph_t graph;
cudaGraphExec_t instance;

cudaStreamBeginCapture(stream, cudaStreamCaptureModeGlobal);
/* Виклики асинхронного конвеєра записуються в граф без виконання */
cudaMemcpyAsync(d_in, h_in, size, cudaMemcpyHostToDevice, stream);
process_kernel<<<grid, block, 0, stream>>>(d_in, d_out, 1.0f, n);
cudaMemcpyAsync(h_out, d_out, size, cudaMemcpyDeviceToHost, stream);
cudaStreamEndCapture(stream, &graph);

/* Інстанціювання оптимізованого графа */
cudaGraphInstantiate(&instance, graph, NULL, NULL, 0);

/* Багаторазовий миттєвий запуск без участі драйвера CPU */
for (int frame = 0; frame < 10000; ++frame) {
    cudaGraphLaunch(instance, stream);
}
```
```cpp
/* C++: RAII-обгортка виконуваного графа CUDA */
#include <cuda_runtime.h>
#include <stdexcept>

class CudaGraphExecutor {
public:
    explicit CudaGraphExecutor(cudaGraph_t graph) {
        if (cudaGraphInstantiate(&instance_, graph, nullptr, nullptr, 0) != cudaSuccess) {
            throw std::runtime_error("cudaGraphInstantiate failed");
        }
    }
    ~CudaGraphExecutor() noexcept {
        if (instance_) cudaGraphExecDestroy(instance_);
    }
    void launch(cudaStream_t stream) {
        cudaGraphLaunch(instance_, stream);
    }

private:
    cudaGraphExec_t instance_{nullptr};
};
```
:::

## Наскрізний мережевий конвеєр (GPUDirect RDMA)

У високопродуктивних обчислювальних кластерах та розподіленому навчанні нейромереж конвеєр не обмежується парою CPU–GPU. Дані надходять із мережевих адаптерів InfiniBand або RoCE безпосередньо у відеопам'ять прискорювача.

Технологія GPUDirect RDMA дозволяє мережевій карті NIC виконувати прямі операції читання та запису у VRAM графічного процесора через шину PCIe. У цьому режимі конвеєр набуває вигляду:
1. `NIC RDMA Read`: надходження пакета з мережі прямо у буфер VRAM `d_in[s]`;
2. `Compute Kernel`: обробка матриць ядрами GPU;
3. `NIC RDMA Write`: пряме вивантаження результату `d_out[s]` у мережу до сусіднього вузла кластера.

Організація подвійної буферизації в такому конвеєрі усуває будь-яке копіювання через оперативну пам'ять хоста і вивільняє центральний процесор для фонової координації вузлів.

## Розмітка фаз конвеєра через NVTX (NVIDIA Tools Extension)

Для наочного відображення роботи конвеєра в системних профілювальниках застосовують бібліотеку маркування **NVTX**. Розмітка кожної стадії кольоровими діапазонами дозволяє в графічному інтерфейсі Nsight Systems чітко бачити межі прологу, стаціонарного режиму та епілогу:

:::tabs
```c
/* C: розмітка стадій конвеєра за допомогою NVTX */
#include <nvtx3/nvToolsExt.h>

void trace_chunk_execution(int chunk_id, cudaStream_t stream) {
    nvtxRangePushA("Pipeline_Stage_H2D");
    /* Асинхронне копіювання */
    nvtxRangePop();

    nvtxRangePushA("Pipeline_Stage_Compute");
    /* Запуск ядра */
    nvtxRangePop();
}
```
```cpp
/* C++: RAII-обгортка діапазону NVTX */
#include <nvtx3/nvToolsExt.h>

class NvtxScope {
public:
    explicit NvtxScope(const char* name) {
        nvtxRangePushA(name);
    }
    ~NvtxScope() noexcept {
        nvtxRangePop();
    }
    NvtxScope(const NvtxScope&) = delete;
    NvtxScope& operator=(const NvtxScope&) = delete;
};
```
:::

## Аналіз конвеєра через профілювальник NVIDIA Nsight Systems

Щоб переконатися, що конвеєр справді функціонує в режимі апаратного перекриття, застосовують системний профілювальник **NVIDIA Nsight Systems** (`nsys`). 

Запуск профілювання виконується командним рядком:

```bash
nsys profile --trace=cuda,nvtx --output=pipeline_report ./pipeline_app
```

При відкритті створеного звіту в графічному інтерфейсі слід звернути увагу на таймлайн апаратних черг:

```
[CUDA Hardware Timeline]
Stream 13:   |-- Memcpy H2D (Chunk 0) --|-- Kernel 0 --|-- Memcpy D2H (Chunk 0) --|
Stream 14:               |-- Memcpy H2D (Chunk 1) --|-- Kernel 1 --|-- Memcpy D2H (Chunk 1) --|
Memory Engines:
  [H2D DMA Engine] : [===== Chunk 0 =====][===== Chunk 1 =====][===== Chunk 2 =====]
  [Compute SMs]    :                      [===== Kernel 0 =====][===== Kernel 1 =====]
  [D2H DMA Engine] :                                            [===== Chunk 0 =====]
```

Ознакою коректно налаштованого конвеєра є **безперервна заповненість обчислювального блоку (Compute SMs)**: між закінченням `Kernel 0` та початком `Kernel 1` не повинно бути порожніх проміжків (бульбашок конвеєра, англ. *pipeline bubbles*).

## Конфігурація операційної системи під максимальну пропускну здатність

Навіть ідеально написаний код конвеєра може втратити до 40% продуктивності через неоптимальні налаштування операційної системи хоста. Для досягнення граничної швидкості передачі по шині PCIe рекомендується виконати наступні системні кроки:

1. **Вимкнення енергозберігаючих станів PCIe (PCIe ASPM)**:
   Механізм Active State Power Management переводить лінії PCIe у стан сну при відсутності активності. Вихід із низькоенергетичного стану L0s/L1 додає кілька мікросекунд затримки на кожну транзакцію. У конфігурації завантажувача Linux додають параметр ядра `pcie_aspm=off`.
2. **Встановлення профілю максимальної продуктивності CPU**:
   Динамічне масштабування частоти ядер хоста через регулятор `powersave` призводить до затримок постановки задач у чергу драйвера. Переведення в режим максимальної швидкості виконується командою `cpupower frequency-set -g performance`.
3. **Збільшення ліміту блокування пам'яті (memlock)**:
   За замовчуванням операційна система Linux обмежує обсяг пам'яті, яку звичайний користувач може зафіксувати через `mlock`/`cudaHostAlloc` (параметр `ulimit -l`). У файлі конфігурації `/etc/security/limits.conf` слід встановити необмежений ліміт `* hard memlock unlimited` та `* soft memlock unlimited`.

## Багатопристроєвий конвеєр (Multi-GPU Pipeline Parallelism)

У промислових системах обробки великих мовних моделей або високошвидкісного потокового відеопотоку обчислення розподіляються між кількома відеокартами. У таких системах конвеєр організується за схемою прямого передавання між пристроями:

```
Host RAM 
  --[PCIe DMA H2D]--> VRAM GPU 0 
  --[Обчислення Стадії 1 (SM)]-->
  --[P2P DMA через NVLink]--> VRAM GPU 1 
  --[Обчислення Стадії 2 (SM)]-->
  --[PCIe DMA D2H]--> Host RAM
```

Завдяки технології GPUDirect P2P передача результатів проміжної стадії з GPU 0 на GPU 1 виконується викликом `cudaMemcpyPeerAsync()`. Вона відбувається безпосередньо через міст NVLink або комутатор PCIe без будь-якого копіювання в оперативну пам'ять процесора хоста, що зберігає пропускну здатність системної шини.

## Оптимізація заповнюваності мультипроцесорів (Occupancy & Block Tuning)

Під час налаштування конвеєра критично правильно обрати розмір блоку ниток `dim3 block`. Якщо ядро використовує занадто багато регістрів на нитку або занадто великий обсяг розділюваної пам'яті (Shared Memory), кількість активних варпів на мультипроцесорі різко падає. Утиліта API `cudaOccupancyMaxActiveBlocksPerMultiprocessor()` дозволяє в рантаймі визначити теоретичну заповнюваність пристрою (*Occupancy*) та динамічно розрахувати оптимальну конфігурацію сітки. Для досягнення повного перекриття передач та обчислень рекомендується підтримувати рівень теоретичної заповнюваності не менше 50–75%, щоб планувальник варпів міг приховувати затримки доступу до локальної пам'яті VRAM під час роботи паралельних рушіїв DMA.

## Підводні камені та типові помилки конвеєризації

Під час реалізації асинхронних конвеєрів розробники найчастіше припускаються чотирьох типових помилок, що руйнують паралелізм:

1. **Неявна синхронізація через типовий потік (Default Stream / Null Stream)**:
   Якщо будь-яка частина програми запускає ядро чи передачу в типовий потік без прапорця `cudaStreamNonBlocking`, драйвер CUDA зупиняє виконання операцій в *усіх* інших активних потоках пристрою до моменту завершення команди в нульовому потоці.

2. **Неправильний порядок постановки задач у чергу (Issue Order)**:
   Якщо замість циклу з почерговим чергуванням команд `(H2D[0], Kernel[0], D2H[0], H2D[1], Kernel[1], D2H[1])` помилково згрупувати виклики за фазами, конвеєр розпадається на три монолітні блоки:

:::tabs
```c
/* ПОМИЛКА: фазове групування руйнує асинхронний конвеєр */
for (int i = 0; i < N; ++i) {
    cudaMemcpyAsync(d_in[i % 2], h_in + i * S, S * sizeof(float), cudaMemcpyHostToDevice, streams[i % 2]);
}
for (int i = 0; i < N; ++i) {
    kernel<<<grid, block, 0, streams[i % 2]>>>(d_in[i % 2], d_out[i % 2]);
}
for (int i = 0; i < N; ++i) {
    cudaMemcpyAsync(h_out + i * S, d_out[i % 2], S * sizeof(float), cudaMemcpyDeviceToHost, streams[i % 2]);
}
```
```cpp
/* C++ ілюстрація помилкового фазового запуску */
for (size_t i = 0; i < num_chunks; ++i) {
    cudaMemcpyAsync(dev_in[i % 2].data(), host_in.data() + i * chunk_sz, 
                    chunk_sz * sizeof(float), cudaMemcpyHostToDevice, streams[i % 2].get());
}
for (size_t i = 0; i < num_chunks; ++i) {
    process_kernel<<<grid, block, 0, streams[i % 2].get()>>>(dev_in[i % 2].data(), dev_out[i % 2].data());
}
for (size_t i = 0; i < num_chunks; ++i) {
    cudaMemcpyAsync(host_out.data() + i * chunk_sz, dev_out[i % 2].data(), 
                    chunk_sz * sizeof(float), cudaMemcpyDeviceToHost, streams[i % 2].get());
}
```
:::

   Рушій обчислень не зможе почати обробку першої порції, доки черга копіювань не отримає всі команди `H2D`.

3. **Недостатній розмір порції (Tile Size) та накладні витрати запуску**:
   Запуск кожного виклику `cudaMemcpyAsync` та ядра CUDA має програмну затримку постановки команди в чергу драйвера (*Driver Launch Overhead*) порядку 3–5 мікросекунд. Якщо порція даних занадто мала (наприклад, менше 256 КБ), час накладних витрат процесора перевищить час самої передачі по шині PCIe, зведячи нанівець переваги конвеєризації. Оптимальний розмір тайла зазвичай становить від 4 МБ до 64 МБ.

4. **NUMA-дисбаланс вузлів процесора (NUMA Node Affinity)**:
   У двопроцесорних серверах шина PCIe конкретної відеокарти фізично підключена до кореневого комплексу одного з процесорних сокетів (наприклад, Socket 0). Якщо потік керування програми виділяє Pinned Memory на вузлі пам'яті Socket 1, кожен DMA-трансфер змушений долати міжпроцесорну шину (Intel UPI або AMD Infinity Fabric). Це знижує пропускну здатність на 30–50% і збільшує затримки. Прив'язка процесу до правильного NUMA-домену виконується утилітою `numactl --cpunodebind=0 --membind=0 ./app`.
