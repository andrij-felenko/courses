# ⚙️ Модуль ядра та утиліта відтворення й тестування lockup-станів

Для перевірки надійності серверної інфраструктури, калібрування систем моніторингу та тестування аварійного скидання дампів пам'яті (`kdump`) інженерам необхідно вміти контрольовано відтворювати стани Soft Lockup, Hard Lockup та Hung Task у тестовому середовищі (віртуальній машині QEMU/KVM). Без можливості штучно викликати відключення переривань або нескінченні цикли в режимі Ring 0 неможливо гарантувати, що підсистема NMI Watchdog або аварійні сценарії `panic_on_lockup` коректно спрацюють під час реального виробничого збою.

Нижче наведено повний вихідний код завантажуваного модуля ядра Linux `lockup_trigger`, що створює діагностичний інтерфейс у `debugfs`, а також користувацьку консольну утиліту керування `lockup_ctl`, реалізовану паралельно мовами C та C++.

---

## 1. Архітектурні принципи генерації штучних зависань

Щоб протестувати роботу всіх трьох детекторів ядра, модуль реалізує три принципово різні механізми порушення нормального виконання:

1. **Симуляція Soft Lockup:**
   Модуль викликає функцію `spin_lock()`. У ядрі Linux взяття спінлока інкрементує лічильник вимкнення витіснення (`preempt_count++`), що забороняє планувальнику перемикати контекст на інші задачі. Проте апаратний прапорець переривань `IF` у регістрі `EFLAGS` залишається активним. Запустивши функцію затримки `mdelay(25000)`, модуль змушує CPU крутитися в активному циклі 25 секунд. Зауважимо важливу відмінність: виклик `msleep()` тут був би неприпустимим, оскільки `msleep()` намагається добровільно віддати процесор через `schedule()`, що викликало б негайне попередження ядра про неприпустимість сну у вимкненій преемпції (`scheduling while atomic`). Функція `mdelay()`, навпаки, є чистим обчислювальним циклом активного очікування (`busy-wait loop`). Апаратний таймер `hrtimer` продовжує цокати кожні 4 секунди, але потік реального часу `watchdog/K` не може отримати квант процесорного часу. Через 20 секунд таймер фіксує прострочення мітки часу і виводить повідомлення `BUG: soft lockup`.

2. **Симуляція Hard Lockup:**
   Модуль викликає функцію `local_irq_disable()`, яка безпосередньо виконує апаратну інструкцію `cli` на x86 (або запис у системний регістр `DAIF` на ARM64). Після цього масковані апаратні переривання процесора повністю блокуються на рівні кремнію. Вхід у нескінченний цикл `while (1) cpu_relax();` призводить до повного паралічу звичайного коду ядра: таймери `hrtimer` більше не отримують керування. Єдиним механізмом, який пробиває це блокування, є апаратне переривання NMI від лічильника `perf_event`, що фіксує зупинку лічильника `hrtimer_interrupts` і викликає паніку.

3. **Симуляція Hung Task (D-state):**
   Модуль створює окремий ядерний потік `kthread`, який переводить свій стан у `TASK_UNINTERRUPTIBLE` і засинає через `schedule_timeout()` на 150 секунд. У цьому стані потік вилучається з черги готових до виконання задач (`runqueue`) і не споживає такти процесора. Лічильник перемикань контексту `nvcsw + nivcsw` застигає. Фоновий демон `khungtaskd` під час чергового сканування виявляє відсутність активності задачі протягом 120 секунд і друкує попередження в `dmesg`.

---

## 2. Модуль ядра `lockup_trigger.c` (Kernel Space)

Модуль створює каталог `/sys/kernel/debug/lockup_trigger/` у віртуальній файловій системі `debugfs`. Усі вузли мають права доступу `0200` (write-only), що запобігає випадковому читанню файлів утилітами типу `grep` чи сканерами безпеки, яке могло б спровокувати побічні ефекти. Запис символу `'1'` у відповідний файл активує симуляцію.

