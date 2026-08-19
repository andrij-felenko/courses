# ⚙️ Маскування та емуляція CPUID у віртуалізації KVM

В [апаратній віртуалізації](book:programming/hardware-virtualization) гіпервізор повинен мати абсолютний контроль над тим, які можливості заліза бачить гостьова операційна система. Якщо в хмарному кластері частина серверів побудована на нових процесорах (наприклад, Intel Ice Lake з підтримкою AVX-512), а частина — на старіших (Intel Skylake), віртуальна машина, яка скомпілювала або завантажила бінарний код під AVX-512 на новому сервері, впаде з аварійною зупинкою (`SIGILL` / `#UD`) відразу після «гарячої» міграції (live migration) на старіший сервер.

Щоб забезпечити сумісність кластера, безпеку та ізоляцію, гіпервізор **перехоплює виконання інструкції CPUID** у непривілейованому гостьовому коді та повертає замість фізичних даних кремнію штучно сформовану (замасковану) таблицю конфігурації.

У цьому проекті розібрано програмний інтерфейс ядра Linux KVM (`/dev/kvm`), простежено внутрішній шлях обробки події `EXIT_REASON_CPUID` у ядрі, розібрано роботу з трасуванням подій `ftrace`, реалізовано фільтрацію бітів інструкцій та налаштовано віртуальний vCPU за допомогою системних викликів `ioctl`.

## Апаратне перехоплення CPUID у режимі VMX / SVM

У процесорах Intel VT-x та AMD-V виконання інструкції `CPUID` всередині гостьової віртуальної машини (режим VMX non-root) **безумовно викликає вихід у гіпервізор (VM-Exit)** з кодом причини `EXIT_REASON_CPUID` (код 10 в архітектурі Intel VMX). Це апаратна гарантія: гість ніколи не зможе виконати `CPUID` напряму в обхід гіпервізора.

Коли процесор фіксує опкод `0F A2` у гостьовому коді, апаратура виконує наступну послідовність дій:
1. Зберігає поточний стан регістрів гостя в керуючу структуру [VMCS](book:programming/hardware-virtualization) (Virtual Machine Control Structure) або [VMCB](book:programming/hardware-virtualization) в AMD;
2. Записує код причини виходу `EXIT_REASON_CPUID` у поле `VM_EXIT_REASON`;
3. Перемикає процесор у кореневий режим хоста (VMX root) і передає керування обробнику ядра `kvm_emulate_cpuid` у модулі `kvm-intel.ko` або `kvm-amd.ko`.

Ядро KVM дозволяє простору користувача (наприклад, процесу QEMU чи хмарному демону Firecracker) один раз передати сформовану таблицю листків через структуру `struct kvm_cpuid2`. Після цього KVM самостійно обробляє `EXIT_REASON_CPUID` всередині ядра на максимальній швидкості, не виходячи щоразу в простір користувача.

```
Внутрішній цикл емуляції CPUID у ядрі KVM (arch/x86/kvm/cpuid.c):
1. EAX_in = kvm_rax_read(vcpu);
2. ECX_in = kvm_rcx_read(vcpu);
3. entry = kvm_find_cpuid_entry(vcpu, EAX_in, ECX_in);
4. Якщо entry знайдено:
     kvm_rax_write(vcpu, entry->eax);
     kvm_rbx_write(vcpu, entry->ebx);
     kvm_rcx_write(vcpu, entry->ecx);
     kvm_rdx_write(vcpu, entry->edx);
   Інакше:
     обнулити всі чотири регістри.
5. kvm_rip_write(vcpu, kvm_rip_read(vcpu) + 2); // Інкремент RIP на 2 байти опкоду 0F A2
6. Виконати VM-Entry та повернутися до гостя.
```

```
Структура kvm_cpuid2 в Linux:
┌───────────────────────────────────────────────────────────┐
│ nent: кількість записів (struct kvm_cpuid_entry2)         │
│ padding: вирівнювання                                     │
│ entries[]: гнучкий масив структур записів листків:        │
│   ├── function: номер листка (EAX)                        │
│   ├── index: номер підлистка (ECX)                        │
│   ├── flags: прапорці KVM_CPUID_FLAG_SIGNIFCANT_INDEX     │
│   └── eax, ebx, ecx, edx: значення віртуальних регістрів  │
└───────────────────────────────────────────────────────────┘
```

