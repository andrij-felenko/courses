# ⚙️ Практика розробки: драйвер із підтримкою MSI-X та конфігурація черг

У сучасних багатоядерних системах продуктивність драйвера введення-виведення безпосередньо залежить від здатності розподіляти апаратні переривання між різними процесорними ядрами. Створення багаточергового драйвера PCIe вимагає коректного виділення діапазону векторів MSI-X, реєстрації обробників для кожної черги, налаштування спорідненості ядер та організації відкладеної обробки без блокувань.

Коли пристрій підтримує апаратну багаточерговість (наприклад, мережевий адаптер із чергами RX/TX або дисковий контролер NVMe), кожна черга функціонує як незалежний канал передачі даних. Якщо всі ці черги надсилають переривання на одну лінію або на одне процесорне ядро, виникає вузьке місце: процесор витрачає час на синхронізацію кешів та очікування між'ядерних замків. Механізм MSI-X усуває це обмеження, надаючи кожній черзі персональний вектор переривання, що адресується безпосередньо на потрібне ядро.

## Життєвий цикл ініціалізації переривань у драйвері ядра

Під час ініціалізації пристрою у функції `probe()` драйвер проходить чітку послідовність кроків:

1. **Активація пристрою та майстерингу шини.** Виклик `pci_enable_device()` переводить пристрій зі стану сну D3 у робочий стан D0 та виділяє ресурси MMIO. Наступний обов'язковий виклик — `pci_set_master()`: він виставляє біт Bus Master Enable (BME) у регістрі команд PCI Command Register. Без цього біта апаратний контролер не має права генерувати транзакції Memory Write на шині PCIe, отже, жодне повідомлення MSI-X не зможе покинути пристрій.
2. **Відображення регістрів керування (MMIO BAR).** Функція `pci_iomap()` відображає базовий адресний регістр пристрою у віртуальний адресний простір ядра, надаючи драйверу доступ до внутрішніх регістрів черг.
3. **Запит векторів через `pci_alloc_irq_vectors()`.** Замість застарілих викликів минулих версій ядра драйвер використовує уніфікований інтерфейс. Драйвер вказує мінімально необхідну кількість векторів (зазвичай 1) та бажаний максимум (кількість доступних процесорних ядер у системі). Прапорець `PCI_IRQ_AFFINITY` дає вказівку ядру автоматично згенерувати оптимальні маски спорідненості для кожного вектора з урахуванням фізичної топології процесорних сокетів і вузлів NUMA.
4. **Реєстрація обробників переривань.** Для кожного виділеного вектора функція `pci_irq_vector(pdev, i)` повертає глобальний номер Linux IRQ. Драйвер реєструє функцію обробника через `request_irq()`. Зверніть увагу: на відміну від ліній INTx, для MSI-X **заборонено** передавати прапорець `IRQF_SHARED`, оскільки кожен вектор є строго унікальним для своєї черги.

Нижче наведено повний вихідний код модуля ядра Linux, що реалізує описаний алгоритм.

