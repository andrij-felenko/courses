# ⚙️ Практикум: тригерування Oops/Panic та аналіз crash-дампів

Практичний порадник містить симуляційний модуль ядра для контрольованого виклику різних типів збоїв (Kernel Oops та Kernel Panic), розробку користувацької утиліти аналізу логів трасування та покрокову методику post-mortem аналізу аварійного дампа пам'яті (`vmcore`) за допомогою інструмента `crash`.

---

## 1. Драйвер симуляції аварійних ситуацій ядра (C Kernel Module)

Для дослідження механізмів обробки помилок необхідно мати інструмент, який дозволяє контрольовано тригерувати збої у різних контекстах виконання ядра Linux: у контексті звичайного процесу (`process context`), у контексті обробника переривань (`IRQ context`), а також при спробі порушення прав доступу до захищених сторінок пам'яті.

Код наведеного нижче модуля завантажується у простір ядра та створює файл у псевдофайловій системі `/proc/oops_trigger`. Запис спеціальних команд у цей файл викликає відповідний тип аварії.

> ⚠️ **Виняток C++ у просторі ядра (§5 Канону):** Код драйверів Linux працює виключно в режимі ядра (Ring 0), де відсутні винятки C++, RTTI та стандартна бібліотека C++. Тому модуль ядра наведено виключно мовою C.

```c
/* oops_trigger_mod.c — Симулятор аварійних ситуацій ядра Linux */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/proc_fs.h>
#include <linux/uaccess.h>
#include <linux/timer.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Kernel Observability Guide");
MODULE_DESCRIPTION("Module for triggering Oops and Panic for testing Kdump");

static struct proc_dir_entry *proc_entry;
static struct timer_list fault_timer;

/* Обробник таймера: виняток у контексті переривання (IRQ Context) */
static void irq_fault_timer_handler(struct timer_list *t)
{
    int *null_ptr = NULL;
    pr_emerg("oops_trigger: Triggering NULL dereference in IRQ handler!\n");
    /* Збій у контексті переривання неминуче трансформується у Kernel Panic */
    *null_ptr = 0xDEADBEEF;
}

static ssize_t oops_proc_write(struct file *file, const char __user *buffer,
                               size_t count, loff_t *pos)
{
    char kbuf[32];
    if (count >= sizeof(kbuf))
        return -EINVAL;

    if (copy_from_user(kbuf, buffer, count))
        return -EFAULT;

    kbuf[count] = '\0';
    if (count > 0 && kbuf[count - 1] == '\n')
        kbuf[count - 1] = '\0';

    if (strcmp(kbuf, "null") == 0) {
        int *ptr = NULL;
        pr_emerg("oops_trigger: Executing NULL pointer dereference in process context...\n");
        *ptr = 42; /* Простий Oops (за замовчуванням вбиває лише поточний процес) */
    } else if (strcmp(kbuf, "panic") == 0) {
        pr_emerg("oops_trigger: Calling panic() directly!\n");
        panic("oops_trigger: Manual execution of panic()");
    } else if (strcmp(kbuf, "irq_null") == 0) {
        pr_emerg("oops_trigger: Scheduling timer for IRQ fault in 100ms...\n");
        timer_setup(&fault_timer, irq_fault_timer_handler, 0);
        mod_timer(&fault_timer, jiffies + msecs_to_jiffies(100));
    } else if (strcmp(kbuf, "ro_write") == 0) {
        char *ro_text = (char *)oops_proc_write;
        pr_emerg("oops_trigger: Attempting to write to read-only kernel text segment...\n");
        *ro_text = 0x90; /* Порушення прав доступу до сторінки тексту ядра */
    } else {
        pr_info("oops_trigger: Unknown command '%s'. Supported: null, panic, irq_null, ro_write\n", kbuf);
    }

    return count;
}

static const struct proc_ops oops_proc_ops = {
    .proc_write = oops_proc_write,
};

static int __init oops_trigger_init(void)
{
    proc_entry = proc_create("oops_trigger", 0200, NULL, &oops_proc_ops);
    if (!proc_entry)
        return -ENOMEM;

    pr_info("oops_trigger: Loaded. Write to /proc/oops_trigger to test faults.\n");
    return 0;
}

static void __exit oops_trigger_exit(void)
{
    del_timer_sync(&fault_timer);
    if (proc_entry)
        proc_remove(proc_entry);
    pr_info("oops_trigger: Unloaded.\n");
}

module_init(oops_trigger_init);
module_exit(oops_trigger_exit);
```

