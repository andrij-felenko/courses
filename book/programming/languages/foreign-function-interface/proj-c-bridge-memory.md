# ⚙️ Побудова надійного FFI-мосту з контролем пам'яті та структур

Головна небезпека під час побудови міжмовного інтерфейсу полягає не в передачі простих чисел (цілі числа й дроби процесор розкладає по регістрах автоматично), а в **керуванні життєвим циклом пам'яті та розкладці складних структур**. Якщо мова вищого рівня спробує виділити пам'ять власним менеджером, а рідна C-бібліотека викличе для цієї адреси стандартний `free()`, рантайм зазнає фатального краху через несумісність внутрішніх структур купи.

Розгляньмо еталонну реалізацію міжмовного мосту для пакетної обробки числових сигналів. Інтерфейс вимагає суворого дотримання чотирьох інваріантів:
1. **Явне двійкове вирівнювання:** порядок полів та їхні зміщення у структурах мають бути ідентичними в усіх мовах.
2. **Симетрія алокаторів:** будь-який блок пам'яті, виділений всередині нативної бібліотеки, звільняється виключно функціями цієї ж бібліотеки.
3. **Статусні коди замість винятків:** C ABI не підтримує розкрутку стека винятків (англ. *exception unwinding*), тому всі помилки передаються через цілочисельні статуси.
4. **Непрозорі покажчики (Opaque Handles):** внутрішній стан бібліотеки приховується за типізованим або порожнім покажчиком, захищаючи поля від несанкціонованої модифікації клієнтом.

## 1. Заголовний файл C/C++ інтерфейсу

Двійковий контракт оголошується мовою C для максимальної сумісності, а для C++ клієнтів надається ідіоматична обгортка на базі `std::span` та RAII.