## Прапорець SIGNIFCANT_INDEX: пастка підлистків

У структурі `struct kvm_cpuid_entry2` поле `flags` має вирішальне значення. За замовчуванням KVM під час пошуку запису перевіряє лише номер листка (`function`). Проте для листків зі структурованими підлистками (Leaf 4 для кешів, Leaf 7 для розширених прапорців, Leaf 0xD для XSAVE та Leaf 0x1F для топології) номер підлистка в `ECX` є значущим.

Якщо для таких листків у полі `flags` не встановити прапорець `KVM_CPUID_FLAG_SIGNIFCANT_INDEX`, ядро KVM під час пошуку візьме перший-ліпший запис із цим номером функції, проігнорувавши `ECX`. У результаті гостьова ОС отримуватиме однакові дані для всіх підлистків, що призведе до повного руйнування топології кешу або неможливості ініціалізувати AVX-512.

## Головні сценарії маскування у хмарній інфраструктурі

1. **Базові моделі процесорів для Live Migration (Міграція без зупинки):**
   Утиліта QEMU надає набір стандартизованих віртуальних моделей процесорів: `Nehalem`, `Westmere`, `SandyBridge`, `Haswell`, `Broadwell`, `Skylake-Server`, `Cascadelake-Server`, `EPYC-Rome`, `EPYC-Milan`. Гіпервізор на кожному вузлі кластера фільтрує відповіді `CPUID` так, щоб віртуальна машина «бачила» лише можливості обраної базової моделі, навіть якщо фізичний хост підтримує новіші інструкції.
2. **Апаратні латки від атак через спекулятивне виконання (Spectre/Meltdown):**
   Під час виявлення уразливостей у мікроархітектурі Intel та AMD випустили оновлення мікрокоду, які додали нові прапорці в Листок 7 (`EDX[26]` `IBRS`/`IBPB`, `EDX[27]` `STIBP`, `EDX[31]` `SSBD`) та Листок `0x80000008`. Гіпервізор повинен явно передавати ці біти у віртуальну машину, щоб гостьове ядро Linux увімкнуло захисні бар'єри у власних системних викликах.
3. **Паравіртуалізація та сигнатура гіпервізора (Листок 0x40000000):**
   Встановлення біта 31 у регістрі `ECX` Листка 1 повідомляє гостю про наявність віртуалізації. Гіпервізор створює листок `0x40000000`, де повертає власну текстову сигнатуру (наприклад, `"KVMKVMKVM\0\0\0"`), відкриваючи доступ до паравіртуальних інтерфейсів годинника KVM Clock, механізмів доставки переривань та гіпервикликів.
4. **Приховування віртуалізації (Bypass Anti-Cheat та робота з GPU):**
   Деякі пропрієтарні драйвери графічних прискорювачів та модулі захисту комп'ютерних ігор перевіряють біт `ECX[31]` або наявність листка `0x40000000`. Якщо вони виявляють роботу у віртуальному середовищі, вони блокують запуск. Спеціальне налаштування гіпервізора (наприклад, опція `kvm=off` та `hidden=on` у QEMU) повністю маскує ці ознаки, видаючи гостю паспорт справжнього комп'ютера.

## Трасування виходів CPUID через ftrace у Linux

Щоб переконатися, що емуляція `CPUID` працює і з'ясувати частоту викликів гостя, системний інженер може скористатися вбудованим механізмом трасування ядра Linux:

```bash
# Увімкнення трасування виходів VM-exit для CPUID
echo 1 > /sys/kernel/debug/tracing/events/kvm/kvm_cpuid/enable
echo 1 > /sys/kernel/debug/tracing/events/kvm/kvm_exit/enable

# Читання логу перехоплень у реальному часі
cat /sys/kernel/debug/tracing/trace_pipe
```

У виводі трасування з'являються докладні записи з номерами функцій та підлистків, які запитував гість:
```text
qemu-system-x86-12480 [004] kvm_exit:  reason CPUID rip 0xffffffff8105c3a0 info 0 0
qemu-system-x86-12480 [004] kvm_cpuid: func 1 idx 0 rax 0x806ec rbx 0x0 rcx 0x7ffafbff rdx 0x178bfbff
```

## Програмна реалізація маскування CPUID через KVM API

