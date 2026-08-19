# ⚙️ Практичний аналіз дивергенції варпів, коалесцингу та конфліктів банків

Особливість програмування під GPU полягає в тому, що синтаксично коректний код, скомпільований без жодних попереджень, може працювати у 10–50 разів повільніше за теоретичну пропускну здатність заліза. Причина криється в порушенні апаратних інваріантів моделі SIMT: дивергенції потоків усередині варпу, незлитих зверненнях до глобальної пам'яті та конфліктах банків у спільній пам'яті.

Нижче наведено детальний аналіз практичних експериментів, які демонструють природу цих вузьких місць, інструменти їх профілювання, дизасемблювання машинних інструкцій SASS, подвійну буферизацію з асинхронним копіюванням, порозрядне сортування (Radix Sort), бітонічне сортування без розгалужень на базі warp shuffle, 2D реєстрове тайлування матричного множення, векторні транзакції `float4`, двовимірні трафарети з обміном ореолами (halo exchange), перекриття копіювання з обчисленнями через CUDA Streams та високоефективні алгоритми на базі внутрішньоварпових примітивів для мов C і C++.

### Експеримент 1: Дивергенція варпу та безрозгалужені обчислення

Розглянемо задачу обробки масиву, де над кожним елементом виконується важка математична функція `compute_heavy_a()` або `compute_heavy_b()` залежно від умови.

У наївному варіанті гілка вибирається за умовою, яка чергується для кожного сусіднього потоку:

:::tabs
```c
// Наївне ядро з дивергенцією варпу (C)
__global__ void kernel_divergent(const float *in, float *out, int n)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n) return;

    float val = in[idx];
    // Парні потоки йдуть в одну гілку, непарні — в іншу
    if ((threadIdx.x % 2) == 0) {
        val = sinf(val) * cosf(val) + expf(val * 0.1f);
    } else {
        val = sqrtf(fabsf(val)) * logf(fabsf(val) + 1.0f) + 1.0f;
    }
    out[idx] = val;
}
```
```cpp
// Наївне ядро з дивергенцією варпу (C++)
#include <cuda_runtime.h>
#include <cmath>

__global__ void kernel_divergent(const float *in, float *out, int n)
{
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n) {
        return;
    }

    float val = in[idx];
    // Парні потоки йдуть в одну гілку, непарні — в іншу
    if ((threadIdx.x % 2) == 0) {
        val = std::sin(val) * std::cos(val) + std::exp(val * 0.1f);
    } else {
        val = std::sqrt(std::abs(val)) * std::log(std::abs(val) + 1.0f) + 1.0f;
    }
    out[idx] = val;
}
```
:::

У цьому коді кожен варп розпадається на дві групи по 16 потоків. Оскільки лічильник команд (PC) спільний на всі 32 потоки варпу, апаратна частина серіалізує виконання:
1. Спочатку 16 парних потоків рахують `sinf/cosf/expf`, тоді як 16 непарних потоків замасковані й простоюють (ККД = 50%).
2. Потім маска інвертується: 16 непарних потоків рахують `sqrtf/logf`, а 16 парних потоків очікують (ККД = 50%).

Загальний час виконання дорівнює сумі тривалості обох гілок.

#### Аналіз згенерованого асемблера SASS

Поглянемо на машинний код (SASS), який компілятор `nvcc` генерує для умовного переходу всередині ядра:

```
/* 0010 */  ISETP.NE.AND P0, PT, R0, RZ, PT;   // P0 = (threadIdx.x % 2 != 0)
/* 0020 */  @!P0 MUFU.SIN R2, R1;              // Якщо !P0: рахуємо sin (парні потоки)
/* 0030 */  @!P0 MUFU.COS R3, R1;              // Якщо !P0: рахуємо cos (парні потоки)
/* 0040 */  @!P0 FFMA R4, R2, R3, R5;          // Якщо !P0: множимо
/* 0050 */  @P0  MUFU.SQRT R6, R1;             // Якщо P0: рахуємо sqrt (непарні потоки)
/* 0060 */  @P0  MUFU.LG2  R7, R6;             // Якщо P0: рахуємо log
/* 0070 */  @P0  FADD R4, R7, 1.0;             // Якщо P0: додаємо одиницю
```

У дизасемблері чітко видно предикатні прапорці `@P0` та `@!P0`. Інструкції обох гілок розташовані одна за одною в єдиному потоці коду. Конвеєр GPU змушений послідовно пройти всі інструкції від адреси `0020` до `0070`, що призводить до подвоєння часу виконання.

#### Оптимізація: перегрупування на рівні цілих варпів

Якщо умова розгалуження залежить від геометрії обчислень або типу задачі, потоки організують так, щоб усі 32 потоки варпу завжди вибирали однаковий шлях виконання:

:::tabs
```c
// Оптимізоване ядро: поділ на рівні цілих варпів (C)
__global__ void kernel_warp_aligned(const float *in, float *out, int n)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n) return;

    float val = in[idx];
    int warp_id = threadIdx.x / 32;

    // Усі 32 потоки варпу йдуть в одну й ту саму гілку:
    // парні варпи виконують шлях A, непарні — шлях B
    if ((warp_id % 2) == 0) {
        val = sinf(val) * cosf(val) + expf(val * 0.1f);
    } else {
        val = sqrtf(fabsf(val)) * logf(fabsf(val) + 1.0f) + 1.0f;
    }
    out[idx] = val;
}
```
```cpp
// Оптимізоване ядро: поділ на рівні цілих варпів (C++)
#include <cuda_runtime.h>
#include <cmath>

__global__ void kernel_warp_aligned(const float *in, float *out, int n)
{
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n) {
        return;
    }

    float val = in[idx];
    const int warp_id = threadIdx.x / 32;

    // Усі 32 потоки варпу йдуть в одну й ту саму гілку:
    // дивергенція всередині варпу відсутня, ККД виконання = 100%
    if ((warp_id % 2) == 0) {
        val = std::sin(val) * std::cos(val) + std::exp(val * 0.1f);
    } else {
        val = std::sqrt(std::abs(val)) * std::log(std::abs(val) + 1.0f) + 1.0f;
    }
    out[idx] = val;
}
```
:::