:::tabs
```c
#ifndef BRIDGE_CORE_H
#define BRIDGE_CORE_H

#include <stdint.h>
#include <stddef.h>

#ifdef _WIN32
  #define BRIDGE_API __declspec(dllexport)
#else
  #define BRIDGE_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* Коди помилок операцій */
typedef enum {
    BRIDGE_OK = 0,
    BRIDGE_ERR_NULL_PTR = 1,
    BRIDGE_ERR_INVALID_PARAM = 2,
    BRIDGE_ERR_OUT_OF_MEMORY = 3,
    BRIDGE_ERR_COMPUTATION = 4
} BridgeStatus;

/* Структура конфігурації з явним вирівнюванням */
typedef struct {
    int32_t sample_rate;    /* 4 байти, зміщення 0 */
    int32_t channels;       /* 4 байти, зміщення 4 */
    double  scale_factor;   /* 8 байтів, зміщення 8 (вирівняно по 8) */
    uint8_t enable_filter;  /* 1 байт, зміщення 16 */
    uint8_t padding[7];     /* 7 байтів явної набивки до загального розміру 24 байти */
} BridgeConfig;

/* Непрозорий тип контексту обробки */
typedef struct BridgeContext BridgeContext;

/* Життєвий цикл контексту: створення, обробка, знищення */
BRIDGE_API BridgeStatus bridge_create_context(const BridgeConfig *config, BridgeContext **out_ctx);
BRIDGE_API BridgeStatus bridge_process_buffer(BridgeContext *ctx, const float *input, size_t count, float **out_buf, size_t *out_count);
BRIDGE_API void         bridge_free_buffer(float *buf);
BRIDGE_API void         bridge_free_context(BridgeContext *ctx);
BRIDGE_API const char*  bridge_get_last_error(BridgeStatus status);

#ifdef __cplusplus
}
#endif

#endif /* BRIDGE_CORE_H */
```
```cpp
#pragma once
#include <cstdint>
#include <cstddef>
#include <span>
#include <vector>
#include <string_view>
#include <expected>
#include <memory>

#ifdef _WIN32
  #define BRIDGE_API __declspec(dllexport)
#else
  #define BRIDGE_API __attribute__((visibility("default")))
#endif

extern "C" {

enum class BridgeStatus : int32_t {
    Ok = 0,
    ErrNullPtr = 1,
    ErrInvalidParam = 2,
    ErrOutOfMemory = 3,
    ErrComputation = 4
};

struct alignas(8) BridgeConfig {
    int32_t sample_rate;
    int32_t channels;
    double  scale_factor;
    uint8_t enable_filter;
    uint8_t padding[7];
};

struct BridgeContext;

BRIDGE_API BridgeStatus bridge_create_context(const BridgeConfig *config, BridgeContext **out_ctx);
BRIDGE_API BridgeStatus bridge_process_buffer(BridgeContext *ctx, const float *input, size_t count, float **out_buf, size_t *out_count);
BRIDGE_API void         bridge_free_buffer(float *buf);
BRIDGE_API void         bridge_free_context(BridgeContext *ctx);
BRIDGE_API const char*  bridge_get_last_error(BridgeStatus status);

} // extern "C"

// Ідіоматичний C++23 RAII-клас для безпечного клієнтського використання
class SafeBridgeClient {
public:
    static std::expected<SafeBridgeClient, std::string_view> create(const BridgeConfig& cfg) {
        BridgeContext* raw_ctx = nullptr;
        BridgeStatus st = bridge_create_context(&cfg, &raw_ctx);
        if (st != BridgeStatus::Ok) {
            return std::unexpected(bridge_get_last_error(st));
        }
        return SafeBridgeClient(raw_ctx);
    }

    ~SafeBridgeClient() {
        if (ctx_) bridge_free_context(ctx_);
    }

    SafeBridgeClient(const SafeBridgeClient&) = delete;
    SafeBridgeClient& operator=(const SafeBridgeClient&) = delete;
    SafeBridgeClient(SafeBridgeClient&& o) noexcept : ctx_(std::exchange(o.ctx_, nullptr)) {}
    SafeBridgeClient& operator=(SafeBridgeClient&& o) noexcept {
        if (this != &o) {
            if (ctx_) bridge_free_context(ctx_);
            ctx_ = std::exchange(o.ctx_, nullptr);
        }
        return *this;
    }

    std::expected<std::vector<float>, std::string_view> process(std::span<const float> input) {
        float* out_raw = nullptr;
        size_t out_len = 0;
        BridgeStatus st = bridge_process_buffer(ctx_, input.data(), input.size(), &out_raw, &out_len);
        if (st != BridgeStatus::Ok) {
            return std::unexpected(bridge_get_last_error(st));
        }
        std::vector<float> result(out_raw, out_raw + out_len);
        bridge_free_buffer(out_raw);
        return result;
    }

private:
    explicit SafeBridgeClient(BridgeContext* ctx) : ctx_(ctx) {}
    BridgeContext* ctx_{nullptr};
};
```
:::

## 2. Реалізація бібліотеки на стороні C та C++

У нативній реалізації бібліотека контролює виділення пам'яті через системні виклики та інкапсулює внутрішні поля структури в купі процесу:

