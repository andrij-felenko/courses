# 📋 Інтерфейс ioctl для конфігурації CPUID у ядрі KVM

Підсистема віртуалізації Linux KVM (Kernel-based Virtual Machine) надає розробникам моніторів віртуальних машин (VMM) низькорівневий інтерфейс керування віртуальним процесором через системні виклики `ioctl` над файловими дескрипторами `/dev/kvm`, дескрипторами віртуальної машини `vm_fd` та дескрипторами конкретного віртуального процесора `vcpu_fd`.

Конфігурація інструкції `CPUID` є ключовою частиною ініціалізації vCPU. Вона визначає, які апаратні прапорці, назву виробника, топологію кешів та паравіртуальні інтерфейси бачитиме гостьова операційна система. Усі структури даних, бітові маски та константи команд визначено в системному заголовному файлі ядра Linux `<linux/kvm.h>`.

## Огляд команд ioctl підсистеми CPUID

Керування `CPUID` у KVM розділено на дві фази: **інтроспекцію можливостей хоста** (виконується над загальним дескриптором підсистеми KVM) та **завантаження конфігурації у vCPU** (виконується над дескриптором конкретного віртуального процесора перед його першим запуском).

| Команда `ioctl` | Цільовий дескриптор | Опис та семантика виклику |
| :--- | :--- | :--- |
| `KVM_GET_SUPPORTED_CPUID` | `/dev/kvm` | Повертає повний перелік листків і бітових прапорців, які фізично підтримуються кремнієм хоста та можуть бути безпечно надані гостю ядром KVM. |
| `KVM_GET_EMULATED_CPUID` | `/dev/kvm` | Повертає перелік прапорців інструкцій, які ядро KVM здатне повністю емулювати програмно, навіть якщо фізичний процесор хоста їх не підтримує. |
| `KVM_SET_CPUID2` | `vcpu_fd` | Завантажує остаточну відфільтровану таблицю листків `CPUID` у структуру віртуального процесора. Фіксує апаратний паспорт vCPU. |
| `KVM_GET_CPUID2` | `vcpu_fd` | Зчитує поточну активну таблицю `CPUID`, завантажену у віртуальний процесор. Використовується під час збереження стану для міграції. |

### Різниця між підтримуваними та емульованими можливостями

Важливо розрізняти результат викликів `KVM_GET_SUPPORTED_CPUID` та `KVM_GET_EMULATED_CPUID`:

1. **`KVM_GET_SUPPORTED_CPUID`** повертає перетин фізичних можливостей хостового процесора та програмної готовності KVM. Якщо хостовий процесор має векторні блоки AVX-512, але ядро KVM запущене на застарілій версії без підтримки збереження розширеного стану `XSAVE` для регістрів `ZMM`, KVM автоматично скине прапорець `AVX512F` у цій таблиці, щоб запобігти пошкодженню контексту гостя.
2. **`KVM_GET_EMULATED_CPUID`** повертає список розширень, які KVM перехоплює і повністю моделює через програмний емулятор інструкцій `x86_emulate_instruction()`. До таких інструкцій належать `RDTSCP`, `MOVBE`, `CLFLUSHOPT`, інструкція захисту пам'яті користувача від супервізора `UMIP` (User-Mode Instruction Prevention) та розширення транзакційної пам'яті TSX. Це дає змогу вмикати певні сучасні інструкції для гостя навіть на застарілих хостових процесорах.

## Структури даних ядра: пам'ять та вирівнювання

Головним контейнером для передачі списку листків є структура `struct kvm_cpuid2`, яка містить заголовок із лічильником елементів та гнучкий масив структур (flexible array member) `struct kvm_cpuid_entry2`.

