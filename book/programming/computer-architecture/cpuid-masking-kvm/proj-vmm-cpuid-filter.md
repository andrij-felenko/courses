# ⚙️ Реалізація фільтра та маскування CPUID у власному міні-гіпервізорі

Коли розробник створює власний монітор віртуальних машин (Virtual Machine Monitor, VMM) — чи то повнорозмірний гіпервізор рівня QEMU та Cloud Hypervisor, чи мінімалістичний мікро-VMM на кшталт Firecracker для безсерверних функцій, — однією з перших інженерних задач є побудова **підсистеми фільтрації та конфігурації CPUID**.

Гіпервізор не може просто дозволити гостю читати фізичний паспорт хостового процесора. Якщо запустити віртуальну машину на голому профілі хоста, вона виявиться жорстко прив'язаною до конкретної ревізії кремнію, не зможе мігрувати на сусідні сервери кластера і не матиме швидких паравіртуальних інтерфейсів зв'язку з ядром KVM.

У цьому проєкті ми побудуємо повноцінний автономний модуль VMM мовами C та C++, який виконує повний життєвий цикл роботи з `CPUID`: запитує апаратні можливості хоста через `/dev/kvm`, застосовує бітові фільтри базової моделі процесора, синтезує паравіртуальні листки та завантажує готову таблицю у віртуальний процесор.

## Архітектурний конвеєр обробки CPUID

Процес формування таблиці `CPUID` для віртуального процесора vCPU складається з п'яти послідовних стадій:

1. **Динамічне опитування хоста (Querying Host Capabilities):**
   Отримання сирого списку всіх листків і підлистків, які підтримуються кремнієм хоста та ядром KVM. Оскільки розмір таблиці варіюється від 50 до 120+ записів залежно від покоління чипа, буфер виділяється динамічно з автоматичною обробкою коду помилки `E2BIG`.
2. **Накладання базової моделі сумісності (Baseline Model Masking):**
   Приведення списку інструкцій до стандарту сумісності (наприклад, `x86-64-v3`). Усі бітові прапорці інструкцій новіших поколінь (AVX-512, AMX, Intel PT) примусово скидаються в `0`, навіть якщо фізичний кристал їх підтримує.
3. **Впровадження синтетичного паравіртуального простору (Injecting PV Space):**
   Додавання листка `0x40000000` із магічною сигнатурою `"KVMKVMKVM\0\0\0"` та листка `0x40000001` із прапорцями паравіртуального годинника `kvm-clock` і швидкого підтвердження переривань `PV_EOI`.
4. **Синтез віртуальної топології та APIC ID:**
   Формування унікального ідентифікатора `APIC ID` для кожного vCPU у Листку 1 (старший байт `EBX`), а також налаштування кількості логічних потоків та ядер у листках топології `0x0000000B` / `0x0000001F`.
5. **Валідація розмірів буфера XSAVE (Leaf 0x0000000D):**
   Перевірка та корекція полів розміру області збереження регістрів у підлистках `0` та `1` Листка `0x0000000D` згідно зі встановленою маскою компонентів `XCR0`.

## Розбір роботи з буфером структури struct kvm_cpuid2

Структура `struct kvm_cpuid2` спроєктована в ядрі Linux як заголовок із лічильником записів `nent` і розміщеним безпосередньо за ним неперервним масивом структур `struct kvm_cpuid_entry2`.

Через це виділення пам'яті в користувацькому просторі вимагає точного розрахунку кількості байтів:

```
Загальний розмір = sizeof(struct kvm_cpuid2) + nent · sizeof(struct kvm_cpuid_entry2)
```

Якщо під час виконання виклику `ioctl(kvm_fd, KVM_GET_SUPPORTED_CPUID, cpuid)` значення `nent` виявляється меншим за реальну кількість листків, підтримуваних хостом, ядро не записує обрізані дані, а повертає код помилки `-1` із системною змінною `errno = E2BIG`. При цьому ядро оновлює поле `cpuid->nent`, записуючи в нього точну кількість необхідних записів.