### Детальний механізм функціонування та крайові випадки модуля:

1. **Безпечне копіювання даних з користувацького простору (`copy_from_user`):**
   Функція `copy_from_user()` перевіряє права доступу та наявність сторінок віртуальної пам'яті буфера користувача. Якщо буфер знаходиться у невалідній зоні пам'яті, ядро повертає помилку `-EFAULT` без генерації Oops. Це демонструє штатний механізм обробки некоректних аргументів системного виклику.

2. **Розрізнення контексту процесу та контексту переривання:**
   - Коли виконано команду `null`, код виконується у контексті поточного процесу `sh`. Поточний потік має валідну структуру `task_struct`, тому обробник `die()` після збору логів може безпечно завершити потік через `make_task_dead(SIGSEGV)`.
   - Коли виконується команда `irq_null`, таймер викликає обробник `irq_fault_timer_handler()` у контексті апаратного переривання (SoftIRQ/HardIRQ). У цьому контексті значення `in_interrupt()` повертає істину. Оскільки переривання не зв'язані з жодним користувацьким процесом, знищувати немає кого. Спроба викликати `make_task_dead()` у контексті переривання призвела б до невизначеної поведінки планивальника, тому ядро автоматично трансформує виняток у `panic()`.

3. **Захист сегмента коду від запису (`ro_write`):**
   Сучасні ядра Linux компілюються з прапорцем `CONFIG_STRICT_KERNEL_RWX`. Сторінки пам'яті, що містять машинний код ядра та модулів, позначаються прапорцем Read-Only (RO) та Executable (X). Спроба запису байта за адресою функції `oops_proc_write` викликає апаратне порушення захисту сторінки `Page Fault (Protection Violation)`, запобігаючи модифікації коду ядра під час виконання.

---

## 2. Збирання, завантаження та випробування драйвера

Для збирання модуля у середовищі дистрибутиву Linux використовується стандартний інструментарій Kbuild та заголовні файли ядра (`linux-headers`):

```bash
# Створення файла інструкцій збирання Makefile
cat << 'EOF' > Makefile
obj-m += oops_trigger_mod.o
all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules
clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
EOF

# Компіляція модуля ядра
make

# Завантаження згенерованого бінарного модуля .ko в ядро
sudo insmod oops_trigger_mod.ko

# Перевірка реєстрації та прав доступу до procfs файлу
ls -l /proc/oops_trigger

# 1. Тест м'якого збою Oops (завершується лише процес sh):
sudo sh -c 'echo null > /proc/oops_trigger'

# Аналіз отриманого логу у системному журналі dmesg
dmesg | tail -n 25

# 2. Тест фатальної паніки в контексті переривання (викликає Паніку та Kdump):
sudo sh -c 'echo irq_null > /proc/oops_trigger'
```

---

## 3. Користувацька утиліта декодування логу аварії (Userspace Log Parser)

Під час аналізу текстових логів `dmesg` розробнику необхідно швидко перевести сирі адреси `RIP: 0010:my_driver_write+0x35/0x90` у конкретні рядки C-коду. Наведена нижче утиліта зчитує лог аварії, знаходить рядок `RIP:`, розбирає назву символу та зміщення, після чого запускає `gdb` у пакетному режимі для автодекодування.