:::tabs
```c
#include <linux/types.h>

/* Опис одного листка або підлистка CPUID */
struct kvm_cpuid_entry2 {
    __u32 function;        /* Номер листка CPUID (значення регістра EAX) */
    __u32 index;           /* Номер підлистка CPUID (значення ECX, якщо значуще) */
    __u32 flags;           /* Керуючі прапорці запису (KVM_CPUID_FLAG_*) */
    __u32 eax;             /* Значення, що повертається у віртуальний EAX */
    __u32 ebx;             /* Значення, що повертається у віртуальний EBX */
    __u32 ecx;             /* Значення, що повертається у віртуальний ECX */
    __u32 edx;             /* Значення, що повертається у віртуальний EDX */
    __u32 padding[3];      /* Резерв для вирівнювання на 64-бітну межу (має бути 0) */
};

/* Загальний контейнер масиву листків */
struct kvm_cpuid2 {
    __u32 nent;            /* Кількість дійсних елементів у масиві entries */
    __u32 padding;         /* Вирівнювання структури */
    struct kvm_cpuid_entry2 entries[0]; /* Гнучкий масив записів */
};
```
```cpp
#include <cstdint>
#include <vector>
#include <span>

/* C++ представлення окремого листка CPUID */
struct alignas(8) CpuidEntry {
    std::uint32_t function{0};   // Номер листка (EAX)
    std::uint32_t index{0};      // Номер підлистка (ECX)
    std::uint32_t flags{0};      // Керуючі прапорці (KVM_CPUID_FLAG_*)
    std::uint32_t eax{0};        // Результат EAX
    std::uint32_t ebx{0};        // Результат EBX
    std::uint32_t ecx{0};        // Результат ECX
    std::uint32_t edx{0};        // Результат EDX
    std::uint32_t padding[3]{0}; // Вирівнювання
};

/* C++ безпечний контейнер таблиці CPUID */
struct CpuidTable {
    std::vector<CpuidEntry> entries;

    [[nodiscard]] std::size_t byte_size() const noexcept {
        return sizeof(std::uint32_t) * 2 + entries.size() * sizeof(CpuidEntry);
    }
};
```
:::

### Значення керуючого прапорця KVM_CPUID_FLAG_SIGNIFICANT_INDEX

Поле `flags` у структурі `struct kvm_cpuid_entry2` відіграє вирішальну роль у маршрутизації викликів. За замовчуванням більшість базових функцій `CPUID` (наприклад, Листок 0 або Листок 1) ігнорують вхідне значення регістра `ECX`.

Проте складені листки містять підрозділи (підлистки), стан яких залежить від значення `ECX`. Для таких листків у полі `flags` обов'язково встановлюється біт `KVM_CPUID_FLAG_SIGNIFCANT_INDEX` (`1U << 0`).

Коли цей прапорець встановлено, ядро KVM під час пошуку порівнює не лише номер листка `function == EAX`, а й номер підлистка `index == ECX`. Цей біт є критично обов'язковим для таких функцій:

* **Листок `0x00000004` (Deterministic Cache Parameters):** підлистки `0, 1, 2, 3...` послідовно описують рівні кешу L1D, L1I, L2, L3;
* **Листок `0x00000007` (Structured Extended Features):** підлисток 0 повертає прапорці AVX2, AVX-512, SMEP, SMAP; підлисток 1 повертає прапорці AVX_VNNI, AMX_TILE;
* **Листки `0x0000000B` та `0x0000001F` (Extended Topology Enumeration):** підлисток 0 описує рівень логічного потоку SMT, підлисток 1 — рівень фізичного ядра Core, підлисток 2 — модуль або сокет;
* **Листок `0x0000000D` (XSAVE Features and Component Sizes):** підлисток 0 містить сумарні розміри буфера для поточного `XCR0`; підлисток 1 описує підтримку `XSAVEC`/`XSAVES`; підлистки `2..62` повертають точний розмір та зміщення в пам'яті для кожного окремого компонента стану (AVX, AVX-512, AMX, PKRU);
* **Листок `0x00000014` (Intel Processor Trace):** описує апаратні можливості трасування конвеєра;
* **Листок `0x0000001D` та `0x00000024` (Intel AMX Tiles):** описують геометрію матричних акумуляторів і конфігурацію регістрів плиток TMUL.