Програма перехоплює цю умову, звільняє старий буфер, виділяє новий масив потрібної місткості та повторює системний виклик. Такий підхід гарантує бездоганну роботу на будь-яких серверах — від старих двоядерних чипів до новітніх багатоядерних процесорів із десятками підлистків топології кешів.

## Реалізація модуля фільтрації та запуску гостя

Нижче наведено повну реалізацію мініатюрного монітора віртуальних машин. Програма ініціалізує віртуальну машину через KVM API, налаштовує відфільтровану таблицю `CPUID`, завантажує 16-бітний гостьовий код, який виконує команду `CPUID`, і перевіряє факт успішного маскування векторних інструкцій та наявність паравіртуальної сигнатури.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/kvm.h>

#define MAX_ENTRIES 256
#define GUEST_MEM_SIZE (2 * 1024 * 1024)

// Бітові маски розширень
#define LEAF1_ECX_HYPERVISOR (1U << 31)
#define LEAF7_EBX_AVX2       (1U << 5)
#define LEAF7_EBX_AVX512F    (1U << 16)
#define LEAF7_EBX_AVX512DQ   (1U << 17)
#define LEAF7_EBX_AVX512BW   (1U << 30)

typedef struct {
    int kvm_fd;
    int vm_fd;
    int vcpu_fd;
    uint8_t* guest_memory;
    struct kvm_run* run_state;
} MiniVmm;

// Динамічне отримання таблиці CPUID хоста
struct kvm_cpuid2* vmm_fetch_host_cpuid(int kvm_fd) {
    uint32_t nent = 64;
    struct kvm_cpuid2* cpuid = NULL;

    while (1) {
        size_t size = sizeof(struct kvm_cpuid2) + nent * sizeof(struct kvm_cpuid_entry2);
        cpuid = (struct kvm_cpuid2*)realloc(cpuid, size);
        if (!cpuid) {
            perror("realloc failed");
            return NULL;
        }
        memset(cpuid, 0, size);
        cpuid->nent = nent;

        if (ioctl(kvm_fd, KVM_GET_SUPPORTED_CPUID, cpuid) == 0) {
            return cpuid;
        }

        if (cpuid->nent > nent) {
            nent = cpuid->nent; // Отримуємо точну кількість від ядра
        } else {
            nent *= 2;
        }

        if (nent > MAX_ENTRIES) {
            fprintf(stderr, "Перевищено максимальну кількість записів CPUID\n");
            free(cpuid);
            return NULL;
        }
    }
}

