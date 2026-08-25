# ⚙️ Налаштування KVM IRQFD та маршрутизації переривань у просторі користувача

Підсистема **IRQFD** у ядрі Linux дозволяє пов'язати дескриптор асинхронних подій `eventfd` безпосередньо з лінією переривання (GSI) віртуальної машини KVM. Щойно фоновий робочий потік, користувацький мережевий стек (наприклад, DPDK або SPDK) або емулятор пристрою записує 64-бітне число в `eventfd`, KVM у ядрі перехоплює сигнал і негайно інжектує відповідний вектор у vCPU без виходу у простір користувача та без виконання повторних системних викликів.

Нижче наведено детальний розбір архітектури швидкого шляху доставки подій, покроковий опис внутрішньої взаємодії з ядром та повний робочий приклад ініціалізації віртуальної машини KVM, створення внутрішньоядерного контролера переривань (`KVM_CREATE_IRQCHIP`), конфігурації таблиці маршрутизації GSI та асинхронної доставки сигналів через IRQFD мовами C та C++.

---

## 1. Архітектурний принцип та внутрішній конвеєр ядра

Традиційна схема доставки переривання від емульованого пристрою вимагає від простору користувача виконання виклику `ioctl(vcpu_fd, KVM_INTERRUPT)`. Це призводить до значних затримок: робочий потік змушений виконувати перехід у простір ядра, захоплювати м'ютекси vCPU та пробуджувати цільовий потік віртуального процесора.

Механізм **IRQFD** кардинально оптимізує цей процес за рахунок використання дескриптора `eventfd` ядра Linux як черги подій нульового копіювання:

```
[ Робочий потік (Worker Thread / DPDK) ]
                │
                ▼ (write 8 байтів: val = 1)
       [ struct file / eventfd ]
                │
                ▼ (wake_up на черзі очікування wait_queue)
       [ irqfd_wakeup() callback у kvm.ko ]
                │
                ▼ (Виклик безпосередньо в контексті події)
       [ kvm_set_irq(kvm, KVM_USERSPACE_IRQ_SOURCE_ID, gsi, 1) ]
                │
                ▼ (Пошук у таблиці RCU kvm_irq_routing_table)
       [ in-kernel IO-APIC / Local APIC ]
                │
                ▼ (Встановлення біта vIRR)
       [ Цільовий vCPU отримує вектор переривання ]
```

### Внутрішні етапи роботи KVM IRQFD:
1. **Реєстрація (`kvm_irqfd_assign`):** Під час виклику `ioctl(vm_fd, KVM_IRQFD)` ядро KVM отримує вказівник на структуру `struct file` відповідного `eventfd`. KVM ініціалізує внутрішню структуру `struct kvm_kernel_irqfd`, реєструє функцію зворотного виклику `irqfd_wakeup()` у черзі очікування `wait_queue_head_t` дескриптора `eventfd` за допомогою `init_waitqueue_func_entry()` та підключає її через `vfs_poll()`.
2. **Асинхронний сигнал (`write`):** Будь-який процес хоста або потік ядра, що володіє файловим дескриптором `eventfd`, виконує операцію `write(efd, &val, 8)`. Внутрішній 64-бітний лічильник дескриптора збільшується, і ядро миттєво викликає зареєстровану функцію `irqfd_wakeup()`.
3. **Пряма інжекція (`kvm_set_irq`):** Функція `irqfd_wakeup()` виконується безпосередньо в контексті потоку, який здійснив запис (або в контексті обробника переривань хоста). Вона зчитує номер GSI та викликає функцію `kvm_set_irq()`, яка знаходить цільовий пін у таблиці `struct kvm_irq_routing_table` (захищеній за допомогою RCU) та виставляє біт у черзі `vIRR` відповідного vCPU.
4. **Мінімальні блокування:** Завдяки використанню RCU для таблиць маршрутизації та атомарних бітових операцій для встановлення прапорців у Local APIC, доставка події через IRQFD практично не створює взаємних блокувань (lock contention) навіть за одночасної роботи десятків фонових потоків.

---

