# ⚙️ Архітектура та реалізація гібридного BPF/Rust планувальника scx_rustland

Цей проектний матеріал розкриває практичний устрій, внутрішні механізми та вихідний код гібридного планувальника `scx_rustland`. Головна інженерна ідея `scx_rustland` полягає у винесенні логіки прийняття рішень щодо вибору процесів із ядра у демон простору користувача мовою Rust, де BPF-програма виконує роль високошвидкісного транспорту та шини подій.

---

## 1. Архітектурна ідея гібридного планування

Традиційні BPF-планувальники виконують 100% обчислень усередині BPF-програми у просторі ядра. Це забезпечує наносекундні затримки, але накладає суворі обмеження: BPF-верифікатор блокує складні циклічні структури, виділення довільної динамічної пам'яті та використання сторонніх системних бібліотек.

`scx_rustland` демонструє альтернативний гібридний підхід:
1. **Ядерний BPF-шар** перехоплює ядрові події `enqueue`, `dequeue` та `dispatch`. Замість того, щоб самостійно вирішувати долю процесу, BPF-код упаковує параметр події у структуру і відправляє сповіщення через `BPF Ring Buffer` у простір користувача.
2. **Користувацький демон (Rust)** зчитує події з кільцевого буфера, підтримує власну чергу чи впорядковане дерево задач (наприклад, `BTreeMap` — B-дерево зі стандартної бібліотеки Rust — або купу з пріоритетами `BinaryHeap`) і розраховує оптимальний порядок виконання процесів.
3. **Запис рішень у BPF Map**: Демон простору користувача записує обрані пари `(cpu -> pid)` у спеціальну BPF-карту типу `BPF_MAP_TYPE_ARRAY` або `HASH`.
4. **Ядрова відправка (`dispatch`)**: Коли ядро Linux викликає хук `dispatch` для вільного процесора, BPF-програма вичитає рішення з BPF Map і миттєво відправляє обрану задачу в локальну чергу `SCX_DSQ_LOCAL`.

```
[Ядро: Task Wakes] ──(enqueue)──> [BPF Ring Buffer] ──> [Rust User Daemon]
                                                               │
                                                       (Прийняття рішення)
                                                               │
[Ядро: CPU Idle] <──(dispatch)─── [BPF Map / Decision] <───────┘
```

Така розширюваність дозволяє реалізовувати алгоритми планування будь-якої складності, включно з урахуванням зовнішніх системних метрик — від температури пакета до статистики вводу-виводу.

---

## 2. Kernel-side BPF Код (`scx_rustland.bpf.c`)

Ядрова BPF-програма реалізує мінімальні callbacks для обробки подій та обміну даними через BPF maps та кільцевий буфер.

```c
#include <scx/common.bpf.h>

char _license[] SEC("license") = "GPL";

// Структура події, що передається через Ring Buffer у User Space
struct task_queued_event {
    s32 pid;
    s32 cpu;
    u64 flags;
};

// BPF Ring Buffer для передачі подій у простір користувача
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} event_ringbuf SEC(".maps");

// BPF Array для збереження обраного PID для кожного виконуючого CPU
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 1024); // Підтримка до 1024 ядер CPU
    __type(key, u32);
    __type(value, s32);
} cpu_decision_map SEC(".maps");

s32 BPF_STRUCT_OPS(rustland_select_cpu, struct task_struct *p, s32 prev_cpu, u64 wake_flags)
{
    // Зауваження: Повертаємо попередній CPU як підказку ядра
    return prev_cpu;
}

void BPF_STRUCT_OPS(rustland_enqueue, struct task_struct *p, u64 enq_flags)
{
    struct task_queued_event *ev;

    // Резервуємо слот у кільцевому буфері подій
    ev = bpf_ringbuf_reserve(&event_ringbuf, sizeof(*ev), 0);
    if (!ev) {
        // Якщо буфер переповнено, аварійно відправляємо задачу в глобальну чергу ядра
        scx_bpf_dispatch(p, SCX_DSQ_GLOBAL, SCX_SLICE_DFL, enq_flags);
        return;
    }

    ev->pid = p->pid;
    ev->cpu = scx_bpf_task_cpu(p);
    ev->flags = enq_flags;

    // Публікуємо подію для демона у просторі користувача
    bpf_ringbuf_submit(ev, 0);
}

void BPF_STRUCT_OPS(rustland_dispatch, s32 cpu, struct task_struct *prev)
{
    u32 key = cpu;
    s32 *target_pid;
    struct task_struct *p;

    // Вичитати рішення демона Rust для поточного процесора
    target_pid = bpf_map_lookup_elem(&cpu_decision_map, &key);
    if (target_pid && *target_pid > 0) {
        p = bpf_task_from_pid(*target_pid);
        if (p) {
            // Рішення є: кладемо саме цю задачу в локальну DSQ цього CPU
            scx_bpf_dispatch(p, SCX_DSQ_LOCAL, SCX_SLICE_DFL, 0);
            bpf_task_release(p);
        }
        // Комірку звільняємо лише після спроби диспетчеризації
        *target_pid = 0;
    }

    // Вичитуємо чергу ядра для забезпечення постійного просування задач
    scx_bpf_consume(SCX_DSQ_GLOBAL);
}

SEC(".struct_ops.link")
struct sched_ext_ops rustland_ops = {
    .select_cpu = (void *)rustland_select_cpu,
    .enqueue    = (void *)rustland_enqueue,
    .dispatch   = (void *)rustland_dispatch,
    .name       = "rustland",
};
```