У вирівняному варіанті всі 32 потоки одного варпу виконують одну й ту саму гілку. Дивергенція зникає, а час виконання ядра зменшується рівно вдвічі.

### Експеримент 2: Злитий та незлитий доступ до глобальної пам'яті

Розглянемо читання чисел із масиву з різним кроком (англ. *stride*). При кроці `stride = 1` сусідні потоки читають сусідні байти (коалесцинг). При кроці `stride = 32` сусідні потоки читають елементи, рознесені на 128 байтів один від одного:

:::tabs
```c
// Ядро тестування коалесцингу (C)
__global__ void kernel_strided_access(const float *in, float *out, int stride, int n)
{
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    int idx = tid * stride;
    if (idx < n) {
        out[tid] = in[idx] + 1.0f;
    }
}
```
```cpp
// Ядро тестування коалесцингу (C++)
#include <cuda_runtime.h>

__global__ void kernel_strided_access(const float *in, float *out, int stride, int n)
{
    const int tid = blockIdx.x * blockDim.x + threadIdx.x;
    const int idx = tid * stride;
    if (idx < n) {
        out[tid] = in[idx] + 1.0f;
    }
}
```
:::

Вимірювання реальної ефективної пропускної здатності (англ. *effective bandwidth*) на графічному процесорі Nvidia RTX 4090 (теоретична пікова смуга VRAM — 1008 ГБ/с) дає такі результати:

```
Крок (stride)   Транзакцій на варп   Реальна смуга   ККД шини
stride = 1      1 (128 байтів)       840 ГБ/с        83.3%
stride = 2      2 (256 байтів)       430 ГБ/с        42.6%
stride = 4      4 (512 байтів)       220 ГБ/с        21.8%
stride = 8      8 (1024 байти)       112 ГБ/с        11.1%
stride = 32     32 (1024 байти)       32 ГБ/с         3.1%
```

При зростанні кроку до 32 смуга пам'яті деградує у 26 разів. Обчислювальні конвеєри GPU простоюють понад 95% часу, очікуючи на завантаження розкиданих байтів.

### Експеримент 3: Векторизовані транзакції пам'яті через float4

Для насичення шини пам'яті з меншою кількістю активних варпів застосовують векторизовані 128-бітні інструкції завантаження `float4` (машинна інструкція `LDG.E.128`):

:::tabs
```c
// Векторизоване копіювання через float4 (C)
__global__ void copy_vectorized_float4(const float4 *in, float4 *out, int n_float4)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n_float4) {
        // За одне звернення потік вичитує відразу 16 байтів у 4 регістри
        float4 v = in[idx];
        v.x += 1.0f; v.y += 1.0f; v.z += 1.0f; v.w += 1.0f;
        out[idx] = v;
    }
}
```
```cpp
// Векторизоване копіювання через float4 (C++)
#include <cuda_runtime.h>

__global__ void copy_vectorized_float4(const float4 *in, float4 *out, int n_float4)
{
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n_float4) {
        float4 v = in[idx];
        v.x += 1.0f;
        v.y += 1.0f;
        v.z += 1.0f;
        v.w += 1.0f;
        out[idx] = v;
    }
}
```
:::

Використання `float4` зменшує загальну кількість інструкцій вибірки й адресного розрахунку вчетверо, дозволяючи досягти 90%+ пропускної здатності шини VRAM навіть при помірній окупансі мультипроцесора.

### Експеримент 4: Двійкова редукція в спільній пам'яті та shuffle-інструкції

Класична задача паралельної редукції (обчислення суми масиву з 1024 чисел усередині блоку) демонструє еволюцію роботи з пам'яттю на GPU.

#### Варіант А: Редукція з конфліктами банків

У наївному дереві редукції крок збільшується вдвічі на кожній ітерації (`stride = 1, 2, 4, 8, 16`):

:::tabs
```c
// Редукція з конфліктами банків (C)
__global__ void reduce_bank_conflicts(const float *g_in, float *g_out)
{
    __shared__ float sdata[256];
    int tid = threadIdx.x;
    int i = blockIdx.x * blockDim.x + threadIdx.x;

    sdata[tid] = g_in[i];
    __syncthreads();

    // Небезпечний цикл: крок подвоюється, виникають 2-, 4-, 8-кратні конфлікти банків
    for (int s = 1; s < blockDim.x; s *= 2) {
        int index = 2 * s * tid;
        if (index < blockDim.x) {
            sdata[index] += sdata[index + s];
        }
        __syncthreads();
    }

    if (tid == 0) g_out[blockIdx.x] = sdata[0];
}
```
```cpp
// Редукція з конфліктами банків (C++)
#include <cuda_runtime.h>

__global__ void reduce_bank_conflicts(const float *g_in, float *g_out)
{
    __shared__ float sdata[256];
    const int tid = threadIdx.x;
    const int i = blockIdx.x * blockDim.x + threadIdx.x;

    sdata[tid] = g_in[i];
    __syncthreads();

    // Парні індекси б'ють у ті самі банки пам'яті
    for (int s = 1; s < blockDim.x; s *= 2) {
        const int index = 2 * s * tid;
        if (index < blockDim.x) {
            sdata[index] += sdata[index + s];
        }
        __syncthreads();
    }

    if (tid == 0) {
        g_out[blockIdx.x] = sdata[0];
    }
}
```
:::

Коли `s = 2`, потоки 0, 1, 2, 3 звертаються до індексів 0, 4, 8, 12. Коли `s = 16`, потоки звертаються до індексів 0, 32, 64, 96 — усі вони потрапляють у Банк 0, викликаючи 16-кратний конфлікт банків і серіалізацію.

#### Варіант Б: Безконфліктна редукція з чергуванням

Змінивши напрямок згортки на зворотний (крок зменшується вдвічі, потоки працюють послідовно), конфлікти банків повністю усуваються:

:::tabs
```c
// Безконфліктна редукція зі зсувом діапазону (C)
__global__ void reduce_conflict_free(const float *g_in, float *g_out)
{
    __shared__ float sdata[256];
    int tid = threadIdx.x;
    int i = blockIdx.x * blockDim.x + threadIdx.x;

    sdata[tid] = g_in[i];
    __syncthreads();

    // Зворотний крок: потоки з індексами 0..s-1 читають сусідні банки
    for (int s = blockDim.x / 2; s > 0; s >>= 1) {
        if (tid < s) {
            sdata[tid] += sdata[tid + s];
        }
        __syncthreads();
    }

    if (tid == 0) g_out[blockIdx.x] = sdata[0];
}
```
```cpp
// Безконфліктна редукція зі зсувом діапазону (C++)
#include <cuda_runtime.h>

__global__ void reduce_conflict_free(const float *g_in, float *g_out)
{
    __shared__ float sdata[256];
    const int tid = threadIdx.x;
    const int i = blockIdx.x * blockDim.x + threadIdx.x;

    sdata[tid] = g_in[i];
    __syncthreads();

    // Сусідні потоки tid звертаються до сусідніх банків: 1 такт, 0 конфліктів
    for (int s = blockDim.x / 2; s > 0; s >>= 1) {
        if (tid < s) {
            sdata[tid] += sdata[tid + s];
        }
        __syncthreads();
    }

    if (tid == 0) {
        g_out[blockIdx.x] = sdata[0];
    }
}
```
:::

#### Варіант В: Редукція через регістрові інструкції варпу (Warp Shuffle)

Найшвидший спосіб виконання редукції в межах одного варпу (32 потоки) взагалі не використовує спільну пам'ять. Інструкція `__shfl_down_sync` дозволяє потокам одного варпу обмінюватися значеннями регістрів безпосередньо через апаратну комутаційну матрицю за 1 такт:

:::tabs
```c
// Редукція варпу через Shuffle-інструкції (C)
__inline__ __device__ float warp_reduce_sum(float val)
{
    // Маска 0xffffffff означає, що всі 32 потоки беруть участь
    #pragma unroll
    for (int offset = 16; offset > 0; offset /= 2) {
        val += __shfl_down_sync(0xffffffff, val, offset);
    }
    return val;
}

__global__ void reduce_warp_shuffle(const float *g_in, float *g_out)
{
    __shared__ float warp_sums[8]; // До 8 варпів у блоці на 256 потоків
    int tid = threadIdx.x;
    int lane = tid % 32;
    int warp_id = tid / 32;
    int i = blockIdx.x * blockDim.x + threadIdx.x;

    float sum = g_in[i];
    // Крок 1: Редукція всередині кожного варпу через регістри
    sum = warp_reduce_sum(sum);

    // Перший потік кожного варпу записує суму варпу в Shared Memory
    if (lane == 0) {
        warp_sums[warp_id] = sum;
    }
    __syncthreads();

    // Крок 2: Перший варп підсумовує результати всіх варпів
    if (warp_id == 0) {
        float final_sum = (lane < (blockDim.x / 32)) ? warp_sums[lane] : 0.0f;
        final_sum = warp_reduce_sum(final_sum);
        if (lane == 0) {
            g_out[blockIdx.x] = final_sum;
        }
    }
}
```
```cpp
// Редукція варпу через Shuffle-інструкції (C++)
#include <cuda_runtime.h>

__inline__ __device__ float warp_reduce_sum(float val)
{
    constexpr unsigned int active_mask = 0xffffffffU;
    #pragma unroll
    for (int offset = 16; offset > 0; offset /= 2) {
        val += __shfl_down_sync(active_mask, val, offset);
    }
    return val;
}

__global__ void reduce_warp_shuffle(const float *g_in, float *g_out)
{
    __shared__ float warp_sums[8];
    const int tid = threadIdx.x;
    const int lane = tid % 32;
    const int warp_id = tid / 32;
    const int i = blockIdx.x * blockDim.x + threadIdx.x;

    float sum = g_in[i];
    // Регістрова редукція в межах варпу за 5 тактів без Shared Memory
    sum = warp_reduce_sum(sum);

    if (lane == 0) {
        warp_sums[warp_id] = sum;
    }
    __syncthreads();

    if (warp_id == 0) {
        const float final_val = (lane < (blockDim.x / 32)) ? warp_sums[lane] : 0.0f;
        const float total = warp_reduce_sum(final_val);
        if (lane == 0) {
            g_out[blockIdx.x] = total;
        }
    }
}
```
:::

#### Варіант Г: Сучасний підхід на основі C++ Cooperative Groups

У сучасних стандартах CUDA C++ (починаючи з CUDA 9) прямі магічні маски `0xffffffff` та низькорівневі інтринсики замінюють типізованими групами кооперативних потоків (англ. *Cooperative Groups*):

:::tabs
```c
// Редукція через класичні інтринсики (C)
__device__ float reduce_subgroup_c(float val)
{
    for (int mask = 16; mask > 0; mask >>= 1) {
        val += __shfl_xor_sync(0xffffffff, val, mask);
    }
    return val;
}
```
```cpp
// Редукція через Cooperative Groups (C++)
#include <cooperative_groups.h>

namespace cg = cooperative_groups;

__device__ float reduce_subgroup_cpp(cg::thread_block_tile<32> tile, float val)
{
    // Типобезпечний обмін без ручних шістнадцяткових бітових масок
    #pragma unroll
    for (int offset = tile.size() / 2; offset > 0; offset /= 2) {
        val += tile.shfl_down(val, offset);
    }
    return val;
}
```
:::

Порівняння швидкодії трьох алгоритмів редукції для масиву на 64 мільйони елементів:

```
Алгоритм редукції           Час виконання   Пропускна здатність
А: З конфліктами банків     4.82 мс         53.1 ГБ/с
Б: Безконфліктна (SMem)     1.65 мс         155.1 ГБ/с
В: Warp Shuffle (регістри)  0.34 мс         752.9 ГБ/с
```

### Експеримент 5: Префіксна сума (Warp Scan) та фільтрація даних без атоміків

Ще одним класичним примітивом паралельного програмування є **префіксна сума** (англ. *inclusive scan*): кожен потік `i` повинен отримати суму всіх елементів від `0` до `i`.

