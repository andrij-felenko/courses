# ⚙️ Динамічна диспетчеризація SIMD та функціональне мультиверсіонування

Створення високопродуктивних числових бібліотек ставить перед розробником дилему сумісності. Векторні інструкції [SIMD](book:programming/simd-vectorization) (AVX2, AVX-512) дають прискорення обчислень у рази, проте спроба виконати 256-бітну чи 512-бітну команду на процесорі, який їх не підтримує, призводить до аварійної зупинки програми через апаратне виключення [недійсної інструкції](book:programming/cpu-exception-handling) (`#UD` / сигнал `SIGILL`). Скомпілювати всю програму з прапорцем `-mavx2` — означає втратити сумісність зі старішими чи енергоефективними чипами.

Єдиний інженерний розв'язок — **динамічна диспетчеризація на етапі запуску (runtime dispatching)**: бінарний файл містить кілька версій гарячих функцій (скалярну, SSE4.2, AVX2, AVX-512) і під час завантаження обирає найшвидшу, спираючись на результат інструкції `CPUID`.

У цьому проекті розібрано повний ланцюг перевірки (включно з пасткою `XCR0`), проаналізовано апаратні ефекти зниження частоти ядер при виконанні AVX-512, реалізовано ручний диспетчер функціональних покажчиків та налаштовано механізм непрямих функцій `GNU IFUNC` без накладних витрат на кожному виклику.

## Пастка XSAVE: чому перевірки тільки CPUID недостатньо

Початківці часто припускаються критичної помилки: зчитують Листок 1 або Листок 7 через `CPUID`, бачать встановлений біт `AVX2` і одразу перемикають виконання на векторний код. На віртуальних машинах чи в застарілих версіях операційних систем це гарантовано призводить до збою.

Векторні інструкції використовують широкі регістри (`YMM` розміром 256 бітів, `ZMM` розміром 512 бітів). Коли операційна система перемикає контекст між потоками, вона мусить зберігати значення цих регістрів у пам'ять. Якщо ядро ОС не навчене зберігати 256-бітні регістри (або завантажене з вимкненою опцією `xsave`), спроба виконати інструкцію `VEX`/`EVEX` викличе `#UD` навіть на найсучаснішому кремнії.

Безпечний алгоритм перевірки складається з чотирьох послідовних кроків:

```
1. Викликати CPUID (Leaf 1, ECX) -> перевірити біт 26 (XSAVE) та біт 27 (OSXSAVE).
2. Якщо OSXSAVE = 1: виконати недискреційну інструкцію XGETBV з ECX = 0.
3. Перевірити бітову маску регістра XCR0:
   - Біт 1 (XMM / SSE) повинен бути 1;
   - Біт 2 (YMM / AVX) повинен бути 1;
   - Для AVX-512: біти 5 (Opmask k0..k7), 6 (ZMM_Hi256) та 7 (Hi16_ZMM) повинні бути 1.
4. Якщо стан XCR0 валідний: викликати CPUID (Leaf 7, Sub-leaf 0) і перевірити біт AVX2 або AVX512F.
```

## Апаратна ціна AVX-512: скидання частоти та ліцензії напруги

При диспетчеризації векторних ядер мало знати, що інструкція підтримується залізом — треба враховувати її вплив на енергоспоживання чипа.

У мікроархітектурах Intel Skylake-SP, Cascade Lake та Ice Lake виконання важких 512-бітних векторних операцій з плаваючою комою (FMA) вимагає значного збільшення струму живлення. Щоб запобігти локальному перегріву кристала та просіданню напруги, блок керування живленням процесора ([PCU](book:programming/dvfs)) перемикає ядро на нижчу «ліцензію частоти» (License Level):
* **License 0 (Nominal):** виконання скалярного коду та інструкцій SSE — максимальна турбо-частота;
* **License 1 (AVX2):** виконання 256-бітних операцій — зниження частоти на 100–200 МГц;
* **License 2 (AVX-512 Heavy):** виконання 512-бітних інструкцій із подвійним FMA — зниження базової та турбо-частоти на 400–800 МГц для всього фізичного ядра.