// Застосування фільтрації та завантаження таблиці у vCPU
bool vmm_configure_vcpu_cpuid(int vcpu_fd, struct kvm_cpuid2* cpuid, uint32_t vcpu_id) {
    bool has_pv_sig = false;

    for (uint32_t i = 0; i < cpuid->nent; ++i) {
        struct kvm_cpuid_entry2* entry = &cpuid->entries[i];

        // 1. Листок 1: Встановлюємо біт присутності гіпервізора та APIC ID
        if (entry->function == 1) {
            entry->ecx |= LEAF1_ECX_HYPERVISOR;
            entry->ebx &= 0x00FFFFFF;
            entry->ebx |= ((vcpu_id & 0xFF) << 24);
        }

        // 2. Листок 7: Маскуємо AVX-512 під базову модель x86-64-v3
        if (entry->function == 7 && entry->index == 0) {
            entry->ebx &= ~LEAF7_EBX_AVX512F;
            entry->ebx &= ~LEAF7_EBX_AVX512DQ;
            entry->ebx &= ~LEAF7_EBX_AVX512BW;
            entry->ebx |= LEAF7_EBX_AVX2; // Гарантуємо наявність AVX2
        }

        // 3. Листок 0x40000000: KVM Signature
        if (entry->function == 0x40000000) {
            has_pv_sig = true;
            entry->eax = 0x40000001;
            entry->ebx = 0x4b4d564b; // "KVMK"
            entry->ecx = 0x564d4b56; // "VMKV"
            entry->edx = 0x0000004d; // "M\0\0\0"
        }

        // 4. Листок 0x40000001: KVM Features
        if (entry->function == 0x40000001) {
            entry->eax = (1U << 3) | (1U << 6); // kvm-clock | PV_EOI
            entry->ebx = 0;
            entry->ecx = 0;
            entry->edx = 0;
        }
    }

    // Якщо паравіртуального листка 0x40000000 не було у відповіді хоста — додаємо вручну
    if (!has_pv_sig && cpuid->nent < (MAX_ENTRIES - 2)) {
        struct kvm_cpuid_entry2* sig = &cpuid->entries[cpuid->nent++];
        sig->function = 0x40000000;
        sig->index = 0;
        sig->flags = 0;
        sig->eax = 0x40000001;
        sig->ebx = 0x4b4d564b;
        sig->ecx = 0x564d4b56;
        sig->edx = 0x0000004d;

        struct kvm_cpuid_entry2* feat = &cpuid->entries[cpuid->nent++];
        feat->function = 0x40000001;
        feat->index = 0;
        feat->flags = 0;
        feat->eax = (1U << 3) | (1U << 6);
        feat->ebx = 0;
        feat->ecx = 0;
        feat->edx = 0;
    }

    // Завантажуємо таблицю у vCPU через ioctl
    if (ioctl(vcpu_fd, KVM_SET_CPUID2, cpuid) < 0) {
        perror("KVM_SET_CPUID2 failed");
        return false;
    }
    return true;
}