На GPU цей алгоритм обчислюється всередині варпу за 5 тактів за допомогою інструкції `__shfl_up_sync`:

:::tabs
```c
// Інклюзивний скан варпу на регістрах (C)
__inline__ __device__ float warp_scan_inclusive(float val)
{
    int lane = threadIdx.x % 32;
    #pragma unroll
    for (int offset = 1; offset < 32; offset *= 2) {
        float n = __shfl_up_sync(0xffffffff, val, offset);
        if (lane >= offset) {
            val += n;
        }
    }
    return val;
}
```
```cpp
// Інклюзивний скан варпу на регістрах (C++)
#include <cuda_runtime.h>

__inline__ __device__ float warp_scan_inclusive(float val)
{
    const int lane = threadIdx.x % 32;
    constexpr unsigned int mask = 0xffffffffU;

    #pragma unroll
    for (int offset = 1; offset < 32; offset *= 2) {
        const float n = __shfl_up_sync(mask, val, offset);
        if (lane >= offset) {
            val += n;
        }
    }
    return val;
}
```
:::

Цей примітив дозволяє розв'язати задачу **ущільнення потоку даних** (англ. *stream compaction* — фільтрація масиву за предикатом, наприклад, `val > 0`) без жодної атомарної операції:
1. Кожен потік голосує через `__ballot_sync(0xffffffff, condition)`, отримуючи 32-бітну бітову маску того, які потоки пройшли фільтр.
2. Потік рахує кількість одиниць у масці перед своїм номером за допомогою апаратного підрахунку бітів [popcount](book:programming/popcount) (`__popc(mask & ((1 << lane) - 1))`).
3. Отримане число є точним вихідним індексом у результуючому масиві!
4. Потоки виконують злитий запис результатів у пам'ять без будь-яких блокувань.

### Експеримент 6: Порозрядне сортування варпу (Warp-Level Radix Sort)

Порозрядне сортування (Radix Sort) для цілих 32-бітних чисел є базовим алгоритмом для баз даних і рушіїв просторового пошуку на GPU. Алгоритм розбиває кожне число на 1-бітні або 4-бітні розряди та виконує послідовне стабільне перегрупування потоків без розгалужень:

:::tabs
```c
// 1-бітний крок сортування всередині варпу (C)
__inline__ __device__ unsigned int warp_radix_step_1bit(unsigned int key, int bit_pos)
{
    int lane = threadIdx.x % 32;
    int bit = (key >> bit_pos) & 1;

    // Отримуємо бітову маску потоків з 1 у поточному біті
    unsigned int mask_ones = __ballot_sync(0xffffffff, bit == 1);
    unsigned int mask_zeros = ~mask_ones;

    // Рахуємо позицію потоку серед нулів або одиниць
    int zeros_before = __popc(mask_zeros & ((1U << lane) - 1));
    int ones_before  = __popc(mask_ones & ((1U << lane) - 1));
    int total_zeros  = __popc(mask_zeros);

    int new_lane = (bit == 0) ? zeros_before : (total_zeros + ones_before);

    // Переставляємо значення ключів у варпі
    return __shfl_sync(0xffffffff, key, new_lane);
}
```
```cpp
// 1-бітний крок сортування всередині варпу (C++)
#include <cuda_runtime.h>

__inline__ __device__ unsigned int warp_radix_step_1bit(unsigned int key, int bit_pos)
{
    const int lane = threadIdx.x % 32;
    const unsigned int bit = (key >> bit_pos) & 1U;
    constexpr unsigned int full_mask = 0xffffffffU;

    const unsigned int mask_ones = __ballot_sync(full_mask, bit == 1U);
    const unsigned int mask_zeros = ~mask_ones;

    const int zeros_before = __popc(mask_zeros & ((1U << lane) - 1U));
    const int ones_before  = __popc(mask_ones & ((1U << lane) - 1U));
    const int total_zeros  = __popc(mask_zeros);

    const int new_lane = (bit == 0U) ? zeros_before : (total_zeros + ones_before);

    return __shfl_sync(full_mask, key, new_lane);
}
```
:::

За 32 кроки `warp_radix_step_1bit` варп повністю сортує 32 числа виключно в регістрах. Завдяки операціям `__ballot_sync` та `__popc` алгоритм не містить жодної інструкції розгалуження, забезпечуючи 100% завантаження АЛП.

### Експеримент 7: Бітонічне сортування варпу на регістрах (Bitonic Sort)

Сортування масиву всередині варпу є чудовою ілюстрацією паралелізму без дивергенції. Класичне швидке сортування (Quicksort) викликає катастрофічну дивергенцію на GPU через непередбачувані рекурсивні розгалуження.

Натомість **бітонічна сортувальна мережа** (англ. *Bitonic Sorting Network*) виконує фіксовану послідовність порівнянь і перестановок над парами елементів. За допомогою інструкції `__shfl_xor_sync` 32 потоки варпу сортують 32 числа повністю в регістрах за 15 тактів без жодного звернення до Shared Memory чи VRAM:

:::tabs
```c
// Бітонічне сортування 32 елементів усередині варпу (C)
__inline__ __device__ float warp_bitonic_sort(float val)
{
    int lane = threadIdx.x % 32;

    // Зовнішній цикл за розміром бітонічної послідовності (2, 4, 8, 16, 32)
    #pragma unroll
    for (int k = 2; k <= 32; k *= 2) {
        // Внутрішній цикл злиття
        #pragma unroll
        for (int j = k / 2; j > 0; j /= 2) {
            float other = __shfl_xor_sync(0xffffffff, val, j);
            int dir = ((lane & k) == 0); // Напрямок сортування (за зростанням/спаданням)

            if (dir) {
                if (val > other) val = other;
            } else {
                if (val < other) val = other;
            }
        }
    }
    return val;
}
```
```cpp
// Бітонічне сортування 32 елементів усередині варпу (C++)
#include <cuda_runtime.h>
#include <algorithm>

__inline__ __device__ float warp_bitonic_sort(float val)
{
    const int lane = threadIdx.x % 32;
    constexpr unsigned int mask = 0xffffffffU;

    #pragma unroll
    for (int k = 2; k <= 32; k *= 2) {
        #pragma unroll
        for (int j = k / 2; j > 0; j /= 2) {
            const float other = __shfl_xor_sync(mask, val, j);
            const bool ascending = ((lane & k) == 0);

            if (ascending) {
                val = (val > other) ? other : val;
            } else {
                val = (val < other) ? other : val;
            }
        }
    }
    return val;
}
```
:::

