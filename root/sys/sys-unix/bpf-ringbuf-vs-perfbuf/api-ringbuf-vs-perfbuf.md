# 📋 Довідник API та структур даних BPF Ring Buffer та Perf Event Array

Цей довідник описує повний інтерфейсний контракт, хелпери ядра Linux, функції бібліотеки `libbpf`, бітові прапори та детальний топологічний опис структур пам'яті, необхідних для розробки та міграції систем збору подій між картками `BPF_MAP_TYPE_PERF_EVENT_ARRAY` та `BPF_MAP_TYPE_RINGBUF`.

Для забезпечення високої швидкодії та мінімального навантаження на систему обидва механізми спираються на спеціалізовані типи карт BPF (BPF maps), однак конфігурування, виділення пам'яті в ядрі та інтерфейси простору користувача у них суттєво відрізняються.

---

## 1. Специфікація типів карт BPF

Оголошення карт в ядрі Linux виконується за допомогою BTF-визначень (BPF Type Format) у секції `.maps`. BTF надає верифікатору ядра повну інформацію про типи даних та розміри структур під час завантаження ELF-об'єкта.

Карта `BPF_MAP_TYPE_PERF_EVENT_ARRAY` вимагає явного визначення параметрів `key_size` та `value_size`, оскільки вона реалізована у вигляді масиву файлових дескрипторів. Кожен елемент масиву відповідає логічному ядру CPU в системі:
- Параметр `key_size` обов'язково дорівнює `sizeof(int)` і задає індекс процесорного ядра (від `0` до `NR_CPUS - 1`).
- Параметр `value_size` дорівнює `sizeof(int)` і містить файловий дескриптор відкритими буфера підсистеми `perf_event`.
- Параметр `max_entries` визначає кількість елементів у масиві. Якщо вказано `0`, бібліотека `libbpf` під час завантаження скелета автоматично підставляє кількість логічних ядер процесора, отриману з системи.

Натомість карта `BPF_MAP_TYPE_RINGBUF` реалізована як єдиний суцільний кільцевий буфер пам'яті, який розшарюється між усіма ядрами CPU. У зв'язку з цим поняття «ключ-значення» відсутнє:
- Поля `key_size` та `value_size` обов'язково повинні дорівнювати нулю (`0`).
- Єдиним визначним параметром конфігурації є `max_entries`, який визначає загальний розмір корисного навантаження кільцевого буфера у байтах. Цей розмір обов'язково повинен бути кратним розміру сторінки пам'яті системи (зазвичай 4096 байтів) та ступеню двійки (наприклад, 64 КБ, 512 КБ, 4 МБ, 16 МБ).

| Параметр конфігурації | `BPF_MAP_TYPE_PERF_EVENT_ARRAY` | `BPF_MAP_TYPE_RINGBUF` |
| :--- | :--- | :--- |
| **Мінімальна версія ядра Linux** | 4.4+ | 5.8+ |
| **Обов'язкові поля BTF** | `type`, `key_size`, `value_size`, `max_entries` | `type`, `max_entries` |
| **Значення `key_size`** | `sizeof(int)` (індекс CPU) | Не використовується (мусить бути 0) |
| **Значення `value_size`** | `sizeof(int)` (fd `perf_event`) | Не використовується (мусить бути 0) |
| **Значення `max_entries`** | Кількість CPU (або 0 для автовизначення) | Розмір буфера у байтах (кратний PAGE_SIZE та 2ⁿ) |
| **Виділення пам'яті у ядрі** | `max_entries × per_cpu_buffer_size` | Єдиний суцільний блок розміру `max_entries` |
| **Шлях у sysfs/procfs** | `/sys/kernel/debug/tracing/events` | `/sys/fs/bpf` (при пінінгу мапи) |

### Приклад оголошення в BPF-коді (C)

```c
// BPF kernel space - C only (виняток §5 AUTHORING: простір ядра Linux)
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

// 1. Оголошення застарілого Perf Event Array
struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __uint(key_size, sizeof(int));
    __uint(value_size, sizeof(int));
    __uint(max_entries, 0); // 0 означає автовизначення за кількістю ядер CPU
} perf_map SEC(".maps");

// 2. Оголошення сучасного BPF Ring Buffer
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 1024 * 1024); // 1 МБ заповнюваного буфера для всіх CPU
} ringbuf_map SEC(".maps");
```

---