## Внутрішня валідація у ядрі: функція kvm_check_cpuid()

Коли процес VMM викликає `ioctl(vcpu_fd, KVM_SET_CPUID2, cpuid)`, ядро KVM не просто копіює масив у пам'ять, а запускає суворий ланцюг перевірок цілісності у функції `kvm_check_cpuid()`:

1. **Контроль кількості записів:** Перевіряється, що `nent <= KVM_MAX_CPUID_ENTRIES` (256 або 512 залежно від конфігурації ядра). Якщо ліміт перевищено, ядро негайно повертає `-EINVAL`.
2. **Перевірка архітектурної несуперечливості:**
   * Якщо у Листку 1 увімкнено прапорець `AVX` (`ECX[28]`), перевіряється наявність біта `OSXSAVE` (`ECX[27]`) та наявність Листка `0x0000000D`;
   * Якщо у Листку 7 увімкнено `AVX512F`, ядро перевіряє, що в Листку `0x0000000D` маска компонентів містить біти 5 (opmask), 6 (ZMM_Hi256) та 7 (Hi16_ZMM);
   * Якщо увімкнено прапорець `XSAVES` (Leaf `0x0000000D`, підлисток 1, `EAX[3]`), перевіряється наявність апаратної підтримки MSR `IA32_XSS` на хості.
3. **Оновлення робочого стану vCPU (kvm_update_cpuid_runtime):**
   Після успішної валідації KVM автоматично перераховує залежні біти стану: активує емуляцію APIC, оновлює бітові маски дозволених записів у керуючі регістри `CR4` (наприклад, біт `CR4.OSXSAVE` або `CR4.FSGSBASE`) та скидає кешовані покажчики швидкого доступу в структурі `struct kvm_vcpu_arch`.

## Паравіртуальні прапорці ядра KVM (Листок 0x40000001)

У синтетичному листку `0x40000001` (KVM Features) гіпервізор повідомляє гостьовому ядру Linux про доступність оптимізованих інтерфейсів прямої взаємодії. Прапорці повертаються у 32-бітному регістрі `EAX`:

| Бітовий прапорець | Числове значення | Інженерне призначення |
| :--- | :--- | :--- |
| `KVM_FEATURE_CLOCKSOURCE` | `1U << 0` | Перше покоління паравіртуального годинника KVM (застаріле). |
| `KVM_FEATURE_NOP_IO_DELAY` | `1U << 1` | Дозволяє гостьовій системі не виконувати штучні затримки вводу-виводу на повільний порт `0x80`. |
| `KVM_FEATURE_MMU_OP` | `1U << 2` | Паравіртуальні пакетні операції оновлення таблиць сторінок (застаріле). |
| `KVM_FEATURE_CLOCKSOURCE2` | `1U << 3` | Сучасний стабільний системний годинник `kvm-clock`. Зменшує накладні витрати читання часу до кількох тактів без виходу у гіпервізор. |
| `KVM_FEATURE_ASYNC_PF` | `1U << 4` | Асинхронне сповіщення про промахи сторінок пам'яті. Дозволяє гостю перемикати задачі, поки хост читає сторінку зі свопу. |
| `KVM_FEATURE_STEAL_TIME` | `1U << 5` | Звітування гостьовій ОС про кількість часу, протягом якого vCPU був готовий виконувати код, але хост відібрав процесор на користь інших процесів. |
| `KVM_FEATURE_PV_EOI` | `1U << 6` | Паравіртуальне підтвердження переривань контролера APIC через спільну сторінку пам'яті без генерування VM-exit. |
| `KVM_FEATURE_PV_UNHALT` | `1U << 7` | Оптимізація спінлоків: vCPU викликає гіпервиклик при тривалому очікуванні блокування, щоб віддати квант часу власнику блокування. |
| `KVM_FEATURE_POLL_CONTROL` | `1U << 12` | Дозволяє гостю керувати тривалістю адаптивного полінгу хоста перед переходом vCPU в стан сну `HLT`. |
| `KVM_FEATURE_PV_SCHED_YIELD` | `1U << 13` | Спрямована передача процесорного часу конкретному vCPU у багатоядерних гостьових системах. |
| `KVM_FEATURE_MSI_EXT_DEST_ID` | `1U << 15` | Розширений 15-бітний ідентифікатор адресата для переривань MSI, що дає змогу адресувати понад 254 vCPU без апаратного переривання interrupt remapping. |