```c
/*
 * lockup_trigger.c — Модуль для контрольованої симуляції зависань ядра Linux.
 * Призначений виключно для налагодження та тестування в ізольованому середовищі.
 */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/debugfs.h>
#include <linux/delay.h>
#include <linux/kthread.h>
#include <linux/sched.h>
#include <linux/spinlock.h>
#include <linux/interrupt.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Unix & Linux Observability Guide");
MODULE_DESCRIPTION("Synthetic Soft/Hard Lockup and Hung Task Generator");

static struct dentry *debugfs_dir;
static struct task_struct *hung_task_kthread;

/* Спінлок для симуляції довгого утримання в Soft Lockup */
static DEFINE_SPINLOCK(dummy_spinlock);

/*
 * 1. Генератор Soft Lockup:
 * Захоплює спінлок (що вимикає витіснення на цьому CPU) і крутиться у глухому циклі
 * протягом 25 секунд. Апаратні IRQ активні, проте планувальник не може перемкнути задачу.
 */
static ssize_t trigger_soft_lockup_write(struct file *file, const char __user *user_buf,
                                        size_t count, loff_t *ppos)
{
    pr_warn("lockup_trigger: [CPU#%d] Ініціалізація Soft Lockup на 25 секунд...\n",
            raw_smp_processor_id());

    /* Захоплюємо spinlock без вимикання IRQ — преемпція вимкнена, таймери цокають */
    spin_lock(&dummy_spinlock);
    
    /* Цикл активного очікування (25000 мс > 2 * watchdog_thresh = 20 с) */
    mdelay(25000);
    
    spin_unlock(&dummy_spinlock);

    pr_info("lockup_trigger: [CPU#%d] Soft Lockup завершено успішно\n",
            raw_smp_processor_id());
    return count;
}

/*
 * 2. Генератор Hard Lockup:
 * Вимикає апаратні переривання на поточному ядрі CPU через local_irq_disable()
 * і входить у безкінечний цикл. Звичайні таймери hrtimer паралізовані.
 * Виявити цей стан здатне лише немасковане переривання NMI.
 */
static ssize_t trigger_hard_lockup_write(struct file *file, const char __user *user_buf,
                                        size_t count, loff_t *ppos)
{
    pr_emerg("lockup_trigger: [CPU#%d] Ініціалізація Hard Lockup (local_irq_disable)...\n",
             raw_smp_processor_id());

    /* Вимикаємо локальні апаратні переривання процесора (скидаємо прапорець IF в EFLAGS) */
    local_irq_disable();

    /* Безкінечний мертвий цикл ядра */
    while (1) {
        cpu_relax();
    }

    /* Сюди ядро не дійде ніколи */
    return count;
}

/*
 * 3. Функція ядерного потоку для симуляції Hung Task (D-state)
 */
static int hung_task_worker(void *data)
{
    pr_warn("lockup_trigger: Потік hung_task_worker запущено (PID: %d), перехід у D-state на 150 с...\n",
            current->pid);

    /* Переводимо задачу в непереривний сон */
    set_current_state(TASK_UNINTERRUPTIBLE);

    /* Засинаємо на 150 секунд (більше за замовчуваний тайм-аут 120 с) */
    schedule_timeout(msecs_to_jiffies(150000));

    pr_info("lockup_trigger: Потік hung_task_worker прокинувся\n");
    return 0;
}

static ssize_t trigger_hung_task_write(struct file *file, const char __user *user_buf,
                                      size_t count, loff_t *ppos)
{
    hung_task_kthread = kthread_run(hung_task_worker, NULL, "kworker_hung_sim");
    if (IS_ERR(hung_task_kthread)) {
        pr_err("lockup_trigger: Не вдалося створити kthread\n");
        return PTR_ERR(hung_task_kthread);
    }
    return count;
}

static const struct file_operations soft_fops = {
    .owner = THIS_MODULE,
    .write = trigger_soft_lockup_write,
};

static const struct file_operations hard_fops = {
    .owner = THIS_MODULE,
    .write = trigger_hard_lockup_write,
};

static const struct file_operations hung_fops = {
    .owner = THIS_MODULE,
    .write = trigger_hung_task_write,
};

static int __init lockup_trigger_init(void)
{
    debugfs_dir = debugfs_create_dir("lockup_trigger", NULL);
    if (!debugfs_dir)
        return -ENOMEM;

    debugfs_create_file("trigger_soft_lockup", 0200, debugfs_dir, NULL, &soft_fops);
    debugfs_create_file("trigger_hard_lockup", 0200, debugfs_dir, NULL, &hard_fops);
    debugfs_create_file("trigger_hung_task",   0200, debugfs_dir, NULL, &hung_fops);

    pr_info("lockup_trigger: Модуль завантажено. Вузли debugfs створено.\n");
    return 0;
}

static void __exit lockup_trigger_exit(void)
{
    debugfs_remove_recursive(debugfs_dir);
    pr_info("lockup_trigger: Модуль вивантажено.\n");
}

module_init(lockup_trigger_init);
module_exit(lockup_trigger_exit);
```