## 2. Хелпери ядра (Kernel Helper Functions)

Виклики хелперів ядра з BPF-програми здійснюють передачу сформованих подій з простору ядра у кільцеві буфери. Кожен хелпер має власні умови виклику, вимоги до вирівнювання та коди повернення.

### 2.1 Хелпери для Perf Event Array

#### `bpf_perf_event_output`
```c
long bpf_perf_event_output(void *ctx, void *map, u64 flags, void *data, u64 size);
```
Функція `bpf_perf_event_output` виконує скопіювання пам'яті з тимчасового буфера BPF-програми у кільцевий буфер підсистеми `perf`, прив'язаний до поточного логічного процесора.

Детальний аналіз аргументів:
- `ctx`: Вказівник на контекст виконання BPF-програми (`struct pt_regs *`, `struct __sk_buff *`, `struct trace_event_raw_sys_enter *` тощо). Контекст необхідний ядру для вилучення додаткової регістрової інформації або зрізу мережевого пакета.
- `map`: Вказівник на раніше оголошену карту `BPF_MAP_TYPE_PERF_EVENT_ARRAY`.
- `flags`: 64-бітне поле бітових прапорів. Нижнє 32-бітне слово визначає індекс CPU, у буфер якого буде записано подію. Спеціальне значення `BPF_F_CURRENT_CPU` (`0xffffffffULL`) вказує ядру автоматично обрати поточний логічний процесор. Верхні 32 біти можуть містити розмір даних для автоматичного захоплення початкового заголовка мережевого пакета.
- `data`: Вказівник на область пам'яті (зазвичай розміщену на стеку BPF або у Per-CPU масиві), де заповнено структуру події.
- `size`: Розмір даних у байтах для копіювання (не може перевищувати розмір структури).

Повертане значення: `0` у разі успішного запису; у разі помилки повертається від'ємний код помилки ядра:
- `-ENOENT`: Карта не містить валідного файлового дескриптора `perf_event` для даного CPU.
- `-ENOSPC`: Кільцевий буфер поточного CPU повністю заповнений (відбулася втрата події).
- `-EINVAL`: Невалідні прапори або непідтримуваний розмір даних.

---

### 2.2 Хелпери для BPF Ring Buffer

#### `bpf_ringbuf_reserve`
```c
void *bpf_ringbuf_reserve(void *ringbuf, u64 size, u64 flags);
```
Функція `bpf_ringbuf_reserve` здійснює атомарне резервування області пам'яті всередині спільного кільцевого буфера. На відміну від `perfbuf`, вона не виконує копіювання даних, а повертає вказівник на виділений слот пам'яті безпосередньо у буфері ядра.

Детальний аналіз аргументів та механізму:
- `ringbuf`: Вказівник на карту `BPF_MAP_TYPE_RINGBUF`.
- `size`: Запитуваний розмір події у байтах. Ядро автоматично додає 8-байтовий заголовок запису `struct bpf_ringbuf_hdr` та вирівнює підсумковий розмір слота до межі 8 байтів.
- `flags`: Зарезервовано для майбутніх розширень ядерного API (мусить дорівнювати `0`).
- Повертане значення: Прямий вказівник на зарезервовану область пам'яті всередині буфера ядра, або `NULL`, якщо буфер переповнений.
- Критичний нюанс: З моменту успішного повернення вказівника до виклику `bpf_ringbuf_submit` або `bpf_ringbuf_discard`, зарезервований слот перебуває у заблокованому стані `BPF_RINGBUF_BUSY_BIT`. Якщо програма завершиться без виклику цих функцій, буфер блокується назавжди.

#### `bpf_ringbuf_submit`
```c
void bpf_ringbuf_submit(void *data, u64 flags);
```
Функція `bpf_ringbuf_submit` знімає прапор `BPF_RINGBUF_BUSY_BIT` з раніше зарезервованого слота та робить подію доступною для прочитання споживачем у просторі користувача.

Аргументи та прапори:
- `data`: Вказівник на область пам'яті, раніше отриманий викликом `bpf_ringbuf_reserve`.
- `flags`: Бітові прапори управління сповіщеннями користувацького процесу:
  - `BPF_RB_NO_WAKEUP`: Забороняє надсилання сигналу розбудження `epoll` демону простору користувача. Використовується при високоінтенсивному потоці подій, коли демон сам активно опитує буфер.
  - `BPF_RB_FORCE_WAKEUP`: Примусово надсилає сигнал розбудження незважаючи на рівень заповнення буфера та стан поллінгу.
  - `0`: Адаптивний режим ядра (сигнал відправляється лише якщо демон заснув у виклику `epoll_wait`).