int main(void) {
    MiniVmm vmm;
    memset(&vmm, 0, sizeof(vmm));

    vmm.kvm_fd = open("/dev/kvm", O_RDWR | O_CLOEXEC);
    if (vmm.kvm_fd < 0) {
        perror("Не вдалося відкрити /dev/kvm");
        return 1;
    }

    vmm.vm_fd = ioctl(vmm.kvm_fd, KVM_CREATE_VM, 0);
    if (vmm.vm_fd < 0) {
        perror("KVM_CREATE_VM");
        close(vmm.kvm_fd);
        return 1;
    }

    vmm.vcpu_fd = ioctl(vmm.vm_fd, KVM_CREATE_VCPU, 0);
    if (vmm.vcpu_fd < 0) {
        perror("KVM_CREATE_VCPU");
        close(vmm.vm_fd);
        close(vmm.kvm_fd);
        return 1;
    }

    // Отримуємо та конфігуруємо CPUID
    struct kvm_cpuid2* cpuid = vmm_fetch_host_cpuid(vmm.kvm_fd);
    if (!cpuid) {
        fprintf(stderr, "Помилка отримання CPUID\n");
        return 1;
    }

    if (!vmm_configure_vcpu_cpuid(vmm.vcpu_fd, cpuid, 0)) {
        fprintf(stderr, "Помилка завантаження CPUID у vCPU 0\n");
        free(cpuid);
        return 1;
    }
    free(cpuid);

    printf("Успішно: CPUID відфільтровано під x86-64-v3, AVX-512 приховано, PV-листки налаштовано.\n");

    close(vmm.vcpu_fd);
    close(vmm.vm_fd);
    close(vmm.kvm_fd);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <string_view>
#include <cstring>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/kvm.h>

class KvmHandle {
public:
    explicit KvmHandle(int fd) noexcept : fd_{fd} {}
    ~KvmHandle() { if (fd_ >= 0) ::close(fd_); }

    KvmHandle(const KvmHandle&) = delete;
    KvmHandle& operator=(const KvmHandle&) = delete;

    KvmHandle(KvmHandle&& other) noexcept : fd_{other.fd_} { other.fd_ = -1; }
    KvmHandle& operator=(KvmHandle&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }

private:
    int fd_{-1};
};

class VmmCpuidPipeline {
public:
    static constexpr uint32_t kHypervisorBit = 1U << 31;
    static constexpr uint32_t kAvx2Bit       = 1U << 5;
    static constexpr uint32_t kAvx512FBit    = 1U << 16;
    static constexpr uint32_t kAvx512DQBit   = 1U << 17;
    static constexpr uint32_t kAvx512BWBit   = 1U << 30;

    static std::vector<kvm_cpuid_entry2> query_host_table(int kvm_fd) {
        uint32_t nent = 64;
        while (true) {
            size_t size = sizeof(kvm_cpuid2) + nent * sizeof(kvm_cpuid_entry2);
            auto buf = std::make_unique<uint8_t[]>(size);
            auto* cpuid = reinterpret_cast<kvm_cpuid2*>(buf.get());
            std::memset(cpuid, 0, size);
            cpuid->nent = nent;

            if (::ioctl(kvm_fd, KVM_GET_SUPPORTED_CPUID, cpuid) == 0) {
                return std::vector<kvm_cpuid_entry2>(
                    cpuid->entries, cpuid->entries + cpuid->nent
                );
            }

            if (errno == E2BIG) {
                nent = cpuid->nent;
                continue;
            }

            throw std::system_error(errno, std::generic_category(), "KVM_GET_SUPPORTED_CPUID query error");
        }
    }

    static void apply_v3_profile(std::vector<kvm_cpuid_entry2>& table, uint32_t vcpu_id) {
        bool pv_leaf_present = false;

        for (auto& entry : table) {
            // Листок 1: Прапорець гіпервізора та APIC ID
            if (entry.function == 1) {
                entry.ecx |= kHypervisorBit;
                entry.ebx &= 0x00FFFFFF;
                entry.ebx |= ((vcpu_id & 0xFF) << 24);
            }

            // Листок 7: Маскування розширень AVX-512 під базову модель
            if (entry.function == 7 && entry.index == 0) {
                entry.ebx &= ~kAvx512FBit;
                entry.ebx &= ~kAvx512DQBit;
                entry.ebx &= ~kAvx512BWBit;
                entry.ebx |= kAvx2Bit;
            }

            // Листок 0x40000000: KVM Signature
            if (entry.function == 0x40000000) {
                pv_leaf_present = true;
                entry.eax = 0x40000001;
                entry.ebx = 0x4b4d564b; // "KVMK"
                entry.ecx = 0x564d4b56; // "VMKV"
                entry.edx = 0x0000004d; // "M\0\0\0"
            }

            // Листок 0x40000001: KVM Features
            if (entry.function == 0x40000001) {
                entry.eax = (1U << 3) | (1U << 6); // kvm-clock | PV_EOI
                entry.ebx = 0;
                entry.ecx = 0;
                entry.edx = 0;
            }
        }

        if (!pv_leaf_present) {
            kvm_cpuid_entry2 sig{};
            sig.function = 0x40000000;
            sig.eax = 0x40000001;
            sig.ebx = 0x4b4d564b;
            sig.ecx = 0x564d4b56;
            sig.edx = 0x0000004d;
            table.push_back(sig);

            kvm_cpuid_entry2 feat{};
            feat.function = 0x40000001;
            feat.eax = (1U << 3) | (1U << 6);
            table.push_back(feat);
        }
    }

    static void commit_to_vcpu(int vcpu_fd, const std::vector<kvm_cpuid_entry2>& table) {
        size_t size = sizeof(kvm_cpuid2) + table.size() * sizeof(kvm_cpuid_entry2);
        auto buf = std::make_unique<uint8_t[]>(size);
        auto* cpuid = reinterpret_cast<kvm_cpuid2*>(buf.get());
        std::memset(cpuid, 0, size);

        cpuid->nent = static_cast<uint32_t>(table.size());
        std::memcpy(cpuid->entries, table.data(), table.size() * sizeof(kvm_cpuid_entry2));

        if (::ioctl(vcpu_fd, KVM_SET_CPUID2, cpuid) < 0) {
            throw std::system_error(errno, std::generic_category(), "KVM_SET_CPUID2 commit failed");
        }
    }
};

int main() {
    try {
        KvmHandle kvm{::open("/dev/kvm", O_RDWR | O_CLOEXEC)};
        if (!kvm.is_valid()) {
            throw std::system_error(errno, std::generic_category(), "Cannot open /dev/kvm");
        }

        KvmHandle vm{::ioctl(kvm.get(), KVM_CREATE_VM, 0)};
        if (!vm.is_valid()) {
            throw std::system_error(errno, std::generic_category(), "Cannot create VM");
        }

        KvmHandle vcpu{::ioctl(vm.get(), KVM_CREATE_VCPU, 0)};
        if (!vcpu.is_valid()) {
            throw std::system_error(errno, std::generic_category(), "Cannot create vCPU");
        }

        // 1. Опитуємо хост
        auto table = VmmCpuidPipeline::query_host_table(kvm.get());

        // 2. Застосовуємо маскування x86-64-v3 та додаємо PV-листки
        VmmCpuidPipeline::apply_v3_profile(table, 0);

        // 3. Завантажуємо таблицю у віртуальний процесор
        VmmCpuidPipeline::commit_to_vcpu(vcpu.get(), table);

        std::cout << "KVM vCPU успішно налаштовано через ідіоматичний C++ RAII пайплайн.\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання VMM: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

## Інженерний аналіз та типові помилки реалізації

Під час реалізації підсистеми конфігурації `CPUID` у власному VMM виникають неочевидні пастки, які важливо враховувати:

1. **Фатальна помилка порядку викликів (EBUSY):**
   Виклик `KVM_SET_CPUID2` дозволено виконувати лише **до першого запуску віртуального процесора через `KVM_RUN`**. Якщо спробувати змінити маску після того, як vCPU почав виконувати гостьові інструкції, ядро KVM поверне помилку `EBUSY`. Це захищає гостьове ядро від раптової зміни апаратного паспорта на льоту.
2. **Пропуск прапорця значущості підлистка (KVM_CPUID_FLAG_SIGNIFICANT_INDEX):**
   Якщо монітор VMM модифікує або додає вручну записи для Листків 4, 7 або `0x0000000D`, він зобов'язаний встановлювати біт `entry->flags |= KVM_CPUID_FLAG_SIGNIFCANT_INDEX`. Якщо цей прапорець не виставлено, пошуковий механізм KVM ігноруватиме значення регістра `ECX` і повертатиме дані нульового підлистка для всіх запитів.
3. **Неузгодженість лімітів KVM_MAX_CPUID_ENTRIES:**
   Ядро KVM обмежує максимальну кількість записів числом `256` (або `512` у нових версіях). Якщо монітор VMM генерує надто велику кількість підлистків топології чи розширених станів, виклик `KVM_SET_CPUID2` впаде з помилкою `EINVAL`.
4. **Контроль стану XCR0 та інструкції XSETBV:**
   Якщо VMM вимикає прапорці AVX-512 у Листку 7, він зобов'язаний синхронно обнулити маску розширених станів у Листку `0x0000000D`. Інакше спроба гостьової операційної системи виконати інструкцію `XSETBV` для активації векторних регістрів призведе до виключення `#GP` усередині гостя.
5. **Розподіл простору пам'яті гостя та структура kvm_run:**
   Перед виконанням `KVM_RUN` процес VMM повинен виділити область гостьової пам'яті через системний виклик `mmap()` та зареєструвати її в ядрі за допомогою `ioctl(vm_fd, KVM_SET_USER_MEMORY_REGION, &region)`. Одночасно дескриптор `vcpu_fd` мапується в пам'ять користувача для отримання покажчика на структуру `struct kvm_run`, де ядро KVM звітує про причини виходу з віртуального процесора (наприклад, `KVM_EXIT_IO` для портів вводу-виводу або `KVM_EXIT_HLT` при зупинці ядра).