Завдяки оператору `__shfl_xor_sync` обмін значеннями відбувається миттєво між парами потоків, чиї біти індексів різняться в позиції `j`. Порівняння `(val > other)` транслюється компілятором у скалярні предикатні команди вибору мінімуму `FMNMX`, що повністю виключає дивергенцію лічильника команд.

### Експеримент 8: Двовимірне реєстрове тайлування матричного множення (2D Register Tiling)

У високоефективних числових бібліотеках (cuBLAS, CUTLASS) звичайного тайлування в спільну пам'ять недостатньо. Щоб мінімізувати звернення навіть до Shared Memory, кожен потік обчислює мікротайл `4 × 4` елементи результату, тримаючи проміжні акумулятори у власних фізичних регістрах:

:::tabs
```c
// 2D Реєстрове тайлування матричного множення (C)
#define BM 64
#define BN 64
#define BK 8
#define TM 4
#define TN 4

__global__ void matmul_register_tiled(const float *A, const float *B, float *C, int M, int N, int K)
{
    __shared__ float s_A[BM][BK];
    __shared__ float s_B[BK][BN];

    int tx = threadIdx.x % 16;
    int ty = threadIdx.x / 16;

    float r_c[TM][TN] = {0.0f};
    float r_a[TM];
    float r_b[TN];

    for (int bk = 0; bk < K; bk += BK) {
        // Коалесцинг завантаження блоків A та B у Shared Memory
        s_A[ty * TM + 0][tx] = A[(blockIdx.y * BM + ty * TM + 0) * K + bk + tx];
        s_B[ty][tx * TN + 0] = B[(bk + ty) * N + blockIdx.x * BN + tx * TN + 0];
        __syncthreads();

        // Обчислення внутрішнього добутку повністю на регістрах
        #pragma unroll
        for (int dot_idx = 0; dot_idx < BK; ++dot_idx) {
            #pragma unroll
            for (int i = 0; i < TM; ++i) r_a[i] = s_A[ty * TM + i][dot_idx];
            #pragma unroll
            for (int j = 0; j < TN; ++j) r_b[j] = s_B[dot_idx][tx * TN + j];

            #pragma unroll
            for (int i = 0; i < TM; ++i) {
                #pragma unroll
                for (int j = 0; j < TN; ++j) {
                    r_c[i][j] += r_a[i] * r_b[j];
                }
            }
        }
        __syncthreads();
    }

    // Злитий запис 16 елементів результату у VRAM
    #pragma unroll
    for (int i = 0; i < TM; ++i) {
        #pragma unroll
        for (int j = 0; j < TN; ++j) {
            int row = blockIdx.y * BM + ty * TM + i;
            int col = blockIdx.x * BN + tx * TN + j;
            if (row < M && col < N) C[row * N + col] = r_c[i][j];
        }
    }
}
```
```cpp
// 2D Реєстрове тайлування матричного множення (C++)
#include <cuda_runtime.h>

constexpr int BM = 64;
constexpr int BN = 64;
constexpr int BK = 8;
constexpr int TM = 4;
constexpr int TN = 4;

__global__ void matmul_register_tiled(const float *A, const float *B, float *C, int M, int N, int K)
{
    __shared__ float s_A[BM][BK];
    __shared__ float s_B[BK][BN];

    const int tx = threadIdx.x % 16;
    const int ty = threadIdx.x / 16;

    float r_c[TM][TN] = {0.0f};
    float r_a[TM];
    float r_b[TN];

    for (int bk = 0; bk < K; bk += BK) {
        s_A[ty * TM + 0][tx] = A[(blockIdx.y * BM + ty * TM + 0) * K + bk + tx];
        s_B[ty][tx * TN + 0] = B[(bk + ty) * N + blockIdx.x * BN + tx * TN + 0];
        __syncthreads();

        #pragma unroll
        for (int dot_idx = 0; dot_idx < BK; ++dot_idx) {
            #pragma unroll
            for (int i = 0; i < TM; ++i) r_a[i] = s_A[ty * TM + i][dot_idx];
            #pragma unroll
            for (int j = 0; j < TN; ++j) r_b[j] = s_B[dot_idx][tx * TN + j];

            #pragma unroll
            for (int i = 0; i < TM; ++i) {
                #pragma unroll
                for (int j = 0; j < TN; ++j) {
                    r_c[i][j] += r_a[i] * r_b[j];
                }
            }
        }
        __syncthreads();
    }

    #pragma unroll
    for (int i = 0; i < TM; ++i) {
        #pragma unroll
        for (int j = 0; j < TN; ++j) {
            const int row = blockIdx.y * BM + ty * TM + i;
            const int col = blockIdx.x * BN + tx * TN + j;
            if (row < M && col < N) {
                C[row * N + col] = r_c[i][j];
            }
        }
    }
}
```
:::

Реєстрове тайлування підносить арифметичну інтенсивність ядра з `2.0 FLOP/байт` до понад `64.0 FLOP/байт`, дозволяючи чипу досягати 90–95% пікової теоретичної продуктивності FP32.

### Експеримент 9: Двовимірний трафарет (2D Stencil) з обміном ореолами

При обробці зображень або моделюванні диференціальних рівнянь (фільтр Гауса, рівняння теплопровідності) кожен піксель обчислюється як зважена сума своїх 4 або 8 сусідів.

Якщо кожен потік вичитує 9 значень безпосередньо з глобальної пам'яті VRAM, трафік шини пам'яті збільшується у 9 разів. Розв'язок полягає в завантаженні тайла `16 × 16` точок у спільну пам'ять із додаванням 1-піксельного ореолу (англ. *halo cells*), тобто буфера `18 × 18` елементів:

:::tabs
```c
// 2D Трафаретний фільтр у спільній пам'яті (C)
#define BLOCK_DIM 16
#define RADIUS 1
#define SMEM_DIM (BLOCK_DIM + 2 * RADIUS)

__global__ void stencil_2d_shared(const float *in, float *out, int width, int height)
{
    __shared__ float tile[SMEM_DIM][SMEM_DIM];

    int tx = threadIdx.x;
    int ty = threadIdx.y;
    int gx = blockIdx.x * BLOCK_DIM + tx;
    int gy = blockIdx.y * BLOCK_DIM + ty;

    // Внутрішні координати в локальному буфері
    int lx = tx + RADIUS;
    int ly = ty + RADIUS;

    // Завантаження центрального елемента
    if (gx < width && gy < height)
        tile[ly][lx] = in[gy * width + gx];
    else
        tile[ly][lx] = 0.0f;

    // Завантаження 4 сусідніх елементів ореолу (Halo)
    if (tx < RADIUS) {
        int left_gx = gx - RADIUS;
        tile[ly][tx] = (left_gx >= 0 && gy < height) ? in[gy * width + left_gx] : 0.0f;
        int right_gx = gx + BLOCK_DIM;
        tile[ly][lx + BLOCK_DIM] = (right_gx < width && gy < height) ? in[gy * width + right_gx] : 0.0f;
    }
    if (ty < RADIUS) {
        int top_gy = gy - RADIUS;
        tile[ty][lx] = (top_gy >= 0 && gx < width) ? in[top_gy * width + gx] : 0.0f;
        int bottom_gy = gy + BLOCK_DIM;
        tile[ly + BLOCK_DIM][lx] = (bottom_gy < height && gx < width) ? in[bottom_gy * width + gx] : 0.0f;
    }
    __syncthreads();

    // 5-точковий трафарет обчислюється повністю в швидкій пам'яті
    if (gx < width && gy < height) {
        float sum = tile[ly][lx] * 0.5f +
                   (tile[ly][lx - 1] + tile[ly][lx + 1] +
                    tile[ly - 1][lx] + tile[ly + 1][lx]) * 0.125f;
        out[gy * width + gx] = sum;
    }
}
```
```cpp
// 2D Трафаретний фільтр у спільній пам'яті (C++)
#include <cuda_runtime.h>

constexpr int BLOCK_DIM = 16;
constexpr int RADIUS = 1;
constexpr int SMEM_DIM = BLOCK_DIM + 2 * RADIUS;

__global__ void stencil_2d_shared(const float *in, float *out, int width, int height)
{
    __shared__ float tile[SMEM_DIM][SMEM_DIM];

    const int tx = threadIdx.x;
    const int ty = threadIdx.y;
    const int gx = blockIdx.x * BLOCK_DIM + tx;
    const int gy = blockIdx.y * BLOCK_DIM + ty;

    const int lx = tx + RADIUS;
    const int ly = ty + RADIUS;

    if (gx < width && gy < height) {
        tile[ly][lx] = in[gy * width + gx];
    } else {
        tile[ly][lx] = 0.0f;
    }

    if (tx < RADIUS) {
        const int left_gx = gx - RADIUS;
        tile[ly][tx] = (left_gx >= 0 && gy < height) ? in[gy * width + left_gx] : 0.0f;
        const int right_gx = gx + BLOCK_DIM;
        tile[ly][lx + BLOCK_DIM] = (right_gx < width && gy < height) ? in[gy * width + right_gx] : 0.0f;
    }
    if (ty < RADIUS) {
        const int top_gy = gy - RADIUS;
        tile[ty][lx] = (top_gy >= 0 && gx < width) ? in[top_gy * width + gx] : 0.0f;
        const int bottom_gy = gy + BLOCK_DIM;
        tile[ly + BLOCK_DIM][lx] = (bottom_gy < height && gx < width) ? in[bottom_gy * width + gx] : 0.0f;
    }
    __syncthreads();

    if (gx < width && gy < height) {
        const float sum = tile[ly][lx] * 0.5f +
                         (tile[ly][lx - 1] + tile[ly][lx + 1] +
                          tile[ly - 1][lx] + tile[ly + 1][lx]) * 0.125f;
        out[gy * width + gx] = sum;
    }
}
```
:::

### Експеримент 10: Асинхронна подвійна буферизація (Double Buffering)

Щоб повністю ліквідувати простої під час передачі даних, застосовують конвеєр подвійної буферизації: поки АЛП обчислюють дані з буфера 0 у спільній пам'яті, апаратний двигун копіювання завантажує наступний блок даних із глобальної пам'яті в буфер 1:

:::tabs
```c
// Подвійна буферизація з чергуванням буферів (C)
__global__ void double_buffer_matmul(const float *A, const float *B, float *C, int N)
{
    __shared__ float s_A[2][16][16];
    __shared__ float s_B[2][16][16];

    int tx = threadIdx.x, ty = threadIdx.y;
    int row = blockIdx.y * 16 + ty;
    int col = blockIdx.x * 16 + tx;

    float acc = 0.0f;
    int write_stage = 0;
    int read_stage = 0;

    // Початкове передзавантаження нульового блоку
    s_A[write_stage][ty][tx] = A[row * N + tx];
    s_B[write_stage][ty][tx] = B[ty * N + col];
    __syncthreads();

    for (int k = 16; k < N; k += 16) {
        write_stage ^= 1;
        // Завантаження наступного блоку
        s_A[write_stage][ty][tx] = A[row * N + (k + tx)];
        s_B[write_stage][ty][tx] = B[(k + ty) * N + col];

        // Обчислення поточного блоку
        #pragma unroll
        for (int i = 0; i < 16; ++i) {
            acc += s_A[read_stage][ty][i] * s_B[read_stage][i][tx];
        }
        __syncthreads();
        read_stage ^= 1;
    }

    // Обчислення фінального блоку
    #pragma unroll
    for (int i = 0; i < 16; ++i) {
        acc += s_A[read_stage][ty][i] * s_B[read_stage][i][tx];
    }
    C[row * N + col] = acc;
}
```
```cpp
// Подвійна буферизація з чергуванням буферів (C++)
#include <cuda_runtime.h>

constexpr int TILE_SIZE = 16;

__global__ void double_buffer_matmul(const float *A, const float *B, float *C, int N)
{
    __shared__ float s_A[2][TILE_SIZE][TILE_SIZE];
    __shared__ float s_B[2][TILE_SIZE][TILE_SIZE];

    const int tx = threadIdx.x, ty = threadIdx.y;
    const int row = blockIdx.y * TILE_SIZE + ty;
    const int col = blockIdx.x * TILE_SIZE + tx;

    float acc = 0.0f;
    int write_stage = 0;
    int read_stage = 0;

    s_A[write_stage][ty][tx] = A[row * N + tx];
    s_B[write_stage][ty][tx] = B[ty * N + col];
    __syncthreads();

    for (int k = TILE_SIZE; k < N; k += TILE_SIZE) {
        write_stage ^= 1;
        s_A[write_stage][ty][tx] = A[row * N + (k + tx)];
        s_B[write_stage][ty][tx] = B[(k + ty) * N + col];

        #pragma unroll
        for (int i = 0; i < TILE_SIZE; ++i) {
            acc += s_A[read_stage][ty][i] * s_B[read_stage][i][tx];
        }
        __syncthreads();
        read_stage ^= 1;
    }

    #pragma unroll
    for (int i = 0; i < TILE_SIZE; ++i) {
        acc += s_A[read_stage][ty][i] * s_B[read_stage][i][tx];
    }
    C[row * N + col] = acc;
}
```
:::

### Експеримент 11: Транспонування матриці та усунення конфліктів через Padding

Транспонування квадратної матриці розміром `N × N` є класичним тестом для перевірки одночасно двох ефектів: коалесцингу глобальної пам'яті та конфліктів банків спільної пам'яті.

Щоб запис і читання з глобальної пам'яті були повністю злитими (coalesced), блок завантажує прямокутний тайл `32 × 32` елементи з глобальної пам'яті в спільну пам'ять рядок за рядком, а потім записує його в результуючу матрицю стовпчик за стовпчиком.

Якщо спільну пам'ять оголошено як `__shared__ float tile[32][32]`, то при читанні стовпчиків усі 32 потоки варпу звертаються до одного й того самого банку (32-кратний конфлікт банків). Додавання одного фіктивного елемента `__shared__ float tile[32][33]` зсуває індекси банків для кожного рядка і повністю ліквідує конфлікти:

:::tabs
```c
// Транспонування матриці з усуненням конфліктів через padding (C)
#define TILE_DIM 32
#define BLOCK_ROWS 8

__global__ void transpose_matrix_padded(const float *idata, float *odata, int width, int height)
{
    // Фіктивний стовпець +1 (33 замість 32) усуває конфлікти банків
    __shared__ float tile[TILE_DIM][TILE_DIM + 1];

    int x = blockIdx.x * TILE_DIM + threadIdx.x;
    int y = blockIdx.y * TILE_DIM + threadIdx.y;

    // Злите читання з глобальної пам'яті в спільну
    for (int j = 0; j < TILE_DIM; j += BLOCK_ROWS) {
        if ((x < width) && ((y + j) < height)) {
            tile[threadIdx.y + j][threadIdx.x] = idata[(y + j) * width + x];
        }
    }
    __syncthreads();

    // Перераховуємо координати для запису транспонованого блоку
    x = blockIdx.y * TILE_DIM + threadIdx.x;
    y = blockIdx.x * TILE_DIM + threadIdx.y;

    // Злитий запис у глобальну пам'ять із безконфліктної спільної пам'яті
    for (int j = 0; j < TILE_DIM; j += BLOCK_ROWS) {
        if ((x < height) && ((y + j) < width)) {
            odata[(y + j) * height + x] = tile[threadIdx.x][threadIdx.y + j];
        }
    }
}
```
```cpp
// Транспонування матриці з усуненням конфліктів через padding (C++)
#include <cuda_runtime.h>

constexpr int TILE_DIM = 32;
constexpr int BLOCK_ROWS = 8;

__global__ void transpose_matrix_padded(const float *idata, float *odata, int width, int height)
{
    // Завдяки TILE_DIM + 1 кожен наступний рядок починається в наступному банку
    __shared__ float tile[TILE_DIM][TILE_DIM + 1];

    int x = blockIdx.x * TILE_DIM + threadIdx.x;
    int y = blockIdx.y * TILE_DIM + threadIdx.y;

    #pragma unroll
    for (int j = 0; j < TILE_DIM; j += BLOCK_ROWS) {
        if ((x < width) && ((y + j) < height)) {
            tile[threadIdx.y + j][threadIdx.x] = idata[(y + j) * width + x];
        }
    }
    __syncthreads();

    x = blockIdx.y * TILE_DIM + threadIdx.x;
    y = blockIdx.x * TILE_DIM + threadIdx.y;

    #pragma unroll
    for (int j = 0; j < TILE_DIM; j += BLOCK_ROWS) {
        if ((x < height) && ((y + j) < width)) {
            odata[(y + j) * height + x] = tile[threadIdx.x][threadIdx.y + j];
        }
    }
}
```
:::

### Контроль регістрового тиску та директиви компілятора

Щоб компілятор не виділив забагато регістрів і не обвалив окупансі мультипроцесора, у виробничому коді застосовують директиву `__launch_bounds__`:

:::tabs
```c
// Обмеження регістрів через launch bounds (C)
__launch_bounds__(256, 4)
__global__ void bounded_kernel(float *data, int n)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        data[idx] = data[idx] * 2.0f + 1.0f;
    }
}
```
```cpp
// Обмеження регістрів через launch bounds (C++)
#include <cuda_runtime.h>

constexpr int MAX_THREADS_PER_BLOCK = 256;
constexpr int MIN_BLOCKS_PER_SM = 4;

__launch_bounds__(MAX_THREADS_PER_BLOCK, MIN_BLOCKS_PER_SM)
__global__ void bounded_kernel(float *data, int n)
{
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        data[idx] = data[idx] * 2.0f + 1.0f;
    }
}
```
:::