#### `bpf_ringbuf_discard`
```c
void bpf_ringbuf_discard(void *data, u64 flags);
```
Функція `bpf_ringbuf_discard` позначає зарезервований слот прапором `BPF_RINGBUF_DISCARD_BIT`. Вона застосовується у випадках, коли під час заповнення структури події BPF-програма з'ясувала, що подія не підлягає відправці (наприклад, процес не пройшов фільтрацію за UID або розширенням файла). Читач у просторі користувача прозоро пропустить цей слот, просунувши вказівник читання далі без виклику користувацького callback-обробника.

#### `bpf_ringbuf_output`
```c
long bpf_ringbuf_output(void *ringbuf, void *data, u64 size, u64 flags);
```
Зручна функція-обгортка, яка послідовно викликає `bpf_ringbuf_reserve`, виконує копіювання `memcpy(&dest, data, size)` та викликає `bpf_ringbuf_submit`. Ця функція створена для забезпечення прямої сумісності з `bpf_perf_event_output`, коли дані вже зібрані в окремому скретчпаді.

---

## 3. Топологія пам'яті та бітові прапори Ring Buffer

Кожен запис у BPF Ring Buffer обов'язково вирівнюється на межу 8 байтів і передується 8-байтовим заголовком `struct bpf_ringbuf_hdr`.

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|B|D|                   LEN (30 bits)                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       PAYLOAD DATA...                         |
|                       (aligned to 8 bytes)                    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### Бітові маски та розшифровка заголовка

Для інтерпретації старших бітів заголовка ядро та бібліотека `libbpf` використовують наступні маски:

- `BPF_RINGBUF_BUSY_BIT` (`1U << 31` або `0x80000000`): Найстарший біт 31. Якщо встановлений, слот перебуває у процесі заповнення BPF-програмою. Споживач припиняє читання на цьому слоті до зняття біта.
- `BPF_RINGBUF_DISCARD_BIT` (`1U << 30` або `0x40000000`): Біт 30. Якщо встановлений, подія скасована. Споживач пропускає payload розміром `LEN` байтів.
- `BPF_RINGBUF_HDR_SZ` (`8` байтів): Константний розмір заголовка запису в байтах.
- `LEN` (`len & 0x3FFFFFFF`): Молодші 30 бітів, що визначають фактичну довжину корисних даних у байтах (до 1 ГБ).

### Структура сторінки керування ядра (`producer_page`)

На самому початку мапінгу пам'яті кільцевого буфера розміщується сторінка керування метаданими, доступна для зчитування з простору користувача:

```c
struct bpf_ringbuf_page_hdr {
    unsigned long producer_pos; // 64-бітний абсолютний лічильник зарезервованих байтів (модифікує ядро/BPF)
    unsigned long consumer_pos; // 64-бітний абсолютний лічильник прочитаних байтів (модифікує user space)
};
```

Різниця `producer_pos - consumer_pos` визначає поточний обсяг невичитаних даних у буфері. Для синхронізації доступу між ядрами та простором користувача ядро використовує бар'єри пам'яті `smp_wmb()` та `smp_rmb()`.

---

## 4. API простору користувача (libbpf)

Бібліотека `libbpf` забезпечує високорівневі абстракції для управління буферами у просторі користувача.