:::tabs
```c
#include "bridge_core.h"
#include <stdlib.h>
#include <string.h>

struct BridgeContext {
    BridgeConfig config;
    double accumulated_scale;
};

BRIDGE_API BridgeStatus bridge_create_context(const BridgeConfig *config, BridgeContext **out_ctx) {
    if (!config || !out_ctx) return BRIDGE_ERR_NULL_PTR;
    if (config->sample_rate <= 0 || config->channels <= 0) return BRIDGE_ERR_INVALID_PARAM;

    BridgeContext *ctx = (BridgeContext*)malloc(sizeof(BridgeContext));
    if (!ctx) return BRIDGE_ERR_OUT_OF_MEMORY;

    ctx->config = *config;
    ctx->accumulated_scale = config->scale_factor;
    *out_ctx = ctx;
    return BRIDGE_OK;
}

BRIDGE_API BridgeStatus bridge_process_buffer(BridgeContext *ctx, const float *input, size_t count, float **out_buf, size_t *out_count) {
    if (!ctx || !input || !out_buf || !out_count) return BRIDGE_ERR_NULL_PTR;
    if (count == 0) return BRIDGE_ERR_INVALID_PARAM;

    float *processed = (float*)malloc(sizeof(float) * count);
    if (!processed) return BRIDGE_ERR_OUT_OF_MEMORY;

    double factor = ctx->accumulated_scale;
    for (size_t i = 0; i < count; ++i) {
        processed[i] = (float)(input[i] * factor);
    }

    *out_buf = processed;
    *out_count = count;
    return BRIDGE_OK;
}

BRIDGE_API void bridge_free_buffer(float *buf) {
    if (buf) {
        free(buf);
    }
}

BRIDGE_API void bridge_free_context(BridgeContext *ctx) {
    if (ctx) {
        free(ctx);
    }
}

BRIDGE_API const char* bridge_get_last_error(BridgeStatus status) {
    switch (status) {
        case BRIDGE_OK:                return "Успішне виконання";
        case BRIDGE_ERR_NULL_PTR:      return "Передано нульовий покажчик";
        case BRIDGE_ERR_INVALID_PARAM: return "Некоректні вхідні параметри";
        case BRIDGE_ERR_OUT_OF_MEMORY: return "Недостатньо системної пам'яті";
        case BRIDGE_ERR_COMPUTATION:   return "Помилка обчислень";
        default:                       return "Невідомий код помилки";
    }
}
```
```cpp
#include "bridge_core.hpp"
#include <vector>
#include <memory>
#include <new>

struct BridgeContext {
    BridgeConfig config;
    double accumulated_scale;

    explicit BridgeContext(const BridgeConfig& cfg)
        : config(cfg), accumulated_scale(cfg.scale_factor) {}
};

BRIDGE_API BridgeStatus bridge_create_context(const BridgeConfig *config, BridgeContext **out_ctx) {
    if (!config || !out_ctx) return BridgeStatus::ErrNullPtr;
    if (config->sample_rate <= 0 || config->channels <= 0) return BridgeStatus::ErrInvalidParam;

    try {
        *out_ctx = new BridgeContext(*config);
        return BridgeStatus::Ok;
    } catch (const std::bad_alloc&) {
        return BridgeStatus::ErrOutOfMemory;
    }
}

BRIDGE_API BridgeStatus bridge_process_buffer(BridgeContext *ctx, const float *input, size_t count, float **out_buf, size_t *out_count) {
    if (!ctx || !input || !out_buf || !out_count) return BridgeStatus::ErrNullPtr;
    if (count == 0) return BridgeStatus::ErrInvalidParam;

    float* processed = static_cast<float*>(std::malloc(sizeof(float) * count));
    if (!processed) return BridgeStatus::ErrOutOfMemory;

    const double factor = ctx->accumulated_scale;
    for (size_t i = 0; i < count; ++i) {
        processed[i] = static_cast<float>(input[i] * factor);
    }

    *out_buf = processed;
    *out_count = count;
    return BridgeStatus::Ok;
}

BRIDGE_API void bridge_free_buffer(float *buf) {
    std::free(buf);
}

BRIDGE_API void bridge_free_context(BridgeContext *ctx) {
    delete ctx;
}

BRIDGE_API const char* bridge_get_last_error(BridgeStatus status) {
    switch (status) {
        case BridgeStatus::Ok:              return "Успішне виконання";
        case BridgeStatus::ErrNullPtr:      return "Передано нульовий покажчик";
        case BridgeStatus::ErrInvalidParam: return "Некоректні вхідні параметри";
        case BridgeStatus::ErrOutOfMemory:  return "Недостатньо системної пам'яті";
        case BridgeStatus::ErrComputation:  return "Помилка обчислень";
        default:                            return "Невідомий код помилки";
    }
}
```
:::

## 3. Клієнтська інтеграція: Python (ctypes) та Rust

Клієнти на мовах вищого рівня використовують нативну бібліотеку як динамічний спільний об'єкт (`.so` або `.dll`):