## 2. Реалізація: C та ідіоматичний C++

Нижче наведено повний зразок програми, яка створює віртуальну машину KVM, ініціалізує внутрішньоядерний контролер переривань (`KVM_CREATE_IRQCHIP`), налаштовує таблицю маршрутизації GSI 4 на пін 4 контролера IO-APIC, реєструє зв'язку `eventfd ↔ GSI` через `KVM_IRQFD` та запускає фоновий потік для асинхронної генерації переривань.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <pthread.h>
#include <sys/ioctl.h>
#include <sys/eventfd.h>
#include <linux/kvm.h>

struct worker_args {
    int efd;
    volatile int running;
};

static void* interrupt_worker(void* arg) {
    struct worker_args* args = (struct worker_args*)arg;
    uint64_t signal_val = 1;

    for (int i = 0; i < 5; ++i) {
        usleep(100000); // Інтервал 100 мс між подіями
        ssize_t s = write(args->efd, &signal_val, sizeof(signal_val));
        if (s != sizeof(signal_val)) {
            perror("Помилка запису в eventfd");
            break;
        }
        printf("[Worker] Сигнал переривання #%d надіслано через eventfd\n", i + 1);
    }
    args->running = 0;
    return NULL;
}

int main(void) {
    int kvm_fd = open("/dev/kvm", O_RDWR | O_CLOEXEC);
    if (kvm_fd < 0) {
        perror("Не вдалося відкрити /dev/kvm");
        return 1;
    }

    int vm_fd = ioctl(kvm_fd, KVM_CREATE_VM, 0);
    if (vm_fd < 0) {
        perror("Помилка створення віртуальної машини KVM_CREATE_VM");
        close(kvm_fd);
        return 1;
    }

    // 1. Створюємо in-kernel irqchip (PIC + IOAPIC + Local APIC)
    if (ioctl(vm_fd, KVM_CREATE_IRQCHIP, 0) < 0) {
        perror("Помилка ініціалізації KVM_CREATE_IRQCHIP");
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }

    // 2. Створюємо неблокуючий дескриптор eventfd
    int irq_efd = eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC);
    if (irq_efd < 0) {
        perror("Помилка створення eventfd");
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }

    // 3. Налаштовуємо таблицю маршрутизації переривань GSI
    struct kvm_irq_routing* routing = calloc(1, sizeof(struct kvm_irq_routing) +
                                                sizeof(struct kvm_irq_routing_entry));
    if (!routing) {
        perror("Не вдалося виділити пам'ять під таблицю маршрутизації");
        close(irq_efd);
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }

    routing->nr = 1;
    routing->flags = 0;
    routing->entries[0].gsi = 4; // Прив'язка до лінії GSI 4
    routing->entries[0].type = KVM_IRQ_ROUTING_IRQCHIP;
    routing->entries[0].u.irqchip.irqchip = KVM_IRQCHIP_IOAPIC;
    routing->entries[0].u.irqchip.pin = 4; // Пін 4 на контролері IO-APIC

    if (ioctl(vm_fd, KVM_SET_GSI_ROUTING, routing) < 0) {
        perror("Помилка налаштування KVM_SET_GSI_ROUTING");
        free(routing);
        close(irq_efd);
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }
    free(routing);

    // 4. Реєструємо зв'язку IRQFD
    struct kvm_irqfd irqfd_cfg;
    memset(&irqfd_cfg, 0, sizeof(irqfd_cfg));
    irqfd_cfg.fd = irq_efd;
    irqfd_cfg.gsi = 4;
    irqfd_cfg.flags = 0;

    if (ioctl(vm_fd, KVM_IRQFD, &irqfd_cfg) < 0) {
        perror("Помилка прив'язки KVM_IRQFD");
        close(irq_efd);
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }

    printf("[Host] IRQFD успішно прив'язано до GSI 4. Запуск генератора подій...\n");

    // 5. Запускаємо фоновий робочий потік
    struct worker_args args = { .efd = irq_efd, .running = 1 };
    pthread_t thread;
    if (pthread_create(&thread, NULL, interrupt_worker, &args) == 0) {
        pthread_join(thread, NULL);
    }

    // 6. Відв'язуємо дескриптор перед завершенням роботи
    irqfd_cfg.flags = KVM_IRQFD_FLAG_DEASSIGN;
    ioctl(vm_fd, KVM_IRQFD, &irqfd_cfg);

    close(irq_efd);
    close(vm_fd);
    close(kvm_fd);
    printf("[Host] Ресурси успішно звільнено, пайплайн переривань зупинено.\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
#include <stdexcept>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/eventfd.h>
#include <linux/kvm.h>

// RAII обгортка для безпечного керування системними дескрипторами Linux
class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_;
};