---

## 3. User-side Демон у просторі користувача (Rust та C++)

Демон простору користувача зчитує події з кільцевого буфера, накопичує стан задач та регулярно оновлює карту рішень BPF. Для забезпечення переносності подано реалізації мовами Rust та C++.

:::tabs
```rust
// Rust Daemon: цикл демона на libbpf-rs
// (у справжньому scx_rustland цю обв'язку дає crate scx_rustland_core
//  з типом BpfScheduler, який ховає і кільцевий буфер, і карту рішень)
use anyhow::Result;
use libbpf_rs::{Map, MapCore, MapFlags, RingBufferBuilder};
use std::collections::VecDeque;
use std::sync::mpsc;
use std::time::Duration;

#[repr(C)]
struct TaskQueuedEvent {
    pid: i32,
    cpu: i32,
    flags: u64,
}

fn run(ringbuf_map: &Map, decision_map: &Map) -> Result<()> {
    let mut task_queue: VecDeque<i32> = VecDeque::new();
    let (tx, rx) = mpsc::channel::<i32>();

    // Обробник кільцевого буфера лише перекидає pid у канал демона:
    // усе впорядкування робиться поза ним
    let mut builder = RingBufferBuilder::new();
    builder.add(ringbuf_map, move |data: &[u8]| {
        if data.len() >= std::mem::size_of::<TaskQueuedEvent>() {
            let ev = unsafe { &*(data.as_ptr() as *const TaskQueuedEvent) };
            let _ = tx.send(ev.pid);
        }
        0
    })?;
    let ringbuf = builder.build()?;

    println!("[scx_rustland] Демон користувача Rust успішно запущено.");

    loop {
        // 1. Вичитати накопичені події enqueue
        ringbuf.poll(Duration::from_millis(1))?;
        while let Ok(pid) = rx.try_recv() {
            task_queue.push_back(pid);
        }

        // 2. Записати рішення для вільного CPU у cpu_decision_map
        if let Some(pid) = task_queue.pop_front() {
            let cpu: u32 = 0; // тут стоїть вибір CPU власним алгоритмом
            decision_map.update(&cpu.to_ne_bytes(), &pid.to_ne_bytes(), MapFlags::ANY)?;
        }
    }
}
```
```cpp
// C++ User Daemon (Реалізація через libbpf C++ wrapper та RAII)
#include <iostream>
#include <vector>
#include <deque>
#include <thread>
#include <chrono>
#include <csignal>
#include <memory>

struct TaskQueuedEvent {
    int32_t pid;
    int32_t cpu;
    uint64_t flags;
};

class RustlandUserDaemon {
private:
    std::deque<int32_t> task_queue_;
    bool running_{true};

public:
    void run() {
        std::cout << "[scx_rustland_cpp] C++ Демон користувача запущено.\n";
        while (running_) {
            if (!task_queue_.empty()) {
                int32_t next_pid = task_queue_.front();
                task_queue_.pop_front();
                // Запис обраного PID у BPF map через bpf_map_update_elem()
            }
            std::this_thread::sleep_for(std::chrono::microseconds(500));
        }
    }

    void stop() { running_ = false; }
};

int main() {
    RustlandUserDaemon daemon;
    daemon.run();
    return 0;
}
```
:::

---

## 4. Механізм обробки подій та керування станом у демоні

Простір користувача отримує події про зміну стану процесів асинхронно через кільцевий буфер `BPF Ring Buffer`. Демон підтримує власну таблицю процесів у пам'яті `ProcessTable`, де зберігається точна інформація про поточний стан кожного потоку в системі.