:::tabs
```python
import ctypes
import os
import platform

# 1. Завантаження DSO/DLL бібліотеки
lib_name = "bridge_core.dll" if platform.system() == "Windows" else "./libbridge_core.so"
lib = ctypes.CDLL(os.path.abspath(lib_name))

# 2. Опис C-структури з точним порядком і розміром полів
class BridgeConfig(ctypes.Structure):
    _fields_ = [
        ("sample_rate", ctypes.c_int32),
        ("channels", ctypes.c_int32),
        ("scale_factor", ctypes.c_double),
        ("enable_filter", ctypes.c_uint8),
        ("padding", ctypes.c_uint8 * 7),
    ]

# 3. Налаштування сигнатур (argtypes та restype)
lib.bridge_create_context.argtypes = [ctypes.POINTER(BridgeConfig), ctypes.POINTER(ctypes.c_void_p)]
lib.bridge_create_context.restype = ctypes.c_int

lib.bridge_process_buffer.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_float),
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.POINTER(ctypes.c_float)),
    ctypes.POINTER(ctypes.c_size_t)
]
lib.bridge_process_buffer.restype = ctypes.c_int

lib.bridge_free_buffer.argtypes = [ctypes.POINTER(ctypes.c_float)]
lib.bridge_free_buffer.restype = None

lib.bridge_free_context.argtypes = [ctypes.c_void_p]
lib.bridge_free_context.restype = None

lib.bridge_get_last_error.argtypes = [ctypes.c_int]
lib.bridge_get_last_error.restype = ctypes.c_char_p

# 4. Виконання виклику з гарантованим очищенням ресурсів
config = BridgeConfig(sample_rate=48000, channels=2, scale_factor=1.5, enable_filter=1)
ctx = ctypes.c_void_p()

status = lib.bridge_create_context(ctypes.byref(config), ctypes.byref(ctx))
if status != 0:
    err_msg = lib.bridge_get_last_error(status).decode("utf-8")
    raise RuntimeError(f"FFI Помилка створення контексту: {err_msg}")

try:
    input_array = (ctypes.c_float * 4)(1.0, 2.0, 3.0, 4.0)
    out_buf = ctypes.POINTER(ctypes.c_float)()
    out_len = ctypes.c_size_t()

    res = lib.bridge_process_buffer(ctx, input_array, len(input_array), ctypes.byref(out_buf), ctypes.byref(out_len))
    if res != 0:
        err_msg = lib.bridge_get_last_error(res).decode("utf-8")
        raise RuntimeError(f"FFI Помилка обробки: {err_msg}")

    try:
        # Копіюємо дані у стандартний список Python
        result = [out_buf[i] for i in range(out_len.value)]
        print(f"Результат обробки ({out_len.value} елементів): {result}")
    finally:
        # Звільняємо буфер виключно через рідну функцію бібліотеки!
        lib.bridge_free_buffer(out_buf)
finally:
    # Звільняємо контекст
    lib.bridge_free_context(ctx)
```
```rust
use std::os::raw::{c_char, c_int};
use std::ffi::CStr;

#[repr(C)]
pub struct BridgeConfig {
    pub sample_rate: i32,
    pub channels: i32,
    pub scale_factor: f64,
    pub enable_filter: u8,
    pub padding: [u8; 7],
}

enum BridgeContextOpaque {}

extern "C" {
    fn bridge_create_context(config: *const BridgeConfig, out_ctx: *mut *mut BridgeContextOpaque) -> c_int;
    fn bridge_process_buffer(
        ctx: *mut BridgeContextOpaque,
        input: *const f32,
        count: usize,
        out_buf: *mut *mut f32,
        out_count: *mut usize,
    ) -> c_int;
    fn bridge_free_buffer(buf: *mut f32);
    fn bridge_free_context(ctx: *mut BridgeContextOpaque);
    fn bridge_get_last_error(status: c_int) -> *const c_char;
}

pub struct NativeBridge {
    raw: *mut BridgeContextOpaque,
}

impl NativeBridge {
    pub fn new(sample_rate: i32, channels: i32, scale_factor: f64) -> Result<Self, String> {
        let config = BridgeConfig {
            sample_rate,
            channels,
            scale_factor,
            enable_filter: 1,
            padding: [0; 7],
        };
        let mut raw = std::ptr::null_mut();
        unsafe {
            let status = bridge_create_context(&config, &mut raw);
            if status != 0 {
                let err = CStr::from_ptr(bridge_get_last_error(status)).to_string_lossy().into_owned();
                return Err(err);
            }
            Ok(Self { raw })
        }
    }

    pub fn process(&self, data: &[f32]) -> Result<Vec<f32>, String> {
        let mut out_ptr = std::ptr::null_mut();
        let mut out_len = 0usize;

        unsafe {
            let status = bridge_process_buffer(self.raw, data.as_ptr(), data.len(), &mut out_ptr, &mut out_len);
            if status != 0 {
                let err = CStr::from_ptr(bridge_get_last_error(status)).to_string_lossy().into_owned();
                return Err(err);
            }

            let slice = std::slice::from_raw_parts(out_ptr, out_len);
            let result = slice.to_vec();
            bridge_free_buffer(out_ptr);
            Ok(result)
        }
    }
}

impl Drop for NativeBridge {
    fn drop(&mut self) {
        unsafe {
            if !self.raw.is_null() {
                bridge_free_context(self.raw);
            }
        }
    }
}
```
:::