// Контролер життєвого циклу підсистеми віртуальних переривань KVM
class KvmIrqPipeline {
public:
    KvmIrqPipeline() {
        kvm_fd_.reset(::open("/dev/kvm", O_RDWR | O_CLOEXEC));
        if (!kvm_fd_.valid()) {
            throw std::system_error(errno, std::generic_category(), "Відкриття /dev/kvm невдале");
        }

        vm_fd_.reset(::ioctl(kvm_fd_.get(), KVM_CREATE_VM, 0));
        if (!vm_fd_.valid()) {
            throw std::system_error(errno, std::generic_category(), "KVM_CREATE_VM помилка створення VM");
        }

        // 1. Створюємо in-kernel irqchip
        if (::ioctl(vm_fd_.get(), KVM_CREATE_IRQCHIP, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "KVM_CREATE_IRQCHIP помилка");
        }

        // 2. Створюємо non-blocking eventfd
        irq_efd_.reset(::eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC));
        if (!irq_efd_.valid()) {
            throw std::system_error(errno, std::generic_category(), "Створення eventfd невдале");
        }
    }

    void setupRoutingAndIrqfd(uint32_t target_gsi, uint32_t ioapic_pin) {
        // 3. Формуємо динамічний буфер під структуру KVM маршрутизації
        std::vector<uint8_t> buffer(sizeof(struct kvm_irq_routing) + sizeof(struct kvm_irq_routing_entry), 0);
        auto* routing = reinterpret_cast<struct kvm_irq_routing*>(buffer.data());

        routing->nr = 1;
        routing->flags = 0;
        routing->entries[0].gsi = target_gsi;
        routing->entries[0].type = KVM_IRQ_ROUTING_IRQCHIP;
        routing->entries[0].u.irqchip.irqchip = KVM_IRQCHIP_IOAPIC;
        routing->entries[0].u.irqchip.pin = ioapic_pin;

        if (::ioctl(vm_fd_.get(), KVM_SET_GSI_ROUTING, routing) < 0) {
            throw std::system_error(errno, std::generic_category(), "KVM_SET_GSI_ROUTING помилка");
        }

        // 4. Прив'язуємо eventfd до GSI лінії
        std::memset(&irqfd_cfg_, 0, sizeof(irqfd_cfg_));
        irqfd_cfg_.fd = irq_efd_.get();
        irqfd_cfg_.gsi = target_gsi;
        irqfd_cfg_.flags = 0;

        if (::ioctl(vm_fd_.get(), KVM_IRQFD, &irqfd_cfg_) < 0) {
            throw std::system_error(errno, std::generic_category(), "KVM_IRQFD помилка реєстрації");
        }
        gsi_bound_ = true;
    }

    void triggerInterrupt() const {
        uint64_t val = 1;
        ssize_t bytes = ::write(irq_efd_.get(), &val, sizeof(val));
        if (bytes != sizeof(val)) {
            throw std::system_error(errno, std::generic_category(), "Запис у дескриптор eventfd невдалий");
        }
    }

    ~KvmIrqPipeline() {
        // Гарантоване відв'язування IRQFD перед закриттям дескрипторів
        if (gsi_bound_ && vm_fd_.valid()) {
            irqfd_cfg_.flags = KVM_IRQFD_FLAG_DEASSIGN;
            ::ioctl(vm_fd_.get(), KVM_IRQFD, &irqfd_cfg_);
        }
    }