## Емуляція гіпервізора Microsoft Hyper-V (Enlightenments)

Для оптимізації гостьових систем під керуванням Windows ядро KVM підтримує повну емуляцію інтерфейсу Microsoft Hyper-V. Для цього VMM додає синтетичні листки в діапазоні `0x40000000`–`0x4000000A`:

* **Листок `0x40000000`:** повертає рядок виробника `"Microsoft Hv"`;
* **Листок `0x40000001` (HV_RECOMMENDATIONS):** повертає сигнатуру сумісності інтерфейсу `0x31237648` (`"Hv#1"`);
* **Листок `0x40000003` (HV_FEATURES):** повідомляє про доступність синтетичних таймерів (SynIC), паравіртуальних переривань (APIC enlightenments) та швидких гіпервикликів Hyper-V.

## Помилки, коди повернення та життєвий цикл викликів

Виклики `ioctl` підсистеми `CPUID` можуть завершуватися з такими кодами помилок у системній змінній `errno`:

1. **`E2BIG` (Argument list too long):**
   Виникає під час виклику `KVM_GET_SUPPORTED_CPUID`, якщо виділений користувацьким простором буфер має поле `nent`, менше за реальну кількість підтримуваних листків хоста. Ядро записує в поле `cpuid->nent` необхідну кількість елементів і повертає помилку `-1` (`errno = E2BIG`). Монітор VMM зобов'язаний перерозподілити пам'ять відповідного розміру і повторити виклик;
2. **`EFAULT` (Bad address):**
   Переданий покажчик на структуру `struct kvm_cpuid2` вказує на недійсну адресу пам'яті процесу або пам'ять, захищену від запису;
3. **`EINVAL` (Invalid argument):**
   Виникає під час виклику `KVM_SET_CPUID2`, якщо:
   * Кількість записів `nent` перевищує максимальну місткість внутрішнього масиву ядра KVM (зазвичай 256 або 512 елементів);
   * Виявлено некоректні або взаємовиключні комбінації прапорців;
   * Спроба увімкнути розширення, які хостовий процесор не здатний забезпечити (наприклад, увімкнення VMX без підтримки вкладеної віртуалізації);
4. **`EBUSY` (Device or resource busy):**
   Спроба викликати `KVM_SET_CPUID2` після того, як віртуальний процесор уже був запущений системним викликом `KVM_RUN`. Конфігурація `CPUID` є незмінною протягом усього життєвого циклу vCPU і не може модифікуватися на льоту.

## Повний приклад використання інтерфейсу

Наведемо завершений модуль запиту та безпечного завантаження таблиці `CPUID` із коректною обробкою динамічного буфера.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <linux/kvm.h>

struct kvm_cpuid2* kvm_alloc_cpuid(uint32_t nent) {
    size_t size = sizeof(struct kvm_cpuid2) + nent * sizeof(struct kvm_cpuid_entry2);
    struct kvm_cpuid2* cpuid = (struct kvm_cpuid2*)malloc(size);
    if (cpuid) {
        memset(cpuid, 0, size);
        cpuid->nent = nent;
    }
    return cpuid;
}