---

## 3. Утиліта користувацького простору `lockup_ctl`

Консольна утиліта `lockup_ctl` перевіряє активність сторожових таймерів у `/proc/sys/kernel/`, інспектує лічильники переривань NMI у `/proc/interrupts` та ініціює запис у відповідний вузол `debugfs`. Утиліту наведено паралельно у двох варіантах: класичний POSIX C та сучасний ідіоматичний C++20.

:::tabs
```c
/* lockup_ctl.c — Утиліта моніторингу та ініціалізації тестів зависань ядра (C99/POSIX) */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

static void print_usage(const char *prog) {
    fprintf(stderr, "Використання: %s <soft|hard|hung|status>\n", prog);
    fprintf(stderr, "  soft   - викликати Soft Lockup (25 с утримування spinlock)\n");
    fprintf(stderr, "  hard   - викликати Hard Lockup (local_irq_disable + dead loop)\n");
    fprintf(stderr, "  hung   - викликати Hung Task (150 с у TASK_UNINTERRUPTIBLE)\n");
    fprintf(stderr, "  status - перевірити поточні параметри watchdog у sysctl\n");
}

static int read_sysctl_int(const char *path) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) return -1;
    char buf[32] = {0};
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    if (n <= 0) return -1;
    return atoi(buf);
}

static void show_status(void) {
    printf("=== Стан сторожових таймерів ядра Linux ===\n");
    printf("kernel.watchdog:         %d\n", read_sysctl_int("/proc/sys/kernel/watchdog"));
    printf("kernel.watchdog_thresh:  %d с\n", read_sysctl_int("/proc/sys/kernel/watchdog_thresh"));
    printf("kernel.nmi_watchdog:     %d\n", read_sysctl_int("/proc/sys/kernel/nmi_watchdog"));
    printf("kernel.softlockup_panic: %d\n", read_sysctl_int("/proc/sys/kernel/softlockup_panic"));
    printf("kernel.hardlockup_panic: %d\n", read_sysctl_int("/proc/sys/kernel/hardlockup_panic"));
    printf("kernel.hung_task_timeout:%d с\n", read_sysctl_int("/proc/sys/kernel/hung_task_timeout_secs"));
    printf("kernel.hung_task_panic:  %d\n", read_sysctl_int("/proc/sys/kernel/hung_task_panic"));
}

static int write_trigger(const char *node) {
    char path[128];
    snprintf(path, sizeof(path), "/sys/kernel/debug/lockup_trigger/%s", node);
    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s (чи завантажено модуль?)\n",
                path, strerror(errno));
        return 1;
    }
    if (write(fd, "1", 1) < 0) {
        fprintf(stderr, "Помилка запису у тригер: %s\n", strerror(errno));
        close(fd);
        return 1;
    }
    close(fd);
    printf("Тригер '%s' успішно активовано.\n", node);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        print_usage(argv[0]);
        return 1;
    }

    if (strcmp(argv[1], "status") == 0) {
        show_status();
        return 0;
    } else if (strcmp(argv[1], "soft") == 0) {
        return write_trigger("trigger_soft_lockup");
    } else if (strcmp(argv[1], "hard") == 0) {
        return write_trigger("trigger_hard_lockup");
    } else if (strcmp(argv[1], "hung") == 0) {
        return write_trigger("trigger_hung_task");
    } else {
        print_usage(argv[0]);
        return 1;
    }
}
```
```cpp
// lockup_ctl.cpp — Утиліта моніторингу та ініціалізації тестів зависань ядра (C++20)
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <filesystem>
#include <optional>
#include <format>

namespace fs = std::filesystem;

class LockupController {
public:
    static void printUsage(std::string_view progName) {
        std::cerr << std::format("Використання: {} <soft|hard|hung|status>\n", progName)
                  << "  soft   - викликати Soft Lockup (25 с утримування spinlock)\n"
                  << "  hard   - викликати Hard Lockup (local_irq_disable + dead loop)\n"
                  << "  hung   - викликати Hung Task (150 с у TASK_UNINTERRUPTIBLE)\n"
                  << "  status - перевірити поточні параметри watchdog у sysctl\n";
    }

    static std::optional<int> readSysctl(std::string_view path) {
        std::ifstream file(path.data());
        if (!file.is_open()) return std::nullopt;
        int value = 0;
        if (file >> value) return value;
        return std::nullopt;
    }

    static void showStatus() {
        std::cout << "=== Стан сторожових таймерів ядра Linux ===\n";
        auto printParam = [](std::string_view name, std::string_view path, std::string_view unit = "") {
            auto val = readSysctl(path);
            if (val.has_value()) {
                std::cout << std::format("{:<26} {}{}\n", name, *val, unit.empty() ? "" : std::format(" {}", unit));
            } else {
                std::cout << std::format("{:<26} [недоступно]\n", name);
            }
        };

        printParam("kernel.watchdog:", "/proc/sys/kernel/watchdog");
        printParam("kernel.watchdog_thresh:", "/proc/sys/kernel/watchdog_thresh", "с");
        printParam("kernel.nmi_watchdog:", "/proc/sys/kernel/nmi_watchdog");
        printParam("kernel.softlockup_panic:", "/proc/sys/kernel/softlockup_panic");
        printParam("kernel.hardlockup_panic:", "/proc/sys/kernel/hardlockup_panic");
        printParam("kernel.hung_task_timeout:", "/proc/sys/kernel/hung_task_timeout_secs", "с");
        printParam("kernel.hung_task_panic:", "/proc/sys/kernel/hung_task_panic");
    }

    static bool triggerLockup(std::string_view nodeName) {
        const fs::path nodePath = fs::path("/sys/kernel/debug/lockup_trigger") / nodeName;
        std::ofstream triggerFile(nodePath);
        if (!triggerFile.is_open()) {
            std::cerr << std::format("Помилка відкриття {}: чи завантажено модуль ядра?\n", nodePath.string());
            return false;
        }
        triggerFile << "1\n";
        if (triggerFile.bad()) {
            std::cerr << "Помилка під час запису команди у вузол debugfs\n";
            return false;
        }
        std::cout << std::format("Тригер '{}' успішно активовано.\n", nodeName);
        return true;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        LockupController::printUsage(argv[0]);
        return 1;
    }

    const std::string_view cmd = argv[1];
    if (cmd == "status") {
        LockupController::showStatus();
        return 0;
    } else if (cmd == "soft") {
        return LockupController::triggerLockup("trigger_soft_lockup") ? 0 : 1;
    } else if (cmd == "hard") {
        return LockupController::triggerLockup("trigger_hard_lockup") ? 0 : 1;
    } else if (cmd == "hung") {
        return LockupController::triggerLockup("trigger_hung_task") ? 0 : 1;
    } else {
        LockupController::printUsage(argv[0]);
        return 1;
    }
}
```
:::