private:
    UniqueFd kvm_fd_;
    UniqueFd vm_fd_;
    UniqueFd irq_efd_;
    struct kvm_irqfd irqfd_cfg_{};
    bool gsi_bound_{false};
};

int main() {
    try {
        KvmIrqPipeline pipeline;
        constexpr uint32_t test_gsi = 4;
        pipeline.setupRoutingAndIrqfd(test_gsi, 4);

        std::cout << "[Host] C++ RAII пайплайн налаштовано для GSI " << test_gsi << ".\n";

        std::thread worker([&pipeline]() {
            for (int i = 0; i < 5; ++i) {
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
                pipeline.triggerInterrupt();
                std::cout << "[Worker] Асинхронне переривання #" << (i + 1) << " доставлено в KVM!\n";
            }
        });

        worker.join();
        std::cout << "[Host] Усі події оброблено. Автоматичне завершення.\n";
    } catch (const std::exception& ex) {
        std::cerr << "Виняткова ситуація: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

---

## 3. Практичні аспекти, оптимізація та крайові випадки

### Імпульсні (Edge-triggered) проти рівневих (Level-triggered) сигналів
* **Імпульсні сигнали (Edge / MSI / MSI-X):** Більшість сучасних віртуальних пристроїв Virtio використовують імпульсну семантику. Для них запис у `eventfd` є самодостатньою подією: один виклик `write()` призводить до встановлення біта в `vIRR` та одноразового виклику обробника гостьового ядра.
* **Рівневі сигнали (Level / INTx Resampling):** Застарілі емульовані пристрої шини PCI (наприклад, мережеві адаптери e1000 або контролери IDE) вимагають утримання логічного рівня переривання доти, доки гостьовий драйвер не виконає скидання регістрів стану пристрою та не підтвердить завершення обробки записом у регістр `EOI`.
  
  Для таких ліній прапорець `KVM_IRQFD_FLAG_RESAMPLE` у структурі `struct kvm_irqfd` є обов'язковим. KVM реєструє внутрішній перехоплювач EOI (EOI intercept callback). Щойно гостьова ОС записує нуль у регістр EOI локального контролера APIC, KVM генерує подію в дескриптор `resamplefd`, сповіщаючи емулятор пристрою на хості про готовність приймати наступні запити. Без ресемплінгу лінія переривання назавжди зависне в активному стані (IRQ starvation).

### Переповнення лічильника eventfd та неблокуючий режим
Дескриптор `eventfd` зберігає 64-розрядне беззнакове число (`uint64_t`). Кожен виклик `write()` додає передане значення до внутрішнього лічильника ядра.

1. **Неблокуючий ввід/вивід (`EFD_NONBLOCK`):** Якщо лічильник досягає максимального значення `0xFFFFFFFFFFFFFFFE`, наступний виклик `write()` у блокуючому режимі зупинить виконання робочого потоку. Використання прапорця `EFD_NONBLOCK` гарантує повернення помилки `EAGAIN`, запобігаючи деградації та зависанню високопродуктивних потоків обробки трафіку (fast-path workers).
2. **Пакетизація подій:** Якщо робочий потік генерує переривання швидше, ніж vCPU встигає їх обробляти, лічильник `eventfd` накопичує кількість подій. KVM виконує коалесценцію (об'єднання сигналів), запобігаючи переповненню черг переривань у гостьовому ядрі.

### Використання в архітектурі vhost та VFIO
* **`vhost-net` і `vhost-user`:** Драйвери передають файловий дескриптор `eventfd` безпосередньо у відповідний потік ядра хоста або користувацький процес (наприклад, OVS-DPDK). При надходженні мережевого пакета драйвер виконує запис у дескриптор у контексті мережевого обробника softirq/NAPI, зводячи затримку доставки до часток мікросекунди.
* **`vfio-pci`:** Підсистема прямого доступу до апаратних пристроїв використовує `eventfd` для трансляції апаратних ліній MSI/MSI-X хоста у віртуальні лінії GSI гостьової віртуальної машини, коли пряма апаратна доставка (Posted Interrupts) не підтримується чипсетом або процесором хоста.
