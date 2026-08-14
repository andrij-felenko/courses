# ⚙️ Практична лабораторія: виявлення та ліквідація перегонів у модулі ядра

У цьому проекті ми розберемо повний практичний цикл діагностики, аналізу та виправлення станів перегонів (data races) у коді ядра Linux. Ми створимо навчальний модуль ядра з навмисно введеною помилкою несинхронізованого доступу до спільного стану, протестуємо його під моніторингом KCSAN, детально розберемо згенерований дамп `dmesg` та покажемо, як правильно анотувати код за допомогою макросів `READ_ONCE`, `WRITE_ONCE` та `ASSERT_EXCLUSIVE_WRITER`.

У другій частині ми реалізуємо повноцінну програму простору користувача мовами C та C++, яка продемонструє еквівалентні механізми атомарної синхронізації та впорядкування пам'яті (memory ordering).

---

## 1. Створення модуля ядра з несинхронізованим доступом

Розглянемо поширений випадок у драйверах системних пристроїв: один ядерний потік (`writer_thread`) відповідає за оновлення статусу пристрою та лічильника оброблених подій, а другий потік (`reader_thread`) здійснює моніторинг стану з іншого ядра CPU без використання важких м'ютексів чи спінлоків.

У нашому початковому модулі структура `shared_device_state` виділяється у динамічній пам'яті ядра через `kzalloc()`. Потік-письменник періодично інкрементує лічильник пакетів `packets_counter`, оновлює час останньої модифікації `last_update_jiffies` та виставляє прапорець готовності `is_ready = 1`. При цьому всі операції виконуються за допомогою звичайного сирого доступу через вказівник C, без жодного використання атомарних макросів чи бар'єрів пам'яті.

Це спричиняє дві фундаментальні проблеми паралелізму. По-перше, звичайний інкремент `global_dev->packets_counter++` розпадається на інструкції зчитування, модифікації та запису (load-modify-store), що призводить до втрати оновлень під час конфліктних звернень. По-друге, компілятор C має право поміняти місцями записи `global_dev->packets_counter++` та `global_dev->is_ready = 1`, у результаті чого потік-читач може побачити прапорець `is_ready == 1` ще до того, як нове значення лічильника буде записане у пам'ять.

Якщо проаналізувати машинний код, згенерований компілятором для немодифікованої функції `writer_thread_func` за допомогою утиліти `objdump -d kcsan_demo.o`, ми побачимо звичайні інструкції `movl %eax, (%rdi)`, які відправляються у буфер запису процесора без будь-яких префіксів `lock` чи апаратних бар'єрів `mfence`. Це робить операції абсолютно незахищеними від міжпроцесорного перевпорядкування.

### 1.1. Сирцевий код модуля з помилкою перегонів (`kcsan_demo.c`)

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/kthread.h>
#include <linux/delay.h>
#include <linux/slab.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Observability Course");
MODULE_DESCRIPTION("KCSAN Data Race Demonstration Module");

static struct task_struct *writer_task;
static struct task_struct *reader_task;

/* Спільна структура даних між двома потоками ядра */
struct shared_device_state {
    int packets_counter;
    int is_ready;
    unsigned long last_update_jiffies;
};

static struct shared_device_state *global_dev;

/* Потік-письменник: оновлює лічильник та прапорці без блокувань */
static int writer_thread_func(void *arg)
{
    pr_info("kcsan_demo: Writer thread started on CPU %d\n", smp_processor_id());

    while (!kthread_should_stop()) {
        if (global_dev) {
            /* ПОМИЛКА: Несинхронізований звичайний запис у спільну пам'ять */
            global_dev->packets_counter++;
            global_dev->last_update_jiffies = jiffies;
            
            /* Імітація паузи перед встановленням прапорця готовності */
            udelay(5);
            global_dev->is_ready = 1;
        }
        msleep(20);
    }
    return 0;
}

/* Потік-читач: перевіряє прапорець та зчитує лічильник */
static int reader_thread_func(void *arg)
{
    pr_info("kcsan_demo: Reader thread started on CPU %d\n", smp_processor_id());

    while (!kthread_should_stop()) {
        if (global_dev) {
            /* ПОМИЛКА: Несинхронізоване читання прапорця та даних */
            if (global_dev->is_ready) {
                int count = global_dev->packets_counter;
                if (count % 100 == 0) {
                    pr_info("kcsan_demo: Milestone reached: %d packets\n", count);
                }
            }
        }
        msleep(15);
    }
    return 0;
}