---

## 4. Складання, запуск та практичний сценарій тестування

Для складання модуля ядра та обох варіантів користувацької утиліти використовується стандартний `Makefile`:

```makefile
obj-m += lockup_trigger.o
KDIR ?= /lib/modules/$(shell uname -r)/build

all: module cli

module:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

cli:
	gcc -O2 -Wall lockup_ctl.c -o lockup_ctl_c
	g++ -O2 -std=c++20 -Wall lockup_ctl.cpp -o lockup_ctl_cpp

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
	rm -f lockup_ctl_c lockup_ctl_cpp
```

### Порядок проведення експерименту в ізольованій VM:

1. **Монтування налагоджувальної файлової системи `debugfs`:**
   ```bash
   mount -t debugfs none /sys/kernel/debug
   ```

2. **Завантаження скомпільованого модуля ядра:**
   ```bash
   insmod lockup_trigger.ko
   ```

3. **Перевірка поточного статусу та лічильників переривань NMI:**
   ```bash
   ./lockup_ctl_cpp status
   grep NMI /proc/interrupts
   ```

4. **Тест 1: Виклик Soft Lockup:**
   ```bash
   # Ініціація 25-секундного застрягання у spinlock:
   ./lockup_ctl_cpp soft
   
   # Спостереження у журналі dmesg (повідомлення з'явиться через ~20 секунд):
   dmesg -T | tail -n 25
   ```
   *Очікуваний результат:* Ядро виведе повідомлення виду `BUG: soft lockup - CPU#... stuck for 22s!`, надрукує стек викликів `Call Trace` із зазначенням функції `trigger_soft_lockup_write` та успішно продовжить роботу після завершення 25-секундного інтервалу затримки.