```c
// SPDX-License-Identifier: GPL-2.0
/*
 * msi_x_demo_driver.c — Каркас багаточергового драйвера з підтримкою MSI-X
 */

#include <linux/module.h>
#include <linux/pci.h>
#include <linux/interrupt.h>
#include <linux/kernel.h>
#include <linux/slab.h>

#define DRIVER_NAME "msix_demo_pci"
#define MAX_HW_QUEUES 8

struct queue_context {
    unsigned int queue_id;
    unsigned int irq;
    atomic_t interrupt_count;
    struct demo_device *parent;
};

struct demo_device {
    struct pci_dev *pdev;
    void __iomem *bar0_mmio;
    unsigned int num_allocated_irqs;
    struct queue_context queues[MAX_HW_QUEUES];
};

/* Обробник переривання конкретної черги (верхня половина) */
static irqreturn_t demo_queue_isr(int irq, void *dev_id)
{
    struct queue_context *q = (struct queue_context *)dev_id;

    /* Збільшуємо локальний лічильник оброблених подій */
    atomic_inc(&q->interrupt_count);

    /*
     * Оскільки для MSI-X переривання є фронтальним (edge-triggered)
     * та унікальним для кожної черги, читати статусний регістр через MMIO
     * для підтвердження факту події не потрібно.
     */
    return IRQ_HANDLED;
}

static int demo_pci_probe(struct pci_dev *pdev, const struct pci_device_id *id)
{
    struct demo_device *priv;
    int err, allocated, i;
    unsigned int nvec = min_t(unsigned int, num_online_cpus(), MAX_HW_QUEUES);

    dev_info(&pdev->dev, "Знайдено пристрій PCIe, запит на %u черг\n", nvec);

    err = pci_enable_device(pdev);
    if (err) {
        dev_err(&pdev->dev, "Помилка увімкнення пристрою: %d\n", err);
        return err;
    }

    pci_set_master(pdev);

    priv = kzalloc(sizeof(*priv), GFP_KERNEL);
    if (!priv) {
        err = -ENOMEM;
        goto err_disable;
    }
    priv->pdev = pdev;
    pci_set_drvdata(pdev, priv);

    err = pci_request_regions(pdev, DRIVER_NAME);
    if (err) {
        dev_err(&pdev->dev, "Не вдалося виділити MMIO-регіони: %d\n", err);
        goto err_free_priv;
    }

    priv->bar0_mmio = pci_iomap(pdev, 0, 0);
    if (!priv->bar0_mmio) {
        dev_err(&pdev->dev, "Помилка відображення BAR0\n");
        err = -EIO;
        goto err_release_regions;
    }

    /*
     * Виділення векторів переривань:
     * Просимо від 1 до nvec векторів із пріоритетом MSI-X.
     * Прапорець PCI_IRQ_AFFINITY автоматично розподіляє вектори по NUMA-вузлах.
     */
    allocated = pci_alloc_irq_vectors(pdev, 1, nvec,
                                      PCI_IRQ_MSIX | PCI_IRQ_MSI |
                                      PCI_IRQ_LEGACY | PCI_IRQ_AFFINITY);
    if (allocated < 0) {
        dev_err(&pdev->dev, "Не вдалося виділити переривання: %d\n", allocated);
        err = allocated;
        goto err_unmap;
    }

    priv->num_allocated_irqs = allocated;
    dev_info(&pdev->dev, "Успішно виділено %d векторів переривань\n", allocated);

    /* Реєстрація обробника для кожного виділеного вектора */
    for (i = 0; i < allocated; i++) {
        struct queue_context *q = &priv->queues[i];
        q->queue_id = i;
        q->parent = priv;
        q->irq = pci_irq_vector(pdev, i);
        atomic_set(&q->interrupt_count, 0);

        err = request_irq(q->irq, demo_queue_isr, 0, DRIVER_NAME, q);
        if (err) {
            dev_err(&pdev->dev, "Помилка request_irq для вектора %d (IRQ %u): %d\n",
                    i, q->irq, err);
            while (--i >= 0) {
                free_irq(priv->queues[i].irq, &priv->queues[i]);
            }
            goto err_free_vectors;
        }
    }

    return 0;

err_free_vectors:
    pci_free_irq_vectors(pdev);
err_unmap:
    pci_iounmap(pdev, priv->bar0_mmio);
err_release_regions:
    pci_release_regions(pdev);
err_free_priv:
    kfree(priv);
err_disable:
    pci_disable_device(pdev);
    return err;
}

static void demo_pci_remove(struct pci_dev *pdev)
{
    struct demo_device *priv = pci_get_drvdata(pdev);
    int i;

    dev_info(&pdev->dev, "Видалення драйвера, звільнення переривань\n");

    for (i = 0; i < priv->num_allocated_irqs; i++) {
        free_irq(priv->queues[i].irq, &priv->queues[i]);
    }

    pci_free_irq_vectors(pdev);
    pci_iounmap(pdev, priv->bar0_mmio);
    pci_release_regions(pdev);
    kfree(priv);
    pci_disable_device(pdev);
}

static const struct pci_device_id demo_pci_ids[] = {
    { PCI_DEVICE(0x10ee, 0x9038) }, /* Тестовий ідентифікатор FPGA/NIC */
    { 0, }
};
MODULE_DEVICE_TABLE(pci, demo_pci_ids);

static struct pci_driver demo_driver = {
    .name = DRIVER_NAME,
    .id_table = demo_pci_ids,
    .probe = demo_pci_probe,
    .remove = demo_pci_remove,
};

module_pci_driver(demo_driver);

MODULE_AUTHOR("Unix & Linux Systems Team");
MODULE_DESCRIPTION("Демонстраційний драйвер PCIe з підтримкою MSI-X");
MODULE_LICENSE("GPL");
```

## Діагностика через sysfs та ручне керування спорідненістю з простору користувача