static int __init kcsan_demo_init(void)
{
    pr_info("kcsan_demo: Initializing module and allocating state...\n");

    global_dev = kzalloc(sizeof(*global_dev), GFP_KERNEL);
    if (!global_dev)
        return -ENOMEM;

    /* Запуск двох потоків ядра */
    writer_task = kthread_run(writer_thread_func, NULL, "kcsan_writer_thread");
    if (IS_ERR(writer_task)) {
        pr_err("kcsan_demo: Failed to create writer thread\n");
        kfree(global_dev);
        return PTR_ERR(writer_task);
    }

    reader_task = kthread_run(reader_thread_func, NULL, "kcsan_reader_thread");
    if (IS_ERR(reader_task)) {
        pr_err("kcsan_demo: Failed to create reader thread\n");
        kthread_stop(writer_task);
        kfree(global_dev);
        return PTR_ERR(reader_task);
    }

    pr_info("kcsan_demo: Both threads running successfully\n");
    return 0;
}

static void __exit kcsan_demo_exit(void)
{
    pr_info("kcsan_demo: Stopping threads and unloading...\n");

    if (writer_task)
        kthread_stop(writer_task);
    if (reader_task)
        kthread_stop(reader_task);

    kfree(global_dev);
    pr_info("kcsan_demo: Module unloaded cleanly\n");
}

module_init(kcsan_demo_init);
module_exit(kcsan_demo_exit);
```

---

## 2. Інструкція зі збірки, запуску та аналізу звітів

Для проведения експерименту та збірки даного модуля необхідне ядро Linux, зібране з увімкненим прапорцем конфігурації `CONFIG_KCSAN=y`. Використовуйте стандартний `Makefile` для збірки за межами дерева сирцевих текстів ядра (Out-of-tree module build).

### 2.1. Створення Makefile

Створіть файл `Makefile` у теці з сирцевими файлами модуля:

```makefile
obj-m += kcsan_demo.o

KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	make -C $(KDIR) M=$(PWD) modules

clean:
	make -C $(KDIR) M=$(PWD) clean
```

### 2.2. Запуск та фіксація результатів у dmesg

Процес тестування складається з наступних послідовних кроків. Спочатку за допомогою команди `make` виконується компіляція модуля. Потім отриманий файл `kcsan_demo.ko` завантажується у систему через утиліту `insmod`.

```bash
make
sudo insmod kcsan_demo.ko
```

Одразу після завантаження підсистема KCSAN починає семплювати доступи до пам'яті з боку створених потоків `kcsan_writer_thread` та `kcsan_reader_thread`. Під час одного зі шляхів вибірки KCSAN встановить watchpoint на адресу `global_dev->packets_counter` і призупинить потік-письменник на 80 мікросекунд через `udelay()`. У цей самий момент потік-читач виконує перевірку прапорця `is_ready` та доступ до лічильника. KCSAN виявить конфлікт доступів та негайно виведе звіт у системний журнал `dmesg`.

Для перегляду згенерованого звіту виконайте команду:
```bash
dmesg | tail -n 40
```

Ви побачите структуроване повідомлення KCSAN:

```text
==================================================================
BUG: KCSAN: data-race in reader_thread_func / writer_thread_func

write to 0xffff888102a49000 of 4 bytes by task 2841 on cpu 1:
 writer_thread_func+0x34/0x80 [kcsan_demo]
 kthread+0x118/0x140
 ret_from_fork+0x1f/0x30

read to 0xffff888102a49000 of 4 bytes by task 2842 on cpu 2:
 reader_thread_func+0x2a/0x70 [kcsan_demo]
 kthread+0x118/0x140
 ret_from_fork+0x1f/0x30

value changed: 0x0000000e -> 0x0000000f