:::tabs
```c
/* oops_parser.c — Аналізатор адрес збою мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

void parse_and_decode(const char *filename, const char *vmlinux_path) {
    FILE *f = fopen(filename, "r");
    if (!f) {
        perror("Failed to open crash log");
        return;
    }

    char line[512];
    while (fgets(line, sizeof(line), f)) {
        char *rip_pos = strstr(line, "RIP:");
        if (rip_pos) {
            printf("[+] Found Faulting Instruction Pointer line:\n    %s", line);
            
            char func_name[128];
            unsigned long offset = 0, size = 0;
            
            if (sscanf(rip_pos, "RIP: %*x:%[^+]+0x%lx/0x%lx", func_name, &offset, &size) == 3) {
                printf("[+] Parsed symbol: Function=%s, Offset=0x%lx, Size=0x%lx\n",
                       func_name, offset, size);
                
                if (vmlinux_path && access(vmlinux_path, R_OK) == 0) {
                    char cmd[512];
                    snprintf(cmd, sizeof(cmd), "gdb -batch -ex 'info line *%s+0x%lx' %s 2>/dev/null",
                             func_name, offset, vmlinux_path);
                    printf("[+] Resolving via GDB:\n");
                    fflush(stdout);
                    system(cmd);
                }
            }
        }
    }
    fclose(f);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <dmesg_oops.txt> [vmlinux_path]\n", argv[0]);
        return 1;
    }
    parse_and_decode(argv[1], (argc > 2) ? argv[2] : NULL);
    return 0;
}
```
```cpp
// oops_parser.cpp — Аналізатор адрес збою мовою C++20
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <regex>
#include <cstdlib>
#include <filesystem>

namespace fs = std::filesystem;

class OopsParser {
public:
    explicit OopsParser(fs::path vmlinux_path = {}) 
        : vmlinux_path_(std::move(vmlinux_path)) {}

    void process_log(const fs::path& log_path) const {
        std::ifstream file(log_path);
        if (!file.is_open()) {
            std::cerr << "Error: Cannot open log file: " << log_path << '\n';
            return;
        }

        const std::regex rip_regex(R"(RIP:\s+[0-9a-fA-F]+:([a-zA-Z0-9_]+)\+0x([0-9a-fA-F]+)/0x([0-9a-fA-F]+))");
        std::string line;

        while (std::getline(file, line)) {
            std::smatch match;
            if (std::regex_search(line, match, rip_regex)) {
                const std::string func = match[1].str();
                const std::string offset_hex = match[2].str();
                const unsigned long offset = std::stoul(offset_hex, nullptr, 16);

                std::cout << "[+] Found Faulting RIP:\n    " << line << '\n';
                std::cout << "[+] Extracted Symbol: " << func << " + 0x" << std::hex << offset << std::dec << '\n';

                if (!vmlinux_path_.empty() && fs::exists(vmlinux_path_)) {
                    resolve_with_gdb(func, offset);
                }
            }
        }
    }

private:
    fs::path vmlinux_path_;

    void resolve_with_gdb(std::string_view func, unsigned long offset) const {
        char offset_buf[32];
        snprintf(offset_buf, sizeof(offset_buf), "%lx", offset);

        const std::string cmd = "gdb -batch -ex 'info line *" + std::string(func) + 
                                "+0x" + std::string(offset_buf) + "' " + vmlinux_path_.string() + " 2>/dev/null";
        
        std::cout << "[+] Resolving via GDB:\n";
        std::clog.flush();
        std::system(cmd.c_str());
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <dmesg_oops.txt> [vmlinux_path]\n";
        return 1;
    }

    const fs::path log_path = argv[1];
    const fs::path vmlinux_path = (argc > 2) ? argv[2] : "";

    OopsParser parser(vmlinux_path);
    parser.process_log(log_path);
    return 0;
}
```
:::

---

## 4. Налаштування Kdump та покроковий аналіз дампа пам'яті (vmcore)

Для розгортання повноцінного середовища збору дампів пам'яті після аварійного збою виконується наступний регламент налаштувань.

### Крок 1: Конфігурація резервування RAM у завантажувачі

У конфігураційному файлі завантажувача `/etc/default/grub` до змінної `GRUB_CMDLINE_LINUX_DEFAULT` додається параметр резервування пам'яті `crashkernel`:

```bash
# Резервування 512 МБ пам'яті під Crash Kernel
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash crashkernel=512M"

# Оновлення конфігурації GRUB та перезавантаження
sudo update-grub
sudo reboot
```

Після перезавантаження перевірте факт резервування області пам'яті:

```bash
# Перевірка завантаження аварійного ядра у резервовану область
cat /sys/kernel/kexec_crash_loaded
# Повернуте значення повинно дорівнювати 1

# Перевірка зарезервованого діапазону фізичних адрес
cat /proc/iomem | grep "Crash kernel"
```

### Крок 2: Встановлення пакета інструментів аналізу

```bash
# Встановлення kexec-tools, makedumpfile та аналізатора crash
sudo apt-get update
sudo apt-get install crash kexec-tools makedumpfile

# Встановлення образу ядра з символами зневадження (dbgsym / debuginfo)
sudo apt-get install linux-image-$(uname -r)-dbgsym
```

### Крок 3: Симуляція аварії та створення дампа vmcore

Для перевірки роботи всього ланцюжка Kdump примусово тригерується паніка ядра через інтерфейс SysRq з увімкненим `panic_on_oops`:

```bash
sudo sh -c 'echo 1 > /proc/sys/kernel/panic_on_oops'
sudo sh -c 'echo c > /proc/sysrq-trigger'
```