## 4. Механіка вирівнювання та розкладка пам'яті

Розгляньмо, як структура `BridgeConfig` розміщується в оперативній пам'яті на 64-бітних архітектурах x86_64 та ARM64:

```
Побайтова карта зміщень структури BridgeConfig (розмір 24 байти):
  Байт 0..3:   sample_rate (int32_t, 4 байти)
  Байт 4..7:   channels (int32_t, 4 байти)
  Байт 8..15:  scale_factor (double, 8 байтів, адреса кратна 8)
  Байт 16:     enable_filter (uint8_t, 1 байт)
  Байт 17..23: padding[7] (набивка, 7 байтів для кратності розміру до 8 байтів)
```

Чому наявність явного поля `padding[7]` є критичною? Компілятор C/C++ автоматично доповнює структуру нулями наприкінці, оскільки поле `scale_factor` вимагає 8-байтового вирівнювання, а за правилами стандарту розмір усієї структури (`sizeof`) мусить бути кратним максимальному вирівнюванню її елементів (`alignof(double) = 8`). Завдяки цьому масиви таких структур `BridgeConfig[N]` зберігають правильне вирівнювання для кожного елемента.

Якщо мова-клієнт (наприклад, скрипт на Python або зовнішній серіалізатор) оголосить структуру без урахування цих 7 байтів, розмір структури клієнта становитиме 17 байтів. При передачі покажчика функція C прочитає зміщення коректно, але при спробі передати масив таких структур другий елемент масиву зміститься на 7 байтів відносно очікуваного положення, перетворивши змінні `sample_rate` та `channels` на випадкове сміття.

## 5. Пастка різнорідних алокаторів (CRT Mismatch на Windows)

На операційній системі Windows ця проблема проявляється найбільш гостро через архітектуру бібліотек часу виконання (C Runtime — CRT). Якщо основна програма зібрана з динамічною бібліотекою `ucrtbase.dll`, а сторонній нативний плагін скомпільовано статично з `/MT` (статична лінковка CRT), кожна з них отримує власний незалежний дескриптор купи Win32 (`HANDLE HeapCreate()`).

Коли C-код плагіна викликає `malloc()`, блок виділяється у внутрішній купі плагіна `HeapA`. Якщо клієнтський додаток отримає цей покажчик і викличе для нього функцію `free()` зі свого середовища `HeapB`, диспетчер пам'яті Windows негайно зафіксує звернення до чужої купи через перевірку `_CrtIsValidHeapPointer()` і викличе аварійне завершення `STATUS_HEAP_CORRUPTION` (код `0xC0000374`).