Reported by Kernel Concurrency Sanitizer on:
CPU: 2 PID: 2842 Comm: kcsan_reader_thr Tainted: G        W         5.15.0-kcsan #1
==================================================================
```

Аналіз отриманого дампа деталізує чотири ключові деталі:
1. Адреса конфліктної комірки пам'яті у просторі ядра: `0xffff888102a49000`.
2. Операція 1: Запис 4 байтів на CPU 1 у функції `writer_thread_func` (потік `kcsan_writer_thread`).
3. Операція 2: Паралельне читання 4 байтів на CPU 2 у функції `reader_thread_func` (потік `kcsan_reader_thread`).
4. Зміна значення під час штучної затримки `udelay()`: `0x0e -> 0x0f`.

---

## 3. Виправлення модуля: Анотування та твердження виключності

Для належного усунення перегонів та захисту від компіляторного перевпорядкування інструкцій застосуємо три важливі механізми синхронізації ядра:

1. Макроси `READ_ONCE()` та `WRITE_ONCE()` для атомарного зчитування та запису лічильника `packets_counter`. Вони гарантують використання атомарної ширини слова при збереженні та запобігають оптимізаційному складанню записів компілятором.
2. Макроси впорядкування пам'яті `smp_store_release()` та `smp_load_acquire()` для публікації та зчитування прапорця `is_ready`. Операція `smp_store_release()` встановлює бар'єр публікації (Release barrier): вона гарантує, що всі попередні записи у пам'ять (включаючи інкремент лічильника) стануть видимими для інших ядер CPU **суворо до того**, як прапорець `is_ready` набуде значення `1`. Відповідно, `smp_load_acquire()` створює бар'єр отримання (Acquire barrier), що забороняє виконувати читання наступних даних до завершення зчитування прапорця.
3. Твердження `ASSERT_EXCLUSIVE_WRITER(global_dev->packets_counter)` для динамічної перевірки контракту єдиного письменника. Якщо інший розробник у майбутньому додасть другий потік, який намагатиметься писати в цю саму змінну, KCSAN згенерує звіт про помилку.

### Виправлений сирцевий код (`kcsan_demo_fixed.c`)

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/kthread.h>
#include <linux/delay.h>
#include <linux/slab.h>
#include <linux/compiler.h>
#include <linux/kcsan-checks.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Observability Course");
MODULE_DESCRIPTION("KCSAN Data Race Fixed Demo Module");

static struct task_struct *writer_task;
static struct task_struct *reader_task;

struct shared_device_state {
    int packets_counter;
    int is_ready;
    unsigned long last_update_jiffies;
};

static struct shared_device_state *global_dev;

static int writer_thread_func_fixed(void *arg)
{
    while (!kthread_should_stop()) {
        if (global_dev) {
            /* 1. Твердження: Лише цей потік має право змінювати packets_counter */
            ASSERT_EXCLUSIVE_WRITER(global_dev->packets_counter);

            int current_cnt = READ_ONCE(global_dev->packets_counter);
            
            /* 2. Атомарний маркований запис */
            WRITE_ONCE(global_dev->packets_counter, current_cnt + 1);
            WRITE_ONCE(global_dev->last_update_jiffies, jiffies);
            
            /* 3. Упорядковане встановлення прапорця готовності */
            smp_store_release(&global_dev->is_ready, 1);
        }
        msleep(20);
    }
    return 0;
}

static int reader_thread_func_fixed(void *arg)
{
    while (!kthread_should_stop()) {
        if (global_dev) {
            /* 1. Впорядковане читання прапорця із семантикою Acquire */
            if (smp_load_acquire(&global_dev->is_ready)) {
                /* 2. Марковане читання лічильника */
                int count = READ_ONCE(global_dev->packets_counter);
                if (count % 100 == 0) {
                    pr_info("kcsan_demo_fixed: Safe read milestone: %d\n", count);
                }
            }
        }
        msleep(15);
    }
    return 0;
}

static int __init kcsan_demo_fixed_init(void)
{
    pr_info("kcsan_demo_fixed: Initializing sanitized module...\n");

    global_dev = kzalloc(sizeof(*global_dev), GFP_KERNEL);
    if (!global_dev)
        return -ENOMEM;

    writer_task = kthread_run(writer_thread_func_fixed, NULL, "kcsan_w_fixed");
    reader_task = kthread_run(reader_thread_func_fixed, NULL, "kcsan_r_fixed");

    return 0;
}

static void __exit kcsan_demo_fixed_exit(void)
{
    if (writer_task)
        kthread_stop(writer_task);
    if (reader_task)
        kthread_stop(reader_task);

    kfree(global_dev);
    pr_info("kcsan_demo_fixed: Unloaded cleanly without KCSAN warnings\n");
}

module_init(kcsan_demo_fixed_init);
module_exit(kcsan_demo_fixed_exit);
```