Директива `__launch_bounds__(256, 4)` наказує оптимізатору компілятора обмежити кількість регістрів на потік таким чином, щоб на кожному SM гарантовано могло одночасно розміститися щонайменше 4 блоки по 256 потоків (1024 активні потоки, тобто 32 варпи).

При компіляції прапорець `-Xptxas -v` виводить точну статистику ресурсів для кожного ядра:

```
ptxas info : Compiling entry function 'bounded_kernel' for 'sm_89'
ptxas info : Used 32 registers, 0 bytes smem, 384 bytes cmem[0]
```

### Повний хостовий драйвер виклику та вимірювання часу

Нижче наведено повний хостовий код керування пристроєм: виділення пам'яті, створення подій `cudaEvent` для точного апаратного профілювання, запуск ядра та перевірка статусів помилок.

:::tabs
```c
// Хостовий запуск і таймінг ядра (C)
#include <stdio.h>
#include <stdlib.h>
#include <cuda_runtime.h>

void run_benchmark_c(int n)
{
    size_t bytes = n * sizeof(float);
    float *h_in = (float *)malloc(bytes);
    float *h_out = (float *)malloc(bytes);
    for (int i = 0; i < n; i++) h_in[i] = (float)i;

    float *d_in = NULL, *d_out = NULL;
    cudaMalloc((void **)&d_in, bytes);
    cudaMalloc((void **)&d_out, bytes);
    cudaMemcpy(d_in, h_in, bytes, cudaMemcpyHostToDevice);

    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);

    int block_size = 256;
    int grid_size = (n + block_size - 1) / block_size;

    cudaEventRecord(start, 0);
    kernel_warp_aligned<<<grid_size, block_size>>>(d_in, d_out, n);
    cudaEventRecord(stop, 0);
    cudaEventSynchronize(stop);

    float milliseconds = 0.0f;
    cudaEventElapsedTime(&milliseconds, start, stop);
    printf("Час виконання ядра: %.3f мс\n", milliseconds);

    cudaMemcpy(h_out, d_out, bytes, cudaMemcpyDeviceToHost);

    cudaEventDestroy(start);
    cudaEventDestroy(stop);
    cudaFree(d_in);
    cudaFree(d_out);
    free(h_in);
    free(h_out);
}
```
```cpp
// Хостовий запуск і таймінг ядра з RAII та розумними покажчиками (C++)
#include <iostream>
#include <vector>
#include <memory>
#include <stdexcept>
#include <cuda_runtime.h>

struct CudaDeleter {
    void operator()(void* ptr) const noexcept {
        if (ptr) cudaFree(ptr);
    }
};

template <typename T>
using DeviceBuffer = std::unique_ptr<T[], CudaDeleter>;

template <typename T>
DeviceBuffer<T> make_device_buffer(std::size_t count) {
    T* raw_ptr = nullptr;
    if (cudaMalloc(&raw_ptr, count * sizeof(T)) != cudaSuccess) {
        throw std::runtime_error("Помилка cudaMalloc при виділенні пам'яті GPU");
    }
    return DeviceBuffer<T>(raw_ptr);
}

void run_benchmark_cpp(int n)
{
    std::vector<float> host_in(n);
    std::vector<float> host_out(n);
    for (int i = 0; i < n; ++i) host_in[i] = static_cast<float>(i);

    auto dev_in = make_device_buffer<float>(n);
    auto dev_out = make_device_buffer<float>(n);

    cudaMemcpy(dev_in.get(), host_in.data(), n * sizeof(float), cudaMemcpyHostToDevice);

    cudaEvent_t start{}, stop{};
    cudaEventCreate(&start);
    cudaEventCreate(&stop);

    const int block_size = 256;
    const int grid_size = (n + block_size - 1) / block_size;

    cudaEventRecord(start);
    kernel_warp_aligned<<<grid_size, block_size>>>(dev_in.get(), dev_out.get(), n);
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);

    float milliseconds = 0.0f;
    cudaEventElapsedTime(&milliseconds, start, stop);
    std::cout << "Час виконання ядра: " << milliseconds << " мс\n";

    cudaMemcpy(host_out.data(), dev_out.get(), n * sizeof(float), cudaMemcpyDeviceToHost);

    cudaEventDestroy(start);
    cudaEventDestroy(stop);
}
```
:::

### Інструментальне простеження через NVIDIA Nsight Compute

Для діагностики проблем SIMT на рівні апаратних лічильників використовують профайлер **NVIDIA Nsight Compute** (`ncu`). Нижче наведено ключові метрики профайлера, які дозволяють виявити розглянуті дефекти:

1. **Дивергенція варпів:**
   * Метрика `smsp__sass_average_branch_targets_threads_uniform.pct` показує відсоток розгалужень, де всі потоки пішли в одному напрямку. Значення нижче 90% свідчить про високу дивергенцію.
   * Метрика `smsp__thread_inst_executed_per_inst_executed.ratio` показує середню кількість активних потоків на інструкцію (ідеально — 32.0; значення 16.0 означає 50% втрат через дивергенцію).

2. **Коалесцинг глобальної пам'яті:**
   * `l1tex__t_sectors_pipe_lsu_mem_global_op_ld.sum` — загальна кількість 32-байтових секторів, вичитаних із пам'яті.
   * `l1tex__t_requests_pipe_lsu_mem_global_op_ld.sum` — кількість інструкцій завантаження варпів.
   * Відношення `сектори / запити`: ідеальне значення — 4.0 (128 байтів = 4 сектори на варп). Значення 32.0 сигналізує про повну відсутність коалесцингу.

3. **Конфлікти банків спільної пам'яті:**
   * `smsp__sass_l1tex_data_bank_conflicts_pipe_lsu_mem_shared_op_ld.sum` — сумарна кількість додаткових тактів серіалізації, викликаних конфліктами банків при читанні. У добре оптимізованому ядрі ця метрика дорівнює нулю.