5. **Тест 2: Виклик Hung Task (D-state):**
   ```bash
   ./lockup_ctl_cpp hung
   
   # Зачекати 125 секунд і перевірити системний журнал:
   sleep 125
   dmesg -T | grep -A 10 "blocked for more than 120 seconds"
   ```
   *Очікуваний результат:* Демон `khungtaskd` зафіксує створений потік `kworker_hung_sim`, надрукує його стан сну та стек блокування на функції `schedule_timeout`.

6. **Тест 3: Фатальний Hard Lockup із перевіркою NMI та перезавантаження:**
   ```bash
   # Увімкнути паніку при виявленні hard lockup:
   sysctl -w kernel.hardlockup_panic=1
   
   # Запуск мертвого циклу з вимкненими перериваннями:
   ./lockup_ctl_cpp hard
   ```
   *Очікуваний результат:* Через 10 секунд апаратний лічильник `perf_event` згенерує немасковане переривання NMI. Обробник виявить, що `hrtimer_interrupts` застиг, надрукує `Watchdog detected hard LOCKUP on cpu ...` і викличе `panic()`, що переведе систему в аварійне перезавантаження або викличе захоплення дампа пам'яті через `kdump`.

---

## 5. Аналіз збереженого дампа пам'яті `vmcore` через утиліту `crash`

Якщо під час тестування Hard Lockup або Hung Task було активовано аварійний механізм `kdump`, після перезавантаження в каталозі `/var/crash/<timestamp>/` з'явиться файл `vmcore`. Для його аналізу використовується системний відлагоджувач ядра `crash`:

```bash
# Запуск аналізу дампа пам'яті разом із відлагоджувальним ядром vmlinux
crash /usr/lib/debug/boot/vmlinux-$(uname -r) /var/crash/2026-08-20-14:00/vmcore
```

Корисні команди всередині оболонки `crash`:
- `bt -a` — вивести стек викликів (backtrace) для **всіх** процесорних ядер у момент збою. Дозволяє одразу побачити ядро, на якому спрацював NMI Watchdog.
- `log` — переглянути останні рядки кільцевого буфера логів ядра перед аварійною зупинкою.
- `ps -u` — вивести список усіх процесів, які перебували у стані `TASK_UNINTERRUPTIBLE` (D-state).
- `struct task_struct <адреса>` — роздрукувати повний вміст структури задачі, включаючи лічильники `nvcsw` та `nivcsw`.

### Діагностика проблем у віртуальних машинах QEMU

Якщо під час тестування Hard Lockup NMI Watchdog не спрацьовує і віртуальна машина просто висить без реакції, причиною зазвичай є відсутність віртуалізації апаратного блоку PMU в конфігурації QEMU:
- Для KVM необхідно обов'язково передавати параметр процесора `-cpu host,pmu=on` або `-cpu max`.
- Якщо QEMU запущено без апаратного прискорення KVM (режим чистої TCG емуляції), переривання `perf_event` PMU не емулюються в повному обсязі. У такому разі для тестування рекомендується перемкнутися на емуляцію через `CONFIG_HARDLOCKUP_DETECTOR_BUDDY`.