Перехід між рівнями ліцензій займає кілька мікросекунд, під час яких процесор може пригальмовувати конвеєр. Якщо програма виконує коротке 512-бітне векторне обчислення раз на секунду, а решту часу обробляє звичайні скалярні запити, сумарна продуктивність впаде через те, що все ядро сповільниться на час дії ліцензії (близько 1–2 мілісекунд після останньої AVX-512 інструкції).

Тому сучасні бібліотеки під час диспетчеризації обирають або розширення `AVX-512 VL` (Vector Length Extensions, де операції AVX-512 виконуються на безпечніших 256-бітних регістрах без падіння частоти), або перемикаються на повний 512-бітний режим лише за умови великого обсягу матричних чи потокових обчислень.

## Реалізація безпечної інспекції мікроархітектури

Створимо модуль інспекції, який виконує повний дворівневий аналіз заліза, стану операційної системи та наявності розширень AVX2, FMA3 і AVX-512.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <cpuid.h>
#include <immintrin.h>

typedef struct {
    bool has_sse42;
    bool has_avx2;
    bool has_avx512f;
    bool has_avx512vl;
    bool has_fma;
    bool has_bmi2;
} CpuCapabilities;

static inline uint64_t read_xcr0(void) {
    uint32_t eax, edx;
    __asm__ __volatile__("xgetbv" : "=a"(eax), "=d"(edx) : "c"(0));
    return ((uint64_t)edx << 32) | eax;
}

CpuCapabilities detect_cpu_features(void) {
    CpuCapabilities caps = {false, false, false, false, false, false};
    uint32_t eax, ebx, ecx, edx;

    // Перевірка максимального доступного базового листка
    if (!__get_cpuid(0, &eax, &ebx, &ecx, &edx) || eax < 1) {
        return caps;
    }

    // Листок 1: базові можливості та OSXSAVE
    __cpuid(1, eax, ebx, ecx, edx);
    caps.has_sse42 = (ecx & bit_SSE4_2) != 0;
    caps.has_fma   = (ecx & bit_FMA) != 0;

    bool osxsave = (ecx & bit_OSXSAVE) != 0;
    bool ymm_supported = false;
    bool zmm_supported = false;

    if (osxsave) {
        uint64_t xcr0 = read_xcr0();
        // Біт 1 = SSE (XMM), біт 2 = AVX (YMM)
        ymm_supported = (xcr0 & 0x06) == 0x06;
        // Біти 5, 6, 7 = стан ZMM та Opmask для AVX-512
        zmm_supported = ymm_supported && ((xcr0 & 0xE0) == 0xE0);
    }

    // Листок 7 (підлисток 0): розширені прапорці
    if (eax >= 7) {
        __cpuid_count(7, 0, eax, ebx, ecx, edx);
        caps.has_bmi2 = (ebx & bit_BMI2) != 0;

        if (ymm_supported && (ebx & bit_AVX2)) {
            caps.has_avx2 = true;
        }
        if (zmm_supported) {
            caps.has_avx512f  = (ebx & bit_AVX512F) != 0;
            caps.has_avx512vl = (ebx & bit_AVX512VL) != 0;
        }
    }

    return caps;
}
```
```cpp
#include <cstdint>
#include <cpuid.h>
#include <immintrin.h>

struct CpuCapabilities {
    bool has_sse42{false};
    bool has_avx2{false};
    bool has_avx512f{false};
    bool has_avx512vl{false};
    bool has_fma{false};
    bool has_bmi2{false};
};