Після компіляції та завантаження виправленого модуля `dmesg` залишається повністю чистим, оскільки KCSAN розпізнає анотовані доступи і розуміє семантику впорядкування.

---

## 4. Еквівалентна програма простору користувача (C та C++)

Для порівняльного аналізу розберемо, як принципи атомарного впорядкування пам'яті (Memory Ordering) передаються у програмування простору користувача за допомогою стандартних бібліотек C11 та C++20.

У стандарту C11 застосовується заголовок `<stdatomic.h>` та explicit-функції з вказанням моделей пам'яті `memory_order_relaxed`, `memory_order_release` та `memory_order_acquire`. Вони аналогічні за дією до системних макросів ядра `READ_ONCE`/`WRITE_ONCE` та `smp_store_release`/`smp_load_acquire`.

У C++20 використовується шаблон `std::atomic<T>` у поєднанні з безпечним керуванням потоками через `std::jthread` (RAII-концепція автоматичного приєднання потоку в деструкторі).

:::tabs
```c
/* user_concurrency_demo.c (POSIX Threads + C11 stdatomic) */
#include <stdio.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <pthread.h>
#include <unistd.h>

struct shared_state {
    atomic_int counter;
    atomic_bool ready;
};

static struct shared_state global_state;

void* writer_thread(void* arg) {
    for (int i = 0; i < 5; ++i) {
        /* Еквівалент WRITE_ONCE з relaxed-впорядкуванням */
        int cur = atomic_load_explicit(&global_state.counter, memory_order_relaxed);
        atomic_store_explicit(&global_state.counter, cur + 1, memory_order_relaxed);
        
        /* Еквівалент smp_store_release */
        atomic_store_explicit(&global_state.ready, true, memory_order_release);
        usleep(2000);
    }
    return NULL;
}

void* reader_thread(void* arg) {
    for (int i = 0; i < 5; ++i) {
        /* Еквівалент smp_load_acquire */
        if (atomic_load_explicit(&global_state.ready, memory_order_acquire)) {
            int val = atomic_load_explicit(&global_state.counter, memory_order_relaxed);
            printf("C Userspace: Counter observed = %d\n", val);
        }
        usleep(1500);
    }
    return NULL;
}

int main(void) {
    pthread_t t_writer, t_reader;

    atomic_init(&global_state.counter, 0);
    atomic_init(&global_state.ready, false);

    pthread_create(&t_writer, NULL, writer_thread, NULL);
    pthread_create(&t_reader, NULL, reader_thread, NULL);

    pthread_join(t_writer, NULL);
    pthread_join(t_reader, NULL);

    printf("C Userspace Concurrency Test Passed Cleanly.\n");
    return 0;
}
```
```cpp
// user_concurrency_demo.cpp (C++20 std::atomic + std::jthread + RAII)
#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>

struct SharedState {
    std::atomic<int> counter{0};
    std::atomic<bool> ready{false};
};

class UserspaceConcurrencyApp {
public:
    void run() {
        SharedState state;

        // Використовуємо jthread з автоматичним приєднанням (RAII)
        std::jthread writer([&state]() {
            for (int i = 0; i < 5; ++i) {
                int cur = state.counter.load(std::memory_order_relaxed);
                state.counter.store(cur + 1, std::memory_order_relaxed);
                
                // Еквівалент smp_store_release
                state.ready.store(true, std::memory_order_release);
                std::this_thread::sleep_for(std::chrono::milliseconds(2));
            }
        });

        std::jthread reader([&state]() {
            for (int i = 0; i < 5; ++i) {
                // Еквівалент smp_load_acquire
                if (state.ready.load(std::memory_order_acquire)) {
                    int val = state.counter.load(std::memory_order_relaxed);
                    std::cout << "C++ Userspace: Counter observed = " << val << "\n";
                }
                std::this_thread::sleep_for(std::chrono::milliseconds(2));
            }
        });
    }
};

int main() {
    UserspaceConcurrencyApp app;
    app.run();
    std::cout << "C++ Userspace Concurrency Test Passed Cleanly.\n";
    return 0;
}
```
:::