struct kvm_cpuid2* get_host_supported_cpuid(int kvm_fd) {
    uint32_t nent = 64;
    struct kvm_cpuid2* cpuid = kvm_alloc_cpuid(nent);
    if (!cpuid) return NULL;

    while (ioctl(kvm_fd, KVM_GET_SUPPORTED_CPUID, cpuid) < 0) {
        if (errno == E2BIG) {
            nent = cpuid->nent; // Ядро записало точну необхідну кількість
            free(cpuid);
            cpuid = kvm_alloc_cpuid(nent);
            if (!cpuid) return NULL;
            continue;
        }
        perror("Помилка KVM_GET_SUPPORTED_CPUID");
        free(cpuid);
        return NULL;
    }
    return cpuid;
}

int apply_vcpu_cpuid_configuration(int vcpu_fd, struct kvm_cpuid2* cpuid) {
    // Модифікація прапорців перед завантаженням
    for (uint32_t i = 0; i < cpuid->nent; ++i) {
        struct kvm_cpuid_entry2* entry = &cpuid->entries[i];

        // Маскуємо векторні інструкції AVX-512 для сумісності міграції
        if (entry->function == 7 && entry->index == 0) {
            entry->ebx &= ~(1U << 16); // AVX512F
            entry->ebx &= ~(1U << 17); // AVX512DQ
            entry->ebx &= ~(1U << 30); // AVX512BW
        }
    }

    if (ioctl(vcpu_fd, KVM_SET_CPUID2, cpuid) < 0) {
        perror("Помилка KVM_SET_CPUID2");
        return -1;
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <cstring>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/kvm.h>

class KvmCpuidService {
public:
    static std::vector<kvm_cpuid_entry2> fetch_supported_cpuid(int kvm_fd) {
        uint32_t nent = 64;
        while (true) {
            size_t size = sizeof(kvm_cpuid2) + nent * sizeof(kvm_cpuid_entry2);
            auto buffer = std::make_unique<uint8_t[]>(size);
            auto* cpuid = reinterpret_cast<kvm_cpuid2*>(buffer.get());
            std::memset(cpuid, 0, size);
            cpuid->nent = nent;

            if (::ioctl(kvm_fd, KVM_GET_SUPPORTED_CPUID, cpuid) == 0) {
                return std::vector<kvm_cpuid_entry2>(
                    cpuid->entries, cpuid->entries + cpuid->nent
                );
            }

            if (errno == E2BIG) {
                nent = cpuid->nent; // Отримуємо точний розмір від ядра
                continue;
            }

            throw std::system_error(errno, std::generic_category(), "KVM_GET_SUPPORTED_CPUID failed");
        }
    }

    static void configure_vcpu(int vcpu_fd, std::vector<kvm_cpuid_entry2>& entries) {
        for (auto& entry : entries) {
            if (entry.function == 7 && entry.index == 0) {
                entry.ebx &= ~(1U << 16); // Вимикаємо AVX512F
                entry.ebx &= ~(1U << 17); // Вимикаємо AVX512DQ
                entry.ebx &= ~(1U << 30); // Вимикаємо AVX512BW
            }
        }

        size_t size = sizeof(kvm_cpuid2) + entries.size() * sizeof(kvm_cpuid_entry2);
        auto buffer = std::make_unique<uint8_t[]>(size);
        auto* cpuid = reinterpret_cast<kvm_cpuid2*>(buffer.get());
        std::memset(cpuid, 0, size);

        cpuid->nent = static_cast<uint32_t>(entries.size());
        std::memcpy(cpuid->entries, entries.data(), entries.size() * sizeof(kvm_cpuid_entry2));

        if (::ioctl(vcpu_fd, KVM_SET_CPUID2, cpuid) < 0) {
            throw std::system_error(errno, std::generic_category(), "KVM_SET_CPUID2 failed");
        }
    }
};
```
:::