Після успішного завантаження модуля ядро створює файли дескрипторів у каталозі `/sys/bus/pci/devices/<BDF>/msi_irqs/`. Кожен файл у цьому каталозі названо системним номером Linux IRQ, а його вміст вказує протокол доставки (`msix` або `msi`).

Для високонавантажених мережевих сервісів та баз даних стандартний автоматичний розподіл переривань демоном `irqbalance` часто вимикають. Замість цього застосовують строге ручне закріплення (англ. *IRQ pinning*), коли вектор кожної черги прив'язується до строго визначеного процесорного ядра або ізольованого сокета NUMA.

Керування спорідненістю здійснюється записом маски у файл `/proc/irq/<IRQ>/smp_affinity` (шістнадцяткова бітова маска) або у `/proc/irq/<IRQ>/smp_affinity_list` (список десяткових номерів ядер).

Нижче наведено повноцінний діагностичний інструмент простору користувача, реалізований мовами C та C++, який сканує виділені вектори MSI-X заданого PCI-пристрою і налаштовує їхню спорідненість до процесорних ядер за круговою схемою (round-robin).

:::tabs
```c
/*
 * msix_inspector.c — Перевірка векторів MSI-X та конфігурація SMP Affinity (C11)
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

static void set_irq_affinity(const char *irq_str, int cpu_id)
{
    char path[256];
    snprintf(path, sizeof(path), "/proc/irq/%s/smp_affinity_list", irq_str);

    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", path, strerror(errno));
        return;
    }

    char cpu_buf[32];
    int len = snprintf(cpu_buf, sizeof(cpu_buf), "%d\n", cpu_id);
    if (write(fd, cpu_buf, len) < 0) {
        fprintf(stderr, "Не вдалося записати спорідненість для IRQ %s: %s\n",
                irq_str, strerror(errno));
    } else {
        printf("IRQ %s успішно прив'язано до CPU %d\n", irq_str, cpu_id);
    }

    close(fd);
}

int main(int argc, char *argv[])
{
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <PCI BDF, наприклад 0000:01:00.0>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *bdf = argv[1];
    char msi_dir_path[256];
    snprintf(msi_dir_path, sizeof(msi_dir_path), "/sys/bus/pci/devices/%s/msi_irqs", bdf);

    DIR *dir = opendir(msi_dir_path);
    if (!dir) {
        fprintf(stderr, "Каталог %s не знайдено (пристрій не використовує MSI/MSI-X)\n",
                msi_dir_path);
        return EXIT_FAILURE;
    }

    printf("Аналіз переривань для пристрою %s:\n", bdf);
    struct dirent *entry;
    int cpu_counter = 0;
    long num_cpus = sysconf(_SC_NPROCESSORS_ONLN);

    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') {
            continue;
        }

        char file_path[512];
        snprintf(file_path, sizeof(file_path), "%s/%s", msi_dir_path, entry->d_name);

        FILE *f = fopen(file_path, "r");
        if (!f) {
            continue;
        }

        char irq_type[32];
        if (fgets(irq_type, sizeof(irq_type), f)) {
            irq_type[strcspn(irq_type, "\r\n")] = '\0';
            printf("  • Знайдено вектор Linux IRQ %s (тип: %s)\n", entry->d_name, irq_type);

            /* Призначаємо спорідненість до CPU */
            int target_cpu = cpu_counter % (int)num_cpus;
            set_irq_affinity(entry->d_name, target_cpu);
            cpu_counter++;
        }
        fclose(f);
    }

    closedir(dir);
    return EXIT_SUCCESS;
}
```
```cpp
//
// msix_inspector.cpp — Перевірка векторів MSI-X та конфігурація SMP Affinity (C++20)
//

#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <vector>
#include <system_error>
#include <unistd.h>

namespace fs = std::filesystem;

class IrqManager {
public:
    explicit IrqManager(std::string pci_bdf)
        : bdf_(std::move(pci_bdf)),
          num_cpus_(static_cast<int>(sysconf(_SC_NPROCESSORS_ONLN))) {}

    void inspect_and_balance() {
        const fs::path msi_path = fs::path("/sys/bus/pci/devices") / bdf_ / "msi_irqs";

        std::error_code ec;
        if (!fs::exists(msi_path, ec) || !fs::is_directory(msi_path, ec)) {
            std::cerr << "Каталог " << msi_path << " не знайдено (пристрій не має MSI/MSI-X)\n";
            return;
        }

        std::cout << "Аналіз переривань для пристрою " << bdf_ << ":\n";
        int cpu_index = 0;

        for (const auto &entry : fs::directory_iterator(msi_path)) {
            if (!entry.is_regular_file()) {
                continue;
            }

            const std::string irq_num = entry.path().filename().string();
            std::ifstream type_file(entry.path());
            std::string irq_type;

            if (std::getline(type_file, irq_type)) {
                std::cout << "  • Знайдено вектор Linux IRQ " << irq_num
                          << " (тип: " << irq_type << ")\n";

                int target_cpu = cpu_index % num_cpus_;
                bind_affinity(irq_num, target_cpu);
                cpu_index++;
            }
        }
    }

private:
    void bind_affinity(const std::string &irq, int cpu_id) {
        const fs::path aff_path = fs::path("/proc/irq") / irq / "smp_affinity_list";
        std::ofstream aff_file(aff_path);

        if (!aff_file) {
            std::cerr << "Не вдалося відкрити " << aff_path << " для запису\n";
            return;
        }

        aff_file << cpu_id << "\n";
        if (aff_file.good()) {
            std::cout << "IRQ " << irq << " успішно прив'язано до CPU " << cpu_id << "\n";
        } else {
            std::cerr << "Помилка запису спорідненості для IRQ " << irq << "\n";
        }
    }

    std::string bdf_;
    int num_cpus_;
};

int main(int argc, char *argv[])
{
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <PCI BDF, наприклад 0000:01:00.0>\n";
        return 1;
    }

    IrqManager manager(argv[1]);
    manager.inspect_and_balance();

    return 0;
}
```
:::