Після виконання цієї команди основне ядро миттєво викликає `crash_kexec()`, передає управління Crash Kernel у зарезервованій пам'яті. Утиліта `makedumpfile` стискає вміст `/proc/vmcore` та записує його у каталог `/var/crash/<timestamp>/vmcore`.

### Детальні механізми фільтрації пам'яті у `makedumpfile`:
Створення повноцінного дампа оперативної пам'яті обсягом сотні гігабайтів на дисковий носій зайняло б надто багато часу. Утиліта `makedumpfile` використовує прапорці рівня стиснення (dump level `-d`), які дозволяють виключити з дампа нентрібні сторінки:
- `Level 1` — виключення порожніх сторінок (zero pages).
- `Level 2` — виключення сторінок кешу файлової системи (cache pages).
- `Level 4` — виключення сторінок дискових буферів (buffer pages).
- `Level 8` — виключення сторінок простору користувача (user space pages).
- `Level 31` — виключення усіх вищеперелічених сторінок, залишаючи в дампі виключно структури даних самого ядра.

### Крок 4: Запуск та дослідження дампа в утиліті `crash`

Запустіть аналізатор `crash`, передавши йому образ `vmlinux` із символами зневадження та збережений дамп `vmcore`:

```bash
crash /usr/lib/debug/boot/vmlinux-$(uname -r) /var/crash/20260814-1200/vmcore
```

Після ініціалізації зневаджувача відкривається інтерактивний консольний інтерфейс. Основні команди дослідження:

1. **Огляд загального стану системи (`sys`):**
   ```text
   crash> sys
   KERNEL: /usr/lib/debug/boot/vmlinux-6.1.0-21-amd64
   DUMPFILE: /var/crash/20260814-1200/vmcore
   CPUS: 4
   DATE: Fri Aug 14 12:00:00 2026
   PANIC: "Kernel panic - not syncing: sysrq triggered crash"
   TAINTED: 0x00000200 (W)
   ```

2. **Розкрутка стека викликів для збійного CPU (`bt`):**
   ```text
   crash> bt
   PID: 1422     TASK: ffff921405102000  CPU: 3   COMMAND: "sh"
   #0 [ffffa93201463c10] crash_nmi_callback at ffffffff810452a0
   #1 [ffffa93201463c18] nmi_handle at ffffffff810321b0
   #2 [ffffa93201463c60] default_do_nmi at ffffffff810325c0
   #3 [ffffa93201463c80] exc_nmi at ffffffff81a012d0
   #4 [ffffa93201463ca0] end_repeat_nmi at ffffffff81c01540
   #5 [ffffa93201463d10] sysrq_handle_crash at ffffffff81561230
   #6 [ffffa93201463d20] __handle_sysrq at ffffffff81561a40
   #7 [ffffa93201463d50] write_sysrq_trigger at ffffffff81561ed0
   ```

3. **Дизідемування інструкцій машинного коду (`dis -l`):**
   ```text
   crash> dis -l sysrq_handle_crash+0x10
   /usr/src/kernel/drivers/tty/sysrq.c: 155
   0xffffffff81561230 <sysrq_handle_crash+16>: movb   $0x1,0x0(%rax)
   ```

4. **Дамп внутрішніх структур ядра (`struct`):**
   ```text
   crash> struct task_struct.comm,pid,state ffff921405102000
     comm = "sh\0\0\0\0\0\0\0\0\0\0\0\0\0"
     pid = 1422
     state = 0x0 (TASK_RUNNING)
   ```

5. **Аналіз виділених сторінок пам'яті та відкритих файлів (`files`, `kmem`):**
   ```text
   crash> files 1422
   PID: 1422     TASK: ffff921405102000  CPU: 3   COMMAND: "sh"
   ROOT: /    CWD: /root
   FD      FILE            DENTRY           INODE       TYPE PATH
    0 ffff921404101000 ffff921402203000 ffff921401104000 CHR  /dev/pts/0
    1 ffff921404102000 ffff921402205000 ffff921401106000 REG  /proc/sysrq-trigger

   crash> kmem -i
   # Виводить стан використання оперативної пам'яті, кешу slab та сторінок ядра
   ```

6. **Читання повного логу dmesg з дампа (`log`):**
   ```text
   crash> log | tail -n 30
   ```

Використання інструменту `crash` дозволяє провести глибокий аналіз пам'яті ядра без абстракцій, точно встановити значення будь-якої змінної у момент аварії та виявити приховані помилки взаємного блокування (deadlocks) або пошкодження пам'яті.