class CpuFeatureDetector {
public:
    static CpuCapabilities probe() noexcept {
        CpuCapabilities caps{};
        std::uint32_t eax = 0, ebx = 0, ecx = 0, edx = 0;

        if (!__get_cpuid(0, &eax, &ebx, &ecx, &edx) || eax < 1) {
            return caps;
        }

        __cpuid(1, eax, ebx, ecx, edx);
        caps.has_sse42 = (ecx & bit_SSE4_2) != 0;
        caps.has_fma   = (ecx & bit_FMA) != 0;

        const bool osxsave = (ecx & bit_OSXSAVE) != 0;
        bool ymm_supported = false;
        bool zmm_supported = false;

        if (osxsave) {
            const std::uint64_t xcr0 = read_xcr0();
            ymm_supported = (xcr0 & 0x06) == 0x06;
            zmm_supported = ymm_supported && ((xcr0 & 0xE0) == 0xE0);
        }

        if (eax >= 7) {
            __cpuid_count(7, 0, eax, ebx, ecx, edx);
            caps.has_bmi2 = (ebx & bit_BMI2) != 0;

            if (ymm_supported && (ebx & bit_AVX2)) {
                caps.has_avx2 = true;
            }
            if (zmm_supported) {
                caps.has_avx512f  = (ebx & bit_AVX512F) != 0;
                caps.has_avx512vl = (ebx & bit_AVX512VL) != 0;
            }
        }

        return caps;
    }

private:
    static std::uint64_t read_xcr0() noexcept {
        std::uint32_t eax = 0, edx = 0;
        __asm__ __volatile__("xgetbv" : "=a"(eax), "=d"(edx) : "c"(0));
        return (static_cast<std::uint64_t>(edx) << 32) | eax;
    }
};
```
:::

## Мультиверсіонування: реалізація векторного обчислювального ядра

Для демонстрації візьмемо задачу обчислення зваженого скалярного добутку або суми масиву чисел з плаваючою комою. Реалізуємо два альтернативні обчислювальні ядра: скалярне для гарантованої сумісності та оптимізоване AVX2-ядро з 256-бітними регістрами.

:::tabs
```c
#include <stddef.h>
#include <immintrin.h>

// Скалярне ядро: працює на будь-якому процесорі x86
float vec_sum_scalar(const float* data, size_t count) {
    float sum = 0.0f;
    for (size_t i = 0; i < count; ++i) {
        sum += data[i];
    }
    return sum;
}

// AVX2 ядро: обробка по 8 елементів float за один такт
__attribute__((target("avx2,fma")))
float vec_sum_avx2(const float* data, size_t count) {
    __m256 acc = _mm256_setzero_ps();
    size_t i = 0;
    for (; i + 8 <= count; i += 8) {
        __m256 v = _mm256_loadu_ps(data + i);
        acc = _mm256_add_ps(acc, v);
    }
    // Горизонтальне згортання 8 елементів регістру YMM
    __m128 lo = _mm256_castps256_ps128(acc);
    __m128 hi = _mm256_extractf128_ps(acc, 1);
    __m128 sum128 = _mm_add_ps(lo, hi);
    sum128 = _mm_hadd_ps(sum128, sum128);
    sum128 = _mm_hadd_ps(sum128, sum128);
    float total = _mm_cvtss_f32(sum128);

    // Обробка залишкових елементів
    for (; i < count; ++i) {
        total += data[i];
    }
    return total;
}

typedef float (*vec_sum_fn)(const float*, size_t);
```
```cpp
#include <span>
#include <cstddef>
#include <numeric>
#include <immintrin.h>

struct VectorKernels {
    static float sum_scalar(std::span<const float> data) noexcept {
        return std::accumulate(data.begin(), data.end(), 0.0f);
    }

    __attribute__((target("avx2,fma")))
    static float sum_avx2(std::span<const float> data) noexcept {
        __m256 acc = _mm256_setzero_ps();
        const std::size_t count = data.size();
        const float* ptr = data.data();
        std::size_t i = 0;

        for (; i + 8 <= count; i += 8) {
            __m256 v = _mm256_loadu_ps(ptr + i);
            acc = _mm256_add_ps(acc, v);
        }

        __m128 lo = _mm256_castps256_ps128(acc);
        __m128 hi = _mm256_extractf128_ps(acc, 1);
        __m128 sum128 = _mm_add_ps(lo, hi);
        sum128 = _mm_hadd_ps(sum128, sum128);
        sum128 = _mm_hadd_ps(sum128, sum128);
        float total = _mm_cvtss_f32(sum128);

        for (; i < count; ++i) {
            total += ptr[i];
        }
        return total;
    }
};