### 4.1. Модель стану задач у просторі користувача
Кожен потік перебуває в одному з трьох основних станів усередині структури Rust:
1. **Queued (В черзі готовності)**: Потік отримав сповіщення `enqueue` від ядра, але ще не призначений ні на один з виконуючих процесорів.
2. **Running (Виконується)**: Потік обраний демоном і записаний у BPF-карту `cpu_decision_map`.
3. **Sleeping / Blocked (Заблокований)**: Потік вилучено з черги через виклик `dequeue` (наприклад, очікування блокування файла або сокета).

При отриманні нової події `TaskQueuedEvent` демон оновлює відповідний запис у пам'яті. Якщо потік прокинувся, він вміщується у відповідну категорію черги пріоритетів.

### 4.2. Алгоритм формування розкладу у Rust
Основний цикл демона Rust зчитує доступні події з буфера і періодично викликає внутрішній планувальник `schedule_tasks()`.
- Демон ітерується по списку вільних або незабаром вільних процесорів у системі.
- Для кожного CPU з черги зчитується потік із найвищим пріоритетом.
- Обраний `pid` записується в BPF-карту `cpu_decision_map` через `bpf_map_update_elem()` — обгортку libbpf над системним викликом `bpf(2)`.

---

## 5. Глибокий аналіз затримок та крайові випадки

Гібридна архітектура вимагає ретельного аналізу потенційних проблем продуктивності та надійності.

### 5.1. Витрати на перемикання контексту та затримки IPC
Передача кожної події з ядра у простір користувача додає затримку перемикання контексту та виклику `poll`/`epoll`. Порядки величин такі:
- Сама передача події через `BPF Ring Buffer` коштує сотні наносекунд.
- Головна ціна — пробудження демона простору користувача та вичитання події: одиниці мікросекунд, і залежать вони від завантаженості системи.

Саме тому `scx_rustland` не застосовується для задач високочастотного трейдингу (HFT), але є ідеальним для настільних ПК, де мікросекундний оверхед є непомітним для людини, а гнучке планування між E-cores та P-cores дає вирішальну перевагу.

### 5.2. Переповнення кільцевого буфера (Ring Buffer Overflow)
Якщо демон простору користувача затримується (наприклад, через високе навантаження на систему), кільцевий буфер подій може заповнитися до межі.
- **Стратегія захисту**: У функції `rustland_enqueue` перевіряється результат виклику `bpf_ringbuf_reserve()`. Якщо повертається `NULL`, BPF-програма миттєво відправляє задачу в `SCX_DSQ_GLOBAL`. Це запобігає зависанню або втраті задач у ядрі.

### 5.3. Аварійна зупинка демона (Process Crash Recovery)
Якщо демон у просторі користувача падає через виключення або вбивається системним OOM Killer, BPF-карта рішень припиняє оновлюватися. У цьому випадку спрацьовує ядровий **watchdog timer** `sched_ext`: коли задачі перестають просуватися довше за тайм-аут (стеля й типове значення — 30 секунд), ядро розриває зв'язок із BPF-планувальником і безпечно повертає всі процеси системи під управління класичного EEVDF.

### 5.4. Налагодження та моніторинг BPF-карт
Для перевірки стану BPF-карт `scx_rustland` у реальному часі використовуються системні інструменти Linux:

```bash
# Дамп стану карти рішень BPF за допомогою bpftool
bpftool map dump name cpu_decision_map

# Перевірка вмісту кільцевого буфера через trace_pipe
cat /sys/kernel/debug/tracing/trace_pipe | grep rustland
```

---

## 6. Практичне профілювання та вимірювання продуктивності

Під час тестування гібридного планувальника `scx_rustland` на настільних системах із процесорами Intel Alder Lake (архітектура з P-cores та E-cores) було проведено серію вимірювань за допомогою `perf` та вбудованої статистики планувальника (`--stats`):

1. **Вимірювання частоти перемикання контексту**: Виклик `perf stat -e context-switches,cpu-migrations -a -- sleep 10` показує помітно менше між'ядерних міграцій, ніж стандартний EEVDF. Це пояснюється тим, що демон Rust утримує процеси однієї групи на продуктивних P-ядрах.
2. **Накладні витрати демона**: Демон Rust тримається в межах відсотка процесорного часу й десятка мебібайтів пам'яті — на тлі системних служб це майже непомітно.
3. **Пропускна здатність Ring Buffer**: Кільцевий буфер eBPF розрахований на потік у мільйони подій за секунду: резервування слота — це одна атомарна операція, без блокувань і без копіювання даних.