## Практична перевірка та спостереження за допомогою системних утиліт

Для верифікації коректності роботи реалізованого драйвера використовують системні інструменти Linux:

1. **Перевірка апаратного стану структури MSI-X Capability.**
   Команда `lspci -s 01:00.0 -vvv` відображає прапорець активації (`Enable+`), загальну кількість векторів таблиці (`Count=8`), стан маскування (`Masked-`) та базові регістри BAR, де розміщено `Vector table` та `PBA`.
2. **Перевірка розподілу лічильників переривань.**
   Команда `cat /proc/interrupts | grep msix_demo_pci` показує кількість подій, оброблених кожним процесорним ядром окремо. За умови коректного налаштування спорідненості лічильники кожного вектора зростають виключно у стовпчику призначеного йому CPU.
3. **Трасування затримки обробки через `ftrace` / `trace-cmd`.**
   Для вимірювання часу реакції верхньої половини обробника можна увімкнути ядерне трасування подій:
   ```
   # trace-cmd record -e irq:irq_handler_entry -e irq:irq_handler_exit
   # trace-cmd report
   ```
   Трасування підтверджує відсутність блокувальних MMIO-зчитувань у тілі `demo_queue_isr()`: час виконання обробника MSI-X зазвичай не перевищує 50–150 наносекунд.

## Типові помилки та пастки реалізації

1. **Виклик `request_irq` до увімкнення майстерингу шини.**
   Якщо не викликати `pci_set_master(pdev)`, контролер не зможе генерувати транзакції Memory Write на шині PCIe. Обробник переривання буде зареєстрований успішно, але жодне переривання в систему так і не прийде.
2. **Невивільнення векторів перед видаленням пристрою.**
   Виклик `pci_free_irq_vectors(pdev)` обов'язково має передувати виклику `pci_disable_device(pdev)`. Спроба вимкнути пристрій із зареєстрованими векторами залишає висячі дескриптори в підсистемі IRQ domain ядра, що призводить до kernel panic під час повторного підключення модуля.
3. **Ігнорування поверненого значення `pci_alloc_irq_vectors()`.**
   Функція повертає кількість **фактично виділених** векторів. Якщо драйвер просив 16 черг, але на платформі виявилося вільними лише 4 вектори, функція поверне `4`. Драйвер зобов'язаний адаптувати свою внутрішню структуру і створити лише 4 черги (або згрупувати кілька черг на один вектор), а не намагатися реєструвати обробники з 5 по 16.
4. **Використання прапорця `IRQF_SHARED` для векторів MSI-X.**
   Спроба передати `IRQF_SHARED` у функцію `request_irq()` для MSI-X вектора є концептуальною помилкою. Оскільки кожен вектор MSI-X є фронтальним і виділяється монопольно для однієї черги, спільне використання вектора різними обробниками не підтримується і може викликати непередбачувану поведінку диспетчера переривань.