using VecSumFn = float (*)(std::span<const float>) noexcept;
```
:::

## Механізм GNU IFUNC: нульова ціна виклику через dynamic loader

Класичний виклик через глобальний покажчик `fn_ptr(data, len)` створює дві проблеми: непрямий стрибок `call *%rax` навантажує передбачувач переходів і заважає компілятору вбудовувати код.

В операційних системах сімейства Linux із бінарним форматом ELF існує спеціалізоване розширення — **GNU Indirect Functions (IFUNC)**. Під час старту програми динамічний лінкер `ld.so` знаходить у таблиці символів запис типу `STT_GNU_IFUNC` і викликає прив'язану функцію-резолвер. Резолвер виконує `CPUID`, визначає найкращу версію алгоритму і повертає її адресу.

Після цього лінкер записує цю адресу безпосередньо в таблицю зв'язування `GOT` (Global Offset Table) за допомогою релокації `R_X86_64_IRELATIVE`. Усі наступні виклики виконуються як прямий стрибок без жодного розгалуження чи перевірки прапорців!

:::tabs
```c
#include <stdio.h>

// Функція-резолвер: викликається динамічним лінкером ld.so один раз під час старту
static vec_sum_fn resolve_vec_sum(void) {
    CpuCapabilities caps = detect_cpu_features();
    if (caps.has_avx2 && caps.has_fma) {
        return vec_sum_avx2;
    }
    return vec_sum_scalar;
}

// Оголошення публічної функції з атрибутом ifunc
float vec_sum(const float* data, size_t count)
    __attribute__((ifunc("resolve_vec_sum")));

int main(void) {
    float numbers[16] = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f, 7.0f, 8.0f,
                         9.0f, 10.0f, 11.0f, 12.0f, 13.0f, 14.0f, 15.0f, 16.0f};

    // Прямий виклик: динамічний лінкер уже спрямував точку входу на потрібне ядро
    float result = vec_sum(numbers, 16);
    printf("Обчислена сума: %f\n", result);
    return (result > 0.0f) ? 0 : 1;
}
```
```cpp
#include <iostream>
#include <array>
#include <span>

extern "C" {
    static VecSumFn resolve_vec_sum_cpp() noexcept {
        const auto caps = CpuFeatureDetector::probe();
        if (caps.has_avx2 && caps.has_fma) {
            return VectorKernels::sum_avx2;
        }
        return VectorKernels::sum_scalar;
    }

    float fast_vec_sum(std::span<const float> data) noexcept
        __attribute__((ifunc("resolve_vec_sum_cpp")));
}

int main() {
    constexpr std::array<float, 16> numbers{
        1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f, 7.0f, 8.0f,
        9.0f, 10.0f, 11.0f, 12.0f, 13.0f, 14.0f, 15.0f, 16.0f
    };

    const float result = fast_vec_sum(numbers);
    std::cout << "Обчислена сума: " << result << "\n";
    return (result > 0.0f) ? 0 : 1;
}
```
:::

## Керування диспетчеризацією через оточення та підводні камені

1. **Небезпека виклику зовнішніх бібліотек у резолвері IFUNC:**
   Під час виклику резолвера лінкер ще не завершив обробку інших релокацій у програмі. Якщо резолвер спробує викликати функцію з динамічної бібліотеки (наприклад, `malloc`, `printf` або `getopt`), покажчик на неї в таблиці GOT може бути неініціалізованим, що викличе негайний сегментаційний збій (`SIGSEGV`). Резолвер повинен містити лише прямі інструкції (`CPUID`, `XGETBV`) та просту умовну логіку.

2. **Примусове відключення наборів інструкцій через GLIBC Tunables:**
   Для тестування сумісності або ізоляції помилок системний адміністратор може примусово вимкнути розширення без перекомпільовування бінарних файлів за допомогою змінної середовища:
   ```bash
   GLIBC_TUNABLES=glibc.cpu.hwcaps=-AVX2_Usable,-AVX512F_Usable ./my_application
   ```
   Це змушує стандартну бібліотеку `glibc` ігнорувати апаратні біти `CPUID` для власних оптимізованих функцій (наприклад, `memcpy` та `strlen`), перемикаючи їх на базові реалізації SSE2.

3. **Асиметрія гібридних ядер (Intel Alder Lake / Raptor Lake):**
   На процесорах із гетерогенною мікроархітектурою продуктивні ядра (P-cores) та енергоефективні ядра (E-cores) фізично підтримують різні набори векторних розширень. Щоб потік виконання не впав із `#UD` при міграції з P-core на E-core, операційна система та мікрокод маскують прапорці `CPUID` так, щоб вони відображали найменший спільний набір інструкцій, доступний на всіх активних ядрах системи.