Створимо завершений програмний модуль на C та C++, який:
1. Відкриває інтерфейс KVM (`/dev/kvm`) та ініціалізує віртуальну машину з vCPU;
2. Зчитує список підтримуваних залізом листків через системний виклик `ioctl(kvm_fd, KVM_GET_SUPPORTED_CPUID, ...)`;
3. Маскує розширення (примусово вимикає AVX-512 для кластерної міграційної сумісності);
4. Встановлює біт присутності гіпервізора (`ECX[31]` у Листку 1) та записує фірмову сигнатуру в Листок `0x40000000`;
5. Застосовує оновлену таблицю до віртуального процесора через `ioctl(vcpu_fd, KVM_SET_CPUID2, ...)`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/kvm.h>

#define MAX_KVM_CPUID_ENTRIES 100

// Функція конфігурації та маскування листків CPUID для віртуального ядра
int configure_vcpu_cpuid(int vcpu_fd, int kvm_fd) {
    size_t size = sizeof(struct kvm_cpuid2) +
                  sizeof(struct kvm_cpuid_entry2) * MAX_KVM_CPUID_ENTRIES;
    struct kvm_cpuid2* cpuid = (struct kvm_cpuid2*)calloc(1, size);
    if (!cpuid) {
        return -1;
    }

    cpuid->nent = MAX_KVM_CPUID_ENTRIES;

    // Зчитуємо базову конфігурацію, яку підтримує фізичний хост
    if (ioctl(kvm_fd, KVM_GET_SUPPORTED_CPUID, cpuid) < 0) {
        free(cpuid);
        return -2;
    }

    // Проходимо по всіх отриманих листках та маскуємо потрібні біти
    for (uint32_t i = 0; i < cpuid->nent; ++i) {
        struct kvm_cpuid_entry2* entry = &cpuid->entries[i];

        // Листок 1: встановлюємо біт присутності гіпервізора (ECX біт 31)
        if (entry->function == 1) {
            entry->ecx |= (1U << 31); // HYPERVISOR bit
        }

        // Листок 7 (підлисток 0): маскуємо AVX-512 для міграційної сумісності
        if (entry->function == 7 && entry->index == 0) {
            entry->flags |= KVM_CPUID_FLAG_SIGNIFCANT_INDEX;
            entry->ebx &= ~(1U << 16); // Вимикаємо AVX512F
            entry->ebx &= ~(1U << 30); // Вимикаємо AVX512BW
            entry->ebx &= ~(1U << 31); // Вимикаємо AVX512VL
        }
    }

    // Додаємо власний паравіртуальний листок 0x40000000
    if (cpuid->nent < MAX_KVM_CPUID_ENTRIES) {
        struct kvm_cpuid_entry2* hyp = &cpuid->entries[cpuid->nent++];
        hyp->function = 0x40000000;
        hyp->index = 0;
        hyp->flags = 0;
        hyp->eax = 0x40000001; // Максимальний листок гіпервізора

        // 12-байтова сигнатура "CustomKVM\0\0\0"
        memcpy(&hyp->ebx, "Cust", 4);
        memcpy(&hyp->ecx, "omKV", 4);
        memcpy(&hyp->edx, "M\0\0\0", 4);
    }

    // Завантажуємо відфільтровану таблицю у стан віртуального ядра vCPU
    int res = ioctl(vcpu_fd, KVM_SET_CPUID2, cpuid);
    free(cpuid);
    return res;
}