:::tabs
```c
// C API (libbpf)
#include <stdio.h>
#include <stdlib.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

// 1. Callback обробника події для Perf Buffer
static void handle_perf_event(void *ctx, int cpu, void *data, __u32 size) {
    const char *msg = (const char *)data;
    printf("[Perfbuf CPU %d] Event size %u: %s\n", cpu, size, msg);
}

// 2. Callback обробника події для Ring Buffer (без CPU аргументу!)
static int handle_ring_event(void *ctx, void *data, size_t size) {
    const char *msg = (const char *)data;
    printf("[Ringbuf Total Order] Event size %zu: %s\n", size, msg);
    return 0; // Повертає 0 для продовження поллінгу
}

int setup_buffers(int perf_map_fd, int ring_map_fd) {
    // Налаштування Perf Buffer
    struct perf_buffer_opts pb_opts = {};
    pb_opts.sample_cb = handle_perf_event;
    struct perf_buffer *pb = perf_buffer__new(perf_map_fd, 8 /* pages per CPU */, &pb_opts);
    if (!pb) {
        fprintf(stderr, "Failed to create perf buffer\n");
        return -1;
    }

    // Налаштування Ring Buffer
    struct ring_buffer *rb = ring_buffer__new(ring_map_fd, handle_ring_event, NULL, NULL);
    if (!rb) {
        fprintf(stderr, "Failed to create ring buffer\n");
        perf_buffer__free(pb);
        return -1;
    }

    // Цикл поллінгу під час обробки подій
    int err = ring_buffer__poll(rb, 100 /* timeout_ms */);
    
    ring_buffer__free(rb);
    perf_buffer__free(pb);
    return err;
}
```
```cpp
// C++20 Ідіоматичний API (libbpf з RAII та std::span)
#include <iostream>
#include <memory>
#include <span>
#include <string_view>
#include <expected>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

namespace ebpf {

// RAII обгортка для ring_buffer
class RingBuffer {
public:
    using EventCallback = std::function<void(std::span<const std::byte>)>;

    static std::expected<RingBuffer, std::string> create(int map_fd, EventCallback cb) {
        auto cb_holder = std::make_unique<EventCallback>(std::move(cb));
        
        auto raw_cb = [](void *ctx, void *data, size_t size) -> int {
            auto *fn = static_cast<EventCallback*>(ctx);
            auto payload = std::span<const std::byte>(
                reinterpret_cast<const std::byte*>(data), size
            );
            (*fn)(payload);
            return 0;
        };

        ring_buffer *rb = ring_buffer__new(map_fd, raw_cb, cb_holder.get(), nullptr);
        if (!rb) {
            return std::unexpected("Failed to allocate ring_buffer in libbpf");
        }

        return RingBuffer(rb, std::move(cb_holder));
    }

    ~RingBuffer() {
        if (rb_) {
            ring_buffer__free(rb_);
        }
    }

    RingBuffer(const RingBuffer&) = delete;
    RingBuffer& operator=(const RingBuffer&) = delete;

    RingBuffer(RingBuffer&& other) noexcept 
        : rb_(std::exchange(other.rb_, nullptr)), 
          cb_holder_(std::move(other.cb_holder_)) {}

    int poll(int timeout_ms) {
        return ring_buffer__poll(rb_, timeout_ms);
    }

    int consume() {
        return ring_buffer__consume(rb_);
    }

    int epoll_fd() const noexcept {
        return ring_buffer__epoll_fd(rb_);
    }

private:
    RingBuffer(ring_buffer *rb, std::unique_ptr<EventCallback> cb)
        : rb_(rb), cb_holder_(std::move(cb)) {}

    ring_buffer *rb_{nullptr};
    std::unique_ptr<EventCallback> cb_holder_;
};

} // namespace ebpf
```
:::

---

## 5. Порівняльна матриця викликів та функцій

| Задача в коді | Звільнений `perfbuf` API | Сучасний `ringbuf` API |
| :--- | :--- | :--- |
| **Резервування пам'яті в ядрі** | Неможливо (тільки стек BPF) | `bpf_ringbuf_reserve(map, sz, flags)` |
| **Надсилання даних з ядра** | `bpf_perf_event_output(ctx, map, cpu, data, sz)` | `bpf_ringbuf_submit(data, flags)` |
| **Скасування надсилання** | Неможливо після виклику | `bpf_ringbuf_discard(data, flags)` |
| **Створення об'єкта в User Space** | `perf_buffer__new(fd, page_cnt, &opts)` | `ring_buffer__new(fd, sample_cb, ctx, opts)` |
| **Додавання додаткової карти** | `perf_buffer__add(pb, map_fd, sample_cb)` | `ring_buffer__add(rb, map_fd, sample_cb)` |
| **Поллінг нових подій** | `perf_buffer__poll(pb, timeout_ms)` | `ring_buffer__poll(rb, timeout_ms)` |
| **Зчитування без очікування (drain)** | `perf_buffer__consume(pb)` | `ring_buffer__consume(rb)` |
| **Отримання файлового дескриптора epoll** | Не підтримується напряму | `ring_buffer__epoll_fd(rb)` |
| **Очищення ресурсів** | `perf_buffer__free(pb)` | `ring_buffer__free(rb)` |