Саме тому золоте правило проектування FFI-інтерфейсів формулюється категорично: **хто виділив ресурс — той його і звільняє**. Клієнтський код ніколи не повинен викликати системний `free()` напряму, а зобов'язаний передати покажчик назад бібліотеці через експортовану функцію `bridge_free_buffer()`.

## 6. Багатопотоковість та блокування GIL у мовах сценаріїв

Під час виклику тривалих обчислювальних функцій через FFI мови з глобальним блокуванням інтерпретатора (такі як Python з GIL) ризикують заблокувати паралельне виконання інших потоків. Бібліотека `ctypes` під час виклику C-функції утримує GIL за замовчуванням. Це означає, що доки функція `bridge_process_buffer()` обробляє масив даних, жоден інший потік Python не зможе виконати навіть одного рядка байткоду.

Для уникнення цього низькорівневі C-бібліотеки або спеціалізовані обгортки (CFFI / Cython) звільняють блокування перед передачею керування:

:::tabs
```c
/* Звільнення блокування інтерпретатора на час важких обчислень (CPython C API) */
Py_BEGIN_ALLOW_THREADS
bridge_process_buffer(ctx, input, count, &out_buf, &out_len);
Py_END_ALLOW_THREADS
```
```cpp
// Ідіоматичне C++ RAII-звільнення GIL (pybind11 або C++ CPython wrapper)
{
    pybind11::gil_scoped_release release_gil;
    bridge_process_buffer(ctx, input, count, &out_buf, &out_len);
}
```
:::

Це повертає операційній системі можливість вільно планувати потоки на різних ядрах процесора, забезпечуючи справжній апаратний паралелізм.

## 7. Апаратне простеження: рух даних по регістрах процесора

Щоб упевнитися, як саме процесор виконує виклик `bridge_process_buffer()`, простежимо стан регістрів загального призначення на архітектурі x86_64 під керуванням System V ABI у момент передачі керування інструкцією `call`:

```
Стан регістрів у момент входу в bridge_process_buffer:
  %rdi  <- 0x7fff5a001000  (1-й аргумент: покажчик на BridgeContext)
  %rsi  <- 0x7fff5a002400  (2-й аргумент: покажчик на вихідний масив input)
  %rdx  <- 0x000000000004  (3-й аргумент: кількість елементів count = 4)
  %rcx  <- 0x7fffffffe100  (4-й аргумент: адреса змінної для out_buf)
  %r8   <- 0x7fffffffe108  (5-й аргумент: адреса змінної для out_count)
  %rsp  <- вирівняно строго по межі 16 байтів перед виконанням call
```

Коли рідна функція завершує виконання, статус повернення `BRIDGE_OK` (число 0) поміщається в регістр `%rax`. Викликач (інтерпретатор Python або рантайм Rust) зчитує `%rax`, перевіряє його на нуль і лише після цього розпаковує отримані за адресами в `%rcx` та `%r8` вихідні дані. Ця послідовність усуває зайві копіювання: нативний код записує виділену адресу безпосередньо у стек клієнта.

## 8. Валідація через AddressSanitizer (ASan)

Для перевірки відсутності витоків пам'яті та подвійних звільнень (англ. *double free*) нативний міст компілюється з увімкненим санітайзером:

```bash
# Збирання бібліотеки з контролем меж пам'яті
gcc -shared -fPIC -fsanitize=address -g bridge_core.c -o libbridge_core.so

# Запуск клієнтського скрипту під контролем ASan
LD_PRELOAD=$(gcc -print-file-name=libasan.so) python test_bridge.py
```

Якщо клієнтський код спробує звернутися до `out_buf` після виклику `bridge_free_buffer()`, AddressSanitizer миттєво перехопить помилку *Use-After-Free* з точним стеком викликів, зупинивши програму до виникнення прихованого пошкодження купи.