int main(void) {
    int kvm_fd = open("/dev/kvm", O_RDWR | O_CLOEXEC);
    if (kvm_fd < 0) {
        perror("Не вдалося відкрити /dev/kvm");
        return 1;
    }

    int vm_fd = ioctl(kvm_fd, KVM_CREATE_VM, 0);
    if (vm_fd < 0) {
        close(kvm_fd);
        return 1;
    }

    int vcpu_fd = ioctl(vm_fd, KVM_CREATE_VCPU, 0);
    if (vcpu_fd < 0) {
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }

    if (configure_vcpu_cpuid(vcpu_fd, kvm_fd) == 0) {
        printf("CPUID віртуального процесора успішно налаштовано та замасковано.\n");
    }

    close(vcpu_fd);
    close(vm_fd);
    close(kvm_fd);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/kvm.h>

class ScopedFd {
public:
    explicit ScopedFd(int fd = -1) noexcept : fd_{fd} {}
    ~ScopedFd() noexcept { reset(); }

    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;

    ScopedFd(ScopedFd&& other) noexcept : fd_{other.release()} {}
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        const int old = fd_;
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
    int fd_{-1};
};

class KvmCpuidManager {
public:
    static constexpr std::size_t MaxEntries = 100;

    static bool apply_masked_cpuid(int vcpu_fd, int kvm_fd) {
        const std::size_t buffer_size = sizeof(struct kvm_cpuid2) +
                                        sizeof(struct kvm_cpuid_entry2) * MaxEntries;
        std::vector<std::uint8_t> buffer(buffer_size, 0);

        auto* cpuid = reinterpret_cast<struct kvm_cpuid2*>(buffer.data());
        cpuid->nent = static_cast<std::uint32_t>(MaxEntries);

        if (::ioctl(kvm_fd, KVM_GET_SUPPORTED_CPUID, cpuid) < 0) {
            return false;
        }

        for (std::uint32_t i = 0; i < cpuid->nent; ++i) {
            auto& entry = cpuid->entries[i];

            // Leaf 1: встановлюємо Hypervisor bit
            if (entry.function == 1) {
                entry.ecx |= (1U << 31);
            }

            // Leaf 7: маскуємо AVX-512
            if (entry.function == 7 && entry.index == 0) {
                entry.flags |= KVM_CPUID_FLAG_SIGNIFCANT_INDEX;
                entry.ebx &= ~(1U << 16); // AVX512F
                entry.ebx &= ~(1U << 30); // AVX512BW
                entry.ebx &= ~(1U << 31); // AVX512VL
            }
        }

        // Додаємо Leaf 0x40000000
        if (cpuid->nent < MaxEntries) {
            auto& hyp = cpuid->entries[cpuid->nent++];
            hyp.function = 0x40000000;
            hyp.index = 0;
            hyp.flags = 0;
            hyp.eax = 0x40000001;

            std::memcpy(&hyp.ebx, "Cust", 4);
            std::memcpy(&hyp.ecx, "omKV", 4);
            std::memcpy(&hyp.edx, "M\0\0\0", 4);
        }

        return ::ioctl(vcpu_fd, KVM_SET_CPUID2, cpuid) >= 0;
    }
};

int main() {
    ScopedFd kvm{::open("/dev/kvm", O_RDWR | O_CLOEXEC)};
    if (!kvm.valid()) {
        std::cerr << "Не вдалося відкрити /dev/kvm\n";
        return 1;
    }

    ScopedFd vm{::ioctl(kvm.get(), KVM_CREATE_VM, 0)};
    if (!vm.valid()) return 1;

    ScopedFd vcpu{::ioctl(vm.get(), KVM_CREATE_VCPU, 0)};
    if (!vcpu.valid()) return 1;

    if (KvmCpuidManager::apply_masked_cpuid(vcpu.get(), kvm.get())) {
        std::cout << "CPUID віртуального процесора успішно налаштовано.\n";
    }

    return 0;
}
```
:::

## Інженерні нюанси та верифікація конфігурації

1. **Проблема невідповідності MSR та CPUID:**
   Якщо гіпервізор увімкнув певний прапорець у `CPUID` (наприклад, біт підтримки `FSGSBASE` у Leaf 7 чи регістрів контролю безпеки `SPEC_CTRL`), але не дозволив доступ до відповідних системних регістрів MSR у бітовій карті перехоплення `MSR_BITMAP`, гостьова операційна система спробує звернутися до дозволеного нею регістра і отримає виключення загального захисту ([#GP](book:programming/cpu-exception-handling)). Конфігурація `CPUID` та `MSR_BITMAP` повинна бути суворо узгодженою.
2. **Топологія багатоядерності (Листок 0x0000001F та 0x0000000B):**
   Для правильного планування процесів гостьове ядро має розуміти структуру NUMA-вузлів, сокетів, фізичних ядер та логічних потоків (SMT / Hyper-Threading). Листок `0x1F` повертає ієрархію рівнів (SMT, Core, Module, Tile, Die, Package). Якщо гіпервізор неправильно налаштує біти зміщення APIC ID у цьому листку, гостьова ОС вважатиме віртуальні ядра окремими сокетами, що може призвести до порушення ліцензійних обмежень комерційного ПЗ або неоптимального розподілу пам'яті.
